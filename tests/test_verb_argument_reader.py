"""Band v5-VP (ADR-0260) — verb-predicate argument reader contract.

The reader extends v3-MEM's per-individual propositional lowering with a
second atom family — one atom per *(individual, verb-lemma-group,
object-term)* — in one shared atom space, so a verb universal's
instantiation can be discharged by a membership fact minted from a copula
sentence. It is pure and deterministic. Soundness rides on the ROBDD engine;
these tests pin that the reader hands it the RIGHT problem — in particular
that third-person-singular agreement links a universal's base verb form to a
singular fact's 3sg form via the closed verb relation (NOT the noun table).
"""

from __future__ import annotations

import pytest

from generate.proof_chain.member import MemberRefusal, read_member_argument
from generate.proof_chain.shape import (
    EN_VERB_CHAIN,
    EN_VERB_FACT,
    EN_VERB_NEGATIVE,
    EN_VERB_UNIVERSAL,
)
from generate.proof_chain.verb import (
    MAX_ATOMS,
    MAX_PREMISE_SENTENCES,
    VerbArgument,
    VerbRefusal,
    read_verb_argument,
)


def _read(text: str) -> VerbArgument:
    arg = read_verb_argument(text)
    assert isinstance(arg, VerbArgument), arg
    return arg


def _refusal(text: str) -> VerbRefusal:
    ref = read_verb_argument(text)
    assert isinstance(ref, VerbRefusal), ref
    return ref


# --- the gap this band fills is real -----------------------------------------


def test_the_gap_this_band_fills_is_real() -> None:
    """The exact ADR-0258 §6.3 verb-predicate scope-out: v3-MEM refuses verb
    sentences (no copula ⇒ ``sentence_shape_out_of_band``); this band decides
    them. Both facts hold at once — v3-MEM is unchanged, this is a new tier."""
    text = "All philosophers teach. Socrates is a philosopher. Therefore Socrates teaches."
    assert isinstance(read_member_argument(text), MemberRefusal)
    assert isinstance(read_verb_argument(text), VerbArgument)


# --- the flagship reading -----------------------------------------------------


def test_flagship_universal_verb_instantiation() -> None:
    arg = _read(
        "All philosophers teach. Socrates is a philosopher. Therefore Socrates teaches."
    )
    assert arg.band == EN_VERB_UNIVERSAL
    # Universal instantiates at the one named individual: mem -> verb; the
    # membership fact anchors it; the query is the instantiated verb atom.
    assert arg.premise_formulas == ("(a0) -> (a1)", "a0")
    assert arg.query_formula == "a1"
    assert arg.atoms == ("socrates : philosophers", "socrates : teach")


def test_agreement_links_base_and_third_person_forms() -> None:
    # +s rule: live/lives must land in ONE verb group (and must NOT be routed
    # through the noun table, where "lives" is the plural of "life").
    arg = _read("All men live. Socrates is a man. Therefore Socrates lives.")
    assert arg.query_formula == "a1"  # same atom as the instantiated consequent
    assert "socrates : live" in arg.atoms


@pytest.mark.parametrize(
    "universal_form, conclusion_form",
    [
        ("teach", "teaches"),   # +es after sibilant
        ("study", "studies"),   # y -> ies
        ("go", "goes"),         # irregular table
        ("bark", "barks"),      # +s
    ],
)
def test_agreement_rules_each_link(universal_form: str, conclusion_form: str) -> None:
    arg = _read(
        f"All wolves {universal_form}. Rex is a wolf. Therefore Rex {conclusion_form}."
    )
    assert arg.band == EN_VERB_UNIVERSAL
    assert arg.premise_formulas == ("(a0) -> (a1)", "a0")
    assert arg.query_formula == "a1"


def test_transitive_object_is_part_of_the_atom_key() -> None:
    arg = _read(
        "All poets write verses. Homer is a poet. Therefore Homer writes verses."
    )
    assert arg.query_formula == "a1"
    assert "homer : write verses" in arg.atoms
    # A different object is a DIFFERENT atom — arity/object at face value.
    arg2 = _read(
        "All poets write verses. Homer is a poet. Therefore Homer writes epics."
    )
    assert arg2.query_formula == "a2"


def test_negative_universal_instantiates_negated() -> None:
    arg = _read("Miriam is a nun. No nuns marry. Therefore Miriam does not marry.")
    assert arg.band == EN_VERB_NEGATIVE
    assert arg.premise_formulas == ("a0", "(a0) -> (~(a1))")
    assert arg.query_formula == "~(a1)"


def test_membership_chain_discharges_verb_universal() -> None:
    arg = _read(
        "Felix is a tortoise. All tortoises are reptiles. All reptiles crawl. "
        "Therefore Felix crawls."
    )
    assert arg.band == EN_VERB_CHAIN
    assert arg.premise_formulas == ("a0", "(a0) -> (a1)", "(a1) -> (a2)")
    assert arg.query_formula == "a2"


