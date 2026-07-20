"""ADR-0244 §2.2/§4a — operator-preservation identity gate (fail-closed).

Pins the wave-field path on ``IdentityCheck``: MissingWaveStateError on absent
ψ, fail-closed validation of a malformed versor, the operator-preservation
score, the ``boundary_ids`` intersection predicate, and admit-or-abstain
``C_id`` (``IdentityGateRefusal``). Scalar-L2 dual-mode is excised.
"""

from __future__ import annotations

import numpy as np
import pytest

from algebra.cl41 import N_COMPONENTS
from core.physics.identity import (
    IdentityCheck,
    IdentityGateRefusal,
    IdentityManifold,
    IdentityScore,
    MissingWaveStateError,
    ValueAxis,
)

_E12, _E14 = 6, 8  # e12, e14 bivector component indices


def _spatial_rotor(biv_idx: int, theta: float) -> np.ndarray:
    R = np.zeros(N_COMPONENTS, dtype=np.float32)
    R[0] = np.cos(theta / 2.0)
    R[biv_idx] = np.sin(theta / 2.0)
    return R


def _identity_versor() -> np.ndarray:
    R = np.zeros(N_COMPONENTS, dtype=np.float32)
    R[0] = 1.0
    return R


def _wave_manifold(threshold: float = 0.45, boundary_ids=frozenset()) -> IdentityManifold:
    axes = (
        ValueAxis(name="truthfulness", direction=(1.0, 0.0, 0.0)),
        ValueAxis(name="coherence", direction=(0.0, 1.0, 0.0)),
        ValueAxis(name="reverence", direction=(0.0, 0.0, 1.0)),
    )
    return IdentityManifold(
        value_axes=axes, boundary_ids=boundary_ids, alignment_threshold=threshold
    )


class _Traj:
    trajectory_id = "t-wave"
    total_coherence_delta = 0.0
    frames = ()


# --- fail-closed absent wave ------------------------------------------------

def test_absent_wave_field_raises_missing_wave_state():
    with pytest.raises(MissingWaveStateError, match="wave_field"):
        IdentityCheck().check(_Traj(), _wave_manifold())


def test_wave_field_activates_operator_preservation_path():
    score = IdentityCheck().check(
        _Traj(), _wave_manifold(), wave_field=_identity_versor()
    )
    assert score.wave_mode_active is True


# --- the operator-preservation score --------------------------------------

def test_identity_versor_scores_aligned_and_unflagged():
    score = IdentityCheck().check(
        _Traj(), _wave_manifold(), wave_field=_identity_versor()
    )
    assert score.leakage_norm < 1e-6
    assert score.min_self_alignment == pytest.approx(1.0, abs=1e-6)
    assert score.score == pytest.approx(1.0, abs=1e-6)
    assert score.flagged is False
    assert score.deviation_axes == frozenset()


def test_tilt_toward_alien_dimension_raises_leakage_lowers_score():
    check = IdentityCheck()
    manifold = _wave_manifold()
    small = check.check(_Traj(), manifold, wave_field=_spatial_rotor(_E14, 0.5))
    large = check.check(_Traj(), manifold, wave_field=_spatial_rotor(_E14, 1.2))
    assert small.leakage_norm > 0.0
    assert large.leakage_norm > small.leakage_norm
    assert large.score < small.score < 1.0


def test_in_subspace_inversion_is_flagged_via_orientation():
    # π rotation in e12 sends e1 → −e1 (stays in the value subspace, leakage ~0),
    # but inverts it — caught only by the signed self-alignment.
    score = IdentityCheck().check(
        _Traj(), _wave_manifold(), wave_field=_spatial_rotor(_E12, np.pi)
    )
    assert score.leakage_norm < 1e-5
    assert score.min_self_alignment < -0.9
    assert score.flagged is True
    assert "truthfulness" in score.deviation_axes


# --- fail-closed validation (malformed wave field never falls back) -------

def test_nonfinite_wave_field_raises_not_silent_legacy():
    bad = _identity_versor()
    bad[3] = np.nan
    with pytest.raises(ValueError, match="non-finite"):
        IdentityCheck().check(_Traj(), _wave_manifold(), wave_field=bad)


