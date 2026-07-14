"""
core/physics/holographic_vault.py

ADR-0241 durable holographic standing-wave spectrum (issue D / vault store).

Session-local WaveManifold modes are not enough for restart lock-in. This
module is the **durable** standing-wave path:

  * Writes go through ``VaultStore.store`` only (INV-21 one-mutation-path;
    this module must be allowlisted when GREEN).
  * Default epistemic status is SPECULATIVE (INV-22/23); COHERENT only via
    explicit authorized seal (INV-29 transitions stay in vault/store.py).
  * Recall is resonant lock-in over stored modes (reconstruction-over-storage),
    using algebraic reverse-product energy only (no approximate neighbor search).
  * Empty spectrum / cold start refuses confabulated recall.

Status: RED stubs (#21-adjacent productization). GREEN implements seal/load/recall.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Sequence

import numpy as np

from algebra.cl41 import N_COMPONENTS
from teaching.epistemic import EpistemicStatus
from vault.store import VaultStore

_SCHEMA = "holographic_mode_v1"
_KIND = "standing_wave_mode"
_CLOSURE_TOL = 1e-6


class HolographicVaultError(ValueError):
    """Fail-closed refusal from holographic vault operations."""

    def __init__(self, reason: str, **disclosure: Any) -> None:
        self.reason = reason
        self.disclosure = dict(disclosure)
        super().__init__(f"holographic_vault refused [{reason}]: {self.disclosure}")


@dataclass(frozen=True, slots=True)
class SealedMode:
    """One durable standing-wave mode as reconstructed from the vault."""

    mode: np.ndarray
    vault_index: int
    epistemic_status: EpistemicStatus
    mode_id: str
    metadata: dict[str, Any]


class HolographicVaultStore:
    """Durable standing-wave spectrum backed by VaultStore + WaveManifold recall.

    Does not invent a parallel memory path: every durable write is
    ``VaultStore.store``. Session manifold is a reconstruction cache.
    """

    def __init__(
        self,
        vault: Optional[VaultStore] = None,
        *,
        epsilon_drift: float = 1e-6,
    ) -> None:
        self._vault = vault if vault is not None else VaultStore()
        self.epsilon_drift = float(epsilon_drift)
        # Session reconstruction cache — never the sole source of truth.
        self._mode_ids: list[str] = []

    @property
    def vault(self) -> VaultStore:
        return self._vault

    def seal_mode(
        self,
        psi: np.ndarray,
        *,
        mode_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> SealedMode:
        """Persist a standing-wave mode as SPECULATIVE (default admission).

        Refuses non-closed / high-drift states. Never writes COHERENT.
        """
        raise NotImplementedError(
            "HolographicVaultStore.seal_mode: ADR-0241 holographic vault GREEN pending"
        )

    def seal_mode_reviewed(
        self,
        psi: np.ndarray,
        *,
        authorized: bool = False,
        mode_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> SealedMode:
        """Persist a mode as COHERENT — only with explicit authorization.

        Unauthorized calls refuse (proposal-only; same discipline as GoldTether
        promote). Does not self-authorize.
        """
        raise NotImplementedError(
            "HolographicVaultStore.seal_mode_reviewed: ADR-0241 GREEN pending"
        )

    def load_spectrum(
        self,
        *,
        min_status: EpistemicStatus | None = None,
    ) -> tuple[SealedMode, ...]:
        """Rebuild the standing-wave spectrum from the vault (restart path).

        Reconstruction-over-storage: manifold cache is cleared and refilled
        from vault entries tagged as standing-wave modes.
        """
        raise NotImplementedError(
            "HolographicVaultStore.load_spectrum: ADR-0241 GREEN pending"
        )

    def resonant_recall(
        self,
        psi_query: np.ndarray,
        *,
        min_status: EpistemicStatus | None = None,
    ) -> tuple[np.ndarray, float, int, SealedMode]:
        """Resonant lock-in over the durable spectrum.

        Empty spectrum / cold start without load → refuse (no confabulation).
        Uses algebraic reverse-product energy, never cosine/ANN.
        """
        raise NotImplementedError(
            "HolographicVaultStore.resonant_recall: ADR-0241 GREEN pending"
        )

    def spectrum_size(self) -> int:
        """Number of standing-wave modes currently in the reconstruction cache."""
        raise NotImplementedError(
            "HolographicVaultStore.spectrum_size: ADR-0241 GREEN pending"
        )


__all__ = [
    "HolographicVaultError",
    "HolographicVaultStore",
    "SealedMode",
    "_SCHEMA",
    "_KIND",
]
