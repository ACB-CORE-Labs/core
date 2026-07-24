"""Curriculum-grounded serving (ADR-0262) — the Phase-2 contract.

These tests pin the epistemology, not just the plumbing: that answers come
from the ratified curriculum and nowhere else, that an untaught fact is
UNKNOWN rather than "no", that a chain the curriculum does not teach is never
composed into a claim, and that a question whose vocabulary the subject has
never been taught is declined rather than answered from world knowledge.
"""

from __future__ import annotations

import pytest

from chat.curriculum_serve_license import curriculum_serve_license
from chat.curriculum_surface import (
    CurriculumQuery,
    CurriculumRefusal,
    band_for,
    curriculum_grounded_surface,
    decide_curriculum_question,
    is_curriculum_question,
    looks_like_curriculum_question,
    read_curriculum_question,
    resolve_domain,
    resolve_family,
)
from evals.curriculum_serve.oracle import oracle_answer
from teaching.curriculum_premises import (
    UnratifiedChain,
    compile_premises,
    load_curriculum,
    resolve_pinned,
)


# --- the curriculum is the only premise source --------------------------------


def test_premises_come_only_from_ratified_chains() -> None:
    curriculum = load_curriculum("physics")
    premises, chain_ids = compile_premises(curriculum, "causal")
    assert premises == (
        "force causes acceleration",
        "acceleration causes motion",
        "work causes energy",
        "charge causes field",
        "field causes force",
        "temperature reveals motion",
        "entropy reveals energy",
    )
    assert all(cid.startswith("physics-") for cid in chain_ids)


def test_pinned_chain_that_is_not_ratified_fails_loudly() -> None:
    """§4.3 provenance: a case whose curriculum moved under it must break, not
    quietly answer from what remains."""
    curriculum = load_curriculum("physics")
    with pytest.raises(UnratifiedChain):
        resolve_pinned(curriculum, ("physics-causal-999",))


def test_family_scoping_never_loses_a_taught_edge() -> None:
    """Compilation is family-scoped; every taught edge is reachable from the
    family its own connective implies, so scoping cannot hide an answer."""
    curriculum = load_curriculum("physics")
    for chain in curriculum.chains:
        premises, _ = compile_premises(curriculum, chain.family)
        assert chain.sentence in premises


# --- the verdicts that matter -------------------------------------------------


def test_taught_edge_is_entailed() -> None:
    decision = decide_curriculum_question("Does force cause acceleration?")
    assert decision.verdict == "entailed"
    assert decision.band == band_for("physics", "causal")


def test_untaught_composition_is_unknown_not_entailed() -> None:
    """The curriculum teaches force→acceleration and acceleration→motion. It
    does NOT teach that causation composes, so "force causes motion" is
    unsettled. Composing it would be inventing a rule nobody taught."""
    assert decide_curriculum_question("Does force cause motion?").verdict == "unknown"


def test_untaught_fact_is_unknown_never_refuted() -> None:
    """Open-world: silence is not denial. No question answerable from a purely
    positive curriculum may come back "no"."""
    for text in (
        "Does mass require energy?",          # true in the world, untaught
        "Does motion cause force?",           # the taught edge runs the other way
        "Does work cause motion?",            # both terms taught, no relation
    ):
        assert decide_curriculum_question(text).verdict == "unknown", text


def test_relation_is_read_at_face_value() -> None:
    """"entropy reveals energy" is taught; "entropy causes energy" is not. Same
    family, different relation — the curriculum said one and not the other."""
    assert decide_curriculum_question("Does entropy reveal energy?").verdict == "entailed"
    assert decide_curriculum_question("Does entropy cause energy?").verdict == "unknown"


def test_question_may_spell_the_relation_in_its_base_form() -> None:
    """The question says "cause", the curriculum says "causes" — normalized by
    the SAME closed agreement relation the verb band uses (ADR-0260)."""
    assert decide_curriculum_question("Does charge cause field?").verdict == "entailed"


# --- anti-recall ---------------------------------------------------------------


@pytest.mark.parametrize(
    "text", ["Does gravity cause acceleration?", "Does current cause field?"]
)
def test_untaught_vocabulary_declines_rather_than_recalling(text: str) -> None:
    """Both are true physics and both are outside every mounted pack. The
    DECIDER declines — it has no curriculum to decide them from — and the
    composer does not claim the turn at all, so the question reaches the rest
    of dispatch instead of being answered with a remark about curriculum."""
    decision = decide_curriculum_question(text)
    assert decision.verdict == "declined"
    assert decision.reason == "untaught_vocabulary"
    assert curriculum_grounded_surface(text) is None


