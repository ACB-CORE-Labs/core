"""ADR-0243 Phase 4 — falsifiability benchmark (metrics eval, OFF-SERVING).

The plan (``docs/plans/adr-0243-implementation-plan.md`` §5 Phase 4) requires the
cognitive lifecycle to be measured against *concrete, falsifiable* comparison
classes — not described in architecture prose. This module is that measurement.
Every metric is grounded in a live lifecycle primitive; none is decorative:

* **fidelity** — decode overlap ``|⟨ψ_steady, target⟩|`` after
  :func:`relax_to_ground` on :func:`compile_quadratic_well` from a perturbed
  start. The well's ground space is exactly ``span(target)`` at energy 0 with a
  gap of ``curvature``; a genuine decoder must land back on the target it was
  perturbed from. Falsified if any panel case decodes below
  :data:`FIDELITY_MIN`.
* **surprise separation (ID vs OOD)** — energy-above-ground ``ψᵀHψ − λ0`` of an
  incoming field against a fixed identity well. In-distribution fields (small
  rotations of the identity) sit low; out-of-distribution fields (large-angle
  rotations into distinct Cl(4,1) planes) sit high. The operator must separate
  the two classes: ``min(OOD) − max(ID) > `` :data:`SURPRISE_MIN_SEPARATION`.
  Falsified if the classes overlap in energy.
* **insertion cost** — relaxation ``certificate.steps_taken`` to decode. Every
  panel case must *certify* convergence (never mis-certified) within
  :data:`INSERTION_STEP_BOUND` steps, and the panel must exercise real decoding
  work (``max steps_taken > 0``).
* **f32 drift over T=1000** — a unit versor iterated ``T`` times by a fixed unit
  rotor via :func:`algebra.cl41.geometric_product` with **no renormalization**.
  Right-multiplication by a unit versor conserves the reverse-norm ``ψψ̃`` and,
  for these spatial-plane rotors, the Euclidean norm — *exactly* in f64, up to
  rounding in f32. The metric reports both, quantifying the ``float32``
  truncation gap that motivates the serving-boundary cast contract (ADR-0244
  §2.5) and the f64 fast-path (ADR-0244 §2.6). f64 must hold closure to
  :data:`F64_DRIFT_MAX`; the f32 gap is reported for evidence. Ties to the
  no-f32-truncation invariant (``docs/…/cl41-algebra-pitfalls``).
* **falsifier** — the decisive propositional field-vs-ROBDD-gold check
  (:func:`run_propositional_falsifier`); ``wrong`` must be 0.

Off-serving: lives under ``evals/`` only; never imported by ``chat/runtime.py``
(A-04 quarantine, inherited transitively through
``core.physics.cognitive_lifecycle``). Deterministic: fixed construction, no
wall-clock, no unseeded randomness — the artifact is byte-stable across runs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from algebra.cl41 import N_COMPONENTS, geometric_product, reverse
from algebra.rotor import make_rotor_from_angle
from core.physics.cognitive_lifecycle import (
    compile_quadratic_well,
    relax_to_ground,
)
from core.physics.wave_manifold import WaveManifold
from evals.adr_0243_cognitive_lifecycle.propositional_falsifier import (
    run_propositional_falsifier,
)

__all__ = [
    "FIDELITY_MIN",
    "SURPRISE_MIN_SEPARATION",
    "INSERTION_STEP_BOUND",
    "F64_DRIFT_MAX",
    "DRIFT_STEPS",
    "MetricResult",
    "BenchmarkVerdict",
    "run_benchmark",
]

# --- Falsifiable thresholds (one place; the pass/fail contract) --------------------
FIDELITY_MIN: float = 0.999
SURPRISE_MIN_SEPARATION: float = 0.05
INSERTION_STEP_BOUND: int = 256
F64_DRIFT_MAX: float = 1e-9
DRIFT_STEPS: int = 1000

# Identity axis for the surprise metric. Rotation planes e12/e13/e14 (indices
# 6/7/8) all *contain* e1, so a rotor built on one genuinely moves the axis — a
# rotor on a disjoint plane would commute past e1 and leave it invariant, the trap
# that makes a naive OOD field read as ID.
_E1_AXIS: int = 0


def _euclidean_unit(psi: np.ndarray) -> np.ndarray:
    arr = np.asarray(psi, dtype=np.float64)
    norm = float(np.linalg.norm(arr))
    if norm <= 0.0 or not np.isfinite(norm):
        raise ValueError("degenerate state has no Euclidean-unit direction")
    return arr / norm


def _basis_vector(axis: int) -> np.ndarray:
    """Unit grade-1 basis vector e_{axis} (0-indexed) as a 32-component field."""
    v = np.zeros(N_COMPONENTS, dtype=np.float64)
    v[1 + int(axis)] = 1.0
    return v


def _sandwich(rotor: np.ndarray, field: np.ndarray) -> np.ndarray:
    """Rotate ``field`` by ``rotor``: R X R̃ (pure algebra, no backend dispatch).

    ``make_rotor_from_angle(θ, B)`` rotates a vector in plane ``B`` by exactly
    ``θ``; when ``B`` contains the vector's axis the overlap becomes ``cos θ``.
    """
    return geometric_product(geometric_product(rotor, field), reverse(rotor))


@dataclass(frozen=True, slots=True)
class MetricResult:
    """One falsifiable metric: its measured evidence and whether it passed."""

    name: str
    passed: bool
    detail: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {"name": self.name, "passed": self.passed, "detail": self.detail}


@dataclass(frozen=True, slots=True)
class BenchmarkVerdict:
    """Typed benchmark outcome: per-metric results and the overall pass gate."""

    metrics: tuple[MetricResult, ...]
    overall_passed: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "kind": "ADR0243BenchmarkVerdict",
            "overall_passed": self.overall_passed,
            "metrics": [m.as_dict() for m in self.metrics],
        }


# --- Metric 1: fidelity (decode overlap) -------------------------------------------


def _fidelity_and_insertion(
    *,
    curvature: float = 1.0,
) -> tuple[MetricResult, MetricResult]:
    """Decode a perturbed field back to its well's target; measure overlap + steps.

    One pass produces both the fidelity metric and the insertion-cost metric so
    the (expensive) relaxations run once. Each target is a unit basis axis; each
    perturbed start is that axis rotated by a small angle in a plane that
    *contains* it (so the start genuinely differs from the target and relaxation
    must do real work to decode back).
    """
    # (target axis, rotation plane containing it, perturbation angles)
    target_specs = (
        (0, 6, (0.15, 0.30)),  # e1 rotated in e12
        (1, 6, (0.20, 0.35)),  # e2 rotated in e12
        (2, 7, (0.25, 0.40)),  # e3 rotated in e13
        (3, 8, (0.30, 0.18)),  # e4 rotated in e14
    )

    fidelities: list[float] = []
    steps: list[int] = []
    all_converged = True
    cases: list[dict[str, Any]] = []

    for axis, plane, perturb_angles in target_specs:
        target = _basis_vector(axis)
        well = compile_quadratic_well(target, curvature=curvature)
        for p_angle in perturb_angles:
            perturb = make_rotor_from_angle(p_angle, plane)
            start = _euclidean_unit(_sandwich(perturb, target))
            result = relax_to_ground(start, well)
            cert = result.certificate
            overlap = abs(float(np.dot(result.psi_steady, target)))
            fidelities.append(overlap)
            steps.append(int(cert.steps_taken))
            all_converged = all_converged and bool(cert.converged)
            cases.append(
                {
                    "axis": axis,
                    "plane": plane,
                    "perturb_angle": round(p_angle, 4),
                    "fidelity": overlap,
                    "steps_taken": int(cert.steps_taken),
                    "converged": bool(cert.converged),
                    "reason": cert.reason,
                }
            )

    min_fidelity = min(fidelities)
    max_steps = max(steps)
    fidelity_metric = MetricResult(
        name="fidelity",
        passed=min_fidelity >= FIDELITY_MIN,
        detail={
            "min_fidelity": min_fidelity,
            "threshold": FIDELITY_MIN,
            "n_cases": len(fidelities),
            "cases": cases,
        },
    )
    insertion_metric = MetricResult(
        name="insertion_cost",
        passed=all_converged and 0 < max_steps <= INSERTION_STEP_BOUND,
        detail={
            "all_converged": all_converged,
            "max_steps_taken": max_steps,
            "min_steps_taken": min(steps),
            "step_bound": INSERTION_STEP_BOUND,
            "n_cases": len(steps),
        },
    )
    return fidelity_metric, insertion_metric


# --- Metric 2: surprise separation (ID vs OOD) -------------------------------------


def _energy_above_ground(psi: np.ndarray, hamiltonian_matrix: np.ndarray, lam0: float) -> float:
    return float(psi @ hamiltonian_matrix @ psi) - lam0


def _surprise_separation(*, curvature: float = 1.0) -> MetricResult:
    """Separate small-rotation (ID) from large-rotation (OOD) fields by energy.

    The identity well targets the fixed e1 axis; incoming fields are rotations
    of e1 in planes that contain it (so the rotation is effective — a rotor on a
    disjoint plane commutes past e1 and would leave a genuine OOD field reading
    as ID). ID = small angles; OOD = large angles toward orthogonality (energy
    ``c·sin²θ`` is monotone in θ, so this falsifies a miscompiled well, not a
    hand-built number). λ0 is read from the spectrum and verified ≈ 0, not
    assumed.
    """
    target = _basis_vector(_E1_AXIS)
    well = compile_quadratic_well(target, curvature=curvature)
    H = well.matrix
    lam0 = float(np.linalg.eigvalsh(H)[0])
    if abs(lam0) > 1e-9:
        # The quadratic well is constructed with ground energy 0; a nonzero λ0
        # would mean the primitive drifted. Fail-closed rather than mask it.
        return MetricResult(
            name="surprise_separation",
            passed=False,
            detail={"error": "well_ground_energy_nonzero", "lam0": lam0},
        )

    # Small rotations (ID) vs near-orthogonal rotations (OOD) into distinct planes.
    id_specs = ((0.15, 6), (0.25, 7), (0.35, 8), (0.20, 6))
    ood_specs = ((1.40, 6), (1.45, 7), (1.50, 8), (1.35, 7))

    def _energies(specs: tuple[tuple[float, int], ...]) -> list[float]:
        out: list[float] = []
        for angle, biv in specs:
            rotor = make_rotor_from_angle(angle, biv)
            field = _euclidean_unit(_sandwich(rotor, target))
            out.append(_energy_above_ground(field, H, lam0))
        return out

    id_energies = _energies(id_specs)
    ood_energies = _energies(ood_specs)
    separation = min(ood_energies) - max(id_energies)
    return MetricResult(
        name="surprise_separation",
        passed=separation > SURPRISE_MIN_SEPARATION,
        detail={
            "separation": separation,
            "threshold": SURPRISE_MIN_SEPARATION,
            "max_id_energy": max(id_energies),
            "min_ood_energy": min(ood_energies),
            "id_energies": id_energies,
            "ood_energies": ood_energies,
            "lam0": lam0,
        },
    )


# --- Metric 3: f32 drift over T steps (no renormalization) -------------------------


def _closure_drift(origin_dtype: np.dtype, *, steps: int) -> tuple[float, float]:
    """Max Euclidean-norm deviation and max versor residual over ``steps`` products.

    ψ ← ψ · R_step, R_step a fixed unit rotor, no renormalization. Both operands
    share ``origin_dtype`` so ``geometric_product`` keeps the trajectory in that
    precision — the whole point is to let ``float32`` rounding accumulate.
    """
    r_step = make_rotor_from_angle(0.05, 6).astype(origin_dtype)
    psi = make_rotor_from_angle(0.30, 7).astype(origin_dtype)
    manifold = WaveManifold()
    max_norm_dev = abs(float(np.linalg.norm(psi)) - 1.0)
    max_residual = float(manifold.measure_unitary_residual(psi))
    for _ in range(int(steps)):
        psi = geometric_product(psi, r_step)
        max_norm_dev = max(max_norm_dev, abs(float(np.linalg.norm(psi)) - 1.0))
        max_residual = max(max_residual, float(manifold.measure_unitary_residual(psi)))
    return max_norm_dev, max_residual


def _drift_metric(*, steps: int = DRIFT_STEPS) -> MetricResult:
    f64_norm_dev, f64_residual = _closure_drift(np.dtype(np.float64), steps=steps)
    f32_norm_dev, f32_residual = _closure_drift(np.dtype(np.float32), steps=steps)
    return MetricResult(
        name="f32_drift",
        # The falsifiable claim is on the f64 substrate (the source of truth):
        # versor closure holds to F64_DRIFT_MAX over T steps with no renorm. The
        # f32 figures are reported as the truncation-gap evidence, not gated.
        passed=(f64_norm_dev <= F64_DRIFT_MAX and f64_residual <= F64_DRIFT_MAX),
        detail={
            "steps": int(steps),
            "f64_max_norm_dev": f64_norm_dev,
            "f64_max_versor_residual": f64_residual,
            "f32_max_norm_dev": f32_norm_dev,
            "f32_max_versor_residual": f32_residual,
            "f64_threshold": F64_DRIFT_MAX,
            "f32_over_f64_residual_ratio": (
                f32_residual / f64_residual if f64_residual > 0.0 else float("inf")
            ),
        },
    )


# --- Metric 5: decisive propositional falsifier ------------------------------------


def _falsifier_metric() -> MetricResult:
    artifact = run_propositional_falsifier()
    wrong = int(artifact["wrong"])
    return MetricResult(
        name="falsifier",
        passed=(
            wrong == 0
            and artifact["id_case_count"] > 0
            and artifact["refusal_parity_count"] > 0
            and bool(artifact["ood_field_refused"])
            and bool(artifact["ood_gold_decided"])
        ),
        detail={
            "wrong": wrong,
            "id_case_count": int(artifact["id_case_count"]),
            "refusal_parity_count": int(artifact["refusal_parity_count"]),
            "ood_field_refused": bool(artifact["ood_field_refused"]),
            "ood_gold_decided": bool(artifact["ood_gold_decided"]),
        },
    )


def run_benchmark(*, drift_steps: int = DRIFT_STEPS) -> BenchmarkVerdict:
    """Run all five falsifiable metrics; return a typed, JSON-safe verdict.

    Deterministic and side-effect-free. ``drift_steps`` is exposed only so tests
    can exercise a shorter trajectory; the shipped contract is ``DRIFT_STEPS``.
    """
    fidelity, insertion = _fidelity_and_insertion()
    metrics = (
        fidelity,
        _surprise_separation(),
        insertion,
        _drift_metric(steps=drift_steps),
        _falsifier_metric(),
    )
    overall = all(m.passed for m in metrics)
    return BenchmarkVerdict(metrics=metrics, overall_passed=overall)
