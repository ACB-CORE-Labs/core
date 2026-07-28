# L10 Always-On Heartbeat Soak — Contract

**Status:** soak (falsifiable long-horizon gate) · **Not in default smoke** (run on demand / nightly).

The continuity lane (`evals/l10_continuity`) soaks the **turn loop**. This lane soaks the
**idle heartbeat** (`chat/always_on.run_continuous` — the loop the `core always-on` daemon
drives). It seeds a real continuous life (a held self + a cognitive turn to excite the
field), then runs the engine over N beats with **no user turn**, and evaluates falsifiable
predicates over the per-beat evidence. It converts the claim *"the always-on process is
built"* into *"the always-on process holds over uptime"* — the idle-path claims that the
short daemon unit tests (≤5 beats) and the turn-loop soak (disjoint from `run_continuous`)
do **not** prove at horizon.

Run: `PYTHONPATH=. .venv/bin/python -m evals.l10_always_on [n_beats] [reboot_beat]`
(pass a large `n_beats` — e.g. `100000` — for a true long-horizon soak; default `24`).

## The stance on "now" (R-2, ruled B — recorded here *before* the re-run, deliberately)

A continuous life experiences sequence and duration; determinism bans clocks from cognition.
Both commitments are correct, and their intersection was undesigned — which meant this lane's
central claim, *"holds over indefinite uptime,"* could not be stated precisely. It is stated
here, before the soak runs, so that the soak measures a decided question rather than deciding
one by accident.

**Beats are the unit of cognitive time.** "Now" is the current beat index; "before" is a lower
index; "how long" is a beat count. No cognitive path reads a wall clock, and the H1–H4
predicates are defined over beat indices alone. The Fibonacci recency schedule (τ_n,
ADR-0242) is a constants schedule, not a clock; `turn_count` and idle ticks are ordinals, not
durations.

**R-2 was ruled B** — *beats govern cognition; a wall-clock stamp is permitted in telemetry
only, never read by any cognitive path.* Measured at 2026-07-28, **this lane carries no
wall-clock at all**, in cognition or telemetry: `runner.py`, `predicates.py` and `report.py`
contain no `time`, `datetime`, or timestamp of any kind. That is stronger than B requires, and
it is kept rather than "completed," for three reasons stated so the absence is not later read
as an oversight:

1. **B's permissive half is a permission, not an obligation.** Nothing in this lane needs a
   duration. Adding a field so that the code matches the letter of a ruling — then adding a
   pin to guard the field — is a mechanism whose only purpose is to be guarded.
2. **The cadence's question is already answered elsewhere, exactly once.** *"When was this last
   run?"* is the commit date of the committed report artifact: immutable, verifiable, and
   single-sourced. A `generated_at` inside the artifact would be a second statement of one
   fact, drifting from the first the moment a report is regenerated and not committed — the
   same defect this repository registered as G-23 the same week.
3. **It keeps the digest honestly deterministic.** `deterministic_digest` covers hardware-stable
   evidence only (per-beat shape + verdicts). A timestamp would have to be excluded from it,
   which means shipping a field the digest deliberately does not cover — a value in the
   artifact that the artifact's own integrity check ignores.

**What would change this.** If a predicate is ever added whose claim is genuinely about
*duration* rather than *sequence* — H5's resource-cost leg is the live candidate, since cost
per unit time is not cost per beat — then a wall-clock enters **telemetry**, excluded from the
digest, with a pin asserting no cognitive path reads it. That is B exercised, and B is already
ruled, so it needs no new decision — only the predicate that requires it.

## Predicates

| ID | Proves | Fails loudly when | Mutation-verified bite |
|----|--------|-------------------|------------------------|
| **H1** closure | every OBSERVED idle beat has `versor_condition < 1e-6` (closure holds over idle uptime, READ never repaired) | the idle heartbeat drifts/corrupts the field, or the field never existed (vacuous) | a beat with `versor_condition ≥ 1e-6`; an all-`None` (no-field) soak |
| **H2** bounded idle | a `did_work=False` beat adds NOTHING to the vault (no idle resource leak) | a converged idle life keeps growing a store — invisible at 5 beats, fatal at 100k | an idle beat whose `vault_size` grew over the prior beat |
| **H3** convergence | a saturated idle life SETTLES and stays settled (no re-awakening), at rest at the end, closure intact on the tail | the life churns forever, thrashes (work-after-rest), or breaks closure once settled | a never-settling run; a rest→work re-awakening |
| **H4** reboot resume | a reboot mid-soak resumes the SAME life (strict identity guard passes, pre-reboot DERIVED learning survives, post-reboot closure holds) | a reboot forks a new life, loses learning, or breaks closure | `resumed_cleanly=False`; `learned_fact_survived=False` |

