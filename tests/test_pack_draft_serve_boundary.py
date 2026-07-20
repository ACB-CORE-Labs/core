"""Architecture pin: draft language-pack trees are not serve import authority.

ADR-0253 / Master Blueprint Stage 1 dual-pack boundary:

* Runtime language packs load from ``packs/data/<pack_id>/`` via
  ``packs.compiler.load_pack``.
* Source trees ``packs/he``, ``packs/grc`` (and peers) are draft material;
  serve entrypoints must not import them as Python packages.

This is a static + process probe — not a substitute for compile-time validation.
"""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]

# Draft/source language trees — not compiled runtime authority.
_DRAFT_PACK_MODULES = frozenset(
    {
        "packs.he",
        "packs.grc",
        "packs.en",
        "packs.el",
    }
)

# Serve-adjacent entry modules that must not import draft pack packages.
_SERVE_ENTRY_FILES = (
    _ROOT / "chat" / "runtime.py",
    _ROOT / "core" / "cognition" / "pipeline.py",
    _ROOT / "core" / "cli.py",
)


def _module_imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                found.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.add(node.module)
    return found


def test_serve_entry_files_do_not_import_draft_language_pack_packages():
    offenders: list[str] = []
    for path in _SERVE_ENTRY_FILES:
        assert path.is_file(), f"missing serve entry {path}"
        imports = _module_imports(path)
        for draft in _DRAFT_PACK_MODULES:
            if draft in imports or any(
                imp == draft or imp.startswith(draft + ".") for imp in imports
            ):
                offenders.append(f"{path.relative_to(_ROOT)} imports {draft}")
    assert not offenders, "draft pack imports on serve entries:\n" + "\n".join(offenders)


def test_compiler_load_pack_resolves_under_packs_data_only():
    """``_load_pack_cached`` must root pack_dir at packs/data/<id>."""
    compiler_path = _ROOT / "packs" / "compiler.py"
    src = compiler_path.read_text(encoding="utf-8")
    assert 'Path(__file__).parent / "data"' in src
    assert "def load_pack(" in src
    # No alternate root that points at packs/he or packs/grc as compiled home.
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            # Allow incidental strings in comments/docs only via absence of
            # path construction to /he/ or /grc/ as pack_dir — checked below.
            pass
    # Explicit: load path construction uses data/, not he/ or grc/.
    assert '/ "he"' not in src and "/ 'he'" not in src
    assert '/ "grc"' not in src and "/ 'grc'" not in src


def test_import_chat_runtime_does_not_load_draft_he_grc_modules():
    """Process probe: serve import must not pull packs.he / packs.grc into sys.modules."""
    banned = sorted(_DRAFT_PACK_MODULES)
    probe = (
        "import importlib, sys, json;"
        "importlib.import_module('chat.runtime');"
        f"banned={banned!r};"
        "leaked=sorted(m for m in sys.modules for b in banned "
        "if m==b or m.startswith(b+'.'));"
        "print(json.dumps(leaked))"
    )
    result = subprocess.run(
        [sys.executable, "-c", probe],
        cwd=str(_ROOT),
        capture_output=True,
        text=True,
        env={"PYTHONPATH": str(_ROOT), "PATH": ""},
        check=False,
    )
    assert result.returncode == 0, f"probe failed: {result.stderr[-2000:]}"
    import json as _json

    leaked = _json.loads(result.stdout.strip().splitlines()[-1])
    assert leaked == [], f"serve process loaded draft pack modules: {leaked}"


def test_mapping_document_exists_and_forbids_overwrite_policy():
    mapping = _ROOT / "docs" / "adr" / "MASTER-BLUEPRINT-2026-07-20-ADR-MAPPING.md"
    assert mapping.is_file()
    text = mapping.read_text(encoding="utf-8")
    assert "Do **not** overwrite" in text or "Do not overwrite" in text
    assert "ADR-0246" in text and "Induced Identity Action" in text
    assert "packs/data" in text
