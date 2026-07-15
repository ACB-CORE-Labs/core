"""
core/physics/goldtether.py

GoldTether — Coherence Residual Monitor + Dynamic Autonomy Floor
ADR-0238

Note (fidelity #19, RETIRED): an earlier draft borrowed grade-5 "pseudoscalar"
vocabulary from Super-Blueprint §3.3 for the autonomy floor and read ``F[31]``
into telemetry. That anchor is vacuous in odd-dim Cl(4,1) — field-state versors
are even (``F[31] ≡ 0``) and ``I₅`` is central (``V·I₅·Ṽ = I₅`` for every
versor), so no non-vacuous grade-5 transition invariant exists. The namesake is
removed; the integrity-anchor role is carried by versor closure + the harmonized
GoldTether residual + biography/identity holonomy. See
``docs/research/third-door-blueprint-fidelity.md`` §5.

Absolute mastery implementation on the live Cl(4,1) algebra kernel.
All operators are pure where possible, dual-corrected, and enforce algebraic
closure on versor-valued outputs.

Distinct from Arena GoldTether (ADR-0199 / core.learning_arena.protocols).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Literal, Optional, Tuple

import numpy as np

from algebra.backend import geometric_product, versor_condition
from algebra.cl41 import N_COMPONENTS, reverse
from algebra.rotor import rotor_power, word_transition_rotor
from algebra.versor import versor_unit_residual
from core.physics.chiral_gate import ChiralOrientationGate
from core.physics.wave_manifold import WaveManifold

_CLOSURE_TOL = 1e-6
_NEAR_ZERO = 1e-12
_TELEMETRY_SCHEMA = "goldtether_coherence_v2"  # v2: dropped vacuous grade-5 channel (#19)
_E4_IDX = 4
_E5_IDX = 5

PruneMode = Literal["fifo", "principal_axes"]


@dataclass(frozen=True, slots=True)
class GoldPromotionProof:
    """Caller-supplied proof for replay-verified promotion into 𝓘_gold (ADR-0092).

    Physics never signs reviews. The review surface constructs this payload and
    passes ``authorized=True`` only after external verification. ``replay_hash``
    is opaque to GoldTether (determinism pin for the caller).
    """

    residual: float
    replay_hash: str
    reviewer_id: str
    closed: bool


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

    Canonical path (ADR-0241 Slice 2): :meth:`WaveManifold.measure_unitary_residual`
    — unitary wave amplitude drift, not a parallel residual implementation.
    """
    return WaveManifold().measure_unitary_residual(_as_mv(F))