def test_sentential_not_wraps_a_verb_fact() -> None:
    arg = _read(
        "Boris does not smoke. Therefore it is not the case that Boris smokes."
    )
    assert arg.band == EN_VERB_FACT
    assert arg.premise_formulas == ("~(a0)",)
    assert arg.query_formula == "~(a0)"


def test_universal_does_not_leak_across_individuals() -> None:
    arg = _read(
        "All monks chant. Basil is a monk. Therefore Gregory chants."
    )
    # The universal instantiates at BOTH named individuals; the query is
    # Gregory's verb atom, whose membership antecedent nothing anchors.
    assert arg.premise_formulas == ("(a0) -> (a1)", "(a2) -> (a3)", "a0")
    assert arg.query_formula == "a3"
    assert arg.atoms[2] == "gregory : monks"


def test_verb_and_class_words_never_cross_families() -> None:
    # "teacher" (class) and "teaches" (verb) must stay distinct atoms even
    # though the noun rules could relate the strings.
    arg = _read("Socrates teaches. Therefore Socrates is a teacher.")
    assert arg.premise_formulas == ("a0",)
    assert arg.query_formula == "a1"


# --- band classification ------------------------------------------------------


@pytest.mark.parametrize(
    "text, band",
    [
        ("All poets write. Homer is a poet. Therefore Homer writes.",
         EN_VERB_UNIVERSAL),
        ("Homer is a poet. All poets are artists. All artists dream. Therefore Homer dreams.",
         EN_VERB_CHAIN),
        ("Homer is a poet. No poets whistle. Therefore Homer does not whistle.",
         EN_VERB_NEGATIVE),
        ("Homer writes. Homer is a poet. Therefore Homer writes.",
         EN_VERB_FACT),
    ],
)
def test_band_classification(text: str, band: str) -> None:
    assert _read(text).band == band


# --- typed refusals -----------------------------------------------------------


@pytest.mark.parametrize(
    "text, reason",
    [
        ("Caesar did not surrender. Therefore Caesar surrenders.",
         "tense_out_of_band"),
        ("The old sailor whittles. Therefore Socrates naps.",
         "sentence_shape_out_of_band"),
        ("Nero fiddles in Rome. Therefore Nero fiddles.",
         "sentence_shape_out_of_band"),
        ("Hannah gives Samuel bread. Therefore Hannah gives Samuel bread.",
         "sentence_shape_out_of_band"),
        # "do not" after a multi-token subject: the negation is real but the
        # grammar cannot normalize it (the exact ``<name> does not`` shape is
        # the only one read), so the honest reason is the unread negation.
        ("The twins do not quarrel. Therefore the twins quarrel.",
         "internal_negation_unread"),
        ("If Noah builds then Noah rests. Noah builds. Therefore Noah rests.",
         "mixed_structure_out_of_band"),
        ("Someone sneezes. Therefore Ora sneezes.",
         "quantifier_out_of_band"),
        ("All men do not teach. Socrates is a man. Therefore Socrates teaches.",
         "internal_negation_unread"),
        ("Jonah preaches. Therefore all prophets preach.",
         "universal_conclusion_out_of_band"),
        ("Socrates teaches. Do philosophers teach?",
         "question_sentence"),
        # Delegated copula parses keep v3-MEM's own typed refusals.
        ("Dogs are loyal. Rex barks. Therefore Rex barks.",
         "bare_plural_out_of_band"),
        ("Socrates is the philosopher. Socrates teaches. Therefore Socrates teaches.",
         "definite_description_out_of_band"),
        ("Socrates is a man who teaches. Therefore Socrates teaches.",
         "relative_clause_out_of_band"),
        # A pure-copula argument is never decided by this band (defensive
        # closure — such texts belong to v3-MEM/v4-CM).
        ("Socrates is a man. Therefore Socrates is a man.",
         "sentence_shape_out_of_band"),
    ],
)
def test_typed_refusals(text: str, reason: str) -> None:
    assert _refusal(text).reason == reason


# --- honesty caps -------------------------------------------------------------


def test_premise_cap_refuses_not_truncates() -> None:
    body = " ".join(f"Zed{i} naps." for i in range(MAX_PREMISE_SENTENCES + 1))
    ref = _refusal(body + " Therefore Zed0 naps.")
    assert ref.reason == "too_many_premises"


def test_atom_cap_refuses_not_truncates() -> None:
    # Each premise mints one verb atom; 16 premises fit the premise cap, but
    # a universal instantiated at every individual overflows MAX_ATOMS.
    names = [f"Kip{i}" for i in range(12)]
    body = " ".join(f"{n} naps." for n in names)
    body += " " + " ".join(f"{n} is a squirrel." for n in names[:4])
    text = body + " All squirrels forage. Therefore Kip0 forages."
    ref = _refusal(text)
    assert ref.reason in ("too_many_atoms", "too_many_premises")


# --- determinism --------------------------------------------------------------


def test_reading_is_deterministic() -> None:
    text = (
        "All poets write. Homer is a poet. Therefore Homer writes."
    )
    assert read_verb_argument(text) == read_verb_argument(text)
    assert MAX_ATOMS == 24 and MAX_PREMISE_SENTENCES == 16
