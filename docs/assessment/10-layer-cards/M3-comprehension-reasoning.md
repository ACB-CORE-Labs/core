# M3 — Comprehension & Reasoning

**Kind:** layer · **Parent:** CORE · **Assessor:** Opus 5 (Phase 2)
**Verified at:** `8927c563` (2026-07-27)
**Liveness:** `partial-wiring-debt` · **Fitness:** `strained` (with one `superseded-in-place` sub-region) · **Topology role:** runtime boundary

> The wiring that thinks. Per the governing mental model — the field is electricity, the intelligence is in the wiring — M3 is where CORE's intelligence actually lives. It takes what M2 admitted and what M1 knows, and produces a decided proposition: what is the case, what follows, what cannot be determined. Its governing competence standard is ADR-0252: comprehension must grasp *deep relational structure* that subsumes a family of problems, not surface features of one.

**Telos stages:** comprehend, think/reason (primary); recall (in-turn)
**Macro role:** Turns admitted input into a decided, evidence-bearing proposition graph — or a typed refusal.

---

## What it is / What it does

M3 spans recognition (`recognition/`, teaching-derived structural recognizers via anti-unification), the cognition pipeline (`core/cognition/`, 13 modules, `pipeline.py` at 1381 lines), the comprehension attempt/router (`core/comprehension_attempt/`: `classify.py`, `failure_family.py`, `router.py`, `proposal.py`), the determine phase (`generate/determine/`: `determine.py`, `consolidate.py`, `estimate.py`, `estimation_license.py`, `render.py`), the realize phase (`generate/realize/`, `generate/realizer.py`), the deduction flagship (`generate/proof_chain/` — ROBDD tautology engine under six ratified bands), curriculum-grounded reasoning, the GSM8K math reader (demoted to diagnostic), and the field-wedge research zone (a recorded negative result).

Operationally, the live path enters M3 after ingest: intent classification → `PropositionGraph` construction → determination or entailment → `ArticulationTarget`. Deduction serving is **ratified ON** (`deduction_serving_enabled=True`, `core/config.py:397`); curriculum serving is **OFF** (`curriculum_serving_enabled=False`, `:412`), as are `ask_serving_enabled` and `verified_serving_enabled`. The deduction engine is `generate/proof_chain/entail.py` — canonicalize `(P1 & … & Pn) → Q`, ask `is_tautology` over a ROBDD. It is a decision procedure, not a derivation: `EntailmentTrace` carries an outcome, a reason, and five canonical BDD node keys (opaque hashes). **There are no intermediate proof steps in the object**, which is why "the renderer drops the proof chain" was previously diagnosed at the wrong layer — nothing is dropped because nothing exists to drop. Multi-step articulation is engine work.

---

## Contract

- **Inputs:** injected `FieldState`, tokenized/OOV-policed text, mounted packs and vocabulary (M1), session context.
- **Outputs:** `PropositionGraph` (now carrying `GraphNode.negated`, ADR-0265), `ArticulationTarget`, `EntailmentTrace` / `Determined` / `Undetermined`, typed refusals, recognizer outcomes, `ContractAssessment`.
- **Invariants:**
  - **INV-30** — open-world `determine()` constructs only `Determined(answer=True)` or refuses; never asserts `False` — pin: `tests/test_architectural_invariants.py` — suite: present in the test tree; **suite membership unverified at this SHA** (flagged).
  - **INV-31** — closed-world `FrameVerdict` cannot reach the open-world runtime (transitive import containment + single construction allowlist + typed refusal) — pin: `tests/test_architectural_invariants.py`.
  - **INV-34** — cognition-pipeline failures are typed, never silent; a `None` `ContractAssessment` is itself a violation; unresolvable referents refuse rather than fill; no PASSTHROUGH in the intent ratifier — pin: `tests/test_linguistic_governance_phases.py`.
  - Kernel no-new-legacy — new derivation must consume `ProblemFrame`/`KernelFacts`; new raw-prose regex requires an explicit `LEGACY_EXCEPTION` — pin: `tests/test_kernel_no_new_legacy_derivation_surfaces.py`.

---

## Design vs build

- **Design:** **ADR-0252 (Accepted, governing)** — the problem-solving paradigm and its §4 conformance bar; ADR-0251 (halt bespoke per-case regex work; the prohibition governing every math-reader increment); ADR-0249/0250 (reader→Hamiltonian compiler); ADR-0256–0261 (six deduction bands); ADR-0262/0264 (curriculum); ADR-0265 (negation in the proposition graph); ADR-0243 (wave-field lifecycle); ADR-0142 (epistemic taxonomy).
- **Build:** `partial-wiring-debt`.
- **Evidence:**
  - Deduction serving decides real arguments end-to-end, `wrong=0` across all splits — lane — `evals/deduction_serve/report.json`, pinned SHA `0b461a5a…` in `CLAIMS.md` — would-fail-if-absent: **yes**.
  - Propositional entailment scored against an independent truth-table oracle, 716/716 correct, `wrong=0`, `refused=0` — lane — `evals/deductive_logic/report.json`, pinned `97a23094…` — would-fail-if-absent: **yes**.
  - `deductive` suite exists and carries 20 test files — code-read — `core/cli_test.py` — would-fail-if-absent: **yes**.
  - 25 sealed bands / 18,000 cases / `wrong=0`; capability index breadth 13, `wrong_total=0` — measurement — `chat/data/deduction_serve_ledger.json`, `evals/capability_index/baseline.json` (confirmed mechanically 2026-07-25).
  - **Structure-mapping (the ADR-0252 §6 correction) — not built.** `conformal_procrustes` exists in `core/physics/dynamic_manifold.py` but is off-serving and unwired to comprehension. would-fail-if-absent: **no**.

