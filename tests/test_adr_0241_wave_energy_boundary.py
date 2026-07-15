"""P10 Trace B — wave residual → energy boundary + Fibonacci τ + crystallization.

ADR-0241 cohesion package P10:
  * Unitary residual from WaveManifold feeds energy / trajectory gates.
  * Multi-scale recency τ_n = F_n · τ_0 is a constants table (not dogma).
  * E0–E1 crystallization + closed residual may SPECULATIVE-seal; else refuse.
  * Serve remains quarantined from this module.
"""

from __future__ import annotations

import ast
from pathlib import Path

import numpy as np
import pytest

from algebra.rotor import make_rotor_from_angle
from core.physics.energy import EnergyClass
from core.physics.wave_energy_boundary import (
    CrystallizationDecision,
    assess_wave_trajectory,
    crystallization_for_holographic_seal,
    energy_profile_from_wave,
    fibonacci_tau_schedule,
    recency_band_index,
    wave_unitary_residual,
)
from core.physics.trajectory_invariants import TrajectoryInvariantError

_ROOT = Path(__file__).resolve().parents[1]


def _closed(angle: float = 0.3, plane: int = 6) -> np.ndarray:
    return make_rotor_from_angle(angle, bivector_idx=plane)


def _dirty() -> np.ndarray:
    v = np.zeros(32, dtype=np.float64)
    v[0] = 0.5
    v[1] = 0.5
    return v


# --- Wave residual wiring ---------------------------------------------------


def test_wave_unitary_residual_closed_under_eps():
    r = wave_unitary_residual(_closed(0.25))
    assert r < 1e-6


def test_wave_unitary_residual_dirty_above_eps():
    r = wave_unitary_residual(_dirty())
    assert r > 1e-6


def test_energy_profile_from_wave_uses_residual():
    profile = energy_profile_from_wave(_closed(0.1))
    assert profile.coherence_residual < 1e-6
    # Low residual + defaults → crystallizable class (E0/E1).
    assert profile.energy_class in {EnergyClass.E0, EnergyClass.E1}


def test_energy_profile_from_wave_high_residual_feeds_raw():
    profile = energy_profile_from_wave(_dirty())
    # Operator clamps residual into [0,1] for the scalar mix.
    assert profile.coherence_residual > 0.0


def test_assess_wave_trajectory_closed_path_energy_ok():
    steps = [_closed(0.1 * i, plane=6) for i in range(1, 5)]
    assessment = assess_wave_trajectory(steps)
    assert assessment.energy_ok is True
    assert assessment.n_steps == 4
    assert assessment.within_replay_bound is True


def test_assess_wave_trajectory_refuses_empty():
    with pytest.raises(TrajectoryInvariantError):
        assess_wave_trajectory([])


# --- Fibonacci multi-scale τ ------------------------------------------------


def test_fibonacci_tau_schedule_matches_F_n_tau0():
    # F_1=1, F_2=1, F_3=2, F_4=3, F_5=5
    taus = fibonacci_tau_schedule(tau0=0.5, levels=5)
    assert taus == (0.5, 0.5, 1.0, 1.5, 2.5)


def test_fibonacci_tau_schedule_rejects_bad_inputs():
    with pytest.raises(ValueError):
        fibonacci_tau_schedule(tau0=0.0, levels=3)
    with pytest.raises(ValueError):
        fibonacci_tau_schedule(tau0=1.0, levels=0)


def test_recency_band_index_progressive():
    taus = fibonacci_tau_schedule(tau0=1.0, levels=5)  # 1,1,2,3,5
    assert recency_band_index(0.5, taus) == 0
    assert recency_band_index(1.0, taus) == 0
    assert recency_band_index(1.5, taus) == 2
    assert recency_band_index(10.0, taus) == len(taus)  # beyond schedule


# --- Crystallization ↔ holographic seal policy ------------------------------


def test_crystallization_closed_e0_may_speculative_seal():
    decision = crystallization_for_holographic_seal(_closed(0.12))
    assert isinstance(decision, CrystallizationDecision)
    assert decision.residual_closed is True
    assert decision.vault_candidate is True
    assert decision.may_speculative_seal is True
    assert decision.energy.energy_class.vault_candidate is True


def test_crystallization_dirty_refuses_seal():
    decision = crystallization_for_holographic_seal(_dirty())
    assert decision.residual_closed is False
    assert decision.may_speculative_seal is False


def test_crystallization_high_activity_not_vault_candidate():
    # Force E3/E4 via structural inputs while residual stays closed.
    decision = crystallization_for_holographic_seal(
        _closed(0.05),
        convergence_density=20,
        activation_count=20,
        current_cycle=1,
        last_activation_cycle=1,
        anchor_adjacent=True,
    )
    assert decision.residual_closed is True
    assert decision.vault_candidate is False
    assert decision.may_speculative_seal is False


# --- Serve quarantine -------------------------------------------------------


def test_serve_runtime_does_not_import_wave_energy_boundary():
    tree = ast.parse((_ROOT / "chat/runtime.py").read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            assert "wave_energy_boundary" not in node.module
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert "wave_energy_boundary" not in alias.name
