"""Deterministic surface templates for rhetorical moves.

Each template is a format string keyed by RhetoricalMove. Slots:
  {subject}   — primary subject from the articulation step
  {predicate} — semantic predicate (e.g. "is_defined_as", "contrasts_with")
  {obj}       — object slot from the graph node (may be "<pending>")

Templates are intentionally simple. The goal is structural correctness,
not fluency — fluency comes in a later phase when the generation stream
consumes these as constraints rather than final output.
"""

from __future__ import annotations

from generate.lexicon import (
    IRREGULAR_PLURALS,
    PLURAL_QUANTIFIERS,
    PREDICATE_DISPLAY,
)
from generate.articulation_legality import (
    ArticulationLegality,
    validate_finite_predicate_legality,
)
from generate.graph_planner import RhetoricalMove
from generate.morphology import (
    agree_plural_phrase,
    base_form,
    is_mass_noun,
    past_participle,
    past_tense,
    pluralize,
    present_participle,
)


# Noun pluralisation — used under quantifiers (all/some/many/few/most).
# Closes english_fluency_ood gaps.md G2 (plural agreement).
#
# Phase 2B: the rules moved to generate/morphology.py, which now owns number
# in both directions. Re-exported here because this module's public surface
# is consumed by the eval runners.
_IRREGULAR_PLURALS: dict[str, str] = IRREGULAR_PLURALS


# Quantifiers that demand plural agreement on the subject + verb.
# "the" / "a" stay singular; "every" / "each" are singular by English
# rule even though semantically universal.
_PLURAL_QUANTIFIERS: frozenset[str] = PLURAL_QUANTIFIERS

_PREDICATE_DISPLAY: dict[str, str] = PREDICATE_DISPLAY


def _humanize_predicate(predicate: str) -> str:
    return _PREDICATE_DISPLAY.get(predicate, predicate.replace("_", " "))


_MOVE_TEMPLATES: dict[RhetoricalMove, str] = {
    RhetoricalMove.ASSERT: "{subject} {predicate_h} {obj}",
    RhetoricalMove.ELABORATE: "furthermore, {subject} {predicate_h} {obj}",
    RhetoricalMove.CONTRAST: "in contrast, {subject} {predicate_h} {obj}",
    RhetoricalMove.SEQUENCE: "next, {subject} {predicate_h} {obj}",
    RhetoricalMove.CORRECT: "correction: {subject} {predicate_h} {obj}",
}


def _inflect_predicate(
    predicate_h: str,
    *,
    negated: bool = False,
    tense: str | None = None,
    aspect: str | None = None,
    plural_subject: bool = False,
) -> str:
    """Apply tense/aspect/negation to a humanized predicate.

    When ``plural_subject`` is true, the conjugation uses plural
    agreement (do not / have / are / bare-base verb in present) so
    surfaces like "all molecules bind enzyme" come out correctly
    instead of "all molecule binds enzyme" (english_fluency_ood G2).
    """
    verb = predicate_h
    copular = any(
        predicate_h.startswith(prefix)
        for prefix in ("is ", "are ", "has ", "have ", "belongs ")
    )
    base = base_form(verb)

    match (aspect, tense, negated, plural_subject):
        case ("perfective", _, _, True):
            return f"have {past_participle(verb)}"
        case ("perfective", _, _, False):
            return f"has {past_participle(verb)}"
        case ("imperfective", _, _, True):
            return f"are {present_participle(verb)}"
        case ("imperfective", _, _, False):
            return f"is {present_participle(verb)}"
        case (_, "past", True, _):
            return f"did not {base}"
        case (_, "past", False, _):
            return past_tense(verb)
        case (_, "future", True, _):
            return f"will not {base}"
        case (_, "future", False, _):
            return f"will {base}"
        case (_, _, True, True):
            # Plural + negated. Agree the head first, then negate around it:
            # a plural copula takes a bare "not" ("are not defined as"), while
            # any other verb needs do-support ("do not have the following
            # steps", "do not belong to"). Previously this was
            # ``f"do not {base}"`` over the whole phrase, which produced
            # "do not is defined a".
            agreed = agree_plural_phrase(predicate_h)
            head, sep, rest = agreed.partition(" ")
            if head in ("are", "were"):
                return f"{head} not{sep}{rest}" if rest else f"{head} not"
            return f"do not {agreed}"
        case (_, _, True, False) if copular:
            if predicate_h.startswith("is "):
                return "is not " + predicate_h[3:]
            if predicate_h.startswith("are "):
                return "are not " + predicate_h[4:]
            if predicate_h.startswith("has "):
                return "has not " + predicate_h[4:]
            if predicate_h.startswith("have "):
                return "have not " + predicate_h[5:]
            if predicate_h.startswith("belongs "):
                return "does not belong " + predicate_h[8:]
            return f"is not {base}"
        case (_, _, True, False):
            return f"does not {base}"
        case (_, _, False, True):
            # Plural agreement on the whole phrase, not base_form() of it.
            # This is the branch the 9-of-26 defect lived in: it returned the
            # bare base and never consulted ``copular``, so "is defined as"
            # came back "is defined a" instead of "are defined as".
            return agree_plural_phrase(predicate_h)
        case _:
            return verb


def render_step(
    move: RhetoricalMove,
    subject: str,
    predicate: str,
    obj: str,
    *,
    negated: bool = False,
    quantifier: str | None = None,
    tense: str | None = None,
    aspect: str | None = None,
) -> str:
    """Render a single articulation step into a surface fragment."""
    template = _MOVE_TEMPLATES[move]
    # Mass nouns under a quantifier stay singular ("all evidence
    # supports", not "all evidences support").  Count nouns
    # pluralise and the verb de-conjugates ("all molecules bind").
    plural_q = quantifier is not None and quantifier.lower() in _PLURAL_QUANTIFIERS
    is_mass = is_mass_noun(subject)
    plural = plural_q and not is_mass
    predicate_h = _humanize_predicate(predicate)
    legality = validate_finite_predicate_legality(
        predicate_humanized=predicate_h,
        negated=negated,
    )
    if legality.legality is ArticulationLegality.ILLEGAL_NON_VERB_FINITE_PREDICATE:
        return "I cannot realize that proposition coherently yet."
    predicate_h = _inflect_predicate(
        predicate_h,
        negated=negated, tense=tense, aspect=aspect,
        plural_subject=plural,
    )
    obj_display = obj if obj != "<pending>" else "..."
    subject_form = pluralize(subject) if plural else subject
    subject_display = f"{quantifier} {subject_form}" if quantifier else subject_form
    return template.format(
        subject=subject_display,
        predicate_h=predicate_h,
        obj=obj_display,
    )
