"""
core/physics/holographic_vault.py

ADR-0241 durable holographic standing-wave spectrum (vault-backed).

Session-local WaveManifold modes are not enough for restart lock-in. This
module is the **durable** standing-wave path:

  * Writes go through ``VaultStore.store`` only (INV-21 one-mutation-path;
    this module is on ALLOWED_VAULT_WRITERS).
  * Default epistemic status is SPECULATIVE (INV-22/23); COHERENT only via
    explicit authorized seal (status stamped at store time — INV-29 remains
    owned by vault/store.py transitions).
  * Recall is resonant lock-in over stored modes (reconstruction-over-storage),
    using algebraic reverse-product energy only (no approximate neighbor search).
  * Empty spectrum / cold start refuses confabulated recall.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Optional

import numpy as np

from algebra.backend import versor_condition
from algebra.cl41 import N_COMPONENTS
from core.physics.wave_manifold import WaveManifold
# SANCTIONED SEAM (W1 Finding #4): the one physics→teaching import — boundary
# vocabulary only (SPECULATIVE/COHERENT standing), no teaching logic crosses.
# Extraction to a shared kernel is deferred until a second physics module
# needs the vocabulary (32 consumers repo-wide; not a LOW-batch relocation).
# NOTE: core/epistemic_state.py holds a DIFFERENT concept (turn-level
# EpistemicState) — do not merge the two.
from teaching.epistemic import EpistemicStatus
from vault.store import VaultStore, _parse_entry_status, _status_admits

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


def _as_mv(psi: np.ndarray, name: str = "ψ") -> np.ndarray:
    arr = np.asarray(psi, dtype=np.float64)
    if arr.shape != (N_COMPONENTS,):
        raise HolographicVaultError(
            "bad_shape", name=name, shape=tuple(arr.shape)
        )
    return arr


def _default_mode_id(psi: np.ndarray) -> str:
    digest = hashlib.sha256(np.asarray(psi, dtype=np.float64).tobytes()).hexdigest()
    return f"mode-{digest[:16]}"


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
        self._manifold = WaveManifold(epsilon_drift=self.epsilon_drift)
        # Reconstruction cache (never sole source of truth).
        self._sealed: list[SealedMode] = []

    @property
    def vault(self) -> VaultStore:
        return self._vault

    def _admit(self, psi: np.ndarray) -> np.ndarray:
        """Refuse non-closed or high-drift states (dual-checked unitary residual)."""
        arr = _as_mv(psi)
        cond = float(versor_condition(arr))
        drift = float(self._manifold.measure_unitary_residual(arr))
        if cond >= _CLOSURE_TOL or drift > self.epsilon_drift:
            raise HolographicVaultError(
                "not_closed_or_high_drift",
                versor_condition=cond,
                residual=drift,
                epsilon_drift=self.epsilon_drift,
            )
        return arr

    def _seal(
        self,
        psi: np.ndarray,
        *,
        status: EpistemicStatus,
        mode_id: str | None,
        metadata: dict[str, Any] | None,
    ) -> SealedMode:
        arr = self._admit(psi)
        mid = mode_id if mode_id is not None else _default_mode_id(arr)
        meta: dict[str, Any] = dict(metadata) if metadata else {}
        meta.update(
            {
                "kind": _KIND,
                "schema_version": _SCHEMA,
                "mode_id": mid,
            }
        )
        idx = self._vault.store(arr, meta, epistemic_status=status)
        sealed = SealedMode(
            mode=arr.copy(),
            vault_index=int(idx),
            epistemic_status=status,
            mode_id=mid,
            metadata=dict(meta),
        )
        # Warm reconstruction cache so same-instance recall works after seal.
        self._manifold.register_resonant_mode(arr)
        self._sealed.append(sealed)
        return sealed

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
        return self._seal(
            psi,
            status=EpistemicStatus.SPECULATIVE,
            mode_id=mode_id,
            metadata=metadata,
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

        Unauthorized calls refuse (proposal-only). Does not self-authorize.
        """
        if not authorized:
            raise HolographicVaultError(
                "authorization_required",
                detail="seal_mode_reviewed requires authorized=True (review gate)",
            )
        return self._seal(
            psi,
            status=EpistemicStatus.COHERENT,
            mode_id=mode_id,
            metadata=metadata,
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
        self._manifold.clear_resonant_modes()
        self._sealed.clear()
        for i, meta in self._vault.iter_metadata():
            if meta.get("kind") != _KIND:
                continue
            status = _parse_entry_status(meta.get("epistemic_status", "speculative"))
            if min_status is not None and not _status_admits(status, min_status):
                continue
            # Public read ABI — never reach into VaultStore private deques.
            mode = np.asarray(self._vault.get_versor(i), dtype=np.float64)
            mid = str(meta.get("mode_id") or f"idx-{i}")
            sealed = SealedMode(
                mode=mode,
                vault_index=int(i),
                epistemic_status=status,
                mode_id=mid,
                metadata=dict(meta),
            )
            self._manifold.register_resonant_mode(mode)
            self._sealed.append(sealed)
        return tuple(self._sealed)

    def resonant_recall(
        self,
        psi_query: np.ndarray,
        *,
        min_status: EpistemicStatus | None = None,
    ) -> tuple[np.ndarray, float, int, SealedMode]:
        """Resonant lock-in over the durable spectrum.

        Empty spectrum / cold start without modes → refuse (no confabulation).
        Uses algebraic reverse-product energy via WaveManifold.
        """
        spectrum = self._spectrum_for_status(min_status)
        if not spectrum:
            raise HolographicVaultError(
                "empty_spectrum",
                detail="no standing-wave modes for resonant recall (no confabulation)",
            )
        query = _as_mv(psi_query, "ψ_query")
        modes = [s.mode for s in spectrum]
        mode, energy, idx = self._manifold.resonant_recall(query, modes=modes)
        return mode, float(energy), int(idx), spectrum[int(idx)]

    def resonant_reconstruct(
        self,
        psi_query: np.ndarray,
        *,
        min_status: EpistemicStatus | None = None,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, tuple[SealedMode, ...]]:
        """Superposition reconstruct over the durable spectrum.

        ``min_status=COHERENT`` excludes SPECULATIVE modes so hypothesis
        mass cannot masquerade as reviewed evidence (Trace A / INV-24).
        Empty filtered spectrum refuses (no confabulation).
        """
        spectrum = self._spectrum_for_status(min_status)
        if not spectrum:
            raise HolographicVaultError(
                "empty_spectrum",
                detail=(
                    "no standing-wave modes for resonant reconstruct "
                    f"(min_status={getattr(min_status, 'value', min_status)!r})"
                ),
            )
        query = _as_mv(psi_query, "ψ_query")
        modes = [s.mode for s in spectrum]
        psi_hat, coeffs, energies = self._manifold.resonant_reconstruct(
            query, modes=modes
        )
        return psi_hat, coeffs, energies, tuple(spectrum)

    def _spectrum_for_status(
        self,
        min_status: EpistemicStatus | None,
    ) -> list[SealedMode]:
        if min_status is not None:
            # Rebuild filtered view so COHERENT-tier evidence excludes SPECULATIVE.
            return list(self.load_spectrum(min_status=min_status))
        spectrum = list(self._sealed)
        if not spectrum:
            # Cold start: attempt unfiltered load once.
            spectrum = list(self.load_spectrum())
        return spectrum

    def spectrum_size(self) -> int:
        """Number of standing-wave modes currently in the reconstruction cache."""
        return len(self._sealed)


__all__ = [
    "HolographicVaultError",
    "HolographicVaultStore",
    "SealedMode",
    "_SCHEMA",
    "_KIND",
]
