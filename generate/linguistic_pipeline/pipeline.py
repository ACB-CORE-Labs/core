"""End-to-end linguistic constraint → field → articulation entry path."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from core.cognition.fail_closed import CoherenceRefusal
from generate.linguistic_pipeline.articulation import (
    ArticulationFirewallVerdict,
    articulate_from_proof,
)
from generate.linguistic_pipeline.field_integration import (
    AmbiguousFieldState,
    CoherentFieldState,
    FieldOutcome,
    integrate_constraints,
    outcome_as_dict,
    outcome_kind,
)
from generate.linguistic_pipeline.layer_a_english import (
    SurfaceConstraintSet,
    extract_english_surface,
)
from generate.linguistic_pipeline.layer_b_hebrew import (
    EventOperatorSet,
    classify_hebrew_events,
)
from generate.linguistic_pipeline.layer_c_koine import (
    RelationGraph,
    TemporalTopology,
    bind_koine_relation_time,
)


@dataclass(frozen=True, slots=True)
class LinguisticPipelineResult:
    surface_constraints: SurfaceConstraintSet
    event_operators: EventOperatorSet
    relation_graph: RelationGraph
    temporal_topology: TemporalTopology
    field_outcome: FieldOutcome
    articulation: ArticulationFirewallVerdict | CoherenceRefusal

    @property
    def outcome_kind(self) -> str:
        return outcome_kind(self.field_outcome)

    def as_dict(self) -> dict[str, Any]:
        art: dict[str, Any]
        if isinstance(self.articulation, CoherenceRefusal):
            art = self.articulation.as_dict()
        else:
            art = {
                "surface": self.articulation.surface,
                "hallucinated": list(self.articulation.hallucinated),
                "clean": self.articulation.clean,
                "claims": [c.text for c in self.articulation.legal_claims],
            }
        return {
            "outcome_kind": self.outcome_kind,
            "field": outcome_as_dict(self.field_outcome),
            "articulation": art,
            "missing_referents": [
                m.referent_id for m in self.relation_graph.missing_referents
            ],
            "manifolds": [m.manifold_id for m in self.event_operators.manifolds],
        }


def run_linguistic_pipeline(
    text: str,
    *,
    force_geometry_fail: bool = False,
) -> LinguisticPipelineResult:
    """Shipped public entry: English text → typed outcomes only."""
    surface = extract_english_surface(text)
    events = classify_hebrew_events(surface)
    relation_graph, temporal = bind_koine_relation_time(surface, events)
    outcome = integrate_constraints(
        surface,
        events,
        relation_graph,
        temporal,
        force_geometry_fail=force_geometry_fail,
    )
    articulation = articulate_from_proof(outcome)
    return LinguisticPipelineResult(
        surface_constraints=surface,
        event_operators=events,
        relation_graph=relation_graph,
        temporal_topology=temporal,
        field_outcome=outcome,
        articulation=articulation,
    )


__all__ = [
    "LinguisticPipelineResult",
    "run_linguistic_pipeline",
    "CoherentFieldState",
    "AmbiguousFieldState",
    "CoherenceRefusal",
]
