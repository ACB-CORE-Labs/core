"""Explicit user-facing surface resolution for cognitive turns.

The pipeline produces several candidate surfaces in one turn:

* runtime/canonical surface from ChatRuntime
* semantic realizer surface from the proposition graph
* deterministic operator folds from walk / compose inference

Historically these mutated one string in evaluation order.  This module
centralizes the policy so fold behavior is declared and unit-testable.
"""

from __future__ import annotations

from dataclasses import dataclass

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from generate.graph_planner import PropositionGraph
    from generate.problem_frame_contracts import ContractAssessment


@dataclass(frozen=True, slots=True)
class SurfaceResolution:
    """Resolved user-facing and articulation surfaces.

    ``authority`` records the prefix authority before deterministic folds
    are appended.  ``fold_sources`` records which inference suffixes were
    appended, in deterministic order.

    When authority == "substrate_realizer", the PropositionGraph +
    realize_semantic path was granted supremacy by the Shadow Coherence
    Gate (strict structural + contract + coherence proof). Legacy runtime
    and walk/compose folds are still applied after, never before.
    """

    surface: str
    articulation_surface: str
    authority: str
    fold_sources: tuple[str, ...] = ()


def _base_runtime_surface(
    *,
    canonical_surface: str,
    pre_decoration_surface: str,
    response_surface: str,
    response_articulation_surface: str,
) -> tuple[str, str, str]:
    """Select the runtime-owned base surface by declared precedence."""

    if canonical_surface:
        return canonical_surface, response_articulation_surface, "runtime_canonical"
    if pre_decoration_surface:
        return pre_decoration_surface, response_articulation_surface, "runtime_pre_decoration"
    return response_surface, response_articulation_surface, "runtime"


def resolve_surface(
    *,
    canonical_surface: str = "",
    pre_decoration_surface: str = "",
    response_surface: str = "",
    response_articulation_surface: str = "",
    realized_surface: str = "",
    realizer_useful: bool = False,
    gate_fired: bool = False,
    walk_surface: str = "",
    compose_surface: str = "",
    proposition_graph: "PropositionGraph | None" = None,
    contract_assessment: "ContractAssessment | None" = None,
) -> SurfaceResolution:
    """Resolve the final turn surface under one explicit policy.

    The Shadow Coherence Gate (Strangler Fig Pattern per the refined plan):

    - The PropositionGraph and realize_semantic are executed *unconditionally*
      on every turn (already true in pipeline before this call).
    - Authority is granted to the substrate realizer **only** when the
      strict geometric guard passes:
        * graph.is_fully_grounded()  (no <pending> slots remain)
        * contract assessment (if present) is closed (no missing_bindings,
          no unresolved_hazards)
        * gate did not fire (unknown domain safety)
      Versor coherence (< 1e-6) is presupposed by construction at the
      boundaries that produced the graph/bindings; it is not re-"repaired"
      here.
    - When the guard refuses, we fall back to the legacy runtime surface
      and the *precise* topological delta is recorded upstream as
      SUBSTRATE_BYPASS_HAZARD telemetry. This makes every test run and
      every production turn a diagnostic that lights exactly which
      ProblemFrame / recall / realizer gaps still block substrate supremacy.
    - Legacy "realizer_useful" path is retained only as a transitional
      compat shim; the supreme check is the load-bearing decision.

    Walk/compose folds are *always* suffixes — they never affect the
    authority prefix decision.

    Three Engineering Pillars are non-negotiable here:
    I. Mechanical Sympathy — the entire decision is a handful of O(N)
       structural inspections on tiny tuples; zero extra alloc, zero
       cross-language roundtrip, zero sensitivity to FMA/assoc drift.
    II. Semantic Rigor — every term ("fully_grounded", "substrate_realizer",
        "bypass_hazard") has one precise meaning. No numeric tolerance,
        no "good enough" surface.
    III. Third Door — we did not pick "keep the regex sidecar" nor
        "rip it out and break the suite". We built the substrate spine
        as the sole authority path and made the old path the observable
        bypass that starves itself to zero.

    See also: engineer's assessment §1 (Authority Flip Cliff), AGENTS.md
    (versor only at owned boundaries, exact recall, kernel substrate rule),
    runtime_contracts.md (surface selection contract).
    """

    surface, articulation_surface, authority = _base_runtime_surface(
        canonical_surface=canonical_surface or "",
        pre_decoration_surface=pre_decoration_surface or "",
        response_surface=response_surface or "",
        response_articulation_surface=response_articulation_surface or "",
    )

    # === SHADOW COHERENCE GATE ===
    # Unconditional substrate execution has already occurred.
    # We now decide authority strictly.
    if not gate_fired and realized_surface:
        if _substrate_supreme(proposition_graph, contract_assessment):
            surface = realized_surface
            articulation_surface = realized_surface
            authority = "substrate_realizer"
        elif realizer_useful:
            # Transitional shim (pre full coverage of grounding + organs).
            # Will be removed when hazard frequency for the legacy path hits zero.
            surface = realized_surface
            articulation_surface = realized_surface
            authority = "realizer"

    fold_sources: list[str] = []
    if walk_surface:
        surface = f"{surface} — {walk_surface}" if surface else walk_surface
        articulation_surface = (
            f"{articulation_surface} — {walk_surface}"
            if articulation_surface
            else walk_surface
        )
        fold_sources.append("walk")

    if compose_surface:
        surface = f"{surface} — {compose_surface}" if surface else compose_surface
        articulation_surface = (
            f"{articulation_surface} — {compose_surface}"
            if articulation_surface
            else compose_surface
        )
        fold_sources.append("compose")

    return SurfaceResolution(
        surface=surface,
        articulation_surface=articulation_surface,
        authority=authority,
        fold_sources=tuple(fold_sources),
    )


def _substrate_supreme(
    proposition_graph: "PropositionGraph | None",
    contract_assessment: "ContractAssessment | None",
) -> bool:
    """Return True only when the geometric substrate has earned authority.

    This is the single source of truth for "use the PropositionGraph path
    as the cognitive spine instead of legacy runtime/pack/walk".

    Conditions (all must hold):
    - A graph was produced.
    - graph.is_fully_grounded() — every slot bound by exact recall or
      direct construction (no <pending>).
    - If a ContractAssessment is supplied, it must be closed
      (zero missing_bindings and zero unresolved_hazards).
      (Assessments are still diagnostic-only in many organs; when the
      main spine wires ProblemFrame + assess_contracts, this becomes
      active backpressure — see Layer 3/Phase D.)

    Versor coherence is *not* re-checked with a repair here. It is
    required by construction at the sites that emit versors (see
    VersorBinding and algebra/versor.py). Passing a non-coherent state
    here is a programmer error, not a runtime tolerance.

    When this returns False the caller (pipeline) must emit the
    SUBSTRATE_BYPASS_HAZARD with graph.get_unresolved_topology() so the
    failure is actionable rather than silent.
    """
    if proposition_graph is None:
        return False
    if not proposition_graph.is_fully_grounded():
        return False
    if contract_assessment is not None:
        if contract_assessment.missing_bindings or contract_assessment.unresolved_hazards:
            return False
    return True
