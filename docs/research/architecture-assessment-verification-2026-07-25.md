> **Correction note — 2026-07-27, at `ed06dd64` (holistic assessment Phase 6).**
> One claim in this document is false and is corrected here rather than silently edited, because this document is itself a *corrective* one and its error was inherited downstream.
>
> **The claim:** that `accrue_realized_knowledge` *"is enabled by the production L10 process."*
> **The code:** `CONTINUOUS_LIFE_CONFIG_FLAGS` (`chat/always_on_daemon.py:45-49`) forces `persist_session_state`, `consolidate_determinations`, and `strict_identity_continuity` — **not** `accrue_realized_knowledge`. The daemon therefore consolidates determinations while the only turn-path writer of realized facts stays off, which is finding F-6: *as coded, the continuous life may consolidate an empty set.*
> **Not this document's fault alone:** `core/config.py`'s own docstrings for both flags make the same claim (recorded as H-8d in `docs/assessment/31-hindrance-audit.md`). Whether the flag set is incomplete or the dormancy is intended is ruling R-3 in `docs/assessment/50-rulings.md`; whichever way it goes, either one line of code or three records change.
>
> Everything else in this document was re-verified in the holistic assessment's Phases 2–3 and stands.
>
> ---
>
> **Second note — 2026-07-28: R-3 was ruled, and it made this document's original claim TRUE.**
> **The correction above is now itself out of date, and is kept rather than deleted because how it went out of date is the point.**
>
> R-3 (ruled **A — incomplete flag set**) added `accrue_realized_knowledge` to `CONTINUOUS_LIFE_CONFIG_FLAGS`. The production L10 process **does** now enable it, alongside `persist_session_state` and `consolidate_determinations`. So this document's sentence — *"is enabled by the production L10 process"* — is accurate as of `chat/always_on_daemon.py` at 2026-07-28, and the note above describing it as false is accurate only about the window `ed06dd64` … R-3.
>
> **What was actually wrong, restated precisely:** the document asserted a configuration that did not yet exist. It was describing the intended profile, and so were both of `core/config.py`'s docstrings (H-8d). Three records agreed with each other and disagreed with four lines of code — which is why R-3 resolved as *incomplete flag set* rather than *intended dormancy*. The dormancy reading would have required correcting three records that were right about the design.
>
> **Why this second note exists at all,** and it is the more useful lesson: a correction note is a record, and records go stale in both directions. This one was written to fix a claim, and was made wrong by that claim being fixed. **A dated correction that names the window it applies to survives its own subject changing; an undated "this is false" does not.** Both notes here now carry their commit range for that reason.
>
> F-6 is closed. The always-on life no longer consolidates an empty set — the daemon forces the producer (Step B) alongside the consumer (Step D). The 2026-07-19 soak result recorded in `evals/l10_always_on/contract.md` predates this change and therefore describes a **different configuration than the one that now ships**; re-running it under the corrected profile is PR-11.

# Independent verification of the Tier-S arc assessment (2026-07-25)

**Input:** an external architectural assessment of the deduction-serve generalization arc
(18 numbered observations) plus a synthesized five-pillar execution blueprint built on it.
**Method:** every load-bearing claim re-checked against the tree at `6a06cb2` by reading the
implicated code — and, where possible, by executing it. **Result:** roughly a third of the
blueprint's work items are falsified by the codebase; one flagship item is diagnosed at the wrong
layer; and the most urgent live defect appears in neither document.

The forward-discipline praise is accurate and was confirmed mechanically:
`chat/data/deduction_serve_ledger.json` holds 25 sealed bands / 18,000 cases / `wrong=0`, and
`evals/capability_index/baseline.json` reports breadth 13, `wrong_total=0`,
`assert_mode_valid=true`. What follows concerns only what the assessment proposed to do *next*.

## 1. The live defect neither document names

**Workbench records a proved deduction answer as ungrounded.** Verified by execution, not by
reading:

```
_run_chat_turn('If it rains then the ground is wet. It rains. Therefore the ground is wet.')

surface          = 'Given: if it rains then the ground is wet; it rains.
                    Your premises entail: the ground is wet.'
grounding_source = 'none'                    <- TurnEvent carried 'deduction'
epistemic_state  = 'epistemic_state_needed'
```

The chain:

