"""Deduction-serve lane — wrong=0 gate over the committed v1 corpus.

Scores the PRODUCTION serving decider end-to-end from raw text (the same
pipeline ``chat/deduction_surface.py`` runs), distinct from the bare-engine
``evals/deductive_logic`` lane and the reader-fidelity
``evals/comprehension/propositional_runner.py`` lane. See
``evals/deduction_serve/contract.md`` for the full contract.
"""

from __future__ import annotations

from evals.deduction_serve.runner import (
    _ROOT,
    _load,
    build_combined_report,
    build_report,
)

_V1 = _ROOT / "v1" / "cases.jsonl"
_V2_EN = _ROOT / "v2_en" / "cases.jsonl"
_V2_MEMBER = _ROOT / "v2_member" / "cases.jsonl"
_V2_CONDMEM = _ROOT / "v2_condmem" / "cases.jsonl"
_V2_VERB = _ROOT / "v2_verb" / "cases.jsonl"
_V2_EXIST = _ROOT / "v2_exist" / "cases.jsonl"


def test_v1_lane_wrong_is_zero() -> None:
    report = build_report(_load(_V1))
    assert report["n"] == 28
    assert report["counts"]["wrong"] == 0
    assert report["all_cases_correct"] is True
    # the sizeable, honest signal: non-trivial committed classes covered,
    # including the categorical band (valid + invalid) added in Phase 4.
    # (declined dropped from 6 to 4 when the two documented Band v1 boundary
    # cases — multiword conditional, nested-negation contraposition — became
    # DECIDED by Band v2-EN, ADR-0257; they are now entailed gold.)
    cbg = report["correct_by_gold"]
    assert cbg.get("entailed", 0) >= 7
    assert cbg.get("refuted", 0) >= 5
    assert cbg.get("unknown", 0) >= 5
    assert cbg.get("declined", 0) >= 4
    assert cbg.get("valid", 0) >= 3
    assert cbg.get("invalid", 0) >= 1


def test_v2_en_lane_wrong_is_zero() -> None:
    """Band v2-EN (ADR-0257): hand-authored REAL-English arguments — content
    deliberately disjoint from the synthetic practice lexicon — decided by the
    production pipeline with wrong=0, across all four inference verdicts and
    five distinct honest-decline shapes (ds-en-0022, the membership decline,
    was promoted declined→entailed when the member band landed — ADR-0258)."""
    report = build_report(_load(_V2_EN))
    assert report["n"] == 26
    assert report["counts"]["wrong"] == 0
    assert report["all_cases_correct"] is True
    cbg = report["correct_by_gold"]
    assert cbg.get("entailed", 0) >= 14
    assert cbg.get("refuted", 0) >= 3
    assert cbg.get("unknown", 0) >= 4
    assert cbg.get("declined", 0) >= 5


def test_v2_member_lane_wrong_is_zero() -> None:
    """Band v3-MEM (ADR-0258): hand-authored membership/universal arguments —
    real nouns exercising every number-link row-type (irregular, invariant,
    each regular suffix rule) — decided with wrong=0 across all four verdicts
    and five distinct honest-decline shapes. (``ds-mem-0024``, a bare
    conditional with no anchor, was promoted declined->unknown when Band
    v4-CM landed — ADR-0259; it is genuinely UNKNOWN, not entailed, since the
    antecedent is never asserted. ``ds-mem-0020``, the ADR-0258 existential
    scope-out, was promoted declined->unknown when Band v6-EX landed —
    ADR-0261; genuinely UNKNOWN, since an anonymous witness never transfers to
    a named individual.)"""
    report = build_report(_load(_V2_MEMBER))
    assert report["n"] == 26
    assert report["counts"]["wrong"] == 0
    assert report["all_cases_correct"] is True
    cbg = report["correct_by_gold"]
    assert cbg.get("entailed", 0) >= 12
    assert cbg.get("refuted", 0) >= 3
    assert cbg.get("unknown", 0) >= 6
    assert cbg.get("declined", 0) >= 5


def test_v2_condmem_lane_wrong_is_zero() -> None:
    """Band v4-CM (ADR-0259): hand-authored conditional-membership arguments
    — v2-EN's connective grammar composed over v3-MEM's singular-membership
    sentence reading, including genuine universal+connective fusion cases —
    decided with wrong=0 across all four verdicts and seven distinct honest-
    decline shapes."""
    report = build_report(_load(_V2_CONDMEM))
    assert report["n"] == 26
    assert report["counts"]["wrong"] == 0
    assert report["all_cases_correct"] is True
    cbg = report["correct_by_gold"]
    assert cbg.get("entailed", 0) >= 10
    assert cbg.get("refuted", 0) >= 4
    assert cbg.get("unknown", 0) >= 5
    assert cbg.get("declined", 0) >= 7


