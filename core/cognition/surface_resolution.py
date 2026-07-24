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
    contract_assessment_none_violation,
    open_geometry_refusal,
)
from core.cognition.proof_trace import ProofTrace, build_refusal_trace, geometry_contract_trace

if TYPE_CHECKING:
    from generate.graph_planner import PropositionGraph
    from generate.problem_frame_contracts import ContractAssessment


_ABSTENTION_AUTHORITY = "coherence_abstention"

# --- T13 decision (2): grounded-open hedge arm --------------------------------
# Grounding provenances whose surfaces are curated enough to hedge (serve
# non-authoritatively) rather than hard-refuse when the geometric contract is
# open. Mirrors the "grounded" test in chat.runtime (pack / teaching).
_GROUNDED_PROVENANCES = frozenset({"pack", "teaching"})

# The ONLY open tokens that are hedgeable: geometric-coherence residuals that a
# pack surface never claimed to certify. Any token outside this set — where a
# genuine safety/harm/imperative hazard would land — fails closed to a hard
# refusal (INV-34). Deliberately excludes "missing_wave_field": the absence of
# any field is a harder failure than an open-but-computed residual.
_HEDGEABLE_GEOMETRIC_RESIDUALS = frozenset({"versor_condition", "goldtether_residual"})

_GROUNDED_OPEN_HEDGE_AUTHORITY = "grounded_open_hedge"
_GROUNDED_OPEN_HEDGE_PREFIX = "Grounded but not geometrically certified —"


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

    ``hedged`` is True only on the grounded-open hedge arm (T13 decision 2):
    a curated pack/teaching surface served non-authoritatively because the
    geometric contract is open on a known coherence residual. It is mutually
    exclusive with ``refusal``/``contract_violation`` and never authoritative.
    """

    surface: str
    articulation_surface: str
    authority: str
    fold_sources: tuple[str, ...] = ()
    authoritative: bool = True
    hedged: bool = False
    refusal: CoherenceRefusal | None = None
    contract_violation: ContractViolation | None = None
    proof_trace: ProofTrace | None = None
    hash_surface: str = ""
    """Truth-path surface for ``trace_hash`` folding (ADR-0069 inv C).

    ``surface`` carries the *served* bytes (post register R6/R4);
    ``hash_surface`` carries the register-invariant truth-path bytes
    (canonical-precedence base plus the same substrate/fold suffixes).
    Empty means the served surface IS the truth-path surface (refusal,
    abstention, and legacy callers) — the pipeline falls back to
    ``surface`` when folding the trace."""


def _base_runtime_surface(
    *,
    canonical_surface: str,
    pre_decoration_surface: str,
    response_surface: str,
    response_articulation_surface: str,
) -> tuple[str, str, str]:
    """Select the runtime-owned base surface by declared precedence.

    ``response_surface`` is the runtime's final *served* bytes — post
    realizer-guard, post substantive register (ADR-0077 R6), post seeded
    decoration (ADR-0071 R4) — and always wins when present.
    ``canonical_surface`` / ``pre_decoration_surface`` are truth-path
    identity captures the pipeline folds into ``trace_hash``; they are
    fallbacks for callers that never sealed a response surface, never a
    substitute for served bytes.  Preferring canonical here strips the
    entire register axis from pipeline-served turns (terse/convivial
    stop differing from neutral) while trace_hash stays green — the
    register-tour claims are the falsifiable contract that catches it.
    """

    if response_surface:
        return response_surface, response_articulation_surface, "runtime"
    if pre_decoration_surface:
        return pre_decoration_surface, response_articulation_surface, "runtime_pre_decoration"
    if canonical_surface:
        return canonical_surface, response_articulation_surface, "runtime_canonical"
    return "", response_articulation_surface, "runtime"


def _truth_path_base(
    *,
    canonical_surface: str,
    pre_decoration_surface: str,
    response_surface: str,
) -> str:
    """Register-invariant base folded into ``trace_hash``.

    Canonical-first: the composer's pre-R6 capture is the truth-path
    identity field, byte-identical across register packs (ADR-0069
    inv C / ADR-0077).  Falls through to pre-decoration, then the
    response itself for turns that never captured a canonical surface.
    """

    return canonical_surface or pre_decoration_surface or response_surface


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


def _is_pack_grounded(grounding_provenance: str) -> bool:
    """Structural discriminator: is the surface curated pack/teaching grounded?

    Purely provenance-based — it never inspects the question text. A lexical
    "definitional/epistemic" cue-table would fail a geometric gate open on a
    surface cue (fail-open; ADR-0252 / INV-34), which the ruling rejected.
    """
    return (grounding_provenance or "").strip().lower() in _GROUNDED_PROVENANCES


def _grounded_open_hedge_admissible(
    contract_assessment: "ContractAssessment",
    grounding_provenance: str,
) -> bool:
    """True iff an open-geometry surface may hedge instead of hard-refuse.

    Predicate (authorized): ``pack_grounded ∧ every open token is a known
    geometric-coherence residual``. Fail-closed: an unrecognized open token —
    where a genuine safety/harm/imperative hazard would appear — makes this
    False, so the caller hard-refuses. ``¬hazard`` is thus enforced
    *structurally* by the residual allowlist, not by question typing.
    """
    if not _is_pack_grounded(grounding_provenance):
        return False
    open_tokens = set(contract_assessment.missing_bindings) | set(
        contract_assessment.unresolved_hazards
    )
    if not open_tokens:
        # Defensive: the caller only reaches here when the conjugate is open.
        return False
    return open_tokens <= _HEDGEABLE_GEOMETRIC_RESIDUALS


def _grounded_open_hedge_resolution(
    *,
    canonical_surface: str,
    pre_decoration_surface: str,
    response_surface: str,
    response_articulation_surface: str,
) -> SurfaceResolution:
    """Serve the pack surface, honestly hedged and non-authoritative.

    The surface is emitted (not refused) but ``authoritative=False`` and
    ``hedged=True``: the pack grounding stands on its textual provenance while
    explicitly disclaiming the open geometric certification. Walk/compose folds
    are suppressed — a hedge never accretes deterministic inference authority.
    """
    base_surface, base_articulation, _authority = _base_runtime_surface(
        canonical_surface=canonical_surface,
        pre_decoration_surface=pre_decoration_surface,
        response_surface=response_surface,
        response_articulation_surface=response_articulation_surface,
    )
    truth_base = _truth_path_base(
        canonical_surface=canonical_surface,
        pre_decoration_surface=pre_decoration_surface,
        response_surface=response_surface,
    )
    surface = (
        f"{_GROUNDED_OPEN_HEDGE_PREFIX} {base_surface}" if base_surface else base_surface
    )
    hash_surface = (
        f"{_GROUNDED_OPEN_HEDGE_PREFIX} {truth_base}" if truth_base else truth_base
    )
    articulation = (
        f"{_GROUNDED_OPEN_HEDGE_PREFIX} {base_articulation}"
        if base_articulation
        else base_articulation
    )
    return SurfaceResolution(
        surface=surface,
        articulation_surface=articulation,
        authority=_GROUNDED_OPEN_HEDGE_AUTHORITY,
        fold_sources=(),
        authoritative=False,
        hedged=True,
        refusal=None,
        contract_violation=None,
        proof_trace=None,
        hash_surface=hash_surface,
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
    grounding_provenance: str = "",
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

    **Grounded-open hedge arm (T13 decision 2).** When the conjugate is open
    but the surface is ``pack``/``teaching`` grounded (``grounding_provenance``)
    and every open token is a known geometric-coherence residual, the pack
    surface is served *honestly hedged* (``authoritative=False``, ``hedged=True``)
    instead of hard-refused. The discriminator is purely structural (provenance
    + residual allowlist) — never question typing — and fails closed: an
    unrecognized open token or non-pack grounding takes the unchanged refusal.
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
        # --- T13 decision (2): grounded-open hedge arm ---
        # A curated pack/teaching surface whose ONLY open tokens are known
        # geometric-coherence residuals is served honestly hedged
        # (authoritative=False) rather than hard-refused: the pack surface never
        # claimed geometric certification. Structural predicate only (grounding
        # provenance + residual allowlist); any unrecognized token or non-pack
        # grounding falls through to the unchanged fail-closed refusal below.
        if _grounded_open_hedge_admissible(contract_assessment, grounding_provenance):
            del gate_fired  # hedge does not depend on the residual-failure flag
            return _grounded_open_hedge_resolution(
                canonical_surface=canonical_surface or "",
                pre_decoration_surface=pre_decoration_surface or "",
                response_surface=response_surface or "",
                response_articulation_surface=response_articulation_surface or "",
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
    hash_surface = _truth_path_base(
        canonical_surface=canonical_surface or "",
        pre_decoration_surface=pre_decoration_surface or "",
        response_surface=response_surface or "",
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
        hash_surface = realized_surface
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
        hash_surface = realized_surface
        articulation_surface = realized_surface
        authority = "realizer"

    fold_sources: list[str] = []
    if walk_surface:
        surface = f"{surface} — {walk_surface}" if surface else walk_surface
        hash_surface = (
            f"{hash_surface} — {walk_surface}" if hash_surface else walk_surface
        )
        articulation_surface = (
            f"{articulation_surface} — {walk_surface}"
            if articulation_surface
            else walk_surface
        )
        fold_sources.append("walk")

    if compose_surface:
        surface = f"{surface} — {compose_surface}" if surface else compose_surface
        hash_surface = (
            f"{hash_surface} — {compose_surface}" if hash_surface else compose_surface
        )
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
        hash_surface=hash_surface,
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
