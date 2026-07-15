"""core.physics.fibonacci_search — evidence-gated Fibonacci section search (ADR-0242 V1).

Deterministic 1D unimodal minimization for construction / calibration /
GoldTether κ-style scalar brackets. Not a serve-path operator (A-04 quarantine).

Public result is always a typed ``FibonacciSearchCertificate`` or
``OptimizationFailure`` — never a bare float (Drive evidence discipline).

Fail-closed on:
  * nonfinite objective values
  * invalid bounds / budget
  * sampled unimodality violation (values must decrease to the observed
    minimum then increase when sorted by coordinate)
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field
from typing import Callable, Union


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
        if not str(self.objective_id).strip():
            raise ValueError("objective_id is required")
        if not str(self.objective_version).strip():
            raise ValueError("objective_version is required")


@dataclass(frozen=True, slots=True)
class FibonacciSearchCertificate:
    """Cryptographically content-addressed, replayable optimization result."""

    minimizer: float
    final_interval: tuple[float, float]
    evaluations: int
    ordered_points: tuple[float, ...]
    ordered_values: tuple[float, ...]
    objective_id: str
    objective_version: str
    cert_id: str = field(default="")

    def __post_init__(self) -> None:
        if not self.cert_id:
            object.__setattr__(self, "cert_id", _cert_digest(self))

    def as_dict(self) -> dict[str, object]:
        return {
            "kind": "FibonacciSearchCertificate",
            "cert_id": self.cert_id,
            "minimizer": self.minimizer,
            "final_interval": list(self.final_interval),
            "evaluations": self.evaluations,
            "ordered_points": list(self.ordered_points),
            "ordered_values": list(self.ordered_values),
            "objective_id": self.objective_id,
            "objective_version": self.objective_version,
        }


@dataclass(frozen=True, slots=True)
class OptimizationFailure:
    """Typed failure — never silently accept a candidate minimizer."""

    reason: str
    final_interval: tuple[float, float]
    evaluations: int
    objective_id: str
    objective_version: str

    def as_dict(self) -> dict[str, object]:
        return {
            "kind": "OptimizationFailure",
            "reason": self.reason,
            "final_interval": list(self.final_interval),
            "evaluations": self.evaluations,
            "objective_id": self.objective_id,
            "objective_version": self.objective_version,
        }


# Backward-compat view (cohesion sketches). Prefer Certificate | Failure.
@dataclass(slots=True)
class SearchTrace:
    best_observed_point: float
    eval_sequence: list[float] = field(default_factory=list)
    certificate: dict = field(default_factory=dict)


SearchResult = Union[FibonacciSearchCertificate, OptimizationFailure]

BASELINE_KAPPA: float = 1.0


def fibonacci_number(n: int) -> int:
    """F_0=0, F_1=1, … standard Fibonacci. n may be 0."""
    if n < 0:
        raise ValueError("fibonacci index must be non-negative")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def _fibonacci(n: int) -> int:
    return fibonacci_number(n)


def _cert_digest(cert: FibonacciSearchCertificate) -> str:
    payload = {
        "minimizer": cert.minimizer,
        "final_interval": list(cert.final_interval),
        "evaluations": cert.evaluations,
        "ordered_points": list(cert.ordered_points),
        "ordered_values": list(cert.ordered_values),
        "objective_id": cert.objective_id,
        "objective_version": cert.objective_version,
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _unimodality_ok(eval_values: dict[float, float]) -> bool:
    sorted_points = sorted(eval_values.keys())
    if len(sorted_points) < 2:
        return True
    min_idx = 0
    min_val = float("inf")
    for i, x in enumerate(sorted_points):
        v = eval_values[x]
        if v < min_val:
            min_val = v
            min_idx = i
    for i in range(min_idx):
        left = eval_values[sorted_points[i]]
        right = eval_values[sorted_points[i + 1]]
        if left < right - 1e-9:
            return False
    for i in range(min_idx, len(sorted_points) - 1):
        left = eval_values[sorted_points[i]]
        right = eval_values[sorted_points[i + 1]]
        if left > right + 1e-9:
            return False
    return True


def _failure(
    objective: BoundedUnimodalObjective,
    *,
    reason: str,
    a: float,
    b: float,
    evaluations: int,
) -> OptimizationFailure:
    return OptimizationFailure(
        reason=reason,
        final_interval=(float(a), float(b)),
        evaluations=int(evaluations),
        objective_id=objective.objective_id,
        objective_version=objective.objective_version,
    )


def fibonacci_section_search(
    objective: BoundedUnimodalObjective,
    func: Callable[[float], float],
) -> SearchResult:
    """Fibonacci section search with evidence-gated result.

    Returns :class:`FibonacciSearchCertificate` on success or
    :class:`OptimizationFailure` on any fail-closed condition.
    Never returns a bare float.
    """
    n = int(objective.evaluation_budget)
    a0 = float(objective.lower)
    b0 = float(objective.upper)
    a, b = a0, b0

    if n < 2:
        return _failure(
            objective,
            reason="budget_too_low_for_unimodal_search",
            a=a0,
            b=b0,
            evaluations=0,
        )

    f_n_plus_1 = _fibonacci(n + 1)
    f_n_minus_1 = _fibonacci(n - 1)
    f_n = _fibonacci(n)
    if f_n_plus_1 == 0:
        return _failure(
            objective,
            reason="degenerate_fibonacci_schedule",
            a=a0,
            b=b0,
            evaluations=0,
        )

    c = a + (f_n_minus_1 / f_n_plus_1) * (b - a)
    d = a + (f_n / f_n_plus_1) * (b - a)

    points: list[float] = []
    values: list[float] = []
    eval_values: dict[float, float] = {}

    def _eval(x: float) -> float | OptimizationFailure:
        if x < objective.lower - 1e-12 or x > objective.upper + 1e-12:
            return _failure(
                objective,
                reason=f"bounds_violation: evaluated {x} outside [{objective.lower}, {objective.upper}]",
                a=a,
                b=b,
                evaluations=len(points),
            )
        try:
            y = float(func(x))
        except Exception as exc:  # noqa: BLE001 — typed failure surface
            return _failure(
                objective,
                reason=f"evaluation_error: {type(exc).__name__}: {exc}",
                a=a,
                b=b,
                evaluations=len(points),
            )
        if not math.isfinite(y):
            return _failure(
                objective,
                reason=f"nonfinite_objective_value_at_{x}",
                a=a,
                b=b,
                evaluations=len(points),
            )
        return y

    r_c = _eval(c)
    if isinstance(r_c, OptimizationFailure):
        return r_c
    r_d = _eval(d)
    if isinstance(r_d, OptimizationFailure):
        return r_d
    fc, fd = r_c, r_d
    points.extend([c, d])
    values.extend([fc, fd])
    eval_values[c] = fc
    eval_values[d] = fd

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
            r_c = _eval(c)
            if isinstance(r_c, OptimizationFailure):
                return r_c
            fc = r_c
            points.append(c)
            values.append(fc)
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
            r_d = _eval(d)
            if isinstance(r_d, OptimizationFailure):
                return r_d
            fd = r_d
            points.append(d)
            values.append(fd)
            eval_values[d] = fd
            if fd < best_f:
                best_f = fd
                best_x = d
        k += 1

    if not _unimodality_ok(eval_values):
        return _failure(
            objective,
            reason="unimodality_violation_multiple_extrema_detected",
            a=a,
            b=b,
            evaluations=len(points),
        )

    # Drive cert uses midpoint of final bracket; track also retains best sample.
    minimizer = 0.5 * (a + b)
    # Prefer best sample if it lies inside final bracket (more accurate under noise).
    if a - 1e-15 <= best_x <= b + 1e-15:
        minimizer = float(best_x)

    return FibonacciSearchCertificate(
        minimizer=float(minimizer),
        final_interval=(float(a), float(b)),
        evaluations=len(points),
        ordered_points=tuple(float(p) for p in points),
        ordered_values=tuple(float(v) for v in values),
        objective_id=objective.objective_id,
        objective_version=objective.objective_version,
    )


def propose_kappa_from_search(
    result: SearchResult,
    *,
    baseline: float = BASELINE_KAPPA,
) -> tuple[float, SearchResult]:
    """Evidence-gated κ: cert → minimizer; failure → baseline (default 1.0).

    Never promotes COHERENT standing or mutates identity — caller telemetry only.
    """
    if isinstance(result, FibonacciSearchCertificate):
        return float(result.minimizer), result
    return float(baseline), result


def search_trace_from_result(result: SearchResult) -> SearchTrace:
    """Legacy adapter for sketches that expect SearchTrace (raises on failure)."""
    if isinstance(result, OptimizationFailure):
        raise ValueError(result.reason)
    return SearchTrace(
        best_observed_point=result.minimizer,
        eval_sequence=list(result.ordered_points),
        certificate={
            "budget": result.evaluations,
            "objective_id": result.objective_id,
            "objective_version": result.objective_version,
            "lower_bound": result.final_interval[0],
            "upper_bound": result.final_interval[1],
            "best_value": None,
            "n_evals": result.evaluations,
            "cert_id": result.cert_id,
            "kind": "FibonacciSearchCertificate",
        },
    )


__all__ = [
    "BASELINE_KAPPA",
    "BoundedUnimodalObjective",
    "FibonacciSearchCertificate",
    "OptimizationFailure",
    "SearchResult",
    "SearchTrace",
    "fibonacci_number",
    "fibonacci_section_search",
    "propose_kappa_from_search",
    "search_trace_from_result",
]
