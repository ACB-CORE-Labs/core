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


def distinct_gold_problems() -> list[Any]:
    """The practice corpus with replayed cases collapsed — one per distinct decision.

    **R-13, 2026-07-28.** Wilson lower-bound licensing (`conservative_floor`) is a
    statement about *independent trials*. A replay of the same sealed case is one
    trial observed again, not a new one, so folding the raw corpus inflated every
    band: 720 "committed" decisions drawn from as few as **28** distinct cases, and
    `conservative_floor(720, 720) = 0.990868` cleared θ_SERVE=0.99 on evidence that
    `conservative_floor(28, 28) = 0.808413` does not come close to supporting.

    The key is the case **text**, which is the definition already agreed in-repo by
    ``tests/test_volume_honesty.py`` and the audit behind it: two cases with identical
    text are indisputably the same decision. It deliberately *under*-reports — a
    tighter key (the normalized atom tuple) would collapse spelling variants and find
    more inflation — because under-reporting makes the measured gap a **floor** on the
    real gap rather than a guess at it.

    The raw corpus is left alone: it is the practice *material*, and running a case
    twice is a legitimate thing for practice to do. What may not happen is a replay
    being *counted* as new evidence when a license is computed from the count.
    """
    seen: set[tuple[str, str]] = set()
    out: list[Any] = []
    for problem in all_gold_problems():
        key = (problem.class_name, problem.payload["text"])
        if key in seen:
            continue
        seen.add(key)
        out.append(problem)
    return out


def assert_sealed_evidence_distinct(ledger: dict[str, ClassTally]) -> None:
    """The R9 invariant on the LEDGER ABOUT TO BE SEALED: a padded producer cannot seal.

    Mirrors ``evals.curriculum_serve.practice.runner.assert_practice_atoms_distinct``,
    which has carried this guarantee on the sibling ledger since ADR-0264 R9. The
    deduction sealer had no equivalent, which is precisely how 21 of 25 bands came to
    hold SERVE licences their evidence never supported.

    Catching it *here* rather than in the audit matters: an audit finds a padded ledger
    after it is committed and trusted, and unwinding that exposure then needs a ruling
    (it needed one — R-13). This raises before the artifact exists.

    **It takes the built ledger, and that is the whole point.** The first version of
    this guard compared ``all_gold_problems()`` to ``distinct_gold_problems()`` — two
    functions that agree with each other by construction, and neither of which is what
    ``build_ledger`` folds. Reverting ``build_ledger`` to the raw corpus sailed straight
    past it and re-sealed the inflated artifact. A guard that checks something
    *adjacent* to the thing it protects is the exact failure this ledger already
    suffered once; it was caught here only because the guard was sabotage-tested rather
    than trusted. The invariant is about the **artifact**, so the artifact is the input.
    """
    distinct: dict[str, set[str]] = {}
    for problem in all_gold_problems():
        distinct.setdefault(problem.class_name, set()).add(problem.payload["text"])

    padded = {
        band: (tally.committed, len(distinct.get(band, ())))
        for band, tally in ledger.items()
        if tally.committed != len(distinct.get(band, ()))
    }
    if padded:
        detail = ", ".join(
            f"{band}: ledger committed={got} but only {want} distinct cases exist"
            for band, (got, want) in sorted(padded.items())
        )
        raise ValueError(
            "refusing to seal — the ledger counts replays as independent trials, which "
            "is the precondition conservative_floor assumes and these bands violate: "
            f"{detail}"
        )


def build_ledger() -> dict[str, ClassTally]:
    """Run sealed practice over the corpus → per-band ledger, on DISTINCT evidence.

    ``committed == distinct`` by construction, which is the same guarantee the
    curriculum ledger states in its own seal note. Before R-13 this folded the raw
    corpus and the difference was invisible in the artifact: a band recorded 720/720
    whether that was 720 decisions or 28 decisions replayed.
    """
    report = run_practice(distinct_gold_problems(), DeductionSolver(), ConstructionGoldTether())
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


def build_sealed_artifact(ledger: dict[str, ClassTally] | None = None) -> dict[str, Any]:
    """The committed sealed-ledger dict (self-verifying ``content_sha256``).

    Formatting and hashing come from the shared bridge (ADR-0263) — byte
    -identical to what this module wrote before the extraction, which is how
    the refactor is proven safe: re-sealing must not move the artifact.
    """
    return seal_artifact(
        build_ledger() if ledger is None else ledger,
        schema="deduction_serve_ledger_v1",
        note=(
            "Sealed-practice committed ledger for deduction serving (ADR-0256). "
            "Engine reads, never writes. Ceilings stay at safe defaults "
            "(theta_SERVE=0.99). A band earns SERVE by demonstrated pipeline "
            "reliability (reader+projector+engine) at volume >= 657 committed. "
            "RE-COUNTED 2026-07-28 under R-13: one committed case per DISTINCT "
            "decision (case text), so committed == distinct evidence by construction. "
            "The prior seal folded the raw corpus and counted replays as independent "
            "trials, which the Wilson floor assumes they are not; 21 of 25 bands held "
            "SERVE licences their evidence never supported and are demoted here."
        ),
        provenance="evals.deduction_serve.practice.runner.seal_ledger",
    )


def seal_ledger(path: Path = _SEALED_LEDGER_PATH) -> dict[str, Any]:
    """Regenerate + write the committed sealed ledger.

    Two preconditions, both checked before anything is written:

    * ``assert_practice_gold_sound()`` — a mis-stated gold can never seal.
    * ``assert_sealed_evidence_distinct(ledger)`` — a producer counting replays as
      independent trials can never seal (R-13 / ADR-0264 R9). It is handed the built
      ledger rather than the corpus, because the corpus is not what gets sealed.
    """
    assert_practice_gold_sound()
    ledger = build_ledger()
    assert_sealed_evidence_distinct(ledger)
    return write_sealed_ledger(path, build_sealed_artifact(ledger))


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
