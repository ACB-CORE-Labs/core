"""Band v3-MEM (ADR-0258) — member-argument reader contract.

The reader is pure and deterministic: closed sentence grammar (singular
membership/predicate facts + A/E universals), per-individual propositional
lowering over minted opaque atoms, closed-table number linking, refusal-first
with a typed reason vocabulary, honesty caps. Soundness rides on the ROBDD
engine; these tests pin that the reader hands it the RIGHT problem.
"""

from __future__ import annotations

import pytest

from generate.proof_chain.member import (
    MAX_ATOMS,
    MAX_PREMISE_SENTENCES,
    MemberArgument,
    MemberRefusal,
    read_member_argument,
)
from generate.proof_chain.shape import (
    EN_MEMBER_ATOMIC,
    EN_MEMBER_CHAIN,
    EN_MEMBER_NEGATIVE,
    EN_MEMBER_SINGLE,
)


def _read(text: str) -> MemberArgument:
    arg = read_member_argument(text)
    assert isinstance(arg, MemberArgument), arg
    return arg


def _refusal(text: str) -> MemberRefusal:
    ref = read_member_argument(text)
    assert isinstance(ref, MemberRefusal), ref
    return ref


# --- the flagship reading -----------------------------------------------------


def test_flagship_socrates_reads_as_instantiated_modus_ponens() -> None:
    arg = _read("Socrates is a man. All men are mortal. Therefore Socrates is mortal.")
    # "men" links to "man" (irregular table) — the universal instantiates at
    # Socrates over the SAME atom the first premise minted.
    assert arg.premise_formulas == ("a0", "(a0) -> (a1)")
    assert arg.query_formula == "a1"
    assert arg.premise_texts == ("socrates is a man", "all men are mortal")
    assert arg.query_text == "socrates is mortal"
    assert arg.band == EN_MEMBER_SINGLE
    assert len(arg.atoms) == 2


def test_universal_before_singular_reads_identically() -> None:
    arg = _read("Every man is mortal. Socrates is a man. Therefore Socrates is mortal.")
    # Two-pass lowering: the universal instantiates at individuals introduced
    # LATER — premise formula order stays sentence order.
    assert arg.premise_formulas == ("(a0) -> (a1)", "a0")
    assert arg.query_formula == "a1"


def test_universal_instantiates_at_every_named_individual() -> None:
    arg = _read(
        "Plato is a man. Aristotle is a man. All men are mortal. "
        "Therefore Aristotle is mortal."
    )
    assert arg.premise_formulas == (
        "a0", "a1", "(a0) -> (a2)", "(a1) -> (a3)",
    )
    assert arg.query_formula == "a3"
    assert len(arg.atoms) == 4


def test_negative_universal_lowers_to_negated_consequent() -> None:
    arg = _read("Fido is a dog. No dogs are cats. Therefore Fido is not a cat.")
    assert arg.premise_formulas == ("a0", "(a0) -> (~(a1))")
    assert arg.query_formula == "~(a1)"
    assert arg.band == EN_MEMBER_NEGATIVE


def test_membership_chain_through_plural_links() -> None:
    arg = _read(
        "Rex is a dog. All dogs are mammals. All mammals are animals. "
        "Therefore Rex is an animal."
    )
    assert arg.premise_formulas == ("a0", "(a0) -> (a1)", "(a1) -> (a2)")
    assert arg.query_formula == "a2"
    assert arg.band == EN_MEMBER_CHAIN


def test_atomic_band_negation_forms() -> None:
    contraction = _read("Rex isn't a cat. Therefore Rex is not a cat.")
    assert contraction.premise_formulas == ("~(a0)",)
    assert contraction.query_formula == "~(a0)"
    assert contraction.band == EN_MEMBER_ATOMIC

    sentential = _read("It is not the case that Rex is a cat. Therefore Rex is not a cat.")
    assert sentential.premise_formulas == ("~(a0)",)
    assert sentential.query_formula == "~(a0)"


def test_case_and_comma_normalization() -> None:
    arg = _read("SOCRATES IS A MAN. All men are mortal. Therefore, Socrates is mortal.")
    assert arg.premise_formulas == ("a0", "(a0) -> (a1)")
    assert arg.query_text == "socrates is mortal"


# --- number linking (the closed morphology table) -----------------------------


@pytest.mark.parametrize(
    ("singular", "plural"),
    [
        ("man", "men"),            # irregular table
        ("person", "people"),      # irregular table
        ("child", "children"),     # irregular table
        ("wolf", "wolves"),        # irregular table
        ("sheep", "sheep"),        # invariant
        ("dog", "dogs"),           # regular +s
        ("fox", "foxes"),          # regular +es
        ("pony", "ponies"),        # regular y↔ies
    ],
)
def test_number_linking_identifies_the_class(singular: str, plural: str) -> None:
    arg = _read(
        f"Kai is a {singular}. All {plural} are calm. Therefore Kai is calm."
    )
    assert arg.premise_formulas == ("a0", "(a0) -> (a1)")
    assert arg.query_formula == "a1"


