# Arc-Close Brief — Curriculum License Loop

**Arc:** curriculum-license-loop-2026-07 · **Closed:** 2026-07-26 · **Closing tier:** Opus 5
**Plan of record:** `docs/plans/curriculum-license-loop-2026-07-25.md` (carries an
`AMENDED 2026-07-25` block; §4.2 of ADR-0264 carries a `CORRECTED 2026-07-26` block)
**ADRs minted:** ADR-0264 (the arc's only new ADR; ADR-0262 gained three forward-pointers)

**Nothing in this arc is merged.** Seven PRs (#119–#120 merged; #121–#125 plus the
doc branch open) sit awaiting authorization. Read §2 before assuming any behaviour
changed: it did not.

## 1. What shipped

| Capability | ADR | Enforcement site | Evidence |
|---|---|---|---|
| Query-scoped premise compilation — a >16-chain family answers again | 0264 R5–R7 | `teaching/curriculum_premises.py::compile_premises` | #120 merged; 0 verdict mismatches / 8,190 questions |
| Volume-honesty invariant — committed volume must be DISTINCT evidence | 0264 R9 | `tests/test_volume_honesty.py`, `core/reliability_gate/evidence.py` | #117 merged; 21/25 deduction bands measured short |
| The curriculum practice producer (the ledger's only writer) | 0262/0264 | `evals/curriculum_serve/practice/` | #121; 11 bands, wrong=0, inflation 1.0 |
| `core proposal-queue reseal` — the `ledger_reseal` ceremony stage | 0262 | `teaching/ledger_reseal.py` | #122; refuses to grant a license without `--allow-new-licenses` |
| Durable telemetry carries the POST-override turn event | audit-ledger R7 | `chat/runtime.py::_emit_turn_event`, `pipeline.run` | #123; I1–I8 pinned, 3 mechanisms mutation-checked |
| Taught curriculum NEGATIVES — `polarity` is read | 0264 R1–R4/R8 | `CurriculumChain.sentence`, `validate_admissible`, `oracle.py` | #125; 22 tests, 3 rules mutation-checked |
| `core rust build` works at all | — | `core/cli.py::_run` | #124; raised `TypeError` on every prior invocation |

## 2. Flag state at close

**No flag moved. No serving behaviour changed anywhere in this arc.**

| Flag | Default at close | Ratified by | Notes |
|---|---|---|---|
| `curriculum_serving_enabled` | **OFF** | — | unchanged; no band holds a license because no ledger is committed |
| `deduction_serving_enabled` | **ON** | ratified 2026-07-24 | untouched. Its ledger's distinct-evidence exposure is measured and pinned, **not** repaired |
| `identity_wave_gate` | OFF | ADR-0244/0245 | untouched |
| `CORE_BACKEND` | `python` | — | untouched. `core_rs` importable ≠ active; verified |

`chat/data/curriculum_serve_ledger.json` is **deliberately absent** — see §3.1.

## 3. Falsified assumptions

| Plan assumed | Measurement showed | Evidence |
|---|---|---|
| "The binding constraint is ratified curriculum volume, not machinery" | Half wrong both ways. The 16-premise cap meant **no** band could earn at any volume (engineering, not content); and once fixed, the *unknown class alone* clears the floor (content is not the constraint either) | ADR-0264 §4.1; `curriculum-practice-producer-2026-07-26.md` §1 |
| Phase 1 exits with "a real (still-unearned) ledger" | **Unreachable.** Reliability is commitment precision and a correct UNKNOWN is a commitment, so any band with ≥657 routable atoms clears θ_SERVE on non-commitments alone. A committed ledger is necessarily an earning one | #121; `conservative_floor(660,660)=0.990046` |
| 8 of 11 bands cannot reach n=657 (`systems_software·causal` impossible at 630) | **7 of 11.** I sized bands from per-*term* exclusivity; the router's predicate is per-*pair*, which is looser. `systems_software·causal` is **720** | ADR-0264 §4.2 CORRECTED block; `BAND_ATOM_SPACE` |
| R5 narrowing is "verdict-identical" | Identical wherever the full family was **readable**; verdict-*improving* over the cap, where full-family compilation refuses outright | ADR-0264 R5 precision note |
| R7: the sink holds "a stale surface and a stale `trace_hash`" | `trace_hash` is **never serialized** — `chat/telemetry.py` has zero references. Only the surface half was real | #123; `test_trace_hash_is_not_in_the_wire_format_at_all` |
| The R7 surface divergence is exercised by default | `finalize_turn_surface` is a **no-op on all 36 default-config turns probed**. It fires only under `realizer_grounded_authority` (24/84) | #123 fixture |
| "Rerun the hash-pinned lanes under `CORE_BACKEND=rust`" measures parity | **Cannot fail.** Sabotaging every Rust kernel still yields 11/11 pins matching. Zero Rust calls in the deductive lane; exactly ONE per pipeline turn | #124; `rust-parity-measurement-2026-07-26.md` §2 |
| Curriculum vocabulary is safe to enumerate over | `then` and `therefore` are **taught lemmas that are also the reader's control words** — 164 atoms refuse, in the Phase F target band | #121 §3 |

## 4. Binding constraint going into the next arc

**The outcome-mix ruling.** It is the single thing between a fully built license
loop and four unearned SERVE licenses. Every mechanism now exists — producer,
audit, reseal verb, negatives — and running `core proposal-queue reseal
curriculum_serve --allow-new-licenses` today would license
`philosophy_theology·{modal,contrast}`, `physics·causal` and
`systems_software·causal` on evidence that is **99.0%–99.98% correct
non-commitment**, which ADR-0262 §5.1 rules unacceptable and which `ClassTally`
structurally cannot see (no verdict axis: a correct UNKNOWN is indistinguishable
from a correct ENTAILED once tallied). Max entailed volume in any band today is
**9**. Until mix is enforced *at the producer*, curriculum volume is not the
constraint — the absence of a mix rule is.

## 5. Trigger state

- **Articulation depth (plan §5).** Trigger **not met, and structurally cannot
  be**: `generate/proof_chain/entail.py` decides by asking `is_tautology` on
  `(P1 ∧ … ∧ Pn) → Q`, so there are no intermediate steps to drop. The stated
  trigger describes an event that cannot occur. Recorded here because the previous
  arc left it unrecorded, which is what made it re-triggerable. The real
  deliverable remains a **feasibility study for proof-term extraction over the
  ROBDD** — not undertaken this arc, and it is a study, never a ticket.
- **Phase F content.** Unblocked in mechanism, gated on §4's ruling. Target is
  `philosophy_theology · modal` (45,300 routable atoms), **not** `physics · modal`
  (480, impossible at any authoring volume).
- **Phase G flag.** Not triggerable: requires an earned license, which requires §4.

## 6. What is NOT next, and why

- **Authoring `physics · modal` volume.** Ceiling 480 < 657 with every possible
  question counted. No amount of chain authoring raises it; only growing
  `en_physics_v1` would.
- **Committing the curriculum ledger as housekeeping.** It is a ratification that
  licenses four bands (§4). #122's verb refuses by default for exactly this reason.
- **"Repairing" the deduction ledger's distinct-evidence exposure.** SHA-sealed,
  ratified, gating a live flag. Re-sealing is Shay's. Any unit that makes
  `test_volume_honesty.py` fail has found a real signal, not a stale pin.
- **Making Rust the default backend (plan §6B).** Its premise rests on a
  measurement that cannot fail (§3). Flipping it today changes one call per turn.
- **Accelerating the CGA hot path before fixing the dispatch (plan §6C).** 69 call
  sites bypass `algebra.backend` entirely and every dispatch arm swallows all
  exceptions, so no lane-hash measurement can currently see whether Rust ran.
  Order: fail loudly → a test that fails when Rust is not *taken* → then route.
- **`.metal` Cl(4,1) kernel / MLX fusion / bf16.** Explicitly refuted in prior
  arcs; unchanged.

## 7. Open items carried forward

| Item | Kind | Where it is recorded |
|---|---|---|
| Outcome-mix ruling (per-verdict-class volume) | **blocked on Shay** — now the binding constraint | `distinct-evidence-audit-2026-07-25.md`; #121 |
| Band-level capability index scoring | blocked on ruling | plan §4A |
| Discovery-yield stratification | blocked on new persisted counters | plan §4B |
| `hash_surface` on `TurnEvent` | blocked on ruling; explicitly out of R7's scope | plan §4C; `runtime_contracts.md` |
| Reserved-word screening (curriculum vocab vs reader grammar) | deferred; bound pinned at 2 lemmas | #121 §3 |
| Rust dispatch fails silently; hot path bypasses it | deferred, escalated not fixed | `rust-parity-measurement-2026-07-26.md` §3 |
| A lane case covering empty-scope→UNKNOWN (R6) | deferred — moves the `curriculum_serve_v1` pin | this brief §9 |
| E3 ADR status vocabulary sweep (312 files) | deferred to Haiku | DIVISION-OF-WORK §5 |
| Proof-term extraction feasibility study | untested | plan §5 |
| `arena_queue_entry` ceremony stage | deferred (only `ledger_reseal` was built) | `teaching/ratification.py` |

## 8. Gates and their state at close

Per-branch, in-worktree, canonical **CPython 3.12.13** with `uv sync --locked`.
Arc-start baselines: smoke 555 → **569** after Phases A+B.

| Gate | Command | Result at close |
|---|---|---|
| smoke | `uv run core test --suite smoke -q` | #121 **571** · #122 571 · #123 **591** · #124 **575** · #125 **593** |
| deductive | `uv run core test --suite deductive -q` | #121 **310** · #122 **327** · #123 291 · #124 291 · #125 **332** |
| lane pins | `scripts/verify_lane_shas.py` | **11/11** on every branch; no pin moved in this arc |
| curriculum lane | `python -m evals.curriculum_serve.runner` | `n=32 correct=32 wrong=0 anti_recall=5` throughout |
| cargo | `PYO3_PYTHON=… cargo test --offline` | **43 passed / 0 failed** |
| sink suites | 7 files, unchanged | **80 passed** under #123 |

Every count is `baseline + exactly the tests that branch adds`; the arithmetic is
in each PR body. Mutation checks were run on all five gate-bearing units.

## 9. Ground truth corrections for the next opener

**Read §3 before the plan.** The plan of record is now wrong in five places and
carries an `AMENDED` block for four of them; ADR-0264 §4.2 carries a `CORRECTED`
block for the fifth. Original text is preserved everywhere — nothing was rewritten
to look right in hindsight.

**Two things I got wrong that are worth internalizing as patterns, not incidents.**

1. **I sized a question space from the wrong predicate** (per-term exclusivity vs
   per-pair routability) and shipped a table of eleven ceilings with one wrong
   verdict in it. The fix was not cleverness — it was asking the *router* instead
   of reimplementing its rule. `evals/curriculum_serve/practice/generator.py` now
   calls `resolve_domain` rather than restating routability, and the ceilings are
   pinned as measured values.
2. **I wrote an assertion spec against a field that is not serialized.** The E1
   spec asserted a stale `trace_hash` in the durable stream; `chat/telemetry.py`
   never wrote one. Specifying assertions before reading the wire format is the
   error, and it survived until implementation because a spec has no gate.

**The load-bearing test-design lesson of this arc:** three separate times, the
obvious measurement would have passed while proving nothing — the R7 fixture under
the default config (`finalize_turn_surface` no-ops), the Rust lane parity
(sabotage-proof), and the R8 depth check (needed an affirmative control). Each was
caught only by asking "what would this look like if the thing I am testing were
absent?" Ask that of every new pin. `test_the_pipeline_really_does_override_the_
sealed_surface` and `test_e2e_an_affirmative_row_in_the_same_slot_WOULD_create_
that_path` exist purely to keep their siblings from going vacuous, and both should
be preserved if those files are ever refactored.

**Stale reasoning still in the tree, named because nobody greps for it:**

- `evals/curriculum_serve/practice/runner.py` docstring explains why the ledger is
  uncommitted. If the mix ruling lands and the ledger is committed, that docstring
  and `test_curriculum_ledger_is_not_committed` must be updated **together** —
  the test is deliberately written to fail loudly rather than let the file appear
  as housekeeping.
- `teaching/ratification.py`'s module docstring still says every one of the eleven
  bands "is 24×–73× short of the entailed-bucket floor." That framing predates
  R5 and §4 above; the shortfall is real but the mechanism named for it is not.
- `tests/test_curriculum_practice.py::test_gold_mix_has_no_refuted_class` is a
  statement about **content**, not machinery, as of #125. Polarity works; no
  negative row is committed. Phase F should update that pin deliberately when it
  authors one.
- The R6 empty-scope path (52.7% of the question space) is guarded by exactly
  **one** test, `test_empty_scope_is_unknown_not_declined`, and **not** by the
  lane: 0 of 32 lane cases exercise it (all 12 `unknown` cases have non-empty
  scope; the 6 with `scope_size == 0` decline before scope is computed). Verified
  by mutation. Adding a lane case is a small, deliberate act that moves the
  `curriculum_serve_v1` pin — which is why it was not bolted onto a PR that
  asserts the pin is unchanged.
