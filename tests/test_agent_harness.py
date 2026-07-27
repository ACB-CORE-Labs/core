"""The agent harness must be load-bearing, not decorative.

The defect these tests exist to prevent is specific and was real: a previous
routing config declared a `modelRouting` block that Claude Code does not read.
It parsed, it validated, it looked configured -- and removing it entirely would
have changed nothing. The startup script "verified" it by checking the file was
valid JSON, which passes either way.

So every test here is written to fail if the mechanism is removed. Where a
check could pass vacuously, it is paired with a control that asserts the
opposite when the mechanism is absent.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
CLAUDE = REPO / ".claude"
GUARD = CLAUDE / "hooks" / "guard_paths.py"
GUARD_CONFIG = CLAUDE / "guard-paths.json"
SETTINGS = CLAUDE / "settings.json"
OFFLOAD = CLAUDE / "bin" / "ollama-offload"


def _run_guard(payload: dict, project_dir: Path) -> subprocess.CompletedProcess:
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(project_dir))
    return subprocess.run(
        [sys.executable, str(GUARD)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
    )


# --------------------------------------------------------------------------
# The guard fires, and provably would not without its config
# --------------------------------------------------------------------------


def test_guard_injects_invariants_on_a_guarded_path() -> None:
    result = _run_guard(
        {"tool_name": "Edit", "tool_input": {"file_path": "algebra/versor.py"}}, REPO
    )
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    context = payload["hookSpecificOutput"]["additionalContext"]
    assert "versor_condition" in context
    assert payload["hookSpecificOutput"]["hookEventName"] == "PreToolUse"


def test_guard_asks_before_a_governance_edit() -> None:
    result = _run_guard({"tool_name": "Edit", "tool_input": {"file_path": "AGENTS.md"}}, REPO)
    payload = json.loads(result.stdout)
    assert payload["hookSpecificOutput"]["permissionDecision"] == "ask"


def test_guard_is_silent_on_an_unguarded_path() -> None:
    """Without this, "the guard fired" could just mean "it fires on everything"."""
    result = _run_guard({"tool_name": "Edit", "tool_input": {"file_path": "README.md"}}, REPO)
    assert result.returncode == 0
    assert result.stdout.strip() == ""


def test_guard_is_a_no_op_without_its_config() -> None:
    """The control. Same call, config absent -> nothing. If this test fails, the
    guard is producing output it did not derive from the config, which means the
    config is not what is doing the work."""
    with tempfile.TemporaryDirectory() as tmp:
        empty = Path(tmp)
        (empty / ".claude" / "hooks").mkdir(parents=True)
        shutil.copy(GUARD, empty / ".claude" / "hooks" / "guard_paths.py")
        result = _run_guard(
            {"tool_name": "Edit", "tool_input": {"file_path": "algebra/versor.py"}}, empty
        )
    assert result.returncode == 0
    assert result.stdout.strip() == ""


@pytest.mark.parametrize(
    "payload",
    [
        "",
        "not json",
        "[]",
        '{"tool_name": "Edit"}',
        '{"tool_input": {"file_path": "algebra/versor.py"}}',
        '{"tool_name": "Edit", "tool_input": {"file_path": 12345}}',
    ],
)
def test_guard_never_wedges_the_session(payload: str) -> None:
    """A guard that crashes must degrade to "no guard", never to "no session"."""
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(REPO))
    result = subprocess.run(
        [sys.executable, str(GUARD)],
        input=payload,
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
    )
    assert result.returncode == 0


# --------------------------------------------------------------------------
# The config cannot rot silently
# --------------------------------------------------------------------------


def test_every_guarded_path_exists_in_the_repo() -> None:
    """A rule pointing at a path that no longer exists guards nothing, and reads
    like coverage."""
    rules = json.loads(GUARD_CONFIG.read_text())["rules"]
    missing = [
        pattern
        for rule in rules
        for pattern in rule["paths"]
        if not any(ch in pattern for ch in "*?[") and not (REPO / pattern.rstrip("/")).exists()
    ]
    assert not missing, "guard-paths.json points at paths that do not exist: {0}".format(missing)


def test_every_rule_names_an_invariant_or_a_lane() -> None:
    """Reminders that cannot be traced to AGENTS.md train agents to skim."""
    rules = json.loads(GUARD_CONFIG.read_text())["rules"]
    assert rules, "guard-paths.json declares no rules"
    for rule in rules:
        text = " ".join(rule["reminder"])
        assert rule["reminder"], "rule {0} has no reminder".format(rule["id"])
        assert (
            "INV-" in text or "versor_condition" in text or "uv run core test" in text
        ), "rule {0} cites neither an invariant nor a validation lane".format(rule["id"])


# --------------------------------------------------------------------------
# Settings must use mechanisms that exist
# --------------------------------------------------------------------------

# Keys that look like configuration and are silently ignored by Claude Code.
# settings.json accepts unknown keys, so a fabricated mechanism is invisible
# at load time -- it has to be caught here.
FABRICATED_KEYS = ("modelRouting", "subagent_overrides", "subagentModel", "routing")


def test_settings_declares_no_mechanism_that_does_not_exist() -> None:
    settings = json.loads(SETTINGS.read_text())
    present = [key for key in FABRICATED_KEYS if key in settings]
    assert not present, (
        "settings.json declares {0}, which Claude Code does not read. Unknown keys "
        "are accepted silently, so this would look configured and do nothing. "
        "Route models by pinning `model:` in .claude/agents/*.md instead.".format(present)
    )


def test_the_hook_command_points_at_a_file_that_exists() -> None:
    settings = json.loads(SETTINGS.read_text())
    commands = [
        hook["command"]
        for group in settings["hooks"]["PreToolUse"]
        for hook in group["hooks"]
        if hook["type"] == "command"
    ]
    assert commands, "no PreToolUse command hook is configured"
    for command in commands:
        assert "guard_paths.py" in command
    assert GUARD.exists()


def test_every_agent_pins_a_model() -> None:
    """An unpinned agent silently inherits the caller's model, which turns cost
    routing into a coincidence."""
    agents = sorted((CLAUDE / "agents").glob("*.md"))
    assert agents, "no agents defined"
    unpinned = [
        path.name
        for path in agents
        if not any(line.startswith("model:") for line in path.read_text().splitlines()[:12])
    ]
    assert not unpinned, "agents with no pinned model: {0}".format(unpinned)


def test_every_agent_and_skill_declares_a_name_and_description() -> None:
    files = sorted((CLAUDE / "agents").glob("*.md")) + sorted(
        (CLAUDE / "skills").glob("*/SKILL.md")
    )
    for path in files:
        head = path.read_text().splitlines()[:12]
        assert any(line.startswith("name:") for line in head), path
        assert any(line.startswith("description:") for line in head), path


# --------------------------------------------------------------------------
# The local-model tool fails correctly -- checkable without Ollama running
# --------------------------------------------------------------------------


def test_offload_reports_unreachable_rather_than_returning_a_result() -> None:
    """Exit 4, not 0 and not a traceback. A caller must never be able to mistake
    "the local model was unavailable" for "the local model said nothing"."""
    result = subprocess.run(
        [sys.executable, str(OFFLOAD), "classify", "--labels", "a,b", "--host", "http://127.0.0.1:1"],
        input="some text",
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 4
    assert result.stdout.strip() == ""


def test_offload_rejects_input_it_would_have_to_truncate() -> None:
    """Summarising a silently truncated log is a lie about the log."""
    result = subprocess.run(
        [sys.executable, str(OFFLOAD), "summarize", "--max-input", "10"],
        input="x" * 500,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 2


def test_offload_exposes_no_mode_that_asserts() -> None:
    """The trust boundary is structural: there is no mode that writes, decides,
    or answers. Adding one is the failure this test names in advance."""
    result = subprocess.run(
        [sys.executable, str(OFFLOAD), "--help"], capture_output=True, text=True, timeout=60
    )
    assert result.returncode == 0
    modes = result.stdout
    for forbidden in ("answer", "write", "fix", "decide", "patch"):
        assert "{0},".format(forbidden) not in modes and "{0}}}".format(forbidden) not in modes
