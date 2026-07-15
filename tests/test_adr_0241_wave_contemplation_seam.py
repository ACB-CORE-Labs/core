"""P9 Trace A — contemplation → SPECULATIVE holographic seal → teaching corridor.

ADR-0241 cohesion plan package P9:
  * Contemplation may SPECULATIVE-seal standing-wave modes (no COHERENT).
  * Resonant reconstruct as *hypothesis* may use SPECULATIVE spectrum.
  * Resonant reconstruct as *evidence* requires min_status=COHERENT.
  * Serve path remains quarantined from this seam.
  * Writes go only through HolographicVaultStore.seal_mode (INV-21).
"""

from __future__ import annotations

import ast
from pathlib import Path

import numpy as np
import pytest

from algebra.rotor import make_rotor_from_angle
from core.contemplation.schema import FindingKind
from core.physics.holographic_vault import HolographicVaultError, HolographicVaultStore
from teaching.epistemic import EpistemicStatus
from vault.store import VaultStore

from core.contemplation.wave_seam import (
    WaveModeHypothesis,
    WaveReconstructResult,
    reconstruct_as_evidence,
    reconstruct_as_hypothesis,
    speculative_seal_from_contemplation,
)

_ROOT = Path(__file__).resolve().parents[1]


def _closed(angle: float = 0.3, plane: int = 6) -> np.ndarray:
    return make_rotor_from_angle(angle, bivector_idx=plane)


# --- SPECULATIVE seal from contemplation ------------------------------------


def test_speculative_seal_writes_speculative_only():
    hv = HolographicVaultStore(VaultStore())
    hyp = speculative_seal_from_contemplation(
        hv,
        _closed(0.21),
        substrate_hash="sub-abc",
        subject="mode-from-contemplation",
        mode_id="p9-m0",
    )
    assert isinstance(hyp, WaveModeHypothesis)
    assert hyp.sealed.epistemic_status is EpistemicStatus.SPECULATIVE
    assert hyp.sealed.mode_id == "p9-m0"
    assert hyp.finding.epistemic_status is EpistemicStatus.SPECULATIVE
    assert hyp.finding.kind is FindingKind.RESONANT_MODE_CANDIDATE
    assert hyp.finding.substrate_hash == "sub-abc"
    assert hyp.standing == "hypothesis"
    # Evidence ref points at vault mode, not pack mutation.
    assert any(
        e.source_type == "holographic_vault" and "p9-m0" in e.source_id
        for e in hyp.finding.evidence_refs
    )


def test_speculative_seal_refuses_non_closed():
    hv = HolographicVaultStore(VaultStore())
    dirty = np.zeros(32, dtype=np.float64)
    dirty[0] = 0.5
    dirty[1] = 0.5
    with pytest.raises((HolographicVaultError, ValueError)):
        speculative_seal_from_contemplation(
            hv, dirty, substrate_hash="sub", subject="bad"
        )


def test_seam_has_no_coherent_write_surface():
    """Contemplation seam must not *call* seal_mode_reviewed or VaultStore.store."""
    src = (_ROOT / "core/contemplation/wave_seam.py").read_text(encoding="utf-8")
    assert "min_status" in src  # evidence path filters COHERENT; does not write it
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Attribute) and func.attr in {
            "store",
            "seal_mode_reviewed",
        }:
            pytest.fail(
                f"wave_seam must not call .{func.attr}(...) "
                "(INV-21 / no COHERENT self-write)"
            )
        if isinstance(func, ast.Name) and func.id in {"store", "seal_mode_reviewed"}:
            pytest.fail(f"wave_seam must not call {func.id}(...)")


# --- Hypothesis vs evidence reconstruct -------------------------------------


def test_hypothesis_reconstruct_uses_speculative_spectrum():
    hv = HolographicVaultStore(VaultStore())
    psi = _closed(0.33, plane=7)
    speculative_seal_from_contemplation(
        hv, psi, substrate_hash="s", subject="m", mode_id="only-spec"
    )
    result = reconstruct_as_hypothesis(hv, psi)
    assert isinstance(result, WaveReconstructResult)
    assert result.standing == "hypothesis"
    assert result.psi_hat.shape == (32,)
    # Overlap with the sealed mode should be strong.
    assert float(np.linalg.norm(result.psi_hat)) > 0.0


def test_evidence_reconstruct_refuses_speculative_only_spectrum():
    """Evidence path requires COHERENT modes — SPECULATIVE must not masquerade."""
    hv = HolographicVaultStore(VaultStore())
    psi = _closed(0.18)
    speculative_seal_from_contemplation(
        hv, psi, substrate_hash="s", subject="m", mode_id="spec-only"
    )
    with pytest.raises((HolographicVaultError, ValueError), match="empty|COHERENT|evidence|spectrum"):
        reconstruct_as_evidence(hv, psi)


def test_evidence_reconstruct_accepts_coherent_modes():
    hv = HolographicVaultStore(VaultStore())
    psi = _closed(0.27, plane=8)
    # Teaching corridor: authorized COHERENT seal (not via contemplation seam).
    hv.seal_mode_reviewed(psi, authorized=True, mode_id="reviewed")
    result = reconstruct_as_evidence(hv, psi)
    assert result.standing == "evidence"
    assert result.min_status is EpistemicStatus.COHERENT
    assert float(np.linalg.norm(result.psi_hat)) > 0.0


def test_mixed_spectrum_evidence_ignores_speculative():
    hv = HolographicVaultStore(VaultStore())
    psi_coh = _closed(0.4, plane=6)
    psi_spec = _closed(0.9, plane=9)
    speculative_seal_from_contemplation(
        hv, psi_spec, substrate_hash="s", subject="spec", mode_id="spec"
    )
    hv.seal_mode_reviewed(psi_coh, authorized=True, mode_id="coh")
    # Evidence reconstruct should lock to COHERENT geometry, not SPECULATIVE.
    result = reconstruct_as_evidence(hv, psi_coh)
    assert result.standing == "evidence"
    # Coefficient mass on the single COHERENT mode.
    assert result.coeffs.shape[0] == 1


# --- Serve quarantine -------------------------------------------------------


def test_serve_runtime_does_not_import_wave_seam():
    runtime_path = _ROOT / "chat/runtime.py"
    tree = ast.parse(runtime_path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            assert "wave_seam" not in node.module
            assert "wave_contemplation" not in node.module
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert "wave_seam" not in alias.name
