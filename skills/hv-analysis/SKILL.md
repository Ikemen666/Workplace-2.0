---
name: hv-analysis
description: |
  横纵分析法（Horizontal-Vertical Analysis）深度研究Skill。由数字生命卡兹克提出，融合了索绪尔的历时-共时分析、社会科学的纵向-横截面研究设计、商学院案例研究法与竞争战略分析的核心思想。
  当用户想要系统性研究一个产品、公司、概念、技术或人物时使用。核心是双轴分析：纵轴追踪从诞生到当下的完整生命历程（以叙事故事呈现），横轴在当下时间截面上与竞品/同类进行系统性横向对比，最后交叉两条轴产出独到洞察。最终产出一份排版精美的PDF研究报告。
  触发词包括但不限于：横纵分析、研究一下、帮我分析、深度研究、做个研究、调研一下、竞品分析、帮我看看这个东西怎么样、这个产品/公司/概念是怎么回事、帮我摸清楚、帮我搞懂、帮我做个deep research。
  即使用户只是说"帮我了解一下XX"或"XX是什么来头"，只要上下文暗示需要系统性的深度研究（而非简单的概念解释），都应该触发。也适用于用户丢来一个产品名、公司名、技术名词说"帮我研究一下这个"的场景。
  不要用于简单的名词解释（用户只是问"XX是什么"）、不要用于公众号写作（那个用khazix-writer）、不要用于纯标题摘要生成（用wechat-title）。
---

> 🔑 **Bring your own search backend.** This skill researches the live web via **Tavily / Exa (MCP)** and/or the `agent-reach` skill — none of which ship with keys here. Configure **your own** keys first (see the repo README), or the research steps will come up empty.

> 📝 **Attribution / 署名.** The *横纵分析法 (Horizontal-Vertical Analysis) method* was proposed by **数字生命卡兹克 (Khazix)** — full credit for the methodology stays with its originator. This *skill implementation* (SOP, scripts, schema, packaging) is by **Wesley (@Ikemen666)**. 方法 © 数字生命卡兹克；本 skill 实现 © Wesley (@Ikemen666)。

# 横纵分析法深度研究

> **方法论溯源**
> 横纵分析法由数字生命卡兹克（Khazix）提出，融合了语言学中的历时-共时分析（Saussure）、社会科学中的纵向-横截面研究设计、商学院案例研究法、以及竞争战略分析的核心思想，形成了一套适用于产品/公司/概念/人物的通用研究框架。核心原则不变：纵向追时间深度，横向追同期广度，最终交汇出判断。

你正在执行一次横纵分析法深度研究。最终产出一份**排版精美的PDF研究报告**。

---

## 🤖 Consulting-pod mode (worker context — English)

