# Phase 3 — Findings, Corrections, and the Phase 4 Handoff

**Executor:** Fable 5, 2026-07-27. **Verified against:** `forgejo/main` @ `8927c563`.
**Deliverable:** eight component cards in `20-component-cards/` — the four ⚑ zero-subsystem zones (`comprehend-organ`, `determine-phase`, `realize-phase`, `sensorium-falsification`) plus `always-on-process`, `derivation-organs`, `surface-selection`, `attention-allocation`.

The assessment's correction chain continued into its third phase, in the same direction every time: **documents (including this assessment's own earlier phases) overstate or understate; code decides.** Phase 2 corrected Phase 0; Phase 3 corrects Phase 2 twice and the system map three more times.

---

## 1. Corrections

**C-1 — Three map `live-serving` labels demoted to `live-internal`.** `comprehend-organ` (`core/comprehension_attempt/` — imported by neither serving entrypoint; its consumers are the flag-gated ask path, proposal review, and eval lanes), `determine-phase`, and `realize-phase` (both reachable only through `_accrue_in_turn` / `idle_tick`, gated by flags that default False). **No default-config serving turn touches any of the three.** The map called all three live-serving; the serving path they were presumed to sit on runs through `proof_chain`/`curriculum_surface`/the realizer instead.

**C-2 — Phase 2's M6 card overstated ephemerality.** "T1 vault and field discarded on exit by design" is the *default-config* posture. Under the daemon, `persist_session_state=True` activates **Shape B+** persistence ("restored bit-exactly", `chat/always_on.py:9`; sites at `chat/runtime.py:893–952`). The residency mechanism exists, is opt-in, and is daemon-forced; what remains open is its exact coverage and horizon proof. Banner added to the M6 card.

**C-3 — Phase 2's M4 card understated the resolver.** `core/cognition/surface_resolution.py` (494 lines) *is* a declared-precedence resolver for the pipeline seam (served-bytes-wins base selection, canonical-first truth path, abstention, hedge admissibility, substrate folds). The accretion concern survives only for the upstream composer arms in `chat/runtime.py`. The Third-Door candidate refines from "create a resolver" to "extend the existing resolver's pattern upstream." Banner added to the M4 card.

**C-4 — The 34-vs-18 organ discrepancy is resolved: basis mismatch, not paydown.** At the ADR-0252 ratification commit itself (`1ccef491`) the tree already had exactly **18** `resolve_promotable_*` entry organs across 33 tree entries. "34" plausibly counted modules (~32–33 including support modules), never entry organs. Consequences: no consolidation has occurred since ratification, and the governing ADR's headline number has no stated basis — a one-sentence amendment fixes it.

**C-5 — A prior verification document is contradicted at this SHA.** `architecture-assessment-verification-2026-07-25.md` §2 claims `accrue_realized_knowledge` "is enabled by the production L10 process." `CONTINUOUS_LIFE_CONFIG_FLAGS` is exactly `{persist_session_state, consolidate_determinations, strict_identity_continuity}` — accrual is **not** in it.

---

## 2. New findings

**F-6 — The continuous life may consolidate an empty set.** The daemon forces the *consolidator* on (`consolidate_determinations`) but not the *accruer* (`accrue_realized_knowledge`) — and `realize_comprehension`, the only turn-path writer of realized facts, sits behind the accrual flag. As coded, the always-on life's Step-D learning loop may have nothing to work on unless facts are seeded some other way. Either the flag set is incomplete or the dormancy is intended; **neither reading is documented.** This is the sharpest single new finding of Phase 3: the two halves of the lived learning loop are gated by different flags and only one is forced.

**F-7 — The allocation layer landed, mutated, without governance.** ADR-0008's Allocation Physics is live in composed form: physics curvature kernel → generation-facing `SalienceOperator` → `AttentionOperator` scalar-threshold plan → candidate intersection in the walk, with the salience `budget` fed back so attention *self-narrows* across a walk (`stream.py:637`). `InhibitionMask` is decoration (imported by `__init__` only, never constructed on any path). The tuned constants (`top_k=16`, `threshold=0.3`) have no recorded derivation. CR-1's ruling question is now precise: own the flag, the two constants, the feedback loop, and the mask's disposition — a one-page ADR.

