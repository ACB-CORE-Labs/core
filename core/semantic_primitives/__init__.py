"""Shared typed semantic primitives for linguistic → field compilation.

Authoritative representations are frozen validated dataclasses — never bare
dicts, free strings, or JSON blobs at the new compiler seams.

Linguistic layers may only *emit candidates* bound to these types. They must
not assign Cl(4,1) field state.
"""

from core.semantic_primitives.model import (
    AmbiguityManifold,
    ConservationLaw,
    Container,
    DimensionalType,
    Entity,
    Event,
    IdentityBridge,
    LogosConstraint,
    MissingReferent,
    Operator,
    OperatorClass,
    ProvenanceSpan,
    Quantity,
    Relation,
    RelationKind,
    TemporalExtent,
    TemporalFrame,
    TemporalKind,
    ValidationError,
)

__all__ = [
    "AmbiguityManifold",
    "ConservationLaw",
    "Container",
    "DimensionalType",
    "Entity",
    "Event",
    "IdentityBridge",
    "LogosConstraint",
    "MissingReferent",
    "Operator",
    "OperatorClass",
    "ProvenanceSpan",
    "Quantity",
    "Relation",
    "RelationKind",
    "TemporalExtent",
    "TemporalFrame",
    "TemporalKind",
    "ValidationError",
]