def test_v2_verb_lane_wrong_is_zero() -> None:
    """Band v5-VP (ADR-0260): hand-authored verb-predicate arguments —
    universals discharged by membership facts across every closed agreement
    rule (+s, +es, y↔ies, irregular go/goes), transitive objects at face
    value, and eight distinct honest-decline shapes — decided wrong=0."""
    report = build_report(_load(_V2_VERB))
    assert report["n"] == 28
    assert report["counts"]["wrong"] == 0
    assert report["all_cases_correct"] is True
    cbg = report["correct_by_gold"]
    assert cbg.get("entailed", 0) >= 11
    assert cbg.get("refuted", 0) >= 4
    assert cbg.get("unknown", 0) >= 5
    assert cbg.get("declined", 0) >= 8


def test_v2_exist_lane_wrong_is_zero() -> None:
    """Band v6-EX (ADR-0261): hand-authored existential arguments — the full
    square of opposition (Darii, Ferio, both contradictory pairs, the
    no-existential-import subaltern), witnesses that never transfer to a named
    individual, the arbitrary element that keeps the domain open, and eleven
    distinct honest-decline shapes — decided wrong=0."""
    report = build_report(_load(_V2_EXIST))
    assert report["n"] == 32
    assert report["counts"]["wrong"] == 0
    assert report["all_cases_correct"] is True
    cbg = report["correct_by_gold"]
    assert cbg.get("entailed", 0) >= 11
    assert cbg.get("refuted", 0) >= 4
    assert cbg.get("unknown", 0) >= 6
    assert cbg.get("declined", 0) >= 11


def test_runner_treats_wrong_verdict_as_the_only_real_failure() -> None:
    """A committed disagreement with gold is ``wrong``; a decline never is,
    even when gold expected a definite verdict (that's a miss, tracked via
    ``all_cases_correct``, not conflated with a confabulation)."""
    report = build_report([
        {"id": "bad", "text": "If p then q. p. Therefore q.", "gold": "unknown"}
    ])
    assert report["counts"]["wrong"] == 1
    assert report["all_cases_correct"] is False


def test_the_pinned_report_records_what_the_user_actually_reads() -> None:
    """Every committed case contributes its SERVED PROSE to the pinned bytes.

    Before 2026-07-27 the pinned artifact held verdict counts only, on the
    stated rationale that prose is "presentation, not decision" and that
    wording was covered by ``tests/test_deduction_surface.py``. Measured, it
    was not: see the mutation test below.
    """
    report = build_combined_report()
    for name, split in report["splits"].items():
        assert len(split["surfaces"]) == split["n"], name
        assert len(split["surface_sha256"]) == 64, name
        for row in split["surfaces"]:
            assert row["surface"], f"{name}/{row['id']} served empty prose"


def test_surface_hash_moves_when_the_renderer_is_sabotaged(monkeypatch) -> None:
    """THE MUTATION PROOF — without this, the field above is decoration.

    A pin that cannot fail guards nothing. This corrupts the categorical noun
    renderer exactly as the 2026-07-27 investigation did (every clause becomes
    "all SABOTAGE_dogs are SABOTAGE_animals") and requires the pinned digest to
    move.

    Historical note, and the reason this test exists: under that same sabotage
    the 11 lane SHA pins stayed 11/11 byte-identical, this file's other 20
    tests passed, and all 41 tests in ``tests/test_deduction_surface.py``
    passed. Only ``evals/grammar_roundtrip`` caught it. CORE could have served
    word salad indefinitely with every hash gate green.
    """
    from generate.proof_chain import render

    clean = build_combined_report()

    original = render._display_noun
    monkeypatch.setattr(
        render, "_display_noun", lambda term: "SABOTAGE_" + original(term)
    )
    sabotaged = build_combined_report()

    moved = [
        name
        for name in clean["splits"]
        if clean["splits"][name]["surface_sha256"]
        != sabotaged["splits"][name]["surface_sha256"]
    ]
    assert moved, "sabotaging the renderer did not move any surface digest"

    # And the verdicts must be untouched — this proves the digest is tracking
    # PROSE, not smuggling in a decision change.
    assert clean["aggregate"] == sabotaged["aggregate"]
    assert sabotaged["wrong_is_zero"] is True
