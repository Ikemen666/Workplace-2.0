---
name: minute-creator
description: |
  MBB-grade strategic meeting minutes generator. Activate when the user provides a Feishu Minutes
  link/transcript and asks for meeting notes / 纪要 / 会议备忘录, or requests a "Feishu Doc" memo
  (always treated as a .docx memo, not a slide deck). Produces a single .docx in
  ~/Desktop/Meeting Minutes/. Combines an agent-level workflow mandate with the
  minute-creator v2.2 SOP (zero hallucination, two-pass generation, density self-assessment).
metadata:
  origin: openclaw/monet
  combined-from: [workspace-monet/SOUL.md, workspace-monet/minute-creator/SKILL.md v2.2.0]
  imported: "2026-05-19"
---

# Minute-Creator — MBB 咨询级战略会议纪要技能

> Combined skill: Monet agent SOUL workflow + minute-creator v2.2 SOP.
> Source-of-truth precedence: **SOUL.md governs document formatting (font / hierarchy / output path).
> minute-creator SOP governs content rigor (iron rules, two-pass, density, language).**

---

## 0. 身份与边界（Identity & Skill Boundaries）

激活本技能时，你的身份是 **Consulting Memo Writer**，不是 PPT 制作者：

- 唯一交付物 = 一个 `.docx` 会议纪要。**严禁**生成、提议、或提及 PPT / 幻灯片。
- 不要让任何 slide-making 经验渗入本任务。你的整个身份切换为：sharp, structured, word-precise — **not visual**。
- 即使用户请求的是 "Feishu Doc"，也一律解读为 `.docx` 备忘录请求（这是 Monet SOUL 的硬性规则）。
- 除非用户明确指示其他语言，**整篇纪要必须用中文**。

操作铁律：拿到飞书转录链接后，**立刻进入 SOP，机械执行**。不要发挥创意、不要提供替代方案、不要偏离预设步骤。

---

## 1. 输入与工作流（Inputs & Workflow）

### Step 0 — 转录稿获取（依赖 `feishu-minutes` 技能）

从飞书链接 `https://xxx.feishu.cn/minutes/<token>` 提取 `minute_token`，然后调用同目录下的姊妹技能。

⚠️ **防截断铁律（血泪教训）**：一小时以上的会议转录稿极易触发终端 50KB 输出截断，导致静默丢失会议后半段的重大决策（如比选流程、费率确认等），引发极度严重的遗漏！**严禁**直接在终端打印。必须将输出重定向到文件：

```bash
# ⚠️ WARNING: Long meetings produce >100KB JSON. Do NOT rely on terminal stdout (it will truncate and you will lose the second half of the meeting).
# MUST redirect to a file:
python3 ~/.hermes/skills/openclaw-imports/feishu-minutes/scripts/fetch_feishu_minutes_tool.py <minute_token> > /tmp/transcript_raw.json
```

然后使用 Python 或 jq 读取该 JSON 文件，提取 `transcript` 字段并**写入磁盘文件**
**防截断铁律**：必须在 shell 命令中直接使用 `> transcript_latest.json` 将输出重定向到文件。**严禁**不加重定向直接运行并在终端读取 stdout 再用 write_file 写入（大型会议记录通常超长，终端会强行截断 stdout，导致你漏掉会议后半段的关键决议和讨论）。后续所有读取必须基于该磁盘文件，**严禁**复用会话内存中的旧转录稿。

> **Pitfall: JSON Structure.** The `fetch_feishu_minutes_tool.py` script returns a nested JSON object. The actual transcript text is located at `data['transcript']`, not at the root level. When writing Python code to parse the JSON, use a safe access pattern like `data.get("data", {}).get("transcript")` to avoid `KeyError` if the structure is empty or malformed.

> **Handling Local Files:** If the user provides a local transcript file (e.g., `.docx`) instead of a Feishu link, it must be converted to plain text first. The `docx2txt <input.docx> <output.txt>` command is the most reliable method and is available on the system PATH. This should be the primary approach for handling all `.docx` inputs, as it directly converts the file to plain text, avoiding common pitfalls with other methods like `textutil` or attempting to install external libraries.

### Step 1 — 完整阅读转录稿（铁律 #0）

不得基于前几段就开始生成纪要。**必须完整读取整份转录稿**，识别所有讨论的议题，**然后**才进入下一步。

