"""ADR-0250 increment 1 — Q3 hazard-close: q:difference is fail-closed.

Josh's Q3 ruling deferred the q:difference *capability* (its cases strand on
multi-compound) but required the hazard be CLOSED now: the partial Pattern-B
"how many more/fewer" path must never emit a guessed-direction answer. The
direction bit ("more…than" → A−B vs "fewer…than" → B−A) is a wrong=0 driver
that must be positively determined; until it is, the question MUST refuse.

`_pattern_b_comparative_candidates` is inert by construction (returns []), so
these questions refuse end-to-end. This suite LOCKS that so a future D.5 wiring
cannot silently reopen the hazard without the direction determination. The
critical cases are the ones where every STATEMENT injects cleanly — a guessed
answer would be most likely there, and matching gold by luck would be a
sealed-test wrong wearing a success costume.
"""
from __future__ import annotations

import pytest

from generate.math_candidate_graph import parse_and_solve

# Each: statements parse cleanly; only the q:difference question is in play.
# Every one MUST refuse (answer is None) — never a signed-difference answer.
_Q_DIFFERENCE_PROBLEMS = [
    "Alice has 10 apples. Bob has 4 apples. How many more apples does Alice have than Bob?",
    "Alice has 10 apples. Bob has 4 apples. How many fewer apples does Bob have than Alice?",
    "Whitney bought 9 books and 7 magazines. How many more books than magazines did Whitney buy?",
    "Tom made 12 cookies. Sam made 5 cookies. How many more cookies did Tom make than Sam?",
    "Mary has a bag holding 20 pounds. She buys 4 pounds of beans. How many more pounds can Mary fit?",
]


@pytest.mark.parametrize("problem", _Q_DIFFERENCE_PROBLEMS)
def test_q_difference_refuses_no_guessed_direction(problem: str) -> None:
    result = parse_and_solve(problem)
    assert result.answer is None, (
        "q:difference must refuse (deferred capability, hazard closed): a "
        f"guessed-direction answer {result.answer!r} is a wrong=0 hole. Problem: {problem!r}"
    )
