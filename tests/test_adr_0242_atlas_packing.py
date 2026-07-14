"""ADR-0242 — Golden-Angle atlas packing behavioral pins."""

from __future__ import annotations

import math

import numpy as np
import pytest

from algebra.cga import is_null
from core.physics.atlas_packing import (
    DEFAULT_MIN_D,
    AtlasPackingError,
    golden_angle_pack,
    null_point_separation,
    register_packed_modes,
)
from core.physics.wave_manifold import WaveManifold


def test_golden_angle_pack_n_modes_min_geodesic_ge_0_12():
    modes = golden_angle_pack(n=10, alpha=0.5)
    assert len(modes) == 10
    min_d = min(
        null_point_separation(modes[i], modes[j])
        for i in range(len(modes))
        for j in range(i + 1, len(modes))
    )
    assert min_d >= DEFAULT_MIN_D


def test_golden_angle_pack_rejects_when_alpha_too_dense():
    with pytest.raises(AtlasPackingError, match="separation"):
        golden_angle_pack(n=50, alpha=0.01)


def test_packing_lift_produces_closed_or_null_legal_points():
    modes = golden_angle_pack(n=5, alpha=0.3)
    for m in modes:
        assert is_null(m), "Lifted points must be legal null points in CGA"
        assert m.shape == (32,)
        assert m.dtype == np.float64


def test_packing_deterministic_for_fixed_alpha_n():
    modes1 = golden_angle_pack(n=20, alpha=0.4)
    modes2 = golden_angle_pack(n=20, alpha=0.4)
    for m1, m2 in zip(modes1, modes2):
        np.testing.assert_allclose(m1, m2)


def test_no_poincare_runtime_storage_in_wave_or_vault_metadata_truth():
    manifold = WaveManifold()
    modes = golden_angle_pack(n=5, alpha=0.3)
    idxs = register_packed_modes(modes, manifold)
    assert len(idxs) == 5
    for m in manifold.resonant_modes:
        assert m.shape == (32,)
        assert m.dtype == np.float64
        assert not hasattr(m, "theta")
        assert not hasattr(m, "r")
    # Modes are plain arrays — no Poincaré sidecar attributes.
    assert not hasattr(modes[0], "theta")


def test_null_point_separation_matches_euclidean_embed():
    """cga_inner contract: ⟨P,Q⟩ = −d²/2 for embedded Euclidean points."""
    from algebra.cga import embed_point

    p = embed_point(np.asarray([0.1, 0.0, 0.0], dtype=np.float64), dtype=np.float64)
    q = embed_point(np.asarray([0.4, 0.0, 0.0], dtype=np.float64), dtype=np.float64)
    d = null_point_separation(p, q)
    assert abs(d - 0.3) < 1e-9
