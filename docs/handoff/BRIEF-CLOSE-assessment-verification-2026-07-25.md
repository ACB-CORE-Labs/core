# Arc-Close Brief — Assessment Verification & Lateral Closures

**Arc:** assessment-verification-2026-07-25 · **Closed:** 2026-07-25 · **Closing tier:** Opus 5
**Plan of record:** independent verification of an external Tier-S assessment + its five-pillar blueprint
**ADRs minted:** none (one amendment: ADR-0263 gains rule 5, recorded in `core/ratified_ledger.py`)

> First use of `ARC-CLOSE-TEMPLATE.md`, written in the same arc. Filling it in
> was also the test of it.

## 1. What shipped

| Capability | Enforcement site | Evidence |
|---|---|---|
| `deduction`/`curriculum` registered as grounding sources, cross-stack | `core/epistemic_state.py`, `workbench-ui/` badges + snapshot | `tests/test_workbench_deduction_provenance.py` (14) |
| Coercion derives its whitelist from the enum instead of restating it | `workbench/api.py::_coerce_grounding_source` | same file, parametrized over the registration |
| Ledger absence policy declared, not passed (ADR-0263 rule 5) | `core/ratified_ledger.py::CAPABILITY_LEDGERS` | `tests/test_ratified_ledger_bridge.py::TestCapabilityManifest` |
| Deductive suite in the pre-push gate | `scripts/hooks/pre-push` | measured 285 tests / 29s vs smoke 216 / 62s |
| Smoke↔CI parity assertion made bidirectional | `tests/test_cli_test_suites.py` | mutation-checked; carries a dated `PENDING_IN_CI` list — see §7 |
| Correction-binding lockstep pinned on the deduction path | `tests/test_prior_surface_deduction_binding.py` (6) | mutation-checked |
| Ratification ceremony + `core proposal-queue ratify` | `teaching/ratification.py`, `core/cli_proposal_queue.py` | `tests/test_ratification_ceremony.py` (14) |
| Domain-keyed ADR index | `docs/adr/INDEX-by-domain.md` | `tests/test_adr_index.py` (5) |
| Arc-close brief template | `docs/handoff/ARC-CLOSE-TEMPLATE.md` | this file |

## 2. Flag state at close

| Flag | Default at close | Ratified by | Notes |
|---|---|---|---|
| `deduction_serving_enabled` | **True** | ADR-0256, 2026-07-24 | Unchanged. Its suite is now a pre-push gate, not async CI. |
| `curriculum_serving_enabled` | False | — | Unchanged. Blocked on volume, not machinery; the ceremony is the volume path. |
| `accrue_realized_knowledge` | False | — | Unchanged, and **not** debt: a deployment profile (session memory), ON in production L10. |

No flag was flipped in this arc.

## 3. Falsified assumptions

| The assessment assumed | Measurement showed | Evidence |
|---|---|---|
| `parents[n]` audit is high-payoff | 168 sites, **0** outside the repo root | audit run |
| Guard exemption undocumented | Documented at **both** guard sites with rationale | `chat/runtime.py:2371`, `:3007` |
| T12 ledger entry missing | Present as an open pattern-watch item | `weekly-audit-2026-07-22-stragglers-todo.md:170` |
| `assert_corpus_sound` has one impl | Already domain-parameterized, called unconditionally | `evals/curriculum_serve/runner.py:71,105-108` |
| Promotion oracle must be built | Already the `wrong=0` lane gate | `tier-s-housekeeping-2026-07-24.md` §3 |
| `EntailmentTrace` drops proof chains | ROBDD tautology check; **no intermediate steps exist** | `generate/proof_chain/entail.py:125-190` |
| Cross-subject proof could emerge accidentally | `resolve_domain` refuses `ambiguous_reading` | `chat/curriculum_surface.py:138` |
| Second subject arena is next | 11 bands across 4 subjects already route; all 24×–73× short | `curriculum-volume-quantification-2026-07-24.md` §2 |
| **(mine)** `versor_condition` is the hot spot | **0.22%** of a turn | `cga-hot-path-measurement-2026-07-25.md` §2 |
| **(mine)** Workbench also falsifies `epistemic_state` | It does not — reads `epistemic_state_needed`, honest | `workbench/api.py:818` |

## 4. Binding constraint going into the next arc

Unchanged and unmoved: **ratified curriculum volume.** Eleven live bands, every
one 24×–73× short of the entailed-bucket floor, and physics — the deepest — has
16 chains against a ~219 floor. This arc built the machine that converts a
reviewed decision into a routable chain and proved it moves the band
(`causal: 7 → 8` on a dry run), but it ratified no content. The ceremony is a
pipe; someone still has to put curriculum through it. Nothing else in the
roadmap unblocks until that number moves.

## 5. Trigger state

**Core Logos Phase 5 (multi-step articulation) is NOT triggered**, contrary to
the assessment's reading. The trigger was described as "the renderer discards
intermediate proof chains" — there are none to discard.
`evaluate_entailment_with_trace` decides by asking whether
`(P1 & … & Pn) -> Q` is a tautology; `EntailmentTrace` carries five opaque BDD
node keys.

What must land in a higher tier **before** any implementation: a feasibility
study for **proof-term extraction** over the ROBDD — a derivation calculus with
a real soundness surface, not a data-structure refactor. Scoping it as the
latter produces a renderer with nothing to render.

## 6. What is NOT next, and why

