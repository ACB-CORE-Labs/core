---
name: core-pr-ready
description: Pre-merge gate for CORE — run the validation lanes that actually cover the change, answer the AGENTS.md PR checklist, and write the PR description with its [Verification] block. Use before opening or updating a PR on core-labs/core.
---

# CORE pre-PR gate

CORE's CI is local-first. The lanes you run in the worktree **are** the gate;
the Forgejo Actions runner is a local Act runner on the Mac and simply queues
when the machine is asleep. So the evidence in the PR description is the
evidence — there is no second system that will catch what you skipped.

## 1. Run the lanes that cover the change

```bash
uv run core test --suite smoke -q          # always
```

Then every lane the change actually touches:

| Touched | Lane |
| :-- | :-- |
| `algebra/`, `field/`, `core/physics/` | `--suite algebra` |
| `vault/`, `teaching/`, `session/` | `--suite teaching` |
| `core/cognition/`, `generate/` | `--suite cognition` |
| `packs/` | `--suite packs` |
| runtime / serving paths | `--suite runtime` |
| trust boundaries, broad refactor | `--suite full` |

Two traps worth naming:

- **The smoke gate is not the full suite.** Run the PR's own tests against the
  *rebased base*, not against the branch you started from.
- **A pin registered in no suite never runs.** Suites are hand-curated tuples in
  `core/cli_test.py`. If you added a test, confirm the suite's collected count
  moved. A test that exists and is never selected is not coverage.

## 2. Answer the AGENTS.md checklist — in writing

```text
What capability, performance property, or security boundary did this add or protect?
Which invariant proves the field remained valid?
Which validation lane proves the change?
Did this avoid hidden normalization, stochastic fallback, approximate recall, and unreviewed mutation?
If it touched user input, files, dynamic imports, or logs, what trust boundary was enforced?
```

## 3. Apply the absence test

For every claim of a green result, ask: **would this measurement look identical
with the mechanism removed?** If yes, you have measured a decoration. Add the
control — remove or disable the mechanism and show the number moves — or state
plainly that the result is not yet evidence.

Same discipline for counts: never quote an acceptance metric without its
identity metric. A corpus cannot size an inventory.

## 4. Write the description

```markdown
## Summary
<what changed and why, in the terms of the cognitive model — not the diff>

## Changes
<file-level, grouped by concern>

## Invariants protected
<INV-nn, and the mechanism by which each holds>

## [Verification]:
<exact commands run, and their real output — pass AND fail>
<what was NOT run, and why>
```

The `[Verification]:` block is load-bearing. Paste real output. If a lane
failed, say so with the output — a PR that reports success on an unrun lane is
worse than one that reports a failure honestly.

## 5. Push and open

```bash
git push -u forgejo-https <branch>
```

Explicit remote name. Never `gh`, never `tea` — use the `forgejo-core` MCP
server or the Forgejo web UI for the PR itself.

Then stop. A green PR sits until Shay authorizes the merge; there is no
auto-merge and no self-authorization. After a merge, delete the branch **and**
its worktree immediately.
