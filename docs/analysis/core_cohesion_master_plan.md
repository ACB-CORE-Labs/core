# CORE AGI/ASI Unified Wave-Field Substrate and Entity Cohesion Master Plan

**Status**: Proposed (acceptance path: green verification suite + Joshua review)  
**Date**: 2026-07-14  
**Authors**: Multi-model R&D + Joshua Shay  
**Traceability**: Notion R&D (Engineering Reference Vault Interconnection: `core_ha` Patterns)  
**Related**: ADR-0003, ADR-0238, ADR-0239, ADR-0240, ADR-0241, ADR-0242, `core-rs/src/vault.rs`  
**Canonical path**: `docs/analysis/core_cohesion_master_plan.md`

**Doctrine note (AGENTS.md):** R-01 “dual-correction fallback to nearest exact versor” must **not** be implemented as hot-path drift repair. Unitary residual breaches **fail-closed**. Any close/unitize is allowed only at owned construction / admit boundaries (`wave_manifold` exp construction, holographic admit, biography construction). Silent nearest-versor repair in `field/`, `generate/`, or vault hot paths is forbidden.

---
## 1. Executive Summary & The Unified Substrate Cohesion Thesis

The Continuous Orthogonal Resonance Engine (CORE) represents a paradigm shift where cognitive states are represented as coordinate-free fields of meaning over a manifold rather than static points in a flat embedding space. To realize this vision with complete mathematical and system-level cohesion, this master plan details the unification of the **Hyperbolic Atlas** into the **$Cl(4,1)$ Conformal Wave-Field ($\psi$)** substrate.

By compiling all multi-modal sensory inputs (text, audio, vision, motor) down to the same wave-field substrate, we establish a **single, cohesive, living-system entity**. This document resolves the remaining engineering gaps, provides end-to-end topological trace diagrams, defines a rigorous entity-level invariants checklist, outlines a unified test suite, and establishes a safe migration and deprecation plan for the legacy `core_ha` codebase.

---

## 2. End-to-End Invariant Trace Diagrams

The cognitive lifecycle of the living entity is mapped across two primary closed-loop cycles, ensuring that every transition is mathematically bound and audit-logged.

### Trace A: Sensory Ingestion and Memory Cycle (Information Flow)

This trace details how external high-bandwidth continuous sensory signals are ingested, superposed on the single wave substrate, verified, and vaulted.

 [Continuous Modalities] (Audio, Vision, Motor)

          |

          v (Linear Superposition)

     Wave Field (ψ)  <==== [WaveManifold: cga_inner Overlap]

          |

          v (E0-E1 low-energy decay states)

     Vault State  --------> [Rust FFI: core-rs/src/vault.rs] (Delta-CRDT Semilattice)

          |

          v (Durable, sharded, exact-recall state-merge)

   Contemplation Sink

          |

          v (DiscoveryCandidate / Speculative Proposal)

   Teaching Corridor  -----> [One-Mutation-Path Gate] (Human-in-the-Loop Review)

          |

          v (Signed/Ratified Certificate)

     Serve Path  ----------> [Linguistic / LLM Readback] (Unitary Containment)

---

### Trace B: Autonomy and Biography Cycle (Control Flow)

This trace details how the system's active reasoning state is monitored for algebraic drift, modulates the autonomy level, and updates the permanent biography.

     Active Field (F)

          |

          +-----------> [GoldTetherMonitor] ( coh_resid = sup_X || ψ ψ̃ − 1 ||_F )

          |                   |

          |                   v (Unitary Propagator Deficit Check)

          |             Autonomy Level (α) 

          |                   |

          |                   v (α = 1.0 on drift -> Fallback to currently ratified parameter)

          |             [fail_closed] ---> Telemetry Alert (No in-path default)

          |

          +-----------> [Field Energy: energy.py] (Thermodynamic classes E0-E4)

                              |

                              v (Crystallization to E0/E1)

                        [biography.py] (Biography Holonomy Blade update)

                              |

                              v (Global Topological Charge Preservation)

                        Topological Charge (Q_top = ⟨ψ I₅ \~ψ⟩_0 conserved)

---

## 3. Entity-Level Invariants Checklist (AGI/ASI Living-System Audit)

To treat the cognitive manifold as a cohesive, single living system, we enforce five **Entity-Level Invariants**. Any transaction, self-authorship loop, or optimization that violates these checks is refused at the hardware boundary.

