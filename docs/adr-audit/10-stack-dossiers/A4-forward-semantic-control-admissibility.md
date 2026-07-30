# Stack dossier — A4 · Forward Semantic Control & Admissibility

**Zone(s):** M3 · `L4-recognition` (per `docs/assessment/02-layer-taxonomy.md` §3–4); ties directly to Candidate Register **CR-1** (attention / allocation, in-turn) | **Tier:** A
**Member ADRs:** ADR-0022, ADR-0023, ADR-0024, ADR-0025, ADR-0026, ADR-0046 (read in that order — sequential decision chain)
**Dossier author:** Claude Opus 5 (Batch 1, Phase 3) | **`verified_at` SHA:** `cbfc8ccb`
**Prior evidence adopted, not re-derived:**
- `docs/assessment/02-layer-taxonomy.md` §5 **CR-1** — cites ADR-0024/0025/0026 by number as the *only* partial existence found for an attention/allocation layer. This dossier is load-bearing evidence for that open ruling item (see §3).
- `docs/assessment/20-component-cards/attention-allocation.md` — the live CR-1 mechanism (salience→attention), `live-serving`, fitness `strained`; establishes the interaction contract: "salience/attention prune *candidates*; admissibility … then judges them. Two allocation stages, only the second governed by ADRs."
- `docs/assessment/10-layer-cards/M3-comprehension-reasoning.md` — M3 `partial-wiring-debt` / `strained`; **INV-34** ("no PASSTHROUGH in the intent ratifier") is adopted as a settled constraint.
- `docs/assessment/30-gap-register.md` — **G-14** (CR-1 attention governance, the one-page ADR), **G-20** (`refusal_reason` materialisation, "anticipated by the ADR-0024 chain"), **G-24** (the perception-arc diagnosis: geometry participates in exactly two cognitive mechanisms, "salience→attention (bypassed by every licensed lane)").
- `docs/assessment/31-hindrance-audit.md` — **H-3** (typed refusal discarded at the `str` boundary), **H-5** (underived constants; cites `admissibility_margin δ=0.4` as the *in-repo counterexample standard* — positive fitness for ADR-0026).
- `docs/assessment/01-phase0-ground-truth.md` §7 **Finding 0-F** + `docs/research/cga-hot-path-measurement-2026-07-25.md` — the ~73% `cga_inner`→`geometric_product` hot-path measurement.
- `docs/census/cbfc8ccb…/` — `stale-references.jsonl`, `docstring-drift.jsonl`, `suite-membership-gap.jsonl`, `magic-numbers.jsonl`.
- **ADR-0047 and ADR-0058** are *not* members of this stack but are its decisive fitness evidence; their findings are adopted, not re-derived.

---

## 0. Why this is one stack

One concept, introduced once and refined four times, then given a new source.

ADR-0022 introduces `AdmissibilityRegion` — a typed object that bounds which manifold region a turn's field walk may propagate into — and applies it as a **candidate-set prefilter** at the `propose()` / `generate()` boundary. ADR-0023 adds no new runtime semantics; it is pure proof apparatus (per-transition trace, hash fold, ratification accounting, single-variable ablation) whose job is to show the region, and not some confound, caused the answer. ADR-0024 pushes the check *inside* the walk — per-step, per-candidate, with re-selection on rejection — which is the first genuine semantic change since 0022. ADR-0026 replaces 0024's absolute score gate with a **relative** ranked-with-margin gate, because Phase 4 characterization proved blade norms vary ~10× so no single static threshold is geometrically meaningful. ADR-0025 (written *after* 0026, despite its number) closes 0024's explicit deferral by adding the orthogonal **rotor-side** gate — does the rotor's effect on the field stay in the frame's positive cone — in a sibling module, after reversing its own draft's architectural recommendation.

ADR-0046 is the odd member and belongs here for a precise reason: it changes nothing about the admissibility contract and everything about where regions *come from*. Where 0022–0026 build regions from intents and relation chains, 0046 converts a `PropositionGraph` into a region before `generate()` runs — making the graph a forward constraint rather than a post-hoc description.

The arc in one line each: **0022** the mechanism · **0023** the proof it is causal · **0024** the mechanism moved inside the loop · **0026** the gate made scale-invariant · **0025** the orthogonal rotor axis · **0046** a new source for the same object.

## 1. Stack-level claim

> The proposition graph and the classified intent are *forward operators on field propagation* — they bound where the walk may go before any token is produced — and when no admissible transition exists the turn refuses honestly rather than relaxing into a fluent, ungrounded surface.

This is falsifiable, and the stack pre-registered its own criterion. It has been measured **twice, on two different populations, with opposite results.** Both measurements are honest; they are not in conflict; the stack's own documents record both.

- **Pre-registered criterion (ADR-0023 §Lane metrics):** `region_only_gap` — same runtime, same vocab, same field state after primes, same persona, same prompt; the *only* varying input is `region=None` vs `region=AdmissibilityRegion`. The region is causally load-bearing iff this gap is materially > 0.
- **Measurement performed / already available:**
  - **Purpose-built lanes — GO.** `evals/forward_semantic_control/results/`: `region_only_gap = 1.00` (0/5 → 5/5 on chain-dependent cases, ADR-0023); `phase3_v2_report.json` `mechanism_isolated = true`, `boundary_decoy_rate = 1.00`, `rejection_traced_rate = 1.00`; `phase5_report.json` 20/20 under both threshold and margin across 5 stratified failure-mode families; `phase6_demo_report.json` `all_three_conditions_pass = true`. Re-verified green at this SHA (125 tests, §5).
  - **Production cognition lane — NULL.** ADR-0047's A/B on the 13-case public cognition split: `intent_accuracy`, `surface_groundedness`, `term_capture_rate`, `versor_closure_rate` **byte-identical** with the constraint flag flipped, while 6/13 cases produced a non-trivial constraint label. ADR-0058 promoted that null result to a *deliberate, pinned invariant* and declined to flip the default.
  - **Default serving path — the mechanism does not execute at all.** Measured fresh at `cbfc8ccb` (§3, `AA-A4-1`): across three default-config `ChatRuntime.chat()` turns, `check_transition`, `check_margin`, `rank_candidates_by_blade`, `filter_candidates`, `check_rotor_admissibility` and `build_graph_constraint` were each called **zero** times.
- **Verdict:** **GO on the mechanism, NO-GO on the integration — and the two are not the same claim.** The narrow claim ("an `AdmissibilityRegion`, when supplied, deterministically and traceably changes which token is emitted, and refuses honestly when it cannot") is **proven**, by a cleaner single-variable ablation than most of the repo carries. The broad claim in the stack's own framing ("semantic structure becomes causally active inside propagation", ADR-0022 §Context) is **not in effect**: no production configuration supplies a region, the one flag that would has a ratified null-lift, and the rotor axis has no producer at all. The distinction matters because ADR-0022 wrote the broad claim as its purpose and the lanes measure the narrow one.

Note the discipline this stack applied to itself, which is genuinely creditable and should survive any downstream triage: it *measured its own null result* (ADR-0047), *refused to widen `top_k` until the failure went away* (ADR-0047 §Why opt-in), *declined to flip its own default on the strength of a mechanism lane* (ADR-0058), and *pinned the null as a regression test*. That is the sabotage test run by the authors on their own work, before this audit existed.

## 2. Per-ADR sections

### ADR-0022 — Forward Semantic Control

**Audit ID (if a numbering collision):** — | **Family (if phased):** ADR-0024 chain (Phases 1–6, `docs/PROGRESS.md`)
**Zone / stack:** M3 · `L4-recognition` / A4 | **Tier:** A
**ADR status (as recorded in the file):** Accepted (2026-05-17 — all five TBDs addressed; all eight acceptance gates met) | **ADR date:** 2026-05-17
**Card author:** Claude Opus 5 | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary

- **Decision made:** The proposition graph becomes a forward operator on field propagation rather than a backward structure over walk output. It yields an `AdmissibilityRegion` (relation constraint + slot constraints + rotor constraints) that bounds the manifold region the field may propagate into; propagation must satisfy it or fail honestly; and the intent classifier is itself field-coupled via regex-seed + field-ratification.
- **Alternatives explicitly rejected:** templates / direct token choice / surface authoring / statistical candidate scoring (§1); silently relaxing the constraint to rescue a turn (§2); for the intent oracle (TBD-1) — the pure-projection oracle (requires a frame-relation manifold the runtime does not carry) and defer-to-v2 (leaves the load-bearing oracle as regex).
- **Artifacts the ADR claims will exist:**
  - `generate/admissibility.py` — `AdmissibilityRegion` (frozen, slots)
  - constructors `unconstrained`, `region_from_frame_relation`, `region_from_relation_chain`
  - composition `intersect` (set intersection on indices, outer product on blades with zero-blade neutral, sandwich conjugation on frame versors)
  - predicate `check_transition` → typed `AdmissibilityVerdict` carrying the failing region's label
  - bridge `filter_candidates` preserving empty intersections as a 0-length array
  - `generate/intent_ratifier.py` — `ratify_intent(intent, prompt_versor, *, vocab, threshold)` → `RatifiedIntent` with outcome **RATIFIED / DEMOTED / PASSTHROUGH**
  - `generate/intent_ratifier.py` — `region_for_intent(intent, *, vocab)` building a region from grounded anchors
  - `generate/proposition.py::propose()` consumes a region; empty admissible set raises `ValueError`
  - `generate/stream.py::generate()` consumes a region; region intersects with language/salience candidates
  - `core/cognition/pipeline.py` step 1b.i FIELD-RATIFY
  - `tests/test_forward_semantic_control.py` (25 tests), `tests/test_intent_ratifier.py` (8 tests)
  - `evals/forward_semantic_control/` lane (contract, cases, runner)
  - *Explicitly not changed:* `algebra/versor.py`, `vault/store.py`, `teaching/*`, `field/propagate.py`

#### 2. Implementation cross-reference

| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `AdmissibilityRegion` | yes | `generate/admissibility.py:75` | `@dataclass(frozen=True, slots=True)` as specified |
| `unconstrained` | yes | `generate/admissibility.py:163` | |
| `region_from_frame_relation` | yes | `generate/admissibility.py:173` | |
| `region_from_relation_chain` | yes | `generate/admissibility.py:196` | |
| `intersect` (TBD-2) | yes | `generate/admissibility.py:296` | All three composition rules present: `_intersect_indices:231`, `_compose_blades:252` (zero-blade neutral), `_compose_frame_versors:268` (routes through `algebra.backend.versor_apply`, exactly as claimed) |
| `check_transition` / `AdmissibilityVerdict` | yes | `generate/admissibility.py:352` / `:336` | Verdict carries `region_label` + `reason`, so the failure surface can name the blocking constraint |
| `filter_candidates` | yes | `generate/admissibility.py:646` | Empty intersection preserved as 0-length array (`:249` `np.intersect1d`), not relaxed to `None` — as promised |
| `ratify_intent` | yes | `generate/intent_ratifier.py:199` | |
| `RatificationOutcome.PASSTHROUGH` | **no** | `generate/intent_ratifier.py:85-88` | Enum has **only** `RATIFIED` / `DEMOTED`. Excised under INV-34; `:152` comment reads "…after PASSTHROUGH excision". See `AA-A4-3` |
| `region_for_intent` | yes (uncalled) | `generate/intent_ratifier.py:278` | **No non-test caller anywhere in the repo.** See `AA-A4-2` |
| `propose()` consumes region | yes | `generate/proposition.py:27` | imports `AdmissibilityRegion`, `filter_candidates` |
| `generate()` consumes region | yes | `generate/stream.py:279` | `region: AdmissibilityRegion \| None = None` |
| region ∩ language/salience candidates | yes | `generate/stream.py:342-343` | `filter_candidates(region, candidate_indices)` after `_intersect_candidates(language, salience)` at `:326` |
| empty set → honest refusal | yes | `generate/stream.py:352-357` | Raises `InnerLoopExhaustion` (⊂ `ValueError`), `step_index=-1` marking the pre-walk site |
| pipeline step 1b.i FIELD-RATIFY | yes | `core/cognition/pipeline.py:296` | `self._ratify_intent(seeded_intent, field_state_before)` → `:1073` `ratify_intent(...)` |
| `tests/test_forward_semantic_control.py` | yes | 10,828 bytes | Green at this SHA |
| `tests/test_intent_ratifier.py` | yes | 6,669 bytes | Green at this SHA |
| `evals/forward_semantic_control/` | yes | `contract.md`, `runner.py`, `dev/`, `public/`, `results/` | A discoverable lane (`evals/framework.py:229 get_lane` requires exactly `contract.md` + `runner.py`) |
| `algebra/versor.py` unchanged | yes | — | No admissibility import; no `unitize_versor`/`normalize_to_versor` call in `generate/admissibility.py`. Verified by grep, as the ADR claimed to verify by inspection |
| `vault/store.py` unchanged | yes | — | No ANN/HNSW introduced |
| `field/propagate.py` unchanged | yes | — | No region-aware variant added; confirmed |

**Build axis:** **full** — every named artifact exists at the named location with the named shape, and the four "not changed" commitments hold under grep. Two fidelity defects (`region_for_intent` uncalled; `PASSTHROUGH` excised) are recorded in §5, not §2, because the artifacts do exist.

#### 3. Liveness / integration

- **Call chain, traced.** `chat/runtime.py` has two `generate()` call sites: `:2171` passes `region=None` literally; `:2850` passes `region=forward_region`, which is initialised `None` at `:2818` and only assigned when `self.config.forward_graph_constraint` is true (`:2823-2824`) — and that flag defaults `False` (`core/config.py:64`). The cognition pipeline consumes the region *trace* (`pipeline.py:837-839`) but never constructs a region. `region_for_intent`, the ADR's own intent→region constructor, has no non-test caller.
- **Sabotage test — performed, not reasoned.** Instrumenting every admissibility entry point and running three default-config `ChatRuntime.chat()` turns yields `check_transition=0, check_margin=0, rank_candidates_by_blade=0, filter_candidates=0, check_rotor_admissibility=0, build_graph_constraint=0`. Removing the entire region machinery would change **nothing observable** on the default serving path. Under the charter's own words: *this is a decoration finding, not a minor caveat* — for the region half of the ADR.
- The ratifier half is a different verdict. Measured on the pipeline: `ratify_intent` fires once per turn, returns `ratified`, and its outcome is carried on `CognitiveTurnResult`. It is default-on, has no flag, and is pinned by INV-34. Deleting it would change intent routing.
- **Liveness axis:** **wired-but-unreached** (region machinery) / **live** (intent ratifier). One ADR, two mechanisms, two honest verdicts — recorded split rather than averaged, because averaging would hide both.

