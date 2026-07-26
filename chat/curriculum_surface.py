"""chat/curriculum_surface.py — CURRICULUM composer (generalization arc Phase 2).

The second question shape of the curriculum-entailment gold contract
(docs/plans/generalization-arc-2026-07-24.md §4.2b): an exam question that
supplies only the QUERY — "Does force cause acceleration?" — answered from the
ratified curriculum of the subject it is about, and from nothing else.

The decision is made by the SAME argument bands the deduction composer uses
(ADR-0256…0261). This module compiles ratified chains into premise sentences,
appends the question as a "Therefore …" conclusion, and hands the assembled
argument to `deduction_grounded_surface`'s decider. There is no subject-
specific reasoning code anywhere in this path — physics differs from
philosophy only in which curriculum rows load, which is what makes "port the
lifecycle to a new subject" a data operation rather than an engineering one.

Why an UNTAUGHT fact is UNKNOWN and never "no": the curriculum is read
OPEN-world. "The curriculum does not teach it" is not "it is false", and a
system that decoded the former into the latter would be inventing negative
knowledge it was never given. The only verdicts reachable from a purely
positive curriculum are therefore ENTAILED and UNKNOWN — a real limit of the
present corpora, recorded in ADR-0262 §5 rather than papered over.

Fail-closed (INV-34) BEHIND A NARROW GATE: once `is_curriculum_question` fires,
every path below returns a committed, honest surface — typed refusal or decided
verdict — never a silent fall-through. The gate itself is deliberately narrow
(routable, not merely `Does …?`-shaped): shape alone is not a signal of intent
for a polar question, so claiming every one of them would hijack ordinary turns.
See :func:`is_curriculum_question`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable

from chat.curriculum_serve_license import curriculum_serve_license
from core.reliability_gate import LicenseDecision
from generate.proof_chain.entail import (
    INCONSISTENT_PREMISES,
    Entailment,
    evaluate_entailment_with_trace,
)
from generate.proof_chain.exist import ExistArgument, read_exist_argument
from generate.proof_chain.verb import VerbArgument, read_verb_argument, verb_forms_link
from teaching.curriculum_premises import (
    CONNECTIVE_FAMILY,
    compile_premises,
    load_curriculum,
)

#: Subjects this composer serves, in a stable resolution order. A question is
#: routed to the subject whose ratified vocabulary contains BOTH of its terms;
#: more than one match is an `ambiguous_reading` refusal, never a guess.
SERVED_DOMAINS: tuple[str, ...] = (
    "physics",
    "mathematics_logic",
    "systems_software",
    "philosophy_theology",
)

#: The closed exam-question grammar: ``Does <subject> <verb> <object>?``.
#: Deliberately one shape. A question the grammar cannot read refuses typed —
#: the reader is never asked to guess which token is the relation.
_QUESTION_RE = re.compile(r"^\s*does\s+(.+?)\s*\?\s*$", re.IGNORECASE)


@dataclass(frozen=True, slots=True)
class CurriculumQuery:
    """A read exam question: the edge the curriculum is being asked about."""

    subject: str
    verb: str
    obj: str


@dataclass(frozen=True, slots=True)
class CurriculumRefusal:
    """A typed refusal — the closed reason vocabulary of ADR-0262 §4.6."""

    reason: str
    detail: str = ""


def looks_like_curriculum_question(text: str) -> bool:
    """True iff *text* has the ``Does …?`` polar-question SHAPE.

    A cheap syntactic pre-filter, NOT the commit gate — see
    :func:`is_curriculum_question`, which is what decides whether this
    composer claims a turn.
    """
    return bool(_QUESTION_RE.match(text or ""))


def is_curriculum_question(text: str) -> bool:
    """True iff *text* is a curriculum question this composer should CLAIM.

    The deduction composer can commit on shape alone because its gate — a
    sentence-initial "therefore" — is a genuine signal of intent: text shaped
    that way IS an argument. ``Does …?`` carries no such signal; it is one of
    the most common ways to open any English question. Committing on it would
    take "Does the build pass?" away from the rest of dispatch and answer it
    with a remark about curriculum gaps, which is worse than useless.

    So the gate is *routability*, not shape: claim the turn only when the
    question parses to three tokens AND its terms are vocabulary some served
    subject actually teaches. Everything past that point stays fail-closed
    (INV-34) — including ``ambiguous_reading``, where both terms ARE taught
    and the only problem is that two subjects claim them, and
    ``out_of_curriculum``, where the terms are taught and only the relation is
    unknown. Those are real curriculum questions with honest answers. A
    question whose vocabulary CORE has never been taught is simply not this
    composer's turn.
    """
    query = read_curriculum_question(text)
    if not isinstance(query, CurriculumQuery):
        return False
    domain = resolve_domain(query)
    if isinstance(domain, CurriculumRefusal):
        return domain.reason != "untaught_vocabulary"
    return True


def read_curriculum_question(text: str) -> CurriculumQuery | CurriculumRefusal:
    """Read *text* as ``Does <subject> <verb> <object>?``, or refuse (typed)."""
    match = _QUESTION_RE.match(text or "")
    if match is None:
        return CurriculumRefusal("question_shape_out_of_band", text or "")
    tokens = match.group(1).replace(",", " ").lower().split()
    if len(tokens) != 3:
        # Two-token ("does force act") and four-token ("does a force cause
        # acceleration") shapes are genuinely different readings; the closed
        # grammar refuses rather than dropping or inventing a slot.
        return CurriculumRefusal("question_shape_out_of_band", " ".join(tokens))
    return CurriculumQuery(tokens[0], tokens[1], tokens[2])


def resolve_domain(query: CurriculumQuery) -> str | CurriculumRefusal:
    """The subject whose ratified vocabulary contains BOTH of the query's
    terms — or a typed refusal (§4.6).

    ``untaught_vocabulary`` is the anti-recall boundary made mechanical: a
    term no mounted pack teaches cannot be reasoned about here at all, however
    familiar it is. ``ambiguous_reading`` fires when two subjects would both
    claim the question; the composer declines rather than picking one.
    """
    matches = [
        domain
        for domain in SERVED_DOMAINS
        if {query.subject, query.obj} <= load_curriculum(domain).vocabulary
    ]
    if not matches:
        return CurriculumRefusal(
            "untaught_vocabulary", f"{query.subject} / {query.obj}"
        )
    if len(matches) > 1:
        return CurriculumRefusal("ambiguous_reading", ", ".join(matches))
    return matches[0]


def resolve_family(query: CurriculumQuery) -> str | CurriculumRefusal:
    """The relation family of the query's verb, under the SAME closed
    agreement relation the verb-predicate band uses (ADR-0260) — so a question
    may spell the relation in its base form ("cause") while the curriculum
    states it in the third person ("causes")."""
    for connective, family in CONNECTIVE_FAMILY.items():
        if verb_forms_link(query.verb, connective):
            return family
    return CurriculumRefusal("out_of_curriculum", query.verb)


def _resolve_connective(query: CurriculumQuery, family: str) -> str:
    """The curriculum's own spelling of *query*'s relation, within *family* —
    the SAME closed agreement relation the verb-predicate band uses
    (ADR-0260), so a question may spell the relation in its base form while
    the curriculum states it in the third person. Guarded by
    :func:`resolve_family`: any *family* reaching this function already has a
    connective that links to ``query.verb``."""
    for connective in CONNECTIVE_FAMILY:
        if CONNECTIVE_FAMILY[connective] == family and verb_forms_link(
            query.verb, connective
        ):
            return connective
    return query.verb  # pragma: no cover - guarded above


def _query_sentence(query: CurriculumQuery, family: str) -> str:
    """The conclusion sentence, spelled with the CURRICULUM's own connective
    form so the reader's agreement linking has nothing to do — the question's
    base form is normalized here, once, visibly."""
    return f"{query.subject} {_resolve_connective(query, family)} {query.obj}"


def band_for(domain: str, family: str) -> str:
    """The capability band an answer is licensed under: *(subject × relation
    family)* — ADR-0262 §4."""
    return f"curriculum_{domain}_{family}"


@dataclass(frozen=True, slots=True)
class CurriculumDecision:
    """What the composer decided, before rendering — the lane scores this."""

    verdict: str          # entailed | refuted | unknown | declined
    band: str             # "" when the question never reached a band
    reason: str           # typed refusal reason, or "" when decided
    domain: str = ""
    family: str = ""
    premise_count: int = 0  # FAMILY size — user-visible (ADR-0264 R7)
    scope_size: int = 0     # compiled, query-scoped premise count (R5/R7)


def decide_curriculum_question(text: str) -> CurriculumDecision:
    """Read, route, compile, and decide — the production decision path.

    Kept separate from the rendering below so the lane can pin the DECISION
    without pinning prose (the same split ``evals/deduction_serve/runner.py``
    uses).
    """
    query = read_curriculum_question(text)
    if isinstance(query, CurriculumRefusal):
        return CurriculumDecision("declined", "", query.reason)
    domain = resolve_domain(query)
    if isinstance(domain, CurriculumRefusal):
        return CurriculumDecision("declined", "", domain.reason)
    family = resolve_family(query)
    if isinstance(family, CurriculumRefusal):
        return CurriculumDecision("declined", "", family.reason, domain=domain)

    curriculum = load_curriculum(domain)
    family_chains = curriculum.family(family)
    if not family_chains:
        return CurriculumDecision(
            "declined", "", "empty_curriculum", domain=domain, family=family
        )
    family_size = len(family_chains)
    band = band_for(domain, family)
    connective = _resolve_connective(query, family)
    premises, _chain_ids = compile_premises(
        curriculum, family, query=(query.subject, connective, query.obj)
    )
    if not premises:
        # An empty SCOPE — no ratified chain mentions either query term — is
        # the open-world UNKNOWN reading (ADR-0264 R6). Distinct from an
        # empty FAMILY (handled above), which stays `empty_curriculum`.
        return CurriculumDecision(
            "unknown", band, "", domain=domain, family=family, premise_count=family_size,
        )
    conclusion = _query_sentence(query, family)
    argument = ". ".join(premises) + f". Therefore {conclusion}."

    # The SAME argument bands decide it. The verb band reads these sentences
    # (each is `<term> <connective> <term>`); the existential band is tried
    # after it exactly as in serving, so the cascade order here matches the
    # deduction composer's tail and no subject-specific decider exists.
    arg = read_verb_argument(argument)
    if not isinstance(arg, VerbArgument):
        arg = read_exist_argument(argument)
        if not isinstance(arg, ExistArgument):
            return CurriculumDecision(
                "declined", "", "compiled_premises_unreadable",
                domain=domain, family=family, premise_count=family_size,
            )
    trace = evaluate_entailment_with_trace(arg.premise_formulas, arg.query_formula)
    verdict = {
        Entailment.ENTAILED: "entailed",
        Entailment.REFUTED: "refuted",
        Entailment.UNKNOWN: "unknown",
        Entailment.REFUSED: "declined",
    }[trace.outcome]
    reason = trace.reason if trace.outcome is Entailment.REFUSED else ""
    return CurriculumDecision(
        verdict,
        band,
        reason,
        domain=domain,
        family=family,
        premise_count=family_size,
        scope_size=len(premises),
    )


_LicenseLookup = Callable[[str], LicenseDecision | None]

_REFUSAL_SURFACE = {
    "question_shape_out_of_band": (
        "That reads as a question about a subject I study, but not in a form I "
        "can decide yet (I read \"Does <term> <relation> <term>?\")."
    ),
    "out_of_curriculum": (
        "I haven't been taught the relation \"{detail}\", so I can't decide "
        "that question from my curriculum."
    ),
    "ambiguous_reading": (
        "Those terms are taught in more than one subject I study ({detail}), "
        "so I can't tell which curriculum you're asking about."
    ),
    "empty_curriculum": (
        "I have no ratified material for that kind of relation yet, so there "
        "is nothing for me to decide it from."
    ),
    "compiled_premises_unreadable": (
        "I have the curriculum for that, but I can't read it back precisely "
        "enough to decide the question yet."
    ),
    INCONSISTENT_PREMISES: (
        "The curriculum I have for that is inconsistent — I won't assert "
        "anything from it until it is corrected."
    ),
}
_DEFAULT_REFUSAL_SURFACE = (
    "I can't decide that from my curriculum as stated."
)

#: Disclosed hedge for a band that has not earned SERVE — same posture as
#: the deduction composer (ADR-0256): the answer is sound, the track record
#: is not yet demonstrated, so it is served DISCLOSED rather than withheld.
_UNVERIFIED_SHAPE_DISCLOSURE = (
    "(answered from my curriculum, but I haven't yet earned a verified track "
    "record on questions of this shape) "
)


def curriculum_grounded_surface(
    text: str, *, license_lookup: _LicenseLookup = curriculum_serve_license,
) -> str | None:
    """Return a deterministic CURRICULUM-tier surface, or ``None``.

    ``None`` when *text* is not a curriculum question this composer should
    claim (:func:`is_curriculum_question`) — the caller then falls through to
    its pre-existing dispatch, byte-identical to before this composer existed.
    """
    if not is_curriculum_question(text):
        return None
    decision = decide_curriculum_question(text)
    query = read_curriculum_question(text)
    # Restate the question in the CURRICULUM's own spelling of the relation —
    # the normalization the reader performed is shown, not hidden.
    shown = (
        _query_sentence(query, decision.family)
        if isinstance(query, CurriculumQuery) and decision.family
        else text.strip()
    )
    if decision.verdict == "declined":
        template = _REFUSAL_SURFACE.get(decision.reason, _DEFAULT_REFUSAL_SURFACE)
        return template.format(detail=_detail_of(text, decision))
    if decision.verdict == "entailed":
        surface = (
            f"Yes — my {decision.domain} curriculum teaches that {shown}, "
            f"directly, among the {decision.premise_count} {decision.family} "
            f"relations it states."
        )
    elif decision.verdict == "refuted":
        surface = (
            f"No — my {decision.domain} curriculum rules out that {shown}."
        )
    else:
        surface = (
            f"My {decision.domain} curriculum doesn't settle whether {shown}. "
            f"It states {decision.premise_count} {decision.family} relations, "
            f"and none of them decides this one — which is not the same as "
            f"its being false."
        )
    return _license_gate(surface, decision.band, license_lookup)


def _detail_of(text: str, decision: CurriculumDecision) -> str:
    """The user-visible fragment a typed refusal names (empty when the reason
    carries no detail slot)."""
    query = read_curriculum_question(text)
    if not isinstance(query, CurriculumQuery):
        return ""
    if decision.reason == "out_of_curriculum":
        return query.verb
    if decision.reason == "ambiguous_reading":
        return ", ".join(
            d
            for d in SERVED_DOMAINS
            if {query.subject, query.obj} <= load_curriculum(d).vocabulary
        )
    return ""


def _license_gate(surface: str, band: str, license_lookup: _LicenseLookup) -> str:
    """Serve *surface* authoritatively iff *band* holds a SERVE license; else
    serve the same sound answer DISCLOSED (hedged)."""
    decision = license_lookup(band)
    if decision is not None and decision.licensed:
        return surface
    return _UNVERIFIED_SHAPE_DISCLOSURE + surface


__all__ = [
    "CurriculumDecision",
    "CurriculumQuery",
    "CurriculumRefusal",
    "SERVED_DOMAINS",
    "band_for",
    "curriculum_grounded_surface",
    "decide_curriculum_question",
    "is_curriculum_question",
    "looks_like_curriculum_question",
    "read_curriculum_question",
    "resolve_domain",
    "resolve_family",
]
