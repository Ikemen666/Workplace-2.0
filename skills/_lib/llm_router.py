"""
llm_router.py — Central model router for the ingest pipeline.

Every skill that calls an LLM imports call_model() from here.
Reads API keys and routing table from ~/.openclaw/ingest-config.json.
Never logs full API keys — always masks in output.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


# ── Config ──────────────────────────────────────────────────────────────────

def _load_config() -> dict:
    path = Path.home() / ".openclaw" / "ingest-config.json"
    if not path.exists():
        raise FileNotFoundError(f"ingest-config.json not found at {path}")
    with open(path) as f:
        return json.load(f)


def _mask_key(key: str) -> str:
    if len(key) > 8:
        return key[:4] + "***" + key[-4:]
    return "***"


# ── Routing table ────────────────────────────────────────────────────────────

TASK_ROUTING = {
    "classify_source":  {"model": "deepseek-chat",           "provider": "deepseek"},
    "distill":          {"model": "gemini-2.5-pro",           "provider": "google"},
    "distill_long":     {"model": "kimi-k2.5",                "provider": "moonshot"},
    "pdf_vision":       {"model": "gemini-2.5-flash",         "provider": "google"},
    "keyframe_caption": {"model": "gemini-2.5-flash",         "provider": "google"},
    "xlsx_narrate":     {"model": "deepseek-chat",            "provider": "deepseek"},
    "gap_synthesis":    {"model": "gemini-2.5-flash",         "provider": "google"},
    "concept_dedupe":   {"model": "deepseek-chat",            "provider": "deepseek"},
    "asr_chinese":      {"model": "paraformer-realtime-v2",   "provider": "dashscope"},
}


# ── Provider clients ─────────────────────────────────────────────────────────

def _call_google(model: str, prompt: str, api_key: str, **kwargs) -> dict:
    from google import genai  # type: ignore
    from google.genai import types  # type: ignore

    client = genai.Client(api_key=api_key)

    # Map generic max_tokens → Google's max_output_tokens
    max_tokens = kwargs.pop("max_tokens", None)
    gen_cfg = kwargs.pop("generation_config", None)
    if max_tokens is not None:
        gen_cfg = types.GenerateContentConfig(max_output_tokens=max_tokens)

    # Handle multimodal content (list of parts) vs plain text
    if isinstance(prompt, list):
        contents = prompt
    else:
        contents = prompt

    resp = client.models.generate_content(
        model=model,
        contents=contents,
        config=gen_cfg,
        **kwargs,
    )
    text = resp.text if hasattr(resp, "text") else resp.candidates[0].content.parts[0].text
    return {
        "text": text,
        "model": model,
        "provider": "google",
        "finish_reason": str(resp.candidates[0].finish_reason) if resp.candidates else None,
    }


def _call_deepseek(model: str, prompt: str, api_key: str, **kwargs) -> dict:
    from openai import OpenAI  # type: ignore
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    messages = kwargs.pop("messages", [{"role": "user", "content": prompt}])
    resp = client.chat.completions.create(model=model, messages=messages, **kwargs)
    return {
        "text": resp.choices[0].message.content,
        "model": model,
        "provider": "deepseek",
        "finish_reason": resp.choices[0].finish_reason,
        "usage": resp.usage.model_dump() if resp.usage else None,
    }


def _call_moonshot(model: str, prompt: str, api_key: str, **kwargs) -> dict:
    from openai import OpenAI  # type: ignore
    client = OpenAI(api_key=api_key, base_url="https://api.moonshot.cn/v1")
    messages = kwargs.pop("messages", [{"role": "user", "content": prompt}])
    resp = client.chat.completions.create(model=model, messages=messages, **kwargs)
    return {
        "text": resp.choices[0].message.content,
        "model": model,
        "provider": "moonshot",
        "finish_reason": resp.choices[0].finish_reason,
        "usage": resp.usage.model_dump() if resp.usage else None,
    }


def _call_dashscope(model: str, prompt: str, api_key: str, **kwargs) -> dict:
    """DashScope text completion (non-ASR). ASR uses separate dashscope SDK path."""
    from openai import OpenAI  # type: ignore
    client = OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    messages = kwargs.pop("messages", [{"role": "user", "content": prompt}])
    resp = client.chat.completions.create(model=model, messages=messages, **kwargs)
    return {
        "text": resp.choices[0].message.content,
        "model": model,
        "provider": "dashscope",
        "finish_reason": resp.choices[0].finish_reason,
        "usage": resp.usage.model_dump() if resp.usage else None,
    }


# ── ASR (DashScope Paraformer) — separate path ───────────────────────────────

def call_asr_chinese(audio_path: str) -> dict:
    """
    Transcribe audio using DashScope Paraformer ASR.
    audio_path: local wav/mp3 file path.
    Returns: {transcript, segments, model, provider}
    """
    config = _load_config()
    api_key = config["api_keys"]["DASHSCOPE_API_KEY"]

    import dashscope  # type: ignore
    from dashscope.audio.asr import Recognition

    dashscope.api_key = api_key
    rec = Recognition(
        model="paraformer-realtime-v2",
        format="wav",
        sample_rate=16000,
        callback=None,
    )
    result = rec.call(audio_path)
    if result.status_code != 200:
        raise RuntimeError(f"DashScope ASR failed: {result.code} — {result.message}")

    sentences = result.get_sentence() or []
    return {
        "transcript": " ".join(s.get("text", "") for s in sentences),
        "segments": sentences,
        "model": "paraformer-realtime-v2",
        "provider": "dashscope",
    }


# ── Main entry point ─────────────────────────────────────────────────────────

def call_model(task: str, content: Any, **kwargs) -> dict:
    """
    Route a task to the appropriate model and provider.

    Args:
        task:    Task name from TASK_ROUTING table (e.g. "distill", "gap_synthesis")
        content: Prompt string, or structured content (list for vision tasks)
        **kwargs: Passed through to the provider call (e.g. max_tokens, temperature)

    Returns:
        dict with at minimum: {text, model, provider}

    Raises:
        KeyError: unknown task
        FileNotFoundError: ingest-config.json missing
        RuntimeError: provider API error
    """
    if task not in TASK_ROUTING:
        raise KeyError(f"Unknown task '{task}'. Known tasks: {list(TASK_ROUTING)}")

    config = _load_config()
    route = TASK_ROUTING[task]

    # Allow per-call override via config (e.g. for testing)
    if "models" in config and task in config["models"]:
        route = config["models"][task]

    provider = route["provider"]
    model = route["model"]

    # Get API key
    key_map = {
        "google":    "GEMINI_API_KEY",
        "deepseek":  "DEEPSEEK_API_KEY",
        "moonshot":  "MOONSHOT_API_KEY",
        "dashscope": "DASHSCOPE_API_KEY",
    }
    if provider not in key_map:
        raise KeyError(f"Unknown provider '{provider}'")

    api_key = config["api_keys"][key_map[provider]]

    # Build prompt string
    if isinstance(content, str):
        prompt = content
    else:
        prompt = json.dumps(content, ensure_ascii=False)

    # Dispatch
    if provider == "google":
        return _call_google(model, prompt, api_key, **kwargs)
    elif provider == "deepseek":
        return _call_deepseek(model, prompt, api_key, **kwargs)
    elif provider == "moonshot":
        return _call_moonshot(model, prompt, api_key, **kwargs)
    elif provider == "dashscope":
        return _call_dashscope(model, prompt, api_key, **kwargs)
    else:
        raise RuntimeError(f"No handler for provider '{provider}'")


# ── Ping (used by test_llm_router.py) ───────────────────────────────────────

def ping_all_providers() -> dict[str, dict]:
    """
    Send a minimal one-token request to each provider to verify keys work.
    Returns {provider: {ok: bool, masked_key: str, error: str|None}}
    """
    config = _load_config()
    results = {}

    providers = [
        ("google",    "distill",        "Say: OK"),
        ("deepseek",  "classify_source","Say: OK"),
        ("moonshot",  "distill_long",   "Say: OK"),
        ("dashscope", "xlsx_narrate",   "Say: OK"),
    ]

    key_map = {
        "google":    "GEMINI_API_KEY",
        "deepseek":  "DEEPSEEK_API_KEY",
        "moonshot":  "MOONSHOT_API_KEY",
        "dashscope": "DASHSCOPE_API_KEY",
    }

    for provider, task, ping_prompt in providers:
        key = config["api_keys"][key_map[provider]]
        masked = _mask_key(key)
        try:
            resp = call_model(task, ping_prompt, max_tokens=5)
            results[provider] = {
                "ok": True,
                "masked_key": masked,
                "response_preview": (resp.get("text") or "")[:40],
                "error": None,
            }
        except Exception as e:
            results[provider] = {
                "ok": False,
                "masked_key": masked,
                "response_preview": None,
                "error": str(e),
            }

    # Tavily ping (HTTP, not LLM)
    try:
        import requests  # type: ignore
        tavily_key = config["api_keys"]["TAVILY_API_KEY"]
        r = requests.post(
            "https://api.tavily.com/search",
            json={"api_key": tavily_key, "query": "ping", "max_results": 1},
            timeout=10,
        )
        results["tavily"] = {
            "ok": r.status_code == 200,
            "masked_key": _mask_key(tavily_key),
            "response_preview": str(r.status_code),
            "error": None if r.status_code == 200 else r.text[:100],
        }
    except Exception as e:
        results["tavily"] = {
            "ok": False,
            "masked_key": _mask_key(config["api_keys"]["TAVILY_API_KEY"]),
            "response_preview": None,
            "error": str(e),
        }

    return results
