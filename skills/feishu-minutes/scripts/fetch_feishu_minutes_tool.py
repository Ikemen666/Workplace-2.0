import requests
import json
import os
import sys

# Fetch Feishu Minutes tool script
def get_tenant_access_token(app_id, app_secret):
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {"app_id": app_id, "app_secret": app_secret}
    headers = {"Content-Type": "application/json; charset=utf-8"}
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json().get("tenant_access_token")
    except Exception as e:
        print(f"Auth error: {e}", file=sys.stderr)
        return None

def get_minute_title(token, minute_token):
    """Fetch the 飞书妙记 title from the minutes info endpoint (transcript endpoint omits it)."""
    url = f"https://open.feishu.cn/open-apis/minutes/v1/minutes/{minute_token}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        return r.json().get("data", {}).get("minute", {}).get("title", "")
    except Exception as e:
        print(f"Title fetch error: {e}", file=sys.stderr)
        return ""


def get_minutes_transcript(token, minute_token):
    url = f"https://open.feishu.cn/open-apis/minutes/v1/minutes/{minute_token}/transcript"
    params = {
        "file_format": "txt",
        "need_speaker": "true",
        "need_timestamp": "true"
    }
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers, params=params, timeout=20)
        response.raise_for_status()
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            return response.json()
        else:
            # txt format returns plain text directly; force UTF-8 decode
            # (requests defaults to ISO-8859-1 for text/plain with no charset)
            transcript_text = response.content.decode('utf-8')
            return {"data": {"transcript": transcript_text}}
    except Exception as e:
        print(f"Transcript Fetch Error: {e}", file=sys.stderr)
        return {"error": str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 fetch_feishu_minutes_tool.py <minute_token> [app_id] [app_secret]")
        sys.exit(1)

    MINUTE_TOKEN = sys.argv[1]
    # Credentials come from CLI args or environment variables — NEVER hardcode them.
    # Create your own Feishu (Lark) self-built app and use ITS App ID / App Secret:
    #   https://open.feishu.cn/app  →  scopes: minutes:minutes:readonly
    APP_ID = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("FEISHU_APP_ID", "")
    APP_SECRET = sys.argv[3] if len(sys.argv) > 3 else os.environ.get("FEISHU_APP_SECRET", "")
    if not APP_ID or not APP_SECRET:
        print(
            "ERROR: missing Feishu credentials.\n"
            "Provide your own app credentials one of two ways:\n"
            "  1) export FEISHU_APP_ID=... ; export FEISHU_APP_SECRET=...\n"
            "  2) python3 fetch_feishu_minutes_tool.py <minute_token> <app_id> <app_secret>\n"
            "Get them by creating a self-built app at https://open.feishu.cn/app",
            file=sys.stderr,
        )
        sys.exit(1)

    token = get_tenant_access_token(APP_ID, APP_SECRET)
    if token:
        result = get_minutes_transcript(token, MINUTE_TOKEN)
        # include the title so downstream can name the output file after it
        if isinstance(result, dict) and "error" not in result:
            result.setdefault("data", {})["title"] = get_minute_title(token, MINUTE_TOKEN)
        print(json.dumps(result, ensure_ascii=True, indent=2))
    else:
        print(json.dumps({"error": "Authentication failed"}, ensure_ascii=True))
        sys.exit(1)
