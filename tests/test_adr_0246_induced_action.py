"""ADR-0246 Ring-1 §3 — pure induced-action / d_orth / d_stab / typed-residual pins.

These pin the canonical primitives promoted from the slice-0 diagnostic prototype
into ``core.physics.identity_manifold`` (induced action A(F), orthogonality defect
d_orth, typed residual energy) and the new ``core.physics.identity_action`` (the
locked singleton stabilizer H_id={I} and the stabilizer defect d_stab).

Ground truth is the brief §3.1–§3.3/§3.6 and §6.1 constructions: identity versor →
A=I; an in-span rotation is a G-isometry (d_orth≈0) but NOT the identity action
(d_stab>0); an in-span permutation/inversion is leakage-invisible but d_stab-visible;
an e4 tilt fires only the null/conformal channel; an e5 boost fires the boost channel
and is non-isometric (d_orth>0). The primitives are pure (algebra-only, off-serving).
"""

from __future__ import annotations

import numpy as np
import pytest

from algebra.cl41 import N_COMPONENTS, basis_vector
from core.physics.identity_manifold import (
    IdentityManifoldGeometry,
    E4_GRADE1_INDEX,
    E5_GRADE1_INDEX,
)
from core.physics.identity_action import (
    IdentityStabilizer,
    stabilizer_defect,
    stabilizer_defect_for_versor,
)

# grade-2 bivector plane indices (grade-2 block starts at 6)
_E12, _E13, _E14, _E15, _E23, _E24, _E25 = 6, 7, 8, 9, 10, 11, 12


def _rotor(biv: int, theta: float) -> np.ndarray:
    r = np.zeros(N_COMPONENTS, dtype=np.float64)
    r[0] = np.cos(theta / 2.0)
    r[biv] = np.sin(theta / 2.0)
    return r


def _boost(biv: int, theta: float) -> np.ndarray:
    r = np.zeros(N_COMPONENTS, dtype=np.float64)
    r[0] = np.cosh(theta / 2.0)
    r[biv] = np.sinh(theta / 2.0)
    return r


def _identity_versor() -> np.ndarray:
    v = np.zeros(N_COMPONENTS, dtype=np.float64)
    v[0] = 1.0
    return v


@pytest.fixture(scope="module")
def geometry() -> IdentityManifoldGeometry:
    # default pack: span(e1,e2,e3), Gram = I3
    return IdentityManifoldGeometry.from_directions(
        ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))
    )


def test_blade_index_constants_match_algebra():
    assert basis_vector(3)[E4_GRADE1_INDEX] == 1.0  # e4
    assert basis_vector(4)[E5_GRADE1_INDEX] == 1.0  # e5
    assert np.count_nonzero(basis_vector(3)) == 1
    assert np.count_nonzero(basis_vector(4)) == 1


def test_identity_versor_action_is_identity(geometry):
    action = geometry.induced_action(_identity_versor())
    assert np.allclose(action, np.eye(3), atol=1e-12)
    assert geometry.orthogonality_defect(_identity_versor()) < 1e-12
    assert stabilizer_defect_for_versor(geometry, _identity_versor()) < 1e-12


def test_inplane_rotation_is_isometry_but_not_identity_action(geometry):
    theta = 0.4
    versor = _rotor(_E12, theta)
    action = geometry.induced_action(versor)
    # e12 rotor rotates the e1/e2 plane; e3 fixed.
    assert action[2, 2] == pytest.approx(1.0, abs=1e-9)
    assert abs(action[0, 0]) == pytest.approx(abs(np.cos(theta)), abs=1e-6)
    assert geometry.orthogonality_defect(versor) < 1e-6  # G-isometry
    assert stabilizer_defect_for_versor(geometry, versor) > 0.05  # not H_id={I}


def test_permutation_and_inversion_are_leakage_invisible_but_dstab_visible(geometry):
    for versor in (_rotor(_E12, np.pi / 2.0), _rotor(_E12, np.pi)):
        leak, _ = geometry.axis_response(versor)
        assert max(leak) < 1e-6
        assert stabilizer_defect_for_versor(geometry, versor) > 0.05


def test_e4_tilt_fires_only_null_conformal_channel(geometry):
    channels = geometry.typed_residual_energy(_rotor(_E14, 1.2))
    assert channels["null_or_conformal"] > 0.05
    assert channels["boost_like"] == pytest.approx(0.0, abs=1e-12)
    assert channels["unclassified"] < 1e-9


