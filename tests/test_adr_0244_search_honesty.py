"""ADR-0244 §2.4 search-honesty pins (cohesion directive Mandate 6).

The Fibonacci section search is a Bracketed Local refiner: it observes a
*sampled* unimodality violation (finite samples cannot prove global
unimodality), fails closed with the honestly-named reason, and never silently
substitutes a fallback parameter in-path. ``propose_kappa_from_search`` keeps
the κ = 1.0 no-op on failure (the unchanged-threshold policy) but returns the
typed failure so a caller can tell "proposed 1.0" from "failed → holding 1.0".
"""

from __future__ import annotations

import math
from pathlib import Path

from core.physics.fibonacci_search import (
    BASELINE_KAPPA,
    BoundedUnimodalObjective,
    FibonacciSearchCertificate,
    OptimizationFailure,
    _unimodality_ok,
    fibonacci_section_search,
    propose_kappa_from_search,
)


def _obj(lo: float, hi: float, budget: int = 16) -> BoundedUnimodalObjective:
    return BoundedUnimodalObjective(
        lower=lo,
        upper=hi,
        evaluation_budget=budget,
        objective_id="search_honesty_test",
        objective_version="v1",
    )


def _multimodal(x: float) -> float:
    # Highly oscillatory → the golden-section samples straddle several extrema,
    # so the *sampled* trajectory is non-monotone and the violation fires. (A
    # smooth bimodal, by contrast, converges to one local min — the search is a
    # Bracketed-Local refiner and reports a certificate for that min, not a
    # violation. The violation is an honest-sample observation, not a global
    # unimodality proof.)
    return math.cos(8.0 * math.pi * x)


def _single_well(x: float) -> float:
    return (x - 0.3) ** 2


def test_sampled_unimodality_check_is_a_finite_sample_observation() -> None:
    # Monotone down-then-up over the sampled points → OK.
    assert _unimodality_ok({0.0: 3.0, 1.0: 1.0, 2.0: 2.0}) is True
    # A bump before the observed minimum → not monotone-to-min → violation.
    assert _unimodality_ok({0.0: 1.0, 1.0: 0.5, 2.0: 0.8, 3.0: 0.3}) is False


def test_multimodal_objective_returns_sampled_unimodality_violation() -> None:
    result = fibonacci_section_search(_obj(0.0, 1.0), _multimodal)
    assert isinstance(result, OptimizationFailure)
    assert result.reason == "sampled_unimodality_violation_observed"


def test_unimodal_objective_returns_certificate() -> None:
    result = fibonacci_section_search(_obj(-2.0, 2.0), _single_well)
    assert isinstance(result, FibonacciSearchCertificate)
    assert abs(result.minimizer - 0.3) < 0.2


def test_kappa_failure_is_legible_and_holds_the_no_op_baseline() -> None:
    result = fibonacci_section_search(_obj(0.0, 1.0), _multimodal)
    kappa, outcome = propose_kappa_from_search(result)
    # baseline κ = 1.0 is the unchanged-threshold no-op...
    assert kappa == BASELINE_KAPPA == 1.0
    # ...and the failure is legibly the second element, not swallowed.
    assert isinstance(outcome, OptimizationFailure)
    assert outcome.reason == "sampled_unimodality_violation_observed"


def test_kappa_success_returns_certified_minimizer() -> None:
    result = fibonacci_section_search(_obj(-2.0, 2.0), _single_well)
    kappa, outcome = propose_kappa_from_search(result)
    assert isinstance(outcome, FibonacciSearchCertificate)
    assert abs(kappa - 0.3) < 0.2


def test_no_stale_reason_string_in_source() -> None:
    src = Path(__file__).resolve().parents[1] / "core" / "physics" / "fibonacci_search.py"
    text = src.read_text(encoding="utf-8")
    assert "sampled_unimodality_violation_observed" in text
    assert "unimodality_violation_multiple_extrema_detected" not in text
