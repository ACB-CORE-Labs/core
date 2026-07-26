"""Grammar round-trip eval lane.

Measures whether CORE can read what it writes, and write what it reads, in
both directions, with a negative corpus that must be rejected.

Why this lane exists
--------------------
``evals/deterministic_fluency`` reports 1.00 on all six of its predicates and
still passes ``"banana does the."``, ``"wet ground rains the is."`` and
``"is is is is."``.  It checks terminal punctuation, the presence of a
verb-shaped token, and two anti-shape regexes; it cannot distinguish English
from word salad.  Heuristic predicates will always have that failure mode,
because **grammaticality cannot be measured without a grammar**.

So this lane measures agreement between the two halves of CORE that already
encode grammar — the reader and the writer — and requires the measurement to
fail on salad.  Round-trip is falsifiable without a judge, an embedding, or a
gold aesthetic.

What round-trip does NOT prove
------------------------------
Round-trip is **necessary, not sufficient** for fluency.  It measures *mutual
intelligibility*: both halves agreeing about a surface.  Two halves can agree
on an impoverished construction — ``english_fluency_ood`` accepts ``"river
flows valley"`` as correct — and round-trip would be perfectly happy.  A high
round-trip rate therefore licenses the claim "CORE means what it says", not
"CORE writes well".  The negative corpus is what stops the lane from drifting
into the first failure mode; nothing here stops the second, and no metric in
this lane should ever be cited as evidence of prose quality.

Framework contract: ``run_lane(cases, config=None) -> LaneReport``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from generate.graph_planner import (
    ArticulationStep,
    ArticulationTarget,
    GraphNode,
    PropositionGraph,
    RhetoricalMove,
)
from generate.intent import IntentTag
from generate.meaning_graph.reader import Refusal, comprehend
from generate.realizer import realize_target

from evals.grammar_roundtrip.corpora import (
    GraphCase,
    SurfaceCase,
    negative_surface_cases,
    positive_graph_cases,
    positive_surface_cases,
)
from evals.grammar_roundtrip.projection import (
    Agreement,
    compare,
    from_meaning_graph,
    from_proposition_graph,
)

#: Reading-side predicate -> categorical form letter, for the S-round-trip
#: re-render.  Only the three quantified forms have a categorical surface;
#: ``member`` / ``less`` and friends have no ``all X are Y`` shape, and cases
#: carrying them are reported as ``no_renderer`` rather than as a match
#: failure — conflating "we cannot write this at all" with "we wrote it wrong"
#: would hide which of the two is actually blocking.
_PREDICATE_TO_FORM: dict[str, str] = {
    "subset": "A",
    "disjoint": "E",
    "intersects": "I",
}


@dataclass(frozen=True, slots=True)
class LaneReport:
    metrics: dict[str, Any] = field(default_factory=dict)
    case_details: list[dict[str, Any]] = field(default_factory=list)


def _normalize_surface(surface: str) -> str:
    """Lowercase and drop terminal punctuation for surface comparison.

    Case and the sentence-final period are the renderer's caller's business,
    not the clause renderer's, so comparing them would report a failure the
    grammar is not responsible for.
    """
    return surface.strip().rstrip(".!?").strip().lower()


def _build(case: GraphCase) -> tuple[ArticulationTarget, PropositionGraph]:
    nodes = tuple(
        GraphNode(
            node_id=str(n["node_id"]),
            subject=str(n["subject"]),
            predicate=str(n["predicate"]),
            obj=str(n["obj"]),
            source_intent=IntentTag.UNKNOWN,
        )
        for n in case.nodes
    )
    steps = tuple(
        ArticulationStep(
            node_id=str(n["node_id"]),
            move=RhetoricalMove.ASSERT,
            predicate=str(n["predicate"]),
            subject=str(n["subject"]),
            negated=bool(n.get("negated", False)),
            quantifier=n.get("quantifier"),  # type: ignore[arg-type]
            tense=n.get("tense"),  # type: ignore[arg-type]
            aspect=n.get("aspect"),  # type: ignore[arg-type]
        )
        for n in case.nodes
    )
    return (
        ArticulationTarget(steps=steps, source_intent=IntentTag.UNKNOWN),
        PropositionGraph(nodes=nodes),
    )


def _render_categorical(predicate: str, subject: str, obj: str) -> str | None:
    """Re-render one canonical proposition through the SERVING renderer.

    Deliberately reaches ``generate.proof_chain.render._categorical_clause``
    even though it is private: that function is what band v1b actually serves,
    and a lane that measured a private copy would measure something users
    never see.
    """
    from generate.proof_chain.render import _categorical_clause

    form = _PREDICATE_TO_FORM.get(predicate)
    if form is None:
        return None
    return _categorical_clause({"form": form, "subject": subject, "predicate": obj})


def _run_graph_case(case: GraphCase) -> dict[str, Any]:
    """G-round-trip: graph -> surface -> graph."""
    target, graph = _build(case)
    expected = from_proposition_graph(graph, target)
    surface = realize_target(target, graph).surface
    row: dict[str, Any] = {
        "case_id": case.case_id,
        "direction": "graph",
        "surface": surface,
        "wrote": bool(surface),
        "read": False,
        "refusal_reason": None,
    }
    if not surface:
        row["agreement"] = Agreement(len(expected), 0, 0, 0, 0).as_dict()
        return row
    result = comprehend(surface, source_id="grammar_roundtrip")
    if isinstance(result, Refusal):
        row["refusal_reason"] = result.reason
        row["agreement"] = Agreement(len(expected), 0, 0, 0, 0).as_dict()
        return row
    row["read"] = True
    row["agreement"] = compare(expected, from_meaning_graph(result.meaning_graph)).as_dict()
    return row


def _run_surface_case(case: SurfaceCase) -> dict[str, Any]:
    """S-round-trip: surface -> graph -> surface."""
    row: dict[str, Any] = {
        "case_id": case.case_id,
        "direction": "surface",
        "surface": case.surface,
        "note": case.note,
        "read": False,
        "rendered": None,
        "renderable": False,
        "surface_match": False,
        "refusal_reason": None,
    }
    result = comprehend(case.surface, source_id="grammar_roundtrip")
    if isinstance(result, Refusal):
        row["refusal_reason"] = result.reason
        return row
    row["read"] = True
    props = sorted(from_meaning_graph(result.meaning_graph))
    if not props:
        row["refusal_reason"] = "empty_projection"
        return row
    rendered = [_render_categorical(p.predicate, p.subject, p.obj) for p in props]
    if any(r is None for r in rendered):
        row["rendered"] = None
        return row
    row["renderable"] = True
    joined = "; ".join(r for r in rendered if r is not None)
    row["rendered"] = joined
    row["surface_match"] = _normalize_surface(joined) == _normalize_surface(case.surface)
    return row


def _run_negative_case(case: SurfaceCase) -> dict[str, Any]:
    """A negative case passes when the reader REFUSES or recovers nothing."""
    result = comprehend(case.surface, source_id="grammar_roundtrip")
    if isinstance(result, Refusal):
        return {
            "case_id": case.case_id,
            "direction": "negative",
            "surface": case.surface,
            "note": case.note,
            "rejected": True,
            "refusal_reason": result.reason,
        }
    props = from_meaning_graph(result.meaning_graph)
    return {
        "case_id": case.case_id,
        "direction": "negative",
        "surface": case.surface,
        "note": case.note,
        # Comprehending salad into ZERO propositions still counts as rejected:
        # the reader committed to no meaning. Comprehending it into one or more
        # propositions is a real failure — the lane must go red for that.
        "rejected": not props,
        "recovered": sorted(f"{p.predicate}({p.subject},{p.obj})" for p in props),
        "refusal_reason": None,
    }


def _rate(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 6) if denominator else 0.0


def run_lane(cases: list[dict[str, Any]] | None = None, config: Any = None) -> LaneReport:  # noqa: ARG001
    """Run the grammar round-trip lane over its own committed corpora.

    ``cases`` is accepted for framework-contract compatibility and ignored:
    the corpora are derived from committed case files and in-module tables so
    the lane's numbers are reproducible without an external split.
    """
    graph_rows = [_run_graph_case(c) for c in positive_graph_cases()]
    surface_rows = [_run_surface_case(c) for c in positive_surface_cases()]
    negative_rows = [_run_negative_case(c) for c in negative_surface_cases()]

    n_graph = len(graph_rows)
    wrote = sum(1 for r in graph_rows if r["wrote"])
    g_read = sum(1 for r in graph_rows if r["read"])
    expected_total = sum(int(r["agreement"]["expected"]) for r in graph_rows)
    args_total = sum(int(r["agreement"]["args_match"]) for r in graph_rows)
    preds_total = sum(int(r["agreement"]["predicates_match"]) for r in graph_rows)
    exact_total = sum(int(r["agreement"]["exact_match"]) for r in graph_rows)

    n_surface = len(surface_rows)
    s_read = sum(1 for r in surface_rows if r["read"])
    s_renderable = sum(1 for r in surface_rows if r["renderable"])
    s_match = sum(1 for r in surface_rows if r["surface_match"])

    n_neg = len(negative_rows)
    rejected = sum(1 for r in negative_rows if r["rejected"])

    metrics: dict[str, Any] = {
        # --- G-round-trip: graph -> surface -> graph ---
        "graph_cases": n_graph,
        "g_write_rate": _rate(wrote, n_graph),
        "g_read_rate": _rate(g_read, n_graph),
        "g_propositions_expected": expected_total,
        "g_args_rate": _rate(args_total, expected_total),
        "g_predicates_rate": _rate(preds_total, expected_total),
        "g_exact_rate": _rate(exact_total, expected_total),
        # --- S-round-trip: surface -> graph -> surface ---
        "surface_cases": n_surface,
        "s_read_rate": _rate(s_read, n_surface),
        "s_renderable_rate": _rate(s_renderable, n_surface),
        "s_surface_match_rate": _rate(s_match, n_surface),
        # --- negative corpus: salad must be rejected ---
        "negative_cases": n_neg,
        "reject_rate": _rate(rejected, n_neg),
    }
    return LaneReport(metrics=metrics, case_details=[*graph_rows, *surface_rows, *negative_rows])


__all__ = ("LaneReport", "run_lane")
