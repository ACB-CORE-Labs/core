"""Layer B — Hebrew-inspired event classification (constraint candidates only).

Root labels never prove the intended operation alone. Multi-class roots retain
AmbiguityManifold entries; the field resolves.
"""

from __future__ import annotations

from dataclasses import dataclass

from core.semantic_primitives import (
    AmbiguityManifold,
    Event,
    Operator,
    OperatorClass,
    TemporalExtent,
    TemporalFrame,
    TemporalKind,
    ValidationError,
)
from generate.linguistic_pipeline.layer_a_english import (
    CandidateEntity,
    CandidateRelation,
    SurfaceConstraintSet,
)

# Authored multi-class roots: surface/root cue → possible operator classes.
# Multiple classes ⇒ AmbiguityManifold (no collapse).
_MULTI_CLASS_ROOTS: dict[str, tuple[OperatorClass, ...]] = {
    # Hebrew-inspired: מכר / sell can be transfer or removal depending on frame
    "sold": (OperatorClass.TRANSFER, OperatorClass.REMOVAL),
    "mkr": (OperatorClass.TRANSFER, OperatorClass.REMOVAL),
    "gave": (OperatorClass.TRANSFER, OperatorClass.REMOVAL),
    "ntn": (OperatorClass.TRANSFER, OperatorClass.REMOVAL),
    # single-class examples
    "bought": (OperatorClass.TRANSFER,),
    "earned": (OperatorClass.ACCUMULATION,),
    "lost": (OperatorClass.REMOVAL,),
    "made": (OperatorClass.CREATION,),
    "shared": (OperatorClass.PARTITION,),
}


@dataclass(frozen=True, slots=True)
class EventOperatorCandidate:
    candidate_id: str
    operator_class: OperatorClass
    participants: tuple[str, ...]
    direction: str
    conserved_quantity_hint: str
    source: str
    target: str
    temporal_extent_kind: TemporalKind
    root_cue: str
    confidence: float


@dataclass(frozen=True, slots=True)
class EventOperatorSet:
    events: tuple[Event, ...]
    operators: tuple[Operator, ...]
    candidates: tuple[EventOperatorCandidate, ...]
    manifolds: tuple[AmbiguityManifold, ...]

    def __post_init__(self) -> None:
        for e in self.events:
            if not isinstance(e, Event):
                raise ValidationError("EventOperatorSet.events must be Event instances")


def _entity_ids(entities: tuple[CandidateEntity, ...]) -> tuple[str, ...]:
    return tuple(e.candidate_id for e in entities)


def classify_hebrew_events(surface: SurfaceConstraintSet) -> EventOperatorSet:
    """Map Layer A candidates → event operator candidates; preserve multi-class roots."""
    if not isinstance(surface, SurfaceConstraintSet):
        raise ValidationError("Layer B requires SurfaceConstraintSet")

    participants = _entity_ids(surface.entities)
    candidates: list[EventOperatorCandidate] = []
    manifolds: list[AmbiguityManifold] = []
    events: list[Event] = []
    operators: list[Operator] = []

    cues: list[tuple[str, CandidateRelation | None]] = []
    for rel in surface.relations:
        cues.append((rel.cue.lower(), rel))
    # Also scan free text for multi-class root tokens not captured as relations
    lower = surface.source_text.lower()
    for root in _MULTI_CLASS_ROOTS:
        if root in lower and not any(c[0] == root for c in cues):
            cues.append((root, None))

    seen_roots: set[str] = set()
    for idx, (cue, rel) in enumerate(cues):
        if cue in seen_roots:
            continue
        classes = _MULTI_CLASS_ROOTS.get(cue)
        if classes is None:
            continue
        seen_roots.add(cue)
        source = participants[0] if participants else ""
        target = participants[1] if len(participants) > 1 else ""
        cand_ids: list[str] = []
        for j, op_class in enumerate(classes):
            cid = f"he_ev:{idx}:{j}:{op_class.value}"
            cand_ids.append(cid)
            candidates.append(
                EventOperatorCandidate(
                    candidate_id=cid,
                    operator_class=op_class,
                    participants=participants,
                    direction="source_to_target" if op_class is OperatorClass.TRANSFER else "egress",
                    conserved_quantity_hint="quantity:primary",
                    source=source,
                    target=target,
                    temporal_extent_kind=TemporalKind.PRIOR_COMPLETED,
                    root_cue=cue,
                    confidence=0.6 if len(classes) > 1 else 0.8,
                )
            )
            # Events are incomplete when multi-class — still emit typed Event
            # with unresolved operator class alternatives in manifold.
            ev = Event(
                event_id=cid,
                operator_class=op_class,
                agent_entity_id=source or None,
                patient_entity_id=target or None,
                source_entity_id=source or None,
                target_entity_id=target or None,
                conserved_quantity_id="quantity:primary" if surface.numerics else None,
                temporal_extent=TemporalExtent(
                    frame=TemporalFrame(
                        frame_id="frame:prior",
                        kind=TemporalKind.PRIOR_COMPLETED,
                    )
                ),
                direction="source_to_target",
                unresolved_roles=() if source and target else ("source", "target"),
            )
            events.append(ev)
            operators.append(
                Operator(
                    operator_id=f"op:{cid}",
                    operator_class=op_class,
                    event_id=cid,
                    executable_symbol=op_class.value,
                )
            )
        if len(classes) > 1:
            manifolds.append(
                AmbiguityManifold(
                    manifold_id=f"he_root:{cue}",
                    candidate_ids=tuple(cand_ids),
                    candidate_kinds=tuple(c.value for c in classes),
                    resolution_condition=(
                        "field_unique_admissible_operator_under_relation_graph"
                    ),
                )
            )

    return EventOperatorSet(
        events=tuple(events),
        operators=tuple(operators),
        candidates=tuple(candidates),
        manifolds=tuple(manifolds),
    )
