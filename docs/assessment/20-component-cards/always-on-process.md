# always-on-process — `chat/always_on.py`, `chat/always_on_daemon.py`, `engine_state/`, `evals/l10_*`

**Kind:** component (M6's built half) · **Parent:** M6 · **Assessor:** Fable 5 (Phase 3)
**Re-verified:** `39331dbc` (2026-07-28) — see the arc note below.
**Verified at:** `8927c563` (2026-07-27)
**Liveness:** `live-internal` (CLI-reachable, suite-orphaned) · **Fitness:** `strained` (proof debt, not design debt) · **Topology role:** runtime boundary


**Arc note — 2026-07-28 (`39331dbc`).** PR-9 (H-11) made the accrual backstop visible: `_accrue_in_turn`'s broad guard stays — accrual is additive and must never crash a turn — but a swallowed exception is now counted and named instead of writing the same `None` a quiet turn writes. `_last_turn_accrual` is unchanged on failure, so consumer behavior is byte-identical by construction.

> The process that runs the continuous-life heartbeat. Its design center is a single sentence from the daemon module: a restart is *the same life or it stops — never a silent fork*.

## What it is / What it does

`run_continuous(runtime, heartbeats, …)` — each beat advances `idle_tick` (continuous learning), records closure + learning evidence, self-checkpoints on real work, checkpoints once at exit; `heartbeats=None` runs unbounded until `stop`, which is checked before each beat *and* interrupts the inter-beat wait. `run_daemon` wraps it with a single-instance `fcntl.flock` lock — kernel-released on process death, so no stale-lock window and no PID-reuse ambiguity; the lock file is deliberately never unlinked (unlinking would let a peer flock a different inode). `lived_life.json` feeds the Workbench Lived Life surface. Landed 2026-06-14 (`18e25580`, `efd280d4`).

**The forced flag set (exact, from `CONTINUOUS_LIFE_CONFIG_FLAGS`):**

```python
{"persist_session_state": True,      # Shape B+ — persist the lived session across reboot
 "consolidate_determinations": True, # Step D — learn from determined facts each beat
 "strict_identity_continuity": True} # load-time identity guard — same life or refuse
```

## Correction to the Phase 2 M6 card (Shape B+)

The M6 layer card carried forward "T1 vault and field excitation are discarded on exit **by design** (ADR-0146)." That is the **default-config** posture only. Under the daemon, `persist_session_state=True` activates Shape B+ persistence — `chat/always_on.py:9`: the lived state is "restored bit-exactly" — with opt-in persistence sites in `chat/runtime.py:893–952`. So the residency question the M6 card called "the highest-value M6 question" (*should the process hold vault/field?*) is already partially answered in code: **the mechanism exists, is opt-in, and is daemon-forced.** What remains open is exactly what Shape B+ covers (session context vs full T1 vault vs field excitation — the persistence sites need a Phase-4 read) and whether it is *proven* at horizon.

## What the soak would prove if run (`evals/l10_always_on`)

- **H1 closure** — every observed idle beat is a valid versor, with an explicit vacuity guard: a run where the field never existed cannot pass "by saying nothing."
- **H2 bounded idle** — a no-work idle beat adds nothing to the vault (no idle resource leak); flagged consolidation writes are exempt.
- **H3 convergence** — a saturated idle life *settles and stays settled*, with a `min_converged_tail` so "settled" is observed, not assumed.
- **H4 reboot-resume** — a mid-soak reboot resumes the SAME life; post-reboot closure holds on every segment.

Each predicate has `*_holds` and `*_bites` test pairs (mutated evidence must fail). This is exemplary falsification design. **No recorded artifact exists; no suite runs any of it** — the long horizon is `python -m evals.l10_always_on`'s job, per its own docstring "run on demand / nightly," and no nightly exists.

## Judgment

**Fitness: `strained` — proof debt on a sound design.** The lock discipline, the never-silent-fork rule, the vacuity-guarded predicates, and the bites-pairs are all careful work. What is missing is entirely evidentiary: a recorded soak artifact, a scheduled runner, and an ADR that owns the daemon (ADR-0146 rejected Shape A; the daemon is unowned by any ratifying decision).

**Honest wrinkles:**
- The flag set forces the *consolidator* on but not the *accruer* (`accrue_realized_knowledge` absent) — see the determine-phase card: the continuous life may be consolidating an empty set. Unresolved.
- `strict_identity_continuity=True` under the daemon vs `False` default means identity-continuity refusal behavior differs between the daemon and every other entrypoint — correct by design, but nowhere stated outside the flag dict.
- The soak evals' own docstring designates a nightly cadence that has never been provisioned. Given the local-first CI doctrine (Mac runner, queue waits while asleep), a nightly soak is architecturally awkward — which may be *why* it never ran. That tension deserves a ruling, not silence.

**Open questions:** run the soak, record the artifact (→ the still-owed ADR-0146 Phase-4 spike); which suite owns `l10`/`always_on` pins (→ Phase 4); daemon's ratifying ADR (→ ruling); exact Shape B+ coverage (→ Phase 4 read of `runtime.py:893–952`).
