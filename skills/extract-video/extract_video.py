#!/usr/bin/env python3
"""
extract_video.py — Download audio from video URLs/files, transcribe, caption keyframes.

Language routing:
  1. Run faster-whisper on first 30s for language detection
  2. If zh (confidence > 0.4) → DashScope Paraformer for full file
  3. Otherwise → faster-whisper 'small' model for full file

Keyframe captioning via Gemini Flash (requires ffmpeg in PATH).

Usage:
    cd skills
    uv run --with yt-dlp --with faster-whisper --with google-genai --with openai --with requests \
        python extract-video/extract_video.py "https://youtube.com/watch?v=..."

    uv run --with yt-dlp --with faster-whisper --with google-genai --with openai --with requests \
        python extract-video/extract_video.py /path/to/video.mp4
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

BASE = Path(__file__).parent.parent
sys.path.insert(0, str(BASE / "_lib"))

KEYFRAME_INTERVAL = 60   # seconds between keyframes
MAX_KEYFRAMES = 8
LANG_DETECT_SECS = 30    # seconds of audio for language detection
ZH_CONFIDENCE_THRESHOLD = 0.4


def detect_language(text: str) -> str:
    if not text:
        return "en"
    cjk = sum(1 for c in text if "\u4e00" <= c <= "\u9fff")
    if cjk / max(len(text), 1) > 0.1:
        return "zh"
    return "en"


# ── Audio helpers ────────────────────────────────────────────────────────────

def trim_audio(audio_path: Path, duration_secs: int, output_path: Path) -> bool:
    """Trim audio to first N seconds using ffmpeg. Returns True on success."""
    try:
        result = subprocess.run(
            [
                "ffmpeg", "-y", "-i", str(audio_path),
                "-t", str(duration_secs),
                "-ar", "16000", "-ac", "1",
                str(output_path),
            ],
            capture_output=True, timeout=60,
        )
        return result.returncode == 0 and output_path.exists()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def convert_to_wav(input_path: Path, output_path: Path) -> bool:
    """Convert audio/video file to 16kHz mono WAV."""
    try:
        result = subprocess.run(
            [
                "ffmpeg", "-y", "-i", str(input_path),
                "-ar", "16000", "-ac", "1", "-vn",
                str(output_path),
            ],
            capture_output=True, timeout=300,
        )
        return result.returncode == 0 and output_path.exists()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


# ── Download (URL sources) ───────────────────────────────────────────────────

def download_video(url: str, tmpdir: Path) -> tuple[Path, dict]:
    """
    Download audio track from video URL via yt-dlp.
    Returns (wav_path, metadata_dict).
    """
    import yt_dlp  # type: ignore

    audio_template = str(tmpdir / "audio.%(ext)s")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": audio_template,
        "quiet": True,
        "no_warnings": True,
        "postprocessors": [],  # we'll convert manually with ffmpeg
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)

    metadata = {
        "url": url,
        "title": info.get("title", ""),
        "uploader": info.get("uploader", ""),
        "duration": info.get("duration"),
        "upload_date": info.get("upload_date", ""),
        "description": (info.get("description", "") or "")[:500],
        "view_count": info.get("view_count"),
        "webpage_url": info.get("webpage_url", url),
    }

    # Find the downloaded file
    downloaded_files = list(tmpdir.glob("audio.*"))
    if not downloaded_files:
        raise RuntimeError(f"yt-dlp downloaded nothing to {tmpdir}")

    audio_raw = downloaded_files[0]

    # Convert to WAV for ASR
    wav_path = tmpdir / "audio.wav"
    if not convert_to_wav(audio_raw, wav_path):
        # ffmpeg not available or failed — try using the raw file directly
        wav_path = audio_raw

    return wav_path, metadata


# ── Transcription ────────────────────────────────────────────────────────────

def transcribe_whisper(audio_path: Path, model_size: str = "small") -> dict:
    """Transcribe with faster-whisper. Returns {transcript, segments, language}."""
    from faster_whisper import WhisperModel  # type: ignore

    model = WhisperModel(
        model_size,
        compute_type="int8",  # Apple Silicon safe; no Metal issues
        device="cpu",
    )
    segments_gen, info = model.transcribe(
        str(audio_path),
        beam_size=5,
        vad_filter=True,
    )
    segments = []
    for seg in segments_gen:
        segments.append({
            "start": round(seg.start, 2),
            "end": round(seg.end, 2),
            "text": seg.text.strip(),
        })

    full_transcript = " ".join(s["text"] for s in segments)
    return {
        "transcript": full_transcript,
        "segments": segments,
        "language": info.language,
        "language_probability": round(info.language_probability, 3),
    }


def detect_lang_fast(audio_path: Path, tmpdir: Path) -> tuple[str, float]:
    """
    Run faster-whisper on first LANG_DETECT_SECS of audio to detect language.
    Returns (language_code, confidence).
    """
    trimmed = tmpdir / "detect_trim.wav"
    if trim_audio(audio_path, LANG_DETECT_SECS, trimmed):
        detect_src = trimmed
    else:
        detect_src = audio_path  # fallback: full file

    try:
        from faster_whisper import WhisperModel  # type: ignore
        model = WhisperModel("tiny", compute_type="int8", device="cpu")
        _, info = model.transcribe(
            str(detect_src),
            beam_size=1,
            language=None,
        )
        return info.language, info.language_probability
    except Exception as e:
        print(f"[extract-video] Language detection failed: {e}", file=sys.stderr)
        return "en", 0.0


# ── Keyframe captioning ──────────────────────────────────────────────────────

def extract_keyframes(video_path: Path, images_dir: Path, duration: int | None) -> list[int]:
    """
    Extract one frame every KEYFRAME_INTERVAL seconds using ffmpeg.
    Returns list of timestamps (seconds) for extracted frames.
    """
    if not duration:
        duration = 3600  # assume max 1h if unknown

    timestamps = list(range(0, min(duration, KEYFRAME_INTERVAL * MAX_KEYFRAMES), KEYFRAME_INTERVAL))
    timestamps = timestamps[:MAX_KEYFRAMES]

    extracted = []
    for ts in timestamps:
        frame_path = images_dir / f"frame_{ts:05d}.jpg"
        try:
            result = subprocess.run(
                [
                    "ffmpeg", "-y", "-ss", str(ts), "-i", str(video_path),
                    "-vframes", "1", "-q:v", "5",
                    str(frame_path),
                ],
                capture_output=True, timeout=30,
            )
            if result.returncode == 0 and frame_path.exists():
                extracted.append(ts)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            break  # ffmpeg not available

    return extracted


def caption_keyframes(
    images_dir: Path,
    timestamps: list[int],
    api_key: str,
) -> list[dict]:
    """Caption extracted frames using Gemini Flash vision."""
    from google import genai  # type: ignore
    from google.genai import types  # type: ignore

    client = genai.Client(api_key=api_key)
    captions = []

    for ts in timestamps:
        frame_path = images_dir / f"frame_{ts:05d}.jpg"
        if not frame_path.exists():
            continue
        try:
            image_bytes = frame_path.read_bytes()
            resp = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                    "Describe what is shown in this video frame in one concise sentence.",
                ],
                config=types.GenerateContentConfig(max_output_tokens=80),
            )
            caption = (resp.text or "").strip()
            captions.append({
                "time": ts,
                "path": str(frame_path),
                "caption": caption,
            })
        except Exception as e:
            captions.append({
                "time": ts,
                "path": str(frame_path),
                "caption": f"[captioning failed: {e}]",
            })

    return captions


# ── Main extraction ──────────────────────────────────────────────────────────

def extract_video(source: str) -> dict:
    from llm_router import call_asr_chinese, _load_config  # type: ignore

    config = _load_config()
    gemini_key = config["api_keys"]["GEMINI_API_KEY"]

    source_path = Path(source).expanduser()
    is_url = source.startswith("http://") or source.startswith("https://")

    # Temp workspace
    src_hash = hashlib.sha1(source.encode()).hexdigest()[:8]
    tmpdir = Path(tempfile.gettempdir()) / f"ingest-video-{src_hash}"
    tmpdir.mkdir(exist_ok=True)
    images_dir = Path(tempfile.gettempdir()) / f"ingest-images-{src_hash}"
    images_dir.mkdir(exist_ok=True)

    # ── Step 1: Get audio + metadata ────────────────────────────────────────
    if is_url:
        print(f"[extract-video] Downloading: {source}", file=sys.stderr)
        audio_path, metadata = download_video(source, tmpdir)
    else:
        if not source_path.exists():
            raise FileNotFoundError(f"Video file not found: {source_path}")
        audio_path = tmpdir / "audio.wav"
        if not convert_to_wav(source_path, audio_path):
            # ffmpeg failed; try using original
            audio_path = source_path
        metadata = {
            "url": "",
            "title": source_path.stem,
            "uploader": "",
            "duration": None,
            "upload_date": "",
            "description": "",
            "view_count": None,
            "webpage_url": str(source_path),
        }

    print(f"[extract-video] Audio at: {audio_path}", file=sys.stderr)

    # ── Step 2: Language detection ───────────────────────────────────────────
    print("[extract-video] Detecting language...", file=sys.stderr)
    detected_lang, lang_conf = detect_lang_fast(audio_path, tmpdir)
    print(f"[extract-video] Detected: {detected_lang} (conf={lang_conf:.2f})", file=sys.stderr)

    # ── Step 3: Full transcription ───────────────────────────────────────────
    use_qwen = (detected_lang == "zh" and lang_conf >= ZH_CONFIDENCE_THRESHOLD)

    if use_qwen:
        print("[extract-video] Using DashScope Paraformer (zh)", file=sys.stderr)
        asr_result = call_asr_chinese(str(audio_path))
        segments = asr_result.get("segments", [])
        full_transcript = asr_result.get("transcript", "")
        asr_used = "qwen-asr"
        final_lang = "zh"
    else:
        print("[extract-video] Using faster-whisper small", file=sys.stderr)
        whisper_result = transcribe_whisper(audio_path, model_size="small")
        segments = whisper_result["segments"]
        full_transcript = whisper_result["transcript"]
        asr_used = "faster-whisper"
        final_lang = whisper_result.get("language", detected_lang)

    print(f"[extract-video] Transcript: {len(full_transcript)} chars, {len(segments)} segments", file=sys.stderr)

    # ── Step 4: Keyframe extraction + captioning ─────────────────────────────
    keyframe_captions: list[dict] = []
    duration = metadata.get("duration")

    # Only for video files (local or downloaded) — not audio-only
    video_source = source_path if not is_url else tmpdir / "video_for_frames"
    if is_url:
        # Check if we have the original video file (yt-dlp may have left it)
        video_files = [f for f in tmpdir.glob("audio.*") if f.suffix.lower() in (".mp4", ".webm", ".mkv")]
        if video_files:
            video_source = video_files[0]
        else:
            video_source = None

    if video_source and Path(str(video_source)).exists() if video_source else (not is_url and source_path.exists()):
        actual_src = video_source if video_source else source_path
        print("[extract-video] Extracting keyframes...", file=sys.stderr)
        timestamps = extract_keyframes(actual_src, images_dir, duration)
        if timestamps:
            print(f"[extract-video] Captioning {len(timestamps)} keyframes...", file=sys.stderr)
            keyframe_captions = caption_keyframes(images_dir, timestamps, gemini_key)

    language_hint = "zh" if final_lang == "zh" else "en"

    return {
        "raw_text": full_transcript,
        "transcript_segments": segments,
        "full_transcript": full_transcript,
        "detected_language": final_lang,
        "asr_used": asr_used,
        "keyframes": keyframe_captions,
        "metadata": metadata,
        "images_dir": str(images_dir),
        "language_hint": language_hint,
        "source_metadata": {
            "source_type": "video",
            "original_url_or_path": source,
            "title": metadata.get("title", ""),
            "uploader": metadata.get("uploader", ""),
            "duration": duration,
            "language": language_hint,
            "asr_used": asr_used,
            "images_dir": str(images_dir),
        },
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Extract transcript from video URL or file")
    parser.add_argument("source", help="Video URL or local file path")
    args = parser.parse_args()

    result = extract_video(args.source)
    preview = dict(result)
    if len(preview.get("raw_text", "")) > 600:
        preview["raw_text"] = preview["raw_text"][:600] + f"\n... [{len(result['raw_text'])} chars total]"
    preview["transcript_segments"] = f"[{len(result['transcript_segments'])} segments]"
    print(json.dumps(preview, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
