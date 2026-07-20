"""Track B Increment 2 — S2–S4 canonicals, selector, coverage extract, gates."""

from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest

from generate.math_candidate_graph import parse_and_solve
from generate.math_problem_graph import (
    Comparison,
    InitialPossession,
    MathProblemGraph,
    Operation,
    Quantity,
    Rate,
    Unknown,
)
from generate.structure_mapping.canonicals import (
    CANONICAL_LIBRARY,
    S1_CANONICAL,
    S2_CANONICAL,
    S3_CANONICAL,
    S4_CANONICAL,
)
from generate.structure_mapping.convert import graph_to_role_graph
from generate.structure_mapping.mapper import (
    StructureMapRefuse,
    StructureMapResult,
    map_to_s1,
    map_to_s2,
    map_to_s3,
    map_to_s4,
)
from generate.structure_mapping.pipeline import run_structure_mapping_pipeline
from generate.structure_mapping.selector import select_structure
from generate.structure_mapping.solve import solve_binding, try_structure_map_and_solve
from generate.structure_mapping.text_extract import extract_pure_s1

# Real holdout pure-S1 coverage targets (organ misses; SM extract carries).
COVERAGE_CASES = (
    (
        "gsm8k-holdout-dev-v1-0148",
        "At a people counting station, the number of people counted on the first day "
        "was twice the total number counted on the second day. If 500 people were "
        "counted on the second day, how many people were counted on the two days?",
        1500.0,
    ),
    (
        "gsm8k-holdout-dev-v1-0228",
        "There are two warehouses. The first warehouse has twice as many boxes as "
        "the second warehouse. If the first warehouse has 400 boxes, how many boxes "
        "are there in both warehouses combined?",
        600.0,
    ),
    (
        "gsm8k-holdout-dev-v1-0234",
        "A special school for deaf and blind students has a deaf student population "
        "three times the size of blind student population. If the number of deaf "
        "students is 180, how many students are there altogether?",
        240.0,
    ),
    (
        "gsm8k-holdout-dev-v1-0441",
        "Zig wrote four times as many books as Flo. If Zig wrote 60 books, how many "
        "books did they write altogether?",
        75.0,
    ),
)


def test_canonical_library_has_s1_through_s4():
    ids = {c.structure_id for c in CANONICAL_LIBRARY}
    assert ids == {"S1", "S2", "S3", "S4"}
    for c in (S1_CANONICAL, S2_CANONICAL, S3_CANONICAL, S4_CANONICAL):
        assert all(t.kind == "var" for p in c.predicates for t in p.args)


def test_s2_transfer_map_and_solve_public_shape():
    text = (
        "Eve has 15 coins. David has 47 coins. Eve hands 7 coins to David. "
        "How many coins does David have?"
    )
    organ = parse_and_solve(text)
    assert organ.selected_graph is not None
    rg = graph_to_role_graph(organ.selected_graph)
    mapped = map_to_s2(rg)
    assert isinstance(mapped, StructureMapResult)
    assert mapped.structure_id == "S2"
    out = try_structure_map_and_solve(organ.selected_graph)
    assert out.emitted
    assert out.answer == pytest.approx(54.0)
    assert out.structure_id == "S2"
    assert out.multi_register_certified
    assert "transfer" in (out.derivation or "")


def test_s2_refuses_when_compare_present():
    g = MathProblemGraph(
        entities=("A", "B"),
        initial_state=(
            InitialPossession(entity="A", quantity=Quantity(value=1, unit="u")),
            InitialPossession(entity="B", quantity=Quantity(value=1, unit="u")),
        ),
        operations=(
            Operation(
                actor="A",
                kind="transfer",
                operand=Quantity(value=1, unit="u"),
                target="B",
            ),
            Operation(
                actor="B",
                kind="compare_multiplicative",
                operand=Comparison(
                    reference_actor="A", delta=None, factor=2.0, direction="times"
                ),
            ),
        ),
        unknown=Unknown(entity="B", unit="u"),
    )
    mapped = map_to_s2(graph_to_role_graph(g))
    assert isinstance(mapped, StructureMapRefuse)


def test_s1_inverted_seed_binding():
    """b seeded, a = b/k — pure S1."""
    g = MathProblemGraph(
        entities=("Flo", "Zig"),
        initial_state=(
            InitialPossession(entity="Zig", quantity=Quantity(value=60, unit="books")),
        ),
        operations=(
            Operation(
                actor="Zig",
                kind="compare_multiplicative",
                operand=Comparison(
                    reference_actor="Flo", delta=None, factor=4.0, direction="times"
                ),
            ),
        ),
        unknown=Unknown(entity=None, unit="books"),
    )
    # contain only on b; convert will emit contain(Zig) + compare + total
    rg = graph_to_role_graph(g)
    mapped = map_to_s1(rg)
    assert isinstance(mapped, StructureMapResult)
    assert mapped.binding["a_value"] == pytest.approx(15.0)
    assert mapped.binding["seed_mode"] == "b_seeded"
    out = solve_binding("S1", mapped.binding)
    assert out.emitted
    assert out.answer == pytest.approx(75.0)