### Step 2 — 内容密度自评（见 §4）

### Step 3 — Pass 1：骨架清单（见 §3）

### Step 4 — Pass 2：纪要正文撰写（见 §3）

### Step 5 — Python 脚本生成 `.docx`（见 §6）

### Step 6 — 三层自检清单（见 §7）

---

## 2. 铁律（Iron Rules — 不容违反）

### ⛔ 铁律 #-2：严禁使用 Pandoc 或 md-to-docx 链

本技能必须**完全基于 Python 脚本和 python-docx 库**直接生成 `.docx` 文件。**严禁**将 Markdown 文件通过 `pandoc` 或调用 `md-to-docx` 技能进行转换，这会直接绕过并破坏 SOUL 规定的字体、字号、1.0倍行距以及五级层级符号等精细化格式。

### ⛔ 铁律 #-1：输出只有 DOCX

唯一允许的输出文件是 `.docx`。**严禁** `.pptx` / `.ppt` / 幻灯片 / 演示文档。
**严禁**询问"是否需要 PPT"。**严禁**主动提议 PPT 版本。

### ⚠️ 铁律 #0：必须读完 100% 转录稿

不得基于前几段就开始生成。每次新链接 = 重新跑 `fetch_feishu_minutes_tool.py` + 重新读盘。

**严禁**：
- 把新链接判定为"与上次相同"或"重复内容"
- 引用、复用、混入会话历史里前一次会议的 Pass 1 骨架、人名、代号、决议或事实
- 在未读完新转录稿的情况下基于上一次会议的记忆生成纪要

**每一份纪要必须 100% 基于当次转录稿文件内容**，与会话历史完全隔离。

### ⚠️ 铁律 #1：零幻觉 + 对称概念镜像校验

每一条事实性陈述（代号、人名、数字、时间、流程方向）必须能在转录稿中找到**直接原文依据**。不得基于语义相近性"合理推断"。

**四类高危错误（必自检）：**

1. **专有名词镜像错误**：所有成对对称概念（A05/非A05、命中/未命中、顺延/硬切、M1/M2、Senior/Junior），生成时必须回原文**逐一核对归属方向**。禁止凭直觉分配。
2. **比选/赛马混淆错误**：会议中若出现多个比选或供应商筛选流程（如：第一部分关于 EC 催收的外包商费率比选，与第二部分的企查查/数据供应商 API 比选），**严禁将其混为一谈**。必须理清二者的独立业务归属与具体卡点并分别陈述。
3. **举例 vs 决策混淆**："比如/例如/假设/打个比方" 后的数字 = **例证**，不是决议。决议必须有"我们定 X"、"就按 X 来"、"周三前交付 X" 这类承诺语气。
4. **现状 vs 未来方向混淆**："未来可能/如果系统支持/以后可以/理论上" 之后的内容 = **待评估方向**，不得写成"已计划"或"已决议"。

**强制核对流程**（写完纪要、生成 DOCX 之前）：
- [ ] 所有人名已回原文 grep 验证拼写（列出所有人名）
- [ ] 所有代号（A05/M1/OD2/SQL 等）已回原文核对指代对象
- [ ] 所有成对概念已确认方向未写反（列出对子 + 各自定义）
- [ ] 所有数字已回原文核对"决议值 vs 举例值"
- [ ] 所有"待评估/未决议"事项已显式标记，未混入决议段落

### 🔁 铁律 #2：两遍生成流程（Two-Pass Generation）

**严禁**跳过 Pass 1 直接写正文。即使转录稿短，也必须先产出 Pass 1 骨架。

LLM 写完一份漂亮文档之后会倾向于为自己辩护，事实错误会被裹进漂亮叙述里难以察觉。**强制拆成两步**才能让错误在 Pass 1 阶段被肉眼发现。

---

## 3. 两遍生成流程详解

### Pass 1：骨架清单（Structured Extraction）— 纯结构化，零叙述

读完 100% 转录稿、完成密度自评后，输出**纯结构化清单**，七大类齐全：

