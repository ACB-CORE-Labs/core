"""Evaluation boundary helpers for numeric tolerance.

Provides a single controlled boundary for comparing outputs from the geometric
algebra substrate (which uses floats) to exact test harness expectations. This
is NOT a semantic relaxation; it is purely a measurement tolerance for float 
precision (e.g. 21.000000000007148 vs 21).
"""
import math
from typing import Union

def assert_eval_close(actual: Union[float, int, None], expected: Union[float, int]) -> None:
    """Assert that an actual value is numerically equivalent to expected.

    This helper enforces a tight tolerance (1e-6) for geometric noise. It must
    only be used at the final evaluation boundary for numerical values (e.g. 
    Quantity values, r.answer), NOT for semantic labels or discrete counts.
    """
    if actual is None and expected is None:
        return
    assert actual is not None, f"Expected {expected} but got None"
    assert expected is not None, f"Expected None but got {actual}"
    # The versor invariant condition is < 1e-6, so we use that as the maximum
    # allowable geometric drift threshold for scalar reads.
    assert math.isclose(actual, expected, rel_tol=1e-6, abs_tol=1e-6), (
        f"Numeric mismatch (float noise > 1e-6): actual={actual}, expected={expected}"
    )

def is_eval_close(actual: Union[float, int, None], expected: Union[float, int]) -> bool:
    """Check if an actual value is numerically equivalent to expected."""
    if actual is None and expected is None:
        return True
    if actual is None or expected is None:
        return False
    return math.isclose(actual, expected, rel_tol=1e-6, abs_tol=1e-6)
