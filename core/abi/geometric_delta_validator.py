"""Validation contracts for GeometricDelta.

Ensures that any update to the Master substrate complies with Cl(4,1) shape
invariants, provenance metadata, and truth-seeking constraints.
"""

import os
from typing import Tuple
from core.abi.geometric_delta import GeometricDelta
from core.epistemic_state import EpistemicState

DEFAULT_TOLERANCE = 1e-6

class GeometricDeltaValidationError(ValueError):
    """Raised when a GeometricDelta violates the ABI contract."""
    pass

def validate_geometric_delta(delta: GeometricDelta, tolerance: float | None = None) -> Tuple[bool, str]:
    """Validates the structure, metadata, and closure of a GeometricDelta.
    
    Returns:
        (True, "") if valid.
        (False, reason) if invalid.
        
    Raises:
        GeometricDeltaValidationError: If strict checks are failed.
    """
    if tolerance is None:
        try:
            tolerance = float(os.getenv("CORE_ABI_TOLERANCE", str(DEFAULT_TOLERANCE)))
        except ValueError:
            tolerance = DEFAULT_TOLERANCE

    # 1. Shape and basis check
    if not isinstance(delta.delta_versor, list):
        raise GeometricDeltaValidationError("delta_versor must be a list of floats")
    if len(delta.delta_versor) != 32:
        raise GeometricDeltaValidationError(
            f"delta_versor must have exactly 32 components, got {len(delta.delta_versor)}"
        )
    if not all(isinstance(x, (int, float)) for x in delta.delta_versor):
        raise GeometricDeltaValidationError("delta_versor must contain only numeric values")

    # 2. Epistemic state check
    if not isinstance(delta.epistemic, EpistemicState):
        raise GeometricDeltaValidationError(
            f"epistemic must be an instance of EpistemicState, got {type(delta.epistemic)}"
        )

    # 3. Provenance structure check
    if not isinstance(delta.provenance, dict):
        raise GeometricDeltaValidationError("provenance must be a dictionary")
    
    required_provenance_keys = {"source", "time", "hash", "adr_refs"}
    missing_keys = required_provenance_keys - set(delta.provenance.keys())
    if missing_keys:
        raise GeometricDeltaValidationError(
            f"provenance missing required keys: {missing_keys}"
        )

    # 4. AMR scope structure check
    if not isinstance(delta.amr_scope, dict):
        raise GeometricDeltaValidationError("amr_scope must be a dictionary")

    # 5. Closure check stub
    # Delegates to guarded projector check (scale + monotone Newton).
    # For now, this is a placeholder/contract interface.
    # In Sopher or CORE-rs, this triggers the algebraic Cl(4,1) projector.
    is_closed, residual = check_cl41_closure_invariant(delta.delta_versor, tolerance)
    if not is_closed:
        return False, f"Cl(4,1) closure invariant violated: residual {residual} > tolerance {tolerance}"

    return True, ""

def check_cl41_closure_invariant(versor: list[float], tolerance: float) -> Tuple[bool, float]:
    """Stub for Cl(4,1) algebraic closure verification.
    
    In full implementation, this calls core-rs or mlx_cl41 to verify
    ||F * reverse(F) - 1||_F < tolerance.
    """
    # Simple placeholder: for now, assume valid or check a simple norm condition.
    # If the user has set CORE_STRICT_PROJECTOR, we would execute the guarded projector.
    # We return True and a dummy residual of 0.0 for this abstract stub.
    return True, 0.0
