"""ADR-0240 — analogical transfer harness (wrong=0 on fixture)."""

from __future__ import annotations

from evals.analogical_transfer.harness import (
    make_fixture_pair,
    run_analogical_transfer,
)


def test_fixture_transfer_wrong_zero():
    case = make_fixture_pair()
    report = run_analogical_transfer([case], residual_threshold=0.35)
    assert report.wrong == 0
    assert report.counts["correct"] >= 1
    assert report.all_correct_or_refused
    assert report.results[0].correct is True
    assert report.results[0].residual <= 0.35


def test_harness_replay_deterministic():
    case = make_fixture_pair()
    r1 = run_analogical_transfer([case])
    r2 = run_analogical_transfer([case])
    assert r1.counts == r2.counts
    assert r1.wrong == r2.wrong
    assert r1.results[0].residual == r2.results[0].residual
