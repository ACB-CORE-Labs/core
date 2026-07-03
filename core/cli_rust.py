"""Rust backend CLI command handlers.

The top-level CLI owns argparse construction and subprocess policy. This module
owns the Rust/native-substrate command behavior so ``core/cli.py`` does not keep
absorbing every command family.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import NoReturn, Protocol


DEFAULT_REPO_ROOT = Path(__file__).resolve().parent.parent
CORE_RS_DIR = DEFAULT_REPO_ROOT / "core-rs"
CORE_RS_MANIFEST = CORE_RS_DIR / "Cargo.toml"


class CommandRunner(Protocol):
    def __call__(
        self,
        *args: str,
        check: bool = False,
        cwd: Path | None = None,
        env: dict[str, str] | None = None,
    ) -> int: ...


class DieHandler(Protocol):
    def __call__(self, message: str, *, code: int = 2) -> NoReturn: ...


def rust_paths(repo_root: Path = DEFAULT_REPO_ROOT) -> tuple[Path, Path]:
    core_rs_dir = repo_root / "core-rs"
    return core_rs_dir, core_rs_dir / "Cargo.toml"


def run_command(
    *args: str,
    check: bool = False,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
) -> int:
    completed = subprocess.run(args, check=check, text=True, cwd=cwd, env=env)
    return int(completed.returncode)


def die(message: str, *, code: int = 2) -> NoReturn:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(code)


def rust_build_env() -> dict[str, str]:
    """Return the environment used for PyO3-backed Rust build/test commands."""
    env = os.environ.copy()
    # PyO3 0.21 supports Python through 3.12. Fresh uv environments may be
    # 3.13+, so use PyO3's documented forward-compatibility escape hatch unless
    # the operator has provided a more specific PYO3_* policy.
    env.setdefault("PYO3_USE_ABI3_FORWARD_COMPATIBILITY", "1")
    return env


def probe_core_rs() -> tuple[bool, str]:
    try:
        import core_rs
    except Exception as exc:
        return False, f"{exc.__class__.__name__}: {exc}"
    return True, str(getattr(core_rs, "__file__", "<built-in>"))


def print_rust_status(*, repo_root: Path = DEFAULT_REPO_ROOT) -> bool:
    from algebra.backend import using_rust

    core_rs_dir, core_rs_manifest = rust_paths(repo_root)
    active = using_rust()
    importable, import_detail = probe_core_rs()
    print(f"core_rs crate : {core_rs_dir}")
    print(f"cargo manifest: {core_rs_manifest}")
    print(f"CORE_BACKEND  : {os.environ.get('CORE_BACKEND', '') or '(default python)'}")
    print(f"core_rs import: {'ok' if importable else 'missing'}")
    print(f"core_rs detail: {import_detail}")
    print(f"rust backend  : {'active' if active else 'inactive'}")
    if not active:
        print("activation    : run `core rust build`")
    return active


def cmd_rust_status(
    args: argparse.Namespace,
    *,
    repo_root: Path = DEFAULT_REPO_ROOT,
) -> int:
    """Print Rust backend activation status."""
    return 0 if print_rust_status(repo_root=repo_root) or not args.require_active else 1


def cmd_rust_build(
    args: argparse.Namespace,
    *,
    repo_root: Path = DEFAULT_REPO_ROOT,
    run: CommandRunner = run_command,
    fail: DieHandler = die,
    python_executable: str = sys.executable,
) -> int:
    """Build/install core_rs into the active Python environment."""
    _, core_rs_manifest = rust_paths(repo_root)
    if not core_rs_manifest.exists():
        fail(f"core-rs manifest not found: {core_rs_manifest}", code=1)
    if shutil.which("uv") is not None:
        rc = run("uv", "pip", "install", "maturin")
        if rc != 0:
            return rc
    cmd = [
        python_executable,
        "-m",
        "maturin",
        "develop",
        "--release",
        "--manifest-path",
        str(core_rs_manifest),
    ]
    if args.skip_auditwheel:
        cmd.append("--skip-auditwheel")
    return run(*cmd, env=rust_build_env())


def cmd_rust_test(
    args: argparse.Namespace,
    *,
    repo_root: Path = DEFAULT_REPO_ROOT,
    run: CommandRunner = run_command,
    fail: DieHandler = die,
) -> int:
    """Run Rust crate tests."""
    del args
    core_rs_dir, _ = rust_paths(repo_root)
    if shutil.which("cargo") is None:
        fail("cargo not found. Install a Rust toolchain first.", code=1)
    return run("cargo", "test", "--release", cwd=core_rs_dir, env=rust_build_env())
