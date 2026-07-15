"""ADR-0241 §2.4C / core_ha §5.2 — chiral orientation gate (sgn(Q) = const).

RED until core/physics/chiral_gate.py lands.

The blueprint's mirror-inversion safeguard: the global chiral anomaly sign of
the spinor field must stay constant — "preserving the sign … anchors the
global orientation of the cognitive manifold, preventing mirror-image
inversions." The substrate has a verified non-vacuous READOUT
(WaveManifold.chiral_charge; Q = ⟨ψ I₅ ψ̃⟩₀), but its only consumer
(GoldTetherMonitor.goldtether_residual) takes abs(), discarding the sign —
so orientation was measured, never enforced (integration-plan missing piece).

Fixture algebra (grade-1 v, central I₅ with I₅² = −1, Ĩ₅ = I₅):
    Q(v + v·I₅) = −2 v²   and   Q(v − v·I₅) = +2 v²
so the mirror pair is a genuine sign flip — and it is unreachable by any
rotor transport (Q is strictly conserved under ψ → Rψ), i.e. it models
exactly the corruption class the gate exists to catch.
"""

from __future__ import annotations

import numpy as np
import pytest

from algebra.cl41 import N_COMPONENTS, geometric_product
from algebra.rotor import make_rotor_from_angle
from core.physics.chiral_gate import (
    ChiralObservation,
    ChiralOrientationError,
    ChiralOrientationGate,
)
from core.physics.goldtether import GoldTetherMonitor
from core.physics.wave_manifold import WaveManifold, _I5


def _e(i: int, val: float = 1.0) -> np.ndarray:
    v = np.zeros(N_COMPONENTS, dtype=np.float64)
    v[i] = val
    return v


def _spinor_pair() -> tuple[np.ndarray, np.ndarray]:
    """(ψ, mirror-ψ) with Q(ψ) = −2.5 and Q(mirror) = +2.5."""
    v = _e(1) + 0.5 * _e(3)
    psi = v + geometric_product(v, _I5)
    mirror = v - geometric_product(v, _I5)
    return psi, mirror


# --- Latch + conservation ----------------------------------------------------


def test_gate_latches_then_reports_conserved_under_left_spinor_transport():
    gate = ChiralOrientationGate()
    M = WaveManifold()
    psi, _ = _spinor_pair()

    first = gate.observe(psi)
    assert isinstance(first, ChiralObservation)
    assert first.verdict == "latched"
    assert first.sign == -1
    assert first.latched_sign == -1
    assert abs(first.q) > 0.1

    R = make_rotor_from_angle(0.4, bivector_idx=7)
    psi_next = M.left_spinor_step(psi, R)
    second = gate.observe(psi_next)
    assert second.verdict == "conserved"
    assert second.sign == -1
    assert abs(second.q - first.q) < 1e-9  # Q strictly conserved


def test_gate_fails_closed_on_mirror_inversion():
    gate = ChiralOrientationGate()
    psi, mirror = _spinor_pair()
    gate.observe(psi)

    with pytest.raises(ChiralOrientationError, match="orientation_flip"):
        gate.observe(mirror)


# --- Even-field honesty (#19 family) ------------------------------------------


def test_gate_honest_on_even_versor_never_latches():
    """Even field-states have Q ≈ 0: no orientation is defined, the gate must
    not fabricate one, and repeated vacuous observations are not violations
    (does not revive the retired #19 gate)."""
    gate = ChiralOrientationGate()
    for angle, plane in ((0.9, 11), (0.3, 6), (0.55, 8)):
        obs = gate.observe(make_rotor_from_angle(angle, bivector_idx=plane))
        assert obs.verdict == "vacuous"
        assert obs.sign == 0
        assert obs.latched_sign == 0


def test_gate_vacuous_after_latch_is_not_violation_but_flip_reemergence_is():
    """|Q| may legitimately pass below the floor (superposition states); the
    latch persists, and a materially re-emerging FLIPPED sign still fails."""
    gate = ChiralOrientationGate()
    psi, mirror = _spinor_pair()

    gate.observe(psi)
    even = make_rotor_from_angle(0.7, bivector_idx=9)
    mid = gate.observe(even)
    assert mid.verdict == "vacuous"
    assert mid.latched_sign == -1  # latch persists

    same = gate.observe(psi)
    assert same.verdict == "conserved"

    with pytest.raises(ChiralOrientationError, match="orientation_flip"):
        gate.observe(mirror)


# --- Determinism ---------------------------------------------------------------


def test_gate_determinism():
    psi, _ = _spinor_pair()
    even = make_rotor_from_angle(0.2, bivector_idx=6)
    seq = (psi, even, psi)

    def run() -> tuple[str, ...]:
        gate = ChiralOrientationGate()
        return tuple(gate.observe(x).verdict for x in seq)

    assert run() == run() == ("latched", "vacuous", "conserved")


# --- GoldTether wiring (the enforcement point) ---------------------------------


def test_goldtether_residual_latches_and_fails_closed_on_flip():
    monitor = GoldTetherMonitor()
    psi, mirror = _spinor_pair()

    r = monitor.goldtether_residual(psi)
    assert np.isfinite(r)
    assert monitor.chiral_gate.latched_sign == -1

    with pytest.raises(ChiralOrientationError, match="orientation_flip"):
        monitor.goldtether_residual(mirror)


def test_goldtether_residual_unchanged_and_inert_on_even_serve_fields():
    """Serve-path even field-states are vacuous: the gate never latches and
    the residual VALUE is byte-identical to the pre-gate computation
    (drift + abs(chiral) magnitude semantics untouched)."""
    monitor = GoldTetherMonitor()
    wave = WaveManifold()
    F = make_rotor_from_angle(0.42, bivector_idx=8)

    r = monitor.goldtether_residual(F)
    assert monitor.chiral_gate.latched_sign == 0

    # Replicate the pre-gate residual formula exactly (ADR-0238 §2.3): the
    # gate must not perturb the value. Fresh monitors seed primal gold
    # invariants, so the geometric term is live.
    drift = wave.measure_unitary_residual(F)
    chiral = abs(float(wave.chiral_charge(F)))
    drift_term = (drift + chiral) / monitor.epsilon_drift
    scale = float(np.linalg.norm(F))
    min_dist = min(
        float(np.linalg.norm(F - np.asarray(inv, dtype=np.float64)))
        for inv in monitor.gold_invariants
    )
    geo_term = min_dist / scale
    expected = monitor.w_drift * drift_term + (1.0 - monitor.w_drift) * geo_term
    assert abs(r - expected) < 1e-15
