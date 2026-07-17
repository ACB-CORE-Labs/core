"""ADR-0243 Phase 4 — decisive falsifier: field relaxation decoder vs ROBDD gold.

The propositional slice of ADR-0243's falsifiability benchmark (plan §5 Phase 4).
Two independent engines decide the SAME propositional entailment problems:

* **Field decoder** — :func:`core.physics.cognitive_lifecycle.propositional_entails`
  reads the ground energy of a Cl(4,1) wave field relaxed on a diagonal penalty
  Hamiltonian (ADR-0243 §2.2). ``entailed`` ⇔ ``premises ∧ ¬conclusion`` has
  ground energy > 0 (UNSAT).
* **Gold** — :func:`generate.proof_chain.entail.evaluate_entailment` decides
  ``(⋀premises) → query`` by an exact ROBDD tautology check (ADR-0201 keystone).
  A canonical, complete, mechanism-disjoint decision procedure.

The bridge renders each CNF clause to the gold's formula syntax (``a | ~b | c``;
premises are one string per clause) so both engines decide byte-for-byte the same
problem, and the gold is genuinely independent — not the field decoder checking
itself.

**What wrong == 0 means (plan's decisive falsifier).** On the satisfiable-premise
panel the two verdicts are directly comparable: ``field.entailed`` ⇔
``gold.outcome is ENTAILED``. A single divergence confirms *"the field engine is
NOT the reasoner today"* on this domain; zero divergence over the panel is the
evidence that the decode-not-generate thesis holds on checkable propositional
logic. Inconsistent premises are handled honestly, not swept under the rug: the
field decoder discloses ``satisfiable_premises=False`` (vacuous ex-falso
entailment) exactly where the gold returns ``REFUSED`` — a matched refusal, not a
disagreement. Out-of-regime problems (> 5 atoms) are where the field decoder
*refuses* by construction while the gold still decides — the honest ID/OOD scope
boundary, in the propositional domain.

Off-serving: lives under ``evals/`` only; never imported by ``chat/runtime.py``.
Deterministic: the panel is enumerated (no wall-clock, no unseeded randomness).
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import Any, Iterator, Sequence

from core.physics.cognitive_lifecycle import (
    HamiltonianCompileError,
    PropositionalProblem,
    propositional_entails,
)
from generate.proof_chain.entail import Entailment, evaluate_entailment

# A CNF clause: disjunction of (atom, polarity) literals — the shape
# ``PropositionalProblem.clauses`` and ``propositional_entails``'s conclusion
# both accept. Defined locally rather than importing the module's non-exported
# ``Clause`` alias.
Clause = tuple[tuple[str, bool], ...]

__all__ = [
    "FalsifierCase",
    "render_clause",
    "run_propositional_falsifier",
]


def render_clause(clause: Clause) -> str:
    """Render a CNF clause (disjunction of literals) in the gold's syntax.

    ``(("a", True), ("b", False))`` → ``"a | ~b"``. A single literal renders
    bare (``"a"`` / ``"~a"``); the ROBDD parser treats ``|`` as OR, ``~`` as NOT.
    """
    if not clause:
        raise ValueError("render_clause: empty clause has no propositional meaning")
    return " | ".join(atom if polarity else f"~{atom}" for atom, polarity in clause)


def _premise_strings(problem: PropositionalProblem) -> tuple[str, ...]:
    return tuple(render_clause(c) for c in problem.clauses)


@dataclass(frozen=True, slots=True)
class FalsifierCase:
    """One field-vs-gold comparison record (JSON-safe via :meth:`as_dict`)."""

    premises: tuple[str, ...]
    conclusion: str
    field_entailed: bool
    field_premises_satisfiable: bool
    gold_outcome: str
    gold_reason: str
    lane: str  # "id" | "refusal_parity"
    agree: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "premises": list(self.premises),
            "conclusion": self.conclusion,
            "field_entailed": self.field_entailed,
            "field_premises_satisfiable": self.field_premises_satisfiable,
            "gold_outcome": self.gold_outcome,
            "gold_reason": self.gold_reason,
            "lane": self.lane,
            "agree": self.agree,
        }


def _atom_literals(atoms: Sequence[str]) -> list[Clause]:
    """All 1- and 2-literal clauses over ``atoms`` (a 2-literal clause never
    repeats an atom — that would be a tautological or contradictory clause the
    field compiler rejects as a duplicate literal)."""
    singles: list[Clause] = [((a, p),) for a in atoms for p in (True, False)]
    pairs: list[Clause] = []
    for a, b in itertools.combinations(atoms, 2):
        for pa in (True, False):
            for pb in (True, False):
                pairs.append(((a, pa), (b, pb)))
    return singles + pairs


def _enumerate_problems(
    atoms: tuple[str, ...],
    *,
    max_clauses: int,
) -> Iterator[tuple[PropositionalProblem, Clause]]:
    """Deterministically enumerate (problem, conclusion) pairs over ``atoms``.

    Premise sets are size 1..``max_clauses`` combinations of the atom clauses;
    the conclusion ranges over every single literal. Order is fully determined
    by ``itertools`` iteration over the sorted atom clauses — no randomness.
    """
    clauses = _atom_literals(atoms)
    conclusions: list[Clause] = [((a, p),) for a in atoms for p in (True, False)]
    for size in range(1, max_clauses + 1):
        for premise_combo in itertools.combinations(clauses, size):
            problem = PropositionalProblem(atoms=atoms, clauses=tuple(premise_combo))
            for conclusion in conclusions:
                yield problem, conclusion


def run_propositional_falsifier(
    *,
    atoms: tuple[str, ...] = ("a", "b", "c"),
    max_clauses: int = 2,
    ood_atoms: tuple[str, ...] = ("a", "b", "c", "d", "e", "f"),
) -> dict[str, Any]:
    """Score the field decoder against the ROBDD gold; return a JSON-safe artifact.

    ``wrong`` counts ID-lane divergences (``field.entailed`` ≠
    ``gold is ENTAILED`` on satisfiable premises) plus refusal-parity mismatches
    (inconsistent premises where the field failed to disclose unsatisfiable
    premises, or the gold did not refuse). ``ood_field_refused`` records that a
    > 5-atom problem is rejected by the field decoder (out of its exact regime)
    while remaining decidable for the gold.
    """
    id_cases: list[FalsifierCase] = []
    refusal_cases: list[FalsifierCase] = []
    wrong = 0

    for problem, conclusion in _enumerate_problems(atoms, max_clauses=max_clauses):
        field = propositional_entails(problem, conclusion)
        gold = evaluate_entailment(_premise_strings(problem), render_clause(conclusion))

        if gold.outcome is Entailment.REFUSED:
            # Gold refuses only on inconsistent premises here (input is always
            # in-regime propositional). The field decoder must disclose the same
            # via satisfiable_premises=False rather than assert real entailment.
            agree = field.satisfiable_premises is False
            refusal_cases.append(
                FalsifierCase(
                    premises=_premise_strings(problem),
                    conclusion=render_clause(conclusion),
                    field_entailed=field.entailed,
                    field_premises_satisfiable=field.satisfiable_premises,
                    gold_outcome=gold.outcome.value,
                    gold_reason=gold.reason,
                    lane="refusal_parity",
                    agree=agree,
                )
            )
            if not agree:
                wrong += 1
            continue

        # Satisfiable-premise ID lane: field.entailed ⇔ gold is ENTAILED.
        gold_entailed = gold.outcome is Entailment.ENTAILED
        agree = field.entailed == gold_entailed
        id_cases.append(
            FalsifierCase(
                premises=_premise_strings(problem),
                conclusion=render_clause(conclusion),
                field_entailed=field.entailed,
                field_premises_satisfiable=field.satisfiable_premises,
                gold_outcome=gold.outcome.value,
                gold_reason=gold.reason,
                lane="id",
                agree=agree,
            )
        )
        if not agree:
            wrong += 1

    # OOD: > 5 atoms is outside the field decoder's exact ≤ 32-assignment regime.
    # It must refuse (typed) rather than guess; the gold still decides.
    ood_field_refused = False
    ood_gold_decided = False
    ood_conclusion: Clause = ((ood_atoms[0], True),)
    ood_clauses: tuple[Clause, ...] = tuple(((a, True),) for a in ood_atoms)
    try:
        PropositionalProblem(atoms=ood_atoms, clauses=ood_clauses)
    except HamiltonianCompileError:
        ood_field_refused = True
    ood_gold = evaluate_entailment(
        tuple(render_clause(c) for c in ood_clauses), render_clause(ood_conclusion)
    )
    ood_gold_decided = ood_gold.outcome is not Entailment.REFUSED

    return {
        "wrong": wrong,
        "id_case_count": len(id_cases),
        "id_disagreements": [c.as_dict() for c in id_cases if not c.agree],
        "refusal_parity_count": len(refusal_cases),
        "refusal_parity_mismatches": [c.as_dict() for c in refusal_cases if not c.agree],
        "ood_field_refused": ood_field_refused,
        "ood_gold_decided": ood_gold_decided,
        "atoms": list(atoms),
        "max_clauses": max_clauses,
    }
