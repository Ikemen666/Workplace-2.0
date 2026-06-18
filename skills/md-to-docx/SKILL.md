---
name: md-to-docx
description: |
  Convert a Markdown file to a styled Word .docx using pandoc + a pre-built
  reference doc. Activate whenever the user asks for a `.docx` output from
  markdown — briefings, memos, reports, research docs, anything that isn't
  a meeting minute. For meeting minutes from a Feishu transcript, use the
  `minute-creator` skill instead.
metadata:
  origin: claude-code/2026-05-19
  authoritative-tool: pandoc 3.x
  reference-doc: assets/reference.docx
---

# md-to-docx — General Markdown → Word converter

**This is the default tool for producing a `.docx` from any markdown source.**
Use it whenever the user wants Word output from a `.md` file — research briefings,
memos, reports, longform writing, summaries.

Output characteristics:

- Aptos Display 12pt body, line spacing 1.0, pure black
- Title (16pt centered) → Subtitle → Author → Date → Heading 1 (14pt) →
  Heading 2 (13pt) → Heading 3 (12pt) hierarchy
- Native Word bullets via `numPr` (clean small `•` markers with proper indents) —
  NOT giant `●` characters typed into body text
- Real Word footnotes (page-bottom) from `[^N]` markdown footnote refs
- Markdown tables → real Word tables with bold headers
- Block quotes (`> ...`) → Block Text style (italic, indented)

## When to use this skill vs. other docx-producing skills

| Source                          | Output                          | Use which skill              |
|---------------------------------|---------------------------------|------------------------------|
| Any `.md` file                  | Word `.docx`                    | **md-to-docx** (this skill)  |
| Feishu meeting transcript       | Strict-format meeting memo      | `minute-creator`             |
| Raw notes / chat / freeform     | Word `.docx`                    | Write to `.md` first, then md-to-docx |

If in doubt: this skill. The only specialized alternative is `minute-creator`,
which exists because meeting minutes have a non-negotiable house format and
content-rigor SOP that pandoc can't enforce.

## How to invoke

```bash
~/.hermes/skills/openclaw-imports/md-to-docx/scripts/convert.sh \
    <input.md> \
    [output.docx]
```

If `output.docx` is omitted, defaults to `<input>.docx` next to the source.

## Title / metadata block (optional, auto-detected)

If the markdown starts with this pattern:

```markdown
# Document Title Here
**Date:** May 19, 2026
**Prepared by:** Someone
**Subtitle:** Optional second-line tagline

---

Body starts here...
```

…the script lifts the title and metadata into Word's `Title` / `Subtitle` /
`Author` / `Date` styles automatically.

Recognized metadata keys (case-insensitive, after the `# Title` line, before the
first `---`): `Date`, `Author`, `Prepared by`, `By`, `Subtitle`, `Tagline`. A
bare `**Confidential ...**` line is also treated as a subtitle.

If no `---` separator is present after the title, the metadata block ends at
the first line that isn't a `**Key:** value` pair or blank.

If line 1 is not a `# Title`, the entire file is fed to pandoc unchanged.

## Why pandoc, not python-docx, not plain `pandoc x.md -o x.docx`

Three lessons learned from prior failures (Hermes hit all three before this
skill existed):

1. **`---` as a horizontal rule trips pandoc's YAML metadata parser.** The
   default markdown reader sees the second `---` as the close of a YAML
   frontmatter block and errors with *"mapping values are not allowed in this
   context"*. Fix: use `--from=gfm` (this skill's default) or
   `--from=markdown-yaml_metadata_block`.

2. **`--from=markdown` mangles pipe tables next to headings.** A 5-column
   comparison table got rendered as a 1-column 6-row "table" containing the
   heading text. `--from=gfm` parses pipe tables and nested-list structures
   robustly.

3. **No `--reference-doc` → ugly defaults.** Without a reference, you get
   Calibri 11pt, oversized Word default headings, and loose bullet spacing.
   The bundled `assets/reference.docx` overrides Normal, Title, Subtitle,
   Heading 1–6, Body Text, First Paragraph, Compact, Block Text, Footnote
   Text, and Caption to a tight readable house style.

## Inline-formatting cheatsheet for source markdown

What pandoc + this reference doc handles cleanly:

- `**bold**` → bold run
- `*italic*` → italic run
- `` `code` `` → inline code (monospace, from pandoc default)
- `[^1]`, `[^2]` … with `[^1]: text` definitions → real Word footnotes
- `> quoted text` → Block Text style (italic, indented)
- `| a | b |` pipe tables → Word tables with bold headers
- `*  item` or `- item` bullets → native Word bullets (numPr)
- `1.  item` ordered lists → native Word numbering
- `---` → horizontal rule (outside the title metadata block)

What will NOT render well — fix in the source before converting:

- Mixed bullet markers (`*` and `-` in the same list) — pick one
- Headings deeper than `####` (H4) — flatten or refactor
- HTML embedded in markdown (`<u>...</u>`) — pandoc passes through but
  inconsistently styles it; use bold/italic instead
- A `**1. Heading**` line followed by `*  sub-bullets` — pandoc 3.x with
  `gfm` handles this; the plain `markdown` reader does not. Always
  `--from=gfm`.

## Reference doc — when to rebuild

The bundled `assets/reference.docx` is pre-built. Rebuild only when:

- pandoc is upgraded and its default reference.docx shape changes
- The house style needs to change (font, sizes, line spacing, bullet rhythm)

```bash
/usr/bin/python3 ~/.hermes/skills/openclaw-imports/md-to-docx/scripts/build_reference.py
```

The build script fetches pandoc's default via
`pandoc --print-default-data-file=reference.docx`, mutates the style
definitions via python-docx, and writes back to `assets/reference.docx`.

To customize the house style: edit the constants and `tune()` calls in
`scripts/build_reference.py`, then rerun.

## File layout

```
~/.hermes/skills/openclaw-imports/md-to-docx/
├── SKILL.md                       ← this file
├── assets/
│   └── reference.docx             ← pre-built pandoc reference, house-styled
└── scripts/
    ├── build_reference.py         ← regenerate reference from pandoc default
    └── convert.sh                 ← main entry point (markdown → docx)
```

## Quick smoke test

```bash
~/.hermes/skills/openclaw-imports/md-to-docx/scripts/convert.sh \
    ~/Desktop/some_file.md
# → ~/Desktop/some_file.docx
```

The script prints `✅  Saved: <path>` on success.
