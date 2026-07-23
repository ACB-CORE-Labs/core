# Weekly Audit — 2026-07-22 — cleanup-week integrity pass, stragglers, and TODO

**Scope**: main from PR #76 (`compare_multiplicative` increment plan) through
PR #97 (`logos` bulk live morph authority) — the week that landed the reader-arc
recalibration (ADR-0251), the paradigm consolidation (ADR-0252), the Master
Blueprint collision freeze (ADR-0253 + mapping), and Master Convergence
Stages 1–4 (#95) plus #96/#97. 134 files, +17,028/−770.

**Auditor**: Claude (session audit), read-only verification against
`forgejo/main` @ `f94dbd40` plus doctrine-authorized hygiene cleanup.

---

## 1. Verified sound (no action)

- **Smoke suite green on landed main**: 180 passed, 0 failed (2:17),
  `uv run core test --suite smoke -q` @ `f94dbd40`.
- **`uv lock --check`**: lock file consistent with `pyproject` (217 packages).
- **ADR status registry vs. mapping doc**: ADR-0240 Proposed; 0241–0250 and
  0252–0253 Accepted; 0251 partial (§§1–4 ratified) — matches
  `MASTER-BLUEPRINT-2026-07-20-ADR-MAPPING.md` registry table exactly.
- **Superseded-in-place annotations** (ADR-0164, ADR-0174, ADR-0243 sketch
  pins, ADR-0244 dual-mode excision rewrite) are present and accurate against
  code: no `_axis_projection` / `_mean_frame_coherence` / scalar-L2 remnants in
  `core/`; `tests/test_stage2_physics_hardening.py` pins the removed symbols
  as absent.
- **ADR-0252 §9 retirement record**: all five formulations physically moved to
  `docs/paradigm-archive/` with git history preserved (`--follow` verified);
  old paths gone from `docs/analysis|handoffs|implementation`.
- **Gate defaults match doc claims**: `RuntimeConfig.identity_wave_gate = False`
  (`core/config.py:301`) — consistent with ADR-0244's "live refusal remains
  flag-gated" and the standing non-authorization.
- **No new TODO/FIXME/HACK markers** entered `*.py` across the whole week's
  diff; no merge-conflict markers anywhere in tracked `*.py`/`*.md`.
- **New `scripts/measure_trackb_*.py`** are referenced by the Track-B research
  dossiers (not orphans).
- **`epistemic-taxonomy-ownership-stage3.md`** placement in `docs/adr/` is
  deliberate (binding ownership note, not an ADR renumber) — now indexed from
  `docs/adr/README.md` (fixed in this PR).

## 2. Small issues fixed in this PR

1. **ADR-0132 dangling parent pointer** — pointed at
   `docs/implementation/semantic-symbolic-binding-graph-proposal.md`, which
   ADR-0252 §9 moved to `docs/paradigm-archive/`. Pointer updated with the
   retirement annotation.
2. **Stale near-duplicate of ratified ADR-0243** —
   `docs/research/ADR-0243-…md` still carried `Status: Proposed` and had
   drifted from the canonical body by a few annotation lines. Replaced with a
   tombstone pointing at the canonical Accepted ADR; the one annotation unique
   to the copy (`modality_transition_sandwich` ingress note) is preserved in
   the tombstone.
3. **`docs/adr/README.md`** — added an index entry for the binding
   non-ADR ownership note (`epistemic-taxonomy-ownership-stage3.md`), which was
   referenced nowhere.

## 3. Hygiene cleanup performed (session, no PR needed)

Per the merge-then-cleanup doctrine (branch AND worktree deleted immediately
after merge) — all four verified clean and fully merged before removal:

- Worktrees removed: `core-postmerge-pr87-integrity-audit` (#88),
  `core-relational-operator-ablation` (#87), `core-wt-trackb` (#85),
  `core-wt-trackb2` (#86); matching local branches deleted.
- Forgejo remote branches deleted (0 commits ahead of main):
  `feat/trackb-symbolic-sme-s1`, `feat/trackb-symbolic-sme-s2s4`,
  `fix/a2k-fraction-decrease-scale-range`.
- Local `main` fast-forwarded to `forgejo/main` (`f94dbd40`).

## 4. TODO — items needing a ruling or deeper investigation

- [ ] **T1 (governance): register convergence-era runtime invariants — or rule
  that tests suffice.** `docs/specs/runtime_contracts.md` cites no ADR newer
  than the 0230s. The week landed several fail-closed runtime invariants that
  are currently enforced only by code + architecture tests: ADR-0244 wave-only
  identity (`MissingWaveStateError`), ADR-0253 dual-pack serve boundary
  (`tests/test_pack_draft_serve_boundary.py`), #96 fail-closed linguistic
  governance phases, #97 bulk live morph authority. `AGENTS.md` invariants
  (INV-…) also saw zero changes all week. Decide: add contract entries /
  INV lines, or record explicitly that the arch-test layer is the SoT here.
- [ ] **T2 (runtime state): stale `engine_state/` checkpoint.** Smoke emits
  `RuntimeWarning: engine_state checkpoint was written at revision '4b9dbe72…'
  but the current revision is 'f94dbd40…'` (`chat/runtime.py:807`). Given
  continuity doctrine, clearing is NOT something to do casually — decide
  whether to re-baseline the checkpoint on current main or keep it and accept
  the warning.
- [ ] **T3 (worktree): Antigravity worktree
  `~/.gemini/antigravity/worktrees/core/implement-substrate-linguistic-anchors`**
  — branch tip is ON main history (0 ahead) but the tree has 4 uncommitted
  files. Likely superseded by PR #96 (linguistic governance). Reconcile the
  4 files, then remove worktree + branch.
- [ ] **T4 (worktrees): two stale detached demo worktrees** —
  `/private/tmp/builder-ii-flagship-demo/demo-worktree` and the
  `grok-goal-…/recipe3_demo_loop/demo-worktree` under `$TMPDIR`, both clean,
  detached @ `18c578d9`. Remove via `git worktree remove` once confirmed no
  running demo serves from them (left alone in this pass for that reason).
- [ ] **T5 (branch garden): stale branch sweep.** ~50 local branches (many
  `audit-*`, `backup/*`, `chore/*` from May–June) and ~210 `origin/*` branches
  on the GitHub mirror. Needs a batched merged-vs-unmerged triage; separate
  authorization before any mass deletion.
- [ ] **T6 (active experiments): ADR-0252 §5 structure-mapping worktrees** —
  `core-wt-sme` (`rnd/structure-mapping-experiment`, 1 ahead) and
  `core-wt-sme2` (`rnd/sme-experiment-v2`, 1 ahead + 2 untracked scripts:
  `extract_sme_corpus.py`, `test_single_pair.py`). Active and authorized; track
  them to a dossier/PR so the untracked scripts don't rot outside history.
- [ ] **T7 (ADR annotation): `modality_transition_sandwich` sentence** — the
  annotation preserved in the ADR-0243 research tombstone exists nowhere in the
  canonical ADR. If it is load-bearing for the SD-B pin record, fold it into
  the canonical ADR-0243 annotation under a separate small ruling.
- [ ] **T8 (declared debt, consolidation): fold the week's declared residuals
  into next-arc planning.** #97's honest accounting
  (`docs/analysis/logos-bulk-live-authority-residual-2026-07-20.md`) lists six
  open residuals (parallel `generate/linguistic_pipeline` cue tables, lexicon
  breadth, legacy math/meaning_graph IR outside the morph seam, holonomy crown
  not LIVE, disconnected pack frames, single `plural_abstain` rule type). These
  are declared debt, not stragglers — but they now live only in an analysis
  doc; pull them into whatever planning artifact governs the next Logos/IR arc
  so they don't silently age out.
- [ ] **T9 (docs, minor): historical docs referencing pre-archive paths** —
  `docs/workbench/capability-mastery-implementation-plan.md:33,85-86` and
  `docs/briefs/parallel-2026-05-23/L2-opus2-binding-graph-phase1.md` cite the
  retired paradigm docs at their old `docs/analysis|implementation/` paths.
  Both are point-in-time records; either leave as history (default) or annotate
  with the archive location. No governance weight either way.

---

## Rulings & execution addendum (2026-07-22, same day)

Shay ruled on T1–T9 (pillars: epistemic rigor / absolute provenance /
fail-closed determinism). Execution status:

| Item | Ruling | Status |
|------|--------|--------|
| T1 | Tests = executable SoT; contracts/AGENTS = governance SoT — register | **DONE** (this PR): INV-32/33/34 in `AGENTS.md` + new/updated sections in `docs/specs/runtime_contracts.md` (wave-only identity, dual-pack boundary, linguistic governance, morph authority) |
| T2 | Re-baseline to `f94dbd40` with migration trace | **DONE + root cause found.** Baseline gen-21702 @ `f94dbd404575` (turn 14990, `engine_identity` parent==self `c9e5968a…`, scheme 2, schema v2, packs byte-identical across the gap → reconcile MATCH; no `MissingWaveStateError` exposure — identity consumes the live per-turn field and Shape B+ session persistence is opt-in-off). The warning churn's root cause was the suite itself writing the live store — see T10 |
| T3 | Diff antigravity files vs #96; salvage or scrap | **DONE**: not #96 material — an un-ADR'd anchor-lens/Hamiltonian experiment (fail-open `except: pass`, unratified serving-physics mutation). Salvaged with full diff → `docs/analysis/antigravity-substrate-linguistic-anchors-salvage-2026-07-22.md`; worktree + branch scrapped |
| T4 | Nuke /tmp demo worktrees | **DONE** (both removed; worktree list is now 5, all live) |
| T5 | Hard prune all stale branches; stash unknowns | **DONE locally**: 178 local branches pruned, every tip SHA stashed in `docs/analysis/branch-prune-ledger-2026-07-22.md`. **Origin mirror (204 branches) pending**: bulk remote deletion was tool-permission blocked; operator command in the ledger doc |
| T6 | No untracked logic in active workspaces | **DONE**: both scripts formalized → `rnd/sme-experiment-v2` @ `bed29a09`. Hazard found & fixed pre-commit: the extractor's glob read ALL of `evals/gsm8k_math/**` (practice/dev/train/public), exceeding the §5 `holdout_dev/v1`-only authorization — now scope-pinned |
| T7 | Fold `modality_transition_sandwich` into canonical ADR-0243 | **DONE** (annotation folded; tombstone updated to point at it) |
| T8 | Escalate #97 residuals into this ledger | **DONE** — R1–R6 below |
| T9 | Global sweep of pre-archive paths | **DONE**: 6 references across 3 docs redirected to `docs/paradigm-archive/` with per-file provenance notes (ADR-0252 §9 retirement record + archive self-references left as deliberate history) |

### New findings from the execution pass

- [x] **T10 (FIXED + MERGED — PR #100 @ `80100c18`): the test
  suite wrote the live life-store.** Module-scoped fixtures (e.g.
  `tests/test_achat.py`) construct `ChatRuntime()` BEFORE the function-scoped
  isolation fixture exists (pytest sets up wider scopes first), binding the
  real `engine_state/`: smoke runs loaded it and committed generations
  (turn_count 14989→14990 observed). Fix: session-scoped baseline fixture +
  regression pin; `docs/issues/default-engine-state-test-hygiene.md` addendum.
- [x] **T11 (RULED + EXECUTED 2026-07-22): live-store provenance reset.**
  DECISIVE FINDING: candidates carry NO timestamp / run-id / test-prod field
  (only a `source_turn_trace` hash + `review_state`), and gen-21701 == gen-21702
  were byte-identical — "the 465" was the ENTIRE live candidate corpus, not a
  separable tainted subset, so a surgical per-record quarantine (the original
  `TEST_TAINTED` spec) was impossible. The candidates were inert (proposal /
  contemplation only, never the serving surface). **Ruling (Shay): Option (a) —
  clear, don't asterisk.** Executed via
  `scripts/ops/reset_candidate_corpus_t11_20260722.py`: an ADR-0219 atomic
  generation reset (begin → carry recognizers/session/identity+turn_count →
  empty candidate ledger → commit `keep=1`). Result: candidates 465 → 0,
  `turn_count` 14990 preserved, gen-21701/21702 physically GC'd, `current` →
  gen-21703 @ `9a428d84`. Idle-tick discovery repopulates organically.
  **`turn_count` itself left as-is** (honest lived count; the pre-fix test turns
  are not separably identifiable, and resetting the counter would fabricate a
  number — the candidate corpus was the provenance hazard, not the scalar).
- [ ] **T12 (pattern watch): experiment scaffolding scope over-reach.** The T6
  glob hazard suggests a cheap architecture pin: `rnd`/scripts corpus readers
  should be lint-checked against sealed/practice eval paths.

### R1–R6 — PR #97 declared residuals (escalated per T8; source:
`docs/analysis/logos-bulk-live-authority-residual-2026-07-20.md`)

- [ ] **R1** — `generate/linguistic_pipeline` cue tables (English "sold"/"mkr"
  hand maps) remain a parallel constraint producer on the governance demo
  path; they consult no `packs/data/he_*` morphology and are not answer
  authority. Migrate onto the Logos morph seam or retire.
- [ ] **R2** — lexicon breadth: only `he_logos_micro_v1` observed surfaces; no
  full HE/GRC tables, no binyan universals, no GRC case→role.
- [ ] **R3** — legacy math / meaning_graph IR still parallel outside the Logos
  morph seam; not migrated onto `semantic_primitives`.
- [ ] **R4** — holonomy crown not robust; no LIVE claim.
- [ ] **R5** — pack frames largely disconnected (sense disambiguation);
  first-match pack semantics unchanged outside the morph rule.
- [ ] **R6** — one rule type only (`he_morph_v0.plural_abstain`);
  construct-state / prep+case / aspect deferred.
- [ ] **R7** (opened by the T13 fix, 2026-07-22) — the opt-in telemetry SINK
  stream (`attach_telemetry_sink`) still receives the pre-override `TurnEvent`
  (pre-resolution surface + empty `trace_hash`) — the same provisional-then-
  back-stamped limitation `finalize_turn_trace_hash` already carries. A single
  deferred sink emission at the pipeline serve boundary would repair BOTH
  surface and `trace_hash` in the durable stream. Deferred (default sink is
  `None`, so no live consumer is affected today); own PR when a sink consumer
  lands.
- [x] **T13 (main regression, serving-provenance — telemetry FIXED + MERGED #101):
  fast lane was red on main** (was 0-red 2026-07-16):
  `tests/test_warmed_session_lane.py::TestPipelineOverrideGateInvariants::test_telemetry_consistency_rate_is_one`
  fails at 0.9444 (17/18). Verified pre-existing on unmodified main (fails
  plain AND state-isolated; unrelated to the T10 isolation fix). Root cause:
  `CognitiveTurnPipeline.run()` emits `TurnEvent` inside `runtime.chat()`
  (`core/cognition/pipeline.py:287`) and only THEN applies the PR #96
  fail-closed surface resolution (`resolve_surface`, line 470) and the PR #97
  logos morph override (~line 517) — so an overridden turn serves a surface
  telemetry never saw. Introduced by `e0d1b475` (#96). Reproducer: warmed
  case "What is doubt?" — TurnEvent carries the pack-grounded surface
  ("To doubt means to think maybe not. pack-grounded (en_core_meta_v1).")
  while the pipeline returns the typed refusal ("I cannot certify an answer:
  the geometric coherence contract is open (goldtether_residual)."). Two
  decisions for the fix PR: (1) restore single-point surface truth — emit
  (or re-stamp) `TurnEvent` AFTER surface resolution; runtime_contracts'
  selection policy + this lane must move in the same PR per the contract's
  own rule; (2) rule whether an open goldtether residual should refuse a
  pack-grounded, honestly-hedged definition at all (possible over-refusal —
  the pack surface never claimed geometric certification). Note: smoke does
  not cover this lane, and GitHub Actions are dead signals — nothing gates
  fast-lane red on main right now.

  **Resolution (2026-07-22, PR #101 `fix/telemetry-serve-boundary` @ `9a428d84`, MERGED):**
  - **(1) FIXED** — `ChatRuntime.finalize_turn_surface` back-stamps the
    pipeline's resolved surface onto `turn_log[-1]`, a sibling to
    `finalize_turn_trace_hash`, called from `pipeline.py` immediately after
    the trace-hash back-stamp. Lane green: `telemetry_consistency_rate`
    0.9444 → 1.0 (10/10 warmed_session tests pass). `trace_hash` byte-identity
    preserved — it folds the pre-decoration surface, not the served surface.
  - **(2) RULED + IMPLEMENTED (PR #103, `feat/grounded-open-geometry-hedge-arm`, ADR-0254).**
    Ruling: fix the READING, not the question — route open-geometry-but-**pack-grounded**
    surfaces to a hedge arm (`authoritative=False`, honestly hedged), discriminated
    by grounding *provenance* (structural), never by question type (the query-type
    classifier bypass was REJECTED as a fail-open cue-table; ADR-0252 + INV-34).
    Built: the decision lives **inside the gate** (`resolve_surface`) — predicate
    `pack_grounded ∧ every open token ∈ {versor_condition, goldtether_residual}`.
    `¬hazard` is enforced structurally by that residual allowlist: any unrecognized
    open token (where a real safety/harm hazard lands), non-pack grounding, or
    `None` assessment → unchanged hard refusal. New authority tag
    `grounded_open_hedge`. Validation: RED→GREEN unit suite +
    `warmed_session_consistency` real-data (the "What is doubt?" over-refusal now
    hedges) + GSM8K `wrong=0` preserved + architectural invariants green.
    **Deferred:** unifying the hedge marker with the ADR-0038 manifold
    `preferred_hedge_soft` vocabulary (defer substrate-vocab commitment).
  - **(3) RULED (Shay, 2026-07-22): local pre-push gate — IMPLEMENTED.**
    `scripts/hooks/pre-push` + `scripts/hooks/install.sh` (`core.hooksPath`) run
    the smoke suite **plus** the warmed_session lane pin on every push — the
    targeted gate (NOT the ~9-min full fast-lane, which stays async CI).
    AGENTS.md §Local-First CI Validation Protocol updated. (This PR.)
  - Durable-sink residual tracked as **R7** above.
