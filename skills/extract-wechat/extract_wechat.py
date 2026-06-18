#!/usr/bin/env python3
"""
extract_wechat.py — Fetch WeChat 公众号 articles via Playwright (persistent profile).

WeChat article links expire (48–72h). HTML is cached immediately on first fetch.
Supports URL fetch, cached HTML, and manual-paste HTML/text fallback.

Usage:
    cd skills

    # First-run login (opens headed browser):
    uv run --with playwright --with beautifulsoup4 --with requests \
        python extract-wechat/extract_wechat.py --login

    # Fetch live article:
    uv run --with playwright --with beautifulsoup4 --with requests \
        python extract-wechat/extract_wechat.py "https://mp.weixin.qq.com/s/..."

    # Manual-paste fallback (saved .html file):
    uv run --with playwright --with beautifulsoup4 --with requests \
        python extract-wechat/extract_wechat.py /path/to/saved.html
"""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path

PROFILE_DIR = Path.home() / ".openclaw" / "playwright-profile"
CACHE_DIR = Path.home() / ".openclaw" / "wechat-cache"

WECHAT_URL_PREFIX = "https://mp.weixin.qq.com/"


def detect_language(text: str) -> str:
    if not text:
        return "zh"  # WeChat is primarily Chinese
    cjk = sum(1 for c in text if "\u4e00" <= c <= "\u9fff")
    if cjk / max(len(text), 1) > 0.05:
        return "zh"
    return "en"


def cache_path(url: str) -> Path:
    sha = hashlib.sha1(url.encode()).hexdigest()
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR / f"{sha}.html"


def fetch_with_playwright(url: str) -> str:
    """Fetch WeChat article HTML using Playwright with persistent profile."""
    from playwright.sync_api import sync_playwright  # type: ignore

    PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            str(PROFILE_DIR),
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        page = context.new_page()
        page.set_extra_http_headers({
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 "
                "MicroMessenger/8.0.47"
            )
        })
        try:
            page.goto(url, wait_until="networkidle", timeout=30000)
            # Wait for article body to appear
            try:
                page.wait_for_selector("#js_content", timeout=8000)
            except Exception:
                pass
            html = page.content()
        finally:
            context.close()

    return html


def do_login():
    """Open headed browser for manual WeChat login."""
    from playwright.sync_api import sync_playwright  # type: ignore

    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Opening browser with profile at: {PROFILE_DIR}")
    print("Navigate to https://mp.weixin.qq.com/ and log in.")
    print("Press Ctrl+C or close the browser when done.\n")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            str(PROFILE_DIR),
            headless=False,
        )
        page = context.new_page()
        page.goto("https://mp.weixin.qq.com/")
        print("Browser opened. Log in, then press Enter here to save and exit...")
        try:
            input()
        except KeyboardInterrupt:
            pass
        finally:
            context.close()

    print("Profile saved. Future runs will reuse this session.")


# ── HTML parsing ─────────────────────────────────────────────────────────────

def parse_wechat_html(html: str, source_url: str) -> dict:
    """Parse WeChat article HTML → structured content dict."""
    from bs4 import BeautifulSoup  # type: ignore
    import re

    soup = BeautifulSoup(html, "html.parser")

    # Title
    title = ""
    title_el = (
        soup.select_one("h1.rich_media_title") or
        soup.select_one("#activity-name") or
        soup.find("meta", property="og:title")
    )
    if title_el:
        if title_el.name == "meta":
            title = title_el.get("content", "")
        else:
            title = title_el.get_text(strip=True)

    if not title:
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.get_text(strip=True)

    # Author (公众号 name)
    author = ""
    author_el = (
        soup.select_one("#js_name") or
        soup.select_one("span.rich_media_meta_text") or
        soup.find("meta", attrs={"name": "author"})
    )
    if author_el:
        if author_el.name == "meta":
            author = author_el.get("content", "")
        else:
            author = author_el.get_text(strip=True)

    # Publish date
    publish_date = ""
    date_el = soup.select_one("#publish_time") or soup.select_one("em#publish_time")
    if date_el:
        publish_date = date_el.get_text(strip=True)

    if not publish_date:
        # Try script tags for publish time
        for script in soup.find_all("script"):
            m = re.search(r'var\s+ct\s*=\s*"(\d+)"', script.string or "")
            if m:
                import datetime
                ts = int(m.group(1))
                publish_date = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
                break

    # Article body: primary selector #js_content, fallback .rich_media_content
    body_el = soup.select_one("#js_content") or soup.select_one(".rich_media_content")

    raw_text = ""
    image_urls: list[str] = []

    if body_el:
        # Extract images before stripping HTML
        for img in body_el.find_all("img"):
            # WeChat uses data-src for lazy loading
            src = img.get("data-src") or img.get("src") or ""
            if src and src.startswith("http") and "mmbiz.qpic.cn" in src:
                image_urls.append(src)

        # Get clean text
        raw_text = body_el.get_text(separator="\n", strip=True)
        # Collapse excessive blank lines
        raw_text = re.sub(r"\n{3,}", "\n\n", raw_text)
    else:
        # Fallback: get all text from page body
        raw_text = soup.get_text(separator="\n", strip=True)
        raw_text = re.sub(r"\n{3,}", "\n\n", raw_text)[:10000]

    return {
        "title": title,
        "author": author,
        "publish_date": publish_date,
        "raw_text": raw_text,
        "image_urls": image_urls,
    }


