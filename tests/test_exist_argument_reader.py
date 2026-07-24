"""Band v6-EX (ADR-0261) — existential argument reader contract.

The reader completes the all/no/some square by widening v5-VP's per-individual
domain with a Skolem WITNESS per existential premise and one ARBITRARY element
per existential conclusion, then lowering an existential conclusion to the
disjunction over that whole domain. It is pure and deterministic. Soundness
rides on the ROBDD engine; these tests pin that the reader hands it the RIGHT
problem — above all that the arbitrary element is present, since without it an
existential conclusion would be "refuted" by domain closure, which is the one
way this lowering could be unsound.
"""

from __future__ import annotations

import pytest

from generate.proof_chain.entail import Entailment, evaluate_entailment_with_trace
from generate.proof_chain.exist import (
    MAX_ATOMS,
    MAX_PREMISE_SENTENCES,
    ExistArgument,
    ExistRefusal,
    read_exist_argument,
)
from generate.proof_chain.shape import (
    EN_EXIST_CHAIN,
    EN_EXIST_NEGATIVE,
    EN_EXIST_UNIVERSAL,
    EN_EXIST_WITNESS,
)
from generate.proof_chain.verb import VerbRefusal, read_verb_argument


def _read(text: str) -> ExistArgument:
    arg = read_exist_argument(text)
    assert isinstance(arg, ExistArgument), arg
    return arg


def _refusal(text: str) -> ExistRefusal:
    ref = read_exist_argument(text)
    assert isinstance(ref, ExistRefusal), ref
    return ref


def _decide(text: str) -> Entailment:
    arg = _read(text)
    return evaluate_entailment_with_trace(arg.premise_formulas, arg.query_formula).outcome


# --- the gap this band fills is real -----------------------------------------


def test_the_gap_this_band_fills_is_real() -> None:
    """Every earlier fallback band refuses a ``some``-led sentence (v5-VP is
    the last of them, via ``quantifier_out_of_band``); this band reads it.
    Both facts hold at once — v5-VP is unchanged, this is a new tier."""
    text = "All mammals are vertebrates. Some whales are mammals. Therefore some whales are vertebrates."
    v5 = read_verb_argument(text)
    assert isinstance(v5, VerbRefusal) and v5.reason == "quantifier_out_of_band"
    assert isinstance(read_exist_argument(text), ExistArgument)


# --- the flagship reading -----------------------------------------------------


def test_flagship_darii_lowering() -> None:
    arg = _read(
        "All mammals are vertebrates. Some whales are mammals. "
        "Therefore some whales are vertebrates."
    )
    assert arg.band == EN_EXIST_UNIVERSAL
    # The universal instantiates at BOTH domain elements (witness + arbitrary);
    # the existential premise is the witness conjunction; the query is the
    # disjunction of the conclusion's conjunction over the whole domain.
    assert arg.premise_formulas == ("(a0) -> (a1)", "(a2) -> (a3)", "(a4) & (a0)")
    assert arg.query_formula == "((a4) & (a1)) | ((a5) & (a3))"
    assert arg.atoms == (
        "witness 1 : mammals",
        "witness 1 : vertebrates",
        "any individual : mammals",
        "any individual : vertebrates",
        "witness 1 : whales",
        "any individual : whales",
    )
    assert _decide(
        "All mammals are vertebrates. Some whales are mammals. "
        "Therefore some whales are vertebrates."
    ) is Entailment.ENTAILED


def test_arbitrary_element_keeps_the_domain_open() -> None:
    """THE soundness test. Every NAMED wolf here fails to be tame, so a
    witness-only lowering would report REFUTED — asserting that no wolf
    anywhere is tame. The arbitrary element is what makes the honest UNKNOWN
    come out, and it must be visibly in the atom set."""
    text = "Rex is a wolf. Rex is not tame. Therefore some wolves are tame."
    arg = _read(text)
    assert "any individual : wolf" in arg.atoms
    assert "any individual : tame" in arg.atoms
    assert _decide(text) is Entailment.UNKNOWN


def test_no_existential_import() -> None:
    """A universal says nothing about whether its class has members — the
    subaltern moods are UNKNOWN under the modern reading this band uses."""
    assert _decide("All unicorns are horned. Therefore some unicorns are horned.") is (
        Entailment.UNKNOWN
    )


@pytest.mark.parametrize(
    "text",
    [
        # A and O are contradictories — the A-form refutes the O-form.
        "All squares are rectangles. Therefore some squares are not rectangles.",
        # E and I are contradictories — the E-form refutes the I-form.
        "No fish are mammals. Therefore some fish are mammals.",
    ],
)
def test_contradictories_of_the_square_refute(text: str) -> None:
    assert _decide(text) is Entailment.REFUTED


def test_witness_never_transfers_to_a_named_individual() -> None:
    text = "Some sailors are brave. Magellan is a sailor. Therefore Magellan is brave."
    assert _decide(text) is Entailment.UNKNOWN


def test_each_existential_premise_gets_its_own_witness() -> None:
    arg = _read(
        "Some wolves are tame. Some wolves are swift. Therefore some tame are swift."
    )
    assert "witness 1 : wolves" in arg.atoms
    assert "witness 2 : wolves" in arg.atoms
    # Two witnesses + the arbitrary element ⇒ three query disjuncts.
    assert arg.query_formula.count("|") == 2
    assert _decide(
        "Some wolves are tame. Some wolves are swift. Therefore some tame are swift."
    ) is Entailment.UNKNOWN