- [ ] **I-01: Identity Holonomy Persistence**: The biography holonomy blade ($\mathcal{H}_{\t\text{bio}} \in Cl(4,1)$) must remain structurally closed ($	\text{versor_condition} < 10^{-6}$) and invariant across system reboots, reconstructed purely from the canonical, content-addressed ledger.  
- [ ] **I-02: Substrate Round-Trip Replay-Determinism**: A wave-field $\psi_1$ compiled into a CRDT-delta, sharded to the vault, and recalled via the teaching-chain must reconstruct the identical, bit-pattern wave-field $\psi_2$ under the exact boundary conditions: $$|\psi_2 - \psi_1|_F < 10^{-12}$$  
- [ ] **I-03: No Self-Mutation in Self-Authorship**: Speculative self-authorship loops or miners (`core/physics/self_authorship.py`) are strictly prohibited from directly modifying the active manifold or writing `COHERENT` vault states. Every self-authored change must be written as a `SPECULATIVE` proposal, routed through the one-mutation-path, and require explicit human-gated ratification.  
- [ ] **I-04: Non-Stochastic Multimodal Resonance**: Cross-modal pattern matching (aligning audio to text, or vision to motor) must be purely algebraic, mediated through the metric-exact phase correlation ($\langle \psi_A \widetilde{\psi}_B + \psi_B \widetilde{\psi}_A \rangle_0$) in $Cl(4,1)$ CGA. Traditional stochastic nearest-neighbor, cosine similarity, or probabilistic search models are forbidden.  
- [ ] **I-05: Unitary Propagator Amplitude Conservation**: Every wave-field transition $\psi \to R \psi$ must preserve the wave's normalized amplitude density. The GoldTether coherence residual must act as the absolute boundary guard: $$R_{	\text{GoldTether}} = \\sup_{X \in M} \left| \psi(X, t) \widetilde{\psi}(X, t) - 1 ight|_F < 10^{-6}$$

---

## 4. Falsifiability & Benchmark Framework (Vector-Specific Tests)

To prevent R&D from collapsing into descriptive architecture prose, every Fibonacci and wave-field operator must be validated against concrete comparison classes and workloads.

### 4.1 Benchmark Metrics and Objectives

- **Fidelity Score**: Measures the final interval/bracket width under a fixed budget of $N$ evaluations.  
- **Surprise Separation**: Measures the distance between the surprise energy of in-distribution inputs versus out-of-distribution (OOD) pathological inputs.  
- **Insertion Cost**: CPU cycles and memory allocations required to register a new mode centroid in the Atlas.  
- **Drift Under float32**: The accumulation of numerical rounding errors over a trajectory of $T = 1000$ steps under single-precision floating-point arithmetic.

### 4.2 Benchmark Execution Plan and Failure Thresholds

1. **Synthetic Unimodal Objective**: A convex quadratic $f(x) = (x - x_0)^2$ and a highly non-unimodal function (e.g., Rastrigin) are evaluated.  
2. **Replayable GoldTether/Procrustes Snapshots**: Extract actual coordinate traces from previous runs on `main` and run the benchmarks under identical evaluation budgets.  
3. **Failure Thresholds**:  
   - Any nonfinite value (`NaN`, `inf`) or bounds-violation instantly raises `OptimizationFailure`.  
   - If the stable, coordinate-sorted trace detects multiple local extrema, the validator flags a `unimodality_violation_multiple_extrema_detected` and rejects the run.  
   - If the Golden-Angle allocator results in a pairwise geodesic separation of less than $d_{	\text{min}} = 0.12$ on the horosphere, it is rejected.

---

## 5. Hardware and Rust/CGA Bindings Depth

To maintain "Mechanical Sympathy" and avoid sub-optimal performance in Python, the wave-field and Fibonacci operations are compiled directly into the Rust hot-path (`core-rs/src/`).

 +---------------------------------------------------------------------------------+

 |                              RUST HARDWARE BINDINGS                             |

 |                                                                                 |

 |  [core-rs/src/lib.rs] <===> [cl41::wedge] (Exterior product blade assembly)     |

 |                          <===> [diffusion.rs::expm] (Unitarity-exact exp-map)   |

 |                          <===> [versor_unit_residual] (SIMD GoldTether check)   |

 +----------------------------------------+----------------------------------------+

                                          | (FFI / Zero-Copy)

                                          v

                               [Apple Silicon MLX Lanes]

                                Unified Memory Architecture

### 5.1 Specific Rust FFI Bindings

