"""ADR-0131.G.3 — G3 Numerics capability runner.

Feeds curated cases from cases.jsonl through the candidate-graph pipeline,
ensuring wrong == 0 is preserved and verifying the correct outcomes.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from evals.gsm8k_math.runner import _score_one_candidate_graph

_HERE = Path(__file__).resolve().parent
_CASES_PATH = _HERE / "cases.jsonl"
_REPORT_PATH = _HERE / "report.json"


def load_cases(path: Path = _CASES_PATH) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def _adapt(case: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": case["case_id"],
        "problem": case["problem"],
        "expected_answer": case["expected_answer"] if case["expected_answer"] is not None else 0.0,
        "expected_unit": case["expected_unit"] if case["expected_unit"] is not None else "",
    }


def build_report(cases: list[dict[str, Any]]) -> dict[str, Any]:
    per_case: list[dict[str, Any]] = []
    counts = {"correct": 0, "wrong": 0, "refused": 0}
    
    for raw in cases:
        expected_outcome = raw["expected"]
        outcome = _score_one_candidate_graph(_adapt(raw))
        
        # Decide if the outcome matches expectation
        if expected_outcome == "solved_correct":
            if outcome.outcome == "correct":
                verdict = "correct"
            else:
                verdict = outcome.outcome
        elif expected_outcome == "refused":
            if outcome.outcome == "refused":
                verdict = "correct"
            else:
                verdict = "wrong"
        else:
            verdict = "wrong"
            
        counts[verdict] += 1
        per_case.append(
            {
                "case_id": raw["case_id"],
                "verdict": verdict,
                "outcome": outcome.outcome,
                "reason": outcome.reason,
            }
        )
        
    total = len(cases)
    correct_rate = counts["correct"] / total if total else 0.0
    wrong_count_is_zero = counts["wrong"] == 0
    passed = wrong_count_is_zero and (correct_rate >= 1.0)
    
    metrics = {
        "cases_total": total,
        "correct": counts["correct"],
        "wrong": counts["wrong"],
        "refused": counts["refused"],
        "correct_rate": correct_rate,
        "wrong_count_is_zero": wrong_count_is_zero,
        "overall_pass": passed,
    }
    
    return {
        "schema_version": 1,
        "adr": "0131.G.3",
        "sample_path": "evals/math_capability_axes/G3_numerics/v1/cases.jsonl",
        "sample_count": total,
        "metrics": metrics,
        "exit_criterion": {
            "correct_min_rate": 1.0,
            "wrong_max": 0,
            "passed": passed,
        },
        "per_case": per_case,
    }


def write_report(report: dict[str, Any], path: Path = _REPORT_PATH) -> None:
    path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    cases = load_cases()
    report = build_report(cases)
    write_report(report)
    print(f"Metrics: {report['metrics']}")
    return 0 if report["exit_criterion"]["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
