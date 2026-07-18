"""ADR-0250 T2a — multi-entity arithmetic (multi-register executor) pins.

Multi-entity problems solved as a product of independent conformal lines, with
coupled-translator transfers, a relative conservation pin (hard-reject), and
prepare→validate→commit atomicity. Measured on the real GSM8K single-entity
refused holdout at wrong=0.
"""
from __future__ import annotations

import dataclasses
import json
from pathlib import Path

import pytest

from generate.math_problem_graph import (
    InitialPossession,
    MathProblemGraph,
    Operation,
    Quantity,
    Rate,
    Unknown,
)

from evals.turn_program import TurnProgramError, compile_turn_program
from evals.multi_register_program import (
    MultiRegisterError,
    compile_multi_register_program,
    execute_multi_register_program,
    verify_multi_register_chain,
)

_DEV = Path(__file__).resolve().parents[1] / "evals" / "gsm8k_math" / "dev" / "cases.jsonl"


def _solve(graph: MathProblemGraph):
    return execute_multi_register_program(compile_multi_register_program(graph))


# --- Coupled-translator transfers between registers --------------------------


def _ruth_sara(unknown_entity: str) -> MathProblemGraph:
    return MathProblemGraph(
        entities=("Ruth", "Sara"),
        initial_state=(
            InitialPossession("Ruth", Quantity(36, "cards")),
            InitialPossession("Sara", Quantity(19, "cards")),
        ),
        operations=(Operation("Ruth", "transfer", Quantity(5, "cards"), target="Sara"),),
        unknown=Unknown(unknown_entity, "cards"),
    )


def test_transfer_updates_both_registers() -> None:
    assert abs(_solve(_ruth_sara("Ruth")).answer - 31.0) < 1e-4  # 36 - 5
    assert abs(_solve(_ruth_sara("Sara")).answer - 24.0) < 1e-4  # 19 + 5


def test_multi_step_large_magnitude_relative_conservation() -> None:
    # Gwen: 37 *3 *2 -> 222, then two transfers to Leo, then -26 -> 26.
    # Large intermediate (222) exercises the RELATIVE conservation pin.
    graph = MathProblemGraph(
        entities=("Gwen", "Leo"),
        initial_state=(
            InitialPossession("Gwen", Quantity(37, "cards")),
            InitialPossession("Leo", Quantity(90, "cards")),
        ),
        operations=(
            Operation("Gwen", "multiply", Quantity(3, "factor")),
            Operation("Gwen", "multiply", Quantity(2, "factor")),
            Operation("Gwen", "transfer", Quantity(100, "cards"), target="Leo"),
            Operation("Gwen", "transfer", Quantity(70, "cards"), target="Leo"),
            Operation("Gwen", "subtract", Quantity(26, "cards")),
        ),
        unknown=Unknown("Gwen", "cards"),
    )
    outcome = _solve(graph)
    assert abs(outcome.answer - 26.0) < 1e-4
    assert outcome.certified is True


def test_transfer_conserves_total() -> None:
    ruth = _solve(_ruth_sara("Ruth")).answer
    sara = _solve(_ruth_sara("Sara")).answer
    assert abs((ruth + sara) - (36 + 19)) < 1e-4  # nothing created or destroyed


# --- The real GSM8K single-entity refused holdout, wrong=0 -------------------


@pytest.fixture(scope="module")
def real_single_entity_stats():
    cases = [json.loads(line) for line in _DEV.read_text().splitlines() if line.strip()]
    from generate.math_problem_graph import graph_from_dict

    solved = wrong = 0
    for case in cases:
        graph = graph_from_dict(case["ground_truth_graph"])
        try:
            compile_turn_program(graph)  # already Tier-1
            continue
        except TurnProgramError:
            pass
        if graph.unknown.entity is None:
            continue  # total-like -> summation turn (2b), not T2a
        outcome = _solve(graph)
        if abs(outcome.answer - float(case["expected_answer"])) < 1e-4:
            solved += 1
        else:
            wrong += 1
    return solved, wrong


def test_real_single_entity_wrong_zero(real_single_entity_stats) -> None:
    solved, wrong = real_single_entity_stats
    assert wrong == 0  # the load-bearing claim
    assert solved == 18  # coverage tracker: dev holdout single-entity subset


# --- Content-addressed chain: carries the entity, tamper-evident, no answer --


def test_chain_verifies_carries_entity_and_detects_tamper() -> None:
    outcome = _solve(_ruth_sara("Ruth"))
    assert verify_multi_register_chain(outcome.records) is True
    assert {r.entity for r in outcome.records} == {"Ruth", "Sara"}  # both legs recorded
    tampered = list(outcome.records)
    tampered[0] = dataclasses.replace(tampered[0], certificate_id="forged")
    assert verify_multi_register_chain(tampered) is False


def test_records_carry_no_decoded_answer() -> None:
    outcome = _solve(_ruth_sara("Ruth"))
    fields = {f.name for f in dataclasses.fields(outcome.records[0])}
    assert "answer" not in fields and "decoded" not in fields


def test_deterministic() -> None:
    a = [r.record_digest() for r in _solve(_ruth_sara("Ruth")).records]
    b = [r.record_digest() for r in _solve(_ruth_sara("Ruth")).records]
    assert a == b


# --- Fail-closed refusals (Tier-2a scope) -----------------------------------


def test_total_unknown_compiles_to_summation() -> None:
    # "how many altogether" (None unknown) is no longer refused — 2b sums it.
    graph = MathProblemGraph(
        entities=("Ann", "Bob"),
        initial_state=(
            InitialPossession("Ann", Quantity(5, "apples")),
            InitialPossession("Bob", Quantity(3, "apples")),
        ),
        operations=(),
        unknown=Unknown(None, "apples"),
    )
    program = compile_multi_register_program(graph)
    assert program.answer_entity is None  # the summation signal
    assert abs(execute_multi_register_program(program).answer - 8.0) < 1e-4


def test_refuses_derived_operand() -> None:
    graph = MathProblemGraph(
        entities=("Ann",),
        initial_state=(InitialPossession("Ann", Quantity(5, "apples")),),
        operations=(Operation("Ann", "apply_rate", Rate(2.0, "dollars", "apple")),),
        unknown=Unknown("Ann", "dollars"),
    )
    with pytest.raises(MultiRegisterError):
        compile_multi_register_program(graph)


def test_refuses_non_positive_scale() -> None:
    graph = MathProblemGraph(
        entities=("Ann",),
        initial_state=(InitialPossession("Ann", Quantity(5, "apples")),),
        operations=(Operation("Ann", "multiply", Quantity(0, "factor")),),
        unknown=Unknown("Ann", "apples"),
    )
    with pytest.raises(MultiRegisterError):
        compile_multi_register_program(graph)


def test_refuses_unit_mismatch() -> None:
    graph = MathProblemGraph(
        entities=("Ann",),
        initial_state=(InitialPossession("Ann", Quantity(5, "apples")),),
        operations=(Operation("Ann", "add", Quantity(3, "oranges")),),
        unknown=Unknown("Ann", "apples"),
    )
    with pytest.raises(MultiRegisterError):
        compile_multi_register_program(graph)
