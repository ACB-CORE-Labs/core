"""core.physics.biography — Biography Holonomy Blade (ADR-0240).

Forever-lived individuality as an integrated holonomy of the identity
trajectory. Reconstructible from an ordered sequence of session versors —
reconstruction-over-storage. Not a raw experience dump; not a parallel
identity store.

Integrates with ``algebra.holonomy.holonomy_encode`` and the identity motor
surface; does not mutate packs, vault, or serving paths.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

import numpy as np

from algebra.cl41 import N_COMPONENTS
from algebra.holonomy import holonomy_encode, holonomy_similarity
from algebra.versor import unitize_versor, versor_condition

_CLOSURE_TOL = 1e-6
_TELEMETRY_SCHEMA = "biography_holonomy_v1"


@dataclass(frozen=True, slots=True)
class BiographyHolonomyBlade:
    """Integrated holonomy blade of a lived trajectory."""

    blade: np.ndarray
    n_steps: int
    trajectory_hash: str
    closure: float

    def similarity(self, other: "BiographyHolonomyBlade") -> float:
        return float(holonomy_similarity(self.blade, other.blade))


def _as_versor(v: np.ndarray, name: str) -> np.ndarray:
    arr = np.asarray(v, dtype=np.float64)
    if arr.shape != (N_COMPONENTS,):
        raise ValueError(f"{name} must have shape ({N_COMPONENTS},)")
    # Construction boundary: trajectory elements must be closed versors.
    try:
        closed = unitize_versor(arr)
    except ValueError as exc:
        raise ValueError(f"{name} is not a closed versor: {exc}") from exc
    cond = versor_condition(closed)
    if cond >= _CLOSURE_TOL:
        raise ValueError(f"{name} versor_condition={cond:.3e}")
    return closed.astype(np.float64, copy=False)


def _trajectory_hash(versors: Sequence[np.ndarray]) -> str:
    import hashlib

    h = hashlib.sha256()
    for v in versors:
        h.update(np.asarray(v, dtype=np.float64).tobytes())
    return h.hexdigest()


def integrate_biography(
    trajectory: Sequence[np.ndarray],
    *,
    alpha: float = 0.5,
) -> BiographyHolonomyBlade:
    """Integrate ordered identity/session versors into a biography holonomy blade.

    Order is load-bearing. Empty trajectory is refused (no confabulated self).
    """
    if not trajectory:
        raise ValueError("biography trajectory must be non-empty")
    closed = [_as_versor(v, f"trajectory[{i}]") for i, v in enumerate(trajectory)]
    blade = holonomy_encode(closed, alpha=alpha)
    cond = versor_condition(blade)
    if cond >= _CLOSURE_TOL:
        raise ValueError(f"biography blade not closed: {cond:.3e}")
    return BiographyHolonomyBlade(
        blade=np.asarray(blade, dtype=np.float64),
        n_steps=len(closed),
        trajectory_hash=_trajectory_hash(closed),
        closure=float(cond),
    )


def reconstruct_biography(
    trajectory: Sequence[np.ndarray],
    *,
    alpha: float = 0.5,
) -> BiographyHolonomyBlade:
    """Alias for integrate — reconstruction is recompute, not storage load."""
    return integrate_biography(trajectory, alpha=alpha)


def biography_telemetry(blade: BiographyHolonomyBlade) -> dict[str, Any]:
    """Workbench-safe projection (no full multivector dump required for UI)."""
    return {
        "schema_version": _TELEMETRY_SCHEMA,
        "n_steps": int(blade.n_steps),
        "trajectory_hash": blade.trajectory_hash,
        "closure": float(blade.closure),
        "blade_scalar": float(blade.blade[0]),
        "blade_pseudoscalar": float(blade.blade[31]),
        "blade_l2": float(np.linalg.norm(blade.blade)),
    }