#### 4. Design fidelity — pillars and axioms

| Pillar | Honors / Tension / Violates | Citation (ADR clause + pillar text) |
|---|---|---|
| I. Mechanical Sympathy | **Honors** | §"Not changed" keeps region enforcement at the candidate-set boundary explicitly so "the hot-path rotor application [is] identical to the unconstrained case and preserves Rust parity by construction"; §Acceptance gate 8 measures the cost (~2.8% wall-clock) rather than asserting it |
| II. Semantic Rigor | **Honors** | §"What this ADR is NOT" fixes four terms against drift by naming their negations: not symbolic NLP, not a probability model, not a new closure invariant, not a Rust prerequisite. `AdmissibilityVerdict` carries `region_label` so a refusal names *which* constraint fired |
| III. Third Door | **Honors** | §Context refuses both visible options — "graph authors the sentence" (symbolic NLP) and "graph describes the output" (status quo) — and builds the third: the graph bounds *where the field may go*, authoring nothing |

| Axiom | Honors / Tension / Violates | Citation |
|---|---|---|
| 1. Geometry-First | **Honors** | The region is a blade + versor + index set; selection within it "remains exact CGA inner product — no learned ranking, no sampling" (§1) |
| 2. Field-State | **Honors** | The constraint is a *boundary on a field region*, not a filter over object lists; §2 frames admissibility as a manifold-subset bound |
| 3. Propagation-over-Mutation | **Honors** | Region is computed once and consulted; §"Not changed" forbids a region-aware `propagate_step` variant precisely to keep the propagation loop unbranched |
| 4. Dual-Correction | **Tension** | The forward operator ships with a *refusal*, not a *conjugate*. Honest refusal is a fail-closed valve, not a corrective counterpart — nothing in the stack derives a region *back* from an emitted surface to correct the next region. Legitimate for v1, but the axiom is unmet rather than n/a |
| 5. Reconstruction-over-Storage | **Honors** | The region stores an index set + one blade + one versor + a label; the trace stores decisions, not states |
| 6. Compilation-Last | **Honors** | Pure numpy over the existing algebra; no kernels, no tables, no learned structures |
| 7. Reality-over-Inheritance | **Honors** (as written) | §Acceptance gate 5 audits explicitly for reintroduced anti-patterns. The axiom's *bite*, however, lands on this ADR later — see §7 and `AA-A4-1` |

#### 5. Build fidelity — does the code match the decision?

Three divergences, in descending severity.

1. **`PASSTHROUGH` was excised, and neither this ADR nor ADR-0023 was amended.** §Decision item 3 specifies three outcomes and argues at length that PASSTHROUGH "is *not* a license to silently accept an unverified intent" — a considered position. `RatificationOutcome` now carries two members (`generate/intent_ratifier.py:85-88`), pinned by `tests/test_linguistic_governance_phases.py::test_no_passthrough_in_ratifier` under INV-34. The later ruling is almost certainly the better one (it removes the escape hatch), but ADR-0022 still reads as though PASSTHROUGH exists, and ADR-0023's gate-3 metrics still measure it. `AA-A4-3`.
2. **`region_for_intent` is built and unreached.** It is the ADR's designed bridge from a ratified intent to a region — the mechanism by which §Decision item 3 was supposed to feed §Decision item 1. Without a caller, ratification and admissibility are two features that share a file and nothing else. `AA-A4-2`.
3. **Document defect:** the ADR's `## Code impact` section contains a duplicated `### New` and `### Not changed (explicit)` pair (`:180-250` landed text, then `:252-286` the pre-landing draft text repeated verbatim-ish). Harmless to code, but a reader diffing "claimed vs landed" hits two inconsistent lists. `AA-A4-11`.

Everything else matches, including the fiddly parts: empty intersections really are preserved rather than relaxed; frame-versor composition really does route through `algebra.backend.versor_apply` rather than reimplementing the sandwich; and the four "not changed" files really are untouched.

**Build-fidelity axis:** **partial drift** — the region algebra matches the decision exactly; the intent-coupling half of the decision is one excised enum member and one uncalled function away from what was written.

#### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs

- **Contradicts `Whitepaper.md`?** No. Axiom 4 (Dual-Correction) is under-served rather than contradicted (§4).
- **Contradicts `Yellowpaper.md`?** No — it defers to the Whitepaper for axioms and this ADR introduces no formal object that competes with it.
- **Other ADRs.** Depends on 0018/0019/0021 as declared; 0019's no-ANN commitment is explicitly preserved and verified. **Superseded in part by INV-34** (`AGENTS.md:133`) on the PASSTHROUGH question — an unreconciled supersession, since INV-34 does not cite ADR-0022 and ADR-0022 does not record the amendment. Extended cleanly by 0023/0024/0025/0026; given a new region source by 0046. Its §"Not changed" pledge on `field/propagate.py` is honored by every later member — notably ADR-0025 §Option C re-litigates and re-affirms it.
- **Continuity axis:** **unreconciled contradiction** — narrowly, on PASSTHROUGH. Everything else in the citation graph is clean.

#### 7. Necessity / generality

1. **Necessity.** The *idea* is necessary: a bounded cognitive system must constrain where it may go, and CORE's alternative (unconstrained nearest-neighbour walk) is exactly the "sequence sampling" the architecture rejects. The *instance* is not currently load-bearing: measured zero calls on the default path (§3). A mechanism can be conceptually necessary and operationally absent, and this is that case.
2. **Reducibility.** Not reducible to L0/L1. `algebra/` supplies `cga_inner`, `outer_product`, `versor_apply`; the region composes them but adds something the algebra layer does not have and should not have — *pack-derived semantic provenance* (`RegionSource`, `label`) attached to a constraint. ADR-0025 makes this argument explicitly and correctly (admissibility ≠ closure; putting a semantic test in `algebra/` creates the structural temptation to *repair* inadmissible rotors, which CLAUDE.md forbids). **The relevant reduction is sideways, not downward** — see item 3.
3. **Extensibility.** `AdmissibilityRegion.allowed_indices` and `AttentionPlan.allowed_indices` (`generate/attention.py:14`) are the same type, carry the same meaning, serve the same role, and are combined in `generate/stream.py` by the same intersection operator (`_intersect_candidates` at `:326`, then `filter_candidates` at `:343`). Three sources of one concept — language, salience/curvature, admissibility — with three vocabularies and no unifying owner. This is the primary consolidation pairing for `22-consolidation-report.md` and the sharpest input to the CR-1 ruling (§3, `AA-A4-5`).

**Necessity/generality axis:** **generalization-candidate** — the region is the best-typed and best-governed of the three `allowed_indices` producers, and is the natural shape for all three to consolidate *into*, not away from.

#### 8. Fitness / value

- **Purpose-built lane, positive:** `region_only_gap = 1.00` (ADR-0023 §Lane metrics) — the single cleanest one-variable ablation in the stack. Adopted, not re-derived.
- **Production lane, null:** ADR-0047's A/B — 0 Δ on all four cognition-lane metrics with the constraint engaged on 6/13 cases.
- **Cost, measured:** ~2.8% wall-clock at gate 8; later `evals/reports/cost_latest.json` showed the chain net-faster than the ADR-0022 baseline (ADR-0023 gate 6).
- **Not claimed anywhere it counts:** `evals/CLAIMS.md` contains **no** forward-semantic-control or admissibility claim at any tier. The lane exists, passes, and is cited by no claim — so nothing in the repo's claim ledger would fail if the mechanism regressed. `AA-A4-10`.
- The intent-ratifier half carries independent fitness: it is pinned by INV-34 and by `tests/test_linguistic_governance_phases.py`, and ADR-0023 gate 3 records that the ratification metric *itself* caught a real wiring bug (`runtime.vocab` vs `runtime.session.vocab`) on its first run — a measurement earning its keep.

**Fitness axis:** **mechanism proven, integration null, unclaimed** — cite `evals/forward_semantic_control/results/` (positive, unpinned) against ADR-0047 §Characterisation (null) and the absence from `evals/CLAIMS.md`.

#### 9. Findings raised

- `AA-A4-1` 🟡 — Region machinery measured at zero calls across three default-config turns; the ADR's broad claim ("semantic structure becomes causally active inside propagation") is not in effect on any serving path. (§3)
- `AA-A4-2` 🟡 — `region_for_intent` has no non-test caller; the ADR's own intent→region bridge is unreached, leaving ratification and admissibility structurally unconnected. (§2, §5)
- `AA-A4-3` 🟡 — `PASSTHROUGH` excised from `RatificationOutcome` under INV-34; ADR-0022 §Decision item 3 and ADR-0023 §Decision item 3 both still specify it. Unreconciled supersession. (§5, §6)
- `AA-A4-5` 🔵 — Three producers of `allowed_indices` (language / salience / admissibility) composed by one operator with no owning concept. Consolidation cluster + CR-1 feeder. (§7)
- `AA-A4-10` 🟢 — No admissibility claim in `evals/CLAIMS.md`; lane reports carry no SHA or timestamp pin. (§8)
- `AA-A4-11` 🟢 — ADR-0022 `## Code impact` contains a duplicated `### New` / `### Not changed` pair with inconsistent content. (§5)

#### 10. Evidence sources actually consulted

Read in full: the ADR; `generate/admissibility.py` (669 lines); `generate/graph_constraint.py`; `generate/rotor_admissibility.py`; `generate/attention.py`; `generate/salience.py`; `docs/assessment/02-layer-taxonomy.md`; `20-component-cards/attention-allocation.md`; `10-layer-cards/M3-comprehension-reasoning.md`; ADR-0047; ADR-0058. Read in part: `generate/stream.py:250-360` and the admissibility grep-map; `chat/runtime.py:2760-2880`; `core/cognition/pipeline.py` (grep); `generate/intent_ratifier.py:80-110, 199-300`; `core/config.py:35-64`; `core/cli_test.py:360-443`; `conftest.py:95-196`; `docs/specs/runtime_contracts.md` (grep); `docs/PROGRESS.md:10-45`; `evals/framework.py:220-240`. Executed: the six-entry-point instrumentation over three default-config turns (§3); `pytest` over 13 stack test files (125 passed). Grepped: `30-gap-register.md`, `31-hindrance-audit.md`, `evals/CLAIMS.md`, and five `docs/census/cbfc8ccb…/*.jsonl` sweeps.

---

### ADR-0023 — Forward Semantic Control: Proof Evidence

**Audit ID:** — | **Family:** ADR-0024 chain
**Zone / stack:** M3 · `L4-recognition` / A4 | **Tier:** A
**ADR status:** Accepted | **ADR date:** 2026-05-17 | **Extends:** ADR-0022
**Card author:** Claude Opus 5 | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary

- **Decision made:** Five evidence-strengthening changes that add *no* runtime semantics — same-path ablation, per-transition admissibility trace folded into the deterministic trace hash, ratification accounting, `region=None` instrumentation, and lane expansion with adversarial distractors — so that "the region caused this answer" becomes inspectable and replayable rather than asserted.
- **Alternatives explicitly rejected:** relying on the pipeline-vs-runtime integration leg alone (retained as corroboration, not as proof); introducing mutation/normalization/repair on the trace path; using PASSTHROUGH as a fallback for failed ratification; fail-closing `region=None` in production (deferred, observation only).
- **Artifacts the ADR claims will exist:**
  - `generate()` returns `admissibility_trace: tuple[AdmissibilityTraceStep, ...]` recording per step: region label, candidates before/after filtering, selected destination, typed verdict
  - `CognitiveTurnResult.admissibility_trace_hash`, folded into `compute_trace_hash`
  - `hash_admissibility_trace`
  - `CognitiveTurnResult` carries the `RatificationOutcome`
  - lane metrics `ratified_rate` / `demoted_rate` / `passthrough_rate` / `passthrough_on_scored`
  - `CognitiveTurnResult.region_was_unconstrained: bool`
  - runner exposes `_run_region_ablation`; metrics `region_only_constrained_rate` / `region_only_unconstrained_rate` / `region_only_gap`
  - `evals/forward_semantic_control/dev/cases.jsonl` — 8 cases, 4 relation axes, 2 adversarial distractors
  - `tests/test_admissibility_trace.py` — same-trace-same-hash, mutation-changes-hash, reason-change-changes-hash, pre-ADR-0023 byte preservation

#### 2. Implementation cross-reference

| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `AdmissibilityTraceStep` | yes | `generate/admissibility.py:592` | Carries `step_index`, `region_label`, `region_source`, `candidates_before/after`, `selected_index/word`, `verdict` — exactly the claimed shape |
| `.canonical()` deterministic form | yes | `generate/admissibility.py:626` | Folds `rejected_attempts` **only when non-empty** (`:639`), preserving pre-ADR-0024 bytes as promised |
| `generate()` returns the trace | yes | `generate/stream.py:601, 640` | `admissibility_trace=tuple(admissibility_trace)` on the result |
| `hash_admissibility_trace` | yes | `core/cognition/trace.py` (imported `pipeline.py:31`) | |
| `admissibility_trace_hash` on result | yes | `core/cognition/pipeline.py:839, 881, 959` | |
| folded into `compute_trace_hash` | yes | `core/cognition/pipeline.py:31, 881` | |
| `RatificationOutcome` on result | yes | `core/cognition/result.py` | Confirmed live: measured `ratification_outcome = "ratified"` on a real pipeline turn |
| `region_was_unconstrained` | yes | `generate/stream.py:334`; `pipeline.py:838, 883, 961` | Measured `True` on the production pipeline path |
| `_run_region_ablation` | yes | `evals/forward_semantic_control/runner.py:140` | |
| `region_only_gap` etc. | yes | `runner.py` metrics block | |
| dev lane, 8 cases / 4 axes / 2 distractors | yes | `evals/forward_semantic_control/dev/cases.jsonl` | Rewritten pack-grounded by ADR-0024's Phase 1 addendum |
| `tests/test_admissibility_trace.py` | yes | 5,648 bytes | Green at this SHA |
| `passthrough_rate` / `passthrough_on_scored` | yes (**dead metric**) | `evals/forward_semantic_control/runner.py` | Computes the rate of an outcome the enum can no longer produce; always `0.0` / `false` by construction. See `AA-A4-3` |

**Build axis:** **full** — every claimed artifact exists at the claimed location, including the fiddly backward-compatibility conditions on the canonical form.

#### 3. Liveness / integration

