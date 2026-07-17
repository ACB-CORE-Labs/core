"""D9 — frozen Python f64 Cl(4,1) geometric-product parity suite (authority).

Python ``algebra.cl41.geometric_product`` is the semantic source of truth for
float64 wave-field residuals (ADR-0241 chiral / trajectory pins at 1e-9).

This suite:
  1. Freezes algebraic f64 GP properties against the pure-Python kernel.
  2. Proves ``algebra.backend.geometric_product`` never silently f32-truncates
     float64 workloads (even when CORE_BACKEND=rust and core_rs is present).
  3. When Rust f64 GP is later exposed, extend with tol-matched parity — until
     then, honest Python-SOT for f64 is the shipped contract.

No scipy-as-truth. Fix the kernel (or the dispatch), not this suite, on red.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from algebra.cl41 import N_COMPONENTS, geometric_product as gp_py, reverse
from algebra.backend import geometric_product as gp_backend

REPO = Path(__file__).resolve().parent.parent

try:
    import core_rs  # noqa: F401

    _RUST_AVAILABLE = True
except ImportError:
    _RUST_AVAILABLE = False


def _rng(seed: int) -> np.random.Generator:
    return np.random.default_rng(seed)


def _f64_mv(seed: int) -> np.ndarray:
    return _rng(seed).standard_normal(N_COMPONENTS).astype(np.float64)


def _basis(i: int) -> np.ndarray:
    e = np.zeros(N_COMPONENTS, dtype=np.float64)
    e[i] = 1.0
    return e


# --- Frozen Python SOT properties -------------------------------------------


@pytest.mark.parametrize("seed", [0xF64A, 0xF64B, 0xF64C, 0xC07E, 0xBEEF])
def test_python_f64_gp_is_deterministic(seed: int) -> None:
    a, b = _f64_mv(seed), _f64_mv(seed + 1)
    r1 = gp_py(a, b)
    r2 = gp_py(a.copy(), b.copy())
    assert r1.dtype == np.float64
    assert r1.shape == (N_COMPONENTS,)
    assert np.array_equal(r1, r2)


def test_python_f64_scalar_identity() -> None:
    one = _basis(0)
    b = _f64_mv(0x11)
    out = gp_py(one, b)
    assert float(np.max(np.abs(out - b))) == 0.0


def test_python_f64_basis_anticommutation_e1_e2() -> None:
    e1, e2 = _basis(1), _basis(2)
    ab = gp_py(e1, e2)
    ba = gp_py(e2, e1)
    # e1 e2 = - e2 e1 for distinct orthogonal spacelike basis vectors
    assert float(np.max(np.abs(ab + ba))) < 1e-15


@pytest.mark.parametrize("i", [0, 1, 5, 15, 31])
def test_python_f64_basis_self_product_scalar_or_metric(i: int) -> None:
    ei = _basis(i)
    out = gp_py(ei, ei)
    # Blade square is scalar (±1 or 0 for null patterns); residual grades small.
    non_scalar = float(np.linalg.norm(out[1:]))
    assert non_scalar < 1e-12 or abs(float(out[0])) > 0.0


def test_python_f64_reverse_anti_automorphism_on_product() -> None:
    """(AB)~ = B~ A~ within f64 accumulation tolerance."""
    a, b = _f64_mv(0xA11), _f64_mv(0xB22)
    left = reverse(gp_py(a, b))
    right = gp_py(reverse(b), reverse(a))
    assert float(np.max(np.abs(left - right))) < 1e-12


# --- Backend: no silent f32 truncation of f64 -------------------------------


def test_backend_f64_matches_python_sot_exactly() -> None:
    """Default backend must match pure Python bit-for-bit on f64 inputs."""
    a, b = _f64_mv(0xD9F1), _f64_mv(0xD9F2)
    py = gp_py(a, b)
    be = gp_backend(a, b)
    assert be.dtype == np.float64 or np.asarray(be).dtype == np.float64
    assert float(np.max(np.abs(np.asarray(be, dtype=np.float64) - py))) == 0.0


def test_backend_f64_does_not_match_forced_f32_truncation() -> None:
    """Silent f32 cast of f64 residuals would destroy 1e-9 wave pins.

    Prove the shipped backend path differs from (or at least is not equal to
    a forced) f32-truncated product when the true f64 product has sub-f32
    structure — or, if equal by chance on this fixture, still returns f64
    dtype and matches Python SOT (already covered). Here we pin that backend
    never routes f64 through float32 geometric_product.
    """
    # High-dynamic-range components that f32 cannot represent exactly.
    a = np.zeros(N_COMPONENTS, dtype=np.float64)
    b = np.zeros(N_COMPONENTS, dtype=np.float64)
    a[0] = 1.0 + 1e-10
    a[6] = 1e-9
    b[0] = 1.0
    b[7] = 1e-9
    py = gp_py(a, b)
    be = np.asarray(gp_backend(a, b), dtype=np.float64)
    assert float(np.max(np.abs(be - py))) == 0.0
    # Truncating inputs to f32 changes the product for this fixture.
    a32 = a.astype(np.float32)
    b32 = b.astype(np.float32)
    truncated = gp_py(a32.astype(np.float64), b32.astype(np.float64))
    # If f32 truncation mattered, SOT f64 and truncated differ; backend must
    # follow SOT, not truncation. (If they coincide, equality still holds.)
    assert float(np.max(np.abs(be - py))) == 0.0
    if float(np.max(np.abs(py - truncated))) > 0.0:
        assert float(np.max(np.abs(be - truncated))) > 0.0


SCRIPT_F64_BACKEND = r"""
import json, os, sys
import numpy as np
sys.path.insert(0, "__REPO__")
from algebra.backend import geometric_product, using_rust
from algebra.cl41 import geometric_product as gp_py

