from __future__ import annotations

import re
from pathlib import Path

import conftest


ROOT = Path(__file__).resolve().parents[1]


def test_top_level_contemplation_is_artifact_namespace_only() -> None:
    artifact_root = ROOT / "contemplation"
    code_root = ROOT / "core" / "contemplation"

    assert (artifact_root / "README.md").is_file()
    assert (artifact_root / "runs").is_dir()
    assert not (artifact_root / "__init__.py").exists()
    assert not list(artifact_root.rglob("*.py"))
    assert (code_root / "__init__.py").is_file()


def test_quarantine_doc_matches_registry_count() -> None:
    doc = (ROOT / "docs" / "test-debt-quarantine.md").read_text(encoding="utf-8")
    match = re.search(r"^Current quarantined tests: (\d+)\.$", doc, re.MULTILINE)

    assert match is not None
    assert int(match.group(1)) == len(conftest.QUARANTINE)


def test_provider_files_delegate_to_agents() -> None:
    for name in ("CLAUDE.md", "GEMINI.md"):
        text = (ROOT / name).read_text(encoding="utf-8")

        assert len(text.encode("utf-8")) <= 600
        assert "`AGENTS.md` is the canonical governance file" in text
        assert "Do not place architecture, invariants, memory rules" in text


def test_notes_are_non_executable_artifacts() -> None:
    notes_root = ROOT / "notes"

    assert (notes_root / "README.md").is_file()
    assert not list(notes_root.rglob("*.py"))


def test_intentional_topology_splits_have_local_readmes() -> None:
    required = (
        "calibration",
        "contemplation",
        "core/demos",
        "core_ingest",
        "demos",
        "ingest",
        "packs",
        "notes",
        "packs",
        "workbench",
        "workbench-ui",
        "workbench_data",
    )

    missing = [path for path in required if not (ROOT / path / "README.md").is_file()]
    assert missing == []
