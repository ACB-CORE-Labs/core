"""Explicit user-facing surface resolution for cognitive turns.

The pipeline produces several candidate surfaces in one turn:

* runtime/canonical surface from ChatRuntime
* semantic realizer surface from the proposition graph
* deterministic operator folds from walk / compose inference

Historically these mutated one string in evaluation order.  This module
centralizes the policy so fold behavior is declared and unit-testable.

Phase 1 linguistic governance:
  * ``contract_assessment is None`` → typed ContractViolation; no certified answer
  * open geometric contract → typed CoherenceRefusal; no certified answer
  * walk/compose folds never upgrade an uncertified base into authority
"""

from __future__ import annotations

from dataclasses import dataclass

from typing import TYPE_CHECKING

from core.cognition.fail_closed import (
    CoherenceRefusal,
    ContractViolation,
    FailureClass,
    ResidualState,
    contract_assessment_none_violation,
    open_geometry_refusal,
)
from core.cognition.proof_trace import ProofTrace, build_refusal_trace, geometry_contract_trace

if TYPE_CHECKING:
    from generate.graph_planner import PropositionGraph
    from generate.problem_frame_contracts import ContractAssessment


_ABSTENTION_AUTHORITY = "coherence_abstention"


@dataclass(frozen=True, slots=True)
class SurfaceResolution:
    """Resolved user-facing and articulation surfaces.

    ``authority`` records the prefix authority before deterministic folds
    are appended.  ``fold_sources`` records which inference suffixes were
    appended, in deterministic order.

    When authority == "substrate_realizer", the PropositionGraph +
    realize_semantic path was granted supremacy by the Shadow Coherence
    Gate (strict structural + contract + coherence proof).

    ``authoritative`` is True only when a certified answer may leave the
    system. Geometry-open and assessment-missing paths set this False and
    attach a typed refusal/violation.
    """

    surface: str
    articulation_surface: str
    authority: str
    fold_sources: tuple[str, ...] = ()
    authoritative: bool = True
    refusal: CoherenceRefusal | None = None
    contract_violation: ContractViolation | None = None
    proof_trace: ProofTrace | None = None


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


def _assessment_residual(
    contract_assessment: "ContractAssessment | None",
) -> ResidualState | None:
    if contract_assessment is None:
        return ResidualState(detail="contract_assessment is None")
    return ResidualState(
        missing_bindings=tuple(contract_assessment.missing_bindings),
        unresolved_hazards=tuple(contract_assessment.unresolved_hazards),
        detail=str(contract_assessment.explanation or ""),
    )


def _abstention_resolution(
    *,
    refusal: CoherenceRefusal | None,
    violation: ContractViolation | None,
) -> SurfaceResolution:
    if violation is not None:
        msg = (
            f"I cannot certify an answer: {violation.refusal_reason} "
            f"(condition={violation.violated_condition})."
        )
        trace = build_refusal_trace(
            reason=violation.refusal_reason,
            violated_condition=violation.violated_condition,
        )
        return SurfaceResolution(
            surface=msg,
            articulation_surface=msg,
            authority=_ABSTENTION_AUTHORITY,
            fold_sources=(),
            authoritative=False,
            refusal=None,
            contract_violation=violation,
            proof_trace=trace,
        )
    assert refusal is not None
    msg = refusal.message
    trace = build_refusal_trace(
        reason=refusal.refusal_reason,
        violated_condition=refusal.violated_condition,
    )
    return SurfaceResolution(
        surface=msg,
        articulation_surface=msg,
        authority=_ABSTENTION_AUTHORITY,
        fold_sources=(),
        authoritative=False,
        refusal=refusal,
        contract_violation=None,
        proof_trace=trace,
    )


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
    require_closed_geometry: bool = True,
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

    When ``require_closed_geometry`` is True (default), a missing or open
    geometric contract yields a typed abstention — no runtime fluent answer
    is emitted as certified content. Walk/compose folds are suppressed on
    abstention paths.
    """

    # --- Fail-closed: missing assessment never silently passes ---
    if require_closed_geometry and contract_assessment is None:
        return _abstention_resolution(
            refusal=None,
            violation=contract_assessment_none_violation(),
        )

    conjugate_ok = _conjugate_coherence_ok(contract_assessment)
    if require_closed_geometry and not conjugate_ok:
        if contract_assessment is None:
            # Unreachable when require_closed_geometry handled None above,
            # but keep branch explicit for non-require callers.
            return _abstention_resolution(
                refusal=None,
                violation=contract_assessment_none_violation(),
            )
        refusal = open_geometry_refusal(
            missing_bindings=tuple(contract_assessment.missing_bindings),
            unresolved_hazards=tuple(contract_assessment.unresolved_hazards),
            explanation=str(contract_assessment.explanation or ""),
        )
        # gate_fired is the pipeline's residual-failure flag; either way the
        # contract is not closed for certified answers.
        del gate_fired  # used as documentation of pipeline dual; gate is conjugate
        return _abstention_resolution(refusal=refusal, violation=None)

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

    # When require_closed_geometry is False, preserve historical gate_fired
    # blocking of substrate even if assessment looks closed.
    if not require_closed_geometry:
        gate_blocks = gate_fired
    else:
        # Under fail-closed geometry, open conjugate already returned.
        # gate_fired with a closed assessment is treated as residual conflict
        # → still refuse substrate, keep runtime only if conjugate ok.
        gate_blocks = gate_fired

    if not gate_blocks and realized_surface and forward_ok and conjugate_ok:
        surface = realized_surface
        articulation_surface = realized_surface
        authority = "substrate_realizer"
    elif (
        not gate_blocks
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

    proof: ProofTrace | None = None
    if conjugate_ok and contract_assessment is not None:
        # Closed geometry path: embed gate scalars when explanation carries them.
        proof = geometry_contract_trace(
            versor_condition=0.0,
            goldtether_residual=0.0,
            closed=True,
        )

    return SurfaceResolution(
        surface=surface,
        articulation_surface=articulation_surface,
        authority=authority,
        fold_sources=tuple(fold_sources),
        authoritative=True,
        refusal=None,
        contract_violation=None,
        proof_trace=proof,
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


__all__ = [
    "SurfaceResolution",
    "resolve_surface",
    "_conjugate_coherence_ok",
    "_forward_surface_ok",
    "_substrate_supreme",
]