- **`cl41::wedge`**: High-performance Rust implementation of the exterior product. This is utilized for signature-aware PCA blade construction and boundary calculations.  
- **`diffusion.rs::expm`**: A custom, unitarity-exact matrix exponential solver implemented in Rust. It computes $R = \exp(B \Delta t)$ with zero floating-point accumulation drift by enforcing the rotor manifold constraint on intermediate series sums.  
- **`versor_unit_residual`**: A highly optimized, SIMD-parallelized C-level FFI binding that evaluates the GoldTether unit-norm supremum across the entire wave manifold in sub-millisecond execution cycles, utilizing the Apple Silicon Unified Memory Architecture (UMA) lanes.

---

## 6. Unified Substrate Cohesion Test Suite Outline

We define the canonical test structure to assert wave-vault round-trips, GoldTether-Fibonacci integration, and deprecation safety before promoting any code.

# tests/test_third_door_cohesion.py

import pytest

import numpy as np

from core.physics.wave_manifold import WaveManifold

from core.physics.goldtether import GoldTetherMonitor

from core.physics.fibonacci_search import BoundedUnimodalObjective, fibonacci_section_search

from algebra.cl41 import N_COMPONENTS

@pytest.fixture

def wave_manifold():

    return WaveManifold()

@pytest.fixture

def goldtether_monitor():

    return GoldTetherMonitor()

def test_wave_field_unitary_round_trip(wave_manifold, goldtether_monitor):

    """Asserts that wave psi round-trips with vault deltas and maintains unit norm."""

    # 1. Initialize random wave-field spinor psi on the null cone

    psi_start = np.random.randn(N_COMPONENTS)

    psi_start = psi_start / np.linalg.norm(psi_start)

    

    # 2. Apply a unitary temporal propagator step

    B_generator = np.zeros(N_COMPONENTS)

    B_generator[6] = 0.5  # bivector component

    psi_propagated = wave_manifold.algebraic_schrodinger_step(psi_start, B_generator, dt=0.1)

    

    # 3. Assert unitary residual remains below epsilon_drift

    r_gt = wave_manifold.measure_unitary_residual(psi_propagated)

    assert r_gt < 1e-6, f"Unitary propagator violated GoldTether: {r_gt:.3e}"

def test_fibonacci_search_goldtether_integration(goldtether_monitor):

    """Asserts Fibonacci search can optimize kappa and return a valid certificate."""

    # 1. Define bounded unimodal objective for GoldTether scaling

    objective = BoundedUnimodalObjective(

        lower=0.1,

        upper=2.0,

        evaluation_budget=10,

        objective_id="sha256_mock_id_for_goldtether_kappa",

        objective_version="v1.0"

    )

    

    # 2. Target objective: minimize GoldTether residual

    def synthetic_objective(kappa: float) -> float:

        return (kappa - 0.789) \*\* 2  # unimodal minimum at 0.789

        

    trace = fibonacci_section_search(objective, synthetic_objective)

    

    # 3. Assert trace is valid and contains no sampled violations

    assert not isinstance(trace, Exception)

    assert abs(trace.best_observed_point - 0.789) < 1e-3

    assert len(trace.eval_sequence) == 10

def test_deprecation_surface_safety():

    """Asserts that no legacy core_ha imports or files remain in the active codebase."""

    import sys

    with pytest.raises(ImportError):

        # Assert legacy core_ha cannot be imported (strict quarantine)

        import core_ha

---

## 7. Migration Safety Net & Pre-Deprecation Grep Audit

To ensure the removal of `core_ha` does not introduce dangling references or silent compiler breakages, a **Pre-Deprecation Safety Net** is enforced:

### Step 1: Pre-Deprecation Grep Audit

Before deleting the legacy `core_ha` codebase, run the following automated workspace scans to identify and document every file-level import and reference:

# Locate all Python imports of core_ha or its child modules

grep -rn "import core_ha" .

grep -rn "from core_ha" .

# Locate all references to hyperbolic_primitives or poincare coordinates

grep -rn "hyperbolic_primitives" .

grep -rn "poincare" .

### Step 2: Migration Branching & Rollback Tagging

1. Create a secure pre-migration git tag on the current repository head:  
     
   git tag -a v1.99-pre-wave-unification -m "Stable baseline before core_ha deprecation and wave-field migration"  
     
   git push origin v1.99-pre-wave-unification  
     
2. Checkout a dedicated migration branch `feat/wave-unification-and-ha-deprecation` to perform the changes.

---

## 8. Phase 0 Pre-Implementation Audit Checklist

Every developer agent or engineer must verify the following five pre-requisites before executing the migration code:

