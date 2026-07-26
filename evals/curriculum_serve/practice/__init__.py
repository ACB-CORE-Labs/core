"""Sealed practice for curriculum-grounded serving (ADR-0262/0264, Phase C).

The missing producer named by ``chat/curriculum_serve_license.py``'s docstring:
that module reads ``chat/data/curriculum_serve_ledger.json`` and declares
``evals.curriculum_serve.practice.runner.seal_ledger`` "the only writer" of it.
Until this package existed the writer did not, so authoring curriculum could not
earn a license at any volume.
"""

from evals.curriculum_serve.practice.generator import (
    CASES_PER_BAND,
    CurriculumOracleTether,
    CurriculumSolver,
    QueryAtom,
    all_gold_problems,
    assert_practice_atoms_distinct,
    band_cases,
    routable_atoms,
    taught_atoms,
)

__all__ = [
    "CASES_PER_BAND",
    "CurriculumOracleTether",
    "CurriculumSolver",
    "QueryAtom",
    "all_gold_problems",
    "assert_practice_atoms_distinct",
    "band_cases",
    "routable_atoms",
    "taught_atoms",
]
