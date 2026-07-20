"""Shared Logos morph authority — single decision entry for live seams + ablation.

Teaching store and CognitiveTurn consult the same pure decision function
(``apply_he_morph_constraint``) via helpers here. Modes:

  * canonical / metadata / executable / adversarial

Morph may force abstain/refuse; it never soft-passes a certified singular
exclusivity claim against observed plural HE morphology.
"""

from __future__ import annotations

from typing import Sequence

from core.cognition.fail_closed import (
    CoherenceRefusal,
    FailureClass,
    ResidualState,
)
from core.semantic_primitives import LogosConstraint, ProvenanceSpan
from generate.observed_he_morph_v0.consumer import (
    ConstraintDecision,
    DecisionKind,
    apply_he_morph_constraint,
)
from generate.observed_he_morph_v0.records import (
    CanonicalConstraint,
    ObservedHebrewSurface,
    load_observed_morphology,
)
from generate.observed_he_morph_v0.rules import PLURAL_ABSTAIN_RULE_V0

_DEFAULT_PACK = "he_logos_micro_v1"
_CATALOG: tuple[ObservedHebrewSurface, ...] | None = None
_LOAD_ATTEMPTED = False


def load_default_catalog() -> tuple[ObservedHebrewSurface, ...] | None:
    """Load compiled HE morphology once; None if pack missing (fail closed)."""
    global _CATALOG, _LOAD_ATTEMPTED
    if _LOAD_ATTEMPTED:
        return _CATALOG
    _LOAD_ATTEMPTED = True
    try:
        _CATALOG = load_observed_morphology(_DEFAULT_PACK)
    except Exception:
        _CATALOG = None
    return _CATALOG


def reset_catalog_cache() -> None:
    """Test-only: clear process-local catalog cache."""
    global _CATALOG, _LOAD_ATTEMPTED
    _CATALOG = None
    _LOAD_ATTEMPTED = False


def scan_observed_he_surface(
    text: str,
    catalog: Sequence[ObservedHebrewSurface] | None = None,
) -> ObservedHebrewSurface | None:
    """Longest exact observed HE surface substring present in ``text``."""
    cat = catalog if catalog is not None else load_default_catalog()
    if not cat or not text:
        return None
    hits = [s for s in cat if s.surface and s.surface in text]
    if not hits:
        return None
    hits.sort(key=lambda s: len(s.surface), reverse=True)
    return hits[0]


def evaluate_logos_on_text(
    *,
    text: str,
    mode: str = "executable",
    catalog: Sequence[ObservedHebrewSurface] | None = None,
    lemma_key: str | None = None,
    he_surface: str | None = None,
) -> ConstraintDecision | None:
    """Evaluate Logos morph authority on free text.

    Returns None when no HE surface is present and mode is not adversarial
    (no-op for English-only turns). Otherwise returns the shared
    ``ConstraintDecision`` from ``apply_he_morph_constraint``.
    """
    cat = catalog if catalog is not None else load_default_catalog()
    if cat is None:
        if mode.strip().lower() == "adversarial":
            return ConstraintDecision(
                kind=DecisionKind.FAIL_CLOSED,
                reason="morph_catalog_unavailable",
            )
        return None

    surface_row = None
    if he_surface is not None:
        surface = he_surface
    else:
        surface_row = scan_observed_he_surface(text, cat)
        if surface_row is None:
            if mode.strip().lower() == "adversarial":
                return apply_he_morph_constraint(
                    proposal_text=text,
                    lemma_key=lemma_key or "",
                    observed_catalog=cat,
                    mode="adversarial",
                    he_surface=None,
                )
            return None
        surface = surface_row.surface

    lemma = lemma_key or (surface_row.lemma if surface_row is not None else "")
    if not lemma and surface:
        # Recover lemma from catalog when only surface was supplied.
        from generate.observed_he_morph_v0.records import lookup_surface

        hits = lookup_surface(cat, surface)
        if hits:
            lemma = hits[0].lemma

    return apply_he_morph_constraint(
        proposal_text=text,
        lemma_key=lemma or surface,
        observed_catalog=cat,
        rule=PLURAL_ABSTAIN_RULE_V0,
        mode=mode,
        he_surface=surface,
    )


def logos_blocks_certified_answer(decision: ConstraintDecision | None) -> bool:
    """True when morph authority forbids a certified fluent answer."""
    if decision is None:
        return False
    return decision.kind in (DecisionKind.ABSTAIN, DecisionKind.FAIL_CLOSED)


def decision_as_coherence_refusal(
    decision: ConstraintDecision,
) -> CoherenceRefusal:
    """Map morph ConstraintDecision → typed fail-closed CoherenceRefusal."""
    if decision.kind is DecisionKind.FAIL_CLOSED:
        fclass = FailureClass.AMBIGUITY
        if "oov" in decision.reason or "missing" in decision.reason:
            fclass = FailureClass.MISSING_REFERENT
        elif "invalid" in decision.reason:
            fclass = FailureClass.CONSTRAINT
        return CoherenceRefusal(
            failure_class=fclass,
            violated_condition=f"logos_morph:{decision.reason}",
            residual_state=ResidualState(
                detail=decision.reason,
                unresolved_hazards=(decision.reason,),
            ),
            refusal_reason=decision.reason,
            surface_message=(
                f"Abstaining: Logos morph constraint ({decision.reason})."
            ),
        )
    # ABSTAIN
    return CoherenceRefusal(
        failure_class=FailureClass.CONSTRAINT,
        violated_condition=f"logos_morph:{decision.reason}",
        residual_state=ResidualState(
            detail=decision.reason,
            unresolved_hazards=(decision.reason,),
        ),
        refusal_reason=decision.reason,
        surface_message=(
            f"Abstaining: observed HE morphology blocks claim "
            f"({decision.rule_id or decision.reason})."
        ),
    )


def constraint_to_logos(constraint: CanonicalConstraint) -> LogosConstraint:
    """Project live CanonicalConstraint into shared semantic_primitives IR."""
    return constraint.to_logos_constraint()


def first_logos_constraint(
    decision: ConstraintDecision | None,
) -> LogosConstraint | None:
    if decision is None or not decision.constraints:
        return None
    return decision.constraints[0].to_logos_constraint()


__all__ = [
    "constraint_to_logos",
    "decision_as_coherence_refusal",
    "evaluate_logos_on_text",
    "first_logos_constraint",
    "load_default_catalog",
    "logos_blocks_certified_answer",
    "reset_catalog_cache",
    "scan_observed_he_surface",
]
