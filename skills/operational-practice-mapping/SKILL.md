---
name: operational-practice-mapping
description: |
  Deep-dive into how industry peers actually execute a specific operational practice —
  customer acquisition, dealer management, pricing, fulfillment, after-sales, lead routing,
  CRM, channel mix, anti-poaching mechanisms, retention motions, anything execution-level.
  Activate when the user asks "how do peers X / Y / Z handle <operational practice>" or
  "benchmark <target>'s <practice> against the industry" or "what's the playbook for <practice>
  in <industry>" — i.e., they want execution-level depth, not positioning/market-structure.
  For positioning or market structure, use `competitive-analysis` instead.

  Produces a peer × practice matrix with evidence-tagged entries, per-peer and per-practice
  summaries, H/M/L effectiveness ratings with basis, open questions, and a numbered sources
  list. Works standalone or as Phase 04 of a multi-phase CDD workflow (see COMPOSITION.md
  for workflow-mode behavior).
metadata:
  origin: claude-code/operational-practice-mapping
  created: "2026-05-20"
  companion-doc: COMPOSITION.md
---

> 🔑 **Bring your own search backend.** This skill researches the live web via **Tavily / Exa (MCP)** and/or the `agent-reach` skill — none of which ship with keys here. Configure **your own** keys first (see the repo README), or the research steps will come up empty.

# operational-practice-mapping — Peer Practice Deep-Dive

