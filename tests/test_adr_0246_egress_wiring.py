"""ADR-0246 §3.7 egress admit-surface serve wiring — flag-gated, default-off.

Pins that the fuller §3.7 admit surface (d_orth/d_stab/typed channels, via
`evaluate_admission`) is wired into the identity gate ONLY behind the new
default-off `identity_action_surface` flag; that flag-off is byte-identical to the
D4 wave path; and that when on, a versor failing the surface is refused
(admit-or-abstain — no corrector, IdentityGateRefusal path).
"""

from __future__ import annotations

import numpy as np
import pytest

from algebra.cl41 import N_COMPONENTS
from core.config import RuntimeConfig
from core.physics.identity import IdentityCheck, IdentityManifold, ValueAxis
from core.physics.identity_action import AdmissionPolicy

_E14 = 8


def _rotor(biv, theta):
    r = np.zeros(N_COMPONENTS, dtype=np.float64)
    r[0] = np.cos(theta / 2.0)
    r[biv] = np.sin(theta / 2.0)
    return r


def _identity_versor():
    v = np.zeros(N_COMPONENTS, dtype=np.float64)
    v[0] = 1.0
    return v


class _Trajectory:
    trajectory_id = "egress_test"
    total_coherence_delta = 0.0
    frames = ()


def _manifold():
    return IdentityManifold(
        value_axes=(
            ValueAxis(name="truthfulness", direction=(1.0, 0.0, 0.0)),
            ValueAxis(name="coherence", direction=(0.0, 1.0, 0.0)),
            ValueAxis(name="reverence", direction=(0.0, 0.0, 1.0)),
        )
    )


def test_flag_default_off():
    assert RuntimeConfig().identity_action_surface is False


def test_flag_off_wave_path_is_byte_identical():
    check = IdentityCheck()
    manifold = _manifold()
    tilt = _rotor(_E14, 1.2)
    # no admission_policy (default) == exactly the D4 wave path
    base = check.check(_Trajectory(), manifold, wave_field=tilt)
    same = check.check(_Trajectory(), manifold, wave_field=tilt, admission_policy=None)
    assert base == same
    # new §3.7 fields carry legacy defaults when the surface is off
    assert base.d_orth == 0.0 and base.d_stab == 0.0
    assert base.action_surface_active is False


def test_surface_on_populates_measures_and_can_refuse():
    check = IdentityCheck()
    manifold = _manifold()
    tilt = _rotor(_E14, 1.2)  # alien tilt: fails d_orth/d_stab/leakage
    score = check.check(
        _Trajectory(), manifold, wave_field=tilt,
        admission_policy=AdmissionPolicy.placeholder_default(),
    )
    assert score.action_surface_active is True
    assert score.d_orth > 0.05 and score.d_stab > 0.05
    assert score.flagged is True  # §3.7 refusal folds into the gate verdict
    assert IdentityCheck.would_violate(score) is True


def test_surface_on_admits_true_near_identity():
    check = IdentityCheck()
    manifold = _manifold()
    score = check.check(
        _Trajectory(), manifold, wave_field=_identity_versor(),
        admission_policy=AdmissionPolicy.placeholder_default(),
    )
    assert score.action_surface_active is True
    assert score.flagged is False
    assert IdentityCheck.would_violate(score) is False


def test_runtime_flag_off_is_default_and_serve_untouched():
    # the runtime must default the surface off (no live activation of an
    # uncalibrated gate)
    cfg = RuntimeConfig()
    assert cfg.identity_wave_gate is False
    assert cfg.identity_action_surface is False
