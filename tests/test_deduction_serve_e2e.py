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


def test_natural_english_argument_is_decided_end_to_end() -> None:
    """The Band v1 boundary case is now the Band v2-EN (ADR-0257) flagship:
    a natural-English argument decided through the real REPL spine, with the
    verdict rendered over the user's own clauses."""
    rt = _runtime(True)
    resp = rt.chat("If it rains then the ground is wet. It rains. Therefore the ground is wet.")
    assert resp.grounding_source == "deduction"
    assert "Your premises entail: the ground is wet" in resp.surface

    tollens = rt.chat(
        "If the seal is broken then the tank is empty. If the tank is empty then "
        "the pump is dry. The pump is not dry. Therefore the seal is not broken."
    )
    assert tollens.grounding_source == "deduction"
    assert "Your premises entail: the seal is not broken" in tollens.surface


def test_quoted_clause_surface_is_exempt_from_realizer_guard() -> None:
    """Regression (ADR-0257): the C1 slot-type guard must not reject a
    deduction surface for quoting the user's own clause. The pack lists
    ``open`` as VERB (its composed sense), which made R3 fire on the honest
    quoted copular "the door is not open" and silently replace a CORRECT
    entailment with the disclosure fallback. Deduction surfaces are exempt
    (quoted template, not slot composition) — pinned cold AND warm, since the
    guard runs on both dispatch paths."""
    text = (
        "Either the door is open or the window is open. The door isn't open. "
        "Therefore the window is open."
    )
    cold = _runtime(True)
    resp = cold.chat(text)
    assert resp.grounding_source == "deduction"
    assert "Your premises entail: the window is open" in resp.surface

    warm = _runtime(True)
    warm.chat("If p then q. p. Therefore q.")  # advance past the cold turn
    resp_warm = warm.chat(text)
    assert resp_warm.grounding_source == "deduction"
    assert "Your premises entail: the window is open" in resp_warm.surface


def test_member_argument_is_decided_end_to_end() -> None:
    """The ADR-0258 flagship: the classic instantiation syllogism ("Socrates
    is a man…"), decided through the real REPL spine via per-individual
    lowering, rendered over the user's own sentences — including the A-chain
    into an E-form."""
    rt = _runtime(True)
    resp = rt.chat("Socrates is a man. All men are mortal. Therefore Socrates is mortal.")
    assert resp.grounding_source == "deduction"
    assert "Your premises entail: socrates is mortal" in resp.surface

    negative = rt.chat(
        "Tweety is a canary. All canaries are birds. No birds are reptiles. "
        "Therefore Tweety is not a reptile."
    )
    assert negative.grounding_source == "deduction"
    assert "Your premises entail: tweety is not a reptile" in negative.surface


def test_out_of_regime_argument_refuses_honestly() -> None:
    """A 'therefore' argument NO band can read (verb-phrase negation —
    ADR-0257 scope-out #2, morphology work reserved for a future band) gets an
    honest committed refusal surface, never a fluent-but-ungrounded answer or
    a silent fall-through (INV-34 fail-closed)."""
    rt = _runtime(True)
    resp = rt.chat("The engine doesn't start. Therefore the engine is broken.")
    assert resp.grounding_source == "deduction"
    assert "can't parse" in resp.surface  # honest reader-refusal disclosure
