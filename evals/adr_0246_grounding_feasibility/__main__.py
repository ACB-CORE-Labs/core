"""Run the ADR-0246 §11 grounding-feasibility study and emit the report.

Usage:  uv run python -m evals.adr_0246_grounding_feasibility [out.json]

Collects the live TRAIN (benign) and HELD-OUT (paraphrase) cohorts (spins up a
fresh empty-vault runtime twice), runs the recovery controls + cross-cohort
generator analysis + discrimination check, and prints the honest verdict.
"""

from __future__ import annotations

import json
import sys

from evals.adr_0246_grounding_feasibility import build_feasibility_report


def main() -> int:
    report = build_feasibility_report()
    summary = {
        "cohorts": report["cohorts"],
        "recovery_controls": report["recovery_controls"],
        "cross_cohort_top2_cosine_similarity": report["cross_cohort_top2_cosine_similarity"],
        "cross_cohort_cosine_percentile_in_null": report["cross_cohort_cosine_percentile_in_null"],
        "discrimination_auc_adversarial_vs_heldout": report["discrimination_auc_adversarial_vs_heldout"],
        "discrimination_auc_ci95": report["discrimination_auc_ci95"],
        "precision_transport": report["precision_transport"],
        "plane_energy_fractions": report["plane_energy_fractions"],
        "verdict": report["verdict"],
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    if len(sys.argv) > 1:
        with open(sys.argv[1], "w", encoding="utf-8") as fh:
            fh.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
        print(f"\nfull report written to {sys.argv[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
