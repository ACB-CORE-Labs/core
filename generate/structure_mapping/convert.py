"""Deterministic MathProblemGraph → role-predicate graph converter.

Pure function of the typed surface graph. No structure labels. No geometry.
"""

from __future__ import annotations

import hashlib
from typing import Iterable

from generate.math_problem_graph import (
    Comparison,
    MathProblemGraph,
    Quantity,
    Rate,
)
from generate.structure_mapping.role_predicate import (
    RoleGraph,
    RolePredicate,
    RoleTerm,
)


def graph_to_role_graph(graph: MathProblemGraph) -> RoleGraph:
    """Convert a parsed :class:`MathProblemGraph` into a :class:`RoleGraph`.

    Mapping rules (load-bearing):
    - ``initial_state`` → ``contain(entity, qty)``
    - ``compare_multiplicative`` → ``compare(actor, reference, factor)``
      (actor is k× reference — S1 role order ``compare(b, a, k)``)
    - ``transfer`` → ``transfer(src, dst, qty)``
    - ``apply_rate`` → ``rate`` with rate value / denominator-as-count placeholder
    - ``unknown.entity is None`` → ``total`` over entities that hold ``unknown.unit``
      (or all entities when unit carriers are incomplete)
    - other ops (add/subtract/multiply/…) emit no role predicates in this slice
      (they are attribute-level or deferred families)

    Returns a sorted, frozen role graph. Raises nothing on partial coverage —
    empty predicate lists are valid (mapper will refuse).
    """
    if not isinstance(graph, MathProblemGraph):
        raise TypeError(
            f"graph_to_role_graph expects MathProblemGraph, got {type(graph).__name__}"
        )

    preds: list[RolePredicate] = []

    for poss in graph.initial_state:
        preds.append(
            RolePredicate(
                kind="contain",
                args=(
                    RoleTerm(kind="entity", name=poss.entity),
                    RoleTerm(
                        kind="quantity",
                        name=f"q:{poss.entity}:{poss.quantity.unit}",
                        value=float(poss.quantity.value),
                        unit=poss.quantity.unit,
                    ),
                ),
            )
        )

    for op in graph.operations:
        if op.kind == "compare_multiplicative":
            assert isinstance(op.operand, Comparison)
            factor = float(op.operand.factor) if op.operand.factor is not None else None
            if factor is None:
                continue
            preds.append(
                RolePredicate(
                    kind="compare",
                    args=(
                        RoleTerm(kind="entity", name=op.actor),  # b
                        RoleTerm(kind="entity", name=op.operand.reference_actor),  # a
                        RoleTerm(
                            kind="quantity",
                            name="factor",
                            value=factor,
                            unit=None,
                        ),  # k
                    ),
                )
            )
        elif op.kind == "transfer":
            if not isinstance(op.operand, Quantity) or op.target is None:
                continue
            preds.append(
                RolePredicate(
                    kind="transfer",
                    args=(
                        RoleTerm(kind="entity", name=op.actor),
                        RoleTerm(kind="entity", name=op.target),
                        RoleTerm(
                            kind="quantity",
                            name=f"xfer:{op.actor}:{op.target}",
                            value=float(op.operand.value),
                            unit=op.operand.unit,
                        ),
                    ),
                )
            )
        elif op.kind == "apply_rate":
            if not isinstance(op.operand, Rate):
                continue
            preds.append(
                RolePredicate(
                    kind="rate",
                    args=(
                        RoleTerm(
                            kind="quantity",
                            name="rate_value",
                            value=float(op.operand.value),
                            unit=op.operand.numerator_unit,
                        ),
                        RoleTerm(kind="entity", name=op.actor),
                        RoleTerm(
                            kind="quantity",
                            name="rate_total_slot",
                            value=0.0,
                            unit=op.operand.numerator_unit,
                        ),
                    ),
                )
            )

    # Total query: unknown over all entities (sum) — S1 family signature.
    if graph.unknown.entity is None:
        unit = graph.unknown.unit
        holders = _entities_with_unit(graph, unit)
        if not holders:
            holders = list(graph.entities)
        part_terms = tuple(RoleTerm(kind="entity", name=e) for e in holders)
        sum_term = RoleTerm(
            kind="quantity",
            name="sum_query",
            value=0.0,  # unknown; placeholder attribute
            unit=unit,
        )
        preds.append(RolePredicate(kind="total", args=part_terms + (sum_term,)))

    ordered = tuple(_sort_predicates(preds))
    digest = hashlib.sha256(graph.canonical_bytes()).hexdigest()
    return RoleGraph(predicates=ordered, source_graph_hash=digest)


def _entities_with_unit(graph: MathProblemGraph, unit: str) -> list[str]:
    seen: list[str] = []
    for poss in graph.initial_state:
        if poss.quantity.unit == unit and poss.entity not in seen:
            seen.append(poss.entity)
    for op in graph.operations:
        if op.kind == "compare_multiplicative" and isinstance(op.operand, Comparison):
            # compare-defined entity inherits the reference unit; include actor
            if op.actor not in seen:
                seen.append(op.actor)
            if op.operand.reference_actor not in seen:
                seen.append(op.operand.reference_actor)
    return seen


def _sort_predicates(preds: Iterable[RolePredicate]) -> list[RolePredicate]:
    def key(p: RolePredicate) -> tuple:
        arg_key = tuple(
            (a.kind, a.name, a.value if a.value is not None else 0.0, a.unit or "")
            for a in p.args
        )
        return (p.kind, arg_key)

    return sorted(preds, key=key)
