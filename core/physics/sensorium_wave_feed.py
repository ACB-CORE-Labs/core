"""D7 sensorium → ψ feed (I-04 boundary).

Thin construction-boundary adapter: modality surface packets become Cl(4,1)
wave fields for algebraic multimodal resonance.

Real modality compilers remain in ``sensorium/*``. This module only standardizes
the feed into the wave substrate:

  * :class:`ModalityPacket` (or dict) — modality id + 32-float coefficients
  * :func:`compile_packet_to_psi` — validate / lift to shape ``(32,)``
  * :func:`superpose_packets` — ``ψ_total = Σ ψ_i``
  * :func:`phase_correlate` — delegates **only** to
    :meth:`WaveManifold.phase_correlation` (metric-exact ρ; no cosine / ANN)

Honest test fixtures via :func:`fake_deterministic_packet` use closed rotors
from :func:`algebra.rotor.make_rotor_from_angle` when live compilers are not
under test. That is a fixture, not a claim that audio/vision compilers ran.

Off-serve: must not be imported by ``chat/runtime.py`` (A-04 quarantine).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence, Union

import numpy as np

from algebra.cl41 import N_COMPONENTS
from algebra.rotor import make_rotor_from_angle
from core.physics.wave_manifold import WaveManifold

PacketLike = Union["ModalityPacket", Mapping[str, Any]]


@dataclass(frozen=True, slots=True)
class ModalityPacket:
    """Construction-boundary packet: modality tag + 32 Cl(4,1) coefficients.

    After compile, the field has no modality concept (Logos recovery).
    ``modality_id`` is provenance only.
    """

    modality_id: str
    coefficients: np.ndarray  # shape (N_COMPONENTS,)

    def __post_init__(self) -> None:
        mid = str(self.modality_id).strip()
        if not mid:
            raise ValueError("modality_id must be non-empty")
        arr = np.asarray(self.coefficients, dtype=np.float64).reshape(-1)
        if arr.shape != (N_COMPONENTS,):
            raise ValueError(
                f"coefficients must have shape ({N_COMPONENTS},); got {arr.shape}"
            )
        object.__setattr__(self, "modality_id", mid)
        object.__setattr__(self, "coefficients", arr.copy())


def _coerce_packet(packet: PacketLike) -> ModalityPacket:
    if isinstance(packet, ModalityPacket):
        return packet
    if isinstance(packet, Mapping):
        mid = packet.get("modality_id", packet.get("modality"))
        coeffs = packet.get("coefficients")
        if coeffs is None:
            coeffs = packet.get("coeffs")
        if coeffs is None:
            coeffs = packet.get("psi")
        if mid is None or coeffs is None:
            raise ValueError(
                "packet mapping requires modality_id (or modality) and "
                "coefficients (or coeffs / psi)"
            )
        return ModalityPacket(modality_id=str(mid), coefficients=np.asarray(coeffs))
    raise TypeError(
        f"packet must be ModalityPacket or mapping; got {type(packet).__name__}"
    )


def compile_packet_to_psi(packet: PacketLike) -> np.ndarray:
    """Lift a modality packet to a wave field ψ of shape ``(32,)``.

    Construction-boundary only: validates shape/dtype and returns a fresh
    float64 copy. Does not repair non-unit packets (no hidden unitize).
    """
    p = _coerce_packet(packet)
    return p.coefficients.astype(np.float64, copy=True)


def superpose_packets(packets: Sequence[PacketLike]) -> np.ndarray:
    """Linear superposition ``ψ_total = Σ_i compile_packet_to_psi(packet_i)``.

    Empty input refuses (no confabulated zero field as resonance truth).
    """
    if not packets:
        raise ValueError("superpose_packets: empty packet list")
    total = np.zeros(N_COMPONENTS, dtype=np.float64)
    for packet in packets:
        total = total + compile_packet_to_psi(packet)
    return total


def phase_correlate(
    psi_a: np.ndarray,
    psi_b: np.ndarray,
    *,
    manifold: WaveManifold | None = None,
) -> float:
    """Algebraic multimodal resonance ρ(A,B) for I-04.

    Delegates solely to :meth:`WaveManifold.phase_correlation`.
    Forbidden: cosine similarity, ANN, sklearn neighbors, embedding ranking.
    """
    m = manifold if manifold is not None else WaveManifold()
    return float(m.phase_correlation(psi_a, psi_b))


def fake_deterministic_packet(
    modality_id: str,
    *,
    angle: float = 0.3,
    plane: int = 6,
) -> ModalityPacket:
    """Honest deterministic fixture when real modality compilers are absent.

    Builds a closed unit rotor via :func:`make_rotor_from_angle`. This is a
    test/construction fixture — not a live audio/vision compile path.
    """
    coeffs = make_rotor_from_angle(float(angle), bivector_idx=int(plane))
    return ModalityPacket(modality_id=modality_id, coefficients=coeffs)


__all__ = [
    "ModalityPacket",
    "PacketLike",
    "compile_packet_to_psi",
    "superpose_packets",
    "phase_correlate",
    "fake_deterministic_packet",
]
