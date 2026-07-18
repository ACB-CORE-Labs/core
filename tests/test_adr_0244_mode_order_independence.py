"""ADR-0244 §2.9 — standing-wave-mode registration is insertion-order-independent.

The §2.9 concern is a low-discrepancy *mode-centroid allocator* so the standing-
wave spectrum does not depend on the order modes were registered. Two facts make
that hold **by construction**, so the honest deliverable is to *prove* it rather
than bolt an allocator onto a path that does not need one:

1. **Recall is a metric-exact subspace projection.** `WaveManifold` recall
   (`compute_spectral_leakage`) projects the incoming ψ onto `span(modes)` via a
   Gram least-squares solve (`_metric_project`). Projection onto a subspace span
   is mathematically invariant to the order of the spanning set — permuting the
   modes permutes G's rows/columns identically and leaves the projection (and
   thus the residual / surprise) unchanged. Verified here to machine epsilon.
2. **The allocator is reconstructible from ordinals.** `atlas_packing.golden_
   angle_pack(n, α)` places mode k at a deterministic golden-angle coordinate
   derived from k alone (`ALLOCATOR_VERSION` + ordinal), so its layout is
   order-independent by construction — there is no opaque mutable coordinate
   table to drift.

Wiring the allocator into the durable content-seal path (`holographic_vault`)
would be a category mismatch: that path seals *content* versors at their own ψ,
not allocator positions. §2.9 is satisfied by (1)+(2), pinned below.
"""

from __future__ import annotations

import itertools

import numpy as np

from algebra.cl41 import N_COMPONENTS
from core.physics.atlas_packing import (
    allocator_layout_descriptor,
    golden_angle_pack,
)
from core.physics.wave_manifold import WaveManifold

_TOL = 1e-12  # observed order-to-order drift is ~1e-15 (float64 round-off)


def _recall(perm, modes, probe):
    manifold = WaveManifold()
    for i in perm:
        manifold.register_resonant_mode(modes[i])
    residual, energy = manifold.compute_spectral_leakage(probe, manifold.resonant_modes)
    return energy, residual


def test_allocator_is_deterministic_and_ordinal_reconstructible():
    a = golden_angle_pack(6, 0.6)
    b = golden_angle_pack(6, 0.6)
    assert all(np.array_equal(x, y) for x, y in zip(a, b))
    # a prefix of a larger pack is the same modes (layout depends on ordinal only)
    bigger = golden_angle_pack(9, 0.6)
    assert all(np.array_equal(x, y) for x, y in zip(a, bigger[:6]))
    # descriptor is content-free reconstruction metadata (no coordinate leak)
    desc = allocator_layout_descriptor(6, 0.6)
    assert desc["allocator_version"] == "golden_angle_v1"
    assert "alpha" in desc and "min_d" in desc


def test_recall_projection_is_insertion_order_independent():
    modes = golden_angle_pack(5, 0.6)
    # probe fully inside span(modes) → residual ≈ 0, still order-invariant
    in_span = np.asarray(
        modes[0] * 0.4 + modes[2] * 0.5 + modes[4] * 0.3, dtype=np.float64
    )
    base_e, base_r = _recall(range(5), modes, in_span)
    perms = list(itertools.islice(itertools.permutations(range(5)), 0, 120, 13))
    for perm in perms:
        e, r = _recall(list(perm), modes, in_span)
        assert abs(e - base_e) < _TOL
        assert float(np.max(np.abs(r - base_r))) < _TOL


def test_order_independence_holds_for_nontrivial_residual():
    modes = golden_angle_pack(5, 0.6)
    alien = np.zeros(N_COMPONENTS, dtype=np.float64)
    alien[3] = 1.0
    # a genuine out-of-span component → nonzero residual energy
    probe = np.asarray(modes[1] * 0.6 + modes[3] * 0.4 + alien * 0.7, dtype=np.float64)
    base_e, base_r = _recall(range(5), modes, probe)
    assert base_e > 0.1  # the residual is meaningful, not numerical dust
    for perm in itertools.islice(itertools.permutations(range(5)), 0, 120, 11):
        e, r = _recall(list(perm), modes, probe)
        assert abs(e - base_e) < _TOL
        assert float(np.max(np.abs(r - base_r))) < _TOL
