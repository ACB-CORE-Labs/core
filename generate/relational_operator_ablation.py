"""Deterministic Relational Operator Ablation — fraction_decrease vertical slice.

Scientific framing
------------------
Hypothesis under test (narrow): explicit canonical relation operators compiled
into the existing geometric (VersorBinding / CGA) layer are measurable against
a math-frame-only baseline, and depth *metadata* is inert unless an explicit
executable mapping is activated.

This module does **not**:
- translate English problems into Hebrew or Greek,
- invent case/binyan roles from English,
- relax refusal gates,
- or claim full-GSM8K competence.

Conditions
----------
- ``baseline``: ProblemFrame roles + pure rational arithmetic (no VersorBinding).
- ``operator``: live Gate-A2k geometric path (``resolve_promotable_fraction_decrease``).
- ``depth``: same as operator with an explicit depth-contribution record.
  On English-only inputs there is **no** valid executable depth mapping
  (anti-circularity); contribution is recorded as inactive.
- ``metadata_only``: depth labels passed through ``assess_contracts`` (decorate
  explanations) then operator path — must not change the answer.
- ``invalid`` / adversarial: typed refusal, never a guessed answer.

Integrity model (project-native, not invented dual-adjoint jargon)
-------------------------------------------------------------------
- VersorBinding enforces ``versor_condition < 1e-6`` at construction.
- Organ self-verification requires grounded fraction token + base quantity.
- Readback reconstructs roles, scale surface, spans, and condition lineage.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from fractions import Fraction
from typing import Any, Literal, Mapping

from generate.derivation.fraction_decrease import (
    _asks_decrease_delta,
    _has_hazard_surface,
    compose_fraction_decrease,
    resolve_promotable_fraction_decrease,
)
from generate.derivation.target import _question_clause
from generate.problem_frame_builder import build_problem_frame
from generate.problem_frame_contracts import (
    ContractAssessment,
    assess_contracts,
    assess_fraction_decrease,
    assess_geometric_proposals,
)

ConditionName = Literal[
    "baseline",
    "operator",
    "depth",
    "metadata_only",
    "invalid",
]

OutcomeName = Literal["correct", "wrong", "refused"]

# Stable mapping-rule id for the (currently empty) English executable depth path.
DEPTH_EXECUTABLE_MAPPING_RULE: str = "depth_executable.fraction_decrease.v0_absent"
DEPTH_METADATA_RULE: str = "depth_metadata.enrich_assessments_with_depth.v1"


@dataclass(frozen=True, slots=True)
class DepthContribution:
    """Provenance for any depth-derived constraint (executable or inactive)."""

    mapping_rule_id: str
    source_pack_ids: tuple[str, ...]
    source_record_ids: tuple[str, ...]
    evidence_spans: tuple[tuple[int, int, str], ...]
    validity: Literal["inactive_no_mapping", "metadata_only", "executable", "invalid"]
    reason: str

    def as_json(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class RelationReadback:
    """Human-auditable reconstruction of the grounded relation."""

    relation_type: str
    roles: tuple[tuple[str, str], ...]  # (role, target_id_or_surface)
    scale_surface: str | None
    base_surface: str | None
    missing_bindings: tuple[str, ...]
    explanation: str
    has_versor_binding: bool
    versor_error: float | None

    def as_json(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class AblationResult:
    condition: ConditionName
    case_id: str
    outcome: OutcomeName
    answer: float | None
    answer_unit: str | None
    expected_answer: float | None
    refusal_reason: str
    readback: RelationReadback | None
    depth: DepthContribution | None
    frame_runnable: bool
    operator_bindings: int
    explanation_has_root_note: bool = False

    def as_json(self) -> dict[str, Any]:
        payload = {
            "condition": self.condition,
            "case_id": self.case_id,
            "outcome": self.outcome,
            "answer": self.answer,
            "answer_unit": self.answer_unit,
            "expected_answer": self.expected_answer,
            "refusal_reason": self.refusal_reason,
            "frame_runnable": self.frame_runnable,
            "operator_bindings": self.operator_bindings,
            "explanation_has_root_note": self.explanation_has_root_note,
            "readback": None if self.readback is None else self.readback.as_json(),
            "depth": None if self.depth is None else self.depth.as_json(),
        }
        return payload


@dataclass(frozen=True, slots=True)
class AblationCase:
    case_id: str
    problem: str
    expected_answer: float | None
    expected_unit: str
    expected_outcome: Literal["correct", "refused"]
    tags: tuple[str, ...] = ()
    depth_override: Mapping[str, Mapping[str, str]] | None = None
    notes: str = ""


def _score(
    *,
    answer: float | None,
    expected: float | None,
    expected_outcome: str,
) -> OutcomeName:
    if answer is None:
        return "refused"
    if expected is None:
        # Gold is abstention; any committed answer is wrong.
        return "wrong"
    if abs(float(answer) - float(expected)) < 1e-6:
        return "correct"
    return "wrong"


def _readback_from_assessment(
    assessment: ContractAssessment,
    frame_roles: tuple[tuple[str, str], ...],
) -> RelationReadback:
    scale_surface = None
    versor_error = None
    has_binding = bool(assessment.bindings)
    if assessment.bindings:
        scale_surface = assessment.bindings[0].semantic_identity
        versor_error = float(assessment.bindings[0].versor_error)
    return RelationReadback(
        relation_type="decrease_to_fraction",
        roles=frame_roles,
        scale_surface=scale_surface,
        base_surface=next((t for r, t in frame_roles if r == "base_quantity"), None),
        missing_bindings=tuple(assessment.missing_bindings),
        explanation=assessment.explanation,
        has_versor_binding=has_binding,
        versor_error=versor_error,
    )


def _frame_roles(frame) -> tuple[tuple[str, str], ...]:
    roles: list[tuple[str, str]] = []
    for relation in frame.bound_relations:
        if relation.relation_type != "decrease_to_fraction":
            continue
        for role in relation.roles:
            roles.append((role.role, role.target_id))
    return tuple(roles)


def _extract_base_and_scale(frame) -> tuple[Fraction, Fraction, str, str] | None:
    """Return (base, scale, base_surface, scale_surface) from grounded frame roles."""
    quantities = {q.fact_id: q for q in frame.quantities}
    mentions = {m.mention_id: m for m in frame.mentions}
    # Map mention_id → quantity value via fact_id when available.
    mention_value: dict[str, Fraction] = {}
    for mention in frame.mentions:
        if mention.kind != "quantity":
            continue
        if mention.fact_id and mention.fact_id in quantities:
            value = quantities[mention.fact_id].value
            mention_value[mention.mention_id] = (
                value if isinstance(value, Fraction) else Fraction(str(value))
            )
    # Prefer role targets from the unique decrease_to_fraction relation.
    relations = [
        r for r in frame.bound_relations if r.relation_type == "decrease_to_fraction"
    ]
    if len(relations) != 1:
        return None
    relation = relations[0]
    base_id = next((r.target_id for r in relation.roles if r.role == "base_quantity"), None)
    scale_id = next((r.target_id for r in relation.roles if r.role == "scale"), None)
    if base_id is None or scale_id is None:
        return None
    if base_id not in mention_value or scale_id not in mention_value:
        # Fall back: match by surface token against scalars.
        return None
    base = mention_value[base_id]
    scale = mention_value[scale_id]
    base_surface = mentions[base_id].surface if base_id in mentions else str(base)
    scale_surface = mentions[scale_id].surface if scale_id in mentions else str(scale)
    if not (0 < float(scale) < 1):
        return None
    return base, scale, base_surface, scale_surface


def run_baseline(case: AblationCase) -> AblationResult:
    """Canonical math-frame path: rational arithmetic from grounded roles only.

    Shares organ *refusal* discipline (question shape + hazard surfaces) with
    the live fraction_decrease organ so the ablation compares scalar vs geometric
    *execution*, not divergent gate policy. Does **not** apply VersorBinding/CGA.
    """
    frame = build_problem_frame(case.problem)
    assessment = assess_fraction_decrease(frame)
    roles = _frame_roles(frame)
    readback = _readback_from_assessment(assessment, roles)
    question = _question_clause(case.problem)

    if not assessment.runnable:
        return AblationResult(
            condition="baseline",
            case_id=case.case_id,
            outcome=_score(answer=None, expected=case.expected_answer, expected_outcome=case.expected_outcome),
            answer=None,
            answer_unit=None,
            expected_answer=case.expected_answer,
            refusal_reason=assessment.explanation or "frame_not_runnable",
            readback=readback,
            depth=None,
            frame_runnable=False,
            operator_bindings=0,
        )

    # Shared refuse gates with generate.derivation.fraction_decrease (no geometry).
    if not _asks_decrease_delta(question):
        return AblationResult(
            condition="baseline",
            case_id=case.case_id,
            outcome="refused",
            answer=None,
            answer_unit=None,
            expected_answer=case.expected_answer,
            refusal_reason="baseline_question_not_decrease_delta",
            readback=readback,
            depth=None,
            frame_runnable=True,
            operator_bindings=0,
        )
    if _has_hazard_surface(case.problem, question):
        return AblationResult(
            condition="baseline",
            case_id=case.case_id,
            outcome="refused",
            answer=None,
            answer_unit=None,
            expected_answer=case.expected_answer,
            refusal_reason="baseline_hazard_surface",
            readback=readback,
            depth=None,
            frame_runnable=True,
            operator_bindings=0,
        )

    extracted = _extract_base_and_scale(frame)
    if extracted is None:
        return AblationResult(
            condition="baseline",
            case_id=case.case_id,
            outcome="refused",
            answer=None,
            answer_unit=None,
            expected_answer=case.expected_answer,
            refusal_reason="baseline_scale_or_base_unresolved",
            readback=readback,
            depth=None,
            frame_runnable=True,
            operator_bindings=0,
        )

    base, scale, _base_s, _scale_s = extracted
    # decrease_by = base * (1 - scale) — pure rational, no geometric payload.
    answer = float(base * (Fraction(1) - scale))
    unit = ""
    for mention in frame.mentions:
        if mention.kind == "unit":
            unit = mention.surface
            break

    return AblationResult(
        condition="baseline",
        case_id=case.case_id,
        outcome=_score(
            answer=answer,
            expected=case.expected_answer,
            expected_outcome=case.expected_outcome,
        ),
        answer=answer,
        answer_unit=unit or None,
        expected_answer=case.expected_answer,
        refusal_reason="",
        readback=readback,
        depth=None,
        frame_runnable=True,
        operator_bindings=0,
    )


def run_operator(case: AblationCase) -> AblationResult:
    """Executable geometric operator path (live A2k organ)."""
    frame = build_problem_frame(case.problem)
    assessment = assess_fraction_decrease(frame)
    geom = assess_geometric_proposals(frame)
    geom_fd = next(
        (g for g in geom if g.candidate_organ == "fraction_decrease"),
        None,
    )
    roles = _frame_roles(frame)
    # Prefer obligation-complete assessment for readback; fall back to geometric.
    read_src = assessment if assessment.runnable else geom_fd
    readback = (
        _readback_from_assessment(read_src, roles)
        if read_src is not None
        else RelationReadback(
            relation_type="decrease_to_fraction",
            roles=roles,
            scale_surface=None,
            base_surface=None,
            missing_bindings=(),
            explanation="no_fraction_decrease_assessment",
            has_versor_binding=False,
            versor_error=None,
        )
    )

    resolution = resolve_promotable_fraction_decrease(case.problem)
    if resolution is None:
        reason = "operator_refused"
        if not assessment.runnable:
            reason = assessment.explanation or reason
        elif geom_fd is not None and not geom_fd.runnable:
            reason = geom_fd.explanation or reason
        return AblationResult(
            condition="operator",
            case_id=case.case_id,
            outcome=_score(answer=None, expected=case.expected_answer, expected_outcome=case.expected_outcome),
            answer=None,
            answer_unit=None,
            expected_answer=case.expected_answer,
            refusal_reason=reason,
            readback=readback,
            depth=None,
            frame_runnable=assessment.runnable,
            operator_bindings=len(assessment.bindings) if assessment.bindings else (
                len(geom_fd.bindings) if geom_fd else 0
            ),
        )

    return AblationResult(
        condition="operator",
        case_id=case.case_id,
        outcome=_score(
            answer=float(resolution.answer),
            expected=case.expected_answer,
            expected_outcome=case.expected_outcome,
        ),
        answer=float(resolution.answer),
        answer_unit=resolution.answer_unit or None,
        expected_answer=case.expected_answer,
        refusal_reason="",
        readback=readback,
        depth=None,
        frame_runnable=assessment.runnable,
        operator_bindings=len(assessment.bindings) or (
            len(geom_fd.bindings) if geom_fd else 0
        ),
    )


def run_depth(case: AblationCase) -> AblationResult:
    """Operator path + explicit depth-contribution provenance.

    For English-only problems there is no authored executable depth mapping.
    The contribution is recorded as ``inactive_no_mapping`` so the experiment
    cannot claim depth value it did not earn. Answer equals the operator path.
    """
    op = run_operator(case)
    depth = DepthContribution(
        mapping_rule_id=DEPTH_EXECUTABLE_MAPPING_RULE,
        source_pack_ids=(),
        source_record_ids=(),
        evidence_spans=(),
        validity="inactive_no_mapping",
        reason=(
            "No authored executable depth→relation mapping for English surface; "
            "anti-circularity forbids inventing Greek case / Hebrew binyan from English."
        ),
    )
    return AblationResult(
        condition="depth",
        case_id=op.case_id,
        outcome=op.outcome,
        answer=op.answer,
        answer_unit=op.answer_unit,
        expected_answer=op.expected_answer,
        refusal_reason=op.refusal_reason,
        readback=op.readback,
        depth=depth,
        frame_runnable=op.frame_runnable,
        operator_bindings=op.operator_bindings,
        explanation_has_root_note=op.explanation_has_root_note,
    )


def run_metadata_only(
    case: AblationCase,
    depth_labels: Mapping[str, Mapping[str, str]] | None = None,
) -> AblationResult:
    """Depth labels decorate assessments; operator answer must stay unchanged.

    Labels default to a synthetic he root note that must not affect arithmetic.
    """
    labels: dict[str, dict[str, str]] = {
        k: dict(v)
        for k, v in (
            depth_labels
            or case.depth_override
            or {"p0": {"language": "he", "root": "א-מ-נ"}}
        ).items()
    }
    frame = build_problem_frame(case.problem)
    assessments = assess_contracts(frame, depth=labels)
    fd = next((a for a in assessments if a.candidate_organ == "fraction_decrease"), None)
    has_root_note = bool(
        fd is not None and "[root:" in (fd.explanation or "")
    )

    # Operator path is independent of assess_contracts decoration.
    resolution = resolve_promotable_fraction_decrease(case.problem)
    roles = _frame_roles(frame)
    readback = (
        _readback_from_assessment(fd, roles)
        if fd is not None
        else RelationReadback(
            relation_type="decrease_to_fraction",
            roles=roles,
            scale_surface=None,
            base_surface=None,
            missing_bindings=(),
            explanation="no_fraction_decrease_in_assess_contracts",
            has_versor_binding=False,
            versor_error=None,
        )
    )
    depth = DepthContribution(
        mapping_rule_id=DEPTH_METADATA_RULE,
        source_pack_ids=("synthetic_metadata_only",),
        source_record_ids=tuple(sorted(labels.keys())),
        evidence_spans=(),
        validity="metadata_only",
        reason="Depth labels decorate ContractAssessment.explanation only; not executable.",
    )

    if resolution is None:
        return AblationResult(
            condition="metadata_only",
            case_id=case.case_id,
            outcome=_score(answer=None, expected=case.expected_answer, expected_outcome=case.expected_outcome),
            answer=None,
            answer_unit=None,
            expected_answer=case.expected_answer,
            refusal_reason=(fd.explanation if fd is not None else "operator_refused"),
            readback=readback,
            depth=depth,
            frame_runnable=bool(fd and fd.runnable),
            operator_bindings=len(fd.bindings) if fd and fd.bindings else 0,
            explanation_has_root_note=has_root_note,
        )

    return AblationResult(
        condition="metadata_only",
        case_id=case.case_id,
        outcome=_score(
            answer=float(resolution.answer),
            expected=case.expected_answer,
            expected_outcome=case.expected_outcome,
        ),
        answer=float(resolution.answer),
        answer_unit=resolution.answer_unit or None,
        expected_answer=case.expected_answer,
        refusal_reason="",
        readback=readback,
        depth=depth,
        frame_runnable=bool(fd and fd.runnable),
        operator_bindings=len(fd.bindings) if fd and fd.bindings else 0,
        explanation_has_root_note=has_root_note,
    )


def run_invalid(case: AblationCase) -> AblationResult:
    """Force the invalid/adversarial condition: commit only on clean organ admit."""
    # Same as operator scoring: confusers must refuse, not guess.
    result = run_operator(case)
    return AblationResult(
        condition="invalid",
        case_id=result.case_id,
        outcome=result.outcome,
        answer=result.answer,
        answer_unit=result.answer_unit,
        expected_answer=result.expected_answer,
        refusal_reason=result.refusal_reason or (
            "committed" if result.answer is not None else "refused"
        ),
        readback=result.readback,
        depth=DepthContribution(
            mapping_rule_id="invalid.control",
            source_pack_ids=(),
            source_record_ids=(),
            evidence_spans=(),
            validity="invalid",
            reason="Adversarial/invalid control case; refuse preferred over wrong.",
        ),
        frame_runnable=result.frame_runnable,
        operator_bindings=result.operator_bindings,
    )


_CONDITION_RUNNERS = {
    "baseline": run_baseline,
    "operator": run_operator,
    "depth": run_depth,
    "metadata_only": run_metadata_only,
    "invalid": run_invalid,
}


def run_condition(condition: ConditionName, case: AblationCase) -> AblationResult:
    return _CONDITION_RUNNERS[condition](case)


def run_all_conditions(case: AblationCase) -> dict[ConditionName, AblationResult]:
    # For gold-solve cases, skip invalid runner (same as operator); for refuse gold, use invalid.
    results: dict[ConditionName, AblationResult] = {}
    for name in ("baseline", "operator", "depth", "metadata_only"):
        results[name] = run_condition(name, case)  # type: ignore[arg-type]
    if case.expected_outcome == "refused" or "adversarial" in case.tags or "invalid" in case.tags:
        results["invalid"] = run_invalid(case)
    return results


def answers_match(a: AblationResult, b: AblationResult, *, tol: float = 1e-6) -> bool:
    """True when both refuse, or both commit equal answers."""
    if a.answer is None and b.answer is None:
        return True
    if a.answer is None or b.answer is None:
        return False
    return abs(float(a.answer) - float(b.answer)) < tol
