"""core.physics.learning — ADR-0014 vault promotion criteria."""

from __future__ import annotations

from dataclasses import dataclass

from core.physics.energy import EnergyClass, EnergyProfile


@dataclass(frozen=True, slots=True)
class PromotionDecision:
    promote: bool
    reason: str
    energy_class: EnergyClass


class VaultPromotionPolicy:
    """Promote only settled, *geometrically* coherent regions to COHERENT.

    Stage 3A / Master Blueprint: COHERENT standing requires the unitary
    residual condition (``coherence_residual ≤ 1e-6`` by default), not a
    soft energy-band threshold alone. Tests may pass a looser
    ``residual_threshold`` explicitly for energy-class isolation fixtures;
    production ``VaultPromotionPolicy()`` uses the geometric floor.
    """

    def __init__(self, residual_threshold: float = 1e-6) -> None:
        if residual_threshold < 0.0:
            raise ValueError("residual_threshold must be non-negative")
        self.residual_threshold = float(residual_threshold)

    def decide(self, energy: EnergyProfile | None) -> PromotionDecision:
        if energy is None:
            return PromotionDecision(False, "missing_energy_profile", EnergyClass.E2)
        if not energy.energy_class.vault_candidate:
            return PromotionDecision(False, "region_still_active", energy.energy_class)
        # Full geometric unitarity gate for COHERENT promotion (Stage 3A).
        if energy.coherence_residual > self.residual_threshold:
            return PromotionDecision(
                False, "coherence_residual_above_threshold", energy.energy_class
            )
        # Residual must also be finite and non-negative (typed safety).
        r = float(energy.coherence_residual)
        if not (r == r) or r < 0.0:  # NaN or negative
            return PromotionDecision(False, "coherence_residual_invalid", energy.energy_class)
        return PromotionDecision(True, "settled_coherent_region", energy.energy_class)
