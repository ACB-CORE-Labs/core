# Batch 4 — Tier A Remainder (44 files across ADR-0151–0200) — REDO

**Verified against:** `main` @ `cbfc8ccb` | **Auditor:** Claude (subagent, Batch-4 remainder) | **Date:** 2026-07-29
**Supersedes for this range:** the retracted `AA-352`…`AA-377` (see `20-finding-register.md` §RETRACTION NOTICE). Findings carry their final corpus IDs `AA-515`–`AA-540` (see `20-finding-register.md`).
**Excluded (already carded):** 0164, 0164.1–.4, 0165, 0174, 0175 (`Batch4-TierA-reader-reliability-redo.md`); 0180, 0181, 0196, 0197 (`Batch4-TierA-carryforward-redo.md`).
**Collisions** carded separately with census audit IDs: `0163~1`/`0163~2`, `0178~1`/`0178~2`, `0184~1`/`0184~2` (`01-adr-census.md` §1).

## Headline

The sibling dossier's closing pattern — *`Proposed`/`Draft` ADRs functioning as live, cited, test-enforced authority* — **is the dominant condition of this range, not an exception**: **25 of 44 files** carry a status line contradicted by what is built. Five of them say so on their own status line (`Proposed (implemented in this PR)`); four more say `Proposed … no runtime mutation in this PR` while being the sole authority for a live pack-mutation boundary. The corpus already contains the fix precedent: **ADR-0170 reconciled its own stale status on 2026-06-15** (`AA-515`).

Two things are worse than record drift and are raised as 🔴: a shipped CI workflow that ratifies proposals and pushes the active teaching corpus to `main` in direct contradiction of the trust boundaries of the two Accepted ADRs it cites (`AA-516`), and the FrameClaim/CompositionClaim pack-mutation boundary whose only governing doctrine is unratified (`AA-517`).

---

## 1. Contemplation → auto-proposal → checkpoint arc (0151–0159)

### ADR-0151 — Auto-Proposal Pipeline at Load
- **Build** full. `chat/runtime.py:915-916` inside `_load_engine_state` (`:832`) gates on `config.auto_proposal_enabled` (`core/config.py:277`, default `False`) and calls `_auto_propose_from_candidates`.
- **Liveness** live-but-opt-in; `tests/test_adr_0151_auto_proposal.py` exercises both flag states.
- **Design fidelity** pass. Load-time (not checkpoint-time) placement keeps turn completion a pure checkpoint — Axiom 3 respected.
- **Build fidelity** matches, including the determinism contract (`proposal_id` over `(candidate_id, proposed_chain)`).
- **Continuity** clean. **Fitness** test-pinned + exercised by the learning-arc demo. **Necessity** irreducible.
- One inherited hazard: its §Trust Boundary ("never writes the active teaching corpus") is contradicted downstream — `AA-516`.

