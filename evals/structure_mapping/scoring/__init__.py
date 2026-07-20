"""Scoring-only helpers for structure-mapping evals.

**CRITICAL:** These modules load gold structure labels. They must never be
imported by ``generate/structure_mapping`` (the mapper). Tests that audit
blindness check this import boundary.
"""

from evals.structure_mapping.scoring.labels import (
    S1_HOLDOUT_CASE_IDS,
    load_structure_labels,
    score_label,
)

__all__ = [
    "S1_HOLDOUT_CASE_IDS",
    "load_structure_labels",
    "score_label",
]
