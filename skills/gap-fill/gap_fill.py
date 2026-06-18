#!/usr/bin/env python3
"""
gap_fill.py — Fill knowledge gaps using bounded Tavily searches.

Hard cap enforced in code. Never hallucinates — omits gaps with no useful results.

Usage:
    echo '<json>' | uv run --with tavily-python --with google-genai --with openai --with requests python gap_fill.py
    uv run ... python gap_fill.py input.json
"""

from __future__ import annotations

import json
import sys
import os
from pathlib import Path


def load_config() -> dict:
    path = Path.home() / ".openclaw" / "ingest-config.json"
    if not path.exists():
        raise FileNotFoundError(f"ingest-config.json not found at {path}")
    with open(path) as f:
        return json.load(f)


def tavily_search(query: str, api_key: str) -> list[dict]:
    """Run one Tavily search. Returns list of {title, url, content} dicts."""
    from tavily import TavilyClient  # type: ignore
    client = TavilyClient(api_key=api_key)
    resp = client.search(
        query=query,
        search_depth="basic",
        max_results=3,
    )
    return resp.get("results", [])


def synthesize_context(term: str, results: list[dict], api_key: str) -> dict | None:
    """
    Synthesize 1–2 sentences of context from Tavily results.
    Returns {term, context, source_url} or None if results are empty/useless.
    """
    if not results:
        return None

    # Build a brief for the synthesis LLM
    snippets = "\n".join(
        f"[{i+1}] {r.get('title', '')} — {r.get('content', '')[:300]}"
        for i, r in enumerate(results[:3])
    )
    if not snippets.strip():
        return None

    prompt = (
        f"You are filling a knowledge gap about: {term!r}\n\n"
        f"Search results:\n{snippets}\n\n"
        f"Write 1–2 factual sentences that define or explain '{term}' "
        f"based only on the search results above. "
        f"Do not add information not present in the results. "
        f"If the results don't contain useful information about '{term}', reply with exactly: SKIP"
    )

    # Add _lib to path for llm_router
    lib_path = str(Path(__file__).parent.parent / "_lib")
    if lib_path not in sys.path:
        sys.path.insert(0, lib_path)
    from llm_router import call_model

    resp = call_model("gap_synthesis", prompt, max_tokens=300)
    text = (resp.get("text") or "").strip()

    if not text or text.upper() == "SKIP" or len(text) < 10:
        return None

    # Pick the best source URL (first result)
    source_url = results[0].get("url", "")

    return {
        "term": term,
        "context": text,
        "source_url": source_url,
    }


def fill_gaps(data: dict) -> dict:
    """
    Main entry point.
    Reads knowledge_gaps from data, runs bounded Tavily searches, adds enriched_context.
    """
    config = load_config()
    budget: int = int(config.get("gap_fill", {}).get("budget", 3))
    tavily_key = config["api_keys"]["TAVILY_API_KEY"]

    gaps = data.get("knowledge_gaps", [])

    # Hard cap enforced here
    gaps_to_process = gaps[:budget]

    enriched_context = []

    for gap in gaps_to_process:
        term = gap.get("term_or_question", "")
        query = gap.get("search_query", term)
        if not term or not query:
            continue

        try:
            results = tavily_search(query, tavily_key)
            ctx = synthesize_context(term, results, tavily_key)
            if ctx is not None:
                enriched_context.append(ctx)
        except Exception as e:
            # Log to stderr, never silently hallucinate
            print(f"[gap-fill] Warning: gap '{term}' failed: {e}", file=sys.stderr)
            continue

    result = dict(data)
    result["enriched_context"] = enriched_context
    return result


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Fill knowledge gaps with Tavily")
    parser.add_argument("input", nargs="?", help="JSON input file (or stdin)")
    args = parser.parse_args()

    if args.input:
        with open(args.input) as f:
            data = json.load(f)
    else:
        data = json.load(sys.stdin)

    result = fill_gaps(data)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
