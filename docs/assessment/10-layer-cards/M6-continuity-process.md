# M6 — Continuity & Process

**Kind:** layer · **Parent:** CORE · **Assessor:** Opus 5 (Phase 2)
**Verified at:** `8927c563` (2026-07-27)
**Liveness:** `partial-wiring-debt` · **Fitness:** `strained` · **Topology role:** runtime boundary

> The life itself. M6 is the layer that makes CORE an organism rather than a function call: a process that persists across time, accumulates capability across reboots, and resumes as *the same life*. Every other layer describes a capability; M6 describes the subject that has them. The foundational telos — "one continuous life" — is this layer's charter, and its condition is the single sharpest measure of the distance between what CORE is for and what CORE is.

**Telos stages:** replay/determinism, backbone-runtime · hosts every other stage (the cycle's runner)
**Macro role:** Holds field, vault, session, and identity continuity over indefinite time; runs the heartbeat that lets the engine learn when nobody is talking to it.

---

> **Phase 3 correction (C-2, `05-phase3-findings.md`):** this card's "T1 vault and field excitation are discarded on exit by design" describes the **default config only**. The daemon forces `persist_session_state=True` (Shape B+ — "restored bit-exactly"), so residency machinery exists and is daemon-forced; open items are its exact coverage (`chat/runtime.py:893–952`) and horizon proof. The daemon's forced flag set is exactly `{persist_session_state, consolidate_determinations, strict_identity_continuity}` — see `20-component-cards/always-on-process.md`.

## ⚠️ Correction to Phase 0 Finding 0-C and to the system map

**Phase 0 recorded that the L11 always-on process is unbuilt. That is wrong, and the error is instructive.**

`chat/always_on.py::run_continuous` (279 lines) and `chat/always_on_daemon.py::run_daemon` (195 lines) exist and are reachable from the CLI as `core always-on` (`core/cli.py:244 cmd_always_on`). Both landed **2026-06-14** (`18e25580`, `efd280d4` / PR #758) — **five days after** the `.system-map/` snapshot of 2026-06-09 that declared "no forever entrypoint exists." Phase 0 inherited that claim without re-verification; Phase 2's re-verification obligation is exactly what caught it.

This is the clearest possible vindication of schema principle P3 (stamped verification) and of the taxonomy's rule that the map is a prior, never a source. It also means the assessment's own worst risk is real: **a 48-day-old map is wrong precisely where the project moved fastest.** Every card in Phases 2–3 must assume the map is stale on anything load-bearing.

What remains true from Phase 0: the **spike was never run to completion and never recorded**, and the built process is **ungated**. Those are the findings below, and they are different — and more actionable — than "unbuilt."

---

## What it is / What it does

M6 is two halves at very different maturity, joined by a checkpoint.

**The built half.** `engine_state/EngineStateStore` performs atomic checkpointing (same-dir temp → `fsync` → `os.replace`, mode-bits preserved) of the `RecognizerRegistry`, the `DiscoveryCandidate` working set, and a manifest, written at turn boundaries and reloaded on the next process start. A revision mismatch *warns and never refuses* — "reboot is recovery, not control flow." A `reboot_event` audit line records that a lifetime was lost and regained. On top of this sits `run_continuous`: an unbounded heartbeat loop where each beat advances `idle_tick` (continuous learning), records closure and learning evidence, self-checkpoints on real work, and checkpoints once at exit. `run_daemon` wraps it with a single-instance lock (one life per engine-state dir, lock file deliberately never unlinked), SIGINT/SIGTERM-wired `stop` checked before each beat and interrupting the inter-beat wait, and a load-time identity guard. A `lived_life.json` report feeds the Workbench's Lived Life surface.

**The unbuilt half — restated correctly.** Not the process: the *proof*, the *gate*, and the *residency*. The 24h+ no-drift soak has a complete falsifiable harness (`evals/l10_always_on`, four predicates H1 closure / H2 bounded-idle / H3 convergence / H4 reboot-resume, each with `*_holds` and `*_bites` test pairs, plus `evals/l10_continuity`) and **has never been run to a recorded artifact**. And per ADR-0146 the T1 vault and field excitation remain deliberately ephemeral, so what compounds across reboots is the recognizer/discovery layer — not the recalled or excited substrate.

---

## Contract

- **Inputs:** `DerivedRecognizer` objects, `DiscoveryCandidate` objects, `turn_count`, `CORE_ENGINE_STATE_DIR`, git short-revision, prior on-disk checkpoint.
- **Outputs:** `engine_state/{recognizers,discovery_candidates}.jsonl`, `manifest.json`, `lived_life.json`, buffered `reboot_event`, restored working set, advisory `RuntimeWarning` on revision mismatch.
- **Invariants:**
  - Atomic checkpoint — crash between write and replace leaves the prior checkpoint intact — pin: `tests/test_adr_0146_engine_state.py` — suite: **none** — status: **not run by any suite**.
  - Reboot round-trip byte-identity — state after (boot, N turns, reboot, reload) equals state after (boot, N turns) — pin: flagged by the system map as possibly *schema-as-decoration* — status: **unverified at this SHA**.
  - Versor closure under long-horizon idle (`VERSOR_CEILING`) — pin: `tests/test_l10_always_on_soak.py` — suite: **none** — status: **not run by any suite**.
  - One life per engine-state dir — pin: `tests/test_l10_always_on_daemon.py` — suite: **none**.

---

## Design vs build

- **Design:** `docs/adr/L10-runtime-model-scope.md` (scope only — process shape, state partitioning, reboot recovery, async HITL left open), ADR-0146 (Shape B hybrid checkpoint chosen over Shape A daemon / Shape C audit replay), ADR-0156/0157/0158, `L11-hitl-async-queue-scope.md`. **The design record is now behind the code**: ADR-0146 explicitly *rejected* the Shape A daemon, and a daemon was subsequently built. No ADR ratifies `always_on_daemon.py`. That is a governance gap, not merely a documentation lag.
- **Build:** `partial-wiring-debt`. Key files: `engine_state/__init__.py`, `chat/always_on.py`, `chat/always_on_daemon.py`, `core/cli.py::cmd_always_on`, `evals/l10_always_on/`, `evals/l10_continuity/`.
- **Evidence:**
  - Always-on loop and daemon exist and are CLI-reachable — code-read — `chat/always_on.py:179`, `core/cli.py:244` — would-fail-if-absent: **yes** (CLI command would not resolve).
  - Falsifiable soak harness with holds/bites predicate pairs exists — code-read — `evals/l10_always_on/predicates.py`, `tests/test_l10_always_on_soak.py` — would-fail-if-absent: **yes**.
  - Long-horizon no-drift result — **absent**. No JSON artifact under `evals/l10_always_on/` or `evals/l10_continuity/`. would-fail-if-absent: **n/a — the claim has no evidence**.
  - Suite enforcement — **absent**. No `l10`/`always_on` test appears in any of the 21 `TEST_SUITES` tuples. would-fail-if-absent: **no — nothing runs these pins**.
  - Persistence defaults — `persist_session_state=False`, `strict_identity_continuity=False` (`core/config.py:285,293`) — measurement — the continuity machinery is **off by default**.

---

## Capacity

- **Designed:** an indefinitely-running single process holding field + vault + session without drift, contemplating in slack, resuming as the same life through interruption.
- **Measured:** heartbeat loop runs for a bounded `heartbeats` count or until `stop`; checkpoint round-trip works at turn granularity; **no measured horizon exists** — the longest verified run is whatever the short soak tests exercise, and those run in no suite. The compounding surface is the recognizer/discovery layer only.
- **Ceilings:** T1 vault and field excitation are discarded on exit **by design** (ADR-0146), so recall and excitation substrate reset every process. Cross-reboot `EngineIdentity` verification is shelved. Async HITL-while-serving is still CLI-synchronous (W-009 open).

---

## Dependencies & provenance

- **feeds** → M4 (`ChatRuntime` is the sole consumer of the checkpoint store); **recalls-from** → M3 (recognizer registry) and M1/M5 (discovery candidates); **reads** → M1 (vault, deliberately ephemeral) and M0 (field, deliberately ephemeral); **verifies** → MV (round-trip byte-identity is a replay obligation); **depends-on** → MG (same-life identity continuity overlaps identity doctrine, not yet wired to the identity axes).
- **Owning ADRs:** ADR-0146, ADR-0156, ADR-0157, ADR-0158, ADR-0220 (identity/build-provenance split); scopes `L10-runtime-model-scope.md`, `L11-hitl-async-queue-scope.md`. **Unowned:** `chat/always_on_daemon.py`.

---

## Stage coverage

| Stage | Verdict | Evidence |
|---|---|---|
| backbone-runtime | **claimed-only** | Process exists and runs; no measured horizon, no suite-enforced pin, continuity flags default off |
| replay/determinism | **claimed-only** | Round-trip byte-identity invariant flagged as possible schema-as-decoration; unverified at this SHA |
| *(hosting the cycle)* | **covered, degraded** | `idle_tick` genuinely advances learning per beat; but what compounds is recognizers/discovery only — field and vault reset |

**Zone roster:** `L10-11-runtime-identity` (partial-wiring-debt → **revised: build materially more complete than mapped**), `engine-state` (live-internal, confirmed), `edge-sync` (inert, not re-verified), `core-protocol-ctp` (spike, not re-verified).

**Rollup note:** zone liveness is a weakest-link rollup and is not a completion rate. M6 is better built than either the map or Phase 0 reported, and *less proven* than the existence of the code suggests. Those are not in tension — they are the layer's actual condition.

---

## Judgment

**Fitness: `strained`.** Not `wrong-solution`: Shape B checkpointing is a sound mechanism, and the daemon built on top of it is a reasonable shape. Strained because the layer's *proof obligations* have not kept pace with its *code*, and because its central design document still rejects the architecture that was subsequently built. A layer whose invariants are pinned by tests that no suite runs is protected by nothing.

**Honest wrinkles:**
- The most telos-critical component in CORE is enforced by **zero running tests**. Every `l10`/`always_on` pin sits outside all 21 suites. By the project's own doctrine (a pin in no suite never runs), the continuous life is unguarded.
- **`DriveGradientMap` is constructed and never read.** `chat/runtime.py:716` builds `self._drive_map`; no site reads it. Deleting it would change no output. This is textbook decoration and is recorded here rather than fixed.
- `ExertionMeter` *is* exercised (`record` at :2912, `fatigue` at :2913) but its output flows only to `drive_summaries` and `fatigue_index` — telemetry. Fatigue **gates no decision**. It is live-internal, not load-bearing.
- The daemon has no ratifying ADR while the governing ADR-0146 explicitly rejected the daemon shape. Whatever the right answer, the record currently contradicts the code.
- "One continuous life" remains, in substance, *many short lives sharing a recognizer checkpoint* — but the reason is now a **deliberate ADR-0146 scoping decision** about vault/field ephemerality, not an absence of process machinery. That reframes the L10 question entirely: it is no longer "build the process" but "decide what the process is allowed to hold."

**Open questions:**
- Run the long-horizon soak and record the artifact — what horizon does the engine actually survive? (→ ruling: this is the ADR-0146 Phase-4 spike, still owed)
- Should `l10`/`always_on` pins enter a suite, and which? (→ Phase 4)
- Does the daemon need a ratifying ADR that supersedes ADR-0146's Shape-A rejection? (→ ruling)
- Is vault/field ephemerality still the right call now that a real process exists to hold them? (→ ruling; this is the highest-value M6 question)
