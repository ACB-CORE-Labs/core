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
    PREDICATIVE_NOMINAL,
)
from generate.articulation_legality import (
    ArticulationLegality,
    validate_finite_predicate_legality,
)
from generate.graph_planner import RhetoricalMove
from generate.morphology import (
    agree_plural_phrase,
    base_form,
    inflect_phrase_head,
    is_mass_noun,
    past_participle,
    past_tense,
    pluralize,
    present_participle,
    takes_bare_not,
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


def _drop_indefinite_article(predicate_h: str) -> str:
    """Strip a trailing ``a``/``an`` from an inflected predicate.

    ``is_a`` humanizes to "is a" and pluralizes to "are a"; the article cannot
    survive a plural nominal ("all dogs are a mammals" is not English).
    """
    head, sep, rest = predicate_h.rpartition(" ")
    return head if sep and rest in ("a", "an") else predicate_h


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
    match (aspect, tense, negated, plural_subject):
        # Every branch below inflects the phrase HEAD and carries tokens 2..n
        # through untouched. Phase 3 fixed only the two plural branches, so
        # these eight were still handing whole phrases to single-verb
        # functions: "belongs to" came back "has belongs toed" (perfective),
        # "is belongs toing" (imperfective), "belongs toed" (past), and
        # "is defined as" came back "will is defined a" (future).
        case ("perfective", _, _, True):
            return f"have {inflect_phrase_head(verb, past_participle)}"
        case ("perfective", _, _, False):
            return f"has {inflect_phrase_head(verb, past_participle)}"
        case ("imperfective", _, _, True):
            return f"are {inflect_phrase_head(verb, present_participle)}"
        case ("imperfective", _, _, False):
            return f"is {inflect_phrase_head(verb, present_participle)}"
        case (_, "past", True, _):
            # A be/have head negates in place and carries its own past tense
            # ("was not defined as"); anything else takes do-support in the
            # past ("did not belong to"), where the head reverts to the base.
            if takes_bare_not(verb):
                past = inflect_phrase_head(verb, past_tense)
                p_head, sep, rest = past.partition(" ")
                if plural_subject:
                    p_head = {"was": "were", "has": "have", "did": "did"}.get(p_head, p_head)
                return f"{p_head} not{sep}{rest}" if rest else f"{p_head} not"
            return f"did not {inflect_phrase_head(verb, base_form)}"
        case (_, "past", False, _):
            past = inflect_phrase_head(verb, past_tense)
            if plural_subject:
                p_head, sep, rest = past.partition(" ")
                return {"was": "were"}.get(p_head, p_head) + sep + rest
            return past
        case (_, "future", True, _):
            return f"will not {inflect_phrase_head(verb, base_form)}"
        case (_, "future", False, _):
            return f"will {inflect_phrase_head(verb, base_form)}"
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
            return f"is not {inflect_phrase_head(verb, base_form)}"
        case (_, _, True, False):
            # Do-support puts the head in the bare infinitive. This branch was
            # the ninth instance of the same defect: ``base_form`` on the whole
            # phrase left "contrasts with" untouched (no -s/-es/-ies suffix to
            # strip from "with"), yielding "does not contrasts with".
            return f"does not {inflect_phrase_head(verb, base_form)}"
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
    # A predicate nominal names the subject's category, so it agrees with the
    # subject in number and sheds its indefinite article: "all dogs are
    # mammals", never "all dogs are a mammal". Restricted to the closed
    # PREDICATIVE_NOMINAL set — a prepositional object carries its own number
    # ("all claims are grounded in evidence") and pluralizing it produces
    # "evidences". The reader accepts the agreeing form and refuses the other,
    # which is why this was the last writer-side blocker on G-round-trip.
    if plural and predicate in PREDICATIVE_NOMINAL:
        obj_display = pluralize(obj_display)
        predicate_h = _drop_indefinite_article(predicate_h)
    subject_form = pluralize(subject) if plural else subject
    subject_display = f"{quantifier} {subject_form}" if quantifier else subject_form
    return template.format(
        subject=subject_display,
        predicate_h=predicate_h,
        obj=obj_display,
    )
