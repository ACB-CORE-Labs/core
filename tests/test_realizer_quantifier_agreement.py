"""Realizer plural agreement under quantifiers — G2 regression.

Closes english_fluency_ood gaps.md G2: under universal/existential
quantifiers, count-noun subjects pluralise and the verb de-conjugates
to the bare base.  Mass nouns (evidence, wisdom, …) stay singular
under the same quantifiers ("all evidence supports truth" is correct;
"all evidences support truth" is wrong English).

Coverage also includes the quantifier-tense / quantifier-aspect /
quantifier-negation interactions so future regressions are caught.
"""

from __future__ import annotations

import pytest

from generate.graph_planner import RhetoricalMove
from generate.templates import is_mass_noun, pluralize, render_step


# Count-noun pluralisation under "all"/"some" quantifiers.
_PLURAL_CASES: list[tuple[str, str, str, str, str]] = [
    ("all",  "molecule", "binds", "enzyme",   "all molecules bind enzyme"),
    ("all",  "atom",     "forms", "bond",     "all atoms form bond"),
    ("some", "river",    "flows", "valley",   "some rivers flow valley"),
    ("all",  "child",    "fits",  "school",   "all children fit school"),     # irregular plural
    ("all",  "analysis", "yields","insight",  "all analyses yield insight"),  # latinate
    ("some", "ribosome", "assembles", "protein", "some ribosomes assemble protein"),
]


@pytest.mark.parametrize("quantifier,subj,pred,obj,expected", _PLURAL_CASES)
def test_count_noun_pluralises_under_quantifier(
    quantifier: str, subj: str, pred: str, obj: str, expected: str
) -> None:
    surface = render_step(RhetoricalMove.ASSERT, subj, pred, obj, quantifier=quantifier)
    assert surface == expected


# Mass-noun cases — must NOT pluralise; verb stays singular too.
_MASS_CASES: list[tuple[str, str, str, str, str]] = [
    ("all",  "evidence", "supports", "truth",     "all evidence supports truth"),
    ("all",  "wisdom",   "requires", "patience",  "all wisdom requires patience"),
    ("some", "truth",    "requires", "courage",   "some truth requires courage"),
    ("some", "knowledge","grounds",  "action",    "some knowledge grounds action"),
    ("all",  "water",    "flows",    "downhill",  "all water flows downhill"),
]


@pytest.mark.parametrize("quantifier,subj,pred,obj,expected", _MASS_CASES)
def test_mass_noun_stays_singular_under_quantifier(
    quantifier: str, subj: str, pred: str, obj: str, expected: str
) -> None:
    surface = render_step(RhetoricalMove.ASSERT, subj, pred, obj, quantifier=quantifier)
    assert surface == expected


# Quantifier + negation interaction: plural subject → "do not", mass/none → "does not".
def test_quantifier_negation_uses_do_not_for_plural_subject() -> None:
    s = render_step(
        RhetoricalMove.ASSERT, "molecule", "binds", "enzyme",
        quantifier="all", negated=True,
    )
    assert s == "all molecules do not bind enzyme"


def test_quantifier_negation_uses_does_not_for_mass_subject() -> None:
    s = render_step(
        RhetoricalMove.ASSERT, "evidence", "supports", "truth",
        quantifier="all", negated=True,
    )
    assert s == "all evidence does not support truth"


# Quantifier + aspect: plural subject → "have/are", mass/none → "has/is".
def test_quantifier_perfective_aspect_uses_have_for_plural() -> None:
    s = render_step(
        RhetoricalMove.ASSERT, "molecule", "binds", "enzyme",
        quantifier="all", aspect="perfective",
    )
    assert s == "all molecules have bound enzyme"


def test_quantifier_imperfective_aspect_uses_are_for_plural() -> None:
    s = render_step(
        RhetoricalMove.ASSERT, "atom", "forms", "bond",
        quantifier="some", aspect="imperfective",
    )
    assert s == "some atoms are forming bond"


# Helper-level checks (so future code changes that bypass render_step
# still hit the same rules).
def test_pluralize_handles_irregular_and_latinate() -> None:
    assert pluralize("child") == "children"
    assert pluralize("analysis") == "analyses"
    assert pluralize("bus") == "buses"
    assert pluralize("city") == "cities"
    assert pluralize("leaf") == "leaves"
    assert pluralize("fish") == "fish"  # invariant