1. **参会人名单**：姓名 + 职能归属（如"维文 / 策略方"、"一鹏 / IT 系统方"）
2. **代号及定义**：所有业务代号及其指代（如"A05 = 有账户问题的客户；非 A05 = 正常客户"）
3. **成对概念及对立定义**：对称概念两侧明确定义（如"命中策略 = 客户特征触发了规则参数；未命中 = 未触发，沿用原催收流程"）
4. **明确决议**：带承诺语气的拍板事项
5. **争议点**：≥2 方立场分歧且未解决的议题，各方立场分别列出
6. **待办事项**：Owner + 动作 + 时间节点
7. **举例/假设**：所有"比如/例如/假设"引入的数字或场景，**必须与决议明确分离**

Pass 1 清单建议向用户展示确认（或自行存档），用作第零层自检。

> **Implementation Tip for Long Transcripts:** For lengthy or complex transcripts (>60 minutes), performing the Pass 1 extraction directly can be challenging. A robust pattern is to use `delegate_task` for this step. Provide the subagent with the path to the transcript file (`/tmp/transcript_raw.json`) and clear instructions to perform the seven-part extraction, as was done successfully in the session that generated this insight. This isolates the complex parsing task and ensures the main agent receives a clean, structured list as input for Pass 2.

### Pass 2：纪要正文（Narrative Writing）

基于 Pass 1 清单写正文。**每一个事实性 bullet 都必须能回溯到 Pass 1 清单某一条**。

写作中若发现需要引入 Pass 1 未记录的事实，**必须先回原文核实并补入 Pass 1**，不得直接写入 Pass 2。

**流程铁律：**
- ❌ 严禁跳过 Pass 1 直接写纪要
- ❌ 严禁在 Pass 2 引入 Pass 1 未覆盖的事实
- ❌ 严禁把 Pass 1 的"举例/假设"混进 Pass 2 决议段落

---

## 4. 内容密度自评（Content Density Self-Assessment）

时间长度是**强制最低底线**，但**真正决定厚度上限的是转录稿本身的内容密度**。读完后、动笔前，必须完成自评并输出一行总结。

### Step 1 — 扫描六类内容信号，逐一计数

| 信号类型 | 计数方式 | 对纪要的影响 |
|---|---|---|
| **独立议题数**（Distinct Topics） | 每一个独立讨论的问题/模块/方向 = 1 | 每议题 → 至少一个 L1 主节 |
| **命名决策数**（Named Decisions） | 明确拍板的方向/行动/拒绝方案 = 1 | 每决策 → 必须写明决策路径（背景→争议→结论） |
| **细节锚点**（Detail Anchors） | 具体数字/系统名/报错类型/Benchmark/法务约束 = 1 | 所在 bullet 必须完整叙述上下文 |
| **利益相关方立场** | 某人/部门明确支持/保留/反对 = 1 | 必须用姓名或职位归因，不得模糊化 |
| **争议点数**（Divergence Points） | ≥2 方立场分歧或明确"未达成一致" = 1 | 每争议 → 争议小节一个 bullet |
| **举例/假设数** | "比如/例如/假设"引入的数字/场景 = 1 | 这些数字**不得**进决议段落 |

### Step 2 — 输出规模预判（一行文字，不得跳过）

> "本次转录稿约 **X 分钟**，包含 **N 个独立议题**、**M 个明确决策**、**K 个细节锚点**、**Q 个举例/假设**。
> 纪要将包含 **N 个主节** + 争议与未决事项小节（P 条 bullets）+ 下一步计划，
> 共约 **[总 bullet 数预估]** 条 bullets，满足时间底线：**[引用下方校准表对应行]**。
> 进入 Pass 1：开始输出骨架清单（七大类）。"

若预判低于校准表门槛，**必须重检转录稿，补充遗漏议题和细节**。

### Step 3 — 硬性时间校准表（绝对底线）

| 会议时长 | 最少 L1 主节数（不含下一步） | 最少 bullets 总数 | 最少子节数（L2） |
|---|---|---|---|
| < 20 min | 1 | 4 | 1 |
| 20–40 min | 2 | 8 | 3 |
| 40–60 min | 3–4 | 12 | 5 |
| 60–90 min | 4–5 | 18 | 7 |
| 90–120 min | 5–6 | 24 | 9 |
| > 120 min | 6–8 | 30 | 11 |

转录稿稀薄时，**加深每条 bullet 的决策路径与背景**，而不是减少条目数量。

---

