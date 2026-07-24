"""Curriculum-serve lane — scores curriculum-grounded exam answering.

The Phase-2 lane of the generalization arc. For each committed case, the raw
question text runs through the exact production path
``chat/curriculum_surface.py::decide_curriculum_question`` — question reader →
subject routing → ratified-curriculum premise compilation → the argument bands
→ the ROBDD engine — and the resulting verdict is compared to gold authored
INDEPENDENTLY by ``evals.curriculum_serve.oracle`` (plan §4.4).

Three guards run before any case is scored, and any of them failing is a lane
failure, not a case miss:

1. **Provenance** (§4.3) — every chain id a case pins must resolve in the
   subject's ratified curriculum. A case whose curriculum moved under it
   breaks loudly instead of quietly answering from what is left.
2. **Corpus soundness** (§4.4) — the independent oracle must agree with every
   committed gold. A gold nobody can re-derive from the curriculum is not gold.
3. **Anti-recall coverage** (§4.7) — the split MUST contain cases whose answer
   is true in the world but absent from the curriculum. Without them the lane
   cannot show the system decodes rather than recalls, and it must not ship.

Counts mirror the deduction-serve lane exactly: ``wrong`` (a committed verdict
that disagrees with gold) MUST stay 0; a decline where gold expected a verdict
is a coverage miss, tracked but never conflated with a confabulation.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from chat.curriculum_surface import decide_curriculum_question, read_curriculum_question
from evals.curriculum_serve.oracle import oracle_answer
from teaching.curriculum_premises import load_curriculum, resolve_pinned

_ROOT = Path(__file__).resolve().parent

_SPLITS: tuple[tuple[str, str, Path], ...] = (
    # (split name, subject domain, cases)
    ("physics", "physics", _ROOT / "physics" / "cases.jsonl"),
)

#: A split must carry at least this many anti-recall probes (§4.7). The class
#: prefix is the contract: a probe is a case whose answer is true in the world
#: and absent from the curriculum, so the honest verdict is a non-commitment.
_ANTI_RECALL_PREFIX = "anti_recall"
_MIN_ANTI_RECALL = 3


class LaneContractError(AssertionError):
    """A guard failed — the lane itself is unsound, not merely under-covered."""


def _load(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def assert_provenance(domain: str, cases: list[dict]) -> None:
    """Every pinned chain id must resolve in the ratified curriculum (§4.3)."""
    curriculum = load_curriculum(domain)
    for case in cases:
        pinned = tuple(case.get("chains", ()))
        if not pinned:
            continue
        resolve_pinned(curriculum, pinned)  # raises UnratifiedChain


def assert_corpus_sound(domain: str, cases: list[dict]) -> None:
    """The independent oracle must re-derive every committed gold (§4.4)."""
    for case in cases:
        query = read_curriculum_question(case["text"])
        gold = case["gold"]
        if not hasattr(query, "subject"):
            # Unreadable question shapes are gold-``declined`` by construction;
            # the oracle has no opinion on a text it cannot parse either.
            if gold != "declined":
                raise LaneContractError(
                    f"{case['id']}: unreadable question with gold={gold}"
                )
            continue
        verdict = oracle_answer(domain, query.subject, query.verb, query.obj)
        if verdict.verdict != gold:
            raise LaneContractError(
                f"{case['id']}: oracle={verdict.verdict} gold={gold} "
                f"(family={verdict.family} depth={verdict.depth}) text={case['text']!r}"
            )


def assert_anti_recall_coverage(cases: list[dict]) -> None:
    """The split must probe recall, or it must not ship (§4.7)."""
    probes = [c for c in cases if str(c.get("class", "")).startswith(_ANTI_RECALL_PREFIX)]
    if len(probes) < _MIN_ANTI_RECALL:
        raise LaneContractError(
            f"split has {len(probes)} anti-recall probes, needs >= {_MIN_ANTI_RECALL}"
        )
    for probe in probes:
        if probe["gold"] in ("entailed", "refuted"):
            raise LaneContractError(
                f"{probe['id']}: an anti-recall probe cannot have a committed gold"
            )


def build_report(domain: str, cases: list[dict]) -> dict:
    assert_provenance(domain, cases)
    assert_corpus_sound(domain, cases)
    assert_anti_recall_coverage(cases)

    counts = Counter({"correct": 0, "wrong": 0, "declined": 0})
    by_gold: Counter[str] = Counter()
    correct_by_gold: Counter[str] = Counter()
    by_band: Counter[str] = Counter()
    mismatches: list[dict] = []

    for case in cases:
        gold = case["gold"]
        by_gold[gold] += 1
        decision = decide_curriculum_question(case["text"])
        if decision.band:
            by_band[decision.band] += 1
        if decision.verdict == gold:
            counts["correct"] += 1
            correct_by_gold[gold] += 1
        elif decision.verdict == "declined":
            counts["declined"] += 1
            mismatches.append(
                {"id": case["id"], "gold": gold, "got": decision.verdict,
                 "reason": decision.reason, "text": case["text"]}
            )
        else:
            counts["wrong"] += 1
            mismatches.append(
                {"id": case["id"], "gold": gold, "got": decision.verdict,
                 "reason": decision.reason, "text": case["text"]}
            )

    return {
        "n": len(cases),
        "counts": dict(counts),
        "by_gold": dict(by_gold),
        "correct_by_gold": dict(correct_by_gold),
        "by_band": dict(by_band),
        "anti_recall_probes": sum(
            1 for c in cases if str(c.get("class", "")).startswith(_ANTI_RECALL_PREFIX)
        ),
        "all_cases_correct": counts["correct"] == len(cases),
        "mismatch_examples": mismatches[:10],
    }


def build_combined_report() -> dict:
    """Deterministic per-split + aggregate report — safe to SHA-pin."""
    splits: dict[str, dict] = {}
    aggregate = {"n": 0, "correct": 0, "wrong": 0, "declined": 0}
    for name, domain, path in _SPLITS:
        report = build_report(domain, _load(path))
        splits[name] = {
            "n": report["n"],
            "domain": domain,
            "counts": report["counts"],
            "by_gold": report["by_gold"],
            "correct_by_gold": report["correct_by_gold"],
            "by_band": report["by_band"],
            "anti_recall_probes": report["anti_recall_probes"],
            "all_cases_correct": report["all_cases_correct"],
        }
        aggregate["n"] += report["n"]
        for key in ("correct", "wrong", "declined"):
            aggregate[key] += report["counts"][key]
    return {
        "schema_version": 1,
        "lane": "curriculum_serve",
        "arc": "generalization",
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
    parser.add_argument("--report", type=Path, default=None)
    args = parser.parse_args(argv)

    if args.report is not None:
        report = write_combined_report(args.report)
        return 0 if (report["wrong_is_zero"] and report["all_correct"]) else 1

    all_ok = True
    for name, domain, path in _SPLITS:
        report = build_report(domain, _load(path))
        c = report["counts"]
        print(
            f"[{name}] n={report['n']} correct={c['correct']} wrong={c['wrong']} "
            f"declined_mismatch={c['declined']} anti_recall={report['anti_recall_probes']}"
        )
        for m in report["mismatch_examples"]:
            print(f"    {m['id']}: gold={m['gold']} got={m['got']} "
                  f"reason={m['reason']} text={m['text']!r}")
        all_ok = all_ok and report["all_cases_correct"]
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
