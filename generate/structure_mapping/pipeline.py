"""End-to-end off-serving structure-mapping pipeline.

``text → (serving parse | SM-owned extract) → role graph → selector → solve``

Serving reader is tried first; SM-owned extractors run only on refuse, and
never feed the live organ path. Gold labels never enter.
"""

from __future__ import annotations

from dataclasses import dataclass

from generate.math_candidate_graph import parse_and_solve
from generate.math_problem_graph import MathProblemGraph
from generate.structure_mapping.convert import graph_to_role_graph
from generate.structure_mapping.solve import SolveOutcome, try_structure_map_and_solve
from generate.structure_mapping.text_extract import extract_pure_s1


@dataclass(frozen=True, slots=True)
class PipelineTrace:
    """Diagnostics for measurement scripts (not a gold label)."""

    organ_parsed: bool
    organ_answer: float | None
    organ_refusal: str | None
    extract_used: bool
    extract_pattern: str | None
    graph_source: str  # "organ" | "sm_extract" | "none"


def run_structure_mapping_pipeline(
    problem: str,
    *,
    families: tuple[str, ...] = ("S1", "S2", "S3", "S4"),
    allow_sm_extract: bool = True,
) -> tuple[SolveOutcome, PipelineTrace, MathProblemGraph | None]:
    """Full off-serving path for one problem text.

    Returns ``(outcome, trace, graph_used)``.
    """
    organ = parse_and_solve(problem)
    graph: MathProblemGraph | None = organ.selected_graph
    extract_used = False
    extract_pattern: str | None = None
    graph_source = "organ" if graph is not None else "none"

    if graph is None and allow_sm_extract:
        ext = extract_pure_s1(problem)
        if ext.graph is not None:
            graph = ext.graph
            extract_used = True
            extract_pattern = ext.pattern_id
            graph_source = "sm_extract"

    trace = PipelineTrace(
        organ_parsed=organ.selected_graph is not None,
        organ_answer=organ.answer,
        organ_refusal=organ.refusal_reason,
        extract_used=extract_used,
        extract_pattern=extract_pattern,
        graph_source=graph_source,
    )

    if graph is None:
        return (
            SolveOutcome(
                emitted=False,
                answer=None,
                refusal_reason="parser_frontier:no_graph",
                binding=None,
                derivation=None,
                multi_register_certified=False,
                classical_verified=False,
            ),
            trace,
            None,
        )

    # Optional: convert for hash; solve path re-converts.
    _ = graph_to_role_graph(graph)
    out = try_structure_map_and_solve(graph, families=families)
    return out, trace, graph