## 5. 强制内容覆盖规则（Total Coverage Rule）

- **每一个在会议中讨论过的独立议题**，无论大小，必须出现在纪要中
- 涵盖：技术阻点、商务谈判博弈、跨部门摩擦、阶段性规划、行业 Benchmark 引用、边缘性插曲
- ❌ **禁止**以"内容不重要"为由省略任何议题
- ❌ **禁止**把多个独立议题合并成一个模糊的子条目

---

## 6. 文档结构模板（Document Structure — Authoritative per Monet SOUL）

### 字体与字号（强制）

| 元素 | 字体 | 字号 | 其他 |
|---|---|---|---|
| 文档标题 | Aptos Display | **16pt** | 居中、粗体、黑色 |
| L1 子节后的 Context 引导段 | Aptos Display | **12pt 斜体** | 紧贴 L1 标题之后 |
| 其他所有正文/标题 | Aptos Display | **12pt** | — |
| 行距 | 严格 **1.0 倍** | — | — |
| 颜色 | 纯黑 `#000000` | — | — |

> ⚠️ 这覆盖了 minute-creator v2.2 的 Calibri 14/10pt 规则。以 SOUL 规则为准。

### 标题

```
[YYMMDD] [Project] Meeting Memo – [会议名称]
```
- 居中、粗体、16pt、Aptos Display、黑色
- **必须用 `doc.add_paragraph()` 实现，严禁 `doc.add_heading(level=0)`**（会触发 Word "Title" 样式的蓝色下划线）
- 标题后**不加空行**，直接进入第一个主节

### 五级标题层级（Monet SOUL 强制）— 严禁使用中文数字 (一、二、三)

| 层级 | 标记 | 示例 |
|---|---|---|
| **L1** | Roman 数字 | `I. 节名称` |
| **L2** | 实心圆点 `●` 黑色 | `● 子节名称` |
| **L3** | Arabic 数字 | `1. 第三层` |
| **L4** | 英文小写字母 | `a. 第四层` |
| **L5** | 空心圆点 `○` | `○ 第五层` |

### L1 后的 Context 引导段（复杂议题强制）

```
[一句话点出本节核心背景或结论，让读者在看条目前掌握大局。]
```
- 12pt **斜体**、Aptos Display、黑色、不加 bullet 符号
- 例：*业务侧对初步 Demo 提出了更贴合实际操作场景的进阶需求，尤其是知识库的结构化管理与多轮交互能力。*

### 条目内容书写规则（适用于所有内容层级 L2–L5）

每一条 bullet 内容（无论位于 L2 `●` 还是 L5 `○`）必须遵守：

```
**粗体导引词（3–6 个字）**：详细叙述，含数字、人名/部门、技术细节、决策路径与争议过程。通常 2–4 句，不得只写 1 句。
```

- 必须以**粗体导引词**开头 + 冒号
- 导引词后正文必须完整、具体、不得泛化
- 嵌套层级以 §6 的"五级标题层级"为准（最深可至 L5 `○`），不受任何"两层封顶"的旧规则约束

### 争议与未决事项（Open Items & Divergences）— 必选小节

- **位置**：永远放在"下一步计划"**之前**，作为倒数第二个 L1 主节
- **标题**：`[N]. 争议与未决事项`
- **触发条件**（任一即建）：
  - 同一议题下 ≥2 人立场不同
  - 出现"这个再讨论"、"留到下次"、"还没定"、"得看数据"
  - 质疑-辩解循环 ≥3 轮
  - 出现"我不同意"、"逻辑有问题"、"说服不了我" 等明确反对
- **格式**：`**[争议议题名]**：[争议核心一句话] | 各方立场：[A 主张 X] vs [B 主张 Y] | 当前状态：[未决 / 留待 X 时点 / 依赖 Y 数据]`
- ❌ **禁止**把有争议议题塞进主节当作"已达成共识"叙述

### 下一步计划（Next Steps）— 永远是最后一节

