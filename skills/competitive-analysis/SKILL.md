---
name: competitive-analysis
description: Framework for building competitive landscape decks — market positioning, competitor deep-dives, comparative analysis, strategic synthesis. Use when the user asks for a competitive landscape, competitor analysis, peer comparison, market positioning assessment, strategic review, or investment memo deck. Also triggers on "who are the competitors to X", "benchmark X against peers", "build a market map", or any request to systematically evaluate competitive dynamics across an industry.
---

> 🔑 **Bring your own search backend.** This skill researches the live web via **Tavily / Exa (MCP)** and/or the `agent-reach` skill — none of which ship with keys here. Configure **your own** keys first (see the repo README), or the research steps will come up empty.

# Competitive Landscape Mapping

Build a complete competitive analysis deck. This is a two-phase process: gather requirements and get outline approval first, then build.

## 🤖 Consulting-pod mode (worker context)

> **If you are running as a consulting-pod Junior worker (you'll see this in your kanban task body — lane spec, framework lens, etc.), skip the interactive Phase 1/2 and produce the three mandatory artifacts below directly. Phase 1/2 are for direct user interaction; the pod has already scoped the engagement.**

### Mandatory output artifacts (all three required)

#### Artifact 1 — Per-competitor data card (BD/CDD-grade, 15 fields)

Universe-driven, no hardcoded quota. Industry structure determines N (4 in an oligopoly, 15 in a fragmented market — both fine).

State the universe explicitly:
> "The {market segment} contains N material players defined by [criterion: ≥X% market share / direct overlap with subject / strategic relevance]. The N players are: [list]."

Then, for **each** player in the universe, harvest against this 15-field BD/CDD schema. **Missing fields must be explicitly marked `[not surfaced — channels: X, Y, Z]`** — never silently omitted. The "[not surfaced]" markers tell the human consultant which fields to chase via paid databases.

Required fields per player:

| # | Field | What to capture |
|---|---|---|
| 1 | **Legal entity + parent / ownership** | Public ticker / private / family-owned / PE-backed; parent company + ownership %; entity registered in jurisdiction X |
| 2 | **Year of market entry** (or founding if local) | Entry year + entry mode (organic / JV / acquisition / franchise) |
| 3 | **Revenue** | Latest FY value with date (e.g., "RMB 9.47B (FY2023)") + source URL. If undisclosed: `[not disclosed — see Numbers we tried to find]` |
| 4 | **Store / outlet count** | Latest count + date (e.g., "9,650 outlets (Apr 2023)") + source URL |
| 5 | **Core products** | ≥3 named brand or SKU families |
| 6 | **Price band / price range** | Currency low–high with example SKUs (e.g., "RMB 50-400 per bottle — multivit 50ct entry, joint-care premium") |
| 7 | **Distribution channels** | Online (Tmall / JD / Douyin / WeChat-CRM / DTC website) and offline (own retail / pharmacy / mass-market / direct) |
| 8 | **Recent strategic moves (last 12 months)** | Funding rounds, M&A, new product launches, geo expansion, partnership announcements |
| 9 | **Management changes (last 12 months)** | C-suite changes, board changes, founder transitions — if traceable |
| 10 | **Litigation / regulatory / ESG flags** | Active lawsuits, regulator actions, ESG controversies (e.g., supply chain, labor, environmental) — if any traceable |
| 11 | **Expansion vs contraction trajectory** | Direction: aggressive expansion / steady / contraction / wind-down — with the evidence behind that call |
| 12 | **Strategic posture vs subject** | Direct competitor / adjacent / partner / irrelevant — and why |
| 13 | **Key strength** | One sentence + source URL |
| 14 | **Key vulnerability** | One sentence + source URL |
| 15 | **Open question for human follow-up** | The one thing about this competitor that would change the analysis if known (typically the thing you couldn't surface) |

Format each player as a structured card (multi-line) — NOT a single table row. A 15-field profile in a single row is unreadable. One H4 heading per player, then bulleted fields.

Example:

```markdown
**Yum China Holdings** (NYSE: YUMC; parent of KFC China + Pizza Hut China + Lavazza China)
- Legal entity + parent: Public (NYSE: YUMC), spun off from Yum! Brands 2016
- Year of market entry: 1987 (KFC opened first Beijing store)
- Revenue: USD 11.3B FY2024 (https://...10-K)
- Store count: 16,395 restaurants year-end 2024 (https://...)
- Core products: KFC, Pizza Hut, Taco Bell China (limited), Lavazza coffee, Huang Ji Huang
- Price band: RMB 25-120 per main meal (KFC); RMB 80-300 (Pizza Hut sit-down)
- Distribution: dine-in + delivery (90% digital orders); 25k+ stores via direct + franchised
- Recent strategic moves: Lavazza JV expansion 2024; share buyback program continued
- Management changes: Joey Wat (CEO since 2018, no recent change); CFO Andy Yeung announced retirement Q3 2024
- Litigation / regulatory / ESG: 2014 supply chain scandal historical; current ESG report Q4 2024
- Trajectory: aggressive expansion — guidance 20,000 stores by 2026
- Strategic posture vs subject: direct competitor (largest Western QSR in CN)
- Key strength: distribution depth + digital infrastructure (https://...)
- Key vulnerability: chicken-category concentration ~70% of KFC sales (https://...)
- Open question: gross margin trajectory in lower-tier cities — disclosed only in Q&A, not formal disclosures
```

Anything you cannot surface gets the `[not surfaced — channels: X, Y, Z]` marker, e.g., `Revenue: [not surfaced — channels searched: 公众号 (失败), 雪球 (data behind paywall), Exa (no recent SEC-style filing)]`.

#### Artifact 2 — Scored dimension matrix

A peer × dimension table:
- Rows: each player in the universe
- Columns: ≥7 dimensions relevant to the strategic question (NOT generic — pick dimensions the question demands: e.g., for VMS: Brand Equity / Pricing Power / Store Network / Digital Presence / Product Innovation / Profitability / Channel Mix / Regulatory Position)
- Cells: 1-5 score OR H/M/L OR a concrete value

#### Artifact 3 — Price-band × product-category positioning matrix

The 2D market map that shows where each player plays:

```
            | Product Cat A | Product Cat B | Product Cat C | Product Cat D
------------|---------------|---------------|---------------|---------------
Premium     | Brand X       | Brand Y       | Brand X, Z    |
Mid         | Brand X, Y    | Brand W       | Brand Z       | Brand V
Mass        | Brand W, V    | Brand V       |               | Brand U
Entry       |               | Brand U       | Brand U       | Brand U
```

- Rows: price bands (Premium / Mid / Mass / Entry — or what fits the market)
- Columns: product categories (e.g., for VMS: Multivitamin / Single-ingredient / Beauty-from-within / Joint & Bone / Probiotics / Specialty)
- Cells: brand names that play in that price-band × category cell

This artifact reveals market structure (white space, crowded segments, premium-only players, etc.) that the scored matrix alone misses.

### Methodology section requirement

Your evidence file's `## Methodology applied` section must explicitly reference:
1. How you arrived at the universe (search trail evidence)
2. Which scoring rubric you used for Artifact 2
3. How you mapped price bands for Artifact 3 (what currency thresholds delimit Premium / Mid / Mass / Entry)

### Artifact non-degeneracy rules (mandatory in pod mode)

**Artifact 3 (positioning matrix) is 2D by definition.** Each axis must have ≥2 distinct levels. A single-column matrix (one product category) or single-row matrix (one price band) is degenerate — the artifact has not been produced. Submit it as `[missing — could not decompose <X-axis or Y-axis name>]` with a one-line reason rather than as a 1-axis table. The column-count is determined by the market's actual category structure; enumerate every category that exists, don't pad or compress.

If product-category decomposition is genuinely unavailable for this market, switch the X-axis to a different competitive dimension (target user segment / brand-positioning archetype / distribution channel) — but the X-axis must still have ≥2 distinct levels. What CANNOT happen: a 1-column matrix labeled with the market's name.

**Artifact 2 (scored dimension matrix) is mandatory — non-skip.** If quantitative data is unavailable, downgrade cells to H/M/L with one-line basis per cell. A qualitative scoring rubric is acceptable; skipping the artifact and citing "data limitations" is not. Either produce H/M/L cells with stated basis OR submit as `[missing — qualitative scoring infeasible because <specific reason>]`. "Insufficient data" without naming the specific gap is rejected — name what's missing.

**Artifact 1 (per-competitor data cards) — partial population via `[not surfaced]` markers is allowed**, but every player named in the universe statement must appear as a card. Universe ↔ Cards is 1:1.

### Skip the interactive parts of Phase 1/2 when in pod mode

The pod has already:
- Scoped the engagement (in `01-pm-dissection.md` and `swarm-spec.json`)
- Defined the lane's research question and framework lens
- Selected the specialist skill (you)

Do not call `ask_user_question` — the pod is non-interactive. Go straight to research and produce the three artifacts.

---

## Environment check

This skill works in both the PowerPoint add-in and chat. Identify which you're in before starting — the mechanics differ, the workflow doesn't:

- **Add-in** — the deck is open live; build slides directly into it.
- **Chat** — generate a `.pptx` file (or build into one the user uploaded).

Everything below applies in both.

## Phase 1 — Scope the analysis

Competitive analysis means different things to different people. Before any research or slide-building, use `ask_user_question` to pin down what they actually want. Don't guess — a 20-slide peer benchmarking deck and a 5-slide market map are both "competitive analysis" and take completely different shapes.

Gather in one round if you can (the tool takes up to 4 questions):

- **Scope** — Single target company with competitors around it? Or multi-company side-by-side with no protagonist?
- **Competitor set** — Which companies are in scope? If the user names them, use exactly those. If they say "the usual suspects," propose a set and confirm.
- **Audience and depth** — Quick read for someone already in the space, or a full primer? This drives whether you need market sizing, industry economics, and history — or can skip to the comparison.
- **Investment context** — Do they need bull/base/bear scenarios and signposts? That's Step 9 below; skip it if this is a strategic review rather than an investment thesis.

If they've uploaded an Excel/CSV with competitor data, confirm which columns map to which metrics before you start pulling numbers. Source-file fidelity matters: use values exactly as given, don't recalculate or re-round.

## Phase 2 — Outline, approve, then build

**Do not create slides until the outline is approved.** Propose slide titles and one-line content notes, present them to the user, get a yes. A competitive deck is 10-20 slides of interlocking content — rebuilding because slide 4 was wrong is expensive. The outline is the cheap iteration point.

When proposing the outline, `ask_user_question` works well for the structural decisions: which positioning visualization (2×2 matrix / radar / tier diagram — Step 5 below), how to group competitors (by business model / segment / posture — Step 4). These are taste calls the user likely has an opinion on.

---

## Standards — apply throughout

### Prompt fidelity

When the user specifies something, that's a requirement, not a suggestion:
- **Slide titles and section names** — exact wording. If they say "Overview and Competitive Scope," don't swap in "FY2024 Competitive Landscape."
- **Chart vs. table** — not interchangeable. "Embedded chart" means a real chart object with data labels on the bars/slices, not a formatted table.
- **Complete data series** — if they list 7 competitors, include all 7. If they show 2015-2025, include every year.
- **Exact values and ratios** — "surpasses DoorDash 4:1, Lyft 8:1" means those ratios, not "7.6x Lyft."

### Source quality, when sources conflict

1. 10-Ks / annual reports (audited)
2. Earnings calls / investor presentations (management commentary)
3. Sell-side research (analyst estimates, useful for private company sizing)
4. Industry reports (McKinsey, Gartner — market sizing, trends)
5. News (recent developments only; verify against primary sources)

### Data comparability

- All competitor metrics from the same fiscal year; flag exceptions explicitly ("FY24" vs "H1 2024")
- Same metric definitions across competitors
- Convert to USD for international; note the exchange rate and date
- **Zero-Estimate Rule:** Missing data shows as "-" or "N/A". Do not use `[E]` to guess a metric. Every number must have a verifiable footnote.
- **Directional Anchoring:** If a specific number cannot be found after exhaustive search, tag it `[directional]` and explicitly state the comparable cited rate it is anchored to (e.g., "Rate assumed at 20% [directional], anchored to a reported 17-25% range per [source]").
- **Missing URL Fallback:** If you read multiple case studies but lost the exact URL during tool churn, use the honest fallback pattern: `[case study, on file] Source on file: searched query [query], multiple corroborating case studies regarding [topic], exact URL not preserved. Available on request.`
- Every number has a citation: "[Company] [Document] ([Date])"

### Design

- **Slide titles are insights, not labels.** "Scale leaders pulling away from niche players" — not "Competitive Analysis."
- **Signposts are quantified.** "Margin below 40%" — not "margins decline."
- **Ratings show the actual.** "●●● $160B" — not just "●●●."
- **Charts are real chart objects** — not text tables dressed up to look like charts.

**Typography** — set explicitly, don't rely on defaults:
- Slide titles: 28-32pt bold
- Section headers: 18-20pt bold
- Body text: 14-16pt (never below 14pt)
- Table text: 14pt
- Sources/footnotes: 14pt, gray
- Same element type = same size throughout the deck

**Charts:**
- Legend inside the chart boundary, not floating over the plot area
- Right-side legend for pies (≤6 slices), bottom legend for line/bar (≤4 series)
- More than 6 series → split into multiple charts or use a table
- Pie charts show percentages on slices, not just in the legend

**Tables:**
- Light gray header row, bold
- Right-align numbers, left-align text
- Enough cell padding that text doesn't touch borders

**Color:** 2-3 colors max. Muted — navy, gray, one accent. Same color meanings throughout.

### Executive Communication & Voice
- **Recommendations, not questions:** When framing open issues for executives (CEOs/C-suite), do not sound like a junior consultant asking permission. Present a clear recommendation, 2-4 sentences of evidence-backed reasoning, the accepted trade-off, and a specific Yes/No decision they must confirm or override.
- **Economic Cases:** Never use point estimates for financials (e.g., "CAC will be $50"). Use sensitivity tables (Bear/Base/Bull scenarios) where numbers actively flex based on explicit input ranges (e.g., margins, conversion rates).

### Banned AI Phrases (Scrub Before Delivery)
Never use: "comprehensive analysis", "critical need", "treasure trove", "gold mine", "ace in the hole", "unfair advantage" (describe the concept, don't use the phrase), "transform from X into Y", "strategic imperative", "leverage" (as a verb — use "use" or "activate"), "robust", "best-in-class", "unparalleled".

### What's strict vs. flexible

| Always | Case-by-case |
|---|---|
| Exact titles/sections when user specifies | Creative titles when they don't |
| Chart when user says chart; table when they say table | Visualization type when unspecified |
| Every competitor/data point they list | Number of competitors when unspecified |
| Exact values when specified | Rounding when precision unspecified |
| Titles fit without overflow | Number of competitor categories |
| No overlapping elements | Which dimensions to compare |

---

## Analysis workflow

### Step 0 — Industry-defining metrics

Before anything else: what 3-5 metrics does this industry actually run on? Use these consistently across every competitor.

| Industry | Key metrics |
|---|---|
| SaaS | ARR, NRR, CAC payback, LTV/CAC, Rule of 40 |
| Payments | GPV, take rate, attach rate, transaction margin |
| Marketplaces | GMV, take rate, buyer/seller ratio, repeat rate |
| Retail | Same-store sales, inventory turns, sales per sq ft |
| Logistics | Volume, cost per unit, on-time delivery %, capacity utilization |

Industry not listed — pick the metrics investors and operators benchmark on.

### Step 1 — Market context

Size, growth, drivers, headwinds. With sources.

Correct: "Embedded payments is $80-100B in 2024, growing 20-25% CAGR (McKinsey 2024)"
Wrong: "The market is large and growing rapidly"

### Step 2 — Industry economics

Map how value flows. Approach depends on industry structure:
- **Vertically structured** — value chain layers, typical margin at each
- **Platform/network** — ecosystem participants, value flows between them
- **Fragmented** — consolidation dynamics, margin differences by scale

### Step 3 — Target company profile

```
| Metric | Value |
|---|---|
| Revenue | $4.96B |
| Growth | +26% YoY |
| Gross Margin | 45% |
| Profitability | $373M Adj. EBITDA |
| Customers | 134K |
| Retention | 92% |
| Market Share | ~15% |
```

Multi-segment companies add a breakdown:

```
| Segment | Revenue | Rev YoY | Rev % | EBITDA | EBITDA YoY | Margin |
|---|---|---|---|---|---|---|
| Seg A | $25.1B | +26% | 57% | $6.5B | +31% | 26% |
| Seg B | $13.8B | +31% | 31% | $2.5B | +64% | 18% |
| Seg C | $5.1B | -2% | 12% | -$74M | -16% | -1% |
| Total | $44.0B | +18% | 100% | $6.5B* | - | 15% |
```
*Note corporate costs if applicable

### Step 4 — Competitor mapping

Group by whichever lens fits (this is a good `ask_user_question` decision if the user hasn't specified):
- By business model — platform / vertical / horizontal
- By segment — enterprise / SMB / consumer
- By posture — direct / adjacent / emerging
- By origin — incumbent / disruptor / new entrant

### Step 5 — Positioning visualization

| Type | When |
|---|---|
| 2×2 matrix | Two dominant competitive factors |
| Radar/spider | Multi-factor comparison |
| Tier diagram | Natural clustering into strategic groups |
| Value chain map | Vertical industries |
| Ecosystem map | Platform markets |

See `references/frameworks.md` for 2×2 axis pairs by industry.

### Step 6 — Competitor deep-dives

Two tables per competitor.

**Metrics:**
```
| Metric | Value |
|---|---|
| Revenue | $X.XB |
| Growth | +XX% YoY |
| Gross Margin | XX% |
| Market Cap | $X.XB |
| Profitability | $XXXM EBITDA |
| Customers | XXK |
| Retention | XX% |
| Market Share | ~XX% |
```

**Qualitative:**
```
| Category | Assessment |
|---|---|
| Business | What they do (1 sentence) |
| Strengths | 2-3 bullets |
| Weaknesses | 2-3 bullets |
| Strategy | Current priorities |
```

### Step 7 — Comparative analysis

```
| Dimension | Company A | Company B | Company C |
|---|---|---|---|
| Scale | ●●● $160B | ●●○ $45B | ●○○ $8B |
| Growth | ●●○ +26% | ●●● +35% | ●●○ +22% |
| Margins | ●●○ 7.5% | ●○○ 3.2% | ●●● 15% |
```

### Step 8 — Strategic context

M&A transactions (multiples, rationale), partnership trends, capital raising patterns, regulatory developments. See `references/schemas.md` for the M&A transaction table format.

### Step 9 — Synthesis

**Moat assessment** — rate each competitor Strong / Moderate / Weak on:

| Moat | What to assess |
|---|---|
| Network effects | User/supplier flywheel strength; cross-side vs same-side |
| Switching costs | Technical integration depth, contractual lock-in, behavioral habits |
| Scale economies | Unit cost advantages at volume; minimum efficient scale |
| Intangible assets | Brand, proprietary data, regulatory licenses, patents |

**Required synthesis elements:**
- Durable advantages (hard to replicate) — map to moat categories
- Structural vulnerabilities (hard to fix)
- Current state vs. trajectory

**For investment contexts** (skip if the Phase 1 scoping said no):

```
| Scenario | Probability | Key driver |
|---|---|---|
| Bull | 30% | Market share gains, margin expansion |
| Base | 50% | Current trajectory continues |
| Bear | 20% | Competitive pressure, margin compression |
```

---

## Quality checklist

Before finishing:

**Prompt fidelity**
- Slide titles match what the user specified, verbatim
- Charts where they said chart; tables where they said table
- Every competitor/year/data point they listed is present
- Exact values and formats as specified

**Data consistency**
- Source-file values extracted directly, not recalculated
- Same metric shows the same value on every slide it appears
- Same decimal precision as the source

**Layout**
- Titles fit without overflow
- No overlapping elements
- All text within containers, no clipping

**Content**
- Every number has a citation
- All metrics from the same fiscal period (or flagged)
- Slide titles state insights, not topics
- Charts are real chart objects

Run standard visual verification checks on every slide — this catches overlaps, overflow, and low-contrast text that don't show up when you're reading back the XML.
