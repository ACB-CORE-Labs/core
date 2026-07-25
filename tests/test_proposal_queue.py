"""tests/test_proposal_queue.py — HITL proposal-queue (Tier S4).

Fully isolated: every test passes its own ``roots``/``log_path`` (or
``tmp_path`` fixtures) rather than touching the real
``teaching/proposals/`` sinks or ``teaching/proposals/review_log.jsonl`` —
that file is real operator data, never a test fixture.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

from core.proposal_review.queue import (
    QueueEntry,
    queue_status,
    record_review,
    reviewed_keys,
    scan_all,
)
from generate.determine.derived_close_proposals import DEFAULT_SINK as DERIVED_CLOSE_SINK


def _write_comprehension_artifact(root: Path, content_hash: str, **overrides: object) -> None:
    root.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": "proposal_only",
        "failure_family": "missing_total_count",
        "problem_text_sha256": "a" * 64,
        "mounted": False,
        "requires_review": True,
        "observed_attempts": [],
        **overrides,
    }
    (root / f"{content_hash}.json").write_text(json.dumps(payload), encoding="utf-8")


def _write_derived_close_artifact(root: Path, content_hash: str, **overrides: object) -> None:
    root.mkdir(parents=True, exist_ok=True)
    payload = {
        "source": "derived_close_fact",
        "predicate": "member",
        "subject": "socrates",
        "object": "mortal",
        "status": "proposal_only",
        "requires_review": True,
        "mounted": False,
        **overrides,
    }
    (root / f"{content_hash}.json").write_text(json.dumps(payload), encoding="utf-8")


def test_derived_close_default_sink_resolves_inside_the_repo() -> None:
    """Pins the off-by-one fix: parents[2], not parents[3] — the sink must
    resolve under <repo>/teaching/proposals/derived_close_facts, not one
    directory above the repository."""
    repo_root = Path(__file__).resolve().parents[1]
    assert DERIVED_CLOSE_SINK == repo_root / "teaching" / "proposals" / "derived_close_facts"
    assert DERIVED_CLOSE_SINK.is_relative_to(repo_root)


def test_scan_all_reads_both_sinks_via_roots_override(tmp_path: Path) -> None:
    comp_root = tmp_path / "comprehension_failures"
    close_root = tmp_path / "derived_close_facts"
    _write_comprehension_artifact(comp_root, "a" * 64)
    _write_derived_close_artifact(close_root, "b" * 64)

    entries, malformed = scan_all(roots={"comprehension_failures": comp_root, "derived_close_facts": close_root})

    assert malformed == []
    assert {e.sink for e in entries} == {"comprehension_failures", "derived_close_facts"}
    comp_entry = next(e for e in entries if e.sink == "comprehension_failures")
    assert comp_entry.family == "missing_total_count"
    close_entry = next(e for e in entries if e.sink == "derived_close_facts")
    assert close_entry.family == "member:socrates:mortal"


def test_scan_all_sink_filter(tmp_path: Path) -> None:
    comp_root = tmp_path / "comprehension_failures"
    close_root = tmp_path / "derived_close_facts"
    _write_comprehension_artifact(comp_root, "a" * 64)
    _write_derived_close_artifact(close_root, "b" * 64)

    entries, _ = scan_all(
        ("comprehension_failures",),
        roots={"comprehension_failures": comp_root, "derived_close_facts": close_root},
    )
    assert [e.sink for e in entries] == ["comprehension_failures"]


def test_scan_all_missing_sink_directory_is_empty_not_an_error(tmp_path: Path) -> None:
    entries, malformed = scan_all(
        ("derived_close_facts",), roots={"derived_close_facts": tmp_path / "does_not_exist"}
    )
    assert entries == []
    assert malformed == []


def test_derived_close_malformed_missing_required_field(tmp_path: Path) -> None:
    root = tmp_path / "derived_close_facts"
    root.mkdir(parents=True)
    (root / ("c" * 64 + ".json")).write_text(
        json.dumps({"status": "proposal_only", "mounted": False}), encoding="utf-8"
    )
    _entries, malformed = scan_all(("derived_close_facts",), roots={"derived_close_facts": root})
    assert len(malformed) == 1
    assert "missing_fields" in malformed[0].reason


def test_derived_close_malformed_invalid_json(tmp_path: Path) -> None:
    root = tmp_path / "derived_close_facts"
    root.mkdir(parents=True)
    (root / "d.json").write_text("not json", encoding="utf-8")
    _entries, malformed = scan_all(("derived_close_facts",), roots={"derived_close_facts": root})
    assert len(malformed) == 1
    assert "invalid_json" in malformed[0].reason


def test_record_review_unknown_hash_raises(tmp_path: Path) -> None:
    comp_root = tmp_path / "comprehension_failures"
    _write_comprehension_artifact(comp_root, "a" * 64)
    with pytest.raises(KeyError):
        record_review(
            "comprehension_failures",
            "nonexistent",
            path=tmp_path / "review_log.jsonl",
            roots={"comprehension_failures": comp_root},
        )


def test_record_review_does_not_touch_the_artifact(tmp_path: Path) -> None:
    comp_root = tmp_path / "comprehension_failures"
    content_hash = "a" * 64
    _write_comprehension_artifact(comp_root, content_hash)
    artifact_path = comp_root / f"{content_hash}.json"
    before = artifact_path.read_text(encoding="utf-8")

    record_review(
        "comprehension_failures",
        content_hash,
        note="looks fine",
        path=tmp_path / "review_log.jsonl",
        roots={"comprehension_failures": comp_root},
    )

    after = artifact_path.read_text(encoding="utf-8")
    assert before == after  # the review NEVER mutates the artifact


def test_record_review_then_reviewed_keys(tmp_path: Path) -> None:
    comp_root = tmp_path / "comprehension_failures"
    content_hash = "a" * 64
    _write_comprehension_artifact(comp_root, content_hash)
    log_path = tmp_path / "review_log.jsonl"

    assert reviewed_keys(log_path) == frozenset()
    record_review(
        "comprehension_failures", content_hash, note="ok",
        path=log_path, roots={"comprehension_failures": comp_root},
    )
    assert reviewed_keys(log_path) == {("comprehension_failures", content_hash)}


def test_reviewed_keys_missing_log_is_empty(tmp_path: Path) -> None:
    assert reviewed_keys(tmp_path / "no_such_log.jsonl") == frozenset()


def test_queue_status_counts(tmp_path: Path) -> None:
    comp_root = tmp_path / "comprehension_failures"
    close_root = tmp_path / "derived_close_facts"
    _write_comprehension_artifact(comp_root, "a" * 64)
    _write_comprehension_artifact(comp_root, "b" * 64)
    _write_derived_close_artifact(close_root, "c" * 64)
    log_path = tmp_path / "review_log.jsonl"

    record_review(
        "comprehension_failures", "a" * 64, note="reviewed",
        path=log_path, roots={"comprehension_failures": comp_root},
    )

    status = queue_status(
        roots={"comprehension_failures": comp_root, "derived_close_facts": close_root},
        log_path=log_path,
    )
    assert status["comprehension_failures"] == {
        "total": 2, "pending_review": 1, "reviewed": 1,
        "no_review_needed": 0, "malformed": 0,
    }
    assert status["derived_close_facts"] == {
        "total": 1, "pending_review": 1, "reviewed": 0,
        "no_review_needed": 0, "malformed": 0,
    }


def test_queue_entry_is_the_expected_shape() -> None:
    entry = QueueEntry(
        sink="comprehension_failures", content_hash="x", family="f",
        status="proposal_only", requires_review=True, mounted=False, path="/tmp/x.json",
    )
    assert entry.sink == "comprehension_failures"


def test_cli_review_command_reports_error_on_unknown_hash(tmp_path: Path, monkeypatch, capsys) -> None:
    from core.proposal_review import queue as queue_module
    import core.cli_proposal_queue as cli_module

    comp_root = tmp_path / "comprehension_failures"
    _write_comprehension_artifact(comp_root, "a" * 64)
    monkeypatch.setattr(
        queue_module,
        "SINKS",
        (queue_module.SinkSpec("comprehension_failures", comp_root, "test"),),
    )
    monkeypatch.setattr(queue_module, "_SINKS_BY_NAME", {"comprehension_failures": queue_module.SINKS[0]})
    monkeypatch.setattr(queue_module, "REVIEW_LOG_PATH", tmp_path / "review_log.jsonl")

    args = argparse.Namespace(sink="comprehension_failures", content_hash="does-not-exist", note=None)
    rc = cli_module.cmd_proposal_queue_review(args)
    captured = capsys.readouterr()
    assert rc == 2
    assert "error" in captured.out