def test_selector_picks_s1_over_refuse_others():
    g = MathProblemGraph(
        entities=("Ann", "Bea"),
        initial_state=(
            InitialPossession(entity="Ann", quantity=Quantity(value=7, unit="pts")),
        ),
        operations=(
            Operation(
                actor="Bea",
                kind="compare_multiplicative",
                operand=Comparison(
                    reference_actor="Ann", delta=None, factor=3.0, direction="times"
                ),
            ),
        ),
        unknown=Unknown(entity=None, unit="pts"),
    )
    sel = select_structure(graph_to_role_graph(g))
    assert not sel.refused
    assert sel.selected is not None
    assert sel.selected.structure_id == "S1"


def test_selector_picks_s2_not_s1_on_transfer():
    g = MathProblemGraph(
        entities=("Alice", "Bob"),
        initial_state=(
            InitialPossession(entity="Alice", quantity=Quantity(value=10, unit="apples")),
            InitialPossession(entity="Bob", quantity=Quantity(value=5, unit="apples")),
        ),
        operations=(
            Operation(
                actor="Alice",
                kind="transfer",
                operand=Quantity(value=3, unit="apples"),
                target="Bob",
            ),
        ),
        unknown=Unknown(entity="Bob", unit="apples"),
    )
    sel = select_structure(graph_to_role_graph(g))
    assert not sel.refused
    assert sel.selected is not None
    assert sel.selected.structure_id == "S2"
    # S1 must have refused this graph
    assert any(f == "S1" for f, _ in sel.refused_families)


def test_selector_refuses_empty():
    g = MathProblemGraph(
        entities=("X",),
        initial_state=(
            InitialPossession(entity="X", quantity=Quantity(value=1, unit="u")),
        ),
        operations=(),
        unknown=Unknown(entity="X", unit="u"),
    )
    sel = select_structure(graph_to_role_graph(g))
    assert sel.refused
    assert sel.selected is None


def test_s3_maps_but_mr_frontier_refuses_emit():
    """S3 pure map succeeds; multi-register out-of-scope → refuse (gate holds)."""
    g = MathProblemGraph(
        entities=("worker",),
        initial_state=(
            InitialPossession(entity="worker", quantity=Quantity(value=5, unit="hours")),
        ),
        operations=(
            Operation(
                actor="worker",
                kind="apply_rate",
                operand=Rate(
                    value=10.0, numerator_unit="pages", denominator_unit="hours"
                ),
            ),
        ),
        unknown=Unknown(entity="worker", unit="pages"),
    )
    mapped = map_to_s3(graph_to_role_graph(g))
    assert isinstance(mapped, StructureMapResult)
    out = try_structure_map_and_solve(g)
    # Either S3 selected and MR refuses, or emit only if corridor supports it.
    if out.emitted:
        assert out.multi_register_certified
        assert out.answer == pytest.approx(50.0)
    else:
        assert out.refusal_reason is not None
        assert "multi_register" in out.refusal_reason or "structure_map" in (
            out.refusal_reason or ""
        )


@pytest.mark.parametrize("case_id,text,gold", COVERAGE_CASES)
def test_coverage_gain_holdout_pure_s1(case_id: str, text: str, gold: float):
    organ = parse_and_solve(text)
    assert organ.selected_graph is None or organ.answer is None
    out, trace, _ = run_structure_mapping_pipeline(text)
    assert trace.extract_used
    assert out.emitted
    assert out.answer == pytest.approx(gold)
    assert out.structure_id == "S1"
    assert out.multi_register_certified
    assert out.classical_verified
    assert out.derivation is not None


def test_surface_variant_inverted_s1():
    variant = (
        "Ava wrote five times as many essays as Ben. If Ava wrote 40 essays, "
        "how many essays did they write altogether?"
    )
    out, trace, _ = run_structure_mapping_pipeline(variant)
    assert out.emitted
    assert out.answer == pytest.approx(48.0)
    assert out.structure_id == "S1"
    assert trace.graph_source == "sm_extract"


def test_mapper_modules_do_not_import_scoring_labels():
    root = Path("generate/structure_mapping")
    for path in root.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                assert "structure_mapping.scoring" not in node.module
                assert "holdout_dev_v1_labels" not in (node.module or "")


def test_select_structure_signature_blind():
    sig = inspect.signature(select_structure)
    assert "label" not in sig.parameters
    assert "gold" not in sig.parameters
