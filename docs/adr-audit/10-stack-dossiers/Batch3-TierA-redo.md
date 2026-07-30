# Batch 3 — Tier A Redo Dossier (ADR-0101–0150 Tier A stacks)

**Verified against:** `cbfc8ccb` | **Date:** 2026-07-29 | **Rigor:** 2026-07-29 amended tier (no test/CLI execution; targeted reads/greps; terse 7-axis cards).

**Replaces:** `Batch3-TierA-consolidated.md` (RETRACTED — its findings `AA-331`–`AA-344` are void). Stack groupings A3.1–A3.7 retained from that file as scaffolding; every verdict re-derived from code at HEAD. Prior-evidence check done up front per charter: `20-finding-register.md` (AA-75, AA-220, AA-231–250, AA-262), `21-drift-report.md` §1 (FA-1 cascade), `30-gap-register.md` (G-2, G-21, G-24, G-25).

**Redo integrity note:** the retracted dossier cited at least three nonexistent artifacts — `core/evals/holdout_runner.py` (real path: `evals/holdout_runner.py`), `tests/test_adr_0106_expert_demo_contract.py` (real: `tests/test_expert_demo_contract.py`), `tests/test_adr_0107_deferral.py` (no equivalent exists) — corroborating the retraction's verify-against-code failure diagnosis.

**Working-tree caveat:** `evals/obligation_6_depth_curve/B3_bounded_grammar.json` and `evals/obligation_8_adversarial/obligation_8_adversarial_v1.json` carry uncommitted local modifications; this audit reads HEAD only.

---

## Stack A3.1 — Hebrew-Greek Textual Reasoning & Fluency Attachment (ADR-0102, ADR-0103)

**Falsifiable stack claim:** the four HE/GRC packs constitute a `reasoning-capable` domain because the 9 ADR-0091 predicates pass. On-disk evidence supports the predicate half (test-pinned) and **refutes the substance half**: FA-1 ruled the cross-language alignment ground defective (AUC 0.557, NO-GO) and G-25 records zero curriculum bands for this exact domain. Prior finding **AA-75 (🔴) is CONFIRMED and still live at HEAD** — the retracted dossier's downgrade to 🟡 (`AA-332`) is refuted; see AA-439.

### ADR-0102 — Hebrew-Greek reasoning-capable ratification
- **Build:** full — all four packs exist (`packs/data/{he_core_cognition_v1,he_logos_micro_v1,grc_logos_cognition_v1,grc_logos_micro_v1}`); manifest contract fields pinned by `tests/test_adr_0100_0102_sibling_ratifications.py`.
- **Liveness:** live — ledger row computed on every `ledger_report()` (`core/capability/reporting.py:383`); test asserts status ∈ (`reasoning-capable`, `audit-passed`) and predicate true (`tests/test_adr_0100_0102_sibling_ratifications.py:119-121`).
- **Design fidelity:** violation of Axiom 1/Pillar II by inheritance — the license's semantic substance rests on the alignment ground FA-1 retired; the ADR carries no annotation.
- **Build fidelity:** matches on the letter (manifest fields, chains, lanes as specified); the licensing mechanism (`reporting.py:428-434`) consults chain counts + manifest checksums + one plaintext-holdout existence check, no eval result and no ground quality — see AA-439.
- **Continuity:** unreconciled contradiction — FA-1/G-25 (2026-07-28) falsify the ratification's premise; no amendment, no demotion path (Axiom-4 gap, same shape as AA-247).
- **Necessity/generality:** generalization-candidate — first multi-pack ratification; the multi-pack uniformity invariant is real and reusable.
- **Fitness:** contract-level evidence test-pinned; capability-level evidence against it (G-25: zero curriculum bands produced by this domain).

### ADR-0103 — Fluency lane attachment
- **Build:** full — both lanes exist with dev/public/holdout case files (`evals/hebrew_fluency/`, `evals/koine_greek_fluency/`), runners, contracts.
- **Liveness:** partial — public split has one committed result per lane (`results/v1_public_20260517T035718Z.json`); **holdout split has zero committed results ever** (AA-440).
- **Design fidelity:** tension with Pillar II — attaches "holdout" splits that are plaintext and repo-readable, i.e. not held out from anyone.
- **Build fidelity:** matches its own text — but its own text ("Both lanes now ship plaintext holdout sets") contradicts ADR-0105, accepted the same day (AA-441).
- **Continuity:** unreconciled contradiction — ADR-0102 §Eval lane scope conditioned attachment on *sealed* holdouts; ADR-0103 attached plaintext ones and ADR-0105 banned them; none of the three reconciles.
- **Necessity/generality:** irreducible as a data attachment; no mechanism introduced.
- **Fitness:** one public-split run per lane; holdout discipline never exercised.

---

## Stack A3.2 — Expert-Demo / Audit-Passed Promotion Contract (ADR-0106, 0107, 0109, 0110, 0111, 0112, 0113)

**Falsifiable stack claim:** `audit-passed` = 9 ADR-0091 predicates + signed reproducible digest + CORE claim shapes. The digest/shape half is supported in code; the 9-predicate half is **false in code** — prior finding **AA-220 (🔴) CONFIRMED** (AA-442). New: the gate's step-1 `reasoning_capable` input is structurally incompatible with ADR-0105 (AA-443).

### ADR-0106 — Expert-demo promotion contract
- **Build:** full — `core/capability/expert_demo.py` (`evaluate_expert_demo`:288, `derive_evidence_digest`:236); registry in `docs/reviewers.yaml` (`audit_passed_claims`:29).
- **Liveness:** live — called per-domain from `reporting.py:453`; pinned by `tests/test_expert_demo_contract.py`.
- **Design fidelity:** pass (Pillar II, Axiom 5) for the digest/replay mechanism; the domain-scoping corrects the incoherence its own §Context documents (`reporting.py:418` cognition-only flip, since removed).
- **Build fidelity:** partial drift — §1.1 "ADR-0093 contract still holds" is implemented as the `reasoning_capable` boolean of `reporting.py:428-434`, which consults no eval result (Batch-2 AA-233 territory) and a plaintext-holdout existence check (AA-443); §1.2's uniform thresholds superseded by ADR-0109.
- **Continuity:** clean — amended by 0109, renamed by 0113.
- **Necessity/generality:** irreducible — the promotion contract layer.
- **Fitness:** the ADR-0107 refusal and ADR-0200 quarantine both show the gate refusing for real; digest replay not re-executed here (charter: no execution).

