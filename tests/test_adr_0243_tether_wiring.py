"""Seam S3 — unified autonomy floor wired into the cognitive lifecycle.

Pins the tether control law composed with pin SD-A: closed certified states
update the GoldTether monitor (may elevate autonomy), non-admitted states
fail-close it (autonomy hard 0), and ADMITTED OPEN SUPERPOSITIONS are
measured without a state update — punishing legitimate interference states
would encode the exact defect the egress gate refuses to. Chiral orientation
is observed on every reading and a material flip raises (fail-closed).
"""

from __future__ import annotations

import dataclasses

import numpy as np
import pytest

from algebra.rotor import make_rotor_from_angle
from core.physics.chiral_gate import ChiralOrientationError
from core.physics.cognitive_lifecycle import (
    CognitiveLifecycleEngine,
    PropositionalProblem,
    compile_propositional,
    compile_quadratic_well,
    egress_gate,
    relax_to_ground,
    tether_reading,
    uniform_assignment_state,
)
from core.physics.goldtether import GoldTetherMonitor
from core.physics.sensorium_wave_feed import fake_deterministic_packet


def _closed_solve(monitor: GoldTetherMonitor):
    engine = CognitiveLifecycleEngine(monitor=monitor)
    target = np.asarray(make_rotor_from_angle(0.3, bivector_idx=6), dtype=np.float64)
    packets = [fake_deterministic_packet("audio", angle=0.25, plane=6)]
    return engine.solve(packets, "tether-demo", compile_quadratic_well(target))


def test_closed_certified_turn_updates_monitor():
    monitor = GoldTetherMonitor()
    outcome = _closed_solve(monitor)
    assert outcome.verdict.admitted and outcome.verdict.versor_closed
    tether = outcome.tether
    assert tether is not None and tether.updated
    assert tether.residual < 1e-6
    assert tether.chiral_verdict == "vacuous"  # closed versor: Q = 0 by theorem
    assert len(monitor.history) == 1


def test_solve_without_monitor_records_no_tether():
    engine = CognitiveLifecycleEngine()
    target = np.asarray(make_rotor_from_angle(0.3, bivector_idx=6), dtype=np.float64)
    packets = [fake_deterministic_packet("audio", angle=0.25, plane=6)]
    outcome = engine.solve(packets, "tether-demo", compile_quadratic_well(target))
    assert outcome.tether is None


def test_admitted_open_superposition_measures_without_update():
    """SD-A dual: a legitimate interference state must not decay the floor."""
    problem = PropositionalProblem(
        atoms=("a", "b"),
        clauses=((("a", True), ("b", True)), (("a", False), ("b", True))),
    )
    result = relax_to_ground(uniform_assignment_state(problem), compile_propositional(problem))
    verdict = egress_gate(result.psi_steady, result.certificate)
    assert verdict.admitted and not verdict.versor_closed

    monitor = GoldTetherMonitor(floor=0.4, autonomy=0.2)
    tether = tether_reading(
        monitor,
        result.psi_steady,
        admitted=verdict.admitted,
        versor_closed=verdict.versor_closed,
    )
    assert not tether.updated
    assert tether.residual > monitor.epsilon_drift  # honest: open state, big residual
    assert monitor.floor == 0.4 and monitor.autonomy == 0.2  # untouched
    assert len(monitor.history) == 0


def test_non_admitted_turn_fails_closed_to_zero_autonomy():
    monitor = GoldTetherMonitor(floor=0.6, autonomy=0.5)
    outcome_engine = CognitiveLifecycleEngine()
    target = np.asarray(make_rotor_from_angle(0.3, bivector_idx=6), dtype=np.float64)
    packets = [fake_deterministic_packet("audio", angle=0.25, plane=6)]
    outcome = outcome_engine.solve(packets, "tether-demo", compile_quadratic_well(target))
    refused = dataclasses.replace(outcome.verdict, admitted=False, reason="forced_refusal")
    tether = tether_reading(
        monitor,
        outcome.relaxation.psi_steady,
        admitted=refused.admitted,
        versor_closed=refused.versor_closed,
    )
    assert tether.updated
    # Closed state but the turn is refused → update path ran; the monitor's own
    # law applies (this closed versor has residual ≤ ε, so autonomy may step,
    # bounded by the floor). The FAIL-CLOSED zeroing fires on drifted states:
    drifted = np.zeros(32, dtype=np.float64)
    drifted[0] = 0.5  # non-unit ⇒ ψψ̃ far from 1
    t2 = tether_reading(monitor, drifted, admitted=False, versor_closed=False)
    assert t2.updated and monitor.autonomy == 0.0


def test_material_chiral_flip_raises_fail_closed():
    monitor = GoldTetherMonitor()
    monitor.chiral_gate.observe_q(0.5)  # latch +1
    flipped = np.zeros(32, dtype=np.float64)
    flipped[0], flipped[31] = 0.8, 0.6  # material Q of opposite sign
    with pytest.raises(ChiralOrientationError):
        tether_reading(monitor, flipped, admitted=True, versor_closed=False)
