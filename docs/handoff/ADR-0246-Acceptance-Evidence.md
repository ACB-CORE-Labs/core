# ADR-0246 / 0247 / 0248 — Acceptance Evidence (intelligence-loop arc)

**Status**: Evidence for Shay's §8 rulings — NOT an acceptance; no flags flipped, no ADR status changed.
**Date**: 2026-07-18 (branch `feat/intelligence-loop-arc`)
**Companion**: `docs/audit/adr-0246-acceptance-packet-2026-07-17.md` (the packet holding the
pending rulings), `docs/research/intelligence-loop-homestretch-plan-2026-07-18.md` (the arc plan),
`docs/research/spark-audit-adjudication-2026-07-18.md` (the evidence firewall).
**Reproduce**: `uv run python -m pytest tests/test_generalized_lift_instrument.py -q` and the
two entry points below — everything here is deterministic recompute, nothing is stored state.

---

## 1. What this arc added (seams S1–S5, all merged to the arc branch)

| Seam | Mechanism | Where |
| :--- | :--- | :--- |
| S1 | Egress `readback_eligible` → geometric token readback (⟨ψ ψ̃_T⟩₀ spectrum) + "hearing ourselves think" round-trip via `WaveManifold.phase_correlation` | `core/physics/linguistic_readback.py` |
| S2 | Chiral sgn(Q_top) precondition composed into the PASS-gated biography write-path (provenance v2) + first real harness-driven caller + `<f8` trajectory digests | `core/physics/biography_wiring.py`, `evals/analogical_transfer/biography_session.py` |
| S3 | Unified autonomy floor: `CognitiveLifecycleEngine` feeds `GoldTetherMonitor` one `tether_reading` per turn (control law composed with pin SD-A) | `core/physics/cognitive_lifecycle.py` |
| S4 | Generalized-lift instrument: corridor vs symbolic baseline, 3 domains, independent gold, honest-NULL protocol | `evals/generalized_lift_instrument.py` |
| S5 | Lift evidence through Ring-2 ports + Ring-3 handoff (off-serving, flag-off) | `evals/lift_evidence_handoff.py` |

## 2. Instrument results (live run, deterministic)

Entry point: `evals.generalized_lift_instrument.run_generalized_lift_instrument()`

| Domain | Corridor (correct/wrong/refused) | Baseline (correct/wrong/refused) | Δ | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| propositional (10 enumerated entailments; gold = independent truth tables; baseline = ROBDD flagship) | 10 / **0** / 0 | 10 / 0 / 0 | 0 | **PARITY** |
| constrained-recognition (9 rotor modes, ambiguous 0.45/0.55 two-mode ingress; baseline = constraint-blind argmax) | 9 / 0 / 0 | 0 / 9 / 0 | **+9** | **LIFT** |
| multimodal-completion (audio partial → audio+vision full percept) | 1 / 0 / 0 | 1 / 0 / 0 | 0 | PARITY |

- **wrong=0 guard: HELD** (corridor produced zero wrong entailment verdicts in the flagship regime).
- **honest_null: False** — one genuine lift domain; the two parities are recorded, not spun.
- Round-trip ("hearing ourselves think") agreement on every recognition case: **1.0** (> 0.99 criterion).
- Reading the lift honestly (disclosed in the instrument's own notes): the recognition delta
  isolates the **relax+readback stages'** contribution against a constraint-blind baseline — an
  eigensolver baseline WITH access to H would reach parity. It proves the loop is closed and
  articulate, not that the corridor out-reasons the symbolic engine.
- Multimodal parity detail: the vision token already resonates ≥ 0.4 with the audio-only partial
  (compiler versors overlap), so the baseline also names both percepts. Measured, disclosed.

**Scope limitation (recorded, not silently dropped):** GSM8K / natural-language arithmetic is NOT
ingestible by corridor v1 — no reader→Hamiltonian compiler exists beyond the ≤5-atom propositional
and quadratic-well domains. That compiler is the composition frontier; this instrument is the
harness already waiting to measure it.

## 3. Ports + handoff evidence (ADR-0247 / ADR-0248)

Entry point: `evals.lift_evidence_handoff.run_lift_evidence_handoff()` — two REAL certified
lifecycle turns (relax → egress → governed f64→f32 `serving_cast`), each run through
`IdentityPort` + `PrecisionPort` (Ring-2 seven-stage grammar) and fused by `coordinate_handoff`
(Ring-3). The acceptance evidence is the **contrast**:

| Turn | IdentityPort | PrecisionPort | Replay chain | Handoff |
| :--- | :--- | :--- | :--- | :--- |
| identity-action (canonical lawful turn under H_id={I}) | proceed | proceed | verified | **proceed** (digest `580e686463b06af6…`) |
| frame-rotating (e1∧e2 rotor, θ=0.5) | **abstain: `d_stab>epsilon_turn`** | proceed | verified | **abstain: `port:identity:d_stab>epsilon_turn`** (digest `6ce9949fccdd224d…`) |

The machinery discriminates: lawful turns route through, frame-rotating turns abstain with typed,
port-attributed reasons, and both replay chains verify. Flags stayed off; policy is
`AdmissionPolicy.placeholder_default()` (uncalibrated — activation would still be refused by the
serve gate, exactly as ADR-0246 §3.7 requires).

## 4. Ring-2 Smith-chart conformity note (master-prompt §3)

Assessed, nothing built (no ADR authorizes new machinery): the Ring-2 grammar already frames
ports as the conformal interconnect between non-identical native geometries (`core/ports/adapters.py`
docstring pins the future Atlas/Evidence/Articulation adapter slots). No Smith-chart math library
was written — the directive's own constraint. When a hyperbolic-atlas port lands, its Z→Γ mapping
belongs in the adapter as Spin(4,1) conformal rotor transport; that is a future ADR's work.

## 5. Master-prompt adjudication deltas (applied vs corrected)

- Applied to the REAL tree: `multimodal_lifecycle.py` → `cognitive_lifecycle.py`;
  `ingest_sensorium` → `ingest_context`; `GoldTetherMonitor.calculate_coherence_residual` →
  `coherence_residual` / `update`.
- "Wire Fibonacci to calibrate κ/θ" — already satisfied in the evals quarantine
  (`evals/adr_0244_gamma_calibration`, `evals/analogical_transfer/kappa_calibration.py`); wiring it
  into live streams stays rejected (A-04 / I-03 / R-04).
- §4.1 "fail closed, defaulting back to κ=1.0" — contradiction resolved in favor of the code's
  actual contract: typed `OptimizationFailure`, consumers keep the last RATIFIED constant; a silent
  1.0 default is exactly what the same directive's Subsystem-B clause prohibits.
- §4.3 "remove `default=str` fallbacks in content-id serialization" — verified already clean: the
  only `default=str` occurrences are human-readable CLI display printing (`core/cli.py`), which
  ADR-0245 §2.3 permits; every content-id site refuses non-serializable payloads.
- §Phase-2 chiral composition — implemented, with the honesty theorem pinned: I₅ is central in odd
  Cl(4,1), so closed versors have Q ≡ 0 exactly; the precondition is vacuous-by-theorem on
  admissible trajectories and LIVE against raw non-versor mirror flips (both pinned in tests).
