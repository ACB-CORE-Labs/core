# ADR-0242: Deterministic Fibonacci Operators and Evidence-Gated Optimization

> Committed authority copy. Retrieved verbatim 2026-07-15 from the R&D Google Doc
> (`doc_id 15_NECCPy-tEWGfYi_BNqawm8GytUTMkz1DsOqGVMXhI`, pointer:
> `docs/research/ADR-0242-deterministic-fibonacci-operators-and-evidence-gated-optimization.md.gdoc`),
> formatting normalized from the Docs export. The Drive document remains the
> editable source; this copy exists so fidelity audits can cite in-repo text.
> Fidelity audit: `docs/audit/adr-0241-0242-acceptance-packet-2026-07-15.md` §7.

**Status**: Proposed (acceptance path: benchmark evidence + Joshua review)
**Date**: 2026-07-13
**Deciders**: Joshua Shay + multi-model R&D
**Traceability**: Notion R&D (Fibonacci and Golden Ratio Dynamics)
**Related**: ADR-0238, ADR-0239, ADR-0240, ADR-0241, core/physics/goldtether.py, core/physics/surprise.py, core/physics/energy.py
**Canonical path**: docs/adr/

## 1. Context and Problem Statement

The introduction of continuous wave-field representations (ADR-0241) in the Continuous Orthogonal Resonance Engine (CORE) establishes a unified, coordinate-free geometric substrate. As we refine the physical layers of CORE, we encounter several optimization, scheduling, and multi-scale allocation challenges:

- **Optimization of Unimodal Scalars**: Bounded parameters such as the GoldTether valence-scaling factor (κ) or the Conformal Procrustes alignment angle (θ) require fast, exact, and reproducible bracketing.
- **Hierarchical Temporal Horizons**: Modeling decay, salience, and consolidation requires a deterministic temporal basis to segregate transient noise from long-horizon semantic structures.
- **Mode Centroid Allocation**: Registering new standing-wave modes in WaveManifold requires a low-discrepancy, incrementally extensible spacing algorithm to prevent spectral mode collision without global repacking.
- **Observability Scheduling**: Periodic background checks risk phase-locking with external batching cycles, requiring quasi-periodic, non-harmonic scheduling.

In natural and mathematical systems, Fibonacci recurrences (F_n = F_{n-1} + F_{n-2}) and Golden Ratio (φ) limits govern optimal packings, anyon fusion, and optimal search. However, CORE's **Third Door** philosophy explicitly rejects the dogmatic adoption of "sacred geometry" or aesthetic doctrines. Any mathematical operator must "earn its place" through a measurable, isolated, and falsifiable advantage, and its results must be bound by strict evidence-gated promotion.

## 2. Decision and Reframed Thesis

We establish the **CORE Fibonacci Evidence Discipline**:

**Fibonacci structure is implemented only where CORE requires a deterministic, reconstructible, multi-scale allocation, search, or selection mechanism — not because φ is inherently privileged, but because a Fibonacci recurrence can be evaluated empirically against competing schedules, packings, or optimizers under CORE's rigorous evidence gating.**

We define **five targeted vectors** of Fibonacci integration, structured from near-term engineering deliverables to long-horizon theoretical research, each isolated behind clean programmatic boundaries and cryptographic validation gates:

```
                        [CORE Evidence Discipline]
                                    |
     +-----------------+------------+------------+-----------------+
     |                 |                         |                 |
     v                 v                         v                 v
 [Vector 1]        [Vector 2]                [Vector 3]        [Vector 4/5]
Fibonacci Search  Temporal Basis             Anchor Alloc    Word Choreography
 (Optimization)   (Decay Study)             (Mode Packing)   (Quasi-Periodic)
  Certificate     E_n(t) = E_n*exp(-t/tau)   Low-discrep     W_n+1 = W_n · W_n-1
```

## 3. The Five Fibonacci Vectors

### 3.1 Vector 1: Bounded Fibonacci-Section Search (Immediate Opportunity)

We implement Fibonacci-section search as a highly constrained, pure, and deterministic scalar optimizer.

For a known, fixed evaluation budget N, Fibonacci search provides the mathematically optimal final bracket width among comparison-based methods under unimodality assumptions. It is superior to golden-section search because it leverages a precomputed Fibonacci schedule to minimize interval length exactly at step N, reusing one function evaluation per step.

