"""CLI: python -m evals.adr_0242_v2_energy_compare [--out PATH]

Writes the fixed-replay Fibonacci/dyadic/log comparative artifact as JSON.
Research-only; never mutates FieldEnergyOperator defaults.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from evals.adr_0242_v2_energy_compare import run_fixed_replay


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Optional output path (default: stdout)",
    )
    args = p.parse_args(argv)
    artifact = run_fixed_replay()
    text = json.dumps(artifact, indent=2, sort_keys=True) + "\n"
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
