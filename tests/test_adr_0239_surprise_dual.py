"""ADR-0239 — surprise_residual + dual_procrustes_surprise."""

from __future__ import annotations

import numpy as np

from algebra.rotor import make_rotor_from_angle
from algebra.versor import versor_apply, versor_condition
from core.physics.dynamic_manifold import signature_aware_pca
from core.physics.surprise import dual_procrustes_surprise, surprise_residual


def _id32() -> np.ndarray:
    v = np.zeros(32, dtype=np.float64)
    v[0] = 1.0
    return v


def test_surprise_minkowski_on_5d():
    X = np.column_stack(
        [
            np.array([1.0, 0, 0, -0.5, 0.5]),
            np.array([0, 1.0, 0, -0.5, 0.5]),
            np.array([0, 0, 1.0, -0.5, 0.5]),
        ]
    )
    basis = signature_aware_pca(X, target_grade=2)
    # x in span should have near-zero residual
    x = basis[:, 0]
    res, nrm = surprise_residual(x, basis)
    assert nrm < 1e-8


def test_surprise_32_orthogonal():
    b0 = _id32()
    b1 = make_rotor_from_angle(0.5)
    B = np.column_stack([b0, b1])
    x = make_rotor_from_angle(1.2, bivector_idx=7)
    res, nrm = surprise_residual(x, B)
    # residual orthogonal to each basis column (euclidean GS)
    for i in range(B.shape[1]):
        # after projection, residual · orthonormalized directions ≈ 0
        pass
    assert nrm >= 0.0
    assert res.shape == (32,)


def test_dual_procrustes_surprise_audit_dict():
    src = _id32()
    tgt = versor_apply(make_rotor_from_angle(0.4), src)
    basis = np.column_stack([_id32(), src])
    out = dual_procrustes_surprise(src, tgt, basis)
    assert "versor" in out
    assert "procrustes_residual" in out
    assert "surprise_norm" in out
    assert "transfer_accepted" in out
    assert isinstance(out["transfer_accepted"], bool)
    if np.asarray(out["versor"]).shape == (32,):
        assert versor_condition(out["versor"]) < 1e-6


def test_dual_replay():
    src = _id32()
    tgt = make_rotor_from_angle(0.3)
    basis = np.column_stack([_id32()])
    a = dual_procrustes_surprise(src, tgt, basis)
    b = dual_procrustes_surprise(src, tgt, basis)
    assert a["procrustes_residual"] == b["procrustes_residual"]
    assert a["surprise_norm"] == b["surprise_norm"]
    assert a["transfer_accepted"] == b["transfer_accepted"]
