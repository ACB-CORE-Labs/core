"""ADR-0244 §2.1/§4a — operator-preservation identity manifold primitive.

Pins the falsifiable claims of the metric-exact operator-preservation geometry
(governance annotation item 12): a versor's action on the value axes reveals
whether it PRESERVES the identity subspace. Subspace leakage catches tilt toward
alien dimensions (e4/e5); signed self-alignment catches in-subspace inversion.
Both are required and non-redundant.

All numbers here were pre-verified against ``algebra.cl41`` before implementation
(see the ADR-0244 D4 plan progress log, 2026-07-17 operator-preservation entry).
"""

from __future__ import annotations

import numpy as np
import pytest

from algebra.cl41 import N_COMPONENTS, basis_vector, grade_start, grade_count
from core.physics.identity_manifold import (
    CONDITION_BOUND,
    IdentityManifoldGeometry,
    ManifoldConditioningError,
    euclidean_norm,
    gram_matrix,
    lift_axis,
    sandwich,
    subspace_project,
)

# Default identity pack axes (packs/identity/default_general_v1.json): the three
# spatial basis directions truthfulness/coherence/reverence.
DEFAULT_DIRECTIONS = ([1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0])

# Grade-2 bivector component indices (grade-2 block starts at grade_start(2)=6;
# combinations(range(5),2) order → (0,1)=e12=6, (0,3)=e14=8, (0,4)=e15=9).
_E12, _E14, _E15 = 6, 8, 9


def _spatial_rotor(biv_idx: int, theta: float) -> np.ndarray:
    """Unit rotor cos(θ/2) + sin(θ/2)·B for a B²=−1 (spatial) plane."""
    R = np.zeros(N_COMPONENTS, dtype=np.float64)
    R[0] = np.cos(theta / 2.0)
    R[biv_idx] = np.sin(theta / 2.0)
    return R


def _boost(biv_idx: int, theta: float) -> np.ndarray:
    """Unit boost cosh(θ/2) + sinh(θ/2)·B for a B²=+1 (e5-containing) plane."""
    R = np.zeros(N_COMPONENTS, dtype=np.float64)
    R[0] = np.cosh(theta / 2.0)
    R[biv_idx] = np.sinh(theta / 2.0)
    return R


def _identity_versor() -> np.ndarray:
    R = np.zeros(N_COMPONENTS, dtype=np.float64)
    R[0] = 1.0
    return R


def _geom() -> IdentityManifoldGeometry:
    return IdentityManifoldGeometry.from_directions(DEFAULT_DIRECTIONS)


# --- lift_axis ------------------------------------------------------------

def test_lift_axis_places_components_at_grade1_slots():
    psi = lift_axis([1.0, 0.0, 0.0])
    assert psi.dtype == np.float64
    assert psi.shape == (N_COMPONENTS,)
    # e1 lives at component index 1 (basis_vector(0)); everything else zero.
    np.testing.assert_array_equal(psi, basis_vector(0).astype(np.float64))
    assert psi[1] == 1.0
    assert np.count_nonzero(psi) == 1


def test_lift_axis_is_pure_grade1():
    psi = lift_axis([0.6, 0.8, 0.0])
    g1_start, g1_count = grade_start(1), grade_count(1)
    grade1_energy = float(np.sum(psi[g1_start : g1_start + g1_count] ** 2))
    total_energy = float(np.sum(psi**2))
    assert grade1_energy == pytest.approx(total_energy)  # all energy in grade 1
    assert psi[1] == pytest.approx(0.6)
    assert psi[2] == pytest.approx(0.8)


def test_lift_axis_rejects_non_r3():
    with pytest.raises(ValueError):
        lift_axis([1.0, 0.0])


# --- gram_matrix ----------------------------------------------------------

def test_gram_of_default_pack_is_identity():
    geom = _geom()
    np.testing.assert_allclose(geom.gram, np.eye(3), atol=1e-12)
    np.testing.assert_allclose(geom.gram_inv, np.eye(3), atol=1e-12)


def test_gram_is_symmetric():
    axes = [lift_axis(d) for d in ([0.6, 0.8, 0.0], [0.0, 0.6, 0.8], [0.8, 0.0, 0.6])]
    G = gram_matrix(axes)
    np.testing.assert_allclose(G, G.T, atol=1e-12)


def test_near_degenerate_axes_raise_conditioning_error():
    # Two almost-parallel axes → ill-conditioned Gram → fail closed.
    axes = [
        lift_axis([1.0, 0.0, 0.0]),
        lift_axis([1.0, 1e-7, 0.0]),
        lift_axis([0.0, 0.0, 1.0]),
    ]
    with pytest.raises(ManifoldConditioningError):
        gram_matrix(axes)


def test_empty_axes_rejected():
    with pytest.raises(ValueError):
        gram_matrix([])


# --- subspace_project -----------------------------------------------------

