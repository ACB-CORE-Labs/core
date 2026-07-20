"""Unit tests for Track B Increment 1 — symbolic S1 structure-mapping.

Drives the **shipped** converter / mapper / solve corridor. Gold structure
labels are loaded only in the isolated scoring helper, never as mapper input.
"""

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
    Unknown,
)
from generate.structure_mapping.canonicals import S1_CANONICAL
from generate.structure_mapping.convert import graph_to_role_graph
from generate.structure_mapping.mapper import (
    StructureMapRefuse,
    StructureMapResult,
    map_to_s1,
)
from generate.structure_mapping.solve_s1 import (
    graph_from_s1_binding,
    solve_s1_binding,
    try_s1_structure_map_and_solve,
)

# Real holdout S1 texts (from evals/gsm8k_math/holdout_dev/v1/cases.jsonl).
S1_CASES = (
    (
        "gsm8k-holdout-dev-v1-0101",
        "Eduardo is a teacher. He taught 3 classes last week while his colleague "
        "Frankie taught double what Eduardo teaches. How many classes did Eduardo "
        "and Frankie teach in total?",
        9.0,
    ),
    (
        "gsm8k-holdout-dev-v1-0108",
        "Dana Point beach has four times the number of sharks as Newport Beach. "
        "If Newport Beach has 22 sharks, how many sharks are there in total on "
        "the two beaches?",
        110.0,
    ),
    (
        "gsm8k-holdout-dev-v1-0411",
        "In a class, there were 13 female students. There were three times as many "
        "male students in this class. How many students were in the class?",
        52.0,
    ),
    (
        "gsm8k-holdout-dev-v1-0453",
        "Olaf is playing a game with his dad. He scored three times more points "
        "than his dad, who scored 7 points. How many points did they score in total?",
        28.0,
    ),
    (
        "gsm8k-holdout-dev-v1-0268",
        "Yesterday, Bruce and Michael were playing football in the park. Bruce "
        "scored 4 goals While Michael scored 3 times more than Bruce. How many "
        "goals did Bruce and Michael score altogether?",
        16.0,
    ),
)


def _pure_s1_graph(
    a: str = "Alice",
    b: str = "Bob",
    a_value: float = 7.0,
    k: float = 3.0,
    unit: str = "apples",
) -> MathProblemGraph:
    return MathProblemGraph(
        entities=(a, b),
        initial_state=(
            InitialPossession(entity=a, quantity=Quantity(value=a_value, unit=unit)),
        ),
        operations=(
            Operation(
                actor=b,
                kind="compare_multiplicative",
                operand=Comparison(
                    reference_actor=a,
                    delta=None,
                    factor=k,
                    direction="times",
                ),
            ),
        ),
        unknown=Unknown(entity=None, unit=unit),
    )


def test_s1_canonical_is_role_vars_only() -> None:
    for pred in S1_CANONICAL.predicates:
        for arg in pred.args:
            assert arg.kind == "var", "canonical must not use surface literals"
    kinds = {p.kind for p in S1_CANONICAL.predicates}
    assert kinds == {"contain", "compare", "total"}


def test_converter_emits_compare_contain_total_on_pure_s1() -> None:
    g = _pure_s1_graph()
    rg = graph_to_role_graph(g)
    assert "compare" in rg.kinds()
    assert "contain" in rg.kinds()
    assert "total" in rg.kinds()
    assert "transfer" not in rg.kinds()
    compares = rg.of_kind("compare")
    assert len(compares) == 1
    b, a, k = compares[0].args
    assert b.name == "Bob" and a.name == "Alice"
    assert k.value == 3.0


def test_mapper_matches_pure_s1_and_binds_roles() -> None:
    rg = graph_to_role_graph(_pure_s1_graph(a_value=5.0, k=4.0))
    result = map_to_s1(rg)
    assert isinstance(result, StructureMapResult)
    assert result.maps_to_s1 is True
    assert result.binding["a"] == "Alice"
    assert result.binding["b"] == "Bob"
    assert result.binding["k"] == 4.0
    assert result.binding["a_value"] == 5.0


def test_mapper_refuses_transfer_graph() -> None:
    g = MathProblemGraph(
        entities=("Sam", "Alex"),
        initial_state=(
            InitialPossession(entity="Sam", quantity=Quantity(value=10, unit="apples")),
            InitialPossession(entity="Alex", quantity=Quantity(value=0, unit="apples")),
        ),
        operations=(
            Operation(
                actor="Sam",
                kind="transfer",
                operand=Quantity(value=3, unit="apples"),
                target="Alex",
            ),
        ),
        unknown=Unknown(entity="Sam", unit="apples"),
    )
    rg = graph_to_role_graph(g)
    result = map_to_s1(rg)
    assert isinstance(result, StructureMapRefuse)
    assert "transfer" in result.reason


