"""Canonical role-predicate skeletons (expert schema library).

Increment 1 ships **S1 only**: compare-multiplicative-then-total
(``compare(b, a, k) ∧ total(a, b, sum)``). Typed roles; no surface literals
as schema identity. S2–S4 deliberately absent until the S1 slice is reviewed.
"""

from __future__ import annotations

from dataclasses import dataclass

from generate.structure_mapping.role_predicate import RolePredicate, RoleTerm


@dataclass(frozen=True, slots=True)
class CanonicalStructure:
    """A named schema with abstract role variables (not surface attributes)."""

    structure_id: str
    """Stable id for the schema (e.g. ``S1``). Used only as prior-knowledge
    library key — never read from gold labels at match time."""

    description: str
    predicates: tuple[RolePredicate, ...]
    """Abstract skeleton; terms are ``var`` roles only."""


def _var(name: str) -> RoleTerm:
    return RoleTerm(kind="var", name=name)


# S1: "b is k× a; find a+b"
# compare(b, a, k) ∧ contain(a, a_qty) ∧ total(a, b, sum)
S1_CANONICAL: CanonicalStructure = CanonicalStructure(
    structure_id="S1",
    description=(
        "compare-multiplicative-then-total: b = k×a; query a+b. "
        "Roles: a=reference quantity entity, b=scaled entity, k=factor."
    ),
    predicates=(
        RolePredicate(
            kind="contain",
            args=(_var("a"), _var("a_qty")),
        ),
        RolePredicate(
            kind="compare",
            args=(_var("b"), _var("a"), _var("k")),
        ),
        RolePredicate(
            kind="total",
            args=(_var("a"), _var("b"), _var("sum")),
        ),
    ),
)
