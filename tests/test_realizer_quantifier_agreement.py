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


# ---------------------------------------------------------------------------
# Phase 4: the phrase-vs-single-verb defect on the EIGHT branches Phase 3 left
# ---------------------------------------------------------------------------
#
# Phase 3 fixed the two plural branches of ``_inflect_predicate`` by hand and
# pinned them with a hand-written oracle.  That left the other eight branches
# handing whole predicate phrases to single-verb functions, so the same root
# cause was still live:
#
#     "belongs to"  --perfective-->  "has belongs toed"
#     "belongs to"  --imperfective->  "is belongs toing"
#     "belongs to"  --past-------->  "belongs toed"
#     "is defined as" --future---->  "will is defined a"
#
# 49 of 80 (branch x multi-word predicate) pairs were wrong.  A per-branch
# oracle would have to be extended by hand every time a branch is added, and a
# branch added without one is invisible — which is how eight of them survived
# Phase 3.  So the pin here is a STRUCTURAL INVARIANT instead:
#
#     English marks tense, number and aspect on the FINITE VERB.  Inflecting a
#     predicate phrase must leave tokens 2..n byte-identical.
#
# It is falsifiable, it needs no oracle, and it covers branches nobody has
# written yet.

_INFLECTION_BRANCHES: list[tuple[str, dict[str, object]]] = [
    ("plural",              {"plural_subject": True}),
    ("plural+negated",      {"plural_subject": True, "negated": True}),
    ("negated",             {"negated": True}),
    ("past",                {"tense": "past"}),
    ("past+plural",         {"tense": "past", "plural_subject": True}),
    ("past+negated",        {"tense": "past", "negated": True}),
    ("future",              {"tense": "future"}),
    ("future+negated",      {"tense": "future", "negated": True}),
    ("perfective",          {"aspect": "perfective"}),
    ("perfective+plural",   {"aspect": "perfective", "plural_subject": True}),
    ("imperfective",        {"aspect": "imperfective"}),
    ("imperfective+plural", {"aspect": "imperfective", "plural_subject": True}),
]


def _multi_word_predicates() -> list[str]:
    from generate.lexicon import PREDICATE_DISPLAY

    return sorted({d for d in PREDICATE_DISPLAY.values() if " " in d})


@pytest.mark.parametrize(("branch", "kwargs"), _INFLECTION_BRANCHES, ids=[b for b, _ in _INFLECTION_BRANCHES])
def test_inflection_only_touches_the_head_verb(branch: str, kwargs: dict[str, object]) -> None:
    """Tokens 2..n of a predicate phrase survive inflection byte-identically."""
    from generate.templates import _inflect_predicate

    violations = []
    for display in _multi_word_predicates():
        tail = display.split(" ")[1:]
        got = _inflect_predicate(display, **kwargs)  # type: ignore[arg-type]
        if got.split(" ")[-len(tail):] != tail:
            violations.append((display, got))
    assert not violations, f"{branch} mangled the phrase tail: {violations}"


@pytest.mark.parametrize(
    ("kwargs", "expected"),
    [
        ({"tense": "past"},                       "was defined as"),
        ({"tense": "past", "plural_subject": True}, "were defined as"),
        ({"tense": "past", "negated": True},      "was not defined as"),
        ({"tense": "future"},                     "will be defined as"),
        ({"tense": "future", "negated": True},    "will not be defined as"),
        ({"aspect": "perfective"},                "has been defined as"),
        ({"aspect": "perfective", "plural_subject": True}, "have been defined as"),
        ({"aspect": "imperfective"},              "is being defined as"),
        ({"aspect": "imperfective", "plural_subject": True}, "are being defined as"),
    ],
)
def test_copular_head_inflects_as_be(kwargs: dict[str, object], expected: str) -> None:
    """The head of every copular predicate is a form of BE, and BE is irregular
    in all four of these paradigms.  ``_base_form`` is a suffix stripper, so
    before the irregular tables ``base_form("is")`` was **"i"** and
    ``present_participle("is")`` was **"iing"**."""
    from generate.templates import _inflect_predicate

    assert _inflect_predicate("is defined as", **kwargs) == expected  # type: ignore[arg-type]


def test_do_support_is_used_when_the_head_is_not_an_auxiliary() -> None:
    """"did not belong to", never "did not belonged to" or "belonged not to"."""
    from generate.templates import _inflect_predicate

    assert _inflect_predicate("belongs to", tense="past", negated=True) == "did not belong to"
    assert _inflect_predicate("belongs to", tense="past") == "belonged to"
    assert _inflect_predicate("belongs to", tense="future") == "will belong to"


# ---------------------------------------------------------------------------
# Phase 4: predicate-nominal object agreement
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    ("predicate", "obj", "expected"),
    [
        # Predicate nominal: the object names the subject's category, so it
        # agrees in number and the indefinite article goes.
        ("is_a",           "mammal",   "all dogs are mammals"),
        ("is_defined_as",  "compound", "all dogs are defined as compounds"),
        # Prepositional object: number is the speaker's, not the subject's.
        ("is_grounded_in", "evidence", "all dogs are grounded in evidence"),
        ("is_caused_by",   "observation", "all dogs are caused by observation"),
        ("belongs_to",     "pack",     "all dogs belong to pack"),
    ],
)
def test_only_predicate_nominals_agree_in_number(predicate: str, obj: str, expected: str) -> None:
    """``all dogs are a mammal`` was the last writer-side blocker on
    G-round-trip: the reader accepts "all dogs are mammals" and refuses the
    other.  But the fix must NOT be "pluralize the object under a plural
    subject" — that yields "grounded in evidences".  Hence a closed set."""
    assert render_step(RhetoricalMove.ASSERT, "dog", predicate, obj, quantifier="all") == expected


def test_singular_subjects_keep_the_article_and_the_singular_object() -> None:
    assert render_step(RhetoricalMove.ASSERT, "dog", "is_a", "mammal") == "dog is a mammal"


def test_predicative_nominal_is_a_closed_set_not_every_copular_predicate() -> None:
    """If this set ever becomes "anything starting with is", the mass-noun
    control above starts failing."""
    from generate.lexicon import PREDICATIVE_NOMINAL

    assert PREDICATIVE_NOMINAL == frozenset({"is_a", "is_defined_as"})


def test_do_support_puts_the_head_in_the_bare_infinitive() -> None:
    """The ninth instance of the same defect, and the one the tail invariant
    CANNOT see: "does not contrasts with" preserves the tail perfectly and is
    still wrong, because the error is on the head.

    ``base_form("contrasts with")`` returned the phrase unchanged — "with" has
    no -s/-es/-ies suffix to strip — so the 3sg -s survived do-support. A tail
    invariant is necessary, not sufficient; this is the sufficiency half.
    """
    from generate.templates import _inflect_predicate

    assert _inflect_predicate("contrasts with", negated=True) == "does not contrast with"
    assert _inflect_predicate("belongs to", negated=True) == "does not belong to"
    assert _inflect_predicate("causes", negated=True) == "does not cause"
    # A copular head negates in place and keeps its finite form.
    assert _inflect_predicate("is defined as", negated=True) == "is not defined as"
