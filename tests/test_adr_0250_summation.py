"""ADR-0250 2b — certified summation turn (the 6 "altogether" cases) pins.

A total-like unknown (`unknown.entity is None`) compiles to a certified summation
over all registers: each addition is a certified turn, and the operand is the
decode of a certified register state, bound by ``operand_source_digest`` so the
Python layer cannot tamper with the intermediate value (chain of custody). The
capstone pins the full GSM8K dev holdout at 50/50, wrong=0.
"""
from __future__ import annotations

import dataclasses
import json
from pathlib import Path

from generate.math_problem_graph import (
    InitialPossession,
    MathProblemGraph,
    Operation,
    Quantity,
    Unknown,
    graph_from_dict,
)

from evals.turn_program import (
    TurnProgramError,
    compile_turn_program,
    execute_turn_program,
)
from evals.multi_register_program import (
    compile_multi_register_program,
    execute_multi_register_program,
    verify_multi_register_chain,
)

_DEV = Path(__file__).resolve().parents[1] / "evals" / "gsm8k_math" / "dev" / "cases.jsonl"


def _total(entities_seeds, ops=()):
    graph = MathProblemGraph(
        entities=tuple(e for e, _ in entities_seeds),
        initial_state=tuple(InitialPossession(e, Quantity(v, "x")) for e, v in entities_seeds),
        operations=tuple(ops),
        unknown=Unknown(None, "x"),
    )
    return execute_multi_register_program(compile_multi_register_program(graph))


# --- Certified summation ----------------------------------------------------


def test_altogether_bare_registers() -> None:
    assert abs(_total([("Ann", 5), ("Bob", 3), ("Cal", 4)]).answer - 12.0) < 1e-4


def test_altogether_after_ops() -> None:
    # Ann 5*2=10, Bob 3, total 13 — registers are summed AFTER their turns.
    out = _total([("Ann", 5), ("Bob", 3)], ops=(Operation("Ann", "multiply", Quantity(2, "factor")),))
    assert abs(out.answer - 13.0) < 1e-4
    assert out.certified is True


# --- Chain of custody: operand bound to the source state's digest -----------


def test_summation_records_bind_operand_source_digest() -> None:
    out = _total([("Ann", 5), ("Bob", 3)])
    sum_records = [r for r in out.records if r.entity == "__total__"]
    assert len(sum_records) == 1  # one addition for the second register
    assert sum_records[0].operand_source_digest != ""  # operand is bound to its source state
    assert verify_multi_register_chain(out.records) is True


def test_summation_chain_detects_tamper() -> None:
    out = _total([("Ann", 5), ("Bob", 3), ("Cal", 4)])
    tampered = list(out.records)
    tampered[0] = dataclasses.replace(tampered[0], operand_source_digest="forged")
    assert verify_multi_register_chain(tampered) is False


# --- Capstone: the full real GSM8K dev holdout, 50/50 wrong=0 ---------------


def test_full_dev_holdout_solved_wrong_zero() -> None:
    cases = [json.loads(line) for line in _DEV.read_text().splitlines() if line.strip()]
    solved = wrong = 0
    for case in cases:
        graph = graph_from_dict(case["ground_truth_graph"])
        try:  # Tier-1 single-accumulator
            answer = execute_turn_program(compile_turn_program(graph)).answer
        except TurnProgramError:  # Tier-2: multi-register (single-entity or summation)
            answer = execute_multi_register_program(compile_multi_register_program(graph)).answer
        if abs(answer - float(case["expected_answer"])) < 1e-4:
            solved += 1
        else:
            wrong += 1
    assert wrong == 0  # the headline: zero wrong on the entire real holdout
    assert solved == 50  # Tier-1 (26) + T2a single-entity (18) + summation (6)
