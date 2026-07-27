# M5 — Learning & Growth

**Kind:** layer · **Parent:** CORE · **Assessor:** Opus 5 (Phase 2)
**Verified at:** `8927c563` (2026-07-27)
**Liveness:** `partial-wiring-debt` · **Fitness:** `fit` (mechanism) / `strained` (throughput) · **Topology role:** runtime boundary + reviewed pack data

> Controlled mutation. M5 answers the question that separates a cognitive engine from a database: how does the system come to know something it did not know, without acquiring the ability to lie to itself? CORE's answer is a **typed** boundary — durable standing is reviewed or proof-carrying; provisional standing may update autonomously *iff* it is typed, isolated, replayable, and structurally unable to masquerade as ratified truth. This is the layer where the project's epistemology becomes mechanism.

**Telos stages:** learn from reviewed correction (primary); replay/determinism
**Macro role:** Converts served experience and curated material into standing knowledge, at a rate and standing the evidence licenses.

---

## What it is / What it does

Four regions. **Teaching** (`teaching/`, 46 modules): the reviewed loop — proposals, review, store, replay-equivalence gate, discovery, curriculum premises, ratification, domain chains. **Formation** (`formation/`, 23 modules): the content-addressed data foundry — Mine → Smelt → Forge → Compose → Compile → Run → Ratify → Promote — with six declared trust boundaries, every boundary content-addressed in and out, every rejection producing an audit record. **Reliability calibration** (`core/reliability_gate/`, `core/ratified_ledger.py`): earned SERVE licenses under a Wilson floor (θ_SERVE = 0.99), sealed practice ledgers, hash-verified on load. **Capability** (`core/capability/`, 14 modules): the ledger, the nine-predicate domain contract, lane-shape registry, reviewer registry, expert-demo promotion.

The boundary is enforced by failing-when-violated invariants rather than convention — INV-21 (vault-writer allowlist), INV-22/23 (unmarked defaults to SPECULATIVE), INV-24 (recall categorization; user-facing evidence is COHERENT-only), INV-29 (only `vault/store.py` transitions `epistemic_status`), INV-30 (open-world `determine()` never asserts False). Autonomous provisional writes — idle CLOSE consolidation, reliability counts, proposal emission, disclosed estimates — all flow through the same `VaultStore.store` path, written SPECULATIVE, rendered `as_told` / `[approximate]` / "proposal". There is no parallel learning path, which is itself an invariant.

---

## Contract

- **Inputs:** served turns and corrections (M4), comprehension failures and typed refusals (M3), curated source material (formation), curator/HITL rulings, sealed practice results.
- **Outputs:** `PackMutationProposal` / `ReviewedTeachingExample` (SPECULATIVE at creation), ratified chain corpora, sealed + SHA-verified ledgers, `LicenseDecision`, capability ledger rows, `MasteryReport` (self-sealing SHA).
- **Invariants:** INV-21/22/23/24/29/30 as above; formation's six trust boundaries; content-addressing rules (canonical JSON, sorted keys, **no floats in hashed payloads**, **no pickle** — pickle defeats replay and is a code-execution surface); pack mutation proposal-only until reviewed; identity-manifold mutation by prompt or correction **forbidden**.

---

## Design vs build

- **Design:** ADR-0021 (epistemic surface + one-mutation-path), ADR-0057 (teaching-chain proposal/review/replay-equivalence), ADR-0175 (calibrated attempt-and-eliminate learning; an engine cannot raise its own bar), ADR-0263 (ratified-ledger bridge: seal → ratify → SHA-verify → serve-gate), ADR-0262/0264 (curriculum + negative curriculum), ADR-0091/0106/0109 (domain contracts, expert-demo promotion, lane-shape registry), ADR-0218 (`apply_certified_promotion`), ADR-0161 (HITL async queue — **scope only**), `docs/teaching_order.md` (five-layer prerequisite-topological doctrine).
- **Build:** `partial-wiring-debt`.
- **Evidence:**
  - Miner- and curriculum-sourced proposals route through the *single* reviewed teaching path — lanes — `evals/miner_loop_closure`, `evals/curriculum_loop_closure`, both pinned in `CLAIMS.md` — would-fail-if-absent: **yes**.
  - Earned-license machinery is real: 25 sealed bands / 18,000 cases with `wrong=0` gate deduction's SERVE — measurement — `chat/data/deduction_serve_ledger.json` — would-fail-if-absent: **yes**.
  - `formation` suite exists and points at `tests/formation` — code-read — `core/cli_test.py:208` — would-fail-if-absent: **yes**.
  - Five Tier-1 domains carry ratified status (3 `audit-passed`, 2 `reasoning-capable`), all with zero open gaps — `CLAIMS.md`, mechanically generated.
  - **Curriculum serve ledger does not exist.** `chat/curriculum_serve_license.py:46` is the single production call site passing `missing_ok=True`, correctly, because `chat/data/curriculum_serve_ledger.json` is absent — code-read.