**F-8 — Two naming traps are load-bearing.** `comprehend-organ` is a *math setup router*, not the chat comprehension organ (that is `generate/meaning_graph/reader.py` — the two-grammars reader, 19 constructions, fabricating on 22, measured/pinned/held). `generate/realize/` (knowledge realization) vs `generate/realizer.py` (surface realization) are unrelated mechanisms with confusable names. Both traps would misdirect a grep-first investigation; both cards carry permanent disambiguation.

**F-9 — REALIZE is sound; its ceiling is its feeder.** The realize phase holds whatever the reader hands it, at honest SPECULATIVE standing, with full derivation provenance. The truth-defect class is entirely upstream in the reading — consistent with fix-upstream doctrine and with holding the #138 fixes for a serving-truth ADR. A defensive option for that ADR: refuse to *hold* a reading whose construction lies outside the reader's verified inventory, converting inventory truth into a mechanical gate at the holding boundary.

**F-10 — A silent-failure pinhole in a typed layer.** `_accrue_in_turn` wraps the reader/DETERMINE/REALIZE chain in a broad guard that converts any exception into a no-op accrual with no telemetry. Honest as a backstop; invisible as a failure signal.

---

## 3. Phase 4 seed list (consolidated from Phases 2–3)

**Hindrance-audit candidates (`31-hindrance-audit.md`):**
1. Wilson/replay independence in license counting — possible `wrong-solution` in the counting basis; 21/25 bands affected (Phase 2).
2. `DriveGradientMap` constructed-never-read; `InhibitionMask` exported-never-constructed — deletion candidates (mastery step 2).
3. The empty-string refusal at the public `str` boundary — truth constructed, then discarded (M4/surface-selection).
4. Composer-arm precedence: extend `surface_resolution`'s declared-precedence pattern upstream (refined Third Door).
5. The F-6 flag-set incoherence (consolidator without accruer).
6. Tuned constants without derivation at the semantic center (`top_k=16`, `threshold=0.3`, `admissibility_margin=0.4` has a recorded derivation — the contrast is instructive).
7. M2 lacking formation's trust-boundary table (F-3).
8. ADR/code contradictions: unowned daemon vs ADR-0146's Shape-A rejection; ADR-0252's unreproducible "34"; the 2026-07-25 doc's accrual claim (C-5).

**Gap-register candidates (`30-gap-register.md`):**
1. The #138 fabrications — pre-labeled *measured & pinned, fix held for ADR + ratification*.
2. Reader inventory 19-wide vs writer 1739 (close fabrications before widening, per standing ruling).
3. No suite runs any `l10`/`always_on` pin; no soak artifact; no nightly (and the local-first/Mac-runner doctrine makes "nightly" itself need a ruling).
4. Non-text ingest uncovered; sensorium's 59 modules disconnected; no entry criterion.
5. No flag-default register (F-1: 17 flags, only deduction ON, no document states the set — now nuanced by the daemon's forced trio).
6. No orphaned-pin meta-check (F-2 — the mechanism by which M6's harness went unscheduled).
7. Curriculum query-scoping (the ADR-0264 §4.1 blocker); the absent curriculum serve ledger.
8. CR-2 agenda/drive: mechanisms without a chooser (confirmed at component depth); CR-3 efferent ruling; CR-4 temporal stance.
9. ADR-0252 §5 experiment unrun — the top open item, now with stakes note: GSM8K's demotion mispriced the experiment, but the paradigm governs *all* future comprehension.
10. The Candidate Register items needing one-line rulings vs real design work — separate them.

**Verification obligations for Phase 4:** the registers decide nothing — every entry carries evidence pointers and names its deciding authority (ruling vs ADR vs mechanical fix). Rank by leverage, not ease, per the AGENTS.md protocol. Where a hindrance names a better home, name the evidence too.

---

## 4. Note on method, for the record

Three phases in, the correction ledger reads: Phase 0 inherited a stale map claim (always-on "unbuilt"); Phase 2 caught it by reading code, then itself overstated ephemerality and understated the resolver; Phase 3 caught both by reading deeper, and demoted three more map labels. **Nothing in this chain was caught by re-reading documents.** The assessment's value is exactly proportional to how much code each phase actually read — which is the empirical vindication, inside the assessment itself, of `AGENTS.md` protocol step 1 and the mastery framework's demand that constraints trace to verifiable ground.
