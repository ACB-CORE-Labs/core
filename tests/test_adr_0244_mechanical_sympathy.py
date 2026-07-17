"""ADR-0244 §2.8 mechanical-sympathy pins (cohesion directive Mandate 2).

The eigendecomposition inside ``relax_to_ground`` for a non-diagonal, frozen,
content-addressed ``ProblemHamiltonian`` must be memoized — a fresh LAPACK
``eigh`` on an identical matrix is wasted AMX compute. The cache must return
bit-identical, read-only ``(evals, evecs)`` so a hit can never be mutated into a
different result, and a cached decomposition must equal a fresh one.

(Mandate 1 — the Rust f64 ``geometric_product`` fast-path — is pinned by the
bit-identical parity suite in ``tests/test_geometric_product_f64_parity.py``.)
"""

from __future__ import annotations

import numpy as np

from algebra.rotor import make_rotor_from_angle
from core.physics.cognitive_lifecycle import (
    _cached_eigh,
    compile_quadratic_well,
    relax_to_ground,
)


def _dense_well():
    # c·(I − TTᵀ) is non-diagonal → exercises the eigh (not the diagonal) branch.
    target = np.ascontiguousarray(make_rotor_from_angle(0.9, 7), dtype=np.float64)
    well = compile_quadratic_well(target, curvature=1.0)
    assert well.is_diagonal is False
    return well


def test_cached_eigh_matches_fresh_eigh() -> None:
    well = _dense_well()
    evals, evecs = _cached_eigh(well.hamiltonian_id, well.matrix.tobytes())
    fresh_evals, fresh_evecs = np.linalg.eigh(well.matrix)
    # Same matrix bytes → same LAPACK call → bit-identical.
    assert np.array_equal(evals, fresh_evals)
    assert np.array_equal(evecs, fresh_evecs)


def test_cached_eigh_returns_readonly_arrays() -> None:
    well = _dense_well()
    evals, evecs = _cached_eigh(well.hamiltonian_id, well.matrix.tobytes())
    assert evals.flags.writeable is False
    assert evecs.flags.writeable is False


def test_cached_eigh_hit_returns_identical_objects() -> None:
    # Distinct target → distinct hamiltonian_id/bytes → clean miss then hit.
    target = np.ascontiguousarray(make_rotor_from_angle(1.27, 8), dtype=np.float64)
    well = compile_quadratic_well(target, curvature=1.3)
    key = (well.hamiltonian_id, well.matrix.tobytes())
    a_evals, a_evecs = _cached_eigh(*key)
    b_evals, b_evecs = _cached_eigh(*key)
    # A cache hit hands back the very same frozen objects (no recompute).
    assert a_evals is b_evals
    assert a_evecs is b_evecs


def test_relaxation_is_deterministic_through_the_cache() -> None:
    well = _dense_well()
    start = np.ascontiguousarray(make_rotor_from_angle(0.2, 6), dtype=np.float64)
    start = start / float(np.linalg.norm(start))
    r1 = relax_to_ground(start, well)
    r2 = relax_to_ground(start, well)
    assert r1.certificate.certificate_id == r2.certificate.certificate_id
    assert r1.certificate.converged is True
    assert np.array_equal(r1.psi_steady, r2.psi_steady)
