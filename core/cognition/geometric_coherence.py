"""Turn-level geometric coherence verdict (Master Blueprint Stage 3A).

Ownership model (deliberate dual taxonomy — do NOT collapse names):

* ``teaching.epistemic.EpistemicStatus`` — vault / pack durable standing
  (SPECULATIVE | COHERENT | CONTESTED | FALSIFIED). Mutation only via
  ``vault/store.py`` (INV-29).
* ``core.epistemic_state.EpistemicState`` — turn / surface taxonomy for
  dialogue observability (perceived, verified, decoded, …). **No** member
  named COHERENT — vault COHERENT maps to DECODED via
  ``epistemic_state_for_vault_status``.

This module adds a third, geometry-native axis: whether the *field* closed
under versor + GoldTether residual checks on this turn. It never renames
EpistemicState and never stamps vault COHERENT by itself.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

import numpy as np

from algebra.backend import versor_condition
from core.physics.goldtether import coherence_residual

_CLOSURE = 1e-6


class GeometricCoherenceStatus(str, Enum):
    """Turn-level geometric standing — orthogonal to vault EpistemicStatus."""

    GEOMETRICALLY_VERIFIED = "geometrically_verified"
    UNVERIFIED = "unverified"
    REFUSED = "refused"


@dataclass(frozen=True, slots=True)
class GeometricCoherenceVerdict:
    """Pipeline-visible geometric coherence for one turn.

    ``GEOMETRICALLY_VERIFIED`` requires:
      * field present
      * versor_condition(F) < 1e-6
      * R_GoldTether ≤ 1e-6
    Identity leakage flags are observational while identity_wave_gate is off
    (ADR-0244 honest scope) and do not alone refuse this verdict unless
    ``boundary_violations`` is non-empty.
    """

    status: GeometricCoherenceStatus
    versor_condition: float
    goldtether_residual: float
    field_present: bool
    identity_boundary_breach: bool = False
    detail: str = ""

    @property
    def closed(self) -> bool:
        return self.status is GeometricCoherenceStatus.GEOMETRICALLY_VERIFIED

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "closed": self.closed,
            "versor_condition": float(self.versor_condition),
            "goldtether_residual": float(self.goldtether_residual),
            "field_present": bool(self.field_present),
            "identity_boundary_breach": bool(self.identity_boundary_breach),
            "detail": self.detail,
        }


def evaluate_geometric_coherence(
    F,
    *,
    identity_score=None,
    epsilon: float = _CLOSURE,
) -> GeometricCoherenceVerdict:
    """Compute turn geometric coherence from the live field versor."""
    if F is None:
        return GeometricCoherenceVerdict(
            status=GeometricCoherenceStatus.REFUSED,
            versor_condition=float("inf"),
            goldtether_residual=float("inf"),
            field_present=False,
            detail="missing_wave_field",
        )
    arr = np.asarray(F, dtype=np.float64)
    vc = float(versor_condition(arr))
    r_gt = float(coherence_residual(arr))
    boundary = bool(getattr(identity_score, "boundary_violations", ()) or ())
    if boundary:
        return GeometricCoherenceVerdict(
            status=GeometricCoherenceStatus.REFUSED,
            versor_condition=vc,
            goldtether_residual=r_gt,
            field_present=True,
            identity_boundary_breach=True,
            detail="identity_boundary_breach",
        )
    if vc >= float(epsilon) or r_gt > float(epsilon):
        return GeometricCoherenceVerdict(
            status=GeometricCoherenceStatus.UNVERIFIED,
            versor_condition=vc,
            goldtether_residual=r_gt,
            field_present=True,
            detail=f"versor_condition={vc:.3e}; R_GoldTether={r_gt:.3e}",
        )
    return GeometricCoherenceVerdict(
        status=GeometricCoherenceStatus.GEOMETRICALLY_VERIFIED,
        versor_condition=vc,
        goldtether_residual=r_gt,
        field_present=True,
        detail="versor_and_goldtether_closed",
    )
