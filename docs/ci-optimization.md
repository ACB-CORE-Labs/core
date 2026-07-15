# CI optimization — runner bottleneck and lane policy

Companion to [testing-lanes.md](./testing-lanes.md) (SSoT for markers and
workflow → lane mapping). This note records **why** the multi-lane CI split
exists and what capacity still limits PR queue time.

## The bottleneck

A single self-hosted Act runner (≈2 vCPU / limited RAM) serializes all workflows
that target `ubuntu-latest` for this repo. When post-merge CI ran the **full**
non-quarantine suite (`-m "not quarantine"`) with `-n 2`, the slow registry
dominated wall-clock:

- Module fixture floor: `test_inner_loop_phase2` ≈16 min setup alone
- ~912 tests classified `slow` in `conftest.py` (including the register matrix)
- Thrashing under oversubscription can stretch the job toward **1–2 hours**

While that job holds the runner, PR gates (`smoke`, `lane-shas`) sit in
**Waiting**. That is a queue problem first, a test-count problem second.

## What we changed (in-repo)

| Change | Effect |
|---|---|
| `full-pytest.yml` → fast marker | Main push runs `not quarantine and not slow`; frees the runner much sooner after merge |
| `nightly-full-pytest.yml` | Full suite (`not quarantine`) daily at 02:00 UTC + `workflow_dispatch`; timeout 120 min |
| `lane-shas.yml` job-level path skip | PR pin verify runs only when pin-relevant paths change; job still green when skipped (no required-check hang) |
| Contract comments | `smoke.yml`, `conftest.py`, `testing-lanes.md` match the real PR / main / nightly split |

Workflow **id** `full-pytest` is kept on purpose so Forgejo history / required-check
names do not break; the job display name is `fast pytest (...)`.

## What is out of band (ops, not git)

Host cgroup limits, hung-container cleanup, and adding a second runner are
**VM/ops** actions. They are not encoded in this repository. Document them in
ops runbooks when you change the host; do not treat this file as a substitute.

## Expected feedback loop after this change

| Stage | Typical hold |
|---|---|
| Local | Targeted tests; `make test-fast` before push |
| PR | `smoke` (+ `lane-shas` when pin-relevant paths change) |
| Main | Fast `full-pytest` + always-on `lane-shas` |
| Nightly | Full soak including slow registry |

This is roughly **hours of runner hold after merge → tens of minutes** on the
fast lane for the same host class — not infinite parallel capacity. Multiple
open PRs still queue on one runner.

## Capacity still required

1. **Second Act runner or larger VM** — only real fix for concurrent PR + main
   execution.
2. **xdist hermeticity** — see follow-ups in `testing-lanes.md` before raising
   `-n` further.
3. **Warm-runtime fixture** — long tail of `ChatRuntime` construction in the
   fast lane.
4. **Nightly failure signal** — wire Forgejo notification / issue on red
   `nightly-full-pytest` so ≤24h slow-break debt is not silent.
5. **Optional path-triggered slow job** — if main must catch soak breaks same-day
   without nightly wait, add a non-blocking or path-filtered slow workflow later.

## Validation

```bash
# Local parity with main CI
make test-fast

# Local parity with nightly
make test-full

# Lane pins (same as lane-shas job body)
uv run python scripts/verify_lane_shas.py
uv run python scripts/generate_claims.py --check
```
