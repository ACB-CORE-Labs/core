# CORE Agent Instructions

This is the canonical governance file for this repository.

If any provider-specific file (`CLAUDE.md`, `GEMINI.md`, or future agent files) overlaps with this document, `AGENTS.md` wins. Provider files should only contain minimal startup and workflow notes, not alternate architecture or alternate invariants.

## Session Continuity (lightweight, session-break only)

When you are approaching a stopping point, known pause, or session break:
- Create a file named `session-break-summary-<YYYY-MM-DD-HHMM>.md` (precise datetime recommended) at the repo root or in `docs/sessions/`.
- Keep it short and actionable: current branch/state, what was just completed, exact next concrete steps, any open invariants/tests/hazards, and key files to re-read.
- At the **start of any new session** (or subagent): Quickly scan for any recent `session-break-summary-*.md` files. Read the most relevant one if present.
- Once you have resumed the work and continued past the break point, **delete the file**. Its only purpose is temporary continuity for the immediate next pickup.

The previous heavy `HANDOFF-*.md` / formal handoff machinery is retired (see history in git and docs/handoffs/ for old artifacts).

## Mission

CORE is a deterministic cognitive engine under construction.

It is:
- inspectable
- replayable
- evidence-governed
- coherence-first

It is not:
- a transformer wrapper
- a generic chatbot
- an infrastructure playground
- a stochastic fallback shell

## North star

CORE should become capable of:

```text
listen -> comprehend -> recall -> think -> articulate -> learn from reviewed correction -> replay deterministically
```

The live path is:

```text
CognitiveTurnPipeline
-> tokenize / OOV policy / inject
-> intent classification
-> PropositionGraph
-> ArticulationTarget
-> deterministic realizer / articulation surface
-> telemetry / trace
-> reviewed teaching capture when applicable
-> deterministic replay / eval / calibration
```

Improve CORE by strengthening this path, not by bypassing it.

## Non-negotiable invariants

### Field invariant
Every runtime field state `F` must satisfy:

```text
versor_condition(F) < 1e-6
```

Do not weaken this threshold to make code or tests pass.
Fix the operator or construction boundary that violated it.

### Allowed normalization boundaries
Normalization / closure / canonicalization belongs only at explicit construction or algebra boundaries, such as:
- `ingest/gate.py`
- `packs/compiler.py`
- `algebra/versor.py`
- `sensorium/*/canonical.py`
- `session/context.py` for session-scoped **semantic anchoring** of the field toward the session concept-attractor (the anchor pull, hemisphere consistency). Allowed ONLY because every such op (1) preserves `versor_condition` BY CONSTRUCTION — composed from `rotor_power` / `word_transition_rotor` / `versor_apply` on the Spin manifold, never a post-hoc `unitize`/grade-projection — AND (2) carries semantic meaning in the cognitive model.
- other explicitly documented construction boundaries

Forbidden in hot paths and repair layers, including:
- `generate/stream.py`
- `field/propagate.py`
- `vault/store.py`
- logging / telemetry / shell glue

**The bright line — semantic anchoring vs. drift repair.** An op is *semantic anchoring* (allowed at the sites above) iff it preserves `versor_condition` by construction AND expresses a relation in the cognitive model. It is *drift repair* (forbidden) iff its purpose is to restore a numerical invariant a prior function should have preserved. Closure of field transitions is owned solely by `algebra/versor.py` (`_close_applied_versor`); no other site may "fix" it. Naming must not disguise the distinction: an op that anchors semantically must not be named or documented as a "drift fix".

Do not add drift repair, watchdog normalization, hidden unitization, or post-hoc algebra fixes outside owned boundaries.

### Exact recall
Runtime recall remains exact and deterministic.
Do not add:
- cosine similarity
- ANN / approximate nearest neighbor
- HNSW
- embedding ranking as runtime memory truth

Use exact CGA recall primitives only.

### No opaque fallback cognition
Do not add stochastic generation, hidden LLM fallback logic, or probabilistic substitutes inside the deterministic cognitive path.

