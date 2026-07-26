"""The injected `CommandRunner` must accept everything its call sites pass.

`core/cli.py::_run` is injected into `cli_rust.cmd_rust_build` and
`cli_test`'s runner. Both are typed against a `CommandRunner` Protocol carrying
`check`, `cwd` and `env`. `_run` was missing `env`, so `core rust build` raised
`TypeError: _run() got an unexpected keyword argument 'env'` on every
invocation — the documented Rust activation path had never worked.

Nothing caught it because the runner is only exercised through subprocess-y
commands that tests avoid calling for real. So the pin is on the SIGNATURE,
checked against the Protocol rather than against a hand-written list, so a
future keyword added to one side cannot drift from the other.
"""

from __future__ import annotations

import inspect

import pytest

from core.cli import _run
from core.cli_test import CommandRunner, run_command


def _keywords(fn: object) -> set[str]:
    sig = inspect.signature(fn)  # type: ignore[arg-type]
    return {
        name
        for name, p in sig.parameters.items()
        if p.kind in (p.KEYWORD_ONLY, p.POSITIONAL_OR_KEYWORD)
        and name not in ("args", "self")
    }


def test_injected_runner_satisfies_the_command_runner_protocol() -> None:
    """Derived from the Protocol, so it cannot fall behind it."""
    protocol_kwargs = _keywords(CommandRunner.__call__)
    assert protocol_kwargs, "CommandRunner.__call__ has no keywords — protocol changed?"
    missing = protocol_kwargs - _keywords(_run)
    assert not missing, (
        f"core.cli._run is missing {sorted(missing)} — it is injected into "
        "cli_rust.cmd_rust_build, which passes env=rust_build_env(). A runner "
        "that cannot accept what its call sites pass raises TypeError at runtime."
    )


def test_default_runner_and_injected_runner_agree() -> None:
    """Both runners are used interchangeably; their keywords must match."""
    assert _keywords(_run) == _keywords(run_command)


@pytest.mark.parametrize("keyword", ["check", "cwd", "env"])
def test_runner_accepts_each_documented_keyword(keyword: str) -> None:
    assert keyword in _keywords(_run)


def test_rust_build_passes_env_so_the_runner_must_accept_it() -> None:
    """Pins the actual call site that broke, not just the signature.

    Runs `cmd_rust_build` with a recording fake runner: it must reach the
    maturin invocation and carry an env, rather than raising TypeError.
    """
    import argparse

    from core import cli_rust

    seen: list[dict[str, object]] = []

    def fake_run(*args: str, check: bool = False, cwd: object = None,
                 env: dict[str, str] | None = None) -> int:
        seen.append({"args": args, "env": env})
        return 0

    args = argparse.Namespace(skip_auditwheel=False)
    rc = cli_rust.cmd_rust_build(
        args, run=fake_run, fail=lambda m, code=2: (_ for _ in ()).throw(SystemExit(code)),
        python_executable="python3",
    )
    assert rc == 0
    maturin = [c for c in seen if "maturin" in c["args"]]
    assert maturin, f"maturin was never invoked; calls={seen}"
    env = maturin[-1]["env"]
    assert isinstance(env, dict)
    assert env.get("PYO3_USE_ABI3_FORWARD_COMPATIBILITY") == "1", (
        "the env is the whole reason the keyword exists — PyO3 0.21 supports "
        "Python through 3.12 and needs the forward-compatibility escape hatch"
    )
