# CORE — Claude

`AGENTS.md` is the canonical governance file. If this file conflicts, follow `AGENTS.md`.

Startup: read `AGENTS.md`, `docs/specs/runtime_contracts.md`, inspect tree, smallest lane.
Remote: `core-gitquarters.acbcontent.org`. No GitHub/`gh`/`tea`. Forgejo MCP.
CI: local-first (smoke in-worktree, then merge). No Docker CI. Host runner only: `ubuntu-latest:host`. See `AGENTS.md`.

Before non-trivial edits, apply the protocol in `AGENTS.md`.

Do not place architecture, invariants, memory rules, or alternate workflow policy here. Update `AGENTS.md` instead.
