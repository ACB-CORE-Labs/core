"""Symbolic relational structure-mapper — S1 vertical slice (Track B).

Aligns a problem's role-predicate graph to the S1 canonical by **relational
role matching** (predicate kinds + systematicity). Surface attributes
(entity names, numbers) become the binding; they do not drive the match.

Blind: never reads gold structure labels. Refuse is a first-class outcome.
Deterministic: single compare-total pattern, fixed role assignment rules.

Pure-S1 gate (Increment 1): the problem must be *exactly* two roles
``a`` (seeded) and ``b`` (defined by ``k×a``) with total over ``{a,b}``.
A total that merely *includes* ``a`` and ``b`` among other parts, or any
seeded ``contain`` on a third entity, is refused — never bound and rebuilt
as a smaller pure-S1 problem (that would emit a wrong certified answer).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from generate.structure_mapping.canonicals import S1_CANONICAL
from generate.structure_mapping.role_predicate import RoleGraph


@dataclass(frozen=True, slots=True)
class StructureMapResult:
    """Successful map onto S1 with variable binding."""

    maps_to_s1: bool
    """Always True on this type; present for the public ``(bool, binding)`` contract."""

    binding: Mapping[str, object]
    """Roles: ``a`` (ref entity), ``b`` (scaled entity), ``k`` (factor float),
    ``a_value`` (float), ``unit`` (str), ``a_qty_term`` reserved."""

    matched_predicates: tuple[str, ...]
    """Predicate kinds that participated (for right-reason audits)."""


@dataclass(frozen=True, slots=True)
class StructureMapRefuse:
    """No admissible S1 alignment."""

    reason: str


def map_to_s1(role_graph: RoleGraph) -> StructureMapResult | StructureMapRefuse:
    """Map ``role_graph`` to the S1 canonical or refuse.

    Algorithm (deterministic, systematicity-first, pure-S1 only):
    1. Require exactly one ``compare`` predicate (multiplicative factor present).
    2. Require exactly one admissible ``total`` whose **part-set equals**
       ``{a, b}`` (not a superset — extras would be dropped by rebuild solve).
    3. Require a ``contain`` on the compare reference entity (role ``a``) with
       a known quantity — the seed.
    4. Refuse any ``contain`` whose entity is not ``a`` (including ``b`` and
       any third entity ``c``). ``b`` is defined only via the compare.
    5. Refuse on transfer/rate co-presence (multi-frontier; out of Increment 1).

    Gold labels are never consulted.
    """
    if not isinstance(role_graph, RoleGraph):
        raise TypeError(
            f"map_to_s1 expects RoleGraph, got {type(role_graph).__name__}"
        )

    # Deliberately unused: S1_CANONICAL is the prior schema we match *against*
    # by construction of the rules below (same predicate multiset). Referencing
    # it keeps the library load-bearing and prevents "orphan canonical" drift.
    _ = S1_CANONICAL.structure_id

    compares = role_graph.of_kind("compare")
    totals = role_graph.of_kind("total")
    contains = role_graph.of_kind("contain")
    transfers = role_graph.of_kind("transfer")
    rates = role_graph.of_kind("rate")

    if transfers:
        return StructureMapRefuse(reason="non_s1_has_transfer")
    if rates:
        return StructureMapRefuse(reason="non_s1_has_rate")
    if len(compares) != 1:
        return StructureMapRefuse(
            reason=f"compare_count_not_one:{len(compares)}"
        )
    if not totals:
        return StructureMapRefuse(reason="missing_total_query")

    compare = compares[0]
    b_term, a_term, k_term = compare.args
    if a_term.kind != "entity" or b_term.kind != "entity":
        return StructureMapRefuse(reason="compare_args_not_entities")
    if k_term.kind != "quantity" or k_term.value is None:
        return StructureMapRefuse(reason="compare_factor_missing")
    if k_term.value <= 0:
        return StructureMapRefuse(reason="compare_factor_non_positive")

    a_name = a_term.name
    b_name = b_term.name
    if a_name == b_name:
        return StructureMapRefuse(reason="compare_self_reference")

    k = float(k_term.value)
    expected_parts = frozenset({a_name, b_name})

    # Pure S1: total part-set must equal {a, b} exactly — not a superset.
    # A total that merely includes a,b among other parts is multi-entity and
    # must refuse; rebuilding a+b alone would emit the wrong problem's answer.
    exact_total = False
    for total in totals:
        part_names = frozenset(
            t.name for t in total.args[:-1] if t.kind == "entity"
        )
        if part_names == expected_parts:
            exact_total = True
            break
    if not exact_total:
        # Distinguish "missing roles" vs "extra parts" for auditability.
        any_cover = any(
            a_name in (t.name for t in total.args[:-1] if t.kind == "entity")
            and b_name in (t.name for t in total.args[:-1] if t.kind == "entity")
            for total in totals
        )
        if any_cover:
            return StructureMapRefuse(reason="total_parts_not_exactly_a_b")
        return StructureMapRefuse(reason="total_does_not_cover_compare_roles")

    # contain(a, qty) required; no other entity may carry a seed contain.
    a_value: float | None = None
    unit: str | None = None
    for c in contains:
        ent, qty = c.args
        if ent.kind != "entity" or qty.kind != "quantity":
            continue
        if qty.value is None:
            continue
        if ent.name == a_name:
            a_value = float(qty.value)
            unit = qty.unit
            continue
        # Any contain on b or a third entity is not pure S1.
        if ent.name == b_name:
            return StructureMapRefuse(
                reason="b_has_independent_contain_not_pure_s1"
            )
        return StructureMapRefuse(
            reason=f"extra_contain_not_pure_s1:{ent.name}"
        )

    if a_value is None:
        return StructureMapRefuse(reason="missing_contain_on_reference_a")

    binding: dict[str, object] = {
        "a": a_name,
        "b": b_name,
        "k": k,
        "a_value": a_value,
        "unit": unit or "",
        "canonical_id": S1_CANONICAL.structure_id,
    }
    return StructureMapResult(
        maps_to_s1=True,
        binding=binding,
        matched_predicates=("contain", "compare", "total"),
    )


def binding_roles_only(binding: Mapping[str, object]) -> dict[str, object]:
    """Return the solve-relevant subset of a binding (no label fields)."""
    keys = ("a", "b", "k", "a_value", "unit")
    return {k: binding[k] for k in keys if k in binding}
