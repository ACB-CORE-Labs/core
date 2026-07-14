"""#21 A — trajectory invariants + zero-fabrication (R&D §2.2)."""

from __future__ import annotations

import numpy as np
import pytest

from algebra.rotor import make_rotor_from_angle
from algebra.versor import versor_condition
from core.physics.trajectory_invariants import (
    TrajectoryInvariantError,
    assess_trajectory,
    energy_boundary_ok,
    relative_holonomy,
    trajectory_divergence,
)


def _id() -> np.ndarray:
    v = np.zeros(32, dtype=np.float64)
    v[0] = 1.0
    return v


def test_relative_holonomy_identity_pair_is_identity():
    H = relative_holonomy(_id(), _id())
    assert versor_condition(H) < 1e-6
    assert abs(H[0] - 1.0) < 1e-9


def test_relative_holonomy_order_sensitive():
    A = make_rotor_from_angle(0.3, bivector_idx=6)
    B = make_rotor_from_angle(0.9, bivector_idx=7)
    H_ab = relative_holonomy(A, B)
    H_ba = relative_holonomy(B, A)
    assert not np.allclose(H_ab, H_ba, atol=1e-9)


def test_trajectory_divergence_zero_on_constant_path():
    path = [_id(), _id(), _id()]
    assert trajectory_divergence(path) == 0.0


def test_trajectory_divergence_positive_on_moving_path():
    path = [
        make_rotor_from_angle(0.1 * i, bivector_idx=6) for i in range(1, 6)
    ]
    D = trajectory_divergence(path)
    assert D > 0.0


def test_trajectory_divergence_deterministic():
    path = [make_rotor_from_angle(0.2 * i) for i in range(1, 4)]
    assert trajectory_divergence(path) == trajectory_divergence(path)


def test_trajectory_divergence_refuses_empty_and_short():
    with pytest.raises(TrajectoryInvariantError, match="empty"):
        trajectory_divergence([])
    with pytest.raises(TrajectoryInvariantError, match="too_short"):
        trajectory_divergence([_id()])


def test_trajectory_divergence_refuses_non_closed():
    dirty = np.zeros(32, dtype=np.float64)
    dirty[0] = 0.5
    dirty[1] = 0.5
    with pytest.raises(TrajectoryInvariantError, match="not_closed"):
        trajectory_divergence([_id(), dirty])


def test_energy_boundary_ok_and_refuse_negative():
    assert energy_boundary_ok(1.0, 2.0, kappa=1.0) is True
    assert energy_boundary_ok(3.0, 2.0, kappa=1.0) is False
    assert energy_boundary_ok(3.0, 2.0, kappa=2.0) is True
    with pytest.raises(TrajectoryInvariantError, match="negative_energy"):
        energy_boundary_ok(-0.1, 1.0)


def test_assess_trajectory_replay_bound():
    path = [make_rotor_from_angle(0.05 * i) for i in range(1, 4)]
    a = assess_trajectory(
        path, E_exertion=0.5, E_sensory=1.0, eps_trajectory=1.0, kappa=1.0
    )
    assert a.energy_ok is True
    assert a.n_steps == 3
    assert a.divergence >= 0.0
    # Tight eps → may fail replay bound on moving path
    tight = assess_trajectory(
        path, E_exertion=0.5, E_sensory=1.0, eps_trajectory=1e-30, kappa=1.0
    )
    assert tight.within_replay_bound is False
