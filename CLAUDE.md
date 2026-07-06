# CORE Agent Instructions for Claude

`AGENTS.md` is the canonical governance file for this repo. If this file
conflicts with `AGENTS.md`, follow `AGENTS.md`.

Claude-specific startup: read `AGENTS.md`, read
`docs/specs/runtime_contracts.md`, inspect the working tree, then use the
smallest validation lane that proves the change.
**CRITICAL**: Our remote and CI/CD platform is `core-gitquarters.acbcontent.org`. We are deprecating GitHub usage. Use the Forgejo MCP tools if available; otherwise, fallback to the `gitea`/`tea` CLI or `forgejo` CLI.

Before any non-trivial edit, apply the Reasoning and Problem-Solving
Discipline protocol in `AGENTS.md`.

Do not place architecture, invariants, memory rules, or alternate workflow
policy here. Update `AGENTS.md` instead.
