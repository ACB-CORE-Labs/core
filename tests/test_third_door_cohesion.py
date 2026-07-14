"""Third-Door / ADR-0241 entity cohesion suite.

Authority: docs/analysis/core_cohesion_master_plan.md
Pins Phase 0 audits (A-02…A-04, pre-deprecation grep), entity invariants
I-01…I-05 (progressive), serve quarantine, and vault public ABI.

Deterministic fixtures only — no random Euclidean-norm spinors as truth.
"""

from __future__ import annotations

import ast
import importlib.util
import re
from pathlib import Path

import numpy as np
import pytest

from algebra.cl41 import N_COMPONENTS
from algebra.rotor import make_rotor_from_angle
from algebra.versor import versor_condition
from core.physics.biography import integrate_biography
from core.physics.holographic_vault import HolographicVaultError, HolographicVaultStore
from core.physics.self_authorship import SelfAuthorshipMiner
from core.physics.wave_manifold import WaveManifold
from teaching.epistemic import EpistemicStatus
from vault.store import VaultStore

_ROOT = Path(__file__).resolve().parents[1]
_CLOSURE = 1e-6
# VaultStore stores float32; I-02 float64 ideal is 1e-12. Honest dual pin:
_I02_F32_TOL = 1e-6
_I02_F64_PATH_TOL = 1e-12


def _closed(angle: float = 0.3, plane: int = 6) -> np.ndarray:
    return make_rotor_from_angle(angle, bivector_idx=plane)


# --- Phase 0 / pre-deprecation hygiene ---------------------------------------


def test_phase0_a02_wave_bindings_in_third_door_operators():
    """A-02: surprise + dynamic_manifold bind WaveManifold (not parallel residual)."""
    surprise_src = (_ROOT / "core/physics/surprise.py").read_text()
    dyn_src = (_ROOT / "core/physics/dynamic_manifold.py").read_text()
    assert "WaveManifold" in surprise_src
    assert "compute_spectral_leakage" in surprise_src
    assert "WaveManifold" in dyn_src
    assert "wave_field_conjugacy" in dyn_src or "wave_analogical_polar" in dyn_src


