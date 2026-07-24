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
    _UNVERIFIED_SHAPE_DISCLOSURE,
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


def test_multiword_conditional_is_decided_band_v2_en() -> None:
    """Natural-English multi-word propositions — Band v1's documented boundary
    case (this exact text used to surface ``reserved_word_in_np``) — are now
    DECIDED by the English-clause band (ADR-0257), authoritatively (the
    ``en_conditional_single`` band holds an earned SERVE license), with the
    verdict rendered over the user's own clauses."""
    surface = deduction_grounded_surface(
        "If it rains then the ground is wet. It rains. "
        "Therefore the ground is wet."
    )
    assert surface is not None
    assert "Your premises entail: the ground is wet" in surface
    assert not surface.startswith(_UNVERIFIED_SHAPE_DISCLOSURE)


def test_contraposition_is_decided_band_v2_en() -> None:
    """The other documented Band v1 boundary case (nested negation in a
    conditional conclusion) — now decided: contraposition is ENTAILED."""
    surface = deduction_grounded_surface("If p then q. Therefore if not q then not p.")
    assert surface is not None
    assert "Your premises entail: if not q then not p" in surface


def test_english_modus_tollens_via_copular_negation() -> None:
    surface = deduction_grounded_surface(
        "If the alarm is armed then the light is on. The light is not on. "
        "Therefore the alarm is not armed."
    )
    assert surface is not None
    assert "Your premises entail: the alarm is not armed" in surface


def test_english_unknown_is_scoped_to_the_opaque_reading() -> None:
    """UNKNOWN is the one verdict that is NOT substitution-closed (internal
    clause structure this band did not read could settle it), so its surface
    must scope the claim to the opaque reading explicitly (ADR-0257 §3)."""
    surface = deduction_grounded_surface(
        "If it rains then the ground is wet. The ground is wet. Therefore it rains."
    )
    assert surface is not None
    assert "Reading each clause as one indivisible claim" in surface
    assert "don't settle" in surface


def test_english_unearned_band_would_be_hedged() -> None:
    """The en_* bands ride the SAME earned-license gate: strip the license and
    the same sound answer is served DISCLOSED, never authoritatively."""
    surface = deduction_grounded_surface(
        "If it rains then the ground is wet. It rains. Therefore the ground is wet.",
        license_lookup=lambda band: None,
    )
    assert surface is not None
    assert surface.startswith(_UNVERIFIED_SHAPE_DISCLOSURE)
    assert "Your premises entail: the ground is wet" in surface


def test_english_reader_refusal_keeps_prior_honest_surface() -> None:
    """When the English band ALSO cannot read the argument, the pre-existing
    honest surfaces are preserved verbatim — the band only widens."""
    surface = deduction_grounded_surface("It never snows. Therefore it never snows.")
    assert surface is not None
    assert "can't parse" in surface


def test_membership_syllogism_is_decided_band_v3_mem() -> None:
    """The classic instantiation syllogism — reserved by ADR-0257 §6.1, now
    DECIDED by the member band (ADR-0258), authoritatively (the
    ``en_member_single`` band holds an earned SERVE license), with the verdict
    rendered over the user's own sentences."""
    surface = deduction_grounded_surface(
        "Socrates is a man. All men are mortal. Therefore Socrates is mortal."
    )
    assert surface is not None
    assert "Your premises entail: socrates is mortal" in surface
    assert not surface.startswith(_UNVERIFIED_SHAPE_DISCLOSURE)


def test_member_negative_universal_is_decided() -> None:
    """The E-form ("no …") lowers to a negated instantiation and decides."""
    surface = deduction_grounded_surface(
        "Fido is a dog. No dogs are cats. Therefore Fido is not a cat."
    )
    assert surface is not None
    assert "Your premises entail: fido is not a cat" in surface


