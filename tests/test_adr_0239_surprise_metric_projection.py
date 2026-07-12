"""ADR-0239 finding #20 — surprise_residual is a metric-orthogonal projection.

These assert the *behavioral* fix (the exact CGA-metric projection replacing the
Euclidean Gram-Schmidt), not just closure/shape. See
docs/research/third-door-blueprint-fidelity.md §6.

Tests are labelled by what they prove:
  * METRIC-DISTINGUISHING — would FAIL under the old Euclidean projection
    (test_metric_projection_differs_from_euclidean, test_five_vector_branch_*,
    test_null_pair_projection_is_metric_exact, test_lone_null_column_refused,
    test_null_residual_reports_nonzero_surprise).
  * REGRESSION / CONTAINMENT GUARD — metric-agnostic properties that must hold
    regardless (in-span→0, grade purity, determinism, redundant-basis admission).
"""

from __future__ import annotations

import numpy as np
import pytest

from algebra.cga import blade_norm, cga_inner
from algebra.cl41 import grade_project
from algebra.rotor import make_rotor_from_angle
from core.physics.surprise import (
    SurpriseResidualError,
    dual_operator,
    surprise_residual,
)

_ETA5 = np.diag([1.0, 1.0, 1.0, 1.0, -1.0]).astype(np.float64)


def _id32() -> np.ndarray:
    v = np.zeros(32, dtype=np.float64)
    v[0] = 1.0
    return v


def _n_o() -> np.ndarray:
    v = np.zeros(32, dtype=np.float64)
    v[5], v[4] = 0.5, -0.5
    return v


def _n_inf() -> np.ndarray:
    v = np.zeros(32, dtype=np.float64)
    v[4], v[5] = 1.0, 1.0
    return v


def _vec(idx: int, val: float = 1.0) -> np.ndarray:
    """Grade-1 basis vector e_idx (idx in 1..5) as a 32-vector."""
    v = np.zeros(32, dtype=np.float64)
    v[idx] = val
    return v


# --- METRIC-DISTINGUISHING: the load-bearing proofs of the fix ---------------

def test_metric_projection_differs_from_euclidean():
    """Projection uses cga_inner, NOT the Euclidean dot.

    b = 2*e1 + e5 is non-null (<b,b> = 4 - 1 = 3). Projecting x = e1 gives a
    metric coefficient 2/3, whereas a Euclidean projection would give 2/5 — a
    provably different residual.
    """
    b = 2.0 * _vec(1) + _vec(5)
    x = _vec(1)
    res, _nrm = surprise_residual(x, b.reshape(32, 1))

    c_metric = cga_inner(b, x) / cga_inner(b, b)  # 2/3
    assert np.allclose(res, x - c_metric * b, atol=1e-12)

    c_eucl = float(np.dot(b, x)) / float(np.dot(b, b))  # 2/5
    assert not np.allclose(res, x - c_eucl * b, atol=1e-6)


def test_null_residual_reports_nonzero_surprise():
    """Regression (adversarial pass, HIGH): a probe whose UNEXPLAINED component is
    a metric-null direction (n_inf) must report NONZERO surprise. The reversion
    pseudo-norm returns a false 0 there (n_inf is on the light cone), which would
    admit a fully-unexplained direction as an in-span productive transfer.
    """
    # x = 1 + n_inf; basis = {1}. Projection removes the scalar; residual = n_inf.
    x = _id32() + _n_inf()
    res, nrm = surprise_residual(x, _id32().reshape(32, 1))
    assert np.allclose(res, _n_inf(), atol=1e-12)     # residual is the null n_inf
    assert blade_norm(res) < 1e-9                      # (metric pseudo-norm is 0 here)
    assert nrm > 0.5                                   # definite norm is NOT 0

    src = make_rotor_from_angle(0.5, bivector_idx=7)
    out = dual_operator(x, _id32().reshape(32, 1), [("a0", src, src)])
    assert out["surprise_norm"] > 0.5
    assert out["productive"] is False


def test_null_pair_projection_is_metric_exact():
    """{n_o, n_inf} spans a NON-degenerate hyperbolic plane — admitted, and the
    projection is metric-exact: x = n_o + e1 projects out exactly the n_o
    component (residual == e1) via the off-diagonal gram [[0,-1],[-1,0]]. A
    Euclidean projection would not leave exactly e1.
    """
    B = np.column_stack([_n_o(), _n_inf()])
    x = _n_o() + _vec(1)
    res, _nrm = surprise_residual(x, B)  # must not raise
    assert np.allclose(res, _vec(1), atol=1e-12)


def test_five_vector_branch_metric_and_refusal():
    """The 5-vector eta-metric branch: metric-vs-Euclidean divergence + null refusal."""
    b = np.array([2.0, 0.0, 0.0, 0.0, 1.0])  # 2*e1 + e5, eta-norm^2 = 4 - 1 = 3
    x = np.array([1.0, 0.0, 0.0, 0.0, 0.0])
    res, _nrm = surprise_residual(x, b.reshape(5, 1))
    c_metric = float(x @ (_ETA5 @ b)) / float(b @ (_ETA5 @ b))  # 2/3
    assert np.allclose(res, x - c_metric * b, atol=1e-12)
    c_eucl = float(np.dot(b, x)) / float(np.dot(b, b))  # 2/5
    assert not np.allclose(res, x - c_eucl * b, atol=1e-6)

    null5 = np.array([0.0, 0.0, 0.0, 1.0, 1.0])  # e4 + e5, eta-norm^2 = 1 - 1 = 0
    with pytest.raises(SurpriseResidualError):
        surprise_residual(x, null5.reshape(5, 1))