### ADR-0152 — Learning-Arc Demo
- **Build** full: `evals/learning_arc/run_demo.py`, wired at `core/cli.py:1838-1839`, listed at `:1470`. **Liveness** live (CLI + the contemplation workflow's payload). **Design fidelity** pass — tempdir-only writes, byte-identical active corpus asserted.
- **Build fidelity** matches; `tests/test_learning_arc_demo.py` present. **Continuity** clean. **Fitness** it is the input artifact for ADR-0159's eval lane — real downstream consumer. **Necessity** irreducible (the only observable engine-authored-vs-operator-authored contrast).

### ADR-0153 — TurnEvent `trace_hash` back-stamp
- **Build** full: `trace_hash: str = ""` at `core/physics/identity.py:668`; `ChatRuntime.finalize_turn_trace_hash` at `chat/runtime.py:1196`; called from `core/cognition/pipeline.py:894` after `compute_trace_hash`, exactly as specified.
- **Liveness** live on the main turn path. **Design fidelity** pass (Axiom 5 — provenance reconstructed, not duplicated). **Build fidelity** matches, incl. the halt-at-first-stamped back-walk. **Continuity** clean. **Fitness** `tests/test_adr_0153_trace_hash_backstamp.py` pins the on-disk effect, not just the field. **Necessity** irreducible.
- Its own §Out of scope (OOV candidates, same root cause) remains open — disclosed, not drifted.

### ADR-0154 — DerivedRecognizer producer wiring
- **Build** full: producer at `core/cognition/pipeline.py:257-262`, inside `if _rec_outcome.admitted`, guarded by `hasattr`. **Liveness** live and unconditional, as specified. **Design fidelity** pass. **Build fidelity** matches. **Continuity** clean. **Fitness** `tests/test_adr_0154_recognizer_producer_wiring.py`. **Necessity** irreducible.
- **The one real gap is its own disclosed hazard, now shipped as the default:** producer unconditional + consumer `recognition_grounded_graph=False` (`core/config.py:251`) + no cap on `_pending_recognizer_examples` (`chat/runtime.py:787,1194`) = the exact configuration the ADR said needed a bound first. `AA-518`.

### ADR-0155 — CI contemplation runner
- **Status `scoping`** — the weakest status in the range, yet `.github/workflows/contemplation.yml` shipped verbatim to spec (schedule, `workflow_dispatch`, `CONTEMPLATION_ENABLED` soft kill, `peter-evans/create-pull-request@v7`, concurrency group).
- **Build** full. **Liveness dead.** `contemplation/runs/` contains exactly two reports, both dated 2026-05-26; nothing since. Sabotage: delete the workflow and no measurement changes.
- **Design fidelity violation (Pillar I, Mechanical Sympathy).** The whole rationale — GitHub-hosted Linux minutes, a Pro budget table, `ubuntu-latest` as the trace-hash determinism anchor — is obsolete against the ratified architecture (`AGENTS.md:363-367`: local macOS Act runner, `ubuntu-latest:host`, "the `ubuntu-latest` environment name is a fiction", GitHub Actions "billing-locked… dead signals"). The ADR's own §Out of scope names this failure ("switching runner classes invalidates the trace_hash equality check"). `AA-519`.
- **Build fidelity contradicts** on the load-bearing clause: its §Decision says the CI runner "**never** commits directly to `main`, **never** mutates `corpora/`, **never** ratifies proposals" — and `.github/workflows/ratify-proposal.yml`, which cites ADR-0155 in its own header and commit message, does all three. `AA-516`.
- **Continuity** unreconciled. **Fitness** two reports, no eval consuming them at HEAD. **Necessity** reducible — a local `core demo learning-arc --json` in the pre-push lane delivers the artifact without the runner-class premise.

### ADR-0156 — Atomic engine-state checkpoint writes
- **Build** full (`engine_state._atomic_write_text`: NamedTemporaryFile in target dir → flush → fsync → `os.replace`). **Liveness** live for all three `save_*` paths. **Design fidelity** pass. **Build fidelity** matches. **Continuity** clean; its three deferrals were each closed or explicitly re-scoped (W-023→0157, W-024→0158; parent-dir fsync still open by stated choice). **Fitness** `tests/test_adr_0156_atomic_checkpoint.py`, including replace-failure preservation. **Necessity** irreducible. **Cleanest ADR in the range.**

### ADR-0157 — Revision-mismatch warning on load
- **Build** full; **Liveness** live in `EngineStateStore.load_manifest`, evidenced by the warning at `chat/runtime.py:890-899`. **Design fidelity** pass ("reboot is recovery, not control flow" honored — warns, never raises). **Build fidelity** matches, incl. the `"unknown"` suppression rationale. **Continuity** clean. **Fitness** `tests/test_adr_0157_revision_mismatch_warning.py`. **Necessity** irreducible.

### ADR-0158 — `reboot_event` audit trail entry
- **Build** full: `serialize_reboot_event`/`format_reboot_event_jsonl` at `chat/telemetry.py:302,343`, exported `:516,520`; buffered at `chat/runtime.py:908`, flushed exactly once at `:1532-1534`.
- **Liveness** live. **Design fidelity** pass — metadata only, no surface text or coordinates. **Build fidelity** matches the two-step buffered emission and the "precedes any turn event" ordering. **Continuity** clean; closes the L10b sequence table honestly. **Fitness** `tests/test_adr_0158_reboot_event.py`. **Necessity** irreducible.

### ADR-0159 — Contemplation Quality Eval Lane
- **Build** full: `evals/contemplation_quality/{runner.py,contract.md}`; **all nine named metrics present** in `runner.py`. **Liveness** live and reachable from three surfaces (CLI, workbench API `/evals/…`, `workbench/readers.py:69` `SAFE_EVAL_LANES`).
- **Design fidelity** pass — the read-only MUST-NOT list is respected (the lane is the sole member of `SAFE_EVAL_LANES`). **Build fidelity partial drift:** the ADR's only operator-facing invocation is `core eval contemplation-quality` (hyphen); the registered id is `contemplation_quality`. `AA-520`. **Continuity** clean. **Fitness** `tests/test_contemplation_quality_lane.py`. **Necessity** irreducible.

---

## 2. Workbench, HITL queue, design system, trust boundary (0160, 0161, 0162, 0173)

### ADR-0160 — CORE Workbench v1
- **Status `proposed`**, while `docs/adr/INDEX-by-domain.md:100` cites it as governing `workbench/`. **Build** full and large: `workbench/` is **23 modules** (`api.py`, `server.py`, `readers.py`, `replay.py`, `journal.py`, evidence/practice/construction endpoints…), plus `workbench-ui/`.
- **Liveness** live: `core workbench api [--port|--host|--allow-nonlocal-bind]` is in the CLI epilog and the UI has its own CI job.
- **Design fidelity tension.** §114 "V1 is **read-only by default**" is no longer true of the surface: `workbench/readers.py:1380-1431` applies Lexical/Frame/Composition claims into `packs/data/…`, and the module docstring still reads `"""Read-only readers for the CORE Workbench W-026 API."""`. **Build fidelity** partial drift. `AA-521`.
- **Continuity unreconciled:** ADR-0173 §70 records 0160 as "**Amended**, narrowly"; ADR-0160 carries **zero** references to ADR-0173. **Fitness** heavy real use (evidence panels, journal, replay). **Necessity** irreducible.

### ADR-0161 — HITL Async Queue
- **Status `Proposed`**; `INDEX-by-domain.md:101` cites it as governing `teaching/proposals.py` + `core proposal-queue`.
- **Build partial.** Landed: the 256 pending cap and `CORE_HITL_PENDING_CAP` (`core/cognition/backpressure.py:20,38,48`), the typed `queue_full` report (`core/cli_teaching.py:465,588`), the two read-only projections (`core teaching hitl-queue list|show`), and `core/cli_proposal_queue.py` (status/list/show/review). Derived-view sources both exist (`teaching/proposals/proposals.jsonl`; `contemplation/runs/*.json`).
- **Not built:** Surface B's specified `transition` event — `ratifier_kind`, `actor`, `commit_sha`, `workflow_run_id` have **no producer** (`teaching/proposals.py` contains zero `ratifier_kind` support; `workflow_run_id` appears nowhere in the repo), and `action ∈ {accept,reject,withdraw}` was never parameterized (the workflow still exposes accept-only). `AA-522`.
- **Design fidelity violation on the safety leg:** §Surface-B precondition 4 and §466 require a fail-closed repo-owner allow-list on `github.actor`; the shipped workflow's only gate is `vars.CONTEMPLATION_ENABLED == 'true'`. `AA-516`.
- **Continuity** clean w.r.t. ADR-0173 (which correctly declines to make the workbench a fourth surface). **Fitness** `tests/test_hitl_queue_submission_invariants.py`. **Necessity** irreducible (queue identity = `proposal_id`, no new persistence — Axiom 5 done right).

### ADR-0162 — Workbench Design System v1
- **Status `Proposed`**; `INDEX-by-domain.md:102` cites §3d as build-time enforced. **Build** full: `workbench-ui/src/design/{tokens,components,doctrine}/`, `workbench-ui/enum-snapshot.json`, and the enforcement pair `src/design/components/badges/enumCoverage.test.ts` + `src/design/doctrine/schemaDrift.test.ts`.
- **Liveness live and gate-enforced** — `.github/workflows/workbench-ui.yml` runs `pnpm build` + `pnpm test` + a Playwright smoke job. This is one of the better-enforced §3d-style contracts in the corpus: engine enums bind to UI badges and the binding fails a build.
- **Design fidelity** pass (semantic tokens, 1:1 enum→badge). **Build fidelity** near-total; one named component (`EvalCenter`, §414/§587) does not exist. `AA-523`. **Continuity** clean. **Fitness** CI-enforced. **Necessity** irreducible.

### ADR-0173 — Workbench Ratification Trust Boundary
- **Status Accepted** (2026-05-29) — the one Accepted governor of this quartet, and it correctly amends 0160 and holds 0161's surface set.
- **Build** full on its own terms: `ratifier_kind="workbench"` at `workbench/readers.py:1385,1408,1431` and `workbench/api.py:106`; `127.0.0.1` default bind; three ratify-parity tests (`tests/test_workbench_ratify_{lexical,frame,composition}.py`) asserting byte-equivalence with the CLI path modulo `ratifier_kind`.
- **Liveness** live. **Design fidelity** pass; the "not a permission discriminant" clause (§388) is honored. **Build fidelity partial drift:** §380's enum `ratifier_kind ∈ {"cli","workflow_dispatch","workbench"}` is 2/3 real — `"workflow_dispatch"` has no producer, matching `AA-522`.
- **Continuity tension:** §71 characterizes ADR-0161 as "CI workflows cannot ratify," but 0161's Surface B *is* a CI workflow that ratifies and pushes to `main`. `AA-516`. **Fitness** parity tests are the right shape (identity, not equal-looking values). **Necessity** irreducible.

---

## 3. GSM8K corridor: spec, sequencing, evidence, decomposition (0163~1, 0163~2, 0166, 0167, 0172)

### ADR-0163~1 — F2 Confuser Corpus Spec
- **Status `Proposed (spec only — no code)`** — **false at HEAD.** `evals/gsm8k_math/confusers/v1/{cases.jsonl,runner.py}` exist, plus `tests/test_adr_0163_f2_confusers.py` (which ADR-0182 also cites as its own pin).
- **Build** full. **Liveness** live (the confuser lane is 0182's evidence). **Design fidelity** pass. **Build fidelity** matches except the ADR names `cases.json`; disk has `cases.jsonl`. **Continuity** unreconciled status. **Fitness** cited by 0182. **Necessity** irreducible.

### ADR-0163~2 — GSM8K Path to Mastery
- **Status `Proposed — Phases B–E prescription superseded by ADR-0164`**, and ADR-0207 §Supersedes independently confirms it. **Continuity: exemplary** — the supersession is scoped to the phases, dated, and named in both directions.
- **Build** partial-by-design; its surviving sub-phases (D.2/D.3/D.4) have pins (`tests/test_adr_0163_d{2,3,4}_*.py`). Superseded prescriptions left dangling artifacts: `generate/math_versor_arithmetic.py`, `evals/…/refusal_taxonomy/v1/taxonomy.json` and five other cited paths do not exist — correct for a retired prescription, but uncaught by any link check (`AA-58` class).
- **Design fidelity** pass. **Fitness** its refusal taxonomies are preserved as evidence per 0207. **Necessity** irreducible as a record.
- **Collision note:** both 0163 files are `Proposed` on unrelated subjects — the pair carries no cross-reference. `AA-524`.

### ADR-0166 — Measurement-Capability Sequencing Discipline
- **Status `Proposed`**, yet Accepted ADR-0170 names it "**Gating rule:**" in its header. **Build** N/A by design — a PR-review discipline, not code. **Liveness** convention-only; no enforcing pin exists and the ADR does not claim one.
- **Design fidelity** pass and genuinely Pillar-III shaped ("capability lands before the measurement that depends on it"). **Build fidelity** N/A. **Continuity** unreconciled status.
- **Fitness — weak positive evidence, stated as such:** both counter-examples the ADR was written against (`spatial_geometry_ood`, `historical_sequence_ood`) exist nowhere in the repo. That is consistent with the rule holding, not proof of it. `AA-525`. **Necessity** irreducible (nothing else in the corpus orders capability before measurement).

### ADR-0167 — Audit-as-Teaching-Evidence
- **Status `Proposed (scoping ADR; no code in this PR)`** — stale. The evidence floor it defines is live and enforced: `teaching/math_frame_ratification.py:17` ("evidence pointers MUST carry `source=\"math_audit\"` — never `\"corpus\"`") and `:201`, with `EvidenceLaundering` raised in `teaching/math_composition_ratification.py` and pinned at `tests/test_math_composition_ratification.py:319-321,730-758`.
- **Build** full (as the doctrine consumed by 0168/0169). **Liveness** live. **Design fidelity** pass — this is the Axiom-4 conjugate the A3 stack found missing elsewhere: the forward "audit produces evidence" operator has a "evidence may not be laundered as corpus" corrective. **Build fidelity** matches. **Continuity** unreconciled status. **Fitness** enforced by a raising test. **Necessity** irreducible.
- Document defect: two `## Decision` headings (`:36`, `:186` "Decision (pending operator ratification of this ADR)"). `AA-526`.

### ADR-0172 — Math Corpus Decomposition Mechanism
- **Status `Proposed (scoping ADR; no runtime change in this PR)`** — stale by six test files: `tests/test_adr_0172_w{0,0_1,1,2,3,4,5}_*.py` (reasoning trace, replay equivalence, shape proposal, decomposer, CLI lane, workbench E2E, inference proposal).
- **Build** near-full. **Liveness** live, including a workbench E2E path. **Design fidelity** pass. **Build fidelity partial drift:** three named artifacts absent — `ProposalVerdict`, `teaching/math_proposal_verdicts/index.json`, `tests/test_math_contemplation_decomposition.py` (the ADR's own cited test). `AA-523`. **Continuity** unreconciled status. **Fitness** `core eval math-contemplation` is in the CLI epilog. **Necessity** irreducible.

---

## 4. Claim ratification doctrines and the injector contract (0168, 0168.1, 0169, 0169.1, 0170)

### ADR-0168 — FrameClaim Ratification Doctrine
- **Status `Proposed (doctrine/scoping ADR; no runtime mutation in this PR)`. This is now false and safety-relevant.** `teaching/math_frame_ratification.py` exists as an explicit post-review **pack-mutation boundary** writing `packs/data/en_core_math_v1/frames/`, and its module docstring quotes ADR-0168 §"Decision" as its **hard rules** (`:11-20`: `SAFE_FRAME_CATEGORIES` allowlist, the case-0050 hazard pin, the `math_audit` evidence rule, the affirms/falsifies polarity split).
- **Build** full. **Liveness live and load-bearing** — reached from the workbench (`workbench/readers.py`, `_HANDLER_DISPATCH["frame_reclassification"] == "FrameClaim"`, pinned at `tests/test_math_frame_ratification.py:779`), and `tests/test_adr_0172_w2_decomposer.py:354` cites its allowlist.
- **Design fidelity** pass — the case-0050 hazard pin is a proper sabotage-resistant guard (ratify anything, case 0050 must still refuse). **Build fidelity** matches the doctrine. **Continuity** unreconciled — and the mismatch is between an unratified doctrine and a live mutation boundary. `AA-517`. **Fitness** two large dedicated suites, both **gate-reachable** (absent from `tests/full_only_baseline.txt`). **Necessity** irreducible.

### ADR-0168.1 — Math FrameClaim Proposal Adapter
- **Status `Proposed (design bridge; no runtime FrameClaim admission in this PR)`** — stale: `teaching/math_frame_proposal.py` exists and `teaching/math_frame_ratification.py:201` cites "ADR-0168.1 §'Evidence floor'" as the authority for its `math_audit` check.
- **Build** full. **Liveness** live. **Design fidelity** pass (proposal/admission separation preserved). **Build fidelity** matches. **Continuity** unreconciled. **Fitness** pinned via the ratification suite. **Necessity** irreducible. `AA-517`.

### ADR-0169 — CompositionClaim Ratification Doctrine
- **Status `Proposed (… no runtime mutation in this PR)`** — stale. `teaching/math_composition_ratification.py` + `tests/test_math_composition_ratification.py` (20 numbered obligations, ~780 lines) are live, and a separate hazard pin cites this ADR by section: `tests/test_consumption_case_0050_hazard_pin.py:3-6` — *"ADR-0169 §'Acceptance gates': ratifying any synthetic CompositionClaim…"*. **An unratified doctrine is the named authority for a CI pin.**
- **Build** full for the three admitted primitives. **Liveness** live. **Design fidelity** pass. **Build fidelity** matches — and the five kinds the corpus lacks (`comparative_composition`, `percentage_composition`, `unit_conversion_composition`, `time_composition`, `chained_composition`) are **explicitly deferred** by the ADR itself (§264-268), so their absence is *evidence of absence*, not a gap. **Continuity** unreconciled status. **Fitness** the strongest test-to-doctrine ratio in the range. **Necessity** irreducible. `AA-517`.

### ADR-0169.1 — Math CompositionClaim Proposal Adapter
- **Status `Proposed (design bridge; no runtime CompositionClaim admission in this PR)`** — stale: `teaching/math_composition_proposal.py` exists; its anti-laundering obligation is pinned (`tests/test_math_composition_ratification.py:730-758`, under a slightly different function name than the ADR cites). **Build** full. **Liveness** live. **Design fidelity/Build fidelity** pass/matches. **Continuity** unreconciled. **Fitness** pinned. **Necessity** irreducible. `AA-517`.

### ADR-0170 — Recognizer Injector Contract Widening
- **Status Accepted — and it is the range's positive exemplar.** Its header explicitly records its own repair: *"Status reconciled 2026-06-15 (mastery-v2 Step 2; was the stale 'Proposed / no runtime change in this PR', which never tracked W1/W2 landing)."* This is exactly the fix the other 24 mismatches need. `AA-515`.
- **Build** partial-as-declared: W1 (type widening) + W2 (`CandidateOperation(add)`) in `generate/recognizer_anchor_inject.py::inject_from_match` (`:86`), pinned by `tests/test_adr_0170_w{1,2}_*.py`. **Liveness** live on the serving path.
- **Design fidelity** pass; declares ADR-0166 as its gating rule (which is itself `Proposed`). **Build fidelity** matches.
- **Continuity — the range's cleanest structural defect:** W3–W5 and the `SentenceChoice` widening are deferred to **ADR-0171, which does not exist** (one of the census's 13 numbering gaps), and the named prerequisites `CandidateRate`/`apply_rate` exist nowhere in the repo. The successor mechanism (ADR-0186's seal) is empty. `AA-527`. **Fitness** wrong=0 at `train_sample 4/0/46`. **Necessity** irreducible.
- Citation rot: `docs/handoff/DCS-S1-FINDING.md` / `docs/handoff/WAVE-NEXT-REVISED.md` — both live at `docs/handoffs/…` (`AA-58` one-character class). `AA-523`.

---

## 5. Comprehension/composition increments (0176, 0177, 0178~1, 0178~2, 0179, 0184~2)

### ADR-0176 — Multi-step Composition Question Targeting
- **Status `Proposed`**; four test files shipped (`tests/test_adr_0176_{comparatives_pack,ms1_question_target,ms2_chain,ms3_search}.py`). **Build** full for MS-1/2/3. **Liveness** live.
- **Continuity — a specific gap:** ADR-0176 is the **only** member of the 0164→0179 comprehension arc that ADR-0207 does not mention at all (0 occurrences), so it was left outside the ratification that moved 0164/0165/0174/0178/0179 out of limbo. `AA-528`.
- **Design fidelity** pass (`test_adr_0176_ms1_question_target.py:4` describes its own patterns as "ADR-0165-safe" — the propagation `AA-490` credits). **Build fidelity** matches. **Fitness** pinned. **Necessity** irreducible.

### ADR-0177 — Cue-Precision Learning
- **Status `Proposed`**; `generate/cue_precision/trainer.py` + `evals/gsm8k_math/practice/v1/cue_precision_report.py` + `tests/test_adr_0177_cp{1_ledger,2a_training}.py` shipped. **Build** full for CP-1/CP-2a. **Liveness** live. **Design fidelity** pass. **Build fidelity** matches; the ADR writes `N_min` where the pinned global is `N_MIN` (`core/reliability_gate/floor.py:24`) — cosmetic but a Pillar-II nick. **Continuity** unreconciled status. **Fitness** pinned. **Necessity** possible consolidation with ADR-0199's floor (both reason about minimum-evidence thresholds).

### ADR-0178~1 — GB3b Referent Accumulation Scope
- **Status `Proposed (scope only — no code)`** — false: `tests/test_adr_0178_gb3b1_accumulation.py` exists. **Build** partial (GB3b.1). **Liveness** live. **Design fidelity** pass. **Build fidelity** matches. **Continuity** unreconciled status; also collides with 0178~2 with no cross-reference (`AA-524`). **Fitness** pinned. **Necessity** irreducible.
- Cited `comprehension/lifecycle.py` resolves to `generate/comprehension/lifecycle.py` — relative-path citation, not a missing file.

### ADR-0178~2 — Compositional Structure
- **Status Accepted (ratified by ADR-0207, 2026-06-03)** — correct and independently confirmed in 0207 §Consolidates. **Build** full: `tests/test_adr_0178_gb{1_clauses,2_compose,3_referent_guard}.py`. **Liveness** live. **Design fidelity** pass. **Build fidelity** matches. **Continuity clean** — a properly ratified member. **Fitness** pinned; named by 0207 §153 as "the actual wall." **Necessity** irreducible.

### ADR-0179 — Extraction Richness
- **Status Accepted (ratified by ADR-0207)**; **Build** full (`generate/derivation/extract.py`, `tests/test_adr_0179_{extract,ex2_decimal_grounding}.py`). **Liveness** live. **Design fidelity** pass; `test_adr_0179_extract.py:106` self-describes as "ADR-0165-safe."
- **Continuity — unreconciled and flagged by its own ratifier.** ADR-0207 §Open items states verbatim: *"**ADR-0179 §Context drift.** Its 'thin extractor' table predates the landed…"*. ADR-0179 carries no amendment note. The Accepted ADR that ratified it named the drift and the drift was never annotated. `AA-529`. **Fitness** pinned. **Necessity** irreducible.

### ADR-0184~2 — Scoped Semantic State Transitions
- **Status `Proposed`** with the explicit line **"Supersedes: no runtime path yet; this is a scope-setting ADR for the next implementation sequence."** — flatly false. `generate/derivation/state/` is **8 modules** (`bind`, `change`, `ledger`, `model`, `provenance`, `replay`, `source`, `__init__`) with four pins (`tests/test_adr_0184_s{1,2,4,4b}_*.py`, incl. an S4b replay-equivalence gate).
- **Build** partial: S1/S2/S4/S4b shipped; S3 and S5–S9 not (the seven modules the ADR names for them — `compare.py`, `dag.py`, `rate.py`, `target.py`, `time.py`, `transfer.py`, `world.py` — are correctly absent). **Liveness** live. **Design fidelity** pass (S1 declared behavior-equivalent and its test pins non-vacuity). **Build fidelity** matches the shipped rungs. **Continuity** the range's second-worst status mismatch. `AA-530`. **Fitness** pinned. **Necessity** irreducible.

---

## 6. English math-grammar increments (0182, 0184~1, 0185, 0186, 0189, 0189a, 0191–0195)

### ADR-0182 — Cross-Composer Disagreement Pooling
- **Status Accepted / Implemented (PRs #476, #480, #481)** — honest. **Build** full (`generate/derivation/pool.py`, `tests/test_adr_0182_pool.py`). **Liveness** live. **Design fidelity** pass — pooling + commit-ineligibility is an Axiom-4 shape (a forward reading gets a disagreement conjugate). **Build fidelity** matches. **Continuity** clean. **Fitness** pinned, and cross-cited by 0185's supersession banner. **Necessity** irreducible.

### ADR-0184~1 — Distinct-Unit Product Rule
- **Status Accepted / Implemented**, with the status line itself recording that implementation *refined* the mechanism — good practice. **Build** full (`tests/test_adr_0184_distinct_unit_product.py`). **Liveness** live. **Design fidelity** pass (dimensional impossibility used to *eliminate*, `13 → 8`). **Build fidelity** matches, refinement disclosed. **Continuity** clean. **Fitness** pinned. **Necessity** irreducible.

### ADR-0185 — Division Reading
- **Status Superseded by ADR-0186 (premise refuted; not implemented)** — **positive exemplar.** The banner is dated, states the refuted premise, gives the disjointness evidence (the derivation reader vs. `generate/math_candidate_graph`), names the correct destination, and says explicitly "retained as a record only." Same class as `AA-487`. `AA-531`.
- **Build** ghost by design. **Liveness** dead by design. **Design fidelity** pass. **Build fidelity** N/A. **Continuity** exemplary — with one wrinkle: it is retired **by a `Proposed` ADR whose seal registry is empty** (`AA-532`). **Fitness** the topology audit it triggered is the value. **Necessity** irreducible as a record.

### ADR-0186 — Sealed Candidate-Graph Injector Lane
- **Status `Proposed (scoping + seal-mechanism ADR; first injector ships behind the seal)`.** The seal mechanism shipped; **the claim in the status line did not.**
- **Build** mechanism full, lane empty: `inject_from_match(..., sealed: bool = False)` at `generate/recognizer_anchor_inject.py:86-122` consults `_SEALED_INJECTORS`, which is **`{}`** at `:905`. The ADR's named runner `evals/gsm8k_math/train_sample/v1/run_sealed_injectors.py` and its metric `report_sealed.json` **do not exist**.
- **Liveness** scaffolded. Sabotage test: with an empty registry the `sealed=True` path is byte-identical to the frozen path — the only thing that notices the mechanism's removal is its own pin (`tests/test_adr_0186_sealed_injector_lane.py::test_sealed_flag_is_noop_when_registry_empty`).
- **Design fidelity** pass — one dispatch with a boolean seal is genuinely the right shape (it refuses the two-reader duplication ADR-0170 §178 warns about). **Build fidelity contradicts** the "first injector ships" claim. **Continuity** it retires 0185 and is meant to resume 0170 W2–W5; neither the resumption nor ADR-0171 exists. `AA-532`, `AA-527`. **Fitness** the leak/dead-seal pin is well-designed but tests an empty set; the pin is post-merge-only. **Necessity** irreducible *if* the lane is populated; pure decoration if it is not.

### ADR-0189 — Comparative Verb Unit Widening
- **Status `Proposed (implemented in this PR)`** — self-declared contradiction. **Build** full (the widening shipped in #488). **Liveness** live on the serving reader.
- **No pin of its own.** `rg 'ADR-0189\b' tests/` returns one hit, inside `tests/test_adr_0189a_day_enum_activity.py:10`, describing it as "already shipped." No `tests/test_adr_0189_*.py` exists.
- **Design fidelity tension / Build fidelity contradicts:** ADR-0191 §1 documents that #488 (ADR-0189/0189a) **introduced two real-corpus confabulations** (idx 693, 7369 — "they refused correctly before that PR and confabulated after"), i.e. an unpinned, unratified widening breached the project's cardinal `wrong=0` invariant on the full 7,473-question split. **Continuity unreconciled** — 0189 carries no note of it. `AA-533`. **Fitness** the regression is the only measured outcome recorded. **Necessity** likely irreducible once pinned.

### ADR-0189a — Day-Enum Activity-First Flip
- **Status Accepted (implemented)**. **Build** full; **Liveness** live; pinned by `tests/test_adr_0189a_day_enum_activity.py`. **Design fidelity** pass. **Build fidelity** matches. **Continuity unreconciled** — co-author of the same two regressions, no note. `AA-533`. **Fitness** pinned. **Necessity** irreducible.

### ADR-0191 — Candidate-Graph Completeness Guard
- **Status `Proposed (implemented in this PR)`** for what the ADR itself calls a "**serving-path firewall fix**." The highest-consequence status mismatch in the range after 0199.
- **Build** full: the completeness leg lands in the candidate-graph reader's admissibility gate, mirroring `verify.py`'s `grounding ∧ cue ∧ unit ∧ completeness ∧ uniqueness`. **Liveness** live on the canonical serving reader (`generate.math_candidate_graph.parse_and_solve`).
- **Design fidelity — the best-argued ADR in the range.** It identifies one structural hole rather than five anecdotes; the guard is **refusal-only** by construction ("it can never turn a refusal into an answer, so it cannot create a wrong answer"), which is the correct Axiom-4/`wrong=0` posture. **Build fidelity** matches; `tests/test_candidate_graph_completeness_guard.py` pins refusal on the exact corpus strings.
- **Continuity** unreconciled status; also the record of 0189/0189a's regressions (`AA-533`). **Fitness** real-corpus `wrong 5 → 0`, `train_sample` byte-identical `4/46/0` — the strongest fitness evidence in the range. **Necessity** irreducible; §"the derivation reader already refuses this" makes it a consolidation *toward* an existing primitive rather than a new mechanism (the physics-efficient direction).
- Caveat worth carrying: the pin is a five-string allowlist, not a corpus sweep; case 605 has since been relaxed (admitted via R1 reconstruction). The 47-case blind spot the ADR exposed is narrowed, not closed. Its pin is in `tests/full_only_baseline.txt` (post-merge only) — `AA-534`.

### ADR-0192 — Discrete-Count Open Noun Class
- **Status `Proposed (implemented in this PR)`**. **Build** full; **Liveness** live; `tests/test_discrete_count_open_noun_class.py` pins both directions (`test_open_noun_now_extracts`, `test_dangerous_shapes_still_refuse`). **Design fidelity** pass — widening paired with a refusal pin is the correct Dual-Correction shape. **Build fidelity** matches; the ADR cites a pin named `test_unobserved_counted_noun_refused` (§92) that does not exist under that name. `AA-523`. **Continuity** unreconciled status. **Fitness** pinned (post-merge lane). **Necessity** irreducible.

### ADR-0193 — Aggregate Existential Question Frame
- **Status `Proposed (implemented in this PR)`**. **Build** full; **Liveness** live; `tests/test_aggregate_total_question_forms.py`. **Design fidelity** pass. **Build fidelity** matches. **Continuity** unreconciled status. **Fitness** pinned (post-merge lane). **Necessity** irreducible.

### ADR-0194 — Labeled Container Subject
- **Status `Proposed (implemented in this PR)`**. **Build** full; **Liveness** live; `tests/test_labeled_container_subject.py`. **Design fidelity** pass. **Build fidelity** matches. **Continuity** unreconciled status. **Fitness** pinned (post-merge lane). **Necessity** irreducible.

### ADR-0195 — Product Promotion Bridge
- **Status Accepted / Implemented** — honest, and the shortest ADR in the range (39 lines) for a correspondingly small mechanism. **Build** full (`generate/derivation/product_bridge.py`, `tests/test_adr_0195_product_bridge.py`). **Liveness** live. **Design fidelity** pass. **Build fidelity** matches. **Continuity** clean. **Fitness** pinned. **Necessity** irreducible; a good example of proportionate documentation.

---

## 7. Modality forks, arena contract, expert-claim reconciliation (0183, 0198, 0199, 0200)

### ADR-0183 — Lawful Audio-to-Lexeme Path
- **Status `Proposed (stub — placeholder to record the fork; not yet a full design)`** — **honest, and the only status in the range that matches reality exactly.** **Build** ghost by design; no named artifact, and `rg 'lawful_audio|audio_lexeme'` returns nothing. **Liveness** dead by design. **Design fidelity** pass. **Build fidelity** N/A. **Continuity** clean; its two cited docs (`docs/audio_pipeline_overview.md`, `docs/plans/audio-compiler-eval-plan.md`) both exist. **Fitness** none claimed. **Necessity — consolidation candidate:** 117 lines to record a fork whose content is one paragraph of ADR-0181's teacher-boundary section. `AA-535` (this is the verified form of the retracted `AA-363`).

### ADR-0198 — Motor Efferent Decoder Spike
- **Status Accepted (design spike)** with an explicit split — "Gap A protocol change + a baseline efferent gate have landed; the §3 verdict-lowering and the motor compiler/decoder remain deferred. See **Implementation Status** below." **Positive exemplar** of partial-build honesty. `AA-536`.
- **Build** partial-as-declared: `sensorium/efferent.py` + `tests/test_efferent_gate.py`. **Liveness** live, fail-closed. **Design fidelity** pass. **Build fidelity** matches. **Continuity clean** — the deferral names ADR-0216, which **exists** (`ADR-0216-motor-verdict-lowering.md`), unlike ADR-0170's phantom ADR-0171. **Fitness** pinned. **Necessity** irreducible.

### ADR-0199 — Cross-Domain Learning Arena Contract
- **Status `Proposed`** — and this is the range's headline 🔴. **Build** full and central: `core/learning_arena/` = `protocols.py`, `engine.py`, `report.py`, `__init__.py`, with `tests/test_adr_0199_learning_arena_engine.py` proving L-1/L-3/L-4.
- **Liveness live and load-bearing across four eval lanes**: `evals/gsm8k_math/practice/v1/runner.py:30-33`, `evals/determination_estimation/{runner.py:14, gold.py:21}`, `evals/deduction_serve/practice/{runner.py:24, gold.py:32}`, `evals/curriculum_serve/practice/generator.py:52`. **Accepted ADR-0238 §28 names `core.learning_arena.protocols.GoldTether` as the canonical namespace it forbids shadowing.** An Accepted ADR's non-shadowing rule points at a `Proposed` ADR's module. `AA-537`.
- **Design fidelity** pass and well-argued: one pinned floor for all subjects (`WILSON_Z = 2.576`, `N_MIN = 10` verified at `core/reliability_gate/floor.py:22,24`; **no competing definition exists anywhere in the repo** — L-1 holds by sabotage-check), θ ceilings as the only per-domain dial.
- **Build fidelity** matches for PR-1/PR-2. **Continuity unreconciled status**, and PR-3/4/5 (`systems_software`, `physics`, `hebrew_greek_textual_reasoning`) never shipped: the three lanes that *do* consume `run_practice` carry `domain_id`s (`determination_estimation`, `curriculum_serve`, `deduction_serve`) that are **not members of `core/capability/domains.py`'s five-subject registry**. The fold generalized; the subjects it was written for did not. `AA-538`.
- **Fitness** the shared floor licenses the deduction-serve bands (independently recomputed in `Batch6-TierA-redo.md`). **Necessity** irreducible.
- **Pillar II positive:** the two `GoldTether` concepts are disambiguated in three independent places — ADR-0238 §25-28's table + "Never shadow…", `core/physics/goldtether.py:16` ("Distinct from Arena GoldTether (ADR-0199 / core.learning_arena.protocols)"), and 0199's own protocol. **The two do not silently overlap.** `AA-539`.

### ADR-0200 — Expert-Claim Reconciliation
- **Status `Proposed (review-gated — every claim/test change below awaits operator ratification)`. Every one of the six prescribed changes has landed.** Verified individually: `evals/math_expert_claims/v1/expert_claims_math_v1_signed.json` regenerated (`promote_admitted: false` `:80`, `reviewer_signature_matches: false` `:94`, live digest `02f6d3c8…` vs signed `4c46f530…`); `ADR-0120-math-expert-ledger-flip.md` carries the dated *"Reconciliation note (ADR-0200, 2026-06-02)"*; `docs/reviewers.yaml:56-66` carries the `QUARANTINED (ADR-0200…)` block; `tests/test_mathlogic_expert_ledger_flip.py:128-150` now asserts the fail-closed revert (`status == "audit-passed"`, expert_reason explains the digest mismatch).
- **Build** full. **Liveness** live — the ledger reports `audit-passed` and the composer refuses. **Design fidelity** pass and doctrinally strong: it records a revert as designed behavior rather than a regression, and applies refuse-rather-than-guess to CORE's own status. **Build fidelity** matches.
- **Continuity — the reconciliation ADR is the last unreconciled artifact in its own reconciliation.** `AA-540`. Residue: `tests/test_mathlogic_expert_ledger_flip.py:9`'s docstring still reads "mathematics_logic row reports `status: expert` + `predicates.expert: True`" inside the file 0200 flipped.
- **Fitness** three red overclaim tests converted to green mechanism-proving tests. **Necessity** irreducible. Its §3 disclosed coupling smell (non-gating GSM8K disclosure folded into the gating digest) remains deferred and correctly characterized as failing safe.

---

## Findings rollup (final corpus IDs `AA-515`–`AA-540`)

### 🔴 Block (for ruling) — 3

- **`AA-516` 🔴** — **A CI workflow ratifies proposals and pushes the active teaching corpus to `main`, contradicting the trust boundaries of both Accepted ADRs it cites.** `.github/workflows/ratify-proposal.yml` runs `core teaching review --accept`, then `git add teaching/cognition_chains/cognition_chains_v1.jsonl teaching/proposals/proposals.jsonl` → `git push origin main`, under a commit message reading "ADR-0057 / ADR-0155". ADR-0155 §Decision: the CI runner "**never** commits directly to `main`, **never** mutates `corpora/`, **never** ratifies proposals." ADR-0151 §Trust Boundary: "never writes the active teaching corpus." Two aggravators: (a) ADR-0161 §Surface-B precondition 4 / §466 require a fail-closed repo-owner allow-list on `github.actor` — **unimplemented**; the sole gate is `vars.CONTEMPLATION_ENABLED == 'true'`; (b) `${{ inputs.operator_note }}` is interpolated **unquoted** into the accept step's shell (`:88-94`) in a job holding `contents: write`. Flagged for ruling, not repaired. Mirror into the assessment `G`-register — this is a system-level trust-boundary gap, not document fidelity.
- **`AA-517` 🔴** — **The live pack-mutation boundary for math frame/composition evidence is governed only by unratified doctrine.** ADR-0168, 0168.1, 0169, 0169.1 all read `Proposed … no runtime mutation/admission in this PR`, yet `teaching/math_frame_ratification.py` and `teaching/math_composition_ratification.py` write `packs/data/en_core_math_v1/…`, quote ADR-0168 §Decision as their hard rules (`math_frame_ratification.py:11-20`), cite ADR-0168.1 §"Evidence floor" as the authority for their evidence check (`:201`), are dispatched from the workbench (`workbench/readers.py:1385-1431`, `workbench/api.py:106`), and are the named authority for a CI hazard pin (`tests/test_consumption_case_0050_hazard_pin.py:3-6` — "ADR-0169 §'Acceptance gates'"). The mechanism is well built and well pinned; the governance is absent. One ratification closes all four.
- **`AA-537` 🔴** — **The cross-domain reliability substrate is `Proposed` while an Accepted ADR treats it as canonical.** ADR-0199 is `Proposed`; `core/learning_arena/` (4 modules) is the shared attempt→score→ledger fold for four eval lanes, and Accepted ADR-0238 §28 instructs "Never shadow `core.learning_arena.protocols.GoldTether`." Chains directly onto `AA-491`: **0175 (`Proposed`) → 0199 (`Proposed`) → 0238 / 0256 (Accepted)** — the licensing regime for all 25 deduction bands has two unratified links. Rule 0175 and 0199 together.

### 🟡 Repair — 9

- **`AA-519` 🟡** — ADR-0155's premise is obsolete and the mechanism is dead. It anchors determinism on GitHub-hosted `ubuntu-latest` and budgets GitHub Pro Linux minutes; the ratified architecture (`AGENTS.md:363-367`) is a local macOS Act runner behind the `ubuntu-latest:host` label ("the `ubuntu-latest` environment name is a fiction") with GitHub Actions as "billing-locked… dead signals." Its own §Out of scope names this exact break. `contemplation/runs/` holds two files, both 2026-05-26.
- **`AA-532` 🟡** — ADR-0186's seal is empty: `_SEALED_INJECTORS: Mapping[…] = {}` (`generate/recognizer_anchor_inject.py:905`), so its status-line claim "first injector ships behind the seal" is false; the named runner `evals/gsm8k_math/train_sample/v1/run_sealed_injectors.py` and metric `report_sealed.json` do not exist. ADR-0185 is retired *by* this empty mechanism.
- **`AA-527` 🟡** — Accepted ADR-0170 defers W3–W5 and the `SentenceChoice` widening to **ADR-0171, which does not exist** (census §Summary numbering gap); its named prerequisites `CandidateRate`/`apply_rate` exist nowhere. An Accepted deferral pointing at a number that was never written, with the successor seal (0186) empty — the whole injector-widening lane is stalled and no record says so.
- **`AA-521` 🟡** — `workbench/readers.py`'s module docstring is `"""Read-only readers for the CORE Workbench W-026 API."""` while the same module applies Lexical/Frame/Composition claims into `packs/data/…` (`:1380-1431`). ADR-0160 §114 ("V1 is read-only by default") carries **zero** references to the ADR-0173 amendment that narrowed it. Pillar II + AGENTS.md #5.
- **`AA-522` 🟡** — ADR-0161 Surface B is accept-only and untyped: the specified `transition` event with `ratifier_kind` / `actor` / `commit_sha` / `workflow_run_id` has no producer (`teaching/proposals.py` has zero `ratifier_kind` support; `workflow_run_id` appears nowhere), and `action ∈ {accept,reject,withdraw}` was never parameterized. ADR-0173 §380's enum is 2/3 real — and the missing third is the surface that can push to `main` (`AA-516`), so the highest-privilege ratification path is the one leaving no audit discriminant.
- **`AA-530` 🟡** — ADR-0184~2 states "**Supersedes:** no runtime path yet; this is a scope-setting ADR" while S1/S2/S4/S4b shipped: `generate/derivation/state/` (8 modules) + `tests/test_adr_0184_s{1,2,4,4b}_*.py`, including a replay-equivalence gate.
- **`AA-529` 🟡** — ADR-0179 carries no amendment note although Accepted ADR-0207 §Open items records verbatim "**ADR-0179 §Context drift.** Its 'thin extractor' table predates the landed…". The ratifying ADR diagnosed the drift; the ratified ADR was never annotated. Same class as `AA-53`.
- **`AA-533` 🟡** — ADR-0189/0189a introduced two real-corpus confabulations (idx 693, 7369) — documented in ADR-0191 §1 as "regressions introduced by #488… they refused correctly before that PR and confabulated after" — i.e. an unratified, **unpinned** widening breached `wrong=0` on the full 7,473-question split. Neither ADR carries a note, and ADR-0189 has no test pin anywhere in `tests/`. Live defect is closed by 0191; the record is not.
- **`AA-540` 🟡** — ADR-0200 is the reconciliation ADR and is the last unreconciled artifact of its own reconciliation: all six prescribed repairs landed (signed JSON `promote_admitted:false`/`reviewer_signature_matches:false`; ADR-0120's dated note; `docs/reviewers.yaml:56-66` quarantine; `tests/test_mathlogic_expert_ledger_flip.py:128-150` flipped to fail-closed-revert assertions) while its status still reads "awaits operator ratification." Residue: `:9`'s docstring still says "row reports `status: expert`" inside the file 0200 flipped.

### 🔵 Consolidate — 3

- **`AA-535` 🔵** — ADR-0183 is 117 lines recording a fork with no code and no named artifact; its substance is one paragraph of ADR-0181's teacher-boundary section. Fold into 0181 as a §Deferred item. (Verified form of the retracted `AA-363`.)
- **`AA-538` 🔵** — ADR-0199's five-subject generalization is undelivered: PR-3/4/5 (`systems_software`, `physics`, `hebrew_greek_textual_reasoning`) never shipped, and the three lanes that *do* consume `run_practice` carry `domain_id`s (`determination_estimation`, `curriculum_serve`, `deduction_serve`) absent from `core/capability/domains.py`. Either the registry admits arena-only domains or the arenas map onto base subjects; today neither is true and no record notices.
- **`AA-524` 🔵** — The three true collisions in this range (0163~1/~2, 0178~1/~2, 0184~1/~2) each pair a scope-only spec with an implemented increment on a *related* surface, so a reader following one number reaches the wrong document. Per ADR-0225 do not renumber; add reciprocal "not to be confused with" lines. Feeds `21-drift-report.md`.

### 🟢 Monitor — 11

- **`AA-515` 🟢** — **Positive exemplar, and the fix template for this whole range.** ADR-0170's header reconciles its own stale status: *"Status reconciled 2026-06-15 (mastery-v2 Step 2; was the stale 'Proposed / no runtime change in this PR', which never tracked W1/W2 landing)."* Cite this against the 25 mismatches rather than inventing a new convention.
- **`AA-539` 🟢** — **Positive exemplar (Pillar II).** The two `GoldTether` concepts are disambiguated in three independent places: ADR-0238 §25-28's comparison table + "Never shadow `core.learning_arena.protocols.GoldTether`"; `core/physics/goldtether.py:16` "Distinct from Arena GoldTether (ADR-0199 / core.learning_arena.protocols)"; and 0199's own protocol. **The two do not silently overlap.** Direct counterexample to `AA-30`'s name-collision class.
- **`AA-531` 🟢** — **Positive exemplar.** ADR-0185's supersession banner is dated, states the refuted premise, cites the disjointness evidence, names the correct destination, and says "retained as a record only; it is NOT implemented." Same class as `AA-487`.
- **`AA-536` 🟢** — **Positive exemplar.** ADR-0198 carries an explicit "Implementation Status" split in its status line and defers to ADR-0216, which **exists** — the honest contrast to `AA-527`'s phantom ADR-0171.
- **`AA-520` 🟢** — ADR-0159's only operator-facing invocation is wrong: `core eval contemplation-quality` (hyphen) vs the registered lane id `contemplation_quality` (`workbench/readers.py:69`, `tests/test_contemplation_quality_lane.py:40`). All nine named metrics do exist.
- **`AA-518` 🟢** — ADR-0154's disclosed hazard is now the shipped default: it asked for "a future bound (LRU or cap)… before long-running operators enable the producer with the consumer off," which is exactly today's configuration (producer unconditional at `core/cognition/pipeline.py:257-262`; `recognition_grounded_graph=False` at `core/config.py:251`; no cap on `_pending_recognizer_examples`). Unbounded per-session growth in a long-lived runtime.
- **`AA-534` 🟢** — Gate reachability of this range's most consequential pins: ADR-0191's serving-path `wrong=0` firewall pin (`tests/test_candidate_graph_completeness_guard.py`), ADR-0186's seal-leak pin, and ADR-0199's L-1 floor-reuse pin are all in `tests/full_only_baseline.txt` (post-merge only). Registered under the ratified G-7 ratchet, so **not a new gap** — but these three are the range's strongest promotion candidates. (The FrameClaim/CompositionClaim suites are gate-reachable; credit where due.)
- **`AA-523` 🟢** — Citation/naming rot, one line: ADR-0162 names a nonexistent `EvalCenter`; ADR-0192 §92 cites a pin `test_unobserved_counted_noun_refused` whose real equivalent is `test_dangerous_shapes_still_refuse`; ADR-0172 cites `ProposalVerdict`, `teaching/math_proposal_verdicts/index.json` and `tests/test_math_contemplation_decomposition.py` — none exist; ADR-0163~1 cites `cases.json` for on-disk `cases.jsonl`; ADR-0177 writes `N_min` for the pinned `N_MIN`; ADR-0170 cites `docs/handoff/…` for files at `docs/handoffs/…` (the `AA-58`/`AA-85` one-character class, still uncaught).
- **`AA-525` 🟢** — ADR-0166 is a `Proposed` review-discipline rule that Accepted ADR-0170 names as its "**Gating rule:**". No enforcing pin exists (by design — it is a PR-review convention). Weak positive evidence it held: both counter-examples it was written against (`spatial_geometry_ood`, `historical_sequence_ood`) exist nowhere. Stated as weak because absence of a lane is not proof of the rule's causation.
- **`AA-528` 🟢** — ADR-0176 is the only member of the 0164→0179 comprehension arc that ADR-0207 does not mention at all (0 occurrences), so it stayed `Proposed` outside the ratification that moved its five siblings out of limbo — while MS-1/2/3 shipped with four test files. Include it in the reconciliation sweep.
- **`AA-526` 🟢** — ADR-0167 carries two `## Decision` headings (`:36`; `:186` "Decision (pending operator ratification of this ADR)"), so a reader diffing claimed-vs-landed hits two decisions. Same shape as `AA-96`.

---

## Severity tally

| | 🔴 Block | 🟡 Repair | 🔵 Consolidate | 🟢 Monitor | **Total** |
|---|---|---|---|---|---|
| **Batch 4 remainder (44 ADRs)** | **3** | **9** | **3** | **11** | **26** |

Per-ADR rate: 0.59 findings/ADR — below Batches 1–2's ~3/ADR, which is the expected effect of the amended Rigor tier (§00 §Rigor tier, 2026-07-29: ~5-10 tool calls/ADR, one-line findings, no test execution) plus real consolidation: **five of the range's 44 files are governed by a single 🔴 (`AA-517`) and four more by another (`AA-537`/`AA-516`)**, where a per-stack pass would have issued one finding each.

**Mirror into the assessment `G`-register:** `AA-516` (CI trust boundary — system-level, not document fidelity) and `AA-517` (unratified authority over a live pack-mutation boundary). **For `21-drift-report.md`:** `AA-521`, `AA-530`, `AA-529`, `AA-540`, `AA-524`, `AA-520`, `AA-523`, `AA-528`, `AA-526`. **For `22-consolidation-report.md`:** `AA-535`, `AA-538`, `AA-524`.

## Range-level pattern (feeds the post-Batch-6 synthesis)

The sibling dossier proposed a single reconciliation sweep for eight `Proposed`-as-authority files. **This range raises the count by 25** and changes the character of the recommendation:

**25 of 44 files carry a status line contradicted by what is built.** They are not a uniform class:

1. **Self-declared contradictions (5)** — 0189, 0191, 0192, 0193, 0194 literally read `Proposed (implemented in this PR)`. Zero investigation needed; a status normalization pass closes them.
2. **"No runtime change in this PR" that aged out (7)** — 0163~1, 0167, 0168, 0168.1, 0169, 0169.1, 0172, plus 0178~1's "scope only — no code". Each was *true when written* and never revisited. This is the class ADR-0170 already fixed for itself (`AA-515`).
3. **Silent Proposed→live promotions (6)** — 0160, 0161, 0162, 0176, 0177, 0199, all cited as governing live surfaces (three of them by `INDEX-by-domain.md` itself).
4. **Flatly false denials (2)** — 0184~2 ("no runtime path yet" against 8 modules + 4 pins) and 0186 ("first injector ships behind the seal" against `_SEALED_INJECTORS = {}`). These need a *decision*, not a status edit.
5. **`scoping`/review-gated ADRs whose work shipped (3)** — 0155, 0200, and 0166's gating-rule promotion.

**The mechanical part is cheaper than eight separate rulings; the substantive part is smaller than it looks.** Classes 1–3 (18 files) are a single normalization pass with `AA-515` as the precedent template. Only class 4 (2 files) plus the three 🔴s require judgment. The corpus is not badly built here — build fidelity is high, pins are real, and four ADRs in this range (0170, 0185, 0198, 0238-via-0199) are exemplars worth citing corpus-wide. What is missing is a step that closes a status line when the work lands, and its absence has now put an unratified doctrine in charge of a pack-mutation boundary and a CI workflow in charge of the active teaching corpus.
