"""Exact fractional powers of GENERAL (non-simple) rotors in Cl(4,1).

`rotor_power` previously returned the identity for any non-simple rotor — an
approximation where exactness was available (Pillar II), which silently
collapsed geodesic interpolation (slerp, supervised blend) to a no-op. It now
uses the invariant (bivector) decomposition: a general rotor factors into two
commuting simple rotors, R = R1 R2, so R^a = R1^a R2^a exactly, with a closed
form for the isoclinic case. First-principles, no library (Pillar III).

These tests pin the group-theoretic identities to machine precision on rotors
that exercise every plane type (Euclidean rotations, e5 boosts, mixed, and the
isoclinic degenerate case) — the regimes the pre-existing `test_rotor_power.py`
(simple rotors only) never covered.
"""

from __future__ import annotations

import numpy as np
import pytest

from algebra.cl41 import N_COMPONENTS, geometric_product, grade_project
from algebra.rotor import make_rotor_from_angle, rotor_power
from algebra.versor import versor_condition

_ROT = 1e-8          # power-identity tolerance
_CLOSE = 1e-6        # the versor_condition invariant


def _identity() -> np.ndarray:
    v = np.zeros(N_COMPONENTS, dtype=np.float64)
    v[0] = 1.0
    return v


def _rotor(seed: int, nplanes: int, lo: float = -1.2, hi: float = 1.2) -> np.ndarray:
    """A reproducible composed rotor over `nplanes` distinct planes (grades e1..e5)."""
    rng = np.random.default_rng(seed)
    v = _identity()
    planes = rng.choice(range(6, 16), size=nplanes, replace=False)
    for idx in planes:
        v = geometric_product(v, make_rotor_from_angle(float(rng.uniform(lo, hi)), bivector_idx=int(idx)))
    return np.asarray(v, dtype=np.float64)


def _is_non_simple(R: np.ndarray) -> bool:
    return float(np.linalg.norm(grade_project(R, 4))) > 1e-9


# A spread of seeds; most compose into non-simple rotors.
_SEEDS = list(range(40))


@pytest.mark.parametrize("seed", _SEEDS)
def test_power_one_reconstructs_rotor(seed):
    R = _rotor(seed, nplanes=3)
    assert np.linalg.norm(rotor_power(R, 1.0) - R) < _ROT


@pytest.mark.parametrize("seed", _SEEDS)
def test_half_power_squares_to_rotor(seed):
    R = _rotor(seed, nplanes=3)
    half = rotor_power(R, 0.5)
    assert np.linalg.norm(geometric_product(half, half) - R) < _ROT


@pytest.mark.parametrize("seed", _SEEDS)
def test_group_law_additive_exponents(seed):
    R = _rotor(seed, nplanes=4)
    lhs = geometric_product(rotor_power(R, 0.3), rotor_power(R, 0.45))
    rhs = rotor_power(R, 0.75)
    assert np.linalg.norm(lhs - rhs) < _ROT


@pytest.mark.parametrize("seed", _SEEDS)
def test_zero_power_is_identity(seed):
    R = _rotor(seed, nplanes=3)
    assert np.linalg.norm(rotor_power(R, 0.0) - _identity()) < 1e-12


@pytest.mark.parametrize("seed", _SEEDS)
@pytest.mark.parametrize("alpha", [0.0, 0.25, 0.5, 0.75, 1.0, 1.5])
def test_closure_preserved(seed, alpha):
    R = _rotor(seed, nplanes=3)
    assert versor_condition(rotor_power(R, alpha)) < _CLOSE


def test_covers_non_simple_rotors():
    """Guard: the seed pool actually exercises the non-simple path (else the suite
    would be vacuous, à la the fidelity finding it fixes)."""
    n = sum(_is_non_simple(_rotor(s, 3)) for s in _SEEDS)
    assert n >= len(_SEEDS) // 2


@pytest.mark.parametrize("seed", _SEEDS[:20])
def test_non_simple_power_is_not_identity(seed):
    """The exact regression for the bug: a non-simple rotor's interior power must
    MOVE off the identity (the old code returned identity → no-op geodesic)."""
    R = _rotor(seed, nplanes=3)
    if not _is_non_simple(R):
        pytest.skip("simple rotor")
    mid = rotor_power(R, 0.5)
    assert np.linalg.norm(mid - _identity()) > 1e-3


def test_isoclinic_degenerate_is_exact():
    """Coincident invariant planes (same-angle disjoint Euclidean rotations) take the
    closed-form isoclinic branch and reconstruct exactly."""
    for (p, q, th) in [(6, 13, 0.7), (6, 13, 1.2), (7, 15, 0.4)]:
        R = geometric_product(
            make_rotor_from_angle(th, bivector_idx=p),
            make_rotor_from_angle(th, bivector_idx=q),
        )
        assert _is_non_simple(R)
        h = rotor_power(R, 0.5)
        assert np.linalg.norm(geometric_product(h, h) - R) < 1e-10
        assert np.linalg.norm(rotor_power(R, 1.0) - R) < 1e-10


@pytest.mark.parametrize("seed", _SEEDS[:15])
def test_determinism_replay(seed):
    """Same input → byte-identical output (replay determinism, Pillar II)."""
    R = _rotor(seed, nplanes=3)
    a = rotor_power(R, 0.37)
    b = rotor_power(R, 0.37)
    assert np.array_equal(a, b)


def test_backward_compat_simple_rotor_matches_analytic():
    """On a SIMPLE rotor, R^a is the analytic half-angle interpolation, unchanged."""
    theta = 0.9
    R = make_rotor_from_angle(theta, bivector_idx=6)
    for alpha in (0.0, 0.25, 0.5, 0.75, 1.0):
        got = rotor_power(R, alpha)
        expect = make_rotor_from_angle(alpha * theta, bivector_idx=6)
        assert np.linalg.norm(got - expect) < 1e-12