def test_wrong_shape_wave_field_raises():
    with pytest.raises(ValueError, match="shape"):
        IdentityCheck().check(
            _Traj(), _wave_manifold(), wave_field=np.ones(16, dtype=np.float32)
        )


# --- boundary_ids intersection predicate ----------------------------------

def test_boundary_violation_in_manifold_flags_and_records():
    manifold = _wave_manifold(boundary_ids=frozenset({"no_identity_override"}))
    score = IdentityCheck().check(
        _Traj(),
        manifold,
        wave_field=_identity_versor(),
        violated_boundary_ids=frozenset({"no_identity_override", "unrelated"}),
    )
    assert score.boundary_violations == frozenset({"no_identity_override"})
    assert score.flagged is True  # aligned versor, but a committed boundary fell


def test_boundary_violation_outside_manifold_is_ignored():
    manifold = _wave_manifold(boundary_ids=frozenset({"no_identity_override"}))
    score = IdentityCheck().check(
        _Traj(),
        manifold,
        wave_field=_identity_versor(),
        violated_boundary_ids=frozenset({"some_other_boundary"}),
    )
    assert score.boundary_violations == frozenset()
    assert score.flagged is False


def test_boundary_predicate_on_wave_path_without_axis_leakage():
    manifold = _wave_manifold(boundary_ids=frozenset({"no_identity_override"}))
    score = IdentityCheck().check(
        _Traj(),
        manifold,
        wave_field=_identity_versor(),
        violated_boundary_ids=frozenset({"no_identity_override"}),
    )
    assert score.wave_mode_active is True
    assert score.boundary_violations == frozenset({"no_identity_override"})
    assert score.flagged is True


# --- C_id: admit-or-abstain + IdentityGateRefusal -------------------------

def test_conjugate_correct_passes_clean_score_through():
    score = IdentityCheck().check(
        _Traj(), _wave_manifold(), wave_field=_identity_versor()
    )
    assert IdentityCheck.conjugate_correct(score, refuse=True) is score


def test_conjugate_correct_abstains_on_violation():
    score = IdentityCheck().check(
        _Traj(), _wave_manifold(), wave_field=_spatial_rotor(_E12, np.pi)
    )
    with pytest.raises(IdentityGateRefusal):
        IdentityCheck.conjugate_correct(score, refuse=True)


def test_conjugate_correct_never_refuses_when_flag_off():
    score = IdentityCheck().check(
        _Traj(), _wave_manifold(), wave_field=_spatial_rotor(_E12, np.pi)
    )
    # refuse defaults False → admit-or-abstain gate does not fire; no mutation.
    assert IdentityCheck.conjugate_correct(score) is score


# --- would_violate extensions + legacy back-compat ------------------------

def test_would_violate_catches_boundary_and_inversion():
    inverted = IdentityScore(
        score=0.9, flagged=False, deviation_axes=frozenset(), trajectory_id="t",
        wave_mode_active=True, min_self_alignment=-1.0,
    )
    assert IdentityCheck.would_violate(inverted) is True
    breach = IdentityScore(
        score=1.0, flagged=False, deviation_axes=frozenset(), trajectory_id="t",
        boundary_violations=frozenset({"no_identity_override"}),
    )
    assert IdentityCheck.would_violate(breach) is True


def test_identity_score_constructs_with_geometric_defaults():
    score = IdentityScore(
        score=0.7, flagged=False, deviation_axes=frozenset(), trajectory_id="t"
    )
    # Wave path is the only path; default wave_mode_active is True.
    assert score.wave_mode_active is True
    assert score.boundary_violations == frozenset()
    assert IdentityCheck.would_violate(score) is False


def test_wave_score_is_deterministic():
    check = IdentityCheck()
    manifold = _wave_manifold()
    R = _spatial_rotor(_E14, 0.7)
    a = check.check(_Traj(), manifold, wave_field=R)
    b = check.check(_Traj(), manifold, wave_field=R)
    assert (a.score, a.leakage_norm, a.min_self_alignment) == (
        b.score, b.leakage_norm, b.min_self_alignment
    )
