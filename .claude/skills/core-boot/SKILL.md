---
name: core-boot
description: Start a work session on the CORE repo — read the governance files, establish a clean worktree off Forgejo truth, and run the smoke lane before touching anything. Use at the beginning of any non-trivial CORE task, or when resuming and the repo state is ambiguous.
---

# CORE session boot

Statelessness compensation. Run this before editing, proposing, or dispatching.

## 1. Read the governance, in this order

1. `AGENTS.md` — canonical. Invariants, working doctrine, validation lanes, PR
   checklist, provider-file policy.
2. `docs/specs/runtime_contracts.md` — the full contracts behind INV-32/33/34.
3. `CLAIMS.md` — what CORE currently claims, and at what standing.

`CLAUDE.md` and `GEMINI.md` are pointers, not sources. If a provider file
conflicts with `AGENTS.md`, `AGENTS.md` wins.

There is no `GROK.md`. If an instruction tells you to read one, that
instruction is stale — report it rather than working around it.

## 2. Establish where you are

```bash
pwd && git rev-parse --show-toplevel
git status --short --branch
git worktree list
git stash list
```

If the tree is dirty, classify every changed and untracked file **before**
moving branches. Unknown work gets a described stash, never a discard.

## 3. Base off Forgejo, not the mirror

Forgejo is the source of truth for this repo. `origin` is the GitHub mirror and
its Actions are billing-locked dead signals — never chase red CI there, never
base off it.

```bash
git fetch forgejo-https --prune          # or: forgejo
git log --oneline -1 forgejo-https/main
```

Local `main` drifts from Forgejo truth. Diff, base, and rebase against
`forgejo-https/main`.

If a push over `forgejo` (SSH, port 29222) hangs, that is usually a VPN dropping
the port — MCP over 443 still works. Push over `forgejo-https` instead. Always
push by explicit remote name; pushes auto-replicate to the GitHub mirror.

## 4. New work goes in a fresh worktree

Panes share a working directory and a branch. Parallel agents must never share
one.

```bash
git worktree add ../core-wt-<slug> -b <type>/<slug> forgejo-https/main
```

## 5. Prove the baseline before you change it

```bash
uv run core test --suite smoke -q
```

Run it **in the worktree you will work in**. A green smoke lane somewhere else
proves nothing about here. If it fails before you have changed anything, that is
the finding — report it and stop rather than layering work onto a red base.

Use `uv` throughout. Never system `pip`.

## 6. Check for continuity

Look for a recent `session-break-summary-*.md` and read the most relevant one.
Check open PRs at `https://core-gitquarters.acbcontent.org/core-labs/core/pulls`
or via the `forgejo-core` MCP server. Never `gh`, never `tea`.

## 7. State the scope in one sentence

Before any further action, say what this session is for and what it is not.
