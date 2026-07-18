"""ADR-0245 §3 — mechanical-sympathy + semantic-rigor acceptance gate.

The §3 gate has four assertions. Two were already covered before D4:

  * **Parity** (Rust GP bit-identical to Python) — `test_geometric_product_f64_parity.py`
    (f64, N=10,000 bit-identical) + `test_geometric_product_rust_parity.py` (f32,
    component-exact).
  * **0 LAPACK on repeat** (`_cached_eigh` memoization) —
    `test_adr_0244_mechanical_sympathy.py`.

This file closes the two that were missing (D4 Phase 5):

  * **≥10× f32 speedup** of the Rust `geometric_product` fast path over the pure
    Python kernel (Rust-guarded: skips with a reason where `core_rs` is unbuilt).
  * **`_content_id` collision-resistance** — full 256-bit digest, type-faithful,
    fail-closed on non-serializable input (no `default=str` collapse).
"""

from __future__ import annotations

import importlib.util
import time

import numpy as np
import pytest

from core.physics.cognitive_lifecycle import _content_id, _psi_digest

_HAS_RUST = importlib.util.find_spec("core_rs") is not None


# --- ≥10× f32 speedup (Rust-guarded) --------------------------------------


@pytest.mark.skipif(not _HAS_RUST, reason="core_rs not built (Rust f32 kernel unavailable)")
def test_rust_f32_geometric_product_is_at_least_10x():
    import core_rs

    from algebra.cl41 import geometric_product as py_gp

    rng = np.random.default_rng(0)
    A = rng.standard_normal(32).astype(np.float32)
    B = rng.standard_normal(32).astype(np.float32)

    # parity sanity: the speedup must not come from skipping work.
    r_rust = np.asarray(core_rs.geometric_product(A, B), dtype=np.float64)
    r_py = np.asarray(py_gp(A, B), dtype=np.float64)
    np.testing.assert_allclose(r_rust, r_py, atol=1e-5)

    for _ in range(200):  # warmup (JIT-free, but stabilizes caches/branch pred.)
        core_rs.geometric_product(A, B)
        py_gp(A, B)

    def _best(fn, n):
        best = float("inf")
        for _ in range(3):
            t0 = time.perf_counter()
            for _ in range(n):
                fn(A, B)
            best = min(best, time.perf_counter() - t0)
        return best

    n = 200
    t_rust = _best(core_rs.geometric_product, n)
    t_py = _best(py_gp, n)
    speedup = t_py / t_rust
    # Real measured speedup on Apple M-series is ~400-500×; assert a conservative
    # ≥10× so the gate is robust to CI timing noise while still failing loudly if
    # the fast path regresses to the Python order of magnitude.
    assert speedup >= 10.0, f"Rust f32 GP only {speedup:.1f}× faster than Python (< 10×)"


# --- _content_id collision-resistance -------------------------------------


def test_content_id_is_full_256_bit_no_truncation():
    cid = _content_id({"kind": "x", "n": 1})
    assert len(cid) == 64  # 256-bit, not a 16-hex (2^32) truncation
    assert all(c in "0123456789abcdef" for c in cid)


def test_content_id_is_type_and_structure_faithful():
    # distinct payloads that a weak/str-collapsed digest could conflate:
    assert _content_id({"a": 1}) != _content_id({"a": "1"})       # int vs str
    assert _content_id({"a": True}) != _content_id({"a": 1})      # bool vs int
    assert _content_id({"a": {"b": 1}}) != _content_id({"a": {"b": 2}})  # nested
    # key order must NOT matter (canonical sort_keys), but content must:
    assert _content_id({"a": 1, "b": 2}) == _content_id({"b": 2, "a": 1})


def test_content_id_fails_closed_on_non_serializable():
    # No default=str: a non-serializable payload raises instead of silently
    # collapsing distinct objects onto one id (ADR-0245 §2.3 semantic rigor).
    with pytest.raises(TypeError):
        _content_id({"x": object()})


def test_psi_digest_is_full_and_sensitive():
    p1 = np.zeros(32, dtype=np.float64)
    p1[1] = 1.0
    p2 = np.zeros(32, dtype=np.float64)
    p2[1] = 1.0 + 1e-12  # a sub-epsilon perturbation must still change the id
    assert len(_psi_digest(p1)) == 64
    assert _psi_digest(p1) != _psi_digest(p2)
    assert _psi_digest(p1) == _psi_digest(p1.copy())  # deterministic


# --- coverage manifest (legibility of the 4-assertion gate) ---------------


def test_acceptance_gate_coverage_manifest():
    """The four §3 criteria and where each is proven — a failing import here
    means an acceptance leg lost its home."""
    import pathlib

    tests_dir = pathlib.Path(__file__).parent
    coverage = {
        "parity_f64": tests_dir / "test_geometric_product_f64_parity.py",
        "parity_f32": tests_dir / "test_geometric_product_rust_parity.py",
        "zero_lapack_on_repeat": tests_dir / "test_adr_0244_mechanical_sympathy.py",
        "f32_speedup_ge_10x": pathlib.Path(__file__),
        "content_id_collision_resistance": pathlib.Path(__file__),
    }
    for name, path in coverage.items():
        assert path.exists(), f"acceptance leg {name!r} missing its test file {path}"