1. `workbench/api.py:646` — the live HTTP chat route calls `_run_chat_turn(prompt)`.
2. `workbench/api.py:773` — constructs a bare `ChatRuntime()`, i.e. `DEFAULT_CONFIG`.
3. `core/config.py:397` — `deduction_serving_enabled: bool = True` (ratified ON, 2026-07-24).
4. `chat/runtime.py:1748-1757` — the composer commits and stamps
   `TurnEvent.grounding_source = "deduction"`.
5. `workbench/api.py:714-719` — `_coerce_grounding_source` whitelists
   `{pack, teaching, vault, partial, oov, none}` and returns `"none"` for anything else.

`workbench/api.py` contains no occurrence of `"deduction"` or `"curriculum"`.

**Scope of the falsification — one field, not two.** `workbench/api.py:818` prefers
`TurnEvent.epistemic_state` over the grounding-source fallback, and the runtime stamps
`epistemic_state_needed` for the unregistered label. That is honest. So `grounding_source` is
falsified; `epistemic_state` is not.

The asymmetry is the useful part: the *unregistered* path degrades honestly
(`epistemic_state_needed` — "this label needs determination"), while the *hand-copied whitelist*
asserts a falsehood (`none` = ungrounded). The coercion is strictly worse than doing nothing.

**This inverts the assessment's reading.** `chat/runtime.py:477-481` argues the unregistered
literal is "inert today" because "core chat REPL turns do not flow through Workbench's
`CognitivePipelineRecord` path." True, and irrelevant — the traffic flows the other way. Workbench
turns flow through the *deduction* path. That comment has been stale since the flag was ratified ON.

## 2. Falsified items — no session should be spent on these

| Claim | What the code says |
|---|---|
| `parents[n]` audit is "a 30-minute grep with significant payoff" | **Audit run.** 168 `Path(__file__).parents[n]` sites repo-wide; **0** resolve outside the repo root. The `derived_close_proposals.py` bug was isolated. |
| Realizer-guard exemption is undocumented at the guard site | **False.** Documented at *both* sites — `chat/runtime.py:2371-2375`, `:3007-3010` — with the invariant and a worked example (`pack open=VERB` rejecting "the door is not open"). |
| T12 weekly-ledger entry is "completely missing" | **False.** `docs/analysis/weekly-audit-2026-07-22-stragglers-todo.md:170` — an open pattern-watch item. The claim came from grepping commit messages only. |
| `assert_corpus_sound()` has one impl; a second subject must reimplement it | **False.** `evals/curriculum_serve/runner.py:71` is already `assert_corpus_sound(domain, cases)`, and `build_report()` calls it plus `assert_provenance` plus `assert_anti_recall_coverage` unconditionally (`:105-108`). Structural, not discipline-based. |
| Manual promotion sweeps need an automated Promotion Oracle | **Already exists.** `docs/research/tier-s-housekeeping-2026-07-24.md` §3: "*not a one-time manual check… The sweep's proof is the passing gate, not a separate pass.*" `ds-mem-0020` surfaced *as* a lane failure. |
| `accrue_realized_knowledge` is "dark," a closing temporal-consistency window | **Misread** — *and this correction was itself wrong on one point; see the note below.* `core/config.py:316-321` gates **session** memory and is `False` for eval/one-shot runtimes. A deployment profile, not an epistemic debt clock. |
| Cross-subject proof could "emerge accidentally" | **Structurally impossible.** `curriculum_surface.resolve_domain` requires both terms in one subject's vocabulary and refuses `ambiguous_reading` rather than picking. Deduction has no subject notion at all. |

## 3. The flagship item is diagnosed at the wrong layer

The blueprint states that v5-VP and v6-EX "produce intermediate proof chains" that
`render_entailment_verb` "drops to print a terminal verdict."

`generate/proof_chain/entail.py:125-190` decides entailment by canonicalizing
`(P1 & … & Pn) -> Q` and asking `is_tautology` — a BDD equivalence check, not a derivation.
`EntailmentTrace` (`:79-99`) carries `outcome`, `reason`, and five canonical BDD node keys —
opaque hashes. There are no intermediate steps in the object. The renderers (`render.py:62+`)
already emit every premise plus the verdict.

Nothing is dropped because nothing exists to drop. Multi-step articulation is **engine** work —
proof-term extraction, or a derivation calculus over the ROBDD — with a real soundness surface.
Scoping it as "design the trace object, then write the renderer" would produce a renderer with
nothing to render.

## 4. The "second subject arena" premise

