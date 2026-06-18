# gap-fill

> ⚙️ **Setup (bring your own keys):** part of the ingest pipeline — needs API keys + the shared `_lib`. See [`../_lib/README.md`](../_lib/README.md): copy `ingest-config.template.json` to `~/.openclaw/ingest-config.json` and fill in your own keys.

Owned by: `ingest-researcher`

Fills knowledge gaps using bounded Tavily searches. Hard-capped at the configured budget.

## Invocation

```bash
cd skills
echo '<enriched_json>' | uv run --with tavily-python --with requests python gap-fill/gap_fill.py
# or:
uv run --with tavily-python --with requests python gap-fill/gap_fill.py input.json
```

## Input

The full distilled JSON from `ingest-distiller`, including `knowledge_gaps` array.

## Output

Same JSON with `enriched_context` field added:

```json
{
  ...all original fields...,
  "enriched_context": [
    {
      "term": "<term or question from knowledge_gaps>",
      "context": "<1–2 sentences of synthesized context>",
      "source_url": "<URL of most relevant Tavily result>"
    }
  ]
}
```

If `knowledge_gaps` is empty, returns input JSON unchanged with `enriched_context: []`.

## Constraints

- Hard cap: never exceed `gap_fill.budget` from `ingest-config.json`
- One Tavily search per gap
- Omit a gap if Tavily returns nothing useful — never hallucinate
- `search_depth: "basic"`, `max_results: 3` per search
