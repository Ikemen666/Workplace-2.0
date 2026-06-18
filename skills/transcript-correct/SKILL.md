---
name: transcript-correct
description: |
  Clean a raw, auto-generated meeting/voice transcript into a faithful, RAG-ready 逐字稿:
  remove 口癖/填充词, do light 顺句, and fix ASR errors in 人名/公司/术语 via a maintained
  glossary. Works on any rough transcript (飞书妙记 / Teams / Zoom / YouTube 字幕 …) that is
  already saved to a file. Activate when the user hands over a raw transcript and asks to
  纠错 / 清洗 / correct / smooth it, or wants a clean transcript to feed a RAG / search index.
  This skill ONLY cleans the transcript — it never summarizes, and produces no meeting minutes.
metadata:
  origin: "user-authored"
  created: "2026-06-02"
  glossary: "references/dicts/general.json"
---

# transcript-correct — 转写稿纠错 / 清洗(RAG 友好)

> 输入:一份**自动生成的粗转写稿文件**(任何来源:飞书妙记、Teams、Zoom、YouTube 字幕……)。
> 输出:一份**忠实、干净、可直接喂给 RAG**的逐字稿。
> 单一职责:**只清洗,不总结、不提炼、不出纪要。**

---

## 0. 边界(读这一段就够定调)

- 唯一交付物 = 一份**清洗后的逐字稿 `.docx`**(说话人/时间戳结构保留;脚本负责渲染)。
- **保真第一**:绝不删除信息、不合并发言、不改变任何事实/数字/决策。下游是 RAG,
  丢内容 = 检索丢命中。
- 清理力度 = **轻度顺句**:删口癖/填充词 + 把口语断句理顺成通顺句子,**仅此而已**。
  不重写句意、不书面化润色、不改说话风格。
- **不做总结/纪要**。若用户要会议纪要,那是另一个职责,不在本技能范围内 —— 本技能到
  「干净逐字稿」为止。

---

## 0. Prerequisites & Input Format

> ⚠️ **IMPORTANT**: This skill operates on a **plain UTF-8 text file**. The input file must not be a JSON, XML, or any other structured format.
>
> **Workflow Pitfall**: If you are getting a transcript from a tool like `feishu-minutes`, which outputs JSON, you **must first parse the JSON and extract the text content** into a separate `.txt` file. Feeding the raw JSON to this skill will result in garbled output (e.g., `\uXXXX` Unicode escapes).
>
> See the `feishu-minutes` skill for the correct Python code to extract the text before using this skill.

> **Handling `.docx` files**: If the input is a `.docx` file, it must be converted to plain text first. Use the `docx2txt` command, which is available in the environment:
> ```bash
> docx2txt /path/to/input.docx /path/to/output.txt
> ```

---

## 1. 工作流

> 前提:转写稿已是磁盘上的一个文本文件。若用户给的是某平台的链接,先各自用对应方式
> 导出为文本,再交给本技能 —— 导出不属于本技能职责。

### Step 1 — 确定性纠错 + 机械去口癖(脚本)

跑脚本:做**已知错→对**的机械替换,并(可选)**机械清口癖**。这是为长稿(30K+ 字)
设计的,把规模化的脏活交给脚本,LLM 只做需要判断的部分。

```bash
python3 scripts/correct_transcript.py \
  /path/to/raw_transcript.txt --strip-fillers -o /tmp/transcript_pass1.txt
```

> 🧭 **字典可分域,按会议路由 `--domain`**:字典是 `references/dicts/` 下的并行文件,
> **`general.json` 永远加载**(通用术语+口癖,对任何会议安全),`--domain <stem>` 再叠加你为某个
> 项目/客户自建的域字典:
> - **某个专项会议**(有大量该项目专属人名/术语/缩写)→ `--domain my-project`
> - **跨两个域的会** → `--domain my-project,another`
> - **任何无关会议 / 拿不准** → **不加 `--domain`**(只 general,绝不会把某项目的专用词套上去)
>
> 为什么要路由:域字典常含「本身是英文常用词」的 key(例如把某个发音相近的常用词映射到一个专有名词),
> 只在该域语境里安全;套到无关稿会**过度纠错**。所以域字典只在确认是该项目的稿子时才加。
> 仓库自带一个示例域字典 `references/dicts/example-project.json` —— **复制它改成你自己的
> `<项目>.json`**,用 `--domain <项目>` 即用,无需改脚本。
> (`--glossary a.json,b.json` 可显式指定文件;`--no-replace` 彻底跳过所有替换。)

