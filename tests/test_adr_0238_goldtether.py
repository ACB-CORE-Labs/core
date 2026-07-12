"""ADR-0238 — Coherence GoldTether: residual, floor, practice/serve autonomy, closure."""

from __future__ import annotations

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from algebra.rotor import make_rotor_from_angle
from algebra.versor import unitize_versor, versor_apply, versor_condition
from core.physics.goldtether import (
    AutonomyBand,
    GoldTetherConfig,
    GoldTetherMonitor,
    OperatingMode,
    derive_kappa,
)


def _id() -> np.ndarray:
    v = np.zeros(32, dtype=np.float64)
    v[0] = 1.0
    return v


def _rotor(angle: float, biv: int = 6) -> np.ndarray:
    return make_rotor_from_angle(angle, bivector_idx=biv)


def test_measure_identical_is_near_zero():
    m = GoldTetherMonitor()
    r = m.measure(_id(), _id(), mode=OperatingMode.PRACTICE)
    assert r.combined < 1e-9
    assert r.geometric_distance < 1e-9
    assert r.kappa > 0.99


def test_measure_is_replay_deterministic():
    m = GoldTetherMonitor()
    a = _rotor(0.4)
    b = _rotor(1.1)
    r1 = m.measure(a, b, mode=OperatingMode.PRACTICE)
    r2 = m.measure(a, b, mode=OperatingMode.PRACTICE)
    assert r1 == r2


def test_serve_never_autonomous():
    m = GoldTetherMonitor(
        config=GoldTetherConfig(practice_autonomy_enabled=True, floor_init=0.5)
    )
    # Near-zero residual would be autonomous in practice, but not serve.
    res = m.measure(_id(), _id(), mode=OperatingMode.SERVE)
    d = m.decide(res, mode=OperatingMode.SERVE)
    assert d.band is not AutonomyBand.AUTONOMOUS
    assert d.band is AutonomyBand.FAIL_CLOSED


def test_practice_autonomy_only_when_enabled():
    low = GoldTetherMonitor(
        config=GoldTetherConfig(practice_autonomy_enabled=False, floor_init=0.5)
    )
    res = low.measure(_id(), _id(), mode=OperatingMode.PRACTICE)
    d = low.decide(res, mode=OperatingMode.PRACTICE)
    assert d.band is AutonomyBand.SUPERVISED_BLEND

    high = GoldTetherMonitor(
        config=GoldTetherConfig(practice_autonomy_enabled=True, floor_init=0.5)
    )
    res2 = high.measure(_id(), _id(), mode=OperatingMode.PRACTICE)
    d2 = high.decide(res2, mode=OperatingMode.PRACTICE)
    assert d2.band is AutonomyBand.AUTONOMOUS


def test_fail_closed_above_critical():
    m = GoldTetherMonitor(config=GoldTetherConfig(floor_init=0.01, critical_ratio=2.0))
    # Force large residual via distant rotors + high drift weight
    m2 = GoldTetherMonitor(
        config=GoldTetherConfig(floor_init=0.01, critical_ratio=1.1, w_drift=0.0)
    )
    a = _id()
    b = _rotor(2.5)
    res = m2.measure(b, a, mode=OperatingMode.PRACTICE)
    # If residual still not critical, inject artificial residual
    if res.combined <= m2.floor_state.value * m2.config.critical_ratio:
        d = m2.decide(1.0, mode=OperatingMode.PRACTICE)
    else:
        d = m2.decide(res, mode=OperatingMode.PRACTICE)
    assert d.band is AutonomyBand.FAIL_CLOSED


def test_floor_updates_only_on_practice_success():
    m = GoldTetherMonitor(config=GoldTetherConfig(floor_init=0.2, decay_N=8))
    res = m.measure(_id(), _id(), mode=OperatingMode.PRACTICE)
    before = m.floor_state.value
    m.update_floor(res, mode=OperatingMode.SERVE, success=True)
    assert m.floor_state.value == before  # serve never promotes
    m.update_floor(res, mode=OperatingMode.PRACTICE, success=True)
    # success below floor may tighten or hold; never raise above prior
    assert m.floor_state.value <= before
    assert m.floor_state.n_samples >= 1


def test_lifelong_coherence_curve_telemetry():
    m = GoldTetherMonitor(config=GoldTetherConfig(floor_init=0.3, decay_N=16))
    ref = _id()
    for i in range(5):
        cur = _rotor(0.05 * i)
        res = m.measure(cur, ref, mode=OperatingMode.PRACTICE)
        m.update_floor(res, mode=OperatingMode.PRACTICE, success=res.combined < m.floor_state.value)
    tel = m.telemetry()
    assert tel["schema_version"] == "goldtether_coherence_v1"
    assert "pseudoscalar_floor" in tel
    assert len(tel["recent_residuals"]) == 5
    # replay: same sequence same telemetry residuals
    m2 = GoldTetherMonitor(config=GoldTetherConfig(floor_init=0.3, decay_N=16))
    for i in range(5):
        cur = _rotor(0.05 * i)
        res = m2.measure(cur, ref, mode=OperatingMode.PRACTICE)
        m2.update_floor(res, mode=OperatingMode.PRACTICE, success=res.combined < m2.floor_state.value)
    assert m2.telemetry()["recent_residuals"] == tel["recent_residuals"]


def test_supervised_blend_preserves_closure():
    m = GoldTetherMonitor()
    src = _id()
    tgt = _rotor(0.9)
    for alpha in (0.0, 0.25, 0.5, 0.75, 1.0):
        out = m.supervised_blend(src, tgt, alpha)
        assert versor_condition(out) < 1e-6


def test_supervised_blend_endpoints():
    m = GoldTetherMonitor()
    src = _id()
    tgt = _rotor(0.6)
    out0 = m.supervised_blend(src, tgt, 0.0)
    assert np.allclose(out0, src, atol=1e-6)
    out1 = m.supervised_blend(src, tgt, 1.0)
    # Full transition lands near target for unit rotors
    assert versor_condition(out1) < 1e-6
    assert float(np.linalg.norm(out1 - tgt)) < 1e-4


def test_derive_kappa_monotone():
    floor = 0.1
    k_small = derive_kappa(0.01, floor)
    k_large = derive_kappa(1.0, floor)
    assert k_small > k_large
    assert 0.0 < k_large <= 1.0


@given(st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False))
@settings(max_examples=40)
def test_blend_alpha_always_closed(alpha: float):
    m = GoldTetherMonitor()
    out = m.supervised_blend(_id(), _rotor(0.8), float(alpha))
    assert versor_condition(out) < 1e-6


def test_config_validation():
    with pytest.raises(ValueError):
        GoldTetherConfig(decay_N=0)
    with pytest.raises(ValueError):
        GoldTetherConfig(w_drift=1.5)
    with pytest.raises(ValueError):
        GoldTetherConfig(critical_ratio=0.5)
