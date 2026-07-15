"""CLI tests for curated pytest suite aliases."""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

from core import cli_rust
from core import cli


def test_pyproject_installs_core_console_script_under_uv() -> None:
    pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))

    assert data["project"]["scripts"]["core"] == "core.cli:main"
    assert data["tool"]["uv"]["package"] is True
    package_includes = data["tool"]["setuptools"]["packages"]["find"]["include"]
    expected_runtime_packages = {
        "benchmarks*",
        "calibration*",
        "core_ingest*",
        "demos*",
        "engine_state*",
        "evals*",
        "packs*",
        "scripts*",
        "teaching*",
    }
    assert expected_runtime_packages.issubset(package_includes)


def test_core_test_lists_curated_suites(capsys) -> None:
    rc = cli.main(["test", "--list-suites"])

    captured = capsys.readouterr()
    assert rc == 0
    assert "fast" in captured.out.splitlines()
    assert "smoke" in captured.out.splitlines()
    assert "cognition" in captured.out.splitlines()
    assert "teaching" in captured.out.splitlines()
    assert "packs" in captured.out.splitlines()
    assert "deductive" in captured.out.splitlines()
    assert "full" in captured.out.splitlines()


def test_cli_smoke_suite_covers_ci_smoke_gate() -> None:
    """Local-first parity pin: the CLI ``smoke`` suite must cover every test
    path the CI smoke gate (.github/workflows/smoke.yml) runs.

    AGENTS.md makes ``core test --suite smoke`` the mandatory pre-push gate;
    if the CI yaml gains a path the CLI tuple lacks, the local gate silently
    narrows and regressions clear it — this pin makes that divergence loud.
    """
    from core.cli_test import TEST_SUITES

    root = Path(__file__).resolve().parents[1]
    workflow = (root / ".github/workflows/smoke.yml").read_text(encoding="utf-8")

    ci_paths: set[str] = set()
    for token in workflow.split():
        token = token.strip("\\\"'")
        if not token.startswith("tests/"):
            continue
        if "*" in token:
            matches = sorted(root.glob(token))
            assert matches, f"CI smoke glob {token!r} matches no files"
            ci_paths.update(str(m.relative_to(root)) for m in matches)
        else:
            ci_paths.add(token)

    assert ci_paths, "no tests/ paths parsed from smoke.yml — pin needs updating"
    missing = ci_paths - set(TEST_SUITES["smoke"])
    assert not missing, (
        "CLI smoke suite is narrower than the CI smoke gate; add to "
        f"core/cli_test.py TEST_SUITES['smoke']: {sorted(missing)}"
    )


def test_core_test_suite_expands_to_expected_pytest_paths(monkeypatch) -> None:
    calls: list[tuple[str, ...]] = []

    def fake_run(*args: str, check: bool = False, cwd=None) -> int:
        calls.append(args)
        return 0

    monkeypatch.setattr(cli, "_run", fake_run)

    rc = cli.main(["test", "--suite", "cognition", "-q"])

    assert rc == 0
    assert calls
    command = calls[0]
    assert command[:3] == (cli.sys.executable, "-m", "pytest")
    assert "tests/test_intent_proposition_graph.py" in command
    assert "tests/test_cognitive_turn_pipeline.py" in command
    assert "tests/test_articulation_realizer_v2.py" in command
    assert "-q" in command


def test_core_test_fast_suite_expands_to_iteration_lane(monkeypatch) -> None:
    calls: list[tuple[str, ...]] = []

    def fake_run(*args: str, check: bool = False, cwd=None) -> int:
        calls.append(args)
        return 0

    monkeypatch.setattr(cli, "_run", fake_run)

    rc = cli.main(["test", "--suite", "fast", "-q"])

    assert rc == 0
    command = calls[0]
    assert "tests/test_cli_test_suites.py" in command
    assert "tests/test_runtime_config.py" in command
    assert "tests/test_core_semantic_seed_pack.py" in command
    assert "tests/test_cognitive_eval_harness.py" in command
    assert "tests/" not in command


def test_core_test_deductive_suite_expands_to_entailment_lane(monkeypatch) -> None:
    calls: list[tuple[str, ...]] = []

    def fake_run(*args: str, check: bool = False, cwd=None) -> int:
        calls.append(args)
        return 0

    monkeypatch.setattr(cli, "_run", fake_run)

    rc = cli.main(["test", "--suite", "deductive", "-q"])

    assert rc == 0
    assert calls[0] == (
        cli.sys.executable,
        "-m",
        "pytest",
        "tests/test_deductive_logic_entail.py",
        "-q",
    )


def test_core_test_suite_accepts_pytest_flags_without_separator(monkeypatch) -> None:
    calls: list[tuple[str, ...]] = []

    def fake_run(*args: str, check: bool = False, cwd=None) -> int:
        calls.append(args)
        return 0

    monkeypatch.setattr(cli, "_run", fake_run)

    rc = cli.main(["test", "--suite", "packs", "-q"])

    assert rc == 0
    # Assert against the live suite definition rather than re-hardcoding the
    # (growing) packs file list: the contract under test is that a curated
    # suite expands to its files followed by the forwarded "-q", with no "--"
    # separator needed.
    assert calls[0] == (
        cli.sys.executable,
        "-m",
        "pytest",
        *cli._TEST_SUITES["packs"],
        "-q",
    )


def test_core_test_passthrough_still_accepts_arbitrary_pytest_args(monkeypatch) -> None:
    calls: list[tuple[str, ...]] = []

    def fake_run(*args: str, check: bool = False, cwd=None) -> int:
        calls.append(args)
        return 0

    monkeypatch.setattr(cli, "_run", fake_run)

    rc = cli.main(["test", "--", "tests/test_core_semantic_seed_pack.py", "-q"])

    assert rc == 0
    assert calls[0] == (
        cli.sys.executable,
        "-m",
        "pytest",
        "tests/test_core_semantic_seed_pack.py",
        "-q",
    )


def test_core_rust_test_sets_pyo3_forward_compat(monkeypatch) -> None:
    calls: list[tuple[tuple[str, ...], object, dict[str, str] | None]] = []

    def fake_which(name: str) -> str | None:
        return "/usr/bin/cargo" if name == "cargo" else None

    def fake_run(
        *args: str,
        check: bool = False,
        cwd=None,
        env: dict[str, str] | None = None,
    ) -> int:
        calls.append((args, cwd, env))
        return 0

    monkeypatch.setattr(cli_rust.shutil, "which", fake_which)
    monkeypatch.setattr(cli, "_run", fake_run)

    rc = cli.main(["rust", "test"])

    assert rc == 0
    assert len(calls) == 1
    args, cwd, env = calls[0]
    assert args == ("cargo", "test", "--release")
    assert cwd == cli_rust.CORE_RS_DIR
    assert env is not None
    assert env["PYO3_USE_ABI3_FORWARD_COMPATIBILITY"] == "1"


def test_non_test_commands_still_reject_unknown_args() -> None:
    with pytest.raises(SystemExit):
        cli.main(["pack", "list", "-q"])