### Teaching and mutation safety
Learning is controlled mutation.
- session memory may be local and immediate
- reviewed/durable memory goes through the teaching path
- pack mutation is proposal-only until reviewed
- identity override attempts are rejected, not learned

Do not invent a parallel learning path.

#### The learning boundary is typed, not "everything is proposal-only"
A common misreading treats *all* learning as proposal-only. That is a false bottleneck. The real boundary is between **durable** standing and **provisional** standing, and it is already mechanically enforced:
- **Durable mutation stays reviewed or proof-carrying.** Corpus / pack / policy / identity changes, and any promotion to COHERENT/verified standing, go through the reviewed teaching loop (`teaching/*`, proposal-only) or the proof-carrying promotion gate.
- **Provisional state may update autonomously — iff typed, isolated, replayable, and unable to masquerade as ratified truth.** This covers session memory, sealed practice ledgers, SPECULATIVE idle consolidation of soundly-derived facts, reliability-ledger counts, proposal emission, and disclosed licensed estimates. Each is written SPECULATIVE (never COHERENT), through the same `VaultStore.store` path (no parallel memory), deterministically, and carries its standing honestly.

This boundary is a set of failing-when-violated invariants, not a convention:
- **INV-21** — only allowlisted modules may call `VaultStore.store(...)`.
- **INV-22 / INV-23** — an unmarked pack row and an unmarked `store()` default to SPECULATIVE; COHERENT requires an explicit stamp.
- **INV-24** — every `vault.recall` callsite is categorized; user-facing evidence must pass `min_status=COHERENT`.
- **INV-29** — only `vault/store.py` may transition an `epistemic_status`.
- **INV-30** — the open-world `determine()` gear constructs only `Determined(answer=True)` or refuses; it can never assert `answer=False`. Closed-world entailed-negation must use a distinct closed-world type and entry point.

### Kernel substrate rule
New derivation work should consume `KernelFacts` / `ProblemFrame` where the substrate can represent the meaning.
Do not introduce new local prose parsers inside derivation organs unless explicitly marked as legacy exception with migration rationale.

## Working doctrine

Before editing:
1. Read this file.
2. Read `docs/specs/runtime_contracts.md`.
3. Check for any recent `session-break-summary-*.md` files (see top-level section above) and read the relevant one if present.
4. Confirm repo root and inspect working tree state.
5. Run the smallest relevant validation lane.

For non-trivial edits:
- trace imports and call sites first
- identify the invariant being protected
- prefer semantics-preserving cleanup before new mechanisms
- keep changes small and load-bearing
- If working in Arena/parallel subagent mode, each subagent must independently satisfy `versor_condition` and results must be reconciled before merge. No subagent output becomes another subagent's unchecked input.

## Reasoning and Problem-Solving Discipline

LLMs are not reliably intelligent by default. CORE exists partly to fix that.
Agents working in this repository must hold themselves to the following protocol
on every non-trivial task. Skipping steps produces confident-sounding work that
is wrong in load-bearing ways.

### The Protocol

**1. Read the code — never reason from names or structure alone.**
Before forming any opinion about a module, read its implementation. Trace its
imports and call sites. Identify what invariant it is protecting. A file named
`pass_manager.py` tells you nothing until you have read it.

**2. Find the shape — what underlying structure does this problem have?**
Before proposing a solution, identify the repeating structure the problem
expresses. The solution should make that structure visible, not paper over it.
Duplication is a symptom; the cause is an unnamed shape.

**3. Rank by leverage — genius-to-effort, not ease.**
When multiple improvements are possible, rank them explicitly by how much
cognitive/structural load they remove vs. how much effort they require. Implement
in that order. An agent that implements low-leverage changes first and skips
high-leverage ones has optimized for the wrong thing.

**4. Enumerate changes precisely — no ambiguity about what goes where.**
Before committing, state every change, which file it lives in, and why. The
commit message must reflect this. Vague commits ("refactor", "cleanup") are
not acceptable on load-bearing modules.

