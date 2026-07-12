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
_E4_IDX = 4
_E5_IDX = 5


def _primal_gold_invariants() -> list:
    """R&D-Revised §5 bootstrapping seeds: the identity versor and the two
    conformal null directions ``n_o = 0.5(e5-e4)`` and ``n_inf = e4+e5``.
    Coordinate-free algebraic anchors so the geometric distance term never
    degenerates to drift-only at cold start.
    """
    ident = np.zeros(N_COMPONENTS, dtype=np.float64)
    ident[0] = 1.0
    n_o = np.zeros(N_COMPONENTS, dtype=np.float64)
    n_o[_E5_IDX] = 0.5
    n_o[_E4_IDX] = -0.5
    n_inf = np.zeros(N_COMPONENTS, dtype=np.float64)
    n_inf[_E4_IDX] = 1.0
    n_inf[_E5_IDX] = 1.0
    return [ident, n_o, n_inf]


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
    # Harmonized residual + alpha control law (ADR-0238 §2.3 / R&D-Revised §2.3).
    w_drift: float = 0.5
    r_floor: float = 0.1
    r_critical: float = 1.0
    gold_invariants: list = field(default_factory=_primal_gold_invariants, compare=False)

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

    # --- Harmonized residual + alpha control law (ADR-0238 §2.3) ---------------

    def goldtether_residual(self, F: np.ndarray) -> float:
        """Scale-harmonized coherence residual (ADR-0238 §2.3):

            R = w·(drift / ε_drift) + (1−w)·(min_{I∈𝓘_gold} ‖F−I‖_F / ‖F‖_F)

        The algebraic drift term (normalized by the numerical floor ε_drift) and
        the geometric distance-to-gold term (normalized by ‖F‖) are each scaled to
        ``[0, O(1)]`` so neither masks the other — the exact defect §2.3 exists to
        fix. This is the ALIGNMENT signal that drives the constraint weight α; the
        raw :func:`coherence_residual` stays the fail-closed *closure* gate.
        """
        F_arr = _as_mv(F)
        drift = coherence_residual(F_arr)
        drift_term = drift / self.epsilon_drift if self.epsilon_drift > 0.0 else drift
        scale = float(np.linalg.norm(F_arr))
        if self.gold_invariants and scale > _NEAR_ZERO:
            min_dist = min(
                float(np.linalg.norm(F_arr - np.asarray(inv, dtype=np.float64)))
                for inv in self.gold_invariants
            )
            geo_term = min_dist / scale
        else:
            geo_term = 0.0
        w = float(self.w_drift)
        return float(w * drift_term + (1.0 - w) * geo_term)

    def alpha_constraint(
        self,
        F: np.ndarray,
        *,
        mode: OperatingMode | str = OperatingMode.PRACTICE,
    ) -> float:
        """Human-constraint weight ``α ∈ [0,1]`` for the supervised transition
        surface (R&D-Revised §2.3): ``α = Φ(R_gt; r_floor, r_critical)`` — a smooth
        step of the *instantaneous* harmonized residual — composed with the
        earned-autonomy ceiling and the serve-never-autonomous rule.

        ``α = 0`` fully autonomous (trust self); ``α = 1`` full human override.
        Earned autonomy sets the FLOOR on α: the engine may never act more
        autonomously than it has earned over its trajectory, and SERVE is pinned
        to full override.
        """
        op = OperatingMode(mode)
        if op is OperatingMode.SERVE:
            return 1.0
        r = self.goldtether_residual(F)
        lo, hi = float(self.r_floor), float(self.r_critical)
        if r <= lo:
            phi = 0.0
        elif r >= hi or hi <= lo:
            phi = 1.0
        else:
            phi = (r - lo) / (hi - lo)
        alpha_floor = 1.0 - float(self.autonomy)
        return float(min(1.0, max(phi, alpha_floor)))

    def supervised_transition(
        self,
        v_self: np.ndarray,
        v_constraint: np.ndarray,
        F: np.ndarray,
        *,
        mode: OperatingMode | str = OperatingMode.PRACTICE,
    ) -> np.ndarray:
        """Blend the engine's own transition ``v_self`` toward the human/gold
        ``v_constraint`` by the residual-driven constraint weight α.
        ``α=0 → v_self`` (autonomous), ``α=1 → v_constraint`` (override).
        Rides the exact geodesic (`supervised_blend`), so closure is preserved.
        """
        alpha = self.alpha_constraint(F, mode=mode)
        return self.supervised_blend(v_self, v_constraint, alpha)

    def promote_gold_invariant(self, F: np.ndarray, *, authorized: bool = False) -> None:
        """Add a state versor to 𝓘_gold. CALLER-GATED: the ADR-0092 signed /
        replay-verified promotion happens in the caller; this refuses to
        self-authorize (one-mutation-path discipline). The full replay-verified
        promotion pipeline + principal-axis decay are deferred (issue #18 follow-up).
        """
        if not authorized:
            raise ValueError(
                "promote_gold_invariant requires explicit authorization (ADR-0092 gate)"
            )
        self.gold_invariants.append(_as_mv(F).copy())

    def prune_gold_invariants(self, max_size: int = 64) -> None:
        """Bound 𝓘_gold (decay hook), always retaining the three primal seeds.
        Full principal-axis pruning (R&D-Revised §5) is deferred."""
        max_size = max(3, int(max_size))
        if len(self.gold_invariants) > max_size:
            primal = self.gold_invariants[:3]
            recent = self.gold_invariants[3:][-(max_size - 3):]
            self.gold_invariants = primal + recent

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
