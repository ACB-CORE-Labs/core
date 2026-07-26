"""The MeaningGraph <-> PropositionGraph projection this lane measures against.

CORE has two graph models and they are not type-compatible:

* ``MeaningGraph`` (reading) — ``Entity(entity_id, name, span, kind)`` plus
  ``Relation(predicate, arguments: tuple[str, ...], span, negated)``: n-ary
  predicate/argument structure carrying source spans.
* ``PropositionGraph`` (writing) — ``GraphNode(node_id, subject, predicate,
  obj, ...)`` plus ``GraphEdge(source, target, relation)``: fixed
  subject-predicate-object triples with rhetorical discourse edges.

A literal ``read(write(g)) == g`` is therefore not expressible.  This module
defines the projection both sides are compared *through*, and states plainly
what the projection discards.  Everything discarded here is a thing the lane
CANNOT see — that list is the honest limit of the measurement.

Deliberately discarded
----------------------
* **Discourse structure** — rhetorical moves, ``GraphEdge`` relations, and
  sentence order.  Two graphs whose propositions match but whose connectives
  differ project identically.
* **Spans** — ``MeaningSpan`` has no counterpart on the writing side.
* **Entity ``kind``** — the reading side infers ``individual``/``class``;
  the writing side has no slot for it.
* **Tense and aspect** — carried on ``ArticulationStep``, absent from
  ``Relation``.
* **Quantifier identity** — the reading side folds quantification INTO the
  predicate (``all`` -> ``subset``, ``no`` -> ``disjoint``, ``some`` ->
  ``intersects``); the writing side carries ``quantifier`` as a separate slot
  on the step.  The projection keeps the reading side's convention, so a
  writer graph's ``quantifier`` is visible only through
  :func:`quantifier_predicate`.
* **Relations of arity != 2** — the writing side cannot express them at all.

What it keeps
-------------
A frozenset of :class:`CanonicalProposition` — ``(predicate, subject, obj,
negated)``, lowercased and stripped.  Because the two sides do not share a
predicate vocabulary (the writer says ``flows``/``is_defined_as``; the reader
says ``subset``/``member``/``less``), the lane reports argument agreement and
predicate agreement **separately**.  A single match/no-match boolean would
hide exactly the distinction that decides this arc's next direction.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


#: Reading-side folding of a quantifier into a predicate name.  Mirrors
#: ``generate.meaning_graph.reader._QUANTIFIER_PREDICATE``; kept as a local
#: copy ON PURPOSE — this lane must not become a consumer of the thing it
#: measures, or a change to the reader would silently move the yardstick.
#: The duplication is asserted-equal by
#: ``tests/test_grammar_roundtrip.py::test_quantifier_map_matches_reader``,
#: which fails loudly if the reader's map changes.
_QUANTIFIER_PREDICATE: dict[str, str] = {
    "all": "subset",
    "no": "disjoint",
    "some": "intersects",
}


def quantifier_predicate(quantifier: str | None) -> str | None:
    """Reading-side predicate name for a writing-side *quantifier* slot."""
    if quantifier is None:
        return None
    return _QUANTIFIER_PREDICATE.get(quantifier.strip().lower())


@dataclass(frozen=True, slots=True, order=True)
class CanonicalProposition:
    """One binary proposition, normalized so both sides are comparable."""

    predicate: str
    subject: str
    obj: str
    negated: bool = False

    @property
    def args(self) -> tuple[str, str]:
        """The argument pair alone — predicate-vocabulary independent."""
        return (self.subject, self.obj)


def _norm(value: object) -> str:
    return str(value).strip().lower()


def from_meaning_graph(meaning_graph: Any) -> frozenset[CanonicalProposition]:
    """Project a ``MeaningGraph`` into canonical propositions.

    Relations of arity != 2 are dropped — the writing side cannot express
    them, so keeping them would make round-trip unachievable for a reason
    that has nothing to do with grammar.
    """
    out: set[CanonicalProposition] = set()
    for relation in getattr(meaning_graph, "relations", ()) or ():
        arguments = tuple(getattr(relation, "arguments", ()) or ())
        if len(arguments) != 2:
            continue
        out.add(
            CanonicalProposition(
                predicate=_norm(relation.predicate),
                subject=_norm(arguments[0]),
                obj=_norm(arguments[1]),
                negated=bool(getattr(relation, "negated", False)),
            )
        )
    return frozenset(out)


def from_proposition_graph(
    graph: Any, target: Any = None
) -> frozenset[CanonicalProposition]:
    """Project a ``PropositionGraph`` (+ optional target) into canonicals.

    ``target`` supplies the per-step ``negated`` / ``quantifier`` slots, which
    live on ``ArticulationStep`` rather than on ``GraphNode``.  When a step
    carries a quantifier that the reading side folds into a predicate, the
    folded name is used so the two sides are comparable at all.
    """
    steps_by_id: dict[str, Any] = {}
    for step in getattr(target, "steps", ()) or ():
        steps_by_id[step.node_id] = step

    out: set[CanonicalProposition] = set()
    for node in getattr(graph, "nodes", ()) or ():
        step = steps_by_id.get(node.node_id)
        negated = bool(getattr(step, "negated", False)) if step else False
        quantifier = getattr(step, "quantifier", None) if step else None
        folded = quantifier_predicate(quantifier)
        out.add(
            CanonicalProposition(
                predicate=folded or _norm(node.predicate),
                subject=_norm(node.subject),
                obj=_norm(node.obj),
                negated=negated,
            )
        )
    return frozenset(out)


@dataclass(frozen=True, slots=True)
class Agreement:
    """How well two canonical-proposition sets agree, decomposed.

    The decomposition is the point.  ``args_match`` says the *structure*
    survived the round-trip; ``predicates_match`` says the two sides also
    agree on what to CALL the relation.  A high ``args_match`` with a low
    ``predicates_match`` means the grammars are aligned and only the
    vocabulary is split — a very different remedy from both being low.
    """

    expected: int
    actual: int
    args_match: int
    predicates_match: int
    exact_match: int

    @property
    def args_rate(self) -> float:
        return self.args_match / self.expected if self.expected else 0.0

    @property
    def predicates_rate(self) -> float:
        return self.predicates_match / self.expected if self.expected else 0.0

    @property
    def exact_rate(self) -> float:
        return self.exact_match / self.expected if self.expected else 0.0

    def as_dict(self) -> dict[str, object]:
        return {
            "expected": self.expected,
            "actual": self.actual,
            "args_match": self.args_match,
            "predicates_match": self.predicates_match,
            "exact_match": self.exact_match,
            "args_rate": round(self.args_rate, 6),
            "predicates_rate": round(self.predicates_rate, 6),
            "exact_rate": round(self.exact_rate, 6),
        }


def compare(
    expected: frozenset[CanonicalProposition],
    actual: frozenset[CanonicalProposition],
) -> Agreement:
    """Compare two canonical sets, decomposed by argument vs predicate."""
    actual_args = {p.args for p in actual}
    args_match = sum(1 for p in expected if p.args in actual_args)
    # A predicate only counts as agreeing when it agrees ON THE SAME
    # arguments — a shared predicate name over different arguments is not
    # recovery, and counting it would inflate the rate.
    predicates_match = sum(
        1
        for p in expected
        if any(a.predicate == p.predicate and a.args == p.args for a in actual)
    )
    exact_match = len(expected & actual)
    return Agreement(
        expected=len(expected),
        actual=len(actual),
        args_match=args_match,
        predicates_match=predicates_match,
        exact_match=exact_match,
    )


__all__ = (
    "Agreement",
    "CanonicalProposition",
    "compare",
    "from_meaning_graph",
    "from_proposition_graph",
    "quantifier_predicate",
)
