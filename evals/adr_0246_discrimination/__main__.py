"""Run the ADR-0246 §6.3 discrimination report and emit it.

Usage:  uv run python -m evals.adr_0246_discrimination [out.json]

Collects the live benign cohort (spins up a fresh empty-vault runtime), runs the
§3.7 admit surface over benign + adversarial + synthetic-near-identity cohorts,
and prints the honest rates / separation / verdict. Optionally writes the JSON.
"""

from __future__ import annotations

import json
import sys
import time

from evals.adr_0246_discrimination import build_discrimination_report


def main() -> int:
    t0 = time.perf_counter()
    report = build_discrimination_report()
    report["runtime"] = {"report_wall_seconds": round(time.perf_counter() - t0, 3)}
    print(json.dumps(
        {k: report[k] for k in ("cohorts", "rates", "separation", "verdict")},
        indent=2, sort_keys=True,
    ))
    if len(sys.argv) > 1:
        with open(sys.argv[1], "w", encoding="utf-8") as fh:
            fh.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
        print(f"\nreport written to {sys.argv[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
