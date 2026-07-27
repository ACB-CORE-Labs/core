#!/usr/bin/env python3
"""Project-agnostic PreToolUse guard: put a path's invariants in front of the
agent at the moment it edits that path.

This script contains NO project knowledge. Everything it enforces comes from a
sibling ``guard-paths.json``. Drop the pair into any repo, write the rules, and
the guard applies there. With no config file it is a deliberate no-op.

Contract with Claude Code
-------------------------
stdin   PreToolUse hook payload (JSON)
stdout  hook response (JSON) -- this is the channel Claude Code reads
exit 0  always, on every path, including internal failure

Exit 0 is not laziness, it is the safety property: a guard that crashes must
degrade to "no guard", never to "no session". Blocking is expressed in the
response body (``permissionDecision``), never by the exit code.

Config schema (guard-paths.json)
--------------------------------
{
  "rules": [
    {
      "id":       "short-slug",                  # required, unique
      "paths":    ["algebra/", "field/*.py"],    # prefix or fnmatch glob
      "action":   "context" | "ask" | "deny",    # default "context"
      "title":    "one line shown to the human",
      "reminder": ["line fed to the model", "..."]
    }
  ]
}

``context`` injects the reminder and lets the normal permission flow proceed.
``ask`` forces a permission prompt. ``deny`` refuses the call outright.
"""

from __future__ import annotations

import fnmatch
import json
import os
import re
import sys
from typing import Any, Dict, Iterable, List, Sequence, Tuple

# Tools whose payload names the file directly.
_PATH_ARG_TOOLS = {
    "Edit": "file_path",
    "Write": "file_path",
    "NotebookEdit": "notebook_path",
    "MultiEdit": "file_path",
}

# Shell tokens that look like a path we care about. Deliberately generous: the
# default action is to *inform*, so a false positive costs one extra reminder
# while a false negative costs an unguarded edit.
_SHELL_PATH_RE = re.compile(r"[A-Za-z0-9_./-]*[/][A-Za-z0-9_./-]*")

_VALID_ACTIONS = ("context", "ask", "deny")


def _project_dir() -> str:
    """Repo root. Claude Code exports this; fall back to the script's parent."""
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env:
        return env
    # .claude/hooks/guard_paths.py -> repo root is two levels up from .claude
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _load_rules(project_dir: str) -> List[Dict[str, Any]]:
    """Read and validate the rule set. Any defect drops the offending rule
    rather than the whole config -- a typo in one rule must not silently
    disarm the others."""
    path = os.path.join(project_dir, ".claude", "guard-paths.json")
    try:
        with open(path, "r", encoding="utf-8") as handle:
            raw = json.load(handle)
    except (OSError, ValueError):
        return []

    rules: List[Dict[str, Any]] = []
    for entry in raw.get("rules", []) if isinstance(raw, dict) else []:
        if not isinstance(entry, dict):
            continue
        paths = entry.get("paths")
        if not isinstance(paths, list) or not paths:
            continue
        action = entry.get("action", "context")
        if action not in _VALID_ACTIONS:
            action = "context"
        reminder = entry.get("reminder", [])
        rules.append(
            {
                "id": str(entry.get("id", "unnamed")),
                "paths": [str(p) for p in paths],
                "action": action,
                "title": str(entry.get("title", "")),
                "reminder": [str(line) for line in reminder]
                if isinstance(reminder, list)
                else [str(reminder)],
            }
        )
    return rules


def _relativize(candidate: str, project_dir: str) -> str:
    """Normalize to a repo-relative POSIX path so rules stay portable."""
    cleaned = candidate.strip().strip("'\"")
    if not cleaned:
        return ""
    if os.path.isabs(cleaned):
        try:
            cleaned = os.path.relpath(cleaned, project_dir)
        except ValueError:  # different drive on Windows
            return ""
    cleaned = os.path.normpath(cleaned).replace(os.sep, "/")
    return "" if cleaned.startswith("..") else cleaned


def _candidate_paths(tool_name: str, tool_input: Dict[str, Any], project_dir: str) -> List[str]:
    """Every repo-relative path this tool call might touch."""
    arg = _PATH_ARG_TOOLS.get(tool_name)
    if arg:
        value = tool_input.get(arg)
        rel = _relativize(str(value), project_dir) if isinstance(value, str) else ""
        return [rel] if rel else []

    if tool_name == "Bash":
        command = tool_input.get("command")
        if not isinstance(command, str):
            return []
        found = []
        for token in _SHELL_PATH_RE.findall(command):
            rel = _relativize(token, project_dir)
            if rel:
                found.append(rel)
        return found

    return []


def _matches(path: str, pattern: str) -> bool:
    """A pattern ending in '/' is a directory prefix; anything containing a
    glob metacharacter is fnmatch; otherwise exact or prefix match."""
    if pattern.endswith("/"):
        return path == pattern.rstrip("/") or path.startswith(pattern)
    if any(ch in pattern for ch in "*?["):
        return fnmatch.fnmatch(path, pattern)
    return path == pattern or path.startswith(pattern + "/")


def _triggered(rules: Sequence[Dict[str, Any]], paths: Iterable[str]) -> List[Tuple[Dict[str, Any], str]]:
    """Rules hit by these paths, first matching path per rule, config order."""
    hits: List[Tuple[Dict[str, Any], str]] = []
    path_list = list(paths)
    for rule in rules:
        for path in path_list:
            if any(_matches(path, pattern) for pattern in rule["paths"]):
                hits.append((rule, path))
                break
    return hits


def _severity(action: str) -> int:
    return _VALID_ACTIONS.index(action)


def _compose(hits: Sequence[Tuple[Dict[str, Any], str]]) -> Dict[str, Any]:
    """Build the hook response. The strictest triggered action wins."""
    strongest = max(hits, key=lambda hit: _severity(hit[0]["action"]))[0]["action"]

    blocks: List[str] = []
    headlines: List[str] = []
    for rule, path in hits:
        headlines.append("{0} ({1})".format(rule["title"] or rule["id"], path))
        body = "\n".join("  - {0}".format(line) for line in rule["reminder"])
        blocks.append("[{0}] {1}\n{2}".format(rule["id"], path, body) if body else "[{0}] {1}".format(rule["id"], path))

    context = "Guarded path. Before you continue:\n\n" + "\n\n".join(blocks)
    summary = "; ".join(headlines)

    hook_output: Dict[str, Any] = {
        "hookEventName": "PreToolUse",
        "additionalContext": context,
    }
    if strongest in ("ask", "deny"):
        hook_output["permissionDecision"] = "ask" if strongest == "ask" else "deny"
        hook_output["permissionDecisionReason"] = context

    return {"systemMessage": "guard-paths: " + summary, "hookSpecificOutput": hook_output}


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except ValueError:
        return 0
    if not isinstance(payload, dict):
        return 0

    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return 0

    project_dir = _project_dir()
    rules = _load_rules(project_dir)
    if not rules:
        return 0

    paths = _candidate_paths(str(payload.get("tool_name", "")), tool_input, project_dir)
    if not paths:
        return 0

    hits = _triggered(rules, paths)
    if not hits:
        return 0

    json.dump(_compose(hits), sys.stdout)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:  # noqa: BLE001 -- a guard must never wedge the session
        sys.exit(0)
