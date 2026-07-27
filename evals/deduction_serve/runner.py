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
compared to independently-authored gold.

**Surfaces are hashed too (2026-07-27).** This lane previously excluded the
prose-rendering step on the stated grounds that it is "presentation, not
decision", so the pinned bytes would "stay stable against wording-only
changes; wording is covered by ``tests/test_deduction_surface.py``."

That rationale was measured and does not hold. With
``render._display_noun`` sabotaged to prefix every categorical noun — so
CORE served ``all SABOTAGE_dogs are SABOTAGE_animals`` — the following
were all still green:

* the 11 lane SHA pins (11/11 byte-identical),
* ``tests/test_deduction_serve_lane`` + ``_license`` (20 passed),
* ``tests/test_deduction_surface.py`` (41 passed) — the very file named
  above as the wording guard.

Only ``evals/grammar_roundtrip`` caught it. So "wording is covered
elsewhere" was false, and the exclusion left CORE's user-visible output
unguarded by its own hash pins. That is how the ratified v1b band served
``all dog are mammal`` for the whole arc with ``wrong=0`` intact.

``surface_sha256`` now covers every served surface, and ``surfaces``
records them per case so a moved hash can be diffed rather than guessed at.
The accepted cost is exactly what the old rationale wanted to avoid: a
wording-only change moves this pin. That is the point — a wording change IS
a user-visible change and should require a deliberate re-pin.

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
import hashlib
import json
from collections import Counter
from pathlib import Path

from chat.deduction_surface import (
    deduction_grounded_surface,
    looks_like_deductive_argument,
)
from generate.meaning_graph.projectors import to_deductive_logic, to_syllogism
from generate.meaning_graph.reader import Comprehension, comprehend
from generate.proof_chain.categorical import CategoricalError, decide_syllogism
from generate.proof_chain.cond_member import CondMemberArgument, read_cond_member_argument
from generate.proof_chain.english import EnglishArgument, read_english_argument
from generate.proof_chain.entail import Entailment, evaluate_entailment_with_trace
from generate.proof_chain.exist import ExistArgument, read_exist_argument
from generate.proof_chain.member import MemberArgument, read_member_argument
from generate.proof_chain.verb import VerbArgument, read_verb_argument

_ROOT = Path(__file__).resolve().parent

_SPLITS: tuple[tuple[str, Path], ...] = (
    ("v1", _ROOT / "v1" / "cases.jsonl"),
    # Band v2-EN (ADR-0257) — hand-authored REAL-English arguments (content
    # deliberately disjoint from the synthetic practice lexicon, so the earned
    # license's structural-fidelity claim is checked against natural prose).
    ("v2_en", _ROOT / "v2_en" / "cases.jsonl"),
    # Band v3-MEM (ADR-0258) — hand-authored membership/universal arguments,
    # same content-disjoint discipline (incl. the number-link table on real
    # nouns: men, people, children, canaries, sheep).
    ("v2_member", _ROOT / "v2_member" / "cases.jsonl"),
    # Band v4-CM (ADR-0259) — hand-authored conditional-membership arguments,
    # same content-disjoint discipline (connectives composed over singular-
    # membership clauses, incl. universal+connective fusion cases).
    ("v2_condmem", _ROOT / "v2_condmem" / "cases.jsonl"),
    # Band v5-VP (ADR-0260) — hand-authored verb-predicate arguments, same
    # content-disjoint discipline (verb agreement across +s/+es/y↔ies and the
    # irregular table on real verbs: writes, debates, cries, goes).
    ("v2_verb", _ROOT / "v2_verb" / "cases.jsonl"),
    # Band v6-EX (ADR-0261) — hand-authored existential arguments, same
    # content-disjoint discipline (the square of opposition on real nouns,
    # incl. the no-existential-import subalterns and both contradictory pairs).
    ("v2_exist", _ROOT / "v2_exist" / "cases.jsonl"),
)

_OUTCOME_TO_CLASS = {
    Entailment.ENTAILED: "entailed",
    Entailment.REFUTED: "refuted",
    Entailment.UNKNOWN: "unknown",
    Entailment.REFUSED: "declined",
}

#: Categorical outcome → verdict class (matches the composer / arena mapping).
_CATEGORICAL_TO_CLASS = {
    Entailment.ENTAILED: "valid",
    Entailment.REFUTED: "invalid",
    Entailment.UNKNOWN: "invalid",
    Entailment.REFUSED: "declined",
}