---

## Capacity

- **Designed:** an autonomous half that proposes and a reviewed half that ratifies, with volume flowing from curated material through formation into serving licenses.
- **Measured — the binding constraint is throughput, and it is quantified.** Curriculum bands are **24×–73× short** of the entailed-bucket floor, and **no served subject has a family close enough to flag as "next."** Compounding this, ADR-0264 §4.1 establishes that the 16-premise compilation cap holds any band to ≤16 entailed cases, so **no curriculum band can earn SERVE until query-scoping lands** — an engineering blocker gating a content problem. Separately, distinct-evidence counting is unsound where replay is treated as independent trials: **21 of 25 ratified bands are short** on that basis (Wilson assumes independence; a replay is one trial).
- **Ceilings:** HITL review is CLI-synchronous — the operator cannot review while the engine serves (W-009 open, L10-gated). Vocabulary extension is deliberately manual and slow; the position paper states this plainly as an open scaling question.

---

## Dependencies & provenance

**receives** ← M4 (corrections), M3 (failures/refusals); **writes** → M1 (the promotion target; vault and packs); **gated-by** → MG (identity mutation forbidden; safety non-swappable); **evidenced-by** → MV (lanes, ledgers, CLAIMS); **blocked-by** → M6 (async HITL needs the process).

---

## Stage coverage

| Stage | Verdict | Evidence |
|---|---|---|
| learn from reviewed correction | **covered** | Single reviewed path proven by two pinned loop-closure lanes; proposal-only discipline mechanically enforced |
| replay/determinism | **covered** | Replay-equivalence gate on teaching chains; content-addressed, float-free, pickle-free hashing |
| *(autonomous provisional learning)* | **covered, flag-gated** | CLOSE consolidation climbs to deductive-closure fixed point under proof-gating; **every relevant flag defaults OFF** (`consolidate_determinations`, `review_pending_proposals`, `review_derived_close_proposals`, `auto_contemplate`, `auto_proposal_enabled`, `vault_promotion_enabled`) |

**Zone roster:** `L7-teaching`, `formation-curriculum`, `reliability-calibration`, `capability` ✱ (straddles MV; owned here).

**Rollup note:** weakest-link rollup. M5's *mechanisms* are among the most rigorously built in the repository; its *volume* is the constraint. Do not read `partial-wiring-debt` as "the learning loop is unbuilt."

---

## Judgment

**Fitness: `fit` on mechanism, `strained` on throughput.** The typed learning boundary is, in this assessor's reading, CORE's most distinctive and best-executed idea — it dissolves the usual "autonomy versus safety" trade-off rather than splitting it, which is the Third Door done correctly and worth naming as a success rather than only auditing for faults. The strain is entirely on the other side: a ratification pipeline that is architecturally sound and 24×–73× under-fed.

**Honest wrinkles:**
- **The autonomous half is built and switched off.** Six or more learning-related flags default `False`. The machinery for a self-improving loop exists, is proof-gated, and does not run by default. Whether that is correct caution or accumulated hesitancy is a ruling, not a finding — but the gap between "built" and "on" is the largest in this layer.
- **A committed ledger is necessarily an *earning* one**, which makes the outcome-mix ruling the binding constraint — and the curriculum ledger does not exist yet. The one production `missing_ok=True` is honest and narrow, but it is load-bearing scaffolding.
- **The Wilson independence problem is not cosmetic.** If replay is being counted as distinct evidence anywhere a license is earned, licenses are being granted on overstated evidence. 21/25 bands are affected. This deserves Phase 4 attention as a possible `wrong-solution` in the counting, not the gating.
- Formation's trust-boundary table is exemplary — content-addressed in and out, no floats in hashed payloads, no pickle, every rejection audited. It should be the template other layers are measured against, and Phase 4 should check whether M2's ingest boundary meets the same bar.
- `docs/teaching_order.md` records a known gap since 2026-05-17: the identity-divergence curriculum predates the formation pipeline and still flows through `runner.py` rather than Forge → Compose → Ratify → Promote. Unverified at this SHA; carried forward.

**Open questions:**
- Is the Wilson/replay independence defect actually granting licenses on overstated evidence? (→ Phase 4, then ruling)
- Which autonomous-learning flags should be ratified ON, and on what evidence? (→ ruling)
- Does M2's ingest boundary meet formation's trust-boundary bar? (→ Phase 2 M2 card / Phase 3)
- Curriculum query-scoping: the engineering blocker gating all curriculum SERVE (→ ruling; ADR-0264 §4.1 names it)
