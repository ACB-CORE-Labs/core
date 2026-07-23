"""Band v2-EN (ADR-0257) — English-clause argument reader contract.

Pins the closed function-word grammar of ``generate.proof_chain.english``:

  - structure recognition (conditional / disjunction / conjunction / the three
    negation forms) over OPAQUE clause-atoms, with atom identity by normalized
    exact text (same clause → same atom; distinct wording → distinct atoms);
  - the ``en_*`` shape-band classification the earned license keys on;
  - every structural guard that keeps the substitution-soundness argument
    airtight: quantifier-led categorical clauses, is-a membership clauses, and
    unnormalizable negation all REFUSE out of the opaque band (typed);
  - determinism (same text → same reading).
"""

from __future__ import annotations

import pytest

from generate.proof_chain.english import (
    EnglishArgument,
    EnglishRefusal,
    read_english_argument,
)
from generate.proof_chain.shape import (
    EN_ATOMIC,
    EN_CONDITIONAL_CHAIN,
    EN_CONDITIONAL_SINGLE,
    EN_DISJUNCTIVE,
)


def _read(text: str) -> EnglishArgument:
    arg = read_english_argument(text)
    assert isinstance(arg, EnglishArgument), getattr(arg, "reason", arg)
    return arg


def _refusal(text: str) -> EnglishRefusal:
    arg = read_english_argument(text)
    assert isinstance(arg, EnglishRefusal), arg
    return arg


# ---------------------------------------------------------------------------
# Structure recognition
# ---------------------------------------------------------------------------


def test_modus_ponens_reads_to_implication_and_shared_atom() -> None:
    arg = _read("If it rains then the ground is wet. It rains. Therefore the ground is wet.")
    assert arg.premise_formulas == ("(a0) -> (a1)", "a0")
    assert arg.query_formula == "a1"
    assert arg.atoms == ("it rains", "the ground is wet")
    assert arg.band == EN_CONDITIONAL_SINGLE
    assert arg.premise_texts == ("if it rains then the ground is wet", "it rains")
    assert arg.query_text == "the ground is wet"


def test_atom_identity_is_normalized_exact_text() -> None:
    """Case and commas normalize away; different wording stays distinct."""
    arg = _read("The Report Is Filed. Therefore the report is filed.")
    assert arg.premise_formulas == ("a0",)
    assert arg.query_formula == "a0"  # same atom — case-insensitive identity

    distinct = _read("The report is filed. Therefore the report was filed.")
    assert distinct.premise_formulas == ("a0",)
    assert distinct.query_formula == "a1"  # tense differs → distinct atom


def test_copular_negation_normalizes_to_engine_negation() -> None:
    arg = _read(
        "If the alarm is armed then the light is on. The light is not on. "
        "Therefore the alarm is not armed."
    )
    assert arg.premise_formulas == ("(a0) -> (a1)", "~(a1)")
    assert arg.query_formula == "~(a0)"
    assert arg.atoms == ("the alarm is armed", "the light is on")


def test_contractions_and_sentential_negation_normalize() -> None:
    arg = _read("The door isn't open. Therefore it is not the case that the door is open.")
    assert arg.premise_formulas == ("~(a0)",)
    assert arg.query_formula == "~(a0)"
    assert arg.atoms == ("the door is open",)


def test_leading_not_negates_inside_a_conditional() -> None:
    """Nested negation in conditional slots — the formerly-out-of-band
    contraposition shape."""
    arg = _read("If p then q. Therefore if not q then not p.")
    assert arg.premise_formulas == ("(a0) -> (a1)",)
    assert arg.query_formula == "(~(a1)) -> (~(a0))"


def test_either_or_reads_to_disjunction() -> None:
    arg = _read("Either the door is open or the window is open. Therefore the door is open.")
    assert arg.premise_formulas == ("(a0) | (a1)",)
    assert arg.band == EN_DISJUNCTIVE


def test_top_level_and_premise_splits_into_premises() -> None:
    arg = _read("The oven is hot and the dough is ready. Therefore the dough is ready.")
    assert arg.premise_formulas == ("a0", "a1")
    assert arg.premise_texts == ("the oven is hot and the dough is ready",)
    assert arg.band == EN_ATOMIC


