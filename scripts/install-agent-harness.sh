#!/usr/bin/env bash
# =============================================================================
# scripts/install-agent-harness.sh
#
# Install the PORTABLE half of CORE's agent harness into ~/.claude/, so it
# applies to every project on this machine.
#
# The harness is deliberately split:
#
#   portable  (this script installs)   the generic path guard, the local-model
#                                      offload tool, and the skill that says
#                                      when to trust it. Zero project knowledge.
#
#   project   (stays in the repo)      .claude/guard-paths.json and
#                                      .claude/agents/*.md. All CORE-specific
#                                      knowledge lives here, versioned and
#                                      reviewable in a PR.
#
# To use the guard in another repo, install this once, then write that repo's
# own .claude/guard-paths.json. The hook itself needs no changes.
#
# This script never edits ~/.claude/settings.json. It prints the snippet to add.
# Silently rewriting a config you did not read is how harnesses break.
#
# USAGE
#   bash scripts/install-agent-harness.sh            # install
#   bash scripts/install-agent-harness.sh --dry-run  # show what would happen
# =============================================================================

set -euo pipefail

DRY_RUN=0
[ "${1:-}" = "--dry-run" ] && DRY_RUN=1

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$REPO_ROOT/.claude"
DEST="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"

_ok()   { printf '✓ %s\n' "$*"; }
_info() { printf '  %s\n' "$*"; }
_die()  { printf '✗ %s\n' "$*" >&2; exit 1; }

[ -d "$SRC" ] || _die "no .claude/ in $REPO_ROOT — run this from the CORE repo"

printf '\nInstalling portable agent harness → %s\n\n' "$DEST"

install_file() {
    local src="$1" dest="$2" mode="$3"
    [ -f "$src" ] || _die "missing source file: $src"
    if [ "$DRY_RUN" = "1" ]; then
        _info "would install $dest"
        return
    fi
    mkdir -p "$(dirname "$dest")"
    if [ -f "$dest" ] && ! cmp -s "$src" "$dest"; then
        cp "$dest" "$dest.bak"
        _info "existing file backed up → $(basename "$dest").bak"
    fi
    cp "$src" "$dest"
    chmod "$mode" "$dest"
    _ok "$dest"
}

install_file "$SRC/hooks/guard_paths.py"        "$DEST/hooks/guard_paths.py"        755
install_file "$SRC/bin/ollama-offload"          "$DEST/bin/ollama-offload"          755
install_file "$SRC/skills/ollama-offload/SKILL.md" "$DEST/skills/ollama-offload/SKILL.md" 644

printf '\n'
if [ "$DRY_RUN" = "1" ]; then
    _ok "Dry run complete — nothing was written."
else
    _ok "Portable harness installed."
fi

cat <<'SNIPPET'

────────────────────────────────────────────────────────────────────────
Add to ~/.claude/settings.json to arm the guard in every project.
Merge into any existing "hooks" block — do not replace it.

  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit|NotebookEdit|Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$HOME/.claude/hooks/guard_paths.py\"",
            "timeout": 10,
            "statusMessage": "Checking invariant paths"
          }
        ]
      }
    ]
  }

The guard is a NO-OP in any repo without a .claude/guard-paths.json, so
arming it globally is safe. It only speaks where a project has told it
what to protect.

To protect a new repo, create <repo>/.claude/guard-paths.json:

  {
    "rules": [
      {
        "id": "schema",
        "title": "Database schema",
        "paths": ["db/migrations/", "prisma/schema.prisma"],
        "action": "ask",
        "reminder": ["Migrations are forward-only. Never edit an applied one."]
      }
    ]
  }

Verify it fires, and — just as important — that it goes quiet when the
config is removed:

  echo '{"tool_name":"Edit","tool_input":{"file_path":"<guarded path>"}}' \
    | python3 ~/.claude/hooks/guard_paths.py
────────────────────────────────────────────────────────────────────────
SNIPPET
