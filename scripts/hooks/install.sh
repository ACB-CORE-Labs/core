#!/bin/sh
# Install the CORE local-first pre-push gate for THIS clone.
#
# Points git at the tracked hooks directory (scripts/hooks) via core.hooksPath.
# The relative path resolves per-worktree, so every linked worktree gets the
# same gate. Idempotent — safe to re-run. Run once after cloning:
#
#   sh scripts/hooks/install.sh
#
# Uninstall: git config --unset core.hooksPath

set -eu

repo_root="$(git rev-parse --show-toplevel)"
cd "${repo_root}"

chmod +x scripts/hooks/pre-push
git config core.hooksPath scripts/hooks

echo "[install] core.hooksPath -> scripts/hooks"
echo "[install] pre-push gate active: smoke suite + warmed_session lane pin."
echo "[install] emergency bypass (discouraged): git push --no-verify"