def _load(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def decide(text: str) -> str:
    """Run the exact decision pipeline ``chat/deduction_surface.py`` runs in
    serving and return the outcome class: entailed/refuted/unknown (propositional),
    valid/invalid (categorical), or declined.

    Mirrors ``deduction_grounded_surface`` call-for-call up to (but not
    including) the prose render and the license gate — the same production
    decision, typed instead of rendered, so this lane's assertions are robust
    to wording changes.
    """
    if not looks_like_deductive_argument(text):
        return "declined"
    comp = comprehend(text)
    if not isinstance(comp, Comprehension):
        return _decide_english(text)
    projected = to_deductive_logic(comp)
    if projected is not None:
        premises, query = projected
        return _OUTCOME_TO_CLASS[evaluate_entailment_with_trace(premises, query).outcome]
    syllogism = to_syllogism(comp)
    if syllogism is not None:
        structure, s_query = syllogism
        try:
            return _CATEGORICAL_TO_CLASS[decide_syllogism(structure, s_query).outcome]
        except CategoricalError:
            return "declined"
    return _decide_english(text)


def _decide_english(text: str) -> str:
    """Band v2-EN fallback (ADR-0257) — mirrors ``_english_band_surface``;
    chains into the Band v3-MEM fallback exactly as the composer does."""
    arg = read_english_argument(text)
    if not isinstance(arg, EnglishArgument):
        return _decide_member(text)
    outcome = evaluate_entailment_with_trace(arg.premise_formulas, arg.query_formula).outcome
    return _OUTCOME_TO_CLASS[outcome]


def _decide_member(text: str) -> str:
    """Band v3-MEM fallback (ADR-0258) — mirrors ``_member_band_surface``;
    chains into the Band v4-CM fallback exactly as the composer does."""
    arg = read_member_argument(text)
    if not isinstance(arg, MemberArgument):
        return _decide_cond_member(text)
    outcome = evaluate_entailment_with_trace(arg.premise_formulas, arg.query_formula).outcome
    return _OUTCOME_TO_CLASS[outcome]


def _decide_cond_member(text: str) -> str:
    """Band v4-CM fallback (ADR-0259) — mirrors ``_cond_member_band_surface``."""
    arg = read_cond_member_argument(text)
    if not isinstance(arg, CondMemberArgument):
        return _decide_verb(text)
    outcome = evaluate_entailment_with_trace(arg.premise_formulas, arg.query_formula).outcome
    return _OUTCOME_TO_CLASS[outcome]


def _decide_verb(text: str) -> str:
    """Band v5-VP fallback (ADR-0260) — mirrors ``_verb_band_surface``;
    chains into the Band v6-EX fallback exactly as the composer does."""
    arg = read_verb_argument(text)
    if not isinstance(arg, VerbArgument):
        return _decide_exist(text)
    outcome = evaluate_entailment_with_trace(arg.premise_formulas, arg.query_formula).outcome
    return _OUTCOME_TO_CLASS[outcome]


def _decide_exist(text: str) -> str:
    """Band v6-EX fallback (ADR-0261) — mirrors ``_exist_band_surface``, the
    last tier: a refusal here is the pipeline's honest decline."""
    arg = read_exist_argument(text)
    if not isinstance(arg, ExistArgument):
        return "declined"
    outcome = evaluate_entailment_with_trace(arg.premise_formulas, arg.query_formula).outcome
    return _OUTCOME_TO_CLASS[outcome]


def _served_surface(text: str) -> str:
    """The production prose for *text*, or a stable marker when none is served.

    Uses the real ``deduction_grounded_surface`` — the same call chat serving
    makes — so what this lane hashes is what a user would actually read. A
    raised exception is recorded rather than swallowed: a renderer that
    crashes is a surface change too.
    """
    try:
        surface = deduction_grounded_surface(text)
    except Exception as exc:  # noqa: BLE001 - recorded, not handled
        return f"<raised {type(exc).__name__}>"
    return surface if surface is not None else "<not-argument-shaped>"


def build_report(cases: list[dict]) -> dict:
    counts = Counter({"correct": 0, "wrong": 0, "declined": 0})
    by_gold: Counter[str] = Counter()
    correct_by_gold: Counter[str] = Counter()
    wrong_examples: list[dict] = []
    surfaces: list[dict] = []

    for case in cases:
        gold = case["gold"]
        by_gold[gold] += 1
        got = decide(case["text"])
        surfaces.append({"id": case["id"], "surface": _served_surface(case["text"])})
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
    surface_blob = "\n".join(f"{s['id']}\t{s['surface']}" for s in surfaces)
    return {
        "n": len(cases),
        "counts": dict(counts),
        "by_gold": dict(by_gold),
        "correct_by_gold": dict(correct_by_gold),
        "all_cases_correct": all_cases_correct,
        "mismatch_examples": wrong_examples,
        # What the user actually reads. See the module docstring for why this
        # is hashed rather than treated as "presentation, not decision".
        "surface_sha256": hashlib.sha256(surface_blob.encode("utf-8")).hexdigest(),
        "surfaces": surfaces,
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
            # The served prose, hashed AND recorded. Without these the pinned
            # artifact carried verdict counts only, and a renderer that emitted
            # "all SABOTAGE_dogs are SABOTAGE_animals" left every pin
            # byte-identical. Keeping the surfaces (not just the digest) means a
            # moved pin shows the exact sentence that changed in review, instead
            # of an opaque hash someone has to go re-derive.
            "surface_sha256": report["surface_sha256"],
            "surfaces": report["surfaces"],
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
