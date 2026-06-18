#!/usr/bin/env python3
"""
extract_web.py — Extract clean article content from a URL using trafilatura.

Usage:
    uv run --with trafilatura --with requests \
        python extract_web.py "https://example.com/article"
"""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path


def detect_language(text: str) -> str:
    if not text:
        return "en"
    cjk = sum(1 for c in text if "\u4e00" <= c <= "\u9fff")
    if cjk / max(len(text), 1) > 0.1:
        return "zh"
    return "en"


def download_images(image_urls: list[str], images_dir: Path) -> list[str]:
    """Download images from URLs to images_dir. Returns list of saved paths."""
    import requests  # type: ignore

    saved = []
    for url in image_urls[:10]:  # cap at 10 images
        try:
            resp = requests.get(url, timeout=10, stream=True)
            if resp.status_code == 200:
                ext = url.split(".")[-1].split("?")[0][:4].lower()
                if ext not in ("png", "jpg", "jpeg", "gif", "webp"):
                    ext = "jpg"
                fname = hashlib.sha1(url.encode()).hexdigest()[:12] + "." + ext
                dest = images_dir / fname
                with open(dest, "wb") as f:
                    for chunk in resp.iter_content(8192):
                        f.write(chunk)
                saved.append(str(dest))
        except Exception:
            pass
    return saved


def extract_web(url: str) -> dict:
    import trafilatura  # type: ignore
    import trafilatura.settings  # type: ignore

    # Fetch and extract
    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        raise RuntimeError(f"Failed to fetch URL: {url}")

    # Extract metadata
    metadata = trafilatura.extract_metadata(downloaded)
    title = getattr(metadata, "title", "") or ""
    author = getattr(metadata, "author", "") or ""
    date = str(getattr(metadata, "date", "") or "")
    sitename = getattr(metadata, "sitename", "") or ""
    image_urls = []
    try:
        img_list = getattr(metadata, "image", None)
        if img_list:
            image_urls = [img_list] if isinstance(img_list, str) else list(img_list)
    except Exception:
        pass

    # Extract main text
    raw_text = trafilatura.extract(
        downloaded,
        include_tables=True,
        include_images=False,  # we handle images separately
        include_links=False,
        output_format="txt",
        with_metadata=False,
    ) or ""

    # Try to get canonical URL
    canonical_url = url
    try:
        from trafilatura.utils import load_html  # type: ignore
        tree = load_html(downloaded)
        if tree is not None:
            canonical = tree.find(".//link[@rel='canonical']")
            if canonical is not None:
                canonical_url = canonical.get("href", url)
    except Exception:
        pass

    # Download images
    url_hash = hashlib.sha1(url.encode()).hexdigest()[:8]
    images_dir = Path(tempfile.gettempdir()) / f"ingest-images-{url_hash}"
    images_dir.mkdir(exist_ok=True)
    download_images(image_urls, images_dir)

    language_hint = detect_language(raw_text)

    return {
        "raw_text": raw_text,
        "title": title,
        "author": author,
        "publish_date": date,
        "canonical_url": canonical_url,
        "site_name": sitename,
        "images_dir": str(images_dir),
        "language_hint": language_hint,
        "source_metadata": {
            "source_type": "web",
            "original_url_or_path": url,
            "title": title,
            "author": author,
            "language": language_hint,
            "images_dir": str(images_dir),
        },
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Extract content from a web URL")
    parser.add_argument("url", help="URL to extract")
    args = parser.parse_args()

    result = extract_web(args.url)
    preview = dict(result)
    if len(preview.get("raw_text", "")) > 500:
        preview["raw_text"] = preview["raw_text"][:500] + f"\n... [{len(result['raw_text'])} chars total]"
    print(json.dumps(preview, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
