"""RED→GREEN — T13 decision (2): the grounded-open hedge arm.

Weekly-audit 2026-07-22 ruling (Shay): route open-geometry-but-**pack-grounded**
surfaces to the hedge arm (``authoritative=False``), discriminated *purely by
grounding provenance* (structural) plus a geometric-residual allowlist — never
by question type (a lexical cue-table bypass would be a fail-open ADR-0252 /
INV-34 violation).

Predicate (authorized):
    open_conjugate ∧ pack_grounded ∧ ¬hazard → hedge_arm

``¬hazard`` is enforced *structurally*: the only assessment that reaches
``resolve_surface`` is the shadow-coherence-gate geometry assessment, whose open
tokens are ⊆ {``versor_condition``, ``goldtether_residual``, ``missing_wave_field``}.
We hedge iff every open token is a *known geometric-coherence residual* that the
pack surface never claimed to certify. ANY unrecognized token — where a genuine
safety/harm/imperative hazard would land — fails the allowlist and hard-refuses.
Genuine harm/imperative content is refused on the separate SafetyVerdict /
logos-morph axes that supersede this surface downstream.

Anchor: the "What is doubt?" over-refusal — pack surface (``en_core_meta_v1``),
open ``goldtether_residual`` — was hard-refused; it must now hedge.
"""

from __future__ import annotations

import pytest

from core.cognition.surface_resolution import resolve_surface
from generate.problem_frame_contracts import ContractAssessment

_PACK_SURFACE = "To doubt means to think maybe not. pack-grounded (en_core_meta_v1)."


def _open_goldtether_assessment() -> ContractAssessment:
    """Mirror ``_geometry_contract_assessment`` when R_GoldTether > 1e-6.

    goldtether_residual lands in ``unresolved_hazards`` (it is a geometric
    residual token, not a safety hazard); versor closed → no missing binding.
    This is the exact shape behind the "What is doubt?" refusal.
    """
    return ContractAssessment(
        candidate_organ="shadow_coherence_gate",
        missing_bindings=(),
        unresolved_hazards=("goldtether_residual",),
        runnable=False,
        explanation="versor_condition=0.000e+00; R_GoldTether=3.210e-04",
    )


class TestHedgeArmActivates:
    def test_pack_grounded_open_goldtether_hedges_not_refuses(self) -> None:
        res = resolve_surface(
            canonical_surface=_PACK_SURFACE,
            response_surface=_PACK_SURFACE,
            contract_assessment=_open_goldtether_assessment(),
            grounding_provenance="pack",
            require_closed_geometry=True,
        )
        # Hedge arm: served, but never claims geometric certification.
        assert res.authoritative is False
        assert res.hedged is True
        assert res.refusal is None
        assert res.contract_violation is None
        assert res.authority == "grounded_open_hedge"
        # The pack content is served (hedged), not the typed refusal message.
        assert _PACK_SURFACE in res.surface
        assert "cannot certify" not in res.surface.casefold()

    def test_versor_condition_open_also_hedges_when_grounded(self) -> None:
        assessment = ContractAssessment(
            candidate_organ="shadow_coherence_gate",
            missing_bindings=("versor_condition",),
            unresolved_hazards=(),
            runnable=False,
            explanation="versor open",
        )
        res = resolve_surface(
            canonical_surface=_PACK_SURFACE,
            response_surface=_PACK_SURFACE,
            contract_assessment=assessment,
            grounding_provenance="teaching",  # teaching provenance is also grounded
            require_closed_geometry=True,
        )
        assert res.hedged is True
        assert res.refusal is None
        assert res.authoritative is False


class TestFailClosedGuardrails:
    @pytest.mark.parametrize("provenance", ["none", "oov", "vault", "partial", ""])
    def test_non_pack_grounding_still_hard_refuses(self, provenance: str) -> None:
        res = resolve_surface(
            canonical_surface=_PACK_SURFACE,
            response_surface=_PACK_SURFACE,
            contract_assessment=_open_goldtether_assessment(),
            grounding_provenance=provenance,
            require_closed_geometry=True,
        )
        assert res.authoritative is False
        assert res.hedged is False
        assert res.refusal is not None  # ungrounded open geometry never hedges

    def test_unknown_open_token_fails_closed_even_when_pack_grounded(self) -> None:
        # A genuine hazard token (outside the geometric-residual allowlist) must
        # NEVER be hedged, even with pack provenance. This is the ¬hazard floor.
        assessment = ContractAssessment(
            candidate_organ="shadow_coherence_gate",
            missing_bindings=(),
            unresolved_hazards=("harm_imperative",),
            runnable=False,
            explanation="genuine hazard",
        )
        res = resolve_surface(
            canonical_surface=_PACK_SURFACE,
            response_surface=_PACK_SURFACE,
            contract_assessment=assessment,
            grounding_provenance="pack",
            require_closed_geometry=True,
        )
        assert res.hedged is False
        assert res.refusal is not None

    def test_mixed_known_and_unknown_token_fails_closed(self) -> None:
        # Even one unrecognized token among geometric residuals → refuse.
        assessment = ContractAssessment(
            candidate_organ="shadow_coherence_gate",
            missing_bindings=("versor_condition",),
            unresolved_hazards=("goldtether_residual", "harm_imperative"),
            runnable=False,
            explanation="mixed",
        )
        res = resolve_surface(
            canonical_surface=_PACK_SURFACE,
            response_surface=_PACK_SURFACE,
            contract_assessment=assessment,
            grounding_provenance="pack",
            require_closed_geometry=True,
        )
        assert res.hedged is False
        assert res.refusal is not None

    def test_missing_wave_field_not_hedgeable(self) -> None:
        # No field at all is a harder failure than an open residual — fail closed.
        assessment = ContractAssessment(
            candidate_organ="shadow_coherence_gate",
            missing_bindings=("missing_wave_field",),
            unresolved_hazards=(),
            runnable=False,
            explanation="no field versor available for geometric contract",
        )
        res = resolve_surface(
            canonical_surface=_PACK_SURFACE,
            response_surface=_PACK_SURFACE,
            contract_assessment=assessment,
            grounding_provenance="pack",
            require_closed_geometry=True,
        )
        assert res.hedged is False
        assert res.refusal is not None

    def test_none_assessment_still_contract_violation(self) -> None:
        res = resolve_surface(
            canonical_surface=_PACK_SURFACE,
            response_surface=_PACK_SURFACE,
            contract_assessment=None,
            grounding_provenance="pack",
            require_closed_geometry=True,
        )
        assert res.hedged is False
        assert res.contract_violation is not None
        assert res.refusal is None


