# `public_demo` Lane Drift — Root-Caused, Re-Pinned

**Tier S2** (generalization-arc-2026-07-24 §6). Corrects a standing
mischaracterization: `docs/research/lane-drift-investigation-2026-07-24.md`
(the Phase-0.1 investigation this arc opened with) treated `public_demo` as
"not one of the three" drifted lanes, unchanged, its failures explained by
"the known env-timeout flake." That framing is only half right — a
**different, real** flake exists (§4), but the specific drift measured this
session is deterministic content drift with a two-day window of genuine
regression, exactly the class of thing the original investigation found for
`demo_composition`. It was never investigated because every red
`public_demo` in the lane-shas job was reflexively attributed to the flake.

## 1. Method

`scripts/verify_lane_shas.py --update` is never used to diagnose drift (it
rewrites every lane and silently drops erroring lanes' pins — the standing
rule three arcs now depend on). Instead: disposable `git worktree`s at six
specific commits, each with its own `uv sync --locked` venv, running
`evals/public_demo/runner.py` directly and reading its printed `sha256` —
the same measurement `verify_lane_shas.py` performs, isolated to one lane
so six historical points could be checked without six full-suite runs.

## 2. Measured timeline

| commit | date | change | `public_demo` sha256 | `all_claims_supported` |
|---|---|---|---|---|
| `4b9dbe72` (= `e7d116c9~1`) | pre-2026-07-20 | (pin's origin state) | `7d8ba0db…` **(= stale pin)** | true |
| `e7d116c9` | 2026-07-20 | Cl(4,1) geometric sovereignty convergence — widened `compute_trace_hash` (Phase-B graph-topology inclusion), same commit the ORIGINAL investigation found for `demo_composition`'s drift | `3434f255…` | true |
| `e0d1b475` | 2026-07-20 | #96 fail-closed linguistic governance — introduced the register-axis regression (`_base_runtime_surface` canonical-first) | `228f5287…` | true |
| `5a343b49` | 2026-07-22 | T13 "fix" — back-stamped the REGRESSED surface onto `TurnEvent`, making telemetry consistent with the wrong bytes | `31d9db30…` | **false** |
| `5224b5e0` | 2026-07-24 | (PR #110's base — Band v4-CM merge; regression still present) | `c6596e11…` **(matches BRIEF-S's "register-axis-reverted" baseline exactly)** | **false** |
| `f95ac26e` (→ current `main`) | 2026-07-24 | PR #110's fix — restored response-first surface precedence | `da7fad65…` **(= today, re-pinned below)** | true |

Each row measured once except `4b9dbe72`/`e7d116c9`/current-`main`, which
independently reproduce values already stated in this session's prior
work — three independent confirmations, not a single sample.

## 3. Two findings, not one

### 3.1 Benign digest drift (`7d8ba0db…` → `228f5287…`)

`e7d116c9` (trace-hash format widening) and `e0d1b475` (register-axis
regression's *introduction*) both changed `public_demo`'s content-derived
digest while `all_claims_supported` stayed **true**. This half matches the
original investigation's framing for `demo_composition`: intentional or at
least non-breaking content change, stale pin, no functional loss.

### 3.2 A real, two-day regression window (`5a343b49` → `f95ac26e`)

Starting at `5a343b49` (2026-07-22, the T13 back-stamp), `public_demo`'s own
`all_claims_supported` case **fails** — not a digest mismatch, an actual
`passed: 3/4` with `FAIL all_claims_supported`. It stays failing through
`5224b5e0` (2026-07-24, PR #110's base) and is fixed only as a side effect
of `f95ac26e` (PR #110's register-axis restoration, aimed at
`demo_composition`'s register tour, not `public_demo` specifically — see
[[project-register-axis-serving-regression]]). **`public_demo` embeds a
register-tour-sensitive scene** (`core/demos/showcase.py` imports
`RegisterTourDemo` from `core.demos.tour_adapters`, the same adapter
`demo_composition` uses), so it broke and healed on exactly the same
mechanism, in parallel, unnoticed.

For roughly two days of active development (Band v2-EN's Phase 1 spine,
the coherence hedge-arm commit, PRs #107–#109), `public_demo` was
genuinely red on every commit in that window. Per the original
investigation's own §"why no gate caught it" for `demo_composition`: *"the
lane-shas CI job is the only gate that runs the demo lanes, and its
failures were conflated with the known `public_demo` env flake."* This is
the same masking, on the fourth lane, undiagnosed until now.

## 4. The 2026-05-31 env-timeout flake is a SEPARATE, still-real thing

`feedback-env-core-rs-build-and-public-demo-flake` (memory, 2026-05-31)
documents a genuine wall-clock budget overrun:
`DemoContractError: showcase exceeded ADR-0099 runtime budget: ~46-48s >
30000 ms`, reproduced identically on clean `main`, unrelated to content.
That failure mode is real and this document does not retract it — it is a
different assertion (`runtime_under_budget`, and only under
`CORE_SHOWCASE_HARD_BUDGET=1`; the soft path measured throughout this
session never hard-fails on wall-clock) from the one this document
root-causes (`all_claims_supported`, a content assertion). **The error was
conflating two distinct failure modes under one label** — any future red
`public_demo` should be triaged by WHICH case failed
(`all_claims_supported` vs `runtime_under_budget` vs
`determinism_run_to_run_byte_equality` vs `pure_composition_no_new_mechanism`),
never assumed to be either flake without reading the failing case id.

## 5. Fix (this branch)

- `scripts/verify_lane_shas.py`: `public_demo` pin
  `7d8ba0dbae9287cf…` → `da7fad654e77aac4…` (single-line, surgical — the
  standing rule, not `--update`).
- `evals/public_demo/results/v1_dev.json` regenerated (the committed report
  the pin is computed from).
- `CLAIMS.md` regenerated (`scripts/generate_claims.py`, one-line diff —
  the `ADR-0099` row's sha256).
- Current `main` (`5fd9a861`) is 4/4 passing, `da7fad65…`, verified stable
  across three independent measurement points in this document.

## 6. Follow-up recorded, not actioned here

Per the original investigation's own follow-up list: *"document the
lane-shas CI expectation that a red lane job is triaged per-lane, never
assumed to be the public_demo flake"* — §4 above is that documentation.
No CI wiring change is proposed; this is a pin correction plus a corrected
record.

Relates to [[project-register-axis-serving-regression]],
[[project-generalization-arc]],
`docs/research/lane-drift-investigation-2026-07-24.md`.
