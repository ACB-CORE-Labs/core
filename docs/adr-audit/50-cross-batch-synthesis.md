# Phase 6 — Cross-Batch Synthesis

**Verified against:** `main` @ `cbfc8ccb` | **Date:** 2026-07-29 | **Status:** **complete — all six batches, all 314 ADRs.** Batches 1–2 as originally audited (spot-verified, retained); Batches 3–6 redone after the external pass over them was retracted.

The capstone the plan (`docs/plans/2026-07-29-adr-audit-plan.md` §7) reserved for after all six batches: patterns visible only across the whole corpus, which no single batch's dossier could see.

---

## 1. The governance patterns

Four root patterns (A, B, C, D) plus one compound instance of C severe enough to warrant its own entry (C-bis).

### Pattern A — `Proposed`/`Draft` documents functioning as live, cited, test-enforced authority

**The single most consequential corpus-wide finding of this audit.** Two 🔴 instances anchor it; the measured scale (below) is roughly a fifth of the corpus. Worked cases from Batches 4–6:

| ADR | Status | What actually rests on it |
|---|---|---|
| **0175** calibrated learning | `Proposed` | `core/reliability_gate/` (7 modules), 6 test files; **Accepted ADR-0256 cites its "invariant #1/#4" as binding**; its θ_SERVE=0.99 licenses all 25 deduction bands (`AA-491` 🔴) |
| **0201** propositional canonicalizer | `Proposed` | **Accepted ADR-0201.1 "hardens" it**; Accepted 0202–0205 build four phases on it; its 15-module `generate/proof_chain/` package is the live engine under all six Accepted deduction bands (`AA-504` 🔴) |
| **0164.1** lexical primitive scope | `Proposed` | A **live CI pin** (`tests/test_lexeme_primitives.py:282-289`) grants an ADR-0165 exception on its authority (`AA-488`) |
| **0164.2/.3/.4** | `Proposed` ×3 | Parent ADR-0164 declares "Phase 1+2 shipped"; 0164.4 *is* the Phase-2 reader (`AA-489`) |
| **0237** GeometricDelta ABI | `Draft` | `core/abi/geometric_delta{,_validator}.py` landed (`AA-500`) |
| **0238** GoldTether autonomy | `Proposed` | `core/physics/goldtether.py` + **3** dedicated test files; acceptance path's test condition satisfied (`AA-502`) |
| **0226~3** practice loop | `Proposed` | Its own sibling `0226~2` ratification doc says accepted-for-staged-implementation (`AA-499`) |
| **0168/0168.1/0169/0169.1** | `Proposed` ×4 | All read *"no runtime mutation"* yet are the **sole authority** for a live `packs/data/` mutation boundary quoted in module docstrings and pinned by a CI hazard check (`AA-516` 🔴) |
| **0199** Arena GoldTether | `Proposed` | `core/learning_arena/` serves **4 eval lanes**, and Accepted ADR-0238 names it canonical — chaining 0175→0199→0256, three links of which two are unratified (`AA-517` 🔴) |

**Why this is a genuine defect class and not pedantry:** the same sweep found the corpus handling the inverse case *correctly*. ADR-0228–0236 (nine consecutive files) plus 0222/0223/0224 are `Proposed` with **zero implementation and zero tests**, several with self-describing gates ("design-only. Implementation is gated behind…"). That is an honestly-parked design backlog (`AA-503` 🟢). The corpus knows how to label unbuilt work; the Pattern-A cases are specifically built-and-depended-upon work that was never ratified.

**Batch 4's remainder made this the dominant condition, not an exception: 25 of its 44 ADRs carry a Status-vs-reality mismatch**, in five distinct classes — including **five files that literally read `Proposed (implemented in this PR)`** and two that flatly deny a runtime path which exists.

