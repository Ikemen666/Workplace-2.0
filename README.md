# Workplace 2.0

A collection of agent **skills** I ([Wesley · @Ikemen666](https://github.com/Ikemen666)) built
for real consulting / research / meeting work, shared so my teammates can use them too.

> 本着「中国人 = open source」的精神 🙂 — these are mine, they're MIT-licensed, and you're
> welcome to use them. Just keep the attribution.

## License & attribution

Everything under [`skills/`](skills) is **© 2026 Wesley (@Ikemen666), MIT licensed** — free to
use/modify/share, but **keep the credit** (see [`LICENSE`](LICENSE)). The
[`Useful open source skills/`](Useful%20open%20source%20skills) folder is *not* mine — it bundles
third-party skills with their own authors/licenses; see that folder's README.

## What's a "skill"?

A skill is a folder with a `SKILL.md` (instructions an AI agent loads on demand) plus any helper
scripts/data. They work with Claude Code / Claude agents and most skill-aware harnesses. To use
one, drop its folder into your agent's skills directory (e.g. `~/.claude/skills/`) — **the people
who can figure out GitHub can figure out the rest.** 😉

## Repo layout

```
skills/                       ← my original skills (MIT, credit me)
  _lib/                       ← shared runtime for the ingest-pipeline skills (+ config template)
Useful open source skills/    ← third-party skills, credited to their authors
```

## My skills

**Consulting / research / analysis** (prompt-driven; do their web research via Tavily/Exa MCP or
the bundled `agent-reach` — see "Bring your own keys"):
- `competitive-analysis` · `comps-analysis` · `hv-analysis` · `sector-overview`
- _Note: `hv-analysis` implements the 横纵分析法 method by **数字生命卡兹克 (Khazix)** — methodology credited to its originator; the skill implementation is mine. See its SKILL.md._
- `operational-practice-mapping`

**Documents & meetings:**
- `minute-creator` — MBB-grade meeting minutes (.docx)
- `transcript-correct` — clean a raw ASR transcript into a faithful, RAG-ready 逐字稿
- `feishu-minutes` — fetch a Feishu (Lark) meeting transcript by token
- `md-to-docx` — Markdown → Word (.docx)

**Ingest pipeline** (extract → distill → research → vault; share `_lib` + one config):
- `extract-pdf` · `extract-web` · `extract-wechat` · `extract-xlsx` · `extract-video`
- `distill` · `gap-fill`

## ⚠️ Bring your own API keys (no free ride 🙃)

**None of these ship with my keys.** Every skill that touches a paid/free API expects *your own*.
Even where the API is free, get your own — don't ride my effort.

| If you use… | You need to configure |
|---|---|
| `feishu-minutes` (or `minute-creator`, which depends on it) | Your **own Feishu self-built app** → `FEISHU_APP_ID` / `FEISHU_APP_SECRET`. See its SKILL.md. |
| The ingest pipeline (`extract-pdf/xlsx/video`, `gap-fill`, `distill`) | Copy [`skills/_lib/ingest-config.template.json`](skills/_lib/ingest-config.template.json) → `~/.openclaw/ingest-config.json` and add your DeepSeek / Gemini / Moonshot / DashScope / Tavily keys. See [`skills/_lib/README.md`](skills/_lib/README.md). |
| The analysis skills' "robust search" | Your **own Tavily / Exa** (via their MCP servers) and/or the `agent-reach` skill, configured with your keys. |

## Dependencies between skills

- `minute-creator` and `transcript-correct` use `feishu-minutes` to fetch the raw transcript.
- `hv-analysis`, `comps-analysis` and similar lean on `agent-reach` + Tavily/Exa for research —
  set those up first or the research steps will come up empty.
