"""Overlapping-waves selector (ADR-0252 stage 5 / revive ADR-0174).

Given a role-graph, hold candidate canonical mappings, rank them, pick the
best, **refuse on ambiguity/tie**, and suppress surface-similarity as the
decision driver (structure predicates only).

Blind to gold labels. Deterministic ranking.
"""

from __future__ import annotations

from dataclasses import dataclass

from generate.structure_mapping.mapper import (
    MAPPERS,
    StructureMapRefuse,
    StructureMapResult,
)
from generate.structure_mapping.role_predicate import RoleGraph

# Systematicity / specificity scores: more constraining pure-family matches
# rank higher. Ties at the same score → refuse.
_FAMILY_SCORE: dict[str, int] = {
    # Multi-predicate pure families outrank single-predicate ones.
    "S1": 30,  # compare + contain + total
    "S4": 30,  # compare_add + contain + total
    "S2": 25,  # transfer + 2 contains
    "S3": 10,  # single rate
}


@dataclass(frozen=True, slots=True)
class SelectorResult:
    """Selected canonical mapping, or a refuse with diagnostics."""

    selected: StructureMapResult | None
    refused: bool
    reason: str | None
    candidates: tuple[StructureMapResult, ...]
    refused_families: tuple[tuple[str, str], ...]
    """(structure_id, refuse_reason) for families that did not match."""


def select_structure(
    role_graph: RoleGraph,
    *,
    families: tuple[str, ...] = ("S1", "S2", "S3", "S4"),
) -> SelectorResult:
    """Rank pure-family mappers; pick unique best; refuse on empty or tie.

    Surface attributes (entity names, numbers) never affect ranking — only
    which pure-family mappers admit the role graph and their fixed scores.
    """
    if not isinstance(role_graph, RoleGraph):
        raise TypeError(
            f"select_structure expects RoleGraph, got {type(role_graph).__name__}"
        )

    hits: list[StructureMapResult] = []
    refuses: list[tuple[str, str]] = []
    for fam in families:
        mapper = MAPPERS.get(fam)
        if mapper is None:
            refuses.append((fam, "unknown_family"))
            continue
        out = mapper(role_graph)
        if isinstance(out, StructureMapResult):
            hits.append(out)
        else:
            assert isinstance(out, StructureMapRefuse)
            refuses.append((fam, out.reason))

    if not hits:
        return SelectorResult(
            selected=None,
            refused=True,
            reason="no_family_matched",
            candidates=(),
            refused_families=tuple(refuses),
        )

    # Rank by systematicity score; secondary key = structure_id for stability.
    ranked = sorted(
        hits,
        key=lambda m: (-_FAMILY_SCORE.get(m.structure_id, 0), m.structure_id),
    )
    best = ranked[0]
    best_score = _FAMILY_SCORE.get(best.structure_id, 0)
    tied = [m for m in ranked if _FAMILY_SCORE.get(m.structure_id, 0) == best_score]
    if len(tied) > 1:
        ids = ",".join(sorted(m.structure_id for m in tied))
        return SelectorResult(
            selected=None,
            refused=True,
            reason=f"ambiguous_tie:{ids}",
            candidates=tuple(ranked),
            refused_families=tuple(refuses),
        )

    return SelectorResult(
        selected=best,
        refused=False,
        reason=None,
        candidates=tuple(ranked),
        refused_families=tuple(refuses),
    )
