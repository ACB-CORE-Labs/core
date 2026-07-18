"""Run the ADR-0246 §6.1/§6.2 geometric + path eval suite and emit the report.

Usage:  uv run python -m evals.adr_0246_geometric_suite [out.json]

Deterministic, off-serving. Prints a per-case pass/fail summary and the overall
verdict; optionally writes the structured JSON report. Exit code 0 iff every case
passed (so it can gate a run log), 1 otherwise.
"""

from __future__ import annotations

import json
import sys

from evals.adr_0246_geometric_suite import build_suite_report


def main() -> int:
    report = build_suite_report()
    for suite in ("geometric_suite", "path_suite"):
        print(f"\n[{suite}]")
        for case in report[suite]:
            mark = "PASS" if case["passed"] else "FAIL"
            print(f"  {mark}  {case['name']}")
            if not case["passed"]:
                for check, ok in case["checks"].items():
                    if not ok:
                        print(f"        ✗ {check}")
    print(
        f"\n{report['passed_count']}/{report['case_count']} cases passed; "
        f"all_passed={report['all_passed']}"
    )
    print(f"placeholders (uncertified): {report['placeholders']}")
    if len(sys.argv) > 1:
        with open(sys.argv[1], "w", encoding="utf-8") as fh:
            fh.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
        print(f"report written to {sys.argv[1]}")
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