@dataclass
class GoldTetherMonitor:
    """
    Continuous geometric monitor of the forever-lived trajectory.

    Primary residual:
        R(t) = || F(t) * reverse(F(t)) - 1 ||_F

    Dynamic autonomy floor rises only on proven epistemic elevation.
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
    # Chiral orientation enforcement (ADR-0241 §2.4C / core_ha §5.2):
    # sgn(Q) latches on the first non-vacuous spinor reading and a materially
    # re-emerging flip fails closed. Even serve field-states are vacuous
    # (Q ≈ 0), so the gate never latches on today's serve path — inert there.
    chiral_gate: "ChiralOrientationGate" = field(
        default_factory=lambda: ChiralOrientationGate(), compare=False
    )

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

        self.history.append((float(r), float(self.floor), float(self.autonomy)))
        if len(self.history) > self.max_history:
            self.history.pop(0)

        return float(r), float(self.autonomy)

    def may_relax_hitl(self) -> bool:
        """Hard gate: only true when residual is safe AND floor is high enough."""
        if not self.history:
            return False
        last_r, last_floor, last_auto = self.history[-1]
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
        # Unitary amplitude drift (wave substrate) + optional chiral readout.
        # Chiral charge is structurally ~0 on real even field-states (#19 family);
        # included as a non-negative integrity term so a future non-vacuous spinor
        # path can move the residual without a second API.
        wave = WaveManifold()
        drift = wave.measure_unitary_residual(F_arr)
        # Signed charge feeds the fail-closed orientation gate (sgn(Q)=const,
        # ADR-0241 §2.4C / core_ha §5.2). The residual term keeps its
        # magnitude-only semantics unchanged below.
        q_signed = float(wave.chiral_charge(F_arr))
        self.chiral_gate.observe_q(q_signed)
        chiral = abs(q_signed)
        drift_term = (
            (drift + chiral) / self.epsilon_drift
            if self.epsilon_drift > 0.0
            else (drift + chiral)
        )
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

    def promotion_eligible(self, F: np.ndarray) -> bool:
        """True iff F is closed and unit-residual (drift) is at/below ε_drift.

        Bootstrap gate (R&D §5): only coherent states are candidates for 𝓘_gold.
        Uses the dual-checked *closure* residual (not geo distance to gold), so
        novel closed states remain eligible for promotion. Does not authorize.
        """
        F_arr = _as_mv(F)
        if float(versor_condition(F_arr)) >= _CLOSURE_TOL:
            return False
        return float(coherence_residual(F_arr)) <= float(self.epsilon_drift)

    def promote_gold_invariant(
        self,
        F: np.ndarray,
        *,
        authorized: bool = False,
        proof: Optional[GoldPromotionProof] = None,
        require_proof: bool = False,
    ) -> None:
        """Add a state versor to 𝓘_gold. CALLER-GATED (ADR-0092).

        - Without ``authorized=True``: refuse (proposal-only; proof alone is insufficient).
        - With authorize: refuse non-closed or high *drift* residual (live check —
          never trusts proof.closed / proof.residual as truth).
        - ``require_proof=True``: refuse if ``proof`` is missing.
        - Physics never self-signs reviews; ``proof`` is caller-supplied audit pin.
        """
        if not authorized:
            raise ValueError(
                "promote_gold_invariant requires explicit authorization (ADR-0092 gate)"
            )
        if require_proof and proof is None:
            raise ValueError("promote_gold_invariant requires proof when require_proof=True")

        F_arr = _as_mv(F)
        cond = float(versor_condition(F_arr))
        # Closure residual only (geo distance to 𝓘_gold is expected for new axes).
        drift = float(coherence_residual(F_arr))
        if cond >= _CLOSURE_TOL or drift > float(self.epsilon_drift):
            raise ValueError(
                "promote_gold_invariant refused: not a closed versor "
                f"(versor_condition={cond:.3e}) or residual/drift {drift:.3e} "
                f"exceeds epsilon_drift={float(self.epsilon_drift)}"
            )
        self.gold_invariants.append(F_arr.copy())

    def prune_gold_invariants(
        self,
        max_size: int = 64,
        *,
        mode: PruneMode | str = "fifo",
    ) -> None:
        """Bound 𝓘_gold, always retaining the three primal seeds.

        Modes:
          * ``fifo`` — keep primals + most recent (#24).
          * ``principal_axes`` — keep primals + highest principal-energy non-primals
            (R&D §5 decay; coefficient PCA on the non-primal stack).
        ``max_size < 3`` is clamped to 3 so primals are never stripped.
        """
        mode_s = str(mode)
        if mode_s not in ("fifo", "principal_axes"):
            raise ValueError(f"prune_gold_invariants unknown mode: {mode_s!r}")
        max_size = max(3, int(max_size))
        if len(self.gold_invariants) <= max_size:
            return
        if mode_s == "fifo":
            primal = self.gold_invariants[:3]
            recent = self.gold_invariants[3:][-(max_size - 3) :]
            self.gold_invariants = primal + recent
            return
        self._prune_principal_axes(max_size)

    def _prune_principal_axes(self, max_size: int) -> None:
        """R&D §5: retain primals + non-primals with highest principal-subspace energy.

        Stack non-primal 32-vectors as columns, take top eigen-directions of
        ``XXᵀ/m``, score each member by squared projection onto that subspace,
        keep the top ``max_size - 3`` (stable by original index on ties).
        Differs from FIFO (last-N) whenever early high-energy axes outrank recent
        near-identity members.
        """
        primal = list(self.gold_invariants[:3])
        rest = [
            np.asarray(v, dtype=np.float64).copy() for v in self.gold_invariants[3:]
        ]
        n_keep = int(max_size) - 3
        if n_keep <= 0 or not rest:
            self.gold_invariants = primal
            return
        if len(rest) <= n_keep:
            self.gold_invariants = primal + rest
            return

        X = np.column_stack(rest)  # (32, m)
        m = X.shape[1]
        # Gram on ambient 32-space (deterministic; no external deps).
        C = (X @ X.T) / float(max(m, 1))
        evals, evecs = np.linalg.eigh(C)
        # Leading subspace dimension: enough to distinguish members, ≤ n_keep.
        k = max(1, min(n_keep, m, N_COMPONENTS))
        order = np.argsort(evals)[::-1]
        basis = evecs[:, order[:k]]  # (32, k)
        scored: list[tuple[float, int]] = []
        for i, v in enumerate(rest):
            coeff = basis.T @ v
            energy = float(coeff @ coeff)
            scored.append((energy, i))
        # Highest energy first; lower index wins ties (stable, anti-FIFO bias).
        scored.sort(key=lambda t: (-t[0], t[1]))
        keep_idx = sorted(i for _e, i in scored[:n_keep])
        kept = [rest[i] for i in keep_idx]
        # Non-primal retained members should stay closed when they entered as versors.
        for i, inv in enumerate(kept):
            cond = float(versor_condition(inv))
            if cond >= _CLOSURE_TOL:
                raise ValueError(
                    f"prune principal_axes retained non-closed member[{i}]: "
                    f"versor_condition={cond:.3e}"
                )
        self.gold_invariants = primal + kept

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
        """Workbench-safe projection (autonomy floor channel)."""
        last = self.history[-1] if self.history else (0.0, self.floor, self.autonomy)
        return {
            "schema_version": _TELEMETRY_SCHEMA,
            "residual": float(last[0]),
            "autonomy_floor": float(self.floor),
            "supervised_autonomy_level": float(self.autonomy),
            "may_relax_hitl": bool(self.may_relax_hitl()),
            "epsilon_drift": float(self.epsilon_drift),
            "n_history": len(self.history),
            "history_tail": [
                {"r": h[0], "floor": h[1], "autonomy": h[2]}
                for h in self.history[-16:]
            ],
        }


# ---------------------------------------------------------------------------
# ADR-0242 V1 — evidence-gated κ line search (optional, off-serve)
# ---------------------------------------------------------------------------


def propose_kappa_line_search(
    residual_fn,
    *,
    lower: float = 0.1,
    upper: float = 2.0,
    evaluation_budget: int = 16,
    objective_id: str = "goldtether_kappa",
    objective_version: str = "v1",
) -> tuple[float, object]:
    """Optional κ search via Fibonacci section (ADR-0242 Phase 1 seam).

    Returns ``(kappa, cert_or_failure)``. On failure, kappa is baseline 1.0.
    Does **not** mutate GoldTetherMonitor state, COHERENT standing, or serve
    autonomy — caller may record the result as telemetry only.
    """
    from core.physics.fibonacci_search import (
        BoundedUnimodalObjective,
        fibonacci_section_search,
        propose_kappa_from_search,
    )

    objective = BoundedUnimodalObjective(
        lower=float(lower),
        upper=float(upper),
        evaluation_budget=int(evaluation_budget),
        objective_id=str(objective_id),
        objective_version=str(objective_version),
    )
    result = fibonacci_section_search(objective, residual_fn)
    return propose_kappa_from_search(result)
