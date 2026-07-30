# The ADR Audit — plan

**Status:** proposed, not yet ratified. **Scope size:** large (see §7 — phase/priority only, no timelines, per house discipline). **Verified against:** `main` @ `cbfc8ccb` (2026-07-29).

## 0. What this is, and how it relates to work already in flight

The task: read all ~314 ADRs, group the ones that share a concept into stacks, and for each stack or singleton determine (a) how much of the decision actually landed in code, (b) whether the decision — and its implementation — honors the three engineering pillars and seven axioms, (c) whether it contradicts the Whitepaper, the Yellowpaper, or an earlier ADR, (d) whether it integrated into the rest of the system and delivered measurable value, and (e) whether the mechanism it introduced was actually *necessary* — a genuinely irreducible primitive — or a narrower, single-purpose construction duplicating something the shared geometric substrate already does more generally.

That fifth question is not an afterthought bolted onto the others; it is what a physics-native system is supposed to be able to answer. Physical theories get their efficiency from a small number of general laws/operators that many phenomena share, not from one bespoke mechanism per phenomenon — the same rotor/versor structure that turns a vector should not need to be reinvented as a narrower, differently-named operator every time a new subsystem needs "turn this by that." Axiom 7 (Reality-over-Inheritance, §1) already has a track record of applying exactly this test in this repo — the Whitepaper names five mechanisms already deleted because measurement showed they weren't earning their keep (the spectral normalization monitor, the grade guard, the drift correction timer, the ANN index, the pseudoscalar accumulation check). This audit generalizes that one-off pruning into a systematic pass: for every ADR, is what it built a distinct necessary capability, or a special case of something the algebra/field layer already provides that should have been generalized instead of duplicated — and, looking forward, could an existing mechanism be broadened slightly to absorb what a later ADR built narrowly, shrinking total component count rather than growing it.

Two other models drafted generic versions of this plan without reading the repository. Their phase shapes were reasonable; their specifics were wrong or stale — the ADR count they worked from (~130) is under half the real corpus (314 files, 252 distinct numbers, `0001`–`0265`), and their stack list was invented rather than derived from anything in the repo. This plan is written against the actual corpus and, more importantly, against the audit machinery this team already built and validated once.

**This is not a green field.** `docs/assessment/` (2026-07-27/28) is a completed macro→micro audit of CORE's cognitive-cycle *design vs. implementation*, built under `docs/conceptualizing_engineering_mastery.md`, with a numbered gap register (`G-1`…`G-25`+), a hindrance audit (`H-1`…`H-14`+), and a ruling packet (`R-1`…`R-14`), all read-only, all evidence-first. The **Foundations Audit** (`docs/plans/2026-07-28-foundations-audit.md`) is currently mid-flight, running layer-by-layer verdicts (`MASTERFUL` / `SOUND-BUT-STRANDED` / `DEFECTIVE`) bottom-up from L0 (algebra kernel) to L5 (serving); its first result, **FA-1, closed 2026-07-28: L2 (the cross-language semantic ground, governed by ADR-0005 and ADR-0015) is `DEFECTIVE`, central design claim retired** — measured AUC 0.557 against a pre-registered bar of 0.80. The queued "next arc" after the assessment is the **Perception Arc** (`docs/plans/2026-07-28-perception-arc.md`), scoped to capability-widening (`G-3`/`G-4`), not document fidelity.

None of that is an ADR-text audit. Nobody has read all 314 ADRs against the code, the pillars, the axioms, and the papers as a single exercise. That is genuinely new territory — good, because it means no duplication risk — but it means the rubric has to be built, not borrowed wholesale. What *should* be borrowed, because it is proven and ratified in this exact repo:

