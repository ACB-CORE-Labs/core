"""ADR-0243 Phase 3 Lane A — contemplation runner discovery wiring.

Wires the ADR-0242 §5 pinned primitives (`is_discovery_eligible`,
`cross_band_discovery_gate`) into the contemplation runner so a
high-surprise, band-persistent observation history emits a
`DiscoveryCandidate` through the existing `DiscoveryCandidateSink`
(ADR-0243 §2.4 discovery signal).

Surprise-signal sourcing (the Lane A open question, resolved by reading
the substrate): `ContemplationFinding` carries NO surprise measurement —
the report-mining paths (frontier compare / contradiction detection) have
no geometry and are deliberately untouched.  The canonical surprise
carrier is the ADR-0239 dual-operator audit dict
(`core.physics.surprise.dual_procrustes_surprise` / `dual_operator`
output), produced live by `SelfAuthorshipMiner` and the ADR-0240
harness.  The runner therefore consumes explicit caller-timed
`SurpriseObservation`s — never a fabricated per-finding number, never a
wall clock.
"""

from __future__ import annotations

import json

import pytest

from core.contemplation.runner import (
    SurpriseDiscoveryOutcome,
    SurpriseObservation,
    contemplate_surprise_history,
)
from core.physics.multi_scale_energy import CrossBandVerdict
from teaching.discovery import DiscoveryCandidate
from teaching.discovery_sink import DiscoveryBufferSink


def _dual(
    surprise_norm: float,
    *,
    refused: str | None = None,
    productive: bool = False,
    gamma: float = 0.35,
) -> dict:
    """ADR-0239 dual-operator audit dict shape (see dual_procrustes_surprise)."""
    return {
        "surprise_norm": surprise_norm,
        "surprise_refused": refused,
        "transfer_accepted": productive,
        "discovery_eligible": (
            refused is None and not productive and surprise_norm > gamma
        ),
        "discovery_gamma": gamma,
        "procrustes_residual": 0.5,
    }


def _sustained(
    surprise_norm: float = 0.5,
    *,
    n: int = 14,
    tau0: float = 1.0,
    trace: str = "trace-sustained",
) -> list[SurpriseObservation]:
    """Mirror of the carry-seams `_sustained` history: eligible across bands."""
    return [
        SurpriseObservation(
            t=float(i) * tau0,
            dual=_dual(surprise_norm),
            source_turn_trace=trace,
        )
        for i in range(n)
    ]


# --- emission path ------------------------------------------------------------


def test_sustained_high_surprise_emits_candidate_on_sink() -> None:
    sink = DiscoveryBufferSink()
    out = contemplate_surprise_history(
        _sustained(0.5),
        now=13.0,
        tau0=1.0,
        sink=sink,
    )
    assert isinstance(out, SurpriseDiscoveryOutcome)
    assert out.reason == "emitted"
    assert isinstance(out.candidate, DiscoveryCandidate)
    assert out.candidate.trigger == "high_surprise"
    assert out.candidate.review_state == "unreviewed"
    assert out.candidate.proposed_chain["surprise_norm"] == pytest.approx(0.5)
    assert isinstance(out.verdict, CrossBandVerdict)
    assert out.verdict.eligible is True
    assert len(sink.lines) == 1
    line = json.loads(sink.lines[0])
    assert line["trigger"] == "high_surprise"
    assert line["source_turn_trace"] == "trace-sustained"


def test_no_sink_is_a_pure_factory() -> None:
    out = contemplate_surprise_history(_sustained(0.5), now=13.0, tau0=1.0)
    assert out.reason == "emitted"
    assert isinstance(out.candidate, DiscoveryCandidate)


# --- point-eligibility gate (is_discovery_eligible) ---------------------------


def test_low_surprise_is_not_discovery_eligible() -> None:
    sink = DiscoveryBufferSink()
    out = contemplate_surprise_history(
        _sustained(0.1), now=13.0, tau0=1.0, sink=sink
    )
    assert out.candidate is None
    assert out.verdict is None
    assert out.reason == "not_discovery_eligible"
    assert sink.lines == []


def test_refused_current_observation_never_emits() -> None:
    sink = DiscoveryBufferSink()
    history = _sustained(0.5)[:-1] + [
        SurpriseObservation(
            t=13.0,
            dual=_dual(float("inf"), refused="degenerate_metric_span"),
        )
    ]
    out = contemplate_surprise_history(history, now=13.0, tau0=1.0, sink=sink)
    assert out.candidate is None
    assert out.reason == "not_discovery_eligible"
    assert sink.lines == []


def test_productive_transfer_is_not_discovery() -> None:
    sink = DiscoveryBufferSink()
    history = _sustained(0.5)[:-1] + [
        SurpriseObservation(t=13.0, dual=_dual(0.9, productive=True))
    ]
    out = contemplate_surprise_history(history, now=13.0, tau0=1.0, sink=sink)
    assert out.candidate is None
    assert out.reason == "not_discovery_eligible"
    assert sink.lines == []


# --- persistence gate (cross_band_discovery_gate) -----------------------------


