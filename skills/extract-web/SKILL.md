# extract-web

Owned by: `ingest-extractor`

Extracts clean article content from web URLs using trafilatura.

## Invocation

```bash
cd skills
uv run --with trafilatura --with requests \
  python extract-web/extract_web.py "https://example.com/article"
```

## Output

```json
{
  "raw_text": "...",
  "title": "...",
  "author": "...",
  "publish_date": "2026-01-01",
  "canonical_url": "https://...",
  "site_name": "...",
  "images_dir": "/tmp/ingest-images-<hash>/",
  "language_hint": "en|zh|...",
  "source_metadata": {
    "source_type": "web",
    "original_url_or_path": "...",
    "author": "...",
    "language": "...",
    "images_dir": "..."
  }
}
```
