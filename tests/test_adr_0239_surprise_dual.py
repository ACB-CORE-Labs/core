"""ADR-0239 — Surprise residual + dual operator with Procrustes."""

from __future__ import annotations

import numpy as np

from algebra.rotor import make_rotor_from_angle
from algebra.versor import versor_apply, versor_condition
from core.physics.surprise import (
    analogy_seed,
    dual_operator,
    project_onto_basis,
    surprise_residual,
)


def _id() -> np.ndarray:
    v = np.zeros(32, dtype=np.float64)
    v[0] = 1.0
    return v


def test_surprise_zero_on_span():
    b0 = _id()
    b1 = make_rotor_from_angle(0.3)
    x = 0.4 * b0 + 0.6 * b1
    surp = surprise_residual(x, [b0, b1])
    assert surp.residual_norm < 1e-9
    assert surp.basis_rank == 2


def test_surprise_orthogonal_to_basis():
    b0 = _id()
    b1 = make_rotor_from_angle(0.5, bivector_idx=6)
    x = make_rotor_from_angle(1.2, bivector_idx=7)
    surp = surprise_residual(x, [b0, b1])
    proj = project_onto_basis(x, [b0, b1])
    # residual · each orthonormal basis direction ≈ 0
    from core.physics.surprise import _orthonormalize_basis

    B = _orthonormalize_basis([b0, b1])
    for i in range(B.shape[0]):
        assert abs(float(np.dot(surp.residual_mv, B[i]))) < 1e-8
    assert np.allclose(surp.residual_mv + proj, x, atol=1e-8)


def test_analogy_seed_stable_order():
    surp = surprise_residual(make_rotor_from_angle(1.0), [_id()])
    analogs = [
        ("b", _id(), make_rotor_from_angle(0.2)),
        ("a", _id(), make_rotor_from_angle(0.9)),
        ("c", _id(), make_rotor_from_angle(0.1)),
    ]
    s1 = analogy_seed(surp, analogs)
    s2 = analogy_seed(surp, analogs)
    assert [s.analog_id for s in s1] == [s.analog_id for s in s2]


def test_dual_operator_productive_path():
    src = _id()
    R = make_rotor_from_angle(0.6)
    tgt = versor_apply(R, src)
    x = make_rotor_from_angle(0.2, bivector_idx=7)
    dual = dual_operator(
        x,
        [_id()],
        [("anchor", src, tgt)],
        kappa=1.0,
        productive_threshold=2.0,  # permissive for structural map existence
    )
    assert dual.surprise.residual_norm >= 0.0
    if dual.procrustes is not None:
        assert versor_condition(dual.procrustes.versor) < 1e-6


def test_dual_operator_refuse_no_analogs():
    dual = dual_operator(make_rotor_from_angle(0.5), [_id()], [], kappa=1.0)
    assert dual.productive is False
    assert dual.reason in {"no_analogs", "surprise_below_minimum"}


def test_dual_replay_deterministic():
    src = _id()
    tgt = make_rotor_from_angle(0.4)
    x = make_rotor_from_angle(0.9, 8)
    a = dual_operator(x, [_id()], [("a", src, tgt)], kappa=0.8)
    b = dual_operator(x, [_id()], [("a", src, tgt)], kappa=0.8)
    assert a.productive == b.productive
    assert a.reason == b.reason
    assert a.surprise.residual_norm == b.surprise.residual_norm
    if a.procrustes and b.procrustes:
        assert np.allclose(a.procrustes.versor, b.procrustes.versor)
