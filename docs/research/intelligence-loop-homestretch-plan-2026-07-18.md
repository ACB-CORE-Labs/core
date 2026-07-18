# Intelligence-Loop Homestretch Plan

**Status**: EXECUTED — Phases 0–5 merged to `main @ 31f1a824` (PR #64, 2026-07-18); ADR-0246/0247/0248
**Accepted** (Shay's §8 rulings ratified same day). Phase 6 remains open; see §"what's next" in
`docs/handoff/ADR-0246-Acceptance-Evidence.md`. §2's "stay Proposed" constraint is historical.
**Date**: 2026-07-18
**Base**: `main @ 54659b76` (Rings 2+3 merged; ADR-0243/0244/0245 Accepted; ADR-0246/0247/0248 Proposed, flags off)
**Foundation**: `docs/research/spark-audit-adjudication-2026-07-18.md` — every work item below survived
claim-by-claim verification against the live tree; stale audit claims were removed there and must not
resurface as work items.
**Related**: ADR-0240, ADR-0243…0248, `docs/research/core_cohesion_master_plan.md`

---

## 1. Objective (done-when)

Close the comprehend → reason → articulate → contemplate → learn loop and make its value measurable:

1. **All green CI** (smoke + fast lanes) at every phase boundary.
2. **Meaningful, generalized lift in problem solving, without overfitting** — decided by a dedicated
   instrument (Phase 4), not by narrative. An honest NULL is a legitimate, recordable outcome.
3. **Articulate comprehension of inputs and articulate generation of outputs** as one cumulative loop —
   the corridor's field→token readback wired and round-trip-verified (Phase 1).
4. `generate/` ("core_logos" role) upgrade explicitly **deferred** until the above land (Phase 6 scope note).

## 2. Governance constraints binding all phases

- **A-04 serve-path containment**: wave-field / Fibonacci operators stay out of `chat/runtime.py`;
  corridor work lives in `core/physics/` + `evals/` quarantine. Serving consumes only ratified frozen artifacts.
- **I-03 / proposal-only learning**: no autonomous mutation of the active manifold; biography integration
  only via the PASS-gated wiring layer, harness-driven.
- **No self-Accept**: ADR-0246/0247/0248 stay Proposed; phases produce acceptance-packet evidence only.
  Flag flips and Accepts are Shay's alone.
- **Decoding, not generating**: readback refusals are typed and fail-closed; no fallback strings.
- **Worktree discipline**: all work in a worktree off `forgejo/main`; one PR per coherent phase;
  smoke gate in-worktree before any push.

## 3. Phases

### Phase 0 — Worktree + record (small) — DONE
- [x] Spark PDFs copied to `docs/research/`.
- [x] Adjudication doc written (`spark-audit-adjudication-2026-07-18.md`).
- [x] This plan doc written.
- [x] Worktree `feat/intelligence-loop-arc` off `forgejo/main`; baseline smoke 176 passed (133s).
- [x] Opening record committed (`fcea2d3a`).

### Phase 1 — Close the articulation seam, S1 (medium) — DONE (`19d5731a`)
Wire a `readback` stage into the lifecycle corridor (eval-tier, off-serving):
- `egress` `route="readback_eligible"` → `VocabManifold.nearest()` token selection
  (`cognitive_lifecycle.py` gains a vocab consumer; today it imports no `vocab`, `:68-76`).
- Fail-closed: typed refusal when no resonant token exists — no fallback strings.
- **Round-trip feedback eval ("hearing ourselves think")**: re-ingest the articulated token sequence
  and measure phase-integrity / resonance agreement against the pre-articulation steady state.
  Falsifiable pass criterion fixed before implementation.
- TDD anchors: `tests/test_adr_0243_cognitive_lifecycle.py`, `tests/test_vocab_manifold_invariants.py`.
- Scope guard: within Accepted ADR-0243 §2.3 (readback rules); if design exceeds it → ADR amendment, not silent drift.

### Phase 2 — Activate the learning write-path, S2 (medium) — DONE (`f16b4a60`)
- Compose the chiral Q_top latch (`chiral_gate.py`) into `integrate_validated_biography`
  (`biography_wiring.py:174`): charge conservation becomes a precondition of biography updates.
- First real caller: harness-driven — after ADR-0240 validation PASS, integrate holonomy; prove
  **I-01 reboot-invariance** and replay determinism in tests.
- Strictly PASS-gated + harness-driven; no idle-loop auto-integration (I-03).
- Cleanup-as-you-find: `biography.py:62` bare `.tobytes()` → explicit `<f8` coercion.
- TDD anchors: `tests/test_adr_0240_biography_holonomy.py`, `tests/test_adr_0243_biography_wiring.py`.

### Phase 3 — Unify the autonomy floor, S3 (small) — DONE (`d672c712`)
- Route the lifecycle's residual check (`cognitive_lifecycle.py:831`) through `GoldTetherMonitor`
  so autonomy-level modulation + chiral latching govern corridor runs — one guard, not two half-guards.
- Layering direction: lifecycle → goldtether → WaveManifold (the audit's "integrate Monitor into
  WaveManifold" is rejected; see adjudication §2).
- Not wired into serve (A-04). Parallelizable with Phases 1–2.

### Phase 4 — Generalized-lift instrument (medium-large, the crux) — DONE (`62a72deb`; PARITY/LIFT+9/PARITY, wrong=0 guard HELD)
Instrument before consumption (ADR-0190 lesson: build the measurement first):
- Corridor-vs-symbolic-baseline evaluation harness: problem Hamiltonians compiled from the same
  readers both paths use; measure solve success + refusal honesty.
- Panels: 3-domain anti-overfit panel; deductive flagship as a **guard** (wrong=0 must hold);
  real GSM8K holdout slice (never the 150 templated cases); field-reasoner reading-independence wedge.
- Anti-overfit discipline: holdout sealed; no per-case tuning; κ/γ calibration only through the
  existing sealed calibration evals + ratification.
- Honest-NULL protocol: if the corridor adds no eval delta, record NULL (as ADR-0246 §11 did).
  Truth test is eval delta, not artifact append.

### Phase 5 — Handoff evidence for ruling (medium) — DONE (evals/lift_evidence_handoff.py: proceed vs typed abstain, chains verified)
- Run the Phase 4 instrument through ADR-0247 ports + ADR-0248 handoff machinery (flags on in
  evals only) and assemble acceptance-packet evidence for ADR-0246/0247/0248.
- Deliverable: packets ready for Shay's §8 rulings. No self-Accept, no flag flips.

### Phase 6 — Deferred: `generate/` ("core_logos") upgrade
- Out of scope for this arc by explicit direction. Phase 4's results show where articulation
  quality actually binds; that evidence scopes the next arc.

## 4. Dependencies

- Phase 1 → Phase 4 (instrument needs the closed loop). Phases 2–3 parallel with 1.
- Phase 5 needs Phase 4's evidence. Each phase = own PR, smoke-gated, merged before the next builds on it
  (stacked only if necessary; merge-commit discipline).

## 5. Risks (honest register)

| Risk | Level | Handling |
| :--- | :--- | :--- |
| Phase 4 returns NULL lift (corridor doesn't beat symbolic path yet) | **High-likelihood, low-harm** | Honest NULL recorded; instrument makes the question decidable; scopes Phase 6 |
| VocabManifold coverage too sparse for meaningful readback | Medium | Fail-closed refusals are correct behavior; coverage growth is proposal-gated corpus work, not this arc |
| New eval suites bloat fast lane / flake in CI | Medium | Lane markers (`slow`/`quarantine`) assigned at authoring time; smoke gate at every phase |
| Biography wiring drifts toward autonomous mutation | Low | Harness-driven, PASS-gated only; I-03 checked in review at Phase 2 PR |
| Scope creep beyond Accepted ADR text | Low | Each phase names its governing ADR section; exceeding it → ADR amendment PR, not silent drift |

## 6. Decisions to make at phase start (not blockers now)

- Phase 1: exact round-trip pass criterion (resonance-agreement threshold vs rank-agreement of top-k tokens).
- Phase 2: whether the first caller lives in `evals/analogical_transfer/harness.py` or
  `evals/adr_0243_cognitive_lifecycle/` (leaning: adr_0243 harness — it already imports GoldTetherMonitor).
- Phase 4: GSM8K holdout slice size + which 3 panel domains (reuse the universal-structure trio unless
  evidence says otherwise).
