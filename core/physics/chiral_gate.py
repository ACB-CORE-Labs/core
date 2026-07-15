"""Chiral orientation gate — sgn(Q) preservation (ADR-0241 §2.4C / core_ha §5.2).

The topological spinor charge Q = ⟨ψ I₅ ψ̃⟩₀ anchors the global orientation of
the cognitive manifold: "preserving the sign and magnitude of Q_top across all
scales … prevent[s] mirror-image inversions" (ADR-0241 §2.4C), and the
core_ha unification memo pins the invariant safeguard as sgn(Q) = const
(§5.2). The substrate already carries a verified non-vacuous READOUT
(:meth:`WaveManifold.chiral_charge` — conserved exactly under ψ → Rψ), but
its only consumer took ``abs(...)``, discarding the sign. This module is the
missing ENFORCEMENT: latch the orientation on the first non-vacuous reading,
fail closed on any materially re-emerging flip.

Honesty pins (#19 family):
  * Even field-states have Q structurally ~0 — no orientation is defined and
    the gate never fabricates one (``vacuous``; the retired grade-5 gate is
    not revived). Serve-path even versors therefore never latch: wiring this
    gate into GoldTether is behaviorally inert for today's serve fields.
  * |Q| may legitimately pass below the floor (superposition mixtures); the
    latch persists and only a materially re-emerging opposite sign violates.

Tier-1 module: imported by ``goldtether`` (sanctioned serve substrate).
Algebra-native only; no teaching/vault imports.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

import numpy as np

from core.physics.wave_manifold import WaveManifold

#: Below this |Q|, orientation is undefined (even-field honesty; #19 family).
DEFAULT_Q_FLOOR = 0.1


class ChiralOrientationError(ValueError):
    """Fail-closed chiral orientation violation (mirror inversion).

    A sign flip of Q is unreachable under sanctioned rotor transport (Q is
    strictly conserved under left unitary multiplication), so a materially
    flipped sign is evidence of a non-unitary / corrupting transition and the
    gate refuses it rather than averaging it away.
    """

    def __init__(self, reason: str, **disclosure: Any) -> None:
        self.reason = reason
        self.disclosure = dict(disclosure)
        super().__init__(f"chiral_orientation refused [{reason}]: {self.disclosure}")


@dataclass(frozen=True, slots=True)
class ChiralObservation:
    """One gate reading with an honest epistemic verdict."""

    q: float
    sign: int  # −1 / +1, or 0 when |q| < q_floor (no orientation defined)
    latched_sign: int  # 0 until the first non-vacuous reading
    verdict: Literal["vacuous", "latched", "conserved"]

    def as_dict(self) -> dict[str, Any]:
        return {
            "q": self.q,
            "sign": self.sign,
            "latched_sign": self.latched_sign,
            "verdict": self.verdict,
        }


@dataclass(slots=True)
class ChiralOrientationGate:
    """Monitor-style latch for the global chiral orientation sign.

    * First reading with |Q| ≥ ``q_floor`` latches ``sgn(Q)``.
    * Later readings: same sign → ``conserved``; |Q| < floor → ``vacuous``
      (latch persists); opposite sign at material |Q| → raises
      :class:`ChiralOrientationError` (fail-closed; never averages).
    """

    q_floor: float = DEFAULT_Q_FLOOR
    latched_sign: int = 0
    _wave: WaveManifold = field(default_factory=WaveManifold)

    def observe(self, psi: np.ndarray) -> ChiralObservation:
        """Read Q from the field and enforce sign preservation."""
        return self.observe_q(self._wave.chiral_charge(psi))

    def observe_q(self, q: float) -> ChiralObservation:
        """Enforce sign preservation on a precomputed charge readout."""
        q = float(q)
        sign = 0 if abs(q) < self.q_floor else (1 if q > 0.0 else -1)

        if sign == 0:
            # No orientation defined at this reading; latch (if any) persists.
            return ChiralObservation(
                q=q, sign=0, latched_sign=self.latched_sign, verdict="vacuous"
            )
        if self.latched_sign == 0:
            self.latched_sign = sign
            return ChiralObservation(
                q=q, sign=sign, latched_sign=sign, verdict="latched"
            )
        if sign == self.latched_sign:
            return ChiralObservation(
                q=q, sign=sign, latched_sign=self.latched_sign, verdict="conserved"
            )
        raise ChiralOrientationError(
            "orientation_flip",
            q=q,
            sign=sign,
            latched_sign=self.latched_sign,
            q_floor=self.q_floor,
        )


__all__ = [
    "DEFAULT_Q_FLOOR",
    "ChiralObservation",
    "ChiralOrientationError",
    "ChiralOrientationGate",
]