def test_member_unknown_is_scoped_to_the_instantiated_reading() -> None:
    """Member-band UNKNOWN must scope itself (ADR-0258 §3): co-reference of
    distinct names or an unlinked class identity could settle what the
    lowering leaves open, so the claim is stated of the reading."""
    surface = deduction_grounded_surface(
        "Socrates is mortal. All men are mortal. Therefore Socrates is a man."
    )
    assert surface is not None
    assert "Reading each name as one individual" in surface
    assert "don't settle" in surface


def test_member_unearned_band_would_be_hedged() -> None:
    """The en_member_* bands ride the SAME earned-license gate: strip the
    license and the same sound answer is served DISCLOSED, never
    authoritatively."""
    surface = deduction_grounded_surface(
        "Socrates is a man. All men are mortal. Therefore Socrates is mortal.",
        license_lookup=lambda band: None,
    )
    assert surface is not None
    assert surface.startswith(_UNVERIFIED_SHAPE_DISCLOSURE)
    assert "Your premises entail: socrates is mortal" in surface


def test_member_reader_refusal_keeps_prior_honest_surface() -> None:
    """When the member band ALSO cannot read the argument (here: tense, a
    deliberate ADR-0258 scope-out), the pre-existing honest surfaces are
    preserved verbatim — the band only widens."""
    surface = deduction_grounded_surface(
        "Socrates was a man. All men are mortal. Therefore Socrates is mortal."
    )
    assert surface is not None
    assert "can't parse" in surface


def test_conditional_membership_fusion_is_decided_band_v4_cm() -> None:
    """The ADR-0258 §6.1 scope-out, now decided (ADR-0259): a conditional
    whose clauses are membership facts, authoritatively (the
    ``en_condmem_conditional`` band holds an earned SERVE license)."""
    surface = deduction_grounded_surface(
        "If Socrates is a man then Socrates is mortal. Socrates is a man. "
        "Therefore Socrates is mortal."
    )
    assert surface is not None
    assert "Your premises entail: socrates is mortal" in surface
    assert not surface.startswith(_UNVERIFIED_SHAPE_DISCLOSURE)


def test_conditional_membership_fusion_genuinely_fuses() -> None:
    """The mechanism this band adds: a bare universal's instantiated atom
    unifies with a connective leaf's atom — neither mechanism alone decides
    this argument."""
    surface = deduction_grounded_surface(
        "All men are mortal. If Socrates is a philosopher then Socrates is a man. "
        "Socrates is a philosopher. Therefore Socrates is mortal."
    )
    assert surface is not None
    assert "Your premises entail: socrates is mortal" in surface


def test_cond_member_unknown_is_scoped_to_the_instantiated_reading() -> None:
    surface = deduction_grounded_surface(
        "If Socrates is a man then Socrates is mortal. Therefore Socrates is mortal."
    )
    assert surface is not None
    assert "Reading each name as one individual" in surface
    assert "don't settle" in surface


def test_cond_member_unearned_band_would_be_hedged() -> None:
    """The en_condmem_* bands ride the SAME earned-license gate: strip the
    license and the same sound answer is served DISCLOSED, never
    authoritatively."""
    surface = deduction_grounded_surface(
        "If Socrates is a man then Socrates is mortal. Socrates is a man. "
        "Therefore Socrates is mortal.",
        license_lookup=lambda band: None,
    )
    assert surface is not None
    assert surface.startswith(_UNVERIFIED_SHAPE_DISCLOSURE)
    assert "Your premises entail: socrates is mortal" in surface


def test_cond_member_reader_refusal_keeps_prior_honest_surface() -> None:
    """When the conditional-membership band ALSO cannot read the argument
    (here: a conditional nested inside another), the pre-existing honest
    surface is preserved verbatim — the band only widens."""
    surface = deduction_grounded_surface(
        "If the door is open then if the window is open then the room is cold. "
        "Therefore the room is cold."
    )
    assert surface is not None
    assert "can't parse" in surface


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