def test_projection_is_idempotent():
    geom = _geom()
    rng = np.random.default_rng(0)
    x = rng.standard_normal(N_COMPONENTS)
    p1 = geom.project(x)
    p2 = geom.project(p1)
    np.testing.assert_allclose(p2, p1, atol=1e-12)


def test_in_subspace_vector_is_fixed_by_projection():
    geom = _geom()
    x = lift_axis([0.3, -0.5, 0.7])  # lives in span(e1,e2,e3)
    np.testing.assert_allclose(geom.project(x), x, atol=1e-12)


def test_out_of_subspace_grade1_projects_to_zero():
    geom = _geom()
    e4 = basis_vector(3).astype(np.float64)  # e4 ∉ span(e1,e2,e3)
    assert euclidean_norm(geom.project(e4)) < 1e-12


def test_standalone_project_matches_geometry_method():
    geom = _geom()
    rng = np.random.default_rng(1)
    x = rng.standard_normal(N_COMPONENTS)
    np.testing.assert_allclose(
        subspace_project(x, geom.axes_psi, geom.gram_inv), geom.project(x), atol=1e-15
    )


def test_condition_bound_is_the_documented_1e5():
    assert CONDITION_BOUND == pytest.approx(1e5)


# --- sandwich -------------------------------------------------------------

def test_sandwich_identity_leaves_axis_unchanged():
    e1 = basis_vector(0).astype(np.float64)
    np.testing.assert_allclose(sandwich(_identity_versor(), e1), e1, atol=1e-12)


def test_sandwich_preserves_norm_for_versor():
    e1 = basis_vector(0).astype(np.float64)
    R = _spatial_rotor(_E14, 0.9)
    rotated = sandwich(R, e1)
    assert euclidean_norm(rotated) == pytest.approx(1.0, abs=1e-9)


# --- axis_response: the core operator-preservation claims -----------------

def test_identity_versor_perfectly_preserves():
    geom = _geom()
    leakage, self_align = geom.axis_response(_identity_versor())
    assert max(leakage) < 1e-12
    for a in self_align:
        assert a == pytest.approx(1.0, abs=1e-9)


def test_rotation_within_value_plane_does_not_leak():
    # e12 rotation keeps every value axis inside span(e1,e2,e3).
    geom = _geom()
    leakage, _ = geom.axis_response(_spatial_rotor(_E12, 0.5))
    assert max(leakage) < 1e-9


def test_tilt_toward_e4_leaks():
    # e14 rotation tilts the e1 axis toward e4 (out of the value subspace).
    geom = _geom()
    leakage, _ = geom.axis_response(_spatial_rotor(_E14, 0.5))
    assert leakage[0] > 0.05  # e1 axis leaks
    assert geom.leakage_rms(_spatial_rotor(_E14, 0.5)) > 0.05


def test_boost_toward_e5_leaks():
    # e15 boost tilts the e1 axis toward e5 — the Euclidean norm catches this
    # even though the indefinite Cl(4,1) norm would (mis)count e5 as negative.
    geom = _geom()
    leakage, _ = geom.axis_response(_boost(_E15, 0.5))
    assert leakage[0] > 0.05


def test_larger_tilt_leaks_more():
    geom = _geom()
    small = geom.leakage_rms(_spatial_rotor(_E14, 0.5))
    large = geom.leakage_rms(_spatial_rotor(_E14, 1.2))
    assert large > small


def test_in_subspace_inversion_caught_by_self_alignment_not_leakage():
    # π rotation in e12 sends e1 → −e1: still inside span(e1,e2,e3) (leakage 0),
    # but inverted. Only the signed self-alignment catches it.
    geom = _geom()
    leakage, self_align = geom.axis_response(_spatial_rotor(_E12, np.pi))
    assert leakage[0] < 1e-9              # subspace-rejection blind to inversion
    assert self_align[0] < -0.9          # signed orientation catches it


def test_self_alignment_is_signed_not_absolute():
    # A partial rotation gives a self-alignment strictly between the inverted
    # (−1) and preserved (+1) extremes; never collapsed to |·|.
    geom = _geom()
    _, self_align = geom.axis_response(_spatial_rotor(_E12, 2.4))
    assert -1.0 <= self_align[0] < 0.0   # past 90°, genuinely negative


# --- geometry object contract + determinism -------------------------------

def test_geometry_is_frozen():
    geom = _geom()
    with pytest.raises((AttributeError, TypeError)):
        geom.gram_inv = np.eye(3)  # type: ignore[misc]


def test_from_directions_propagates_conditioning_error():
    with pytest.raises(ManifoldConditioningError):
        IdentityManifoldGeometry.from_directions(
            ([1.0, 0.0, 0.0], [1.0, 1e-7, 0.0], [0.0, 0.0, 1.0])
        )


def test_axis_response_is_deterministic():
    geom = _geom()
    R = _spatial_rotor(_E14, 0.7)
    first = geom.axis_response(R)
    second = geom.axis_response(R)
    assert first == second  # bit-exact repeat (pure f64, no randomness)