The blueprint orders its work as "harden lateral contracts before spinning up the second subject
arena." `docs/research/curriculum-volume-quantification-2026-07-24.md` §2 measures otherwise:
**11 bands across 4 subjects already route questions today**, every one is 24×–73× short of the
entailed-bucket floor, and the document concludes in bold that **no served subject has a family
close enough to flag as "next."**

There is no subject to spin up; the wiring is done. What physics has and the others lack is
ratified content volume. That makes the Ratification Ceremony not a third-tier item but the
binding one.

## 5. Confirmed, but materially rescoped

- **`missing_ok`** — real and narrow. Exactly one production call site passes `True`
  (`chat/curriculum_serve_license.py:46`), correctly, because
  `chat/data/curriculum_serve_ledger.json` does not exist yet. Default is `False`. A small
  manifest closes it.
- **Telemetry spine** — the proposed fix is unimplementable as written. `pipeline.py:799` hashes
  `hash_surface`; `runtime.py:1212` stamps the *served* surface; `TurnEvent` never carries
  `hash_surface`, so `trace_hash` is not merely divergent from telemetry but **not reconstructable
  from it**. Both documents also miss the larger sibling flagged in-code at `runtime.py:1235-1241`:
  the external telemetry sink still receives the **pre-override** event (audit-ledger R7).
- **Discovery-yield stratification** — ~4× the implied cost. `teaching/discovery_yield.py:67-70`
  reads a single monotonic `turn_count`; there is no per-source counter to stratify on. Requires
  new persisted manifest fields. The denominator has always included pack/vault/none turns —
  deduction adds to a pre-existing dilution rather than creating it.
- **Band-level capability index** — `index.py` scores via `coverage_geomean`. Adding 25 near-1.0
  band entries would mechanically inflate the headline `capability_score`, against the index's own
  anti-gaming property. Needs a scoring decision before a schema change.
- **`engine_refused` as a standing gate** — `tests/test_vocab_trigger_instrument.py` is already in
  the `deductive` suite. The instrument is defined as a before/after admissions counter; promoting
  a measurement to a gate means pinning an expected value, which is precisely the stale-exact-pin
  failure mode the assessment's own test-freshness item exists to prevent. The two requests collide.
- **`_prior_surface`** — mostly false as diagnosed. `pipeline.py:719` sets
  `_prior_surface = hash_surface`, which *is* updated in lockstep with the logos-morph override
  (`:526`) and the speculative marker (`:676`); the realizer guard runs upstream. The register
  exclusion is deliberate and documented (`:715-717`). A pin is still cheap insurance.
- **Test freshness** — the cited instance was already fixed in `a4d6868` with a docstring
  explaining the failure mode. Remaining `== (` assertions in `tests/test_cli_test_suites.py` pin
  argv prefixes, which is appropriate. A repo-wide de-pin sweep is low yield.
- **Math Phase 4.2 case-first** — fully accurate, and the one strategic item both documents get
  right. Adopt `docs/research/math-reader-phase-4-1-status-2026-07-24.md` verbatim.

## 6. The Apple Silicon / MLX substrate blueprint

A companion document proposes five bare-metal optimizations. Both of its foundational premises are
contradicted by this repo's own measured report.

- *"MLX executes tensor operations on the Neural Engine"* is `README.md:82` — a design aspiration.
  `evals/reports/apple_uma_mechanical_sympathy_latest.md` §10 explicitly disclaims it: "No MLX
  semantic-backend claim. No Neural Engine acceleration claim. No CoreML acceleration claim."
  MLX appears in exactly two files, both under `benchmarks/`. **No MLX in any runtime path.**
- *"Rust remains the incumbent native algebra backend"* — `algebra/backend.py:6-8`: "Pure Python is
  the deterministic default. Rust is an explicit opt-in backend via `CORE_BACKEND=rust`." The
  benchmark run records `core_rs import: False`, `using_rust(): False`, status `python_fallback`.

The algebra is running in pure Python/NumPy. The document proposes GPU shader work for a layer
that has not switched on the CPU kernel it already wrote — `core-rs/src/cl41.rs` already hardcodes
the Cl(4,1) Cayley table at compile time via bitmask anticommutation-parity and metric contraction
(`[u8;1024]` index + `[i8;1024]` sign), which is its own recommendation 1 minus the GPU.

