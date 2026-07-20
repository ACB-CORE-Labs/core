"""Observed-Hebrew morph → canonical constraint vertical slice (Stage 4).

``feat/observed-he-morph-constraint-v0`` — compiled pack data only, no
English-to-Hebrew pseudo-morphology.
"""

from generate.observed_he_morph_v0.ablation import run_four_arm_ablation
from generate.observed_he_morph_v0.consumer import (
    ConstraintDecision,
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
    "ObservedHebrewSurface",
    "PLURAL_ABSTAIN_RULE_V0",
    "apply_he_morph_constraint",
    "load_observed_morphology",
    "run_four_arm_ablation",
]
