# Batch 3 — Tier B Redo (honest re-verification)

**Corpus:** the 38 Tier B files of ADR-0101–0150 · **Verified against:** `main` @ `cbfc8ccb` (2026-07-29)
**Charter:** `docs/adr-audit/00-scope-and-method.md` (cost-corrected rigor tier, 2026-07-29)
**Replaces:** `Batch3-TierB-consolidated.md` (RETRACTED — verdicts void; zone groupings reused per the retraction notice's disposition)

## Corrections to the retracted map, up front

1. **Coverage.** The retracted file claimed 35 ADRs; the true Tier B set is **38**. It silently omitted `ADR-0127-0128-RESULTS.md` (`0127~1`), ADR-0129, and ADR-0130. All three are carded below (0127~1 in B3.2; 0129/0130 as a B3.3 subsection).
2. **Fabricated artifact citations.** The retracted cards cite `core/capability/expert_contract.py`, `core/capability/ledger.py`, and `evals/inference_shape/` as "Found: yes" with file:line. **None of the three exists at HEAD** (verified by existence check). The real artifacts: the expert contract/composer is `core/capability/expert_promotion_math.py`; the capability ledger is computed dynamically in `core/capability/reporting.py` (`_EXPERT_DOMAIN_STATUSES`, `reporting.py:37-46`); the inference-shape checker lives in `core/capability/expert_demo.py:117-125`. The retracted 0120~3 card's artifact (`core/reasoning/adapters.py`) is likewise a mis-attribution — that module is a generic trace→evidence adapter that never cites ADR-0120.
3. **A retracted verdict contradicted by prior verified evidence.** Retracted `AA-345` claimed ADR-0101 "relies on the retired cross-language holonomy premise (`AA-75`)". Verified Batch-2 finding **`AA-245`** ("FA-1 / G-25 alignment defect does not reach this stack") already established that the ADR-0091/0097 ratification predicates are structural/textual (manifest fields, chain coverage, lane declarations), not holonomy-dependent; ADR-0101 applies that same template. AA-345's carry-forward is **not adopted**; no replacement finding is raised on that axis.
4. **A retracted verdict inverted by the tree.** Retracted `AA-349`/`AA-350`/`AA-351` called the versor spikes "unbuilt draft designs" and stopped there; the actual state is stranger and worse in one direction (claimed-passing test artifacts absent — `AA-458`) and better in another (the constructions live on, uncited, in ADR-0249's `core/physics/quantity_kernel.py` — `AA-459`).

Prior-evidence engagements required by the charter are inline per card: `AA-124`/`AA-125` (ADR-0014 `LearningArtifact` dead / stub unruled), `AA-237`/`AA-238` (ratification status drift), `AA-245`, `AA-246`, `AA-248`, `AA-250` (fabrication_control holdout leaked in plaintext), `AA-262`, `AA-293`/`AA-295`/`AA-299` (dead substrate / status drift / flag accumulation classes), `AA-308`–`AA-318` (B2.6 review-gating cluster), `AA-342` (0136→0164 supersession, the retraction's verified-accurate spot check).

---

## Zone B3.1 — Curriculum & Mining Proposal Pipeline (0101, 0104, 0108)

### ADR-0101 — Systems-Software Reasoning-Capable Ratification
- **Build:** full — manifest carries Domain Contract v1 fields (`packs/data/en_systems_software_v1/manifest.json`), chains file exists (`teaching/domain_chains/systems_software_chains_v1.jsonl`), pinning test exists (`tests/test_adr_0100_0102_sibling_ratifications.py`).
- **Liveness:** live — ledger row computed per-turn-of-`core capability ledger` from `core/capability/reporting.py`; the pinning test is real.
- **Design fidelity:** pass on Pillar II (declares its `symbolic_logic` lane-fit limitation explicitly). Per verified `AA-245`, the FA-1 holonomy retirement does not reach these predicates — no Axiom-7 violation adopted (contra retracted AA-345).
- **Build fidelity:** partial drift — acceptance evidence says the test pins status `reasoning-capable`; the live test asserts `status in ("reasoning-capable", "audit-passed")` (`tests/test_adr_0100_0102_sibling_ratifications.py:112-119`), amended when ADR-0124 promoted the domain. The AA-238 pattern, extended to 0101.
- **Continuity:** superseded-cleanly on status (0101 → 0122 deferral → 0123 remap → 0124 promotion, each citing the last). Unreconciled on evidence quality: the declared `fabrication_control` lane inherits `AA-250` (🔴, holdout leaked in plaintext) and `AA-246` (lane CLI path mismatch) — see `AA-460`.
- **Fitness:** cited — the pinning test and `evals/domain_contract_validation/`; also `AA-237`'s record/reality note already covers the ledger-status wording drift.
- **Necessity:** reducible-to-template — third application of the ADR-0097 ratification template; `AA-244` (0100 reducible to 0097 + data row) applies equally here.
- **Findings:** `AA-461`, `AA-460`.

### ADR-0104 — Curriculum-Sourced Teaching Proposals
- **Build:** full — `teaching/from_curriculum.py` (conversion, identity defense, SHA-256 proposal IDs, redacted telemetry), `evals/curriculum_loop_closure/` with `results/v1_dev.json`, `tests/test_curriculum_proposals.py`, CLI wiring at `core/cli_teaching.py:667`.
- **Liveness:** wired-but-unreached downstream — proposals emit and enter review, but per verified `AA-313`/`AA-124` a `PackMutationProposal` has no confirmed path to pack admission, so the "feed the learning loop" consequence is open-circuit; per `AA-308`/`AA-309` the review it enters is not reviewer-identity-gated.
- **Design fidelity:** tension with the sabotage test — hard constraint #4 (replay-equivalence pre-gate) defaults to `NoOpCurriculumReplayChecker` which always passes (`teaching/from_curriculum.py:60,166,224`); with the checker "removed" nothing changes. Identity defense (constraint #3) is genuinely live (`AA-314`).
- **Build fidelity:** matches for constraints #1-#3/#5/#6; #4 is structurally present but decorative at default (the curriculum instance of `AA-310`).
- **Continuity:** clean — extends ADR-0094/0095 as claimed; `AA-318` already records `from_miner.py`/`from_curriculum.py` as near-duplicates (consolidation owned there).
- **Fitness:** cited — `evals/curriculum_loop_closure/results/v1_dev.json` exists; closure lane covers the six claimed cases.
- **Necessity:** reducible — structural sibling of `from_miner.py` by its own admission; one parameterized source-adapter would serve (per `AA-318`).
- **Findings:** `AA-462`, `AA-463`.

### ADR-0108 — Proposed-ADR Sequencing Post-ADR-0105
- **Build:** full at acceptance time (README frontier list landed per the ADR's own acceptance evidence) — but see liveness.
- **Liveness:** dead at HEAD — `docs/adr/README.md` today contains **no** "Current frontier" section and no Proposed-ADR list at all (grep: zero hits for `frontier`/`Proposed`), while **69** ADR files carry `Proposed` status. The `proposed_adr_index_complete` invariant polices nothing; nothing enforces it.
- **Design fidelity:** the decision honored Pillar II when made; its unenforced-invariant shape violates the sabotage test today.
- **Build fidelity:** contradicts at HEAD — the mandated README section was removed (or rewritten away) with no successor ADR, the exact "silent" transition its own `no_silent_withdrawal` invariant forbids for ADRs.
- **Continuity:** unreconciled — no ADR supersedes 0108's README discipline; the sequencing content itself (0106 first, then 0080/0084/0087) was overtaken by events without a re-ranking ADR (0080 later shipped; 0084/0087 audited in B2.4 with `AA-293`/`AA-295`/`AA-298`).
- **Fitness:** value delivered in its window (the 0106→0107 order it set is what happened); none since.
- **Necessity:** irreducible as a governance act; the invariant needed a pin to survive.
- **Findings:** `AA-464`.

---

## Zone B3.2 — Math Parser, Solver & Verifier Core (0115, 0116, 0117, 0118, 0118a, 0122~1, 0123~1, 0126, 0127~1, 0127~2, 0128)

Zone-level liveness fact (applies to every card below, stated once per the rigor tier): the 0115–0118 pipeline is live in eval/capability lanes (`evals/gsm8k_math/`, `evals/gsm8k_parser_dev/`, `core/capability/*`, `evals/obligation_2_ood_ratio/v1/runner.py:27-28`) and consumed by later arcs (`generate/binding_graph/adapter.py`, `generate/structure_mapping/`, `core/reasoning/adapters.py:10-12`), but **nothing in `chat/`, `core/cognition/`, or the CLI serving path imports it** — `chat/runtime.py:3220` explicitly defers "the math-serving seam." (`AA-465`.)

### ADR-0115 — Math Problem Parser and Typed Proposition Graph
- **Build:** full for Phases 1.1–1.3 — schema (`generate/math_problem_graph.py`), 50-case dev set (`evals/gsm8k_parser_dev/cases.jsonl`, 50 lines), parser (`generate/math_parser.py:207` `parse_problem`). Phase 1.4 (runtime binding) never built.
- **Liveness:** live in eval lanes; the promised "first-class runtime input" surface does not exist (zone note).
- **Design fidelity:** pass — frozen dataclasses, construction-time referential integrity, canonical bytes (Pillar II, Axiom 5).
- **Build fidelity:** partial drift — header still reads "Phases 1.2–1.4 In Progress" (2026-05-22) though 1.2/1.3 landed and 1.4 was abandoned to later arcs without amendment.
- **Continuity:** clean upstream (ADR-0114 Phase 1); downstream superseded in role by the candidate-graph parser (0126) and then the 0164 reader, neither of which formally dispositions 0115's Phase 1.4.
- **Fitness:** cited — `tests/test_math_problem_graph.py`; graph schema is the shared IR the rest of the arc verifiably consumes.
- **Necessity:** generalization-candidate — predecessor to `SemanticSymbolicBindingGraph` (ADR-0132 family, Tier A).
- **Findings:** `AA-466` (also `AA-465`, zone).

### ADR-0116 — Deterministic Solver (`MathProblemGraph` → `SolutionTrace`)
- **Build:** full — `generate/math_solver.py`; Obligation #10 provenance real: every step's `pack_lemma_id` resolves from `packs/data/en_arithmetic_v1` at solve time, failing loudly if absent (module doc `generate/math_solver.py:18-21`).
- **Liveness:** live in eval lanes and downstream adapters (`core/reasoning/adapters.py:11`); zone note applies.
- **Design fidelity:** pass — Pillar II (typed refusal on under-determination), Axiom 6 (prose deferred to 0118).
- **Build fidelity:** matches.
- **Continuity:** clean — discharges Obligations #3/#4/#9/#10 as bound by ADR-0114a; the Tier A redo owns re-verifying those obligation auditors themselves.
- **Fitness:** cited — `tests/test_math_solver.py`; wrong=0 preserved across every recorded run of the arc (0121, 0127~1).
- **Necessity:** irreducible within Engine B — but ADR-0139's own table names the Engine A/Engine B split this module embodies; the dual-engine question is ruled at 0139/0249, not here.
- **Findings:** none.

### ADR-0117 — `SolutionTrace` Verifier
- **Build:** full — `generate/math_verifier.py:98` `verify(graph, trace) -> VerifierVerdict`, six named checks as specified.
- **Liveness:** live — invoked by `evals/gsm8k_math/verify.py`/`verify_all.py` and capability auditors; zone note applies.
- **Design fidelity:** pass — Axiom 4 (genuine conjugate of the solver: independent replay, not trust).
- **Build fidelity:** matches (check list in code corresponds 1:1 to the ADR table).
- **Continuity:** clean — extends 0116.
- **Fitness:** cited — `tests/test_math_verifier.py`; the round-trip filter of 0126 reuses it.
- **Necessity:** irreducible — the wrong=0 license leg.
- **Findings:** none.

### ADR-0118 — Stepped Realizer (`SolutionTrace` → Prose)
- **Build:** full — `generate/math_realizer.py`; comparison extensions (0123~1) landed in the same module.
- **Liveness:** live in eval lanes; no chat-path articulation of math traces exists (zone note).
- **Design fidelity:** pass — Pillar II (1:1 step→sentence), Axiom 6.
- **Build fidelity:** matches.
- **Continuity:** clean — extends 0117; heavily extended by the Batch-4 grammar-expansion family (0182–0195) without contradiction.
- **Fitness:** cited — `tests/test_math_realizer.py`.
- **Necessity:** irreducible for the lane; the parser/realizer asymmetry it documents is honest.
- **Findings:** none.

### ADR-0118a — OOD Surface Generator
- **Build:** full — `generate/ood_surface_generator.py`, `tests/test_ood_surface_generator.py`.
- **Liveness:** live in the parser-dev lane (`evals/gsm8k_parser_dev/ood_score.py`) and reused by 0125's suite (`generate/perturbation_suite.py`).
- **Design fidelity:** pass — Axiom 1 honored precisely (graph held constant, surface varied).
- **Build fidelity:** matches.
- **Continuity:** clean — note the current Obligation #2 *auditor* (`core/capability/ood_ratio.py`) is report-reading only; this generator's obligation-discharge role belongs to the lane era before the 0131 rebench. Tier A owns 0114a.2's current-state verdict.
- **Fitness:** cited — deterministic byte-equal variants pinned by tests; OOD ratio 1.00 recorded by 0121.
- **Necessity:** irreducible for its lane; partially overlapped by `perturbation_b3` transforms post-rebench (see `AA-467`).
- **Findings:** none (overlap carried on 0125's card).

### ADR-0122~1 — Parser Expansion: Rate / Per-Unit (substrate-only; lift deferred)
- **Build:** full for the declared substrate — `generate/rate_comprehension/` (model/reader/solver/units/conversion), `tests/test_adr_0122_rate_per_unit.py`.
- **Liveness:** live via later consumers — `core/comprehension_attempt/classify.py:21-22` (practice-loop classification) and `generate/contemplation/pass_manager.py` import it; the deferred sealed-lift never happened under this ADR (by design) and the capability question moved to the 0131/0164 arcs.
- **Design fidelity:** pass — the deferral-is-the-decision pattern honors Pillar II.
- **Build fidelity:** matches — substrate-only status is exactly what shipped.
- **Continuity:** clean — extended (not contradicted) by `generate/combined_rate_comprehension/` in the later arc.
- **Fitness:** cited — downstream reuse is the value evidence; better than the retracted card's "affects rate-specific probes only" (it undersold real consumers).
- **Necessity:** irreducible at the time; candidate for eventual absorption into the 0164 reader's grammar (register there, not here).
- **Findings:** none.

### ADR-0123~1 — Comparison-Phrasing Realizer
- **Build:** full — additive and multiplicative comparison rendering in `generate/math_realizer.py:264,329`, helper at `:107` citing ADR-0123.
- **Liveness:** live when traces carry comparison ops (eval lanes; zone note applies).
- **Design fidelity:** pass — two-clause comparison surface exactly per the substrate contract.
- **Build fidelity:** matches; the in-file disambiguation note against the same-numbered governance ADR is good hygiene.
- **Continuity:** clean — substrate commit lineage (`c9bd5d4`, `en-arith-006/007` lemmas) documented in-file; census records no stale refs here.
- **Fitness:** cited — realizer test suite.
- **Necessity:** irreducible surface increment.
- **Findings:** none.

### ADR-0126 — Candidate-Graph Parser with Round-Trip Verifier-Filter
- **Build:** full despite `Status: Proposed` — `generate/math_candidate_parser.py`, `generate/math_candidate_graph.py`, `generate/math_roundtrip.py` all exist with tests.
- **Liveness:** live — probe substrate for the 0131.G family (Tier A) and consumed by recognizer wiring tests (`tests/test_candidate_graph_recognizer_wiring.py`).
- **Design fidelity:** pass — Axiom 4 (parse forward, verify round-trip back).
- **Build fidelity:** matches the proposal; the status header never flipped (see `AA-468`).
- **Continuity:** clean — honestly documents its Path-A/Path-B decision gate, which 0127~1 then triggered.
- **Fitness:** cited — the 0/50 refusal evidence it produced is what redirected the whole arc; negative results counted.
- **Necessity:** generalization-candidate — superseded in role by the 0164 incremental reader; formal disposition absent.
- **Findings:** `AA-468` (shared).

### ADR-0127~1 — ADR-0127 + ADR-0128 Results (Path-B Triggered)
- **Build / liveness:** n/a-by-kind — a results companion, not a decision record (census `01-adr-census.md` marks it so); the empirical artifacts it reports (train-sample runner, `evals/gsm8k_math/train_sample/v1/`) exist.
- **Design fidelity:** pass — this is Axiom 7 practiced: the parser-by-rule hypothesis was falsified at full substrate (`0/50 correct, 0 wrong, 50 refused`) and recorded rather than tuned away.
- **Build fidelity:** matches — the claims (packs wired, wrong=0 preserved, deterministic re-runs) are consistent with the tree state verified above.
- **Continuity:** clean — explicitly composes with the 0129/0130 backlog (§"Composition with deferred backlog") and hands off to the 0131 rebench, which cites it.
- **Fitness:** high — this document is the pivot evidence for the entire math arc's retargeting.
- **Necessity:** irreducible as evidence; its non-ADR format inside the ADR namespace is a census-documented numbering accident, not a defect to re-raise.
- **Findings:** contributes to `AA-469` (positive chain).

### ADR-0127~2 — `en_units_v1` Pack + Units-Aware Candidate Extractors
- **Build:** full — `packs/data/en_units_v1/` (manifest, lexicon, glosses, conversions).
- **Liveness:** live — consumed by `generate/math_parser.py`, `generate/math_candidate_parser.py`, `generate/binding_graph/units.py`, `packs/unit_dimensions.py`, `evals/dimensional/oracle.py`; it outlived the hypothesis it was built to test.
- **Design fidelity:** pass — Pillar II (units externalized to curated pack data, not code tables).
- **Build fidelity:** matches; status header still `Proposed (scope-only)` while the pack is built and load-bearing (`AA-468`).
- **Continuity:** clean — its exit criterion fired honestly as Path-B (0127~1).
- **Fitness:** cited — downstream consumer breadth is the strongest fitness evidence in this zone.
- **Necessity:** irreducible — the units substrate is what every later comprehension arc reads.
- **Findings:** `AA-468` (shared).

### ADR-0128 — `en_numerics_v1` Pack
- **Build:** full — `packs/data/en_numerics_v1/` (manifest, lexicon, glosses, mastery report) plus generator script (`scripts/generate_en_numerics_v1.py`) and loader (`packs/numerics_loader.py`).
- **Liveness:** live — consumed by `generate/math_parser.py` era modules and `generate/math_completeness.py`, `packs/scalar_equivalence.py`.
- **Design fidelity / build fidelity:** pass / matches (status header drift shared with siblings, `AA-468`).
- **Continuity:** clean — joint exit gate with 0127 honored; jointly falsified into Path-B without either pack being discarded.
- **Fitness:** cited — pack compiler validation; mastery report artifact present.
- **Necessity:** irreducible — English numeric-form substrate.
- **Findings:** `AA-468` (shared).

---

## Zone B3.3 — Capability Ledger Deferrals & Remaps (0120~1, 0120~2, 0120~3, 0121, 0122~2, 0123~2, 0123a, 0124, 0125; + deferred proposals 0129, 0130)

### ADR-0120~1 — First `expert` Promotion Contract
- **Build:** full — the contract is enforced by `core/capability/reporting.py:37-46` (`_EXPERT_DOMAIN_STATUSES` topped by `expert`, `_EXPERT_COMPOSERS` per-domain) + `core/capability/expert_promotion_math.py` (13-check composition). The retracted card's `core/capability/expert_contract.py` citation is fabricated — no such file.
- **Liveness:** live — the contract has evaluated a real promotion, admitted it, and later auto-refused it on digest drift (0120~2's addendum); the sabotage test passes with distinction.
- **Design fidelity:** pass — Pillar II throughout (falsifiable-in-advance gates); one tension: the contract text asserts "**all ten ADR-0114a obligations are now discharged on main**," which verified `AA-250` (🔴) contradicts for Obligation #1's sealed-holdout exemplar. See `AA-470`.
- **Build fidelity:** matches — the composition (10 obligations + 3 gates + signature) is what the composer computes.
- **Continuity:** unreconciled on the AA-250 point; otherwise clean (revised for math by 0131.4, consumed by 0120~2/~3).
- **Fitness:** cited — the 0121 refusal and the 0200-era auto-revert are both the contract demonstrably working.
- **Necessity:** irreducible — the top-tier claim gate.
- **Findings:** `AA-471`, `AA-470`.

### ADR-0120~2 — Mathematics-Logic Promoted to `expert` (ledger flip)
- **Build:** full — status ladder wiring, digest-stability fix, signed claim (`evals/math_expert_claims/v1/expert_claims_math_v1_signed.json`).
- **Liveness:** live-and-refusing — composer currently refuses with `claim_digest mismatch — registry has '4c46f530…', evidence-derived digest is '02f6d3c8…'` (`expert_claims_math_v1_signed.json:81-83`); current ledger status `audit-passed`, exactly as the in-file reconciliation note states.
- **Design fidelity:** pass — Axiom 4/7: the flip carried its own conjugate (auto-revert on evidence drift) and it fired.
- **Build fidelity:** matches, including the historical block preserved as history.
- **Continuity:** superseded-cleanly — the ADR-0200 reconciliation note (2026-06-02) is written **into this file**, the strongest continuity hygiene in the batch.
- **Fitness:** cited — fail-closed property empirically demonstrated at HEAD.
- **Necessity:** irreducible — first worked instance of the expert tier.
- **Findings:** `AA-472` (positive).

### ADR-0120~3 — Math-Expert Promotion Composer Wire-Up
- **Build:** full — `core/capability/expert_promotion_math.py` (docstring self-identifies as this ADR's artifact); emits the canonical signed-claim artifact; repo-relative evidence pointers per the digest-stability decision.
- **Liveness:** live — `core capability math-expert-promote` CLI (`core/cli_capability.py:385-406`) and the ledger's expert predicate consume it.
- **Design fidelity:** pass — pure function over committed evidence; verdict, not side effect.
- **Build fidelity:** matches (the retracted card audited the wrong module — see header correction #2).
- **Continuity:** clean — explicitly contract-only-consumer of 0120~1 and producer for 0120~2.
- **Fitness:** cited — `evals/math_expert_claims/v1/` artifacts exist and carry the live refusal.
- **Necessity:** irreducible — the composition point the contract requires.
- **Findings:** none.

### ADR-0121 — `mathematics_logic` `expert` Promotion — Deferred (first attempt)
- **Build:** full — the deferral record matches the machine state it describes (contract floor 0.60; sealed `correct_rate = 0.0`, 0/1319; wrong = 0 preserved).
- **Liveness:** live as governance — the ledger did not flip on this attempt; the named blocker drove the entire 0122~1→0128 arc and then the rebench.
- **Design fidelity:** pass — the honest-deferral doctrine at its best; one inherited tension: its "10 of 10 obligations pass" premise carries the same `AA-250` contradiction as 0120~1 (`AA-470` covers both).
- **Build fidelity:** matches.
- **Continuity:** clean — pattern-cites 0107/0110 and 0122~2/0124 accurately.
- **Fitness:** cited — the deferral's named blocker was falsifiable and was in fact acted on.
- **Necessity:** irreducible evidence artifact.
- **Findings:** shares `AA-470`; contributes to `AA-469` (positive chain).

### ADR-0122~2 — `systems_software` Audit-Passed Promotion: Deferred
- **Build/liveness:** full/lived — deferral recorded; ledger stayed at `reasoning-capable` until 0124.
- **Design fidelity:** pass — refused on a mechanical lane-shape mismatch rather than papering over it.
- **Build fidelity:** matches — the mismatch it reports (`symbolic_logic` emits inference-style metrics, accuracy-shape checker fails closed) is exactly what 0123~2 then fixed in `expert_demo.py`.
- **Continuity:** superseded-cleanly by 0124 (which cites the full 0101→0122→0123→0124 arc).
- **Fitness:** cited — the deferral caught a real registry bug; that is the mechanism's value.
- **Necessity:** irreducible as a decision record.
- **Findings:** contributes to `AA-469` (positive chain).

### ADR-0123~2 — `symbolic_logic` Lane-Shape Remap (ADR-0109 Amendment)
- **Build:** full — `LANE_SHAPE_REGISTRY["symbolic_logic"] = "inference_shape"` live at `core/capability/expert_demo.py:61`.
- **Liveness:** live — every `symbolic_logic` gate evaluation flows through it.
- **Design fidelity:** pass — corrects a semantic mis-mapping in favor of what the lane actually measures (Pillar II).
- **Build fidelity:** matches.
- **Continuity:** clean as an amendment chain (0109 → 0123~2 → 0123a). Document defect: the body's citations are machine-local `file:///Users/kaizenpro/.gemini/antigravity/worktrees/...` URIs (census `stale-references.jsonl:1135-1136`) — unusable to any other reader or tool.
- **Fitness:** cited — unblocked 0124.
- **Necessity:** irreducible one-line registry fix.
- **Findings:** `AA-473`.

### ADR-0123a — `all_three_pass_rate` Synonym in `inference_shape`
- **Build:** full — synonym fallback at `core/capability/expert_demo.py:117-119`.
- **Liveness:** live in every inference-shape check.
- **Design fidelity:** pass, with a note — a metric synonym is exactly the Pillar-II hazard the ADR mitigates by codifying precedence; the code implements the stated precedence (primary key wins; fallback only when absent).
- **Build fidelity:** matches.
- **Continuity:** clean — documents a widening that ADR-0124's PR had already shipped, honestly labeled as post-hoc codification.
- **Fitness:** cited — gate passes on the real payload key.
- **Necessity:** reducible in principle (renaming the lane's emitted key would have removed the synonym); the ADR chose the compatible path and says so.
- **Findings:** none.

### ADR-0124 — `systems_software` Audit-Passed Promotion
- **Build:** full — promotion recorded; evidence table matches the lane machinery verified above; ledger floor test amended accordingly (see 0101 card).
- **Liveness:** live — `systems_software` reports `audit-passed` through `reporting.py`'s predicate chain.
- **Design fidelity:** tension — the ADR itself documents that `inference_closure`/`fabrication_control` evidence is **shared across all domains**, digest-distinguished only by `domain_id` + revision; that is the mechanism behind verified `AA-248` (🔴, identical fingerprint on vocabulary-disjoint domains) and `AA-262` (single 9-case corpus as 4 domains' negative control).
- **Build fidelity:** matches.
- **Continuity:** unreconciled on evidence quality — the promotion's `fabrication_control` holdout leg inherits `AA-250` (leaked holdout) with no note here or in a successor; otherwise a clean arc closure.
- **Fitness:** cited — third promotion, arc documented end-to-end.
- **Necessity:** irreducible as a ledger decision.
- **Findings:** `AA-474`.

### ADR-0125 — Reasoning-Isolation Perturbation Suite
- **Build:** full — `generate/perturbation_suite.py` (7 transforms as tabled), `evals/gsm8k_parser_dev/perturbation_score.py`, `tests/test_perturbation_suite.py`.
- **Liveness:** live in the parser-dev lane; **not** the live Obligation #5 discharge path — the current expert composer validates Obligation #5 via `core/capability/perturbation_b3.py` (`expert_promotion_math.py:46,239-251`), the B3-surface suite from the Tier A 0114a.5 arc.
- **Design fidelity:** pass — invariance-preserving vs invariance-breaking split is the right sabotage-shaped design; correctly declines to duplicate 0118a's `scale_numbers_by_k`.
- **Build fidelity:** matches.
- **Continuity:** clean upstream; post-rebench role never re-stated.
- **Fitness:** cited — deterministic, test-pinned.
- **Necessity:** reducible-to-perturbation_b3 going forward — two perturbation implementations now discharge one obligation across two eras; consolidation candidate.
- **Findings:** `AA-467`.

### Deferred teaching-loop proposals (omitted by the retracted map)

#### ADR-0129 — Spaced Reviewed-Correction Replay (Deferred Proposal)
- **Build:** ghost by design — Proposed-Deferred; no replay scheduler exists in `teaching/` (correct per status).
- **Liveness:** dead (as declared). Adjacent verified evidence agrees the gap is real: `AA-278` (`ChatRuntime.correct()` has no production call site) means even un-spaced correction replay lacks a production entry point.
- **Design fidelity:** pass — unusually well-argued scope discipline (claims retention, explicitly disclaims far-transfer).
- **Build fidelity:** matches (nothing built, nothing claimed built) — except both context citations: the session doc is `docs/sessions/2026-05-23-pedagogy-research-and-teaching-loop-pivot.md`, not the cited `docs/sessions/SESSION-2026-05-23-…`; and a local `/Users/kaizenpro/Downloads/…` path is cited as a source.
- **Continuity:** monitored, not silent — 0127~1 §"Composition with deferred backlog" and ADR-0131:284-290 both re-acknowledge it; but the un-deferral trigger (Path-A/B resolution) fired 2026-05-23 and no revisit has occurred in 2 months.
- **Fitness:** none yet (by construction).
- **Necessity:** irreducible if built (no other cadence mechanism exists); overlaps the contemplation/practice loops' territory — a future ruling should sequence them.
- **Findings:** `AA-475`, `AA-476` (shared with 0130).

#### ADR-0130 — Pre-Articulation Calibration Logging (Deferred Proposal)
- **Build:** ghost by design — Proposed-Deferred; no prediction/calibration events exist in the teaching subsystem.
- **Liveness:** dead (as declared).
- **Design fidelity:** pass — the prediction-outcome-gap mechanism is deterministic and honestly framed as measurement, not self-report.
- **Build fidelity:** matches; same wrong `SESSION-` filename citation as 0129.
- **Continuity:** same monitored-deferral state as 0129 (`AA-476`).
- **Fitness:** none yet.
- **Necessity:** irreducible if built; nearest live relative is the turn-loop verdict layer (ADR-0035), which records outcomes but no pre-correction predictions.
- **Findings:** shares `AA-475`, `AA-476`.

---

## Zone B3.4 — Epistemic State & Multi-Resolution Recognition (0142, 0143, 0144, 0145, 0148, 0149)

### ADR-0142 — Epistemic State Taxonomy
- **Build:** full — `core/epistemic_state.py:54` `EpistemicState` enum plus `NormativeClearance`; provenance phases staged as declared.
- **Liveness:** live — consumed across `vault/store.py`, `chat/runtime.py`, `core/response_governance/policy.py`, `core/epistemic_disclosure/`, `workbench/schemas.py` and more; this vocabulary genuinely escaped its ADR.
- **Design fidelity:** pass — Pillar II made structural; the later binding ownership note (`docs/adr/epistemic-taxonomy-ownership-stage3.md`) protects the three-axis separation.
- **Build fidelity:** matches with one counting defect — the ADR ratifies "the following **14-state** epistemic vocabulary" over a table of **15** states, and the enum ships 15 (`PERCEIVED`…`EPISTEMIC_STATE_NEEDED`, `core/epistemic_state.py:54-69`).
- **Continuity:** clean — integration honestly gated on 0144 and delivered there.
- **Fitness:** cited — `tests/test_epistemic_invariants.py`, phase-tagged test files, live consumers.
- **Necessity:** irreducible — the taxonomy is the zone's foundation.
- **Findings:** `AA-477`.

### ADR-0143 — Structural Recognition via Multi-Resolution Anti-Unification
- **Build:** full — `recognition/anti_unifier.py` (`DerivedRecognizer`, `recognize`), `recognition/outcome.py`, registry, tests (`tests/test_recognition_phase1.py`).
- **Liveness:** wired-but-unreached in production — reachable only through the pipeline attachment that `recognition_grounded_graph=False` disables (see `AA-478`).
- **Design fidelity:** pass — deterministic, introspectable, teaching-derived; exactly the anti-regex thesis it argues.
- **Build fidelity:** matches the output contract.
- **Continuity:** clean — 0144 delivered the promised integration gate; ADR-0154 (Batch 4) continues the producer side.
- **Fitness:** cited — 8/8 spike tests noted by 0144 and present in tree; no production fitness evidence can exist while dark.
- **Necessity:** irreducible as mechanism; its liveness is a policy decision no record justifies (flag register: "*no criterion recorded*").
- **Findings:** shares `AA-478`.

### ADR-0144 — Epistemic Carrier and Recognition Integration Gate
- **Build:** full — two-graph decision implemented exactly: planner keeps `generate/graph_planner.py::PropositionGraph`, carrier is `recognition/carrier.py::EpistemicGraph` (ADR §Q1; `core/cognition/pipeline.py:45-48` imports both sides), step 0b recognition in `pipeline.py:208-211`.
- **Liveness:** wired-but-unreached — double-gated: recognizer attachment returns `None` when the flag is off (`chat/runtime.py:1274-1277`) and grounded-graph consumption checks the flag again (`pipeline.py:307`); default `False` (`core/config.py:251`).
- **Design fidelity:** pass — resolving the name collision instead of overloading it is Pillar II done right.
- **Build fidelity:** matches.
- **Continuity:** clean — discharges 0142's and 0143's deferrals as promised.
- **Fitness:** cited — `tests/test_epistemic_carrier.py`, wiring tests; dark at default (sabotage-identical in shipped profiles).
- **Necessity:** irreducible carrier; the flag posture is the issue, not the design.
- **Findings:** shares `AA-478`.

### ADR-0145 — Energy-Modulated Vault Surface Readback
- **Build:** full — `energy_modulated_surface` (`generate/realizer.py:39`), prefix table byte-identical to the ADR (`realizer.py:31-33`), `_recall_energy_class_from_hits` (`chat/runtime.py:240`).
- **Liveness:** live — wired unconditionally on the serving path (`chat/runtime.py:2685,3143-3150`); the one un-flagged, production-reached mechanism in this zone.
- **Design fidelity:** pass — closes a real ADR-0006 spec violation (energy stamped but never surfaced).
- **Build fidelity:** matches exactly.
- **Continuity:** clean — cites ADR-0006/W-004 accurately; unaffected by `AA-16`'s valence-scalar bug (different seam: this path reads `energy_class` strings from vault hits, not `_energy_scalar`).
- **Fitness:** cited — deterministic prefix behavior; consumed on every recall-grounded turn.
- **Necessity:** irreducible — the articulated form of the energy taxonomy.
- **Findings:** none.

### ADR-0148 — Wire VaultPromotionPolicy into Turn Boundary
- **Build:** full — flag (`core/config.py:270`), energy metadata persisted at store time, promotion scan at both turn-boundary sites (`chat/runtime.py:2742,2957`), `vault/store.py:361` `promote_eligible_entries`.
- **Liveness:** wired-but-unreached — `vault_promotion_enabled=False` and **not** in `CONTINUOUS_LIFE_CONFIG_FLAGS` (`chat/always_on_daemon.py:60-65`); so the W-007 unlock it exists for (COHERENT entries as recognition anchors) never occurs in any shipped profile, compounding `AA-478`.
- **Design fidelity:** pass on the null-drop discipline; tension with the sabotage test in shipped reality.
- **Build fidelity:** matches.
- **Continuity:** notable — this ADR gives ADR-0014's `VaultPromotionPolicy` (`core/physics/learning.py:17`) its first callers ever, yet neither it nor any successor cites/resolves ADR-0014's "Accepted (Stub)" disposition that verified `AA-124`/`AA-125` flagged for ruling.
- **Fitness:** cited — unit tests; no production evidence possible while dark.
- **Necessity:** irreducible bridge from energy physics to recognition evidence — if ever enabled.
- **Findings:** `AA-479`; shares `AA-478`.

### ADR-0149 — Integrate DerivedRecognizer into CognitiveTurnPipeline
- **Build:** full — `first_admitted_recognizer()` gate (`chat/runtime.py:1274-1277`), pipeline attachment (`pipeline.py:126-139`), `record_recognition_example` + derive-at-checkpoint path; `tests/test_adr_0149_recognizer_pipeline_wiring.py`.
- **Liveness:** wired-but-unreached — the flag-off path is byte-identical by design and is the only path any shipped profile takes.
- **Design fidelity:** pass — deterministic insertion-order admission, explicit-recognizer precedence.
- **Build fidelity:** matches the ADR precisely.
- **Continuity:** clean — completes the 0143→0144→0146→0148 chain it enumerates; ADR-0154 extends it.
- **Fitness:** cited — wiring tests; production value zero while dark.
- **Necessity:** irreducible wiring for the arc; the arc-wide darkness is the finding.
- **Findings:** anchor of `AA-478`.

---

## Zone B3.5 — Versor Arithmetic Spikes & Trace Protocol (0138, 0139, 0140~1, 0140~2, 0141)

### ADR-0138 — Comparative-Reference Layer
- **Build:** ghost — design-only Draft by its own label; no `fraction_operand`/`compound_comparative` implementation exists in `generate/` and no code cites it.
- **Liveness:** dead.
- **Design fidelity:** pass as analysis — the shared-deep-structure observation over the S.x barrier data is sound.
- **Build fidelity:** n/a (nothing claimed built).
- **Continuity:** orphaned — zero citations from any later ADR (grep across `docs/adr/`), and its parent corridor (ADR-0136 family) was superseded by ADR-0164 (verified `AA-342`); its targets were absorbed by the reader arc without disposition of this Draft.
- **Fitness:** none found.
- **Necessity:** moot at HEAD — needs a Withdrawn/Superseded ruling, not implementation.
- **Findings:** `AA-480`.

### ADR-0139 — Arithmetic-as-Versor Spike: `add` Only
- **Build:** ghost at HEAD — the claimed artifacts `tests/test_arithmetic_as_versor_add.py` ("passes", §line 121) and `generate/math_versor_arithmetic.py` do **not** exist (verified; census `stale-references.jsonl:521-527`).
- **Liveness:** dead as-authored; the construction itself (`T_t = 1 − ½·t·n_inf` exact closure) is alive elsewhere — see continuity.
- **Design fidelity:** pass as intent — the Engine A/Engine B table is the clearest statement of the dual-engine problem in the corpus (Axiom 1/7 argument done right).
- **Build fidelity:** contradicts — a Draft asserting a passing test module that is not in the tree is record/reality divergence (Standing Philosophy #5), even at Draft status.
- **Continuity:** unreconciled absorption — ADR-0249's `core/physics/quantity_kernel.py` implements the same translator (and more) from its own 2026-07-18 spike docs, citing neither this ADR nor its siblings anywhere in code, ADR text, or research notes (grepped all three).
- **Fitness:** indirect only — the idea won; the record lost the thread.
- **Necessity:** superseded-by-0249 — consolidation/disposition candidate, not an implementation gap.
- **Findings:** `AA-458`, `AA-459`.

### ADR-0140~1 — CORE Trace Protocol v0
- **Build:** full despite `Status: Proposed` — `core/protocol/` (envelope, events, canonical, replay, jsonl, types) implements the typed/canonical/content-addressed/causally-linked envelope as specified (`core/protocol/envelope.py`: allowed kinds, payload encodings, required turn fields).
- **Liveness:** live in bounded scope — consumed by `core/ports/`, `demos/amr_decision_substrate/`, and `tests/test_core_trace_protocol.py`; **not** wired into `ChatRuntime`, exactly matching its stated non-goal.
- **Design fidelity:** pass — Pillar III posture (native protocol, adapters at the boundary) and Axiom 5 (content-addressed canonical events).
- **Build fidelity:** matches the spec; only the status header lags the tree.
- **Continuity:** clean — ADR-0153's turn-event backstamp (Batch 4) builds adjacent without contradiction; VMP remains an explicitly-deferred payload encoding.
- **Fitness:** cited — protocol test suite; demo consumer.
- **Necessity:** irreducible if the ledger vision proceeds; currently a substrate awaiting its runtime integration ADR.
- **Findings:** `AA-481`.

### ADR-0140~2 — `subtract` as Inverse Translator + Additive Group Closure
- **Build:** ghost at HEAD — claimed `tests/test_arithmetic_subtract_and_group.py` and the `generate/math_versor_arithmetic.py` extension absent (verified; census flags both).
- **Liveness:** dead as-authored; additive-group transport exists in `quantity_kernel.py` (ADR-0249).
- **Design fidelity:** pass as intent — the "the group was already there; we are decoding it" framing is the thesis applied correctly.
- **Build fidelity:** contradicts — same claimed-passing-test defect as 0139.
- **Continuity:** same unreconciled absorption into ADR-0249 (`AA-459`).
- **Fitness:** none found in-record.
- **Necessity:** superseded-by-0249; disposition needed.
- **Findings:** shares `AA-458`, `AA-459`.

### ADR-0141 — `multiply` as Dilator (Positive Non-Zero Only)
- **Build:** ghost at HEAD — claimed `tests/test_arithmetic_multiply_as_dilator.py` and module extension absent (verified; census flags both).
- **Liveness:** dead as-authored; the dilator-with-projective-decode construction is precisely what `quantity_kernel.py` ships (its docstring: `D_α = exp(+½ α·e4e5)`, conformal weight, projective decode).
- **Design fidelity:** pass as intent — the narrow-scope argument (dilation ≠ translation; closure must be re-derived) is correct and is what 0249 in fact re-derived.
- **Build fidelity:** contradicts — same defect class as siblings.
- **Continuity:** same unreconciled absorption (`AA-459`).
- **Fitness:** none found in-record.
- **Necessity:** superseded-by-0249; disposition needed.
- **Findings:** shares `AA-458`, `AA-459`.

---

## Zone B3.6 — Engine-State Persistence & Autonomous Contemplation (0146, 0150)

### ADR-0146 — L10 Shape B Hybrid Engine-State Persistence
- **Build:** full — `checkpoint_engine_state` (`chat/runtime.py:918`) called at the turn boundary via `_checkpointed_response`; engine-state dir, manifest revision check, `DerivedRecognizer`/`DiscoveryCandidate` round-trip as specified.
- **Liveness:** live — the checkpoint path runs unconditionally at turn boundaries; the continuous-life daemon (`chat/always_on_daemon.py`) runs over it with `persist_session_state` forced on.
- **Design fidelity:** pass — Shape B's O(checkpoint) argument honored; recovery-not-control-flow posture maintained (warn-and-continue on revision mismatch, later hardened by 0157's opt-in strict guard).
- **Build fidelity:** matches, including the scope sentence corrected by addendum.
- **Continuity:** exemplary — the in-file **R-12a addendum (2026-07-28)** reconciles the Shape-A rejection with the shipped daemon, table-mapping each formerly-out-of-scope item to its implementation, explicitly to kill the H-8 mechanism. Model for the corpus.
- **Fitness:** cited — daemon runs over it in production profile; checkpoint/restore pinned by tests (Batch 4's 0156 extends atomically).
- **Necessity:** irreducible — the persistence spine of L10.
- **Findings:** `AA-482` (positive).

### ADR-0150 — Autonomous Inter-Session Contemplation
- **Build:** full — enrichment-at-checkpoint wired at `chat/runtime.py:930` inside `checkpoint_engine_state`; `contemplate()` (`generate/contemplation/pass_manager.py:353`) is the ADR-0056 pure function as claimed.
- **Liveness:** wired-but-unreached in every shipped profile — `auto_contemplate=False` (`core/config.py`) and **absent from `CONTINUOUS_LIFE_CONFIG_FLAGS`** (`chat/always_on_daemon.py:60-65`); the flag register lists it in §3c with no forced-ON marker. The continuous-life daemon therefore persists exactly the **unenriched** candidates this ADR exists to prevent.
- **Design fidelity:** pass on trust boundary (read-only enrichment, checkpoint-not-inline latency argument); the title's "Autonomous" fails the sabotage test at HEAD.
- **Build fidelity:** matches the mechanism; the deployment posture contradicts the title's promise.
- **Continuity:** clean upstream (ADR-0056 Phase C1 activation); `AA-286`'s parallel-contemplation-implementations finding (0056 vs 0080) is the adjacent unresolved seam. Downstream, its W-017 unlock (auto-proposal filtering on enriched fields) is a Batch-4 concern — flagged for the Batch-4 redo: with candidates unenriched, ADR-0151's polarity/evidence filters may be selecting over empty attributes (the daemon's own F-6 "consolidating an empty set" failure pattern, one layer up).
- **Fitness:** none in production; `evals/contemplation_quality/` and the CI runner (ADR-0155, Batch 4) exercise contemplation out-of-process.
- **Necessity:** irreducible if the always-on life is to self-enrich; currently a policy gap, not a mechanism gap.
- **Findings:** `AA-483`.

---

## Findings rollup (final corpus IDs)

| ID | Sev | Finding (one line, citations above) |
|---|---|---|
| AA-464 | 🟡 | ADR-0108's `proposed_adr_index_complete` invariant is dead: `docs/adr/README.md` carries no frontier/Proposed list while 69 ADRs sit at `Proposed`; the mandated section vanished with no successor — its own `no_silent_withdrawal` discipline violated against itself. |
| AA-462 | 🟡 | ADR-0104 hard constraint #4 / `curriculum_proposal_replay_equivalence` is decorative at default: `NoOpCurriculumReplayChecker` always passes (`teaching/from_curriculum.py:60,166,224`) — curriculum-path instance of `AA-310`. |
| AA-463 | 🟢 | ADR-0104's "feed the learning loop" consequence is open-circuit downstream per verified `AA-313`/`AA-124` (no proposal→pack-admission path) and un-gated per `AA-308`/`AA-309`; engagement, not re-derivation. |
| AA-461 | 🟢 | ADR-0101 acceptance evidence still says the test pins `reasoning-capable`; live test asserts a floor `in ("reasoning-capable","audit-passed")` (`tests/test_adr_0100_0102_sibling_ratifications.py:112-119`) — `AA-238` pattern extended to 0101. |
| AA-460 | 🟡 | ADR-0101's `fabrication_control` evidence lane (declared with a `holdout` split) inherits `AA-250` (🔴 leaked holdout) and `AA-246` (broken lane CLI); the ratification's negative-control leg is weaker than asserted, unnoted in the ADR or successors. |
| AA-466 | 🟡 | ADR-0115 header "Phases 1.2–1.4 In Progress" is stale: 1.2 (50 cases) and 1.3 (`generate/math_parser.py:207`) landed; 1.4 runtime binding was abandoned (`chat/runtime.py:3220` "math-serving seam … deferred") with no amendment. |
| AA-465 | 🟢 | Zone fact: the whole 0115–0118 pipeline is eval/capability-lane-only; no `chat/`/`core/cognition/`/CLI serving path imports it — ADR-0114's "first-class runtime input" promise transferred to later arcs without a record. |
| AA-468 | 🟢 | ADR-0126/0127~2/0128 all remain `Status: Proposed` while fully built, tested, and load-bearing at HEAD (`math_candidate_parser.py`; `en_units_v1`/`en_numerics_v1` consumed by parser, binding graph, loaders) — `AA-295` status-drift class ×3. |
| AA-467 | 🔵 | Two perturbation suites now exist for one obligation: ADR-0125's `generate/perturbation_suite.py` (retired parser-dev lane) vs `core/capability/perturbation_b3.py`, which is what the live composer validates (`expert_promotion_math.py:46,239`) — consolidate or disposition 0125's suite. |
| AA-469 | 🟢 | Positive counter-instance: 0121 / 0122~2 / 0127~1 form a verified honest-refusal chain — deferrals match machine state, negative results recorded verbatim, each acted on by a real successor (0123~2 fix; 0131 rebench). |
| AA-471 | 🟡 | ADR-0120~1, the governing expert contract, still reads `Status: Proposed` while enforced in production (`reporting.py:37-46`, `_EXPERT_COMPOSERS`; composer live) and having already admitted and auto-reverted a domain. |
| AA-470 | 🟡 | ADR-0120~1 and ADR-0121 both embed "all ten ADR-0114a obligations discharged," contradicted by verified `AA-250` (🔴): Obligation #1's sealed-holdout exemplar (ADR-0119.1) is leaked in plaintext at HEAD; no reconciliation in either ADR or successors. (The contradiction the retracted attempt missed; auditors themselves are Tier A redo scope.) |
| AA-472 | 🟢 | Positive: ADR-0120~2's in-file ADR-0200 reconciliation is accurate at HEAD — composer refuses on digest mismatch `4c46f530… ≠ 02f6d3c8…` (`expert_claims_math_v1_signed.json:81-83`); fail-closed demonstrated, record matches reality. |
| AA-473 | 🟢 | ADR-0123~2's body citations are machine-local `file:///Users/kaizenpro/.gemini/antigravity/worktrees/...` URIs (census `stale-references.jsonl:1135-1136`) — unusable to any other reader; content otherwise verified correct (`expert_demo.py:61`). |
| AA-474 | 🟡 | ADR-0124's promotion evidence self-documents domain-shared `inference_closure`/`fabrication_control` results distinguished only by digest metadata — the mechanism behind verified `AA-248` 🔴/`AA-262` — and its `fabrication_control` holdout leg inherits `AA-250`'s leak, unnoted. |
| AA-475 | 🟢 | ADR-0129 and ADR-0130 both cite `docs/sessions/SESSION-2026-05-23-pedagogy-…`; the file is `docs/sessions/2026-05-23-pedagogy-…` (no prefix); 0129 also cites a `/Users/…/Downloads/` path as a source. |
| AA-476 | 🟢 | 0129/0130's un-deferral trigger (Path-A/B resolution) fired the day they were written (0127~1 §backlog) and was re-acknowledged by ADR-0131:284-290, yet both remain `Proposed — Deferred` two months on — monitored, but with no revisit scheduled. |
| AA-477 | 🟢 | ADR-0142 ratifies a "14-state" vocabulary over a 15-row table; the shipped enum has 15 members (`core/epistemic_state.py:54-69`) — the ratifying count is wrong (identity, not value). |
| AA-478 | 🟡 | The 0143/0144/0148/0149 recognition arc is dark in every shipped profile: `recognition_grounded_graph=False` (`core/config.py:251`; `chat/runtime.py:1274-1277` returns `None` when off; `pipeline.py:307` double-gates), `vault_promotion_enabled=False` (`core/config.py:270`), neither in `CONTINUOUS_LIFE_CONFIG_FLAGS` (`always_on_daemon.py:60-65`); flag register lists `recognition_grounded_graph` under "accumulated hesitancy," "*no criterion recorded*" (`docs/specs/flag_register.md:87`). Re-establishes voided AA-346/347 with citations; extends `AA-299`'s pattern. |
| AA-479 | 🟢 | ADR-0148 gives ADR-0014's `VaultPromotionPolicy` its first callers (`chat/runtime.py:2742,2957`) without citing or resolving ADR-0014's "Accepted (Stub)" status; the ruling verified `AA-125` requests should account for this partial revival. |
| AA-458 | 🟡 | ADR-0139/0140~2/0141 each assert a passing test module (`tests/test_arithmetic_as_versor_add.py`, `…_subtract_and_group.py`, `…_multiply_as_dilator.py`) and a `generate/math_versor_arithmetic.py` that do not exist at HEAD (verified; census `stale-references.jsonl:521-527` +0140/0141 entries) — Draft-status docs claiming green artifacts absent from the tree. |
| AA-459 | 🔵 | The spikes' translator/dilator constructions were re-derived and productionized by ADR-0249's `core/physics/quantity_kernel.py` (same `T_a`, dilator with projective decode) with zero citation of 0139–0141 in code, ADR-0249, or its research notes — mark the three Drafts superseded/withdrawn and link the lineage. |
| AA-480 | 🟢 | ADR-0138 is an orphaned design-only Draft: no code, no later citations, parent corridor superseded by ADR-0164 (`AA-342`); needs a disposition ruling, not implementation. |
| AA-481 | 🟢 | ADR-0140~1 (CTP v0) is implemented (`core/protocol/` consumed by `core/ports/`, demos, `tests/test_core_trace_protocol.py`) while the header still reads `Proposed`; runtime non-integration matches its stated non-goal — status drift only (`AA-295` class). |
| AA-483 | 🟡 | ADR-0150's "Autonomous" contemplation is not autonomous anywhere shipped: `auto_contemplate=False` and excluded from the continuous-life profile, so the daemon persists exactly the unenriched candidates the ADR exists to prevent; flags the W-017 coupling for the Batch-4 redo (0151's filters may select over empty enrichment fields). |
| AA-482 | 🟢 | Positive: ADR-0146's R-12a addendum (2026-07-28) reconciles the shipped daemon with the Shape-A rejection in-file, item-by-item — the corpus's model for keeping a ratified record from contradicting running code. |

## Severity tally

**26 findings over 38 ADRs:** 🔴 Block **0** · 🟡 Repair **10** (AA-464, -2, -5, -6, -11, -12, -15, -19, -21, -25) · 🔵 Consolidate **2** (AA-467, -22) · 🟢 Monitor **14** (four of them positive counter-instances: -10, -13, -26, and the clean 0145/0146 cards).

**Why zero new 🔴, stated for the record (per the retraction's re-check requirement):** the block-grade defects in Batch 3 territory are already registered by verified Batch-2 work (`AA-250` leaked holdout, `AA-248` domain-indistinct fingerprint) and are engaged as carry-forwards on four cards here (0101, 0120~1, 0121, 0124) rather than re-registered — the register's own convention (the `AA-75` 🔴 anchors; dependents carry 🟡). Nothing in this Tier B slice independently makes a false capability claim on a live serving path at HEAD: the two closest candidates — the dark recognition arc and the enforced-but-`Proposed` expert contract — are 🟡 by the register's established precedent for flag-accumulation (`AA-299`) and status drift (`AA-295`). The Tier A redo owns re-verdicting 0114a/0119/0131, where Batch 3's real 🔴 exposure lives.
