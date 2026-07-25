# E1 / audit-ledger R7 — the assertion spec

**Arc:** curriculum-license-loop Phase E1 · **Written:** 2026-07-25 · **By:** Opus 5
**For:** the Sonnet unit "E1 (code half). R7" in `DIVISION-OF-WORK.md` §4
**Read first:** `docs/specs/runtime_contracts.md` §"Open, tracked as audit-ledger R7"

The code move is specified — the contract already says *"defer the single sink
emission to the pipeline serve boundary."* What was never specified is **what to
assert**, and the default sink is `None`, so nothing exercises this path. A wrong
move is therefore silent, which is why the assertion set is written here before
any code moves. This is the same seam that regressed silently for two days in the
#96 register-axis incident.

Do not improvise the assertions. If implementing reveals that one of them is
wrong, that is escalation condition §6.3 — say so with the specifics rather than
adjusting the assertion to match the implementation.

---

## 1. The defect, precisely

`ChatRuntime.chat` seals a `TurnEvent` and emits it to the sink inline
(`chat/runtime.py:3157`, and the refusal-stub path at `:2490`).
`CognitiveTurnPipeline` then applies the surface authority and the canonical
`trace_hash` **after** `chat` returns, back-stamping both onto `turn_log[-1]`:

```
core/cognition/pipeline.py:823   runtime.finalize_turn_trace_hash(trace_hash)
core/cognition/pipeline.py:833   runtime.finalize_turn_surface(surface, articulation_surface)
```

So `turn_log[-1]` ends up correct and **the durable telemetry stream does not**.
The sink holds a stale `surface` and a stale `trace_hash`. `turn_log` is repaired;
the thing that persists is not.

## 2. Mechanism — mirror `_pending_reboot_payload`, do not invent one

A stage-then-flush pattern already exists in this class: `_pending_reboot_payload`
is buffered and flushed in `attach_telemetry_sink` (`chat/runtime.py:1486-1489`).
Mirror its shape. Three rulings make the difference between mirroring it and
reintroducing the bug:

**M1 — Stage an INDEX, not a copy of the event.** Stage the position in
`turn_log`; at flush time, format `self.turn_log[idx]`. A captured `TurnEvent`
object would be the pre-override snapshot, which is the defect with extra steps.
Re-reading `turn_log` picks up both back-stamps for free and cannot go stale.

**M2 — `attach_telemetry_sink` must NOT flush a staged turn event.** This is the
opposite of what it does for `_pending_reboot_payload`, and the asymmetry is
load-bearing: the reboot payload is already final when buffered, whereas a staged
turn event is *mid-flight* and may not yet be back-stamped. Flushing on attach
would emit the pre-override event and silently restore R7. Leave the reboot flush
exactly as it is.

**M3 — The runtime cannot detect whether a pipeline will run**, because
`CognitiveTurnPipeline` wraps the runtime (`self.runtime`) rather than the reverse.
So deferral must be **opt-in and explicit**: the pipeline tells the runtime it
owns the emission, and the runtime emits inline otherwise. A runtime used directly
(`ChatRuntime.chat` with no pipeline — which the eval and demo paths do) must
behave byte-identically to today, including emission timing.

## 3. Invariants to assert

### I1 — Exactly once, on every path
Each `TurnEvent` reaches the sink exactly once: never zero (a deferred event that
nobody flushed), never twice (pipeline flush plus a fallback). Assert a count, not
merely presence. Both emission sites are in scope — the main path (`:3157`) and
the refusal-stub path (`:2490`).

### I2 — The emitted event is the POST-override event
For a turn where the pipeline overrides the surface, the single emitted JSONL line
must carry:

- `surface` == the pipeline's served surface (`pipeline.run().surface`)
- `articulation_surface` == the pipeline's resolved articulation surface
- `trace_hash` == the pipeline's computed `trace_hash` (non-empty)

Construct the test so the override actually fires — a turn where
`TurnEvent.surface != pipeline.run().surface` under today's code. If the fixture
does not produce a divergence, the test proves nothing; assert the divergence
exists on the pre-fix code path, or pin a case that is known to decorate.

