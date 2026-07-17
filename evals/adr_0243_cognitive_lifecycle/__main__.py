"""CLI: python -m evals.adr_0243_cognitive_lifecycle <subcommand> [--out PATH]

Subcommands (research / OFF-SERVING only; never imported from chat/runtime.py):

  benchmark   ADR-0243 Phase 4 falsifiability metrics (default) — fidelity,
              surprise separation, insertion cost, f32 drift, decisive falsifier;
              exits non-zero if the overall gate fails.
  corridor    Fixed-replay sensorium corridor artifact (Lane B, I-04 consumer).
  falsifier   Decisive propositional field-vs-ROBDD-gold artifact (wrong == 0).

Each writes a JSON artifact to ``--out`` (default: stdout).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _emit(payload: dict, out: Path | None) -> None:
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if out is not None:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="evals.adr_0243_cognitive_lifecycle")
    sub = parser.add_subparsers(dest="command")
    for name in ("benchmark", "corridor", "falsifier"):
        p = sub.add_parser(name)
        p.add_argument("--out", type=Path, default=None, help="Output path (default: stdout)")

    args = parser.parse_args(argv)
    command = args.command or "benchmark"
    out = getattr(args, "out", None)

    if command == "benchmark":
        from evals.adr_0243_cognitive_lifecycle.benchmark import run_benchmark

        verdict = run_benchmark()
        _emit(verdict.as_dict(), out)
        # Non-zero exit on falsification so the gate is scriptable.
        return 0 if verdict.overall_passed else 1

    if command == "corridor":
        from evals.adr_0243_cognitive_lifecycle import run_fixed_replay

        _emit(run_fixed_replay(), out)
        return 0

    if command == "falsifier":
        from evals.adr_0243_cognitive_lifecycle.propositional_falsifier import (
            run_propositional_falsifier,
        )

        artifact = run_propositional_falsifier()
        _emit(artifact, out)
        return 0 if int(artifact["wrong"]) == 0 else 1

    parser.error(f"unknown command: {command!r}")  # NoReturn: argparse exits (code 2)


if __name__ == "__main__":
    raise SystemExit(main())
