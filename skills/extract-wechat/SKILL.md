# extract-wechat

Owned by: `ingest-extractor`

Fetches WeChat 公众号 articles via Playwright with a persistent browser profile. Links expire — caches HTML immediately on first fetch.

## ⚠️ Fragility warning

WeChat changes its DOM structure regularly. This skill requires periodic maintenance when extraction breaks. Check the `## Known issues` section below before debugging.

## Invocation

```bash
cd skills
# From a live URL:
uv run --with playwright --with requests \
  python extract-wechat/extract_wechat.py "https://mp.weixin.qq.com/s/..."

# From a saved HTML/text file (manual-paste fallback):
uv run --with playwright --with requests \
  python extract-wechat/extract_wechat.py /path/to/saved.html
```

## First-run login

On first use, run with `--login` to open the browser and log in manually:
```bash
uv run --with playwright python extract-wechat/extract_wechat.py --login
```
The persistent profile is stored at `~/.openclaw/playwright-profile/`.

## HTML caching

On successful fetch, raw HTML is cached to `~/.openclaw/wechat-cache/<sha1-of-url>.html` immediately. WeChat article links expire (typically 48–72h). Cached HTML is permanent.

## Output

```json
{
  "raw_text": "...",
  "title": "...",
  "author": "<公众号 name>",
  "publish_date": "2026-01-01",
  "images_dir": "/tmp/ingest-images-<hash>/",
  "language_hint": "zh",
  "source_metadata": {
    "source_type": "wechat",
    "original_url_or_path": "...",
    "author": "...",
    "language": "zh",
    "images_dir": "..."
  }
}
```

## Manual-paste fallback

If the URL has expired or Playwright fails:
1. Open the article in any browser
2. Save the page as HTML (`File → Save Page As → Web Page, Complete`)
3. Pass the `.html` file path to the script instead of a URL

## Known issues

- WeChat occasionally requires re-login. If extraction fails with "not logged in", run `--login`.
- DOM selectors for article body: `#js_content` (primary), `.rich_media_content` (fallback)

## Status

Built. `extract_wechat.py` live.
