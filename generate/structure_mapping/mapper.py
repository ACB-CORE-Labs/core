"""Symbolic relational structure-mapper — S1–S4 pure-family gates (Track B).

Aligns a problem's role-predicate graph to a canonical by **relational role
matching**. Surface attributes become the binding; they do not drive the match.

Blind: never reads gold structure labels. Refuse is a first-class outcome.
Each family has pure-family gates (exact role/part-set matching; refuse
supersets and stray predicates) so none can rebuild a wrong subproblem.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from generate.structure_mapping.canonicals import (
    S1_CANONICAL,
    S2_CANONICAL,
    S3_CANONICAL,
    S4_CANONICAL,
)
from generate.structure_mapping.role_predicate import RoleGraph


@dataclass(frozen=True, slots=True)
class StructureMapResult:
    """Successful map onto one canonical with variable binding."""

    structure_id: str
    """Matched canonical id (library key from the match, not a gold label)."""

    binding: Mapping[str, object]
    matched_predicates: tuple[str, ...]
    """Predicate kinds that participated (for right-reason audits)."""

    # Back-compat with Increment 1 callers
    @property
    def maps_to_s1(self) -> bool:
        return self.structure_id == "S1"


@dataclass(frozen=True, slots=True)
class StructureMapRefuse:
    """No admissible alignment for the requested family (or all families)."""

    reason: str
    structure_id: str | None = None


def map_to_s1(role_graph: RoleGraph) -> StructureMapResult | StructureMapRefuse:
    """Map ``role_graph`` to the S1 canonical or refuse.

    Pure-S1 gate:
    1. Exactly one multiplicative ``compare``; no transfer/rate/compare_add.
    2. Exactly one ``total`` whose part-set equals ``{a, b}``.
    3. Seed ``contain`` on ``a`` **or** on ``b`` (not both, not a third).
       If only ``b`` is seeded, ``a_value = b_value / k`` (inverted seed).
    4. No extra contains.
    """
    if not isinstance(role_graph, RoleGraph):
        raise TypeError(
            f"map_to_s1 expects RoleGraph, got {type(role_graph).__name__}"
        )
    _ = S1_CANONICAL.structure_id

    compares = role_graph.of_kind("compare")
    totals = role_graph.of_kind("total")
    contains = role_graph.of_kind("contain")
    transfers = role_graph.of_kind("transfer")
    rates = role_graph.of_kind("rate")
    compare_adds = role_graph.of_kind("compare_add")

    if transfers:
        return StructureMapRefuse(reason="non_s1_has_transfer", structure_id="S1")
    if rates:
        return StructureMapRefuse(reason="non_s1_has_rate", structure_id="S1")
    if compare_adds:
        return StructureMapRefuse(reason="non_s1_has_compare_add", structure_id="S1")
    if len(compares) != 1:
        return StructureMapRefuse(
            reason=f"compare_count_not_one:{len(compares)}", structure_id="S1"
        )
    if not totals:
        return StructureMapRefuse(reason="missing_total_query", structure_id="S1")

    compare = compares[0]
    b_term, a_term, k_term = compare.args
    if a_term.kind != "entity" or b_term.kind != "entity":
        return StructureMapRefuse(reason="compare_args_not_entities", structure_id="S1")
    if k_term.kind != "quantity" or k_term.value is None:
        return StructureMapRefuse(reason="compare_factor_missing", structure_id="S1")
    if k_term.value <= 0:
        return StructureMapRefuse(reason="compare_factor_non_positive", structure_id="S1")

    a_name = a_term.name
    b_name = b_term.name
    if a_name == b_name:
        return StructureMapRefuse(reason="compare_self_reference", structure_id="S1")

    k = float(k_term.value)
    expected_parts = frozenset({a_name, b_name})

    exact_total = False
    for total in totals:
        part_names = frozenset(
            t.name for t in total.args[:-1] if t.kind == "entity"
        )
        if part_names == expected_parts:
            exact_total = True
            break
    if not exact_total:
        any_cover = any(
            a_name in (t.name for t in total.args[:-1] if t.kind == "entity")
            and b_name in (t.name for t in total.args[:-1] if t.kind == "entity")
            for total in totals
        )
        if any_cover:
            return StructureMapRefuse(
                reason="total_parts_not_exactly_a_b", structure_id="S1"
            )
        return StructureMapRefuse(
            reason="total_does_not_cover_compare_roles", structure_id="S1"
        )

    a_value: float | None = None
    b_value: float | None = None
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
        if ent.name == b_name:
            b_value = float(qty.value)
            if unit is None:
                unit = qty.unit
            continue
        return StructureMapRefuse(
            reason=f"extra_contain_not_pure_s1:{ent.name}", structure_id="S1"
        )

    if a_value is not None and b_value is not None:
        # Both seeded: only admissible if consistent with b = k×a.
        expected_b = a_value * k
        if abs(expected_b - b_value) > 1e-6 * max(1.0, abs(expected_b)):
            return StructureMapRefuse(
                reason="dual_seed_inconsistent_with_compare", structure_id="S1"
            )
        # Prefer a-seeded pure form.
        b_value = None

    if a_value is None and b_value is None:
        return StructureMapRefuse(
            reason="missing_contain_on_reference_a", structure_id="S1"
        )

    if a_value is None:
        # Inverted seed: b known, a = b/k.
        assert b_value is not None
        if abs(k) < 1e-12:
            return StructureMapRefuse(reason="compare_factor_near_zero", structure_id="S1")
        a_value = float(b_value) / k
        seed_mode = "b_seeded"
    else:
        seed_mode = "a_seeded"

    binding: dict[str, object] = {
        "a": a_name,
        "b": b_name,
        "k": k,
        "a_value": a_value,
        "unit": unit or "",
        "canonical_id": S1_CANONICAL.structure_id,
        "seed_mode": seed_mode,
    }
    return StructureMapResult(
        structure_id="S1",
        binding=binding,
        matched_predicates=("contain", "compare", "total"),
    )


def map_to_s2(role_graph: RoleGraph) -> StructureMapResult | StructureMapRefuse:
    """Pure S2: exactly one transfer, contains on src+dst only, query one endpoint.

    No compare / compare_add / rate / total (total would be multi-entity sum;
    S2 queries a single entity after transfer).
    """
    if not isinstance(role_graph, RoleGraph):
        raise TypeError(
            f"map_to_s2 expects RoleGraph, got {type(role_graph).__name__}"
        )
    _ = S2_CANONICAL.structure_id

    transfers = role_graph.of_kind("transfer")
    contains = role_graph.of_kind("contain")
    compares = role_graph.of_kind("compare")
    compare_adds = role_graph.of_kind("compare_add")
    rates = role_graph.of_kind("rate")
    totals = role_graph.of_kind("total")

    if compares:
        return StructureMapRefuse(reason="non_s2_has_compare", structure_id="S2")
    if compare_adds:
        return StructureMapRefuse(reason="non_s2_has_compare_add", structure_id="S2")
    if rates:
        return StructureMapRefuse(reason="non_s2_has_rate", structure_id="S2")
    if totals:
        return StructureMapRefuse(reason="non_s2_has_total", structure_id="S2")
    if len(transfers) != 1:
        return StructureMapRefuse(
            reason=f"transfer_count_not_one:{len(transfers)}", structure_id="S2"
        )

    xfer = transfers[0]
    src_t, dst_t, qty_t = xfer.args
    if src_t.kind != "entity" or dst_t.kind != "entity":
        return StructureMapRefuse(reason="transfer_endpoints_not_entities", structure_id="S2")
    if qty_t.kind != "quantity" or qty_t.value is None:
        return StructureMapRefuse(reason="transfer_qty_missing", structure_id="S2")
    if qty_t.value < 0:
        return StructureMapRefuse(reason="transfer_qty_negative", structure_id="S2")

    src, dst = src_t.name, dst_t.name
    if src == dst:
        return StructureMapRefuse(reason="transfer_self", structure_id="S2")

    seeds: dict[str, tuple[float, str | None]] = {}
    for c in contains:
        ent, qty = c.args
        if ent.kind != "entity" or qty.kind != "quantity" or qty.value is None:
            continue
        if ent.name not in (src, dst):
            return StructureMapRefuse(
                reason=f"extra_contain_not_pure_s2:{ent.name}", structure_id="S2"
            )
        seeds[ent.name] = (float(qty.value), qty.unit)

    if src not in seeds or dst not in seeds:
        return StructureMapRefuse(reason="missing_src_or_dst_seed", structure_id="S2")

    # Query entity: inferred from a single unknown-less graph later; for pure
    # role match we require the binding to name both post-transfer values.
    # Default query = dst (most common "how many does Y have?" after receive).
    # Callers that know the unknown entity may override via binding later.
    src_val, unit = seeds[src]
    dst_val, unit_d = seeds[dst]
    unit = unit or unit_d or ""
    xfer_qty = float(qty_t.value)

    binding: dict[str, object] = {
        "src": src,
        "dst": dst,
        "xfer_qty": xfer_qty,
        "src_value": src_val,
        "dst_value": dst_val,
        "unit": unit,
        "query_entity": dst,  # default; solve may override from original graph
        "canonical_id": S2_CANONICAL.structure_id,
    }
    return StructureMapResult(
        structure_id="S2",
        binding=binding,
        matched_predicates=("contain", "contain", "transfer"),
    )


def map_to_s3(role_graph: RoleGraph) -> StructureMapResult | StructureMapRefuse:
    """Pure S3: exactly one rate predicate; no transfer/compare/total pollution."""
    if not isinstance(role_graph, RoleGraph):
        raise TypeError(
            f"map_to_s3 expects RoleGraph, got {type(role_graph).__name__}"
        )
    _ = S3_CANONICAL.structure_id

    rates = role_graph.of_kind("rate")
    if len(rates) != 1:
        return StructureMapRefuse(
            reason=f"rate_count_not_one:{len(rates)}", structure_id="S3"
        )
    if role_graph.of_kind("transfer"):
        return StructureMapRefuse(reason="non_s3_has_transfer", structure_id="S3")
    if role_graph.of_kind("compare"):
        return StructureMapRefuse(reason="non_s3_has_compare", structure_id="S3")
    if role_graph.of_kind("compare_add"):
        return StructureMapRefuse(reason="non_s3_has_compare_add", structure_id="S3")
    if role_graph.of_kind("total"):
        return StructureMapRefuse(reason="non_s3_has_total", structure_id="S3")

    rate = rates[0]
    per, count, total_slot = rate.args
    if per.kind != "quantity" or per.value is None:
        return StructureMapRefuse(reason="rate_value_missing", structure_id="S3")
    # count may be entity or quantity depending on converter
    count_value: float | None = None
    count_name = count.name
    if count.kind == "quantity" and count.value is not None:
        count_value = float(count.value)
    # Look for contain on count entity for the duration/count seed
    if count_value is None and count.kind == "entity":
        for c in role_graph.of_kind("contain"):
            ent, qty = c.args
            if ent.kind == "entity" and ent.name == count.name and qty.value is not None:
                count_value = float(qty.value)
                break
    if count_value is None:
        return StructureMapRefuse(reason="rate_count_missing", structure_id="S3")
    if per.value <= 0 or count_value <= 0:
        return StructureMapRefuse(reason="rate_non_positive", structure_id="S3")

    binding: dict[str, object] = {
        "rate_value": float(per.value),
        "count": count_value,
        "count_name": count_name,
        "unit": per.unit or (total_slot.unit if total_slot.kind == "quantity" else "") or "",
        "canonical_id": S3_CANONICAL.structure_id,
    }
    return StructureMapResult(
        structure_id="S3",
        binding=binding,
        matched_predicates=("rate",),
    )


def map_to_s4(role_graph: RoleGraph) -> StructureMapResult | StructureMapRefuse:
    """Pure S4: one compare_add, total over {a,b}, seed contain on a (or b)."""
    if not isinstance(role_graph, RoleGraph):
        raise TypeError(
            f"map_to_s4 expects RoleGraph, got {type(role_graph).__name__}"
        )
    _ = S4_CANONICAL.structure_id

    if role_graph.of_kind("transfer"):
        return StructureMapRefuse(reason="non_s4_has_transfer", structure_id="S4")
    if role_graph.of_kind("rate"):
        return StructureMapRefuse(reason="non_s4_has_rate", structure_id="S4")
    if role_graph.of_kind("compare"):
        return StructureMapRefuse(reason="non_s4_has_multiplicative_compare", structure_id="S4")

    adds = role_graph.of_kind("compare_add")
    totals = role_graph.of_kind("total")
    contains = role_graph.of_kind("contain")
    if len(adds) != 1:
        return StructureMapRefuse(
            reason=f"compare_add_count_not_one:{len(adds)}", structure_id="S4"
        )
    if not totals:
        return StructureMapRefuse(reason="missing_total_query", structure_id="S4")

    cad = adds[0]
    b_term, a_term, d_term = cad.args
    if a_term.kind != "entity" or b_term.kind != "entity":
        return StructureMapRefuse(reason="compare_add_args_not_entities", structure_id="S4")
    if d_term.kind != "quantity" or d_term.value is None:
        return StructureMapRefuse(reason="compare_add_delta_missing", structure_id="S4")

    a_name, b_name = a_term.name, b_term.name
    if a_name == b_name:
        return StructureMapRefuse(reason="compare_add_self_reference", structure_id="S4")
    delta = float(d_term.value)
    expected_parts = frozenset({a_name, b_name})

    if not any(
        frozenset(t.name for t in total.args[:-1] if t.kind == "entity") == expected_parts
        for total in totals
    ):
        return StructureMapRefuse(reason="total_parts_not_exactly_a_b", structure_id="S4")

    a_value: float | None = None
    b_value: float | None = None
    unit: str | None = None
    for c in contains:
        ent, qty = c.args
        if ent.kind != "entity" or qty.kind != "quantity" or qty.value is None:
            continue
        if ent.name == a_name:
            a_value = float(qty.value)
            unit = qty.unit
        elif ent.name == b_name:
            b_value = float(qty.value)
            if unit is None:
                unit = qty.unit
        else:
            return StructureMapRefuse(
                reason=f"extra_contain_not_pure_s4:{ent.name}", structure_id="S4"
            )

    if a_value is None and b_value is None:
        return StructureMapRefuse(reason="missing_seed_for_s4", structure_id="S4")
    if a_value is None:
        assert b_value is not None
        a_value = b_value - delta
        seed_mode = "b_seeded"
    elif b_value is None:
        seed_mode = "a_seeded"
    else:
        if abs((a_value + delta) - b_value) > 1e-6 * max(1.0, abs(b_value)):
            return StructureMapRefuse(
                reason="dual_seed_inconsistent_with_compare_add", structure_id="S4"
            )
        seed_mode = "a_seeded"

    binding: dict[str, object] = {
        "a": a_name,
        "b": b_name,
        "delta": delta,
        "a_value": a_value,
        "unit": unit or "",
        "canonical_id": S4_CANONICAL.structure_id,
        "seed_mode": seed_mode,
    }
    return StructureMapResult(
        structure_id="S4",
        binding=binding,
        matched_predicates=("contain", "compare_add", "total"),
    )


def binding_roles_only(binding: Mapping[str, object]) -> dict[str, object]:
    """Return the solve-relevant subset of a binding (no label fields)."""
    keys = (
        "a",
        "b",
        "k",
        "a_value",
        "unit",
        "src",
        "dst",
        "xfer_qty",
        "src_value",
        "dst_value",
        "query_entity",
        "rate_value",
        "count",
        "delta",
    )
    return {k: binding[k] for k in keys if k in binding}


MAPPERS = {
    "S1": map_to_s1,
    "S2": map_to_s2,
    "S3": map_to_s3,
    "S4": map_to_s4,
}
