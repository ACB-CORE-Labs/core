"""ADR-0239 — signature-aware PCA, Procrustes, Cartan–Iwasawa, residual norms."""

from __future__ import annotations

import numpy as np
import pytest

from algebra.rotor import make_rotor_from_angle
from algebra.versor import versor_apply, versor_condition
from core.physics.dynamic_manifold import (
    AxisClassification,
    cartan_iwasawa_factorize,
    conformal_procrustes,
    dual_correction_slerp,
    procrustes_residual,
    signature_aware_pca,
)


def _id() -> np.ndarray:
    v = np.zeros(32, dtype=np.float64)
    v[0] = 1.0
    return v


def test_signature_aware_pca_classifies_and_counts_nulls():
    # Build a small cloud including a null-ish grade-1 direction (e4+e5 style)
    pts = []
    for a in (0.0, 0.2, 0.4, 0.6):
        pts.append(make_rotor_from_angle(a, bivector_idx=6))
    # Add a near-null vector as a multivector point (not necessarily a versor)
    nullish = np.zeros(32, dtype=np.float64)
    nullish[4] = 1.0
    nullish[5] = 1.0  # e4+e5 related; quadratic form may be null-ish under sig
    pts.append(nullish)
    result = signature_aware_pca(pts, max_axes=8)
    assert result.n_points == len(pts)
    assert len(result.axes) == 8
    total_cls = result.n_null + result.n_spacelike + result.n_timelike + result.n_degenerate
    assert total_cls == 8
    # Every axis has a classification enum
    for ax in result.axes:
        assert isinstance(ax.classification, AxisClassification)


def test_pca_replay_deterministic():
    pts = [make_rotor_from_angle(0.1 * i) for i in range(5)]
    a = signature_aware_pca(pts, max_axes=4)
    b = signature_aware_pca(pts, max_axes=4)
    assert a.mean == b.mean
    assert a.explained == b.explained
    assert a.axes[0].vector == b.axes[0].vector
    assert a.n_null == b.n_null


def test_conformal_procrustes_closes_and_low_residual():
    src = _id()
    R = make_rotor_from_angle(0.55, bivector_idx=6)
    tgt = versor_apply(R, src)
    result = conformal_procrustes([src], [tgt])
    assert versor_condition(result.versor) < 1e-6
    assert result.residual_norm < 1e-5
    assert procrustes_residual(src, tgt, result.versor) < 1e-5


def test_conformal_procrustes_multi_pair_deterministic():
    pairs_s = [_id(), make_rotor_from_angle(0.2, 7)]
    pairs_t = [
        versor_apply(make_rotor_from_angle(0.4, 6), pairs_s[0]),
        versor_apply(make_rotor_from_angle(0.4, 6), pairs_s[1]),
    ]
    r1 = conformal_procrustes(pairs_s, pairs_t)
    r2 = conformal_procrustes(pairs_s, pairs_t)
    assert np.allclose(r1.versor, r2.versor)
    assert r1.residual_norm == r2.residual_norm
    assert versor_condition(r1.versor) < 1e-6


def test_cartan_iwasawa_factors_closed():
    V = make_rotor_from_angle(0.7, bivector_idx=6)
    factors = cartan_iwasawa_factorize(V)
    for name, f in (("K", factors.K), ("A", factors.A), ("N", factors.N)):
        assert versor_condition(f) < 1e-6, name


def test_dual_correction_slerp_closed():
    src = _id()
    tgt = make_rotor_from_angle(1.0)
    for alpha in (0.0, 0.3, 0.7, 1.0):
        out = dual_correction_slerp(src, tgt, alpha)
        assert versor_condition(out) < 1e-6


def test_procrustes_residual_is_dedicated_norm():
    src = _id()
    tgt = make_rotor_from_angle(0.5)
    V = conformal_procrustes([src], [tgt]).versor
    r = procrustes_residual(src, tgt, V)
    assert isinstance(r, float)
    assert r >= 0.0


def test_pca_rejects_empty():
    with pytest.raises(ValueError):
        signature_aware_pca([])
