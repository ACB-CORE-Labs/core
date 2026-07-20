"""Layer C — Koine-inspired relation-time binding.

Forbidden: guessing absent antecedents, owners, units, or time frames.
Absent referents → typed MissingReferent.
"""

from __future__ import annotations

from dataclasses import dataclass

from core.semantic_primitives import (
    MissingReferent,
    Relation,
    RelationKind,
    TemporalFrame,
    TemporalKind,
    ValidationError,
)
from generate.linguistic_pipeline.layer_a_english import SurfaceConstraintSet
from generate.linguistic_pipeline.layer_b_hebrew import EventOperatorSet

_CUE_TO_RELATION: dict[str, RelationKind] = {
    "has": RelationKind.POSSESSION,
    "have": RelationKind.POSSESSION,
    "gave": RelationKind.SOURCE,
    "sold": RelationKind.SOURCE,
    "bought": RelationKind.TARGET,
    "more than": RelationKind.COMPARISON,
    "less than": RelationKind.COMPARISON,
    "each": RelationKind.MEMBERSHIP,
    "per": RelationKind.RATIO,
}


@dataclass(frozen=True, slots=True)
class RelationGraph:
    relations: tuple[Relation, ...]
    missing_referents: tuple[MissingReferent, ...]


@dataclass(frozen=True, slots=True)
class TemporalTopology:
    frames: tuple[TemporalFrame, ...]
    bindings: tuple[tuple[str, str], ...]  # (event_or_entity_id, frame_id)


def bind_koine_relation_time(
    surface: SurfaceConstraintSet,
    events: EventOperatorSet,
) -> tuple[RelationGraph, TemporalTopology]:
    if not isinstance(surface, SurfaceConstraintSet):
        raise ValidationError("Layer C requires SurfaceConstraintSet")
    if not isinstance(events, EventOperatorSet):
        raise ValidationError("Layer C requires EventOperatorSet")

    ent_ids = [e.candidate_id for e in surface.entities]
    relations: list[Relation] = []
    missing: list[MissingReferent] = []

    for i, rel in enumerate(surface.relations):
        kind = _CUE_TO_RELATION.get(rel.cue.lower(), RelationKind.OTHER)
        left = ent_ids[0] if ent_ids else ""
        right = ent_ids[1] if len(ent_ids) > 1 else ""
        if not left:
            missing.append(
                MissingReferent(
                    referent_id=f"miss:left:{i}",
                    role="left",
                    expected_kind="entity",
                    context=rel.cue,
                )
            )
            continue
        # Possession may bind to a quantity-item entity when only one person
        # name is present (right = first quantity_item entity if any).
        if not right and kind is RelationKind.POSSESSION:
            item_ids = [
                e.candidate_id
                for e in surface.entities
                if e.kind_hint == "quantity_item"
            ]
            if item_ids:
                right = item_ids[0]
        if not right and kind in {
            RelationKind.COMPARISON,
            RelationKind.POSSESSION,
            RelationKind.SOURCE,
            RelationKind.TARGET,
        }:
            missing.append(
                MissingReferent(
                    referent_id=f"miss:right:{i}",
                    role="right",
                    expected_kind="entity",
                    context=rel.cue,
                )
            )
            # Do not fabricate right — skip emitting a filled relation
            continue
        if not right:
            missing.append(
                MissingReferent(
                    referent_id=f"miss:right:{i}",
                    role="right",
                    expected_kind="entity",
                    context=rel.cue,
                )
            )
            continue
        relations.append(
            Relation(
                relation_id=f"grc_rel:{i}",
                kind=kind,
                left_entity_id=left,
                right_entity_id=right,
                polarity=True,
                provenance=rel.provenance,
            )
        )

    # Events without agent/source → missing referent
    for ev in events.events:
        if ev.agent_entity_id is None and "agent" in ev.unresolved_roles:
            missing.append(
                MissingReferent(
                    referent_id=f"miss:agent:{ev.event_id}",
                    role="agent",
                    expected_kind="entity",
                    context=ev.event_id,
                )
            )

    frames = (
        TemporalFrame(frame_id="frame:present", kind=TemporalKind.PRESENT),
        TemporalFrame(frame_id="frame:prior", kind=TemporalKind.PRIOR_COMPLETED),
    )
    bindings: list[tuple[str, str]] = []
    for cand in events.candidates:
        if cand.temporal_extent_kind is TemporalKind.PRIOR_COMPLETED:
            bindings.append((cand.candidate_id, "frame:prior"))
        else:
            bindings.append((cand.candidate_id, "frame:present"))

    return (
        RelationGraph(relations=tuple(relations), missing_referents=tuple(missing)),
        TemporalTopology(frames=frames, bindings=tuple(bindings)),
    )
