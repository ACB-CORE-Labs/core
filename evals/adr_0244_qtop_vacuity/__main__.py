"""CLI: python -m evals.adr_0244_qtop_vacuity [--out PATH]

Emits the Q_top vacuity-probe artifact as JSON (ADR-0244 §2.3 / D4 evidence).
Exit 0 iff the hollow-gate verdict is proven. Research / OFF-SERVING only.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from evals.adr_0244_qtop_vacuity import run_qtop_vacuity_probe


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, default=None, help="Output path (default: stdout)")
    args = p.parse_args(argv)
    artifact = run_qtop_vacuity_probe()
    text = json.dumps(artifact, indent=2, sort_keys=True) + "\n"
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0 if artifact["proven_vacuous"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
