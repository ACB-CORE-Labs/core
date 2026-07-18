# ADR-0244 — D4 Acceptance Packet for Joshua

**Arc:** ADR-0244 Wave-Field Identity Manifold & Inalienable Geometric Alignment (D4 Phases 0–6), built on the ADR-0243 lifecycle + the ADR-0245 mechanical-sympathy foundation.
**Evidence base:** `feat/adr-0244-d4 @ 8ef80daa` (Phases 0–5 pushed direct-to-`main` per your sole-worker authorization; Phase 6 = this packet + the ADR-0245 packet).
**Status of ADR-0244:** **Proposed — submitted for your ruling.** The `Proposed → Accepted` flip is a **separate one-line governance commit** carrying your ratification provenance inline (anti-self-Accept guard, `tests/test_adr_0241_governance_p12.py::test_adrs_accepted_with_recorded_ruling_provenance`). **I have NOT flipped it** — §8 is PENDING. See §5 for the one caveat that shapes the ruling.

---

## 1. Evidence summary (what is proven, and how)

| ADR § | Claim | Built as | Evidence | Verdict |
|-------|-------|----------|----------|---------|
| §2.1 | Identity is a fixed geometric subspace; trajectories are checked against it | `core/physics/identity_manifold.py` — **operator-preservation** primitive (`lift_axis`, `gram_matrix`+`ManifoldConditioningError`, `subspace_project`, `sandwich`, `axis_response`) | `test_adr_0244_identity_manifold.py` (25): G=I on the orthonormal pack; idempotent projection; identity versor → 0 leakage/+1 align; e14/e15 tilt → leakage; π-invert → −1 align; near-parallel axes → conditioning error | **Supported, core mechanism corrected (D-1)** |
| §2.2 | Fail-closed spectral-leakage gate + `C_id` + `IdentityGateRefusal`; `boundary_ids` active | dual-mode `IdentityCheck.check(..., wave_field=, violated_boundary_ids=)`, `_validate_wave_field`, admit-or-abstain `conjugate_correct`, wave telemetry; flag-gated wiring in `chat/runtime.py` | `test_adr_0244_identity_gate_wave.py` (16) + `_runtime.py` (3) + `_eval.py` (6): fail-closed on malformed ψ; boundary intersection; flag-off byte-identity; ablation separates geometric attacks 6-vs-0 over legacy | **Built + validated; NOT live (D-2, see §5)** |
| §2.3 | `Q_top` topological-charge conservation at egress | Proven **vacuous** on the versor manifold; retired from egress | `evals/adr_0244_qtop_vacuity` + `test_adr_0244_qtop_vacuity.py`: `Q_top ≡ 0` on every rotor/boost; aligned + adversarial both read 0 | **Retired (D-3), kept as diagnostic** |
| §2.4 | Bracketed-local Fibonacci search calibrates `γ_id` | `evals/adr_0244_gamma_calibration/` — certified `γ* = 0.2126624458513829` (cert `0079b5f2…`), pinned `identity._WAVE_LEAKAGE_BOUND` | `test_adr_0244_gamma_calibration.py` (9): certificate reproducible/deterministic; separates the geometric attack set | **Machinery supported; live flip NOT authorized (D-2)** |
| §2.5 | Governed f64→f32 serving-boundary cast | `serving_cast(...) → ServingState` in `cognitive_lifecycle.py` | `test_adr_0244_serving_cast.py` (10): casts only certified/admitted/digest-matched; precision-checked; f64 stays source of truth | **Supported** |
| §2.6 | Rust GP fast-path + parity | f32 (pre-existing) + f64 (D2) kernels, bit-identical | `test_geometric_product_f64_parity.py` (N=10,000) + f32 parity | **Supported** |
| §2.7 | Full digests / no `default=str` / byte-order guard | D1 hot path + Phase 5a: 4 residual content-ids widened | `schema`/`plan_preflight`/`articulation_quality`/`holographic_vault` full-digest + LE; collision proof in `test_adr_0245_acceptance_gate.py` | **Supported** |
| §2.8 | `eigh` memoization | `_cached_eigh` (D2) | `test_adr_0244_mechanical_sympathy.py` | **Supported** |
| §2.9 | Low-discrepancy mode allocator / order-independence | **Proven** (not wired): recall = Gram lstsq onto span → permutation-invariant to ~1e-15; allocator ordinal-reconstructible | `test_adr_0244_mode_order_independence.py` (3) | **Supported, restated (D-4)** |
| §2.10 | Quasi-periodic Fibonacci-word scheduler reduces phase-locking | audit-confirm the load-bearing claim | `test_adr_0244_scheduler_quasiperiodicity.py` (32): golden-ratio density, no `BB`/`AAA`, aperiodicity | **Supported** |

