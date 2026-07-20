"""Observed-Hebrew morph → canonical constraint vertical slice (Stage 4+).

Compiled pack data only; no English-to-Hebrew pseudo-morphology.
Live authority is shared via ``authority.evaluate_logos_on_text`` for
teaching store and CognitiveTurn (same pure decision function as ablation).
"""

from generate.observed_he_morph_v0.ablation import run_four_arm_ablation
from generate.observed_he_morph_v0.authority import (
    decision_as_coherence_refusal,
    evaluate_logos_on_text,
    first_logos_constraint,
    logos_blocks_certified_answer,
    scan_observed_he_surface,
)
from generate.observed_he_morph_v0.consumer import (
    ConstraintDecision,
    DecisionKind,
    apply_he_morph_constraint,
)
from generate.observed_he_morph_v0.records import (
    AuthoredMappingRule,
    CanonicalConstraint,
    ObservedHebrewSurface,
    load_observed_morphology,
)
from generate.observed_he_morph_v0.rules import PLURAL_ABSTAIN_RULE_V0

__all__ = [
    "AuthoredMappingRule",
    "CanonicalConstraint",
    "ConstraintDecision",
    "DecisionKind",
    "ObservedHebrewSurface",
    "PLURAL_ABSTAIN_RULE_V0",
    "apply_he_morph_constraint",
    "decision_as_coherence_refusal",
    "evaluate_logos_on_text",
    "first_logos_constraint",
    "load_observed_morphology",
    "logos_blocks_certified_answer",
    "run_four_arm_ablation",
    "scan_observed_he_surface",
]
