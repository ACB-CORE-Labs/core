"""Unit, integration, and adversarial proofs for relational operator ablation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from generate.relational_operator_ablation import (
    AblationCase,
    DEPTH_EXECUTABLE_MAPPING_RULE,
    DEPTH_METADATA_RULE,
    answers_match,
    run_all_conditions,
    run_baseline,
    run_condition,
    run_depth,
    run_metadata_only,
    run_operator,
)
from algebra.versor import versor_condition

_CASES = (
    Path(__file__).resolve().parents[1]
    / "evals"
    / "relational_operator_ablation"
    / "v1"
    / "cases.jsonl"
)

GOLD_0001 = AblationCase(
    case_id="unit-gold-0001",
    problem=(
        "In one hour, Addison mountain's temperature will decrease to 3/4 of its temperature. "
        "If the current temperature of the mountain is 84 degrees, what will the temperature "
        "decrease by?"
    ),
    expected_answer=21.0,
    expected_unit="degrees",
    expected_outcome="correct",
    tags=("fraction_decrease", "gold"),
)

FINAL_VALUE = AblationCase(
    case_id="unit-final-value",
    problem=(
        "In one hour, the lake's temperature will decrease to 3/4 of its temperature. "
        "If the current temperature of the lake is 80 degrees, what will the temperature be?"
    ),
    expected_answer=None,
    expected_unit="",
    expected_outcome="refused",
    tags=("adversarial", "invalid"),
)

MULTI_FRACTION = AblationCase(
    case_id="unit-multi-fraction",
    problem=(
        "In one hour, Addison mountain's temperature will decrease to 3/4 of its temperature "
        "and then to 1/2 of its temperature. If the current temperature of the mountain is 84 "
        "degrees, what will the temperature decrease by?"
    ),
    expected_answer=None,
    expected_unit="",
    expected_outcome="refused",
    tags=("adversarial", "invalid"),
)

SCALE_OOR_PREEXISTING = AblationCase(
    case_id="unit-scale-oor-preexisting",
    problem=(
        "In one hour, the river will decrease to 5/4 of its level. "
        "If the current level is 40 feet, what will the level decrease by?"
    ),
    expected_answer=None,
    expected_unit="",
    expected_outcome="refused",
    tags=("preexisting_gap",),
)


def _load_sealed() -> list[AblationCase]:
    cases: list[AblationCase] = []
    for line in _CASES.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        raw = json.loads(line)
        cases.append(
            AblationCase(
                case_id=raw["case_id"],
                problem=raw["problem"],
                expected_answer=raw.get("expected_answer"),
                expected_unit=raw.get("expected_unit") or "",
                expected_outcome=raw["expected_outcome"],
                tags=tuple(raw.get("tags") or ()),
                notes=raw.get("notes") or "",
            )
        )
    return cases


# ---------------------------------------------------------------------------
# Unit
# ---------------------------------------------------------------------------


def test_baseline_pure_rational_no_versor_binding() -> None:
    result = run_baseline(GOLD_0001)
    assert result.outcome == "correct"
    assert result.answer == pytest.approx(21.0)
    assert result.operator_bindings == 0
    assert result.readback is not None
    assert result.readback.has_versor_binding is True or result.frame_runnable
    # Baseline path itself does not *require* bindings to compute; frame may still
    # produce them in assess_fraction_decrease for readback.
    assert result.condition == "baseline"


def test_operator_commits_geometric_binding_with_versor_integrity() -> None:
    result = run_operator(GOLD_0001)
    assert result.outcome == "correct"
    assert result.answer == pytest.approx(21.0, abs=1e-6)
    assert result.operator_bindings >= 1
    assert result.readback is not None
    assert result.readback.scale_surface == "3/4"
    assert result.readback.has_versor_binding is True
    assert result.readback.versor_error is not None
    assert result.readback.versor_error < 1e-6


def test_metadata_only_decorates_but_does_not_change_answer() -> None:
    op = run_operator(GOLD_0001)
    meta = run_metadata_only(GOLD_0001)
    assert answers_match(op, meta)
    assert meta.explanation_has_root_note is True
    assert meta.depth is not None
    assert meta.depth.validity == "metadata_only"
    assert meta.depth.mapping_rule_id == DEPTH_METADATA_RULE


def test_depth_condition_records_inactive_mapping_and_matches_operator() -> None:
    op = run_operator(GOLD_0001)
    depth = run_depth(GOLD_0001)
    assert answers_match(op, depth)
    assert depth.depth is not None
    assert depth.depth.validity == "inactive_no_mapping"
    assert depth.depth.mapping_rule_id == DEPTH_EXECUTABLE_MAPPING_RULE
    assert depth.depth.source_pack_ids == ()


def test_determinism_two_runs_identical() -> None:
    a = run_operator(GOLD_0001)
    b = run_operator(GOLD_0001)
    assert answers_match(a, b)
    assert a.refusal_reason == b.refusal_reason
    assert a.operator_bindings == b.operator_bindings


def test_baseline_and_operator_agree_when_both_commit() -> None:
    base = run_baseline(GOLD_0001)
    op = run_operator(GOLD_0001)
    assert base.answer is not None and op.answer is not None
    assert answers_match(base, op)


# ---------------------------------------------------------------------------
# Integration — sealed fixture end-to-end
# ---------------------------------------------------------------------------


def test_sealed_fixture_has_expected_shape() -> None:
    cases = _load_sealed()
    assert len(cases) == 8
    gold = [c for c in cases if c.expected_outcome == "correct"]
    refuse = [c for c in cases if c.expected_outcome == "refused"]
    assert len(gold) == 2
    assert len(refuse) == 6


def test_sealed_gold_cases_operator_and_baseline_correct() -> None:
    for case in _load_sealed():
        if case.expected_outcome != "correct":
            continue
        base = run_baseline(case)
        op = run_operator(case)
        assert base.outcome == "correct", case.case_id
        assert op.outcome == "correct", case.case_id
        assert answers_match(base, op)


def test_sealed_adversarial_cases_refuse_not_wrong() -> None:
    for case in _load_sealed():
        if case.expected_outcome != "refused":
            continue
        op = run_operator(case)
        base = run_baseline(case)
        assert op.outcome == "refused", (case.case_id, op.outcome, op.answer)
        assert base.outcome == "refused", (case.case_id, base.outcome, base.answer)
        assert op.outcome != "wrong"
        assert base.outcome != "wrong"


def test_runner_report_invariants() -> None:
    from evals.relational_operator_ablation.v1.runner import build_report, _load_cases

    report = build_report(_load_cases())
    assert report["sample_size"] == 8
    assert report["findings"]["metadata_only_inert"] is True
    assert report["findings"]["depth_executable_inactive_equals_operator"] is True
    assert report["findings"]["operator_deterministic"] is True
    assert report["findings"]["operator_wrong_zero"] is True
    assert report["findings"]["baseline_wrong_zero"] is True
    assert report["counts"]["operator"]["correct"] >= 2
    assert report["counts"]["operator"]["wrong"] == 0
    assert report["report_sha256"]
    # Deterministic digest across two builds.
    report2 = build_report(_load_cases())
    assert report["report_sha256"] == report2["report_sha256"]


# ---------------------------------------------------------------------------
# Adversarial
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "case",
    [FINAL_VALUE, MULTI_FRACTION],
    ids=["final_value", "multi_fraction"],
)
def test_adversarial_refuse_closed(case: AblationCase) -> None:
    results = run_all_conditions(case)
    for name, result in results.items():
        assert result.outcome == "refused", (name, result.outcome, result.answer)
        assert result.answer is None


def test_scale_out_of_range_operator_and_baseline_refuse() -> None:
    """Gate A2k: scale>1 is fail-closed on both baseline and geometric operator.

    Formerly pinned a pre-existing geometric bypass (negative delta). Obligation
    and geometric admission now share 0 < scale < 1, so operator must refuse.
    """
    base = run_baseline(SCALE_OOR_PREEXISTING)
    op = run_operator(SCALE_OOR_PREEXISTING)
    assert base.outcome == "refused"
    assert base.answer is None
    assert op.outcome == "refused"
    assert op.answer is None
    assert op.operator_bindings == 0


def test_malformed_depth_labels_cannot_elevate_runnable() -> None:
    """Garbage depth must not create a runnable assessment that wasn't runnable."""
    # Use a refuse-gold problem.
    broken_depth = {
        "p0": {"language": "he", "root": "NOT_A_REAL_ROOT_!!!@@@"},
        "p1": {"language": "grc", "root": ""},
    }
    refuse_case = FINAL_VALUE
    clean = run_operator(refuse_case)
    polluted = run_metadata_only(refuse_case, depth_labels=broken_depth)
    assert clean.outcome == "refused"
    assert polluted.outcome == "refused"
    assert polluted.answer is None
    # Must not flip to correct via depth.
    assert polluted.outcome != "correct"


