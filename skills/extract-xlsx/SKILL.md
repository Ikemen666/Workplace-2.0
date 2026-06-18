# extract-xlsx

> ⚙️ **Setup (bring your own keys):** part of the ingest pipeline — needs API keys + the shared `_lib`. See [`../_lib/README.md`](../_lib/README.md): copy `ingest-config.template.json` to `~/.openclaw/ingest-config.json` and fill in your own keys.

Owned by: `ingest-extractor`

Characterizes Excel workbooks — does NOT dump all rows. Produces a structural summary and a DeepSeek-powered narrative.

## Invocation

```bash
cd skills
uv run --with openpyxl --with pandas --with openai --with requests \
  python extract-xlsx/extract_xlsx.py /path/to/file.xlsx
```

## Output

```json
{
  "sheets": [
    {
      "name": "Sheet1",
      "row_count": 1500,
      "columns": ["Date", "Revenue", "Region"],
      "numeric_stats": {"Revenue": {"min": 0, "max": 9999, "mean": 412.3}},
      "sample_rows": [["2026-01-01", 500, "APAC"]],
      "named_ranges": [],
      "notable_formulas": ["=SUM(B2:B100)"]
    }
  ],
  "structured_summary": "...",
  "narrative_summary": "<DeepSeek narration of what this workbook is about>",
  "metadata": {"filename": "...", "sheet_count": 1},
  "source_metadata": {...}
}
```

## Status

Built. `extract_xlsx.py` live.
