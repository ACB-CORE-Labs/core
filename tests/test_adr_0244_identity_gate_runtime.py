"""ADR-0244 §2.2 — runtime wiring of the operator-preservation identity gate.

Validates the flag-gated wiring in ``chat/runtime.py``:
  * flag OFF (default) → legacy identity score, no wave telemetry (byte-identical
    wire format);
  * flag ON → the wave gate runs on the live versor ``final_state.F``, the score
    is wave-mode with real leakage/orientation, and the telemetry serializer
    surfaces the wave keys.

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


def test_flag_off_scores_are_legacy_no_wave_telemetry():
    for event in _main_path_events(False):
        score = event.identity_score
        assert score.wave_mode_active is False
        assert score.leakage_norm == 0.0
        assert score.min_self_alignment == 1.0
        payload = serialize_turn_event(event)
        assert "identity_wave_mode" not in payload
        assert "identity_leakage_norm" not in payload
        assert "identity_min_self_alignment" not in payload
        assert "identity_boundary_violations" not in payload
        # legacy identity telemetry unchanged
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
    # The flag-off path is byte-identical run to run (the fast lane pins that it
    # is also byte-identical to the pre-ADR-0244 baseline).
    first = [e.surface for e in _main_path_events(False)]
    second = [e.surface for e in _main_path_events(False)]
    assert first == second