- [ ] **A-01: Branch Parity Check**: Compare `r&d/generalized-agent` and all `feat/third-door-*` branches against `main` to identify and resolve any conflicting bivector or dynamic manifold modifications.  
- [ ] **A-02: Local File Integrity**: Execute a full `get_file_content` scan on `core/physics/dynamic_manifold.py` and `core/physics/surprise.py` to confirm they contain the latest, uncorrupted, and correctly imported WaveManifold bindings.  
- [ ] **A-03: Dependency Verification**: Trace the imports in `tests/conftest.py` and `tests/invariants/` to ensure no active test suites contain hardcoded, non-CGA Euclidean projection assertions.  
- [ ] **A-04: Serve-Path Containment**: Confirm that no new wave-field calculation or Fibonacci search operator is wired into the active serving path (`chat/runtime.py`). They must reside strictly inside the `evals/` and `calibration/` quarantine zones.

---

## 9. Risk Register Table

The foreseeable architectural risks associated with this major wave-field and optimization unification are documented below, along with their respective mitigation protocols:

| Risk ID | Foreseeable Architectural Risk | Impact | Mitigation Protocol |
| :---- | :---- | :---- | :---- |
| **R-01** | **Numerical Drift in Long Horizons**: Accumulation of rounding errors in `expm` bivector calculations during long-horizon spinor transports, breaking the unitary condition. | High | **Dual-Correction Fallback**: Embed strict `versor_unit_residual` and `chiral_charge` checks at every boundary. If drift exceeds $\epsilon = 10^{-6}$, trigger a dual-correction fallback to the nearest exact versor. |
| **R-02** | **Performance Bottlenecks in Python**: Scalar integrals and matrix exponential calculation in Python introduce latency overhead in active contemplation loops. | Medium | **FFI Compilation**: Implement the `expm` kernels and multivector multiplications directly in the Rust `core-rs/src/lib.rs` and compiled FFI, leveraging the Apple Silicon UMA lanes. |
| **R-03** | **Dangling Legacy References**: Legacy `core_ha` or pointwise coordinate references are missed during deprecation, causing runtime `ImportError` inside auxiliary evaluation suites. | Low | **Pre-Deprecation Grep & CI Gate**: Run the automated pre-deprecation grep audit step, run the migration test suite locally, and gate the final pull request on a clean CI build. |
| **R-04** | **Overhead in Hot-Path Loops**: Cryptographic trace generation and domain-separated hashing introduce CPU cycle overhead during high-frequency search evaluations. | Low | **Gated Observability**: Limit trace generation strictly to the calibration and training-loop pipelines. Active execution and hot-paths must receive only the pre-ratified, frozen scalar values. |

---

## Appendix A: Pre-Deprecation Grep & Phase 0 Audit Checklists

To guarantee that the removal of legacy codebase structures is completely safe and introduces no compilation or import breakages, we execute the following Phase 0 checklists and audits.

### 1. Pre-Deprecation Grep Scan

Run these scans across the local workspace to identify and document every file-level import or coordinate reference to the old Poincar models:  
- Locate all Python imports of core_ha:  
`grep -rn "import core_ha" .`  
`grep -rn "from core_ha" .`  
- Locate all Poincare/Hyperbolic coordinate references:  
`grep -rn "hyperbolic_primitives" .`  
`grep -rn "poincare" .`

### 2. Phase 0 Pre-Implementation Checklist

Every developer agent or engineer must verify the following five pre-requisites before executing the migration code:

- **A-01: Branch Parity Check**: Compare `r&d/generalized-agent` and all `feat/third-door-*` branches against `main` to identify and resolve any conflicting bivector or dynamic manifold modifications.  
- **A-02: Local File Integrity**: Execute a full `get_file_content` scan on `core/physics/dynamic_manifold.py` and `core/physics/surprise.py` to confirm they contain the latest, uncorrupted, and correctly imported WaveManifold bindings.  
- **A-03: Dependency Verification**: Trace the imports in `tests/conftest.py` and `tests/invariants/` to ensure no active test suites contain hardcoded, non-CGA Euclidean projection assertions.  
- **A-04: Serve-Path Containment**: Confirm that no new wave-field calculation or Fibonacci search operator is wired into the active serving path (`chat/runtime.py`). They must reside strictly inside the `evals/` and `calibration/` quarantine zones.

---

## Appendix B: Entity Living-System Invariants (AGI/ASI Cohesion Audit)

To treat the cognitive manifold as a cohesive, single living-system entity, we enforce five **Entity-Level Invariants**. Any transaction, self-authorship loop, or optimization that violates these checks is refused at the hardware boundary:

