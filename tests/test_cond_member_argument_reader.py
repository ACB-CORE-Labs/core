"""Band v4-CM (ADR-0259) — conditional-membership argument reader contract.

The reader composes v2-EN's connective grammar (if/then, or, and, either)
with v3-MEM's singular-membership sentence reading over ONE shared
per-individual atom space. It is pure and deterministic. Soundness rides on
the ROBDD engine; these tests pin that the reader hands it the RIGHT problem
— in particular that a bare universal's instantiated atom correctly UNIFIES
with a connective leaf's atom when the two mechanisms share a class (the
"fusion" this band is named for).
"""

from __future__ import annotations

import pytest

from generate.proof_chain.cond_member import (
    MAX_ATOMS,
    MAX_PREMISE_SENTENCES,
    CondMemberArgument,
    CondMemberRefusal,
    read_cond_member_argument,
)
from generate.proof_chain.member import MemberRefusal, read_member_argument
from generate.proof_chain.shape import (
    EN_CONDMEM_CHAIN,
    EN_CONDMEM_CONDITIONAL,
    EN_CONDMEM_DISJUNCTIVE,
    EN_CONDMEM_FUSED,
)


def _read(text: str) -> CondMemberArgument:
    arg = read_cond_member_argument(text)
    assert isinstance(arg, CondMemberArgument), arg
    return arg


def _refusal(text: str) -> CondMemberRefusal:
    ref = read_cond_member_argument(text)
    assert isinstance(ref, CondMemberRefusal), ref
    return ref


# --- the composition itself: what v3-MEM refuses, this band decides ----------


def test_the_gap_this_band_fills_is_real() -> None:
    """The exact ADR-0258 §6.1 scope-out: v3-MEM refuses this shape in
    isolation (pinned in test_member_argument_reader.py); this band decides
    it. Both facts hold at once — v3-MEM is unchanged, this is a new tier."""
    text = "If Socrates is a man then Socrates is mortal. Socrates is a man. Therefore Socrates is mortal."
    assert isinstance(read_member_argument(text), MemberRefusal)
    assert isinstance(read_cond_member_argument(text), CondMemberArgument)


# --- the flagship reading -----------------------------------------------------


def test_flagship_socrates_reads_as_conditional_modus_ponens() -> None:
    arg = _read(
        "If Socrates is a man then Socrates is mortal. Socrates is a man. "
        "Therefore Socrates is mortal."
    )
    assert arg.premise_formulas == ("(a0) -> (a1)", "a0")
    assert arg.query_formula == "a1"
    assert arg.premise_texts == (
        "if socrates is a man then socrates is mortal", "socrates is a man",
    )
    assert arg.query_text == "socrates is mortal"
    assert arg.band == EN_CONDMEM_CONDITIONAL
    assert len(arg.atoms) == 2


def test_modus_tollens_over_membership_atoms() -> None:
    arg = _read(
        "If Socrates is a man then Socrates is mortal. Socrates is not mortal. "
        "Therefore Socrates is not a man."
    )
    assert arg.premise_formulas == ("(a0) -> (a1)", "~(a1)")
    assert arg.query_formula == "~(a0)"


def test_or_disjunctive_syllogism() -> None:
    arg = _read(
        "Socrates is a man or Socrates is a god. Socrates is not a god. "
        "Therefore Socrates is a man."
    )
    assert arg.premise_formulas == ("(a0) | (a1)", "~(a1)")
    assert arg.query_formula == "a0"
    assert arg.band == EN_CONDMEM_DISJUNCTIVE


def test_either_spelling_disjunctive_syllogism() -> None:
    arg = _read(
        "Either Socrates is a man or Socrates is a god. Socrates is not a man. "
        "Therefore Socrates is a god."
    )
    assert arg.premise_formulas == ("(a0) | (a1)", "~(a0)")
    assert arg.query_formula == "a1"


def test_and_split_premise_is_two_bare_records_not_a_connective() -> None:
    """A top-level "X and Y" PREMISE (no if/or) splits into independent
    singular records — identical to conjoining, mirroring v2-EN exactly —
    rather than building an ``&`` formula."""
    arg = _read(
        "Socrates is a man and Plato is a man. All men are mortal. "
        "Therefore Socrates is mortal."
    )
    # The universal instantiates at EVERY named individual (Socrates AND
    # Plato), each producing its own freshly-minted consequent atom.
    assert arg.premise_formulas == ("a0", "a1", "(a0) -> (a2)", "(a1) -> (a3)")
    assert arg.query_formula == "a2"
    assert arg.premise_texts == (
        "socrates is a man and plato is a man", "all men are mortal",
    )


def test_two_hop_chain() -> None:
    arg = _read(
        "If Socrates is a man then Socrates is a philosopher. "
        "If Socrates is a philosopher then Socrates is wise. "
        "Socrates is a man. Therefore Socrates is wise."
    )
    assert arg.premise_formulas == ("(a0) -> (a1)", "(a1) -> (a2)", "a0")
    assert arg.query_formula == "a2"
    assert arg.band == EN_CONDMEM_CHAIN


# --- the fusion mechanism: universal instantiation UNIFIES with a connective
# leaf's atom via the SAME closed morphology relation ------------------------


def test_universal_instantiation_unifies_with_connective_leaf() -> None:
    """The mechanism this band is named for: "all MEN are mortal" instantiates
    Socrates : men -> Socrates : mortal via the SAME atom the connective's
    consequent leaf mints for "Socrates is a man" (linked man<->men)."""
    arg = _read(
        "All men are mortal. If Socrates is a philosopher then Socrates is a man. "
        "Socrates is a philosopher. Therefore Socrates is mortal."
    )
    assert arg.premise_formulas == ("(a0) -> (a1)", "(a2) -> (a0)", "a2")
    assert arg.query_formula == "a1"
    assert arg.band == EN_CONDMEM_FUSED
    assert len(arg.atoms) == 3


