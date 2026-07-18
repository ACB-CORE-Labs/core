"""evals.logic_cnf_compiler — structural formula → CNF PropositionalProblem (ADR-0249 P3).

Closes the deduction leg of the reader→Hamiltonian compiler: turns propositional
formula strings (as emitted by ``generate.meaning_graph.to_deductive_logic``, or
any ``logic_canonical``-parseable syntax) into the corridor's CNF
``PropositionalProblem`` plus a query ``Clause``, consumable by
``propositional_entails``.

Structural, not truth-table (spike §4.1): the formula is parsed with the
production ROBDD parser (``generate.logic_canonical`` — reused, never
re-implemented), then rewritten to CNF by the standard sound transform —
eliminate iff/implies, push negations to the literals (NNF), distribute OR over
AND — with constant folding, tautological-clause elimination, and a clause
budget. Equivalence to the source is provable against the ROBDD oracle
(``canonicalize``) and is pinned in tests. The converter never enumerates
assignments and never decides satisfiability or entailment — that is the
corridor's job; this only compiles the constraint shape.

Off-serving (A-04): imports the serving-side logic parser for its grammar only,
lives in the eval quarantine, and is never imported by ``chat/runtime.py``.
"""
from __future__ import annotations

from collections.abc import Sequence

from core.physics.cognitive_lifecycle import Clause, PropositionalProblem
from generate.logic_canonical import (
    _Parser,
    _reject_out_of_regime_text,
    _reject_out_of_regime_tokens,
    _tokenize,
)

__all__ = [
    "CnfCompileError",
    "formula_to_clauses",
    "query_to_clause",
    "compile_entailment",
    "clauses_to_formula",
]

# CNF as a frozenset of clauses; a clause is a frozenset of ``(atom, polarity)``
# literals. Two sentinels: TRUE = no clauses (empty conjunction); FALSE = one
# empty clause (an unsatisfiable disjunction).
_TRUE: frozenset = frozenset()
_FALSE: frozenset = frozenset({frozenset()})
_CLAUSE_BUDGET = 512


class CnfCompileError(ValueError):
    """Typed, fail-closed refusal for CNF compilation (spike §4.3).

    Parse/regime failures propagate as ``logic_canonical.LogicError`` /
    ``LogicRegimeError``; atom-count and structural violations surface as the
    corridor's ``HamiltonianCompileError`` when the ``PropositionalProblem`` is
    built. This type covers the CNF-specific refusals only.
    """

    def __init__(self, reason: str, **disclosure: object) -> None:
        self.reason = reason
        self.disclosure = disclosure
        detail = ", ".join(f"{k}={v!r}" for k, v in disclosure.items())
        super().__init__(f"{reason}({detail})" if detail else reason)


def _parse(formula: str):
    """Mirror ``canonicalize``'s refusal-first front-matter, returning the AST."""
    _reject_out_of_regime_text(formula)
    tokens = _tokenize(formula)
    _reject_out_of_regime_tokens(tokens)
    return _Parser(tokens).parse()


def _eliminate(ast: tuple) -> tuple:
    """Remove ``iff`` and ``implies`` in favour of ``and``/``or``/``not``."""
    kind = ast[0]
    if kind == "iff":
        a, b = _eliminate(ast[1]), _eliminate(ast[2])
        return ("and", ("or", ("not", a), b), ("or", ("not", b), a))
    if kind == "implies":
        return ("or", ("not", _eliminate(ast[1])), _eliminate(ast[2]))
    if kind in ("and", "or"):
        return (kind, _eliminate(ast[1]), _eliminate(ast[2]))
    if kind == "not":
        return ("not", _eliminate(ast[1]))
    return ast  # atom / const


def _nnf(ast: tuple) -> tuple:
    """Push negations inward until they sit only on atoms (De Morgan)."""
    kind = ast[0]
    if kind == "not":
        inner = ast[1]
        ik = inner[0]
        if ik == "not":
            return _nnf(inner[1])
        if ik == "and":
            return ("or", _nnf(("not", inner[1])), _nnf(("not", inner[2])))
        if ik == "or":
            return ("and", _nnf(("not", inner[1])), _nnf(("not", inner[2])))
        if ik == "const":
            return ("const", not inner[1])
        if ik == "atom":
            return ("not", inner)
        raise CnfCompileError("unparseable_negation", node=ik)
    if kind in ("and", "or"):
        return (kind, _nnf(ast[1]), _nnf(ast[2]))
    return ast  # atom / const


