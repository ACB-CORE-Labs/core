"""core.physics.atlas_packing — Golden-Angle mode packing (ADR-0242).

Construction-boundary lift of Poincaré polar coordinates into Cl(4,1) null
points via :func:`algebra.cga.embed_point`. Runtime storage is pure 32-vectors
only (no Poincaré attribute leaks).

Separation uses the CGA null-point distance recovered from ``cga_inner``:

    ⟨P,Q⟩ = −d²/2  ⇒  d = √(−2⟨P,Q⟩)

which is the Euclidean distance of the embedded R³ points (see ``cga_inner``
doc). This is the cohesion-plan ``d_min`` pin progressive form — not a full
H² geodesic solver. Fail-closed if any pair has ``d < min_d``.

Off-serve: do not import from ``chat/runtime.py`` (A-04 quarantine).
"""

from __future__ import annotations

import math
from typing import Sequence

import numpy as np

from algebra.backend import cga_inner
from algebra.cga import embed_point
from core.physics.wave_manifold import WaveManifold

PHI = (1.0 + math.sqrt(5.0)) / 2.0
DEFAULT_MIN_D = 0.12
# Reconstruction-over-storage: layout regenerates from identity + ordinal k.
ALLOCATOR_IDENTITY = "golden_angle"
ALLOCATOR_VERSION = "golden_angle_v1"


class AtlasPackingError(ValueError):
    """Fail-closed packing refusal (separation / bounds)."""


def null_point_separation(p: np.ndarray, q: np.ndarray) -> float:
    """CGA null-point separation d = √(max(0, −2⟨P,Q⟩))."""
    inner = float(cga_inner(np.asarray(p, dtype=np.float64), np.asarray(q, dtype=np.float64)))
    # Clamp tiny positive float dust from null-cone numerics.
    return math.sqrt(max(0.0, -2.0 * min(0.0, inner)))


def golden_angle_pack(
    n: int,
    alpha: float,
    *,
    min_d: float = DEFAULT_MIN_D,
) -> list[np.ndarray]:
    """Golden-Angle packing on the Cl(4,1) null cone (horosphere lift).

    For k = 0..n-1:
      θ_k = 2π k / φ
      r_k = tanh(α √k)
      (x,y) = (r cos θ, r sin θ) → embed_point → null 32-vector

    Rejects with :class:`AtlasPackingError` if any pairwise separation < min_d.

    Layout is reconstructible from :data:`ALLOCATOR_VERSION` and ordinals
    ``0..n-1`` (no opaque mutable coordinate table as truth).
    """
    if n < 1:
        raise AtlasPackingError("n must be >= 1")
    if not math.isfinite(alpha) or alpha <= 0.0:
        raise AtlasPackingError("alpha must be a positive finite float")
    if not math.isfinite(min_d) or min_d < 0.0:
        raise AtlasPackingError("min_d must be a non-negative finite float")

    modes: list[np.ndarray] = []
    for k in range(n):
        # 2π/φ ≈ 222.5°; packing-equivalent complement is the classic ~137.5° golden angle.
        theta_k = 2.0 * math.pi * k / PHI
        r_k = math.tanh(alpha * math.sqrt(float(k)))
        x = r_k * math.cos(theta_k)
        y = r_k * math.sin(theta_k)
        mode = embed_point(np.asarray([x, y, 0.0], dtype=np.float64), dtype=np.float64)
        modes.append(np.asarray(mode, dtype=np.float64))

    for i in range(len(modes)):
        for j in range(i + 1, len(modes)):
            d = null_point_separation(modes[i], modes[j])
            if d < min_d:
                raise AtlasPackingError(
                    f"Packing rejected: separation {d:.4f} between {i} and {j} "
                    f"is less than required minimum {min_d:.4f}."
                )
    return modes


def allocator_layout_descriptor(
    n: int,
    alpha: float,
    *,
    min_d: float = DEFAULT_MIN_D,
) -> dict[str, object]:
    """Content-free reconstruction metadata for packing (no coordinate leak)."""
    return {
        "allocator_identity": ALLOCATOR_IDENTITY,
        "allocator_version": ALLOCATOR_VERSION,
        "n": int(n),
        "alpha": float(alpha),
        "min_d": float(min_d),
        "metric": "cga_null_point_euclidean_d",
        "note": "not_full_H2_geodesic",
    }


def register_packed_modes(
    modes: Sequence[np.ndarray],
    manifold: WaveManifold,
) -> tuple[int, ...]:
    """Register packed null modes on a session WaveManifold. Returns indices.

    Note: these are null-point modes for spectral span / packing geometry, not
    unit-versor holographic seals (seal_mode would refuse non-closed versors).
    """
    indices: list[int] = []
    for mode in modes:
        indices.append(manifold.register_resonant_mode(mode))
    return tuple(indices)


__all__ = [
    "PHI",
    "DEFAULT_MIN_D",
    "ALLOCATOR_IDENTITY",
    "ALLOCATOR_VERSION",
    "AtlasPackingError",
    "null_point_separation",
    "golden_angle_pack",
    "allocator_layout_descriptor",
    "register_packed_modes",
]