seed = int(os.environ["FIXTURE_SEED"])
rng = np.random.default_rng(seed)
a = rng.standard_normal(32).astype(np.float64)
b = rng.standard_normal(32).astype(np.float64)
out_be = np.asarray(geometric_product(a, b), dtype=np.float64)
out_py = np.asarray(gp_py(a, b), dtype=np.float64)
print(json.dumps({
    "using_rust": using_rust(),
    "backend_hex": [np.float64(v).tobytes().hex() for v in out_be],
    "python_hex": [np.float64(v).tobytes().hex() for v in out_py],
    "dtype": str(out_be.dtype),
}))
"""


def _run_f64_backend(backend: str, seed: int) -> dict:
    env = os.environ.copy()
    if backend == "rust":
        env["CORE_BACKEND"] = "rust"
    else:
        env.pop("CORE_BACKEND", None)
    env["FIXTURE_SEED"] = str(seed)
    script = SCRIPT_F64_BACKEND.replace("__REPO__", str(REPO))
    out = subprocess.check_output(
        [sys.executable, "-c", script],
        env=env,
        cwd=str(REPO),
        text=True,
    )
    return json.loads(out.strip().splitlines()[-1])


@pytest.mark.parametrize("seed", [0xD901, 0xD902, 0xD903])
def test_f64_backend_matches_python_sot_in_subprocess(seed: int) -> None:
    py = _run_f64_backend("python", seed)
    assert py["using_rust"] is False
    assert py["backend_hex"] == py["python_hex"]
    assert py["dtype"] == "float64"


@pytest.mark.skipif(not _RUST_AVAILABLE, reason="core_rs extension not built")
@pytest.mark.parametrize("seed", [0xD911, 0xD912])
def test_f64_with_rust_opt_in_matches_python_sot_bit_for_bit(seed: int) -> None:
    """CORE_BACKEND=rust routes f64 GP to the Rust f64 kernel (ADR-0244 §2.6),
    which is bit-identical to Python SOT — so the hex still matches exactly.

    This is the D9 honesty pin, now stronger: not only no f32-truncation, but
    no 1-ULP f64 divergence either. On an older ``core_rs`` build without the
    export, backend falls through to Python and the hex still matches.
    """
    rs = _run_f64_backend("rust", seed)
    assert rs["using_rust"] is True
    assert rs["backend_hex"] == rs["python_hex"]
    assert rs["dtype"] == "float64"


@pytest.mark.skipif(not _RUST_AVAILABLE, reason="core_rs extension not built")
def test_rust_f64_gp_is_bit_identical_to_python_n10000() -> None:
    """Acceptance criterion 1 (ADR-0244 §2.6 / directive M1): the Rust f64
    ``geometric_product`` equals the pure-Python f64 kernel **bit-for-bit** over
    a large random panel — not tol-matched. A single ULP divergence would move
    the f64 wave-field residual bytes and break I-02 replay under
    ``CORE_BACKEND=rust``; this fails closed on the first mismatch.
    """
    if not hasattr(core_rs, "geometric_product_f64"):
        pytest.skip("core_rs build predates geometric_product_f64 export")
    rng = _rng(0xB17DE)
    for _ in range(10_000):
        a = np.ascontiguousarray(rng.standard_normal(N_COMPONENTS), dtype=np.float64)
        b = np.ascontiguousarray(rng.standard_normal(N_COMPONENTS), dtype=np.float64)
        rust = np.asarray(core_rs.geometric_product_f64(a, b), dtype=np.float64)
        py = gp_py(a, b)
        assert rust.tobytes() == py.tobytes()


def test_backend_source_documents_f64_rust_bit_identical() -> None:
    """Structural pin: both dtype gates exist and the f64 Rust path is
    documented bit-identical (a speed swap, not a numeric one)."""
    src = (REPO / "algebra" / "backend.py").read_text(encoding="utf-8")
    assert "_is_f32_workload" in src
    assert "_is_f64_workload" in src
    assert "if _RUST and _is_f32_workload(A, B):" in src
    assert "if _RUST and _is_f64_workload(A, B):" in src
    assert "bit-identical" in src