- **Widening the math reader for cases 0000/0001/0148/0082.** Traced; their
  blocking gaps affect **1 and 2 cases out of 500**. ADR-0251's prohibition now
  rests on a count.
- **A `.metal` Cl(4,1) kernel / MLX fusion / bf16.** The Cayley table already
  exists at compile time in `cl41.rs`; the fusion target is 0.22% of a turn;
  bf16's ε ≈ 7.8e-3 against a 1e-6 gate. And there is an exact CPU win
  available first.
- **The diagonal `cga_inner` shortcut.** Tempting, 32× fewer ops, and **not
  bit-exact** (954/4000 in f32). It would move lane pins.
- **Discovery-yield stratification.** Blocked on new persisted per-source
  counters in the engine_state manifest.
- **Band-level capability index.** Blocked on a scoring decision — 25 near-1.0
  entries inflate `coverage_geomean` against the index's own anti-gaming claim.
- **`engine_refused` as a standing gate.** Classifier already CI-gated; pinning
  a count on an empty bucket is the stale-pin failure mode.

## 7. Open items carried forward

| Item | Kind | Recorded |
|---|---|---|
| Does `core_rs` hold bit-exact parity? | blocked (network policy denies `static.crates.io`) | `cga-hot-path-measurement-2026-07-25.md` §7 |
| Rust typestate `UnverifiedClaim`→`VersorClaim` | blocked on a build | same, §7 |
| Serial-fold `cga_inner` in the search paths | untested (exactness proven, change not made) | same, §6 |
| Audit-ledger **R7** — telemetry sink gets pre-override events | deferred | `docs/specs/runtime_contracts.md` |
| `hash_surface` on `TurnEvent`, or not | undecided | same |
| Arena queue entry + ledger reseal after ratification | deferred by design (bridge rule 1) | `RatificationReceipt.pending_stages` |
| Forgejo zero-length-object claim | unverified from this environment | assessment doc, preamble |
| **Three files owed to `smoke.yml`** | blocked (push credential lacks `workflow` OAuth scope) | `tests/test_cli_test_suites.py::PENDING_IN_CI` |

**On that last row — the one thing this arc found and could not finish.** The
CI smoke gate is narrower than the local one. `test_pack_draft_serve_boundary.py`
(ADR-0253 dual-pack boundary, INV-33) has been in the local pre-push gate and
absent from `smoke.yml`, and the parity pin only ever checked the *other*
direction, so it went unseen. The two new deduction-provenance files belong
there for the same reason. The three-line edit was authored and rejected at push
(`refusing to allow an OAuth App to create or update workflow smoke.yml without
workflow scope`), so it is recorded as a named, dated exception rather than
silently dropped: the assertion still fires on any *new* divergence, and a
second guard fires once the three land so the list cannot rot. Anyone pushing
with `workflow` scope closes it by adding three lines and emptying the tuple.

## 8. Gates and their state at close

| Gate | Command | Result |
|---|---|---|
| smoke | `core test --suite smoke -q` | **236 passed** (216 baseline + 20 new) |
| deductive | `core test --suite deductive -q` | **285 passed** |
| workbench-ui | `vitest run` | **598 passed / 73 files**; `tsc -b` clean |
| capability index | `pytest tests/test_capability_*` | **11 passed**, baseline digest unchanged |
| math holdout | `evals/gsm8k_math/holdout_dev/v1/runner.py` | `correct=5 wrong=0 refused=495` |
| proposal/curriculum sweep | `pytest -k "proposal_queue or ratification or curriculum"` | **246 passed** |
| grounding/epistemic sweep | `pytest -k "workbench or epistemic or grounding or …"` | **741 passed, 1 skipped** |

**Environment caveat, and it matters for how much these are worth.** The repo
pins `requires-python == 3.12.13`, which `uv` cannot fetch for
linux-x86_64, so `uv sync --locked` fails. All Python runs above used a scratch
venv on 3.12.11 with the declared deps — **not the locked dependency universe**,
and not the full ~12k suite. The pin was left untouched. Re-run the real gates
on a 3.12.13 host before treating any of this as merged-quality evidence.

## 9. Ground truth corrections for the next opener

1. **`chat/runtime.py:471-481` was stale and is now rewritten.** It argued the
   unregistered `deduction` label was "inert today" because REPL turns do not
   reach Workbench. True, and irrelevant — Workbench builds a bare
   `ChatRuntime()`, so the traffic flows the other way. Live from the moment
   the flag was ratified ON. This is the class of staleness nobody greps for:
   a comment reasoning from a premise that has since changed.

2. **A second copy of a closed enum is worse than no copy.** The *unregistered*
   path degraded honestly (`epistemic_state_needed` = "needs determination").
   The hand-copied whitelist asserted a falsehood (`none` = ungrounded). Derive
   from the enum; do not restate it.

3. **Silent-drop is correct at serving time and a trap at ratification time.**
   `_ratified_rows` dropping unadmissible rows is right when serving. Appending
   a row the loader will drop looks identical to appending one that works. Any
   future corpus-writing path needs the same confirm-admission discipline.

4. **Do not compare a microbenchmark to a latency figure.** §3's last two rows
   are both mine, and both came from reasoning about measurements instead of
   taking them. The turn is the denominator.

5. **`assert_corpus_sound` is two functions with one name** —
   `evals/deduction_serve/practice/gold.py:1163` (no args, practice corpus) and
   `evals/curriculum_serve/runner.py:71` (`domain, cases`, lane contract). Not
   a missing contract; a name collision. Worth renaming before a third appears.
