"""P10 Trace B — wave unitary residual → energy boundary + multi-scale τ.

ADR-0241 cohesion package P10:

1. **Wire wave residual into energy / trajectory gates** — coherence is not a
   free-floating float; it is :meth:`WaveManifold.measure_unitary_residual`.
2. **Multi-scale recency** ``τ_n = F_n · τ_0`` as a constants table (not dogma).
3. **Crystallization E0–E1 → holographic seal policy** — only low-energy
   classes with closed residual may SPECULATIVE-seal; COHERENT still requires
   authorized teaching review outside this module.

Serve path remains quarantined (no import from ``chat/runtime.py``).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

from core.physics.energy import EnergyClass, EnergyProfile, FieldEnergyOperator
from core.physics.fibonacci_search import fibonacci_number
from core.physics.trajectory_invariants import (
    TrajectoryAssessment,
    assess_trajectory,
)
from core.physics.wave_manifold import WaveManifold

_DEFAULT_EPSILON_DRIFT = 1e-6
_DEFAULT_TAU0 = 1.0


def wave_unitary_residual(
    psi: np.ndarray,
    *,
    manifold: WaveManifold | None = None,
    epsilon_drift: float = _DEFAULT_EPSILON_DRIFT,
) -> float:
    """Unitary residual ‖ψ~ψ − 1‖_F dual-checked via WaveManifold."""
    m = manifold if manifold is not None else WaveManifold(epsilon_drift=epsilon_drift)
    return float(m.measure_unitary_residual(psi))


def energy_profile_from_wave(
    psi: np.ndarray,
    *,
    operator: FieldEnergyOperator | None = None,
    manifold: WaveManifold | None = None,
    epsilon_drift: float = _DEFAULT_EPSILON_DRIFT,
    **compute_kwargs: object,
) -> EnergyProfile:
    """Build an EnergyProfile with coherence_residual from the wave field.

    Structural axes (convergence, activation, aspect) remain caller-supplied;
    residual is never invented — it is measured on ψ.
    """
    residual = wave_unitary_residual(
        psi, manifold=manifold, epsilon_drift=epsilon_drift
    )
    op = operator if operator is not None else FieldEnergyOperator()
    # FieldEnergyOperator.compute takes coherence_residual as float kwarg.
    kwargs = dict(compute_kwargs)
    kwargs["coherence_residual"] = residual
    return op.compute(**kwargs)  # type: ignore[arg-type]


def assess_wave_trajectory(
    versors: Sequence[np.ndarray],
    *,
    eps_trajectory: float = 1e-5,
    kappa: float = 1.0,
    dt: float = 1.0,
    epsilon_drift: float = _DEFAULT_EPSILON_DRIFT,
    manifold: WaveManifold | None = None,
) -> TrajectoryAssessment:
    """Trajectory gate with exertion energy from max wave unitary residual.

    ``E_exertion`` = max residual along the path.
    ``E_sensory`` = ``epsilon_drift`` (GoldTether-scale sensory budget).
    Closed unit paths stay under the boundary when residual ≤ κ · ε.
    """
    if not versors:
        # Delegate fail-closed empty handling to trajectory_invariants.
        return assess_trajectory(
            versors,
            E_exertion=0.0,
            E_sensory=float(epsilon_drift),
            eps_trajectory=eps_trajectory,
            kappa=kappa,
            dt=dt,
        )
    residuals = [
        wave_unitary_residual(v, manifold=manifold, epsilon_drift=epsilon_drift)
        for v in versors
    ]
    e_exertion = float(max(residuals))
    e_sensory = float(epsilon_drift)
    return assess_trajectory(
        versors,
        E_exertion=e_exertion,
        E_sensory=e_sensory,
        eps_trajectory=eps_trajectory,
        kappa=kappa,
        dt=dt,
    )


def fibonacci_tau_schedule(
    tau0: float = _DEFAULT_TAU0,
    *,
    levels: int = 8,
) -> tuple[float, ...]:
    """Multi-scale recency hierarchy τ_n = F_n · τ_0 for n = 1..levels.

    Constants table only — not a runtime dogma. F_1=1, F_2=1, F_3=2, …
    """
    t0 = float(tau0)
    if not (t0 > 0.0) or t0 != t0:  # NaN check via !=
        raise ValueError("tau0 must be a positive finite scalar")
    n = int(levels)
    if n < 1:
        raise ValueError("levels must be >= 1")
    return tuple(float(fibonacci_number(i) * t0) for i in range(1, n + 1))


def recency_band_index(age: float, taus: Sequence[float]) -> int:
    """Smallest band index with age ≤ τ_n, or ``len(taus)`` if beyond schedule."""
    a = float(age)
    if a < 0.0:
        raise ValueError("age must be non-negative")
    for i, tau in enumerate(taus):
        if a <= float(tau) + 1e-15:
            return i
    return len(taus)


@dataclass(frozen=True, slots=True)
class CrystallizationDecision:
    """E0–E1 crystallization gate aligned with holographic SPECULATIVE seal policy."""

    energy: EnergyProfile
    unitary_residual: float
    vault_candidate: bool
    residual_closed: bool
    may_speculative_seal: bool
    reason: str
    epsilon_drift: float

    def as_dict(self) -> dict[str, object]:
        return {
            "energy_class": self.energy.energy_class.value,
            "unitary_residual": self.unitary_residual,
            "vault_candidate": self.vault_candidate,
            "residual_closed": self.residual_closed,
            "may_speculative_seal": self.may_speculative_seal,
            "reason": self.reason,
            "epsilon_drift": self.epsilon_drift,
        }


def crystallization_for_holographic_seal(
    psi: np.ndarray,
    *,
    epsilon_drift: float = _DEFAULT_EPSILON_DRIFT,
    manifold: WaveManifold | None = None,
    operator: FieldEnergyOperator | None = None,
    **energy_kwargs: object,
) -> CrystallizationDecision:
    """Decide whether ψ may enter the SPECULATIVE holographic seal path.

    Policy (Trace B ↔ Trace A):
      * residual must be closed (≤ epsilon_drift) — fail-closed, no repair
      * energy class must be vault_candidate (E0/E1)
      * both required for ``may_speculative_seal``

    COHERENT promotion is never authorized here.
    """
    residual = wave_unitary_residual(
        psi, manifold=manifold, epsilon_drift=epsilon_drift
    )
    energy = energy_profile_from_wave(
        psi,
        operator=operator,
        manifold=manifold,
        epsilon_drift=epsilon_drift,
        **energy_kwargs,
    )
    vault = bool(energy.energy_class.vault_candidate)
    closed = bool(residual <= float(epsilon_drift))
    may_seal = vault and closed
    if may_seal:
        reason = "e0_e1_closed_residual_speculative_seal_ok"
    elif not closed:
        reason = "residual_not_closed"
    elif not vault:
        reason = "energy_class_not_vault_candidate"
    else:
        reason = "refused"
    return CrystallizationDecision(
        energy=energy,
        unitary_residual=residual,
        vault_candidate=vault,
        residual_closed=closed,
        may_speculative_seal=may_seal,
        reason=reason,
        epsilon_drift=float(epsilon_drift),
    )


__all__ = [
    "CrystallizationDecision",
    "assess_wave_trajectory",
    "crystallization_for_holographic_seal",
    "energy_profile_from_wave",
    "fibonacci_tau_schedule",
    "recency_band_index",
    "wave_unitary_residual",
]
