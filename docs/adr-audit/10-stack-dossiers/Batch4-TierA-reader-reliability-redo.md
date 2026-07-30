# Batch 4 — Tier A Reader-Arc & Reliability-Gate Stack (0164 family, 0165, 0174, 0175) — REDO

**Verified against:** `main` @ `cbfc8ccb` | **Auditor:** Claude (main session, direct) | **Date:** 2026-07-29
Eight ADRs chosen from the Batch-4 remainder because they interlock with already-verified evidence: ADR-0175's Wilson floor is the ceiling I independently recomputed across all 25 deduction bands in Batch 6, and 0164/0165 are the mechanisms ADR-0136 (Batch 3) was superseded *into*. Findings: renumbered into the corpus sequence (see `20-finding-register.md`).

## Stack claim

A lexeme-level incremental reader (0164 + .1–.4, replacing regex sentence-templates per 0165) feeds a two-regime reliability gate (0175) that licenses served capability only on an earned, human-set ceiling. All ratified under ADR-0207 (Accepted 2026-06-03).

## Per-ADR (terse)

- **0164** (Incremental Comprehension Reader) — Accepted, ratified by ADR-0207; "Phase 1+2 shipped." Build full: `generate/comprehension/lexeme_primitives.py`, `lifecycle.py`. **Continuity: exemplary** — carries an explicit `Superseded-by: ADR-0252` line that also *scopes* the supersession ("this ADR remains Accepted as the permanent record; the six unratified paradigm docs are retired under ADR-0252, not this ADR itself"). This is the supersession-banner discipline Batches 1–2 found missing on ADR-0009/0032/0034 — a positive exemplar. `AA-487`.
- **0164.1** (Lexical Primitive Scope) — **`Proposed`**, yet its own text says it "ships with the ADR-0164 Phase 1 PR," and a **live CI pin cites it as sanctioning authority**: `tests/test_lexeme_primitives.py:282-289` (`TestADR0165Compliance`) permits a `\s?` exception to ADR-0165's whitespace prohibition *"explicitly sanctioned in ADR-0164.1 §Seed primitive set."* An unratified document is the authority for a live test's correctness exception. `AA-488`.
- **0164.2** (pronoun-entity resolution), **0164.3** (cross-sentence state), **0164.4** (phase-2 statement-frame reader) — all **`Proposed`** while parent 0164 declares Phase 2 shipped; 0164.4 *is* the Phase-2 reader. Status/reality mismatch across the sub-family. `AA-489`.
- **0165** (Regex Scope Rule) — Accepted, ratified by ADR-0207. **Liveness: genuinely pin-enforced** — `tests/test_lexeme_primitives.py::TestADR0165Compliance` asserts no primitive pattern contains `\s`, and two further test files (`test_adr_0179_extract.py:106`, `test_adr_0176_ms1_question_target.py:4`) describe their own patterns as "ADR-0165-safe," i.e. the rule propagated into sibling authors' practice. One of the better-enforced prohibitions in the corpus. `AA-490`.
- **0174** (Held-Hypothesis Comprehension) — Accepted, ratified by ADR-0207, same exemplary scoped `Superseded-by: ADR-0252` banner as 0164. `AA-487`.
- **0175** (Calibrated Attempt-and-Eliminate Learning) — **`Proposed`**, and this is the stack's headline. Build full: `core/reliability_gate/` is a **7-module package** (`ceilings.py`, `evidence.py`, `floor.py`, `gate.py`, `ledger.py`, `propose.py`, `__init__.py`) plus `generate/determine/estimation_license.py`, with **6 dedicated test files** (`test_adr_0175_phase{1,2,3a,3b}_*.py`, `test_adr_0175_propose{,_runner}.py`). Liveness **live and load-bearing**: Accepted ADR-0256 cites *"ADR-0175 invariant #4"* and *"ADR-0175 invariant #1 discipline preserved"* as binding, and its θ_SERVE=0.99 is the ceiling licensing all 25 deduction bands (independently recomputed in `Batch6-TierA-redo.md`). Necessity irreducible. `AA-491`, `AA-492`.

## Findings rollup

- **`AA-491` 🔴** — **The deduction-serve licensing regime's governing invariants are formally unratified.** ADR-0175 is `Proposed`; Accepted ADR-0256 cites its numbered invariants (#1, #4) as binding discipline, and its θ_SERVE=0.99 ceiling licenses every band in `chat/data/deduction_serve_ledger.json`. A ratified ADR cannot derive binding authority from an unratified one — either 0175 is ratified (its acceptance path looks long since satisfied: 7-module package + 6 test files) or 0256's citations need re-grounding. Highest-value single record fix found in Batches 4–6: one status line reconciles the corpus's most load-bearing capability gate.
- **`AA-488` 🟡** — A live CI pin (`tests/test_lexeme_primitives.py:282-289`) grants an ADR-0165 exception on the authority of `Proposed` ADR-0164.1. Test-enforced correctness resting on an unratified sanction.
- **`AA-489` 🟡** — ADR-0164.1/.2/.3/.4 all read `Proposed` while parent ADR-0164 declares "Phase 1+2 shipped" and 0164.1 says it shipped with the Phase-1 PR; 0164.4 *is* the Phase-2 reader. Sub-family status is uniformly stale against the parent's own claim.
- **`AA-492` 🟢** — `docs/adr/INDEX-by-domain.md:57` cites `core/reliability_gate.py`; the real artifact is the package `core/reliability_gate/` (7 modules). One-word index fix.
- **`AA-487` 🟢** — ADR-0164 and ADR-0174 both carry *scoped* `Superseded-by: ADR-0252` banners that state precisely what is and isn't retired. Cite as the model for the ~20 missing-banner cases in Batches 1–2 (with ADR-0252's R-12b note and ADR-0244's Q_top banner).
- **`AA-490` 🟢** — ADR-0165's prohibition is pin-enforced *and* propagated: sibling authors describe their own patterns as "ADR-0165-safe." A prohibition that changed practice rather than only documentation — the inverse of `AA-497` (ADR-0225's zero-adoption citation mandate).

**Severity tally: 1 🔴 / 2 🟡 / 0 🔵 / 3 🟢.**

## Cross-batch pattern (feeds final synthesis)

Combined with `AA-500`/`AA-502` (0237 Draft with landed ABI; 0238 Proposed with 3 test files) and `AA-499` (0226~3 Proposed while its own ratification doc says accepted), this stack establishes a **corpus-wide governance pattern: `Proposed`/`Draft` ADRs functioning as live, cited, test-enforced authority.** Six instances found across Batches 4–6 alone (0164.1, 0164.2, 0164.3, 0164.4, 0175, 0237, 0238, 0226~3 — eight files). Distinct from the Batches 1–2 "stale Accepted status" pattern: these were never ratified at all, yet Accepted ADRs and CI pins cite them as binding. Recommend a single reconciliation sweep rather than eight separate rulings.
