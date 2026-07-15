# ADR-0242: Deterministic Fibonacci Operators and Evidence-Gated Optimization

**Status**: Proposed — V1 cert discipline + V3 packing landed; V2/V4/V5 staged; **not** self-Accepted (Joshua review).  
**Date**: 2026-07-13 (Drive authority); in-repo expansion 2026-07-15  
**Deciders**: Joshua Shay + multi-model R&D  
**Traceability**: Drive ADR-0242 (`15_NECCPy-tEWGfYi_BNqawm8GytUTMkz1DsOqGVMXhI`), PR #37/#38, cohesion plan  
**Related**: ADR-0003, ADR-0238, ADR-0239, ADR-0240, ADR-0241, `docs/analysis/fibonacci_applications_in_core_substrate.md`, `docs/analysis/core_cohesion_master_plan.md`  
**Canonical path**: `docs/adr/`  
**Filename note**: file keeps historical path `ADR-0242-atlas-packing-and-fibonacci.md`; **title/scope match Drive**.

---

## Context

ADR-0241 establishes continuous wave-field \(\psi\). Optimization, scheduling, and multi-scale allocation still need deterministic, reconstructible operators that **earn their place** under CORE’s evidence discipline — not sacred-geometry dogma.

Drive ADR-0242 defines **five Fibonacci vectors**. An earlier in-repo draft understated that thesis as packing + section search only. This document restores the full scope and records honest landing status.

---

## Sovereignty invariant (absolute)

**Fibonacci operators may optimize search parameters, set observation scale, or schedule background checks; they must NEVER dictate proposition truth, safety policy, identity, or authorize autonomous COHERENT promotion.**

Active reasoning, vault standing, and serve remain governed by versor closure, CRDT exactness, and human-gated review.

---

## Decision — five vectors

### Vector 1 — Bounded Fibonacci-section search (production Phase 1) 🟢

Module: `core/physics/fibonacci_search.py`

- `BoundedUnimodalObjective`
- `fibonacci_section_search(objective, func) -> FibonacciSearchCertificate | OptimizationFailure`
- **Never** returns a bare float
- Certificate is content-addressed (`cert_id` = SHA-256 of ordered trace + ids)
- Fail-closed: nonfinite, bounds, unimodality multi-extrema → `OptimizationFailure`
- κ seam: `propose_kappa_from_search` / `goldtether.propose_kappa_line_search`  
  - success → proposed κ = minimizer (telemetry; no auto state mutation)  
  - failure → **baseline κ = 1.0**

### Vector 2 — Multi-scale temporal basis (research) 🟡

Drive:

\[
E_n(t) = E_n(t_0)\,\exp\bigl(-(t-t_0)/(F_n\tau_0)\bigr)
\]

Landed progressive form: `fibonacci_tau_schedule` / `recency_band_index` in `wave_energy_boundary.py` (constants table).  
**Not** yet production default inside `FieldEnergyOperator`. Promotion requires comparative benchmark vs dyadic \(2^n\tau_0\) (Drive comparative hypothesis).

### Vector 3 — Golden-Angle mode allocator 🟢

Module: `core/physics/atlas_packing.py`

- Golden-Angle polar lift via `embed_point` → null 32-vectors  
- Fail-closed if pairwise CGA null-point \(d < d_{\min}\) (default 0.12)  
- Honest metric: Euclidean null-cone readout, **not** full \(H^2\) geodesic  
- Reconstruction-over-storage: `ALLOCATOR_VERSION = golden_angle_v1` + `allocator_layout_descriptor`  
- Not holographic seals (null points ≠ closed unit versors)

### Vector 4 — Fibonacci-word observability choreography 🔴 staged

Drive: \(W_0=B, W_1=A, W_{n+1}=W_n W_{n-1}\) for telemetry / sealed-holdout sampling.  
**Outside cognitive truth path.** Not yet implemented (plan D5).

### Vector 5 — Topological anyon / braid holonomy 🔴 research quarantine

Drive: isolated `algebra/topological_reasoning/` study; blocked from production.  
Not implemented (plan D6). Must not enter serve/FFI until proofs exist.

---

## Phase order (Drive §5)

| Phase | Vector | Status |
|-------|--------|--------|
| 1 | V1 search + κ cert gate | 🟢 |
| 2 | V2 multi-scale energy study | 🟡 table only |
| 3 | V3 packing | 🟢 |
| 4 | V4 word scheduler | 🔴 |
| 5 | V5 anyons | 🔴 quarantine |

---

## Serve quarantine (A-04)

`fibonacci_search`, `atlas_packing`, `wave_energy_boundary` must not be imported from `chat/runtime.py` (AST pin in `tests/test_third_door_cohesion.py`).

---

## Consequences

### Benefits

- Evidence-gated optimizers (typed cert/failure)  
- Deterministic packing without `core_ha` node IDs  
- Clear multi-vector roadmap without dogma  

### Trade-offs

- Sample-based unimodality (not global oracle)  
- Packing separation not full hyperbolic geodesic  
- V2 production promotion deferred pending benchmarks  

---

## Validation

- `tests/test_adr_0242_fibonacci.py` — cert/failure + dual-run digest + κ fallback  
- `tests/test_adr_0242_atlas_packing.py`  
- `tests/test_third_door_cohesion.py` — serve quarantine + κ integration  
- `tests/test_adr_0241_wave_energy_boundary.py` — \(\tau_n\) table  

---

## Acceptance path

Joshua review may Accept after Phase 1 (V1+V3) is verified in merge.  
V2/V4/V5 need not block Phase 1 Accept if status rows remain honest RESEARCH/staged.  
Agents **must not** self-Accept.