#### CORE-Native Certificate Gating

To prevent unreviewed parameters from altering cognitive behavior, the optimizer does *not* return a raw scalar. It outputs a content-addressed, cryptographic **FibonacciSearchCertificate** (or a typed **OptimizationFailure**). This certificate serves as an immutable audit trail of the search trajectory and must be verified before the minimizer can be promoted to drive any active parameter (e.g., GoldTether valence-scaling κ).

### 3.2 Vector 2: Multi-Scale Temporal Basis (Most Native Research Path)

The Field Energy Operator (ADR-0006) simulates thermodynamic cooling of active states. Rather than hard-coding decay constants, we treat the Fibonacci sequence as a candidate **temporal basis family**.

Each active field component carries a deterministic vector of decayed energies across a finite, reconstructible spectrum of horizons:

    E_n(t) = E_n(t_0) · exp(−(t − t_0) / (F_n · τ_0))

where F_n ∈ {1, 2, 3, 5, 8, 13, 21, …} provides the temporal scales.

- F_1·τ_0: Immediate sensory perturbations.
- F_3·τ_0: Working reasoning context.
- F_5·τ_0: Active session structures.
- F_8·τ_0: Long-horizon biography holonomies.

**The Comparative Hypothesis**: We will benchmark this Fibonacci basis against standard dyadic (τ_n = 2^n·τ_0), logarithmic, and hand-tuned bases. The Fibonacci basis is promoted to the production pipeline (e.g., inside core/physics/energy.py) if and only if it separates transient sensory noise from persistent semantic signals with measurably higher fidelity under identical replay workloads.

### 3.3 Vector 3: Golden-Angle Mode Allocator (Anchor Allocation)

When registering a new standing-wave mode ψ_k in the Hyperbolic Atlas, the manifold must assign a spatial centroid anchor X_k that minimizes phase overlap and collision.

We define a pure **AnchorAllocator** strategy interface. One candidate strategy is a **Golden-Angle Hyperbolic Spiral** over the Poincaré disk model, which generates a low-discrepancy, incrementally extensible spatial distribution without requiring global repacking.

The final anchor layout is never stored as a mutable, opaque coordinate table. It is dynamically regenerated from the allocator's identity and the ordinal sequence, preserving the **reconstruction-over-storage** doctrine:

    Layout(n) = AnchorAllocator(n, version="golden_angle_v1")

The golden-angle allocator will be benchmarked against deterministic low-discrepancy sequences, measuring minimum pairwise geodesic separation, recall ambiguity, and insertion cost before adoption.

### 3.4 Vector 4: Fibonacci-Word Operator Choreography (Observability Scheduling)

To reduce phase-locking and harmonic resonance between periodic background checks and input batching cycles, we introduce a quasi-periodic, non-harmonic scheduling operator.

We recursively generate **Fibonacci words** from two safe, existing action classes:

- **Action A**: Low-cost local measurements (e.g., local energy/surprise updates).
- **Action B**: High-cost cross-band evaluations (e.g., biography holonomy or sealed-holdout checks).

    W_0 = B,  W_1 = A,  W_{n+1} = W_n W_{n−1}

For n=4, this yields: A → B → A → A → B → A → B → A → A → B …

This non-periodic, deterministic sequence belongs strictly outside the cognitive truth path. It is used to schedule background measurements, telemetry traces, and sealed-holdout sampling. This prevents cyclic artifacts of the scheduler from corrupting the continuous field dynamics.

### 3.5 Vector 5: Topological Compositional Holonomy (Long-Horizon anyon Theory)

We open an isolated research branch (algebra/topological_reasoning/) to study whether non-commuting semantic composition paths produce stable, topologically protected holonomies under bounded perturbation.

This track will explore if the category data of **Fibonacci anyons** (including its fusion spaces, F-symbols, and R-symbols) can be represented within Cl(4,1) CGA. This remains a pre-research theory program. It must never enter the production pipeline or affect active reasoning until its mathematical representation and stability under floating-point perturbations are fully proven.

## 4. Implementation Specification (Vector 1: Fibonacci Search)