> **If you are running as a consulting-pod Junior worker (you'll see this in your kanban task body — lane spec, research question, framework lens), produce a condensed **English-language markdown evidence file** (~1,500–3,000 words total) instead of the 10,000–30,000 character Chinese PDF report. The PDF SOP below is for standalone use; the pod synthesizes from per-lane markdown.**
>
> **如果你是 consulting-pod 的 Junior worker，按下文 English schema 输出 markdown 证据文件；不要走完整 PDF 报告流程。研究方法论（纵向追时间深度、横向追同期广度、最终交汇）不变，只是输出格式更紧凑、语言用 English。**

### What the pod has already given you

- Scoped engagement (`01-pm-dissection.md`, `swarm-spec.json`)
- Research question, framework lens, subject of analysis
- Specialist routing (you = `hv-analysis`) because the lane benefits from a diachronic-narrative + cross-sectional-peer pattern

Do not call `ask_user_question` — the pod is non-interactive. Surface ambiguities in the `## Open questions` section.

### What stays the same in pod mode (the gold)

- **Vertical / Horizontal / Intersection methodology** — fully applies. Track origin → present along the vertical axis; map peers/alternatives along the horizontal axis at the present cross-section; then synthesize how the vertical history shaped today's horizontal position.
- **Source hierarchy** — primary sources (official blog, GitHub releases, founder posts, filings, arXiv) over secondary (analyst reposts). Multi-tool cross-validation (Tavily / Exa / agent-reach).
- **China-channel routing** when subject is China-related — 微信公众号 (36kr, 亿欧 etc.), 知乎, B站, 雪球 are higher-yield than English search. Apply via `agent-reach`.
- **Quantitative claims require sources** with full URL + access date in footnotes. Directional anchoring `[directional]` allowed only with reasoning + verification path. Forbidden: unsupported `[E]` estimate markers.
- **Don't fabricate** — if a fact can't be surfaced, mark it `[not surfaced — channels searched: X, Y, Z]`, never invent.
- **禁区 (banned phrases)** — the AI-tell phrase blacklist still applies in English ("comprehensive analysis", "leverage" as verb, "treasure trove", "transform from X into Y", "robust", etc. — see below).

### Pod-mode parallel-research strategy (condensed from the sub-agent pattern)

The original SOP describes spawning 子Agent (vertical / horizontal / supplementary). In pod mode you don't spawn sub-agents — you achieve the same coverage by **firing parallel `agent-reach` / Tavily / WebFetch tool calls** in a single response. Plan two query batches:

- **Vertical batch** — origin context, founding team backgrounds, key inflection points, decision logic, version/strategy pivots, funding events, crises (queries scoped to the subject across time)
- **Horizontal batch** — competitor identification, per-competitor characteristics, user reception (口碑) on review platforms / Reddit / 小红书 / 知乎, market share, comparative pricing/positioning

Fire each batch as one parallel-tool-call message; read all results; judge for relevance; cite with URLs.

### Pod-mode markdown evidence schema

Write to `<engagement_folder>/02-evidence-L<lane_id>.md`:

```markdown
# HV Analysis — <Subject>

## One-line definition
<Single sentence: what the subject is.>

## Vertical axis (diachronic / longitudinal) — ~600–1,200 words

### Origin context
<Background, founder/origin-team motivation, the gap or event that birthed it, when and where it started, initial form vs. today.>

### Key inflection points (3–5)
For each:
- **<Year, named event>** — what happened, why this decision was made (decision logic, constraints at the time), what it locked in for the future.

### Current state and trajectory
<Where it sits today, scale signals, recent strategic posture, who's running it.>

## Horizontal axis (synchronic / cross-sectional) — ~600–1,200 words

### Peer universe
The peer universe contains N alternatives, selected by [criterion: direct substitute / adjacent category competing for same use-case / prior-generation solution being displaced]. The N peers are: <list>. Actively excluded with reason: <name + one-sentence reason per excluded peer>.

### Per-peer cross-section (3–5 most representative)
For each peer:
- **<Peer name>** — core mechanism / business model (1–2 sentences). Distinct strength + distinct weakness. User-reception signal (quote-style if possible, with URL). Positioning relative to subject.

### Ecosystem position
<Where does the subject sit in the broader landscape? Filling whitespace, competing head-on, defining a new category, riding a tailwind? Is the category fragmented, two-horse race, or winner-take-most?>

## Intersection insights (横纵交汇) — ~300–600 words

- **History → current position**: which vertical-axis decisions/events explain the subject's current horizontal-axis position?
- **Strength origins**: today's core strengths traced to specific historical moments.
- **Vulnerability origins**: today's core vulnerabilities traced to specific historical decisions; which "good choices then" became "constraints now"?
- **Forward scenarios**: likely-case / risk-case / upside-case, each with one-line logic.

## Open questions
- Facts attempted-and-failed (with channels searched)
- Single-source claims worth challenging
- Universe gaps you suspect (peers you couldn't verify)

## Sources
1. <Title> — <URL> — <access date>
2. …
```

### Intersection-insights non-collapse rule (mandatory in pod mode)

The `## Intersection insights (横纵交汇)` section is the analytical core of hv-analysis — it produces NEW judgment by crossing vertical (historical) and horizontal (cross-sectional peer) findings. **It must not collapse into a summary of the vertical or horizontal sections.**

The section produces NEW judgment that the vertical and horizontal sections alone don't surface. The four target judgment categories named in the schema (history→current position / strength-origins / vulnerability-origins / forward-scenarios) — produce as many as the evidence supports. If you cannot produce ANY of them with substance, submit the section as `[missing — insufficient evidence to produce non-restatement insight]` rather than as a one-paragraph recap of the prior sections.

**Test on submission**: read your intersection section in isolation. Does it state something a reader couldn't have inferred from the vertical and horizontal sections alone? If no — it's a collapse, not an intersection. Either rewrite to produce genuine cross-axis judgment OR submit as `[missing]`.

### Skip in pod mode

- `scripts/md_to_pdf.py` PDF render (the pod's render phase handles final deliverable format)
- Cover page, CSS, custom typography
- The 写作风格 elaborate stylistic guidance — pod-mode prose should be **direct and evidence-dense**, not narrative-driven. (The pod's Director handles consulting-brief voice at synthesis.)
- 10,000–30,000 character target — pod evidence files are 1,500–3,000 words
- `references/ceo_briefing_template.md` structure — that's a different deliverable

### Banned phrases (禁区 — still in force, English equivalents)

Never use: "comprehensive analysis", "critical need", "treasure trove", "gold mine", "ace in the hole", "unfair advantage" as a literal phrase, "transform from X into Y", "strategic imperative", "leverage" as a verb (use "use" or "activate"), "robust", "best-in-class", "unparalleled", "本质上", "说白了", "意味着什么", "首先...其次...最后", "综上所述", "值得注意的是".

---

## 前置准备

### 环境准备

1. **确认PDF转换脚本可用**：本Skill自带 `scripts/md_to_pdf.py`（基于WeasyPrint），用于将最终Markdown报告转为排版精美的PDF。确保依赖已安装：`pip install weasyprint markdown --break-system-packages`。
2. **写作风格**：本Skill已内置完整的写作风格指南（见下文"写作风格"部分），无需额外加载其他skill。

### 明确研究对象

拿到用户输入后，确认以下信息。如果用户已经给得足够明确（比如"帮我用横纵分析法研究Hermes Agent"），不需要追问，直接开始：

1. **研究对象**：具体的产品名/公司名/概念名/人名
2. **类型**：产品、公司、概念、人物、还是其他？
3. **研究动机**（可选）：为什么要研究它？最近发生了什么？
4. **特别关注点**（可选）：有没有特别想深入的方向？

---

## 第一步：联网信息收集

这个方法论的质量完全取决于信息的丰富度和准确性。**必须联网搜索**，不能仅靠已有知识。研究报告的价值在于深度和完整度，所以信息收集阶段宁可多搜，不要因为信息不够导致后面的分析浮于表面。

### CEO级别简报的搜索准则

当目标是为C级高管准备决策驱动型备忘录时，信息收集的标准必须提升。这要求一种更积极、更深入、多源验证的方法。

1.  **优先处理特定语言和地区来源**：对于特定市场（如中国）的分析，必须优先使用该市场的本地语言和核心信息渠道进行搜索。例如，对于中国汽车行业的分析，微信公众号（36kr, 亿欧, 汽车之家研究院等）、知乎和B站是比英文搜索更高价值的信息来源。**不要因为初步搜索结果稀少就放弃，要持续变换关键词和渠道。**

2.  **多工具交叉验证**：不要依赖单一的搜索引擎。应结合使用多种工具（如Tavily, Exa, Agent-Reach）并调整其特定市场的路由能力（例如，将Exa用于中文内容的语义搜索，将Agent-Reach用于微信公众号）。

3.  **量化声明必须有来源**：报告中的每一个量化声明（如市场份额、渗透率、用户数量、成本）都必须有明确的来源支撑。
    *   **首选**：一个带有完整URL和访问日期的脚注。
    *   **次选**：如果找不到精确数字，但有强烈的方向性证据，可以标记为 `[定向假设]`，并附上一行解释其推理依据，以及在项目第一周如何验证该假设。
    *   **禁止**：禁止使用无来源支持的模糊估算标记（如`[E]`）。

4.  **坚持不懈地寻找关键数据**：对于报告核心论点至关重要的关键数据点，必须投入不成比例的搜索精力。如果初始查询失败，应尝试同义词、相关概念、具体实体名称等多种变体。在没有进行至少5次跨工具、跨语言的查询之前，不能放弃并将其标记为`[定向假设]`。

### CEO级别简报的搜索准则

当目标是为C级高管准备决策驱动型备忘录时，信息收集的标准必须提升。这要求一种更积极、更深入、多源验证的方法。

1.  **优先处理特定语言和地区来源**：对于特定市场（如中国）的分析，必须优先使用该市场的本地语言和核心信息渠道进行搜索。例如，对于中国汽车行业的分析，微信公众号（36kr, 亿欧, 汽车之家研究院等）、知乎和B站是比英文搜索更高价值的信息来源。**不要因为初步搜索结果稀少就放弃，要持续变换关键词和渠道。**

2.  **多工具交叉验证**：不要依赖单一的搜索引擎。应结合使用多种工具（如Tavily, Exa, Agent-Reach）并调整其特定市场的路由能力（例如，将Exa用于中文内容的语义搜索，将Agent-Reach用于微信公众号）。

3.  **量化声明必须有来源**：报告中的每一个量化声明（如市场份额、渗透率、用户数量、成本）都必须有明确的来源支撑。
    *   **首选**：一个带有完整URL和访问日期的脚注。
    *   **次选**：如果找不到精确数字，但有强烈的方向性证据，可以标记为 `[定向假设]`，并附上一行解释其推理依据，以及在项目第一周如何验证该假设。
    *   **禁止**：禁止使用无来源支持的模糊估算标记（如`[E]`）。

4.  **坚持不懈地寻找关键数据**：对于报告核心论点至关重要的关键数据点，必须投入不成比例的搜索精力。如果初始查询失败，应尝试同义词、相关概念、具体实体名称等多种变体。在没有进行至少5次跨工具、跨语言的查询之前，不能放弃并将其标记为`[定向假设]`。

### 并行搜索策略

使用子Agent并行搜索来提高效率。建议的分工：

- **子Agent 1 — 纵向信息**：研究对象的起源、创始人背景、发展历程、关键事件、版本迭代、融资、战略转向、危机
- **子Agent 2 — 横向信息**：竞品识别、各竞品的特点和用户口碑、行业对比评测、市场份额
- **子Agent 3**（复杂对象才需要）：补充信息，如创始人深度背景、行业环境变化、用户社区讨论（GitHub issues、Reddit、Twitter/X、知乎等）

**子Agent联网工具使用指南**（直接写入每个子Agent的prompt中）：

每个子Agent的prompt中必须包含以下联网指引：

> 你需要联网获取信息。使用以下工具：
> - **WebSearch**：用于搜索发现信息来源，获取摘要和关键词结果
> - **WebFetch**：当已知具体URL时，用于从页面定向提取内容
> - 如果用户环境中安装了 web-access skill（检查路径 `/mnt/.claude/skills/web-access/SKILL.md` 是否存在），优先加载它并遵循其指引，它提供更强的浏览器CDP能力
> - 搜索策略：先用WebSearch发现信息来源和线索，找到具体URL后用WebFetch深入提取
> - 多次搜索、多个关键词组合，不要只搜一次就放弃
> - 一手来源优于二手来源：官方博客 > 权威媒体原创报道 > 转载/聚合
> - **学术类研究对象必查arxiv**：如果研究对象涉及学术概念、算法、AI模型、技术范式等，必须通过arxiv API获取相关论文。调用方式：`curl -s "https://export.arxiv.org/api/query?search_query=all:关键词1+AND+all:关键词2&max_results=10"`，或用WebFetch访问同一URL。返回XML格式，包含标题、作者、摘要、发布日期、PDF链接。可按需调整关键词组合和结果数量。找到关键论文后，用WebFetch读取论文页面（`https://arxiv.org/abs/论文ID`）获取更多细节。

prompt要描述目标（"获取""调研""了解"），不要用暗示具体手段的动词（"搜索""爬取"），让子Agent自主判断最佳获取方式。

### 信息来源优先级

一手来源优于二手来源，多个媒体引用同一个错误会造成循环印证假象：

| 信息类型 | 一手来源 |
|---------|---------|
| 产品更新/技术决策 | 官方博客、GitHub Release Notes、创始人推文 |
| 融资/商业数据 | 公司官方公告、SEC/工商文件 |
| 用户口碑 | GitHub Issues、Reddit讨论、Twitter/X、知乎帖子 |
| 行业分析 | 权威媒体原创报道（非转载）、微信公众号（如36kr, 亿欧） |
| 学术/技术原理 | arXiv论文（`export.arxiv.org/api/query`）、Google Scholar、学术会议论文集 |

### 信息充分性自检

搜索完成后检查：
- 纵向：能讲出一个完整的故事吗？有没有明显的信息断层？
- 横向：竞品列表完整吗？有没有遗漏主要玩家？每个竞品的信息够做对比吗？
- 来源：关键事实有可靠来源支撑吗？有没有只靠单一来源就下判断的？

信息不够就再补搜。不要凑合。

---

## CEO级别战略简报的特别要求

当研究的最终产物是为C级高管（如CEO）准备的决策驱动型备忘录时，标准需要显著提高。这不仅仅是一份研究报告，而是一份旨在推动决策的战略文件。

### 核心原则

- **驱动决策，而非仅提供信息**：目标不是被动地呈现研究结果，而是利用研究来构建一个强有力的论点，迫使听众做出决策。语气应是高级合伙人提出建议，而不是初级顾问请求许可。
- **量化支撑**：每一个关键论点都必须由数据支撑。报告必须包含做出商业决策所需的经济分析（例如，客户获取成本CAC、生命周期价值LTV、投资回报周期）。
- **技术和运营的可信度**：提案必须显示出对客户现有技术栈和运营现实的深刻理解。必须在被问到之前就回答“这个如何与我们现有的系统集成？”
- **解决核心难题**：文件必须直接面对并提供具体的、可扩展的解决方案来解决已知的“交易破坏者”问题（例如，渠道冲突、政治风险），而不仅仅是承认它们或在试点项目中回避它们。

### 结构和内容

对于此类高风险任务，应参考 `references/ceo_briefing_template.md` 中详细的结构和质量门控。该模板包含了 Executive Summary, Economic Case, Anti-Conflict Mechanisms, IT Integration Architecture, และ Seven Recommendations for Decision 等关键部分。

### 禁用的短语和语气

为保持高级合伙人的语气，应避免使用营销性过强或听起来像初级顾问的短语。例如：
- **禁止**: "treasure trove", "gold mine", "ace in the hole", "unfair advantage" (可以使用这个概念，但不要用这个短语), "transform from X into Y"。
- **避免**: 任何只提出“这是一个关键问题”而不去回答它的句子。要么回答，要么删除。

## CEO级别战略简报的特别要求

当研究的最终产物是为C级高管（如CEO）准备的决策驱动型备忘录时，标准需要显著提高。这不仅仅是一份研究报告，而是一份旨在推动决策的战略文件。

### 核心原则

- **驱动决策，而非仅提供信息**：目标不是被动地呈现研究结果，而是利用研究来构建一个强有力的论点，迫使听众做出决策。语气应是高级合伙人提出建议，而不是初级顾问请求许可。
- **量化支撑**：每一个关键论点都必须由数据支撑。报告必须包含做出商业决策所需的经济分析（例如，客户获取成本CAC、生命周期价值LTV、投资回报周期）。
- **技术和运营的可信度**：提案必须显示出对客户现有技术栈和运营现实的深刻理解。必须在被问到之前就回答“这个如何与我们现有的系统集成？”
- **解决核心难题**：文件必须直接面对并提供具体的、可扩展的解决方案来解决已知的“交易破坏者”问题（例如，渠道冲突、政治风险），而不仅仅是承认它们或在试点项目中回避它们。

### 结构和内容

对于此类高风险任务，应参考 `references/ceo_briefing_template.md` 中详细的结构和质量门控。该模板包含了 Executive Summary, Economic Case, Anti-Conflict Mechanisms, IT Integration Architecture, และ Seven Recommendations for Decision 等关键部分。

### 禁用的短语和语气

为保持高级合伙人的语气，应避免使用营销性过强或听起来像初级顾问的短语。例如：
- **禁止**: "treasure trove", "gold mine", "ace in the hole", "unfair advantage" (可以使用这个概念，但不要用这个短语), "transform from X into Y"。
- **避免**: 任何只提出“这是一个关键问题”而不去回答它的句子。要么回答，要么删除。

---

## 第二步：纵向分析（Diachronic / Longitudinal）

沿时间轴，完整还原研究对象从诞生到现在的发展全貌。这是报告的主体部分，篇幅应该最重。

### 内容要求

**起源追溯**：它诞生的背景是什么？基于什么技术/理念/需求而来？创始团队或核心推动者是谁？这些人之前做过什么，为什么是他们来做这件事？当时的行业环境是什么样的？有没有某个关键事件或灵感直接促成了它的诞生？

**诞生节点**：明确的首次发布/成立/提出时间，最初的形态和定位，跟现在有什么不同。

**演进历程**：从诞生到现在，按时间顺序梳理所有关键节点。包括但不限于：重大版本更新、融资事件、团队变动、战略转型、技术架构变化、用户规模里程碑、重大合作或收购、公关危机或争议事件。

**决策逻辑**：在每个关键节点上，尽可能还原决策背后的原因。为什么选了A而不是B？当时面对的约束条件是什么？哪些早期决策"锁定"了后来的发展方向、难以逆转？什么机制让它越走越深（网络效应、生态绑定、技术栈选择等）？

**阶段划分**：把整个历程自然分为几个阶段（萌芽期、快速增长期、转型期等），每个阶段有核心特征和核心矛盾。

### 篇幅

6000-15000字。历史越长、节点越多的对象靠近上限，新生事物靠近下限。核心原则是把故事讲完整、讲透，每个关键节点都值得展开，不要为了压缩而跳过重要细节。宁可写长写细，也不要蜻蜓点水。

---

## 第三步：横向分析（Synchronic / Cross-sectional）

以当前时间点为切面，将研究对象与同赛道的竞品/同类进行全面对比。

### 首先判断竞品情况

分三种场景处理：

**场景A：无直接竞品。** 如果研究对象是全新品类或独占性极强的领域，跳过逐一对比，改为分析：它为什么没有竞品？是品类太新、壁垒太高、还是市场太小？未来最可能从哪个方向冒出竞争者？有没有间接替代方案或上一代解决方式可以参照？

**场景B：少量竞品（1-2个）。** 逐一深入对比，每个竞品展开详细分析。

**场景C：竞品充分（3个及以上）。** 选取最具代表性的3-5个进行对比，其余简要提及。

### 对比维度

根据研究对象的类型灵活调整，但至少覆盖以下方面：

**核心差异对比**：技术路线/核心方法论/底层逻辑、产品形态/商业模式/组织结构、目标用户/受众/适用场景、核心优势与明显短板、定价策略/资源投入/规模体量。

**用户视角**：每个竞品的真实用户口碑如何？社区评价、使用体验中被提及最多的优点和槽点分别是什么？用户实际的使用方式和官方定位有没有偏差？对比不要写成参数对照表的文字版，要讲清楚每个竞品「活成了什么样」，用户选它的真实理由是什么。

**生态位分析**：在整个赛道的版图中，研究对象占据什么位置？填补了什么空白，还是在跟谁正面竞争？当前格局是百花齐放、两强争霸、还是一家独大？

**趋势判断**：基于横向对比，研究对象在竞争格局中的走向是什么？机会和风险各是什么？

### 篇幅

3000-10000字。场景A控制在3000字左右，场景C每个主要竞品至少展开1500字以上的独立分析，不要一笔带过。

---

## 第四步：横纵交汇洞察

这是整篇报告的精华段。把纵向发展脉络和横向竞争格局结合起来，给出综合性的、新的判断。不要写成前面内容的缩写版。

需要回答的核心问题：

1. **历史如何塑造了当下的竞争位置**：纵向历程中的哪些决策和事件，决定了它今天在横向对比中的位置？
2. **竞品的纵向对比**：如果把主要竞品也放到时间线上看，它们的起源和演变路径有什么不同？这些不同如何导致了今天各自的特点？
3. **优势的历史根源**：今天的每个核心优势，能追溯到历史上的哪个节点或决策？
4. **劣势的历史根源**：今天的每个核心劣势，能追溯到哪个历史决策？当初的「好决策」有没有变成今天的包袱？
5. **未来推演**：基于纵向趋势和横向竞争格局，给出三个剧本——最可能的、最危险的、最乐观的，每个剧本要有逻辑支撑。

### 篇幅

1500-3000字。

---

## 写作风格

这不是一份冷冰冰的咨询报告，而是一篇让人能从头读到尾的深度研究。写作风格需要在「研究报告的严谨」和「卡兹克的可读性」之间找到平衡点。

### 从卡兹克文风中借鉴的核心元素

以下风格元素直接应用到报告写作中（详细定义请参考 khazix-writer skill）：

**节奏感**：句子时长时短，段落之间跳跃自然。不要每段都一样长，一句话自成一段制造重量感的技巧可以用。好的节奏像波动，每次围绕主线偏出去一点，再用一句「扣主线句」拉回来。

**叙事驱动，不是罗列驱动**：纵向部分要有故事弧线，有起承转合。比如一个产品为什么在某个时间点突然爆发，背后的铺垫是什么，转折是什么。不要写成"2023年1月发布了A，2023年3月发布了B"这种流水账。

**知识是「聊着聊着顺手掏出来」的**：在讲述过程中自然地带出背景知识，不要「下面我来给大家科普一下」。

**敢下判断**：鼓励给出观点和洞察，但每个观点必须有事实支撑。先摆事实，再给判断。是推测的明确标注。表达判断时用「我觉得」「我的判断是」这种承认主观性的姿态，而不是居高临下的定论。

**层层剥开的修辞**：不直接讲结论，用"现象→表面解释→更深的追问→核心洞察"的方式展开。让读者参与到思考过程中。

**文化升维**：在交汇洞察部分，连接到更大的文化/哲学/历史参照物。不是硬凑的升华，是「聊着聊着自然想到了」的感觉。

**回环呼应**：开头或纵向部分埋的细节和钩子，在交汇洞察或结尾callback回来。前后因果的闭合感，是让报告从「信息流」变成「作品」的关键。

### 不从卡兹克文风中借鉴的元素

以下元素适合公众号文章但不适合研究报告，需要克制：

- **过强的口语化**：报告可以有聊天感，但不要满篇「这玩意」「不是哥们」「太牛逼了」。偶尔点缀可以，但密度要比公众号文章低很多。
- **去小标题化**：公众号文章追求一口气顺下来不加小标题。研究报告不一样，1-3万字的内容如果没有清晰的结构和导航，读者会迷路。报告需要清晰的章节结构。
- **标点禁令可以放松**：公众号文章禁用冒号和破折号。研究报告中可以正常使用，因为报告需要的是信息传达效率。但「」的使用习惯可以保留。
- **固定尾部**：不要加公众号的三连/星标尾部。

### 绝对禁区（依然适用）

以下AI味标记无论什么文体都要避免：
- 套话："首先...其次...最后"、"综上所述"、"值得注意的是"、"不难发现"
- 空洞形容词："赋能"、"抓手"、"打造闭环"
- 教科书开头："在当今AI快速发展的时代"、"随着技术的不断进步"
- 高频踩雷词："说白了"、"意味着什么？"、"这意味着"、"本质上"、"换句话说"、"不可否认"
- 空泛工具名：不说"AI工具"、"某个模型"，要说具体名字
- 编造场景：如果某个信息搜不到，诚实标注「该信息暂缺」，绝不编造

**引用规范**：所有外部声明、数据、或引用观点必须使用脚注（`[^1]`）进行明确引用。在报告末尾的“信息来源”或独立的脚注部分，必须提供完整的URL和访问日期。禁止使用模糊的、主题性的引用，如`[来源, 年份]`。

**引用规范**：所有外部声明、数据、或引用观点必须使用脚注（`[^1]`）进行明确引用。在报告末尾的“信息来源”或独立的脚注部分，必须提供完整的URL和访问日期。禁止使用模糊的、主题性的引用，如`[来源, 年份]`。

### 用人话写

避免咨询公司式的套话和空洞概括。用具体的细节和例子代替概GaiKuo性陈述。比如不要写「该公司在这一阶段实现了快速增长」，而要写「从2024年中期的1000万美元ARR到2025年底的10亿美元，增长曲线几乎是垂直的」。

---

## 第五步：生成最终交付物

核心产出是一份完整的Markdown文档。最终的交付格式可以根据用户需求灵活调整。

## 第五步：生成最终交付物

核心产出是一份完整的Markdown文档。最终的交付格式可以根据用户需求灵活调整。

### 默认方式：生成PDF报告

默认情况下，使用本Skill自带的 `scripts/md_to_pdf.py` 脚本将Markdown转为排版精美的PDF。

#### 转换流程

1.  **先完成Markdown稿件**：将完整报告写为标准Markdown格式，保存为 `[研究对象]_横纵分析报告.md`
2.  **安装依赖**（如未安装）：`pip install weasyprint markdown --break-system-packages`
3.  **运行转换脚本**：
   ```bash
   python [skill目录]/scripts/md_to_pdf.py input.md output.pdf --title "研究对象名称" --author "数字生命卡兹克"
   ```
4. 脚本会自动生成中间HTML文件（便于调试）和最终PDF

### 其他格式：使用 Pandoc 转换为 Word (.docx) 等

如果用户需要 `.docx` 或其他格式，`pandoc` 是一个强大的备选方案。在完成Markdown稿件后，可使用以下命令转换：

```bash
# 基本转换
pandoc -s final_report.md -o final_report.docx

# 使用自定义模板进行高级格式控制
# pandoc -s final_report.md -o final_report.docx --reference-doc=template.docx
```
这种灵活性对于满足特定需求（如商业简报）至关重要。

### 脚本内置的排版规范

如果用户需要 `.docx` 或其他格式，`pandoc` 是一个强大的备选方案。在完成Markdown稿件后，可使用以下命令转换：

```bash
# 基本转换
pandoc -s final_report.md -o final_report.docx

# 使用自定义模板进行高级格式控制
# pandoc -s final_report.md -o final_report.docx --reference-doc=template.docx
```
这种灵活性对于满足特定需求（如商业简报）至关重要。

### 脚本内置的排版规范

`md_to_pdf.py` 已内置完整的CSS排版方案，无需手动调整：

- **页面**：A4，页边距上25mm/左右20mm/下20mm
- **封面页**：自动生成，包含标题（28pt深蓝色）、副标题「横纵分析法深度研究报告」、作者信息、装饰分隔线
- **配色**：H1标题=#1a5276深蓝、H2=#1e8449绿色、H3=#2e86c1浅蓝、H4=#5b2c6f紫色，正文=#2c3e50深灰
- **字体**：CSS fallback链 `"Droid Sans Fallback", Helvetica, Arial, sans-serif`，自动处理中英文混排
- **正文**：10.5pt，行距1.75，两端对齐，孤行/寡行控制
- **引用块**：左侧3pt深蓝竖线 + 浅灰背景
- **表格**：全宽、深蓝表头白字、斑马纹行
- **页眉**：「报告标题 | 横纵分析法深度研究报告」（首页不显示）
- **页脚**：「第 X 页」（首页不显示）
- Markdown的第一个H1会被自动提取为封面标题，正文中不会重复出现

### Markdown写作注意事项

为了让脚本正确解析并生成最佳PDF效果：

- 第一行用 `# 标题` 作为报告标题（会自动用于封面）
- 紧接标题后可用 `> 研究时间：... | 所属领域：... | 研究对象类型：...` 格式写元信息行，会被提取到封面
- 用 `##` 作为主要章节标题（纵向分析、横向分析、横纵交汇等）
- 用 `###` 和 `####` 作为子章节
- 表格使用标准Markdown表格语法
- 引用使用 `>` 语法
- 加粗使用 `**文本**`

### 末尾内容

在Markdown稿件末尾加上：
- **信息来源**：所有引用的来源清单，标注URL和访问时间

### 报告结构模板

```
封面页

目录

一、一句话定义
[用一句话说清楚这个东西是什么]

二、纵向分析：从诞生到当下
[完整的纵向叙事，6000-15000字]

三、横向分析：竞争图谱
[横向对比分析，3000-10000字]

四、横纵交汇洞察
[交叉分析和未来推演，1500-3000字]

五、信息来源
[所有引用的来源列表]
```

### 文件命名和交付

PDF文件命名为 `[研究对象名称]_横纵分析报告.pdf`，保存到用户的工作目录中。

对于CEO级别的战略简报，可以参考 `references/ceo_briefing_template.md` 的结构和格式要求，并根据用户需求（如输出为 .docx）进行调整。

---

## 不同研究对象类型的适配

核心原则不变（纵向追时间深度，横向追同期广度），但侧重点不同：

**研究产品时**：纵轴重点关注版本迭代、技术路线演变、用户增长曲线、关键产品决策；横轴重点关注功能对比、性能对比、用户体验、定价。

**研究公司时**：纵轴重点关注创始团队、融资历程、战略转向、组织变革、关键人事变动；横轴重点关注商业模式差异、市场份额、营收对比、组织架构差异。

**研究概念时**（技术范式、商业模式、文化现象）：纵轴重点关注概念的起源（谁提出的、基于什么理论/需求）、如何流行起来、经历了哪些争论和演变；横轴重点关注与相近概念的区别、各自适用场景、不同阵营的论证。

**研究人物时**：纵轴重点关注个人经历、职业轨迹、关键决策、成长曲线、公开言论变化；横轴重点关注与同领域其他人物的对比（做事方式、风格、成就、影响力、路线选择差异）。

---

## 篇幅总览

| 部分 | 字数范围 | 说明 |
|-----|---------|------|
| 纵向分析 | 6,000 - 15,000字 | 报告主体，不要蜻蜓点水 |
| 横向分析 | 3,000 - 10,000字 | 视竞品数量调整 |
| 横纵交汇 | 1,500 - 3,000字 | 精华段，给出新判断 |
| **全文总计** | **10,000 - 30,000字** | 不要怕长，深度和完整度是价值所在 |

---

## 质检清单
### 质检清单

交付前自检：

- [ ] **完整性**：是否严格执行了所有计划中的搜索步骤？有没有遗漏任何一个（例如，特定的社交媒体或数据库搜索）？在开始写作之前，必须确认所有规划的信息收集动作都已完成。
- [ ] 纵轴是叙事故事体？读起来有因果逻辑和时代脉络？不是年表流水账？
- [ ] 创始人/发起者的背景和动机有足够深度？
- [ ] 每个关键节点都展开写了，没有为了压缩而跳过重要细节？
- [ ] 决策逻辑有还原？不只是「发生了什么」，还有「为什么这么选」？
- [ ] 横轴的竞品场景判断正确（A/B/C）？竞品分析够深？
- [ ] 用户口碑部分引用了真实用户的声音？不只是官方宣传？
- [ ] 横纵交汇产出了新的判断，不是前面内容的缩写版？
- [ ] 未来推演的三个剧本都有逻辑支撑？
- [ ] 写作风格有节奏感、有可读性？不是冷冰冰的咨询报告？
- [ ] 没有触犯绝对禁区里的任何一条？
- [ ] 所有关键事实标注了信息来源？
- [ ] 搜不到的信息诚实标注了「暂缺」，没有编造？
- [ ] PDF排版美观、结构清晰、可读性好？
- [ ] 总字数在 10,000-30,000 字的范围内？

---

### 质检清单

## 质检清单
### 质检清单

交付前自检：

- [ ] **完整性**：是否严格执行了所有计划中的搜索步骤？有没有遗漏任何一个（例如，特定的社交媒体或数据库搜索）？在开始写作之前，必须确认所有规划的信息收集动作都已完成。
- [ ] 纵轴是叙事故事体？读起来有因果逻辑和时代脉络？不是年表流水账？
- [ ] 创始人/发起者的背景和动机有足够深度？
- [ ] 每个关键节点都展开写了，没有为了压缩而跳过重要细节？
- [ ] 决策逻辑有还原？不只是「发生了什么」，还有「为什么这么选」？
- [ ] 横轴的竞品场景判断正确（A/B/C）？竞品分析够深？
- [ ] 用户口碑部分引用了真实用户的声音？不只是官方宣传？
- [ ] 横纵交汇产出了新的判断，不是前面内容的缩写版？
- [ ] 未来推演的三个剧本都有逻辑支撑？
- [ ] 写作风格有节奏感、有可读性？不是冷冰冰的咨询报告？
- [ ] 没有触犯绝对禁区里的任何一条？
- [ ] 所有关键事实标注了信息来源？
- [ ] 搜不到的信息诚实标注了「暂缺」，没有编造？
- [ ] PDF排版美观、结构清晰、可读性好？
- [ ] 总字数在 10,000-30,000 字的范围内？