def test_lone_null_column_refused():
    """A lone n_o direction (self-inner 0, no reciprocal) is unprojectable."""
    with pytest.raises(SurpriseResidualError) as ei:
        surprise_residual(make_rotor_from_angle(0.3), _n_o().reshape(32, 1))
    assert ei.value.reason == "degenerate_metric_span"
    assert 0 in ei.value.disclosure["null_columns"]


def test_combination_degenerate_span_disclosed():
    """A metric-degenerate span whose columns are each NON-null (a null
    combination) is still refused, and the disclosure names the degenerate
    direction even though null_columns is empty."""
    b1 = _vec(1)                    # e1, <b1,b1> = 1
    b2 = _vec(1) + _n_inf()         # e1 + (e4+e5), <b2,b2> = 1 (non-null)
    B = np.column_stack([b1, b2])
    with pytest.raises(SurpriseResidualError) as ei:
        surprise_residual(make_rotor_from_angle(0.3), B)
    assert ei.value.disclosure["null_columns"] == []       # neither diagonal is 0
    assert len(ei.value.disclosure["degenerate_combo"]) == 2  # but the combo is named


# --- REGRESSION / CONTAINMENT GUARDS (metric-agnostic) -----------------------

def test_null_pair_admitted_not_refused():
    """The non-degenerate null pair {n_o, n_inf} must not trip the fail-closed path."""
    B = np.column_stack([_n_o(), _n_inf()])
    surprise_residual(_vec(1), B)  # must not raise


def test_redundant_nonnull_basis_admitted():
    """[1, 1] is rank-deficient but non-null: admitted (project onto span{1})."""
    B = np.column_stack([_id32(), _id32()])
    x = make_rotor_from_angle(0.6, bivector_idx=7)
    res, _nrm = surprise_residual(x, B)  # must not raise
    expected = x - float(x[0]) * _id32()  # x minus its scalar (grade-0) part
    assert np.allclose(res, expected, atol=1e-9)


def test_in_span_zero_residual():
    b0, b1 = _id32(), make_rotor_from_angle(0.5, bivector_idx=7)
    B = np.column_stack([b0, b1])
    _res, nrm = surprise_residual(b1, B)  # b1 lies in the span
    assert nrm < 1e-9


def test_out_of_span_partial_and_full_energy():
    # Full: a pure bivector is cga-orthogonal to span{1} -> residual == x.
    x = grade_project(make_rotor_from_angle(0.7, bivector_idx=7), 2)
    res, nrm = surprise_residual(x, _id32().reshape(32, 1))
    assert np.allclose(res, x, atol=1e-12)
    assert abs(nrm - float(np.linalg.norm(x))) < 1e-12
    # Partial: a rotor has an in-span scalar and out-of-span bivector, so the
    # residual is a STRICT subset and its surprise is strictly between 0 and full.
    r = make_rotor_from_angle(0.7, bivector_idx=7)
    _res2, nrm2 = surprise_residual(r, _id32().reshape(32, 1))
    assert 1e-9 < nrm2 < float(np.linalg.norm(r)) - 1e-9


def test_even_input_even_residual():
    """Grade-support containment: an even (grade 0+2) input yields an even residual."""
    x = make_rotor_from_angle(0.7, bivector_idx=7)
    B = np.column_stack([_id32(), make_rotor_from_angle(0.3, bivector_idx=9)])
    res, _nrm = surprise_residual(x, B)
    for k in (1, 3, 5):
        assert float(np.linalg.norm(grade_project(res, k))) < 1e-9


def test_determinism():
    x = make_rotor_from_angle(0.9, bivector_idx=8)
    B = np.column_stack([_id32(), make_rotor_from_angle(0.4, bivector_idx=7)])
    r1, n1 = surprise_residual(x, B)
    r2, n2 = surprise_residual(x, B)
    assert n1 == n2 and np.array_equal(r1, r2)


# --- reconciled productivity polarity ---------------------------------------

def test_dual_operator_productive_requires_low_surprise():
    """Same analog (identical -> ~0 Procrustes), surprise alone flips productivity.

    Low surprise (query in span) -> productive transfer. High surprise (query far
    outside span) -> NOT productive (a discovery signal, not a transfer).
    """
    src = make_rotor_from_angle(0.5, bivector_idx=7)
    analogs = [("a0", src, src)]  # identical: structural match, low Procrustes

    out_low = dual_operator(src, np.column_stack([_id32(), src]), analogs)
    x_high = grade_project(make_rotor_from_angle(1.2, bivector_idx=11), 2)
    out_high = dual_operator(x_high, _id32().reshape(32, 1), analogs)

    # identical analog -> identical (low) Procrustes residual for both
    assert out_low["procrustes_residual"] == out_high["procrustes_residual"]
    assert out_low["procrustes_residual"] <= 0.35
    assert out_low["surprise_norm"] < 0.35
    assert out_high["surprise_norm"] > 0.35
    assert out_low["productive"] is True
    assert out_high["productive"] is False
