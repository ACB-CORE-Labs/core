"""Deduction-serve lane — wrong=0 gate over the committed v1 corpus.

Scores the PRODUCTION serving decider end-to-end from raw text (the same
pipeline ``chat/deduction_surface.py`` runs), distinct from the bare-engine
``evals/deductive_logic`` lane and the reader-fidelity
``evals/comprehension/propositional_runner.py`` lane. See
``evals/deduction_serve/contract.md`` for the full contract.
"""

from __future__ import annotations

from evals.deduction_serve.runner import _ROOT, _load, build_report

_V1 = _ROOT / "v1" / "cases.jsonl"


def test_v1_lane_wrong_is_zero() -> None:
    report = build_report(_load(_V1))
    assert report["n"] == 27
    assert report["counts"]["wrong"] == 0
    assert report["all_cases_correct"] is True
    # the sizeable, honest signal: non-trivial committed classes covered
    cbg = report["correct_by_gold"]
    assert cbg.get("entailed", 0) >= 5
    assert cbg.get("refuted", 0) >= 5
    assert cbg.get("unknown", 0) >= 5
    assert cbg.get("declined", 0) >= 5


def test_runner_treats_wrong_verdict_as_the_only_real_failure() -> None:
    """A committed disagreement with gold is ``wrong``; a decline never is,
    even when gold expected a definite verdict (that's a miss, tracked via
    ``all_cases_correct``, not conflated with a confabulation)."""
    report = build_report([
        {"id": "bad", "text": "If p then q. p. Therefore q.", "gold": "unknown"}
    ])
    assert report["counts"]["wrong"] == 1
    assert report["all_cases_correct"] is False
