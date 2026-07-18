"""ADR-0249 P4 — turn-program compiler + chained-relaxation executor pins.

Multi-step arithmetic is solved as a *turn program*: an ordered sequence of
affine relation-wells, each solved in one certified relaxation turn, with the
accumulator flowing turn-to-turn as a field STATE that is never decoded until
the end (anti-hollow, spike §2/§4.1). The sequence is recorded as a
content-addressed, GENESIS-linked turn chain (the Ring-2 chain-integrity
pattern, applied to the mutating arithmetic turns the zero-bound residual
protocol cannot itself carry).
"""
from __future__ import annotations

import dataclasses

import pytest

from generate.math_problem_graph import (
    InitialPossession,
    MathProblemGraph,
    Operation,
    Quantity,
    Unknown,
)

from evals.turn_program import (
    TurnProgramError,
    compile_turn_program,
    execute_turn_program,
    verify_turn_chain,
)


def _graph(seed, steps, unit="apples", entity="tom"):
    """Single-accumulator graph: seed then (kind, operand_value) steps."""
    ops = tuple(
        Operation(entity, kind, Quantity(val, unit if kind in ("add", "subtract") else "factor"))
        for kind, val in steps
    )
    return MathProblemGraph(
        entities=(entity,),
        initial_state=(InitialPossession(entity, Quantity(seed, unit)),),
        operations=ops,
        unknown=Unknown(entity, unit),
    )


def _solve(seed, steps, unit="apples"):
    program = compile_turn_program(_graph(seed, steps, unit))
    return execute_turn_program(program)


# --- Multi-step arithmetic by chained certified relaxation -------------------


@pytest.mark.parametrize(
    ("seed", "steps", "gold"),
    [
        (5.0, [("add", 3.0), ("multiply", 2.0), ("subtract", 4.0)], 12.0),  # ((5+3)*2)-4
        (10.0, [("divide", 2.0), ("add", 7.0), ("multiply", 3.0)], 36.0),   # (10/2+7)*3
        (4.0, [("multiply", 3.0), ("add", 5.0)], 17.0),                     # 4*3+5
        (100.0, [("subtract", 40.0), ("divide", 4.0)], 15.0),              # (100-40)/4
        (7.0, [("add", 0.0)], 7.0),                                        # identity step
    ],
)
def test_multi_step_arithmetic(seed, steps, gold) -> None:
    outcome = _solve(seed, steps)
    assert abs(outcome.answer - gold) < 1e-4
    assert outcome.certified is True
    assert len(outcome.records) == len(steps)


def test_answer_unit_from_graph() -> None:
    assert _solve(5.0, [("add", 3.0)], unit="dollars").answer_unit == "dollars"


# --- Certified turn chain: content-addressed, GENESIS-linked, tamper-evident --


def test_turn_chain_verifies() -> None:
    outcome = _solve(5.0, [("add", 3.0), ("multiply", 2.0)])
    assert verify_turn_chain(outcome.records) is True
    assert tuple(r.sequence_index for r in outcome.records) == (0, 1)


def test_turn_chain_detects_tamper() -> None:
    # Tampering a non-terminal record breaks its successor's prev-link (the
    # standard hash-chain property; the terminal record's self-integrity comes
    # from deterministic re-execution, not a downstream pointer).
    outcome = _solve(5.0, [("add", 3.0), ("multiply", 2.0), ("subtract", 4.0)])
    tampered = list(outcome.records)
    tampered[0] = dataclasses.replace(tampered[0], certificate_id="forged")
    assert verify_turn_chain(tampered) is False


def test_records_are_deterministic() -> None:
    a = _solve(5.0, [("add", 3.0), ("multiply", 2.0)])
    b = _solve(5.0, [("add", 3.0), ("multiply", 2.0)])
    assert [r.record_digest() for r in a.records] == [r.record_digest() for r in b.records]


def test_records_carry_no_decoded_answer() -> None:
    # Anti-hollow: a turn record exposes the constraint provenance (certificate
    # + step), never a decoded intermediate value.
    outcome = _solve(5.0, [("add", 3.0), ("multiply", 2.0)])
    record_fields = {f.name for f in dataclasses.fields(outcome.records[0])}
    assert "answer" not in record_fields
    assert "decoded" not in record_fields


# --- Compilation is a pure, refusal-first mapping ----------------------------


def test_compile_is_pure_no_answer() -> None:
    program = compile_turn_program(_graph(5.0, [("add", 3.0), ("multiply", 2.0)]))
    assert program.seed == 5.0
    assert tuple(s.kind for s in program.steps) == ("add", "multiply")
    assert not hasattr(program, "answer")


# --- Fail-closed refusals (Tier-1 affine single-accumulator scope) -----------


def test_refuses_multi_entity_graph() -> None:
    graph = MathProblemGraph(
        entities=("tom", "sue"),
        initial_state=(
            InitialPossession("tom", Quantity(5, "apples")),
            InitialPossession("sue", Quantity(2, "apples")),
        ),
        operations=(),
        unknown=Unknown("tom", "apples"),
    )
    with pytest.raises(TurnProgramError):
        compile_turn_program(graph)


def test_refuses_transfer_operation() -> None:
    graph = MathProblemGraph(
        entities=("tom", "sue"),
        initial_state=(InitialPossession("tom", Quantity(5, "apples")),),
        operations=(Operation("tom", "transfer", Quantity(2, "apples"), target="sue"),),
        unknown=Unknown("tom", "apples"),
    )
    with pytest.raises(TurnProgramError):
        compile_turn_program(graph)


def test_refuses_non_positive_scale() -> None:
    with pytest.raises(TurnProgramError):
        compile_turn_program(_graph(5.0, [("multiply", 0.0)]))


def test_refuses_add_unit_mismatch() -> None:
    graph = MathProblemGraph(
        entities=("tom",),
        initial_state=(InitialPossession("tom", Quantity(5, "apples")),),
        operations=(Operation("tom", "add", Quantity(3, "oranges")),),
        unknown=Unknown("tom", "apples"),
    )
    with pytest.raises(TurnProgramError):
        compile_turn_program(graph)
