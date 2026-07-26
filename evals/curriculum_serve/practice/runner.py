"""Sealed-practice runner for curriculum serving (ADR-0262/0264, Phase C).

Folds the ADR-0199 ``run_practice`` engine over the enumerated atom corpus
(``generator.py``) and reads each band's ``ClassTally`` through the reliability
gate. Two outputs, exactly mirroring ``evals/deduction_serve/practice/runner.py``:

- ``run()`` — the falsifiable report: which *(subject × relation family)* bands
  earned SERVE, at what committed volume, and with what verdict MIX.
- ``seal_ledger()`` — writes the SHA-sealed artifact the serving reader
  (``chat/curriculum_serve_license.py``) trusts. That module's docstring already
  names this function as the only writer; this is the function it named.

**The artifact is NOT committed by this arc, and that is a finding, not an
omission.** Every band with a routable space ≥657 reaches θ_SERVE on the UNKNOWN
class alone: ``physics · causal`` commits 7 taught edges and 713 correct
non-commitments, and ``conservative_floor(660, 660) = 0.990046 ≥ 0.99``. So
sealing this ledger today would flip four bands from disclosed to authoritative on
a mix that is ~99% non-entailed — which ADR-0262 §5.1 explicitly rules
unacceptable, and which the still-open outcome-mix ruling (ADR-0264 R9's recorded
non-decision; ``docs/research/distinct-evidence-audit-2026-07-25.md``) exists to
settle. The plan of record's Phase-1 exit criterion asked for a ledger that is
"real (still-unearned)"; building the producer shows that state is unreachable.
Committing the artifact is therefore a ratification, and it is left to the
explicit ``core proposal-queue reseal`` verb a human runs (Phase D).

Determinism: the corpus is enumerated + sorted (no clock, no RNG) and
``run_practice`` is a pure fold, so the sealed ledger is byte-identical across
runs — safe to commit and SHA-verify on load, whenever it is committed.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from core.learning_arena.engine import run_practice
from core.ratified_ledger import seal_artifact, write_sealed_ledger
from core.reliability_gate import Action, Ceilings, ClassTally, license_for
from evals.curriculum_serve.practice.generator import (
    CASES_PER_BAND,
    CurriculumOracleTether,
    CurriculumSolver,
    all_gold_problems,
    assert_practice_atoms_distinct,
)

#: The committed sealed ledger lives next to its serving READER (chat/), the
#: topology the estimation and deduction ledgers already use.
_SEALED_LEDGER_PATH = (
    Path(__file__).resolve().parents[3] / "chat" / "data" / "curriculum_serve_ledger.json"
)


def build_ledger(cap: int = CASES_PER_BAND) -> dict[str, ClassTally]:
    """Run sealed practice over the enumerated corpus → per-band ledger."""
    report = run_practice(
        all_gold_problems(cap), CurriculumSolver(), CurriculumOracleTether()
    )
    return dict(report.ledger)


def build_mix(cap: int = CASES_PER_BAND) -> dict[str, dict[str, int]]:
    """Per-band GOLD verdict mix — the figure the reliability gate cannot see.

    ``ClassTally`` carries ``correct``/``wrong``/``refused`` and no verdict axis, so
    a correct UNKNOWN is indistinguishable from a correct ENTAILED once tallied.
    That is precisely why a band can clear θ_SERVE on non-commitments alone, and
    why the mix has to be reported alongside the license rather than inferred from
    it.
    """
    tether = CurriculumOracleTether()
    mix: dict[str, dict[str, int]] = {}
    for problem in all_gold_problems(cap):
        band = mix.setdefault(problem.class_name, {})
        gold = tether.gold_answer(problem)
        band[gold] = band.get(gold, 0) + 1
    return mix


def run(ceilings: Ceilings | None = None, cap: int = CASES_PER_BAND) -> dict[str, Any]:
    """Build the ledger and report the SERVE verdict + mix per band."""
    ceilings = ceilings if ceilings is not None else Ceilings.default()
    ledger = build_ledger(cap)
    mix = build_mix(cap)
    classes: dict[str, Any] = {}
    for band, tally in sorted(ledger.items()):
        serve = license_for(tally, Action.SERVE, ceilings)
        band_mix = mix.get(band, {})
        entailed = band_mix.get("entailed", 0)
        classes[band] = {
            "correct": tally.correct,
            "wrong": tally.wrong,
            "refused": tally.refused,
            "committed": tally.committed,
            "reliability": tally.reliability,
            "coverage": tally.coverage,
            "serve_licensed": serve.licensed,
            "serve_ratio": serve.ratio,
            "gold_mix": dict(sorted(band_mix.items())),
            "entailed_share": (
                round(entailed / tally.committed, 6) if tally.committed else 0.0
            ),
        }
    return {
        "lane": "curriculum-serve-practice",
        "classes": classes,
        "any_band_serve_licensed": any(c["serve_licensed"] for c in classes.values()),
        "wrong_is_zero": all(c["wrong"] == 0 for c in classes.values()),
    }


def build_sealed_artifact(cap: int = CASES_PER_BAND) -> dict[str, Any]:
    """The sealed-ledger dict (self-verifying ``content_sha256``)."""
    return seal_artifact(
        build_ledger(cap),
        schema="curriculum_serve_ledger_v1",
        note=(
            "Sealed-practice committed ledger for curriculum-grounded serving "
            "(ADR-0262, sized per ADR-0264 R9). Engine reads, never writes. "
            "Ceilings stay at safe defaults (theta_SERVE=0.99). One committed case "
            "per DISTINCT routable query atom, so committed == distinct evidence by "
            "construction. NOTE: reliability here is dominated by correct "
            "non-commitments; read `gold_mix` from the runner report before "
            "treating a licensed band as demonstrated curriculum competence."
        ),
        provenance="evals.curriculum_serve.practice.runner.seal_ledger",
    )


def seal_ledger(
    path: Path = _SEALED_LEDGER_PATH, cap: int = CASES_PER_BAND
) -> dict[str, Any]:
    """Regenerate + write the committed sealed ledger.

    Verifies the R9 distinct-evidence invariant first: a producer that padded
    could never seal, rather than sealing and being caught by the audit later.
    """
    assert_practice_atoms_distinct(cap)
    return write_sealed_ledger(path, build_sealed_artifact(cap))


def _full_sweep() -> dict[str, Any]:
    """Every routable atom in every band — the exhaustive agreement measurement.

    Not the sealed corpus (that is capped at :data:`CASES_PER_BAND`); this is the
    evidence that the cap is a sampling choice and not a hiding place. Runs the
    whole ~70k-atom space, so it is a deliberate CLI invocation and not a test.
    """
    return run(cap=10**9)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--seal", action="store_true",
        help="regenerate + write chat/data/curriculum_serve_ledger.json "
             "(a RATIFICATION — see the module docstring before running it)",
    )
    parser.add_argument(
        "--full", action="store_true",
        help="report over EVERY routable atom instead of the capped corpus (slow)",
    )
    args = parser.parse_args(argv)

    if args.seal:
        artifact = seal_ledger()
        print(f"sealed {len(artifact['classes'])} bands -> {_SEALED_LEDGER_PATH}")
        return 0

    report = _full_sweep() if args.full else run()
    for band, c in report["classes"].items():
        print(
            f"  {band:44s} committed={c['committed']:6d} wrong={c['wrong']} "
            f"refused={c['refused']:4d} reliability={c['reliability']:.5f} "
            f"SERVE={str(c['serve_licensed']):5s} entailed={c['gold_mix'].get('entailed', 0):3d} "
            f"({c['entailed_share']:.4%})"
        )
    print(
        f"any_band_serve_licensed={report['any_band_serve_licensed']} "
        f"wrong_is_zero={report['wrong_is_zero']}"
    )
    return 0 if report["wrong_is_zero"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