### I3 — `trace_hash` is verified by REPLAY, never by recomputation
Assert the emitted `trace_hash` equals the `trace_hash` of a fresh pipeline replay
of the same input. Do **not** rebuild it from the emitted record's fields — the
contract states recomputation from a turn record is unsupported *and correct to be
so*, because `TurnEvent` does not carry `hash_surface`. A test that recomputes
would encode the opposite of the ruling.

### I4 — No pipeline, no change
A `ChatRuntime` used directly emits exactly as it does today: same content, same
timing relative to the `chat()` return. Assert against the current behaviour, not
against the deferred behaviour.

### I5 — Exception safety
If the pipeline raises between `chat()` returning and the serve boundary, the
staged event must still reach the sink. Wrap the flush so it runs on the failure
path (`try/finally` at the serve boundary), and test it with a fault injected
after `chat()` — otherwise a pipeline error silently swallows a telemetry record,
which is a worse failure than the one being fixed.

### I6 — Stream order stays monotone in turn number
A durable stream's consumers may rely on order. Two specific orderings:

- turn events appear in turn order;
- a correction event for turn *N* (`_emit_correction_event`,
  `chat/runtime.py:3261`) appears **after** turn *N*'s event. Note
  `_emit_correction_event` runs at `:3255` and then calls `self.chat(...)` at
  `:3259`, so the staged-event flush must be ordered against it deliberately
  rather than by accident.

### I7 — At most one event in flight
Staging a second event while one is unflushed must flush the first, not drop it.
This bounds the worst case to "the final turn of a session whose pipeline raised
before the flush," which I5 already covers. Assert the two-turns-deferred case
explicitly.

### I8 — Default deployment unaffected
With `sink is None` (the default) nothing changes: no new work, no surface change,
`turn_log` back-stamping identical. This is what makes the change safe to land
without a flag.

## 4. Out of scope — do not fold these in

- **`hash_surface` on `TurnEvent`** (plan §5, decision 4C). R7 does **not** depend
  on it: R7 makes the stream carry the *pipeline's* `trace_hash`, which is a
  transport fix. Whether a consumer can recompute it is a separate ruling and is
  still open.
- **The `trace_hash` / `finalize_turn_surface` divergence itself.** The contract
  says these serve different invariants and are correct to differ. R7 is only
  about which of the two the sink receives.
- **Changing what `TurnEvent` contains.** Fields stay as they are.
- **The discovery-candidate sink and the articulation sink.** Different sinks,
  different lifecycles. `_emit_discovery_candidates` already back-stamps via
  `finalize_turn_trace_hash`; leave it.

## 5. Definition of done

1. All eight invariants asserted in a new test module, registered in a **curated
   suite** in `core/cli_test.py` (§4 of `DIVISION-OF-WORK.md` — two files from
   PR #113 landed in no suite and ran only under `full`, which gates nothing).
2. The seven existing sink test files still pass unchanged:
   `test_telemetry_sink.py`, `test_telemetry_fanout_and_summary.py`,
   `test_adr_0158_reboot_event.py`, `test_register_telemetry.py`,
   `test_anchor_lens_telemetry.py`, `test_correction_telemetry.py`,
   `test_workbench_operator_telemetry.py`. If one of them has to change, that is a
   behaviour change outside I1–I8 — stop and report it.
3. `docs/specs/runtime_contracts.md` — the "**Open**, tracked as audit-ledger R7"
   paragraph becomes closed, naming the commit. Leave the surrounding
   `trace_hash`-vs-`finalize_turn_surface` explanation intact; only the R7
   paragraph is resolved.
4. The `NOTE:` block in `finalize_turn_surface`'s docstring
   (`chat/runtime.py:1238-1244`) is removed, since it documents the limitation
   being fixed. `finalize_turn_trace_hash` carries the same limitation — check
   whether its docstring needs the same edit.
5. Pre-push gate green in-worktree on canonical 3.12.13:
   `smoke` and `deductive`. Baselines at the time of writing: smoke **569**,
   deductive **285**.

## 6. Why this is an Opus-then-Sonnet split

Deciding M1–M3 and I5–I7 is where a mistake is invisible: a captured-event stage
(M1), an attach-time flush (M2), or a missing `finally` (I5) all produce a green
suite and a telemetry stream that is quietly wrong — which is precisely the
original defect's failure mode. Once those are fixed in writing, the
implementation has a red/green gate at every step, and iterating against it needs
no design authority.
