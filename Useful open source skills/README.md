# Useful open source skills

⚠️ **These skills were NOT written by me ([@Ikemen666](https://github.com/Ikemen666)).**

They are third-party / community skills that I found useful and bundled here **only so my
teammates can grab everything in one clone**. All original authorship and licensing stays with
the upstream authors. If you build on these, credit the original source, not me.

| Skill | Source | Notes |
|---|---|---|
| `agent-reach` | upstream product (multi-platform research router) | Used as a dependency by some of *my* analysis skills (e.g. `hv-analysis`). Needs its own setup / keys. |
| `ppt-creator` | [clawhub.ai](https://clawhub.ai) registry (`ppt-creator`) | Uses the third-party yoo-ai / yoojober PPT API. Copy `config.json.template` → `config.json` and add **your own** key. |
| `ppt-workflow` | [clawhub.ai](https://clawhub.ai) registry (`ppt-workflow`) | Ships under its own MIT license. |
| `spotify-player` | [clawhub.ai](https://clawhub.ai) registry (`spotify-player`) | Terminal Spotify wrapper. |
| `pua` | community skill (MIT) | "Don't let your AI slack off." Anti–giving-up prompt. |

The `.clawhub/origin.json` inside each folder records the exact upstream slug/version it was
installed from.

> My own original skills are in the top-level [`../skills/`](../skills) folder and are covered by
> the repo's MIT license with my attribution.
