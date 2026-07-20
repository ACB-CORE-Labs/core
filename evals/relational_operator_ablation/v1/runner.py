"""Sealed measurement runner for Deterministic Relational Operator Ablation v1.

Conditions: baseline | operator | depth | metadata_only | invalid (adversarial cases).

Run:
  PYTHONPATH=. python -m evals.relational_operator_ablation.v1.runner

Writes ``report.json`` beside this module (override via CORE_ROA_REPORT_PATH).
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from generate.relational_operator_ablation import (
    AblationCase,
    ConditionName,
    answers_match,
    run_all_conditions,
    run_condition,
)

_HERE = Path(__file__).resolve().parent
_CASES = _HERE / "cases.jsonl"
_REPORT = Path(
    os.environ.get("CORE_ROA_REPORT_PATH", str(_HERE / "report.json"))
)
_SCHEMA_VERSION = 1
_LANE = "relational_operator_ablation/v1"
_CONDITIONS: tuple[ConditionName, ...] = (
    "baseline",
    "operator",
    "depth",
    "metadata_only",
    "invalid",
)


def _load_cases(path: Path = _CASES) -> list[AblationCase]:
    cases: list[AblationCase] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
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


def _empty_counts() -> dict[str, int]:
    return {"correct": 0, "wrong": 0, "refused": 0, "n": 0, "coverage": 0}


def build_report(cases: list[AblationCase]) -> dict[str, Any]:
    per_condition: dict[str, dict[str, int]] = {
        c: _empty_counts() for c in _CONDITIONS
    }
    per_case: list[dict[str, Any]] = []
    inert_checks: list[dict[str, Any]] = []
    determinism: list[dict[str, Any]] = []

    for case in cases:
        row: dict[str, Any] = {"case_id": case.case_id, "tags": list(case.tags)}
        results = run_all_conditions(case)

        # Always score primary four conditions.
        for name in ("baseline", "operator", "depth", "metadata_only"):
            result = results[name]
            bucket = per_condition[name]
            bucket["n"] += 1
            bucket[result.outcome] += 1
            if result.answer is not None:
                bucket["coverage"] += 1
            row[name] = result.as_json()

        # Invalid condition only for adversarial/refuse-gold cases.
        if "invalid" in results:
            result = results["invalid"]
            bucket = per_condition["invalid"]
            bucket["n"] += 1
            bucket[result.outcome] += 1
            if result.answer is not None:
                bucket["coverage"] += 1
            row["invalid"] = result.as_json()
        else:
            row["invalid"] = {
                "condition": "invalid",
                "case_id": case.case_id,
                "outcome": "skipped_not_adversarial",
                "note": "invalid condition reserved for refuse-gold/adversarial tags",
            }

        # Metadata-only must match operator answers (inert depth labels).
        op = results["operator"]
        meta = results["metadata_only"]
        depth = results["depth"]
        base = results["baseline"]
        inert_checks.append(
            {
                "case_id": case.case_id,
                "operator_eq_metadata": answers_match(op, meta),
                "operator_eq_depth": answers_match(op, depth),
                "baseline_eq_operator_when_both_commit": (
                    answers_match(base, op)
                    if base.answer is not None and op.answer is not None
                    else None
                ),
                "metadata_has_root_note_when_runnable": meta.explanation_has_root_note
                if meta.frame_runnable
                else None,
            }
        )

        # Determinism: re-run operator twice.
        again = run_condition("operator", case)
        determinism.append(
            {
                "case_id": case.case_id,
                "operator_repeat_identical": answers_match(op, again)
                and op.refusal_reason == again.refusal_reason,
            }
        )
        per_case.append(row)

    # Coverage fraction
    for name, bucket in per_condition.items():
        n = bucket["n"] or 1
        bucket["coverage_rate"] = bucket["coverage"] / n
        bucket["correct_rate"] = bucket["correct"] / n
        bucket["wrong_rate"] = bucket["wrong"] / n
        bucket["refused_rate"] = bucket["refused"] / n

    inert_ok = all(c["operator_eq_metadata"] for c in inert_checks)
    depth_inactive_ok = all(c["operator_eq_depth"] for c in inert_checks)
    det_ok = all(d["operator_repeat_identical"] for d in determinism)
    no_wrong_on_operator = per_condition["operator"]["wrong"] == 0
    no_wrong_on_baseline = per_condition["baseline"]["wrong"] == 0

    findings = {
        "metadata_only_inert": inert_ok,
        "depth_executable_inactive_equals_operator": depth_inactive_ok,
        "operator_deterministic": det_ok,
        "operator_wrong_zero": no_wrong_on_operator,
        "baseline_wrong_zero": no_wrong_on_baseline,
        "operator_solves_gold_fraction_cases": per_condition["operator"]["correct"]
        >= 2,
        "scientific_note": (
            "Depth executable mapping is intentionally inactive on English-only "
            "inputs (anti-circularity). Metadata-only he-root labels must not "
            "change answers. Operator geometric path and baseline scalar path "
            "should agree when both commit."
        ),
    }

    body = {
        "schema_version": _SCHEMA_VERSION,
        "lane": _LANE,
        "family": "proportional_change.decrease_to_fraction",
        "organ": "fraction_decrease",
        "sample_size": len(cases),
        "conditions": list(_CONDITIONS),
        "counts": per_condition,
        "findings": findings,
        "inert_checks": inert_checks,
        "determinism": determinism,
        "per_case": per_case,
        "limitations": [
            "n=8 sealed cases; not a full GSM8K claim.",
            "Depth-as-executable is unproven for English arithmetic; recorded inactive.",
            "percent_partition dual-track is out of family scope for this slice.",
            "Chat CognitiveTurnPipeline still passes contract_assessment=None.",
        ],
    }
    # Content-addressed digest of counts+findings+case outcomes (stable).
    digest_src = json.dumps(
        {
            "counts": per_condition,
            "findings": findings,
            "outcomes": [
                {
                    "id": row["case_id"],
                    "baseline": row["baseline"]["outcome"],
                    "operator": row["operator"]["outcome"],
                    "depth": row["depth"]["outcome"],
                    "metadata_only": row["metadata_only"]["outcome"],
                }
                for row in per_case
            ],
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    body["report_sha256"] = hashlib.sha256(digest_src).hexdigest()
    return body


def write_report(report: dict[str, Any], path: Path = _REPORT) -> None:
    path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    cases = _load_cases()
    report = build_report(cases)
    write_report(report)
    findings = report["findings"]
    ok = (
        findings["metadata_only_inert"]
        and findings["depth_executable_inactive_equals_operator"]
        and findings["operator_deterministic"]
        and findings["operator_wrong_zero"]
        and findings["baseline_wrong_zero"]
        and findings["operator_solves_gold_fraction_cases"]
    )
    print(
        json.dumps(
            {
                "lane": _LANE,
                "sample_size": report["sample_size"],
                "counts": report["counts"],
                "findings": findings,
                "report_sha256": report["report_sha256"],
                "passed": ok,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
