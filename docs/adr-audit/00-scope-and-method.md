# Scope and method — the ADR Audit

**Promoted from** `docs/plans/2026-07-29-adr-audit-plan.md` (full rationale lives there — this file is the working charter every card/dossier is written against, kept short enough that a subagent auditing one stack can load it in full). **Verified against:** `main` @ `cbfc8ccb`.

## What this is

Read every ADR in `docs/adr/` (314 files) and, per stack or singleton, determine: (a) how much of the decision landed in code, (b) whether the decision and its implementation honor the three engineering pillars and seven axioms, (c) whether it contradicts the Whitepaper, the Yellowpaper, or an earlier ADR, (d) whether it integrated into the system and delivered measurable value, and (e) whether the mechanism it introduced was actually necessary, or a narrower duplicate of something the geometric substrate already provides more generally (the "physics-efficient" test — see the plan's §0 for the full argument).

**Read-only.** This audit changes no runtime behavior, fixes no defect, and decides nothing on its own — it produces evidence and a triage queue for ratification, same discipline as `docs/assessment/`. An ADR is reopened only as a flag for ruling, never as a unilateral recommendation to reverse.

**Not a green field.** Before opening a fresh grep session on any ADR, check in this order: (1) `docs/assessment/10-layer-cards/` and `20-component-cards/` for that zone, (2) the gap register (`docs/assessment/30-gap-register.md`, `G-1`…`G-25`+) and hindrance audit (`31-hindrance-audit.md`, `H-1`…`H-14`+), (3) Foundations Audit verdicts (`docs/analysis/fa1-*` — FA-1 already ruled ADR-0005/0015's L2 claim `DEFECTIVE`, 2026-07-28), (4) `docs/census/<sha>/stale-references.jsonl` and `docstring-drift.jsonl` for rotted citations, (5) `evals/obligation_*/`, `docs/PROGRESS.md`, `docs/analysis/`, `docs/handoffs/` for fitness evidence. Only then fresh `rg` against the codebase.

**Non-goals:** not re-running FA-1 or any Foundations Audit layer (adopt ratified verdicts as evidence). Not duplicating `docs/census/`. Not renumbering `docs/adr/` (ADR-0225 governs that; "repository history wins for IDs"). Not writing or amending ADRs — findings go to a triage queue for human ratification. Not on a timeline — scope size, phase, and priority only.

## The charter (fixed before any ADR is read — grades the ADRs, never graded by them)

**The Three Engineering Pillars** (`README.md`):
- **I. Mechanical Sympathy** — software must understand the machine it runs on.
- **II. Semantic Rigor** — every term has one precise, non-negotiable meaning.
- **III. Third Door** — reject the two visible options; build the first-principles path.

**The Seven Axioms** (`docs/Whitepaper.md` §III):
1. **Geometry-First** — find the intrinsic space before choosing structures.
2. **Field-State** — state is a field/distribution, not isolated objects.
3. **Propagation-over-Mutation** — propagate through a structured medium, don't stepwise-mutate.
4. **Dual-Correction** — every forward operator should have a corrective/conjugate counterpart.
5. **Reconstruction-over-Storage** — encode enough structured state to reconstruct, not every detail.
6. **Compilation-Last** — loops/tensors/tables/classes/kernels chosen last.
7. **Reality-over-Inheritance** — no abstraction is sacred; it survives on structural merit only. (Track record: the spectral normalization monitor, the grade guard, the drift correction timer, the ANN index, the pseudoscalar accumulation check — all deleted under this axiom.)

**Formal anchors:** `docs/Yellowpaper.md` (defers to Whitepaper for axioms/pillars — not a competing source), the three Architecture Invariants in Whitepaper §V, `AGENTS.md` invariants **INV-21…INV-34**.

**Discipline, adopted verbatim from `docs/assessment/00-scope-and-method.md`:**
> **The sabotage test.** For every claim that a mechanism is live and load-bearing, ask what the measurement would look like with the mechanism removed. If it would look identical, the claim is decoration.
> **Identity, not value.** Measure identity, not equal-looking values.
> **Verify against code, not against documents.** A claim sourced only from a document is labeled as such.
> **Settled rulings are constraints, not subjects.** Ratified ADRs enter as given.

Plus, from `AGENTS.md`'s Standing Philosophy: "When a record and reality diverge, that is a defect with the same severity as a wrong answer" (#5); "A closed issue is not evidence the problem is gone" (#10).

**Necessity as a first-class question.** Beyond the sabotage test (liveness), ask whether the mechanism a component already at L0/L1 (algebra/field layer) provides in more general form — in which case the ADR's construction is a consolidation candidate even if perfectly built and wired. See `TEMPLATE-adr-card.md` §7.

**Governance note:** this repo is Forgejo-primary. Any PR/issue mechanics use `forgejo-core` MCP tools, never `gh`/GitHub.

## The 7-axis card schema

Every ADR gets scored on: **Build** (ghost/scaffolded/partial/full), **Liveness** (dead/scaffolded/wired-but-unreached/live), **Design fidelity** (pass/tension/violation per pillar+axiom), **Build fidelity** (matches/partial drift/contradicts), **Continuity** (clean/superseded-cleanly/unreconciled contradiction), **Fitness/value** (cited evidence or "none found"), **Necessity/generality** (irreducible/reducible-to-X/generalization-candidate). Full definitions and the fill-in template: `TEMPLATE-adr-card.md`. Tier A stacks use `TEMPLATE-stack-dossier.md` (embeds the per-ADR card shape plus a stack-level synthesis).

## Stack taxonomy

Primary axis: `docs/assessment/02-layer-taxonomy.md`'s 7 macro layers + 2 cross-cuts over 33 zones (already team-ratified, already the Foundations Audit's spine) — don't invent a new one. Secondary axis: the 11 phased sub-decision families (`0073`, `0114`, `0118`, `0119`, `0131`, `0136`, `0164`, `0168`, `0169`, `0189`, `0201` — see `01-adr-census.md` §2), each audited as one sequential arc regardless of which zone it lands in.

## Tiering

- **Tier A (full dossier):** L0–L2 zones, safety/ethics/admissibility, the reliability/licensing ledger, anything already flagged in the gap/hindrance registers or FA-1, and every phased family with ≥4 files.
- **Tier B (standard card):** every other multi-ADR stack.
- **Tier C (rapid triage):** true singletons, non-ADR scope/session docs, `docs/decisions/` redirects — automated cross-reference + spot-check, promoted to B only if flagged.

## Execution order

Bottom-up, same as the Foundations Audit: L0 → L1 → L2 (cascade-check every ADR depending on the retired ADR-0005/0015 claim first) → safety/ethics/admissibility → the phased mega-families → L3 → L4 → L5, Tier A before Tier B, Tier C in parallel throughout. Batches are tracked in `MANIFEST.md` — always check it before starting work, to avoid re-auditing what's already done or losing track of what isn't.

## Rigor tier, amended 2026-07-29 after Batch 2 — cost correction

Batches 1–2 (102 ADRs) ran 22 agents averaging **~187k tokens each** (~4.1M tokens total) — 6-13 narrow-scope agents per batch (one Tier A dossier per 2-8-ADR stack, one Tier B card per 3-7-ADR zone), each independently paying the fixed cost of reading the charter/template/repo layout, each doing 40-84 tool calls of grep/read/cross-reference, several running live test suites and CLI commands, each writing a 400-900+ line dossier. This produced genuinely high-value, well-corroborated findings, but the shape was wrong: narrow per-agent scope multiplies fixed overhead instead of amortizing it, and depth-per-ADR went well past what most findings needed. **Not sustainable for 4 more batches (212 ADRs) — ratified by the user 2026-07-29, corrected as follows.**

**Batches 3–6 run under both changes at once, not either alone:**

1. **Consolidate agents, don't just shrink them.** **2 agents per batch, not 6-13** — one covering every Tier A stack in the batch in a single pass, one covering every Tier B zone in a single pass, each producing one combined output file (multiple `###`-level sections, not one file per stack/zone). This pays the fixed cost (charter, template, repo-layout exploration, `docs/assessment/` discovery) twice per batch instead of 6-13 times. Tier C stays a single rapid-triage pass, done directly (no agent).
2. **Cut investigation depth per ADR, explicitly bounded.** No live test execution or CLI invocation — read code and existing test files, don't run them (this alone was a major share of tool-call volume in Batches 1-2). Target ~5-10 tool calls per ADR (a handful of targeted greps/reads to confirm the core build/liveness claim and the most likely 1-2 findings), not open-ended exploration. Skip the "check N evidence sources in order" checklist per ADR — check `docs/assessment/` and the gap/hindrance registers once, for the whole batch, up front, not re-derived per stack.
3. **Shorter output, per ADR and per file.** Cards stay 7-axis but each axis gets 1-2 sentences, not a paragraph; skip the full `TEMPLATE-stack-dossier.md` per-stack synthesis prose (§3) in favor of a short bullet list. Findings are one line each, not a paragraph with multiple citations.
4. **Cross-batch pattern-hunting deferred entirely** to one final synthesis pass after Batch 6 — not attempted per-batch (this is what let Batch 2's agents spend heavily re-deriving connections to Batch 1 findings; valuable, but not at every batch's expense).
5. **Tier C absorbs more** — true singletons and small unrelated clusters default to Tier C (existence-check only) unless Phase 2's stack mapping flags them as load-bearing.

**Target: ~2 agents per batch instead of ~13, each doing less per ADR — aiming for total batch cost closer to what one Batch-1/2 agent cost, not what a whole batch cost.** What does not change: the 7-axis schema's categories, the sabotage-test discipline for anything actually flagged, the read-only rule, the severity buckets, and citing file:line for any claim that becomes a finding (not for routine "checked, clean" ADRs — those can be one line with no citation).

## Findings and triage

Findings: `20-finding-register.md`, namespace `AA-N` (mirror into the assessment's `G`-register when a finding is really a system-level gap, not just document fidelity). Drift: `21-drift-report.md`. Consolidation clusters: `22-consolidation-report.md`. Master matrix: `30-alignment-matrix.md`. Triage buckets in `40-triage-queue.md`: 🔴 Block / 🟡 Repair / 🔵 Consolidate / 🟢 Monitor.
