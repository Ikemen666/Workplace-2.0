# extract-pdf

> ⚙️ **Setup (bring your own keys):** part of the ingest pipeline — needs API keys + the shared `_lib`. See [`../_lib/README.md`](../_lib/README.md): copy `ingest-config.template.json` to `~/.openclaw/ingest-config.json` and fill in your own keys.

Owned by: `ingest-extractor`

Extracts text, tables, and metadata from PDF files. Detects scanned PDFs and falls back to vision.

## Invocation

```bash
cd skills
uv run --with pypdf --with pdfplumber --with "google-genai>=1.0" --with requests \
  python extract-pdf/extract_pdf.py /path/to/file.pdf
```

## Output

```json
{
  "raw_text": "...",
  "page_count": 12,
  "tables": [{"page": 2, "data": [["col1", "col2"], ["val1", "val2"]]}],
  "images_dir": "/tmp/ingest-images-<hash>/",
  "metadata": {"title": "...", "author": "...", "subject": "..."},
  "language_hint": "en|zh|...",
  "source_metadata": {
    "source_type": "pdf",
    "original_url_or_path": "...",
    "page_count": 12,
    "author": "...",
    "language": "...",
    "images_dir": "..."
  }
}
```

## Scanned PDF detection

If average extracted text per page < 100 characters, the PDF is likely scanned. Falls back to `pdf_vision` task via `llm_router.py` (Gemini Flash) to describe each page.