**Scale, measured corpus-wide (main session, direct):** of all 314 ADR files, **247 are Accepted-ish, 61 are `Proposed`/`Draft`** (56 Proposed + 5 Draft), 2 Superseded/Retired, 4 other/blank. Cross-checking those 61 against `tests/` for ADR-named suites gives **~16 distinct Proposed/Draft ADR numbers that already carry dedicated test files** — 0084, 0087, 0114, 0119, 0120, 0126, 0128, the 0131 family (14 files), 0163 (both collision files), 0172, 0175, 0176, 0177, 0178, 0184, 0186. Two caveats, both stated so the number isn't over-read: sub-variants within one family share their parent's tests (the eight `0131.*` entries are one family, not eight instances), and this is a **lower bound** on "built" — per `AA-505` this corpus does not consistently name tests after ADRs, so Proposed ADRs whose tests live in differently-named files (as ADR-0201's do) are invisible to this count. Pattern A is therefore not a handful of oversights; it is roughly a fifth of the corpus unratified, with at least sixteen of those actively test-pinned.

**Consequence, stated precisely:** *both* pillars of the deduction-serve arc — the reasoning engine's keystone (0201) and the licensing regime's invariants (0175) — are formally unratified, while every ADR that consumes them (0201.1, 0202–0205, 0256–0261) is Accepted. A ratified decision cannot inherit binding authority from an unratified one. **Recommended as a single reconciliation ruling covering all of Pattern A**, not eight separate ones: for each, either advance the status (most acceptance paths look long since satisfied) or re-ground the citing ADRs.

### Pattern B — Axiom 4 (Dual-Correction): forward operator built, conjugate not

Established in Batch 1 by three independent stacks (`AA-83`) and holding across later batches:
- `readback_rules.py` — gate 5's conjugate to gate 4's pack lift — **does not exist anywhere** (`AA-44`).
- `holonomy_encode`'s reverse walk `R` — the conjugate to `F` — was deleted at `fca6216e` while its docstring still documents `H = F·R`; `alpha` is validated-then-unused; `biography.py:94` steers the inert parameter. **Re-confirmed at HEAD by direct read** in Batch 5 (`AA-494` 🔴).
- Capability promotion has **no demotion conjugate** when evidence rots (`AA-247`).
- Safety/ethics: the *loader* half is gate-enforced, the *refusal* half sits off the pre-push gate (`AA-109`).

Four instances, four subsystems, one axiom. This is the deepest architectural pattern the audit found and the Whitepaper's own axiom 4 predicts exactly it.

### Pattern C — mechanisms whose failure state is indistinguishable from success

The repo's own standing philosophy (#4, `AGENTS.md`) names this class; the audit found it recurring:
- The register axis was **fully inert on `main` for ~2 days with its own "invariant C" test green throughout** — a dead axis satisfies a self-consistency test trivially (Batch 2, A2.2).
- Three of five v1 safety boundaries **cannot fail**: a flag never set `False`, a hash compared to itself, a field never populated — while reporting `runtime_checkable=True` (`AA-104`–`AA-106`).
- Requesting an unratified ethics pack silently downgrades to the zero-refusal default, **inside the layer whose own `no_silent_correction` boundary reports itself upheld** (`AA-107` 🔴).
- ADR-0225's mandated "Governance citations" section: **0% adoption across ~60 subsequent ADRs**, no lint check (`AA-497`). Contrast ADR-0165, whose prohibition is pin-enforced *and* propagated into sibling authors' practice — "ADR-0165-safe" appears in unrelated test files (`AA-490` 🟢). Same corpus, same era: one prohibition changed behaviour, the other changed nothing, and only the enforced one is distinguishable from its own absence.

### Pattern C-bis — a gate that punishes compliance with its own governing ADR

Independently re-verified by the main session at HEAD (the Batch 3 Tier A agent raised it; every element below was re-checked directly rather than taken on trust):

- `core/capability/reporting.py:421` computes `holdout_present` as the existence of **`evals/cognition/holdouts/cases_plaintext.jsonl`**, and `reasoning_capable` (`:428-434`) requires it; absence appends `gap:{domain}_holdout_absent`.
- That file **exists and is git-tracked** (5,130 bytes).
- ADR-0105 §Context states *"Plaintext holdouts inside the repository violate the intended trust splits,"* permits plaintext *"only for local development"* as **transitional-only**, and §Consequences states *"Existing holdouts are resealed as `.age` artifacts."*

So complying with ADR-0105 — resealing or deleting the plaintext holdout — would flip **every domain's** `reasoning_capable` to false. The capability ledger is gated on the continued existence of an artifact its own governing ADR orders removed. Repo-wide the reseal is barely begun: **3 `.age` files against 32 plaintext holdout artifacts.** This is Pattern C's shape (the gate cannot distinguish "sealed correctly" from "missing") plus an inverted incentive, and it compounds `AA-250` (a sealed holdout leaked verbatim in a git-tracked results file).

### Pattern D — a CI workflow that does exactly what its governing ADR forbids

**Independently verified by the main session, line by line** (raised by the Batch-4 agent as `AA-515`; every element re-checked directly):

`ADR-0155` §Decision, lines 40–41, states the CI runner ***"never** commits directly to `main`, **never** mutates `corpora/`, **never** registers recognizers"*, and line 80: ***"Auto-merge. Never.** Every CI proposal stays open until"* a human reviews it.

`.github/workflows/ratify-proposal.yml` does all of it:
- `permissions: contents: write` (`:47`)
- runs `core teaching review <id> --accept` (`:94`) — ratifying a teaching proposal
- then `git push origin main` (`:120`) — committing the mutated active teaching corpus

Two aggravating factors, both confirmed:
- **Shell-injection surface.** `:91-92` interpolates the operator-supplied note unquoted into a shell: `NOTE_FLAG="--note ${{ inputs.operator_note }}"`. GitHub expands `${{ }}` *before* the shell runs, so a crafted note escapes the assignment — inside a job holding `contents: write` and pushing to `main`.
- **No authorization check.** The job's only guard is `if: vars.CONTEMPLATION_ENABLED == 'true'` (`:58`) — a repository variable, not an identity check. `github.actor` is *recorded* in the commit message (`:118`) and the run summary (`:131`) but never *tested*; ADR-0161's actor allow-list is unbuilt.

**Mitigation, stated honestly so the severity isn't oversold:** this repository is Forgejo-primary, and `AGENTS.md`/`CLAUDE.md` record GitHub Actions as billing-locked dead signals — so the workflow is plausibly dormant, and it is additionally gated behind a repo variable and `workflow_dispatch`. That lowers the likelihood, not the defect: the file is present, dispatch-triggerable, contradicts a ratified ADR on three explicit prohibitions, and would write to `main` if enabled. **This is the most immediately actionable finding in the audit** — the fix is deleting or neutering one file, and it needs no ruling on architecture.

---

## 2. What the audit got right about itself

Recording these because an audit that only ever confirms its own priors is the failure mode it exists to catch:

- **A Batch 1 finding was substantially revised by Batch 2.** `AA-74` attributed the semantic-ground collapse to a specific mechanism in the anchor-lens family; A2.1 independently re-derived it, **refuted the specific attribution**, and replaced it with a sharper measured result (anchor-lens output is byte-identical across every lens; the axis reads no versor/rotor/manifold state at all — it fails its own pre-registered "substrate-driven" criterion).
- **A Batch 1 🔴 was refined down by Batch 4 with fresh evidence.** `AA-64` rated ADR-0180's holonomy dependency structural-🔴; direct reading of §1:15-18 showed it is a *framing premise* justifying the design's cost, not a functional dependency — the CRDT mechanics compute no holonomy. Downgraded to framing-🟡 (`AA-484`) **with the evidence stated**, per the register's rule that severity changes require new evidence. This is exactly what the retracted external pass did *not* do when it silently softened `AA-75`.
- **The retraction itself.** Batches 3–6 were audited by an external process while this session was over its limit; an audit-of-the-audit found a direct contradiction with already-registered evidence (Batch 3 called ADR-0119.1/0114a clean; Batch 2's `AA-250` had already proven ADR-0119.1's §Consequences false at HEAD), a silent severity downgrade, and a statistically implausible 3 🔴 across 212 ADRs against 32 🔴 across the prior 102. `AA-331`–`AA-438` were voided with the evidence recorded, not deleted. **The Batch 3 Tier A redo then found 5 🔴 in the same 53 ADRs where the retracted pass found 0**, and explicitly refuted its downgrades — confirming the retraction was correct rather than merely cautious.
- **And the retraction review's own error was caught and corrected.** That first review credited the retracted work with not fabricating file paths, on the strength of two claim-digests that were genuinely real. The redo falsified it: `core/evals/holdout_runner.py` (cited 3× as build evidence, in a directory that does not exist), `core/capability/expert_contract.py` and `core/capability/ledger.py` (both asserted in verification tables with the found-column set to `yes`). The correction is recorded in the register's retraction notice with the line numbers, because a review that only ever finds the *other* party wrong is the same failure it is auditing.

---

## 3. Corpus-wide tallies

**Reliable findings** (Batches 1–2 as originally produced; Batches 3–6 as redone):

| Batch | ADRs | Status | 🔴 | Notes |
|---|---|---|---|---|
| 1 | 50 | closed | 13 | `AA-1`–`AA-159` |
| 2 | 52 | closed | 19 | `AA-160`–`AA-330` |
| 3 | 91 | **closed (redo)** — Tier A 53 ADRs (19 findings, 5 🔴) + Tier B 38 ADRs (26 findings) + 3 Tier C | 5 | Tier B carded 3 ADRs the retracted map silently omitted |
| 4 | 56 | **closed (redo)** — 12/56 direct + 44 by agent | 4 | **25 of 44 remainder ADRs showed a Status-vs-reality mismatch** |
| 5 | 50 | **closed (redo)** — 4 dossiers, all direct | 2 | 0201 keystone + holonomy conjugate |
| 6 | 15 | **closed (redo)** — direct | 0 | genuinely healthiest range; 4 of 8 findings are positive exemplars |

Redo findings total **102**, registered as `AA-439`–`AA-540` with no gaps: **11 🔴 · 39 🟡 · 6 🔵 · 46 🟢** (per-file dedup; a naive line-scan of the register over-counts 🔴 because many lines cite several findings at once). The retracted pass reported **3 🔴** across the identical 212 ADRs. The redo found **11** — and confirmed by direct file:line re-derivation the specific defects the retracted pass had called clean.

**Void:** `AA-331`–`AA-438` (108 IDs, retracted external pass). **Real findings resume at `AA-439`**; the renumbering is two-pass and home-file-grouped, dry-run verified with zero leftover placeholders (`AA-439`–`AA-514` assigned to the nine completed files).

### The healthiest and the weakest ranges, and why that ordering is informative

Batch 6 (ADR-0251–0265) produced **zero 🔴 and four positive exemplars** — and its evidence is the strongest in the audit (every one of 25 band ledger rows read, Wilson bounds recomputed independently, every governs-file existence-checked). Twelve of its fifteen ADRs date from the 2026-07-19→28 arc that the `docs/assessment/` work itself governed: ruling-gated, with verdict banners, in-place corrections (ADR-0252's R-12b note, ADR-0244's empirically-proven-vacuous Q_top retirement), and bidirectional amendment chains (0262↔0264).

The foundational ranges (Batches 1–3) carry almost all the 🔴s. **The corpus got materially better at record discipline over time** — which means the remediation work is concentrated in the oldest, most load-bearing decisions, and the newest work is the model to copy. ADR-0252, ADR-0244, ADR-0164/0174's scoped supersession banners, and ADR-0165's propagated prohibition are the four templates any remediation sweep should follow.

---

## 4. What a remediation program should do first

Ordered by leverage, not by severity count:

1. **Delete or neuter `.github/workflows/ratify-proposal.yml`** (Pattern D, `AA-515`) — it ratifies teaching proposals and pushes to `main` against three explicit ADR-0155 prohibitions, with an unquoted operator note interpolated into a `contents: write` shell and no actor check. One file, no ruling needed, no architecture decision. Do this first regardless of everything else.
2. **One ruling closing Pattern A** — status reconciliation for 0175, 0201, 0164.1–.4, 0237, 0238, 0226~3. Cheapest high-value fix in the corpus: it makes the deduction-serve arc's authority chain sound without touching a line of runtime code.
3. **The FA-1 cascade annotation debt** — *no* cascade member in *any* batch carries a post-retirement note (`AA-485`, `AA-493`). 19 ADRs + 2 non-ADR records. Annotation, not redesign — and per `AA-484`, several are framing-level, so the work is smaller than the 🔴 count implies.
4. **Pattern C's three unfailable safety predicates** (`AA-104`–`AA-106`) and the silent ethics-pack downgrade (`AA-107`) — the only findings in the audit that touch what a user could actually be told.
5. **The sealed-holdout tangle** (Pattern C-bis + `AA-250`): re-point the `holdout_present` gate at the sealed artifact, then finish the reseal (3 `.age` vs 32 plaintext). Sequencing matters — re-pointing the gate *before* resealing avoids a window where compliance demotes the whole ledger.
6. **Consolidation Cluster 2** (`22-consolidation-report.md`): scope the L2 repair as "route through the L0 rotor/geometric-product operators," never as "repair the L2-native version." Two independent stacks converged on this from opposite ends.
7. **Evidence traceability** (`AA-505`): adopt the `Validation:`-names-its-test-files convention the best ADRs already follow voluntarily, so "what proves ADR-N?" has a mechanical answer.
