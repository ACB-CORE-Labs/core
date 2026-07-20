"""Typed fail-closed outcomes for geometry / coherence / contract gates.

These types are the only admissible non-answer results on answer-authority
paths. Silent defaults and heuristic fills are forbidden when the field
cannot close.

Fields required by linguistic governance Phase 1:
  failure_class, violated_condition, residual_state, refusal_reason
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping


class FailureClass(str, Enum):
    """Machine-stable failure taxonomy for answer-authority paths."""

    COHERENCE = "coherence"
    CONTRACT = "contract"
    FIELD = "field"
    CONSTRAINT = "constraint"
    MISSING_REFERENT = "missing_referent"
    AMBIGUITY = "ambiguity"
    ARTICULATION = "articulation"


@dataclass(frozen=True, slots=True)
class ResidualState:
    """Optional residual snapshot when a gate refuses.

    Coordinates are never required; digests / scalar residuals preferred.
    """

    versor_condition: float | None = None
    goldtether_residual: float | None = None
    missing_bindings: tuple[str, ...] = ()
    unresolved_hazards: tuple[str, ...] = ()
    detail: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "versor_condition": self.versor_condition,
            "goldtether_residual": self.goldtether_residual,
            "missing_bindings": list(self.missing_bindings),
            "unresolved_hazards": list(self.unresolved_hazards),
            "detail": self.detail,
        }


@dataclass(frozen=True, slots=True)
class FieldFailure:
    """Geometry / field construction could not produce a closed state."""

    failure_class: FailureClass
    violated_condition: str
    residual_state: ResidualState | None
    refusal_reason: str

    def __post_init__(self) -> None:
        if not self.violated_condition:
            raise ValueError("FieldFailure.violated_condition must be non-empty")
        if not self.refusal_reason:
            raise ValueError("FieldFailure.refusal_reason must be non-empty")
        if not isinstance(self.failure_class, FailureClass):
            raise TypeError("FieldFailure.failure_class must be a FailureClass")

    def as_dict(self) -> dict[str, Any]:
        return {
            "kind": "field_failure",
            "failure_class": self.failure_class.value,
            "violated_condition": self.violated_condition,
            "residual_state": None
            if self.residual_state is None
            else self.residual_state.as_dict(),
            "refusal_reason": self.refusal_reason,
        }


@dataclass(frozen=True, slots=True)
class CoherenceRefusal:
    """No admissible configuration — typed abstention, not a default answer."""

    failure_class: FailureClass
    violated_condition: str
    residual_state: ResidualState | None
    refusal_reason: str
    surface_message: str = ""

    def __post_init__(self) -> None:
        if not self.violated_condition:
            raise ValueError("CoherenceRefusal.violated_condition must be non-empty")
        if not self.refusal_reason:
            raise ValueError("CoherenceRefusal.refusal_reason must be non-empty")
        if not isinstance(self.failure_class, FailureClass):
            raise TypeError("CoherenceRefusal.failure_class must be a FailureClass")

    @property
    def message(self) -> str:
        if self.surface_message:
            return self.surface_message
        return (
            f"Abstaining: {self.refusal_reason} "
            f"(condition={self.violated_condition})."
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "kind": "coherence_refusal",
            "failure_class": self.failure_class.value,
            "violated_condition": self.violated_condition,
            "residual_state": None
            if self.residual_state is None
            else self.residual_state.as_dict(),
            "refusal_reason": self.refusal_reason,
            "surface_message": self.surface_message,
            "message": self.message,
        }


@dataclass(frozen=True, slots=True)
class ContractViolation:
    """Contract assessment missing or structurally incomplete — never silent pass."""

    failure_class: FailureClass
    violated_condition: str
    residual_state: ResidualState | None
    refusal_reason: str

    def __post_init__(self) -> None:
        if self.failure_class is not FailureClass.CONTRACT:
            raise ValueError("ContractViolation.failure_class must be CONTRACT")
        if not self.violated_condition:
            raise ValueError("ContractViolation.violated_condition must be non-empty")
        if not self.refusal_reason:
            raise ValueError("ContractViolation.refusal_reason must be non-empty")

    def as_dict(self) -> dict[str, Any]:
        return {
            "kind": "contract_violation",
            "failure_class": self.failure_class.value,
            "violated_condition": self.violated_condition,
            "residual_state": None
            if self.residual_state is None
            else self.residual_state.as_dict(),
            "refusal_reason": self.refusal_reason,
        }


@dataclass(frozen=True, slots=True)
class ConstraintViolation:
    """A typed semantic constraint could not be satisfied."""

    failure_class: FailureClass
    violated_condition: str
    residual_state: ResidualState | None
    refusal_reason: str

    def __post_init__(self) -> None:
        if not self.violated_condition:
            raise ValueError("ConstraintViolation.violated_condition must be non-empty")
        if not self.refusal_reason:
            raise ValueError("ConstraintViolation.refusal_reason must be non-empty")

    def as_dict(self) -> dict[str, Any]:
        return {
            "kind": "constraint_violation",
            "failure_class": self.failure_class.value,
            "violated_condition": self.violated_condition,
            "residual_state": None
            if self.residual_state is None
            else self.residual_state.as_dict(),
            "refusal_reason": self.refusal_reason,
        }


def contract_assessment_none_violation() -> ContractViolation:
    """Canonical violation when assessment is absent on an answer-authority path."""
    return ContractViolation(
        failure_class=FailureClass.CONTRACT,
        violated_condition="contract_assessment_present",
        residual_state=ResidualState(
            detail="contract_assessment is None — geometric conjugate cannot pass"
        ),
        refusal_reason=(
            "contract_assessment is None; substrate and certified answers are refused"
        ),
    )


def open_geometry_refusal(
    *,
    missing_bindings: tuple[str, ...] = (),
    unresolved_hazards: tuple[str, ...] = (),
    explanation: str = "",
    versor_condition: float | None = None,
    goldtether_residual: float | None = None,
) -> CoherenceRefusal:
    """Typed abstention when versor / GoldTether / binding contract is open."""
    conditions: list[str] = []
    if missing_bindings:
        conditions.extend(missing_bindings)
    if unresolved_hazards:
        conditions.extend(unresolved_hazards)
    violated = "|".join(conditions) if conditions else "geometric_contract_closed"
    return CoherenceRefusal(
        failure_class=FailureClass.COHERENCE,
        violated_condition=violated,
        residual_state=ResidualState(
            versor_condition=versor_condition,
            goldtether_residual=goldtether_residual,
            missing_bindings=missing_bindings,
            unresolved_hazards=unresolved_hazards,
            detail=explanation,
        ),
        refusal_reason=(
            "field geometric contract is not closed; no certified answer is available"
        ),
        surface_message=(
            "I cannot certify an answer: the geometric coherence contract is open "
            f"({violated})."
        ),
    )


def residual_from_mapping(data: Mapping[str, Any] | None) -> ResidualState | None:
    if not data:
        return None
    return ResidualState(
        versor_condition=_opt_float(data.get("versor_condition")),
        goldtether_residual=_opt_float(data.get("goldtether_residual")),
        missing_bindings=tuple(data.get("missing_bindings") or ()),
        unresolved_hazards=tuple(data.get("unresolved_hazards") or ()),
        detail=str(data.get("detail") or ""),
    )


def _opt_float(value: Any) -> float | None:
    if value is None:
        return None
    return float(value)


__all__ = [
    "FailureClass",
    "ResidualState",
    "FieldFailure",
    "CoherenceRefusal",
    "ContractViolation",
    "ConstraintViolation",
    "contract_assessment_none_violation",
    "open_geometry_refusal",
    "residual_from_mapping",
]
