"""
core/physics/goldtether.py

GoldTether — Coherence Residual Monitor + Dynamic Pseudoscalar Floor
ADR-0238

Absolute mastery implementation on the live Cl(4,1) algebra kernel.
All operators are pure where possible, dual-corrected, and enforce algebraic
closure on versor-valued outputs.

Distinct from Arena GoldTether (ADR-0199 / core.learning_arena.protocols).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, Tuple

import numpy as np

from algebra.cl41 import N_COMPONENTS, geometric_product, reverse
from algebra.rotor import rotor_power, word_transition_rotor
from algebra.versor import versor_condition, versor_unit_residual

_CLOSURE_TOL = 1e-6
_NEAR_ZERO = 1e-12
_PSEUDOSCALAR_IDX = 31
_TELEMETRY_SCHEMA = "goldtether_coherence_v1"


class OperatingMode(str, Enum):
    PRACTICE = "practice"
    SERVE = "serve"


class AutonomyBand(str, Enum):
    AUTONOMOUS = "autonomous"
    SUPERVISED_BLEND = "supervised_blend"
    FAIL_CLOSED = "fail_closed"


@dataclass(frozen=True, slots=True)
class CoherenceResidual:
    """Structured residual view (extension of one-shot residual)."""

    primary: float
    dual: float
    combined: float
    kappa: float
    pseudoscalar: float


@dataclass(frozen=True, slots=True)
class AutonomyDecision:
    band: AutonomyBand
    residual: float
    floor: float
    autonomy: float
    mode: OperatingMode
    reason: str


def _as_mv(F: np.ndarray, name: str = "F") -> np.ndarray:
    arr = np.asarray(F, dtype=np.float64)
    if arr.shape != (N_COMPONENTS,):
        raise ValueError(f"{name} must have shape ({N_COMPONENTS},); got {arr.shape}")
    return arr


def coherence_residual(F: np.ndarray) -> float:
    """Public one-shot residual for tests and harnesses.

    R = || F · reverse(F) − 1 ||_F  (dual-checked against reverse(F)).
    """
    F_arr = _as_mv(F)
    r = float(versor_unit_residual(F_arr))
    r_rev = float(versor_unit_residual(reverse(F_arr)))
    return max(r, r_rev)


@dataclass
class GoldTetherMonitor:
    """
    Continuous geometric monitor of the forever-lived trajectory.

    Primary residual:
        R(t) = || F(t) * reverse(F(t)) - 1 ||_F

    Dynamic pseudoscalar floor rises only on proven epistemic elevation.
    supervised_autonomy_level ∈ [0, 1] is the single gate for HITL relaxation
    (exposed as ``autonomy``).
    """

    epsilon_drift: float = 1e-6
    floor: float = 0.0
    autonomy: float = 0.0  # supervised_autonomy_level
    history: list = field(default_factory=list)
    max_history: int = 1024
    floor_step: float = 0.02
    floor_decay: float = 0.05
    autonomy_step: float = 0.01
    hitl_floor_threshold: float = 0.7
    hitl_autonomy_threshold: float = 0.5

    @property
    def supervised_autonomy_level(self) -> float:
        return float(self.autonomy)

    def residual(self, F: np.ndarray) -> float:
        """Compute the primary GoldTether residual. Always ≥ 0. Dual-corrected."""
        return coherence_residual(F)

    def update(
        self,
        F: np.ndarray,
        epistemic_elevation: bool = False,
    ) -> Tuple[float, float]:
        """
        Update monitor with new field state.
        Returns (residual, new_autonomy).
        Dual-correction: residual is checked both ways inside residual().
        """
        r = self.residual(F)

        if r > self.epsilon_drift:
            # Fail-closed: force autonomy to zero
            self.autonomy = 0.0
            self.floor = max(0.0, self.floor - self.floor_decay)
        else:
            if epistemic_elevation:
                # Only proven elevation may raise the floor
                self.floor = min(1.0, self.floor + self.floor_step)
            # Autonomy may never exceed the floor
            self.autonomy = min(self.autonomy + self.autonomy_step, self.floor)

        ps = float(_as_mv(F)[_PSEUDOSCALAR_IDX])
        self.history.append((float(r), float(self.floor), float(self.autonomy), ps))
        if len(self.history) > self.max_history:
            self.history.pop(0)

        return float(r), float(self.autonomy)

    def may_relax_hitl(self) -> bool:
        """Hard gate: only true when residual is safe AND floor is high enough."""
        if not self.history:
            return False
        last_r, last_floor, last_auto, _ps = self.history[-1]
        return (
            last_r < self.epsilon_drift
            and last_floor >= self.hitl_floor_threshold
            and last_auto >= self.hitl_autonomy_threshold
        )

    def force_reset(self) -> None:
        """Emergency fail-closed. Callable by HITL or safety pack only."""
        self.autonomy = 0.0
        self.floor = 0.0
        self.history.clear()

    def measure(self, F: np.ndarray, reference: Optional[np.ndarray] = None) -> CoherenceResidual:
        """Structured residual (primary + optional geometric distance to reference)."""
        F_arr = _as_mv(F)
        primary = float(versor_unit_residual(F_arr))
        dual = float(versor_unit_residual(reverse(F_arr)))
        combined = max(primary, dual)
        if reference is not None:
            ref = _as_mv(reference, "reference")
            product = geometric_product(reverse(ref), F_arr).astype(np.float64)
            product[0] -= 1.0
            geo = float(np.linalg.norm(product))
            combined = max(combined, geo / (1.0 + geo))
        floor = max(self.floor, _NEAR_ZERO)
        kappa = float(1.0 / (1.0 + combined / floor)) if floor > 0 else 0.0
        return CoherenceResidual(
            primary=primary,
            dual=dual,
            combined=float(combined),
            kappa=kappa,
            pseudoscalar=float(F_arr[_PSEUDOSCALAR_IDX]),
        )

    def decide(
        self,
        residual: float | CoherenceResidual,
        *,
        mode: OperatingMode | str = OperatingMode.PRACTICE,
    ) -> AutonomyDecision:
        """Map residual + mode to an autonomy band (HITL-safe defaults)."""
        op = OperatingMode(mode)
        r = float(residual.combined if isinstance(residual, CoherenceResidual) else residual)
        if r > self.epsilon_drift or self.autonomy <= 0.0:
            return AutonomyDecision(
                band=AutonomyBand.FAIL_CLOSED,
                residual=r,
                floor=float(self.floor),
                autonomy=float(self.autonomy),
                mode=op,
                reason="residual_or_autonomy_fail_closed",
            )
        if op is OperatingMode.SERVE:
            # Serve never autonomous; HITL default.
            return AutonomyDecision(
                band=AutonomyBand.FAIL_CLOSED,
                residual=r,
                floor=float(self.floor),
                autonomy=float(self.autonomy),
                mode=op,
                reason="serve_hitl_default",
            )
        if self.may_relax_hitl() and r < self.epsilon_drift:
            return AutonomyDecision(
                band=AutonomyBand.AUTONOMOUS,
                residual=r,
                floor=float(self.floor),
                autonomy=float(self.autonomy),
                mode=op,
                reason="practice_may_relax_hitl",
            )
        return AutonomyDecision(
            band=AutonomyBand.SUPERVISED_BLEND,
            residual=r,
            floor=float(self.floor),
            autonomy=float(self.autonomy),
            mode=op,
            reason="practice_supervised",
        )

    def supervised_blend(
        self,
        source: np.ndarray,
        target: np.ndarray,
        alpha: float,
    ) -> np.ndarray:
        """Spin left-composition geodesic: out = rotor_power(R, α) * source."""
        a = float(alpha)
        if a < 0.0 or a > 1.0:
            raise ValueError("alpha must be in [0, 1]")
        src = _as_mv(source, "source")
        tgt = _as_mv(target, "target")
        if a <= _NEAR_ZERO:
            out = src.copy()
        elif a >= 1.0 - _NEAR_ZERO:
            out = tgt.copy()
        else:
            R = word_transition_rotor(src, tgt)
            R_a = rotor_power(R, a)
            out = geometric_product(R_a, src).astype(np.float64)
        cond = versor_condition(out)
        if cond >= _CLOSURE_TOL:
            raise ValueError(f"supervised_blend broke versor_condition: {cond:.3e}")
        return out

    def telemetry(self) -> dict[str, Any]:
        """Workbench-safe projection (pseudoscalar floor channel)."""
        last = self.history[-1] if self.history else (0.0, self.floor, self.autonomy, 0.0)
        return {
            "schema_version": _TELEMETRY_SCHEMA,
            "residual": float(last[0]),
            "pseudoscalar_floor": float(self.floor),
            "supervised_autonomy_level": float(self.autonomy),
            "may_relax_hitl": bool(self.may_relax_hitl()),
            "epsilon_drift": float(self.epsilon_drift),
            "n_history": len(self.history),
            "history_tail": [
                {"r": h[0], "floor": h[1], "autonomy": h[2], "ps": h[3]}
                for h in self.history[-16:]
            ],
        }