> Note (audit, 2026-07-15): the memo's reference implementation below is
> preserved as-written for the record. The landed implementation
> (`core/physics/fibonacci_search.py`) deliberately deviates in the
> impl-stronger direction — see the acceptance-packet §7 table (cert_id
> digest added; shape-based unimodality check; nonfinite/bounds fail-closed;
> best-sample minimizer). The reference code below is non-executable as
> written (uses `np.argsort` without importing numpy).

To guarantee exactness and absolute reproducibility, we define the strict, frozen Python interface for the unimodal objective, the search certificate, and the deterministic Fibonacci-section search algorithm.

```python
# core/physics/fibonacci_search.py  (memo reference sketch — see note above)

from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Union

@dataclass(frozen=True, slots=True)
class BoundedUnimodalObjective:
    """Represents a bounded, unimodal scalar objective to be optimized."""
    lower: float
    upper: float
    evaluation_budget: int
    objective_id: str
    objective_version: str

@dataclass(frozen=True, slots=True)
class FibonacciSearchCertificate:
    """The cryptographically verifiable, replayable optimization result."""
    minimizer: float
    final_interval: tuple[float, float]
    evaluations: int
    ordered_points: tuple[float, ...]
    ordered_values: tuple[float, ...]
    objective_id: str
    objective_version: str

@dataclass(frozen=True, slots=True)
class OptimizationFailure:
    """Typed failure response indicating why the optimization could not converge."""
    reason: str
    final_interval: tuple[float, float]
    evaluations: int
    objective_id: str
    objective_version: str

def _precompute_fibonacci(n: int) -> list[int]:
    """Generates the first n Fibonacci numbers."""
    fib = [1, 1]
    for i in range(2, n + 2):
        fib.append(fib[-1] + fib[-2])
    return fib

def fibonacci_section_search(
    objective: BoundedUnimodalObjective,
    func: Callable[[float], float]
) -> Union[FibonacciSearchCertificate, OptimizationFailure]:
    """
    Executes a metric-orthogonal Fibonacci search on a unimodal objective.
    Admit only a typed OptimizationFailure or FibonacciSearchCertificate;
    never silently accept a candidate minimizer.
    """
    a = float(objective.lower)
    b = float(objective.upper)
    n = objective.evaluation_budget

    if n < 3:
        return OptimizationFailure(
            reason="budget_too_low_for_unimodal_search",
            final_interval=(a, b),
            evaluations=0,
            objective_id=objective.objective_id,
            objective_version=objective.objective_version,
        )

    fib = _precompute_fibonacci(n)
    L = b - a

    # Pre-calculated evaluation points
    x1 = a + (fib[n] / fib[n + 2]) * L
    x2 = b - (fib[n] / fib[n + 2]) * L

    points: list[float] = [x1, x2]
    try:
        f1 = float(func(x1))
        f2 = float(func(x2))
    except Exception as e:
        return OptimizationFailure(
            reason=f"evaluation_error_at_initial_points: {str(e)}",
            final_interval=(a, b),
            evaluations=0,
            objective_id=objective.objective_id,
            objective_version=objective.objective_version,
        )

    values: list[float] = [f1, f2]
    evals_count = 2

    for k in range(1, n - 1):
        L_next = b - a
        if f1 < f2:
            b = x2
            x2 = x1
            f2 = f1
            x1 = a + (fib[n - k + 1] / fib[n - k + 2]) * L_next
            try:
                f1 = float(func(x1))
            except Exception as e:
                return OptimizationFailure(
                    reason=f"evaluation_error_at_step_{k}: {str(e)}",
                    final_interval=(a, b),
                    evaluations=evals_count,
                    objective_id=objective.objective_id,
                    objective_version=objective.objective_version,
                )
            points.append(x1)
            values.append(f1)
        else:
            a = x1
            x1 = x2
            f1 = f2
            x2 = b - (fib[n - k + 1] / fib[n - k + 2]) * L_next
            try:
                f2 = float(func(x2))
            except Exception as e:
                return OptimizationFailure(
                    reason=f"evaluation_error_at_step_{k}: {str(e)}",
                    final_interval=(a, b),
                    evaluations=evals_count,
                    objective_id=objective.objective_id,
                    objective_version=objective.objective_version,
                )
            points.append(x2)
            values.append(f2)
        evals_count += 1

    minimizer = (a + b) / 2.0

    # Strictly verify the unimodality assumption on the gathered trace.
    # To be unimodal, values must decrease to a minimum and then increase.
    # If the empirical trace contains multiple local extrema, the certificate
    # fails validation.
    sorted_indices = np.argsort(points)
    sorted_vals = [values[i] for i in sorted_indices]

    extrema_count = 0
    for i in range(1, len(sorted_vals) - 1):
        prev_diff = sorted_vals[i] - sorted_vals[i - 1]
        next_diff = sorted_vals[i + 1] - sorted_vals[i]
        if prev_diff < 0 and next_diff > 0:
            extrema_count += 1  # Local minimum
        elif prev_diff > 0 and next_diff < 0:
            extrema_count += 1  # Local maximum

    if extrema_count > 1:
        return OptimizationFailure(
            reason="unimodality_violation_multiple_extrema_detected",
            final_interval=(a, b),
            evaluations=evals_count,
            objective_id=objective.objective_id,
            objective_version=objective.objective_version,
        )

    return FibonacciSearchCertificate(
        minimizer=float(minimizer),
        final_interval=(float(a), float(b)),
        evaluations=evals_count,
        ordered_points=tuple(points),
        ordered_values=tuple(values),
        objective_id=objective.objective_id,
        objective_version=objective.objective_version,
    )
```

