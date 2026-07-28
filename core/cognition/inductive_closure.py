"""Bounded multi-step inductive closure over teaching-store relations (Stage 3C).

Fixed-point expansion of same-relation chains with explicit budgets,
cycle handling, contradiction detection, geometric admissibility, and
replayable provenance.

Atom *identity* for entailment telemetry remains conformal
(``CognitiveTurnPipeline._proof_atom``). This module expands the *relation
graph* of surface triples from ``TeachingStore.triples()`` into a closed
set under transitive composition of equal relation labels — not string
atom join as final identity authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable, Sequence

_DEFAULT_BUDGET = 16

# geometric_admissible(head, relation, tail) -> bool
GeometricAdmissibleFn = Callable[[str, str, str], bool]


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
            "n_admissible_derived": sum(1 for d in self.derived if d.admissible),
        }


def default_geometric_admissible(head: str, relation: str, tail: str) -> bool:
    """Strict default: a derived relation is admissible only if endpoints are
    non-empty distinct tokens and the relation is non-empty. Callers that
    have a vocab/field resolver should pass a stronger callback that checks
    closed Cl(4,1) versors (see pipeline wiring).
    """
    del relation
    h, t = head.strip(), tail.strip()
    return bool(h) and bool(t) and h != t


def expand_relation_closure(
    triples: Sequence[tuple[str, str, str]],
    *,
    budget: int = _DEFAULT_BUDGET,
    relations: Iterable[str] | None = None,
    geometric_admissible: GeometricAdmissibleFn | None = None,
) -> InductiveClosureResult:
    """Compute same-relation transitive closure with budget and contradictions.

    Rules:
      * Base facts: each input triple (normalized).
      * Step k+1: if (a,r,b) and (b,r,c) known and a≠c and (a,r,c) unknown,
        derive (a,r,c) with the witnessing path (a, b, c).
      * Termination is structural, not path-based: ``work`` grows
        monotonically over a finite triple set, so the fixed point is
        reached in at most ``budget`` steps.  The only skips are
        ``a == c`` (a self-edge is not a new fact) and a triple already
        in ``work``.  **No path-revisit check is performed, and none
        should be**: a witness path that revisits a node still proves a
        true transitive fact, so skipping on revisit would refuse sound
        derivations and leave the closure incomplete.  (H-8e, 2026-07-28
        — this rule previously read "Cycle: if path would revisit a
        node, skip", describing a check the code does not do and must
        not do.  The code was right; the sentence was wrong.)
      * ``path`` records the *witnessing* step, ``(head, mid, tail)``, not
        the full derivation ancestry: a depth-k edge names the one
        intermediate that produced it, whose own path names the next.
        Extending it to full ancestry would change ``as_dict`` output,
        and therefore ``operator_invocation`` and ``trace_hash`` — a
        trace-bytes change, not a docstring fix, and deliberately not
        made here.
      * Contradiction: two different tails for the same (head, relation)
        among base facts mark contradiction=True.
      * Geometric admissibility (Stage 3 exit gate): a candidate edge is
        *promoted* into the expansion frontier (``work``) and into
        ``derived`` **only** when ``geometric_admissible(h,r,t)`` is True.
        Non-admissible candidates are excluded — they must not seed further
        fixed-point steps (no ``admissible=False`` intermediates that still
        expand). Base store facts remain visible in ``base`` with their
        admissibility stamp, but only admissible base edges enter ``work``.
        Default requires non-empty distinct endpoints; pipeline supplies
        versor-grounded checks when session vocab is available.
      * Termination: no new triples or budget exhausted.
    """
    if budget < 1:
        raise ValueError("budget must be >= 1")

    geom = geometric_admissible or default_geometric_admissible
    rel_filter = None if relations is None else {_norm(r) for r in relations}

    base_list: list[DerivedRelation] = []
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
        # Base facts are store-grounded; admissible if geometric check passes.
        base_list.append(
            DerivedRelation(
                head=hn,
                relation=rn,
                tail=tn,
                path=(hn, tn),
                step=0,
                admissible=bool(geom(hn, rn, tn)),
            )
        )

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
    # Frontier is geometry-gated: non-admissible base never seeds expansion.
    work: set[tuple[str, str, str]] = {
        dr.as_triple() for dr in base_list if dr.admissible
    }
    steps_taken = 0
    fixed_point = False
    truncated = False

    for step in range(1, budget + 1):
        steps_taken = step
        new_edges: list[DerivedRelation] = []
        by_hr: dict[tuple[str, str], list[str]] = {}
        for h, r, t in work:
            by_hr.setdefault((h, r), []).append(t)

        for (a, r), mids in by_hr.items():
            for b in mids:
                for c in by_hr.get((b, r), ()):
                    if a == c:
                        continue
                    key3 = (a, r, c)
                    if key3 in work:
                        continue
                    # Promote only when geometrically admissible — never
                    # park an inadmissible edge in work to seed hop k+1.
                    if not bool(geom(a, r, c)):
                        continue
                    path = (a, b, c)
                    new_edges.append(
                        DerivedRelation(
                            head=a,
                            relation=r,
                            tail=c,
                            path=path,
                            step=step,
                            admissible=True,
                            contradiction=False,
                        )
                    )

        if not new_edges:
            fixed_point = True
            steps_taken = step - 1 if step > 0 else 0
            break

        for dr in new_edges:
            key3 = dr.as_triple()
            if key3 in work:
                continue
            work.add(key3)
            edge_map.setdefault((dr.head, dr.relation), set()).add(dr.tail)
            derived.append(dr)
    else:
        truncated = True
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