def test_e5_boost_fires_boost_channel_and_is_non_isometric(geometry):
    versor = _boost(_E15, 1.0)
    channels = geometry.typed_residual_energy(versor)
    assert channels["boost_like"] > 0.05
    assert channels["null_or_conformal"] == pytest.approx(0.0, abs=1e-12)
    assert geometry.orthogonality_defect(versor) > 0.05  # boost not a G-isometry


def test_spatial_foreign_channel_is_zero_for_default_pack_by_construction():
    """Resolves the open uncertainty from the Fable/Opus handoff notes: is
    ``spatial_foreign`` structurally broken? No — for the DEFAULT 3-axis pack
    (support = e1,e2,e3, i.e. the full spatial grade-1 block), the rejection
    ``rotated - project(rotated)`` is by construction orthogonal to e1/e2/e3, so
    this channel is TAUTOLOGICALLY zero — there is no "spatial but outside
    support" direction left when the support IS all of span(e1,e2,e3).
    """
    geom3 = IdentityManifoldGeometry.from_directions(
        ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))
    )
    for versor in (_rotor(_E14, 1.3), _boost(_E25, 0.9), _rotor(_E12, 2.0)):
        assert geom3.typed_residual_energy(versor)["spatial_foreign"] == pytest.approx(
            0.0, abs=1e-12
        )


def test_spatial_foreign_channel_fires_for_reduced_support_pack():
    """A pack whose declared axes do NOT span all of e1/e2/e3 (here: only
    e1/e2) has a genuine "spatial but outside support" direction (e3), and a
    versor tilting an axis toward it must register nonzero ``spatial_foreign``
    — confirming the channel is correct in general, not merely inert.
    """
    geom2 = IdentityManifoldGeometry.from_directions(((1.0, 0.0, 0.0), (0.0, 1.0, 0.0)))
    tilt_toward_e3 = _rotor(_E13, 1.0)  # e13 tilts axis e1 toward e3 (out-of-support)
    channels = geom2.typed_residual_energy(tilt_toward_e3)
    assert channels["spatial_foreign"] > 0.05
    assert channels["null_or_conformal"] == pytest.approx(0.0, abs=1e-12)
    assert channels["boost_like"] == pytest.approx(0.0, abs=1e-12)


def test_typed_residual_energy_fractions_are_bounded_and_clean(geometry):
    for versor in (_rotor(_E14, 0.7), _boost(_E25, 0.6), _rotor(_E12, 0.3)):
        ch = geometry.typed_residual_energy(versor)
        total = (
            ch["null_or_conformal"]
            + ch["boost_like"]
            + ch["spatial_foreign"]
            + ch["unclassified"]
        )
        assert 0.0 <= total <= 1.0 + 1e-9
        # sandwich output of a versor stays grade-1: no unclassified contamination
        assert ch["unclassified"] < 1e-9


def test_stabilizer_is_singleton_identity_by_default(geometry):
    stab = IdentityStabilizer.singleton(3)
    assert len(stab.members) == 1
    assert np.allclose(stab.members[0], np.eye(3))
    # d_stab of the identity action is 0; of a rotation, > 0
    eye = np.eye(3)
    assert stabilizer_defect(eye, geometry.gram, stab) < 1e-12
    rot = geometry.induced_action(_rotor(_E12, 0.5))
    assert stabilizer_defect(rot, geometry.gram, stab) > 0.05


def test_stabilizer_defect_g_weighted_reduces_to_frobenius_at_identity_gram(geometry):
    action = geometry.induced_action(_rotor(_E13, 0.35))
    stab = IdentityStabilizer.singleton(3)
    d = stabilizer_defect(action, geometry.gram, stab)
    frob = float(np.linalg.norm(action - np.eye(3), ord="fro"))
    assert d == pytest.approx(frob, abs=1e-9)  # default pack Gram is I3


def test_induced_action_is_deterministic(geometry):
    versor = _boost(_E15, 0.9)
    a1 = geometry.induced_action(versor)
    a2 = geometry.induced_action(versor.copy())
    assert np.array_equal(a1, a2)


def test_primitives_are_pure_offserving():
    import core.physics.identity_manifold as m
    import core.physics.identity_action as a

    for mod in (m, a):
        with open(mod.__file__, encoding="utf-8") as fh:
            src = fh.read()
        assert "chat.runtime" not in src
        assert "import chat" not in src


def test_gate_surface_untouched_by_this_branch():
    from core.config import RuntimeConfig
    from core.physics import identity

    assert RuntimeConfig().identity_wave_gate is False
    assert identity._WAVE_LEAKAGE_BOUND == 0.2126624458513829
