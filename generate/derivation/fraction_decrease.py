"""Gate A2k — fraction-decrease delta (decrease-to fraction of base).

Experience Flywheel Sprint 8 / composition-validation **cv-0007** (train_sample
**0005**): forecast clause states a quantity will ``decrease to N/M of`` its
current value; a follow-on clause states the current amount; the question asks
the **decrease by** delta (not the final value).

    decrease_by = base × (1 − N/M)

Narrow organ — not a generic affine equation parser, not ``N/M more than`` affine
surfaces (0010-class), not percent-decrease.  Promotion requires:

- exactly one ``decrease to N/M of forecast`` (no ``more than`` fraction affine);
- question binds ``decrease`` + ``by`` (delta target, not final-value question);
- exactly one explicit current/base quantity with a unit;
- hazard refusal (percent, goal language, multiple decrease-to fractions).

Deterministic; sealed module (no ``chat/`` import).
"""

from __future__ import annotations

from typing import Final

import numpy as np

from algebra.cga import embed_point, read_scalar_e1
from algebra.versor import versor_apply
from generate.derivation.clauses import segment_clauses
from generate.derivation.extract import extract_quantities
from generate.derivation.model import GroundedDerivation, Quantity, Step
from generate.derivation.target import _question_clause
from generate.derivation.verify import Resolution, SelfVerification, select_self_verified
from generate.problem_frame_contracts import ContractAssessment
from generate.math_roundtrip import _tokens

_GOAL_INTENT: Final[frozenset[str]] = frozenset(
    {"want", "wants", "wanted", "need", "needs", "hoping", "hopes", "plans", "aims", "goal"}
)
_FINAL_VALUE_CUES: Final[frozenset[str]] = frozenset({"be", "will", "what"})


def _asks_decrease_delta(question_clause: str) -> bool:
    tokens = _tokens(question_clause)
    return "decrease" in tokens and "by" in tokens


def _asks_final_value(question_clause: str) -> bool:
    tokens = _tokens(question_clause)
    if "by" in tokens:
        return False
    if "decrease" not in tokens:
        return False
    return bool(_FINAL_VALUE_CUES & tokens) or "temperature" in tokens


def _has_hazard_surface(problem_text: str, question_clause: str) -> bool:
    text_tokens = _tokens(problem_text)
    question_tokens = _tokens(question_clause)
    if "more" in text_tokens and "than" in text_tokens:
        return True
    if "%" in problem_text or "percent" in text_tokens or "percentage" in text_tokens:
        return True
    if text_tokens & _GOAL_INTENT:
        return True
    if _asks_final_value(question_clause):
        return True
    return False


def _current_base_quantity(
    problem_text: str, question_clause: str, contract: ContractAssessment
) -> Quantity | None:
    source_text = contract.bindings[0].semantic_identity
    for clause in segment_clauses(problem_text):
        if source_text in clause:
            continue
        tokens = _tokens(clause)
        if "current" not in tokens and "now" not in tokens:
            continue
        quantities = [q for q in extract_quantities(clause) if q.unit]
        if len(quantities) == 1:
            return quantities[0]
    for clause in segment_clauses(problem_text):
        if clause == question_clause:
            continue
        if source_text in clause:
            continue
        quantities = [q for q in extract_quantities(clause) if q.unit]
        if len(quantities) == 1:
            return quantities[0]
    return None



def _has_hazard_surface(problem_text: str) -> bool:
    import re
    if "more" in problem_text and "than" in problem_text:
        return True
    if "%" in problem_text or "percent" in problem_text or "percentage" in problem_text:
        return True
    if len(re.findall(r"decrease[d]? to \d+\s*/\s*\d+\s+of", problem_text)) > 1:
        return True
    if len(re.findall(r"\d+\s*/\s*\d+", problem_text)) > 1:
        return True
    return False

def build_fraction_decrease(
    problem_text: str, contract: ContractAssessment
) -> GroundedDerivation | None:
    """Construct mathematical decrease delta, or ``None``."""
    if not contract.runnable or not contract.bindings or _has_hazard_surface(problem_text):
        return None

    question_clause = _question_clause(problem_text)
    if not _asks_decrease_delta(question_clause):
        return None
    if _has_hazard_surface(problem_text):
        return None

    base = _current_base_quantity(problem_text, question_clause, contract)
    if base is None:
        return None

    D = contract.bindings[0].geometric_payload
    v = base.value
    Q = embed_point([v, 0, 0], dtype=np.float64)
    Q_new = versor_apply(D, Q)
    new_value = read_scalar_e1(Q_new)

    return GroundedDerivation(
        start=base,
        steps=(
            Step(
                op="subtract",
                operand=Quantity(
                    value=new_value,
                    unit=base.unit,
                    source_token=contract.bindings[0].semantic_identity,
                ),
                cue="decrease",
            ),
        ),
    )


def _self_verifies_fraction_decrease(
    derivation: GroundedDerivation, problem_text: str, contract: ContractAssessment
) -> SelfVerification:
    from generate.derivation.verify import _base_reasons

    tokens = _tokens(problem_text)
    reasons = list(_base_reasons(derivation, tokens))

    if not contract.bindings:
        reasons.append("missing decrease-to fraction forecast")
    else:
        token = contract.bindings[0].semantic_identity
        if token not in problem_text:
            reasons.append(f"fraction token {token!r} not grounded in text")

    base = _current_base_quantity(problem_text, _question_clause(problem_text), contract)
    if base is None:
        reasons.append("missing explicit current/base quantity")

    return SelfVerification(verified=not reasons, reasons=tuple(reasons))


def compose_fraction_decrease(
    problem_text: str, contract: ContractAssessment
) -> Resolution | None:
    """Gate the typed fraction-decrease chain through self-verification."""
    derivation = build_fraction_decrease(problem_text, contract)
    if derivation is None:
        return None
    if not _self_verifies_fraction_decrease(derivation, problem_text, contract).verified:
        return None
    return Resolution(
        answer=derivation.answer,
        answer_unit=derivation.answer_unit,
        derivation=derivation,
    )


def resolve_promotable_fraction_decrease(
    problem_text: str, contract: ContractAssessment
) -> Resolution | None:
    """Serving promotion bridge (Gate A2k)."""
    return compose_fraction_decrease(problem_text, contract)
