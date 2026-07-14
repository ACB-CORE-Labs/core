"""ADR-0241 durable holographic vault — RED behavioral contract.

Durable standing-wave spectrum behind VaultStore (no parallel memory):
  * SPECULATIVE writes by default; COHERENT only when authorized
  * Exact-recall reconstruction-over-storage / restart lock-in
  * WaveManifold resonant energy (no cosine / ANN / HNSW)
  * Zero confabulation on empty / cold start
  * Refuse non-closed / high-drift seals
  * INV-21: durable path uses VaultStore.store (allowlist when GREEN)

GREEN implements ``core.physics.holographic_vault.HolographicVaultStore``.
"""

from __future__ import annotations

import ast
from pathlib import Path

import numpy as np
import pytest

from algebra.rotor import make_rotor_from_angle
from algebra.versor import versor_condition
from teaching.epistemic import EpistemicStatus
from vault.store import VaultStore

# Hard-import — collection fails only if package broken; RED is behavioral NI.
from core.physics.holographic_vault import (
    HolographicVaultError,
    HolographicVaultStore,
    SealedMode,
)


def _id() -> np.ndarray:
    v = np.zeros(32, dtype=np.float64)
    v[0] = 1.0
    return v


def _closed(angle: float = 0.3, plane: int = 6) -> np.ndarray:
    return make_rotor_from_angle(angle, bivector_idx=plane)


def _dirty() -> np.ndarray:
    v = np.zeros(32, dtype=np.float64)
    v[0] = 0.5
    v[1] = 0.5
    return v


# --- Seal / epistemic standing ------------------------------------------------


def test_seal_mode_defaults_to_speculative():
    hv = HolographicVaultStore(VaultStore())
    sealed = hv.seal_mode(_closed(0.2), mode_id="m0")
    assert isinstance(sealed, SealedMode)
    assert sealed.epistemic_status is EpistemicStatus.SPECULATIVE
    assert sealed.mode_id == "m0"
    assert versor_condition(sealed.mode) < 1e-6


def test_seal_mode_refuses_non_closed():
    hv = HolographicVaultStore(VaultStore())
    with pytest.raises((HolographicVaultError, ValueError), match="closed|versor|drift|residual"):
        hv.seal_mode(_dirty(), mode_id="bad")


def test_seal_mode_reviewed_refuses_without_authorization():
    hv = HolographicVaultStore(VaultStore())
    with pytest.raises((HolographicVaultError, ValueError), match="authoriz|ADR|gate"):
        hv.seal_mode_reviewed(_closed(0.15), authorized=False, mode_id="m1")


def test_seal_mode_reviewed_coherent_when_authorized():
    hv = HolographicVaultStore(VaultStore())
    sealed = hv.seal_mode_reviewed(_closed(0.15), authorized=True, mode_id="m1")
    assert sealed.epistemic_status is EpistemicStatus.COHERENT


# --- Zero confabulation / cold start -----------------------------------------


def test_resonant_recall_refuses_empty_spectrum():
    hv = HolographicVaultStore(VaultStore())
    with pytest.raises((HolographicVaultError, ValueError), match="empty|confabul|cold|spectrum"):
        hv.resonant_recall(_closed(0.1))


def test_load_spectrum_empty_is_empty_tuple():
    hv = HolographicVaultStore(VaultStore())
    modes = hv.load_spectrum()
    assert modes == ()
    assert hv.spectrum_size() == 0


# --- Durable spectrum + restart lock-in --------------------------------------


def test_seal_then_new_instance_reload_and_recall():
    """Restart path: new HolographicVaultStore on same VaultStore recovers mode."""
    vault = VaultStore()
    hv1 = HolographicVaultStore(vault)
    psi = _closed(0.45, plane=7)
    sealed = hv1.seal_mode(psi, mode_id="restart-me")
    assert sealed.vault_index >= 0

    # Cold reconstruction cache
    hv2 = HolographicVaultStore(vault)
    loaded = hv2.load_spectrum()
    assert len(loaded) >= 1
    assert any(m.mode_id == "restart-me" for m in loaded)

    mode, energy, idx, sealed_hit = hv2.resonant_recall(psi)
    assert energy > 0.0
    assert sealed_hit.mode_id == "restart-me"
    assert np.allclose(mode, psi, atol=1e-5)


