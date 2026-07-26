"""Practice runner for the deduction-serve arena (Phase 3, ADR-0256).

Folds the ADR-0199 ``run_practice`` engine over the synthetic shape-band corpus
(``gold.py``) and reads the per-band ``ClassTally`` through the reliability gate.
Two outputs:

- ``run()`` — the falsifiable discrimination report: which shape-bands earned
  the SERVE license and at what committed volume/reliability.
- ``seal_ledger()`` — regenerates the committed, SHA-sealed ledger artifact the
  serving reader (``chat/deduction_serve_license.py``) trusts. The engine READS
  that artifact; only this sealed-practice runner WRITES it.

Determinism: the corpus is synthetic + indexed (no clock/RNG), ``run_practice``
is a pure fold, so the sealed ledger is byte-identical across runs — safe to
commit and SHA-verify on load.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from core.learning_arena.engine import run_practice
from core.ratified_ledger import seal_artifact, tally_dict, write_sealed_ledger
from core.reliability_gate import Action, Ceilings, ClassTally, license_for
from evals.deduction_serve.practice.gold import (
    ConstructionGoldTether,
    DeductionSolver,
    all_gold_problems,
    assert_practice_gold_sound,
)

#: The committed sealed ledger lives next to its serving READER (chat/), mirroring
#: the estimation ledger's topology (producer in evals/, artifact by the reader).
_SEALED_LEDGER_PATH = (
    Path(__file__).resolve().parents[3] / "chat" / "data" / "deduction_serve_ledger.json"
)


def build_ledger() -> dict[str, ClassTally]:
    """Run sealed practice over the synthetic corpus → per-band ledger."""
    report = run_practice(all_gold_problems(), DeductionSolver(), ConstructionGoldTether())
    return dict(report.ledger)


def _tally_dict(tally: ClassTally) -> dict[str, Any]:
    return tally_dict(tally)


def run(ceilings: Ceilings | None = None) -> dict[str, Any]:
    """Build the ledger and report the SERVE license verdict per shape-band."""
    ceilings = ceilings if ceilings is not None else Ceilings.default()
    ledger = build_ledger()
    classes: dict[str, Any] = {}
    for cls, tally in sorted(ledger.items()):
        serve = license_for(tally, Action.SERVE, ceilings)
        classes[cls] = {
            "correct": tally.correct,
            "wrong": tally.wrong,
            "refused": tally.refused,
            "reliability": tally.reliability,
            "serve_licensed": serve.licensed,
            "serve_ratio": serve.ratio,
        }
    all_serve = bool(classes) and all(c["serve_licensed"] for c in classes.values())
    wrong_is_zero = all(c["wrong"] == 0 for c in classes.values())
    return {
        "lane": "deduction-serve-practice",
        "classes": classes,
        "all_bands_serve_licensed": all_serve,
        "wrong_is_zero": wrong_is_zero,
    }


def build_sealed_artifact() -> dict[str, Any]:
    """The committed sealed-ledger dict (self-verifying ``content_sha256``).

    Formatting and hashing come from the shared bridge (ADR-0263) — byte
    -identical to what this module wrote before the extraction, which is how
    the refactor is proven safe: re-sealing must not move the artifact.
    """
    return seal_artifact(
        build_ledger(),
        schema="deduction_serve_ledger_v1",
        note=(
            "Sealed-practice committed ledger for deduction serving (ADR-0256). "
            "Engine reads, never writes. Ceilings stay at safe defaults "
            "(theta_SERVE=0.99). A band earns SERVE by demonstrated pipeline "
            "reliability (reader+projector+engine) at volume >= 657 committed."
        ),
        provenance="evals.deduction_serve.practice.runner.seal_ledger",
    )


def seal_ledger(path: Path = _SEALED_LEDGER_PATH) -> dict[str, Any]:
    """Regenerate + write the committed sealed ledger. Verifies corpus soundness
    against the independent oracle first (a mis-stated gold can never seal)."""
    assert_practice_gold_sound()
    return write_sealed_ledger(path, build_sealed_artifact())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--seal", action="store_true",
        help="regenerate + write the committed sealed ledger (chat/data/deduction_serve_ledger.json)",
    )
    args = parser.parse_args(argv)
    if args.seal:
        artifact = seal_ledger()
        print(f"sealed {len(artifact['classes'])} bands -> {_SEALED_LEDGER_PATH}")
        return 0
    report = run()
    for cls, c in report["classes"].items():
        print(f"  {cls:20s} correct={c['correct']:4d} wrong={c['wrong']} "
              f"reliability={c['reliability']:.5f} SERVE={c['serve_licensed']}")
    print(f"all_bands_serve_licensed={report['all_bands_serve_licensed']} "
          f"wrong_is_zero={report['wrong_is_zero']}")
    return 0 if (report["all_bands_serve_licensed"] and report["wrong_is_zero"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
