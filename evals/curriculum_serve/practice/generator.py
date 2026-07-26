"""The curriculum practice corpus — one committed case per DISTINCT query atom.

ADR-0262 (curriculum-grounded serving) supplies the solver; ADR-0264 R9 supplies
the sizing rule. The corpus is enumerated, never authored: a band's case space is
exactly the set of exam questions that ROUTE to its subject and whose relation
falls in its family, so there is no hand-written gold to drift and nothing to
paraphrase-pad.

**Why enumeration is the honest shape here.** ``conservative_floor`` is a Wilson
bound and Wilson assumes independent trials, so a deterministic pipeline replaying
one input N times supplies one trial's evidence, not N (ADR-0264 R9). The
``deduction_serve`` producer sets a flat ``CASES_PER_BAND = 720`` and reaches it by
cycling a template x vocabulary space as small as 28 distinct instances; 21 of its
25 ratified bands therefore do not clear θ_SERVE on distinct evidence
(``tests/test_volume_honesty.py``). This producer cannot repeat that: its case
identity IS the query atom, so ``committed == distinct`` holds by construction
rather than by discipline. The model is ``evals/determination_estimation``
(660 distinct cases per class, zero repeats), which is what
``DIVISION-OF-WORK.md`` §4 directs Phase C to follow.

**Routability is asked, not re-derived.** An atom is in a band's space iff
``chat.curriculum_surface.resolve_domain`` routes its two terms to that subject.
Restating the predicate here would let the corpus and the serving path disagree
about which questions exist — so the corpus asks the serving path. This is not a
gold dependency: gold comes from ``evals.curriculum_serve.oracle``, which shares
no code with the serving path (ADR-0199 L-2).

Note that per-*term* exclusivity is a strictly tighter bound than the per-*pair*
predicate the router actually applies: a term taught in two subjects can still
appear in a pair that only one subject holds both halves of. Sizing a band from
exclusive terms therefore UNDER-counts its space — ``systems_software · causal``
reads as 630 under that bound and is really 720, which is the difference between
"cannot reach 657" and "can".

Determinism: no clock, no RNG. The atom space is sorted, selection is a fixed
stride, so ``all_gold_problems()`` is byte-stable across runs and the sealed
ledger is safe to commit and SHA-verify on load.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from chat.curriculum_surface import (
    SERVED_DOMAINS,
    CurriculumQuery,
    band_for,
    decide_curriculum_question,
    resolve_domain,
)
from core.learning_arena.protocols import BaseAttempt, DomainProblem, Problem
from evals.curriculum_serve.oracle import oracle_answer
from teaching.curriculum_premises import CONNECTIVE_FAMILY, FAMILIES, load_curriculum

#: Committed cases per band, when the band's atom space is larger than this.
#:
#: 660 is ``evals/determination_estimation``'s constant, chosen just above the 657
#: a perfect record needs to clear θ_SERVE=0.99 (``volume_for_theta(0.99)``). It is
#: a ceiling on *committed volume*, not a quota to be filled: a band whose space is
#: smaller emits its whole space and honestly reports a number below the floor.
CASES_PER_BAND = 660


@dataclass(frozen=True, slots=True)
class QueryAtom:
    """One distinct curriculum decision — the unit of committed evidence.

    The atom IS the decision key (ADR-0264 R9). Two cases with the same atom are
    the same decision replayed, so the corpus admits each atom at most once and
    :meth:`key` is what ``tests/test_volume_honesty.py`` audits.
    """

    domain: str
    family: str
    subject: str
    connective: str
    obj: str

    @property
    def text(self) -> str:
        """The exam question, in the closed ``Does <s> <v> <o>?`` grammar."""
        return f"Does {self.subject} {self.connective} {self.obj}?"

    @property
    def key(self) -> tuple[str, str, str, str]:
        """The distinct-decision key. Polarity is deliberately absent: a
        negative curriculum row (ADR-0264 R1-R4) changes a question's ANSWER,
        never its identity, and R4 rejects a corpus that states both polarities
        of one atom at ratification. So polarity cannot distinguish two cases."""
        return (self.domain, self.subject, self.connective, self.obj)

    @property
    def case_id(self) -> str:
        return f"{self.domain}:{self.connective}:{self.subject}->{self.obj}"


@lru_cache(maxsize=None)
def _routes_to(subject: str, obj: str) -> str | None:
    """The subject a term pair routes to, or ``None`` — the router's own answer."""
    domain = resolve_domain(CurriculumQuery(subject, "", obj))
    return domain if isinstance(domain, str) else None


@lru_cache(maxsize=None)
def routable_atoms(domain: str, family: str) -> tuple[QueryAtom, ...]:
    """Every exam question that reaches *(domain, family)*, in sorted order.

    The band's complete case space: ordered term pairs the router sends to
    *domain*, crossed with the family's connectives. Self-pairs are excluded —
    ``Does x cause x?`` is not a curriculum question any corpus states.
    """
    connectives = sorted(c for c, f in CONNECTIVE_FAMILY.items() if f == family)
    terms = sorted(load_curriculum(domain).vocabulary)
    atoms = [
        QueryAtom(domain, family, subject, connective, obj)
        for subject in terms
        for obj in terms
        if subject != obj and _routes_to(subject, obj) == domain
        for connective in connectives
    ]
    return tuple(sorted(atoms, key=lambda a: (a.subject, a.connective, a.obj)))