def test_mapper_refuses_missing_total() -> None:
    g = MathProblemGraph(
        entities=("Alice", "Bob"),
        initial_state=(
            InitialPossession(entity="Alice", quantity=Quantity(value=7, unit="apples")),
        ),
        operations=(
            Operation(
                actor="Bob",
                kind="compare_multiplicative",
                operand=Comparison(
                    reference_actor="Alice",
                    delta=None,
                    factor=2.0,
                    direction="times",
                ),
            ),
        ),
        # entity-bound unknown — not a total query
        unknown=Unknown(entity="Bob", unit="apples"),
    )
    rg = graph_to_role_graph(g)
    result = map_to_s1(rg)
    assert isinstance(result, StructureMapRefuse)
    assert "total" in result.reason


def test_solve_corridor_emits_certified_answer() -> None:
    binding = {
        "a": "Alice",
        "b": "Bob",
        "k": 3.0,
        "a_value": 7.0,
        "unit": "apples",
    }
    out = solve_s1_binding(binding)
    assert out.emitted is True
    assert out.answer == pytest.approx(28.0)
    assert out.multi_register_certified is True
    assert out.classical_verified is True
    assert out.derivation is not None
    assert "3.0" in out.derivation


def test_try_slice_end_to_end_on_synthetic() -> None:
    out = try_s1_structure_map_and_solve(graph=_pure_s1_graph(a_value=10.0, k=2.0))
    assert out.emitted is True
    assert out.answer == pytest.approx(30.0)


def test_graph_from_binding_roundtrip_hash_stable() -> None:
    binding = {"a": "A", "b": "B", "k": 2.0, "a_value": 3.0, "unit": "x"}
    g1 = graph_from_s1_binding(binding)
    g2 = graph_from_s1_binding(binding)
    assert g1.canonical_bytes() == g2.canonical_bytes()


@pytest.mark.parametrize("case_id,text,gold", S1_CASES)
def test_real_s1_holdout_right_reason(case_id: str, text: str, gold: float) -> None:
    parsed = parse_and_solve(text)
    assert parsed.selected_graph is not None, f"{case_id} failed to parse: {parsed.refusal_reason}"
    rg = graph_to_role_graph(parsed.selected_graph)
    mapped = map_to_s1(rg)
    assert isinstance(mapped, StructureMapResult), f"{case_id} refuse: {mapped}"
    out = try_s1_structure_map_and_solve(graph=parsed.selected_graph)
    assert out.emitted is True, f"{case_id} solve refuse: {out.refusal_reason}"
    assert out.answer == pytest.approx(gold)
    assert out.multi_register_certified and out.classical_verified
    # derivation must mention factor path
    assert out.derivation is not None
    assert str(mapped.binding["k"]) in out.derivation or "×" in out.derivation


def test_mapper_module_does_not_import_scoring_labels() -> None:
    """Static blindness: generate.structure_mapping must not import scoring."""
    root = Path(__file__).resolve().parents[1] / "generate" / "structure_mapping"
    forbidden = (
        "evals.structure_mapping.scoring",
        "holdout_dev_v1_labels",
        "load_structure_labels",
        "S1_HOLDOUT_CASE_IDS",
        "score_label",
    )
    for path in root.rglob("*.py"):
        src = path.read_text(encoding="utf-8")
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    for bad in forbidden:
                        assert bad not in alias.name, f"{path} imports {alias.name}"
            if isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                for bad in forbidden:
                    assert bad not in mod, f"{path} imports from {mod}"
        for bad in forbidden:
            # also ban string-literal label file reads in mapper package
            if bad in ("holdout_dev_v1_labels", "load_structure_labels"):
                assert bad not in src, f"{path} references {bad}"


def test_map_to_s1_signature_has_no_label_parameter() -> None:
    sig = inspect.signature(map_to_s1)
    params = list(sig.parameters)
    assert params == ["role_graph"]
    for name in params:
        assert "label" not in name.lower()
        assert "gold" not in name.lower()
        assert "s1" not in name.lower() or name == "role_graph"


def test_scoring_labels_isolated_and_loadable() -> None:
    from evals.structure_mapping.scoring.labels import (
        S1_HOLDOUT_CASE_IDS,
        load_structure_labels,
        score_label,
    )

    labels = load_structure_labels()
    assert set(S1_HOLDOUT_CASE_IDS) <= set(labels)
    for cid in S1_HOLDOUT_CASE_IDS:
        assert labels[cid] == "S1"
    sc = score_label("gsm8k-holdout-dev-v1-0101", True, labels)
    assert sc["tp"] is True
    sc_fp = score_label("gsm8k-holdout-dev-v1-0101", False, labels)
    assert sc_fp["fn"] is True


