# extract-video

> ⚙️ **Setup (bring your own keys):** part of the ingest pipeline — needs API keys + the shared `_lib`. See [`../_lib/README.md`](../_lib/README.md): copy `ingest-config.template.json` to `~/.openclaw/ingest-config.json` and fill in your own keys.

Owned by: `ingest-extractor`

Downloads audio from video URLs, detects language, transcribes with the appropriate ASR model, and captions keyframes.

## Invocation

```bash
cd skills
uv run --with yt-dlp --with faster-whisper --with dashscope --with google-genai --with requests \
  python extract-video/extract_video.py "<url_or_local_path>"
```

## Language routing

1. Run faster-whisper on first 30 seconds only for language detection
2. Confidence > 0.4 AND detected `zh` → Qwen ASR via DashScope for full file
3. Otherwise → faster-whisper `small` model for full file

## Output

```json
{
  "transcript_segments": [{"start": 0.0, "end": 3.2, "text": "..."}],
  "full_transcript": "...",
  "detected_language": "en|zh",
  "asr_used": "faster-whisper|qwen-asr",
  "keyframes": [{"time": 30, "path": "...", "caption": "..."}],
  "metadata": {"url": "...", "duration": 1234, "title": "..."},
  "source_metadata": {...}
}
```

## Notes

- faster-whisper and playwright have conflicting deps — this skill runs in its own uv env
- Apple Silicon: faster-whisper uses `compute_type=int8` to avoid Metal issues
- `yt-dlp -f bestaudio` for audio-only download, convert to wav via ffmpeg

## Status

Built. `extract_video.py` live.
