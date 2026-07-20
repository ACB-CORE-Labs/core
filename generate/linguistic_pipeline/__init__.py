"""Trilingual constraint pipeline: English → Hebrew event → Koine relation-time → field.

Linguistic layers produce typed candidates only. Field integration alone may
close, leave ambiguous, or refuse. Articulation requires a closed proof trace.
"""

from generate.linguistic_pipeline.articulation import (
    ArticulationFirewallVerdict,
    ArticulatedClaim,
    articulate_from_proof,
    firewall_check,
)
from generate.linguistic_pipeline.field_integration import (
    AmbiguousFieldState,
    CoherentFieldState,
    FieldOutcome,
    integrate_constraints,
)
from generate.linguistic_pipeline.layer_a_english import (
    CandidateEntity,
    CandidateRelation,
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
from generate.linguistic_pipeline.pipeline import (
    LinguisticPipelineResult,
    run_linguistic_pipeline,
)

__all__ = [
    "AmbiguousFieldState",
    "ArticulatedClaim",
    "ArticulationFirewallVerdict",
    "CandidateEntity",
    "CandidateRelation",
    "CoherentFieldState",
    "EventOperatorSet",
    "FieldOutcome",
    "LinguisticPipelineResult",
    "RelationGraph",
    "SurfaceConstraintSet",
    "TemporalTopology",
    "articulate_from_proof",
    "bind_koine_relation_time",
    "classify_hebrew_events",
    "extract_english_surface",
    "firewall_check",
    "integrate_constraints",
    "run_linguistic_pipeline",
]
