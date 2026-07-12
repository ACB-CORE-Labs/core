"""ADR-0240 — Biography Holonomy Blade reconstruction + order sensitivity."""

from __future__ import annotations

import numpy as np
import pytest

from algebra.rotor import make_rotor_from_angle
from algebra.versor import versor_condition
from core.physics.biography import (
    biography_telemetry,
    integrate_biography,
    reconstruct_biography,
)


def test_integrate_closes():
    traj = [make_rotor_from_angle(0.1 * i, bivector_idx=6) for i in range(1, 6)]
    blade = integrate_biography(traj)
    assert versor_condition(blade.blade) < 1e-6
    assert blade.n_steps == 5
    assert len(blade.trajectory_hash) == 64


def test_reconstruct_equals_integrate():
    traj = [make_rotor_from_angle(0.2 * i) for i in range(1, 4)]
    a = integrate_biography(traj)
    b = reconstruct_biography(traj)
    assert a.trajectory_hash == b.trajectory_hash
    assert np.allclose(a.blade, b.blade)


def test_order_sensitivity():
    a = make_rotor_from_angle(0.3)
    b = make_rotor_from_angle(0.9)
    c = make_rotor_from_angle(1.4)
    h1 = integrate_biography([a, b, c])
    h2 = integrate_biography([c, b, a])
    assert h1.trajectory_hash != h2.trajectory_hash


def test_empty_refused():
    with pytest.raises(ValueError):
        integrate_biography([])


def test_telemetry_schema():
    traj = [make_rotor_from_angle(0.5)]
    blade = integrate_biography(traj)
    tel = biography_telemetry(blade)
    assert tel["schema_version"] == "biography_holonomy_v1"
    assert tel["n_steps"] == 1
