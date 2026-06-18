# How `operational-practice-mapping` Composes With Future CDD Workflow Modules

A standalone note, not part of the SKILL.md itself. This documents how the skill is designed to plug into a larger preliminary-research / commercial-due-diligence workflow you build later.

---

## The skill is one node in a six-phase workflow

```
cdd-workflow/
├── 01-scoping/                  Define the engagement question
├── 02-market-context/           Size, dynamics, regulation, growth
├── 03-competitive-structure/    Who plays, how positioned
├── 04-operational-practice/     ← THIS SKILL (how peers actually execute)
├── 05-target-diagnosis/         Gaps and opportunities vs. peers
└── 06-strawman-recommendation/  The "so what" and decision asks
```

Each phase reads context from prior phases, writes output the next phase consumes. The skills can run independently (one-off engagement on a single phase) or in sequence (full CDD). They share a **state contract** — see below.

---

## What `operational-practice-mapping` reads from earlier phases

When run inside the workflow, the skill expects to find (and use) these from earlier-phase outputs, located at predictable paths:

| Read from | What | Used for |
|---|---|---|
| `01-scoping/state.md` | Engagement question, target organization, audience, decision being supported | Skill's Phase 1 scoping — skip re-asking what's already answered |
| `02-market-context/state.md` | Geographic scope, regulatory constraints, market sizing | Drives source-routing decisions (China → load agent-reach; financial-services → load PIPL / regulatory checks) |
| `03-competitive-structure/state.md` | Confirmed peer set with positioning rationale | Skill inherits this peer set; does not re-derive |

If these files don't exist, the skill falls back to its native Phase 1 scoping via `ask_user_question`. Standalone mode and workflow mode look identical to the user — the difference is whether prior context is auto-loaded.

---

## What `operational-practice-mapping` writes for later phases

The skill writes one canonical artifact at the end:

`04-operational-practice/state.md`

Contents (defined by the shared `skill-contract.md` your workflow root should hold):

1. **Matrix** — the master peer × practice matrix with evidence tags. Markdown table.
2. **Per-peer summaries** — one paragraph each, structured. Available to `05-target-diagnosis` to identify which peers' patterns are most transferable.
3. **Per-practice summaries** — one paragraph each, structured. Available to `06-strawman-recommendation` to construct the recommended operating model.
4. **Effectiveness ratings** — H/M/L scores with basis. The strawman builder uses these to prioritize what the target should adopt first.
5. **Open questions surfaced during research** — things that need confirmation from the user or further research. Available to `01-scoping` for any follow-up rounds.
6. **Sources** — numbered list, full URLs and dates. Promoted up to the workflow root `sources.md` so downstream phases don't re-cite the same things.

Format roughly:

```markdown
# 04-operational-practice/state.md

## Handoff summary
[One paragraph: what was analyzed, what the matrix surfaces, what's loaded for downstream]

## Matrix
[Master table]

## Per-peer summaries
### Peer A
[...]

## Per-practice summaries
### Practice 1
[...]

## Effectiveness ratings
[Table]

## Open questions
- [...]

## Sources
[Numbered list]
```

This is the same shape as the seo-geo-claude-skills `skill-contract.md` pattern I noticed in the GitHub search — copy that contract rather than inventing a new one.

---

## How downstream phases will use this skill's output

### `05-target-diagnosis` will consume:

- The matrix → identifies practices where the target underperforms vs. peers
- Per-peer summaries → finds the closest analogue to the target's structural position
- Effectiveness ratings → ranks practices by "high effectiveness elsewhere, target absent" — those are the diagnosis priorities

### `06-strawman-recommendation` will consume:

- Effectiveness ratings + the diagnosis priorities → builds the recommended operating model
- Per-practice summaries → uses the cost-to-effectiveness curves to phase the recommendation (cheap-to-start practices in MVP, expensive-to-scale practices in the long-term roadmap)
- Open questions → become the CEO's decision-asks

---

## What changes vs. running standalone

If you're running just this skill (no workflow), nothing changes from the SKILL.md. The skill operates exactly as documented.

If you're running it inside the workflow:

1. **The skill auto-detects workflow context** by checking for the existence of `../01-scoping/state.md` etc. If present, load them and skip re-asking.
2. **The Phase 1 ask_user_question round becomes a *confirmation* round, not a discovery round** — "we have X from scoping and Y from competitive-structure; confirm before we proceed."
3. **Output goes to `state.md` in the workflow folder structure**, not as a free-standing markdown to the user.
4. **A workflow-level orchestrator (which you'll build later) calls the next skill** in sequence after this one completes.

---

## Skill family design principles for the broader CDD workflow

A few things to bake in as you build the other phases:

### Shared contracts

- All phases write `state.md` in a known schema (see seo-geo-claude-skills' pattern).
- All phases append to `sources.md` at the workflow root.
- All phases append to `open-questions.md` at the workflow root.
- All phases append a one-paragraph entry to `decisions-log.md` documenting what was decided and why.

### Modularity

- Every phase must work standalone. No phase depends on a prior phase to function — only to *enrich* its output.
- Skills compose through file-passing, not through tool-passing or function calls. The state files are the API.
- A phase can be re-run mid-workflow without breaking downstream phases (idempotent).

### Source-routing inheritance

- `agent-reach` is loaded once at the workflow root, available to every phase.
- `competitive-analysis` and `operational-practice-mapping` both reference its routing rules; they don't re-implement them.
- The same applies to any future source-routing skills (US-market routing, EU-regulatory routing, etc.).

### Output-format separation

- Every phase outputs `state.md` in markdown.
- A separate **output-format skill** (one for `.docx`, one for `.pptx`, one for client-ready PDF) consumes the state files at the end and renders to the deliverable format.
- This is what's wrong with the existing competitive-analysis skill — it bakes PowerPoint into the analysis logic. Don't repeat that mistake.

### Memory hygiene

- Phase outputs that are durable (peer facts, market sizing, regulatory constraints) get promoted to a workflow-level `cache.md` for reuse across engagements.
- Phase outputs that are engagement-specific (the target's gaps, the strawman) stay in the engagement folder.

---

## Suggested next skills to build (in priority order)

1. **`commercial-diligence-scoping`** — phase 01. This is the cheapest to build and the most important: it sets up the state files all other phases consume.
2. **`target-diagnosis`** — phase 05. The natural pair to operational-practice-mapping. Together these two phases give you "how do peers do it" + "where is the target falling short," which is the core CDD intelligence loop.
3. **`strawman-builder`** — phase 06. Reuses the HV-analysis crossover logic but as a generalized recommendation engine consuming state from earlier phases.
4. **`market-context`** — phase 02. Mostly an adaptation of HV's vertical axis, generalized.
5. **`competitive-structure`** — phase 03. A trimmed competitive-analysis with the deck mechanics removed.
6. **Output-format skills** — `to-docx`, `to-pptx`, `to-brief`. These come last because by that point you'll know what shapes the deliverables actually need.

---

## One thing not to do

**Don't build a workflow orchestrator skill yet.** Build the phase skills first, run them manually in sequence on two or three real engagements, then design the orchestrator after you know what the friction points actually are. Premature orchestration is the most common failure mode in skill-system design.