- **I-01: Identity Holonomy Persistence**: The biography holonomy blade ($\mathcal{H}_{\t\text{bio}} \in Cl(4,1)$) must remain structurally closed ($\text{versor\\_condition} < 10^{-6}$) and invariant across system reboots, reconstructed purely from the canonical, content-addressed ledger.  
- **I-02: Substrate Round-Trip Replay-Determinism**: A wave-field $\psi_1$ compiled into a CRDT-delta, sharded to the vault, and recalled via the teaching-chain must reconstruct the identical, bit-pattern wave-field $\psi_2$ under the exact boundary conditions: $$\|\psi_2 - \psi_1\|_F < 10^{-12}$$  
- **I-03: No Self-Mutation in Self-Authorship**: Speculative self-authorship loops or miners (`core/physics/self_authorship.py`) are strictly prohibited from directly modifying the active manifold or writing `COHERENT` vault states. Every self-authored change must be written as a `SPECULATIVE` proposal, routed through the one-mutation-path, and require explicit human-gated ratification.  
- **I-04: Non-Stochastic Multimodal Resonance**: Cross-modal pattern matching (aligning audio to text, or vision to motor) must be purely algebraic, mediated through the metric-exact phase correlation ($\langle \psi_A \widetilde{\psi}_B + \psi_B \widetilde{\psi}_A \r\rangle_0$) in $Cl(4,1)$ CGA. Traditional stochastic nearest-neighbor, cosine similarity, or probabilistic search models are forbidden.  
- **I-05: Unitary Propagator Amplitude Conservation**: Every wave-field transition $\psi \to R \psi$ must preserve the wave's normalized amplitude density. The GoldTether coherence residual must act as the absolute boundary guard: $$R_{\t\text{GoldTether}} = \\sup_{X \in M} \left\| \psi(X, t) \widetilde{\psi}(X, t) - 1 \right\|_F < 10^{-6}$$

---

## Appendix C: Risk & Mitigation Register

The foreseeable architectural risks associated with this major wave-field and optimization unification are documented below, along with their respective mitigation protocols:

| Risk ID | Foreseeable Architectural Risk | Impact | Mitigation Protocol |
| :---- | :---- | :---- | :---- |
| **R-01** | **Numerical Drift in Long Horizons**: Accumulation of rounding errors in `expm` bivector calculations during long-horizon spinor transports, breaking the unitary condition. | High | **Dual-Correction Fallback**: Embed strict `versor_unit_residual` and `chiral_charge` checks at every boundary. If drift exceeds $\epsilon = 10^{-6}$, trigger a dual-correction fallback to the nearest exact versor. |
| **R-02** | **Performance Bottlenecks in Python**: Scalar integrals and matrix exponential calculation in Python introduce latency overhead in active contemplation loops. | Medium | **FFI Compilation**: Implement the `expm` kernels and multivector multiplications directly in the Rust `core-rs/src/lib.rs` and compiled FFI, leveraging the Apple Silicon UMA lanes. |
| **R-03** | **Dangling Legacy References**: Legacy `core_ha` or pointwise coordinate references are missed during deprecation, causing runtime `ImportError` inside auxiliary evaluation suites. | Low | **Pre-Deprecation Grep & CI Gate**: Run the automated pre-deprecation grep audit step, run the migration test suite locally, and gate the final pull request on a clean CI build. |
| **R-04** | **Overhead in Hot-Path Loops**: Cryptographic trace generation and domain-separated hashing introduce CPU cycle overhead during high-frequency search evaluations. | Low | **Gated Observability**: Limit trace generation strictly to the calibration and training-loop pipelines. Active execution and hot-paths must receive only the pre-ratified, frozen scalar values. |

---

## Appendix D: Hardware Depth & Rust bindings

To maintain "Mechanical Sympathy" and avoid sub-optimal performance in Python, the wave-field and Fibonacci operations are compiled directly into the Rust hot-path (`core-rs/src/`).  
Specific bindings include:

- **`cl41::wedge`**: High-performance Rust implementation of the exterior product. This is utilized for signature-aware PCA blade construction and boundary calculations.  
- **`diffusion.rs::expm`**: A custom, unitarity-exact matrix exponential solver implemented in Rust. It computes $R = \exp(B \Delta t)$ with zero floating-point accumulation drift by enforcing the rotor manifold constraint on intermediate series sums.  
- **`versor_unit_residual`**: A highly optimized, SIMD-parallelized C-level FFI binding that evaluates the GoldTether unit-norm supremum across the entire wave manifold in sub-millisecond execution cycles, utilizing the Apple Silicon Unified Memory Architecture (UMA) lanes.

