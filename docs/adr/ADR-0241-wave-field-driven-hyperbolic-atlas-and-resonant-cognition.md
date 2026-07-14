# ADR-0241: Wave-Field Driven Hyperbolic Atlas and Resonant Algebraic Cognition

**Status**: Proposed — substrate + Slice-2/3 subsumption complete on branch (`wave_manifold`, operator delegates, multi-pair conjugacy thin wrap, resonant recall); acceptance path: Joshua review + merge
**Date**: 2026-07-13
**Deciders**: Joshua Shay + multi-model R&D
**Traceability**: Issue #14, parent #10
**Related**: ADR-0003, ADR-0006, ADR-0238, ADR-0239, ADR-0240, `core/physics/dynamic_manifold.py`, `core/physics/surprise.py`, `core/physics/goldtether.py`, `docs/analysis/core_ha_unification_and_deprecation_plan.md`
**Canonical path**: `docs/adr/`

---

## Context

CORE models meaning as a relational field over Cl(4,1) CGA (ADR-0003), not as flat embeddings. Third-Door operators (ADR-0238–0240) now have faithful Cartan–Iwasawa peel, Kabsch-conformal Procrustes, metric surprise, and partial GoldTether residual+α — still as **pointwise multivector / point-cloud** operators.

Legacy Hyperbolic Atlas / `core_ha` designs (and any pointwise \(H^n\) memory) suffer from:

1. **Thaw coordinate loss** — recall as approximate centroids drifts under noise.
2. **Node eviction rigidity** — discrete frozen nodes do not scale or decompress without reconstruction drift.
3. **Granularity discrepancy** — continuous sensorimotor streams vs discrete symbols force projection overhead in a shared point frame.

This ADR introduces the **Conformal Wave Field** \(\psi\) as the continuous representation layer under Third-Door operators: full subsumption of the hyperbolic atlas into a holographic resonant substrate, not a parallel path.

## Decision

### 1. Conformal wave field \(\psi\)

- \(\psi(X, t) \in Cl(4,1)\) is a multivector-valued field (runtime coefficients: 32-vector).
- In odd dimension \(n=5\), the unit pseudoscalar \(I = e_1 e_2 e_3 e_4 e_5\) is central and satisfies \(I^2 = -1\), so it acts as the native algebraic imaginary (no external \(\mathbb{C}\)).
- Algebraic Schrödinger step: \(\partial_t \psi = \mathcal{H}(\psi)\, I\), realized by a conformal rotor \(R(t) = \exp(B\,\Delta t) \in Spin(4,1)\).

### 2. Transport convention (pinned)

| Kind | Law | Rationale |
|------|-----|-----------|
| **Multivector field** (default for field-state operators) | Sandwich \(\psi' = R\,\psi\,\widetilde{R}\) | Matches `versor_apply` / existing Third-Door multivector ops |
| **Spinor / odd-capable wave packet** (chiral charge path) | Left multiply \(\psi' = R\,\psi\) | Spinor transport; needed for non-vacuous \(\mathcal{Q}\) |

Slice-1 code and tests document which API path uses which law. No silent mix.

### 3. Holographic standing-wave memory

\[
\Psi(X) = \sum_k c_k\,\psi_k(X)
\]

Recall is resonant phase lock-in (overlap + constructive interference), not coordinate thaw. Reconstruction-over-storage.

### 4. Third-Door operator reformulation

| Operator | Pointwise (landed) | Wave-field (this ADR) |
|----------|--------------------|------------------------|
| Conformal Procrustes | Kabsch / field conjugacy | Cross-spectral correlation \(\mathcal{C}_{AB}\) → Clifford polar decomposition for analogy rotor |
| Surprise | Metric-orthogonal residual | Non-resonant **spectral leakage** onto resonant eigenmodes |
| GoldTether | Harmonized drift + dist-to-\(\mathcal{I}_{gold}\) + \(\alpha=\Phi(R)\) | **Unitary amplitude** residual \(\sup\|\psi\widetilde{\psi}-1\|\) + optional chiral anomaly |
| Grade-5 / integrity | RETIRED on even versors (#19) | **Chiral spinor charge** \(\mathcal{Q}=\langle\psi I\widetilde{\psi}\rangle_0\) on general spinor \(\psi\) (non-vacuous) |
| Biography holonomy | `holonomy_encode` trajectory | Resonant standing-wave lock-in of unitary propagators |

### 5. Subsumption of `core_ha`

A separate pointwise `core_ha` database is **deprecated**. Absorption map: `docs/analysis/core_ha_unification_and_deprecation_plan.md`. In `core-labs/core` there is no live `core_ha/` tree; work is documentation + hygiene + wave substrate.

### 6. Module ownership

- **New**: `core/physics/wave_manifold.py` — continuous wave propagation, spectral leakage, polar analogy, unitary / chiral measures.
- **Upgrade in place** (later slices): `dynamic_manifold.py`, `surprise.py`, `goldtether.py`, `biography.py` **delegate into** wave primitives (no permanent dual path).
- **Containment**: wave substrate stays off the serve / wrong=0 path until gates pass. Discovery remains proposal-only (physics never imports teaching).

### 7. Implementation constraints (non-negotiable)

- Use live `algebra/*` (`geometric_product`, `reverse`, `versor_apply`, `rotor_power` / bivector exp). **No scipy matrix-proxy as algebraic truth** (ADR prototype sketch is illustrative only).
- `versor_condition` / unitary amplitude: dual-checked; fail-closed.
- Normalization only at owned construction boundaries — no hot-path unitize in wave propagate.
- Deterministic; no stochastic fallback; no ANN / cosine recall.

## Consequences

### Benefits

- Zero thaw loss via resonant lock-in.
- Multimodal superposition \(\psi_{\mathrm{total}}=\sum_{\mathrm{mod}}\psi_{\mathrm{mod}}\) with phase alignment.
- Non-vacuous topological integrity via spinor chiral charge (rehabilitates intent of Super §3.3 without reviving the vacuous even-versor gate).
- GoldTether grounded in unitary wave energy conservation.

### Trade-offs

- Spectral / exp-map cost → later Rust / MLX acceleration (ADR-0235), not Slice 1.
- Must carefully separate even field-state paths from odd-capable spinor paths so #19 retirement is not re-broken.

## Validation

Behavioral (not closure-only) tests in `tests/test_adr_0241_wave_manifold.py`:

1. Unitary / sandwich step conserves amplitude residual below \(10^{-6}\).
2. Spectral leakage zero on resonant span; positive off-span; metric-exact projection.
3. Wave polar recovers a known sandwich rotor (or left-spinor rotor on spinor path).
4. Chiral charge conserved under unitary \(R\) for odd-capable \(\psi\); even-only states remain honest about vacuous \(\mathcal{Q}\).
5. Fidelity ledger scorecard rows for wave substrate flip only when behavioral pins pass.

## Implementation notes

- Prototype sketch in earlier R&D dump is **not** shippable as written (scipy `expm`, ad-hoc \(I\) matrix). Re-express on Cl(4,1) 32-vectors.
- Ledger: `docs/research/third-door-blueprint-fidelity.md` § Wave-field substrate.
- GoldTether #18 bootstrap/prune remains **deferred** while wave unitary residual lands.
