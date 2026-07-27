# Phase 2 — Findings, Corrections, and the Phase 3 Handoff

**Executor:** Opus 5, 2026-07-27. **Verified against:** `forgejo/main` @ `8927c563`.
**Deliverable:** nine layer cards in `10-layer-cards/` (M0, M1, M2, M3, M4, M5, M6, MG, MV), each schema-compliant per `03-card-schema.md`.

---

## 1. Corrections forced by re-verification

Phase 2's charter was to verify rather than inherit. Three inherited claims did not survive. Recording them prominently, because the *pattern* matters more than any single correction: **every falsified claim came from a document, and every falsification came from reading code.**

### 1.1 The L11 always-on process is BUILT (Phase 0 Finding 0-C was wrong)

`chat/always_on.py::run_continuous` (279 lines), `chat/always_on_daemon.py::run_daemon` (195 lines, single-instance lock, SIGINT/SIGTERM-wired stop, load-time identity guard), and CLI command `core always-on` (`core/cli.py:244`) all exist. They landed **2026-06-14** — five days *after* the `.system-map/` snapshot of 2026-06-09 that declared "no forever entrypoint exists." Phase 0 inherited the map's claim.

The real M6 finding is different and more actionable: the process is built, has a complete falsifiable soak harness (`evals/l10_always_on`, four predicates with `*_holds`/`*_bites` pairs), **has never been run to a recorded long-horizon artifact**, and is **enforced by no suite at all**.

### 1.2 Candidate CR-1 (attention/allocation) is not a missing layer — it is a live, undocumented one

Phase 1 registered attention as a possibly-missing function whose blueprint articulation (ADR-0008) had no successor. **The mechanism is live on the serving path.** `generate/stream.py::_attention_candidates` (`:255-263`) runs `SalienceOperator().compute(...)` then `AttentionOperator(inhibition_threshold).plan(...)`, and the resulting `allowed_indices` are intersected with language candidates at `:329` — replacing them outright at `:331` when language candidates are absent. `use_salience` defaults **True** (`core/config.py:35`).

Note also that `generate/salience.py` *composes* `core.physics.salience.SalienceOperator` (imported as `CurvatureSalienceOperator`) rather than duplicating it — so this is a layering, not the duplicate-implementation hazard it first appeared to be. That correction is recorded here rather than propagated as a false finding.

**CR-1 is therefore re-characterized:** not "does attention exist?" but "the mechanism that gates every generation step, and consumes ~73% of turn time through `cga_inner`, has no owning ADR, no card, and no layer in any ratified articulation." The blueprint's `InhibitionMask` class exists in `core/physics/inhibition.py` but is imported only by `core/physics/__init__.py` — the live inhibition is a scalar threshold, not the operator. The gap is **governance and documentation, not capability** — which makes it cheaper to close and easier to have missed.

### 1.3 Candidate CR-2 (agenda/drive) — the components exist; the claim survives and sharpens

Phase 1 recorded `DriveGradientMap` and `ExertionMeter` as never built. Both are constructed in `chat/runtime.py` (`:716`, `:714`). But:

- **`DriveGradientMap` is constructed and never read.** No site reads `self._drive_map`. Deleting it changes no output. By the sabotage test this is **decoration** — and it is the cleanest instance the assessment found.
- **`ExertionMeter` is exercised** (`record` at `:2912`, `fatigue` at `:2913`) but its output flows only into `drive_summaries` and `fatigue_index` — telemetry. **Fatigue gates no decision.**

So CR-2's substance is confirmed and stated more precisely: CORE has drive and exertion *objects* and no *chooser*. Nothing ranks what to do next. The mechanisms exist as instrumentation; the function does not exist as agency.

---

## 2. The stage-coverage audit

The taxonomy's central instrument, run with evidence. A stage is **covered** only where a live component owns it *and* carries evidence that would fail if the mechanism were deleted.