class TestClosedGeometryUnaffected:
    def test_closed_geometry_pack_stays_authoritative(self) -> None:
        assessment = ContractAssessment(
            candidate_organ="shadow_coherence_gate",
            missing_bindings=(),
            unresolved_hazards=(),
            runnable=True,
            explanation="versor_condition=0.000e+00; R_GoldTether=0.000e+00",
        )
        res = resolve_surface(
            canonical_surface=_PACK_SURFACE,
            response_surface=_PACK_SURFACE,
            contract_assessment=assessment,
            grounding_provenance="pack",
            require_closed_geometry=True,
        )
        assert res.authoritative is True
        assert res.hedged is False
        assert res.refusal is None

    def test_grounding_provenance_defaults_to_no_hedge(self) -> None:
        # Back-compat: callers that do not pass grounding_provenance must get
        # the historical hard-refusal on open geometry (no accidental hedge).
        res = resolve_surface(
            canonical_surface=_PACK_SURFACE,
            response_surface=_PACK_SURFACE,
            contract_assessment=_open_goldtether_assessment(),
            require_closed_geometry=True,
        )
        assert res.hedged is False
        assert res.refusal is not None


# --- coherence refusal marker (distinct from the safety TYPED_REFUSAL_PREFIX) ---
_COHERENCE_REFUSAL_MARKER = "cannot certify"


class TestRealDataHedgeArm:
    """GSM8K-style real-data validation on a warmed ``ChatRuntime``.

    The warmed 'What is doubt?' over-refusal (open ``goldtether_residual`` on a
    pack surface once the field is perturbed by a prior turn) is the exact T13
    case. It must now HEDGE — serve the pack definition non-authoritatively —
    never hard-refuse.
    """

    @staticmethod
    def _warmed_mixed_run() -> list:
        from chat.runtime import ChatRuntime
        from core.cognition.pipeline import CognitiveTurnPipeline

        runtime = ChatRuntime()
        pipeline = CognitiveTurnPipeline(runtime=runtime)
        # Deterministic (CORE has no RNG): perturbing the field with a prior
        # pack turn opens the goldtether residual on the next pack turn.
        sequence = ["What is truth?", "What is doubt?", "Define moment."]
        return [pipeline.run(prompt, max_tokens=8) for prompt in sequence]

    def test_open_geometry_pack_surface_hedges_not_refuses(self) -> None:
        results = self._warmed_mixed_run()
        # No pack-grounded turn in the perturbed sequence is hard-refused.
        for res in results:
            assert _COHERENCE_REFUSAL_MARKER not in res.surface.casefold(), res.surface
        # The hedge arm is genuinely exercised on real field dynamics.
        authorities = [getattr(res, "authority_source", "") for res in results]
        assert "grounded_open_hedge" in authorities, authorities
        # The hedged turn still serves the pack definition content.
        hedged = next(
            res
            for res in results
            if getattr(res, "authority_source", "") == "grounded_open_hedge"
        )
        assert "not geometrically certified" in hedged.surface.casefold()

    def test_warmed_lane_never_hard_refuses_a_pack_surface(self) -> None:
        from evals.framework import get_lane, run_lane

        result = run_lane(
            get_lane("warmed_session_consistency"), version="v1", split="public"
        )
        for case in result.case_details:
            for turn in case["turns"]:
                assert _COHERENCE_REFUSAL_MARKER not in turn["surface"].casefold(), (
                    case["case_id"],
                    turn["turn_index"],
                    turn["surface"],
                )
        # The telemetry + placeholder floors from PR #101 must not regress.
        assert result.metrics["telemetry_consistency_rate"] == 1.0
        assert result.metrics["no_placeholder_rate"] == 1.0
