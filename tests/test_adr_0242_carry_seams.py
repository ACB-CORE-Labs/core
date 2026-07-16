"""ADR-0242 §5 carry seams — cert telemetry (P1) + F5–F7 cross-band gate (P2).

RED until both seams land. These are the two staged items recorded in the
acceptance packet §7 (ruled non-blocking at ratification, tracked work):

P1 (memo §5 Phase 1): "The returned FibonacciSearchCertificate is written to
the execution telemetry. If the certificate fails … defaults to the safe
baseline kappa = 1.0 and logs an OptimizationFailure warning." The search
returns typed results; nothing produced a telemetry-ready event.

P2 (memo §5 Phase 2): "Emits a DiscoveryCandidate in the contemplation loop
*only* when the surprise signal persists across multiple Fibonacci-scaled
temporal bands (F5 to F7), preventing transient noise from triggering
ungrounded updates." Band helpers existed; the persistence gate did not.

Both stay PROPOSAL/telemetry-side: no serve import, no COHERENT promotion,
no truth-status effect (memo §6 sovereignty invariant).
"""

from __future__ import annotations

import json

import pytest

from core.physics.goldtether import kappa_search_event, propose_kappa_line_search
from core.physics.multi_scale_energy import (
    CrossBandVerdict,
    cross_band_discovery_gate,
)

# --- P1: κ-search certificate → execution telemetry event ---------------------


def _good_objective(x: float) -> float:
    return (x - 0.789) ** 2


def _multimodal(x: float) -> float:
    return x**4 - x**2


class _CaptureSink:
    def __init__(self) -> None:
        self.lines: list[str] = []

    def emit(self, line: str) -> None:
        self.lines.append(line)


def test_kappa_search_event_certificate_payload():
    kappa, result = propose_kappa_line_search(_good_objective, evaluation_budget=16)
    event = kappa_search_event(kappa, result)

    assert event["kind"] == "fibonacci_kappa_search"
    assert event["outcome"] == "certificate"
    assert event["kappa"] == pytest.approx(kappa)
    cert = event["result"]
    assert cert["kind"] == "FibonacciSearchCertificate"
    assert len(cert["cert_id"]) == 64  # content-addressed audit trail
    assert cert["evaluations"] == 16
    assert cert["objective_id"] == "goldtether_kappa"
    # JSONL-ready: round-trips through json without custom encoders.
    assert json.loads(json.dumps(event)) == event


def test_kappa_search_event_failure_payload_falls_back_to_baseline():
    kappa, result = propose_kappa_line_search(
        _multimodal, lower=-2.0, upper=2.0, evaluation_budget=10
    )
    event = kappa_search_event(kappa, result)

    assert event["outcome"] == "failure"
    assert event["kappa"] == 1.0  # BASELINE_KAPPA — never a silent minimizer
    assert event["result"]["kind"] == "OptimizationFailure"
    assert "unimodality" in event["result"]["reason"]
    assert json.loads(json.dumps(event)) == event


def test_propose_kappa_line_search_emits_to_sink_when_provided():
    sink = _CaptureSink()
    kappa, result = propose_kappa_line_search(
        _good_objective, evaluation_budget=12, sink=sink
    )
    assert len(sink.lines) == 1
    event = json.loads(sink.lines[0])
    assert event["kind"] == "fibonacci_kappa_search"
    assert event["kappa"] == pytest.approx(kappa)
    assert event["result"]["cert_id"]


def test_kappa_search_event_deterministic():
    _, result_a = propose_kappa_line_search(_good_objective, evaluation_budget=12)
    _, result_b = propose_kappa_line_search(_good_objective, evaluation_budget=12)
    kappa_a, _ = propose_kappa_line_search(_good_objective, evaluation_budget=12)
    assert kappa_search_event(kappa_a, result_a) == kappa_search_event(
        kappa_a, result_b
    )


# --- P2: F5–F7 cross-band surprise persistence gate ----------------------------
#
# Bands: tau_n = F_n · tau0 with (F5, F6, F7) = (5, 8, 13).
# eligible ⇔ every band's decay-weighted accumulated surprise ≥ gamma AND the
# event history spans at least the shortest band (temporal extent — a single
# fresh spike has full weight in every band but zero persistence).


def _sustained(tau0: float, *, per_event: float = 0.5, n: int = 14) -> list[tuple[float, float]]:
    return [(float(i) * tau0, per_event) for i in range(n)]


def test_sustained_signal_is_eligible_across_all_bands():
    tau0 = 1.0
    events = _sustained(tau0)
    verdict = cross_band_discovery_gate(
        events, now=13.0 * tau0, tau0=tau0, gamma=0.35
    )
    assert isinstance(verdict, CrossBandVerdict)
    assert verdict.eligible is True
    assert verdict.bands == (5, 8, 13)
    assert all(e >= verdict.gamma for e in verdict.band_energies)


def test_single_fresh_spike_is_not_eligible_no_temporal_extent():
    tau0 = 1.0
    verdict = cross_band_discovery_gate(
        [(10.0, 5.0)], now=10.0, tau0=tau0, gamma=0.35
    )
    assert verdict.eligible is False
    assert verdict.reason == "insufficient_span"


def test_old_transient_is_not_eligible_short_band_decayed():
    tau0 = 1.0
    # Burst long ago: spans the extent requirement, but by `now` the F5 band
    # (tau = 5·tau0) has decayed it below gamma while F7 may still hold mass.
    events = [(0.0, 1.0), (2.0, 1.0), (4.0, 1.0), (6.0, 1.0)]
    verdict = cross_band_discovery_gate(events, now=40.0, tau0=tau0, gamma=0.35)
    assert verdict.eligible is False
    assert verdict.reason == "band_below_gamma"
    # The shortest band is the one that fails first.
    assert verdict.band_energies[0] < verdict.gamma


def test_gate_is_deterministic_and_pure():
    tau0 = 2.0
    events = _sustained(tau0, per_event=0.4)
    a = cross_band_discovery_gate(events, now=30.0, tau0=tau0, gamma=0.2)
    b = cross_band_discovery_gate(events, now=30.0, tau0=tau0, gamma=0.2)
    assert a == b


def test_gate_refuses_invalid_inputs():
    with pytest.raises(ValueError):
        cross_band_discovery_gate([], now=1.0, tau0=1.0, gamma=0.35)
    with pytest.raises(ValueError):
        cross_band_discovery_gate([(0.0, 1.0)], now=1.0, tau0=-1.0, gamma=0.35)
    with pytest.raises(ValueError):
        cross_band_discovery_gate([(2.0, 1.0)], now=1.0, tau0=1.0, gamma=0.35)  # event after now
    with pytest.raises(ValueError):
        cross_band_discovery_gate([(0.0, -1.0)], now=1.0, tau0=1.0, gamma=0.35)  # negative energy


def test_gate_module_stays_off_serve():
    """multi_scale_energy remains Tier-2: never imported by chat.runtime."""
    import subprocess
    import sys
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    probe = (
        "import importlib, sys;"
        "importlib.import_module('chat.runtime');"
        "print('LEAK' if any(m == 'core.physics.multi_scale_energy' or "
        "m.startswith('core.physics.multi_scale_energy.') for m in sys.modules)"
        " else 'CLEAN')"
    )
    out = subprocess.run(
        [sys.executable, "-c", probe],
        cwd=str(root),
        capture_output=True,
        text=True,
        env={"PYTHONPATH": str(root), "PATH": ""},
    )
    assert out.returncode == 0, out.stderr[-500:]
    assert out.stdout.strip().splitlines()[-1] == "CLEAN"
