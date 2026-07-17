# ADR-0243 — D10 Acceptance Packet for Joshua

**Arc:** ADR-0243 Wave-Field Cognitive Lifecycle (Phases 0–5), built on ADR-0241 (substrate) + ADR-0242 (operators).
**Evidence base:** `feat/adr-0243-phase4-benchmarks @ 2bb57a86` (Phases 0–4 merged to `main` through #56/#58/#59/#60 + this branch's Phase 4). Becomes `main@<merge-sha>` when Phase 4 merges.
**Status of ADR-0243:** still **Proposed**. This packet is submitted *for your ruling*; the `Proposed → Accepted` flip is a **separate one-line governance commit** carrying your ratification provenance inline (per the anti-self-Accept guard, `tests/test_adr_0241_governance_p12.py::test_adrs_accepted_with_recorded_ruling_provenance`). **No status flip has been made** — §8 is PENDING.

---

## 1. Evidence summary (what is proven, and how)

| ADR § | Claim | Built as | Evidence | Verdict |
|-------|-------|----------|----------|---------|
| §2.1 | Ingress = wave ingestion, normalized at one owned boundary | `ingest_context` (superpose via `sensorium_wave_feed`; degenerate superposition refused, never zero-filled) | `test_adr_0243_cognitive_lifecycle` ingress pins; Lane B corridor | **Supported** |
| §2.2 | Reasoning = Hamiltonian well relaxation; "guaranteed, zero intermediate fabrication" | `compile_quadratic_well` / `compile_propositional` + `relax_to_ground` (imaginary-time, D-1); `RelaxationCertificate` (eigen-residual + spectral gap + `psi_digest`) | Phase 4 **fidelity ≥ 0.999**; **insertion cost** all certified + bounded; ground-state property test vs. direct eigensolve | **Supported, honestly restated (D-2)** |
| §2.2 | "The field engine is the reasoner" on checkable logic | `propositional_entails` (ground-energy UNSAT reading) | Phase 4 **decisive falsifier: field vs. ROBDD gold `wrong == 0`** over 1026 decisions (1008 ID + 18 refusal-parity); OOD (>5 atoms) field-refuses / gold-decides | **Supported** on this domain |
| §2.3 | Egress = thermodynamic wave readback, coherence-gated | `egress_gate` (measure_unitary_residual + coherence residual + `EnergyClass` routing); `certificate_state_mismatch` binds cert↔state | egress must-reject pins; E3/E4 → readback-eligible; Lane B corridor readback | **Supported** |
| §2.4 | Speculative contemplation = non-resonant curiosity, proposal-only | surprise→discovery wiring (Lane A `contemplate_surprise_history`); crystallization proposal (I-03) | Lane A discovery pins; crystallization-proposal pin (D-5) | **Supported (proposal-only)** |
| §2.5 | Lifelong learning = biography holonomy update, human-gated | `biography_wiring.integrate_validated_biography` (Lane C); ADR-0240 PASS → integrate seam; I-01 closure at boundary | Lane C report-level PASS gate + I-01 seam + structural no-vault/no-evals pin | **Supported (ratification-gated)** |
| Falsifiability | Metrics separate ID from OOD; f32 truncation is real | Phase 4 `benchmark.py` | **surprise separation 0.834** (> 0.05); **f32 drift** f64 ~8e-14 vs f32 ~4.7e-5 (ratio ~5.9e8) | **Supported** |

The load-bearing result: on the propositional slice — the one domain with an independent, canonical, complete oracle (ADR-0201 ROBDD) — the Cl(4,1) field relaxation decoder agrees with the gold on **every** satisfiable-premise problem (`wrong == 0`), matches its refusal on inconsistent premises, and honestly refuses out-of-regime. "The field engine is NOT the reasoner today" stands unless this evidence says otherwise; it says otherwise, on this domain.

---

## 2. Deviations submitted for ruling (implementation vs. ADR prose)

- **D-1 imaginary-time relaxer** replaces the sketch's `exp(H·I·t)` unitary loop. `exp(−H·dt)` via `np.linalg.eigh` on symmetric H (pure numpy f64, no scipy). Imaginary-time (dissipative) descent is the correct operator for relaxation-to-ground; real-time unitary evolution would not settle.
- **D-2 honest guarantee restatement.** §2.2's "mathematically guaranteed … zero room for intermediate fabrication" is **conditional**, holding iff (a) the Hamiltonian compiler encodes constraints faithfully, (b) a positive spectral gap separates the ground state, (c) iteration has **certified** convergence (not assumed). The certificate records exactly these; unresolved cases fail closed (`spectral_gap_below_tolerance`, `excited_eigenspace`, `max_steps_exhausted`), never mis-certified.
- **D-3 I-05 reconciliation.** Relaxation is *deliberately non-unitary* inside the off-serving solver — that is what dissipation is. I-05 (amplitude conservation) governs **live serve-path** transitions; the relaxer's terminal normalize is an **owned construction boundary** (no hot-path drift repair; boundary breaches fail closed).
- **D-4 R-02 premise retired at v1 scale.** `expm` of a 32×32 symmetric matrix in numpy is trivial; no Rust port needed or permitted for v1. *(The ADR-0244 cohesion arc separately revisits a Rust f64 GP fast-path for the algebra layer — a different surface, gated behind `CORE_BACKEND=rust` with bit-identical parity.)*
- **D-5 E0/E1 crystallization is proposal-only.** No vault writes from the lifecycle; cold states emit a typed crystallization **proposal artifact** through the one-mutation-path (I-03), never a direct `COHERENT` write.

---

## 3. Deferred items (explicitly NOT completion blockers)

- Rust §5 SIMD / MLX acceleration of the algebra layer → ADR-0244 cohesion arc (D2), opt-in `CORE_BACKEND=rust`.
- CRDT multi-writer merge semantics → `docs/analysis/crdt-vs-bitexact-determinism-decision`.
- Serve-path wiring of the lifecycle → remains **A-04 off-serving** (Tier-2); no serve consumer at v1.
- Wave-field IdentityManifold / Gram projection / Q_top egress gate → ADR-0244 (§2.1–2.3), **not** part of this arc; Q_top pending an empirical non-vacuity demonstration (central `I₅` in odd Cl(4,1) makes the naive charge vacuous on versor states — the #19 pseudoscalar failure mode).

---

## 4. Gate results (this arc)

- Phase 2 flagship (#56): smoke 176; fast lane ~11.7k; lane/pins/cohesion/transitive green.
- Phase 3 Lanes C/B/A (#58/#59/#60): each smoke 176 + own tests + fast lane green.
- Phase 4 (this branch, `2bb57a86`): smoke **176**; fast lane **11808 passed, 108 skipped**; Phase 4 tests **17**; benchmark `overall_passed: true` (deterministic); decisive falsifier `wrong == 0`.

---

## 5. Requested action

**Rule on the ADR-0243 arc.** If you rule "Ratify", the follow-up governance commit flips `**Status**: Proposed → **Accepted** — ratified by Joshua Shay <date> (… this packet …)` and records your ruling in §8 below, exactly as the ADR-0241/0242 packet did. The four honest restatements (D-1…D-5) are submitted for acceptance as recommended.

---

## 8. RULING RECORD

**PENDING — awaiting Joshua's explicit ruling.** No status flip has been made; the anti-self-Accept guard requires a recorded human ruling with inline provenance before ADR-0243 may read "Accepted." This line is filled only by/after Joshua's "Ratify" (or amended per his ruling).
