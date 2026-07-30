# Batch 5 — Tier A FA-1 Cascade Stack (0239, 0240, 0241, 0243, 0244, 0246) — REDO

**Verified against:** `main` @ `cbfc8ccb` | **Auditor:** Claude (main session, direct) | **Date:** 2026-07-29
The six Batch-5 members of the FA-1 cascade (`21-drift-report.md` §1, `AA-68`–`AA-72`), audited as one stack. The rest of Batch 5 is scoped separately. Findings: renumbered into the corpus sequence (see `20-finding-register.md`).

## Fresh primary evidence (re-derived, not adopted)

`algebra/holonomy.py:52-92` — the docstring documents *"Reverse walk: R = (1-alpha)·reverse(wn)…; Holonomy: H = F·R"*; the body validates `alpha ∈ [0,1]` (`:69-70`), computes **only the forward walk**, and `return _word_versor(F)`. No reverse walk exists; `alpha` is validated-then-unused. `core/physics/biography.py:94` calls `holonomy_encode(closed, alpha=alpha)` — an inert parameter — then asserts `versor_condition(blade) < _CLOSURE_TOL` and raises *"biography blade not closed"* on a quantity that is not a holonomy (it is a unitized forward product, closed by construction of `_word_versor`). This independently re-confirms `AA-51` and `AA-68` at HEAD, by direct read.

**Annotation check:** grep for FA-1/retirement notes across all six files — zero hits referencing the holonomy retirement. (0241/0243/0244 each contain one "retired" mention; all three concern *other* mechanisms — the P7 polar decomposition, a folded research doc, and 0244's Q_top gate.)

## Per-ADR (terse)

- **0239** (Conformal Procrustes / Surprise Dual) — status **Proposed**, never accepted. Build/liveness deferred to its acceptance path (tests green + review). Cascade posture: downstream feeder into 0240's biography-holonomy acceptance sink (`AA-71`) — exposure is *forward-looking*: must not be accepted without engaging the FA-1 verdict. Continuity: no retirement note (`AA-493`).
- **0240** (Analogical Transfer Harness + Biography Holonomy Blade) — status **Proposed**, never accepted. Its central "reconstructible via `holonomy_encode`" mechanism is confirmed broken at HEAD (above). Necessity: the harness half may survive; the blade half is `reducible-to-<whatever replaces holonomy post-FA-1>`. `AA-494`.
- **0241** (Hyperbolic Atlas) — **Accepted 2026-07-15** via D10 acceptance packet — *13 days before FA-1*. Carries `holonomy_encode` forward into the wave substrate as a known-good quantity (`AA-70`); acceptance evidence never re-examined post-retirement. Build: extensive (P0–P10 + chiral sign-gate, PR #41); this audit did not re-verify the full packet — flagged for re-verdict, not re-derived. `AA-495`.
- **0243** (Wave-Field Cognitive Lifecycle) — **Accepted 2026-07-17** via acceptance packet, same pre-FA-1 exposure for its "non-lossy reconstruction / topologically protected wisdom" claims (`AA-69`); replayability itself survives (the forward product is still deterministic). `AA-495`.
- **0244** (Identity Manifold) — **Accepted 2026-07-17**, live-gate activation LIMITED (consistent with the open G-11 ruling A5 documented). Carries an **exemplary amendment banner**: §2.3's `Q_top` egress gate *proven vacuous* (identically 0 on the valid manifold, empirically pinned by `tests/test_adr_0244_qtop_vacuity.py`) and retired in place — the same honest-record class as 0252's R-12b note. Its quarantine of biography holonomy away from the identity subspace (`AA-72`) is correct and *strengthened* by the FA-1 finding. `AA-496`.
- **0246** (Induced Identity Action) — **Accepted 2026-07-18**. Boundary-assertion cascade member only (`AA-72`); its own mechanism doesn't depend on holonomy closure. No retirement note, but the exposure is annotation-level, not structural.

## Findings rollup

- **`AA-494` 🔴** — `holonomy_encode` computes no reverse walk and returns the forward product while its docstring and ADR-0240's central mechanism describe `H = F·R`; `alpha` is validated-then-unused; `biography.py:94` steers the inert parameter and asserts "closure" on a quantity closed by construction. Re-verified at HEAD by direct read (fresh evidence, confirming `AA-51`/`AA-68`). ADR-0240 must not be accepted in its current form.
- **`AA-493` 🟡** — Zero of the six Batch-5 cascade members carries any FA-1/holonomy-retirement annotation at HEAD; the drift-report's recommended per-ADR re-verdict remains entirely un-started in this range.
- **`AA-495` 🟡** — 0241 and 0243 were Accepted via acceptance packets dated 13/11 days *before* FA-1; their packets include holonomy-adjacent claims never re-examined post-retirement. Actionable form of `AA-69`/`AA-70`: the re-verdict pass should re-open the two packets, not the ADR prose.
- **`AA-496` 🟢** — 0244's Q_top vacuity banner (empirically-proven hollow gate retired in place, pinned test) joins 0252 as a record-maintenance exemplar; its biography-holonomy quarantine is strengthened, not weakened, by FA-1.

**Severity tally: 1 🔴 / 2 🟡 / 0 🔵 / 1 🟢.**