- The **discipline** (§2 of `docs/assessment/00-scope-and-method.md`, quoted in full in §1 below).
- The **orthogonal-axes card design** (`docs/assessment/03-card-schema.md`'s decision to keep liveness, fitness, design, and build as separate fields rather than one conflated score).
- The **layer taxonomy** (`docs/assessment/02-layer-taxonomy.md`'s 7 macro layers + 2 cross-cuts over 33 zones) as the primary stacking axis, instead of inventing a new one.
- The **numbered ledger convention** (`G-N` / `H-N` / `R-N`), extended with a new namespace for this audit's own findings (§4).
- The rule that **an ADR is reopened only as a flag for ruling, never as a unilateral recommendation to reverse** — this audit produces evidence and a triage queue; it does not fix anything.

**Non-goals**, stated up front so scope doesn't creep:
- Not re-running FA-1 or any Foundations Audit layer — where a layer already has a ratified verdict, this audit *adopts* it as evidence (see §3, Tier A workflow) rather than re-deriving it.
- Not duplicating `docs/census/` (the untracked mechanical-defect sweep — dead code, docstring drift, stale references, pinned at the current HEAD). That sweep is code-scoped and axis-orthogonal to this one; its `stale-references.jsonl` and `docstring-drift.jsonl` outputs are a candidate *evidence input* (§3) for catching ADRs whose citations into code have rotted, not something to rerun.
- Not renumbering or reorganizing `docs/adr/`. `ADR-0225-adr-corpus-hygiene.md` already governs numbering discipline and states "repository history wins for IDs" — this audit documents collisions (§2) but does not touch filenames.
- Not writing or amending ADRs. Findings become entries in a triage queue for the same ratification process the assessment used (`RATIFIED 2026-07-28 (Shay)` pattern in `AGENTS.md`) — a human decision, not an automatic edit.
- Not on a timeline. Per the assessment's own rule 5 ("No timelines. Scope size, phase, and priority only."), this plan is phased and tiered, not dated.

## 1. The Evaluation Charter (locked before any ADR is read)

Every judgment in every later phase is made against this fixed frame. Nothing in an ADR overrides it; the charter grades the ADRs, never the reverse.

**The Three Engineering Pillars** (`README.md`, "operational expression" of the axioms below):
- **I. Mechanical Sympathy** — software must understand the machine it runs on.
- **II. Semantic Rigor** — every term has one precise, non-negotiable meaning.
- **III. Third Door** — reject the two visible options (borrow or cut a corner); build the first-principles path.

**The Seven Axioms** (`docs/Whitepaper.md` §III — "formulated before the first line of code," every decision must satisfy them):
1. **Geometry-First** — find the intrinsic space before choosing structures.
2. **Field-State** — state is a field/distribution, not a heap of isolated objects.
3. **Propagation-over-Mutation** — compute by propagation through a structured medium, not stepwise mutation.
4. **Dual-Correction** — every forward operator should have a corrective/conjugate/adjoint counterpart.
5. **Reconstruction-over-Storage** — encode enough structured state to reconstruct, not every detail explicitly.
6. **Compilation-Last** — loops/tensors/tables/classes/kernels are implementation targets chosen last.
7. **Reality-over-Inheritance** — no abstraction is sacred for being old or standard; it survives on structural merit only. (This is the axiom the Whitepaper itself cites for having deleted the spectral normalization monitor, the grade guard, the drift correction timer, the ANN index, and the pseudoscalar accumulation check — i.e., it is not aspirational, it has a track record of actually killing things.)

**Formal anchors**: `docs/Yellowpaper.md` (technical spec, defers to the Whitepaper for axioms/pillars — do not treat it as a second, competing source), the three Architecture Invariants in Whitepaper §V (versor coherence, conformal-memory/CGA distance, the Logos-as-field-projection), and `AGENTS.md`'s numbered runtime invariants **INV-21…INV-34**.

**Audit discipline**, adopted verbatim from `docs/assessment/00-scope-and-method.md` because it already caught a real false-positive in this exact codebase (a reader rate reported as evidence that was `0.0` throughout):
> **The sabotage test.** For every claim that a mechanism is live and load-bearing, ask what the measurement would look like with the mechanism removed. If it would look identical, the claim is decoration and is recorded as such.
> **Identity, not value.** When measuring whether two things are the same thing, measure identity rather than equal-looking values.
> **Verify against code, not against documents.** A claim sourced only from a document is labeled as such. (Precedent: `docs/research/architecture-assessment-verification-2026-07-25.md` falsified roughly a third of an external blueprint's work items by reading the implicated code.)
> **Settled rulings are constraints, not subjects.** Ratified ADRs enter as given. An ADR is reopened only on evidence of hindrance, and only as a flag for ruling — never as a unilateral recommendation to reverse.

Two lines from `AGENTS.md`'s "Standing philosophy (2026-07-28)" apply directly to record-vs-reality auditing and are adopted as charter clauses:
> "Prefer a record that contradicts nothing to a record that impresses... When a record and reality diverge, that is a defect with the same severity as a wrong answer." (#5)
> "A closed issue is not evidence the problem is gone... ask what it actually observed." (#10)

**Necessity as a first-class question.** The sabotage test above ("what would the measurement look like with the mechanism removed") is already a necessity test for *liveness* — is anything actually using this. This audit runs a second, complementary necessity test aimed at *design*, not just wiring: given the mechanism the ADR introduced, does it require its own distinct machinery, or does the geometric substrate (the algebra/field layer, L0–L1) already express the same operation in more general form — in which case the ADR's construction is a special case that should be collapsed into the general one, not maintained alongside it. This is Geometry-First (axiom 1) and Reality-over-Inheritance (axiom 7) read together: find the intrinsic space first, and don't keep an abstraction around past the point it's earning its structural keep. A component can pass every other axis in §4 — built, wired, drift-free, cited correctly — and still be a consolidation candidate under this test.

**Governance note, corrected from the two drafts I was given**: this repository is Forgejo-primary (`core-gitquarters.acbcontent.org`), not GitHub. Any issue/PR mechanics this audit eventually needs go through the `forgejo-core` MCP tools, never `gh`/GitHub.

## 2. Phase 1 — Census and disambiguation

**Goal:** one machine-verified inventory, because the closest thing that exists today (`docs/adr/INDEX-by-domain.md`) is explicitly partial and already stale (it says "312 files"; the real count is 314 ADR-numbered files, 333 including non-ADR docs) — itself a small, free, first finding about record/reality drift.

1. **Enumerate.** Parse every `docs/adr/ADR-*.md` filename into `(number, suffix, title, path)`. Cross-check against `docs/adr/README.md`, `INDEX-by-domain.md`, and `MASTER-BLUEPRINT-2026-07-20-ADR-MAPPING.md` for known reconciliations (the latter already rules "repository history wins for IDs" for the 0240–0253 collision with an external blueprint — adopt as given, don't re-litigate).
2. **Extract per-ADR metadata** from each file's own header/front matter: status (Proposed/Accepted/Superseded/Retired/Amended), date, and any explicit `Supersedes` / `Amended by` / `Related ADRs` / "Governance citations" section (mandatory on ADRs touching runtime/packs/teaching/memory/replay per ADR-0225). This citation graph is what makes cross-ADR consistency checking in Phase 3F tractable — checking all 252×252 pairs by hand is not; walking each ADR's declared neighbors is.
3. **Resolve the true collisions first**, as a standalone disambiguation table, before any stacking: the 10 numbers carrying unrelated decisions with no letter/dot suffix (`0078`, `0120`×3, `0122`, `0123`, `0127`, `0140`, `0163`, `0178`, `0184`, `0226`×3, plus `0225` itself). Assign each a stable internal sub-id (e.g. `0120-a/b/c`) for audit bookkeeping only — no file renames, per the non-goals in §0.
4. **Classify the 19 non-ADR files** living in `docs/adr/` (scope notes, the one binding note `epistemic-taxonomy-ownership-stage3.md`, and 7 dated `SESSION-*.md` journal entries): in-scope-as-context (scope notes feed the stack they belong to) vs. excluded-from-census (session journals, cited only if an ADR references one). `docs/decisions/`'s 3 files are pure redirect stubs — verify they still resolve, nothing more. `docs/architecture/`'s 9 files are supporting design docs, pulled in per-stack as evidence, not audited as top-level units.
5. **Output:** `docs/adr-audit/01-adr-census.md` — the corrected, complete table (number, suffix, title, status, date, cited neighbors, disambiguation flag). This single deliverable already repairs the stated staleness in `INDEX-by-domain.md` and can be cross-linked back into it, directly satisfying ADR-0225's requirement that the index stay live — a concrete, low-risk win available on day one, independent of everything after it.

## 3. Phase 2 — Stack formation

**The key design choice, and the main way this plan differs from both drafts I was given:** don't invent a new stack taxonomy. `docs/assessment/02-layer-taxonomy.md` already fixed a 7-macro-layer + 2-cross-cut decomposition over 33 zones (L0 algebra kernel → L1 field/physics → L2 semantic ground → L3 perception → L4 cognition → L5 serving, plus cross-cutting teaching/governance and always-on-life), team-ratified and already used as the spine for the Foundations Audit. Reusing it means:
- Stack membership isn't a matter of my judgment call vs. Grok's judgment call vs. Gemini's — it's the same skeleton this team already agreed carves the system at its joints.
- Every stack automatically inherits whatever liveness/fitness verdicts the layer cards (`docs/assessment/10-layer-cards/`) and component cards (`20-component-cards/`) already recorded for that zone, which is free evidence for Phase 3.
- Wave ordering (§5) falls out for free: bottom-up, same order as the Foundations Audit, "logos-first."

Procedure:
1. **Primary axis — layer/zone.** Map each ADR to the zone(s) it governs, using the citation graph from Phase 1, the module paths the ADR itself names, and the existing layer/component cards as a cross-check. Most ADRs land in exactly one zone; ADRs spanning zones are flagged and placed in whichever zone owns the *decision*, cross-referenced from the others.
2. **Secondary axis — phased family.** The 22 numbers with sub-variants (`0073a–d`, `0119.1–.8`, the 16-file `0131.*` family, `0114a` + its five auditor sub-ADRs, etc.) are treated as pre-formed micro-stacks regardless of which zone they land in — they are a sequential decision chain and must be read and audited as one arc, not split across the zone boundary.
3. **Singleton isolation.** ADRs matching no zone confidently and no phased family are flagged as true singletons — Tier C by default (§4) unless something about them (blast radius, contradicts a pillar on its face) promotes them.
4. **Output:** `docs/adr-audit/02-stack-taxonomy.md` — the zone-keyed stack manifest, the phased-family list, and the singleton list, each with a first-pass tier assignment (§4).

## 4. Phase 3 — the audit itself, tiered by blast radius

314 ADRs at uniform maximum rigor is not a plan, it's a wish. The assessment's own precedent — nine layer cards and eight component cards, not 33 zone-deep essays — is the model: **spend depth where a wrong verdict would be indistinguishable from a right one, spend a checklist everywhere else.**

**Tier assignment:**
- **Tier A — full dossier.** Anything governing L0–L2 (algebra/geometry, field-state, semantic ground/vocabulary), safety/ethics/admissibility, the reliability/licensing ledger, or already named as load-bearing/contested in the gap register (`G-1`…`G-25`), the hindrance audit, or FA-1. Also every phased family with ≥4 files (`0073`, `0119`, `0131`, `0114a`) — internal complexity alone earns dossier treatment.
- **Tier B — standard card.** Every other multi-ADR stack (teaching, packs, telemetry, renderer, agency/tools, register/realizer, etc.).
- **Tier C — rapid triage.** True singletons, the 19 non-ADR scope/session docs, the `docs/decisions/` redirects. Automated cross-reference (grep the ADR number/title against code, tests, docs) plus spot-check; promoted to Tier B only if the automated pass flags contradiction or orphan risk (zero references anywhere).

**Day-one priority, not generic**: FA-1 just ruled ADR-0005/0015 `DEFECTIVE` (2026-07-28). The single highest-leverage first move in Phase 3 is walking the citation graph from Phase 1 to find every *other* ADR that cites or structurally depends on cross-language holonomy closure, and flagging each for re-verdict. This is a concrete cascading-impact analysis that FA-1 itself didn't do (it closed one layer) and that only an ADR-corpus-wide pass like this one can surface.

**Card schema — orthogonal axes, not one conflated score.** `docs/assessment/03-card-schema.md` deliberately kept liveness, fitness, design, and build as separate fields rather than a fatter single enum ("keep the 17 fields... add the four missing dimensions as orthogonal fields, not fatter enums"). Apply the same discipline here instead of Grok's single T1–T5 tier bolted to a separate 1–5 score:

| Axis | Question | Values |
|---|---|---|
| **Build** | Does the code the ADR describes exist? | ghost / scaffolded / partial / full, each with file:line evidence |
| **Liveness / Integration** | Is it wired into the live serving path, or dead/orphaned/scaffolded-only? | dead / scaffolded / wired-but-unreached / live |
| **Design fidelity** | Does the *decision text itself* honor the pillars, the axioms, the invariants? | pass / tension / violation, per pillar and per axiom, with the specific clause cited |
| **Build fidelity** | Where built, does the *implementation* match what was decided, or did code drift? | matches / partial drift / contradicts |
| **Continuity** | Does it contradict the Whitepaper, Yellowpaper, or an earlier/cited ADR? | clean / superseded-cleanly / unreconciled contradiction |
| **Fitness / value** | Evidence it delivered something — eval score, benchmark, PROGRESS.md entry, obligation lane result? | cite the specific `evals/`, `docs/analysis/`, or `docs/PROGRESS.md` artifact, or record "no evidence found" |
| **Necessity / generality** | Is this a genuinely irreducible primitive, a special case of something the substrate already provides, or a candidate to be generalized outward? | irreducible / reducible-to-\<cite the general mechanism\> / generalization-candidate |

The necessity/generality axis is answered with three concrete sub-questions per ADR, in this order:
1. **Necessity** — sabotage-test it: remove the mechanism, does anything downstream actually change? If not, it's a deletion candidate regardless of how well-built it is.
2. **Reducibility** — does an operator already present at L0/L1 (the algebra/field layer) already do this, under a different name, for a different caller? If so, name it — this ADR's construction is a candidate to be re-expressed in terms of the general one rather than stand alongside it.
3. **Extensibility** — could this mechanism, generalized slightly, have absorbed (or still absorb) what some *other* ADR built narrowly for a similar purpose? Name the other ADR if one comes to mind during the read; the full pairing pass happens in Phase 4 (§5, item 5), since redundancy across stacks is rarely visible from inside a single stack's dossier.

Every card stamps a `verified_at` git SHA, per the assessment's maintenance contract ("a card whose `verified_at` falls behind a load-bearing arc is testimony, not evidence").

**Evidence sources to consult, in order, before opening a fresh grep session** — reuse what's already measured rather than re-deriving it:
1. Layer/component cards in `docs/assessment/10-layer-cards/` and `20-component-cards/` for that zone.
2. Gap register (`30-gap-register.md`, `G-1`…`G-25`+) and hindrance audit (`31-hindrance-audit.md`, `H-1`…`H-14`+) for anything already flagged against that ADR.
3. FA-1 and any later Foundations Audit verdicts (`docs/analysis/fa1-*`) for L0–L2 ADRs.
4. `docs/census/<sha>/stale-references.jsonl` and `docstring-drift.jsonl` for citations into this ADR (or from it) that mechanical scanning already flagged as rotten.
5. `evals/obligation_*/`, `docs/PROGRESS.md`, `docs/analysis/`, `docs/handoffs/` for the fitness/value axis.
6. Only then, fresh `rg` against the codebase for anything the above didn't cover.

**Tier A dossiers** additionally follow the FA-1 shape where the claim is falsifiable: state the ADR's testable claim, pre-register the bar, measure, verdict — the same discipline that produced a credible NO-GO on the first real attempt, rather than a prose-only read.

**Output:** `docs/adr-audit/10-stack-dossiers/<zone>.md` (Tier A), `docs/adr-audit/11-adr-cards/<zone>.md` (Tier B, one file per zone containing all its cards), `docs/adr-audit/12-triage-log.md` (Tier C, one row per ADR).

## 5. Phase 4 — synthesis

1. **Finding register** — `docs/adr-audit/20-finding-register.md`, new namespace **`AA-N`** (ADR-Audit) so IDs never collide with the assessment's `G`/`H`/`R`. Any `AA` finding that is really a system-level gap (not just a document-fidelity issue) gets mirrored into the existing gap register with a cross-citation, rather than forked into a parallel ledger the team then has to reconcile.
2. **Drift report** — `docs/adr-audit/21-drift-report.md`. Every unreconciled contradiction found in Phase 3's Continuity axis, with the specific Whitepaper/Yellowpaper section or prior-ADR clause it conflicts with, and the blast radius (which downstream ADRs/stacks inherit the problem).
3. **Alignment matrix** — `docs/adr-audit/30-alignment-matrix.md`. One row per ADR, seven columns (the axes from §4, including necessity/generality), sortable/filterable — the master reference deliverable.
4. **Index repair** — fold the corrected count and domain coverage from Phase 1/2 back into `docs/adr/INDEX-by-domain.md`, satisfying ADR-0225's living-index requirement as a direct byproduct rather than a separate task.
5. **Consolidation & parsimony report** — `docs/adr-audit/22-consolidation-report.md`. This is the one deliverable that genuinely requires the full picture, not just one card: cluster every ADR marked `reducible-to-<X>` or `generalization-candidate` on the necessity/generality axis, and for each cluster —
   - name the general mechanism (or the mechanism that *could* become general) and cite where it lives (L0/L1 zone, module, ADR of origin);
   - list every ADR whose narrower construction the general mechanism already subsumes, or could subsume with a stated, scoped extension;
   - distinguish **true redundancy** (two mechanisms doing the same thing, one should go) from **legitimate specialization** (the narrower mechanism earns its keep for a reason the general one structurally can't cover — record the reason, don't just assume everything should collapse to one operator);
   - carry a rough consolidation cost/blast-radius estimate, the same way the drift report carries one for contradictions, so this feeds the same triage ranking in Phase 5 rather than becoming a wish list nobody prioritizes.

   This report is where the "physics-efficient" framing pays off concretely — its output is closer to "these 6 ADRs across 3 stacks each built a bespoke rotation/projection helper; ADR-0004's rotor-as-operator already covers all 6 use cases" than to a generic finding. It is also the deliverable most likely to be wrong on a first pass (distinguishing genuine specialization from redundancy requires real domain judgment), so treat its clusters as strong candidates for ruling, not settled conclusions — same "flag for ruling, never unilateral" discipline as everything else in this audit.

## 6. Phase 5 — triage queue, not remediation

`docs/adr-audit/40-triage-queue.md`. Rank every `AA` finding by (a) blast radius — how many stacks break if this is wrong, (b) pillar/axiom violation severity — weighted higher in foundational (Tier A) ADRs, (c) Whitepaper/Yellowpaper divergence. Three buckets, same shape as the assessment's ruling packet:
- 🔴 **Block** — active contradiction of a ratified pillar/axiom or an unreconciled clash with the Whitepaper; needs a ruling before more work builds on it.
- 🟡 **Repair** — implementation drifted from a sound decision; fixable without re-deciding anything.
- 🔵 **Consolidate** — not broken, not contradictory, just redundant with (or absorbable into) a more general mechanism elsewhere; the consolidation-report clusters (§5, item 5) land here, ranked by how many downstream ADRs/stacks a successful consolidation would simplify.
- 🟢 **Monitor** — low blast radius, noted, not urgent.

Per the charter's "settled rulings are constraints, not subjects" clause: this queue is handed to the same ratification process the assessment used — it recommends, it does not execute. No runtime code changes as part of this audit.

## 7. Execution order and mechanics

**Order** (bottom-up, same rationale as the Foundations Audit — "logos-first," don't spend Tier-A depth on L4/L5 stacks whose foundations might still move):
1. Phase 0/1 (this charter + census) — cheap, mostly mechanical, do first regardless.
2. Phase 2 (stack formation against the existing layer taxonomy).
3. Phase 3, Tier A, in layer order: L0 → L1 → L2 (starting with the ADR-0005/0015 cascade check) → safety/ethics/admissibility → the four phased mega-families → L3 → L4 → L5.
4. Phase 3, Tier B, same order, lower depth.
5. Phase 3, Tier C, can run in parallel with anything above — it's mechanical.
6. Phase 4/5 only after all of Phase 3 lands, since the matrix and triage queue need the full picture.

**Mechanics:** Tier A dossiers and Tier B zone-cards are natural units for parallel subagent fan-out (one agent per zone/stack), since each only needs the charter (§1), its zone's assessment cards, and its own ADR files as context. Tier C triage is a single mechanical pass. No multi-agent orchestration (the `Workflow` tool) unless explicitly requested — default execution uses ordinary parallel subagents per stack.

**Deliverables tree:**
```
docs/adr-audit/
  README.md                # reading-order index, assessment-style
  00-scope-and-method.md   # this charter, promoted/copied from this plan once ratified
  01-adr-census.md
  02-stack-taxonomy.md
  10-stack-dossiers/<zone>.md
  11-adr-cards/<zone>.md
  12-triage-log.md
  20-finding-register.md
  21-drift-report.md
  22-consolidation-report.md
  30-alignment-matrix.md
  40-triage-queue.md
```

## 8. Open decision for the user

Everything through Phase 1 (census + disambiguation table) is cheap, mechanical, and reversible — I can start it now. Phase 2 onward commits to the zone taxonomy and starts real reading effort across 314 files. Recommend: ratify this charter, then greenlight Phase 1 as a standalone first deliverable before committing to the full Phase 3 fan-out.
