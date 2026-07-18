"""ADR-0250 reader-arc increment 1 — compare_multiplicative compiler tier.

`compare_multiplicative` (`actor = factor × reference`) as a cross-register
dilation: read the reference register's field state, dilate, write the actor.
The actor may be *defined* by the comparison (no seed); the registers-driven
summation must include it (amendment 1); the record binds the reference entity
+ its state digest for records-alone re-verification (amendment 2). Compare
*creates* a quantity, so it is exempt from the transfer conservation pin.
"""
from __future__ import annotations

import dataclasses
import json
from pathlib import Path

import pytest

from generate.math_candidate_graph import parse_and_solve
from generate.math_problem_graph import (
    Comparison,
    InitialPossession,
    MathProblemGraph,
    Operation,
    Quantity,
    Unknown,
)

from evals.multi_register_program import (
    MultiRegisterError,
    compile_multi_register_program,
    execute_multi_register_program,
    verify_multi_register_chain,
)

_DEV = Path(__file__).resolve().parents[1] / "evals" / "gsm8k_math" / "holdout_dev" / "v1" / "cases.jsonl"


def _cmp_graph(actor, factor, *, direction="times", seed=5, unknown=None, unit="apples"):
    """A→seed; actor = factor × A; unknown None (total) or a concrete entity."""
    return MathProblemGraph(
        entities=("A", actor),
        initial_state=(InitialPossession("A", Quantity(seed, unit)),),
        operations=(
            Operation(actor, "compare_multiplicative", Comparison("A", None, factor, direction)),
        ),
        unknown=Unknown(unknown, unit),
    )


def _solve(graph):
    return execute_multi_register_program(compile_multi_register_program(graph))


# --- The 5 real official compare parses solve end-to-end, wrong=0 -----------


def test_real_compare_cases_solved_wrong_zero() -> None:
    cases = [json.loads(line) for line in _DEV.read_text().splitlines() if line.strip()]
    solved = wrong = seen = 0
    for case in cases:
        try:
            result = parse_and_solve(case["problem"])
        except Exception:
            continue
        graph = result.selected_graph
        if graph is None or not any(op.kind == "compare_multiplicative" for op in graph.operations):
            continue
        seen += 1
        answer = _solve(graph).answer
        if abs(answer - float(case["expected_answer"])) < 1e-4:
            solved += 1
        else:
            wrong += 1
    assert seen == 5  # the compare parses the reader emits today
    assert wrong == 0
    assert solved == 5  # corridor real-reach 0/500 → 5/500 (loop-works proof)


# --- Amendment 1: compare-defined register in the certified sum + unit prop --


def test_compare_defined_register_included_in_total() -> None:
    # A=5, B=3×A=15, total = 20 — B is compare-defined (no seed) yet summed.
    assert abs(_solve(_cmp_graph("B", 3.0, unknown=None)).answer - 20.0) < 1e-4


def test_compare_defines_answer_target_with_unit_propagation() -> None:
    outcome = _solve(_cmp_graph("B", 3.0, unknown="B", unit="dollars"))
    assert abs(outcome.answer - 15.0) < 1e-4
    assert outcome.answer_unit == "dollars"  # propagated from the reference


def test_fraction_direction() -> None:
    assert abs(_solve(_cmp_graph("B", 0.5, direction="fraction", seed=8, unknown="B")).answer - 4.0) < 1e-4


def test_compare_does_not_conserve_and_is_not_rejected() -> None:
    # total (20) exceeds the reference (5): compare creates quantity — no pin fires.
    outcome = _solve(_cmp_graph("B", 3.0, unknown=None))
    assert outcome.certified is True


# --- Amendment 2: the compare record binds the reference (records-alone) -----


def test_compare_record_binds_reference_and_verifies() -> None:
    outcome = _solve(_cmp_graph("B", 3.0, unknown="B"))
    compare_records = [r for r in outcome.records if r.entity == "B"]
    assert len(compare_records) == 1
    rec = compare_records[0]
    assert rec.source_entity == "A"  # the reference is reconstructable from the record
    assert rec.operand_source_digest != ""  # bound to the reference state's digest
    assert verify_multi_register_chain(outcome.records) is True


def test_compare_chain_detects_tamper() -> None:
    # 3-record chain (compare B, then a later op) so a non-terminal tamper breaks a link.
    graph = MathProblemGraph(
        entities=("A", "B"),
        initial_state=(InitialPossession("A", Quantity(5, "x")),),
        operations=(
            Operation("B", "compare_multiplicative", Comparison("A", None, 3.0, "times")),
            Operation("A", "add", Quantity(2, "x")),
        ),
        unknown=Unknown(None, "x"),
    )
    outcome = _solve(graph)
    tampered = list(outcome.records)
    tampered[0] = dataclasses.replace(tampered[0], source_entity="forged")
    assert verify_multi_register_chain(tampered) is False


# --- Criterion 4: non-compare records carry no source_entity ----------------


def test_summation_record_has_no_source_entity() -> None:
    # A summation record keeps only operand_source_digest — source_entity stays
    # empty, so pre-compare record digests are byte-identical.
    graph = MathProblemGraph(
        entities=("A", "B"),
        initial_state=(
            InitialPossession("A", Quantity(5, "x")),
            InitialPossession("B", Quantity(3, "x")),
        ),
        operations=(),
        unknown=Unknown(None, "x"),
    )
    outcome = _solve(graph)
    for record in outcome.records:
        assert record.source_entity == ""


# --- Fail-closed refusals ----------------------------------------------------


def test_refuses_compare_additive() -> None:
    # compare_additive ("more"/"fewer") is a later increment — out of scope now.
    graph = MathProblemGraph(
        entities=("A", "B"),
        initial_state=(
            InitialPossession("A", Quantity(5, "x")),
            InitialPossession("B", Quantity(1, "x")),
        ),
        operations=(
            Operation("B", "compare_additive", Comparison("A", Quantity(2, "x"), None, "more")),
        ),
        unknown=Unknown("B", "x"),
    )
    with pytest.raises(MultiRegisterError):
        compile_multi_register_program(graph)