def test_fusion_reversed_sentence_order_reads_identically() -> None:
    arg = _read(
        "If Socrates is a philosopher then Socrates is a man. All men are mortal. "
        "Socrates is a philosopher. Therefore Socrates is mortal."
    )
    # The connective mints philosopher/man first (a0/a1); the universal's
    # antecedent REUSES a1 (men links to man), minting only mortal fresh (a2).
    assert arg.premise_formulas == ("(a0) -> (a1)", "(a1) -> (a2)", "a0")
    assert arg.query_formula == "a2"
    assert arg.band == EN_CONDMEM_FUSED


def test_fusion_does_not_leak_across_individuals() -> None:
    """Instantiating a bare universal for MULTIPLE named individuals must not
    let one individual's fact force another's conclusion."""
    arg = _read(
        "All men are mortal. If Plato is a philosopher then Plato is a man. "
        "Socrates is a man. Therefore Plato is mortal."
    )
    # mortal(plato) needs man(plato), which needs philosopher(plato) — never
    # asserted; socrates's fact is irrelevant to the query.
    from generate.proof_chain.entail import Entailment, evaluate_entailment_with_trace

    outcome = evaluate_entailment_with_trace(arg.premise_formulas, arg.query_formula).outcome
    assert outcome is Entailment.UNKNOWN


# --- band classification ------------------------------------------------------


@pytest.mark.parametrize(
    ("text", "band"),
    [
        (
            "If Bo is a cat then Bo is quick. Bo is a cat. Therefore Bo is quick.",
            EN_CONDMEM_CONDITIONAL,
        ),
        (
            "Bo is a cat or Bo is a dog. Bo is not a cat. Therefore Bo is a dog.",
            EN_CONDMEM_DISJUNCTIVE,
        ),
        (
            "If Bo is a cat then Bo is a hunter. If Bo is a hunter then Bo is quick. "
            "Bo is a cat. Therefore Bo is quick.",
            EN_CONDMEM_CHAIN,
        ),
        (
            "All cats are hunters. If Bo is a stray then Bo is a cat. Bo is a stray. "
            "Therefore Bo is a hunter.",
            EN_CONDMEM_FUSED,
        ),
    ],
)
def test_band_classification(text: str, band: str) -> None:
    assert _read(text).band == band


# --- typed refusals -----------------------------------------------------------


@pytest.mark.parametrize(
    ("text", "reason"),
    [
        (
            "If the door is open then if the window is open then the room is cold. "
            "Therefore the room is cold.",
            "nested_conditional",
        ),
        (
            "The car is red and the car is fast or the car is loud. "
            "Therefore the car is fast.",
            "ambiguous_and_or",
        ),
        (
            "If Socrates is a man then Socrates is mortal. Socrates is a man. "
            "Therefore Socrates is mortal and Socrates is wise.",
            "compound_conclusion_out_of_band",
        ),
        (
            "Socrates is a man. Therefore all men are mortal.",
            "universal_conclusion_out_of_band",
        ),
        (
            "If someone is a suspect then someone is questioned. "
            "Therefore someone is questioned.",
            "quantifier_out_of_band",
        ),
        (
            "If Socrates is a man then dogs are loyal. Socrates is a man. "
            "Therefore dogs are loyal.",
            "bare_plural_out_of_band",
        ),
        (
            "If Socrates is a man then Socrates is the philosopher. Socrates is a man. "
            "Therefore Socrates is the philosopher.",
            "definite_description_out_of_band",
        ),
        (
            "If Socrates is a man then the dog that barks is loud. Socrates is a man. "
            "Therefore the dog that barks is loud.",
            "relative_clause_out_of_band",
        ),
        (
            "If Socrates was a man then Socrates was mortal. Socrates is a man. "
            "Therefore Socrates is mortal.",
            "sentence_shape_out_of_band",
        ),
        ("Is Socrates a man? Therefore Socrates is mortal.", "question_sentence"),
        (
            "If Socrates is a man then Socrates is mortal. Socrates is a man.",
            "no_conclusion",
        ),
        ("Therefore Socrates is mortal.", "no_premises"),
        (
            "If Socrates is a man then Socrates is mortal. "
            "Therefore Socrates is mortal. Plato is a man.",
            "conclusion_not_last",
        ),
        ("", "empty"),
    ],
)
def test_typed_refusals(text: str, reason: str) -> None:
    assert _refusal(text).reason == reason


# --- honesty caps -------------------------------------------------------------


def test_premise_cap_refuses_not_truncates() -> None:
    facts = " ".join(f"N{i} is a cat." for i in range(MAX_PREMISE_SENTENCES))
    text = f"If Bo is a cat then Bo is quick. {facts} Therefore N0 is a cat."
    ref = _refusal(text)
    assert ref.reason == "too_many_premises"


def test_atom_cap_refuses_not_truncates() -> None:
    n = MAX_ATOMS // 2 + 1
    facts = " ".join(f"N{i} is a dog." for i in range(n))
    ref = _refusal(
        f"If Bo is a dog then Bo is loyal. {facts} All dogs are cats. "
        f"Therefore N0 is a cat."
    )
    assert ref.reason == "too_many_atoms"


# --- determinism --------------------------------------------------------------


def test_reading_is_deterministic() -> None:
    text = (
        "All men are mortal. If Socrates is a philosopher then Socrates is a man. "
        "Socrates is a philosopher. Therefore Socrates is mortal."
    )
    assert read_cond_member_argument(text) == read_cond_member_argument(text)