def test_single_fresh_spike_is_blocked_by_persistence_gate() -> None:
    sink = DiscoveryBufferSink()
    out = contemplate_surprise_history(
        [SurpriseObservation(t=10.0, dual=_dual(5.0))],
        now=10.0,
        tau0=1.0,
        sink=sink,
    )
    assert out.candidate is None
    assert isinstance(out.verdict, CrossBandVerdict)
    assert out.verdict.eligible is False
    assert out.reason == "insufficient_span"
    assert sink.lines == []


def test_decayed_burst_is_blocked_band_below_gamma() -> None:
    sink = DiscoveryBufferSink()
    history = [
        SurpriseObservation(t=t, dual=_dual(1.0)) for t in (0.0, 2.0, 4.0, 6.0)
    ]
    out = contemplate_surprise_history(history, now=40.0, tau0=1.0, sink=sink)
    assert out.candidate is None
    assert out.reason == "band_below_gamma"
    assert sink.lines == []


def test_refused_history_events_contribute_no_energy() -> None:
    """A refusal has no measured energy: excluding it can only lower band
    energy (fail-closed direction), never raise it."""
    measured = _sustained(0.5)
    with_refusals: list[SurpriseObservation] = []
    for obs in measured:
        with_refusals.append(
            SurpriseObservation(
                t=obs.t,
                dual=_dual(float("inf"), refused="degenerate_metric_span"),
            )
        )
        with_refusals.append(obs)
    baseline = contemplate_surprise_history(measured, now=13.0, tau0=1.0)
    interleaved = contemplate_surprise_history(with_refusals, now=13.0, tau0=1.0)
    assert baseline.verdict is not None and interleaved.verdict is not None
    assert interleaved.verdict.band_energies == baseline.verdict.band_energies
    # The interleaved current observation is refused, so only the baseline emits.
    assert baseline.reason == "emitted"


# --- determinism and validation ----------------------------------------------


def test_deterministic_and_pure() -> None:
    sink_a = DiscoveryBufferSink()
    sink_b = DiscoveryBufferSink()
    a = contemplate_surprise_history(_sustained(0.5), now=13.0, tau0=1.0, sink=sink_a)
    b = contemplate_surprise_history(_sustained(0.5), now=13.0, tau0=1.0, sink=sink_b)
    assert a == b
    assert sink_a.lines == sink_b.lines
    assert a.candidate is not None and b.candidate is not None
    assert a.candidate.candidate_id == b.candidate.candidate_id


def test_empty_observations_refused() -> None:
    with pytest.raises(ValueError):
        contemplate_surprise_history([], now=1.0)


def test_missing_surprise_norm_refused() -> None:
    with pytest.raises(ValueError):
        contemplate_surprise_history(
            [SurpriseObservation(t=0.0, dual={"discovery_gamma": 0.35})],
            now=1.0,
        )


def test_decreasing_time_order_refused() -> None:
    history = [
        SurpriseObservation(t=5.0, dual=_dual(0.5)),
        SurpriseObservation(t=1.0, dual=_dual(0.5)),
    ]
    with pytest.raises(ValueError):
        contemplate_surprise_history(history, now=6.0)


def test_observation_after_now_refused_by_gate() -> None:
    with pytest.raises(ValueError):
        contemplate_surprise_history(_sustained(0.5), now=1.0, tau0=1.0)


def test_looser_gamma_override_still_emits() -> None:
    """A stale measurement-time ``discovery_eligible: False`` baked into the
    dual dict must not veto a verdict both runner gates reached with the
    effective (looser) γ."""
    sink = DiscoveryBufferSink()
    history = _sustained(0.2)  # dual bakes gamma=0.35 → discovery_eligible False
    assert history[-1].dual["discovery_eligible"] is False
    out = contemplate_surprise_history(
        history, now=13.0, tau0=1.0, discovery_gamma=0.1, sink=sink
    )
    assert out.reason == "emitted"
    assert isinstance(out.candidate, DiscoveryCandidate)
    assert out.candidate.proposed_chain["discovery_gamma"] == pytest.approx(0.1)
    assert len(sink.lines) == 1


def test_non_string_refusal_marker_refused_at_boundary() -> None:
    dual = _dual(0.5)
    dual["surprise_refused"] = True  # truthy non-string would read as "not refused"
    with pytest.raises(ValueError):
        SurpriseObservation(t=0.0, dual=dual)


def test_negative_surprise_norm_refused_at_boundary() -> None:
    with pytest.raises(ValueError):
        SurpriseObservation(t=0.0, dual=_dual(-0.5))


def test_observation_dual_is_a_frozen_snapshot() -> None:
    raw = _dual(0.5)
    obs = SurpriseObservation(t=0.0, dual=raw)
    raw["surprise_norm"] = 99.0
    assert obs.dual["surprise_norm"] == pytest.approx(0.5)
    with pytest.raises(TypeError):
        obs.dual["surprise_norm"] = 99.0  # type: ignore[index]


def test_explicit_gamma_overrides_dual_dict_gamma() -> None:
    """The runner's gate runs first: a stricter caller γ blocks emission even
    when the dual dict was computed against a looser γ."""
    sink = DiscoveryBufferSink()
    out = contemplate_surprise_history(
        _sustained(0.5),
        now=13.0,
        tau0=1.0,
        discovery_gamma=0.75,
        sink=sink,
    )
    assert out.candidate is None
    assert out.reason == "not_discovery_eligible"
    assert out.discovery_gamma == pytest.approx(0.75)
    assert sink.lines == []