def test_phase0_a04_serve_path_quarantines_wave_and_fibonacci():
    """A-04: chat/runtime must not import wave / holographic / fibonacci / packing."""
    runtime_path = _ROOT / "chat/runtime.py"
    src = runtime_path.read_text()
    tree = ast.parse(src)
    banned_roots = {
        "wave_manifold",
        "holographic_vault",
        "fibonacci_search",
        "atlas_packing",
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                leaf = alias.name.split(".")[-1]
                assert leaf not in banned_roots, f"banned import {alias.name}"
                assert "wave_manifold" not in alias.name
                assert "holographic_vault" not in alias.name
                assert "fibonacci_search" not in alias.name
        if isinstance(node, ast.ImportFrom) and node.module:
            mod = node.module
            for ban in banned_roots:
                assert ban not in mod, f"banned from-import {mod}"
            if node.names:
                for alias in node.names:
                    assert alias.name not in banned_roots


def test_pre_deprecation_grep_no_core_ha_imports_in_python():
    """Pre-deprecation: no live Python import of core_ha / hyperbolic_primitives."""
    offenders: list[str] = []
    patterns = (
        re.compile(r"^\s*(import\s+core_ha\b|from\s+core_ha\b)"),
        re.compile(r"^\s*(import\s+hyperbolic_primitives\b|from\s+hyperbolic_primitives\b)"),
    )
    skip_dirs = {
        ".git",
        ".venv",
        "venv",
        "node_modules",
        "__pycache__",
        ".pytest_cache",
        "workbench-ui",
    }
    for path in _ROOT.rglob("*.py"):
        if any(part in skip_dirs for part in path.parts):
            continue
        # Tests may *mention* core_ha in strings/asserts; ban only import statements.
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if line.lstrip().startswith("#"):
                continue
            for pat in patterns:
                if pat.search(line):
                    offenders.append(f"{path.relative_to(_ROOT)}:{i}:{line.strip()}")
    assert not offenders, "legacy imports found:\n" + "\n".join(offenders)


def test_core_ha_package_absent():
    assert importlib.util.find_spec("core_ha") is None


def test_holographic_vault_does_not_touch_private_versors():
    """P1: holographic reload uses public VaultStore ABI only."""
    src = (_ROOT / "core/physics/holographic_vault.py").read_text()
    assert "._versors" not in src
    assert "get_versor" in src


# --- I-05 unitary amplitude ---------------------------------------------------


def test_i05_unitary_propagator_amplitude_conservation():
    M = WaveManifold()
    psi = _closed(0.41, plane=7)
    R = _closed(0.22, plane=6)
    out = M.sandwich_step(psi, R)
    assert M.measure_unitary_residual(out) < _CLOSURE
    B = np.zeros(N_COMPONENTS, dtype=np.float64)
    B[9] = 1.0
    stepped = M.algebraic_schrodinger_step(psi, B, dt=0.25)
    assert M.measure_unitary_residual(stepped) < _CLOSURE


# --- I-02 vault round-trip (honest float32 storage) ---------------------------


def test_i02_holographic_round_trip_float32_honest():
    """I-02: seal → new instance load recovers mode within float32 store tol."""
    vault = VaultStore()
    hv1 = HolographicVaultStore(vault)
    psi = _closed(0.45, plane=7).astype(np.float64)
    sealed = hv1.seal_mode(psi, mode_id="i02-roundtrip")
    assert sealed.epistemic_status is EpistemicStatus.SPECULATIVE

    hv2 = HolographicVaultStore(vault)
    loaded = hv2.load_spectrum()
    assert len(loaded) == 1
    recovered = loaded[0].mode
    err = float(np.linalg.norm(recovered.astype(np.float64) - psi))
    # Storage is float32: cannot claim 1e-12 bit identity after cast.
    assert err < _I02_F32_TOL, f"round-trip err {err:.3e} exceeds float32 tol"

    # Public ABI path used for reload
    entry = vault.get_entry(sealed.vault_index)
    assert entry["index"] == sealed.vault_index
    assert float(np.linalg.norm(entry["versor"].astype(np.float64) - recovered)) < _I02_F32_TOL


def test_vault_get_versor_out_of_range():
    vault = VaultStore()
    with pytest.raises(IndexError):
        vault.get_versor(0)


# --- I-01 biography + holographic restart ------------------------------------


def test_i01_biography_holonomy_closed_and_modes_reloadable():
    """I-01: holonomy closed; trajectory modes durable via holographic vault."""
    traj = [_closed(0.1 * (i + 1), plane=6 + (i % 3)) for i in range(4)]
    blade = integrate_biography(traj)
    assert blade.closure < _CLOSURE
    assert versor_condition(blade.blade) < _CLOSURE

    vault = VaultStore()
    hv = HolographicVaultStore(vault)
    for i, v in enumerate(traj):
        hv.seal_mode(v, mode_id=f"bio-step-{i}")
    hv2 = HolographicVaultStore(vault)
    spectrum = hv2.load_spectrum()
    assert len(spectrum) == len(traj)
    # Reconstruct biography from reloaded modes preserves closure
    reloaded = [s.mode for s in spectrum]
    blade2 = integrate_biography(reloaded)
    assert blade2.closure < _CLOSURE
    assert blade2.n_steps == blade.n_steps


# --- I-03 self-authorship never COHERENT-seals --------------------------------


def test_i03_self_authorship_proposals_are_speculative_only():
    miner = SelfAuthorshipMiner(residual_threshold=1e-12)
    a = _closed(0.2, plane=6)
    b = _closed(0.9, plane=7)
    proposals = miner.mine_from_trajectory(b, a)
    for p in proposals:
        assert p.epistemic_status == "SPECULATIVE"
        assert p.epistemic_status != "COHERENT"


def test_i03_holographic_reviewed_refuses_without_authorization():
    hv = HolographicVaultStore(VaultStore())
    with pytest.raises(HolographicVaultError, match="authoriz"):
        hv.seal_mode_reviewed(_closed(0.2), authorized=False, mode_id="nope")


# --- I-04 phase correlation ---------------------------------------------------


def test_i04_phase_correlation_symmetric_algebraic():
    M = WaveManifold()
    a = _closed(0.2, plane=6)
    b = _closed(0.55, plane=8)
    rho_ab = M.phase_correlation(a, b)
    rho_ba = M.phase_correlation(b, a)
    assert abs(rho_ab - rho_ba) < 1e-12
    # Self-correlation positive for unit-ish rotors
    assert M.phase_correlation(a, a) > 0.5


def test_i04_wave_manifold_forbids_approx_neighbor_imports():
    src = (_ROOT / "core/physics/wave_manifold.py").read_text()
    tree = ast.parse(src)
    banned = {"faiss", "hnswlib", "annoy", "sklearn"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] not in banned
        if isinstance(node, ast.ImportFrom) and node.module:
            assert node.module.split(".")[0] not in banned


# --- Superposition reconstruct (P3) ------------------------------------------


def test_resonant_reconstruct_partial_combo_closer_than_pure_modes():
    M = WaveManifold()
    a = _closed(0.2, plane=6)
    b = _closed(0.9, plane=10)
    # Query biased toward a linear combo of modes (equal mix in ambient space).
    query = 0.6 * a + 0.4 * b
    modes = [a, b]
    psi_hat, coeffs, energies = M.resonant_reconstruct(query, modes=modes)
    assert coeffs.shape == (2,)
    assert energies.shape == (2,)
    err_hat = float(np.linalg.norm(psi_hat - query))
    err_a = float(np.linalg.norm(a - query))
    err_b = float(np.linalg.norm(b - query))
    assert err_hat < err_a
    assert err_hat < err_b
    # Mass-normalized coeffs should favor the dominant overlap direction.
    assert abs(float(np.sum(np.abs(coeffs))) - 1.0) < 1e-9 or float(np.sum(np.abs(coeffs))) == 0.0


def test_resonant_reconstruct_empty_refused():
    M = WaveManifold()
    with pytest.raises(ValueError, match="empty mode set"):
        M.resonant_reconstruct(_closed(0.1))


# --- ADR-0242 placeholder (Fibonacci not yet landed) --------------------------


def test_fibonacci_search_goldtether_integration():
    """Asserts Fibonacci search can optimize kappa and return a valid certificate."""
    from core.physics.fibonacci_search import BoundedUnimodalObjective, fibonacci_section_search

    objective = BoundedUnimodalObjective(
        lower=0.1,
        upper=2.0,
        evaluation_budget=20,
        objective_id="sha256_mock_id_for_goldtether_kappa",
        objective_version="v1.0",
    )

    def synthetic_objective(kappa: float) -> float:
        return (kappa - 0.789) ** 2  # unimodal minimum at 0.789

    trace = fibonacci_section_search(objective, synthetic_objective)
    assert abs(trace.best_observed_point - 0.789) < 1e-3
    assert len(trace.eval_sequence) == 20
    assert trace.certificate.get("budget") == 20
