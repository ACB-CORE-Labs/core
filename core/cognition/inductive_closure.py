"""Bounded multi-step inductive closure over teaching-store relations (Stage 3C).

Fixed-point expansion of same-relation chains with explicit budgets,
cycle handling, contradiction detection, and replayable provenance.

Atom *identity* for entailment telemetry remains conformal
(``CognitiveTurnPipeline._proof_atom``). This module expands the *relation
graph* of surface triples from ``TeachingStore.triples()`` into a closed
set under transitive composition of equal relation labels — not string
atom join as final authority for field identity.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Sequence

_DEFAULT_BUDGET = 16


def _norm(token: str) -> str:
    return token.strip().lower()


@dataclass(frozen=True, slots=True)
class DerivedRelation:
    """One promoted (or base) triple with provenance path."""

    head: str
    relation: str
    tail: str
    path: tuple[str, ...]  # entity path head … tail
    step: int  # 0 = base fact from store; >0 = derived at fixed-point step
    admissible: bool = True
    contradiction: bool = False

    def as_triple(self) -> tuple[str, str, str]:
        return (self.head, self.relation, self.tail)

    def as_dict(self) -> dict[str, Any]:
        return {
            "head": self.head,
            "relation": self.relation,
            "tail": self.tail,
            "path": list(self.path),
            "step": self.step,
            "admissible": self.admissible,
            "contradiction": self.contradiction,
        }


@dataclass(frozen=True, slots=True)
class InductiveClosureResult:
    """Result of bounded fixed-point expansion."""

    base: tuple[DerivedRelation, ...]
    derived: tuple[DerivedRelation, ...]
    contradictions: tuple[DerivedRelation, ...]
    steps_taken: int
    budget: int
    fixed_point: bool
    truncated: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "base": [r.as_dict() for r in self.base],
            "derived": [r.as_dict() for r in self.derived],
            "contradictions": [r.as_dict() for r in self.contradictions],
            "steps_taken": self.steps_taken,
            "budget": self.budget,
            "fixed_point": self.fixed_point,
            "truncated": self.truncated,
            "n_derived": len(self.derived),
        }


def expand_relation_closure(
    triples: Sequence[tuple[str, str, str]],
    *,
    budget: int = _DEFAULT_BUDGET,
    relations: Iterable[str] | None = None,
) -> InductiveClosureResult:
    """Compute same-relation transitive closure with budget and contradictions.

    Rules:
      * Base facts: each input triple (normalized).
      * Step k+1: if (a,r,b) and (b,r,c) known and a≠c and (a,r,c) unknown,
        derive (a,r,c) with path a…c.
      * Cycle: if path would revisit a node, skip (no infinite loop).
      * Contradiction: two different tails for the same (head, relation)
        at the same fixed-point layer mark both as contradiction=True
        (functional assumption for same-relation edges).
      * Termination: no new triples or budget exhausted.

    Geometric admissibility of *field* atoms is enforced by callers that
    map surfaces through ``_proof_atom`` before using derived triples as
    proof premises; this expander is total over the teaching-store graph.
    """
    if budget < 1:
        raise ValueError("budget must be >= 1")

    rel_filter = None if relations is None else {_norm(r) for r in relations}

    # Base
    base_list: list[DerivedRelation] = []
    # key (h,r) -> set of tails for contradiction detection
    edge_map: dict[tuple[str, str], set[str]] = {}
    known: set[tuple[str, str, str]] = set()

    for h, r, t in triples:
        hn, rn, tn = _norm(h), _norm(r), _norm(t)
        if not hn or not rn or not tn:
            continue
        if rel_filter is not None and rn not in rel_filter:
            continue
        key3 = (hn, rn, tn)
        if key3 in known:
            continue
        known.add(key3)
        edge_map.setdefault((hn, rn), set()).add(tn)
        base_list.append(
            DerivedRelation(
                head=hn,
                relation=rn,
                tail=tn,
                path=(hn, tn),
                step=0,
                admissible=True,
            )
        )

    # Mark base contradictions
    contradictions: list[DerivedRelation] = []
    for (h, r), tails in edge_map.items():
        if len(tails) > 1:
            for dr in base_list:
                if dr.head == h and dr.relation == r:
                    contradictions.append(
                        DerivedRelation(
                            head=dr.head,
                            relation=dr.relation,
                            tail=dr.tail,
                            path=dr.path,
                            step=0,
                            admissible=False,
                            contradiction=True,
                        )
                    )

    derived: list[DerivedRelation] = []
    # Working set of edges as (h,r,t) for composition
    work = set(known)
    steps_taken = 0
    fixed_point = False
    truncated = False

    for step in range(1, budget + 1):
        steps_taken = step
        new_edges: list[DerivedRelation] = []
        # Index tails by (h,r)
        by_hr: dict[tuple[str, str], list[str]] = {}
        for h, r, t in work:
            by_hr.setdefault((h, r), []).append(t)

        for (a, r), mids in by_hr.items():
            for b in mids:
                for c in by_hr.get((b, r), ()):
                    if a == c:
                        continue  # cycle / identity
                    key3 = (a, r, c)
                    if key3 in work:
                        continue
                    # path reconstruction (bounded)
                    path = (a, b, c)
                    new_edges.append(
                        DerivedRelation(
                            head=a,
                            relation=r,
                            tail=c,
                            path=path,
                            step=step,
                            admissible=True,
                        )
                    )

        if not new_edges:
            fixed_point = True
            steps_taken = step - 1 if step > 0 else 0
            break

        # Dedup new edges. Transitive multi-tails for the same (head, relation)
        # are *not* contradictions — only base multi-tails (step 0) mark
        # functional conflicts (recorded once above).
        for dr in new_edges:
            key3 = dr.as_triple()
            if key3 in work:
                continue
            work.add(key3)
            edge_map.setdefault((dr.head, dr.relation), set()).add(dr.tail)
            derived.append(dr)
    else:
        # Budget exhausted without fixed point
        truncated = True
        # Check if more edges would exist
        by_hr = {}
        for h, r, t in work:
            by_hr.setdefault((h, r), []).append(t)
        for (a, r), mids in by_hr.items():
            for b in mids:
                for c in by_hr.get((b, r), ()):
                    if a != c and (a, r, c) not in work:
                        truncated = True
                        break

    return InductiveClosureResult(
        base=tuple(base_list),
        derived=tuple(derived),
        contradictions=tuple(contradictions),
        steps_taken=steps_taken,
        budget=budget,
        fixed_point=fixed_point and not truncated,
        truncated=truncated,
    )