> **Corrected 2026-07-25 by measurement — see
> `cga-hot-path-measurement-2026-07-25.md`.** This section originally argued that
> `versor_condition` (3 calls/turn × the benchmark's `p50 = 0.536 ms`) was "~10× the entire proof
> latency". That was wrong: it multiplied an *isolated microbenchmark* by a call count and
> compared the product against `FrameVerdict` TTFV, which is a single verdict's latency rather
> than a turn's. Measured directly, `versor_condition` is **0.448 ms/turn against a 200 ms turn —
> 0.22%**, so switching the Rust backend on recovers essentially nothing through that path.
>
> The profile does show CGA dominating (~73% of turn time), but through
> `cga_inner` → `geometric_product` (33,986 calls/turn) in nearest-neighbour and salience search,
> not through the versor invariant. Both this assessment and the hardware blueprint aimed at the
> wrong function. The correct target, and why the obvious shortcut is not bit-safe, are in the
> measurement document.

| Proposal | Verdict |
|---|---|
| Rust typestate (`UnverifiedClaim` → `VersorClaim`) | **Adopt.** No `PhantomData`/typestate anywhere in the tree — greenfield, not "recently explored." The only proposal with zero determinism cost, and it needs no GPU. |
| SoA memory layout | **Resequence.** AoS confirmed (`vault.rs:111,149`). But the copy truth-table names the marshalling copy as the cost (`extract_f32_slice`, `lib.rs:348`), while batch paths are already zero-copy (`lib.rs:282`). SoA pays off only after zero-copy scalar bindings. |
| Custom sparse `.metal` Cl(4,1) kernel | **Premature.** The table exists. Rust is off by default *for determinism*; a GPU kernel makes determinism harder. Per `AGENTS.md:276` the `ubuntu-latest:host` label is native macOS on one machine, so a shader would have a single validation host against a local-first merge bar. |
| MLX lazy kernel fusion of the versor invariant | **Blocked on doctrine.** JIT fusion reassociates float ops; `versor_condition < 1e-6` is a non-negotiable (`algebra/versor.py:100`) and `core-rs/tests/test_crdt_hash_parity.rs` pins bit-exact parity. Needs a ratifying ADR, not a ticket. |
| bfloat16 asymmetric precision routing | **Reject as specified.** bf16 ε ≈ 7.8e-3 — four orders coarser than the 1e-6 gate; upcasting inside the shader cannot recover bits lost at storage. `cga.rs:embed_point_raw` computes `0.5*(r²∓1)`, cancellation-prone at bf16 for r ≈ 1 — exactly the unit-normalized regime. |

The actionable question the document missed: **why is `CORE_BACKEND=rust` not the default?**
Establish whether `core_rs` still holds bit-exact parity. (Attempted 2026-07-25 and **blocked**:
`cargo` cannot reach `static.crates.io` under the sandbox network policy. The question stays open
— the measurement above just removes the urgency the performance argument was supplying.)

None of this is on the critical path of the arc that just closed — FrameVerdict TTFV is 0.151 ms
with `producer=proof_chain.entail`, and the deduction/curriculum serving path is pure-Python ROBDD
that never touches CGA.

## 7. Resulting order of work

1. **Stop the provenance falsification.** Red test; register `deduction`/`curriculum` in
   `core/epistemic_state.py` + the TS contract in one commit (`enumCoverage.test.ts` already forces
   atomicity); derive `_coerce_grounding_source`'s whitelist from the enum rather than a hand-copied
   set; delete the stale comment at `chat/runtime.py:471-481`.
2. **Build the Ratification Ceremony** — `proposal → chain record → corpus commit → arena queue
   entry → ledger reseal`, reusing `core/ratified_ledger.py`'s sealers and the `core proposal-queue`
   CLI, with the vocab-trigger admissions delta as the acceptance metric.
3. **Batch the cheap closures** — `missing_ok` manifest; telemetry contract documented honestly
   plus audit-ledger R7 raised; the `_prior_surface` pin; deductive suite into the pre-push gate;
   ADR domain index and an arc-close brief template.
4. **Math Phase 4.2 case-first**, in parallel — cases `0000`/`0001`/`0148`/`0082`, no
   `NEUTRAL_COUNT_VERBS` growth (ADR-0251).
5. **Substrate track**, behind the above — Rust-default parity question, then typestate.

Deferred with stated reasons: multi-step articulation (re-scope as engine work), yield
stratification (blocked on manifest counters), band-level index (blocked on a scoring decision),
`engine_refused` gate (bucket empty), cross-subject ADR (`resolve_domain` fails closed).

Relates to [[project-generalization-arc]].
