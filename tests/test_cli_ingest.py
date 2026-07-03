from __future__ import annotations

import builtins
import hashlib
import json
from pathlib import Path

import pytest

from core.cli import build_parser, main


def test_ingest_help_names_durable_read_only_boundary(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as excinfo:
        build_parser().parse_args(["ingest", "-h"])

    assert excinfo.value.code == 0
    out = capsys.readouterr().out
    assert "durable core_ingest compiler" in out
    assert "read-only" in out
    assert "ingest/gate.py" in out


def test_ingest_compile_text_json_reports_durable_boundary(
    capsys: pytest.CaptureFixture[str],
) -> None:
    text = "The logos is the foundation.\n\nThe field remains coherent."

    rc = main(["ingest", "compile", "--text", text, "--json"])

    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["command"] == "ingest compile"
    assert payload["path"] == "durable"
    assert payload["boundary_owner"] == "core_ingest"
    assert payload["runtime_gate"] == "ingest/gate.py is not imported or called"
    assert payload["mutates"] is False
    assert payload["source"]["kind"] == "text"
    assert payload["source"]["sha256"] == hashlib.sha256(text.encode()).hexdigest()
    assert payload["summary"]["accepted"] == len(payload["artifacts"])
    assert payload["summary"]["accepted"] >= 1


def test_ingest_compile_file_json_reports_regular_file(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    source = tmp_path / "source.md"
    source.write_text("First paragraph.\n\nSecond paragraph.", encoding="utf-8")

    rc = main(["ingest", "compile", "--file", str(source), "--json"])

    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["source"]["kind"] == "file"
    assert payload["source"]["path"] == str(source.resolve())
    assert payload["summary"]["results"] >= 1


def test_ingest_compile_file_rejects_directory(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    rc = main(["ingest", "compile", "--file", str(tmp_path)])

    assert rc == 2
    captured = capsys.readouterr()
    assert "regular file" in captured.err


def test_ingest_compile_file_respects_size_limit(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    source = tmp_path / "source.md"
    source.write_text("too large for this test", encoding="utf-8")

    rc = main(["ingest", "compile", "--file", str(source), "--max-bytes", "4"])

    assert rc == 2
    captured = capsys.readouterr()
    assert "above --max-bytes 4" in captured.err


def test_ingest_compile_does_not_import_runtime_gate(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    real_import = builtins.__import__

    def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "ingest.gate" or (name == "ingest" and "gate" in fromlist):
            raise AssertionError("durable core_ingest CLI imported runtime gate")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", guarded_import)

    rc = main(["ingest", "compile", "--text", "Boundary check.", "--json"])

    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["runtime_gate"] == "ingest/gate.py is not imported or called"
