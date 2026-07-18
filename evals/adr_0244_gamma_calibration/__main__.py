"""CLI: python -m evals.adr_0244_gamma_calibration [--out PATH]

Emits the ADR-0244 §2.4 γ_id tuning certificate + live-separability verdict as
JSON (D4 Phase 3). Exit 0 iff the Fibonacci search produced a valid certificate
that separates the geometric attack signal (the calibration machinery is sound).

Note the verdict distinction the payload carries: ``geometric_calibration_valid``
(gates the exit code) is NOT ``flag_flip_authorized``. The live serving flag flip
is authorized only if benign traffic is also separable — which it is not — so a
clean exit here means "the certificate is valid", not "flip the flag". Research /
OFF-SERVING only.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from evals.adr_0244_gamma_calibration import run_gamma_calibration


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out", type=Path, default=None, help="Output path (default: stdout)"
    )
    args = parser.parse_args(argv)
    artifact = run_gamma_calibration()
    text = json.dumps(artifact, indent=2, sort_keys=True) + "\n"
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0 if artifact["verdict"]["geometric_calibration_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