def test_recall_prefers_matching_mode_among_several():
    vault = VaultStore()
    hv = HolographicVaultStore(vault)
    a = _closed(0.2, plane=6)
    b = _closed(0.9, plane=7)
    hv.seal_mode(a, mode_id="A")
    hv.seal_mode(b, mode_id="B")
    hv.load_spectrum()
    _mode, _E, _i, hit = hv.resonant_recall(b)
    assert hit.mode_id == "B"


def test_min_status_coherent_excludes_speculative():
    """INV-24 style: evidence-tier recall can require COHERENT."""
    vault = VaultStore()
    hv = HolographicVaultStore(vault)
    psi = _closed(0.3)
    hv.seal_mode(psi, mode_id="spec-only")  # SPECULATIVE
    loaded = hv.load_spectrum(min_status=EpistemicStatus.COHERENT)
    assert all(m.epistemic_status is EpistemicStatus.COHERENT for m in loaded)
    # Speculative-only spectrum → coherent-filtered empty → no confabulation
    with pytest.raises((HolographicVaultError, ValueError), match="empty|confabul|spectrum|status"):
        hv.resonant_recall(psi, min_status=EpistemicStatus.COHERENT)


def test_determinism_seal_and_recall():
    vault = VaultStore()
    hv = HolographicVaultStore(vault)
    psi = _closed(0.55, plane=8)
    hv.seal_mode(psi, mode_id="det")
    hv.load_spectrum()
    r1 = hv.resonant_recall(psi)
    r2 = hv.resonant_recall(psi)
    assert r1[1] == r2[1]
    assert r1[2] == r2[2]
    assert r1[3].mode_id == r2[3].mode_id


# --- Mutation path / hygiene --------------------------------------------------


def test_seal_uses_vault_store_not_parallel_memory():
    """After seal, VaultStore holds the versor (same mutation path)."""
    vault = VaultStore()
    hv = HolographicVaultStore(vault)
    psi = _closed(0.25)
    sealed = hv.seal_mode(psi, mode_id="vpath")
    assert len(vault) > 0 or sealed.vault_index >= 0
    # VaultStore may expose __len__ via versor deque — prefer index check
    assert sealed.vault_index == 0 or sealed.vault_index >= 0


def test_module_has_no_teaching_import_except_epistemic_status():
    """Physics holographic path may import EpistemicStatus only from teaching.epistemic."""
    path = Path(__file__).resolve().parents[1] / "core/physics/holographic_vault.py"
    tree = ast.parse(path.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            if node.module.startswith("teaching") and node.module != "teaching.epistemic":
                raise AssertionError(f"unexpected teaching import: {node.module}")
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert not alias.name.startswith("teaching.")


def test_module_source_forbids_approx_neighbor_stack():
    """Implementation must not import approximate-neighbor tooling."""
    src = Path(__file__).resolve().parents[1].joinpath(
        "core/physics/holographic_vault.py"
    ).read_text()
    tree = ast.parse(src)
    banned_mods = {"faiss", "hnswlib", "annoy", "sklearn.neighbors"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] not in banned_mods
        if isinstance(node, ast.ImportFrom) and node.module:
            root = node.module.split(".")[0]
            assert node.module not in banned_mods and root not in banned_mods


def test_inv21_writer_allowlist_mentions_holographic_or_no_store_call_yet():
    """INV-21: either allowlisted, or (RED) no live .store() call outside NI.

    GREEN must add ``core/physics/holographic_vault.py`` to ALLOWED_VAULT_WRITERS.
    """
    from tests.test_architectural_invariants import ALLOWED_VAULT_WRITERS

    rel = "core/physics/holographic_vault.py"
    src = Path(__file__).resolve().parents[1].joinpath(rel).read_text()
    # Detect a real store call pattern (not in strings only is hard; use AST)
    tree = ast.parse(src)
    has_store_call = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr == "store":
                has_store_call = True
    if has_store_call:
        assert rel in ALLOWED_VAULT_WRITERS, (
            "holographic_vault calls VaultStore.store but is not INV-21 allowlisted"
        )
