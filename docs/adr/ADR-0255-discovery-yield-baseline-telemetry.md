# ADR-0255: Discovery-Yield-Per-Served-Turn Baseline Telemetry

**Status:** Accepted (directive + framing ruled by Joshua Shay, 2026-07-23)
**Date:** 2026-07-23
**Deciders:** Joshua Shay (ruling authority) + Claude (implementation)
**Companion docs:** [`docs/analysis/weekly-audit-2026-07-22-stragglers-todo.md`](../analysis/weekly-audit-2026-07-22-stragglers-todo.md) (T11), [`scripts/ops/reset_candidate_corpus_t11_20260722.py`](../../scripts/ops/reset_candidate_corpus_t11_20260722.py), [`docs/adr/ADR-0219-generation-dir-atomic-checkpoint.md`](ADR-0219-generation-dir-atomic-checkpoint.md)

---

## 1. Context

The T11 weekly-audit ruling (2026-07-22) wiped the live discovery-candidate ledger from 465 provenance-tainted records to 0, via the `engine_state` ADR-0219 atomic-generation API. It deliberately left `turn_count` (14990) unchanged — resetting a scalar that tracks real historical served turns would be fabrication, not cleanup.

That leaves no way to measure how fast the candidate corpus repopulates: `turn_count` is a monotonic counter spanning the ledger's entire pre-reset history, while the candidate ledger itself is now clean. Any yield metric computed as `candidates / turn_count` would silently blend pre-reset and post-reset traffic.

The follow-up directive (2026-07-23) asked for a `discovery-yield-per-served-turn` metric, explicitly scoped: **"candidates proposed per served turn on clean, post-reset traffic."** CORE has no always-on background PROCESS yet (`[[project-core-is-one-continuous-life]]`), so "per served turn" can only mean per user-invoked turn — there is no live/background rate to measure until that process exists. This ADR does not build that process; it measures the organic yield of the current (proposal-only, config-gated) discovery mechanism, which is itself a prerequisite for designing that process's metabolic loop.

## 2. Decision

Add one additive-optional manifest field, `turn_count_baseline`, and one pure computation function, `teaching.discovery_yield.compute_discovery_yield`.

- **`turn_count_baseline`** (`engine_state/__init__.py::save_manifest`) — the `turn_count` value at the moment the candidate ledger was last reset to empty. Written through the same atomic generation-dir commit as every other manifest field (no raw file writes). Does **not** bump `schema_version` — same additive-optional discipline as `engine_identity`/`parent_engine_identity`.
- **`compute_discovery_yield(store)`** — reads the live manifest and candidate ledger, returns:
  - `served_turns_since_reset = turn_count - turn_count_baseline`
  - `candidates_since_reset = len(candidates)`
  - `yield_rate = candidates_since_reset / served_turns_since_reset` (or `None` when `served_turns_since_reset == 0`, never a `ZeroDivisionError`)
- **Fail-closed on no baseline**: if `turn_count_baseline` is absent from the manifest, `compute_discovery_yield` returns `None`. It never coerces the missing baseline to `0` or to the current `turn_count` — either would fabricate a denominator against an epoch nobody marked. Absolute Provenance: no metric is better than an invented one.
- **`scripts/ops/stamp_discovery_yield_baseline_20260723.py`** — the one-off script that stamps the baseline into the live store post-T11, mirroring the T11 reset script's atomic begin/commit pattern and idempotent guard (refuses to run if a baseline is already stamped).
- **`core teaching discovery-yield [--json]`** — read-only CLI surface (`core/cli_teaching.py`), same shape as `core teaching coverage`: human-readable by default, `--json` for machine consumption. Exits 1 with a clear stderr message when no baseline is stamped.

## 3. Non-goals

- **Not a live/background rate.** The metric is computed on demand from committed state; it does not run on a clock or a daemon. Building that is a separate, later arc (`[[project-core-is-one-continuous-life]]` Phase 2) and this ADR takes no position on its design beyond noting that this organic yield number is a prerequisite input to it.
- **Not a new telemetry sink.** This does not wire into `chat/telemetry.py`'s `TurnEventSink`/`DiscoveryCandidateSink` JSONL-stream pattern — the metric is a point-in-time snapshot of already-persisted state, not a per-event stream. If a continuous time-series becomes useful later, it can read this same computation at each checkpoint; that is a follow-up, not scope creep here.
- **Does not touch serving physics.** Nothing here reads or writes anything on the `resolve_surface` / pipeline path. Pure read of `engine_state`, pure write of one additive manifest field.

## 4. Consequences

- The live store now carries a `turn_count_baseline` (stamped once, 2026-07-23, at `turn_count=14990` — the same value T11 left it at, since no live-store turns had been served between the T11 reset and this stamp).
- Every served turn from here on advances `turn_count` past the baseline; `core teaching discovery-yield` gives a deterministic, reproducible answer to "how many candidates has the discovery mechanism proposed per served turn since the corpus went clean."
- A manifest written before this directive, or by any caller that never resets the ledger, has no baseline and the CLI/function both fail closed rather than guess.

## 5. Validation

- **Unit (RED→GREEN):** `tests/test_discovery_yield.py` — baseline-absent fail-closed (+ `_bites` mutation), delta computation (+ `_bites`), yield-rate division (+ `_bites`), zero-served-turns → `None` rate not `ZeroDivisionError` (+ `_bites`), `as_dict()` JSON-safety, and CLI-level tests (`core.cli.main`) for the fail-closed exit code and `--json` output.
- **Dry run:** the stamping script was exercised against a throwaway copy of the live store's `gen-21703` before touching the real one — confirmed the idempotent guard aborts a second run and the committed manifest carries `turn_count_baseline=14990` with identity/candidates preserved byte-faithfully.
- **Regression:** smoke + warmed_session lane pin green pre-push (see PR `[Verification]`).
