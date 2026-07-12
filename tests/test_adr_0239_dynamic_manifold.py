"""ADR-0239 — signature_aware_pca, conformal_procrustes, cartan_iwasawa_extract."""

from __future__ import annotations

import numpy as np
import pytest

from algebra.rotor import make_rotor_from_angle
from algebra.versor import versor_apply, versor_condition
from core.physics.dynamic_manifold import (
    AxisClassification,
    cartan_iwasawa_extract,
    cartan_iwasawa_factorize,
    conformal_procrustes,
    dual_correction_slerp,
    procrustes_residual,
    signature_aware_pca,
    signature_aware_pca_report,
)


def _id32() -> np.ndarray:
    v = np.zeros(32, dtype=np.float64)
    v[0] = 1.0
    return v


def test_signature_aware_pca_keeps_nulls():
    # Build 5D cloud including a null direction e4+e5 style
    rng_pts = []
    for t in np.linspace(0, 1, 6):
        v = np.array([t, 0.1 * t, 0.0, 0.5 * (t * t - 1), 0.5 * (t * t + 1)], dtype=np.float64)
        rng_pts.append(v)
    # pure null-ish
    nullish = np.array([0.0, 0.0, 0.0, 1.0, 1.0], dtype=np.float64)
    rng_pts.append(nullish)
    X = np.column_stack(rng_pts)
    basis = signature_aware_pca(X, target_grade=4)
    assert basis.shape[0] == 5
    assert basis.shape[1] == 4
    report = signature_aware_pca_report(X, target_grade=4)
    total = report.n_null + report.n_spacelike + report.n_timelike + report.n_degenerate
    assert total == 4
    for ax in report.axes:
        assert isinstance(ax.classification, AxisClassification)


def test_pca_replay():
    X = np.column_stack(
        [
            np.array([1.0, 0, 0, -0.5, 0.5]),
            np.array([0, 1.0, 0, -0.5, 0.5]),
            np.array([0, 0, 1.0, -0.5, 0.5]),
            np.array([0.5, 0.5, 0, 0.0, 1.0]),
        ]
    )
    a = signature_aware_pca(X, target_grade=3)
    b = signature_aware_pca(X, target_grade=3)
    assert np.allclose(a, b)


def test_conformal_procrustes_multivector_low_residual():
    src = _id32()
    R = make_rotor_from_angle(0.55, bivector_idx=6)
    tgt = versor_apply(R, src)
    V, residual = conformal_procrustes(src, tgt)
    assert versor_condition(V) < 1e-6
    assert residual < 1e-5
    assert procrustes_residual(src, tgt, V) < 1e-5


def test_conformal_procrustes_5d_cloud():
    P = np.column_stack(
        [
            np.array([0.0, 0, 0, -0.5, 0.5]),
            np.array([1.0, 0, 0, 0.0, 1.0]),
        ]
    )
    # rotate first two euclidean coords
    Q = P.copy()
    Q[0, :], Q[1, :] = P[1, :], -P[0, :]
    V, residual = conformal_procrustes(P, Q)
    assert V.shape == (5, 5)
    assert residual >= 0.0


def test_cartan_iwasawa_extract_closed():
    V = make_rotor_from_angle(0.7, bivector_idx=6)
    R, T, D = cartan_iwasawa_extract(V)
    for f in (R, T, D):
        assert versor_condition(f) < 1e-6
    factors = cartan_iwasawa_factorize(V)
    assert factors.reconstruction_residual >= 0.0


def test_dual_correction_slerp_closed():
    src = _id32()
    tgt = make_rotor_from_angle(1.0)
    for a in (0.0, 0.3, 1.0):
        out = dual_correction_slerp(src, tgt, a)
        assert versor_condition(out) < 1e-6


def test_pca_rejects_bad_shape():
    with pytest.raises(ValueError):
        signature_aware_pca(np.zeros((4, 3)))
