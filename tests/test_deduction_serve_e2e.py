"""Deduction-serve arc, Phase 5 — end-to-end workflow through the real REPL path.

The arc's original goal, pinned against the ACTUAL serving spine (``ChatRuntime``,
the driver ``core chat`` constructs) rather than the composer in isolation:

    a user asks a basic logic question -> CORE decides -> an articulated,
    deterministic, telemetered response comes back.

Also pins the peripheral-systems wiring (Phase 5): deduction turns are
well-formed ``TurnEvent``s tagged ``grounding_source="deduction"``, they advance
the served-turn counter (so ADR-0255 discovery-yield counts them), and they
carry an observable ``DispatchAttempt`` — with the whole thing byte-identical
when the flag is off.
"""

from __future__ import annotations

from chat.runtime import ChatRuntime
from core.config import RuntimeConfig


def _runtime(enabled: bool) -> ChatRuntime:
    return ChatRuntime(
        config=RuntimeConfig(deduction_serving_enabled=enabled), no_load_state=True,
    )


def test_end_to_end_propositional_and_categorical_workflow() -> None:
    rt = _runtime(True)
    prop = rt.chat("If p then q. p. Therefore q.")
    assert prop.grounding_source == "deduction"
    assert "Your premises entail: q" in prop.surface

    cat = rt.chat(
        "All mammals are animals. All whales are mammals. "
        "Therefore all whales are animals."
    )
    assert cat.grounding_source == "deduction"
    assert "valid" in cat.surface and "follows" in cat.surface


def test_deduction_turns_are_well_formed_served_turns() -> None:
    """turn_log grows and the served-turn counter advances — so a deduction
    conversation is real served traffic (ADR-0255 discovery-yield denominator)."""
    rt = _runtime(True)
    before = rt._context.turn
    rt.chat("p or q. Not p. Therefore q.")
    rt.chat("If a then b. If b then c. a. Therefore c.")
    assert len(rt.turn_log) == 2
    assert rt._context.turn == before + 2
    last = rt.turn_log[-1]
    assert last.grounding_source == "deduction"


def test_dispatch_trace_records_deduction_commit() -> None:
    rt = _runtime(True)
    resp = rt.chat("If p then q. p. Therefore q.")
    assert resp.dispatch_trace is not None
    assert resp.dispatch_trace.selected == "deduction"
    committed = [
        a for a in resp.dispatch_trace.attempts
        if a.source == "deduction" and a.outcome == "admitted"
    ]
    assert committed, "a committed deduction turn must record an admitted DispatchAttempt"


def test_flag_off_is_byte_identical_across_bands() -> None:
    """With the flag off, both a propositional and a categorical argument fall
    through to the pre-arc pack-token-gloss surface, unchanged."""
    rt = _runtime(False)
    for text in [
        "If p then q. p. Therefore q.",
        "All mammals are animals. All whales are mammals. Therefore all whales are animals.",
    ]:
        resp = rt.chat(text)
        assert resp.grounding_source == "pack"
        assert "Pack-resident tokens" in resp.surface


def test_out_of_regime_argument_refuses_honestly() -> None:
    """A 'therefore' argument the reader can't parse into either band gets an
    honest committed refusal surface, never a fluent-but-ungrounded answer or a
    silent fall-through (INV-34 fail-closed)."""
    rt = _runtime(True)
    resp = rt.chat("If it rains then the ground is wet. It rains. Therefore the ground is wet.")
    assert resp.grounding_source == "deduction"
    assert "can't parse" in resp.surface  # honest reader-refusal disclosure
