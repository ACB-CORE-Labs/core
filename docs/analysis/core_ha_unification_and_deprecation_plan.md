# Technical Memorandum: core_ha Integration, Substrate Unification, and Deprecation Plan

**Status**: Proposed (acceptance path: tests green + Joshua review)
**Date**: 2026-07-13
**Authors**: Multi-model R&D + Joshua Shay
**Traceability**: Notion R&D (Reference Vault Interconnection: `core_HA` Patterns)
**Related**: ADR-0003, ADR-0238, ADR-0239, ADR-0240, ADR-0241, `core-rs/src/vault.rs`
**Canonical path**: `docs/analysis/core_ha_unification_and_deprecation_plan.md`

---

## 1. Executive summary

**A separate, standalone `core_ha` coordinate database is mathematically redundant, architecturally incompatible with ADR-0003 coordinate dissolution, and should be fully deprecated.**

Unification target: single-substrate Cl(4,1) conformal wave-field \(\psi\) (ADR-0241) plus CRDT-gated delta sync at the storage boundary.

- Meaning = continuous wave-field \(\psi(X,t)\in Cl(4,1)\), not discrete points on \(H^n\).
- Relations = geometric phase interference / algebraic inner products, not coordinate distance.
- Sync = commutative, associative, idempotent sharded Delta-CRDT registers (exact-recall determinism).

Keeping `core_ha` as a pointwise store would reintroduce thaw decay and non-commutative BCH drift the wave-field frame eliminates.

## 2. Legacy gaps resolved by wave subsumption

| Legacy gap | Wave-field resolution |
|------------|------------------------|
| Thaw coordinate loss | Holographic standing-wave lock-in reconstructs at resonance spikes |
| Node eviction rigidity | Memory as continuous eigenmode spectrum of \(\mathcal{H}\); algebraic scale/compress |
| Granularity discrepancy | \(\psi_{\mathrm{total}}=\psi_{\mathrm{text}}+\psi_{\mathrm{audio}}+\psi_{\mathrm{vision}}+\psi_{\mathrm{motor}}\) phase alignment |

## 3. File-by-file deprecation and absorption map

| Legacy `core_ha` file | Status in `core-labs/core` | Absorption path |
|-----------------------|----------------------------|-----------------|
| `hyperbolic_primitives.py` | **Obsolete** (not present) | Proximity via `algebra/cga.py`, `algebra/cl41.py` |
| `atlas_id.py` | **Obsolete** (not present) | Resonant lock-in; no explicit coordinate node IDs |
| `operator_plane.py` | **Absorbed concept** | Rotors/translators/dilators in `dynamic_manifold.py` + `core-rs` versor path |
| `runtime_memory.py` | **Subsumed concept** | Field energy operator (`core/physics/energy.py`) E2–E3 active / E0–E1 deep |
| `consolidation.py` | **Subsumed concept** | Thermodynamic cooling → CRDT vaulting |
| `steward.py` | **Subsumed concept** | GoldTether monitor (`goldtether.py`) + unitary residual (ADR-0241) |
| `tombstone.py` | **Subsumed concept** | Delta-CRDT semilattice (`core/sync/`, `core-rs` vault) |

**Inventory fact (2026-07-13):** this repository has **no** `core_ha/` package tree. Deprecation work is documentation, import hygiene, and wave-substrate implementation — not a bulk delete of live modules.

## 4. Integration roadmap

### Step 1 — Hygiene

1. Confirm no `core_ha` / `hyperbolic_primitives` imports in CLI or eval loops (grep-clean).
2. Remove any Poincaré-coordinate fixtures if reintroduced.
3. Keep this memo as the absorption authority.

### Step 2 — Wave substrate (ADR-0241)

1. Land `core/physics/wave_manifold.py` with algebra-native unitary step, spectral leakage, polar analogy, chiral charge.
2. Later: optional Rust/MLX hot-path for bivector exp and cross-spectral correlation.

### Step 3 — Operator wiring

1. Surprise → spectral leakage (same discovery eligibility contract).
2. GoldTether → unitary amplitude residual (bootstrap/prune of \(\mathcal{I}_{gold}\) still deferred under #18).
3. Biography → holonomy of unitary propagators / resonant lock-in.

## 5. Mathematical invariant safeguards

1. **Unitary / sandwich residual:** \(\|\psi\widetilde{\psi}-1\|_F < 10^{-6}\) (dual-checked); fail-closed on breach.
2. **Chiral charge sign** (spinor path): \(\mathrm{sgn}(\langle\psi I\widetilde{\psi}\rangle_0)\) conserved under unitary \(R\).
3. **Hamiltonian / exertion energy boundary** (later motor work): action energy bounded by sensory energy — out of Slice 1 scope.
4. **Serving containment:** wave operators do not enter the wrong=0 serve path until explicit gates pass.

## 6. Validation

- ADR-0241 behavioral suite: `tests/test_adr_0241_wave_manifold.py`
- Fidelity ledger wave section: `docs/research/third-door-blueprint-fidelity.md`
- Regression: existing Third-Door ADR-0238/0239/0240 tests remain green under subsumption