- Unlike the region itself, the trace **is** on the live path. `generate/stream.py` appends an `AdmissibilityTraceStep` per step unconditionally (`:601`), with `region_label="unconstrained"` and `region_source="intent"` when no region is supplied (`:335-340`) — the ADR's stated design that "the trace shape is invariant across constrained / unconstrained walks". The pipeline hashes it into `admissibility_trace_hash` on every turn.
- **Sabotage test.** Removing the trace *would* change an observable: `admissibility_trace_hash` is a field on `CognitiveTurnResult` and is folded into `compute_trace_hash`, which is the repo's determinism spine. So this is not decoration. But the honest qualifier: on the default serving path the trace records a **constant** — every step logs the same `"unconstrained"` label, an unchanged candidate set, and a verdict of `reason="unconstrained"`. It is live apparatus faithfully recording that nothing happened.
- **Liveness axis:** **live** — with the caveat that its information content on the serving path is null, because the mechanism it exists to witness is not running (`AA-A4-1`).

#### 4. Design fidelity — pillars and axioms

| Pillar | Honors / Tension / Violates | Citation |
|---|---|---|
| I. Mechanical Sympathy | **Honors** | §Consequences names the cost it accepts ("per-step trace inflates the result object") and the mitigation (immutable tuples, hash only the canonical serialization); gate 6 measures the bench rather than asserting it |
| II. Semantic Rigor | **Honors** | The whole ADR exists to make one word — *caused* — mean something measurable. §Decision item 1 isolates the single varying input; §Context refuses to let "the mechanism exists" stand in for "the mechanism is the cause" |
| III. Third Door | **Honors** | Rejects both "trust the integration lane" and "rebuild the pipeline to isolate"; builds the same-path ablation that varies one object against a fixed runtime |

| Axiom | Honors / Tension / Violates | Citation |
|---|---|---|
| 1. Geometry-First | n/a | Evidence apparatus; introduces no geometric object |
| 2. Field-State | n/a | Observation only |
| 3. Propagation-over-Mutation | **Honors** | §Anti-patterns: the trace "must not introduce mutation, hidden normalization, or repair operators on the field path. It is observation only." Verified — `AdmissibilityTraceStep` is frozen/slots and `.canonical()` is pure |
| 4. Dual-Correction | **Honors** | This is the closest the stack comes to the axiom: the trace is the conjugate *evidence* operator to the forward constraint — every admissibility decision has an inspectable, replayable counterpart |
| 5. Reconstruction-over-Storage | **Honors** | Stores decisions and index arrays, not field states; hashes the canonical serialization rather than retaining it |
| 6. Compilation-Last | **Honors** | Tuples and dicts; no structures chosen for machine convenience |
| 7. Reality-over-Inheritance | **Honors** | The ADR's own gate 3 records that the measurement caught a bug in the thing being measured, and says so in the ADR rather than quietly fixing it |

#### 5. Build fidelity — does the code match the decision?

Matches, with one rot. The backward-compatibility conditions are implemented precisely as specified — `rejected_attempts` folded only when non-empty, `region_was_unconstrained` folded only when non-default — which is unusually careful and is what makes the ADR-0024 hash-preservation claim true rather than aspirational.

The rot is `AA-A4-3`'s downstream half: §Decision item 3 makes PASSTHROUGH-on-scored-cases a *proof obligation* ("scored causal cases require `ratified`; PASSTHROUGH is forbidden in those cases"), and gate 3 reports `passthrough_rate=1.00`-style metrics as evidence. With the enum member deleted, the runner still computes both metrics over a domain where they are constants. The obligation is now satisfied vacuously and the metric can no longer fail — an assertion that has quietly become decoration. Also recorded in the census: `docstring-drift.jsonl` flags `_run_region_ablation`'s docstring referencing a symbol `R` absent from its body, and `stale-references.jsonl` flags three `.json`-vs-`.jsonl` path references in `threshold_characterization.py:265-267`.

**Build-fidelity axis:** **matches** — the code implements the decision as written; the divergence is that reality moved under one of its metrics, which is `AA-A4-3`'s problem, not this ADR's implementation's.

#### 6. Continuity

- **Whitepaper / Yellowpaper:** no contradiction.
- **ADRs:** Extends ADR-0022 cleanly and explicitly hands inner-loop admissibility to ADR-0024 in writing, which ADR-0024 quotes back — an exemplary handoff. Its §Decision item 3 is the clause INV-34 later overrode (`AA-A4-3`). Its gate-4 commitment — "the lane runner asserts the constrained leg is *not* unconstrained" — is honored in the lane and inverted in production, where `region_was_unconstrained` is measured `True` on every pipeline turn.
- **Continuity axis:** **clean** — save for the shared PASSTHROUGH supersession already booked against ADR-0022.

#### 7. Necessity / generality

1. **Necessity.** Irreducible *as evidence*, and the stack's most transferable asset. Without ADR-0023 the chain would consist of a mechanism and an assertion; `region_only_gap` is what makes the ADR-0022 claim falsifiable at all — and, notably, what made ADR-0047's later null result legible rather than confusing.
2. **Reducibility.** No L0/L1 operator does this. The nearest sibling is the repo's general `compute_trace_hash` determinism apparatus, which this extends rather than duplicates (it folds *into* it, and preserves prior bytes).
3. **Extensibility.** The same-path-ablation pattern — hold the runtime fixed, vary exactly one typed object, report the gap — generalizes well beyond admissibility, and is arguably the methodological template G-24's perception arc and the `use_salience` question both need. Pairing candidate: **the CR-1 ADR (G-14)**, which needs precisely this to derive `salience_top_k` / `inhibition_threshold` the way ADR-0026 derived `δ`.

**Necessity/generality axis:** **irreducible** — and a generalization *source* for other stacks rather than a consolidation target.

#### 8. Fitness / value

- `region_only_gap = 1.00` over 5 chain-dependent cases; `causality_gap = 0.80`; `coincidence_rate = 0.00`; `ratified_rate = 1.00` (ADR-0023 §Lane metrics, dev 2026-05-17).
- Gate 3 records the measurement catching a live wiring bug — direct, cited evidence of the instrument paying for itself.
- Gate 6: `wall_seconds_total = 9.41s` for 20 turns vs the ADR-0022 baseline 12.38s — the evidence layer landed *faster* than the thing it measures.
- Counter-evidence: `evals/forward_semantic_control/results/*.json` carry no `sha`, `commit`, or `generated_at` field — unlike `deduction_serve` / `deductive_logic`, which are SHA-pinned in `evals/CLAIMS.md`. The stack's evidence is unpinned and therefore cannot age-check itself (`AA-A4-10`).

**Fitness axis:** **strong, unpinned** — `evals/forward_semantic_control/results/phase3_v2_report.json` + ADR-0023 §Lane metrics; no `CLAIMS.md` pin.

#### 9. Findings raised

- `AA-A4-3` 🟡 — (shared) `passthrough_rate` / `passthrough_on_scored` are now vacuous metrics over a deleted enum member; a proof obligation that can no longer fail. (§5)
- `AA-A4-10` 🟢 — (shared) lane reports carry no SHA/timestamp pin and no `CLAIMS.md` entry. (§8)
- `AA-A4-12` 🟢 — Census-confirmed rot in the lane: `threshold_characterization.py:265-267` reference `.json` paths that do not exist (`.jsonl` on disk); `_run_region_ablation` docstring drift. Cosmetic, but in the file that carries the stack's load-bearing measurement. (§5)

#### 10. Evidence sources actually consulted

The ADR in full; `generate/admissibility.py:592-668`; `generate/stream.py:334-360, 601-645`; `core/cognition/pipeline.py` (grep for trace/hash/ratify); `core/cognition/result.py` (grep); `evals/forward_semantic_control/runner.py` (grep + census rows); all six `evals/forward_semantic_control/results/*.json` headline metrics extracted mechanically; `evals/CLAIMS.md` (grep — no hit); `docs/census/cbfc8ccb…/{stale-references,docstring-drift}.jsonl`; executed `tests/test_admissibility_trace.py` (green) and a live pipeline probe reading `ratification_outcome` and `region_was_unconstrained`.

---

### ADR-0024 — Inner-Loop Per-Rotor Admissibility