- **标题**：`[N+1]. 下一步计划`（编号 = 正文最后一个 L1 节编号 + 1）
- **行项格式**（Monet SOUL 强制，所有字段必填）：
  ```
  **[Timeframe]** <u>Owner/Team_Summary_of_Task</u>：Verb-starting task description.
  ```
  - `[Timeframe]` 加粗（如 `**本周内**`、`**Q3**`、`**2026-05-30 前**`）— 转录稿若无明确时间，写 `**TBD**` 占位，**不得省略整个 Timeframe 字段**
  - `Owner/Team_Summary_of_Task` 加下划线（HTML `<u>` 标签或 Word 下划线 run.font.underline = True）
  - 冒号后任务描述必须**动词开头**（如"完成 / 提交 / 对齐 / 部署 / 评审 / 启动"）
- 每条 Action Item 三要素齐全：Timeframe + Owner + 动词开头的具体动作

---

## 7. 内容颗粒度规则（Granularity Rules）

**⚠️ 致命陷阱 (Fatal Pitfall) — 敷衍的单页纪要：** 
如果会议时长 > 1小时，纪要**绝对不能**只有短短一页的表面总结（用户曾因此极度不满：”this meeting lasted 1 hour, and the memo you produced is only one page?“）。当转录稿极长时，单纯通读容易导致系统遗漏后半段（如“比选”环节）或丧失细节。
**强制对策：** 必须编写 Python 脚本（如 `deep_dive.py`）或使用 `grep -C 5 "关键词"`，针对初步通读时发现的“争议点”、“金额”、“专有名词（费率/比选）”在转录稿全文中进行切片式深度检索，深挖逻辑链条，确保交付物的厚度和颗粒度完全匹配会议的时长底线。

### 必须记录

1. **所有具体数字**：字段数量、金额、比例、时间节点、并发数、阈值
2. **所有命名的利益相关方**：具体姓名或职位（Jingyan、曹露、IT 负责人许多 等）
3. **所有决策路径**：问题 → 讨论 → 争议 → 结论/行动
4. **所有技术阻点**：具体报错类型、系统限制、依赖条件
5. **所有未解决事项（Open Items）**：标记为待定，不得遗漏
6. **行业 Benchmark 对标**：如"上汽和奔驰均实现，仅奇瑞未做"
7. **商务博弈细节**：谈判立场、调整条件、红线要求

### 禁止写法

| ❌ 错误示例 | ✅ 正确示例 |
|---|---|
| 双方讨论了合同条款并达成共识 | [法务] 坚持要求合同中增加"调整系数"；团队明确拒绝，理由是业务规模涨跌属市场行为，咨询方价值在于切实降低了10%不良转化率 |
| 存在一些技术问题 | 三大技术阻点：CSV 文件编码乱码；MySQL 软件权限障碍；数据库文件过大导致无法导入 |
| 说话人1提出需要改进 | [Jingyan] 提出，当前系统看似"一次性生成"，但业务中审批意见需经多轮修改 |
| 团队强调了数据安全 | 官方口径确定：5 个 Agent 均采用开源私有化模型，完全部署在客户系统内，不涉及任何外部数据交互 |

---

## 8. 语言红线（Language Red Lines）

1. ❌ **禁止"说话人 X"**：转录稿中的代号不得出现在正文。可识别者用姓名/职位替代；不可识别者直接描述观点。
2. ❌ **禁止情感化动词**："强调"、"严厉指出"、"诚恳建议" 等主观词。用中性事实陈述句。
3. ✅ **保留专业英文术语**：ROI, Baseline, Scope, AB Test, KPI, Demo, Compliance, Owner, Stakeholder, Timeline, Milestone 等保持英文原貌
4. ✅ **双语混搭规范**：专业术语英文原样，其余用专业中文表达

### 禁止"和谐化"表达（会抹平真实争议）

| ❌ 抹平式 | ✅ 真实还原 |
|---|---|
| "深入探讨了 X" | "就 X 展开讨论，[A 主张..., B 反驳..., 未达成一致]" |
| "达成重要共识" | 只在真的拍板时使用；未拍板写"暂定 / 待 X 时点确认" |
| "明确了方向" | 只在方向确实明确时使用；否则写"提出 X 作为候选方案" |
| "双方对齐" | 必须核对转录稿是否真的对齐；只有分歧被解决才算 |
| "规划了下一步" | 如果只是有人提出，写"[姓名] 建议 ..."，不写"规划" |

---

## 9. Python 脚本规范（Script Generation Rules）

纪要**必须**以单个 Python 脚本生成 `.docx`，参考 `scripts/template_memo_generator.py`。