---

## Capacity

- **Designed:** comprehension that grasps deep relational structure, one canonical structure subsuming a family (generalization ratio > 1).
- **Measured — the two-grammars result, and it is the sharpest number in the assessment.** Reader and writer inventories measured against each other (PR #138, `c69f9948`): the **writer emits 1739 constructions; the reader comprehends 19; the overlap is 6**, all set-theoretic. The reader **fabricates on 22 more** — `every dog is a mammal` → `member(every_dog, mammal)`; `Given: furthermore; p implies q; p.` reaching served output with `furthermore` recited back as a premise. *These are measured and pinned, held for ADR + ratification — recorded here, not re-discovered and not fixed.* Prior prose claiming the reader "reads" its arguments was falsified: `g_args_rate` was `0.0` throughout.
- **Ceilings:** curriculum bands are capped at ≤16 entailed cases by the 16-premise compilation cap (ADR-0264 §4.1), so **no curriculum band can earn SERVE until query-scoping lands** — an engineering blocker, not a content one. Deduction's ROBDD decides but cannot narrate multi-step derivations. The GSM8K sealed holdout (1,319 cases) has never been opened against a parser with sufficient coverage.

---

## Dependencies & provenance

**reads** → M1 (packs, vocabulary, vault recall), M0 (field, CGA); **receives** ← M2; **feeds** → M4 (articulation and serve seam), M5 (refusals and comprehension failures become proposal candidates); **verified-by** → MV; **governed-by** → MG.

---

## Stage coverage

| Stage | Verdict | Evidence |
|---|---|---|
| comprehend | **covered, narrowly** | Deduction bands decide real arguments with `wrong=0`; but the reader spans 19 constructions against a 1739-construction writer and fabricates on 22 — coverage is real and thin |
| think/reason | **covered** | ROBDD entailment, 716/716 against an independent oracle; idle consolidation climbs to deductive closure under proof-gating |
| recall (in-turn) | **covered** | Exact CGA recall via M1 |

**Zone roster:** `L4-recognition`, `L5-cognition`, `comprehend-organ` ⚑, `determine-phase` ⚑, `realize-phase` ⚑, `reasoning-deductive`, `gsm8k-math`, `field-wedge-research`.

**⚑ Zero-subsystem zones — honest scoping.** Three of the four unmapped zones live here and all three sit on the serving path. What is *known* at this SHA: `comprehend-organ` corresponds to `core/comprehension_attempt/` (6 modules: classify, failure_family, router, proposal, model); `determine-phase` to `generate/determine/` (8 modules incl. consolidate, estimate, estimation_license, render); `realize-phase` to `generate/realize/` + `generate/realizer.py` (306 lines) + `generate/realizer_guard.py`. What is *unmapped*: their internal decomposition, per-component liveness, and the boundary between `comprehension_attempt` and `L5-cognition`. **These are Phase 3's first descent targets.**

**Rollup note:** weakest-link rollup; not a completion rate. M3's deduction region is genuinely strong (ratified, evidenced, `wrong=0`); its comprehension region is measurably narrow. A single layer label cannot express that split, which is why the stage table above separates them.

---

## Judgment

**Fitness: `strained`, with the 18 derivation organs `superseded-in-place`.**

The strain is precisely what ADR-0252 named: an expert substrate driven by a novice reader. The ADR is *ratified*, its diagnosis stands, its §6 correction is designed — and its §5 acceptance gate **has never returned a verdict** (two unmerged worktrees, `rnd/structure-mapping-experiment` and `rnd/sme-experiment-v2`; the latter's tip is "formalize §5 experiment scaffolding"). So the condemned mechanism keeps serving under an explicit ruling that it should, until a proven replacement exists. That is `superseded-in-place`, and the schema's separation of liveness from fitness is what lets this card state it without contradiction.

**Honest wrinkles:**
- **The "34 surface organs" count does not reproduce.** At this SHA there are **18** `resolve_promotable_*` functions, all in `generate/derivation/`. ADR-0252 cites 34. Either the count used a different basis, or consolidation has occurred since ratification. The discrepancy is unresolved and matters, because 34→18 would be evidence the debt is already being paid down — or evidence the ADR's diagnosis was calibrated against something else. Phase 3 should resolve it rather than repeat either number.
- The single load-bearing empirical claim of the *governing* paradigm ADR is unresolved, and a well-controlled NO-GO is defined as full credit — so the experiment is cheap to finish and expensive to leave open. This is the highest-leverage open item in the assessment.
- Deduction's strength and comprehension's narrowness are easy to conflate. `wrong=0` across 18,000 cases is a statement about the *decision procedure*, not about how much English CORE can read.
- `field-wedge-research` is `research-negative` — a mechanism honestly refuted. It is knowledge and must not be tidied into `inert`.

**Open questions:**
- Run ADR-0252 §5 to a verdict (→ ruling; highest leverage)
- Reconcile the 34-vs-18 organ count (→ Phase 3)
- Descend the three ⚑ serving-path zones (→ Phase 3, first)
- Is multi-step proof articulation wanted, given it is engine work with a real soundness surface? (→ ruling)