**Audit ID:** — | **Family:** ADR-0024 chain (the family's namesake)
**Zone / stack:** M3 · `L4-recognition` / A4 | **Tier:** A
**ADR status:** Accepted | **ADR date:** 2026-05-17 | **Extends:** ADR-0022, ADR-0023
**Card author:** Claude Opus 5 | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary

- **Decision made:** Add inner-loop per-rotor admissibility to `generate()`, flag-gated and off by default. When on with a real region, each candidate selected by `_nearest_next` is evaluated by `check_transition`; a rejected candidate is recorded in a step-local `rejected_attempts`, excluded, and the selector re-runs; exhaustion raises `ValueError` naming the region.
- **Alternatives explicitly rejected:** making it a global semantics flip (rejected in favor of per-call-site ramping); adaptive/learned/annealed thresholds (out of scope); frame-versor admissibility (deferred to a future ADR — became ADR-0025); pipeline/runtime wiring (deferred).
- **Artifacts the ADR claims will exist:**
  - `generate()` parameters `inner_loop_admissibility` (default `False`) and `admissibility_threshold`
  - the re-selection loop with a retry budget bounded by `len(candidate_indices)`
  - `ValueError(f"AdmissibilityRegion[{label}] inner-loop rejected all candidates at step {step_index}.")`
  - `AdmissibilityTraceStep.rejected_attempts: tuple[tuple[int, str, float], ...]`, folded into the hash only when non-empty
  - `tests/test_inner_loop_admissibility.py`; `tests/test_admissibility_trace.py::TestComputeTraceHashBackwardCompat`
  - *Addendum (Phase 1):* pack-grounded fixture rewrite; `tests/test_inner_loop_phase4.py::TestV1ChainBladePostGrounding`

#### 2. Implementation cross-reference

| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `inner_loop_admissibility` param | yes | `generate/stream.py:280` | Default `False` as specified |
| `admissibility_threshold` param | yes | `generate/stream.py:281` | Default `0.0` |
| `RuntimeConfig.inner_loop_admissibility` | yes | `core/config.py:38` | Default `False` |
| `RuntimeConfig.admissibility_threshold` | yes | `core/config.py:39` | Default `0.0` |
| per-step `check_transition` gate | yes | `generate/stream.py:502-507` | Gated on `active_region is not None` |
| re-selection with exclude set | yes | `generate/stream.py:486-545` | Retry budget `len(candidate_indices)` when `inner_loop_active` (`:486`) |
| exhaustion raise | yes (**upgraded**) | `generate/stream.py:573, 589` | Raises `InnerLoopExhaustion`, not bare `ValueError` — a *typed* subclass (`generate/exhaustion.py:78`, `InnerLoopExhaustion ⊂ ValueError`). Strictly better than specified; back-compatible for `except ValueError` |
| `rejected_attempts` field | yes | `generate/admissibility.py:624` | Exact declared type `tuple[tuple[int, str, float], ...]` |
| folded only when non-empty | yes | `generate/admissibility.py:639-642` | |
| `inner_loop_force_admit` null control | yes (**undocumented in ADR**) | `generate/stream.py:282` | Phase 2 addition; eval-only, deliberately not on `RuntimeConfig`. Docstring says so |
| `tests/test_inner_loop_admissibility.py` | yes | 13,676 bytes | Green |
| `tests/test_inner_loop_phase4.py` | yes | 5,032 bytes | Green; `TestV1ChainBladePostGrounding` present |
| CLI plumbing | yes | `core/cli.py:87-88` | `inner_loop_admissibility` / `admissibility_threshold` from args, defaulting `False` / `0.0` |
| pipeline/runtime wiring (declared out of scope) | **yes — landed later** | `chat/runtime.py:2851-2853` | `RuntimeConfig` → `generate()` forwarding exists, contra §Out of scope. Landed under the chain's Phase 2; the ADR was not amended |

**Build axis:** **full** — every artifact present, two of them stronger than specified (typed exception; runtime wiring the ADR deferred).

#### 3. Liveness / integration

- The parameter is threaded end-to-end: `RuntimeConfig` → `ChatRuntime.chat` → `generate()`. The gate is `inner_loop_active = inner_loop_admissibility and region_active` (`generate/stream.py:386`) — a conjunction of two conditions that are *both* false by default.
- **Sabotage test.** Measured: zero `check_transition` calls across three default-config turns. Also measured with `forward_graph_constraint=True` (so a real region *is* supplied on 3 of 4 turns): still **zero** `check_transition`, `check_margin`, `rank_candidates_by_blade` and `check_rotor_admissibility` calls, because `inner_loop_admissibility` remains `False`. Removing the entire inner loop would change nothing observable in any configuration reachable from `RuntimeConfig` defaults or from the CLI's defaults. Every exercise of this code is in `tests/` and `evals/`.
- No production identity pack or config profile sets the flag (cross-checked against `docs/specs/flag_register.md`'s profile model via G-8/H-6 — there is no serving profile that enables it).
- **Liveness axis:** **wired-but-unreached** — fully plumbed, comprehensively tested, never executed outside test and eval harnesses. This is the most complete instance of that category in the stack.

#### 4. Design fidelity — pillars and axioms

| Pillar | Honors / Tension / Violates | Citation |
|---|---|---|
| I. Mechanical Sympathy | **Honors** | §Risks quantifies the cost honestly ("up to `len(candidate_indices)` extra `check_transition` calls per step") and explains why it is small in practice, rather than hand-waving |
| II. Semantic Rigor | **Honors** | §Context states the defect in one exact sentence: "the trace says 'rejected' and the walk emits it anyway." That is the whole justification, and it is precise |
| III. Third Door | **Honors** | Refuses both "flip the semantics globally" and "leave the verdict decorative"; builds per-call-site ramping with byte-identical hashes for non-adopters |

| Axiom | Honors / Tension / Violates | Citation |
|---|---|---|
| 1. Geometry-First | **Honors** | The gate is `cga_inner(candidate_versor, relation_blade)` — the intrinsic quantity, not a proxy |
| 2. Field-State | **Honors** | Operates on versors and blades throughout |
| 3. Propagation-over-Mutation | **Honors** | §Invariants: "a selection-side retry; it never rebalances `F`, projects grades, or unitizes rotors." Verified — the rotor is constructed only for the admitted candidate |
| 4. Dual-Correction | **Tension** | Same as ADR-0022: rejection is a valve, not a conjugate. The retry loop re-selects but does not *correct* the region that mis-ranked |
| 5. Reconstruction-over-Storage | **Honors** | `rejected_attempts` stores `(index, word, score)` triples, not versors |
| 6. Compilation-Last | **Honors** | A Python loop with an exclude set; no premature structure |
| 7. Reality-over-Inheritance | **Tension** | The ADR itself is a model of this axiom — its Phase 1 addendum *reattributes rather than closes* a finding, and states plainly "the exhaustion finding is not 'closed' — it is reattributed." But the axiom's other edge (an abstraction survives on structural merit only) now bears on a mechanism that has never run outside a test. See §7 |

#### 5. Build fidelity — does the code match the decision?

Matches, and in two places exceeds. The bare `ValueError` the ADR specified became `InnerLoopExhaustion` — a typed subclass carrying `reason`, `region_label`, `step_index` and `rejected_attempts` — which is what made ADR-0025's `RefusalReason.ROTOR_REJECTION` a one-enum-member change later. The runtime wiring the ADR listed under §Out of scope subsequently landed (`chat/runtime.py:2851`); the ADR records no amendment, so a reader trusting §Out of scope would conclude the flag is unreachable from `RuntimeConfig`, which is false. Minor, and in the safe direction.

The Phase 1 addendum is the strongest single piece of document craft in the stack: it records that exhaustion *increased* after the fixture fix (0.33 → 0.67), explains why that is honest behavior rather than a regression, refuses to declare the finding closed, and states explicitly that "the Phase 2 corpus-observation runner's reuse of v1+dev cases was a categorical error." It also updates the pinning tests to the new state rather than leaving stale assertions.

**Build-fidelity axis:** **matches** — with an unrecorded scope expansion (runtime wiring) that strengthens rather than contradicts the decision.

#### 6. Continuity

- **Whitepaper / Yellowpaper:** no contradiction. §Invariants explicitly re-affirms `versor_condition(F) < 1e-6` and CLAUDE.md §Normalization Rules.
- **ADRs:** Extends 0022/0023; quotes ADR-0023's deferral verbatim before acting on it. **Superseded in part by ADR-0026** — which is declared *by ADR-0026*, correctly and in the right direction ("ADR-0024 remains Accepted; threshold mode is preserved… and is the default"). Its own deferral of frame-versor admissibility is closed by ADR-0025, also explicitly. The whole sub-chain 0024→0026→0025 supersedes by written amendment, never silently. Its §Out of scope on runtime wiring is stale (§5).
- **Continuity axis:** **superseded-cleanly** — this is how the rest of the corpus should read.

#### 7. Necessity / generality

1. **Necessity.** This is where the stack's necessity question actually bites. ADR-0022's boundary prefilter and ADR-0024's inner loop are two mechanisms for one purpose, and ADR-0022 §Implementation sequencing step 4 already recorded that the boundary placement alone "prove[d] … sufficient to produce the load-bearing causality gap." So the inner loop was, by its predecessor's own measurement, not required for the demonstrated result. It buys a genuinely different thing — blade-*direction* enforcement, not just token-set membership — which ADR-0024 §Context argues well. But nothing in production consumes that difference.
2. **Reducibility.** Not reducible downward: `check_transition` composes `cga_inner` with a region's typed provenance, which `algebra/` does not and should not carry. Reducible *upward* into ADR-0026, however — see below.
3. **Extensibility.** ADR-0026 supersedes 0024's *gate* while keeping its *loop*, and the two modes now sit side by side in `generate/stream.py:394-600` as parallel branches with duplicated rotor-check logic (`:450-470` margin path, `:525-540` threshold path). Given that ADR-0026 establishes threshold mode is geometrically incoherent across cases (blade norms vary ~10×), maintaining both is a live consolidation candidate: **fold threshold mode into margin mode with `delta=0` as the degenerate case**, retiring one of the two branches. Pairing: ADR-0024 ↔ ADR-0026, within-stack.

**Necessity/generality axis:** **generalization-candidate** — specifically, reducible-to-ADR-0026's ranked gate, which is strictly more general and which the stack's own Phase 4 evidence says is the correct one.

#### 8. Fitness / value

- `phase3_v2_report.json`: `mechanism_isolated = true`, `pass_rate = 1.00`, `boundary_decoy_rate = 1.00`, `rejection_traced_rate = 1.00` over 5 adversarial cases where the boundary picks a *forbidden* token and the inner loop must override and trace it. This is real, well-designed causal attribution.
- `phase5_report.json`: 20/20 across 5 stratified failure-mode families, `mechanism_isolated_threshold = true`.
- `phase5_benign_inner_loop_report.json`: `exhaustion_gate_pass = true`, `code_path_residual = 0.0`, `causal_attribution_valid = true` — the null control confirming the delta is attributable to *rejection*, not to code-path differences. This is the sabotage test built into the lane.
- `phase6_demo_report.json`: `all_three_conditions_pass = true` (C1 replay determinism, C2 traced rejection, C3 coherent refusal).
- Counter-evidence: none of it is a claim in `evals/CLAIMS.md`, none of the reports is SHA-pinned, and none of it measures a production turn.

**Fitness axis:** **strong within its harness, zero outside it** — `evals/forward_semantic_control/results/{phase3_v2,phase5,phase5_benign_inner_loop,phase6_demo}_report.json`.

#### 9. Findings raised

- `AA-A4-1` 🟡 — (shared) measured zero `check_transition` calls even with a real region supplied, because `inner_loop_admissibility` is `False` in every reachable configuration. (§3)
- `AA-A4-4` 🔵 — Threshold mode and margin mode coexist as parallel branches with duplicated rotor-check logic, after the stack's own Phase 4 established threshold mode is geometrically incoherent. Consolidation candidate. (§7)
- `AA-A4-13` 🟢 — §Out of scope states pipeline/runtime wiring is deferred; that wiring has since landed at `chat/runtime.py:2851` without an amendment. (§5)

#### 10. Evidence sources actually consulted

The ADR in full including the Phase 1 addendum; `generate/stream.py:279-300, 384-400, 480-600`; `generate/exhaustion.py` (structure grep); `generate/admissibility.py:618-644`; `core/config.py:35-46`; `core/cli.py:84-89`; `chat/runtime.py:2840-2875`; `core/cli_test.py:370-395` (the `adr-0024` suite alias); `conftest.py:122-140` (SLOW_FILES); four `results/*.json` reports read mechanically; `docs/PROGRESS.md:10-45` (the six-phase closure table). Executed: `tests/test_inner_loop_admissibility.py`, `tests/test_inner_loop_phase2.py`, `phase3.py`, `phase4.py` (all green; phase2 is 823s and is registered in `SLOW_FILES`); the six-entry-point instrumentation under both flag-off and `forward_graph_constraint=True`.

---

### ADR-0025 — Rotor / Frame Admissibility

**Audit ID:** — | **Family:** ADR-0024 chain (Phase 4)
**Zone / stack:** M3 · `L4-recognition` / A4 | **Tier:** A
**ADR status:** Accepted (2026-05-17) | **ADR date:** 2026-05-17 | **Extends:** ADR-0022, 0023, 0024, **0026** | **Supersedes:** "the design-note version of ADR-0025 (Draft)"
**Card author:** Claude Opus 5 | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary

- **Decision made:** Rotor-side admissibility — does the rotor's effect on the current field land in the region's frame-versor cone — is enforced at the generation/propagation seam by a new sibling module `generate/rotor_admissibility.py`, using a positivity bar (`score > 0`) rather than a margin, with refusal routed through the existing `InnerLoopExhaustion` under a new `RefusalReason.ROTOR_REJECTION`.
- **Alternatives explicitly rejected:** **Option A** inline in `generate/stream.py`'s existing loop (conflates two semantic axes at one decision site); **Option B** `algebra/versor.py` (rejected on re-reading — admissibility is semantic, closure is structural; would invert the layer dependency and create a "repair the inadmissible rotor" temptation CLAUDE.md forbids); **Option C** `field/propagate.py` (CLAUDE.md-forbidden site; even a precondition erodes the rule). Also rejected: rotor-side margin (no calibration corpus yet), rotor-side teaching entanglement (Stance A, hygiene-only).
- **Artifacts the ADR claims will exist:**
  - `generate/rotor_admissibility.py` with `RotorVerdict` and `check_rotor_admissibility(region, *, field_current, rotor)`
  - `frame_versor is None` (or null-norm) → trivial admit with `score = +inf`
  - `generate/stream.py` threshold-mode per-candidate rotor check; margin-mode check on the top-ranked candidate
  - `generate/exhaustion.py::RefusalReason.ROTOR_REJECTION`
  - `docs/specs/runtime_contracts.md` §"Rotor admissibility contract"
  - `tests/test_rotor_admissibility.py` — 11 tests, named individually in §Acceptance evidence

#### 2. Implementation cross-reference

| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `generate/rotor_admissibility.py` | yes | 6,972 bytes | Sibling module, as decided |
| `RotorVerdict` | yes | `generate/rotor_admissibility.py:81` | |
| `check_rotor_admissibility` | yes | `generate/rotor_admissibility.py:109` | Signature exactly `(region, *, field_current, rotor)` |
| the check `cga_inner(versor_apply(V, F), frame_versor) > 0` | yes | `generate/rotor_admissibility.py:158-164` | Strict `>` (refuses at `score == 0`), as §Risks says it deliberately does |
| `frame_versor is None` → `+inf` | yes | `generate/rotor_admissibility.py:141-155` | Also handles null-norm separately, as promised |
| threshold-mode per-candidate check | yes | `generate/stream.py:525-540` | |
| margin-mode top-ranked check | yes | `generate/stream.py:450-470` | |
| `RefusalReason.ROTOR_REJECTION` | yes | `generate/exhaustion.py:69` | An enum member, not a string — as §Invariants insists |
| `InnerLoopExhaustion ⊂ ValueError` unchanged | yes | `generate/exhaustion.py:78` | So pre-Phase-4 `except ValueError` handlers still catch |
| `runtime_contracts.md` §Rotor admissibility contract | yes | `docs/specs/runtime_contracts.md:365-400` | Present with the seam, algorithm and refusal taxonomy |
| `tests/test_rotor_admissibility.py` (11 tests) | yes | 15,360 bytes | Green at this SHA; every named test present |
| no new code in `field/propagate.py`, `algebra/versor.py`, `vault/store.py` | yes | — | Verified by grep — the placement decision held |
| **an upstream producer of `frame_versor`** | **no** | — | **Not claimed by this ADR** (§Out of scope: "Region construction for frame versors… is out of scope here"), and not built by any other. See §3 |

**Build axis:** **full** — the module, the wiring, the enum, the contract section and all 11 tests exist exactly as specified.

#### 3. Liveness / integration

This is the stack's sharpest liveness result, and it is stronger than flag-gating.

- The rotor check is guarded by a **three-way conjunction**: `inner_loop_active` (itself `inner_loop_admissibility and region_active`) **and** `active_region.frame_versor is not None` (`generate/stream.py:450, 525-528`).
- **`frame_versor` has no producer.** Grepping the whole repo for `frame_versor` outside `tests/` returns only the dataclass field (`generate/admissibility.py:104`), the consumer (`generate/stream.py`), the checker (`generate/rotor_admissibility.py`), and a docstring in `generate/exhaustion.py`. Every region constructor that production code can reach leaves it `None`: `unconstrained()` (`:163`), `region_from_relation_chain()` (`:196`, blade only), and `build_graph_constraint()` (`generate/graph_constraint.py:141-159`, `allowed_indices` only). `region_from_frame_relation()` accepts one — and has no non-test caller either.
- **Sabotage test.** Deleting `generate/rotor_admissibility.py` entirely would change no observable in any configuration reachable from `RuntimeConfig`, because the third conjunct can never be satisfied. Confirmed empirically: `check_rotor_admissibility` called zero times with defaults *and* zero times with `forward_graph_constraint=True`. The module's own §Rollback describes the production state as the rollback state: "Construct regions with `frame_versor=None`… the runtime behaves identically to ADR-0026 / Phase 3." That is not a rollback; it is the status quo.
- **Liveness axis:** **scaffolded** — not merely unreached but structurally unreachable: the check has no data source, by the ADR's own explicit scope decision. This is the one member whose liveness is worse than "flag off."

#### 4. Design fidelity — pillars and axioms

Note the split this card must hold: the *decision quality* here is the highest in the stack, and the *liveness* is the lowest. §4 scores the decision as written, per the template.

| Pillar | Honors / Tension / Violates | Citation |
|---|---|---|
| I. Mechanical Sympathy | **Honors** | §Risks costs the check exactly: "one `versor_apply` + one `cga_inner`… in threshold mode at most `len(admissible_set)` extra applies per step; in margin mode, exactly one" |
| II. Semantic Rigor | **Honors — exemplary** | §Option B is a full paragraph distinguishing *closure* ("does the constructed versor satisfy the algebra's idempotency invariant?" — structural) from *admissibility* ("does the rotor's effect on the field land in a pack-grounded admissible region?" — semantic). This is Pillar II performed, not cited |
| III. Third Door | **Honors — exemplary** | The ADR reverses its own draft's recommendation and names a fourth option the draft "did not crystallise." §Option A's rejection reason is upgraded from the draft's ("bloats the hot path") to a better one ("conflates the two semantic axes at one decision site… the fix is *separation*, not relocation") |

| Axiom | Honors / Tension / Violates | Citation |
|---|---|---|
| 1. Geometry-First | **Honors** | The frame cone is the intrinsic object; the test is a sign check on a CGA inner product, not a heuristic |
| 2. Field-State | **Honors** | The check is on the *post-rotor field*, `versor_apply(V, F_current)` — a field property, not a token property. This is the most field-native test in the stack |
| 3. Propagation-over-Mutation | **Honors** | "does not mutate field state"; returns a typed verdict. Verified — no assignment to `field_current` in the module |
| 4. Dual-Correction | **Honors** | This is the stack's only genuine instance: destination admissibility and rotor admissibility are *conjugate gates on the same transition* — one on the endpoint, one on the operator that reaches it. §Context states exactly this: "two independent gates that compose" |
| 5. Reconstruction-over-Storage | **Honors** | `RotorVerdict` carries a scalar and a label |
| 6. Compilation-Last | **Honors** | Two algebra calls and a comparison |
| 7. Reality-over-Inheritance | **Violates — in outcome, not intent** | The ADR reasons impeccably about *where* the mechanism belongs and never asks whether it should exist before a producer for its only input does. §Out of scope defers `frame_versor` construction to "upstream (intent ratification, proposition graph)" — neither of which builds one, then or now. A mechanism whose input has no source has not yet earned its place on structural merit. This is the axiom's plainest application in the stack |

#### 5. Build fidelity — does the code match the decision?

Matches precisely, including details easy to get wrong: the strict `>` bar (not `>=`) that §Risks flags as a deliberate choice; the separate handling of `frame_versor is None` versus null-norm; the `float("inf")` sentinel chosen so "callers comparing scores never treat 'no constraint' as a hard rejection"; the float32 re-cast after `versor_apply` with an in-code comment explaining the Rust-path dtype concern. The module docstring reproduces the Option A/B/C/D argument, so the placement rationale survives at the code.

One documentation-level defect, entirely cosmetic: the file is still named `ADR-0025-rotor-frame-admissibility-design-note.md` though its content is the Accepted promotion that *reverses* the design note; and its header records `Supersedes: The design-note version of ADR-0025 (Draft)` — an ADR superseding itself — and `Extends: … ADR-0026`, a higher-numbered ADR, because Phase 4 followed Phase 3. All three are honest records of a real sequence, and ADR-0225 ("repository history wins for IDs") means none should be renumbered; they simply read oddly. `AA-A4-7`.

**Build-fidelity axis:** **matches**

#### 6. Continuity

- **Whitepaper / Yellowpaper:** no contradiction. The ADR actively defends Whitepaper-adjacent doctrine — its Option B and Option C rejections are both arguments *for* CLAUDE.md's normalization rules against a locally convenient violation.
- **ADRs:** Extends 0022/0023/0024/0026, closing 0024's stated deferral with 0024's own words quoted. Supersedes its own draft. No contradiction with any member. Its §Out of scope explicitly leaves `ChatRuntime.respond()`'s `except ValueError: return ""` residual open — which is exactly **H-3 / G-20** in the assessment registers, cross-listed there as "anticipated by the ADR-0024 chain." The chain named its own unfinished business and the assessment found it independently; those agree.
- **Continuity axis:** **clean**

#### 7. Necessity / generality

1. **Necessity.** Conceptually the strongest case in the stack and operationally the weakest. The rotor axis genuinely asks a question no other member asks — every other gate scores a *destination*; this one scores the *transformation*. That is not a narrower duplicate of anything. But necessity is measured against capability, and the system loses nothing today by losing it, because nothing constructs its input.
2. **Reducibility.** Not reducible to `algebra/` — the ADR proves this itself, and the proof is correct. Not reducible to `check_transition` either: destination alignment and rotor-effect alignment are different predicates over different operands.
3. **Extensibility.** The mechanism is a general "does this operator preserve a declared frame" test, and could absorb any future frame-preservation check — identity-manifold conformance (ADR-0022's unpopulated `IDENTITY` source slot, TBD-4) is the obvious candidate: `intersect(region, identity_region)` with a populated `frame_versor` would give the rotor gate its first real producer *and* close TBD-4 in one move. Pairing: **ADR-0025 ↔ ADR-0022 TBD-4 ↔ the identity-manifold stack (MG)** — flagged for `22-consolidation-report.md`.

**Necessity/generality axis:** **irreducible** — the axis is distinct and correctly placed; the finding against it is liveness (`AA-A4-6`), not redundancy.

#### 8. Fitness / value

- §Acceptance evidence lists six named tests, all present and green; `TestRotorAdmissibilityDeterminism` asserts 5-run replay equality for both admitted and refused turns.
- "Suite green. 1048 passed, 2 skipped… (+11 new rotor tests over the post-Phase-3 baseline of 1037)."
- **No lane measures the rotor axis.** `phase5_report.json` and `phase6_demo_report.json` report threshold/margin metrics; no report carries a rotor-specific rate, and `ROTOR_REJECTION` appears in no report's metrics block. The mechanism's evidence is entirely unit-level.
- No `CLAIMS.md` entry.

**Fitness axis:** **unit-tested, never measured** — `tests/test_rotor_admissibility.py` (11 tests, green); no lane evidence, no production evidence, no claim.

#### 9. Findings raised

- `AA-A4-6` 🟡 — `frame_versor` has **no producer anywhere outside tests**; the rotor gate is structurally unreachable, not merely flag-gated, and the ADR's own §Out of scope deferred the producer to upstream components that never built one. (§3)
- `AA-A4-7` 🟢 — Filename still says `-design-note` for the Accepted promotion that reverses the design note; header records the ADR as superseding itself and extending a higher-numbered ADR. Honest records that read as defects. (§5)
- `AA-A4-14` 🔵 — ADR-0022's unpopulated `IDENTITY` region source (TBD-4) is the natural producer for `frame_versor`; wiring one would close TBD-4 and give the rotor gate its first data source. Consolidation/extension pairing. (§7)

#### 10. Evidence sources actually consulted

The ADR in full; `generate/rotor_admissibility.py` in full; `generate/exhaustion.py` (structure grep); `generate/stream.py:440-545`; `docs/specs/runtime_contracts.md:365-400` (grep); a repo-wide `frame_versor` producer search excluding tests (the decisive check); `tests/test_rotor_admissibility.py` executed (green); all six lane reports scanned for rotor metrics (none found); `docs/assessment/31-hindrance-audit.md` H-3 and `30-gap-register.md` G-20 for the `respond()` residual the ADR names.

---

### ADR-0026 — Ranked Admissibility with Margin

**Audit ID:** — | **Family:** ADR-0024 chain (Phase 3)
**Zone / stack:** M3 · `L4-recognition` / A4 | **Tier:** A
**ADR status:** Accepted (2026-05-17) | **ADR date:** — (census records no date field; body dated 2026-05-17) | **Supersedes (in part):** ADR-0024's static threshold for production admissibility gating
**Card author:** Claude Opus 5 | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary

- **Decision made:** Add an admissibility mode `margin` alongside ADR-0024's `threshold`. Margin mode ranks the post-filter candidate set by `cga_inner(versor, relation_blade)` descending with a strict-`>` / ascending-index tie-break, and admits the top candidate iff the set is non-empty, `ranked[0].score > 0`, and either it is the only candidate or its lead over the second exceeds a single per-runtime `delta` (default `0.4`). Selection becomes blade-rank-driven rather than field-driven — an explicitly acknowledged semantic change. Default off.
- **Alternatives explicitly rejected:** per-case normalised thresholds (`alpha * blade_self_score` — "the constant becomes a knob"); per-pack thresholds ("migrates the tuning problem… same failure mode"); per-family tuned `delta` constants (explicitly forbidden as a *fix* — a family failing the single `delta` is to be reported as an architectural finding); flipping the default (requires a separate ADR + trace-hash migration evidence); CLI flags (UX follow-up, not load-bearing).
- **Artifacts the ADR claims will exist:**
  - `generate/admissibility.py` — `RankedCandidate`, `MarginVerdict`, `rank_candidates_by_blade`, `check_margin`
  - `core/config.py::RuntimeConfig.admissibility_mode: str = "threshold"`, `admissibility_margin: float = 0.4`
  - `chat/runtime.py::ChatRuntime.chat` forwards both
  - `generate/stream.py::generate` accepts both as kwargs
  - `tests/test_margin_admissibility.py` — named tests for strict tie-break, threshold-unchanged, refusal on insufficient margin, 5-run replay determinism

#### 2. Implementation cross-reference

| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `RankedCandidate` | yes | `generate/admissibility.py:435` | |
| `MarginVerdict` | yes | `generate/admissibility.py:444` | Carries the full `ranked` tuple, so refusal evidence is the whole ordering — as decided |
| `rank_candidates_by_blade` | yes | `generate/admissibility.py:464` | Tie-break implemented as `rows.sort(key=lambda r: (-r.score, r.index))` (`:505`) — descending score, ascending index, exactly as specified |
| `check_margin` | yes | `generate/admissibility.py:509` | All four admission conditions present at `:533, :544, :554, :567` in the stated order |
| `versor_lookup` / `word_lookup` hoisted params | yes | `generate/admissibility.py:468-469` | "so this function has no I/O and can be unit-tested with a stub vocab" — an unclaimed but real design win |
| `RuntimeConfig.admissibility_mode` | yes | `core/config.py:45` | Default `"threshold"` |
| `RuntimeConfig.admissibility_margin` | yes | `core/config.py:46` | Default `0.4` |
| `ChatRuntime.chat` forwards both | yes | `chat/runtime.py:2852-2853` | |
| `generate()` kwargs | yes | `generate/stream.py:283-284` | |
| margin branch ordering | yes | `generate/stream.py:394-480` | `rank → check_margin → admit-or-refuse`, matching the ADR's pseudocode |
| refusal carries full ranking | yes | `generate/stream.py:434-440` | `InnerLoopExhaustion` with the ranking in `rejected_attempts` |
| `tests/test_margin_admissibility.py` | yes | 13,343 bytes | Green; `TestRankCandidates::test_strict_tie_break_by_ascending_index` present |
| no new code in `field/propagate.py`, `algebra/versor.py`, `vault/store.py`, `respond()` | yes | — | Verified by grep |
| CLI flag (declared out of scope) | correctly absent | `core/cli.py:87-88` | Only `inner_loop_admissibility` / `admissibility_threshold` are CLI-exposed; `admissibility_mode` is not — matching §Out of scope |

**Build axis:** **full** — every artifact present, including the negative commitments.

#### 3. Liveness / integration

- Fully plumbed `RuntimeConfig` → `ChatRuntime.chat` → `generate()`. But margin mode is guarded by `inner_loop_active and admissibility_mode == "margin"` (`generate/stream.py:394-397`) — and `inner_loop_active` is itself `inner_loop_admissibility and region_active`. Three conditions, all false by default.
- **Sabotage test.** Measured zero `check_margin` and zero `rank_candidates_by_blade` calls across default-config turns and across `forward_graph_constraint=True` turns. Removing margin mode changes nothing observable outside tests and evals.
- A second-order liveness note worth stating plainly: ADR-0026 declares it supersedes ADR-0024's threshold "for **production** admissibility gating." Since `inner_loop_admissibility=False` everywhere reachable, *neither* mode performs production admissibility gating. The superseding ADR and the superseded ADR both describe a production behavior that does not exist. `AA-A4-8`.
- **Liveness axis:** **wired-but-unreached**

#### 4. Design fidelity — pillars and axioms

| Pillar | Honors / Tension / Violates | Citation |
|---|---|---|
| I. Mechanical Sympathy | **Honors** | §Risks: margin mode "evaluates `cga_inner` for every candidate in the admissible set, not just the field-closest one"; bounded because the admissible set is small. Costed, not assumed |
| II. Semantic Rigor | **Honors — exemplary** | §Selection semantics refuses to let the change pass as a refinement: "This is a meaningful semantic difference, not a re-shading," then states both modes' semantics in one sentence each. The distinction between "what direction is admissible" (absolute) and "which candidate is confidently selected over the next-best" (relative) is the ADR's core insight and it is stated exactly |
| III. Third Door | **Honors** | Three options were on the table; two were variants of "pick a better constant," and both were rejected because they relocate the tuning problem rather than dissolve it. Option 3 dissolves it via scale invariance. This is the Third Door executed cleanly |

| Axiom | Honors / Tension / Violates | Citation |
|---|---|---|
| 1. Geometry-First | **Honors — the strongest instance in the stack** | The decision is *derived from the geometry*: blade norms vary ~10×, therefore an absolute score bar is meaningless and only the relative ordering carries semantic separation. The intrinsic structure dictated the mechanism, which is precisely what the axiom asks |
| 2. Field-State | **Honors** | Ranks versors against a blade |
| 3. Propagation-over-Mutation | **Honors** | Rank-and-difference over exact scores; §Invariants confirms the rotor is constructed only for the admitted candidate |
| 4. Dual-Correction | **Tension** | Same stack-wide gap: refusal, not conjugate |
| 5. Reconstruction-over-Storage | **Honors** | Stores an ordering, not the scored versors |
| 6. Compilation-Last | **Honors** | A list sort |
| 7. Reality-over-Inheritance | **Honors — as written** | The default `delta` is declared *falsifiable* with the failure protocol stated in advance: a future family below `0.4` "is architectural and should be reported honestly rather than patched with a per-case override." Pre-registering how you will be wrong is the axiom's highest form |

#### 5. Build fidelity — does the code match the decision?

Matches, closely. The `delta = 0.4` derivation table (five v2 cases, minimum observed margin `0.456`, `delta = 0.5` would refuse V2-002) is reproduced in the module's own comment block (`generate/admissibility.py:409-432`), so the justification travels with the constant. The strict-`>` tie-break is implemented as a compound sort key and pinned by the named test. One nuance the code adds and the ADR does not discuss: `rank_candidates_by_blade` handles a null-norm blade by returning every candidate at `score = 0.0` in vocab-index order with an in-code note that "the caller should not enter margin mode on an unconstrained blade" (`:486-496`) — a defensive path that `check_margin` would then reject at condition 2 (`top.score <= 0.0`). Correct behavior, undocumented in the ADR.

**Build-fidelity axis:** **matches**

#### 6. Continuity

- **Whitepaper / Yellowpaper:** no contradiction; the geometric argument is Axiom 1 applied.
- **ADRs:** Supersedes ADR-0024 in part, declared explicitly and in the correct direction, with ADR-0024 left Accepted and threshold mode preserved as the default so prior acceptance evidence stays valid. Handed the rotor-margin question to ADR-0025, which took it and decided against (positivity, not margin) with a written reason. **Positively cited by the assessment**: `31-hindrance-audit.md` **H-5** holds `δ=0.4` up as the in-repo *counterexample standard* against the underived `salience_top_k=16` / `inhibition_threshold=0.3` — "the standard exists two config lines away."
- The one semantic wrinkle is `AA-A4-8`: "supersedes… for production admissibility gating" names a production behavior that does not exist.
- **Continuity axis:** **superseded-cleanly** (as the superseding party)

#### 7. Necessity / generality

1. **Necessity.** The *gate* is necessary given the geometry — Phase 4 proved a static threshold cannot work across cases, so any admissibility gate that survives contact with real blade-norm variation must be relative. Within the stack this is the member whose reasoning most clearly earns its existence.
2. **Reducibility.** Not reducible to L0/L1. `cga_inner` gives the scores; the ranking, the strict tie-break, and the margin predicate are decision policy, which is correctly *not* in `algebra/`.
3. **Extensibility.** Runs in both directions. **Absorbing:** margin mode should absorb threshold mode (`delta = 0` plus a positivity bar recovers threshold semantics closely enough to retire a branch — `AA-A4-4`). **Being absorbed:** `AttentionOperator.plan` (`generate/attention.py:33-43`) performs the *same shape* of operation — score candidates, apply a relative cut (`max_score * inhibition_threshold`), truncate to a budget — using a hand-set ratio where ADR-0026 uses a derived margin. The margin gate is the governed version of the attention gate. That pairing is the concrete form of the CR-1 question, and H-5 already noticed the two sitting "two config lines away."

**Necessity/generality axis:** **irreducible** — and the stack's best generalization *source*: the mechanism most likely to absorb others rather than be absorbed.

#### 8. Fitness / value

- 5/5 v2 mechanism-isolation cases pass in margin mode at `delta = 0.4`, forbidden token traced in every case's `rejected_attempts` (§Acceptance evidence).
- `phase5_report.json`: `pass_rate_margin = 1.0`, `mechanism_isolated_margin = true`, `margin = 0.4` across 20 cases and 5 families — the stratified attempt to falsify the default `delta`, which it survived. Family B (`near_equal_admissible`) exists specifically to force refusal, and does.
- `test_v2_001_refuses_when_delta_too_high` runs the case at `delta = 0.9` against its `0.597` margin and asserts refusal with the full ranking — a designed falsification test for the mechanism, present and green.
- **Independent citation:** `31-hindrance-audit.md` H-5 cites the `δ=0.4` derivation as the repo's exemplar of a properly derived constant. This is the only member of the stack whose value is attested by a document outside the stack.
- Counter-evidence: no production measurement, no `CLAIMS.md` entry, reports unpinned.

**Fitness axis:** **strongest in the stack** — `phase5_report.json` (`pass_rate_margin=1.0` over 20 stratified cases) + `31-hindrance-audit.md` H-5's external citation.

#### 9. Findings raised

- `AA-A4-1` 🟡 — (shared) zero `check_margin` / `rank_candidates_by_blade` calls in any reachable configuration. (§3)
- `AA-A4-4` 🔵 — (shared) threshold and margin coexist as parallel branches; margin is the general case by the stack's own evidence. (§7)
- `AA-A4-8` 🟡 — "Supersedes… for production admissibility gating" names a production behavior that does not exist, since `inner_loop_admissibility=False` means neither mode gates anything in production. (§3, §6)
- `AA-A4-9` 🔵 — `AttentionOperator.plan`'s relative-cut-plus-budget is the same operation shape as `check_margin`, with an underived ratio where ADR-0026 has a derived margin. Direct feeder for G-14 / CR-1. (§7)

#### 10. Evidence sources actually consulted

The ADR in full; `generate/admissibility.py:409-590` in full; `generate/attention.py` in full (for the §7 pairing); `generate/stream.py:283-284, 394-480`; `core/config.py:45-46`; `chat/runtime.py:2852-2853`; `core/cli.py:84-89` (confirming the CLI flag is correctly absent); `docs/specs/runtime_contracts.md:318-345`; `phase5_report.json` and `phase3_v2_report.json` read mechanically; `31-hindrance-audit.md` H-5. Executed `tests/test_margin_admissibility.py` (green) and the flag-on/flag-off instrumentation.

---

### ADR-0046 — PropositionGraph as Forward Admissibility Constraint

**Audit ID:** — | **Family:** — (adjacent to the 0046→0047→0058 mini-arc)
**Zone / stack:** M3 · `L4-recognition` / A4 | **Tier:** A
**ADR status:** Accepted | **ADR date:** 2026-05-18
**Card author:** Claude Opus 5 | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary

- **Decision made:** Add `generate/graph_constraint.py::build_graph_constraint(graph, vocab, *, top_k=8) -> AdmissibilityRegion`, whose `allowed_indices` is the union of the exact CGA top-k neighbourhoods of every named surface in a `PropositionGraph` — converting the graph from a post-hoc descriptor into a forward constraint, with no change to the `generate()` contract.
- **Alternatives explicitly rejected:** none named for the constraint itself. The ADR does reject one thing forcefully and creditably: a fourth "exact-recall-at-scale" demo built on `standard_normal` vectors run through `unitize_versor` — "that construction is not valid as a versor in `Cl(4,1)`… the demo failed at N=10 000 in exactly the way the construction predicts," so the claim was moved to ADR-0045 rather than published behind a weaker construction.
- **Artifacts the ADR claims will exist:**
  - `generate/graph_constraint.py` with `build_graph_constraint`
  - empty / fully-OOV graph → unconstrained region (fallback contract preserved)
  - `admissibility_trace` carries graph root IDs as the region label
  - `tests/test_graph_constraint.py` — 8 tests
  - `evals/industry_demos/demo_01..03.py` — 3 demos, each exiting 0
  - lane results quoted in §Verification (smoke 67, cognition 121, runtime 19, algebra 132, teaching 17, packs 6)
  - *Explicitly deferred:* the `chat/runtime.py` hot-path wire-up ("a follow-up ADR")

#### 2. Implementation cross-reference

| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `generate/graph_constraint.py` | yes | 5,754 bytes | |
| `build_graph_constraint` | yes | `generate/graph_constraint.py:109` | Signature exactly as specified including `top_k: int = 8` |
| union of exact CGA top-k neighbourhoods | yes | `generate/graph_constraint.py:70-98` | `_neighbourhood_indices` — full `range(n)` scan with `cga_inner` per index, sorted, top-k, `score > 0` filter. Exact scan as claimed, O(\|vocab\| × \|nodes\|) as the ADR's own scope limit states |
| empty/OOV graph → unconstrained | yes | `generate/graph_constraint.py:138-153` | Two separate fallbacks (no node versors; empty neighbourhood), both returning `allowed_indices=None` |
| graph root IDs as region label | yes | `generate/graph_constraint.py:101-106` | `_constraint_label` → `"graph:" + sorted roots`. Verified in ADR-0047's characterisation table as `graph:p0` |
| `generate()` API unchanged | yes | `generate/stream.py:279` | `region` param predates this ADR |
| `tests/test_graph_constraint.py` (8 tests) | yes | 5,007 bytes | Green at this SHA |
| `evals/industry_demos/demo_01_forward_constraint.py` | yes | `:38, :57` | Imports and calls `build_graph_constraint(graph, vocab, top_k=8)` |
| hot-path wire-up "a follow-up ADR" | **landed** | `chat/runtime.py:106, 2823-2824` | Closed by **ADR-0047** — correctly, by a follow-up ADR, exactly as this ADR said it should be |

**Build axis:** **full** — every artifact exists, and the one deferred item was closed by the follow-up ADR the deferral named.

#### 3. Liveness / integration

- Call chain: `chat/runtime.py:2818` initialises `forward_region = None`; `:2822` gates on `self.config.forward_graph_constraint`; `:2824` calls `build_graph_constraint(pre_gen_graph, self._context.vocab)`; `:2850` passes it to `generate()`. The flag defaults `False` (`core/config.py:64`), and `tests/test_forward_graph_constraint_null_lift.py::test_default_config_keeps_flag_off` pins that default as a contract.
- **Sabotage test, in two parts.**
  - *Default:* `build_graph_constraint` called **zero** times across three default-config turns. Removing the module changes nothing.
  - *Flag on:* measured `build_graph_constraint` = 3 calls and `filter_candidates` = 3 calls across four turns — the mechanism genuinely engages, and the 3-of-4 engagement rate matches ADR-0047's characterised 6-of-13 pattern (multi-word OOV subject phrases fall back to unconstrained). But `check_transition` / `check_margin` / `rank_candidates_by_blade` / `check_rotor_admissibility` remained at **zero** even then, because those need `inner_loop_admissibility`. So even fully enabled, ADR-0046 exercises only ADR-0022's index prefilter — none of ADR-0024/0025/0026.
  - *And when it engages, it does nothing observable:* ADR-0047's A/B measured 0 Δ on all four cognition-lane metrics, and ADR-0058 pinned that as an invariant.
- **Liveness axis:** **wired-but-unreached** — with the distinguishing feature that its inertness is **ratified, measured, and regression-pinned** rather than accidental. ADR-0058's own title says it: "Engaged but Inert on Today's Cognition Lane."

#### 4. Design fidelity — pillars and axioms

| Pillar | Honors / Tension / Violates | Citation |
|---|---|---|
| I. Mechanical Sympathy | **Tension** | §Scope limits discloses the cost honestly — "computed over the full vocab on each call (O(\|vocab\| × \|nodes\|))… negligible [at current pack sizes]" — but the implementation is a per-index Python loop calling scalar `cga_inner` (`:88-93`), i.e. the exact shape `docs/research/cga-hot-path-measurement-2026-07-25.md` §6 identifies as the 73% hot path and gives a proven bit-exact serial-fold remedy for. Disclosed, not mitigated |
| II. Semantic Rigor | **Honors** | The ADR draws the before/after distinction in four lines ("The graph describes; it does not constrain") and does not overstate: "This is a *drop-in* — `generate()` already accepts `region`" |
| III. Third Door | **Honors** | Refuses both "graph as descriptor" and "graph as executor"; the graph becomes a geometric neighbourhood constraint, authoring nothing |

| Axiom | Honors / Tension / Violates | Citation |
|---|---|---|
| 1. Geometry-First | **Honors** | §Design constraints: "the allowed set is determined by CGA inner product against node versors, not by string matching or rule lists." Verified — `_neighbourhood_indices` is pure `cga_inner`. The one string operation (`surface.strip().casefold()`, `:58`) is vocabulary lookup, not selection |
| 2. Field-State | **Honors** | The constraint is a neighbourhood on the vocabulary manifold |
| 3. Propagation-over-Mutation | **Honors** | "the region is computed once before propagation begins; nothing inside `generate()` is mutated" |
| 4. Dual-Correction | **Tension** | The module docstring *claims* the axiom — "Dual-correction: an empty graph returns an unconstrained region (identity / pass-through) so the caller's fallback path is safe" — but a safe fallback is not a conjugate operator. This is the axiom cited for a property it does not describe. Minor, and confined to a docstring |
| 5. Reconstruction-over-Storage | **Honors** | "the region encodes the constraint lightly (an index set + label); it does not store every versor" |
| 6. Compilation-Last | **Honors** | "no tensors, no kernels — the index set is a plain frozenset until `AdmissibilityRegion` wraps it" |
| 7. Reality-over-Inheritance | **Honors — exemplary** | The ADR *deletes its own fourth demo* on discovering the construction was invalid, explains the invalidity in `Cl(4,1)` terms, and moves the claim to the ADR that measures it properly. Then ADR-0047/0058 measured this ADR's own mechanism to a null and declined to flip its default. The axiom applied to the author's own work, twice |

#### 5. Build fidelity — does the code match the decision?

Matches. `top_k=8` is the operational default the ADR declared; the fallback contract is implemented at two distinct exit points; the label is the graph roots as promised; the `generate()` signature is untouched.

Two divergences between the ADR's framing and reality, both in the ADR's favor and both closed by later ADRs rather than left to rot:
1. The deferred hot-path wire-up landed in ADR-0047 — the follow-up this ADR asked for.
2. §Consequences claims "the `admissibility_trace` in every `GenerationResult` now carries the graph root IDs as the region label — full traceability from surface token back to the intent node." True only when the flag is on; with the default the label is `"unconstrained"` (`generate/stream.py:335-337`). The ADR predates the flag (which ADR-0047 introduced), so this is sequence, not error — but a reader of ADR-0046 alone would over-read the traceability claim.

One measurement note the ADR could not have made and this audit can: `top_k = 8` is an undated operational default with no derivation, in the same class H-5 flags for `salience_top_k=16`. ADR-0047 §Scope limits says so itself — "this ADR does not re-tune it. An eval that *does* differentiate flag ON vs OFF will need to land before any tuning is justified" — which is the correct posture and also means the constant has never been earned.

**Build-fidelity axis:** **matches**

#### 6. Continuity

- **Whitepaper / Yellowpaper:** no contradiction.
- **ADR-0009 lineage — checked explicitly, per the audit brief.** `02-layer-taxonomy.md` §1.1 dispositions ADR-0009 (Compositional Physics) as "landed as the proposition-graph lineage: `PropositionGraph → ArticulationTarget → realizer`." ADR-0046 does **not** contradict that lineage; it adds a second, orthogonal consumer of the same object. The forward path (`graph → region → generate()`) and the descriptive path (`graph → ArticulationTarget → realizer`) coexist in `chat/runtime.py` on the same turn — `build_graph_from_input` at `:2822` for the constraint, `articulate_with_intent` after `generate()` for surface realization — and ADR-0047 §Consequences states the descriptive path "is left alone" deliberately. So the lineage holds, with one substantive change ADR-0046 makes quietly and should be read as making: **`PropositionGraph` acquires a second role.** In ADR-0009 it is downstream of allocation (`BindingOperator: (AttentionPlan, FieldState) → BindingFrame` — the graph lineage *consumes* an attention plan). Under ADR-0046 it also *produces* one, since `build_graph_constraint` emits `allowed_indices`, the same type `AttentionPlan` carries. The compositional-physics arrow is now bidirectional, and no document says so. That is not a contradiction of the §1.1 disposition, but it is a real change in what `PropositionGraph` does, and it is the technical core of the CR-1 question (§3). Recorded as `AA-A4-5`.
- **ADRs:** Cross-references 0018, 0022–0026, 0045 accurately. Followed by ADR-0047 (wiring + A/B) and ADR-0058 (the null-lift ruling + pinned invariant), both of which cite it correctly. Its influence is recorded honestly in ADR-0058: the null result "scoped ADR-0048 through ADR-0053," which closed the cognition split at 100% surface_groundedness by working in the realizer layer instead — so the ADR's *measurement* delivered value even though its *mechanism* did not.
- **Continuity axis:** **clean**

#### 7. Necessity / generality

1. **Necessity.** The narrowest necessity case in the stack. The mechanism is a well-built, geometry-honest converter; it has been measured to change nothing on the production lane; and its own governing ADR (0058) ruled it stays off. Under Axiom 7 as the charter states it — "no abstraction is sacred; it survives on structural merit only," with the deleted spectral monitor, grade guard, drift timer, ANN index and pseudoscalar check as precedent — ADR-0046's construction is a legitimate retirement candidate. Two counterweights, both real: ADR-0058 explicitly does not foreclose a future realizer-side consumer, and the null-lift test is itself valuable epistemic infrastructure that would be lost with the mechanism. This is a judgement for ruling, not for this audit.
2. **Reducibility.** Reducible in shape to `AttentionOperator` — both produce `allowed_indices` from a scored CGA neighbourhood; the difference is the anchor (graph node versors vs field curvature). Not reducible to `algebra/`, which supplies only the inner product.
3. **Extensibility.** If any of the three `allowed_indices` producers is consolidated into a single typed "candidate constraint" concept with pluggable sources (language / curvature / graph / identity), ADR-0046 becomes one source rather than a standalone mechanism, and its `top_k` joins `salience_top_k` under one derivation regime. Pairing: **ADR-0046 ↔ ADR-0008/`generate/attention.py` ↔ ADR-0022** — the stack's headline consolidation cluster.

**Necessity/generality axis:** **generalization-candidate** — subsumable as one source under a unified candidate-constraint concept; standalone, it is the stack's weakest necessity case.

#### 8. Fitness / value

- **Negative, and ratified as such.** ADR-0047 §Characterisation: 0 Δ on `intent_accuracy`, `surface_groundedness`, `term_capture_rate`, `versor_closure_rate`, 0 `InnerLoopExhaustion`, with 6/13 cases producing a non-trivial constraint. ADR-0058 §Decision: default stays `False`, no pack opts in, and the null becomes a pinned test.
- **Positive, indirectly and substantially.** ADR-0058 records that the null result "scoped ADR-0048 through ADR-0053 — which closed the cognition public split at **100.0% surface_groundedness / 91.7% term_capture_rate** by working in the realizer / surface-assembly layer, not in propagation." A measurement that correctly localised a gap to a different layer, and the localisation paid off. That is real delivered value from a mechanism that delivered none directly, and the distinction should survive triage.
- `tests/test_graph_constraint.py` (8) and `tests/test_forward_graph_constraint_wiring.py` (5) green; `evals/industry_demos/demo_01_forward_constraint.py` present.
- Evidence-hygiene note: ADR-0058 §Decision item 3 says the null-lift finding "becomes a **CI-enforced invariant**." The test does run under `--suite full` (`core/cli_test.py:442` maps `full` → `tests/`) and is in neither `QUARANTINE` (empty) nor `SLOW_FILES`, so it does execute in `full-pytest.yml` on push to main — the claim holds. It is, however, in no *named* suite alias (census `suite-membership-gap.jsonl`), including the `adr-0024` alias, so a reviewer running the chain's own alias does not exercise it. Recorded as hygiene, not as a false claim.

**Fitness axis:** **measured null, ratified; indirect value real** — ADR-0047 §Characterisation + ADR-0058 §Context (the 0048–0053 scoping).

#### 9. Findings raised

- `AA-A4-1` 🟡 — (shared) zero calls by default; with the flag on, the region engages but only ADR-0022's prefilter runs. (§3)
- `AA-A4-5` 🔵 — `PropositionGraph` acquires a second, undocumented role: it now *produces* an allocation constraint (`allowed_indices`) as well as consuming one, inverting the ADR-0009 compositional-physics arrow. No document records the change. (§6)
- `AA-A4-15` 🟢 — `top_k=8` is an underived operational default in the H-5 class; ADR-0047 §Scope limits acknowledges it cannot be tuned without a differentiating eval that does not exist. (§5)
- `AA-A4-16` 🟢 — `_neighbourhood_indices` uses the per-index scalar `cga_inner` loop that `cga-hot-path-measurement-2026-07-25.md` §6 identifies as the hot-path shape with a proven bit-exact remedy; disclosed in §Scope limits, unmitigated. (§4)

#### 10. Evidence sources actually consulted

The ADR in full; ADR-0047 and ADR-0058 in full; `generate/graph_constraint.py` in full; `generate/graph_planner.py` (import surface); `chat/runtime.py:2760-2880`; `core/config.py:64`; `tests/test_forward_graph_constraint_null_lift.py` in full; `core/cli_test.py:440-443` and `conftest.py:95-140` (to test the "CI-enforced" claim rather than accept it); `docs/adr/ADR-0009-compositional-physics.md` §Decision 1–4 (for the lineage check); `02-layer-taxonomy.md` §1.1. Executed: `tests/test_graph_constraint.py`, `tests/test_forward_graph_constraint_wiring.py`, `tests/test_forward_graph_constraint_null_lift.py` (all green); flag-on instrumentation measuring 3 `build_graph_constraint` calls over 4 turns.

---

## 3. Stack-level synthesis

### Internal consistency

**Unusually high — the best-behaved chain seen in this batch.** Every supersession is declared in writing by the superseding party, in the correct direction, with the superseded ADR left Accepted and its evidence explicitly preserved. ADR-0023 hands inner-loop admissibility to ADR-0024 by name; ADR-0024 quotes the handoff back before acting. ADR-0026 supersedes ADR-0024's gate while keeping its loop and says exactly which part. ADR-0025 closes ADR-0024's stated deferral, takes ADR-0026's margin question, and decides *against* margin on the rotor side with a reason ("there is no cross-case calibration evidence to inform a margin constant yet… picking a rotor-margin `delta` today would be guessing"). ADR-0025 even reverses its own draft's architectural recommendation in public and explains why the draft was wrong. This is what a healthy decision chain looks like.

Three inconsistencies, only one of which is the stack's own doing:

1. **PASSTHROUGH (`AA-A4-3`) — the only genuine unreconciled contradiction.** ADR-0022 §Decision item 3 specifies three ratification outcomes and argues for the third; ADR-0023 §Decision item 3 makes its absence a scored proof obligation. `RatificationOutcome` now has two members, excised under INV-34 and pinned by `tests/test_linguistic_governance_phases.py`. The later ruling is better; neither ADR was amended; and the lane still computes `passthrough_rate` / `passthrough_on_scored` over an impossible state, so a proof obligation has silently become a tautology. This is `AGENTS.md` Standing Philosophy #5 exactly — a record and reality diverged.
2. **"Production admissibility gating" (`AA-A4-8`).** ADR-0026 supersedes ADR-0024 "for production admissibility gating"; ADR-0024 §Why flag-gated describes ramping "per-call-site rather than as a global semantics flip." Both presuppose a production gate. `inner_loop_admissibility=False` everywhere reachable means there is none. The two ADRs are consistent with each other and both inconsistent with the runtime.
3. **Stale scope notes.** ADR-0024 §Out of scope defers runtime wiring that has since landed (`AA-A4-13`); ADR-0046 defers a hot-path wire-up that ADR-0047 landed (correctly, by the follow-up ADR it named — this one is fine).

### Cumulative build state

**Build is the strongest axis in the stack and liveness the weakest, and the gap is the finding.**

| ADR | Build | Liveness | Necessity/generality | Fitness |
|---|---|---|---|---|
| 0022 | full | **wired-but-unreached** (region) / **live** (ratifier) | generalization-candidate | mechanism proven, integration null |
| 0023 | full | **live** (recording a constant) | irreducible | strong, unpinned |
| 0024 | full | wired-but-unreached | generalization-candidate → 0026 | strong in-harness, zero outside |
| 0025 | full | **scaffolded** (no producer for its only input) | irreducible | unit-tested, never measured |
| 0026 | full | wired-but-unreached | irreducible (best generalization source) | strongest in stack; externally cited |
| 0046 | full | wired-but-unreached (ratified inert) | generalization-candidate | measured null; indirect value real |

Six of six ADRs are **full build**: every named artifact exists at its named location with its named shape, and every "not changed" negative commitment holds under grep. That is a 100% build rate, which is rare. 125 tests across 13 files pass green at `cbfc8ccb`.

Liveness inverts it. On the default serving path the entire stack executes **zero** admissibility operations — measured, not inferred. Two mechanisms survive the sabotage test: the intent ratifier (ADR-0022 item 3, default-on, INV-34-pinned, catches real intent misclassification) and the admissibility trace (ADR-0023, folded into `trace_hash`, faithfully recording that nothing happened). Everything else is gated behind flags that no production configuration, no identity pack, and no CLI default sets.

So the chain did not stall halfway — it completed, thoroughly, and then was not switched on. Three of the four gates that would switch it on are `False` by default and one (`frame_versor`) has no producer at all. The honest summary: **a six-ADR chain built to completion, proven within its own harness, and integrated nowhere.** And critically, the authors *knew and recorded this* — ADR-0058 is the stack measuring its own inertness and ruling to keep it. This is a governance question, not a discovered failure.

### Cumulative necessity/generality read

**One coherent mechanism, built in five refinements plus a new source — and that mechanism is a *third* implementation of something the system already does twice.**

The stack is internally coherent: `AdmissibilityRegion` is one object; index-set, blade-direction and rotor-frame are three genuinely orthogonal gates on it; margin supersedes threshold on geometric grounds. Nobody built five narrow things that happened to land in sequence. Judged on its own terms this is a well-generalized construction.

The consolidation finding is one level up. `generate/stream.py` composes **three producers of a candidate index set** on every turn:

```
language_candidates          (output-language filter)
  ∩ salience_candidates      AttentionPlan.allowed_indices   — ADR-0008 lineage, default ON, ungoverned
  ∩ region.allowed_indices   AdmissibilityRegion             — this stack, default OFF, governed
```

Same type (`np.ndarray` of `int64`), same meaning ("what may the walk visit next"), same composition operator (set intersection, `_intersect_candidates:326` then `filter_candidates:343`). Three vocabularies, three provenance stories, no unifying concept, no owner.

Worse, the two that matter are governed by **opposite doctrines**, in adjacent lines of the same function:

- `generate/stream.py:327-330` — when `language ∩ salience` is empty, the code **silently relaxes** to salience alone. No refusal, no trace, no record.
- `generate/stream.py:344-357` — when `∩ region` is empty, the code raises `InnerLoopExhaustion` with the region label and step index, because ADR-0022 §2 forbids "silently relaxing the constraint to produce a fluent-but-ungrounded surface — that is the exact failure mode this ADR exists to eliminate."

**The path that silently relaxes is the one that is default-ON. The path that refuses honestly is the one that never runs.** That is `AA-A4-17`, and it is the single most consequential finding in this dossier: the stack's central doctrinal contribution is enforced only where it is inert, and violated where it is live, eight lines apart in the same function.

The generalization is therefore clear and the stack supplies its own template: one typed candidate-constraint concept with pluggable sources (language / curvature / graph / identity), one composition algebra (`intersect`, already written and property-tested at `generate/admissibility.py:296`), one refusal doctrine, one derivation standard for its constants (ADR-0026's falsifiable `δ`, which H-5 already holds up as the repo's exemplar against `salience_top_k=16` / `inhibition_threshold=0.3`). Feed to `22-consolidation-report.md` as cluster **A4-C1**, with the ADR-0024↔ADR-0026 mode merge (`AA-A4-4`) as a smaller within-stack cluster **A4-C2**.

### The CR-1 question — recommendation for ruling (this audit flags; it does not rule)

CR-1 asks: *"is attention a first-class layer, or an emergent property of admissibility that should stay distributed?"* and cites this stack's ADR-0024/0026/0025 plus salience/NN search as its only partial existence, on the grounds that this is "precisely the measured hot path (~73% of turn time through `cga_inner`/`geometric_product`, Finding 0-F)."

**Recommendation: CR-1 should be read as still open, and this stack should be recorded as *narrowing* it rather than satisfying any part of it.** Four findings, in order of force:

1. **The stack is not the hot path, and CR-1's attribution needs correcting.** Finding 0-F's ~73% is `cga_inner`→`geometric_product` inside `generate/proposition.py::_nearest_by_cga` and `generate/salience.py::compute` — both visible in the 2026-07-25 profile, neither belonging to this stack. Admissibility appears nowhere in that profile, and now we know why: it executes zero times. CR-1 groups the admissibility ADRs with salience/NN search as jointly constituting the hot path; the measurement and the instrumentation both say only the salience half is. **Currency check:** the ~73% figure is still structurally valid at `cbfc8ccb` — `_nearest_by_cga` (`generate/proposition.py:381-392`) and `SalienceOperator.compute` (`generate/salience.py:41-54`) both still run per-index Python loops over scalar `cga_inner`; the proven bit-exact serial-fold remedy from that document's §6 has not landed. The number is dated but not stale.
2. **The ADRs CR-1 cites cannot serve as "partial existence" of a live attention layer, because they are not live.** Measured zero calls. Whatever governance CR-1 needs, it cannot inherit it from ADR-0024/0025/0026 by treating them as the built fragment — they are a built fragment of something that is switched off. The `attention-allocation` component card already had this right in its interaction contract ("Two allocation stages, only the second governed by ADRs"); this dossier adds that the governed stage is also the dormant one.
3. **The stack adds a source CR-1 did not enumerate.** `build_graph_constraint` makes `PropositionGraph` a producer of `allowed_indices` — a third allocation source alongside language and curvature, inverting the ADR-0009 compositional-physics arrow (§2 ADR-0046 §6, `AA-A4-5`). CR-1's inventory is one item short.
4. **The stack supplies the standard the CR-1 ADR needs, which is the constructive half.** G-14 asks the CR-1 ADR to own `use_salience`, `salience_top_k=16`, `inhibition_threshold=0.3`, the budget feedback loop, and the `InhibitionMask` disposition. H-5 already names ADR-0026's `δ=0.4` as the in-repo exemplar for how such a constant should be derived — falsifiable, corpus-derived, with the failure protocol pre-registered, and survived a 20-case stratified attempt. ADR-0026 also demonstrates the *relative-not-absolute* insight that `AttentionOperator.plan`'s `max_score * inhibition_threshold` reaches for without derivation.

**Suggested reformulation of CR-1's ruling question**, sharper than the current one and answerable with the evidence now in hand:

> Who owns `allowed_indices` as one typed concept with four possible sources (language, salience/curvature, admissibility/graph, identity)? Which sources may silently relax on an empty intersection and which must refuse honestly — given that today the default-ON source relaxes and the default-OFF source refuses (`AA-A4-17`)? And by what derivation standard are each source's constants set — given that one source already meets the ADR-0026 bar and the others do not (H-5)?

That question subsumes G-14's five items, absorbs this stack's `AA-A4-5`/`AA-A4-9`/`AA-A4-17`, and can be answered by one ADR. It also answers CR-1's original binary the way the evidence points: **attention is not emergent from admissibility** — admissibility is dormant and attention is live and load-bearing without it — **but neither is it a separate layer.** Both are the same allocation function with different anchors, and what is missing is not a layer but an owner.

### Blast radius if this stack's central claim is wrong

The central claim — "the graph/intent constrains the field forward, and the walk refuses rather than relaxing" — has already been measured to two different verdicts (§1), so the useful blast-radius question is: *what re-verdicts if the stack is ruled decorative and retired?*

- **Low blast radius, which is itself the finding.** Because nothing in production consumes a region, retiring `generate/admissibility.py`, `rotor_admissibility.py`, `graph_constraint.py` and their flags would change no served byte, no `trace_hash` (except by removing the constant trace field), and no lane metric except the purpose-built `forward_semantic_control` lane and `evals/industry_demos/demo_01`. This is the sabotage test answered at stack scale.
- **Zones needing re-verdict if retired:** **CR-1** loses the ADR-numbered partial existence it currently cites (arguably a *clarification*, per the recommendation above); the `attention-allocation` component card's interaction contract ("admissibility then judges them") needs correcting to note the judging stage is dormant; **G-14**'s scope would need to absorb the derivation standard directly rather than by reference; **H-5** loses its in-repo counterexample, which is a real cost — `δ=0.4` is the best-derived constant in the repo and the argument for it should be preserved even if its mechanism is not.
- **Zones needing re-verdict if instead ruled load-bearing and switched on:** M3 (`L4-recognition`, `L5-cognition`) liveness; M4 (`L6-chat-runtime`) — `AA-A4-17`'s asymmetry becomes a live serving-path defect the moment regions are supplied, since `InnerLoopExhaustion` would begin reaching `respond()`'s `except ValueError: return ""` (H-3/G-20) and refusals would serve as empty strings; MV (`evals-determinism`) — trace hashes change and lane pins need regeneration; **ADR-0058 would need explicit reversal**, as it ruled the opposite.
- **No cascade into the FA-1 territory.** This stack makes no L2 holonomy-closure-style claim and does not depend on ADR-0005/0015. Cascade-checked and clear.
- **Cross-stack cross-reference (not available to this dossier):** the necessity question "is admissibility distinct from the rotor/algebra layer?" is answered **yes** by this stack's own reasoning (ADR-0025 §Option B: closure is structural, admissibility is semantic, and merging them invites the hot-path repair CLAUDE.md forbids) and the code honors it — `generate/admissibility.py` and `generate/rotor_admissibility.py` import *from* `algebra/` and never invert the dependency, and no admissibility code appears in `algebra/versor.py`, `field/propagate.py` or `vault/store.py`. **Stack A1 (rotor/algebra) should be asked to confirm from its side** that no reciprocal coupling was introduced; this dossier verified the direction only from `generate/`.

## 4. Stack-level findings (`AA-N`)

Placeholder IDs per the brief; renumber into `20-finding-register.md` at rollup.

- `AA-A4-1` 🟡 **Repair** — The entire admissibility stack executes zero operations on the default serving path (measured: `check_transition`/`check_margin`/`rank_candidates_by_blade`/`filter_candidates`/`check_rotor_admissibility`/`build_graph_constraint` all 0 across three default-config `ChatRuntime.chat()` turns). ADR-0022's stated purpose — "semantic structure becomes causally active inside propagation" — is not in effect anywhere. Governance item, not a defect: the inertness is ratified by ADR-0058.
- `AA-A4-2` 🟡 **Repair** — `generate/intent_ratifier.py:278::region_for_intent`, ADR-0022's designed bridge from a ratified intent to a region, has no non-test caller; ratification and admissibility share a file and nothing else.
- `AA-A4-3` 🟡 **Repair** — `RatificationOutcome.PASSTHROUGH` was excised under INV-34; ADR-0022 §Decision 3 and ADR-0023 §Decision 3 both still specify it, and `evals/forward_semantic_control/runner.py` still computes `passthrough_rate` / `passthrough_on_scored` over an impossible state, turning a scored proof obligation into a tautology. Neither ADR amended.
- `AA-A4-4` 🔵 **Consolidate** — Threshold and margin modes coexist as parallel branches in `generate/stream.py:394-600` with duplicated rotor-check logic, after the stack's own Phase 4 established no static threshold is geometrically valid. Fold threshold into margin (`delta=0`) and retire a branch. Cluster **A4-C2**.
- `AA-A4-5` 🔵 **Consolidate** — `PropositionGraph` acquires an undocumented second role under ADR-0046: it now *produces* an allocation constraint (`allowed_indices`) as well as consuming one, inverting the ADR-0009 compositional-physics arrow recorded in `02-layer-taxonomy.md` §1.1. Direct input to the CR-1 ruling.
- `AA-A4-6` 🟡 **Repair** — `AdmissibilityRegion.frame_versor` has **no producer anywhere outside `tests/`**; ADR-0025's rotor gate is structurally unreachable, not merely flag-gated. The ADR's §Out of scope deferred the producer to "upstream (intent ratification, proposition graph)"; neither built one.
- `AA-A4-7` 🟢 **Monitor** — ADR-0025's filename retains `-design-note` for the Accepted promotion that reverses that design note; its header records it as superseding itself and extending higher-numbered ADR-0026. Honest records of a real sequence; per ADR-0225 do not renumber, but a reader-facing note would help.
- `AA-A4-8` 🟡 **Repair** — ADR-0026 declares it supersedes ADR-0024 "for production admissibility gating"; since `inner_loop_admissibility=False` in every reachable configuration, neither mode gates anything in production. Both ADRs describe a production behavior that does not exist.
- `AA-A4-9` 🔵 **Consolidate** — `AttentionOperator.plan` (`generate/attention.py:33-43`) performs the same operation shape as `check_margin` — score, relative-cut, budget — with an underived ratio (`inhibition_threshold=0.3`) where ADR-0026 has a falsifiably derived `δ=0.4`. Direct feeder for G-14 and H-5.
- `AA-A4-10` 🟢 **Monitor** — No admissibility or forward-semantic-control claim appears in `evals/CLAIMS.md` at any tier, and no report in `evals/forward_semantic_control/results/` carries a `sha`, `commit` or `generated_at` field — unlike `deduction_serve`/`deductive_logic`, which are SHA-pinned. The stack's evidence cannot age-check itself and no claim would fail if it regressed.
- `AA-A4-11` 🟢 **Monitor** — ADR-0022 `## Code impact` contains a duplicated `### New` / `### Not changed (explicit)` pair (`:180-250` and `:252-286`) with inconsistent content; a reader diffing claimed-vs-landed hits two lists.
- `AA-A4-12` 🟢 **Monitor** — Census-confirmed rot in the load-bearing lane: `evals/forward_semantic_control/threshold_characterization.py:265-267` reference `.json` paths that are `.jsonl` on disk; `runner.py:140::_run_region_ablation` docstring drift.
- `AA-A4-13` 🟢 **Monitor** — ADR-0024 §Out of scope states pipeline/runtime wiring is deferred; that wiring landed at `chat/runtime.py:2851-2853` without an amendment.
- `AA-A4-14` 🔵 **Consolidate** — ADR-0022's unpopulated `IDENTITY` region source (TBD-4, still open) is the natural producer for ADR-0025's `frame_versor`; one wiring would close TBD-4 and give the rotor gate its first data source. Pairs this stack with the identity-manifold work in MG.
- `AA-A4-15` 🟢 **Monitor** — `top_k=8` (ADR-0046) is an underived operational default in the H-5 class; ADR-0047 §Scope limits concedes it cannot be justified without a differentiating eval that does not exist.
- `AA-A4-16` 🟢 **Monitor** — `generate/graph_constraint.py:88-93` uses the per-index scalar `cga_inner` loop that `docs/research/cga-hot-path-measurement-2026-07-25.md` §6 names as the hot-path shape with a proven bit-exact serial-fold remedy. Disclosed in ADR-0046 §Scope limits, unmitigated. (Same shape as `_nearest_by_cga` and `SalienceOperator.compute`, both also unremedied at this SHA.)
- `AA-A4-17` 🔴 **Block (for ruling)** — **The honest-refusal doctrine is enforced only where it is inert and violated where it is live.** `generate/stream.py:327-330`: when `language ∩ salience` is empty, the walk **silently relaxes** to salience alone — no refusal, no trace, no record. `generate/stream.py:344-357`, eight lines later: when `∩ region` is empty, it raises `InnerLoopExhaustion` naming the region and step, because ADR-0022 §2 declares silent relaxation "the exact failure mode this ADR exists to eliminate." The relaxing path is default-ON; the refusing path never executes. This is the stack's central doctrinal contribution contradicted in the same function by the mechanism that actually runs. Flagged for ruling, not repaired.
- `AA-A4-18` 🟢 **Monitor** — Named-suite asymmetry: ADR-0024/0025/0026's acceptance tests are all registered in the `adr-0024` alias (`core/cli_test.py:387-393`), while ADR-0022's (`test_forward_semantic_control.py`, `test_intent_ratifier.py`), ADR-0023's (`test_admissibility_trace.py`) and ADR-0046's (`test_graph_constraint.py`, `test_forward_graph_constraint_wiring.py`, `test_forward_graph_constraint_null_lift.py`) are in no named alias. All do run under `--suite full` (`cli_test.py:442` → `tests/`) and none is in `QUARANTINE` (empty) or `SLOW_FILES`, so ADR-0058's "CI-enforced invariant" claim holds — but a reviewer running the chain's own alias exercises neither the stack's foundation nor its null-lift pin.

**Rollup note for `21-drift-report.md`:** `AA-A4-3`, `AA-A4-8`, `AA-A4-11`, `AA-A4-12`, `AA-A4-13` are document-vs-reality drift. **For `22-consolidation-report.md`:** cluster **A4-C1** (`AA-A4-5`, `AA-A4-9`, `AA-A4-14`, `AA-A4-17` — the unified candidate-constraint concept, spanning this stack, ADR-0008/`generate/attention.py`, and the identity manifold) and cluster **A4-C2** (`AA-A4-4` — threshold/margin mode merge, within-stack). **Mirror into the assessment `G`-register:** `AA-A4-17` and `AA-A4-5` are system-level gaps, not document fidelity, and belong alongside **G-14**.

## 5. Evidence sources actually consulted (stack-wide)

**Charter and templates:** `docs/adr-audit/00-scope-and-method.md`, `TEMPLATE-stack-dossier.md`, `TEMPLATE-adr-card.md`, `MANIFEST.md`, `02-stack-taxonomy.md` (A4 row), `01-adr-census.md` (rows 0022–0026, 0046).

**ADRs read in full:** ADR-0022, ADR-0023, ADR-0024 (incl. Phase 1 addendum), ADR-0025, ADR-0026, ADR-0046 (members); **ADR-0047** and **ADR-0058** (non-members, decisive fitness evidence); ADR-0009 §Context and §Decision 1–4 (lineage context only, not carded).

**Assessment prior (read before any fresh grep, per the charter's evidence order):** `02-layer-taxonomy.md` in full (§1.1 disposition, §5 CR-1, §6 completeness criteria); `10-layer-cards/M3-comprehension-reasoning.md` in full; `20-component-cards/attention-allocation.md` in full; `30-gap-register.md` (G-8, G-14, G-20, G-24); `31-hindrance-audit.md` (H-3, H-5, H-6); `01-phase0-ground-truth.md` §7 Finding 0-F; `docs/research/cga-hot-path-measurement-2026-07-25.md` §§1-6.

**Census (`docs/census/cbfc8ccbf7fe503ab31abe7aedbb1973ba7d7b4d/`):** `SUMMARY.md`, `stale-references.jsonl`, `docstring-drift.jsonl`, `suite-membership-gap.jsonl`, `magic-numbers.jsonl`, `param-no-effect.jsonl`, `evidence-currency.jsonl`, `silent-drop.jsonl` — filtered for every member ADR and every module in the stack.

**Source read in full:** `generate/admissibility.py` (669 lines), `generate/rotor_admissibility.py` (180), `generate/graph_constraint.py` (159), `generate/attention.py` (43), `generate/salience.py` (62), `tests/test_forward_graph_constraint_null_lift.py` (74).
**Source read in part:** `generate/stream.py:18-40, 250-360, 384-645` (the composition and inner-loop sites); `chat/runtime.py:2760-2880` (both `generate()` call sites and the exhaustion handler); `generate/intent_ratifier.py:80-110, 199-300`; `generate/exhaustion.py` (structure); `generate/proposition.py:27, 381-393`; `core/cognition/pipeline.py` (grep: region/admissibility/ratify); `core/config.py:35-64`; `core/cli.py:84-89`; `core/cli_test.py:360-443`; `conftest.py:95-196`; `evals/framework.py:220-240`; `docs/specs/runtime_contracts.md:277-400`.

**Evidence artifacts read mechanically:** `evals/forward_semantic_control/results/{index,phase2_inner_loop_report,phase3_v2_report,phase4_*,phase5_report,phase5_benign_inner_loop_report,phase6_demo_report}.json` (headline metrics extracted programmatically), `results/README.md` in full; `evals/CLAIMS.md` (grep — no admissibility claim found, itself a finding); `docs/PROGRESS.md:10-45` (the ADR-0024 chain closure table).

**Executed against code, not read from documents:**
- `pytest` over 13 stack test files at `cbfc8ccb`: `test_forward_semantic_control`, `test_intent_ratifier`, `test_graph_constraint`, `test_rotor_admissibility`, `test_margin_admissibility`, `test_inner_loop_admissibility`, `test_admissibility_trace` (**87 passed, 9.6s**); `test_inner_loop_phase2/3/4`, `test_refusal_contract`, `test_forward_graph_constraint_wiring`, `test_forward_graph_constraint_null_lift`, `test_inner_loop_exhaustion_materializes` (**38 passed, 824s** — dominated by `test_inner_loop_phase2.py`, registered in `conftest.py::SLOW_FILES`). **125 green, 0 failed.**
- **The stack-wide sabotage test:** all six admissibility entry points monkeypatched with call counters, three `ChatRuntime.chat()` turns under `RuntimeConfig()` defaults → **all six at zero**.
- **The flag-on counterpart:** same instrumentation under `forward_graph_constraint=True`, four turns → `build_graph_constraint`=3, `filter_candidates`=3, all four inner-loop/rotor entry points still **zero**.
- **Ratifier liveness probe:** `CognitiveTurnPipeline` run → `ratification_outcome="ratified"`, `region_was_unconstrained=True`.
- Repo-wide producer search for `frame_versor` outside `tests/` (the check that decided ADR-0025's liveness axis) and for `region_for_intent` callers (the check that decided `AA-A4-2`).

**Not consulted / out of scope:** the `forward_semantic_control` lane was not re-run (`core demo phase5/phase6`); its committed reports were read instead, and their lack of SHA pinning is recorded as `AA-A4-10` rather than remedied. Stack A1 (rotor/algebra) was not available to this dossier; the algebra-coupling direction was verified from `generate/` only, and a reciprocal check is requested of A1 in §3.
