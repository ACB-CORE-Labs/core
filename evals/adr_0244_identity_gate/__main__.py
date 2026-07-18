"""CLI: python -m evals.adr_0244_identity_gate [--out PATH]

Emits the operator-preservation identity-gate detection-value ablation as JSON
(ADR-0244 §2.2 / D4 Phase 2c). Exit 0 iff the wave gate separates the geometric
attack panel from the aligned panel AND adds detection value over the legacy
path. Research / OFF-SERVING only.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from evals.adr_0244_identity_gate import run_identity_gate_ablation


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out", type=Path, default=None, help="Output path (default: stdout)"
    )
    args = parser.parse_args(argv)
    artifact = run_identity_gate_ablation()
    text = json.dumps(artifact, indent=2, sort_keys=True) + "\n"
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    verdict = artifact["verdict"]
    ok = (
        verdict["gate_discriminates_geometric_attacks"]
        and verdict["detection_value_over_legacy"]
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