@pytest.mark.parametrize(
    "text",
    [
        "Does the build pass?",              # ordinary question, untaught terms
        "Does it rain often?",               # ordinary question, untaught terms
        "Does anyone know the time?",        # not even the three-token shape
        "Does force accelerate?",            # two tokens
        "Does the force cause acceleration?",  # four tokens
    ],
)
def test_ordinary_does_questions_are_not_claimed(text: str) -> None:
    """The commit gate is ROUTABILITY, not shape. "Does …?" is one of the most
    common ways to open any English question; claiming every one of them would
    take ordinary turns away from the rest of dispatch and answer them with a
    curriculum remark. Only questions whose vocabulary a served subject
    actually teaches are this composer's turn."""
    assert curriculum_grounded_surface(text) is None
    assert not is_curriculum_question(text)


@pytest.mark.parametrize(
    "text",
    [
        "Does force cause acceleration?",   # taught, decidable
        "Does force explain acceleration?",  # taught terms, unknown relation
        "Does force cause motion?",         # taught, unsettled
    ],
)
def test_routable_questions_are_claimed_and_answered(text: str) -> None:
    """Past the gate the composer stays fail-closed: every routable question
    gets a committed, honest surface — including the one whose relation the
    curriculum does not teach, since its TERMS plainly are curriculum terms."""
    assert is_curriculum_question(text)
    assert curriculum_grounded_surface(text) is not None


# --- typed refusals ------------------------------------------------------------


@pytest.mark.parametrize(
    "text, reason",
    [
        ("Does force explain acceleration?", "out_of_curriculum"),
        ("Does the force cause acceleration?", "question_shape_out_of_band"),
        ("Does force accelerate?", "question_shape_out_of_band"),
    ],
)
def test_typed_refusals(text: str, reason: str) -> None:
    assert decide_curriculum_question(text).reason == reason


def test_non_question_text_is_not_claimed_at_all() -> None:
    """The composer returns None for anything that is not a ``Does …?``
    question, so pre-existing dispatch is byte-identical."""
    assert curriculum_grounded_surface("Force causes acceleration.") is None
    assert not looks_like_curriculum_question("Is force a cause of acceleration?")


def test_question_reader_shape() -> None:
    query = read_curriculum_question("Does force cause acceleration?")
    assert isinstance(query, CurriculumQuery)
    assert (query.subject, query.verb, query.obj) == ("force", "cause", "acceleration")
    assert isinstance(read_curriculum_question("Why does it move?"), CurriculumRefusal)


def test_domain_and_family_routing() -> None:
    query = read_curriculum_question("Does force cause acceleration?")
    assert isinstance(query, CurriculumQuery)
    assert resolve_domain(query) == "physics"
    assert resolve_family(query) == "causal"


# --- the license posture -------------------------------------------------------


def test_answers_are_disclosed_until_a_band_earns_serve() -> None:
    """No curriculum band holds a SERVE license yet (ADR-0262 §5: ratified
    curriculum volume, not machinery, is the binding constraint), so every
    answer is served DISCLOSED — sound, and honest about its track record."""
    assert curriculum_serve_license(band_for("physics", "causal")) is None
    surface = curriculum_grounded_surface("Does force cause acceleration?")
    assert surface is not None
    assert surface.startswith("(answered from my curriculum")


def test_an_earned_band_is_served_authoritatively() -> None:
    """The gate is wired, not stubbed: hand it a licensed band and the hedge
    disappears."""

    class _Licensed:
        licensed = True

    surface = curriculum_grounded_surface(
        "Does force cause acceleration?", license_lookup=lambda band: _Licensed()
    )
    assert surface is not None
    assert not surface.startswith("(answered from my curriculum")
    assert "physics curriculum teaches that force causes acceleration" in surface


# --- the independent oracle ----------------------------------------------------


def test_oracle_is_independent_and_agrees() -> None:
    """The oracle shares no code with the serving path; agreement across the
    verdict classes is the evidence the compiler reads the curriculum right."""
    for subject, relation, obj, expected in (
        ("force", "cause", "acceleration", "entailed"),
        ("force", "cause", "motion", "unknown"),
        ("gravity", "cause", "acceleration", "declined"),
    ):
        assert oracle_answer("physics", subject, relation, obj).verdict == expected


def test_oracle_reports_reachability_without_claiming_it() -> None:
    """force→acceleration→motion is reachable at depth 2 and still UNKNOWN —
    the property that proves composition is not being silently performed."""
    verdict = oracle_answer("physics", "force", "cause", "motion")
    assert verdict.verdict == "unknown"
    assert verdict.depth == 2
