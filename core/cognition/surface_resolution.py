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
    """Resolve the final turn surface under dual-competing Shadow Coherence Gate.

    Dual-competing gate (forward ∧ conjugate) — both must pass to commit
    substrate authority:

    * **Forward** (surface resolution): graph fully grounded; structural
      contract slots closed when assessment present.
    * **Conjugate** (coherence correction check): geometric contract closed
      — versor_condition / GoldTether residual encoded as zero
      ``missing_bindings`` and zero ``unresolved_hazards`` on
      ``contract_assessment``. Assessment is **required** for substrate
      commit; ``None`` refuses geometric authority (fail-closed).

    When either competitor fails, authority stays on the runtime base surface.
    The transitional ``realizer_useful`` shim is admitted only when conjugate
    coherence still passes (never as a substitute for a failed geometric gate).

    Walk/compose folds are *always* suffixes — they never affect the
    authority prefix decision.
    """

    surface, articulation_surface, authority = _base_runtime_surface(
        canonical_surface=canonical_surface or "",
        pre_decoration_surface=pre_decoration_surface or "",
        response_surface=response_surface or "",
        response_articulation_surface=response_articulation_surface or "",
    )

    # === DUAL-COMPETING SHADOW COHERENCE GATE ===
    # Forward and conjugate evaluated as independent competitors; commit
    # substrate only when both pass (and gate_fired is false).
    forward_ok = _forward_surface_ok(proposition_graph, contract_assessment)
    conjugate_ok = _conjugate_coherence_ok(contract_assessment)

    if not gate_fired and realized_surface and forward_ok and conjugate_ok:
        surface = realized_surface
        articulation_surface = realized_surface
        authority = "substrate_realizer"
    elif (
        not gate_fired
        and realized_surface
        and realizer_useful
        and conjugate_ok
        and not forward_ok
    ):
        # Transitional shim: geometric coherence holds, but graph not yet
        # fully grounded. Never used when conjugate residual fails.
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


def _conjugate_coherence_ok(
    contract_assessment: "ContractAssessment | None",
) -> bool:
    """Conjugate competitor: geometric residual contract must be closed.

    Requires an explicit assessment (populated from versor_condition +
    GoldTether residual upstream). ``None`` fails closed — no soft admit.
    """
    if contract_assessment is None:
        return False
    if contract_assessment.missing_bindings or contract_assessment.unresolved_hazards:
        return False
    return True


def _forward_surface_ok(
    proposition_graph: "PropositionGraph | None",
    contract_assessment: "ContractAssessment | None",
) -> bool:
    """Forward competitor: structural graph readiness for substrate surface."""
    if proposition_graph is None:
        return False
    if not proposition_graph.is_fully_grounded():
        return False
    # Structural contract slots (when assessment carries organ bindings).
    if contract_assessment is not None:
        if contract_assessment.missing_bindings or contract_assessment.unresolved_hazards:
            return False
    return True


def _substrate_supreme(
    proposition_graph: "PropositionGraph | None",
    contract_assessment: "ContractAssessment | None",
) -> bool:
    """True iff both dual-competing Shadow Gate competitors pass."""
    return _forward_surface_ok(proposition_graph, contract_assessment) and (
        _conjugate_coherence_ok(contract_assessment)
    )
