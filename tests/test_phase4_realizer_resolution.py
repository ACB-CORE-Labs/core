"""Phase 4 — which realizer serves, and what the other one's score means.

The arc opened with a fact that had gone unremarked for its whole life:
``english_fluency_ood`` reported 117/117 + 39/39 for ``realize_target``, and
``core/cognition/pipeline.py`` **never calls** ``realize_target``.  It calls
``realize_semantic``.  149 green cases were scoring a function that does not
speak, and the lane said nothing about the one that does.

Phase 4 resolves that by option (b) of the plan: the lanes now report the
serving writer's score alongside, and the claim "realizer fluency is
mechanistic" is restated as a claim about **eval-only code**.  Nothing here
changes a served byte — promoting ``realize_target`` to the serving path is
option (a), it moves surface hashes, and it is Shay's call, not this file's.

What these tests are for
------------------------
Every number below was measured, and each one is pinned so that it cannot
quietly stop being true.  The load-bearing ones are the *controls*: without
them the headline gap could be dismissed as an artifact of the corpora, and
without the negation pin the most serious finding here would live only in a
commit message.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from evals.grammatical_coverage.runner import run_lane
from generate.graph_planner import (
    ArticulationStep,
    ArticulationTarget,
    GraphNode,
    PropositionGraph,
    RhetoricalMove,
)
from generate.intent import IntentTag
from generate.realizer import realize_semantic, realize_target


_EVALS = Path(__file__).resolve().parents[1] / "evals"

#: Every corpus scored through ``realize_target`` by a lane.
_CORPORA = (
    "grammatical_coverage/public/v1",
    "grammatical_coverage/public/v2",
    "grammatical_coverage/dev",
    "grammatical_coverage/holdouts/v1",
    "english_fluency_ood/public/v1",
    "english_fluency_ood/holdouts/v1",
    "english_fluency_ood/dev",
)

#: Content an ``ArticulationStep`` carries and ``render_semantic`` has no
#: parameter for.
_UNEXPRESSIBLE = ("quantifier", "negated", "tense", "aspect")


def _load(name: str) -> list[dict]:
    path = _EVALS / name / "cases.jsonl"
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def _all_cases() -> list[dict]:
    return [case for name in _CORPORA for case in _load(name)]


def _carries_unexpressible(case: dict) -> bool:
    return any(
        node.get(feature) not in (None, False, "")
        for node in case.get("proposition_graph", {}).get("nodes", [])
        for feature in _UNEXPRESSIBLE
    )


def _is_multi_node(case: dict) -> bool:
    return len(case.get("proposition_graph", {}).get("nodes", [])) > 1


def _one_step(**step_kwargs) -> tuple[ArticulationTarget, PropositionGraph]:
    node = GraphNode(
        node_id="n1", subject="knowledge", predicate="is_grounded_in",
        obj="opinion", source_intent=IntentTag.DEFINITION,
    )
    step = ArticulationStep(
        node_id="n1", subject="knowledge", predicate="is_grounded_in",
        move=RhetoricalMove.ASSERT, **step_kwargs,
    )
    return (
        ArticulationTarget(steps=(step,), source_intent=IntentTag.DEFINITION),
        PropositionGraph(nodes=(node,), edges=()),
    )


# --------------------------------------------------------------------------- #
# The headline: the lane now reports what ships
# --------------------------------------------------------------------------- #


def test_the_lane_reports_the_serving_writer_too() -> None:
    """Before Phase 4 a lane could report 1.00 while the writer that actually
    speaks scored 0.23 on the identical cases, and nothing surfaced it."""
    metrics = run_lane(_load("english_fluency_ood/public/v1")).metrics
    assert metrics["passed"] == 117
    assert metrics["serving_passed"] == 36  # was 27 before ADR-0265
    assert "serving_accuracy" in metrics


def test_the_measured_gap_across_every_scored_corpus() -> None:
    """340/347 for the realizer the lanes score; 109/347 for the one that ships.

    Was 85 before ADR-0265. The +24 is precisely the negation-bearing cases:
    the serving writer can now say "not". The remaining gap is quantifier,
    tense, aspect and clause joining — none of which has a producer on the
    serving path (ADR-0265 §3), so it is a capability gap and not a live
    defect.
    """
    cases = _all_cases()
    assert len(cases) == 347
    metrics = run_lane(cases).metrics
    assert metrics["passed"] == 340
    assert metrics["serving_passed"] == 109


# --------------------------------------------------------------------------- #
# CONTROL — the gap is the missing features, not the corpora's IntentTag
# --------------------------------------------------------------------------- #


def test_the_two_realizers_agree_exactly_where_nothing_is_dropped() -> None:
    """THE CONTROL, and the most important test in this file.

    Every corpus here hardcodes ``IntentTag.UNKNOWN``, so "the serving realizer
    scores badly" could be an artifact of never giving it a real intent.  It is
    not.  On the 33 cases that carry no unexpressible feature and have a single
    node, the two realizers score **identically** — which is only possible if
    the gap on the other 314 is the dropped content and the clause joining.

    If this ever goes red, the gap measured above has stopped meaning what the
    Phase 4 ruling says it means, and the ruling needs revisiting.
    """
    control = [c for c in _all_cases()
               if not _carries_unexpressible(c) and not _is_multi_node(c)]
    assert len(control) == 33, "the control bucket changed size"
    metrics = run_lane(control).metrics
    assert metrics["passed"] == 33
    assert metrics["serving_passed"] == 33


@pytest.mark.parametrize(
    ("bucket", "expected_n", "expected_eval", "expected_serving"),
    [
        ("features", 214, 207, 73),   # 49 before ADR-0265
        ("multi_node", 100, 100, 3),
    ],
)
def test_the_gap_decomposes_into_dropped_features_and_clause_joining(
    bucket: str, expected_n: int, expected_eval: int, expected_serving: int
) -> None:
    """Two separate causes, measured separately: content the serving writer has
    no parameter for, and clauses it can only join with a full stop."""
    if bucket == "features":
        cases = [c for c in _all_cases()
                 if _carries_unexpressible(c) and not _is_multi_node(c)]
    else:
        cases = [c for c in _all_cases()
                 if not _carries_unexpressible(c) and _is_multi_node(c)]
    assert len(cases) == expected_n
    metrics = run_lane(cases).metrics
    assert metrics["passed"] == expected_eval
    assert metrics["serving_passed"] == expected_serving


# --------------------------------------------------------------------------- #
# DEFECT PIN — the serving writer cannot express negation
# --------------------------------------------------------------------------- #


def test_the_serving_realizer_now_distinguishes_a_denial_from_its_assertion() -> None:
    """WAS A DEFECT PIN. **Fixed by ADR-0265** — revised deliberately, as the
    pin required, rather than relaxed.

    The recorded defect was::

        negated=False -> 'Knowledge is defined as opinion.'
        negated=True  -> 'Knowledge is defined as opinion.'

    Byte-identical: the serving writer had no ``negated`` parameter and
    ``realize_semantic`` never read ``step.negated``.  Sizing the exposure
    showed it was **live**, not latent — under ``realizer_grounded_authority``
    a real user turn served the affirmative of its own denial — and that it was
    two drops in series, the first being a ``GraphNode`` with no field for a
    denial at all.

    ADR-0265 threads the flag end to end and delegates the clause to
    ``render_step``.  The end-to-end regression lives in
    ``tests/test_negation_survives_articulation.py``; this pin keeps the
    unit-level guarantee that the two surfaces may never collapse again.
    """
    affirmative = realize_semantic(*_one_step(negated=False)).surface
    negated = realize_semantic(*_one_step(negated=True)).surface
    assert affirmative != negated, "the serving realizer collapsed a denial again"
    assert "not" in negated

    # The eval-only realizer distinguishes them too.
    assert realize_target(*_one_step(negated=True)).surface != (
        realize_target(*_one_step(negated=False)).surface
    )
    assert "not" in realize_target(*_one_step(negated=True)).surface


@pytest.mark.parametrize("feature", sorted(set(_UNEXPRESSIBLE) - {"negated"}))
def test_render_semantic_still_has_no_parameter_for_these(feature: str) -> None:
    """Derived from the signature, so it cannot rot into a stale comment.

    ``negated`` left this list in ADR-0265. The other three stay, and stay
    deliberately: **no producer sets them** anywhere on the serving path, so
    threading them would be machinery with no caller. They become expressible
    the moment a producer exists, because ``render_step`` already handles all
    three.
    """
    import inspect

    from generate.semantic_templates import render_semantic

    assert feature not in inspect.signature(render_semantic).parameters


def test_how_much_of_the_corpus_carries_feature_bearing_content() -> None:
    """214 of 347. The scale of the gap, independent of any rubric.

    Post-ADR-0265 the serving writer expresses the *negation* subset of these;
    quantifier, tense and aspect remain unexpressed (and unproduced).
    """
    cases = _all_cases()
    carrying = [c for c in cases if _carries_unexpressible(c)]
    assert len(carrying) == 214
    assert len(cases) == 347


# --------------------------------------------------------------------------- #
# §6 evidence — the writer is not what round-trip is blocked on
# --------------------------------------------------------------------------- #


def test_the_serving_writer_round_trips_nothing_at_all() -> None:
    """§6 of the plan forks on ``read_rate`` after unification, and this is the
    measurement that says which fork.

    Two numbers, and they say different things:

    * **292 of 293** cases refuse with ``no_template_match`` under *either*
      writer.  For those the writer is irrelevant — the reader has no
      SUBJ-VERB-OBJ template at all, so nothing the writer does can help.
    * The **one** case that reads is writer-sensitive: it reads through
      ``realize_target`` (0.003413) and refuses through ``realize_semantic``
      (0.0), because predicate-nominal object agreement lives in
      ``render_step`` and the serving writer has no equivalent.

    So the serving writer round-trips **nothing**, and the eval writer
    round-trips one case — and the gap between 1 and 293 is reader construction
    coverage, not a graph-model mismatch.  That is why §6's pre-committed
    reading (§1.8 ⇒ next step is an ADR) is not what the evidence supports; see
    ``test_grammar_roundtrip.py::test_the_remaining_blockers_are_reader_construction_coverage``
    for the full refusal census.
    """
    import evals.grammar_roundtrip.runner as rt

    baseline = rt.run_lane().metrics["g_read_rate"]
    original = rt.realize_target
    rt.realize_target = realize_semantic
    try:
        swapped = rt.run_lane().metrics["g_read_rate"]
    finally:
        rt.realize_target = original

    assert baseline == 0.003413, "the eval writer reads back exactly one case"
    assert swapped == 0.0, "the serving writer reads back none"
    # Sentinel: prove the swap is actually reaching the lane, so that an
    # equality between two identical runs can never be mistaken for a result.
    def _boom(*_args, **_kwargs):  # pragma: no cover - must raise
        raise RuntimeError("sentinel")

    rt.realize_target = _boom
    try:
        with pytest.raises(RuntimeError, match="sentinel"):
            rt.run_lane()
    finally:
        rt.realize_target = original