def test_multi_token_class_links_on_head_noun() -> None:
    arg = _read(
        "Rex is a guard dog. All guard dogs are loyal. Therefore Rex is loyal."
    )
    assert arg.premise_formulas == ("a0", "(a0) -> (a1)")


@pytest.mark.parametrize(
    ("form_a", "form_b"),
    [
        ("specie", "species"),  # invariant-table priority blocks the +s rule
        ("new", "news"),        # "news" is not the plural of "new"
    ],
)
def test_hazard_pairs_stay_distinct_classes(form_a: str, form_b: str) -> None:
    arg = _read(
        f"Kai is a {form_a}. All {form_b} are calm. Therefore Kai is calm."
    )
    # No link ⇒ the universal instantiates over a DIFFERENT class atom ⇒ the
    # conclusion is honestly unforced (a1 vs the a0 fact) — never a false link.
    assert arg.premise_formulas == ("a0", "(a1) -> (a2)")
    assert arg.query_formula == "a2"


# --- band classification ------------------------------------------------------


@pytest.mark.parametrize(
    ("text", "band"),
    [
        ("Bo is a cat. Therefore Bo is a cat.", EN_MEMBER_ATOMIC),
        ("Bo is a cat. All cats are quick. Therefore Bo is quick.", EN_MEMBER_SINGLE),
        (
            "Bo is a cat. All cats are hunters. All hunters are quick. "
            "Therefore Bo is quick.",
            EN_MEMBER_CHAIN,
        ),
        (
            "Bo is a cat. All cats are hunters. No hunters are tame. "
            "Therefore Bo is not tame.",
            EN_MEMBER_NEGATIVE,
        ),
    ],
)
def test_band_classification(text: str, band: str) -> None:
    assert _read(text).band == band


# --- typed refusals -----------------------------------------------------------


@pytest.mark.parametrize(
    ("text", "reason"),
    [
        ("Some men are wise. Socrates is a man. Therefore Socrates is wise.", "quantifier_out_of_band"),
        ("Everyone is mortal. Therefore Socrates is mortal.", "quantifier_out_of_band"),
        ("Nobody is a saint. Therefore Socrates is not a saint.", "quantifier_out_of_band"),
        ("Dogs are loyal. Rex is a dog. Therefore Rex is loyal.", "bare_plural_out_of_band"),
        ("Socrates is the philosopher. All philosophers are wise. Therefore Socrates is wise.", "definite_description_out_of_band"),
        ("Rex is a dog that barks. All dogs are loyal. Therefore Rex is loyal.", "relative_clause_out_of_band"),
        ("Socrates is a man. Therefore all men are mortal.", "universal_conclusion_out_of_band"),
        ("If Socrates is a man then Socrates is mortal. Therefore Socrates is mortal.", "mixed_structure_out_of_band"),
        ("Socrates is a man or a god. Therefore Socrates is a man.", "mixed_structure_out_of_band"),
        ("Rex never barks. Therefore Rex is loyal.", "sentence_shape_out_of_band"),
        ("Socrates was a man. All men are mortal. Therefore Socrates is mortal.", "sentence_shape_out_of_band"),
        ("Is Socrates a man? Therefore Socrates is a man.", "question_sentence"),
        ("Socrates is a man. Socrates is mortal.", "no_conclusion"),
        ("Therefore Socrates is a man.", "no_premises"),
        ("Socrates is a man. Therefore Socrates is a man. Rex is a dog.", "conclusion_not_last"),
        ("", "empty"),
    ],
)
def test_typed_refusals(text: str, reason: str) -> None:
    assert _refusal(text).reason == reason


# --- honesty caps -------------------------------------------------------------


def test_premise_cap_refuses_not_truncates() -> None:
    facts = " ".join(f"N{i} is a cat." for i in range(MAX_PREMISE_SENTENCES + 1))
    ref = _refusal(f"{facts} Therefore N0 is a cat.")
    assert ref.reason == "too_many_premises"


def test_atom_cap_refuses_not_truncates() -> None:
    # 13 individuals × 2 classes = 26 minted pairs > MAX_ATOMS=24, within the
    # premise cap (13 facts + 1 universal = 14 sentences).
    n = MAX_ATOMS // 2 + 1
    facts = " ".join(f"N{i} is a dog." for i in range(n))
    ref = _refusal(f"{facts} All dogs are cats. Therefore N0 is a cat.")
    assert ref.reason == "too_many_atoms"


# --- determinism --------------------------------------------------------------


def test_reading_is_deterministic() -> None:
    text = (
        "Tara is a person. All people are mortal. No immortals are people. "
        "Therefore Tara is mortal."
    )
    assert read_member_argument(text) == read_member_argument(text)