def test_valid_depth_metadata_on_gold_does_not_change_answer() -> None:
    depths = {
        "p0": {"language": "he", "root": "א-מ-נ"},
        "p1": {"language": "grc", "root": "λογ"},
    }
    op = run_operator(GOLD_0001)
    meta = run_metadata_only(GOLD_0001, depth_labels=depths)
    assert answers_match(op, meta)
    assert meta.explanation_has_root_note is True


def test_distractor_quantity_case_refuses() -> None:
    cases = {c.case_id: c for c in _load_sealed()}
    case = cases["roa-v1-0006"]
    assert run_operator(case).outcome == "refused"
    assert run_baseline(case).outcome == "refused"


def test_percent_partition_out_of_family_refuses_on_fraction_organ() -> None:
    cases = {c.case_id: c for c in _load_sealed()}
    case = cases["roa-v1-0005"]
    assert run_operator(case).outcome == "refused"


def test_affine_confuser_refuses() -> None:
    cases = {c.case_id: c for c in _load_sealed()}
    case = cases["roa-v1-0004"]
    assert run_operator(case).outcome == "refused"


def test_no_mutation_of_input_case() -> None:
    problem = GOLD_0001.problem
    run_operator(GOLD_0001)
    run_baseline(GOLD_0001)
    run_metadata_only(GOLD_0001)
    assert GOLD_0001.problem == problem


def test_readback_preserves_role_provenance_on_gold() -> None:
    result = run_operator(GOLD_0001)
    assert result.readback is not None
    role_names = {r for r, _ in result.readback.roles}
    assert "base_quantity" in role_names
    assert "scale" in role_names
    assert result.readback.scale_surface == "3/4"
