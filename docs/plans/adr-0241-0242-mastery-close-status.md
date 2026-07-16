# ADR-0241 / ADR-0242 Mastery-Close: Plan & Outcome

**Status:** CLOSED — both ADRs Accepted (ratified by Joshua Shay, 2026-07-15). This document is the durable, versioned status surface for the arc; it consolidates the original plan with what actually happened, phase by phase, including the parts that ran past the plan's original scope.

**Why this file exists:** the operational W0–W5 plan that drove this arc (`docs/plans/adr-0241-0242-mastery-close.md` in the authoring session's Claude Code plan store) was never committed — it lived only as a gitignored `.claude/plan/` artifact in a since-orphaned worktree. This doc is the fix: the plan-to-outcome record now lives in the repo, not in an assistant's session memory.

**Related, already-committed artifacts** (unchanged by this doc, cross-referenced below):
- `docs/plans/adr-0241-cohesion-mastery-plan-p0-p12.md` — Plan A (P0–P12), archived point-in-time
- `docs/plans/adr-0242-drive-complete-plan-d0-d10.md` — Plan B (D0–D10), archived point-in-time
- `docs/plans/adr-0241-0242-session-completion-summary-2026-07-15.md` — the 2026-07-15 completion summary
- `docs/audit/adr-0241-0242-acceptance-packet-2026-07-15.md` — the D10 acceptance packet + §8 ruling record
- `docs/audit/adr_0241_cohesion_acceptance_checklist.md` — per-box acceptance evidence
- `docs/adr/ADR-0241-wave-field-driven-hyperbolic-atlas-and-resonant-cognition.md`, `docs/adr/ADR-0242-atlas-packing-and-fibonacci.md` — both now **Accepted**

---

## Original goal (as authored 2026-07-15)

Complete the wave-field substrate program (ADR-0241/0242 + core_ha deprecation + Fibonacci vectors) to the mastery bar: merged green without shortcuts, adversarially verified, acceptance package ready for Joshua.

---

## Phase-by-phase: plan vs. outcome

### W0 — Unblock #38 ✅ COMPLETE
**Plan:** diagnose whether the lane-shas CI failure on PR #38 was a per-lane timeout or a genuine SHA mismatch; fix forward without re-pinning unless mismatch was proven.
**Outcome:** root cause was resource starvation on the (since-retired) Act host, not a timeout or a SHA mismatch — pins were byte-identical 9/9 locally. No re-pin occurred. A debug line that had leaked into the tip commit (`print(f"DEBUG ENV: {dict(os.environ)}")` in `evals/public_demo/runner.py:131`, a live secret-exposure vector under any CI that logs env) was caught and reverted (`4853a55c`) before merge, as the plan's W3 gate required.
**PR:** #38 (`9e1455b9`), #39 (`b80f262f`).

### W1 — Adversarial verification pass ✅ COMPLETE
**Plan:** five cross-authorship attacks against P8 chiral non-vacuity, quarantine transitivity, Fibonacci cert digest/budget exactness, P9 seal discipline, and the fidelity ledger — each attack executed by an operator who did not author the code under attack.
**Outcome:** all five reads executed (not read-only — attacks were run, not just reasoned about). Confirmed solid: chiral charge genuinely non-vacuous and conserved (Q=−2.5), Fibonacci cert budget-exact and digest-stable. **Caught a live, real defect**: `core/physics/__init__.py` eagerly loaded 5 Tier-2 (off-serving) modules into `chat.runtime` via its barrel import — a genuine A-04 transitive serve breach, not a false alarm. Fixed via PEP 562 lazy exports + a new process-level guard test (`tests/test_serve_quarantine_transitive.py`).
**PR:** #40 (`54228d45`).

### W2 — Commit the session artifacts ✅ COMPLETE
**Plan:** copy Grok's three plan/summary docs from an ephemeral worktree into `docs/plans/` so they survive worktree cleanup.
**Outcome:** done as specified; all three files present on `main` today (see "Related artifacts" above).
**PR:** #40 (bundled with W1).

### W3 — Merge + cleanup ✅ COMPLETE (original scope)
**Plan:** merge #38 with explicit authorization, delete arc branches/worktrees, confirm post-merge main is green.
**Outcome:** done. **Naming note:** the label "W3" was later reused for an unrelated, later phase — PR #46 ("isolate xdist polluters blocking `-n auto` default (W3)") is a *different* W3, part of the post-ratification hardening pass below, not this merge-and-cleanup gate. Treat them as distinct; the collision is cosmetic, not a scope conflict.
**PR:** #38, #39, #40.

### W4 — D10 acceptance package ✅ COMPLETE
**Plan:** one-page packet for Joshua — acceptance checklist walkthrough, fidelity ledger state, W1 findings, explicit deviations for ruling (P7 polar demotion, sensorium staged packets, progressive continuous-field integrals), R&D-memo caveats already filtered by implementation.
**Outcome:** packet written (`docs/audit/adr-0241-0242-acceptance-packet-2026-07-15.md`), including a §7 memo-slice addendum (impl-stronger-than-memo table) added after independent verification via the Google Drive connector against the private authority docs. **Joshua ruled "Ratify"** — both ADRs flipped to Accepted with a full ruling record (§8) and provenance-guarded governance test (`tests/test_adr_0241_governance_p12.py`).
**PR:** #41 (chiral sign-gate + packet), #42 (CRDT-vs-bit-exact dossier — one of the ruling's explicit deviations), #43 (ratification: status flip + memo-slice closure + core_ha Path-B correction).

### W5 — Post-Accept backlog — **PARTIALLY SUPERSEDED, see below**
**Plan (as originally written):** D9 Rust f64 parity; runner capacity (second Act runner / larger VM, later superseded by a GitHub-Actions-mirror idea); sensorium real compilers; V2 energy promotion (Fibonacci vs dyadic vs log, benchmark-gated); progressive continuous field.
**Outcome:** none of the W5 items above have been started. Instead, the CI-infra item under-forecast how bad the CI situation would get — see "Unplanned: CI collapse and local-first pivot" below, which consumed the entire post-ratification session. The five W5 items are **still the real backlog**, now joined by items surfaced during the CI pivot (below).

---

## Unplanned: post-ratification hardening + CI collapse and local-first pivot

This work was not anticipated by the original plan (W5 assumed a GitHub-Actions-mirror fix for CI capacity; what actually happened was messier and is worth recording honestly).

**Post-ratification test/governance hardening:**
- #45 (`8f67590d`) — cleared pre-existing full-suite reds; confirmed the "~31 pre-existing red tests" figure was stale (retired).
- #46 (`b0156406`) — isolated `-n auto` xdist polluters (the *second* "W3", unrelated to the merge-gate W3 above).
- #47 (`56e55e6e`) — evolved the anti-self-Accept governance guard (`P12`) for the post-ratification state; the guard correctly went red against the ratification itself and had to be updated to check *provenance* (ratified-by-whom) rather than merely "not yet Accepted."

**CI collapse:**
GitHub Actions became billing-locked (~$6, account-level) mid-arc, forcing a pivot away from the "GitHub-Actions-mirror" idea W5.2 had assumed would supersede the Act-runner ceiling. That idea is now dead; the actual fix was:
- #48 (`9d284d95`) — locked dependency installs (`uv sync --locked`) to stop lane-pin thrash from PyPI drift. Initial version was not self-validating: `uv.lock` was gitignored (existence ≠ tracked), so every locked CI run failed "Unable to find lockfile" until the lockfile itself was committed.
- #49 (`a7279a54`) — ADR-0242 §5 carry-seam items: κ-cert telemetry event + F5–F7 cross-band discovery gate (Tier-2, off-serving).
- CI doctrine rewrite: local-first validation is now the real gate (`uv run core test --suite smoke -q` in the worktree before every push, `[Verification]:` tag in PR descriptions), with a local Mac Act runner (`ubuntu-latest:host`) as secondary/observability CI, replacing the GCP e2-micro runner entirely (that box cannot survive an Actions job — 1GB RAM, OOM class). Doctrine landed in `AGENTS.md` §CI/CD Runner Architecture + a pointer in this repo's `CLAUDE.md`, plus the global `~/.claude/CLAUDE.md`.
- #50 (`31073d55`) — lane-shas streaming progress + configurable timeout, so a hang is visible in the log the moment it happens instead of being silently truncated (same class of failure that caused the original W0 diagnosis to take real forensic work).
- #51 (`207d9c6a`) — this CI doctrine committed to the repo (`AGENTS.md`, `CLAUDE.md`) — also the new Mac runner's first live dispatch test.
- #52 (`18d3c70d`) — assessment note on a rejected parallel-session re-implementation submission (its "three critical bugs" claim did not survive verification; one had a literal Python syntax error).

**Open technical note, not yet actioned:** job logs pulled during #50/#51's CI triage show the Act runner still spinning up Docker containers (`docker pull node:20-bookworm`) rather than the native "no Docker" host execution the `ubuntu-latest:host` label's doctrine describes. Worth checking whenever CI infra is revisited; not currently blocking anything since local-first is the actual gate.

---

## Current state (2026-07-16)

- Both ADRs: **Accepted**, ratified, full audit trail.
- `main` @ `18d3c70d`. Zero open PRs. Arc branches and worktrees deleted.
- CI: local-first is the real gate; `uv.lock` committed and locked installs enforced in all workflows; local Mac Act runner is live and has completed its first dispatch tests (#51, #52).

## Remaining backlog (none are completion blockers)

1. **D9** — Rust f64 GP parity, only if the UMA path must match f64 wave residuals; freeze the Python parity suite first.
2. **Sensorium real compilers** — replace staged packets, closes I-04 feed fully.
3. **V2 energy promotion** — Fibonacci vs. dyadic vs. log under fixed replay, benchmark-gated, explicit Joshua gate required before promotion.
4. **Progressive continuous field** — research track, non-blocking.
5. **Runner Docker-vs-host discrepancy** — confirm whether `ubuntu-latest:host` jobs should truly run without Docker, and if so why the observed runs used containers.
6. **`-n auto` fast-lane default flip** — pending, xdist polluters now isolated (#46) so this is unblocked whenever it's prioritized.
7. **INV-21 allowlist dedup** — minor housekeeping surfaced during the xdist isolation work.
