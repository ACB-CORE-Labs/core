# ADR-0242: Hyperbolic Atlas Golden-Angle Packing and Fibonacci Search

**Status**: Proposed — packing + Fibonacci search + multi-scale τ schedule green; **ready for Joshua acceptance review** (do not self-Accept). Checklist: `docs/audit/adr_0241_cohesion_acceptance_checklist.md`.
**Date**: 2026-07-14  
**Deciders**: Joshua Shay + multi-model R&D (Gemini implementation pass)  
**Traceability**: PR #37, parent ADR-0241 / cohesion master plan  
**Related**: ADR-0003, ADR-0238, ADR-0241, `docs/analysis/core_cohesion_master_plan.md`, `docs/briefs/ADR-0242-atlas-packing-and-fibonacci-brief.md`  
**Canonical path**: `docs/adr/`

---

## Context

ADR-0241 established `WaveManifold` and `HolographicVaultStore`. Entity cohesion still needed:

1. **Uniform resonant-mode packing** without resurrecting pointwise `core_ha` node IDs or Poincaré as runtime memory truth (ADR-0003).
2. **Fixed-budget unimodal scalar search** for construction/calibration (e.g. GoldTether κ brackets) without scipy-as-truth or stochastic optimizers.

## Decision

### 1. Golden-Angle packing (`core/physics/atlas_packing.py`)

For \(k = 0 \ldots n-1\):

\[
\theta_k = 2\pi k / \varphi,\qquad r_k = \tanh(\alpha\sqrt{k})
\]

Lift \((r\cos\theta, r\sin\theta, 0)\) via `algebra.cga.embed_point` to Cl(4,1) **null points**.

**Separation pin:** CGA null-point distance from `cga_inner` contract \(\langle P,Q\rangle = -d^2/2\):

\[
d = \sqrt{-2\langle P,Q\rangle}
\]

Fail-closed (`AtlasPackingError`) if any pair has \(d < d_{\min}\) (default \(0.12\)).

**Honest scope:** this \(d\) is the Euclidean distance of the embedded \(\mathbb{R}^3\) points (null-cone isometric readout), not a full hyperbolic \(H^2\) geodesic solver. Sufficient for the cohesion packing density gate.

**No attribute leaks:** returned modes are pure `float64` 32-vectors. No stored θ/r.

**Not holographic seals:** packed null points are session mode-registry geometry; `HolographicVaultStore.seal_mode` still requires closed unit versors.

### 2. Fibonacci section search (`core/physics/fibonacci_search.py`)

- `BoundedUnimodalObjective(lower, upper, evaluation_budget, objective_id, objective_version)`
- `fibonacci_section_search(objective, func) -> SearchTrace`
- Exactly `evaluation_budget` evaluations
- Fail-closed on nonfinite, bounds violation, sampled unimodality violation
- Certificate carries budget, ids, bounds, best value, n_evals

### 3. Serve quarantine (A-04)

Neither module may be imported from `chat/runtime.py`. Pinned in `tests/test_third_door_cohesion.py`.

## Consequences

### Benefits

- Deterministic atlas packing for standing-wave mode placement
- Algebra-native fixed-budget scalar search for κ / residual brackets
- Continues `core_ha` deprecation (no node IDs / Poincaré runtime store)

### Trade-offs

- Separation is CGA null-point Euclidean distance, not full hyperbolic geodesic
- Unimodality check is sample-based (only evaluated points), not a global oracle
- Packing modes are null points, not unit versors — durable vault seal path remains separate

## Validation

- `tests/test_adr_0242_atlas_packing.py`
- `tests/test_adr_0242_fibonacci.py`
- `tests/test_third_door_cohesion.py` (serve quarantine + κ integration)
