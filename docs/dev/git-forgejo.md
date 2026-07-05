# Git + Forgejo Setup (replaces GitHub CLI)

We do **not** use the `gh` (GitHub CLI) tool.

All Git operations use plain `git`, with remotes transparently forwarded to our self-hosted Forgejo instance via `insteadOf` configuration.

## Required global config

```bash
git config --global url."ssh://git@core-gitquarters.acbcontent.org:29222/core-labs/".insteadOf "git@github.com:core-labs/"
git config --global url."https://core-gitquarters.acbcontent.org/core-labs/".insteadOf "https://github.com/core-labs/"
git config --global url."ssh://git@core-gitquarters.acbcontent.org:29222/AssetOverflow/".insteadOf "git@github.com:AssetOverflow/"
git config --global url."https://core-gitquarters.acbcontent.org/AssetOverflow/".insteadOf "https://github.com/AssetOverflow/"
```

## Usage

- Clone, fetch, push, etc. with normal `git` commands (e.g. `git push -u origin main`).
- The above rules rewrite `git@github.com:AssetOverflow/core.git` etc. to the Forgejo SSH/HTTPS endpoints.
- For PRs, reviews, and issue management: use the Forgejo web UI at https://core-gitquarters.acbcontent.org/forgejo_admin/core

See AGENTS.md for full workflow rules, branch hygiene, and commit/PR guidelines.

This setup is mandatory for all contributors and agents.
