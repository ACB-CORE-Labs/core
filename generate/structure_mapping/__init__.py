"""Track B symbolic structure-mapping (ADR-0252 §6 / Increment 1).

Off-serving. Discovers role correspondence via Gentner-style symbolic
relational graph match — not geometric Procrustes (ruled NO-GO: Kabsch
presupposes the correspondence structure-mapping must discover).

Public surface for the S1 vertical slice only. Gold structure labels
(S1–S4) never enter the mapper; scoring helpers live in
``evals/structure_mapping/scoring`` and must not be imported here.
"""

from __future__ import annotations

from generate.structure_mapping.canonicals import S1_CANONICAL, CanonicalStructure
from generate.structure_mapping.convert import graph_to_role_graph
from generate.structure_mapping.mapper import (
    StructureMapRefuse,
    StructureMapResult,
    map_to_s1,
)
from generate.structure_mapping.role_predicate import (
    PredicateKind,
    RoleGraph,
    RolePredicate,
    RoleTerm,
)
from generate.structure_mapping.solve_s1 import (
    S1SolveOutcome,
    solve_s1_binding,
    try_s1_structure_map_and_solve,
)

__all__ = [
    "CanonicalStructure",
    "PredicateKind",
    "RoleGraph",
    "RolePredicate",
    "RoleTerm",
    "S1_CANONICAL",
    "S1SolveOutcome",
    "StructureMapRefuse",
    "StructureMapResult",
    "graph_to_role_graph",
    "map_to_s1",
    "solve_s1_binding",
    "try_s1_structure_map_and_solve",
]