@lru_cache(maxsize=None)
def taught_atoms(domain: str, family: str) -> frozenset[tuple[str, str, str, str]]:
    """The atom keys a ratified chain states directly — the ``entailed`` class.

    Scarce by nature: a band has as many taught edges as the curriculum states,
    which is why ADR-0262 §5.1 makes authored volume the binding constraint on
    what a band can demonstrate beyond non-commitment.
    """
    return frozenset(
        QueryAtom(domain, family, c.subject, c.connective, c.obj).key
        for c in load_curriculum(domain).family(family)
    )


def band_cases(domain: str, family: str, cap: int = CASES_PER_BAND) -> tuple[QueryAtom, ...]:
    """The committed cases for one band — distinct atoms, at most *cap* of them.

    Whole space when it fits. Otherwise: every taught edge, then a fixed STRIDE
    across the remaining atoms in sorted order.

    The stride is deliberate rather than a prefix. A lexicographic prefix of 660
    atoms out of 45,300 would cover about five subject terms of 151, measuring one
    corner of the band and reporting it as the band; a stride spreads the sample
    across every subject the curriculum teaches. It is not a random sample — there
    is no RNG here — but it is an unbiased-by-construction one, and it cannot be
    tuned per band, which is the property that matters for an evidence artifact.
    Taught edges are force-included because they are the only committed-POSITIVE
    evidence a band has and a sample that missed them would report a band's
    reliability while exercising none of its content.
    """
    atoms = routable_atoms(domain, family)
    if len(atoms) <= cap:
        return atoms
    taught_keys = taught_atoms(domain, family)
    taught = [a for a in atoms if a.key in taught_keys]
    rest = [a for a in atoms if a.key not in taught_keys]
    need = max(cap - len(taught), 0)
    stride = max(len(rest) // need, 1) if need else 1
    picked = rest[::stride][:need]
    return tuple(sorted(taught + picked, key=lambda a: (a.subject, a.connective, a.obj)))


def practice_bands() -> tuple[tuple[str, str], ...]:
    """Every *(domain, family)* pair the ratified corpora actually populate.

    A family with no chains is not a band with zero volume — it is not a band.
    ``decide_curriculum_question`` refuses it ``empty_curriculum`` before any
    band key is assigned, so committing cases under one would invent a capability
    axis the serving path never uses.
    """
    return tuple(
        (domain, family)
        for domain in SERVED_DOMAINS
        for family in FAMILIES
        if load_curriculum(domain).family(family)
    )


def all_gold_problems(cap: int = CASES_PER_BAND) -> tuple[Problem, ...]:
    """The full practice corpus, every band, in a deterministic order."""
    problems: list[Problem] = []
    for domain, family in practice_bands():
        band = band_for(domain, family)
        for atom in band_cases(domain, family, cap):
            problems.append(
                Problem(problem_id=atom.case_id, class_name=band, payload=atom)
            )
    return tuple(problems)


class DuplicateAtom(AssertionError):
    """A band committed the same query atom twice — the R9 invariant, violated."""


def assert_practice_atoms_distinct(cap: int = CASES_PER_BAND) -> None:
    """``committed == distinct``, enforced at the producer (ADR-0264 R9).

    The Phase B audit MEASURES inflation; this refuses to emit it. Both matter:
    a producer that cannot pad is better than one that is caught padding, and the
    audit still guards the sealed artifact against a future producer change.
    """
    seen: dict[str, set[tuple[str, str, str, str]]] = {}
    for problem in all_gold_problems(cap):
        atom: QueryAtom = problem.payload
        keys = seen.setdefault(problem.class_name, set())
        if atom.key in keys:
            raise DuplicateAtom(
                f"{problem.class_name}: query atom {atom.key} committed twice — "
                "practice volume must be distinct evidence (ADR-0264 R9)"
            )
        keys.add(atom.key)


class CurriculumSolver:
    """The production decision path, under test (``chat/curriculum_surface.py``).

    ``committed`` is ``verdict != "declined"``. A typed refusal is an honest
    non-commitment, excluded from reliability's denominator (ADR-0175 §4) and
    counted as coverage — never conflated with a confabulation. That mapping is
    the same one ``evals/curriculum_serve/runner.py`` applies when it separates a
    ``declined`` mismatch from a ``wrong``.
    """

    domain_id = "curriculum_serve"

    def attempt(self, problem: DomainProblem) -> BaseAttempt:
        atom: QueryAtom = problem.payload
        decision = decide_curriculum_question(atom.text)
        committed = decision.verdict != "declined"
        return BaseAttempt(
            committed=committed,
            answer=decision.verdict,
            reason=decision.reason,
            case_id=problem.problem_id,
        )


class CurriculumOracleTether:
    """Tier-1 gold: the INDEPENDENT curriculum oracle (ADR-0199 L-2).

    ``evals/curriculum_serve/oracle.py`` shares no code with the serving path —
    its own loader, ratification predicate, family table, agreement normalization
    and verdict rule. Two independently written procedures agreeing on every atom
    is real evidence the serving path reads the curriculum correctly; a tether
    built from the compiler would only prove the compiler agrees with itself.
    """

    domain_id = "curriculum_serve"

    def is_correct(self, attempt: BaseAttempt, problem: DomainProblem) -> bool:
        return attempt.answer == self.gold_answer(problem)

    def gold_answer(self, problem: DomainProblem) -> str:
        atom: QueryAtom = problem.payload
        return oracle_answer(atom.domain, atom.subject, atom.connective, atom.obj).verdict


__all__ = [
    "CASES_PER_BAND",
    "CurriculumOracleTether",
    "CurriculumSolver",
    "DuplicateAtom",
    "QueryAtom",
    "all_gold_problems",
    "assert_practice_atoms_distinct",
    "band_cases",
    "practice_bands",
    "routable_atoms",
    "taught_atoms",
]
