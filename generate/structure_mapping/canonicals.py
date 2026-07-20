"""Canonical role-predicate skeletons (expert schema library).

Track B Increment 2: S1–S4. Each is a typed role skeleton with abstract
``var`` terms only — no surface literals as schema identity.
"""

from __future__ import annotations

from dataclasses import dataclass

from generate.structure_mapping.role_predicate import RolePredicate, RoleTerm


@dataclass(frozen=True, slots=True)
class CanonicalStructure:
    """A named schema with abstract role variables (not surface attributes)."""

    structure_id: str
    """Stable id for the schema (e.g. ``S1``). Library key only — never read
    from gold labels at match time."""

    description: str
    predicates: tuple[RolePredicate, ...]
    """Abstract skeleton; terms are ``var`` roles only."""


def _var(name: str) -> RoleTerm:
    return RoleTerm(kind="var", name=name)


# S1: "b is k× a; find a+b"
# compare(b, a, k) ∧ contain(a, a_qty) ∧ total(a, b, sum)
# (seed may equivalently be on b; mapper recovers a_value = b_value/k)
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

# S2: transfer-then-query — contain(src), contain(dst), transfer(src→dst, qty);
# query one endpoint after the transfer.
S2_CANONICAL: CanonicalStructure = CanonicalStructure(
    structure_id="S2",
    description=(
        "transfer-then-query: src and dst seeded; qty moves src→dst; "
        "query one endpoint's post-transfer amount."
    ),
    predicates=(
        RolePredicate(kind="contain", args=(_var("src"), _var("src_qty"))),
        RolePredicate(kind="contain", args=(_var("dst"), _var("dst_qty"))),
        RolePredicate(
            kind="transfer",
            args=(_var("src"), _var("dst"), _var("xfer_qty")),
        ),
    ),
)

# S3: rate-application — rate × count → total (or invert).
S3_CANONICAL: CanonicalStructure = CanonicalStructure(
    structure_id="S3",
    description=(
        "rate-application: per_unit rate applied over count yields total. "
        "Roles: rate_value, count, total_slot."
    ),
    predicates=(
        RolePredicate(
            kind="rate",
            args=(_var("rate_value"), _var("count"), _var("total_slot")),
        ),
    ),
)

# S4: additive-comparison-then-total — b = a + delta; query a+b.
# Uses compare_add (additive twin of multiplicative compare).
S4_CANONICAL: CanonicalStructure = CanonicalStructure(
    structure_id="S4",
    description=(
        "additive-comparison-then-total: b = a + delta; query a+b. "
        "Roles: a=reference, b=offset entity, delta=additive gap."
    ),
    predicates=(
        RolePredicate(kind="contain", args=(_var("a"), _var("a_qty"))),
        RolePredicate(
            kind="compare_add",
            args=(_var("b"), _var("a"), _var("delta")),
        ),
        RolePredicate(
            kind="total",
            args=(_var("a"), _var("b"), _var("sum")),
        ),
    ),
)

CANONICAL_LIBRARY: tuple[CanonicalStructure, ...] = (
    S1_CANONICAL,
    S2_CANONICAL,
    S3_CANONICAL,
    S4_CANONICAL,
)

CANONICAL_BY_ID: dict[str, CanonicalStructure] = {
    c.structure_id: c for c in CANONICAL_LIBRARY
}
