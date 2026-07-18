"""ADR-0249 P3 — structural formula→CNF converter pins (deduction leg).

The converter turns propositional formula strings into the corridor's CNF
``PropositionalProblem`` + query ``Clause``. Two guarantees are pinned:
  * soundness — the CNF is logically equivalent to the source, proved against
    the production ROBDD oracle (``canonicalize``), never by truth table;
  * agreement — end-to-end entailment through ``propositional_entails`` matches
    the ROBDD gold (``evaluate_entailment``) with wrong=0 on consistent premises.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from core.physics.cognitive_lifecycle import (
    HamiltonianCompileError,
    propositional_entails,
)
from generate.logic_canonical import LogicRegimeError, canonicalize
from generate.proof_chain.entail import Entailment, evaluate_entailment

from evals.logic_cnf_compiler import (
    CnfCompileError,
    clauses_to_formula,
    compile_entailment,
    formula_to_clauses,
    query_to_clause,
)

# Formulas that do NOT reduce to false (those are tested as refusals).
_SOUNDNESS_PANEL = [
    "P implies Q",
    "P or Q",
    "not P",
    "P",
    "(P implies Q) and (Q implies R)",
    "not (P and Q)",
    "not (P or Q)",
    "P iff Q",
    "(P or Q) and (not P or R)",
    "P and not P",
    "P or not P",
    "not (P implies Q)",
    "(a implies b) implies c",
    "not (not P)",
]


@pytest.mark.parametrize("formula", _SOUNDNESS_PANEL)
def test_cnf_is_robdd_equivalent_to_source(formula: str) -> None:
    # Structural soundness: the compiled CNF, rendered back to a formula, has
    # the same ROBDD identity as the original. No assignment enumeration.
    clauses = formula_to_clauses(formula)
    rendered = clauses_to_formula(clauses)
    assert canonicalize(formula).canonical_key == canonicalize(rendered).canonical_key


# --- End-to-end entailment agrees with the ROBDD gold (consistent premises) --

_ENTAILMENT_PANEL = [
    (("P implies Q", "P"), "Q"),
    (("P implies Q", "P"), "not Q"),
    (("P or Q",), "P"),
    (("P implies Q", "Q implies R"), "P implies R"),
    (("a implies b", "b implies c", "a"), "c"),
    (("P or Q", "not P"), "Q"),
    (("P or Q", "R"), "P or Q"),
]


@pytest.mark.parametrize(("premises", "query"), _ENTAILMENT_PANEL)
def test_entailment_agrees_with_robdd_gold_wrong_zero(premises, query) -> None:
    problem, conclusion = compile_entailment(premises, query)
    corridor = propositional_entails(problem, conclusion).entailed
    gold = evaluate_entailment(tuple(premises), query).outcome is Entailment.ENTAILED
    assert corridor == gold


def test_modus_ponens_entailed() -> None:
    problem, conclusion = compile_entailment(("P implies Q", "P"), "Q")
    verdict = propositional_entails(problem, conclusion)
    assert verdict.entailed is True
    assert verdict.satisfiable_premises is True


def test_ex_falso_entailed_with_unsatisfiable_premises_disclosed() -> None:
    # Inconsistent premises classically entail everything; the corridor says so
    # AND discloses that the premises are unsatisfiable (matches ADR-0243 §).
    problem, conclusion = compile_entailment(("P", "not P"), "Q")
    verdict = propositional_entails(problem, conclusion)
    assert verdict.entailed is True
    assert verdict.satisfiable_premises is False


# --- Clause shape + determinism ---------------------------------------------


def test_clause_literal_shape() -> None:
    clauses = formula_to_clauses("P implies Q")  # -> (~P | Q)
    assert clauses == (( ("P", False), ("Q", True) ),)
    (atom, polarity) = clauses[0][0]
    assert isinstance(atom, str) and isinstance(polarity, bool)


def test_tautology_yields_no_clauses() -> None:
    assert formula_to_clauses("P or not P") == ()


def test_compilation_is_deterministic() -> None:
    a, _ = compile_entailment(("P implies Q", "P"), "Q")
    b, _ = compile_entailment(("P implies Q", "P"), "Q")
    assert a.problem_id == b.problem_id
    assert formula_to_clauses("(P or Q) and (not P or R)") == formula_to_clauses(
        "(P or Q) and (not P or R)"
    )


# --- Fail-closed refusals ----------------------------------------------------


def test_refuses_conjunctive_query() -> None:
    with pytest.raises(CnfCompileError):
        query_to_clause("P and Q")


def test_refuses_constant_query() -> None:
    with pytest.raises(CnfCompileError):
        query_to_clause("P or not P")


def test_refuses_formula_reducing_to_false() -> None:
    with pytest.raises(CnfCompileError):
        formula_to_clauses("false")


def test_refuses_over_five_atoms() -> None:
    # Six distinct atoms exceed the corridor envelope → HamiltonianCompileError.
    with pytest.raises(HamiltonianCompileError):
        compile_entailment(("a or b", "c or d", "e or f"), "a")


def test_out_of_regime_propagates() -> None:
    with pytest.raises(LogicRegimeError):
        formula_to_clauses("forall x P(x)")


# --- Off-serving guard (A-04) ------------------------------------------------


def test_compiler_is_not_serve_wired() -> None:
    source = Path("evals/logic_cnf_compiler.py").read_text()
    assert "import chat" not in source
    assert "from chat" not in source