**5. Prove against real claims — not abstract correctness.**
"Tests pass" is not proof. Identify which specific pinned assertion in
`CLAIMS.md` the change must preserve or enable. State the SHA-256 lane or
`core test --suite` invocation that verifies it. If no existing lane covers
the change, say so explicitly — that is itself a finding.

**6. Connect to the cognitive model — what does this do for the system's reasoning?**
Every non-trivial change must be articulable in terms of what it does for
CORE's actual cognition path:
`listen → comprehend → recall → think → articulate → learn → replay`
If you cannot state what cognitive property the change strengthens, the change
is not yet understood well enough to ship.

**7. Commit with discipline — right branch, right invariant, right lane.**
Confirm repo state and branch before every commit. Never commit directly to
`main` unless the change is documentation or governance (like this one).
State which invariant the change protects. Run the smallest validation lane
that proves the change before declaring it done.

### The Failure Modes This Prevents

- Reasoning from file names instead of reading the code → wrong analysis
- Proposing solutions before finding the underlying shape → solutions that
  recreate the same problem in a different form
- Implementing easy changes first → high-leverage work never gets done
- Vague success criteria → regressions that pass "tests" but break real claims
- Shipping changes that can't be connected to the cognitive model → architectural
  drift away from CORE's mission

## Repository topology discipline
Before calling a directory, module, or file stale/redundant, classify its
intrinsic role:
- runtime boundary
- candidate/provisional compiler
- reviewed pack or corpus data
- read-only Workbench/API projection
- standalone demo envelope
- benchmark/eval/report artifact
- historical note or handoff
- script/tooling surface

Then verify with `rg` imports/callers, tests, docs/ADR references, and CLI
routes before moving or deleting anything. A file is not dead merely because it
is platform-specific, optional, generated-adjacent, or outside `core/`.

When an intentional split exists, make the boundary local and enforceable:
- add or update a short `README.md` at each side of the split;
- state what owns mutation, what is read-only, and which validation lane proves it;
- add or extend a lightweight hygiene/doctor/package test when drift is likely;
- keep artifact namespaces non-executable unless they are deliberately promoted
  to packages or moved under `scripts/`.

Package and CLI changes must check fresh-install visibility, not just source-tree
imports. Use `core doctor`, package include tests, and wheel inspection when a
new top-level package or CLI-imported module is added.

### Workspace Hygiene + Branch Protocol
Before branch movement or edits:
- Confirm cwd/repo root.
- Inspect dirty state (`git status`, `git diff`); classify loose files before stashing or deleting.
- Establish a clean current `main`.
- Prefer a fresh worktree from `origin/main` for non-trivial implementation.

### Git and Forgejo Setup
**CRITICAL**: This repository is hosted on a private **Forgejo** server, NOT GitHub. GitHub is deprecated for core work and CI testing.
Our sole remote and CI/CD platform is **core-gitquarters.acbcontent.org**.
- **DO NOT** use the `gh` (GitHub) CLI for normal work or PR management.
- **DO NOT** attempt to push, pull, or clone from `github.com` for developer/agent loops.
- **USE** the provided Forgejo MCP tools if available.
- **USE** the `tea` CLI (Gitea/Forgejo CLI) for issues, PRs, and repository management targeting `core-gitquarters.acbcontent.org`.

### Local-First CI Validation Protocol
To optimize server resources and bypass external CI billing dependencies, all agents and developers must run validation suites locally.
- **Pre-Push Gate:** Before pushing any branch to Forgejo, you **MUST** run the `smoke` test suite locally using:
  ```bash
  uv run core test --suite smoke -q
  ```
  Ensure all 108+ tests pass. Pushing broken code is a critical protocol violation.
- **Pre-Merge Gate:** Before proposing a merge or requesting a review on a PR, you **MUST** run the larger validation suite relevant to your changes (e.g. `uv run core test --suite cognition` or `uv run core test --suite algebra`).
- **PR Documentation:** When creating a PR on Forgejo (via `tea pr create`), document the local test execution in the PR description, matching this format:
  `[Verification]: Smoke suite passed locally (<run_duration>s, <test_count> passed)`