| Stage | Verdict | Owner | Basis |
|---|---|---|---|
| listen/ingest (text) | **covered** | M2 | `inject` on the live path, closure-checked at the gate |
| listen/ingest (non-text) | **uncovered** | M2 | `sensorium/` (59 modules) imports nowhere on the serving path; no projection heads |
| comprehend | **covered, narrowly** | M3 | Deduction bands `wrong=0` over 18,000 cases; reader spans 19 constructions vs a 1739-construction writer, fabricates on 22 |
| recall | **covered** | M1 | Exact CGA recall live; fabrication-control lane pinned |
| think/reason | **covered** | M3 | ROBDD entailment 716/716 against an independent oracle |
| articulate | **covered** | M4 | Live serving, ratified `wrong=0` lanes, typed refusal, negation now representable |
| learn from reviewed correction | **covered** | M5 | Two pinned loop-closure lanes prove the single reviewed path |
| replay deterministically | **covered** | MV | 11 SHA-pinned lanes, CI-failing on drift |
| *(the cycle's runner)* | **claimed-only** | M6 | Process exists; no measured horizon, no suite-enforced pin, continuity flags default off |

**Seven of nine covered; one uncovered by deliberate scoping; one — the runner — claimed-only.** The single uncovered *stage* is non-text ingest. The single unproven *layer* is the one the telos names.

---

## 3. Cross-cutting findings

**F-1 — Built-and-off is the dominant pattern, and it is unaccounted.** Across layers, substantial machinery exists behind flags that default `False`: `unified_ingest`, `curriculum_serving_enabled`, `ask_serving_enabled`, `verified_serving_enabled`, `consolidate_determinations`, `review_pending_proposals`, `review_derived_close_proposals`, `auto_contemplate`, `auto_proposal_enabled`, `vault_promotion_enabled`, `persist_session_state`, `strict_identity_continuity`, `identity_wave_gate`, `identity_action_surface`, `realizer_grounded_authority`, `accrue_realized_knowledge`, `estimation_enabled`. Only `deduction_serving_enabled` is ratified ON. Each default is individually defensible; **no document states the set**, nor what evidence would flip any of them. This is the largest single lever in the system and it has no register.

**F-2 — Enforcement lags capability, most where it matters most.** M6's soak pins run in no suite; M1's no-approximate-recall prohibition has no verified failing pin; MG's cross-cutting writ has no bypass pin. In each case the *mechanism* is sound and the *guarantee that it stays sound* is doctrinal rather than mechanical. MV's hand-curated suite tuples cannot detect an orphaned pin — the highest-leverage single fix the assessment has found.

**F-3 — The strongest in-repo standard is not applied where exposure is highest.** M5's formation pipeline declares six trust boundaries, content-addressed in and out, no floats in hashed payloads, no pickle, an audit record for every rejection. M2 — the boundary facing untrusted user text in production — has no comparable declared table. The bar exists; it has not been carried to the hotter surface.

**F-4 — Documentation debt is now load-bearing, not cosmetic.** `chat/always_on_daemon.py` has no ratifying ADR while the governing ADR-0146 explicitly *rejected* the daemon shape. The live attention mechanism has no ADR. The `MIND-PHYSICS-BLUEPRINT` renderer line is stale. ADR-0252's "34 surface organs" does not reproduce (**18** `resolve_promotable_*`, all in `generate/derivation/`). When the record contradicts the code, every downstream reasoner inherits the error — as Phase 0 did.

**F-5 — What is excellent, stated plainly.** The typed learning boundary (M5) dissolves the autonomy-versus-safety trade-off rather than splitting it. The selection-not-rewrite surface discipline (M4) preserves the honest artifact even when it is not served. The non-hardening invariant (M1) structurally forbids an axiom flag. Fail-closed unknown lane shapes and NON-CANONICAL run stamping (MV) are the habits of a system that expects to be wrong. Phase 5 should carry these forward as the standard other layers are measured against, not merely as an audit's polite paragraph.

---

## 4. Layer verdict summary

| Layer | Liveness (re-verified) | Fitness | The one-line reason |
|---|---|---|---|
| M0 Substrate | `live-serving` | `fit` | Does one thing without compromise; optimization has twice aimed at the wrong function |
| M1 Knowledge & Memory | `partial-wiring-debt` | `fit` | Exactness and typed standing reinforce each other; what compounds vs resets is invisible in the name |
| M2 Afferent Boundary | `partial-wiring-debt` / `inert` | `strained` | 59 modules reach no serving path; the trust-boundary bar exists elsewhere in-repo |
| M3 Comprehension & Reasoning | `partial-wiring-debt` | `strained` + `superseded-in-place` | Expert substrate, novice reader — ratified diagnosis, unrun acceptance gate |
| M4 Expression & Serving | `live-serving` | `strained` | Excellent discipline; surface precedence accreted one arm per capability |
| M5 Learning & Growth | `partial-wiring-debt` | `fit` / `strained` | Best-executed idea in CORE, 24×–73× under-fed |
| M6 Continuity & Process | `partial-wiring-debt` | `strained` | Built further than reported, proven less than assumed, enforced by nothing |
| MG Governance & Identity | `live-serving` | `fit` / `strained` | Alignment as structure; enforcement gate off and unauthorized |
| MV Verification & Evidence | `partial-wiring-debt` | `strained` | Right instincts; coverage is a curation artifact with a hole at the worst spot |

No layer is `wrong-solution`. Two candidate `wrong-solution` findings are deferred to Phase 4 with evidence: the Wilson/replay independence basis in M5's licensing, and `DriveGradientMap` as constructed decoration.

---

## 5. Handoff to Phase 3

**Deliverable:** component cards in `20-component-cards/`, per `03-card-schema.md` §6 depth allocation.

**Descent order:**
1. **The four ⚑ zero-subsystem zones**, all load-bearing, three on the serving path: `comprehend-organ` (→ `core/comprehension_attempt/`, 6 modules), `determine-phase` (→ `generate/determine/`, 8 modules), `realize-phase` (→ `generate/realize/` + `realizer.py` + `realizer_guard.py`), `sensorium-falsification` (→ `sensorium.environment.falsification`).
2. **M6's built half** — `engine_state/`, `chat/always_on.py`, `chat/always_on_daemon.py`, and the `evals/l10_*` harnesses. Establish what the soak *would* prove if run.
3. **M3's derivation organs** — resolve the 34-vs-18 count against ADR-0252's diagnosis. This determines whether the debt is being paid down or was measured differently.
4. **M4's surface-selection arms** — enumerate every arm and its precedence; this is the input to the Phase 4 Third-Door question.
5. **The CR-1 attention mechanism** — `generate/salience.py`, `generate/attention.py`, `core/physics/{salience,attention,inhibition}.py`. It gates every generation step and owns the hot path; it needs a card regardless of how the layer question is ruled.

**Verification obligations (non-negotiable):**
- Stamp `verified_at` with the SHA actually inspected. The system map is a prior; 2026-06-09 is stale by two major arcs.
- Apply the sabotage test to every `live-*` claim. `DriveGradientMap` shows the failure mode is present in this tree, not hypothetical.
- For every invariant cited, name its pin **and** confirm the suite that runs it. Several Phase 2 cards had to record `suite: none`.
- Distinguish *imported* from *constructed* from *read* from *gating a decision*. All four appear in this tree and only the last is load-bearing.

**Standing:** PR #138's fabrication findings are measured-and-pinned, held for ADR + ratification — record, never re-discover, never fix.

**Open items for Phase 4 seeded by Phase 2:** the flag-default register (F-1); the orphaned-pin meta-check (F-2); M2 adopting formation's trust-boundary table (F-3); the ADR/code contradictions (F-4); Wilson/replay independence in licensing; `DriveGradientMap` deletion; surface-precedence as a declarative table; the `evals/l10_*` suite assignment.