> 🤖 **AGENT:运行前先定 `--domain`(这是你的职责,用户不敲 CLI)**。按以下顺序决定:
> 1. **用户在 prompt 里指明了项目/客户** → 用对应的 `--domain <项目>`。
> 2. **没指明 → 从稿子内容推断**:出现某个已建域字典里的专属术语/人名信号 → 用那个域;
>    多个域信号都明显 → 多个都带(逗号分隔)。
> 3. **既无指明、内容也看不出属于哪个已建域** → **默认 general(不带 --domain)**。**绝不**在没有
>    证据时硬套某个域 —— 套错 = 过度纠错。拿不准且域影响大时,**直接问用户一句**是哪个项目。

`--strip-fillers` 只做**保守**清理(见 glossary `fillers`):去起首语气词(嗯/呃/啊/哦/诶/哎，)、
丢纯感叹词独句、折叠显式结巴对(对对对→对、短短信→短信、我我→我…)。**绝不**盲折叠重复字
(中文动词叠词 看看/想想/试试/慢慢 是有意义的,已在脚本中规避)。不加该 flag 则只做术语替换。

脚本输出 JSON 报告(替换/清理统计 + canonical 人名/公司/术语清单)。**记住这份 canonical
清单**,下一步用它吸附人名。

> ⚠️ **长稿铁律(血泪教训)**:若转写稿 >约 8000 字,**绝不要**让 LLM 一次性重写整篇 ——
> 单次输出会撞 token 上限(`finish_reason=length`),稿子只清一半就被截断,后半段静默丢失。
> 长稿必须走下面的 **Step 1.5 切块 + Step 2 并行清 + Step 2.5 合并**。短稿可跳过切块,直接 Step 2 整篇处理。

### Step 1.5 — 切块(脚本,长稿必走)

```bash
python3 scripts/correct_transcript.py \
  /path/to/raw.txt --strip-fillers --chunk-chars 6000 --chunk-dir /tmp/tc_chunks -o /tmp/pass1.txt
```

脚本会在**说话人边界**(绝不破句)把清洗后的文本切成 `chunk_001.txt … chunk_NNN.txt`
(每块约 `--chunk-chars` 字),报告里返回块清单。

> ⚠️ **防止两份稿串台(已修)**:`--chunk-dir` 默认是固定的 `/tmp/tc_chunks`。若同一环境先后处理
> 多份稿,旧稿残留的高编号 `chunk_NNN.clean.txt` 会被 `--merge` 的 glob 误拼进来,导致**两份转写稿混在一起**。
> 现在脚本已双重防护:① 切块前**自动清空**该目录里旧的 `chunk_*(.clean).txt`;② 合并时**只认有对应
> 源块的 clean 文件**,孤儿块会被忽略并在报告里 `ignored_orphan_clean_chunks` 报警。
> **最佳实践**:每份稿仍建议用**独立目录**(如 `--chunk-dir /tmp/tc_<token或标题>`),彻底杜绝并发/串台。

### Step 2 — 结构化清洗 (代码驱动，非 LLM)

> ⚠️ **核心陷阱: 不要使用 LLM Subagent**
> 
> 实践证明，将整个文件块委托给通用 LLM (如通过 `delegate_task`) 是**不可靠的**。LLM 有强烈的“清理”和“重新格式化”倾向，即使有非常严格的指令，也极有可能破坏时间戳和说话人标签等关键结构，导致转写稿信息丢失。**必须采用代码驱动的、逐行处理的确定性方法来保证结构完整性。**

推荐的工作流是使用 `execute_code` 工具运行以下 Python 脚本，它会循环处理所有 `chunk_NNN.txt` 文件，仅清洗对话行，并保持结构行不变。