### CI/CD Runner Architecture (2026-07-16 doctrine)
**CRITICAL**: Do NOT attempt to run CI jobs on the central Forgejo server (`core-gitquarters`) — the `e2-micro` instance (1GB RAM) cannot handle test workflows without OOM thrashing. The server-side Act runner was deliberately removed on 2026-07-16.
- The `.github/workflows/*.yml` files are canonical and actively used; they install the **locked dependency universe** (`uv sync --locked` against the committed `uv.lock`) so lane pins can only move when code moves.
- CI jobs are dispatched to a **local Act runner on the primary developer's Mac** (registered label `ubuntu-latest:host`): jobs requesting `ubuntu-latest` run natively on the macOS host — the `ubuntu-latest` environment name is a fiction here; do not add Linux-only steps.
- **Availability tradeoff is intentional**: when the Mac is asleep or away, the CI queue simply waits. The real discipline is the pre-push local gates above. Do NOT "fix" a waiting queue by re-provisioning a runner on the GCP server, and do not modify server-side runner configuration.
- GitHub (`AssetOverflow/core`) is a **mirror only**; its Actions are billing-locked and produce dead signals — never chase them.

### Pre-Edit Sweep & Versor Coherence Guardian Protocol
Before modifying any module in `algebra/`, `field/`, `vault/`, or `generate/`:
- Trace every import of the target module and identify all callers.
- Check `calibration/` and `evals/` for tests that exercise the changed path.
- Explicitly confirm the core invariant `||F * reverse(F) - 1||_F < 1e-6` holds for the affected state.

## Documentation Discipline

ADRs, session docs, audit artifacts, and temporary session-break summaries stay as Markdown (GitHub-flavored). Plain-text artifacts are diffable, greppable, and readable by every agent in the dispatch pipeline.

Within Markdown, two GitHub-rendered features are sanctioned and otherwise sparingly used:
- Mermaid fenced blocks (` ```mermaid `) when a state machine, sequence, or dependency graph genuinely communicates more than prose. Inline, not in a sidecar file.
- `<details>` / `<summary>` collapsibles to fold long proofs, large tables, or generated logs without losing single-file context.

Out of scope:
- Standalone HTML artifacts with embedded CSS / inline SVG / sidebar navigation.
- Dashboards, status pages, or visualizers as a substitute for a pinned data artifact. If a visualization is load-bearing, the underlying data must live in a deterministic JSON/JSONL/Markdown artifact first.

## Validation lanes

Use the CLI lanes as the standard validation surface:

```bash
core test --suite smoke -q
core test --suite cognition -q
core test --suite teaching -q
core test --suite packs -q
core test --suite runtime -q
core test --suite algebra -q
core test --suite full -q
core eval cognition
```

Run the smallest relevant suite first.
Run broader suites before merge when the change touches runtime, algebra, cognition, teaching, packs, or trust boundaries.

## Security and trust boundaries

Any change touching user-controlled text, files, dynamic imports, pack loading, validators, logs, or report output must state its trust boundary.

Required defaults:
- explicit opt-in for arbitrary execution
- reject unsafe paths before filesystem access
- centralize safe display/log handling
- no hidden background execution
- no broad filesystem mutation without explicit boundary and tests

## PR checklist

Before merge, answer:

```text
What capability, performance property, or security boundary did this add or protect?
Which invariant proves the field remained valid?
Which validation lane proves the change?
Did this avoid hidden normalization, stochastic fallback, approximate recall, and unreviewed mutation?
If it touched user input, files, dynamic imports, or logs, what trust boundary was enforced?
```

## Provider-file policy

`CLAUDE.md`, `GEMINI.md`, and any future provider file must:
- be short
- stay under 600 bytes unless there is a tool-specific reason reviewed in `AGENTS.md`
- point here as canonical
- avoid duplicating architecture
- avoid introducing provider-only truth
- differ only where tool startup behavior genuinely requires it
