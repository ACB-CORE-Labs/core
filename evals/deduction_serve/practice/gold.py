"""Practice gold lane for the deduction-serve arc (Phase 3, ADR-0256).

The second concrete instance of the ADR-0199 cross-domain learning arena
(GSM8K math is the first). It measures the FULL serving pipeline
(reader → projector → ROBDD engine) per propositional shape-band, so the
reliability gate can earn a per-band SERVE license.

What is measured (and why it is not circular): the ROBDD engine is
sound+complete by construction — it is never wrong on the problem it is
given. The FALLIBLE part is the reader/projector: a template-based reader
can misparse a natural-language argument and hand the engine the *wrong*
problem, which it then soundly decides — a wrong served answer. This arena's
gold is authored **by construction** from the template that generated each
case (independent of the reader — ADR-0199 L-2), so a misread is caught as a
``wrong``. A band earns SERVE only when the whole pipeline reads AND decides
that shape correctly at volume.

Deterministic + synthetic: atoms are indexed (``no clock, no randomness``);
each band mixes entailed/refuted/unknown gold so reliability measures decision
correctness across outcomes, not just how many entailments pass through.

Sized to the SERVE volume floor: a perfect record clears θ_SERVE=0.99 only at
``n/(n+z²) ≥ 0.99`` (z=2.576) ⇒ ``n ≥ 657`` committed. ``CASES_PER_BAND``
exceeds that so each in-band shape earns the license honestly by volume.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from core.learning_arena.protocols import Problem
from generate.meaning_graph.projectors import to_deductive_logic
from generate.meaning_graph.reader import Comprehension, comprehend
from generate.proof_chain.entail import Entailment, evaluate_entailment_with_trace
from generate.proof_chain.shape import (
    ATOMIC,
    CONDITIONAL_CHAIN,
    CONDITIONAL_SINGLE,
    DISJUNCTIVE,
    classify_deduction_shape,
)

_DOMAIN_ID = "deductive_logic_serve"

#: Cases per shape-band. ≥657 lets a perfect record clear the θ_SERVE=0.99
#: Wilson floor; a comfortable margin above it so the earned license is
#: unambiguous. Split across the band's gold-outcome templates.
CASES_PER_BAND = 720

#: A deterministic pool of single-token, non-reserved, identifier-safe atom
#: names. Indexed selection varies the argument per case (distinct problems),
#: with no clock/RNG. Three distinct atoms per case is always enough for the
#: templates below.
_ATOM_POOL: tuple[str, ...] = tuple(f"x{i}" for i in range(3, 300))


def _atoms(index: int, count: int) -> tuple[str, ...]:
    """``count`` distinct atoms for case ``index`` — deterministic, no overlap."""
    base = (index * 3) % (len(_ATOM_POOL) - count)
    return tuple(_ATOM_POOL[base + j] for j in range(count))


#: Each band's gold templates: (gold_outcome, text_builder). A builder takes the
#: distinct atoms and returns the natural-language argument text. Every template's
#: gold is TRUE BY CONSTRUCTION — the logical form guarantees it, verified against
#: the independent oracle at generation time (see ``_assert_sound`` below).
_TEMPLATES: dict[str, tuple[tuple[str, Any], ...]] = {
    CONDITIONAL_SINGLE: (
        ("entailed", lambda a, b, c: f"If {a} then {b}. {a}. Therefore {b}."),
        ("refuted", lambda a, b, c: f"If {a} then {b}. {a}. Therefore not {b}."),
        ("unknown", lambda a, b, c: f"If {a} then {b}. Therefore {a}."),
    ),
    CONDITIONAL_CHAIN: (
        ("entailed", lambda a, b, c: f"If {a} then {b}. If {b} then {c}. {a}. Therefore {c}."),
        ("refuted", lambda a, b, c: f"If {a} then {b}. If {b} then {c}. {a}. Therefore not {c}."),
        ("unknown", lambda a, b, c: f"If {a} then {b}. If {b} then {c}. Therefore {c}."),
    ),
    DISJUNCTIVE: (
        ("entailed", lambda a, b, c: f"{a} or {b}. Not {a}. Therefore {b}."),
        ("refuted", lambda a, b, c: f"{a} or {b}. Not {a}. Therefore {a}."),
        ("unknown", lambda a, b, c: f"{a} or {b}. Therefore {a}."),
    ),
    ATOMIC: (
        ("entailed", lambda a, b, c: f"{a}. Therefore {a}."),
        ("refuted", lambda a, b, c: f"{a}. Therefore not {a}."),
        # No genuine 'unknown' atomic argument exists over a single premise
        # (a bare atom either restates or contradicts); the band is 2/3 the size
        # of the others, still well above the volume floor.
    ),
}


def generate_problems(band: str, n: int) -> list[Problem]:
    """``n`` synthetic problems for ``band``, cycling its gold templates.

    Deterministic: problem ``i`` uses template ``i % len(templates)`` and atoms
    ``_atoms(i, 3)``. Each ``payload`` carries the raw ``text`` and the
    by-construction ``gold`` the tether scores against.
    """
    templates = _TEMPLATES[band]
    problems: list[Problem] = []
    for i in range(n):
        gold, builder = templates[i % len(templates)]
        a, b, c = _atoms(i, 3)
        text = builder(a, b, c)
        problems.append(
            Problem(
                problem_id=f"{band}-{i:04d}",
                class_name=band,
                payload={"text": text, "gold": gold},
            )
        )
    return problems


def all_gold_problems() -> list[Problem]:
    """The full deterministic corpus over every shape-band, in band order."""
    problems: list[Problem] = []
    for band in (CONDITIONAL_SINGLE, CONDITIONAL_CHAIN, DISJUNCTIVE, ATOMIC):
        problems.extend(generate_problems(band, CASES_PER_BAND))
    return problems


# --- the ADR-0199 DomainSolver / GoldTether for deduction serving -------------


@dataclass(frozen=True, slots=True)
class _DeductionAttempt:
    committed: bool
    answer: Any  # the outcome class the pipeline decided, or None on decline
    reason: str
    case_id: str
    shape: str
    derivations: tuple[Any, ...] = field(default_factory=tuple)
    trace_sha256: str = ""


_OUTCOME_TO_CLASS = {
    Entailment.ENTAILED: "entailed",
    Entailment.REFUTED: "refuted",
    Entailment.UNKNOWN: "unknown",
    Entailment.REFUSED: "declined",
}


@dataclass(frozen=True, slots=True)
class DeductionSolver:
    """The production serving pipeline as a ``DomainSolver``.

    Runs exactly what ``chat/deduction_surface.py`` runs — ``comprehend`` →
    ``to_deductive_logic`` → ``evaluate_entailment_with_trace`` — and commits
    the decided outcome class. A reader refusal / non-projectable comprehension
    is an uncommitted attempt (``refused``), never a guessed answer.
    """

    domain_id: str = _DOMAIN_ID

    def attempt(self, problem: Problem) -> _DeductionAttempt:
        text = problem.payload["text"]
        comp = comprehend(text)
        if not isinstance(comp, Comprehension):
            return _DeductionAttempt(
                committed=False, answer=None, reason=f"reader:{getattr(comp, 'reason', '')}",
                case_id=problem.problem_id, shape=problem.class_name,
            )
        projected = to_deductive_logic(comp)
        if projected is None:
            return _DeductionAttempt(
                committed=False, answer=None, reason="unprojectable",
                case_id=problem.problem_id, shape=problem.class_name,
            )
        premises, query = projected
        outcome = evaluate_entailment_with_trace(premises, query).outcome
        answer = _OUTCOME_TO_CLASS[outcome]
        # An engine REFUSED (inconsistent premises / out-of-regime) is an honest
        # non-commitment, not a served verdict.
        committed = outcome is not Entailment.REFUSED
        return _DeductionAttempt(
            committed=committed, answer=answer, reason="",
            case_id=problem.problem_id, shape=classify_deduction_shape(premises, query),
        )


@dataclass(frozen=True, slots=True)
class ConstructionGoldTether:
    """Scores the pipeline's committed outcome against the by-construction gold.

    The gold lives in ``problem.payload["gold"]`` — authored by the generating
    template's logical form, independent of the reader (ADR-0199 L-2). A pipeline
    that misreads the text and decides a different outcome is scored ``wrong``.
    """

    domain_id: str = _DOMAIN_ID

    def is_correct(self, attempt: _DeductionAttempt, problem: Problem) -> bool:
        return bool(attempt.committed) and attempt.answer == problem.payload["gold"]

    def gold_answer(self, problem: Problem) -> str:
        return str(problem.payload["gold"])


def assert_corpus_sound() -> None:
    """Belt-and-suspenders: every generated case's by-construction gold must
    agree with the INDEPENDENT truth-table oracle over its projected form.

    Guards against a template authoring bug (a mis-stated gold) silently
    inflating the ledger. Raises ``AssertionError`` on any disagreement. Uses
    the oracle (``evals.deductive_logic.oracle``), which shares no code with the
    ROBDD serving engine (INV-25), as the construction-time check.
    """
    from evals.deductive_logic.oracle import oracle_entailment

    for problem in all_gold_problems():
        comp = comprehend(problem.payload["text"])
        assert isinstance(comp, Comprehension), problem.payload["text"]
        projected = to_deductive_logic(comp)
        assert projected is not None, problem.payload["text"]
        premises, query = projected
        oracle = oracle_entailment(premises, query)
        assert oracle == problem.payload["gold"], (
            f"{problem.problem_id}: oracle={oracle} gold={problem.payload['gold']} "
            f"text={problem.payload['text']!r}"
        )


__all__ = [
    "CASES_PER_BAND",
    "ConstructionGoldTether",
    "DeductionSolver",
    "all_gold_problems",
    "assert_corpus_sound",
    "generate_problems",
]
