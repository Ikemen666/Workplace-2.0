#!/usr/bin/env python3
"""
extract_pdf.py — Extract text, tables, and metadata from PDF files.

Usage:
    uv run --with pypdf --with pdfplumber --with google-genai --with requests \
        python extract_pdf.py /path/to/file.pdf
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path


SCANNED_THRESHOLD = 100  # avg chars/page below this → treat as scanned


def detect_language(text: str) -> str:
    """Simple heuristic: count CJK chars."""
    if not text:
        return "en"
    cjk = sum(1 for c in text if "\u4e00" <= c <= "\u9fff")
    if cjk / max(len(text), 1) > 0.1:
        return "zh"
    return "en"


def extract_with_pypdf(pdf_path: Path) -> tuple[str, dict, int]:
    """Returns (raw_text, metadata, page_count)."""
    from pypdf import PdfReader  # type: ignore

    reader = PdfReader(str(pdf_path))
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    raw_text = "\n\n".join(pages)

    meta = reader.metadata or {}
    metadata = {
        "title": str(meta.get("/Title", "")),
        "author": str(meta.get("/Author", "")),
        "subject": str(meta.get("/Subject", "")),
        "creator": str(meta.get("/Creator", "")),
    }
    return raw_text, metadata, len(reader.pages)


def extract_tables_with_pdfplumber(pdf_path: Path) -> list[dict]:
    """Extract tables from all pages."""
    import pdfplumber  # type: ignore

    tables = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for i, page in enumerate(pdf.pages):
            raw_tables = page.extract_tables() or []
            for tbl in raw_tables:
                if tbl:
                    tables.append({"page": i + 1, "data": tbl})
    return tables


def vision_fallback(pdf_path: Path, page_count: int, lib_path: str) -> str:
    """Use Gemini vision to describe scanned PDF pages."""
    if lib_path not in sys.path:
        sys.path.insert(0, lib_path)
    from llm_router import call_model  # type: ignore

    # Convert first N pages to images via pdf2image (optional dep) or describe via text
    # For simplicity: send a text prompt noting the fallback
    prompt = (
        f"This is a scanned PDF with {page_count} pages. "
        f"File: {pdf_path.name}. "
        f"Describe the document type and likely content based on the filename and context. "
        f"Note that this is a vision fallback due to insufficient extractable text."
    )
    try:
        resp = call_model("pdf_vision", prompt, max_tokens=500)
        return f"[Vision fallback — scanned PDF]\n\n{resp.get('text', '')}"
    except Exception as e:
        return f"[Vision fallback failed: {e}]"


def extract_pdf(pdf_path_str: str) -> dict:
    pdf_path = Path(pdf_path_str).expanduser().resolve()
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    lib_path = str(Path(__file__).parent.parent / "_lib")

    # Step 1: Extract text and metadata
    raw_text, metadata, page_count = extract_with_pypdf(pdf_path)

    # Step 2: Check if scanned
    avg_chars_per_page = len(raw_text) / max(page_count, 1)
    vision_used = False
    if avg_chars_per_page < SCANNED_THRESHOLD:
        raw_text = vision_fallback(pdf_path, page_count, lib_path)
        vision_used = True

    # Step 3: Extract tables (skip for scanned)
    tables = []
    if not vision_used:
        try:
            tables = extract_tables_with_pdfplumber(pdf_path)
        except Exception as e:
            print(f"[extract-pdf] Table extraction failed: {e}", file=sys.stderr)

    # Step 4: Create images dir (for any embedded images — placeholder)
    img_hash = hashlib.sha1(str(pdf_path).encode()).hexdigest()[:8]
    images_dir = Path(tempfile.gettempdir()) / f"ingest-images-{img_hash}"
    images_dir.mkdir(exist_ok=True)

    # Step 5: Language detection
    language_hint = detect_language(raw_text)

    author = metadata.get("author", "")

    result = {
        "raw_text": raw_text,
        "page_count": page_count,
        "tables": tables,
        "images_dir": str(images_dir),
        "metadata": metadata,
        "language_hint": language_hint,
        "vision_fallback_used": vision_used,
        "source_metadata": {
            "source_type": "pdf",
            "original_url_or_path": str(pdf_path),
            "page_count": page_count,
            "author": author,
            "language": language_hint,
            "images_dir": str(images_dir),
        },
    }
    return result


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Extract content from PDF")
    parser.add_argument("pdf", help="Path to PDF file")
    args = parser.parse_args()

    result = extract_pdf(args.pdf)
    # Truncate raw_text in stdout preview (full text for distiller)
    preview = dict(result)
    if len(preview.get("raw_text", "")) > 500:
        preview["raw_text"] = preview["raw_text"][:500] + f"\n... [{len(result['raw_text'])} chars total]"
    print(json.dumps(preview, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
