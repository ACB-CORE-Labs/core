"""Deduction-serve lane runner — scores the PRODUCTION serving decider.

This is the deduction-serve arc's own capability metric, distinct from
``evals/deductive_logic`` (scores the bare ``entail.py`` engine against
formula strings) and ``evals/comprehension/propositional_runner.py``
(scores reader fidelity via the independent ORACLE as decision procedure).
Here, for each committed case, raw ``text`` is run through the exact
pipeline ``chat/deduction_surface.py`` calls in serving — the shape-gate
(``looks_like_deductive_argument``), the reader (``comprehend``), the
projector (``to_deductive_logic``), and the production ROBDD engine
(``evaluate_entailment_with_trace``) — and the resulting outcome is
compared to independently-authored gold. The prose-rendering step
(``generate.proof_chain.render.render_entailment``) is presentation, not
decision, and is intentionally NOT re-derived here so this lane's pinned
bytes stay stable against wording-only changes; wording is covered by
``tests/test_deduction_surface.py``.

Counts:
* ``correct``  — the pipeline's outcome class matches gold (including a
  correct ``unknown`` or a correct ``declined``).
* ``wrong``    — the pipeline committed to a definite entailed/refuted/
  unknown verdict that disagrees with gold. This MUST stay 0 — a wrong
  answer, not a decline, is the only failure this lane cannot tolerate.
* ``declined`` is never counted as ``wrong`` even when gold expected a
  definite verdict: a decline is a coverage miss (honest), not a
  confabulation. See ``correct_by_gold`` for how many of each class the
  pipeline actually got right, including how many gold-``declined`` cases
  (inconsistent premises, out-of-band shape) it correctly recognized as
  such rather than mis-serving.

Exits non-zero unless every committed case's outcome CLASS matches gold
exactly (a decline scored against a non-``declined`` gold is a miss, not
a pass — this lane's job is to prove committed verdicts are trustworthy
AND that the pipeline declines honestly, not to inflate a pass rate).
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from chat.deduction_surface import looks_like_deductive_argument
from generate.meaning_graph.projectors import to_deductive_logic
from generate.meaning_graph.reader import Comprehension, comprehend
from generate.proof_chain.entail import Entailment, evaluate_entailment_with_trace

_ROOT = Path(__file__).resolve().parent

_SPLITS: tuple[tuple[str, Path], ...] = (
    ("v1", _ROOT / "v1" / "cases.jsonl"),
)

_OUTCOME_TO_CLASS = {
    Entailment.ENTAILED: "entailed",
    Entailment.REFUTED: "refuted",
    Entailment.UNKNOWN: "unknown",
    Entailment.REFUSED: "declined",
}


def _load(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def decide(text: str) -> str:
    """Run the exact pipeline ``chat/deduction_surface.py`` runs in
    serving and return the outcome class: entailed/refuted/unknown/declined.

    Mirrors ``deduction_grounded_surface`` call-for-call up to (but not
    including) the prose render — the same production decision, typed
    instead of rendered, so this lane's assertions are robust to wording
    changes.
    """
    if not looks_like_deductive_argument(text):
        return "declined"
    comp = comprehend(text)
    if not isinstance(comp, Comprehension):
        return "declined"
    projected = to_deductive_logic(comp)
    if projected is None:
        return "declined"
    premises, query = projected
    trace = evaluate_entailment_with_trace(premises, query)
    return _OUTCOME_TO_CLASS[trace.outcome]


def build_report(cases: list[dict]) -> dict:
    counts = Counter({"correct": 0, "wrong": 0, "declined": 0})
    by_gold: Counter[str] = Counter()
    correct_by_gold: Counter[str] = Counter()
    wrong_examples: list[dict] = []

    for case in cases:
        gold = case["gold"]
        by_gold[gold] += 1
        got = decide(case["text"])
        if got == gold:
            counts["correct"] += 1
            correct_by_gold[gold] += 1
        elif got == "declined":
            counts["declined"] += 1
            if len(wrong_examples) < 10:
                wrong_examples.append(
                    {"id": case["id"], "gold": gold, "got": got, "text": case["text"]}
                )
        else:
            counts["wrong"] += 1
            if len(wrong_examples) < 10:
                wrong_examples.append(
                    {"id": case["id"], "gold": gold, "got": got, "text": case["text"]}
                )

    all_cases_correct = counts["correct"] == len(cases)
    return {
        "n": len(cases),
        "counts": dict(counts),
        "by_gold": dict(by_gold),
        "correct_by_gold": dict(correct_by_gold),
        "all_cases_correct": all_cases_correct,
        "mismatch_examples": wrong_examples,
    }


def _run(name: str, path: Path) -> dict:
    report = build_report(_load(path))
    c = report["counts"]
    print(f"[{name}] n={report['n']} correct={c['correct']} "
          f"wrong={c['wrong']} declined_mismatch={c['declined']}")
    if report["mismatch_examples"]:
        print("    MISMATCH examples:")
        for m in report["mismatch_examples"]:
            print(f"      {m['id']}: gold={m['gold']} got={m['got']} text={m['text']!r}")
    return report


def build_combined_report() -> dict:
    """Deterministic per-split + aggregate report over the committed splits.

    Pure over the committed ``cases.jsonl`` files and the deterministic
    production pipeline: same inputs -> byte-identical JSON, safe to
    SHA-pin (``scripts/verify_lane_shas.py``).
    """
    splits: dict[str, dict] = {}
    aggregate = {"n": 0, "correct": 0, "wrong": 0, "declined": 0}
    for name, path in _SPLITS:
        report = build_report(_load(path))
        splits[name] = {
            "n": report["n"],
            "counts": report["counts"],
            "by_gold": report["by_gold"],
            "correct_by_gold": report["correct_by_gold"],
            "all_cases_correct": report["all_cases_correct"],
        }
        aggregate["n"] += report["n"]
        for key in ("correct", "wrong", "declined"):
            aggregate[key] += report["counts"][key]
    return {
        "schema_version": 1,
        "lane": "deduction_serve",
        "arc": "deduction-serve",
        "splits": splits,
        "aggregate": aggregate,
        "wrong_is_zero": aggregate["wrong"] == 0,
        "all_correct": all(s["all_cases_correct"] for s in splits.values()),
    }


def write_combined_report(path: Path) -> dict:
    report = build_combined_report()
    path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--report",
        type=Path,
        default=None,
        help=(
            "write the deterministic combined JSON report to this path "
            "(used by scripts/verify_lane_shas.py); default prints the "
            "human-facing per-split breakdown to stdout"
        ),
    )
    args = parser.parse_args(argv)

    if args.report is not None:
        report = write_combined_report(args.report)
        gate_ok = report["wrong_is_zero"] and report["all_correct"]
        return 0 if gate_ok else 1

    all_ok = True
    for name, path in _SPLITS:
        report = _run(name, path)
        all_ok = all_ok and report["all_cases_correct"]
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