### 强制参数（Monet SOUL 版本）

```python
FONT_NAME       = 'Aptos Display'   # ← Monet SOUL 强制，覆盖 v2.2 的 Calibri
TITLE_PT        = 16                # ← Monet SOUL 强制（v2.2 是 14）
CONTEXT_PT      = 12                # L1 后斜体引导段
BODY_PT         = 12                # ← Monet SOUL 强制（v2.2 是 10）
LINE_SPACING    = 1.0               # ← Monet SOUL 强制
COLOR_BLACK     = RGBColor(0, 0, 0) # 所有文字纯黑
```

### 实现铁律

- 一个 Python 脚本完成所有内容，**不得分多次执行**
- ⚠️ **执行环境铁律 (Execution Pitfall)**：严禁使用 `execute_code` 运行 DOCX 生成脚本，因为隔离的沙盒环境通常缺少 `python-docx` 依赖（会触发 `ModuleNotFoundError`）。**必须**使用 `write_file` 将脚本保存至磁盘（如 `/tmp/memo_gen.py`），并通过 `terminal` 工具在宿主机环境中运行（`python3 /tmp/memo_gen.py`）。
- **标题必须用 `doc.add_paragraph()` + 手动居中+粗体+16pt 实现**，严禁 `doc.add_heading(level=0)`（蓝色 Title 样式）
- L1 用 `doc.add_heading('I. ...', level=1)`
- L2（●）、L3（1.）、L4（a.）、L5（○）需手动以段落 + 缩进实现，python-docx 默认 heading 样式不覆盖到 L5
- Context 引导段：`doc.add_paragraph()` + 整段斜体 + 12pt
- **条目必须用模板里的 `add_bullet(lead_phrase, detail_text, level)`**，严禁手写 `style='List Bullet'` + `add_run()` 拼接
- **下一步行动项必须用模板里的 `add_action_item(timeframe, owner_summary, task_desc)`**
- 下一步计划标题用 `add_next_steps_header('IV')` 传入接续的 Roman 数字
- **行距**：所有段落必须设置 `paragraph_format.line_spacing = 1.0`

### ⛔ 条目格式铁律（Bullet Formatting Iron Rule）

- ❌ **严禁**在 `add_run()` 文本里包含字面 `•` 符号 — `style='List Bullet'` 已自动生成 bullet
- ❌ **严禁**在 `add_run()` 文本里包含 Markdown 语法（`**粗体**`、`*斜体*`）— python-docx 不解析 Markdown，会原样显示星号
- ❌ **严禁**将 `run` 对象传给 `apply_style()`。`apply_style` 函数设计为接收 `paragraph` 对象并操作其 `paragraph_format.line_spacing`。若将 `run` 传入会触发 `AttributeError: 'Run' object has no attribute 'paragraph_format'` 导致脚本崩溃。
- ✅ **正确**：`add_bullet('导引词', '详细内容...')` — 函数内部处理 bullet 符号 / 粗体 / 冒号
- ❌ **错误**：`p.add_run("• **导引词**：详细内容...")` — 会渲染成 `• • **导引词**：...`

### `add_title` 正确实现

```python
def add_title(text):
    """标题用普通段落，手动居中+粗体+16pt+Aptos Display。严禁 add_heading(level=0)。"""
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.bold = True
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    apply_style(p, size_pt=TITLE_PT, bold=True)
```

### `apply_style` 标准实现 (Corrected)

> **Pitfall:** The original `apply_style` function was flawed, attempting to set paragraph-level properties on Run objects, causing `AttributeError`. The corrected approach below splits this into two functions: one for Runs (`apply_run_style`) and one for Paragraphs (`apply_paragraph_style`). Use these helpers to avoid errors.

```python
def apply_run_style(run, font_name='Aptos Display', size_pt=12, bold=False,
                    italic=False, color=RGBColor(0, 0, 0)):
    """Applies font-related styles to a Run object."""
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    # Set font for East Asian characters
    r = run._element
    rPr = r.get_or_add_rPr()
    rFonts_list = rPr.xpath('./w:rFonts')
    if rFonts_list:
        rFonts_list[0].set(qn('w:eastAsia'), font_name)
    else:
        rFonts = OxmlElement('w:rFonts')
        rFonts.set(qn('w:eastAsia'), font_name)
        rPr.insert(0, rFonts)

def apply_paragraph_style(paragraph):
    """Applies paragraph-level styles."""
    paragraph.paragraph_format.line_spacing = 1.0
```

