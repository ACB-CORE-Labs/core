"""Contemplation v0 pass manager (N6) — a single bounded pass chain.

```text
Pass 1  route the problem across the R1/R2 setup compilers   (N3)
Pass 2  classify + enrich each attempt with its failure family (N4)
Pass 3  decide the terminal state
Pass 4  optionally emit a proposal-only artifact              (N5)
```

No loops, no recursion, no background daemon, no L10 runtime — one bounded pass that ends in
exactly one `Terminal`. The recursive "reread with findings" loop is deferred until we have
proof the classifications are useful.

The load-bearing rule: a problem that one organ recognizes as a **substantive boundary** (a
correct wrong=0 refusal) must NEVER generate a proposal merely because the *other* organ refused
with a growth reason. So classification is **boundary-first**, and `input_shape` ("this organ does
not recognize the shape") is treated as non-blocking, not as a boundary. Proposals are emitted
only for genuine growth-surface gaps with no substantive boundary in play — and even then only
proposal-only artifacts (N5), never a mounted change.

Off-serving: imports the R1/R2 organs (`generate`) + the comprehension-attempt layer (`core`);
imports no `evals`, no `generate.derivation`, no `core.reliability_gate`. In v0 the R1 numeric
answer is the eval lane's domain — a routed R1 setup is `SOLVED_VERIFIED` (admissible,
forward-substitutable by construction); R2 is solved + verified end to end here.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, TYPE_CHECKING

from core.comprehension_attempt import (
    ComprehensionAttempt,
    cmb_is_authoritative,
    cmb_reason,
    emit_proposal,
    enrich_family,
    family_for_reason,
    route_setup,
)
from generate.answer_choices.verify import verify_answer_choice
from generate.combined_rate_comprehension.reader import read_combined_rate_problem
from generate.combined_rate_comprehension.solver import solve_combined_rate
from generate.constraint_comprehension.reader import read_constraint_problem
from generate.constraint_comprehension.solver import answer_constraint_problem
from generate.rate_comprehension.reader import read_rate_problem
from generate.rate_comprehension.solver import solve_rate
from generate.contemplation.findings import Finding, Terminal
from generate.meaning_graph.reader import Refusal

if TYPE_CHECKING:
    from core.epistemic_disclosure.limitation import LimitationAssessment
    from core.epistemic_questions.delivery import DeliveryOutcome

#: Substantive boundaries that are *recognized-but-unsupported* capabilities (not hard errors).
_UNSUPPORTED_FAMILIES = frozenset(
    {
        "unsupported_system_size",
        "unsupported_clause_shape",
        "unsupported_rate_duration",
    }
)
# Note: ``unsupported_temporal_state`` is deliberately NOT here — its clock-marker detector can
# fire on non-rate text, so it is a generic REFUSED_KNOWN_BOUNDARY, not a recognized-rate-capability.
#: The non-substantive "this organ does not recognize the shape" family — never blocks a proposal.
_NOT_MY_DOMAIN = "input_shape"


class InternalContemplationError(RuntimeError):
    """Raised when a routing invariant is violated (reader refused after organ was routed).

    This is not a user-visible error and must never be caught as a Refusal.
    It indicates a programming error in the route/read contract.
    """


# ---------------------------------------------------------------------------
# Organ pipeline descriptor
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class OrganPipeline:
    """All organ-specific callables needed by the unified solve/verify path.

    Args:
        organ:          Stable organ identifier string (e.g. ``"r2_constraints"``).
        reader:         Callable that parses *text* into a problem struct or Refusal.
        solver:         Callable that solves the problem struct, returning a numeric
                        value or Refusal.
        reason_adapter: Maps a raw solver refusal reason string to the canonical
                        family-lookup key.  Identity for R2/R3; ``cmb_reason`` for R4.
    """

    organ: str
    reader: Callable[[str], Any]
    solver: Callable[[Any], Any]
    reason_adapter: Callable[[str], str] = field(default=lambda r: r)


_PIPELINES: dict[str, OrganPipeline] = {
    "r2_constraints": OrganPipeline(
        organ="r2_constraints",
        reader=read_constraint_problem,
        solver=answer_constraint_problem,
    ),
    "r3_rate": OrganPipeline(
        organ="r3_rate",
        reader=read_rate_problem,
        solver=solve_rate,
    ),
    "r4_combined_rate": OrganPipeline(
        organ="r4_combined_rate",
        reader=read_combined_rate_problem,
        solver=solve_combined_rate,
        reason_adapter=cmb_reason,
    ),
}


# ---------------------------------------------------------------------------
# Result / Finding helpers
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ContemplationResult:
    """The outcome of one bounded contemplation pass."""

    terminal: Terminal
    findings: tuple[Finding, ...]
    attempts: tuple[ComprehensionAttempt, ...]
    selected_organ: str | None = None
    answer: int | None = None
    family: str | None = None
    proposal_path: str | None = None
    question_path: str | None = None
    message: str | None = None


def _result(
    terminal: Terminal,
    findings: list[Finding],
    attempts: tuple[ComprehensionAttempt, ...],
    /,
    **kwargs: Any,
) -> ContemplationResult:
    """Append the terminal Finding and return a ContemplationResult in one call.

    Guarantees that the terminal Finding is always the last entry in the
    findings sequence — enforced by construction, not by convention.
    """
    findings.append(Finding("terminal", terminal.value))
    return ContemplationResult(terminal, tuple(findings), attempts, **kwargs)


# ---------------------------------------------------------------------------
# Ask-delivery helpers
# ---------------------------------------------------------------------------


def _delivery_outcome_for_limitation(assessment: LimitationAssessment) -> DeliveryOutcome:
    """Helper to delegate to deliver_ask, pure and testable."""
    from core.epistemic_questions.delivery import deliver_ask
    return deliver_ask(assessment)


def _maybe_ask(
    reason: str,
    organ: str,
    findings: list[Finding],
    attempts: tuple[ComprehensionAttempt, ...],
    text: str,
    proposal_root: Path | None,
    question_root: Path | None,
    exercise_ask: bool,
) -> ContemplationResult | None:
    """Return an ask ContemplationResult if *reason* maps to an askable family, else None.

    Centralises the family_by_name / assess_from_family / exercise_ask check that
    previously appeared inline in every _solve_and_verify_r* function.
    """
    from core.comprehension_attempt.failure_family import family_by_name
    from core.epistemic_disclosure.limitation import assess_from_family
    family_obj = family_by_name(reason)
    if family_obj is None:
        return None
    assessment = assess_from_family(family_obj)
    if assessment.resolution_action == "ask_question" and exercise_ask:
        return _handle_ask_delivery(
            assessment, family_obj.name, findings, attempts,
            text, proposal_root, question_root, exercise_ask,
            selected_organ=organ,
        )
    return None


def _handle_ask_delivery(
    assessment: LimitationAssessment,
    family_name: str,
    findings: list[Finding],
    attempts: tuple[ComprehensionAttempt, ...],
    text: str,
    proposal_root: Path | None,
    question_root: Path | None,
    exercise_ask: bool,
    selected_organ: str | None = None,
) -> ContemplationResult:
    outcome = _delivery_outcome_for_limitation(assessment)
    if outcome.terminal == Terminal.QUESTION_NEEDED:
        assert outcome.question is not None
        import json
        from core.epistemic_questions.delivery import question_path

        path = question_path(outcome.question, question_root)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(outcome.question.to_json_dict(), indent=2, sort_keys=True),
            encoding="utf-8",
        )
        findings.append(Finding("ask", f"emitted question-only {assessment.blocking_reason}"))
        return _result(
            Terminal.QUESTION_NEEDED, findings, attempts,
            selected_organ=selected_organ, family=family_name,
            proposal_path=None, question_path=str(path),
        )
    else:
        findings.append(Finding("ask", f"unrenderable ask: {outcome.fallback_reason}"))
        if outcome.terminal == Terminal.PROPOSAL_EMITTED:
            from core.comprehension_attempt.failure_family import family_by_name
            family_obj = family_by_name(family_name)
            if family_obj is not None:
                path = emit_proposal(text, family_obj, attempts, root=proposal_root)
                return _result(
                    Terminal.PROPOSAL_EMITTED, findings, attempts,
                    selected_organ=selected_organ, family=family_name,
                    proposal_path=str(path) if path else None,
                )
        return _result(
            outcome.terminal, findings, attempts,
            selected_organ=selected_organ, family=family_name,
        )


# ---------------------------------------------------------------------------
# Unified solve / verify
# ---------------------------------------------------------------------------


def _solve_and_verify(
    pipeline: OrganPipeline,
    text: str,
    options: dict[str, Any] | None,
    answer_key: str | None,
    findings: list[Finding],
    attempts: tuple[ComprehensionAttempt, ...],
    proposal_root: Path | None,
    question_root: Path | None,
    exercise_ask: bool,
    depth: dict | None = None,  # propagate 3-lang depth for root-aware framing
) -> ContemplationResult:
    """Unified read → solve → maybe_ask → maybe_verify → terminal pipeline.

    Shared by every routed organ (R2, R3, R4, and future organs).  The only
    organ-specific variation is captured in *pipeline*.
    """
    organ = pipeline.organ

    problem = pipeline.reader(text)
    if isinstance(problem, Refusal):
        # Routing guarantees the reader admits a setup — if it refuses here the
        # route/read contract has been violated, which is an internal programming error.
        raise InternalContemplationError(
            f"{organ}: reader refused after routing admitted — "
            f"routing invariant violated: {problem.reason}"
        )

    value = pipeline.solver(problem)
    if isinstance(value, Refusal):
        findings.append(Finding("solve", f"solver refused: {value.reason}"))
        reason = pipeline.reason_adapter(value.reason)
        if ask_result := _maybe_ask(
            reason, organ, findings, attempts, text, proposal_root, question_root, exercise_ask
        ):
            return ask_result
        return _result(
            Terminal.REFUSED_KNOWN_BOUNDARY, findings, attempts,
            selected_organ=organ, family=_family_name(reason),
        )

    verdict = None
    if options is not None:
        noun = (
            getattr(getattr(problem, "query", None), "unit", None)
            if organ == "r2_constraints"
            else None
        )
        verdict = verify_answer_choice(
            value, options, answer_key,
            **({"noun": noun} if noun is not None else {}),
        )
    # Use depth for root-aware (3-lang) if provided from upstream PropositionGraph
    # framing findings added at contemplate entry; no synthetic enrich here
    if depth:
        for nid, d in depth.items():
            if d.get("root"):
                findings.append(Finding("depth", f"root={d['root']} lang={d.get('language')} for node {nid}"))
                break
    if verdict is not None:
        if isinstance(verdict, Refusal):
            findings.append(Finding("verify", f"answer-choice refused: {verdict.reason}"))
            return _result(
                Terminal.REFUSED_KNOWN_BOUNDARY, findings, attempts,
                selected_organ=organ, answer=value,
            )
        if verdict.status == "contradiction":
            findings.append(Finding("verify", verdict.message))
            return _result(
                Terminal.CONTRADICTION_DETECTED, findings, attempts,
                selected_organ=organ, answer=value,
                family="answer_key_contradiction", message=verdict.message,
            )
        findings.append(Finding("verify", verdict.message))

    findings.append(Finding("solve", f"value={value}"))
    return _result(
        Terminal.SOLVED_VERIFIED, findings, attempts,
        selected_organ=organ, answer=value,
    )


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def depth_framing_findings(depth: dict | None) -> tuple[Finding, ...]:
    """Pure framing findings for depth (3-lang roots) at contemplate entry.

    Called when depth provided; returns Findings for root-aware.
    """
    if not depth:
        return ()
    roots = []
    for nid, d in depth.items():
        if d.get("root"):
            roots.append(f"{nid}:{d.get('language','?')}:{d['root']}")
    if roots:
        return (Finding("depth", "roots=" + ",".join(roots)),)
    return ()


def contemplate(
    text: str,
    *,
    options: dict[str, Any] | None = None,
    answer_key: str | None = None,
    proposal_root: Path | None = None,
    question_root: Path | None = None,
    case_id: str | None = None,
    exercise_ask: bool = False,
    depth: dict | None = None,  # 3-lang node depth from PropositionGraph for root-aware
) -> ContemplationResult:
    """Run one bounded contemplation pass over *text*."""
    findings: list[Finding] = []
    if depth:
        findings.extend(depth_framing_findings(depth))

    # Pass 1 — route.
    route = route_setup(text, case_id=case_id)
    findings.append(Finding("route", f"status={route.status}"))

    # Pass 2 — classify + enrich.
    attempts = tuple(enrich_family(a) for a in route.attempts)
    findings.append(
        Finding(
            "classify",
            "; ".join(
                f"{a.organ}:{a.outcome}:{a.family or a.refusal_reason or '-'}" for a in attempts
            ),
        )
    )

    # Pass 3/4 — terminal (+ maybe emit).
    if route.status == "ambiguous":
        return _result(Terminal.AMBIGUOUS_ORGAN, findings, attempts)

    if route.status == "routed":
        assert route.selected is not None
        if route.selected.organ in _PIPELINES:
            return _solve_and_verify(
                _PIPELINES[route.selected.organ],
                text, options, answer_key, findings, attempts,
                proposal_root, question_root, exercise_ask,
                depth=depth,
            )
        # R1: numeric answer is the eval lane's domain in v0.
        findings.append(Finding("solve", "r1 admissible setup (numeric answer is the eval lane in v0)"))
        return _result(
            Terminal.SOLVED_VERIFIED, findings, attempts, selected_organ="r1_quantitative"
        )

    # route.status == "all_refused"
    return _classify_all_refused(
        text, attempts, findings, proposal_root, question_root, exercise_ask
    )


# ---------------------------------------------------------------------------
# All-refused classification
# ---------------------------------------------------------------------------


def _classify_all_refused(
    text: str,
    attempts: tuple[ComprehensionAttempt, ...],
    findings: list[Finding],
    proposal_root: Path | None,
    question_root: Path | None,
    exercise_ask: bool,
) -> ContemplationResult:
    # CMB-over-R3 precedence (family side): when CMB substantively recognized the text, R3's broader
    # partial classification is suppressed, so CMB's sharper diagnosis owns the terminal/proposal.
    considered = attempts
    if cmb_is_authoritative(attempts):
        considered = tuple(a for a in attempts if a.organ != "r3_rate")

    families = [(a, family_for_reason(a.refusal_reason)) for a in considered]

    # Boundary-first: a substantive recognized boundary blocks any proposal or ASK.
    for _attempt, family in families:
        if family is not None and family.must_remain_refused and family.name != _NOT_MY_DOMAIN:
            terminal = (
                Terminal.REFUSED_UNSUPPORTED_FAMILY
                if family.name in _UNSUPPORTED_FAMILIES
                else Terminal.REFUSED_KNOWN_BOUNDARY
            )
            return _result(terminal, findings, attempts, family=family.name)

    # Check for ASK delivery only after substantive boundaries are ruled out.
    for attempt in considered:
        from core.epistemic_disclosure.limitation import assess_from_attempt
        assessment = assess_from_attempt(attempt)
        if assessment is not None and assessment.resolution_action == "ask_question":
            if exercise_ask:
                return _handle_ask_delivery(
                    assessment, assessment.blocking_reason, findings, attempts,
                    text, proposal_root, question_root, exercise_ask,
                )

    # No substantive boundary: a genuine growth surface may emit a proposal-only artifact.
    for _attempt, family in families:
        if family is not None and family.proposal_allowed:
            path = emit_proposal(text, family, attempts, root=proposal_root)
            findings.append(Finding("propose", f"emitted proposal-only {family.name}"))
            return _result(
                Terminal.PROPOSAL_EMITTED, findings, attempts,
                family=family.name, proposal_path=str(path) if path else None,
            )

    return _result(Terminal.NO_PROGRESS, findings, attempts)


# ---------------------------------------------------------------------------
# Internal utilities
# ---------------------------------------------------------------------------


def _family_name(reason: str | None) -> str | None:
    family = family_for_reason(reason)
    return family.name if family is not None else None


__all__ = ["ContemplationResult", "contemplate", "InternalContemplationError"]
