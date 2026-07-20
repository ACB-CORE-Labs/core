"""Typed role-predicate graph for symbolic structure-mapping (Track B).

Two-argument (and n-ary total) relational predicates over entities and
quantities. Surface attributes (names, exact numbers, word order) are
*values* bound to roles — they are not schema identity.

Deterministic: frozen dataclasses, sorted serialization for digests.
No geometry. No structure labels.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Literal

PredicateKind = Literal[
    "contain",
    "transfer",
    "compare",
    "compare_add",
    "rate",
    "total",
]

VALID_PREDICATE_KINDS: Final[frozenset[str]] = frozenset(
    {"contain", "transfer", "compare", "compare_add", "rate", "total"}
)


@dataclass(frozen=True, slots=True)
class RoleTerm:
    """A typed slot filler: entity id, quantity value, or abstract role var.

    ``kind`` discriminates:
    - ``entity``: surface entity string (attribute; discarded for schema match)
    - ``quantity``: numeric value + optional unit (attribute)
    - ``var``: abstract role variable name used only in canonicals (e.g. ``a``)
    """

    kind: Literal["entity", "quantity", "var"]
    name: str
    value: float | None = None
    unit: str | None = None

    def __post_init__(self) -> None:
        if self.kind not in ("entity", "quantity", "var"):
            raise ValueError(f"RoleTerm.kind invalid: {self.kind!r}")
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("RoleTerm.name must be a non-empty string")
        if self.kind == "quantity":
            if self.value is None:
                raise ValueError("quantity RoleTerm requires value")
        if self.kind == "var" and self.value is not None:
            raise ValueError("var RoleTerm must not carry a value")


@dataclass(frozen=True, slots=True)
class RolePredicate:
    """One relational fact: ``kind(args...)``.

    Role order is schema-fixed per kind (not surface word order):
    - contain(entity, qty)
    - transfer(src, dst, qty)
    - compare(b, a, k)  — b is k× a (actor, reference, factor)
    - compare_add(b, a, delta) — b = a + delta (actor, reference, gap)
    - rate(per_unit, count, total)
    - total(part_1, ..., part_n, sum_query)
    """

    kind: PredicateKind
    args: tuple[RoleTerm, ...]

    def __post_init__(self) -> None:
        if self.kind not in VALID_PREDICATE_KINDS:
            raise ValueError(f"unknown predicate kind: {self.kind!r}")
        if not self.args:
            raise ValueError("RolePredicate.args must be non-empty")
        if self.kind == "contain" and len(self.args) != 2:
            raise ValueError("contain requires (entity, qty)")
        if self.kind == "transfer" and len(self.args) != 3:
            raise ValueError("transfer requires (src, dst, qty)")
        if self.kind == "compare" and len(self.args) != 3:
            raise ValueError("compare requires (b, a, k)")
        if self.kind == "compare_add" and len(self.args) != 3:
            raise ValueError("compare_add requires (b, a, delta)")
        if self.kind == "rate" and len(self.args) != 3:
            raise ValueError("rate requires (per_unit, count, total)")
        if self.kind == "total" and len(self.args) < 2:
            raise ValueError("total requires at least one part and a sum slot")


@dataclass(frozen=True, slots=True)
class RoleGraph:
    """A problem's relational structure after attribute-light conversion.

    ``predicates`` are in deterministic order (kind then arg names) so
    equal graphs compare equal regardless of parse emission order when
    converters sort before construction.
    """

    predicates: tuple[RolePredicate, ...]
    source_graph_hash: str | None = None

    def kinds(self) -> frozenset[str]:
        return frozenset(p.kind for p in self.predicates)

    def of_kind(self, kind: PredicateKind) -> tuple[RolePredicate, ...]:
        return tuple(p for p in self.predicates if p.kind == kind)
