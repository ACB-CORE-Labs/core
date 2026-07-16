# CORE Agent Instructions for Claude

`AGENTS.md` is the canonical governance file. If this file conflicts, follow `AGENTS.md`.

Startup: read `AGENTS.md`, `docs/specs/runtime_contracts.md`, inspect working tree, use the smallest validation lane.
**CRITICAL**: Remote is `core-gitquarters.acbcontent.org`. Do not use GitHub/`gh` CLI. Use Forgejo tools/`gitea` CLI.
**CI**: local-first — pre-push gates are mandatory; CI jobs run on the developer's local Mac Act runner, never on the Forgejo server (see `AGENTS.md` §CI/CD Runner Architecture).

Before non-trivial edits, apply the protocol in `AGENTS.md`.

Do not place architecture, invariants, memory rules, or alternate workflow policy here. Update `AGENTS.md` instead.