---

## 2. Deviations submitted for ruling (implementation vs. ADR prose)

- **D-1 — operator-preservation reframe (the core-mechanism correction; ratified 2026-07-17).** §2.1/§2.2's literal "project ψ_traj onto the grade-1 value subspace" is **vacuous** on the real runtime object: `final_state.F` is a **versor (even-grade operator, grades 0/2/4, zero grade-1)**, so `P_id(F) = 0` identically — it would flag every trajectory. Resolution: measure whether the versor *preserves* the value subspace via its action on the axes `F aᵢ F̃` — subspace leakage (tilt toward e4/e5) + signed self-alignment (in-subspace inversion). Both verified necessary and non-redundant. Governance annotation item 12 + §4a. **You ratified this reframe on 2026-07-17.**
- **D-2 — the identity gate is validated scaffolding, NOT a live gate (the honest headline).** See §5. `identity_wave_gate` stays **OFF**.
- **D-3 — `Q_top` dropped from the egress condition.** Proven vacuous (central `I₅` in odd Cl(4,1); the #19 pseudoscalar failure mode). Egress is leakage-based; `Q_top` kept only as a diagnostic. The §2.3 conservation claim is scoped to versors.
- **D-4 — §2.9 proven, not wired.** Recall is already insertion-order-independent by construction (Gram projection onto a span). Wiring the allocator into the durable content-seal path would be a category mismatch (that path seals content ψ, not packing positions), so the honest deliverable is the proof.

---

## 3. Deferred items (explicitly NOT completion blockers, but scoped)

- **The LIVE identity gate → ADR-0246.** Flipping `identity_wave_gate` on is deferred because the current engine gives the identity subspace no dynamical anchoring (§5). The induced-identity-action programme (ADR-0246 preflight brief, already merged) is where identity becomes dynamically load-bearing so the gate separates live traffic.
- **Real identity eigenmodes.** The shipped value axes (`truthfulness=e1`, `coherence=e2`, `reverence=e3`) are nominal basis vectors, not eigenmodes fit from an identity-preserving-vs-violating trace corpus. Fitting them is future work (a data/encoder concern, not a D4 mechanism gap).
- **Bounded corrective `C_id` displacement.** v1 is admit-or-abstain (zero displacement — the conservative bound). A bounded geometric corrective step is a future enhancement.

---

## 4. Gate results (this arc)

- Phase 0 (`ad37d03b`+`459280e3`): smoke 176 + provenance/ADR pins 30.
- Phase 1 (`3c3d2c29`): 25 new + smoke 176 + fast lane 11863/109.
- Phase 2 (`1c7ea26e`+`c7e2b3b6`+`c0ff4720`): 74 targeted + smoke 176 + fast lane 11889/109; flag-off byte-identity confirmed.
- Phase 3 (`f3702ad4`): 9 new + smoke 176 + fast lane 11897/109.
- Phase 4 (`918aa843`): 10 new + smoke 176 + fast lane 11907/109.
- Phase 5 (`5c69b741`+`4a550c1d`+`eacea087`+`b31d6fde`+docs): 43 targeted + smoke 176 + fast lane **12032 passed, 25 skipped** (with a local `core_rs` build, the ~126 Rust-parity + f32-speedup tests ran live, all green).

---

## 5. Requested action — and the one caveat that shapes it

**Rule on the ADR-0244 arc.** Every §-mechanism is built, proven, or audited (§1). The arc is honest and complete **as scaffolding**. There is exactly one thing you must weigh:

> **The identity wave-gate is BUILT and VALIDATED but is NOT wired live** (`identity_wave_gate = False`), and D4 does **not** flip it on. Phase 3 measured the reason directly: real benign turns do **not** preserve `span(e1,e2,e3)` — their leakage spans 0.14–0.81, self-alignment swings negative, and the best achievable balanced error separating benign from attacks is **0.346**. Flipping the flag would mass-refuse benign traffic. Root cause: the pack value axes are *nominal basis vectors, not dynamically-preserved eigenmodes* — the field evolution gives identity no dynamical anchoring. Making identity dynamically load-bearing is the **ADR-0246** programme.

So the ruling is on the ADR **as a specification and a validated mechanism**, with the explicit, recorded understanding that the live gate awaits ADR-0246. If you rule **Ratify**, the follow-up one-line governance commit flips `**Status**: Proposed → **Accepted** — ratified by Joshua Shay <date>` and records the ruling in §8. The four deviations (D-1…D-4) and the "validated-but-off" scope are submitted for acceptance as recommended. **I have not flipped the status; it awaits your explicit word.**

---

## 8. RULING RECORD

**PENDING — awaiting Joshua Shay's ruling.** No status flip has been made; ADR-0244 remains **Proposed**.
