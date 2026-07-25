"""tests/test_vocab_trigger_instrument.py — mechanism-vs-coverage refusal instrument (Tier S3).

Pins the classifier's closed rule and the instrument's arithmetic against the
CURRENT committed lane corpora, so a future band/curriculum change that shifts
the split is a visible diff here rather than a silent behavior change.
"""

from __future__ import annotations

from evals.vocab_trigger_instrument import (
    _all_curriculum_texts,
    _all_deduction_texts,
    admissions_delta,
    build_curriculum_histogram,
    build_deduction_histogram,
    build_report,
    curriculum_refusal_reason,
    deduction_refusal_reason,
    refusal_class_curriculum,
    refusal_class_deduction,
)


def test_deduction_refusals_are_never_coverage_class() -> None:
    """The deduction bands read a closed connective/quantifier grammar, not
    open vocabulary — every declined deduction case classifies as mechanism
    or engine_refused, never coverage (module docstring's central claim)."""
    hist = build_deduction_histogram(_all_deduction_texts())
    assert hist.declined > 0
    assert "coverage" not in hist.by_class


def test_curriculum_has_real_coverage_refusals() -> None:
    """The curriculum composer's untaught_vocabulary/out_of_curriculum gate
    is a genuine coverage axis — the committed physics split exercises it."""
    hist = build_curriculum_histogram(_all_curriculum_texts())
    assert hist.by_class.get("coverage", 0) > 0


def test_refusal_class_curriculum_closed_set() -> None:
    assert refusal_class_curriculum("untaught_vocabulary") == "coverage"
    assert refusal_class_curriculum("out_of_curriculum") == "coverage"
    assert refusal_class_curriculum("question_shape_out_of_band") == "mechanism"
    assert refusal_class_curriculum("ambiguous_reading") == "mechanism"
    assert refusal_class_curriculum("empty_curriculum") == "mechanism"
    assert refusal_class_curriculum("inconsistent_premises") == "engine_refused"
    assert refusal_class_curriculum("out_of_regime_or_malformed") == "engine_refused"


def test_refusal_class_deduction_only_engine_reasons_are_engine_refused() -> None:
    assert refusal_class_deduction("inconsistent_premises") == "engine_refused"
    assert refusal_class_deduction("out_of_regime_or_malformed") == "engine_refused"
    assert refusal_class_deduction("sentence_shape_out_of_band") == "mechanism"
    assert refusal_class_deduction("quantifier_out_of_band") == "mechanism"
    assert refusal_class_deduction("not_argument_shaped") == "mechanism"


def test_deduction_refusal_reason_recovers_engine_level_decline() -> None:
    """A well-formed but self-contradictory Band-v1 argument declines at the
    ENGINE, not at any reader — a real bug this test pins (an earlier version
    of this instrument misattributed it to whichever fallback band happened
    to run last)."""
    band, reason = deduction_refusal_reason("p. Not p. Therefore q.")
    assert band == "v1"
    assert reason == "inconsistent_premises"


def test_deduction_refusal_reason_recovers_reader_level_decline() -> None:
    band, reason = deduction_refusal_reason("colorless green ideas therefore sleep furiously")
    assert band in {"gate", "reader", "v2_en", "v3_mem", "v4_condmem", "v5_verb", "v6_exist"}
    assert reason != ""
    assert refusal_class_deduction(reason) == "mechanism"


def test_curriculum_refusal_reason_matches_decide() -> None:
    from chat.curriculum_surface import decide_curriculum_question

    text = "Does the build pass?"
    assert curriculum_refusal_reason(text) == decide_curriculum_question(text).reason


def test_histogram_totals_partition_the_corpus() -> None:
    hist = build_deduction_histogram(_all_deduction_texts())
    assert hist.admitted + hist.declined == hist.n
    assert sum(hist.by_reason.values()) == hist.declined
    assert sum(hist.by_class.values()) == hist.declined


def test_build_report_is_deterministic() -> None:
    a = build_report()
    b = build_report()
    assert a == b


def test_admissions_delta_is_zero_against_self() -> None:
    report = build_report()
    delta = admissions_delta(report, report)
    assert delta == {
        "deduction_admitted_delta": 0,
        "curriculum_admitted_delta": 0,
        "combined_admitted_delta": 0,
    }


def test_admissions_delta_reflects_a_new_admission() -> None:
    before = build_report()
    after = {
        "deduction": {**before["deduction"], "admitted": before["deduction"]["admitted"] + 3},
        "curriculum": before["curriculum"],
        "combined": {
            **before["combined"],
            "admitted": before["combined"]["admitted"] + 3,
        },
    }
    delta = admissions_delta(before, after)
    assert delta["deduction_admitted_delta"] == 3
    assert delta["combined_admitted_delta"] == 3
    assert delta["curriculum_admitted_delta"] == 0
