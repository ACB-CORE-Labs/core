"""Authored mapping rules for observed-HE morph constraints v0."""

from __future__ import annotations

from generate.observed_he_morph_v0.records import (
    AuthoredMappingRule,
    CanonicalConstraint,
    ObservedHebrewSurface,
)


class PluralAbstainRuleV0(AuthoredMappingRule):
    """Map observed plural HE morphology → plurality_marked constraint.

    Precondition: inflection.number == plural and root non-empty.
    Counterexamples: singular surfaces; OOV; multi-root ambiguous packs.
    Consumer: teaching-store contradiction/abstention — force abstain when a
    proposal asserts exclusive singular identity for the same lemma.
    """

    def __init__(self) -> None:
        super().__init__(
            rule_id="he_morph_v0.plural_abstain",
            preconditions=(
                "language==he",
                "inflection.number==plural",
                "root non-empty",
            ),
            counterexamples=(
                "singular dabar surface must not fire",
                "OOV surface with no pack row must fail closed",
                "ambiguous multi-root without rule must not auto-commit",
            ),
            constraint_kind="plurality_marked",
        )

    def matches(self, surface: ObservedHebrewSurface) -> bool:
        if surface.language != "he":
            return False
        if not surface.root:
            return False
        return surface.number == "plural"

    def to_constraint(self, surface: ObservedHebrewSurface) -> CanonicalConstraint:
        return CanonicalConstraint(
            constraint_id=f"{self.rule_id}:{surface.morphology_id}",
            kind=self.constraint_kind,
            payload={
                "lemma": surface.lemma,
                "root": surface.root,
                "surface": surface.surface,
                "morphology_id": surface.morphology_id,
                "source_span": list(surface.source_span),
                "source_pack_id": surface.source_pack_id,
            },
        )


PLURAL_ABSTAIN_RULE_V0 = PluralAbstainRuleV0()
