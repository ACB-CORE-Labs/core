"""ADR-0238 — GoldTether residual, floor, autonomy, may_relax_hitl, blend."""

from __future__ import annotations

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from algebra.rotor import make_rotor_from_angle
from algebra.versor import versor_condition
from core.physics.goldtether import (
    AutonomyBand,
    GoldTetherMonitor,
    OperatingMode,
    coherence_residual,
)


def _id() -> np.ndarray:
    v = np.zeros(32, dtype=np.float64)
    v[0] = 1.0
    return v


def test_coherence_residual_nonnegative_and_zero_on_identity():
    assert coherence_residual(_id()) == 0.0
    r = coherence_residual(make_rotor_from_angle(0.5))
    assert r >= 0.0


def test_residual_dual_corrected_and_replay():
    m = GoldTetherMonitor()
    F = make_rotor_from_angle(0.4)
    assert m.residual(F) == m.residual(F)
    assert m.residual(F) == coherence_residual(F)


def test_fail_closed_on_drift():
    m = GoldTetherMonitor(epsilon_drift=1e-9)
    # Inject a non-closed multivector by raw coefficients
    dirty = np.zeros(32, dtype=np.float64)
    dirty[0] = 0.5
    dirty[1] = 0.5
    r, auto = m.update(dirty, epistemic_elevation=True)
    assert r > m.epsilon_drift
    assert auto == 0.0
    assert m.may_relax_hitl() is False


def test_epistemic_elevation_raises_floor_and_autonomy():
    m = GoldTetherMonitor(epsilon_drift=1e-5, floor_step=0.1, autonomy_step=0.1)
    F = _id()
    for _ in range(10):
        m.update(F, epistemic_elevation=True)
    assert m.floor > 0.0
    assert m.autonomy > 0.0
    assert m.autonomy <= m.floor
    assert m.supervised_autonomy_level == m.autonomy


def test_never_autonomy_above_floor():
    m = GoldTetherMonitor(floor_step=0.02, autonomy_step=0.5)
    for _ in range(20):
        m.update(_id(), epistemic_elevation=True)
        assert m.autonomy <= m.floor + 1e-12


def test_may_relax_hitl_thresholds():
    m = GoldTetherMonitor(
        hitl_floor_threshold=0.3,
        hitl_autonomy_threshold=0.2,
        floor_step=0.1,
        autonomy_step=0.1,
    )
    assert m.may_relax_hitl() is False
    for _ in range(20):
        m.update(_id(), epistemic_elevation=True)
    assert m.may_relax_hitl() is True


def test_force_reset():
    m = GoldTetherMonitor()
    m.update(_id(), epistemic_elevation=True)
    m.force_reset()
    assert m.floor == 0.0 and m.autonomy == 0.0 and m.history == []


def test_serve_never_autonomous_band():
    m = GoldTetherMonitor(floor_step=0.2, autonomy_step=0.2, hitl_floor_threshold=0.1, hitl_autonomy_threshold=0.1)
    for _ in range(10):
        m.update(_id(), epistemic_elevation=True)
    d = m.decide(0.0, mode=OperatingMode.SERVE)
    assert d.band is not AutonomyBand.AUTONOMOUS


def test_lifelong_curve_telemetry_replay():
    m1 = GoldTetherMonitor()
    m2 = GoldTetherMonitor()
    for i in range(5):
        F = make_rotor_from_angle(0.01 * i) if i else _id()
        # identity always closed; elevation path
        m1.update(_id(), epistemic_elevation=True)
        m2.update(_id(), epistemic_elevation=True)
    assert m1.telemetry()["history_tail"] == m2.telemetry()["history_tail"]
    assert m1.telemetry()["schema_version"] == "goldtether_coherence_v1"


def test_supervised_blend_closure_and_endpoints():
    m = GoldTetherMonitor()
    src = _id()
    tgt = make_rotor_from_angle(0.6)
    assert np.allclose(m.supervised_blend(src, tgt, 0.0), src)
    assert np.allclose(m.supervised_blend(src, tgt, 1.0), tgt, atol=1e-6)
    mid = m.supervised_blend(src, tgt, 0.5)
    assert versor_condition(mid) < 1e-6


@given(st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False))
@settings(max_examples=30)
def test_blend_property_closed(alpha: float):
    m = GoldTetherMonitor()
    out = m.supervised_blend(_id(), make_rotor_from_angle(0.8), float(alpha))
    assert versor_condition(out) < 1e-6