```python
import os
import re
import glob

# NOTE: This is a minimal cleaning function. 
# For more complex rules, this function can be enhanced, 
# or a single dialogue line can be passed to an LLM if necessary.
def clean_dialogue(line):
    fillers = ["嗯", "呃", "啊", "哦", "诶", "哎"]
    for filler in fillers:
        line = line.replace(filler, "")
    line = re.sub(r'\\s+', ' ', line).strip()
    return line

chunk_dir = '/tmp/tc_chunks' # Or wherever the chunks were saved
chunk_files = sorted(glob.glob(os.path.join(chunk_dir, 'chunk_*.txt')))

for input_path in chunk_files:
    if input_path.endswith('.clean.txt'):
        continue

    output_path = input_path.replace('.txt', '.clean.txt')
    
    with open(input_path, 'r') as infile, open(output_path, 'w') as outfile:
        for line in infile:
            # Preserve structural lines (speaker, timestamp, blank lines)
            if re.match(r'^说话人 \d+|^\\d{2}:\\d{2}:\\d{2}|^\\s*$', line):
                outfile.write(line)
            else:
                cleaned_line = clean_dialogue(line)
                outfile.write(cleaned_line + '\\n')

print(f"Cleaned all {len(chunk_files)} chunks and saved to .clean.txt files in {chunk_dir}")
```

> **Step 2.1 — Verification (Crucial Pitfall)**: After running the cleaning script, **you must verify that the `.clean.txt` files were actually created**. The script might complete without errors but fail to produce output, causing the final merge step to fail.
>
> ```bash
> # Always run this check before merging:
> ls -l /tmp/tc_chunks/*.clean.txt
> ```
> If this command returns "No such file or directory", the previous step failed silently. Debug the script before proceeding. This simple check prevents a common and frustrating failure loop.

这个方法将结构控制权掌握在代码手中，确保了 100% 的格式保真度，同时只在需要的地方应用清洗逻辑。

### Step 2.5 — 提取标题 (若适用)

如果源文件来自飞书,最终的 `.docx` 文件名应使用会议标题。从第一步生成的原始 JSON 文件中提取标题。

```python
# Example using execute_code to extract and sanitize the title for use as a filename
import json
import os

raw_json_path = '/tmp/transcript_raw.json' # Path to raw JSON from the fetch step
default_title = 'corrected-transcript'
title = default_title

if os.path.exists(raw_json_path):
    with open(raw_json_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
            raw_title = data.get('data', {}).get('title', default_title)
            # Sanitize title to make it a valid filename by removing invalid characters
            sanitized_title = "".join([c for c in raw_title if c.isalnum() or c in (' ', '-', '_')]).rstrip()
            if sanitized_title: # Use sanitized title only if it's not empty after cleaning
                 title = sanitized_title
        except json.JSONDecodeError:
            # If JSON is malformed, fall back to the default title
            pass

print(title)
```

### Step 2.6 — 合并 + 出 docx(脚本,长稿必走)

各块清完后,按序拼回完整稿。**最终交付物是 `.docx`** —— `-o` 用 `.docx` 后缀,脚本自动渲染
(说话人行加粗、内容成段、保留时间戳与 `[?]`)。

**用户偏好**: 最终文件应保存在 `~/Desktop/transcript/` 目录下。

```bash
# Ensure the directory exists and run the merge command.
# Use the title extracted in the previous step for the filename.
mkdir -p ~/Desktop/transcript/

# Note: The output path must be absolute. The ~ character is not expanded by the script.
# Use $HOME or a full path like /Users/username/Desktop/...
python3 scripts/correct_transcript.py \
  --merge --chunk-dir /tmp/tc_chunks --title "会议标题" -o "$HOME/Desktop/transcript/会议标题.docx"

> ⚠️ **Pitfall: Tilde (~) Expansion**: The `-o` path passed to the Python script **must be an absolute path**. The script does not expand the `~` character to the user's home directory. Using a path like `~/Desktop/...` will cause a `FileNotFoundError`. Always use a variable like `$HOME` (if in a shell context that will expand it) or construct the full, absolute path (e.g., `/Users/your_user/Desktop/...`) before passing it to the script. The example above was updated to use `$HOME` to avoid this error.
```

> ✅ **出 docx 不需要任何外部依赖**:`correct_transcript.py` 用 Python **标准库 `zipfile`** 直接写
> OOXML,**不依赖 python-docx / pandoc / textutil / unoconv**。所以**绝不要**因为「pip 缺失 / 装不了
> python-docx / 没有转换工具」就放弃改交 .txt —— 直接调本脚本的 `--to-docx` 或 `--merge -o X.docx`,
> 任何有 Python 的环境都能出合法 docx(Word 可正常打开)。

渲染 `.docx` 时脚本默认:**去掉每行时间戳**(只留「说话人 N」)、**去掉首行 meta 的钟点**(留日期+时长)、
并把上游误写的**字面转义 `\\n`/`\\t` 兜底还原**成真换行。要保留时间戳加 `--keep-timestamps`。