Each predicate has a `*_holds` test (real soak) **and** a `*_bites` test (mutation), per the
CLAUDE.md schema-as-proof discipline: a predicate that cannot fail under the violation it
nominally catches is decoration, not proof.

## The measured result

On a 5000-beat soak (reboot at 2500): **all gates pass.** `versor_condition` is flat at
`1.389e-07` across all 5000 beats (no drift — the idle heartbeat never perturbs the field,
no repair), the vault stays bounded at 6 entries (no idle leak), the life converges at
beat 1 and the 4999-beat tail stays at rest with closure intact, and the reboot at 2500
resumes the same life with its derived learning intact. This is the empirical resolution of
the L10 riskiest-unknown **for the idle path** (the closure-by-construction ruling covered
the field-transition walk; this covers indefinite idle uptime).

## Not covered (no silent skips)

- **H5 — learning-life resource cost.** This lane proves the **idle (converged)** life is
  resource-bounded. The cost of a continuously-**learning** life under a sustained
  new-fact stream — the full-snapshot checkpoint is O(n²) in facts, `lived_life.json` is
  per-run — is out of scope until an afferent/intake feed and incremental persistence
  exist. Recorded as `not_covered` in the report; a follow-up.

The `deterministic_digest` in the report freezes the per-beat shape (`did_work` /
`field_valid` / learning counts / vault size — all deterministic) + the verdicts, excluding
the machine-variant raw `versor_condition` float. ~~Pin it once the lane is trusted so a
regression flips it.~~ **Pinned 2026-07-28 — see below.**

---

## The committed evidence, and the cadence that keeps it true (R-9, ruled A)

**Artifact:** `evals/l10_always_on/results/report-5000-6c67e88d.json`
**Digest:** `f814fd97f367840b0a9d31a48cb9fb28b2ed01961606f7b1e0b4c3a3593972d6`
**Re-run:** `PYTHONPATH=. uv run python -m evals.l10_always_on 5000 2500`
**Pinned by:** `tests/test_l10_soak_evidence.py`, on the gate.

For nine days this lane's result was **prose in this file** — a real 5000-beat pass with no
machine-readable artifact, no run SHA, no rerun path, and a digest that `report.py` computed
and nothing pinned. The instruction two paragraphs up asked for the pin and it was never
added. **A recorded prose result with no re-derivable artifact is testimony, not evidence**,
and this file is where that distinction was supposed to be enforced.

### The 2026-07-28 re-run, and why the prose number moved

| | recorded 2026-07-19 | re-run 2026-07-28 |
|---|---|---|
| `versor_condition` | "flat at `1.389e-07`" | worst **`6.177e-08`** |
| vault size (bounded) | 6 | **6** |
| convergence beat / tail | 1 / 4999 | **1 / 4999** |
| reboot resume + derived learning | clean | **clean** |
| all four predicates | pass | **pass** |

**Every deterministic fact reproduced exactly; only the machine-variant float moved.** That is
the first real evidence that excluding `versor_condition` from the digest was the right call —
a digest covering it would have flipped on a machine change and taught every reader to ignore
it. The prose figure `1.389e-07` is therefore **superseded, not contradicted**: it was never a
reproducible quantity, and the artifact records the one that is.

### The cadence is change-triggered, not clock-triggered

R-9 ruled the cadence as *"before each arc close, and on any change to the always-on process"* —
**enforced by a pin, not by a schedule.** The local-first doctrine makes "nightly" a ruling
rather than a cron line (`AGENTS.md`: *"when the Mac is asleep or away, the Actions queue
waits… That is fine"*), and a nightly that does not run is green for the wrong reason — H-9's
mechanism exactly.

So instead of asking *"when did we last run it?"* the pin asks the question that matters:
**does this evidence still describe the code that ships?** It holds the SHA-256 of every source
the soak attests — `chat/always_on.py`, `chat/always_on_daemon.py`, and the three harness
modules — and fails when any of them changes, with the message *re-run the soak; do not edit
the hashes.*

**This is not a hypothetical guard. It had already fired, silently, for six weeks.** The
2026-07-19 soak ran with `accrue_realized_knowledge` **absent** from
`CONTINUOUS_LIFE_CONFIG_FLAGS`. R-3 added it on 2026-07-28, so from that moment the recorded
result attested a process that no longer existed — and nothing in the repository could notice.
Had this pin existed, PR-5 would have failed it. That is precisely the intended behaviour, and
it is why the cadence is tied to change rather than to a calendar.

**"When was it last run" is answered by the artifact's commit date** — immutable, verifiable,
and stated once. A `generated_at` field inside the report would be a second copy of that one
fact, drifting the moment a report is regenerated and not committed.