def _multi_entity_compare_total_graph(
    *,
    a_value: float = 5.0,
    c_value: float = 100.0,
    k: float = 2.0,
) -> MathProblemGraph:
    """A=a_value seeded, C=c_value seeded, B=k×A; unknown = total of all.

    True answer is a_value + k*a_value + c_value (e.g. 5+10+100=115).
    A buggy pure-S1 rebuild that drops C would emit a_value*(1+k) (=15).
    """
    return MathProblemGraph(
        entities=("A", "B", "C"),
        initial_state=(
            InitialPossession(entity="A", quantity=Quantity(value=a_value, unit="x")),
            InitialPossession(entity="C", quantity=Quantity(value=c_value, unit="x")),
        ),
        operations=(
            Operation(
                actor="B",
                kind="compare_multiplicative",
                operand=Comparison(
                    reference_actor="A",
                    delta=None,
                    factor=k,
                    direction="times",
                ),
            ),
        ),
        unknown=Unknown(entity=None, unit="x"),
    )


def test_mapper_refuses_total_superset_with_extra_entity() -> None:
    """total parts must equal {a,b}; superset is not pure S1."""
    g = _multi_entity_compare_total_graph()
    rg = graph_to_role_graph(g)
    # Converter should surface contain on C and total over A,B,C.
    assert any(
        p.kind == "contain" and p.args[0].name == "C" for p in rg.predicates
    )
    total_parts = None
    for p in rg.of_kind("total"):
        total_parts = {t.name for t in p.args[:-1] if t.kind == "entity"}
    assert total_parts == {"A", "B", "C"}

    mapped = map_to_s1(rg)
    assert isinstance(mapped, StructureMapRefuse)
    assert mapped.reason in (
        "total_parts_not_exactly_a_b",
        "extra_contain_not_pure_s1:C",
    )


def test_mapper_refuses_extra_contain_even_if_total_were_ab_only() -> None:
    """Seed contain on a third entity is not pure S1."""
    from generate.structure_mapping.role_predicate import (
        RoleGraph,
        RolePredicate,
        RoleTerm,
    )

    # Hand-built role graph: total is exactly {A,B} but C is also seeded.
    rg = RoleGraph(
        predicates=(
            RolePredicate(
                kind="contain",
                args=(
                    RoleTerm(kind="entity", name="A"),
                    RoleTerm(kind="quantity", name="qa", value=5.0, unit="x"),
                ),
            ),
            RolePredicate(
                kind="contain",
                args=(
                    RoleTerm(kind="entity", name="C"),
                    RoleTerm(kind="quantity", name="qc", value=10.0, unit="x"),
                ),
            ),
            RolePredicate(
                kind="compare",
                args=(
                    RoleTerm(kind="entity", name="B"),
                    RoleTerm(kind="entity", name="A"),
                    RoleTerm(kind="quantity", name="factor", value=2.0, unit=None),
                ),
            ),
            RolePredicate(
                kind="total",
                args=(
                    RoleTerm(kind="entity", name="A"),
                    RoleTerm(kind="entity", name="B"),
                    RoleTerm(kind="quantity", name="sum_query", value=0.0, unit="x"),
                ),
            ),
        )
    )
    mapped = map_to_s1(rg)
    assert isinstance(mapped, StructureMapRefuse)
    assert mapped.reason == "extra_contain_not_pure_s1:C"


def test_multi_entity_slice_never_emits_wrong_certified_answer() -> None:
    """Repro of skeptic finding: A=5,C=100,B=2×A,total must not emit 15.

    Must refuse at map time (preferred) or refuse at integrity gate.
    Must never emit 15 with multi_register_certified=True.
    """
    g = _multi_entity_compare_total_graph(a_value=5.0, c_value=100.0, k=2.0)
    # True classical answer of the original graph.
    from generate.math_solver import solve as classical_solve

    true_ans = float(classical_solve(g).answer_value)
    assert true_ans == pytest.approx(115.0)

    out = try_s1_structure_map_and_solve(graph=g)
    # Never emit the dropped-entity wrong answer.
    assert not (out.emitted and out.answer is not None and abs(float(out.answer) - 15.0) < 1e-6)
    # Prefer refuse; if ever emitted, must match original 115 (not wrong).
    if out.emitted:
        assert out.answer == pytest.approx(true_ans)
    else:
        assert out.refusal_reason is not None
        assert (
            "total_parts" in out.refusal_reason
            or "extra_contain" in out.refusal_reason
            or "original_graph" in out.refusal_reason
            or "structure_map_refuse" in out.refusal_reason
        )
    # Certificate must not green-light a wrong answer.
    if out.answer is not None and abs(float(out.answer) - 15.0) < 1e-6:
        assert out.multi_register_certified is False
        assert out.emitted is False


def test_multi_entity_small_c_same_trap() -> None:
    """Second repro: A=5,C=10,B=2×A → true 25; buggy rebuild 15."""
    g = _multi_entity_compare_total_graph(a_value=5.0, c_value=10.0, k=2.0)
    from generate.math_solver import solve as classical_solve

    true_ans = float(classical_solve(g).answer_value)
    assert true_ans == pytest.approx(25.0)
    out = try_s1_structure_map_and_solve(graph=g)
    assert out.emitted is False
    assert out.answer is None
    assert out.refusal_reason is not None