> 若同时还想要纯文本中间产物,可先 `-o ...corrected.txt` 再 `--to-docx` 转一份。

**合并后务必校验完整性**:`grep -c '^说话人'` 的块数应与原始稿一致(本技能的设计保证不增删发言)。
不一致 = 有块清洗时漏行,需重清那块。

### Step 3 — 提议维护 glossary(闭环)

交付最终的 `.docx` 文件后,**主动向用户提议**,将本次清洗过程中发现的新错误修正(例如某个 ASR 常错的
英文名)、新的人名或术语,更新到**对应的域字典**(你的 `<项目>.json`;通用口癖才进 `general.json`)。
获得用户同意后,再执行更新。

这形成了一个持续学习的闭环:
1. 把本次确认的新错→对、新人名/术语,写回对应的域字典 JSON。
2. **数据与逻辑分离**:只改 JSON,不动 skill 逻辑。
3. 下次同样的 ASR 错误就会在 Step 1 被自动修正。

---

## 2. 字典结构(分域,在 `references/dicts/`)

字典是 `references/dicts/` 下的并行文件,用 `--domain` 路由(见上)。每个文件 schema 相同:
- `references/dicts/general.json` — 永远加载;通用术语 + `fillers`(口癖)。**不放**任何域专属/风险词。
- `references/dicts/example-project.json` — **示例域字典**,演示格式。**复制它**改成你自己的
  `<项目>.json`(填该项目真实的人名/公司/术语/已知 ASR 错误),用 `--domain <项目>` 加载。
- 新项目 → 新建 `dicts/<项目>.json`,`--domain <项目>` 即用,无需改脚本。

**加词时改对应域的文件**(项目专属词进该项目字典,通用口癖进 general)。加载时多文件合并(后者覆盖前者)。
> ⚠️ 域字典里会放真实人名/客户术语 —— 那是**你私有的本地数据**。若你 fork 本仓库,**别把自建的
> `<项目>.json` 提交回公开仓库**(`.gitignore` 已忽略 `references/dicts/*` 下除 general/example 外的文件)。

每个文件的字段:
- `canonical.people / orgs / terms` — 正确专有名词清单。用途:让 Step 2 知道该把模糊词吸附到什么。
- `replacements` — `"错":"对"` 映射,Step 1 脚本**子串**替换(长 key 优先)。
  **key 要足够具体**,避免误伤(例如别用一个会成为更长词子串的短词当 key,否则会把那个长词撑坏;
  也别用一个恰好是某人名片段的裸词当 key,会误改人名)。
- `replacements_wordbound` — **整词边界**版替换,只在 key 不被 `[A-Za-z0-9]` 紧邻时命中。
  专给「本身是更长真实术语子串的短英文缩写」用:例如某个 2-3 字母缩写必须走这里,否则子串替换会把
  包含它的更长单词(如 `PRD`、`PROJECT`)一起毁掉。整词边界版只命中独立出现的缩写。
- `fillers` — `--strip-fillers` 用的口癖表(独句感叹词 / 起首语气词 / 显式结巴对)。
- `protect` — **整词边界护栏**:列在这里的词组在替换前会被屏蔽、替换后还原,因此「作为它子串的人名」
  绝不会被误改。中文无空格,这是处理子串撞车的可靠手段。例:某个成语里嵌了一个人名片段时,把该成语
  放进 `protect`,人名替换就只命中独立出现的那个人名,成语完好。遇到新的撞车词(成语/固定词)就往这里加。

> `general.json` 只含通用口癖与术语,**不含任何真实人名/客户词**。域字典(`<项目>.json`)里的人名
> 请先核对再依赖。

---

## 4. User Preference

- **Strict Adherence**: The user has emphasized the importance of following this skill's instructions *religiously*. Do not deviate from the prescribed workflow. The structural integrity of the transcript and the deterministic nature of the cleaning process are paramount.

## 3. 不要做

- ❌ 总结、提炼要点、生成会议纪要(本技能只到「干净逐字稿」为止)
- ❌ 删除任何发言、数字、决策
- ❌ 在没把握时臆改人名(标 `[?]`,不要猜)
- ❌ 把 canonical 词表硬塞进每处相似词(只在明显是 ASR 错误时才吸附)
- ❌ 去抓取/下载源转写(导出不属于本技能;本技能从一个已存在的文本文件开始)
