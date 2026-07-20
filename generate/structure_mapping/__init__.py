"""Track B symbolic structure-mapping (ADR-0252 §6 / Increments 1–2).

Off-serving. Discovers role correspondence via Gentner-style symbolic
relational graph match — not geometric Procrustes (ruled NO-GO: Kabsch
presupposes the correspondence structure-mapping must discover).

Public surface for S1–S4 + selector. Gold structure labels (S1–S4) never
enter the mapper; scoring helpers live in ``evals/structure_mapping/scoring``
and must not be imported here.
"""

from __future__ import annotations

from generate.structure_mapping.canonicals import (
    CANONICAL_BY_ID,
    CANONICAL_LIBRARY,
    S1_CANONICAL,
    S2_CANONICAL,
    S3_CANONICAL,
    S4_CANONICAL,
    CanonicalStructure,
)
from generate.structure_mapping.convert import graph_to_role_graph
from generate.structure_mapping.mapper import (
    StructureMapRefuse,
    StructureMapResult,
    map_to_s1,
    map_to_s2,
    map_to_s3,
    map_to_s4,
)
from generate.structure_mapping.pipeline import (
    PipelineTrace,
    run_structure_mapping_pipeline,
)
from generate.structure_mapping.role_predicate import (
    PredicateKind,
    RoleGraph,
    RolePredicate,
    RoleTerm,
)
from generate.structure_mapping.selector import SelectorResult, select_structure
from generate.structure_mapping.solve import (
    S1SolveOutcome,
    SolveOutcome,
    graph_from_s1_binding,
    solve_binding,
    solve_s1_binding,
    try_s1_structure_map_and_solve,
    try_structure_map_and_solve,
)

__all__ = [
    "CANONICAL_BY_ID",
    "CANONICAL_LIBRARY",
    "CanonicalStructure",
    "PipelineTrace",
    "PredicateKind",
    "RoleGraph",
    "RolePredicate",
    "RoleTerm",
    "S1_CANONICAL",
    "S1SolveOutcome",
    "S2_CANONICAL",
    "S3_CANONICAL",
    "S4_CANONICAL",
    "SelectorResult",
    "SolveOutcome",
    "StructureMapRefuse",
    "StructureMapResult",
    "graph_from_s1_binding",
    "graph_to_role_graph",
    "map_to_s1",
    "map_to_s2",
    "map_to_s3",
    "map_to_s4",
    "run_structure_mapping_pipeline",
    "select_structure",
    "solve_binding",
    "solve_s1_binding",
    "try_s1_structure_map_and_solve",
    "try_structure_map_and_solve",
]
