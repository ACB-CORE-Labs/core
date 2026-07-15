"""P11a — physics hot paths must dispatch Cl(4,1) ops via algebra.backend.

Prevents silent drift back to pure-Python-only imports for geometric_product /
versor_apply / cga_inner / versor_condition in wave-field and related modules.
Python remains default when CORE_BACKEND is unset; Rust accelerates when
CORE_BACKEND=rust and core_rs is built (ADR-0235).
"""

from __future__ import annotations

import ast
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_PHYSICS = _ROOT / "core" / "physics"

# Modules that perform Cl(4,1) multiplies / residuals in the cognitive physics
# layer — must take the load-bearing ops from algebra.backend.
_BACKEND_HOT_MODULES = (
    "wave_manifold.py",
    "goldtether.py",
    "trajectory_invariants.py",
    "dynamic_manifold.py",
    "surprise.py",
    "holographic_vault.py",
    "atlas_packing.py",
    "biography.py",
    "self_authorship.py",
)

# Names that must not be imported from algebra.cl41 / algebra.versor / algebra.cga
# in those modules (use backend instead).
_BANNED_FROM_PURE = frozenset(
    {
        "geometric_product",
        "versor_apply",
        "versor_condition",
        "cga_inner",
    }
)


def _imports_from(module: str, path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == module:
            for alias in node.names:
                names.add(alias.name)
    return names


def test_hot_modules_import_backend_for_algebra_ops():
    for name in _BACKEND_HOT_MODULES:
        path = _PHYSICS / name
        assert path.is_file(), f"missing {path}"
        backend_names = _imports_from("algebra.backend", path)
        # Each file should pull at least one of the dispatch ops.
        assert backend_names & _BANNED_FROM_PURE, (
            f"{name} must import Cl(4,1) hot ops from algebra.backend; "
            f"got backend imports {sorted(backend_names)}"
        )


def test_hot_modules_do_not_import_hot_ops_from_pure_algebra():
    pure_modules = ("algebra.cl41", "algebra.versor", "algebra.cga")
    for name in _BACKEND_HOT_MODULES:
        path = _PHYSICS / name
        for mod in pure_modules:
            pure_names = _imports_from(mod, path)
            offenders = pure_names & _BANNED_FROM_PURE
            assert not offenders, (
                f"{name} imports {sorted(offenders)} from {mod}; "
                "route through algebra.backend for CORE_BACKEND=rust"
            )


def test_wave_manifold_uses_backend_geometric_product_and_versor_apply():
    path = _PHYSICS / "wave_manifold.py"
    backend = _imports_from("algebra.backend", path)
    assert "geometric_product" in backend
    assert "versor_apply" in backend
    assert "versor_condition" in backend
    assert "cga_inner" in backend


def test_backend_using_rust_api_exists():
    from algebra.backend import using_rust

    # Default env: Python path (no silent force of Rust).
    assert using_rust() is False or using_rust() is True  # bool only
    assert isinstance(using_rust(), bool)
