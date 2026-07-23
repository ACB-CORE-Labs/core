"""Deduction-serve arc, Phase 1 — DEDUCTION composer tests.

The contract these tests pin:

  - ``deduction_serving_enabled`` is OFF by default; flag-off ``chat()``
    output is byte-identical to pre-arc behavior for argument-shaped text
    (the pack-token-gloss fallback, unchanged).
  - Flag-on: a sentence-initial "therefore" conclusion clause commits the
    turn to ``chat/deduction_surface.py``; every committed turn returns a
    surface (never a silent fall-through to a different composer).
  - The full propositional comprehension gold corpus (Band v1) decides
    correctly end-to-end through the real ``ChatRuntime.chat()`` path,
    across multiple turns in one session (wrong=0).
  - Out-of-band shapes (categorical/syllogism, multi-word English
    propositions) are honestly declined, not silently misrouted.
  - Non-argument-shaped text is untouched regardless of the flag.
"""

from __future__ import annotations

from chat.deduction_surface import (
    deduction_grounded_surface,
    looks_like_deductive_argument,
)
from chat.runtime import ChatRuntime
from core.config import RuntimeConfig
from evals.propositional_logic.runner import _load_cases


# ---------------------------------------------------------------------------
# Pure-function contract — looks_like_deductive_argument
# ---------------------------------------------------------------------------


def test_looks_like_deductive_argument_true_for_therefore_conclusion() -> None:
    assert looks_like_deductive_argument("If p then q. p. Therefore q.")
    assert looks_like_deductive_argument("p or q. Not p. Therefore q.")
    assert looks_like_deductive_argument(
        "All mammals are animals. All whales are mammals. "
        "Therefore all whales are animals."
    )


def test_looks_like_deductive_argument_requires_sentence_initial_therefore() -> None:
    """"therefore" mid-clause (not its own conclusion clause) does not commit
    the turn — matches the reader's own per-clause discipline."""
    assert not looks_like_deductive_argument("What is light therefore darkness")
    assert not looks_like_deductive_argument("What is light?")
    assert not looks_like_deductive_argument("")


# ---------------------------------------------------------------------------
# Pure-function contract — deduction_grounded_surface
# ---------------------------------------------------------------------------


def test_non_argument_text_returns_none() -> None:
    assert deduction_grounded_surface("What is light?") is None
    assert deduction_grounded_surface("Why does parent exist?") is None


def test_entailed_case_renders_entailment() -> None:
    surface = deduction_grounded_surface("If p then q. p. Therefore q.")
    assert surface is not None
    assert "entail: q" in surface


def test_refuted_case_renders_refutation() -> None:
    surface = deduction_grounded_surface(
        "If p then q. Not q. Therefore not p."
    )
    assert surface is not None
    assert "entail" in surface


def test_unknown_case_renders_honest_indeterminacy() -> None:
    surface = deduction_grounded_surface("p or q. Therefore p.")
    assert surface is not None
    assert "don't settle" in surface


def test_inconsistent_premises_renders_typed_decline() -> None:
    surface = deduction_grounded_surface("p. Not p. Therefore q.")
    assert surface is not None
    assert "inconsistent" in surface


def test_categorical_argument_is_decided_band_v1b() -> None:
    """A valid categorical syllogism is now DECIDED (Band v1b, Phase 4) — the
    production categorical decider serves a validity verdict, no longer a
    decline."""
    surface = deduction_grounded_surface(
        "All mammals are animals. All whales are mammals. "
        "Therefore all whales are animals."
    )
    assert surface is not None
    assert "valid" in surface
    assert "follows" in surface


def test_invalid_categorical_argument_is_rejected() -> None:
    """An invalid syllogism (undistributed middle) is decided INVALID, not
    declined and not falsely served as valid (wrong=0 on the categorical band)."""
    surface = deduction_grounded_surface(
        "All cats are animals. All dogs are animals. Therefore all dogs are cats."
    )
    assert surface is not None
    assert "doesn't follow" in surface


def test_multiword_conditional_declines_reader_refusal() -> None:
    """Natural-English multi-word propositions are out of Band v1's
    single-token-atom scope; the reader refuses and the composer
    surfaces that honestly rather than silently falling through."""
    surface = deduction_grounded_surface(
        "If it rains then the ground is wet. It rains. "
        "Therefore the ground is wet."
    )
    assert surface is not None
    assert "reserved_word_in_np" in surface


def test_surface_is_deterministic() -> None:
    text = "If p then q. p. Therefore q."
    assert deduction_grounded_surface(text) == deduction_grounded_surface(text)


# ---------------------------------------------------------------------------
# Live runtime — flag off is byte-identical to pre-arc dispatch
# ---------------------------------------------------------------------------


def test_flag_off_preserves_pack_token_gloss_byte_identity() -> None:
    rt = ChatRuntime(
        config=RuntimeConfig(deduction_serving_enabled=False), no_load_state=True,
    )
    resp = rt.chat("If p then q. p. Therefore q.")
    assert resp.grounding_source == "pack"
    assert "Pack-resident tokens" in resp.surface


def test_flag_is_off_by_default() -> None:
    assert RuntimeConfig().deduction_serving_enabled is False


# ---------------------------------------------------------------------------
# Live runtime — flag on, single turn
# ---------------------------------------------------------------------------


def test_runtime_deduction_serves_entailed_answer() -> None:
    rt = ChatRuntime(
        config=RuntimeConfig(deduction_serving_enabled=True), no_load_state=True,
    )
    resp = rt.chat("If p then q. p. Therefore q.")
    assert resp.grounding_source == "deduction"
    assert "entail: q" in resp.surface


def test_runtime_non_argument_prompt_unaffected_by_flag() -> None:
    """The flag only intercepts argument-shaped text; ordinary prompts
    still route through the pre-existing dispatch."""
    rt = ChatRuntime(
        config=RuntimeConfig(deduction_serving_enabled=True), no_load_state=True,
    )
    resp = rt.chat("What is light?")
    assert resp.grounding_source != "deduction"


# ---------------------------------------------------------------------------
# Live runtime — full propositional gold corpus, multi-turn session, wrong=0
# ---------------------------------------------------------------------------


def test_runtime_decides_full_propositional_gold_corpus_wrong_zero() -> None:
    """End-to-end regression: every Band v1 gold case, decided through the
    real ``core chat`` serving path across one multi-turn session (not
    just the isolated comprehend->project->oracle lane). wrong=0 is the
    load-bearing assertion; declines are acceptable, a disagreement with
    gold is not."""
    rt = ChatRuntime(
        config=RuntimeConfig(deduction_serving_enabled=True), no_load_state=True,
    )
    cases = _load_cases()
    assert cases, "gold corpus must not be empty"
    wrong: list[str] = []
    for case in cases:
        resp = rt.chat(case["text"])
        assert resp.grounding_source == "deduction", (
            f"expected deduction routing for {case['text']!r}, "
            f"got grounding_source={resp.grounding_source!r}"
        )
        surface = resp.surface
        gold = case["gold"]
        if gold == "entailed" and "Your premises entail:" in surface:
            continue
        if gold == "refuted" and "entail the opposite" in surface:
            continue
        if gold == "unknown" and "don't settle" in surface:
            continue
        wrong.append(f"{case['text']!r} -> gold={gold} surface={surface!r}")
    assert not wrong, "\n".join(wrong)
