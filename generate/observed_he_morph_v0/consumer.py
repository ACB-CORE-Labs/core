"""Teaching-store contradiction / abstention consumer for HE morph constraints."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Sequence

from generate.observed_he_morph_v0.records import (
    AuthoredMappingRule,
    CanonicalConstraint,
    ObservedHebrewSurface,
    lookup_surface,
)
from generate.observed_he_morph_v0.rules import PLURAL_ABSTAIN_RULE_V0
from recognition.depth_canonical import observe_root_ambiguity


class DecisionKind(str, Enum):
    PASS = "pass"  # no effect
    ABSTAIN = "abstain"  # force contested / refuse
    FAIL_CLOSED = "fail_closed"  # ambiguous / OOV / invalid


@dataclass(frozen=True, slots=True)
class ConstraintDecision:
    kind: DecisionKind
    reason: str
    constraints: tuple[CanonicalConstraint, ...] = ()
    surfaces: tuple[ObservedHebrewSurface, ...] = ()
    rule_id: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind.value,
            "reason": self.reason,
            "constraints": [c.as_dict() for c in self.constraints],
            "surfaces": [s.as_dict() for s in self.surfaces],
            "rule_id": self.rule_id,
        }


def apply_he_morph_constraint(
    *,
    proposal_text: str,
    lemma_key: str,
    observed_catalog: Sequence[ObservedHebrewSurface],
    rule: AuthoredMappingRule = PLURAL_ABSTAIN_RULE_V0,
    mode: str = "executable",
    he_surface: str | None = None,
) -> ConstraintDecision:
    """Live consumer at teaching-chain abstention seam.

    Modes:
      * ``canonical`` — ignore HE morph entirely (baseline)
      * ``metadata`` — attach morph records but never change decision
      * ``executable`` — rule may force ABSTAIN
      * ``adversarial`` — invalid/ambiguous inputs must FAIL_CLOSED

    ``lemma_key`` is the language-independent subject/lemma under review.
    ``he_surface`` is the observed HE surface form when present.
    """
    mode = mode.strip().lower()
    if mode == "canonical":
        return ConstraintDecision(kind=DecisionKind.PASS, reason="canonical_baseline")

    if not he_surface:
        if mode == "adversarial":
            return ConstraintDecision(
                kind=DecisionKind.FAIL_CLOSED,
                reason="missing_he_surface",
            )
        return ConstraintDecision(kind=DecisionKind.PASS, reason="no_he_surface")

    hits = lookup_surface(observed_catalog, he_surface)
    if hits is None:
        return ConstraintDecision(
            kind=DecisionKind.FAIL_CLOSED,
            reason="oov_he_surface",
        )
    if len(hits) > 1:
        return ConstraintDecision(
            kind=DecisionKind.FAIL_CLOSED,
            reason="ambiguous_surface_matches",
            surfaces=hits,
        )

    # Multi-root ambiguity across catalog for same lemma → fail closed
    lemma_rows = [s for s in observed_catalog if s.lemma == hits[0].lemma]
    roots = sorted({s.root for s in lemma_rows if s.root})
    if len(roots) > 1:
        depth = {
            s.morphology_id: {"language": "he", "root": s.root}
            for s in lemma_rows
            if s.root
        }
        amb = observe_root_ambiguity(depth)
        if amb is not None:
            return ConstraintDecision(
                kind=DecisionKind.FAIL_CLOSED,
                reason="ambiguous_hebrew_roots",
                surfaces=tuple(lemma_rows),
            )

    surface = hits[0]
    if not surface.root or not surface.morphology_id:
        return ConstraintDecision(
            kind=DecisionKind.FAIL_CLOSED,
            reason="invalid_morphology",
            surfaces=(surface,),
        )

    if mode == "metadata":
        # Morph present for provenance only — decision identical to baseline.
        return ConstraintDecision(
            kind=DecisionKind.PASS,
            reason="metadata_only_inert",
            surfaces=(surface,),
        )

    if mode == "adversarial" and "INVALID" in he_surface:
        return ConstraintDecision(
            kind=DecisionKind.FAIL_CLOSED,
            reason="adversarial_invalid_surface",
            surfaces=(surface,),
        )

    # Executable rule arm
    if not rule.matches(surface):
        return ConstraintDecision(
            kind=DecisionKind.PASS,
            reason="rule_preconditions_unmet",
            surfaces=(surface,),
            rule_id=rule.rule_id,
        )

    constraint = rule.to_constraint(surface)
    # Abstain when proposal asserts exclusive singular / singular-only claim
    # about a lemma that is observed plural in HE morph.
    text_l = proposal_text.lower()
    singular_claim = any(
        tok in text_l
        for tok in ("singular only", "not plural", "must be singular", "exclusive singular")
    )
    lemma_mentioned = lemma_key.lower() in text_l or surface.lemma in proposal_text
    if singular_claim and lemma_mentioned:
        return ConstraintDecision(
            kind=DecisionKind.ABSTAIN,
            reason="plural_morph_blocks_singular_exclusivity",
            constraints=(constraint,),
            surfaces=(surface,),
            rule_id=rule.rule_id,
        )
    return ConstraintDecision(
        kind=DecisionKind.PASS,
        reason="rule_matched_no_conflict",
        constraints=(constraint,),
        surfaces=(surface,),
        rule_id=rule.rule_id,
    )
