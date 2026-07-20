"""ADR-0244 §2.2 — runtime wiring of the operator-preservation identity gate.

Validates the wiring in ``chat/runtime.py`` after geometric convergence:
  * identity scoring always uses the metric-exact wave path on ``final_state.F``
    (scalar-L2 dual-mode excised);
  * ``identity_wave_gate`` only controls live *refusal*, not scoring;
  * wave telemetry keys are present whenever an identity score exists.

The per-turn identity gate lives on the main generation path; a fresh empty-vault
runtime routes ungrounded inputs to the disclosure path (``identity_score=None``),
so the tests seed a short sequence to reach main-path turns.
"""

from __future__ import annotations

from chat.runtime import ChatRuntime
from chat.telemetry import serialize_turn_event
from core.config import RuntimeConfig

# A seeded sequence that reliably produces main-path (identity-checked) turns.
_SEQUENCE = ("water boils", "water boils", "birds fly", "birds fly")


def _main_path_events(flag: bool):
    runtime = ChatRuntime(
        config=RuntimeConfig(identity_wave_gate=flag), no_load_state=True
    )
    events = []
    for text in _SEQUENCE:
        runtime.chat(text)
        event = runtime.turn_log[-1]
        if event.identity_score is not None:
            events.append(event)
    assert events, "expected at least one main-path (identity-checked) turn"
    return events


def test_flag_off_still_scores_wave_geometry():
    """Scoring is always geometric; flag only gates refusal, not the score path."""
    for event in _main_path_events(False):
        score = event.identity_score
        assert score.wave_mode_active is True
        assert 0.0 <= score.leakage_norm <= 1.0
        assert -1.0 <= score.min_self_alignment <= 1.0
        payload = serialize_turn_event(event)
        assert payload.get("identity_wave_mode") is True
        assert "identity_leakage_norm" in payload
        assert "identity_min_self_alignment" in payload
        assert "identity_alignment" in payload
        assert "identity_flagged" in payload


def test_flag_on_activates_wave_gate_with_telemetry():
    for event in _main_path_events(True):
        score = event.identity_score
        assert score.wave_mode_active is True
        assert 0.0 <= score.leakage_norm <= 1.0
        assert -1.0 <= score.min_self_alignment <= 1.0
        payload = serialize_turn_event(event)
        assert payload.get("identity_wave_mode") is True
        assert "identity_leakage_norm" in payload
        assert "identity_min_self_alignment" in payload
        assert isinstance(payload["identity_boundary_violations"], list)


def test_flag_off_is_deterministic_across_runs():
    first = [e.surface for e in _main_path_events(False)]
    second = [e.surface for e in _main_path_events(False)]
    assert first == second
