"""ADR-0238 §2.3 / R&D-Revised §2.3 — harmonized GoldTether residual + α=Φ(R).

The prior GoldTether shipped only the drift term and an "earned-autonomy" ramp
found in neither blueprint. This adds the scale-harmonized residual (drift +
distance-to-gold-set), the gold-invariant set (primal seeds), and the
α=Φ(R_gt) constraint-weight control law — composed with the earned-autonomy
ceiling and the serve-never-autonomous rule, so the two mechanisms operate at
their two timescales (lifetime ceiling × per-transition blend) rather than
compete. See `docs/research/third-door-blueprint-fidelity.md` finding #4 (#18).
"""

from __future__ import annotations

import numpy as np
import pytest

from algebra.rotor import make_rotor_from_angle
from algebra.versor import versor_condition
from core.physics.goldtether import GoldTetherMonitor, OperatingMode, coherence_residual


def _id() -> np.ndarray:
    v = np.zeros(32, dtype=np.float64)
    v[0] = 1.0
    return v


# --- gold-invariant set (R&D §5 bootstrapping seeds) -----------------------

def test_primal_gold_seeds():
    m = GoldTetherMonitor()
    assert len(m.gold_invariants) == 3
    ident, n_o, n_inf = m.gold_invariants
    assert ident[0] == 1.0
    assert n_o[5] == 0.5 and n_o[4] == -0.5          # n_o = 0.5(e5 - e4)
    assert n_inf[4] == 1.0 and n_inf[5] == 1.0       # n_inf = e4 + e5


# --- harmonized residual (§2.3) --------------------------------------------

def test_harmonized_residual_zero_on_identity():
    # identity is both closed (drift 0) and a seed (distance 0)
    assert GoldTetherMonitor().goldtether_residual(_id()) == 0.0


def test_harmonized_residual_nonneg_and_geo_driven_on_closed_versor():
    m = GoldTetherMonitor()
    F = make_rotor_from_angle(1.0)
    r = m.goldtether_residual(F)
    assert r >= 0.0
    # on a closed distant versor the geo term dominates → strictly above drift-only
    assert r > coherence_residual(F)


def test_harmonized_residual_explodes_on_drift_fail_closed():
    m = GoldTetherMonitor()
    dirty = np.zeros(32, dtype=np.float64)
    dirty[0] = 0.5
    dirty[1] = 0.5
    assert m.goldtether_residual(dirty) > 1.0         # drift/ε makes non-closure loud
    m.autonomy = 1.0
    assert m.alpha_constraint(dirty) == 1.0           # → full override


# --- α = Φ(R) control law (§2.3) -------------------------------------------

def test_alpha_serve_is_always_full_override():
    m = GoldTetherMonitor()
    m.autonomy = 1.0
    assert m.alpha_constraint(_id(), mode=OperatingMode.SERVE) == 1.0


def test_alpha_earned_autonomy_is_the_floor():
    m = GoldTetherMonitor()                            # fresh: autonomy 0
    assert m.alpha_constraint(_id()) == 1.0            # cannot go autonomous yet
    m.autonomy = 0.4
    for th in (0.0, 0.5, 1.0, 2.0):
        a = m.alpha_constraint(make_rotor_from_angle(th))
        assert a >= 1.0 - m.autonomy - 1e-12           # α floored by (1 − earned)


def test_alpha_autonomous_when_earned_and_coherent():
    m = GoldTetherMonitor()
    m.autonomy = 1.0
    assert m.alpha_constraint(_id()) == 0.0            # earned + on-seed + closed


def test_alpha_smooth_step_thresholds():
    m = GoldTetherMonitor()
    m.autonomy = 1.0
    F = make_rotor_from_angle(1.0)
    r = m.goldtether_residual(F)
    m.r_floor, m.r_critical = r + 0.1, r + 0.2
    assert m.alpha_constraint(F) == 0.0                # below floor → autonomous
    m.r_floor, m.r_critical = r - 0.2, r - 0.1
    assert m.alpha_constraint(F) == 1.0                # above critical → override
    m.r_floor, m.r_critical = r - 0.1, r + 0.1
    assert 0.0 < m.alpha_constraint(F) < 1.0           # in the ramp


def test_alpha_monotone_non_decreasing_in_distance():
    m = GoldTetherMonitor()
    m.autonomy = 1.0
    m.r_floor, m.r_critical = 0.0, 1.0
    prev = -1.0
    for th in np.linspace(0.05, 3.0, 25):
        a = m.alpha_constraint(make_rotor_from_angle(float(th)))
        assert 0.0 <= a <= 1.0
        assert a >= prev - 1e-9
        prev = a


def test_alpha_determinism_replay():
    F = make_rotor_from_angle(0.7)
    m1 = GoldTetherMonitor()
    m2 = GoldTetherMonitor()
    m1.autonomy = m2.autonomy = 0.5
    assert m1.alpha_constraint(F) == m2.alpha_constraint(F)


# --- supervised transition surface -----------------------------------------

def test_supervised_transition_endpoints_and_closure():
    m = GoldTetherMonitor()
    src, tgt = _id(), make_rotor_from_angle(0.6)
    # fresh (autonomy 0) → α = 1 → transition lands on the constraint
    out = m.supervised_transition(src, tgt, _id())
    assert np.allclose(out, tgt, atol=1e-6)
    assert versor_condition(out) < 1e-6
    # earned + coherent → α = 0 → transition stays on self
    m.autonomy = 1.0
    out = m.supervised_transition(src, tgt, _id())
    assert np.allclose(out, src)


# --- gold-set mutation discipline ------------------------------------------

def test_promote_requires_explicit_authorization():
    m = GoldTetherMonitor()
    with pytest.raises(ValueError):
        m.promote_gold_invariant(make_rotor_from_angle(0.3))
    m.promote_gold_invariant(make_rotor_from_angle(0.3), authorized=True)
    assert len(m.gold_invariants) == 4


def test_prune_retains_primal_seeds():
    m = GoldTetherMonitor()
    for i in range(50):
        m.promote_gold_invariant(make_rotor_from_angle(0.01 * i + 0.01), authorized=True)
    m.prune_gold_invariants(max_size=10)
    assert len(m.gold_invariants) == 10
    assert m.gold_invariants[0][0] == 1.0              # identity seed retained
    assert m.gold_invariants[1][5] == 0.5              # n_o seed retained