### ADR-0107 — mathematics_logic promotion deferred
- **Build/Liveness:** n/a-mechanism — a decision record; no dedicated test file exists (retracted dossier's `test_adr_0107_deferral.py` is fabricated), none needed.
- **Design fidelity:** pass — fail-closed refusal recorded with evidence; honest.
- **Build fidelity:** matches — the two gaps it names (metric-shape mismatch; `inference_closure` 0.4) are the ones ADR-0109/0110 then addressed. Its own table already flagged fabrication_control holdout "not formally re-run after ADR-0105 sealing" — an early trace of the AA-444 seam.
- **Continuity:** superseded-cleanly by ADR-0110 via ADR-0109.
- **Necessity/generality:** irreducible as a record; proved the gate discriminates.
- **Fitness:** the deferral itself is the fitness evidence.

### ADR-0109 — Lane-shape-aware thresholds
- **Build:** full — shape checkers `_check_cognition_shape`/`_check_accuracy_shape`/`_check_inference_shape`/`_check_refusal_shape`/`_check_gsm8k_capability_shape` (`core/capability/expert_demo.py:73-222`), `resolve_lane_shape`:224.
- **Liveness:** live — dispatched via `_meets_thresholds`:268 on every gate evaluation; unknown lanes fail closed (`:271`).
- **Design fidelity:** pass — Axiom 7 correction of ADR-0106's wrong uniformity.
- **Build fidelity:** matches.
- **Continuity:** clean amendment of 0106.
- **Necessity/generality:** generalization-candidate — absorbed gsm8k shape later (ADR-0119.8) as designed.
- **Fitness:** enabled the 0110/0111 promotions that 0107 showed were impossible without it.

### ADR-0110 — mathematics_logic promotion
- **Build:** full — signed claim `docs/reviewers.yaml:30-37` (digest `94d74781…`); `tests/test_adr_0110_math_expert_demo.py`.
- **Liveness:** live — claim consulted on every ledger report; row currently `audit-passed` (per `reviewers.yaml:55-66` quarantine note).
- **Design fidelity:** pass (Axiom 5 digest replay).
- **Build fidelity:** matches (digest present; byte-replay not re-executed under this rigor tier).
- **Continuity:** clean — resolves 0107.
- **Necessity/generality:** irreducible — first worked promotion.
- **Fitness:** replay evidence recorded at acceptance; holdout evidence includes the leaked fabrication_control file (see AA-444 blast radius).

### ADR-0111 — physics promotion
- **Build:** full — claim `docs/reviewers.yaml:38-45` (digest `a104cad1…`); `tests/test_adr_0111_physics_expert_demo.py`.
- **Liveness:** live — same path as 0110.
- **Design/Build fidelity:** pass/matches — second domain through the same contract, unmodified.
- **Continuity:** clean.
- **Necessity/generality:** reducible-to-0106+data-row (the ADR adds no mechanism; same pattern as Batch-2 AA-244 on ADR-0100).
- **Fitness:** demonstrates contract non-bespokeness.

### ADR-0112 — Runnable showcase
- **Build:** full — `core/demos/expert_demo.py` (`run_expert_demo`), CLI wired at `core/cli.py:1739-1744`.
- **Liveness:** live — `core demo audit-passed --domain` registered; `tests/test_expert_demo_runnable.py`.
- **Design fidelity:** pass (Axiom 5 — re-derives, doesn't restate).
- **Build fidelity:** matches; CLI name follows the 0113 rename.
- **Continuity:** clean.
- **Necessity/generality:** generalization-candidate (serves any promoted domain).
- **Fitness:** inspectable proof artifact; not independently exercised here.

### ADR-0113 — Rename expert-demo → audit-passed
- **Build:** full — ledger status strings, YAML key (`audit_passed_claims`), predicate keys renamed (`reporting.py:38,460-461,497`).
- **Liveness:** live — every ledger row and CLI surface uses `audit-passed`.
- **Design fidelity:** pass Pillar II in intent; **its §Context restates a false claim** — see build fidelity.
- **Build fidelity:** **contradicts** — §Context #1 says the gate verifies "all nine ADR-0091 predicates pass"; `evaluate_expert_demo` never consults them (AA-442, confirming AA-220 🔴). Internal `expert_demo` identifiers retained by declared scope (module docstring records it) — AA-445 🟢.
- **Continuity:** clean rename otherwise; ADR-0102's invariant text pins `reasoning-capable` while rows may read `audit-passed` — absorbed by the sibling test's widened assertion (`:119`), unamended in the ADR.
- **Necessity/generality:** irreducible — honest-naming correction.
- **Fitness:** removes the "expert-level" misreading; the residual misclaim in its own §Context undercuts exactly the honesty it was written for.

---

## Stack A3.3 — Anti-Overfitting Proof Obligations (ADR-0114, 0114a, 0114a.2, 0114a.5, 0114a.6, 0114a.8, 0114a.10)

**Falsifiable stack claim:** all 10 obligations are falsifiable and enforced for any `expert` promotion. In code, all 10 are evaluated — but only for `mathematics_logic` (`core/capability/expert_promotion_math.py:146-331`, `_evaluate_obligation_1`…`_10`), and Obligation #1's "substrate already in place" premise is **false repo-wide** (AA-250 confirmed; AA-444/-8).

### ADR-0114 — Expert-capability roadmap (GSM8K-first)
- **Build:** scaffolded (roadmap); phases delivered by 0115–0120/0131 descendants.
- **Liveness:** n/a-mechanism — directs downstream work.
- **Design fidelity:** pass — "honest framing of distance" is the charter's own discipline.
- **Build fidelity:** partial drift — **header still `Proposed` at HEAD** while every phase shipped and its amendments are Accepted (AA-446).
- **Continuity:** clean — amended by 0114a; re-targeted by 0131 without contradiction (GSM8K demoted to stress lane, recorded there).
- **Necessity/generality:** generalization-candidate — the roadmap pattern reused by 0119/0131.
- **Fitness:** the arc it proposed exists end-to-end on disk.

### ADR-0114a — The 10 proof obligations
- **Build:** full as contract — all ten are evaluated in `expert_promotion_math.py` (20 `_evaluate_obligation_*` references; verdict dataclass `ObligationVerdict:88`).
- **Liveness:** live for math only — no domain-generic obligations runner exists (AA-447).
- **Design fidelity:** pass — Pillar II/Axiom 7 exemplar on paper.
- **Build fidelity:** **partial contradicts** — Obligation #1 §Status "Substrate already in place (ADR-0105 sealed holdouts)" is false at HEAD: 42 plaintext holdout case files tracked vs 3 `.age` seals, and the one ADR-0119.1-sealed lane leaks its holdout via a tracked results file (AA-444, AA-448; **AA-250 CONFIRMED**, contra retracted `AA-335`).
- **Continuity:** clean amendment of 0114; `adr_0114a_audit_passed_unaffected` invariant honored (gate code has no obligation checks).
- **Necessity/generality:** irreducible — the anti-overfitting charter.
- **Fitness:** the ADR-0200 quarantine (expert refused on drift) is live proof the framework binds.

### ADR-0114a.2 — OOD-ratio auditor (Obligation #2)
- **Build:** full — `core/capability/ood_ratio.py`; lane `evals/obligation_2_ood_ratio/`.
- **Liveness:** live — consumed at `expert_promotion_math.py:171-177`; `tests/test_adr_0114a_2_ood_ratio.py`.
- **Design/Build fidelity:** pass/matches (spot-verified wiring; per amended rigor, no execution).
- **Continuity:** clean. **Necessity:** irreducible. **Fitness:** obligation-2 verdict feeds the composer.

### ADR-0114a.5 — Perturbation suite (Obligation #5)
- **Build:** full — `core/capability/perturbation_b3.py`; lane `evals/obligation_5_perturbation/`; `tests/test_adr_0114a_5_perturbation.py`.
- **Liveness:** live — `_evaluate_obligation_5` (`expert_promotion_math.py:238`).
- **Design/Build fidelity:** pass/matches. **Continuity:** clean. **Necessity:** irreducible. **Fitness:** wired into composer verdict.

### ADR-0114a.6 — Depth-curve auditor (Obligation #6)
- **Build:** full — `core/capability/depth_curve.py`; lane `evals/obligation_6_depth_curve/`; `tests/test_adr_0114a_6_depth_curve.py`.
- **Liveness:** live — `_evaluate_obligation_6:256`.
- **Design fidelity:** pass; the ADR honestly self-reports "coverage gap deferred to B3-owner follow-up" in its own status line (AA-449 🟢 — B3 v1's depth coverage is thin per its §106).
- **Build fidelity:** matches. **Continuity:** clean. **Necessity:** irreducible. **Fitness:** mechanism accepted; coverage follow-up open.

### ADR-0114a.8 — Adversarial auditor (Obligation #8)
- **Build:** full — `core/capability/adversarial.py`; lane `evals/obligation_8_adversarial/`; `tests/test_adr_0114a_8_adversarial.py`.
- **Liveness:** live — `_evaluate_obligation_8:294`.
- **Design fidelity:** pass; status line honestly records "surfaces 2 known parser-layer gaps" (AA-449).
- **Build fidelity:** matches. **Continuity:** clean. **Necessity:** irreducible. **Fitness:** 9-family/36-case B3 adversarial dataset on disk.

### ADR-0114a.10 — Pack-provenance auditor (Obligation #10)
- **Build:** full — `core/capability/pack_provenance.py`; lane `evals/obligation_10_pack_provenance/`; `tests/test_adr_0114a_10_pack_provenance.py`.
- **Liveness:** live — `_evaluate_obligation_10:331`.
- **Design/Build fidelity:** pass/matches — makes "reasons from concepts" checkable per the parent's §10. **Continuity:** clean. **Necessity:** irreducible. **Fitness:** binds traces to pack lemmas.

---

## Stack A3.4 — Sealed Holdouts & GSM8K Eval Lane (ADR-0105, 0119, 0119.1–0119.8)

**Falsifiable stack claim:** holdouts are sealed and leakage eliminated; the GSM8K lane is a deterministic multi-split pipeline. The pipeline half is supported (artifacts + tests on disk). The sealing half is **falsified at HEAD**: **AA-250 CONFIRMED** (AA-444) and ADR-0105's own acceptance gate is unmet (AA-448). This is the stack the retracted dossier marked clean (`AA-337` 🟢) — that verdict is refuted with file-level evidence.

### ADR-0105 — Sealed holdout encryption via age
- **Build:** mechanism full — `evals/holdout_runner.py` (`HOLDOUT_KEY_ENV`:23, fail-closed semantics :46-50), `scripts/seal_holdouts.py`, `tests/test_holdout_encryption.py`, recipients in `docs/holdout_recipients.txt`. (Retracted dossier's `core/evals/holdout_runner.py` does not exist.)
- **Liveness:** live for 3 lanes only — `git ls-files` shows exactly 3 `.age` seals (`fabrication_control`, `gsm8k_math`, `math_symbolic_equivalence`) against **42 tracked plaintext holdout case files** across the other lanes; the seal tooling discovers them (`PLAINTEXT_NAMES`, `scripts/seal_holdouts.py:18`) but was never run to completion.
- **Design fidelity:** the decision honors Pillar II; the rollout violates the ADR's own trust-boundary rationale — "transitional-only" plaintext became the standing regime.
- **Build fidelity:** **contradicts** — acceptance gate "Existing holdouts are resealed as `.age` artifacts" is false at HEAD (AA-448 🔴).
- **Continuity:** unreconciled — ADR-0103 (same day) celebrates plaintext holdouts; `reporting.py:421` *requires* a plaintext holdout file to exist for every domain's license (AA-443).
- **Necessity/generality:** irreducible — the only leakage control the eval layer has.
- **Fitness:** works where applied (0119.1/0119.7/0131.1.S); 39 lanes outside it.

### ADR-0119 — GSM8K eval lane roadmap
- **Build:** scaffolded (roadmap-only by declaration); all 8 sub-phases delivered.
- **Liveness:** n/a-mechanism.
- **Design/Build fidelity:** pass/matches as a roadmap.
- **Continuity:** clean; header remains `Proposed (roadmap-only)` with no closure record after all sub-phases Accepted (AA-450 🟢).
- **Necessity/generality:** generalization-candidate (decomposition template reused by 0131).
- **Fitness:** decomposition executed 8-for-8.

### ADR-0119.1 — Seal fabrication_control holdout
- **Build:** full — `evals/fabrication_control/holdouts/v1/cases.jsonl.age`; runner decrypts via `evals/holdout_runner.py._decrypt_holdout` (`runner.py:209`); `tests/test_adr_0119_1_sealed_holdout.py`.
- **Liveness:** live — holdout split decryptable, fail-closed without `CORE_HOLDOUT_KEY`.
- **Design fidelity:** pass in mechanism; defeated in outcome.
- **Build fidelity:** **contradicts** — §Consequences "Plaintext leaks of `fabrication_control` holdout are eliminated from the current tree" is false: git-tracked `evals/fabrication_control/results/v1_holdout.json` carries every holdout case's `prompt` and full `surface` (`fab_hld_a1` "Does quibix support flarnel?", …). Worse, that leaked file **is** the holdout evidence the audit-passed gate reads (`reporting.py:102-108` exact-name fallback `v1_holdout.json` → consumed at `:437-452`). **AA-250 CONFIRMED** (AA-444 🔴).
- **Continuity:** falsified consequence unrecorded; ADR-0114a Obligation #1 remains undischarged for this lane.
- **Necessity/generality:** irreducible — first worked seal.
- **Fitness:** negative — the seal exists and the same lane leaks anyway.

### ADR-0119.2 — GSM8K corpus (dev/public)
- **Build:** full — `evals/gsm8k_math/{dev,public,contract.md,verify.py,verify_all.py}`.
- **Liveness:** live — consumed by runner + lane-gate test (dev 50/50, public 150/150 per `tests/test_adr_0119_8_lane_gate.py` invariant 3).
- **Design/Build fidelity:** pass/matches (CORE-original corpus, disjoint from GSM8K per parent). **Continuity:** clean. **Necessity:** irreducible. **Fitness:** corpus feeding all downstream sub-phases.

### ADR-0119.3 — Lane runner
- **Build:** full — `evals/gsm8k_math/runner.py`. **Liveness:** live (test-pinned via 0119.8's invariant 3).
- **Design/Build fidelity:** pass/matches. **Continuity:** clean. **Necessity:** irreducible. **Fitness:** deterministic results per lane-gate test.

### ADR-0119.4 — Frontier baseline comparison
- **Build:** full — `evals/gsm8k_math/baselines/`; `tests/test_adr_0119_4_frontier_baseline.py`. **Liveness:** live in test/audit path (citation-only per ADR-0045 convention).
- **Design/Build fidelity:** pass/matches. **Continuity:** clean; ADR-0131.1.F later re-does this for the composite lanes. **Necessity:** reducible-to-pattern (ADR-0045). **Fitness:** discharges Obligation #7 for the GSM8K lane.

### ADR-0119.5 — Adversarial generation
- **Build:** full — `evals/gsm8k_math/adversarial/` (+ `confusers/`); `tests/test_adr_0119_5_adversarial.py`. **Liveness:** live via tests.
- **Design/Build fidelity:** pass/matches (misparse-zero discipline). **Continuity:** clean. **Necessity:** irreducible (Obligation #8 wiring). **Fitness:** suite exists; obligation-8 auditor (0114a.8) later generalizes it for B3.

### ADR-0119.6 — Depth-curve harness
- **Build:** full — `tests/test_adr_0119_6_depth_curve.py` + scoring artifacts under `evals/gsm8k_math/scoring/`. **Liveness:** live via tests.
- **Design/Build fidelity:** pass/matches (Obligation #6 wiring). **Continuity:** clean; 0114a.6 generalizes to B3. **Necessity:** irreducible then, superseded-in-role now. **Fitness:** curve mechanism proven.

### ADR-0119.7 — Sealed GSM8K test set
- **Build:** full — `evals/gsm8k_math/holdouts/v1/cases.jsonl.age`, `scripts/seal_gsm8k_test.py`, `tests/test_adr_0119_7_sealed_gsm8k.py`. **Liveness:** live.
- **Design/Build fidelity:** pass/matches — one of only three lanes actually meeting ADR-0105. **Continuity:** clean. **Necessity:** irreducible (Obligation #1 for this lane). **Fitness:** the honest counter-example to AA-448.

### ADR-0119.8 — Lane gate
- **Build:** full — `gsm8k_capability_shape` checker (`core/capability/expert_demo.py:167`), registry entry; `tests/test_adr_0119_8_lane_gate.py` pins six invariants incl. zero-wrong (Obligation #4).
- **Liveness:** live — fail-closed via `_meets_thresholds`. **Design/Build fidelity:** pass/matches. **Continuity:** clean — ADR-0109's registry absorbed it as designed. **Necessity:** irreducible. **Fitness:** enforces ADR-0114a #4 in the shipping gate.

---

## Stack A3.5 — Math Expert Re-Benchmark (ADR-0131 family, 16 files)

**Falsifiable stack claim:** the composite gate (B1+B2+B3) measures math capability honestly and fail-closed. **Supported on disk**: `core/capability/composite_math_gate.py` is real, thresholds pinned (`CORRECT_RATE_MIN=0.95`, zero-wrong), and the ADR-0200 quarantine (`docs/reviewers.yaml:55-66`) shows the gate refusing `expert` after probe drift broke the digest — fail-closed firing in production records (AA-451 🟢). Two real defects: pervasive `Proposed` headers on merged work (AA-452) and zero probe-admission movement from the G.x axes (AA-453).

### ADR-0131 — Re-target math promotion to architecture-aligned benchmarks
- **Build:** full — `composite_math_gate.py` wires B1 public+sealed / B2 / B3 report paths (`:79-82`).
- **Liveness:** live — consumed by `expert_promotion_math.py:42`; `tests/test_adr_0131_4_composite_math_gate.py`.
- **Design fidelity:** pass — Axiom 7 in its strongest Batch-3 form (rejects the external benchmark rather than gaming it); GSM8K retained as non-gating honest disclosure (`_gsm8k_honest_disclosure:248`).
- **Build fidelity:** matches.
- **Continuity:** clean vs 0114/0119 (GSM8K demoted with a recorded rationale); **header still `Proposed`** (AA-452).
- **Necessity/generality:** irreducible — the pivot decision.
- **Fitness:** replaced a 0/1319-shaped failure with a measurement the architecture can honestly pass or fail; ADR-0200 quarantine proves the "fail" branch works.

### ADR-0131.1.F — Frontier baseline comparison
- **Build:** full — `evals/math_symbolic_equivalence/v1/frontier/{baselines.py,comparison.json,frontier_runner.py,responses/}`.
- **Liveness:** live — `_evaluate_obligation_7` reads the frontier dir (`expert_promotion_math.py:268`).
- **Build fidelity:** matches; **header `Proposed`** while artifacts are load-bearing (AA-452).
- **Design fidelity:** pass. **Continuity:** clean. **Necessity:** reducible-to-pattern (ADR-0045/0119.4). **Fitness:** Obligation #7 evidence source.

### ADR-0131.1.S — Sealed holdout (B1)
- **Build:** full — `sealed_holdout.age`, `sealed_holdout.pubkey`, `sealed_runner.py`, `sealed_report.json` under `evals/math_symbolic_equivalence/v1/`; `tests/test_adr_0131_1_sealed_holdout.py`.
- **Liveness:** live — `_evaluate_obligation_1` reads the sealed report (`expert_promotion_math.py:146`).
- **Design/Build fidelity:** pass/matches — third and last lane meeting ADR-0105. **Continuity:** clean. **Necessity:** irreducible (Obligation #1 for the composite gate). **Fitness:** the obligation-1 source the math expert path actually uses.

### ADR-0131.2 — Teaching corpus eval (B2)
- **Build:** full — `evals/math_teaching_corpus/v1/{cases.jsonl,runner.py,report.json}`. **Liveness:** live — B2 report read by composite gate (`:81`); `tests/test_adr_0131_2_teaching_corpus_lane.py`.
- **Design/Build fidelity:** pass/matches. **Continuity:** clean. **Necessity:** irreducible (exact-recall benchmark). **Fitness:** committed report on disk.

### ADR-0131.2.B — Teaching corpus enrichment
- **Build:** full — enriched `cases.jsonl` in place. **Liveness:** live via B2 lane. **Design/Build fidelity:** pass/matches. **Continuity:** clean amendment. **Necessity:** reducible-to-0131.2 (data growth, no mechanism). **Fitness:** corpus breadth for B2.

### ADR-0131.3 — Bounded grammar (B3)
- **Build:** full — `evals/math_bounded_grammar/v1/{cases.jsonl,grammar.md,runner.py,report.json}`; `tests/test_adr_0131_3_bounded_grammar_lane.py`.
- **Liveness:** live — B3 report read by composite gate (`:82`); B3 is also the substrate the 0114a.5/.6/.8 auditors run against.
- **Design/Build fidelity:** pass/matches (closed grammar, 100%-or-refuse claim shape). Header uses plain `## Status Accepted` format — cosmetic only.
- **Continuity:** clean. **Necessity:** irreducible. **Fitness:** the lane three obligations audit.

### ADR-0131.4 — Composite math gate
- **Build:** full — `evaluate_composite_math_gate` (`composite_math_gate.py:305`), digest (`_compute_claim_digest:281`).
- **Liveness:** live — sole gate consulted by the expert composer; `tests/test_adr_0131_4_composite_math_gate.py`.
- **Design/Build fidelity:** pass/matches — pure function over committed reports (Axiom 5). **Continuity:** clean — explicitly does not substitute for ADR-0120's 10-obligation contract (docstring `:34-37`). **Necessity:** irreducible. **Fitness:** the mechanism ADR-0200's refusal ran through.

### ADR-0131.5 — GSM8K probe retirement
- **Build/Liveness:** decision record; probe demoted to non-gating honest disclosure (`_gsm8k_honest_disclosure`, `composite_math_gate.py:248`; train-sample report consumed at `expert_promotion_math.py:76`).
- **Design fidelity:** pass — retires a gate that measured the wrong layer, with the negative result published.
- **Build fidelity:** matches.
- **Continuity:** clean amendment of 0131.G.
- **Necessity/generality:** irreducible as a record.
- **Fitness:** its own table is the key measurement: **GSM8K admission 0/50 unchanged after all five G.x axes** — the axes targeted question/initial-state layers while all 50 cases fail at statement-layer parsing (AA-453 🟡; the early form of G-21/G-24's reader-bottleneck diagnosis).

### ADR-0131.G — GSM8K coverage probe
- **Build:** full — `evals/gsm8k_parser_dev/{cases.jsonl,ood_score.py,perturbation_score.py}` + `evals/gsm8k_math/train_sample/` coverage report. **Liveness:** live as disclosure input (non-gating since 0131.5).
- **Design/Build fidelity:** pass/matches. **Continuity:** clean (retired per 0131.5). **Necessity:** irreducible then. **Fitness:** the diff-able baseline that honestly showed 0/50; header `Proposed` (AA-452).

### ADR-0131.G.0 — Probe substrate
- **Build:** full (probe scoring substrate in `gsm8k_parser_dev/`). **Liveness:** live via probe. **Fidelity:** pass/matches. **Continuity:** clean. **Necessity:** reducible-to-0131.G. **Fitness:** substrate only; header `Proposed` (AA-452).

### ADR-0131.G.1 — Verb classes / initial state
- **Build:** full — `evals/math_capability_axes/G1_verb_classes/`; `tests/test_adr_0131_G1_verb_classes.py`. **Liveness:** live (axis lane + tests). **Fidelity:** pass/matches. **Continuity:** clean. **Necessity:** irreducible per-axis. **Fitness:** axis wrong=0; zero probe-admission movement (AA-453).

### ADR-0131.G.2 — Comparatives
- **Build:** full — `G2_comparatives/` axis + `tests/test_adr_0131_G2_comparatives.py` (+ G2a widening test). **Liveness:** live. **Fidelity:** pass/matches; header `Proposed` (AA-452). **Continuity:** clean. **Necessity:** irreducible per-axis. **Fitness:** 31 cases, wrong=0; no probe movement.

### ADR-0131.G.3 — Numerics
- **Build:** full — `G3_numerics/` + `tests/test_adr_0131_G3_numerics.py`. **Liveness:** live. **Fidelity:** pass/matches; header `Proposed`. **Continuity:** clean. **Necessity:** irreducible per-axis. **Fitness:** curated lane, wrong=0; no probe movement.

### ADR-0131.G.3.1 — Numerics extensions
- **Build:** full — `tests/test_adr_0131_G31_numerics_extensions.py`. **Liveness:** live. **Fidelity:** pass/matches; header `Proposed`. **Continuity:** clean amendment. **Necessity:** reducible-to-G.3. **Fitness:** same as G.3.

### ADR-0131.G.4 — Multi-clause
- **Build:** full — `G4_multi_clause/` + `tests/test_adr_0131_G4_multi_clause.py`. **Liveness:** live. **Fidelity:** pass/matches; header `Proposed`. **Continuity:** clean. **Necessity:** irreducible per-axis. **Fitness:** wrong=0; no probe movement.

### ADR-0131.G.5 — Aggregate answer composition
- **Build:** full — `G5_aggregate/` + `tests/test_adr_0131_G5_aggregate.py`. **Liveness:** live. **Fidelity:** pass/matches (Accepted). **Continuity:** clean — the axis whose completion triggered 0131.5's retirement ruling. **Necessity:** irreducible per-axis. **Fitness:** 20 cases wrong=0; probe still 0/50.

---

## Stack A3.6 — Statement-Layer Corridor (ADR-0136, 0136.S.1, 0136.S.2, 0136.S.4, 0136.S2-post-rescan, 0136.S3, 0136.S3-post-rescan)

**Falsifiable stack claim:** graduated S-stage extension widened admission at zero misparse, and was honestly superseded by ADR-0164. Supported: supersession banners are present and accurate on every mechanism ADR (**AA-342 re-verified — the one retracted finding worth keeping**, AA-454 🟢). Residue: the "scheduled for removal" regexes are still live two months on (AA-455 🔵).

### ADR-0136 — Statement-layer corridor
- **Build:** full — corridor taxonomy + refusal classification landed; taxonomies preserved per banner.
- **Liveness:** live — S-stage machinery still on `parse_and_solve` (see S.1 card); refusal taxonomy artifacts under `evals/refusal_taxonomy/`.
- **Design fidelity:** pass — fail-closed graduated admission; regex scope bounded by ADR-0165.
- **Build fidelity:** matches — the header's own supersession note ("Regex sentence-template prescription superseded by ADR-0164 (2026-05-26). Empirical taxonomies preserved") is accurate.
- **Continuity:** superseded-cleanly (exemplary banner discipline).
- **Necessity/generality:** reducible-to-ADR-0164 — seed taxonomies absorbed as lexicon.
- **Fitness:** produced the 50-case refusal classification that later grounded 0131.5's layer diagnosis.

### ADR-0136.S.1 — Rate/event statements
- **Build:** full — closed vocabularies + regexes live at `generate/math_candidate_parser.py:2418-2501` (`_CAPACITY_VERBS`, `_CAPACITY_RE`, `_EARNINGS_RE`); axis lane `evals/math_capability_axes/S1_rate_events/`; `tests/test_adr_0136_S1_rate_events.py`.
- **Liveness:** live — on the `parse_and_solve` path (test pins the end-to-end short-circuit).
- **Design fidelity:** tension — banner says regexes "scheduled for removal under ADR-0164 Phase 3"; still shipping (AA-455).
- **Build fidelity:** matches. **Continuity:** superseded-cleanly on paper, removal pending in code. **Necessity:** reducible-to-0164. **Fitness:** admission gain test-pinned at zero misparse.

### ADR-0136.S.2 — Conditional op question
- **Build:** full — `tests/test_adr_0136_S2_conditional_op.py`; unlike S1/S3/S4 no dedicated `math_capability_axes` lane dir (test-pinned only).
- **Liveness:** live via parser path. **Design fidelity:** same AA-455 tension (banner identical). **Build fidelity:** matches. **Continuity:** superseded-cleanly on paper. **Necessity:** reducible-to-0164. **Fitness:** test-pinned; status vocabulary `Active` vs siblings' `Accepted` — cosmetic.

### ADR-0136.S.4 — Novel initial form
- **Build:** full — `S4_novel_initial_form/` axis + `tests/test_adr_0136_S4_novel_initial_form.py`. **Liveness:** live. **Design fidelity:** AA-455 tension. **Build fidelity:** matches. **Continuity:** superseded-cleanly on paper. **Necessity:** reducible-to-0164. **Fitness:** test-pinned.

### ADR-0136.S2-post-rescan — Post-S2 rescan record
- **Build/Liveness:** measurement-record ADR; no mechanism. **Fidelity:** matches (rescan numbers recorded). **Continuity:** clean. **Necessity:** irreducible as record. **Fitness:** the honest per-stage re-measurement discipline the corridor promised.

### ADR-0136.S3 — Compound initial mutation
- **Build:** full — `S3_compound_initial_mutation/` axis + `tests/test_adr_0136_S3_compound_initial_mutation.py`. **Liveness:** live. **Design fidelity:** AA-455 tension (same banner). **Build fidelity:** matches. **Continuity:** superseded-cleanly on paper. **Necessity:** reducible-to-0164. **Fitness:** test-pinned.

### ADR-0136.S3-post-rescan — Post-S3 rescan record
- **Build/Liveness:** measurement-record ADR. **Fidelity:** matches. **Continuity:** clean. **Necessity:** irreducible as record. **Fitness:** rescan discipline held.

---

## Stack A3.7 — Semantic-Symbolic Binding Graph (ADR-0132–0135)

**Falsifiable stack claim:** the binding graph is the typed compiler boundary between semantic parsing and symbolic solving. Three-quarters supported: the **model** (0132), **admissibility** (0134) and the **BoundUnknown target model** (0135) are live in production (`generate/proof_chain/builder.py:36-41`, `generate/quantitative_comprehension.py:40-49,504,519-524`, `core/comprehension_attempt/model.py:23`, `evals/dimensional/runner.py:18`). The **adapter** (0133) — the piece that makes it a *boundary* from the legacy `MathProblemGraph` — has zero production callers (AA-456 🟡), refuting the retracted dossier's "dispatched during graph construction".

### ADR-0132 — Phase 1 data model
- **Build:** full — `generate/binding_graph/model.py` (frozen dataclasses, half-open spans, `BoundUnknown:317` with closed vocabularies `:61-68`); `tests/test_binding_graph_model.py`.
- **Liveness:** live — imported by proof-chain builder, quantitative comprehension, comprehension-attempt, and eval lanes.
- **Design fidelity:** pass (Pillar II typed boundary; immutability).
- **Build fidelity:** matches.
- **Continuity:** header note "Phases 2–5 deferred" is stale — Phases 2–4 landed as 0133/0134/0135 (AA-457 🟢); parent proposal correctly marked archived per ADR-0252 §9.
- **Necessity/generality:** irreducible — the type layer everything else in the stack rests on.
- **Fitness:** broad production reuse beyond the original math scope.

### ADR-0133 — Phase 2 adapter
- **Build:** full — `bind_math_problem_graph` (`generate/binding_graph/adapter.py:203`) with unit hints and admissibility pre-checks; `tests/test_binding_graph_adapter.py`.
- **Liveness:** **wired-but-unreached** — zero production callers; only tests and `generate/binding_graph/__init__.py:49` re-export. The shipping comprehension path builds graphs directly (`quantitative_comprehension.py:519-524`), bypassing the adapter (AA-456).
- **Design fidelity:** pass in isolation; sabotage test fails — removing it changes no serving or eval output.
- **Build fidelity:** matches its text; the text's role was overtaken.
- **Continuity:** unrecorded bypass — no ADR notes that the quantitative-comprehension path made the adapter vestigial.
- **Necessity/generality:** reducible — candidate for retirement or explicit re-scoping to the legacy-graph migration it served.
- **Fitness:** none found on production paths.

### ADR-0134 — Phase 3 equation admissibility
- **Build:** full — `generate/binding_graph/admissibility.py` (`check_admissibility`, `UnitProof:100`, `AdmissibilityError:73`) + `units.py`; `tests/test_binding_graph_admissibility.py`.
- **Liveness:** live — `quantitative_comprehension.py:504` calls it on the real comprehension path; `evals/dimensional/runner.py:18` consumes the unit algebra.
- **Design fidelity:** pass — fail-closed dimensional checking (Pillar II).
- **Build fidelity:** matches. **Continuity:** clean. **Necessity:** irreducible. **Fitness:** live rejection of dimensionally invalid equations pre-solve.

### ADR-0135 — Phase 4 question target
- **Build:** full — `generate/binding_graph/question_target.py` (`infer_question_form:156`, `bound_unknown_from_math_problem_graph:234`); `tests/test_binding_graph_question_target.py`.
- **Liveness:** split — the `BoundUnknown` target model is live (constructed directly at `quantitative_comprehension.py:519-524`); the ADR's `MathProblemGraph` extraction helper is consumed only by tests and `evals/refusal_taxonomy/shape_categories.py` (same bypass seam as 0133).
- **Design fidelity:** pass (closed question-form vocabulary, refuse-on-ambiguity).
- **Build fidelity:** matches. **Continuity:** clean; extraction-helper half shares 0133's unrecorded bypass. **Necessity:** irreducible for the model half; helper half reducible with 0133. **Fitness:** target binding live in production comprehension.

---

## Findings rollup (renumbered into the corpus sequence)

- **AA-439** 🔴 **Block** — (A3.1) **AA-75 confirmed at HEAD, retracted downgrade refuted:** ADR-0102/0103's `reasoning-capable` license is granted by `core/capability/reporting.py:428-434` from manifest checksums + chain counts + intent shapes + existence of `evals/cognition/holdouts/cases_plaintext.jsonl` — no eval result and no semantic-ground signal — so FA-1's NO-GO and G-25's zero-curriculum-band verdict cannot demote the row, and neither ADR carries an FA-1 annotation.
- **AA-441** 🟡 **Repair** — (A3.1) ADR-0102 §Eval lane scope conditions fluency attachment on *sealed* holdouts; ADR-0103 attached them plaintext ("Both lanes now ship plaintext holdout sets") the same day ADR-0105 banned committed plaintext holdouts — three-way unreconciled contradiction.
- **AA-440** 🟡 **Repair** — (A3.1) `hebrew_fluency`/`koine_greek_fluency` have zero committed holdout-split results (only `results/v1_public_20260517T035718Z.json` each); ADR-0103's dev/public/holdout discipline is declaration-only for the holdout split.
- **AA-442** 🔴 **Block** — (A3.2) **AA-220 confirmed:** ADR-0113 §Context #1 ("gate verifies all nine ADR-0091 predicates pass") is false — `evaluate_expert_demo` (`core/capability/expert_demo.py:288-383`) never consults the predicate results; `reporting.py` computes them (`:393-396`) for display only (`:519`).
- **AA-443** 🔴 **Block** — (A3.2/A3.4) The ledger's `reasoning_capable` predicate **requires a plaintext holdout file to exist** (`reporting.py:421,433`): executing ADR-0105's own acceptance gate (seal/remove plaintext) would demote every domain below `reasoning-capable`. Two Accepted ADRs are mutually unsatisfiable at HEAD; extends Batch-2 AA-233.
- **AA-445** 🟢 **Monitor** — (A3.2) Internal `expert_demo` identifiers retained under ADR-0113's declared semantics-only scope (module docstring records it); sibling test widened to accept both status strings (`tests/test_adr_0100_0102_sibling_ratifications.py:119`). Declared drift; retracted AA-334's substance, correct severity.
- **AA-444** 🔴 **Block** — (A3.3/A3.4) **AA-250 confirmed at HEAD:** git-tracked `evals/fabrication_control/results/v1_holdout.json` carries every sealed holdout case's `prompt` + full `surface`, falsifying ADR-0119.1 §Consequences ("plaintext leaks … eliminated") and leaving ADR-0114a Obligation #1 undischarged for the lane — and the leaked file is itself the holdout evidence the audit-passed gate reads (`reporting.py:102-108` fallback `v1_holdout.json` → `:437-452`), placing it inside every promoted domain's evidence digest.
- **AA-448** 🔴 **Block** — (A3.4) ADR-0105's acceptance gate "Existing holdouts are resealed as `.age` artifacts" is unmet at HEAD: 42 tracked plaintext holdout case files (`git ls-files`, `holdout(s)/**/cases*.jsonl`) vs 3 `.age` seals; ADR-0119.1's "subsequent ADRs" migration arrived only for gsm8k_math (0119.7) and math_symbolic_equivalence (0131.1.S). The "transitional-only" plaintext regime is the standing regime.
- **AA-446** 🟡 **Repair** — (A3.3) ADR-0114 header still `Proposed` at `cbfc8ccb` while Phases 1–5 shipped and all descendants are Accepted (re-verifies void AA-336 with the header read at HEAD).
- **AA-447** 🟡 **Repair** — (A3.3) Obligations #1/#3/#4/#7/#9 have no standalone auditor ADR or module; all ten are enforced only inside `core/capability/expert_promotion_math.py:146-331` against math-lane artifacts — the ADR-0114a framework is domain-agnostic on paper, `mathematics_logic`-only in enforcement.
- **AA-452** 🟡 **Repair** — (A3.5) Status drift re-verified: ADR-0131, 0131.1.F, 0131.G, G.0, G.2, G.3, G.3.1, G.4 read `Proposed` while their artifacts are merged and load-bearing (`composite_math_gate.py`; `evals/math_symbolic_equivalence/v1/frontier/comparison.json`; probe report consumed at `expert_promotion_math.py:76`).
- **AA-453** 🟡 **Repair** — (A3.5) All five G.x axes landed with GSM8K probe admission **0/50 unchanged** (ADR-0131.5's own table): the axes targeted question/initial-state layers while all 50 cases fail at statement-layer parsing — the early, in-family instance of the G-21/G-24 reader-bottleneck diagnosis; capability value on the probe's own metric was zero.
- **AA-455** 🔵 **Consolidate** — (A3.6) S-stage regexes "scheduled for removal under ADR-0164 Phase 3" (banners dated 2026-05-26) are still live at HEAD (`generate/math_candidate_parser.py:2418-2501` on the `parse_and_solve` path); two parser mechanisms coexist with no removal or re-scheduling record.
- **AA-456** 🟡 **Repair** — (A3.7) ADR-0133's sole deliverable `bind_math_problem_graph` (`generate/binding_graph/adapter.py:203`) has zero production callers (tests + package `__init__` only); the shipping path builds binding graphs directly (`generate/quantitative_comprehension.py:519-524`). Sabotage test fails; retracted "dispatched during graph construction" refuted. ADR-0135's extraction helper shares the same unrecorded bypass.
- **AA-457** 🟢 **Monitor** — (A3.7) ADR-0132 header still reads "Phases 2–5 deferred" though Phases 2–4 landed as ADR-0133/0134/0135.
- **AA-451** 🟢 **Monitor** — (A3.5) Positive control: the ADR-0200 quarantine (`docs/reviewers.yaml:55-66`) shows the composite/expert gate fail-closed in production records — probe drift (3/47→4/46) broke digest `4c46f530…`→`02f6d3c8…`, the composer refuses, and the ledger honestly reports `mathematics_logic = audit-passed`.
- **AA-450** 🟢 **Monitor** — (A3.4) ADR-0119 umbrella remains `Proposed (roadmap-only)` with all 8 sub-phases Accepted and built; roadmap-only by design but no closure record exists.
- **AA-454** 🟢 **Monitor** — (A3.6) Retracted AA-342 re-verified accurate: ADR-0136-family supersession banners honestly record the ADR-0164 handover with taxonomies preserved — the corpus's best supersession-hygiene example in this batch.
- **AA-449** 🟢 **Monitor** — (A3.3) ADR-0114a.6 ("coverage gap deferred to B3-owner follow-up") and 0114a.8 ("surfaces 2 known parser-layer gaps") self-report open gaps in their own status lines; honest, unclosed — track to closure.

**Severity tally: 19 findings — 🔴 5 · 🟡 7 · 🔵 1 · 🟢 6.**

**Prior-finding dispositions:** AA-75 **confirmed + extended** (AA-439; retracted AA-332 downgrade refuted). AA-250 **confirmed + extended** (AA-444, -8; retracted AA-335/AA-337 "clean" verdicts refuted). AA-220 **confirmed** (AA-442). AA-232/AA-233 mechanisms re-observed in-scope (`reporting.py:102-108`, `:428-434`) — cited, not re-registered. AA-262 (one 9-case corpus as 4 domains' negative control) still true, cited under A3.4. AA-342 **confirmed accurate** (AA-454).
