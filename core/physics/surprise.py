"""core.physics.surprise — Surprise Residual + dual with Procrustes (ADR-0239).

Surprise Residual:  S(x) = x − proj_B(x)
where B is a known basis (ordered multivector span). High surprise seeds
Conformal Procrustes against vault analogs → productive novelty only when the
post-transfer residual is below threshold; otherwise typed refuse.

No sampling. No statistical ranking. Deterministic ordered analog lists.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

from algebra.cl41 import N_COMPONENTS
from algebra.versor import versor_condition
from core.physics.dynamic_manifold import (
    ConformalProcrustesResult,
    conformal_procrustes,
    procrustes_residual,
)

_NEAR_ZERO = 1e-12
_CLOSURE_TOL = 1e-6
_DEFAULT_PRODUCTIVE_THRESHOLD = 0.35


@dataclass(frozen=True, slots=True)
class SurpriseResult:
    residual_mv: np.ndarray
    residual_norm: float
    projection: np.ndarray
    basis_rank: int


@dataclass(frozen=True, slots=True)
class AnalogySeed:
    analog_id: str
    source: np.ndarray
    target: np.ndarray
    surprise_affinity: float


@dataclass(frozen=True, slots=True)
class DualOperatorResult:
    surprise: SurpriseResult
    procrustes: ConformalProcrustesResult | None
    productive: bool
    kappa: float
    reason: str
    selected_analog_id: str | None


def _as_mv(v: np.ndarray, name: str) -> np.ndarray:
    arr = np.asarray(v, dtype=np.float64)
    if arr.shape != (N_COMPONENTS,):
        raise ValueError(f"{name} must have shape ({N_COMPONENTS},); got {arr.shape}")
    return arr


def _orthonormalize_basis(basis: Sequence[np.ndarray]) -> np.ndarray:
    """Deterministic Gram–Schmidt on coefficient space (ordered input).

    Returns matrix B with shape (rank, 32). Zero / dependent vectors dropped
    in order — not silently as "null PCA axes"; rank is reported.
    """
    cols: list[np.ndarray] = []
    for i, b in enumerate(basis):
        v = _as_mv(b, f"basis[{i}]").copy()
        for u in cols:
            v = v - float(np.dot(v, u)) * u
        n = float(np.linalg.norm(v))
        if n < _NEAR_ZERO:
            continue
        cols.append(v / n)
    if not cols:
        return np.zeros((0, N_COMPONENTS), dtype=np.float64)
    return np.stack(cols, axis=0)


def project_onto_basis(x: np.ndarray, basis: Sequence[np.ndarray]) -> np.ndarray:
    """Orthogonal projection of x onto span(B) in coefficient space."""
    x_arr = _as_mv(x, "x")
    B = _orthonormalize_basis(basis)
    if B.shape[0] == 0:
        return np.zeros(N_COMPONENTS, dtype=np.float64)
    # proj = sum_i <x, u_i> u_i
    coeffs = B @ x_arr
    return (B.T @ coeffs).astype(np.float64, copy=False)


def surprise_residual(
    x: np.ndarray,
    basis: Sequence[np.ndarray],
) -> SurpriseResult:
    """S(x) = x − proj_B(x). Residual is orthogonal to span(B)."""
    x_arr = _as_mv(x, "x")
    proj = project_onto_basis(x_arr, basis)
    residual = (x_arr - proj).astype(np.float64, copy=False)
    B = _orthonormalize_basis(basis)
    return SurpriseResult(
        residual_mv=residual,
        residual_norm=float(np.linalg.norm(residual)),
        projection=proj,
        basis_rank=int(B.shape[0]),
    )


def analogy_seed(
    surprise: SurpriseResult,
    analogs: Sequence[tuple[str, np.ndarray, np.ndarray]],
    *,
    top_k: int | None = None,
) -> tuple[AnalogySeed, ...]:
    """Rank vault analogs by affinity to the surprise residual (deterministic).

    Affinity = |cos| between residual and (target − source) direction in
    coefficient space. Higher affinity → better structural candidate.
    Order is stable: affinity desc, then analog_id asc.
    """
    if surprise.residual_norm < _NEAR_ZERO:
        return ()
    r = surprise.residual_mv
    r_n = surprise.residual_norm
    seeds: list[AnalogySeed] = []
    for item in analogs:
        if len(item) != 3:
            raise ValueError("each analog must be (id, source, target)")
        aid, src, tgt = item
        s = _as_mv(src, f"analog[{aid}].source")
        t = _as_mv(tgt, f"analog[{aid}].target")
        delta = t - s
        dn = float(np.linalg.norm(delta))
        if dn < _NEAR_ZERO:
            aff = 0.0
        else:
            aff = abs(float(np.dot(r, delta)) / (r_n * dn))
        seeds.append(
            AnalogySeed(
                analog_id=str(aid),
                source=s,
                target=t,
                surprise_affinity=float(aff),
            )
        )
    seeds.sort(key=lambda s: (-s.surprise_affinity, s.analog_id))
    if top_k is not None:
        seeds = seeds[: max(0, int(top_k))]
    return tuple(seeds)


def dual_operator(
    x: np.ndarray,
    basis: Sequence[np.ndarray],
    analogs: Sequence[tuple[str, np.ndarray, np.ndarray]],
    *,
    kappa: float = 1.0,
    productive_threshold: float = _DEFAULT_PRODUCTIVE_THRESHOLD,
    min_surprise: float = 1e-6,
) -> DualOperatorResult:
    """Surprise + Procrustes dual.

    High surprise seeds Procrustes against the best analog. Productive only when
    post-transfer residual ≤ productive_threshold * (1/κ-scaled). κ from
    CoherenceGoldTether scales the threshold (higher κ → stricter).
    """
    if kappa <= 0.0:
        raise ValueError("kappa must be positive")
    surprise = surprise_residual(x, basis)
    if surprise.residual_norm < min_surprise:
        return DualOperatorResult(
            surprise=surprise,
            procrustes=None,
            productive=False,
            kappa=float(kappa),
            reason="surprise_below_minimum",
            selected_analog_id=None,
        )

    seeds = analogy_seed(surprise, analogs, top_k=1)
    if not seeds:
        return DualOperatorResult(
            surprise=surprise,
            procrustes=None,
            productive=False,
            kappa=float(kappa),
            reason="no_analogs",
            selected_analog_id=None,
        )

    best = seeds[0]
    # Transfer: Procrustes from analog source→target applied as structural map;
    # measure residual of mapping x's projection-completion toward analog target shape.
    proc = conformal_procrustes([best.source], [best.target])
    # Residual of applying the analog's versor to x vs. the analog target direction.
    transfer_res = procrustes_residual(x, best.target, proc.versor)
    # Also include native procrustes residual of the analog pair itself.
    residual = max(float(proc.residual_norm), float(transfer_res))
    threshold = float(productive_threshold) / float(kappa)
    productive = residual <= threshold and versor_condition(proc.versor) < _CLOSURE_TOL

    return DualOperatorResult(
        surprise=surprise,
        procrustes=proc,
        productive=bool(productive),
        kappa=float(kappa),
        reason="productive_novelty" if productive else "residual_above_threshold",
        selected_analog_id=best.analog_id,
    )