def test_conjunction_and_disjunction_conclusions() -> None:
    conj = _read("The kettle is boiling. The toast is ready. Therefore the kettle is boiling and the toast is ready.")
    assert conj.query_formula == "(a0) & (a1)"
    disj = _read("The train is late. Therefore the train is late or the bus is early.")
    assert disj.query_formula == "(a0) | (a1)"


def test_conditional_conclusion_reads() -> None:
    arg = _read(
        "If it rains then the ground is wet. If the ground is wet then the match is "
        "cancelled. Therefore if it rains then the match is cancelled."
    )
    assert arg.band == EN_CONDITIONAL_CHAIN
    assert arg.query_formula == "(a0) -> (a2)"


def test_disjunctive_antecedent_inside_conditional() -> None:
    arg = _read("If the pump runs or the valve opens then the tank fills. Therefore the tank fills.")
    assert arg.premise_formulas == ("((a0) | (a1)) -> (a2)",)
    # band keys on a disjunction appearing in the premises
    assert arg.band == EN_DISJUNCTIVE


# ---------------------------------------------------------------------------
# Band classification
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("text,band", [
    ("If a is set then b is set. a is set. Therefore b is set.", EN_CONDITIONAL_SINGLE),
    ("If a is set then b is set. If b is set then c is set. Therefore c is set.", EN_CONDITIONAL_CHAIN),
    ("The cat is in or the dog is in. Therefore the cat is in.", EN_DISJUNCTIVE),
    ("The cat is in. Therefore the cat is in.", EN_ATOMIC),
])
def test_band_classification(text: str, band: str) -> None:
    assert _read(text).band == band


# ---------------------------------------------------------------------------
# Structural guards — the soundness perimeter (typed refusals)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("text,reason", [
    # Quantifier-led clause = categorical structure the opaque band must not flatten.
    ("All whales are mammals. Therefore all whales are mammals.", "categorical_shape_out_of_band"),
    ("Some doors are open. Therefore some doors are open.", "categorical_shape_out_of_band"),
    # is-a membership clause — reserved for a future member_chain band.
    ("Socrates is a man. Therefore Socrates is a man.", "membership_shape_out_of_band"),
    # Negation this band cannot normalize must not hide inside an opaque atom.
    ("It never snows. Therefore it never snows.", "internal_negation_unread"),
    ("The engine doesn't start. Therefore the engine doesn't start.", "internal_negation_unread"),
    ("The tank does not fill. Therefore the tank does not fill.", "internal_negation_unread"),
    # Genuinely ambiguous English scope refuses rather than guessing.
    ("The fan spins and the light is on or the door is open. Therefore the door is open.", "ambiguous_and_or"),
    # Nested conditionals are out of the v2-EN grammar.
    ("If the door is open then if the fan spins then the light is on. Therefore the light is on.", "nested_conditional"),
    # Questions are not premises.
    ("Is the door open? Therefore the door is open.", "question_sentence"),
    # The conclusion must be the final sentence, and unique.
    ("Therefore the door is open. The door is open.", "conclusion_not_last"),
    ("The door is open. Therefore the door is open. Therefore the window is open.", "conclusion_not_last"),
    # An argument needs both parts.
    ("Therefore the door is open.", "no_premises"),
    ("The door is open. The window is open.", "no_conclusion"),
    # Structural emptiness.
    ("If then the light is on. Therefore the light is on.", "empty_side"),
])
def test_typed_refusals(text: str, reason: str) -> None:
    assert _refusal(text).reason == reason


def test_atom_cap_refuses_rather_than_truncating() -> None:
    # 13 disjunctive premises mint 26 distinct atoms (> MAX_ATOMS=24) while
    # staying under MAX_PREMISE_SENTENCES — the atom cap is what fires.
    premises = " ".join(
        f"The unit{i} is live or the pack{i} is live." for i in range(13)
    )
    refusal = _refusal(premises + " Therefore the unit0 is live.")
    assert refusal.reason == "too_many_atoms"


def test_premise_cap_refuses_rather_than_truncating() -> None:
    premises = " ".join(f"The unit{i} is live." for i in range(17))
    refusal = _refusal(premises + " Therefore the unit0 is live.")
    assert refusal.reason == "too_many_premises"


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


def test_reading_is_deterministic() -> None:
    text = (
        "If the pump runs then the tank fills. If the valve opens then the tank fills. "
        "The pump runs or the valve opens. Therefore the tank fills."
    )
    assert read_english_argument(text) == read_english_argument(text)
