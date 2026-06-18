#!/usr/bin/env bash
# Convert a Markdown file to .docx using pandoc with a styled reference doc.
#
# Usage:
#   convert.sh <input.md> [output.docx]
#
# If output.docx is omitted, defaults to <input>.docx in the same directory.
#
# The script:
# 1. Detects pandoc + the bundled reference.docx (rebuilds it on first use if missing)
# 2. Optionally splits off a `# Title` line plus a metadata block of the form
#       **Date:** ...
#       **Prepared by:** ...           (or **Author:**)
#       **Subtitle:** ...              (or **Confidential ...**)
#    so they render via Word's Title / Subtitle / Author / Date styles
#    instead of as another H1. Body content starts after the first `---`
#    horizontal rule (if present) or line 2 otherwise.
# 3. Runs pandoc with --from=gfm and the styled reference doc.
#
# Why these flags:
# - --from=gfm : GitHub-Flavored Markdown. Handles pipe tables and nested lists
#                cleanly. The default `markdown` reader mangles tables when ---
#                is used as a horizontal rule and confuses nested list structures.
# - --reference-doc=<reference.docx> : applies the bundled house style
#                (Aptos Display 12pt, line spacing 1.0, heading hierarchy
#                14/13/12pt, tight bullets via the Compact style).

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <input.md> [output.docx]" >&2
  exit 1
fi

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
REFERENCE_DOCX="${SKILL_DIR}/assets/reference.docx"

INPUT="$1"
OUTPUT="${2:-${INPUT%.md}.docx}"

if [[ ! -f "$INPUT" ]]; then
  echo "ERROR: input not found: $INPUT" >&2
  exit 1
fi

if ! command -v pandoc &>/dev/null; then
  echo "ERROR: pandoc not on PATH. Install via 'brew install pandoc'." >&2
  exit 1
fi

# Rebuild reference.docx if missing (e.g., fresh checkout, after spec change)
if [[ ! -f "$REFERENCE_DOCX" ]]; then
  echo "Building reference.docx..."
  /usr/bin/python3 "${SCRIPT_DIR}/build_reference.py"
fi

# ── Extract title + metadata from the markdown head (best-effort) ─────────────
# Looks for:
#   line 1:  # Title text
#   then any **Key:** value lines until the first horizontal rule `---`.
#   Recognized keys (case-insensitive): date, author, prepared by, subtitle,
#   confidential (treated as subtitle).
# Anything else in the header becomes part of the body.
TMP_BODY="$(mktemp -t docx_body.XXXXXX.md)"
TMP_META="$(mktemp -t docx_meta.XXXXXX.sh)"
trap 'rm -f "$TMP_BODY" "$TMP_META"' EXIT

/usr/bin/python3 - "$INPUT" "$TMP_BODY" "$TMP_META" <<'PY'
import re
import sys

src_path, body_path, meta_path = sys.argv[1:4]
text = open(src_path, encoding='utf-8').read()
lines = text.split('\n')

title = ''
date = ''
author = ''
subtitle = ''
body_start = 0

if lines and lines[0].startswith('# '):
    title = lines[0][2:].strip()
    # Scan up to ~20 lines for **Key:** value metadata, stopping at first ---
    found_meta = False
    for i, line in enumerate(lines[1:25], start=1):
        if line.strip() == '---':
            body_start = i + 1
            break
        m = re.match(r'^\*\*([^*:]+):\*\*\s*(.*)$', line)
        if m:
            key = m.group(1).strip().lower()
            val = m.group(2).strip()
            if key == 'date':
                date = val
            elif key in ('author', 'prepared by', 'by'):
                author = val
            elif key in ('subtitle', 'tagline'):
                subtitle = val
            found_meta = True
            continue
        # Plain **Confidential ...** without a colon → treat as subtitle
        m = re.match(r'^\*\*(Confidential[^*]*)\*\*$', line)
        if m:
            subtitle = m.group(1).strip()
            found_meta = True
            continue
        # Blank line is OK between header lines
        if not line.strip():
            continue
        # Hit non-metadata content — if we've seen no metadata and no ---,
        # treat the rest of the file as body and don't strip the title.
        if not found_meta:
            title = ''  # don't lift the title — let pandoc render it as H1
            body_start = 0
        break

    if title and body_start == 0:
        # Title found and metadata seen but no --- separator — strip just the
        # header lines we consumed
        body_start = i + 1 if found_meta else 1

with open(body_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines[body_start:]))

def esc(s):
    return s.replace('"', '\\"')

with open(meta_path, 'w', encoding='utf-8') as f:
    f.write(f'TITLE="{esc(title)}"\n')
    f.write(f'SUBTITLE="{esc(subtitle)}"\n')
    f.write(f'AUTHOR="{esc(author)}"\n')
    f.write(f'DATE="{esc(date)}"\n')
PY

# shellcheck disable=SC1090
source "$TMP_META"

PANDOC_ARGS=(
  --from=gfm
  --to=docx
  --reference-doc="$REFERENCE_DOCX"
  -o "$OUTPUT"
)
[[ -n "${TITLE:-}" ]]    && PANDOC_ARGS+=(--metadata "title=${TITLE}")
[[ -n "${SUBTITLE:-}" ]] && PANDOC_ARGS+=(--metadata "subtitle=${SUBTITLE}")
[[ -n "${AUTHOR:-}" ]]   && PANDOC_ARGS+=(--metadata "author=${AUTHOR}")
[[ -n "${DATE:-}" ]]     && PANDOC_ARGS+=(--metadata "date=${DATE}")

if [[ -n "${TITLE:-}" ]]; then
  pandoc "$TMP_BODY" "${PANDOC_ARGS[@]}"
else
  pandoc "$INPUT" "${PANDOC_ARGS[@]}"
fi

echo "✅  Saved: $OUTPUT"
