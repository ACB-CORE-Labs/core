"""P9 Trace A seam — contemplation → SPECULATIVE holographic standing-wave seal.

ADR-0241 cohesion package P9:

1. Contemplation may **SPECULATIVE-seal** standing-wave modes via
   :meth:`HolographicVaultStore.seal_mode` only.
2. Never writes COHERENT — teaching corridor / authorized
   ``seal_mode_reviewed`` remains outside this module.
3. Resonant reconstruct is available as a **hypothesis** over the full
   spectrum, or as **evidence** only when ``min_status=COHERENT``.
4. Serve path stays quarantined (no import from ``chat/runtime.py``).
5. No direct ``VaultStore.store`` — INV-21 writes stay in holographic_vault.

This module is the living-system bridge for Trace A without collapsing
the teaching / serve containment boundary.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

import numpy as np

from core.contemplation.schema import (
    ContemplationEvidenceRef,
    ContemplationFinding,
    FindingKind,
)
from core.physics.holographic_vault import (
    HolographicVaultError,
    HolographicVaultStore,
    SealedMode,
)
from teaching.epistemic import EpistemicStatus


@dataclass(frozen=True, slots=True)
class WaveModeHypothesis:
    """SPECULATIVE seal + contemplation finding for teaching review."""

    sealed: SealedMode
    finding: ContemplationFinding
    standing: Literal["hypothesis"] = "hypothesis"

    def as_dict(self) -> dict[str, Any]:
        return {
            "standing": self.standing,
            "mode_id": self.sealed.mode_id,
            "vault_index": self.sealed.vault_index,
            "epistemic_status": self.sealed.epistemic_status.value,
            "finding": self.finding.as_dict(),
        }


@dataclass(frozen=True, slots=True)
class WaveReconstructResult:
    """Reconstructed field with honest epistemic standing label."""

    psi_hat: np.ndarray
    coeffs: np.ndarray
    energies: np.ndarray
    spectrum: tuple[SealedMode, ...]
    standing: Literal["hypothesis", "evidence"]
    min_status: EpistemicStatus | None

    def as_dict(self) -> dict[str, Any]:
        return {
            "standing": self.standing,
            "min_status": None if self.min_status is None else self.min_status.value,
            "mode_ids": [s.mode_id for s in self.spectrum],
            "coeff_count": int(self.coeffs.shape[0]),
        }


def speculative_seal_from_contemplation(
    store: HolographicVaultStore,
    psi: np.ndarray,
    *,
    substrate_hash: str,
    subject: str,
    mode_id: str | None = None,
    notes: str = "",
    predicate: str = "propose_standing_wave_mode",
) -> WaveModeHypothesis:
    """SPECULATIVE-seal a closed mode and emit a contemplation finding.

    Fail-closed on non-closed / high-drift ψ (delegates to holographic admit).
    Does **not** accept an authorization flag — COHERENT promotion is not
    available on this seam.
    """
    if not str(substrate_hash).strip():
        raise ValueError("substrate_hash is required for Trace A provenance")
    if not str(subject).strip():
        raise ValueError("subject is required")

    meta: dict[str, Any] = {
        "source": "contemplation_trace_a",
        "substrate_hash": substrate_hash,
        "notes": notes,
        "adr_refs": ["ADR-0241", "ADR-0080"],
    }
    sealed = store.seal_mode(psi, mode_id=mode_id, metadata=meta)
    if sealed.epistemic_status is not EpistemicStatus.SPECULATIVE:
        # Defensive: seal_mode contract is SPECULATIVE-only; never promote here.
        raise RuntimeError(
            "Trace A seam integrity breach: seal_mode returned non-SPECULATIVE"
        )

    mid = sealed.mode_id
    finding = ContemplationFinding(
        kind=FindingKind.RESONANT_MODE_CANDIDATE,
        subject=subject,
        predicate=predicate,
        object=mid,
        evidence_refs=(
            ContemplationEvidenceRef(
                source_type="holographic_vault",
                source_id=mid,
                pointer=f"vault_index:{sealed.vault_index}",
                summary=(
                    "SPECULATIVE standing-wave mode sealed for teaching review; "
                    "not admissible as COHERENT evidence"
                ),
            ),
        ),
        proposed_action="review_standing_wave_mode",
        substrate_hash=substrate_hash,
        epistemic_status=EpistemicStatus.SPECULATIVE,
    )
    return WaveModeHypothesis(sealed=sealed, finding=finding, standing="hypothesis")


def reconstruct_as_hypothesis(
    store: HolographicVaultStore,
    psi_query: np.ndarray,
) -> WaveReconstructResult:
    """Superposition reconstruct over the full spectrum (incl. SPECULATIVE).

    Result standing is always ``hypothesis`` — never claim reviewed evidence.
    """
    psi_hat, coeffs, energies, spectrum = store.resonant_reconstruct(psi_query)
    return WaveReconstructResult(
        psi_hat=psi_hat,
        coeffs=coeffs,
        energies=energies,
        spectrum=spectrum,
        standing="hypothesis",
        min_status=None,
    )


def reconstruct_as_evidence(
    store: HolographicVaultStore,
    psi_query: np.ndarray,
) -> WaveReconstructResult:
    """Superposition reconstruct over COHERENT modes only.

    SPECULATIVE modes are excluded. Empty COHERENT spectrum refuses so
    unreviewed hypothesis mass cannot masquerade as evidence.
    """
    try:
        psi_hat, coeffs, energies, spectrum = store.resonant_reconstruct(
            psi_query,
            min_status=EpistemicStatus.COHERENT,
        )
    except HolographicVaultError as exc:
        if exc.reason == "empty_spectrum":
            raise HolographicVaultError(
                "empty_spectrum",
                detail=(
                    "evidence reconstruct requires COHERENT standing-wave modes; "
                    "SPECULATIVE hypothesis mass is excluded"
                ),
            ) from exc
        raise
    return WaveReconstructResult(
        psi_hat=psi_hat,
        coeffs=coeffs,
        energies=energies,
        spectrum=spectrum,
        standing="evidence",
        min_status=EpistemicStatus.COHERENT,
    )


__all__ = [
    "WaveModeHypothesis",
    "WaveReconstructResult",
    "reconstruct_as_evidence",
    "reconstruct_as_hypothesis",
    "speculative_seal_from_contemplation",
]
