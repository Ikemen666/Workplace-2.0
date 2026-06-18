---
name: feishu-minutes
description: |
  Fetch Feishu meeting transcripts (minutes) using a minute_token. 
  Activate when user mentions meeting minutes, transcripts, or provides a minutes link/token.
---

# Feishu Minutes Tool

Fetch transcripts from Feishu meetings using the `minute_token`.

## Required credentials (bring your own)

This skill calls the **Feishu (Lark) Open Platform API**. It ships with **no credentials** —
you must supply your own:

| Variable | Where to get it |
|---|---|
| `FEISHU_APP_ID` | Create a self-built app at https://open.feishu.cn/app |
| `FEISHU_APP_SECRET` | Same app → Credentials & Basic Info |

Grant the app the `minutes:minutes:readonly` scope. Then either export the two env vars,
or pass them as the 2nd/3rd CLI args. The script refuses to run without them.

```bash
export FEISHU_APP_ID=cli_your_own_app_id
export FEISHU_APP_SECRET=your_own_app_secret
```

## Token Extraction

From URL `https://xxx.feishu.cn/minutes/abcd1234efgh5678` → `minute_token` = `abcd1234efgh5678`

## Usage

### Fetch Transcript

To fetch the full transcript of a meeting:

```bash
python3 scripts/fetch_feishu_minutes_tool.py <minute_token>
```

Returns a JSON object containing the transcript content.

## Pitfalls & Error Handling

### 403 Forbidden Error
If the `fetch_feishu_minutes_tool.py` script returns a `403 Client Error: Forbidden`, it means the agent does not have permission to access the Feishu document. This is common for non-public or restricted links.

**Corrective Action:**
1. Do not retry fetching.
2. Inform the user clearly that you cannot access the link due to a permission error.
3. Use the `clarify` tool to ask the user how they would like to proceed, offering alternatives like providing the transcript as a file path or by pasting the text directly.

## Output Structure & Parsing Pitfall
⚠️ **Data Shape Pitfall**: The output JSON typically structures the full text as a single large string under `data['data']['transcript']`, with timestamps and speakers embedded directly in the text. **It is NOT a list of speaker dictionaries**. 
When processing the output, extract it as a flat string:
```python
import json
with open('/tmp/transcript_raw.json', 'r') as f:
    data = json.load(f)
transcript_text = data['data']['transcript'] # This is a single string
```

## Recommended Workflow

1. **Fetch:** Use the script above and redirect to a file (e.g., `> /tmp/transcript_raw.json`) to prevent stdout truncation on long meetings.
2. **Extract:** Use `execute_code` to parse the JSON and write the raw string to a text file (e.g., `/tmp/transcript_text.txt`). This is a crucial step to avoid feeding raw JSON (with unicode escapes) to downstream tools.

   ```python
   # Recommended execute_code snippet for extraction
   import json
   import os

   raw_json_path = '/tmp/transcript_raw.json' # Path from Step 1
   text_output_path = '/tmp/transcript_text.txt'
   
   transcript_text = ''
   if os.path.exists(raw_json_path):
       with open(raw_json_path, 'r', encoding='utf-8') as f:
           try:
               data = json.load(f)
               transcript_text = data.get('data', {}).get('transcript', '')
           except json.JSONDecodeError:
               # Handle case where JSON is malformed
               pass

   with open(text_output_path, 'w', encoding='utf-8') as text_file:
       text_file.write(transcript_text)

   print(f"Transcript text extracted and saved to {text_output_path}")
   ```

3. **Read:** Use the `read_file` tool to read the `.txt` file into context. (Do NOT use `cat` in the terminal, as it violates system directives and can still truncate long texts).
4. **Process:** Once you have the raw text, the next step depends on the user's goal:
   - To **clean the transcript** into a faithful, RAG-ready version (removing filler words, fixing ASR errors), use the `transcript-correct` skill. This is a common and highly recommended next step.
   - To **generate meeting minutes** or a summary, delegate to the `minute-creator` skill or perform the summarization as requested.
