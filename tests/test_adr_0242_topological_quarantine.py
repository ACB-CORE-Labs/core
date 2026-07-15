"""ADR-0242 V5 (D6) — topological_reasoning research quarantine pins.

Authority: docs/adr/ADR-0242-atlas-packing-and-fibonacci.md Vector 5.
Package may exist under algebra/topological_reasoning/ for isolated study.
Production packages must not import it.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]

# Production surfaces that must never import the research quarantine package.
_PRODUCTION_PACKAGES = (
    "chat",
    "core/physics",
    "generate",
    "vault",
    "teaching",
)

_BANNED_MARKERS = (
    "topological_reasoning",
    "algebra.topological_reasoning",
)


def _iter_python_files(package_rel: str) -> list[Path]:
    base = _ROOT / package_rel
    if not base.is_dir():
        return []
    return sorted(p for p in base.rglob("*.py") if p.is_file())


def _import_mentions_topological(tree: ast.AST) -> list[str]:
    """Return import module strings that reference topological_reasoning."""
    hits: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name
                if any(m in name for m in _BANNED_MARKERS):
                    hits.append(name)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if any(m in mod for m in _BANNED_MARKERS):
                hits.append(mod)
            # from algebra import topological_reasoning
            if mod == "algebra" or mod.endswith(".algebra"):
                for alias in node.names:
                    if alias.name == "topological_reasoning" or (
                        alias.name and "topological_reasoning" in alias.name
                    ):
                        hits.append(f"{mod}.{alias.name}")
    return hits


def test_topological_reasoning_package_imports_in_isolation() -> None:
    """Package is importable on its own without production wiring."""
    import algebra.topological_reasoning as tr

    assert hasattr(tr, "FUSION_RULE")
    assert isinstance(tr.FUSION_RULE, str)
    assert tr.FUSION_RULE == "tau_otimes_tau_eq_1_oplus_tau"
    # Research label only — no callable production fusion API required.
    assert "FUSION_RULE" in tr.__all__


def test_algebra_public_import_still_works() -> None:
    """Quarantine package must not break the algebra package surface."""
    import algebra
    from algebra import versor_condition, word_transition_rotor

    assert callable(versor_condition)
    assert callable(word_transition_rotor)
    # Research package is not re-exported on algebra's public surface.
    assert not hasattr(algebra, "topological_reasoning") or "topological_reasoning" not in getattr(
        algebra, "__all__", ()
    )


def test_topological_reasoning_package_directory_may_exist() -> None:
    """Algebraic research quarantine box is allowed to exist on disk."""
    pkg = _ROOT / "algebra" / "topological_reasoning"
    assert pkg.is_dir()
    assert (pkg / "__init__.py").is_file()
    assert (pkg / "README.md").is_file()


@pytest.mark.parametrize("package_rel", _PRODUCTION_PACKAGES)
def test_production_packages_do_not_import_topological_reasoning(
    package_rel: str,
) -> None:
    """Architectural: production trees must not import topological_reasoning."""
    files = _iter_python_files(package_rel)
    assert files, f"expected python sources under {package_rel}"

    violations: list[str] = []
    for path in files:
        # Never scan the quarantine package itself (it lives under algebra/).
        rel = path.relative_to(_ROOT).as_posix()
        if "topological_reasoning" in rel.split("/"):
            continue
        try:
            src = path.read_text(encoding="utf-8")
        except OSError as exc:
            violations.append(f"{rel}: unreadable ({exc})")
            continue
        try:
            tree = ast.parse(src, filename=rel)
        except SyntaxError as exc:
            violations.append(f"{rel}: syntax error ({exc})")
            continue
        for hit in _import_mentions_topological(tree):
            violations.append(f"{rel}: imports {hit}")

    assert not violations, (
        "ADR-0242 V5 quarantine violated — production import(s) of "
        "topological_reasoning:\n" + "\n".join(violations)
    )
