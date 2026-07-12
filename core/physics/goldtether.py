"""core.physics.goldtether — Coherence GoldTether (ADR-0238).

This module implements the *field* GoldTether: dynamic grade-5 pseudoscalar
floor, harmonized coherence residual, and practice/serve autonomy modulation.

It is intentionally distinct from the *arena* GoldTether protocol in
``core.learning_arena.protocols.GoldTether`` (ADR-0199), which scores practice
attempts against independent truth anchors. Shared metaphor; different contracts.
Never import or subclass the arena protocol from this module.

Construction boundary: supervised blend closes via ``algebra.rotor`` manifold
slerp (``word_transition_rotor`` + ``rotor_power``). No hot-path drift repair.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Any, Mapping

import numpy as np

from algebra.cl41 import N_COMPONENTS, geometric_product, reverse
from algebra.rotor import rotor_power, word_transition_rotor
from algebra.versor import versor_condition

_PSEUDOSCALAR_IDX = 31
_CLOSURE_TOL = 1e-6
_NEAR_ZERO = 1e-12
_DEFAULT_DECAY_N = 32
_DEFAULT_W_DRIFT = 0.35
_DEFAULT_FLOOR_INIT = 0.15
_DEFAULT_CRITICAL_RATIO = 2.5
_TELEMETRY_SCHEMA = "goldtether_coherence_v1"


class OperatingMode(str, Enum):
    """Practice vs Serve — risk-reward physics boundary."""

    PRACTICE = "practice"
    SERVE = "serve"


class AutonomyBand(str, Enum):
    """Residual-relative autonomy envelope (ADR-0238)."""

    AUTONOMOUS = "autonomous"
    SUPERVISED_BLEND = "supervised_blend"
    FAIL_CLOSED = "fail_closed"


@dataclass(frozen=True, slots=True)
class GoldTetherConfig:
    """Named configuration only — no silent magic constants at call sites."""

    decay_N: int = _DEFAULT_DECAY_N
    w_drift: float = _DEFAULT_W_DRIFT
    floor_init: float = _DEFAULT_FLOOR_INIT
    critical_ratio: float = _DEFAULT_CRITICAL_RATIO
    practice_autonomy_enabled: bool = False
    serve_supervised_blend_authorized: bool = False

    def __post_init__(self) -> None:
        if self.decay_N < 1:
            raise ValueError("decay_N must be >= 1")
        if not 0.0 <= self.w_drift <= 1.0:
            raise ValueError("w_drift must be in [0, 1]")
        if self.floor_init <= 0.0:
            raise ValueError("floor_init must be positive")
        if self.critical_ratio <= 1.0:
            raise ValueError("critical_ratio must be > 1")


@dataclass(frozen=True, slots=True)
class CoherenceResidual:
    """Harmonized residual: drift + geometric distance (normalized).

    Distinct from ADR-0006 ``EnergyProfile.coherence_residual`` and from
    ADR-0239 Procrustes/Surprise residuals.
    """

    drift: float
    geometric_distance: float
    combined: float
    kappa: float
    pseudoscalar_current: float
    pseudoscalar_reference: float


@dataclass(frozen=True, slots=True)
class AutonomyDecision:
    band: AutonomyBand
    residual: float
    floor: float
    critical: float
    mode: OperatingMode
    blend_alpha: float
    reason: str


@dataclass(frozen=True, slots=True)
class PseudoscalarFloorState:
    """Dynamic grade-5 coherence floor + sign/magnitude telemetry."""

    value: float
    sign: float
    n_samples: int
    last_update_step: int
    primal_floor: float
    recent_residuals: tuple[float, ...] = ()


def _as_mv(v: np.ndarray, name: str) -> np.ndarray:
    arr = np.asarray(v, dtype=np.float64)
    if arr.shape != (N_COMPONENTS,):
        raise ValueError(f"{name} must have shape ({N_COMPONENTS},); got {arr.shape}")
    return arr


def _pseudoscalar(v: np.ndarray) -> float:
    return float(v[_PSEUDOSCALAR_IDX])


def _geometric_distance(a: np.ndarray, b: np.ndarray) -> float:
    """Closed geometric distance on the versor manifold.

    Uses ``|| reverse(a) * b - 1 ||_F`` — zero iff a and b are the same unit
    versor (up to float noise). Not cosine similarity; not ANN.
    """
    product = geometric_product(reverse(a), b).astype(np.float64)
    product[0] -= 1.0
    return float(np.linalg.norm(product))


def _normalize_distance(d: float, scale: float = 2.0) -> float:
    """Map unbounded residual to [0, 1) for blend with drift."""
    if d <= 0.0:
        return 0.0
    return float(d / (d + scale))


def derive_kappa(combined_residual: float, floor: float) -> float:
    """Monotone κ from residual relative to floor.

    κ ∈ (0, 1]: small residual → κ near 1 (more trust); large residual → κ → 0.
    Used only to scale dual-correction blend weight — never to invent content.
    """
    if floor <= _NEAR_ZERO:
        floor = _NEAR_ZERO
    ratio = max(0.0, float(combined_residual) / float(floor))
    return float(1.0 / (1.0 + ratio))


@dataclass
class GoldTetherMonitor:
    """Stateful monitor for coherence residual, floor, and autonomy decisions.

    State is explicit and reconstructible; updates are pure replacements on
    ``floor_state`` (immutable snapshots). Deterministic for identical sequences.
    """

    config: GoldTetherConfig = field(default_factory=GoldTetherConfig)
    floor_state: PseudoscalarFloorState = field(init=False)
    _step: int = field(default=0, init=False, repr=False)

    def __post_init__(self) -> None:
        self.floor_state = PseudoscalarFloorState(
            value=float(self.config.floor_init),
            sign=1.0,
            n_samples=0,
            last_update_step=0,
            primal_floor=float(self.config.floor_init),
            recent_residuals=(),
        )

    def measure(
        self,
        current: np.ndarray,
        reference: np.ndarray,
        *,
        mode: OperatingMode | str = OperatingMode.PRACTICE,
    ) -> CoherenceResidual:
        """Compute harmonized coherence residual (pure; does not mutate floor)."""
        _ = OperatingMode(mode)  # validate
        cur = _as_mv(current, "current")
        ref = _as_mv(reference, "reference")
        ps_c = _pseudoscalar(cur)
        ps_r = _pseudoscalar(ref)
        drift = abs(ps_c - ps_r)
        # Also fold absolute pseudoscalar magnitude loss relative to reference.
        drift = max(drift, abs(abs(ps_c) - abs(ps_r)))
        geo = _geometric_distance(ref, cur)
        geo_n = _normalize_distance(geo)
        w = float(self.config.w_drift)
        combined = w * drift + (1.0 - w) * geo_n
        kappa = derive_kappa(combined, self.floor_state.value)
        return CoherenceResidual(
            drift=float(drift),
            geometric_distance=float(geo),
            combined=float(combined),
            kappa=float(kappa),
            pseudoscalar_current=ps_c,
            pseudoscalar_reference=ps_r,
        )

    def update_floor(
        self,
        residual: CoherenceResidual | float,
        *,
        mode: OperatingMode | str = OperatingMode.PRACTICE,
        success: bool = True,
        pseudoscalar_sign: float | None = None,
    ) -> PseudoscalarFloorState:
        """Update dynamic floor from practice successes only.

        Serve mode never promotes the floor. Failures only append telemetry
        window; they do not raise the autonomy envelope.
        """
        op_mode = OperatingMode(mode)
        r = float(residual.combined if isinstance(residual, CoherenceResidual) else residual)
        self._step += 1
        recent = list(self.floor_state.recent_residuals) + [r]
        decay_n = int(self.config.decay_N)
        if len(recent) > decay_n:
            recent = recent[-decay_n:]

        new_value = self.floor_state.value
        new_sign = self.floor_state.sign
        n_samples = self.floor_state.n_samples

        if op_mode is OperatingMode.PRACTICE and success and r < self.floor_state.value:
            # Tighten floor toward observed residual while keeping primal anchor.
            # Weighted mean of recent successes under decay window.
            window = [x for x in recent if x < self.floor_state.value] or [r]
            mean_r = float(sum(window) / len(window))
            # Blend toward mean_r but never below half primal (safety).
            floor_floor = 0.5 * self.floor_state.primal_floor
            candidate = 0.5 * self.floor_state.value + 0.5 * mean_r
            new_value = max(floor_floor, min(self.floor_state.value, candidate))
            n_samples = n_samples + 1
            if pseudoscalar_sign is not None and abs(pseudoscalar_sign) > _NEAR_ZERO:
                new_sign = 1.0 if pseudoscalar_sign >= 0.0 else -1.0

        self.floor_state = PseudoscalarFloorState(
            value=float(new_value),
            sign=float(new_sign),
            n_samples=int(n_samples),
            last_update_step=int(self._step),
            primal_floor=float(self.floor_state.primal_floor),
            recent_residuals=tuple(float(x) for x in recent),
        )
        return self.floor_state

    def decide(
        self,
        residual: CoherenceResidual | float,
        *,
        mode: OperatingMode | str = OperatingMode.PRACTICE,
        floor: PseudoscalarFloorState | None = None,
    ) -> AutonomyDecision:
        """Map residual + mode → autonomy band (HITL-safe defaults)."""
        op_mode = OperatingMode(mode)
        r = float(residual.combined if isinstance(residual, CoherenceResidual) else residual)
        fl = floor if floor is not None else self.floor_state
        floor_v = float(fl.value)
        critical = floor_v * float(self.config.critical_ratio)

        if r > critical:
            return AutonomyDecision(
                band=AutonomyBand.FAIL_CLOSED,
                residual=r,
                floor=floor_v,
                critical=critical,
                mode=op_mode,
                blend_alpha=0.0,
                reason="residual_above_critical",
            )

        if op_mode is OperatingMode.SERVE:
            # Serve never autonomous. Supervised blend only if explicitly authorized.
            if r < floor_v and self.config.serve_supervised_blend_authorized:
                alpha = float(1.0 - derive_kappa(r, floor_v))
                return AutonomyDecision(
                    band=AutonomyBand.SUPERVISED_BLEND,
                    residual=r,
                    floor=floor_v,
                    critical=critical,
                    mode=op_mode,
                    blend_alpha=alpha,
                    reason="serve_supervised_authorized",
                )
            if r < floor_v:
                return AutonomyDecision(
                    band=AutonomyBand.FAIL_CLOSED,
                    residual=r,
                    floor=floor_v,
                    critical=critical,
                    mode=op_mode,
                    blend_alpha=0.0,
                    reason="serve_hitl_default_fail_closed",
                )
            # floor <= r <= critical on serve: fail-closed unless blend authorized
            if self.config.serve_supervised_blend_authorized:
                alpha = float(min(1.0, (r - floor_v) / max(critical - floor_v, _NEAR_ZERO)))
                return AutonomyDecision(
                    band=AutonomyBand.SUPERVISED_BLEND,
                    residual=r,
                    floor=floor_v,
                    critical=critical,
                    mode=op_mode,
                    blend_alpha=alpha,
                    reason="serve_midband_supervised",
                )
            return AutonomyDecision(
                band=AutonomyBand.FAIL_CLOSED,
                residual=r,
                floor=floor_v,
                critical=critical,
                mode=op_mode,
                blend_alpha=0.0,
                reason="serve_midband_fail_closed",
            )

        # Practice path
        if r < floor_v and self.config.practice_autonomy_enabled:
            return AutonomyDecision(
                band=AutonomyBand.AUTONOMOUS,
                residual=r,
                floor=floor_v,
                critical=critical,
                mode=op_mode,
                blend_alpha=1.0,
                reason="practice_below_floor_autonomy_enabled",
            )
        if r < floor_v:
            return AutonomyDecision(
                band=AutonomyBand.SUPERVISED_BLEND,
                residual=r,
                floor=floor_v,
                critical=critical,
                mode=op_mode,
                blend_alpha=float(derive_kappa(r, floor_v)),
                reason="practice_below_floor_supervised_default",
            )
        # floor <= r <= critical
        alpha = float(1.0 - min(1.0, (r - floor_v) / max(critical - floor_v, _NEAR_ZERO)))
        return AutonomyDecision(
            band=AutonomyBand.SUPERVISED_BLEND,
            residual=r,
            floor=floor_v,
            critical=critical,
            mode=op_mode,
            blend_alpha=max(0.0, min(1.0, alpha)),
            reason="practice_midband_supervised",
        )

    def supervised_blend(
        self,
        source: np.ndarray,
        target: np.ndarray,
        alpha: float,
    ) -> np.ndarray:
        """Manifold slerp from source toward target by alpha ∈ [0, 1].

        Dual-correction surface on the Spin group (not Euclidean lerp):

            R = word_transition_rotor(source, target)  # = target * reverse(source)
            out = rotor_power(R, α) * source            # left composition

        At α=0 → source; at α=1 → target (unit versors). Sandwich conjugation
        would map the identity to itself and is the wrong geodesic for state
        interpolation. Output must satisfy versor_condition < 1e-6.
        """
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
            raise ValueError(
                f"supervised_blend broke versor_condition: {cond:.3e} >= {_CLOSURE_TOL}"
            )
        return out.astype(np.float64, copy=False)

    def telemetry(self) -> dict[str, Any]:
        """Schema-versioned pure projection for workbench channels."""
        fl = self.floor_state
        return {
            "schema_version": _TELEMETRY_SCHEMA,
            "pseudoscalar_floor": float(fl.value),
            "pseudoscalar_sign": float(fl.sign),
            "n_samples": int(fl.n_samples),
            "last_update_step": int(fl.last_update_step),
            "primal_floor": float(fl.primal_floor),
            "recent_residuals": list(fl.recent_residuals),
            "config": {
                "decay_N": int(self.config.decay_N),
                "w_drift": float(self.config.w_drift),
                "floor_init": float(self.config.floor_init),
                "critical_ratio": float(self.config.critical_ratio),
                "practice_autonomy_enabled": bool(self.config.practice_autonomy_enabled),
                "serve_supervised_blend_authorized": bool(
                    self.config.serve_supervised_blend_authorized
                ),
            },
        }


def with_config(monitor: GoldTetherMonitor, **updates: Any) -> GoldTetherMonitor:
    """Return a new monitor with updated config (immutability-friendly)."""
    cfg = replace(monitor.config, **updates)
    m = GoldTetherMonitor(config=cfg)
    m.floor_state = monitor.floor_state
    m._step = monitor._step
    return m


def residual_from_mapping(payload: Mapping[str, Any]) -> float:
    """Deterministic residual extract for telemetry/replay fixtures."""
    if "combined" in payload:
        return float(payload["combined"])
    raise KeyError("payload missing combined residual")