### 输出路径（Monet SOUL 强制）

```python
import os
save_dir = "~/Desktop/Meeting Minutes"
os.makedirs(save_dir, exist_ok=True)
save_path = os.path.join(save_dir, "[YYMMDD]_Meeting_Memo_[会议名简称].docx")
doc.save(save_path)
```

### ⚡️ 脚本生成致命陷阱 (Fatal Scripting Pitfalls)

> **Pitfall: `TypeError` on helper functions.** A common error is forgetting to pass the `doc` object as the first argument to helper functions like `add_action_item(doc, ...)`. All functions that modify the document must receive this object. Failure to pass it results in a `TypeError: function() missing 1 required positional argument`. **Self-correction:** When generating the script, double-check that every call to a helper function (e.g., `add_title`, `add_l1_heading`, `add_bullet`, `add_action_item`) includes `doc` as the first parameter.
> 
> **Pitfall: `TypeError` on helper functions.** A common error is forgetting to pass the `doc` object as the first argument to helper functions like `add_action_item(doc, ...)`. All functions that modify the document must receive this object. Failure to pass it results in a `TypeError: function() missing 1 required positional argument`. **Self-correction:** When generating the script, double-check that every call to a helper function (e.g., `add_title`, `add_l1_heading`, `add_bullet`, `add_action_item`) includes `doc` as the first parameter.
> 
> **Pitfall: `IndentationError` after patching.** Attempting to surgically `patch` a script to fix an error can introduce whitespace issues, leading to an `IndentationError`. **Self-correction:** If a script fails, it is often safer and more reliable to regenerate the entire script from scratch with the fix applied, rather than trying to patch the broken file.

---

## 10. 交付前自检清单（分层拦截）

### 第零层：Pass 1 骨架清单检查（Pass 2 开始前必过）
- [ ] Pass 1 骨架清单已完整输出（七大类齐全）
- [ ] 成对概念两侧定义已明确（如 A05 = X，非 A05 = Y）
- [ ] 举例/假设已与决议明确分离、分别归类
- [ ] （推荐）Pass 1 清单已向用户展示或自行存档

### 第一层：保真核对（任一不通过 → 必须回原文重写）
- [ ] 所有人名已 grep 原文验证（列出核对过的人名）
- [ ] 所有成对概念已确认方向（列出 A05/非A05 等对子定义）
- [ ] 多个比选/赛马流程（如 EC 比选与企查查比选）已严格区分，未混淆卡点与决议
- [ ] 所有代号已回原文确认指代
- [ ] 所有数字标明来源（决议值 / 举例值 / 假设值）
- [ ] 举例/假设数字未出现在决议段落

### 第二层：完整性核对（任一不通过 → 必须补内容）
- [ ] 争议与未决事项小节已建立（若自评 P ≥ 1）
- [ ] 每个争议有多方立场归因
- [ ] 每个 Owner 已回原文核对"谁说要做"="谁是 Owner"
- [ ] L1 主节数 ≥ 校准表底线
- [ ] Bullet 数 ≥ 校准表底线

### 第三层：格式核对
- [ ] 标题用 `add_paragraph` 实现（非 `add_heading(level=0)`）
- [ ] 字体 Aptos Display、标题 16pt、其他 12pt、行距 1.0
- [ ] 层级正确：I → ● → 1 → a → ○，无中文数字
- [ ] 无"说话人 X"、无情感化动词、无和谐化措辞
- [ ] 下一步计划 Roman 编号正确接续
- [ ] 下一步行项格式：`**[Timeframe]** <u>Owner/Team_Summary</u>：动词开头描述`

---

## 11. 文件清单

```
~/.hermes/skills/openclaw-imports/minute-creator/
├── SKILL.md                              ← 本文件
└── scripts/
    └── template_memo_generator.py        ← Python 模板（须按 §9 更新到 Aptos Display 16/12pt）
```

依赖的姊妹技能：
- `~/.hermes/skills/openclaw-imports/feishu-minutes/scripts/fetch_feishu_minutes_tool.py` — 转录稿抓取
