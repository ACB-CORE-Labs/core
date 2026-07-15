"""core.physics.fibonacci_search — fixed-budget Fibonacci section search (ADR-0242).

Deterministic 1D unimodal minimization for construction / calibration /
GoldTether κ-style scalar brackets. Not a serve-path operator (A-04 quarantine).

Fail-closed on:
  * nonfinite objective values
  * invalid bounds / budget
  * sampled unimodality violation (values must decrease to the observed
    minimum then increase when sorted by coordinate)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable


@dataclass(frozen=True, slots=True)
class BoundedUnimodalObjective:
    lower: float
    upper: float
    evaluation_budget: int
    objective_id: str
    objective_version: str

    def __post_init__(self) -> None:
        if self.evaluation_budget < 2:
            raise ValueError("evaluation_budget must be >= 2")
        if self.upper <= self.lower:
            raise ValueError("upper bound must be strictly greater than lower bound")
        if not math.isfinite(self.lower) or not math.isfinite(self.upper):
            raise ValueError("bounds must be finite")


@dataclass(slots=True)
class SearchTrace:
    best_observed_point: float
    eval_sequence: list[float] = field(default_factory=list)
    certificate: dict = field(default_factory=dict)


def _fibonacci(n: int) -> int:
    """F_0=0, F_1=1, … standard Fibonacci. n may be 0."""
    if n < 0:
        raise ValueError("fibonacci index must be non-negative")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def _assert_sampled_unimodality(eval_values: dict[float, float]) -> None:
    """Fail-closed if sorted samples are not unimodal about the observed min."""
    sorted_points = sorted(eval_values.keys())
    min_idx = 0
    min_val = float("inf")
    for i, x in enumerate(sorted_points):
        v = eval_values[x]
        if v < min_val:
            min_val = v
            min_idx = i

    # Strictly non-increasing toward min (allow float ties).
    for i in range(min_idx):
        left = eval_values[sorted_points[i]]
        right = eval_values[sorted_points[i + 1]]
        if left < right - 1e-9:
            raise ValueError(
                "unimodality violation detected (multiple extrema): "
                "values not decreasing before minimum."
            )

    # Strictly non-decreasing after min (allow float ties).
    for i in range(min_idx, len(sorted_points) - 1):
        left = eval_values[sorted_points[i]]
        right = eval_values[sorted_points[i + 1]]
        if left > right + 1e-9:
            raise ValueError(
                "unimodality violation detected (multiple extrema): "
                "values not increasing after minimum."
            )


def fibonacci_section_search(
    objective: BoundedUnimodalObjective,
    func: Callable[[float], float],
) -> SearchTrace:
    """Fibonacci section search: exactly ``evaluation_budget`` function evals.

    Returns :class:`SearchTrace` with ``best_observed_point``, ``eval_sequence``,
    and a small certificate dict (budget, ids, bounds).
    """
    n = int(objective.evaluation_budget)
    a = float(objective.lower)
    b = float(objective.upper)

    f_n_plus_1 = _fibonacci(n + 1)
    f_n_minus_1 = _fibonacci(n - 1)
    f_n = _fibonacci(n)

    c = a + (f_n_minus_1 / f_n_plus_1) * (b - a)
    d = a + (f_n / f_n_plus_1) * (b - a)

    def _eval(x: float) -> float:
        if x < objective.lower - 1e-12 or x > objective.upper + 1e-12:
            raise ValueError(f"bounds violation: evaluated {x} outside [{objective.lower}, {objective.upper}]")
        y = float(func(x))
        if not math.isfinite(y):
            raise ValueError(f"Objective function returned nonfinite value {y} at {x}")
        return y

    fc = _eval(c)
    fd = _eval(d)
    eval_sequence = [c, d]
    eval_values: dict[float, float] = {c: fc, d: fd}

    best_x = c if fc < fd else d
    best_f = min(fc, fd)

    k = 1
    while k < n - 1:
        if fc < fd:
            b = d
            d = c
            fd = fc
            f_n_minus_k_minus_1 = _fibonacci(n - k - 1)
            f_n_minus_k_plus_1 = _fibonacci(n - k + 1)
            c = a + (f_n_minus_k_minus_1 / f_n_minus_k_plus_1) * (b - a)
            fc = _eval(c)
            eval_sequence.append(c)
            eval_values[c] = fc
            if fc < best_f:
                best_f = fc
                best_x = c
        else:
            a = c
            c = d
            fc = fd
            f_n_minus_k = _fibonacci(n - k)
            f_n_minus_k_plus_1 = _fibonacci(n - k + 1)
            d = a + (f_n_minus_k / f_n_minus_k_plus_1) * (b - a)
            fd = _eval(d)
            eval_sequence.append(d)
            eval_values[d] = fd
            if fd < best_f:
                best_f = fd
                best_x = d
        k += 1

    _assert_sampled_unimodality(eval_values)

    certificate = {
        "budget": objective.evaluation_budget,
        "objective_id": objective.objective_id,
        "objective_version": objective.objective_version,
        "lower_bound": objective.lower,
        "upper_bound": objective.upper,
        "best_value": best_f,
        "n_evals": len(eval_sequence),
    }
    return SearchTrace(
        best_observed_point=float(best_x),
        eval_sequence=list(eval_sequence),
        certificate=certificate,
    )


__all__ = [
    "BoundedUnimodalObjective",
    "SearchTrace",
    "fibonacci_section_search",
]