def _is_tautological(clause: frozenset) -> bool:
    return any((atom, True) in clause and (atom, False) in clause for atom, _ in clause)


def _to_cnf(ast: tuple) -> frozenset:
    """NNF AST → frozenset of clauses (constant-folded, tautologies dropped)."""
    kind = ast[0]
    if kind == "atom":
        return frozenset({frozenset({(ast[1], True)})})
    if kind == "not":  # NNF guarantees the operand is an atom
        return frozenset({frozenset({(ast[1][1], False)})})
    if kind == "const":
        return _TRUE if ast[1] else _FALSE
    left, right = _to_cnf(ast[1]), _to_cnf(ast[2])
    if kind == "and":
        if left == _FALSE or right == _FALSE:
            return _FALSE
        merged = left | right
        if len(merged) > _CLAUSE_BUDGET:
            raise CnfCompileError("cnf_budget_exceeded", clauses=len(merged))
        return frozenset(merged)
    if kind == "or":
        if left == _TRUE or right == _TRUE:
            return _TRUE
        if left == _FALSE:
            return right
        if right == _FALSE:
            return left
        out: set[frozenset] = set()
        for clause_a in left:
            for clause_b in right:
                combined = clause_a | clause_b
                if _is_tautological(combined):
                    continue  # always-true clause drops from the conjunction
                out.add(combined)
                if len(out) > _CLAUSE_BUDGET:
                    raise CnfCompileError("cnf_budget_exceeded", clauses=len(out))
        return frozenset(out) if out else _TRUE
    raise CnfCompileError("unparseable_node", node=kind)


def _sorted_clause(clause: frozenset) -> Clause:
    return tuple(sorted(clause))


def _cnf_of(formula: str) -> frozenset:
    return _to_cnf(_nnf(_eliminate(_parse(formula))))


def formula_to_clauses(formula: str) -> tuple[Clause, ...]:
    """Structural CNF of ``formula`` as a deterministic tuple of clauses.

    A tautological formula yields ``()`` (no constraints); a formula that
    reduces to ``false`` is refused (it cannot be a corridor clause set).
    """
    cnf = _cnf_of(formula)
    if cnf == _FALSE:
        raise CnfCompileError("formula_reduces_to_false", formula=formula)
    if cnf == _TRUE:
        return ()
    return tuple(sorted((_sorted_clause(c) for c in cnf)))


def query_to_clause(query: str) -> Clause:
    """A query must reduce to a single clause (a disjunction of literals).

    That is exactly the shape ``propositional_entails`` negates into unit
    clauses. Conjunctive or constant queries are refused.
    """
    cnf = _cnf_of(query)
    if cnf in (_TRUE, _FALSE):
        raise CnfCompileError("query_reduces_to_constant", query=query, value=(cnf == _TRUE))
    if len(cnf) != 1:
        raise CnfCompileError("query_not_single_clause", query=query, clause_count=len(cnf))
    return _sorted_clause(next(iter(cnf)))


def compile_entailment(
    premises: Sequence[str], query: str
) -> tuple[PropositionalProblem, Clause]:
    """Compile ``premises ⊨ query`` into a corridor ``(PropositionalProblem, Clause)``.

    Run the result through ``propositional_entails`` to decide it. Raises
    ``HamiltonianCompileError`` (``atom_count_out_of_range``) when the shared
    atom set exceeds the corridor's ≤5-atom envelope — the honest boundary.
    """
    premise_clauses: tuple[Clause, ...] = tuple(
        clause for formula in premises for clause in formula_to_clauses(formula)
    )
    query_clause = query_to_clause(query)
    atoms = sorted(
        {atom for clause in premise_clauses for atom, _ in clause}
        | {atom for atom, _ in query_clause}
    )
    problem = PropositionalProblem(atoms=tuple(atoms), clauses=premise_clauses)
    return problem, query_clause


def clauses_to_formula(clauses: Sequence[Clause]) -> str:
    """Render CNF clauses to a ``logic_canonical``-parseable string (``&``/``|``/``~``).

    Round-trips with ``formula_to_clauses`` under the ROBDD identity; ``()``
    (a tautology) renders to ``true``.
    """
    if not clauses:
        return "true"
    rendered = [
        "(" + " | ".join(atom if pol else f"~{atom}" for atom, pol in clause) + ")"
        for clause in clauses
    ]
    return " & ".join(rendered)
