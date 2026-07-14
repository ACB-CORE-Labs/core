# Brief: ADR-0242 Atlas Packing + Fibonacci Section Search

**For:** Antigravity / Gemini design pass  
**From:** CORE ADR-0241/0242 mastery implementation (`feat/adr-0241-0242-implementation`)  
**Date:** 2026-07-14  
**Status:** STOP POINT — do not implement packing/Fibonacci in Grok Build until this design returns and is reviewed against `AGENTS.md`

---

## Why this handoff exists

ADR-0241 local wave operators are GREEN. Entity cohesion mastery still needs:

1. **Hyperbolic Atlas mode packing** (Golden-Angle / phyllotaxis on the Cl(4,1) horosphere) with fail-closed geodesic separation \(d_{\min}=0.12\).
2. **Fibonacci section search** for fixed-budget unimodal line search (GoldTether κ / Procrustes residual brackets).

These are **ADR-0242 track** work under `docs/analysis/core_cohesion_master_plan.md`. They require careful algebraic design so we do **not**:

- resurrect `core_ha` or Poincaré as runtime memory truth (ADR-0003);
- introduce cosine/ANN recall;
- wire anything into `chat/runtime.py` serve path (A-04 quarantine);
- use scipy matrix-proxy as algebraic truth;
- implement R-01 “nearest versor dual-correction” as hot-path drift repair (fail-closed only).

---

## Authority documents

| Doc | Role |
|-----|------|
| `docs/analysis/core_cohesion_master_plan.md` | Entity traces, I-01…I-05, \(d_{\min}\), Fibonacci suite sketch, R-01…R-04 |
| `docs/analysis/core_ha_unification_and_deprecation_plan.md` | core_ha absorption map |
| Fibonacci R&D `.docx` | Phyllotaxis formulas, Fibonacci search prototype, multi-scale τ |
| `docs/adr/ADR-0241-...md` | Wave substrate contract |
| `AGENTS.md` | versor_condition, no ANN, construction-boundary only unitize |

---

## Section A — Golden-Angle atlas packing

### Required design deliverables

1. **Construction-only lift** from Poincaré polar \((\theta_k, r_k)\) to Cl(4,1) null/horosphere multivectors:
   - \(\theta_k = 2\pi k \phi^{-1}\)
   - \(r_k = \tanh(\alpha \sqrt{k})\)
2. **Geodesic separation** on the horosphere (define exact formula with `cga_inner` / null-point tools). Reject allocation if any pair \(d < 0.12\).
3. **Registration API** into `WaveManifold.register_resonant_mode` / optional `HolographicVaultStore.seal_mode` (SPECULATIVE default).
4. **No node IDs**, no thaw coordinates as storage truth.
5. **Insertion cost** metrics only in `evals/` or `calibration/` (R-04 gated observability — not serve hot path).

### RED tests the design must specify (that current code cannot pass)

```text
test_golden_angle_pack_n_modes_min_geodesic_ge_0_12
test_golden_angle_pack_rejects_when_alpha_too_dense
test_packing_lift_produces_closed_or_null_legal_points
test_packing_deterministic_for_fixed_alpha_n
test_no_poincare_runtime_storage_in_wave_or_vault_metadata_truth
```

### Non-goals

- Live `core_ha` package
- Serving-path packing
- Approximate nearest-neighbor packing repair

---

## Section B — Fibonacci section search + GoldTether κ

### Required design deliverables

1. Module sketch: `core/physics/fibonacci_search.py`
   - `BoundedUnimodalObjective(lower, upper, evaluation_budget, objective_id, objective_version)`
   - `fibonacci_section_search(objective, func) -> SearchTrace`
   - `SearchTrace`: `best_observed_point`, `eval_sequence`, certificate fields
2. Fail-closed on nonfinite, bounds violation, multi-extrema when validator enabled.
3. Integration surface: optimize synthetic \(\kappa\) residual; later optional Procrustes residual under fixed N evals (Fidelity Score).
4. **A-04:** must not be importable from `chat/runtime.py` (already AST-pinned in `tests/test_third_door_cohesion.py`).

### RED tests

```text
test_fibonacci_search_hits_known_unimodal_min_within_1e-3
test_fibonacci_search_eval_count_equals_budget
test_fibonacci_search_rejects_nan_objective
test_fibonacci_search_unimodality_violation_fail_closed  # optional if validator included
test_serve_runtime_still_quarantines_fibonacci_search
```

### Non-goals

- Stochastic optimizers
- Serve-path κ adaptation
- Cryptographic hashing on every hot-path eval (R-04: traces in calibration only)

---

## Implementation constraints (hard)

| Constraint | Rule |
|------------|------|
| Algebra | `algebra/*` only for field truth |
| Closure | `versor_condition < 1e-6` at construction boundaries |
| Epistemic | Packing modes seal SPECULATIVE unless reviewed |
| Mutation | Vault writes only via `VaultStore.store` (INV-21) |
| Determinism | No `np.random` in behavioral tests |
| R-01 | Fail-closed on residual breach; no silent unitize repair in hot paths |

---

## What already landed (do not redesign)

| Surface | Status |
|---------|--------|
| `WaveManifold` sandwich / left-spinor / spectral leakage / unitary residual | GREEN |
| `resonant_recall` + `resonant_reconstruct` + `phase_correlation` | GREEN |
| `HolographicVaultStore` + public `VaultStore.get_versor` | GREEN |
| Entity cohesion suite skeleton | `tests/test_third_door_cohesion.py` |
| Serve quarantine AST | GREEN |

---

## Resume condition for Grok Build

Return a design note (Markdown) that:

1. Chooses exact horosphere geodesic formula and packing API signatures.  
2. Chooses Fibonacci search API + certificate schema.  
3. Lists RED tests with expected failures on current `main`/branch.  
4. Confirms AGENTS.md compliance (especially no hot-path drift repair).  

Then Grok Build will TDD-implement P4/P5 and draft `docs/adr/ADR-0242-*.md`.

---

## Suggested dual-ADR split (for your draft)

- **ADR-0241:** wave field, spectral leakage, polar (true polar still open), holographic vault, entity I-04/I-05.  
- **ADR-0242:** atlas packing + Fibonacci search + optional multi-scale energy \(\tau_n=F_n\tau_0\).