def test_a_named_individual_can_be_the_witness() -> None:
    assert _decide(
        "Socrates is a philosopher. Socrates is wise. Therefore some philosophers are wise."
    ) is Entailment.ENTAILED


def test_i_form_converts() -> None:
    arg = _read("Some philosophers are Greeks. Therefore some Greeks are philosophers.")
    assert arg.band == EN_EXIST_WITNESS
    assert arg.premise_formulas == ("(a0) & (a1)",)
    assert arg.query_formula == "((a1) & (a0)) | ((a2) & (a3))"


def test_o_form_witness_carries_the_negation() -> None:
    arg = _read("Some hermits are not sociable. Therefore some hermits are not sociable.")
    assert arg.premise_formulas == ("(a0) & (~(a1))",)
    assert arg.query_formula == "((a0) & (~(a1))) | ((a2) & (~(a3)))"


def test_verb_existentials_ride_the_verb_atom_family() -> None:
    """Ferio over a verb predicate, with the plural ``do not`` O-form that
    v5-VP refuses (there it is genuinely ambiguous; under ``some`` it is not)."""
    text = (
        "No reptiles nurse young. Some lizards are reptiles. "
        "Therefore some lizards do not nurse young."
    )
    arg = _read(text)
    assert arg.band == EN_EXIST_NEGATIVE
    assert "witness 1 : nurse young" in arg.atoms
    assert _decide(text) is Entailment.ENTAILED


def test_number_linking_applies_inside_existentials() -> None:
    """The irregular table (goose/geese) links a singular universal to a plural
    existential — the same closed relation v3-MEM earned, no new authority."""
    text = "Every goose is a bird. Some geese are gray. Therefore some birds are gray."
    arg = _read(text)
    assert "witness 1 : goose" in arg.atoms  # both forms landed in ONE group
    assert _decide(text) is Entailment.ENTAILED


# --- band classification ------------------------------------------------------


@pytest.mark.parametrize(
    "text, band",
    [
        ("Some poets are Greeks. Therefore some Greeks are poets.",
         EN_EXIST_WITNESS),
        ("All poets are artists. Some Greeks are poets. Therefore some Greeks are artists.",
         EN_EXIST_UNIVERSAL),
        ("Some Greeks are poets. All poets are artists. All artists are rare. "
         "Therefore some Greeks are rare.",
         EN_EXIST_CHAIN),
        ("No poets are silent. Some Greeks are poets. Therefore some Greeks are not silent.",
         EN_EXIST_NEGATIVE),
    ],
)
def test_band_classification(text: str, band: str) -> None:
    assert _read(text).band == band


# --- typed refusals -----------------------------------------------------------


@pytest.mark.parametrize(
    "text, reason",
    [
        ("Some of the sailors are brave. Therefore some sailors are brave.",
         "partitive_out_of_band"),
        ("Some sailors were brave. Therefore some sailors are brave.",
         "tense_out_of_band"),
        ("Some sailors did not return. Therefore some sailors return.",
         "tense_out_of_band"),
        # Singular agreement under a plural existential subject is not read.
        ("Some sailors does not sail. Therefore some sailors sail.",
         "sentence_shape_out_of_band"),
        ("Some old sailors whittle driftwood. Therefore some sailors whittle driftwood.",
         "sentence_shape_out_of_band"),
        ("If some sailors are brave then the ship sails. Some sailors are brave. "
         "Therefore the ship sails.",
         "mixed_structure_out_of_band"),
        ("Most sailors are brave. Therefore some sailors are brave.",
         "quantifier_out_of_band"),
        ("Some sailors are brave. Therefore all sailors are brave.",
         "universal_conclusion_out_of_band"),
        ("Some sailors are brave. Do some sailors sing?", "question_sentence"),
        # Delegated v3-MEM / v5-VP parses keep their own typed refusals.
        ("Some sailors who fish are brave. Therefore some sailors are brave.",
         "relative_clause_out_of_band"),
        ("Some sailors are the crew. Therefore some crew are sailors.",
         "definite_description_out_of_band"),
        ("All sailors do not sail. Some sailors are brave. Therefore some sailors sail.",
         "internal_negation_unread"),
        # An argument with no existential at all is never decided here
        # (defensive closure — those texts belong to v3-MEM / v5-VP).
        ("Socrates is a man. All men are mortal. Therefore Socrates is mortal.",
         "sentence_shape_out_of_band"),
    ],
)
def test_typed_refusals(text: str, reason: str) -> None:
    assert _refusal(text).reason == reason


# --- honesty caps -------------------------------------------------------------


def test_premise_cap_refuses_not_truncates() -> None:
    body = " ".join(f"Zed{i} naps." for i in range(MAX_PREMISE_SENTENCES + 1))
    ref = _refusal(body + " Therefore some sailors nap.")
    assert ref.reason == "too_many_premises"


def test_atom_cap_refuses_not_truncates() -> None:
    """Existential conclusions mint up to two atoms per domain element, so the
    cap binds on the query too — and refuses rather than dropping a disjunct
    (a dropped disjunct is exactly how a false REFUTED would appear)."""
    body = " ".join(f"Some crews{i} are brave." for i in range(8))
    ref = _refusal(body + " Therefore some crews0 are swift.")
    assert ref.reason in ("too_many_atoms", "too_many_premises")


# --- determinism --------------------------------------------------------------


def test_reading_is_deterministic() -> None:
    text = "All poets are artists. Some Greeks are poets. Therefore some Greeks are artists."
    assert read_exist_argument(text) == read_exist_argument(text)
    assert MAX_ATOMS == 24 and MAX_PREMISE_SENTENCES == 16
