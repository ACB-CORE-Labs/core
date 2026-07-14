"""
core/physics/trajectory_invariants.py

Continuous-space trajectory invariants + zero-fabrication (R&D-Revised §2.2 / #21).

Python geometry-first surface (algebra/*). A Ring-1 Rust port may later mirror
this contract under ``core-rs``; this module is the behavioral source of truth.

Invariants:
  * Relative holonomy H(t) = V_i · reverse(V_{i+1})
  * Divergence D = Σ log(1 + ‖H·reverse(H) − 1‖_F) · Δt  (discrete integral)
  * Replay bound D < ε_trajectory
  * Hamiltonian energy boundary E_exertion ≤ κ · E_sensory
  * Zero-fabrication: refuse empty / non-closed trajectory steps
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

import numpy as np

from algebra.cl41 import N_COMPONENTS, geometric_product, reverse
from algebra.versor import versor_condition, versor_unit_residual

_CLOSURE_TOL = 1e-6
_DEFAULT_EPS_TRAJECTORY = 1e-5
_NEAR_ZERO = 1e-15


class TrajectoryInvariantError(ValueError):
    """Fail-closed refusal from trajectory invariant checks."""

    def __init__(self, reason: str, **disclosure) -> None:
        self.reason = reason
        self.disclosure = dict(disclosure)
        super().__init__(f"trajectory_invariant refused [{reason}]: {self.disclosure}")


def _as_versor(V: np.ndarray, name: str) -> np.ndarray:
    arr = np.asarray(V, dtype=np.float64)
    if arr.shape != (N_COMPONENTS,):
        raise TrajectoryInvariantError(
            "bad_shape", name=name, shape=tuple(arr.shape)
        )
    cond = float(versor_condition(arr))
    if cond >= _CLOSURE_TOL:
        raise TrajectoryInvariantError(
            "not_closed", name=name, versor_condition=cond
        )
    return arr


def relative_holonomy(V1: np.ndarray, V2: np.ndarray) -> np.ndarray:
    """H = V1 · reverse(V2) — relative transport between consecutive steps."""
    a = _as_versor(V1, "V1")
    b = _as_versor(V2, "V2")
    return geometric_product(a, reverse(b)).astype(np.float64)


def holonomy_unit_residual(H: np.ndarray) -> float:
    """‖H · reverse(H) − 1‖_F (dual-checked via versor_unit_residual)."""
    H_arr = np.asarray(H, dtype=np.float64)
    if H_arr.shape != (N_COMPONENTS,):
        raise TrajectoryInvariantError("bad_shape", name="H", shape=tuple(H_arr.shape))
    r = float(versor_unit_residual(H_arr))
    r_rev = float(versor_unit_residual(reverse(H_arr)))
    return max(r, r_rev)


def trajectory_divergence(
    versors: Sequence[np.ndarray],
    *,
    dt: float = 1.0,
) -> float:
    """Discrete divergence integral D = Σ log(1 + residual(H_i)) · Δt.

    Zero-fabrication: empty or single-step trajectories refused (no confabulated
    path). Each step must be a closed unit versor.
    """
    if not versors:
        raise TrajectoryInvariantError("empty_trajectory")
    if len(versors) < 2:
        raise TrajectoryInvariantError(
            "trajectory_too_short", n=len(versors)
        )
    if float(dt) <= 0.0:
        raise TrajectoryInvariantError("non_positive_dt", dt=float(dt))

    closed = [_as_versor(v, f"versors[{i}]") for i, v in enumerate(versors)]
    D = 0.0
    for i in range(len(closed) - 1):
        H = relative_holonomy(closed[i], closed[i + 1])
        r = holonomy_unit_residual(H)
        D += math.log1p(max(r, 0.0)) * float(dt)
    return float(D)


def energy_boundary_ok(
    E_exertion: float,
    E_sensory: float,
    *,
    kappa: float = 1.0,
) -> bool:
    """Hamiltonian energy boundary: E_exertion ≤ κ · E_sensory.

    Refuse negative energies (zero-fabrication of free action).
    """
    ee = float(E_exertion)
    es = float(E_sensory)
    k = float(kappa)
    if ee < -_NEAR_ZERO or es < -_NEAR_ZERO:
        raise TrajectoryInvariantError(
            "negative_energy", E_exertion=ee, E_sensory=es
        )
    if k < 0.0:
        raise TrajectoryInvariantError("negative_kappa", kappa=k)
    return ee <= k * es + _NEAR_ZERO


@dataclass(frozen=True, slots=True)
class TrajectoryAssessment:
    """Result of assessing a finite trajectory against #21 invariants."""

    divergence: float
    within_replay_bound: bool
    energy_ok: bool
    n_steps: int
    eps_trajectory: float
    kappa: float
    E_exertion: float
    E_sensory: float


def assess_trajectory(
    versors: Sequence[np.ndarray],
    *,
    E_exertion: float,
    E_sensory: float,
    eps_trajectory: float = _DEFAULT_EPS_TRAJECTORY,
    kappa: float = 1.0,
    dt: float = 1.0,
) -> TrajectoryAssessment:
    """Full trajectory gate: divergence bound + energy boundary."""
    D = trajectory_divergence(versors, dt=dt)
    eps = float(eps_trajectory)
    if eps <= 0.0:
        raise TrajectoryInvariantError("non_positive_eps", eps_trajectory=eps)
    e_ok = energy_boundary_ok(E_exertion, E_sensory, kappa=kappa)
    return TrajectoryAssessment(
        divergence=float(D),
        within_replay_bound=bool(D < eps),
        energy_ok=bool(e_ok),
        n_steps=len(versors),
        eps_trajectory=eps,
        kappa=float(kappa),
        E_exertion=float(E_exertion),
        E_sensory=float(E_sensory),
    )


__all__ = [
    "TrajectoryAssessment",
    "TrajectoryInvariantError",
    "assess_trajectory",
    "energy_boundary_ok",
    "holonomy_unit_residual",
    "relative_holonomy",
    "trajectory_divergence",
]
