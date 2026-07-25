# Curriculum License Loop — Plan of Record

**Date:** 2026-07-25 · **Status:** ACTIVE · **Base:** main @ `0a26787f`
(post ADR-governance pin, PR #114)

Successor to `generalization-arc-2026-07-24.md`, which closed its Tier F/O/S
arc, and to the assessment-verification arc (PR #113). Division of work across
tiers: `docs/handoff/curriculum-license-loop-2026-07/DIVISION-OF-WORK.md`
(binding — read it before starting any unit).

---

## 1. Why this arc exists

Two arcs closed on the same stated conclusion: *the binding constraint is
ratified curriculum volume, not machinery.* That conclusion is half right, and
the wrong half is load-bearing. Verified 2026-07-25 by reading code:

1. **`evals/curriculum_serve/practice/` does not exist.** The deduction analogue
   (`evals/deduction_serve/practice/{gold,runner}.py`) is what folds
   `run_practice` over a corpus into per-band `ClassTally`. Curriculum has no
   producer.
2. **`seal_ledger` exists only for deduction**
   (`evals/deduction_serve/practice/runner.py:96`).
   `chat/curriculum_serve_license.py`'s own docstring names
   `evals.curriculum_serve.practice.runner.seal_ledger` as "the only writer" of
   the artifact it reads. **That writer was never built**, and
   `chat/data/curriculum_serve_ledger.json` does not exist.
3. **The ceremony stops short.** `teaching/ratification.py::RatificationReceipt`
   carries `pending_stages = ("arena_queue_entry", "ledger_reseal")` — it grows
   the corpus and explicitly neither practices it nor reseals the ledger.

So the pipeline is `author → ratify chain → ??? → ??? → license → serve`, with
two unbuilt segments. **Authoring curriculum today cannot earn a license at any
volume.** Content is necessary and currently insufficient.

The build is nonetheless *modest*, because the expensive pieces already exist:
`evals/curriculum_serve/oracle.py` is already an independent decision procedure
usable as the gold tether, and ADR-0263 already extracted the sealers
(`core/ratified_ledger.py`) for precisely a third instance.

## 2. Two measured facts that shape the content work

- **`refuted` has never been produced.** The physics lane gold is
  `entailed 14 / unknown 12 / declined 6` — zero refuted. The verdict exists in
  `CurriculumDecision.verdict`; no corpus row can express it.
- **Bands key on `(domain, operator_family)`**
  (`chat/curriculum_surface.py:184`). Negative content must therefore live
  *inside* `operator_family: "modal"` with a row-level polarity marker. A
  separate `modal_negative` family would create a **new band at n=0** instead of
  adding refuted volume to the target band. This is the easiest available way to
  waste the entire authoring effort.

## 3. Decisions taken (2026-07-25, Shay)

| Decision | Choice |
|---|---|
| Leading track | Close the license loop (not articulation, not substrate) |
| First content target | **physics · modal** — n=9, closest of eleven bands (24× short) |
| `refuted` representation | **Explicit negative edges**, polarity inside the existing family |
| Reseal trigger | **Explicit `core proposal-queue reseal` verb**, never automatic on `ratify` |

Reseal is explicit because `AGENTS.md` forbids ratification automation, and
because an auto-reseal per ratified row would churn the ledger's
`content_sha256` on every append.

## 4. Phases

### Phase A — Negative-curriculum epistemology *(design only; gates everything)*
ADR deciding how an explicitly-taught negative coexists with the open-world
reading. Binding constraints: absent edge ⇒ UNKNOWN (never "no"); explicit
negative edge ⇒ REFUTED; polarity is a row-level field or `intent` value, never
a new `operator_family`; `evals/curriculum_serve/oracle.py` must learn polarity
**independently** of the serving path, since that independence is the whole
evidentiary value.

Touches: `teaching/domain_chains/physics_chains_v1.jsonl` schema,
`teaching/curriculum_premises.py`,
`teaching/ratification.py::validate_admissible`,
`evals/curriculum_serve/oracle.py`, lane contract anti-recall probes.

**Done when:** ADR Accepted; schema shape fixed; no code written.

### Phase B — The volume-honesty invariant *(the anti-gaming gate)*
Failing tests written **before** any producer code. The generator must emit at
most one committed case per distinct `(relation, direction, polarity,
question-shape)` tuple and must never paraphrase-pad. S6 already proved
`conservative_floor` cannot distinguish "657 independent facts" from "16 facts
asked 41 times," so an unbounded generator would clear the Wilson floor without
earning anything.

**Done when:** tests exist, fail for the right reason, and fail under mutation
(pad the generator ⇒ red).

### Phase C — The producer *(implementation against Phase B)*
`evals/curriculum_serve/practice/{__init__,generator,runner}.py`, mirroring
`evals/deduction_serve/practice/` topology exactly — producer in `evals/`,
artifact next to its reader in `chat/data/`.

Reuse, do not rewrite: `evals/curriculum_serve/oracle.py` (gold tether),
`core/learning_arena/engine.py::run_practice`,
`core/ratified_ledger.py::{seal_artifact, tally_dict, write_sealed_ledger}`,
`core/reliability_gate::{Action, Ceilings, ClassTally, license_for}`,
`chat/curriculum_surface.py` (solver under test).

**Done when:** Phase B tests green; `wrong=0` on the physics lane.

### Phase D — Close the ceremony's `pending_stages`
`core proposal-queue reseal` verb; `ratify_chain` records the enqueue.
Files: `teaching/ratification.py`, `core/cli_proposal_queue.py`.

**Done when:** the verb produces a SHA-sealed
`chat/data/curriculum_serve_ledger.json`, and
`curriculum_serve_license()` reads a real (still-unearned) ledger rather than an
absent one.

### Phase E — Honesty seams *(parallel, no dependency on A–D)*
- **E1 — audit-ledger R7.** Defer the single sink emission to the pipeline serve
  boundary (`chat/runtime.py::finalize_turn_surface`; spec at
  `docs/specs/runtime_contracts.md:448-456`). Repairs the stale surface and
  stale `trace_hash` together. Default sink is `None`, so no deployment risk.
  Independent of the `hash_surface`-on-`TurnEvent` ruling.
- **E2 — `assert_corpus_sound` name collision.** Two functions, one name:
  `evals/deduction_serve/practice/gold.py:1163` (no args, practice corpus) vs
  `evals/curriculum_serve/runner.py:71` (`domain, cases`, lane contract). Must
  land **before** Phase C adds a third caller.
- **E3 — ADR status vocabulary normalization.** 27 unparseable status lines plus
  `draft`/`ratified`/`active`/`accepted.` variants across 312 files; then widen
  `tests/test_adr_status_governance.py` to a closed vocabulary.

### Phase F — Content *(the actual constraint)*
Author + ratify physics · modal volume: ≈219 distinct taught modal relations for
the entailed bucket, plus matching refuted/unknown. Measure with
`teaching.ratification._count_chains` and
`evals/vocab_trigger_instrument.py --compare` admissions delta.

Relations must be **true**. Drafting candidates is delegable; ratification is
Shay's.

### Phase G — The flag *(Shay only)*
Only after a band clears θ=0.99 at n≥657 with a genuine outcome mix: *propose*
flipping `curriculum_serving_enabled`. On earned evidence, never on proximity.

## 5. Deferred, decision-gated *(a ruling, not effort)*
- **Band-level capability index** — 25 near-1.0 entries would inflate
  `coverage_geomean` against the index's own anti-gaming property. Needs a
  scoring decision before any schema change.
- **Discovery-yield stratification** — blocked on new persisted per-source
  counters in the `engine_state` manifest
  (`teaching/discovery_yield.py:67-70` reads one monotonic `turn_count`).
- **`hash_surface` on `TurnEvent`** — self-verifying telemetry vs replay-only.
  Current contract states recomputation is unsupported *and correct to be so*.

## 6. Off this arc's critical path
- **Articulation depth (Phase 5 / core_logos).** `EntailmentTrace` carries five
  opaque BDD node keys; `generate/proof_chain/entail.py:125-190` decides via
  `is_tautology`. There are no intermediate steps, so nothing is dropped and the
  stated trigger describes an event that cannot occur. CORE's decision procedure
  is **complete but not explanatory.** Next deliverable is a *feasibility study
  for proof-term extraction over the ROBDD* — a derivation calculus with a real
  soundness surface, not a data-structure refactor. Highest intellectual value,
  least schedulable.
- **Substrate.** `CORE_BACKEND=rust` bit-exact parity is now answerable locally
  (cargo 1.97.1 + registry cache present; `core-rs/tests/test_crdt_hash_parity.rs`
  exists; needs `PYO3_PYTHON=/opt/homebrew/bin/python3.12`). Then Rust typestate
  (`UnverifiedClaim` → `VersorClaim`) — zero determinism cost, greenfield. The
  real hot path is `cga_inner` → `geometric_product`, 33,986 calls/turn, ~73% of
  turn time. **Not** the diagonal shortcut — not bit-exact (954/4000 in f32).
  **Refuted, do not revisit:** `.metal` kernel, MLX fusion, bf16.
- **Math.** Phase 4.2 case-first is falsified on a count — cases
  0000/0001/0148/0082 affect 1 and 2 cases out of 500. Only remaining lever is
  the `q:complex` decomposition study (101 cases, one label). Low expected value.

## 7. Dependencies
- **A gates B** (polarity shapes the generator's enumeration — building C before
  A means building it twice).
- **B gates C** (tests first; the invariant *is* the specification).
- **E2 lands before C.** E1/E3 fully parallel.
- **C + D gate F's measurement**, and F gates G.
- Phase 6 items independent and parallel throughout.

## 8. Non-goals
- Flipping any flag without explicit ratification.
- Adding band entries to the capability index before the scoring decision.
- Paraphrase-padding practice volume to reach the Wilson floor.
- Renumbering or overwriting Accepted ADRs.