This skill maps **how peers actually do something** at the execution level — not how they're
positioned in the market, not their financials, not their org charts. The unit of analysis
is a **practice** (e.g., "lead generation from existing customer base," "anti-`飞单` enforcement
mechanism," "end-of-contract retention motion") and the deliverable is a **peer × practice
matrix** with evidence-tagged entries.

## When to activate

YES — activate when the user asks any of:

- "How do <peer A>, <peer B>, <peer C> handle <operational practice>?"
- "Benchmark <target>'s <practice> against the industry"
- "What's the playbook for <practice> in <industry>?"
- "Deep dive into how <peer> does <operational thing>"
- "Map peer practices for <area> across <these companies>"

NO — these belong to other skills:

- "Who are the competitors to <target>?" → `competitive-analysis` (positioning, market map)
- "Where is <target> falling short?" → not yet built (target-diagnosis, phase 05)
- "What should <target> do?" → not yet built (strawman-recommendation, phase 06)
- "Build me a deck of …" → after this skill outputs its markdown, hand off to `pptx-author` or `md-to-docx`

## What this skill is NOT for

- **Not a deck builder.** Output is markdown. Deck rendering is a separate concern handed
  off to `pptx-author` (PPT) or `md-to-docx` (Word). The existing `competitive-analysis`
  skill bakes PPT into the analysis — do NOT repeat that mistake here.
- **Not a positioning analysis.** If the question is about market share, growth rate,
  segment definition, or 2×2 positioning, route to `competitive-analysis`.
- **Not financial benchmarking.** P&L deltas, capital efficiency, unit economics — use
  `comps-analysis` for that.

---

## 🤖 Consulting-pod mode (worker context)

> **If you are running as a consulting-pod Junior worker (you'll see this in your kanban task body — lane spec, research question, peer set, target organization), skip the interactive Phase 1 and produce the Phase 8 markdown artifact directly. Phase 1's `ask_user_question` is for standalone use; the pod has already scoped the engagement.**

### What the pod has already given you

The pod has already:
- Scoped the engagement (in `01-pm-dissection.md` and `swarm-spec.json` in the engagement folder)
- Defined the lane's research question, target organization, peer set, geographic constraints, and the specific operational practice to map
- Selected this skill (`operational-practice-mapping`) because the lane is about execution-level peer benchmarking — not positioning, not financials

Do not call `ask_user_question` — the pod is non-interactive. If anything in the kanban task body is ambiguous (e.g., peer set says "the usual peers"), proceed with reasonable defaults and surface the assumption in the `## Open questions` section of your output.

### Pod-mode workflow (condensed)

Skip Phase 1 (scoping is already done). Run **Phase 2 (source-routing) → Phase 3 (per-peer research) → Phase 4 (matrix) → Phase 5 (per-peer summaries) → Phase 6 (per-practice summaries) → Phase 7 (effectiveness ratings) → Phase 8 (output)** as documented below.

### Pod-mode output schema

Write to `<engagement_folder>/02-evidence-L<lane_id>.md` using the Phase 8 schema below. The matrix (Phase 4), evidence-tier discipline (Phase 3), and H/M/L ratings with named basis (Phase 7) are the load-bearing artifacts — the pod's Director synthesizer relies on them. Do not skip them.

**Universe-statement requirement in pod mode** (additive to the existing Phase 1 peer-set guidance): Add a `## Peer universe` section near the top of your evidence file declaring:
> "The peer universe for this practice contains N peers, selected by [criterion: direct competitor of target / leading executor of this practice / structurally comparable / regulatory peer]. The N peers are: [list]. Actively excluded with reason: [name + one-sentence reason per excluded peer]."

This catches the "missed an obvious peer" failure mode without requiring a hardcoded peer count — peer universe is industry-determined, not skill-determined.

### Artifact non-degeneracy rules (mandatory in pod mode)

**The peer × sub-aspect matrix is 2D by definition.** Each axis must have ≥2 distinct levels:
- ≥2 peers (a single-peer "matrix" is a case study, not a peer comparison)
- ≥2 sub-aspects (a single-aspect "matrix" is a description, not an execution mapping)

Single-axis output → submit the matrix as `[missing — could not produce a 2D peer × sub-aspect mapping because <specific reason: only one peer disclosed practice / only one sub-aspect surfaced consistently>]`. Do NOT produce a single-row or single-column table and label it complete.

Per Phase 4 existing guidance: sub-aspects where ALL peers behave identically do no analytical work. Cut them or replace with sub-aspects that surface variation. If the matrix has multiple sub-aspect columns but all show identical-peer-behavior, the matrix is also degenerate — peers might as well be one row.

**H/M/L effectiveness ratings (Phase 7) — named basis is mandatory per cell.** H without a specific outcome metric cited inline → demote to M with the qualitative basis stated. "It works well" is not basis; a named metric or named multi-source consistency is basis.

### Skip in pod mode

- `ask_user_question` (Phase 1)
- The "Workflow-mode" file-presence detection (pod uses different conventions — your scope comes from the kanban task body, not `../01-scoping/state.md`)
- Hand-off to `pptx-author` / `md-to-docx` (the pod's Director and render phase handle deliverable formatting)

Everything else in this skill applies as written. The 5-tier evidence trust system, the matrix sub-aspect discipline, the H/M/L rating basis requirement, the anti-patterns — all remain in force.

---

## Phase 1 — Scope the mapping (always)

Use `ask_user_question` to pin down the four scoping dimensions in one round (the tool
allows up to 4 questions):

1. **Target** — Which organization is the "from-the-perspective-of"? (May be empty —
   purely external benchmarking is valid; the matrix then has no protagonist.)
2. **Practice to map** — One specific operational dimension. If the user is vague
   ("how peers do CRM"), narrow it: CRM is too broad — is it lead capture, lead
   routing, lifecycle marketing, retention motions, or repeat-purchase mechanics?
   Pick ONE practice per skill run.
3. **Peer set** — Which companies are in scope? Use exactly the names the user gives.
   If they say "the usual peers," propose a list and confirm.
4. **Geographic / regulatory constraints** — Where does the target operate? This
   drives source-routing (see Phase 2). Also surfaces regulatory anchors that
   matter for the practice (e.g., PIPL for China consumer-data practices).

If the user supplies an Excel/CSV with peer data, confirm column-to-field mapping
before research begins. Source-file values are authoritative — do not recompute or
re-round.

### Workflow-mode shortcut

Before asking, check the parent directory for upstream state files:

- `../01-scoping/state.md` → Target, audience, decision context
- `../02-market-context/state.md` → Geographic scope, regulatory constraints
- `../03-competitive-structure/state.md` → Confirmed peer set

If these exist, **load them and skip the matching questions**. Phase 1 then becomes
a *confirmation* round ("we have X from scoping; please confirm before proceeding"),
not a *discovery* round. See `COMPOSITION.md` for the workflow contract.

---

## Phase 2 — Source-routing

Different geographies and platforms require different source-gathering paths. This
skill delegates source-routing to `agent-reach` — do not re-implement.

| Geography / Platform | Route via |
|---|---|
| China (consumer / auto / financial) | `agent-reach` → 小红书, 微博, 知乎, 公众号, 雪球 |
| China (B2B / industrial) | `agent-reach` → 公众号, 知乎, 行业垂直网站 |
| Global Western | Web search (default), industry press, analyst reports |
| Career / org / hiring signals | `agent-reach` → LinkedIn |
| Developer / technical (API, SDK, infra) | `agent-reach` → GitHub, dev forums |
| Investor disclosures | Web search; annual reports; earnings transcripts |

Route ONCE per peer × practice cell. Cache the routing decision in the matrix
under the `evidence-source` column so downstream phases (and re-runs) don't
re-route from scratch.

---

## Phase 3 — Per-peer research per practice

For each peer in the set, gather evidence about **how that peer executes the
practice**. Evidence types ranked by trust:

1. **Public statements with mechanism detail** — earnings transcripts where the
   CFO/CEO describes the actual motion ("our retention rep team calls 90 days
   before contract end and presents a pre-approved loyalty bundle")
2. **Operational case studies** — analyst write-ups, vendor case studies that
   describe the workflow (e.g., a SCRM vendor publishing a GAC Toyota deployment
   walkthrough)
3. **Job descriptions / hiring patterns** — what the peer is staffing tells you
   what they're operationally building (LinkedIn via agent-reach)
4. **Customer-side observations** — Reddit / 小红书 / consumer review threads
   describing the actual customer experience
5. **Inference from product surface area** — apps, web portals, in-product
   features that imply backend processes

Tag each evidence point with:
- **Trust tier** (1–5 per above ranking)
- **Source URL + date** (for the sources list)
- **Quote or paraphrase** (the actual content extracted)

If a peer × practice cell has only tier-4 / tier-5 evidence, flag it as
`weak-evidence` in the matrix — downstream phases need to know what's confirmed
vs. inferred.

---

## Phase 4 — Build the master matrix

The matrix is the canonical artifact. One row per peer. One column per
sub-aspect of the practice (decompose the practice into 4–8 sub-aspects that
make peer differences visible).

Example for practice = "End-of-contract retention motion":

| Peer | Trigger mechanism | Outreach channel | Offer bundle | Hand-off to dealer | Anti-poaching | Effectiveness signal | Evidence |
|---|---|---|---|---|---|---|---|
| SAIC-GMAC | Loan end-date predictive ping | 66 Online app push + SMS | Pre-approved rate + RV guarantee | Dealer fulfillment with commission lock | Quote-ID locked at offer | 4M users by 2020, 6M by 2022 | T1 + T2 (3 sources) |
| GAC Toyota | Salesperson manual via SCRM | WeCom 1:1 to consultant | Standard finance + extended svc | Dealer-led the whole time | Lead persists when SP leaves | Deployed at 500+ dealers | T2 + T3 (2 sources) |
| BYD | App-side lifecycle automation | App push + WeCom community | Battery upgrade + loyalty rate | OEM-locked lead in central system | Central system enforces | 60% captive pen, EOY 2023 | T1 + T4 (4 sources) |
| NIO | App + community thread monitoring | App + NIO House event | "User enterprise" bundle | No dealer hand-off — direct | Structurally impossible | High repurchase, brand-cited | T1 + T2 (3 sources) |

Sub-aspect choice matters more than peer choice. The sub-aspects are what surface
**transferable patterns** — pick them to highlight where the peers diverge in
ways that matter for the target. If all four peers do something the same way,
that sub-aspect probably isn't doing analytical work; drop it.

---

## Phase 5 — Per-peer summaries

One structured paragraph per peer. Format:

> **<Peer name>** — <one-sentence positional anchor: what kind of player they
> are in the practice space>. <Two to three sentences on the mechanism: how
> the practice actually runs end-to-end>. <One sentence on what makes this
> hard to copy at the target: trust deficit, channel gap, capital intensity,
> structural mismatch>.

This is the artifact `05-target-diagnosis` will consume to identify which
peer's pattern is closest-transferable to the target's structural position.

---

## Phase 6 — Per-practice summaries

One paragraph per sub-aspect (column of the matrix). Format:

> **<Sub-aspect name>** — <one-sentence framing of why this sub-aspect
> matters operationally>. <Two to three sentences synthesizing the peer
> variations: who's leading, who's lagging, what the spread reveals>.
> <One sentence on the cost-to-implement curve: cheap-to-start, capex-
> heavy, requires-trust-rebuild, etc.>.

This is the artifact `06-strawman-recommendation` will use to phase the
recommendation (cheap practices first, expensive practices later).

---

## Phase 7 — Effectiveness ratings (H/M/L)

For each peer × sub-aspect, rate effectiveness:

- **H (High)** — Quantitative outcome evidence (CAC numbers, retention rates,
  penetration percentages) AND it's tied to this specific practice. Or:
  consistent qualitative reports from multiple independent sources.
- **M (Medium)** — Mechanism is clearly implemented and operating at scale,
  but outcome evidence is partial or proxy-based.
- **L (Low)** — Mechanism exists but evidence is thin, or it's been observed
  but not at scale.
- **N/A** — Practice not applicable to this peer (e.g., D2C peer has no
  "dealer hand-off" sub-aspect).

The basis (the *why* of the rating) must be cited inline next to the rating.
Don't rate H without naming the specific outcome metric.

---

## Phase 8 — Output

Write a markdown artifact with the schema below. In workflow mode, this
goes to `./state.md` in the current phase directory. In standalone mode,
ask the user where to save (or default to
`~/Desktop/operational-practice-mapping_<YYMMDD>.md`).

```markdown
# Operational Practice Mapping — <Practice> across <Peer Set>

## Handoff summary
[One paragraph: what was analyzed, the matrix's headline finding, what's
loaded for downstream phases.]

## Scope (confirmed)
- Target: <name or "external benchmarking, no protagonist">
- Practice mapped: <one-line description>
- Peer set: <list>
- Geography / constraints: <list>

## Matrix
[The Phase 4 master table, full markdown.]

## Per-peer summaries
### <Peer A>
<Phase 5 paragraph>

### <Peer B>
<Phase 5 paragraph>

(…etc.)

## Per-practice (sub-aspect) summaries
### <Sub-aspect 1>
<Phase 6 paragraph>

### <Sub-aspect 2>
<Phase 6 paragraph>

(…etc.)

## Effectiveness ratings
| Peer | <Sub-aspect 1> | <Sub-aspect 2> | … | Basis |
|---|---|---|---|---|
| <Peer A> | H | M | … | <citation> |

## Open questions
- <Things that need user confirmation or further research>
- <Cells where evidence was thin (tier-4/5 only)>

## Sources
1. <Title> — <URL> — <date>
2. …
```

In workflow mode, **also append** to:
- `<workflow-root>/sources.md` — all numbered sources, promoted up
- `<workflow-root>/open-questions.md` — append the open-questions section
- `<workflow-root>/decisions-log.md` — append a one-paragraph entry on what
  this phase concluded and why

---

## Composition & workflow integration

This skill is designed as Phase 04 of a six-phase CDD workflow. See
`COMPOSITION.md` (in this skill directory) for:

- The full six-phase architecture
- The shared state contract across phases
- How upstream phases (01-scoping, 02-market-context, 03-competitive-
  structure) populate this skill's Phase 1
- How downstream phases (05-target-diagnosis, 06-strawman-recommendation)
  consume this skill's output

Workflow-mode detection is by file presence — no orchestrator required.
The skill remains fully functional standalone.

---

## Anti-patterns to avoid

- **Don't try to do positioning AND practice mapping in one run.** They're
  different units of analysis; mixing them produces a deck that looks
  comprehensive but answers no specific question. Route positioning to
  `competitive-analysis`.
- **Don't pick sub-aspects where all peers behave identically.** Those
  sub-aspects do no analytical work. Cut them or replace with sub-aspects
  that surface variation.
- **Don't rate H without a named outcome metric.** "It works well" is not
  a basis; "60% captive penetration EOY 2023 per Q4 earnings" is.
- **Don't write the deck.** This skill outputs markdown. Hand off to
  `pptx-author` / `md-to-docx` for rendering. Keeping analysis and
  formatting separate is the whole point.
- **Don't ask for the target organization a second time** if `../01-scoping/
  state.md` already has it. Workflow mode = confirm, not re-discover.

---

## Sister skills

| Sister skill | Relationship |
|---|---|
| `competitive-analysis` | Positioning / market-structure deep-dive. Different unit of analysis. |
| `comps-analysis` | Financial / unit-economics benchmarking. Different evidence base. |
| `hv-analysis` | Historical / vertical-axis narrative. Provides "how peers got here" context. |
| `agent-reach` | Source-routing for China + social + dev + career platforms. |
| `md-to-docx` | Renders this skill's markdown output to Word. |
| `pptx-author` | Renders this skill's matrix + summaries to PowerPoint. |
| `commercial-diligence-scoping` (planned, phase 01) | Will provide upstream state for workflow mode. |
| `target-diagnosis` (planned, phase 05) | Will consume this skill's output. |
| `strawman-recommendation` (planned, phase 06) | Will consume this skill's output. |
