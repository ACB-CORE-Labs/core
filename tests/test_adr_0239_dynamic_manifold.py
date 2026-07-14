"""ADR-0239 — signature_aware_pca, conformal_procrustes, cartan_iwasawa_extract."""

from __future__ import annotations

import numpy as np
import pytest

from algebra.cga import embed_point
from algebra.cl41 import geometric_product
from algebra.null_point import dilator, translator
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
    so3_matrix_to_rotor,
)


def _id32() -> np.ndarray:
    v = np.zeros(32, dtype=np.float64)
    v[0] = 1.0
    return v


def _composed_multiplane(seed: float = 0.0) -> np.ndarray:
    v = _id32()
    for k, idx in enumerate((6, 7, 10, 11)):
        angle = 0.35 + 0.11 * k + 0.04 * seed
        v = geometric_product(v, make_rotor_from_angle(angle, bivector_idx=idx))
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
    """Non-identity multiplane F_A; F_B = sandwich(W, F_A); sandwich residual < 1e-5."""
    F_A = _composed_multiplane(seed=1.0)
    W = geometric_product(
        geometric_product(
            make_rotor_from_angle(0.55, bivector_idx=6),
            make_rotor_from_angle(0.4, bivector_idx=7),
        ),
        make_rotor_from_angle(0.3, bivector_idx=10),
    )
    F_B = versor_apply(W, F_A)
    # Guard: this is not the vacuous identity→identity case.
    assert float(np.linalg.norm(F_A - _id32())) > 1e-3
    assert float(np.linalg.norm(F_B - F_A)) > 1e-3

    V, residual = conformal_procrustes(F_A, F_B)
    assert V.shape == (32,)
    assert versor_condition(V) < 1e-6
    assert residual < 1e-5
    assert procrustes_residual(F_A, F_B, V) < 1e-5
    assert float(np.linalg.norm(versor_apply(V, F_A) - F_B)) < 1e-5


def test_conformal_procrustes_5d_cloud():
    """Known rotation on a (5,K) cloud: residual < 1e-6 and mapped points match."""
    pts = [
        np.array([0.0, 0.0, 0.0], dtype=np.float64),
        np.array([1.0, 0.0, 0.0], dtype=np.float64),
        np.array([0.0, 1.0, 0.0], dtype=np.float64),
        np.array([0.5, 0.5, 0.2], dtype=np.float64),
    ]
    P = np.column_stack([embed_point(p, dtype=np.float64)[1:6] for p in pts])
    th = np.pi / 2.0
    R3 = np.array(
        [[np.cos(th), -np.sin(th), 0.0], [np.sin(th), np.cos(th), 0.0], [0.0, 0.0, 1.0]],
        dtype=np.float64,
    )
    Q = np.column_stack(
        [embed_point(R3 @ p, dtype=np.float64)[1:6] for p in pts]
    )
    M, residual = conformal_procrustes(P, Q)
    assert M.shape == (5, 5)
    assert residual < 1e-6
    mapped = M @ P
    # Projective match: dehomogenized Euclidean images agree.
    for k in range(P.shape[1]):
        wm = mapped[4, k] - mapped[3, k]
        wq = Q[4, k] - Q[3, k]
        assert abs(wm) > 1e-9 and abs(wq) > 1e-9
        assert np.allclose(mapped[:3, k] / wm, Q[:3, k] / wq, atol=1e-8)


def test_conformal_procrustes_full_similarity_cloud():
    """Nontrivial scale + rotation + translation on a (5,K) cloud."""
    rng = np.random.default_rng(239)
    X = rng.normal(size=(3, 10))
    s = 1.7
    th = 0.6
    R3 = np.array(
        [[np.cos(th), -np.sin(th), 0.0], [np.sin(th), np.cos(th), 0.0], [0.0, 0.0, 1.0]],
        dtype=np.float64,
    )
    t = np.array([0.5, -0.3, 0.2], dtype=np.float64)
    Y = s * (R3 @ X) + t[:, None]
    P = np.column_stack([embed_point(X[:, k], dtype=np.float64)[1:6] for k in range(10)])
    Q = np.column_stack([embed_point(Y[:, k], dtype=np.float64)[1:6] for k in range(10)])
    M, residual = conformal_procrustes(P, Q)
    assert M.shape == (5, 5)
    assert residual < 1e-6
    mapped = M @ P
    for k in range(10):
        wm = mapped[4, k] - mapped[3, k]
        eu = mapped[:3, k] / wm
        assert np.allclose(eu, Y[:, k], atol=1e-8)


def test_conformal_procrustes_null_point_list_sandwich():
    """List of 32-vec CGA null points recovers V32 with sandwich residual < 1e-6."""
    src_eucl = [
        np.array([0.0, 0.0, 0.0], dtype=np.float64),
        np.array([1.0, 0.0, 0.0], dtype=np.float64),
        np.array([0.0, 1.0, 0.0], dtype=np.float64),
        np.array([0.5, 0.3, 0.1], dtype=np.float64),
        np.array([-0.2, 0.4, 0.5], dtype=np.float64),
    ]
    src = [embed_point(p, dtype=np.float64) for p in src_eucl]
    s, th = 1.5, 0.45
    R3 = np.array(
        [[np.cos(th), -np.sin(th), 0.0], [np.sin(th), np.cos(th), 0.0], [0.0, 0.0, 1.0]],
        dtype=np.float64,
    )
    t = np.array([0.25, -0.1, 0.3], dtype=np.float64)
    W = geometric_product(
        geometric_product(translator(t), dilator(s)),
        so3_matrix_to_rotor(R3),
    )
    tgt = [versor_apply(W, p) for p in src]
    V, residual = conformal_procrustes(src, tgt)
    assert V.shape == (32,)
    assert versor_condition(V) < 1e-6
    assert residual < 1e-6
    for p, q in zip(src, tgt):
        assert float(np.linalg.norm(versor_apply(V, p) - q)) < 1e-6


def test_cartan_iwasawa_extract_closed():
    V = make_rotor_from_angle(0.7, bivector_idx=6)
    R, T, D = cartan_iwasawa_extract(V)
    for f in (R, T, D):
        assert versor_condition(f) < 1e-6
    factors = cartan_iwasawa_factorize(V)
    recon = geometric_product(geometric_product(factors.R, factors.T), factors.D)
    residual = float(np.linalg.norm(recon - V))
    assert residual < 1e-6
    assert factors.reconstruction_residual < 1e-6
    assert abs(factors.reconstruction_residual - residual) < 1e-12


def test_dual_correction_slerp_closed():
    src = _id32()
    tgt = make_rotor_from_angle(1.0)
    for a in (0.0, 0.3, 1.0):
        out = dual_correction_slerp(src, tgt, a)
        assert versor_condition(out) < 1e-6


def test_dual_correction_slerp_translator_half():
    """Null-bivector power must not erase the Cartan translation leg."""
    from algebra.null_point import recover_translation, translator

    src = _id32()
    tgt = translator(np.array([2.0, 0.0, 0.0], dtype=np.float64))
    out = dual_correction_slerp(src, tgt, 0.5)
    assert versor_condition(out) < 1e-6
    a, _ = recover_translation(out)
    assert np.allclose(a, [1.0, 0.0, 0.0], atol=1e-6)


def test_pca_rejects_bad_shape():
    with pytest.raises(ValueError):
        signature_aware_pca(np.zeros((4, 3)))