def test_is_mass_noun_known_set() -> None:
    assert is_mass_noun("evidence")
    assert is_mass_noun("Wisdom")  # case-insensitive
    assert is_mass_noun("water")
    assert not is_mass_noun("molecule")
    assert not is_mass_noun("atom")


# --------------------------------------------------------------------------- #
# Phase 3 — the 9-of-26 agreement defect
#
# ``_inflect_predicate`` applied ``base_form`` — a SINGLE-VERB function — to
# whole humanized predicate phrases, stripping the last character-class of the
# final word, and its plural branch never consulted ``copular``. Nine of the 26
# seed predicates came out wrong, and every multi-word one did.
# --------------------------------------------------------------------------- #

#: Hand-written English, NOT derived from the code under test. Deriving it would
#: make it agree by construction and measure nothing.
PLURAL_AGREEMENT_ORACLE = {
    "addresses": "address",
    "answers": "answer",
    "belongs to": "belong to",
    "causes": "cause",
    "contrasts with": "contrast with",
    "corrects": "correct",
    "defines": "define",
    "entails": "entail",
    "evidences": "evidence",
    "follows": "follow",
    "grounds": "ground",
    "has the following steps": "have the following steps",
    "implies": "imply",
    "is caused by": "are caused by",
    "is defined as": "are defined as",
    "is distinguished from": "are distinguished from",
    "is grounded in": "are grounded in",
    "is verified as": "are verified as",
    "means": "mean",
    "orders": "order",
    "precedes": "precede",
    "recalls": "recall",
    "requires": "require",
    "reveals": "reveal",
    "supports": "support",
    "verifies": "verify",
}


def test_the_oracle_covers_every_seed_predicate() -> None:
    """A partial oracle would let a predicate regress unseen."""
    from generate.lexicon import PREDICATE_DISPLAY

    assert set(PLURAL_AGREEMENT_ORACLE) == set(PREDICATE_DISPLAY.values())


@pytest.mark.parametrize(
    ("display", "expected"), sorted(PLURAL_AGREEMENT_ORACLE.items())
)
def test_plural_subject_agreement_matches_english(display: str, expected: str) -> None:
    """26/26 against hand-written English (was 17/26).

    The nine that were wrong: belongs to, causes ("caus"), contrasts with,
    has the following steps ("has the following step"), and the five
    ``is …`` copulars ("is defined as" -> "is defined a").
    """
    from generate.templates import _inflect_predicate

    assert _inflect_predicate(display, plural_subject=True) == expected


@pytest.mark.parametrize(
    ("display", "expected"),
    [
        ("is defined as", "are not defined as"),
        ("is grounded in", "are not grounded in"),
        ("has the following steps", "do not have the following steps"),
        ("belongs to", "do not belong to"),
        ("supports", "do not support"),
    ],
)
def test_plural_negation_agrees_then_negates(display: str, expected: str) -> None:
    """Plural + negated: a plural copula takes a bare ``not``; anything else
    needs do-support. Previously ``do not {base_form(phrase)}`` produced
    "do not is defined a"."""
    from generate.templates import _inflect_predicate

    assert _inflect_predicate(display, negated=True, plural_subject=True) == expected


def test_base_form_is_a_single_verb_function_and_says_so() -> None:
    """The root cause, pinned directly: ``base_form`` operates on ONE verb.

    It is still wrong on a phrase — that is inherent, not a bug to fix here —
    which is exactly why the plural branch calls ``agree_plural_phrase``
    instead. Pinning it stops someone "fixing" the symptom in the wrong place.
    """
    from generate.morphology import agree_plural_phrase, base_form

    assert base_form("causes") == "cause"          # was "caus"
    assert base_form("passes") == "pass"           # the sibilant rule still fires
    assert base_form("is defined as") == "is defined a"   # single-verb fn on a phrase
    assert agree_plural_phrase("is defined as") == "are defined as"


@pytest.mark.parametrize(
    ("singular", "plural"),
    [("proof", "proofs"), ("chief", "chiefs"), ("roof", "roofs"),
     ("belief", "beliefs"), ("wolf", "wolves"), ("knife", "knives")],
)
def test_f_to_ves_is_a_closed_set_not_a_rule(singular: str, plural: str) -> None:
    """``f`` -> ``ves`` is not productive in English. Applying it as a suffix
    rule made ``pluralize("proof")`` return "prooves", and Phase 2B had put
    ``pluralize`` on the serving path."""
    from generate.morphology import pluralize as _pluralize

    assert _pluralize(singular) == plural
