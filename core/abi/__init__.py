"""CORE ABI namespace.

Exposes GeometricDelta and its validation routines.
"""

from core.abi.geometric_delta import GeometricDelta
from core.abi.geometric_delta_validator import (
    GeometricDeltaValidationError,
    validate_geometric_delta,
)

__all__ = [
    "GeometricDelta",
    "GeometricDeltaValidationError",
    "validate_geometric_delta",
]
