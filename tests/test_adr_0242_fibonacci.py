"""ADR-0242 V1 — evidence-gated Fibonacci section search."""

from __future__ import annotations

from core.physics.fibonacci_search import (
    BASELINE_KAPPA,
    BoundedUnimodalObjective,
    FibonacciSearchCertificate,
    OptimizationFailure,
    fibonacci_section_search,
    propose_kappa_from_search,
)


def test_fibonacci_search_returns_certificate_near_known_min():
    objective = BoundedUnimodalObjective(
        lower=0.1,
        upper=2.0,
        evaluation_budget=20,
        objective_id="test_id",
        objective_version="v1",
    )

    def func(x: float) -> float:
        return (x - 0.789) ** 2

    result = fibonacci_section_search(objective, func)
    assert isinstance(result, FibonacciSearchCertificate)
    assert abs(result.minimizer - 0.789) < 1e-3
    assert result.evaluations == 20
    assert len(result.ordered_points) == 20
    assert len(result.ordered_values) == 20
    assert result.cert_id
    assert len(result.cert_id) == 64


def test_certificate_digest_stable_dual_run():
    objective = BoundedUnimodalObjective(
        lower=-5.0,
        upper=5.0,
        evaluation_budget=15,
        objective_id="stable",
        objective_version="v1",
    )

    def func(x: float) -> float:
        return x**2

    a = fibonacci_section_search(objective, func)
    b = fibonacci_section_search(objective, func)
    assert isinstance(a, FibonacciSearchCertificate)
    assert isinstance(b, FibonacciSearchCertificate)
    assert a.cert_id == b.cert_id
    assert a.as_dict() == b.as_dict()


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

    result = fibonacci_section_search(objective, func)
    assert isinstance(result, FibonacciSearchCertificate)
    assert result.evaluations == 15


def test_fibonacci_search_nonfinite_returns_failure():
    objective = BoundedUnimodalObjective(
        lower=-1.0,
        upper=1.0,
        evaluation_budget=10,
        objective_id="nan",
        objective_version="v1",
    )

    def func(x: float) -> float:
        return float("nan")

    result = fibonacci_section_search(objective, func)
    assert isinstance(result, OptimizationFailure)
    assert "nonfinite" in result.reason


def test_fibonacci_search_unimodality_returns_failure():
    objective = BoundedUnimodalObjective(
        lower=-2.0,
        upper=2.0,
        evaluation_budget=10,
        objective_id="multi",
        objective_version="v1",
    )

    def func(x: float) -> float:
        return x**4 - x**2

    result = fibonacci_section_search(objective, func)
    assert isinstance(result, OptimizationFailure)
    assert "unimodality" in result.reason


def test_never_returns_bare_float():
    objective = BoundedUnimodalObjective(
        lower=0.0,
        upper=1.0,
        evaluation_budget=8,
        objective_id="type",
        objective_version="v1",
    )
    result = fibonacci_section_search(objective, lambda x: (x - 0.3) ** 2)
    assert not isinstance(result, float)
    assert isinstance(result, (FibonacciSearchCertificate, OptimizationFailure))


def test_propose_kappa_cert_uses_minimizer():
    objective = BoundedUnimodalObjective(
        lower=0.1,
        upper=2.0,
        evaluation_budget=16,
        objective_id="kappa",
        objective_version="v1",
    )
    result = fibonacci_section_search(objective, lambda x: (x - 0.5) ** 2)
    kappa, outcome = propose_kappa_from_search(result)
    assert isinstance(outcome, FibonacciSearchCertificate)
    assert abs(kappa - 0.5) < 1e-2


def test_propose_kappa_failure_falls_back_to_baseline():
    objective = BoundedUnimodalObjective(
        lower=-2.0,
        upper=2.0,
        evaluation_budget=10,
        objective_id="kappa_fail",
        objective_version="v1",
    )
    result = fibonacci_section_search(objective, lambda x: x**4 - x**2)
    kappa, outcome = propose_kappa_from_search(result)
    assert isinstance(outcome, OptimizationFailure)
    assert kappa == BASELINE_KAPPA
