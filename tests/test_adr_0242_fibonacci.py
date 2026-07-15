"""ADR-0242 — Fibonacci section search behavioral pins."""

from __future__ import annotations

import pytest

from core.physics.fibonacci_search import (
    BoundedUnimodalObjective,
    fibonacci_section_search,
)


def test_fibonacci_search_hits_known_unimodal_min_within_1e_3():
    objective = BoundedUnimodalObjective(
        lower=0.1,
        upper=2.0,
        evaluation_budget=20,
        objective_id="test_id",
        objective_version="v1",
    )

    def func(x: float) -> float:
        return (x - 0.789) ** 2

    trace = fibonacci_section_search(objective, func)
    assert abs(trace.best_observed_point - 0.789) < 1e-3
    assert len(trace.eval_sequence) == 20


def test_fibonacci_search_eval_count_equals_budget():
    objective = BoundedUnimodalObjective(
        lower=-5.0,
        upper=5.0,
        evaluation_budget=15,
        objective_id="test_id2",
        objective_version="v1",
    )

    def func(x: float) -> float:
        return x**2

    trace = fibonacci_section_search(objective, func)
    assert len(trace.eval_sequence) == 15
    assert trace.certificate["n_evals"] == 15


def test_fibonacci_search_rejects_nan_objective():
    objective = BoundedUnimodalObjective(
        lower=-1.0,
        upper=1.0,
        evaluation_budget=10,
        objective_id="nan",
        objective_version="v1",
    )

    def func(x: float) -> float:
        return float("nan")

    with pytest.raises(ValueError, match="nonfinite"):
        fibonacci_section_search(objective, func)


def test_fibonacci_search_unimodality_violation_fail_closed():
    objective = BoundedUnimodalObjective(
        lower=-2.0,
        upper=2.0,
        evaluation_budget=10,
        objective_id="multi",
        objective_version="v1",
    )

    def func(x: float) -> float:
        # Multiple extrema: x^4 - x^2
        return x**4 - x**2

    with pytest.raises(ValueError, match="unimodality"):
        fibonacci_section_search(objective, func)
