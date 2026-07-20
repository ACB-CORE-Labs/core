"""Typed semantic primitives (linguistic governance Phase 2)."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from fractions import Fraction
from typing import Any, Iterable, Sequence


class ValidationError(ValueError):
    """Ill-typed or incomplete primitive construction."""


class DimensionalType(str, Enum):
    COUNT = "count"
    LENGTH = "length"
    MASS = "mass"
    TIME = "time"
    CURRENCY = "currency"
    RATE = "rate"
    DIMENSIONLESS = "dimensionless"
    UNKNOWN = "unknown"


class RelationKind(str, Enum):
    POSSESSION = "possession"
    COMPARISON = "comparison"
    EQUALITY = "equality"
    RATIO = "ratio"
    MEMBERSHIP = "membership"
    ORDER = "order"
    AGENT = "agent"
    PATIENT = "patient"
    RECIPIENT = "recipient"
    POSSESSOR = "possessor"
    SOURCE = "source"
    TARGET = "target"
    OTHER = "other"


class OperatorClass(str, Enum):
    TRANSFER = "transfer"
    REMOVAL = "removal"
    ACCUMULATION = "accumulation"
    CREATION = "creation"
    PARTITION = "partition"
    COMPARISON = "comparison"
    TRANSFORMATION = "transformation"
    RECURRENCE = "recurrence"
    CAUSATION = "causation"
    IDENTITY_CONTINUITY = "identity_continuity"
    UNKNOWN = "unknown"


class TemporalKind(str, Enum):
    PRIOR_ONGOING = "prior_ongoing"
    PRIOR_COMPLETED = "prior_completed"
    PRESENT = "present"
    FUTURE = "future"
    RECURRING = "recurring"
    UNSPECIFIED = "unspecified"


def _require_nonempty(value: str, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{name} must be a non-empty str")
    return value


def _reject_dict_blob(value: Any, name: str) -> None:
    if isinstance(value, dict):
        raise ValidationError(
            f"{name} must not be an untyped dict; use the typed constructor"
        )


@dataclass(frozen=True, slots=True)
class ProvenanceSpan:
    start: int
    end: int
    text: str = ""

    def __post_init__(self) -> None:
        if self.start < 0 or self.end < self.start:
            raise ValidationError("ProvenanceSpan requires 0 <= start <= end")


@dataclass(frozen=True, slots=True)
class Entity:
    """Persistent identity anchor with typed id, name, type, and frame bindings."""

    entity_id: str
    name: str
    entity_type: str
    frame_ids: tuple[str, ...] = ()
    provenance: ProvenanceSpan | None = None

    def __post_init__(self) -> None:
        _require_nonempty(self.entity_id, "Entity.entity_id")
        _require_nonempty(self.name, "Entity.name")
        _require_nonempty(self.entity_type, "Entity.entity_type")


@dataclass(frozen=True, slots=True)
class Quantity:
    """Value + unit + dimensional type + owner + frame (no raw bare floats alone)."""

    value: Fraction
    unit: str
    dimensional_type: DimensionalType
    owner_entity_id: str
    frame_id: str
    source_token: str = ""
    provenance: ProvenanceSpan | None = None

    def __post_init__(self) -> None:
        if isinstance(self.value, float):
            # Allow float only if caller wrapped — still reject bare construction
            # via type check: Fraction is required.
            raise ValidationError(
                "Quantity.value must be Fraction (not float) to avoid untyped numerics"
            )
        if not isinstance(self.value, Fraction):
            raise ValidationError("Quantity.value must be a Fraction")
        _require_nonempty(self.unit, "Quantity.unit")
        if not isinstance(self.dimensional_type, DimensionalType):
            raise ValidationError("Quantity.dimensional_type must be DimensionalType")
        _require_nonempty(self.owner_entity_id, "Quantity.owner_entity_id")
        _require_nonempty(self.frame_id, "Quantity.frame_id")

    @classmethod
    def from_int(
        cls,
        value: int,
        *,
        unit: str,
        dimensional_type: DimensionalType,
        owner_entity_id: str,
        frame_id: str,
        source_token: str = "",
        provenance: ProvenanceSpan | None = None,
    ) -> "Quantity":
        return cls(
            value=Fraction(value),
            unit=unit,
            dimensional_type=dimensional_type,
            owner_entity_id=owner_entity_id,
            frame_id=frame_id,
            source_token=source_token,
            provenance=provenance,
        )


@dataclass(frozen=True, slots=True)
class Container:
    """Bounded inventory/balance with typed content and conserved quantity id."""

    container_id: str
    owner_entity_id: str
    content_entity_ids: tuple[str, ...]
    conserved_quantity_id: str
    capacity: Quantity | None = None
    frame_id: str = "default"

    def __post_init__(self) -> None:
        _require_nonempty(self.container_id, "Container.container_id")
        _require_nonempty(self.owner_entity_id, "Container.owner_entity_id")
        _require_nonempty(self.conserved_quantity_id, "Container.conserved_quantity_id")
        if not isinstance(self.content_entity_ids, tuple):
            raise ValidationError("Container.content_entity_ids must be a tuple")


@dataclass(frozen=True, slots=True)
class TemporalFrame:
    frame_id: str
    kind: TemporalKind
    label: str = ""

    def __post_init__(self) -> None:
        _require_nonempty(self.frame_id, "TemporalFrame.frame_id")
        if not isinstance(self.kind, TemporalKind):
            raise ValidationError("TemporalFrame.kind must be TemporalKind")


@dataclass(frozen=True, slots=True)
class TemporalExtent:
    frame: TemporalFrame
    start_label: str = ""
    end_label: str = ""


@dataclass(frozen=True, slots=True)
class Event:
    """Typed transformation with roles; incomplete roles must be explicit None."""

    event_id: str
    operator_class: OperatorClass
    agent_entity_id: str | None
    patient_entity_id: str | None
    source_entity_id: str | None
    target_entity_id: str | None
    conserved_quantity_id: str | None
    temporal_extent: TemporalExtent | None
    direction: str = ""
    unresolved_roles: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _require_nonempty(self.event_id, "Event.event_id")
        if not isinstance(self.operator_class, OperatorClass):
            raise ValidationError("Event.operator_class must be OperatorClass")
        if isinstance(self.agent_entity_id, dict):
            raise ValidationError("Event roles must not be dict blobs")


@dataclass(frozen=True, slots=True)
class Operator:
    """Executable semantic transformation linked to an Event type."""

    operator_id: str
    operator_class: OperatorClass
    event_id: str
    executable_symbol: str

    def __post_init__(self) -> None:
        _require_nonempty(self.operator_id, "Operator.operator_id")
        _require_nonempty(self.event_id, "Operator.event_id")
        _require_nonempty(self.executable_symbol, "Operator.executable_symbol")
        if not isinstance(self.operator_class, OperatorClass):
            raise ValidationError("Operator.operator_class must be OperatorClass")


@dataclass(frozen=True, slots=True)
class Relation:
    relation_id: str
    kind: RelationKind
    left_entity_id: str
    right_entity_id: str
    polarity: bool = True
    provenance: ProvenanceSpan | None = None

    def __post_init__(self) -> None:
        _require_nonempty(self.relation_id, "Relation.relation_id")
        if not isinstance(self.kind, RelationKind):
            raise ValidationError("Relation.kind must be RelationKind")
        _require_nonempty(self.left_entity_id, "Relation.left_entity_id")
        _require_nonempty(self.right_entity_id, "Relation.right_entity_id")


@dataclass(frozen=True, slots=True)
class IdentityBridge:
    """Explicit cross-frame entity identity claim with change log."""

    bridge_id: str
    entity_id: str
    from_frame_id: str
    to_frame_id: str
    change_log: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _require_nonempty(self.bridge_id, "IdentityBridge.bridge_id")
        _require_nonempty(self.entity_id, "IdentityBridge.entity_id")
        _require_nonempty(self.from_frame_id, "IdentityBridge.from_frame_id")
        _require_nonempty(self.to_frame_id, "IdentityBridge.to_frame_id")


@dataclass(frozen=True, slots=True)
class ConservationLaw:
    law_id: str
    quantity_id: str
    persists: bool
    flows: bool
    externally_added: bool
    consumed: bool
    transferred: bool
    statement: str = ""

    def __post_init__(self) -> None:
        _require_nonempty(self.law_id, "ConservationLaw.law_id")
        _require_nonempty(self.quantity_id, "ConservationLaw.quantity_id")


@dataclass(frozen=True, slots=True)
class AmbiguityManifold:
    """Set of unresolved semantic candidates with explicit resolution condition."""

    manifold_id: str
    candidate_ids: tuple[str, ...]
    candidate_kinds: tuple[str, ...]
    resolution_condition: str
    resolved_id: str | None = None

    def __post_init__(self) -> None:
        _require_nonempty(self.manifold_id, "AmbiguityManifold.manifold_id")
        if isinstance(self.candidate_ids, dict) or isinstance(self.candidate_kinds, dict):
            raise ValidationError("AmbiguityManifold candidates must not be dict blobs")
        if not self.candidate_ids:
            raise ValidationError("AmbiguityManifold.candidate_ids must be non-empty")
        if len(self.candidate_ids) != len(self.candidate_kinds):
            raise ValidationError(
                "AmbiguityManifold candidate_ids/kinds length mismatch"
            )
        _require_nonempty(
            self.resolution_condition, "AmbiguityManifold.resolution_condition"
        )
        if self.resolved_id is not None and self.resolved_id not in self.candidate_ids:
            raise ValidationError("resolved_id must be one of candidate_ids")

    @property
    def resolved(self) -> bool:
        return self.resolved_id is not None and len(self.candidate_ids) == 1


@dataclass(frozen=True, slots=True)
class MissingReferent:
    """Absent antecedent/owner/unit/time — never silently filled."""

    referent_id: str
    role: str
    expected_kind: str
    context: str = ""

    def __post_init__(self) -> None:
        _require_nonempty(self.referent_id, "MissingReferent.referent_id")
        _require_nonempty(self.role, "MissingReferent.role")
        _require_nonempty(self.expected_kind, "MissingReferent.expected_kind")


def reject_untyped(value: Any, expected_name: str) -> None:
    """Public seam guard: refuse dict/str as authoritative complex primitive."""
    _reject_dict_blob(value, expected_name)
    if isinstance(value, str) and expected_name in {
        "Event",
        "Quantity",
        "AmbiguityManifold",
        "Entity",
        "Container",
    }:
        raise ValidationError(
            f"{expected_name} must not be a bare string as authoritative representation"
        )
