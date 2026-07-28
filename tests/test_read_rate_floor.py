"""Perception Arc Phase 0 — the read-rate floor ratchet (G-21, G-24, keel baseline).

The reader decides **23 of 1,798** sentences of `holdout_dev/v1` (1.28%). That number
is the capability constraint every substrate experiment independently hit (wedge,
operator ablation, §5 — all starved by the reader), the headline of G-24, and the
baseline the keel's perception layer (K4) is accountable for moving **in chunks**.

This pin makes the number an instrument instead of testimony, with the same
both-directions discipline as every honest baseline in this repo:

  * ``read`` may not FALL below the recorded floor — a silent comprehension
    regression in the serving reader fails the gate;
  * the recorded counts may not silently DRIFT from the measurement — if read-rate
    rises (a reader change, a keel absorption), the constants here move in the same
    reviewed commit, so capability motion is a decision with a diff, never an
    accident with a story.

Corpus and reader are deterministic; the counts are exact, not tolerances.
"""

from __future__ import annotations

from evals.perception.read_rate import CORPUS, measure

#: Measured 2026-07-28 at `64ecad00` — the diagnosis baseline (G-24).
FLOOR_READ = 23
RECORDED_SENTENCES = 1798
RECORDED_PROBLEMS = 500
#: The dominant failure, pinned so the *shape* of the gap cannot drift unnoticed:
#: 93.16% of sentences die before vocabulary — upstream of packs, upstream of flags.
RECORDED_NO_TEMPLATE_MATCH = 1675


def test_corpus_is_the_declared_one() -> None:
    """The floor means nothing if the corpus quietly changes underneath it."""
    assert CORPUS.exists(), "holdout_dev/v1 moved — re-anchor the instrument first"
    report = measure()
    assert report.problems == RECORDED_PROBLEMS, (
        f"corpus changed shape: {report.problems} problems vs {RECORDED_PROBLEMS} recorded — "
        "this pin measures the reader, not the corpus; re-baseline deliberately"
    )
    assert report.sentences == RECORDED_SENTENCES, (
        f"sentence split moved: {report.sentences} vs {RECORDED_SENTENCES} — either the "
        "splitter changed or the corpus did; both are reviewed decisions"
    )


def test_read_rate_holds_the_floor_and_the_record() -> None:
    report = measure()
    assert report.read >= FLOOR_READ, (
        f"READ-RATE REGRESSION: {report.read} sentences read, floor is {FLOOR_READ}. "
        "The serving reader lost comprehension it had."
    )
    assert report.read == FLOOR_READ, (
        f"read-rate MOVED UP: {report.read} vs recorded {FLOOR_READ}. Good news is still "
        "a reviewed decision — update FLOOR_READ in this commit so the record matches "
        "reality (the G-22 lesson: two agreeing stale records are not evidence)."
    )
    refusals = dict(report.refusals)
    assert refusals.get("no_template_match") == RECORDED_NO_TEMPLATE_MATCH, (
        f"the gap's shape moved: no_template_match={refusals.get('no_template_match')} "
        f"vs {RECORDED_NO_TEMPLATE_MATCH} recorded — re-baseline deliberately"
    )


def test_the_instrument_is_not_vacuous() -> None:
    """A measurement that cannot fail is not a measurement (R-11's lesson).

    The matcher must still say *no*: the overwhelming majority of real English must
    be refused by the template reader, or the instrument (or reader) changed class
    entirely and every number above means something different.
    """
    report = measure()
    assert report.sentences > 1000, "corpus too small to mean anything"
    assert report.read < report.sentences * 0.5, (
        "the template reader reads >50% of GSM8K English — that is not this reader; "
        "the instrument is measuring something else"
    )
    assert sum(dict(report.refusals).values()) + report.read == report.sentences, (
        "counts don't conserve — the instrument dropped sentences silently"
    )