## 5. R&D Integration and Priority Order

To enforce strict, non-doctrinal evidence gating, the five vectors will be integrated sequentially based on their readiness and safety risk:

1. **Phase 1: Isolated Fibonacci-Section Search (Production-Ready)**
   - **Integration Seam**: Bounded valence-scaling factor (κ) in core/physics/goldtether.py.
   - **Gating**: The returned FibonacciSearchCertificate is written to the execution telemetry. If the certificate fails (e.g. unimodality_violation), the system defaults to the safe, pre-calculated baseline kappa = 1.0 and logs an OptimizationFailure warning.

2. **Phase 2: Multi-Scale Temporal Basis Study (Research Prototype)**
   - **Integration Seam**: The Field Energy Operator (core/physics/energy.py) and the non-resonant surprise accumulator (core/physics/surprise.py).
   - **Gating**: Emits a DiscoveryCandidate in the contemplation loop *only* when the surprise signal persists across multiple Fibonacci-scaled temporal bands (F_5 to F_7), preventing transient noise from triggering ungrounded updates.

3. **Phase 3: Golden-Angle Mode Allocator (Sandbox Scaffold)**
   - **Integration Seam**: Centroid placement inside the WaveManifold memory registry (core/physics/wave_manifold.py).
   - **Gating**: Active only when the standing-wave registry's coordinate and interference operators are fully verified in the main Rust branch.

4. **Phase 4: Fibonacci-Word Observability Scheduler (Telemetry Seam)**
   - **Integration Seam**: Background telemetry traces and sealed-holdout sampling.
   - **Gating**: Operates strictly outside the cognitive truth path; cannot modify any state variables.

5. **Phase 5: Topological Braid Category Study (Pre-Research)**
   - **Integration Seam**: Isolated algebra/topological_reasoning/ branch.
   - **Gating**: Blocked from any FFI or CPython compilation path until algebraic and numerical stability proofs under floating-point perturbations are finalized.

## 6. Architectural Sovereignty Invariant

This ADR establishes the absolute sovereignty of CORE's core logical layers over any mathematical scheduling or optimization:

**Fibonacci operators may optimize the parameters of search, determine the scale of observation, or schedule background checks; they must NEVER dictate the truth status of a proposition, alter safety policies, change CORE's identity, or authorize autonomous promotion.**

Active reasoning, memory vaulting, and supervised transition gating remain strictly governed by CORE's even versor closure invariants, sharded CRDT-delta exactness, and human-gated review boundaries.

## 7. References

1. docs/adr/ADR-0238-GoldTether-Modulated-Supervised-Autonomy.md — GoldTether and supervised blend.
2. docs/adr/ADR-0239-Conformal-Procrustes-Surprise-Dual-Operator.md — Conformal Procrustes and surprise.
3. docs/adr/ADR-0240-Analogical-Transfer-Validation-Harness-Biography-Holonomy.md — Biography holonomy and validation.
4. docs/adr/ADR-0241-wave-field-driven-hyperbolic-atlas-and-resonant-cognition.md — Continuous wave-field framework.