def download_images(image_urls: list[str], images_dir: Path) -> list[str]:
    """Download WeChat images. Returns saved paths."""
    import requests  # type: ignore

    saved = []
    headers = {
        "Referer": "https://mp.weixin.qq.com/",
        "User-Agent": (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 "
            "MicroMessenger/8.0.47"
        ),
    }
    for url in image_urls[:15]:
        try:
            resp = requests.get(url, headers=headers, timeout=15, stream=True)
            if resp.status_code == 200:
                content_type = resp.headers.get("content-type", "image/jpeg")
                ext = "jpg"
                if "png" in content_type:
                    ext = "png"
                elif "gif" in content_type:
                    ext = "gif"
                elif "webp" in content_type:
                    ext = "webp"
                fname = hashlib.sha1(url.encode()).hexdigest()[:12] + "." + ext
                dest = images_dir / fname
                with open(dest, "wb") as f:
                    for chunk in resp.iter_content(8192):
                        f.write(chunk)
                saved.append(str(dest))
        except Exception:
            pass
    return saved


# ── Main ─────────────────────────────────────────────────────────────────────

def extract_wechat(source: str) -> dict:
    """
    Extract WeChat article.
    source: WeChat URL or path to saved .html/.txt file.
    """
    is_url = source.startswith(WECHAT_URL_PREFIX)
    source_path = Path(source) if not is_url else None

    html = None

    if is_url:
        # Check cache first
        cached = cache_path(source)
        if cached.exists():
            print(f"[extract-wechat] Using cached HTML: {cached}", file=sys.stderr)
            html = cached.read_text(encoding="utf-8", errors="replace")
        else:
            print(f"[extract-wechat] Fetching: {source}", file=sys.stderr)
            html = fetch_with_playwright(source)
            # Cache immediately
            cached.write_text(html, encoding="utf-8")
            print(f"[extract-wechat] Cached to: {cached}", file=sys.stderr)

    elif source_path and source_path.exists():
        suffix = source_path.suffix.lower()
        if suffix in (".html", ".htm"):
            html = source_path.read_text(encoding="utf-8", errors="replace")
            # Use filename-based URL stub for metadata
            source = f"file://{source_path}"
        elif suffix == ".txt":
            # Plain text fallback — no HTML parsing possible
            raw_text = source_path.read_text(encoding="utf-8", errors="replace")
            lang = detect_language(raw_text)
            url_hash = hashlib.sha1(str(source_path).encode()).hexdigest()[:8]
            images_dir = Path(tempfile.gettempdir()) / f"ingest-images-{url_hash}"
            images_dir.mkdir(exist_ok=True)
            return {
                "raw_text": raw_text,
                "title": source_path.stem,
                "author": "",
                "publish_date": "",
                "images_dir": str(images_dir),
                "language_hint": lang,
                "source_metadata": {
                    "source_type": "wechat",
                    "original_url_or_path": str(source_path),
                    "author": "",
                    "language": lang,
                    "images_dir": str(images_dir),
                },
            }
        else:
            raise ValueError(f"Unsupported file type: {source_path.suffix}")
    else:
        raise ValueError(
            f"Source must be a WeChat URL (https://mp.weixin.qq.com/...) "
            f"or a path to a saved .html/.txt file. Got: {source!r}"
        )

    # Parse HTML
    parsed = parse_wechat_html(html, source)

    # Download images
    url_hash = hashlib.sha1(source.encode()).hexdigest()[:8]
    images_dir = Path(tempfile.gettempdir()) / f"ingest-images-{url_hash}"
    images_dir.mkdir(exist_ok=True)
    saved_images = download_images(parsed["image_urls"], images_dir)
    print(f"[extract-wechat] Downloaded {len(saved_images)} images", file=sys.stderr)

    lang = detect_language(parsed["raw_text"])

    return {
        "raw_text": parsed["raw_text"],
        "title": parsed["title"],
        "author": parsed["author"],
        "publish_date": parsed["publish_date"],
        "images_dir": str(images_dir),
        "language_hint": lang,
        "source_metadata": {
            "source_type": "wechat",
            "original_url_or_path": source,
            "author": parsed["author"],
            "language": lang,
            "images_dir": str(images_dir),
        },
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Extract WeChat 公众号 article")
    parser.add_argument("source", nargs="?", help="WeChat URL or saved HTML/text file path")
    parser.add_argument("--login", action="store_true",
                        help="Open headed browser for first-run login")
    args = parser.parse_args()

    if args.login:
        do_login()
        return

    if not args.source:
        parser.error("Provide a WeChat URL or file path, or use --login")

    result = extract_wechat(args.source)
    preview = dict(result)
    if len(preview.get("raw_text", "")) > 500:
        preview["raw_text"] = preview["raw_text"][:500] + f"\n... [{len(result['raw_text'])} chars total]"
    print(json.dumps(preview, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
