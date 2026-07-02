"""ADR-0020 parity surface — Rust-exposed CGA helpers match Python exactly."""

from __future__ import annotations

import numpy as np
import pytest

from algebra.cga import embed_point as py_embed_point
from algebra.cga import is_null as py_is_null
from algebra.cga import null_project as py_null_project

try:
    import core_rs

    _RUST_AVAILABLE = True
except ImportError:
    _RUST_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not _RUST_AVAILABLE, reason="core_rs extension not built"
)


def _assert_f32_bit_identity(left: np.ndarray, right: np.ndarray) -> None:
    left_f32 = np.asarray(left, dtype=np.float32)
    right_f32 = np.asarray(right, dtype=np.float32)
    assert left_f32.shape == right_f32.shape
    assert left_f32.tobytes().hex() == right_f32.tobytes().hex()


@pytest.mark.parametrize(
    "point",
    (
        np.array([0.0, 0.0, 0.0], dtype=np.float32),
        np.array([1.0, 2.0, 3.0], dtype=np.float32),
        np.array([-4.5, 0.25, 8.0], dtype=np.float32),
    ),
)
def test_embed_point_matches_python_bit_for_bit(point: np.ndarray) -> None:
    py = py_embed_point(point)
    rs = np.asarray(core_rs.embed_point(point), dtype=np.float32)
    _assert_f32_bit_identity(py, rs)


@pytest.mark.parametrize("seed", (3, 7, 11))
def test_null_project_matches_python_bit_for_bit(seed: int) -> None:
    rng = np.random.default_rng(seed)
    drifted = py_embed_point(rng.standard_normal(3).astype(np.float32)).astype(np.float32)
    drifted[0] += np.float32(0.125)
    drifted[7] -= np.float32(0.5)

    py = py_null_project(drifted)
    rs = np.asarray(core_rs.null_project(drifted), dtype=np.float32)
    _assert_f32_bit_identity(py, rs)


@pytest.mark.parametrize("seed", (5, 9, 13))
def test_is_null_matches_python(seed: int) -> None:
    rng = np.random.default_rng(seed)
    point = py_embed_point(rng.standard_normal(3).astype(np.float32)).astype(np.float32)
    assert py_is_null(point) is bool(core_rs.is_null(point, np.float32(1e-6)))
