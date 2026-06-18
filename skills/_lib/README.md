# `_lib` — shared runtime for the *ingest pipeline* skills

These skills are **not standalone** — they are components of one ingest pipeline and share
this folder:

- **`llm_router.py`** — routes each pipeline step to a model/provider. Every dependent script
  adds this folder to `sys.path` automatically (`Path(__file__).parent.parent / "_lib"`), so
  as long as the skill stays inside `skills/` next to `_lib/`, imports just work.
- **`ingest-config.template.json`** — the config schema.

Skills that depend on `_lib` + config:
`extract-pdf`, `extract-xlsx`, `extract-video`, `gap-fill`, `distill`.

> `extract-web` and `extract-wechat` do **not** use `_lib` — they only extract content and need
> no API keys (just their pip deps: `trafilatura`; `playwright` + `beautifulsoup4`).

## Setup — bring your own API keys

1. Copy the template to the path the skills read from:
   ```bash
   cp skills/_lib/ingest-config.template.json ~/.openclaw/ingest-config.json
   ```
2. Open `~/.openclaw/ingest-config.json` and fill in **your own** keys under `api_keys`:

   | Key | Provider | Used by |
   |---|---|---|
   | `DEEPSEEK_API_KEY` | DeepSeek | classify / xlsx narrate / dedupe |
   | `GEMINI_API_KEY` | Google AI Studio | pdf vision / distill / keyframe / gap synthesis |
   | `MOONSHOT_API_KEY` | Moonshot (Kimi) | long-doc distill |
   | `DASHSCOPE_API_KEY` | Alibaba DashScope | Chinese ASR (video) |
   | `TAVILY_API_KEY` | Tavily | gap-fill web search |

   You only need the keys for the steps you actually run (e.g. just `GEMINI_API_KEY` for PDF).

3. **Never commit your filled-in `ingest-config.json`** — it holds live keys. It lives outside
   this repo (`~/.openclaw/`) by design, and the repo `.gitignore` also ignores it.

These skills ship with **zero credentials**. Get your own keys from each provider's console.
