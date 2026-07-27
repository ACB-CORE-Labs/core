# M1 — Knowledge & Memory

**Kind:** layer · **Parent:** CORE · **Assessor:** Opus 5 (Phase 2)
**Verified at:** `8927c563` (2026-07-27)
**Liveness:** `partial-wiring-debt` · **Fitness:** `fit` · **Topology role:** runtime boundary + reviewed pack data

> What is known, at rest — and the standing at which it is known. M1 is where CORE's rejection of statistical retrieval becomes concrete: a recall hit is a *geometric fact*, not a probabilistic suggestion, because the CGA inner product **is** Euclidean distance in conformal embedding. Exactness here is not a performance trade-off; it is what makes a recalled result verifiable at all. M1 also carries the epistemic-status regime, so it stores not just claims but their position in the revision graph.

**Telos stages:** recall (primary); comprehend and articulate (as the source of packs and vocabulary)
**Macro role:** Holds and returns knowledge exactly, with its standing attached.

---

## What it is / What it does

`vault/` (5 modules) is exact CGA recall — `best_match = argmax_i {Q · V_i}` — with no ANN index, no HNSW, no embedding ranking, no tunable similarity threshold; the runtime invariant forbids introducing any. `packs/` (48 modules) holds compiled runtime language packs plus governance/style modality packs. `vocab/`, `morphology/`, `alignment/` form the lexical substrate. `core/contemplation/` (13 modules) is memory in motion — idle consolidation, the wave seam, hypothesis-versus-evidence reconstruction.

The epistemic surface (ADR-0021) types every claim by its **position in the revision graph**, not by source trust: `COHERENT` (fits current field geometry), `CONTESTED` (incoherent with a reviewed claim, review pending), `SPECULATIVE` (proposed, admissible only as candidate), `FALSIFIED` (incoherent under accumulated evidence — *retained*, eligible for inversion). Two properties deserve emphasis. First, the **non-hardening invariant**: no reviewed claim ever becomes unrevisable; no `final`/`frozen`/`axiom`/`permanent` flag exists or may be added. The only closure in the architecture is mathematical (`versor_condition`), never epistemic. Second, the **curator rule**: status transitions are computed from coherence with the reviewed field, and the curator's *only admissible reasoning is geometric* — source credentials, popularity, and institutional position are explicitly inadmissible as justification.

The dual-pack serve boundary (ADR-0253 / INV-33) separates compiled runtime packs (`packs/data/<pack_id>/`, the only serve authority, loaded via `packs.compiler.load_pack`) from source/draft language trees (`packs/he`, `packs/grc`, `packs/en`, …), which serve entrypoints must not import as Python packages.

---

## Contract

- **Inputs:** reviewed teaching applies and certified promotions (M5), compiled pack artifacts, session writes.
- **Outputs:** exact recall hits with `epistemic_status`, lexical entries, mounted packs, vocabulary manifold positions, consolidated derived facts with `Derivation` provenance.
- **Invariants:**
  - Exact recall only — no cosine similarity, ANN, HNSW, or embedding ranking as runtime memory truth — pin: architectural invariants; **status: enforced by doctrine + review**, mechanical pin not individually re-verified at this SHA.
  - INV-21 (vault-writer allowlist), INV-22/23 (unmarked → SPECULATIVE), INV-24 (recall categorization; user-facing evidence COHERENT-only), INV-29 (only `vault/store.py` transitions status) — pins: `tests/test_architectural_invariants.py`, `tests/test_epistemic_invariants.py`.
  - Non-hardening — pin: `tests/test_epistemic_invariants.py`.
  - INV-33 dual-pack serve boundary — pin: `tests/test_pack_draft_serve_boundary.py` (static AST + process import probe).
  - Morphology rows load only from compiled packs, carrying `language`, `source_pack_id`, `source_span` — provenance-complete or not loaded — pin: `tests/test_observed_he_morph_constraint_v0.py` (four-arm ablation).

---

## Design vs build

- **Design:** ADR-0021 (epistemic surface), ADR-0054 (exact CGA recall indexing/batching), ADR-0253 (dual-pack boundary), ADR-0180 (Delta-CRDT sharded vault), ADR-0243 (wave-field lifecycle), ADR-0241 (holographic standing-wave storage — **off-serve quarantined**), `docs/position_paper.md` §3.3.
- **Build:** `partial-wiring-debt`. Key files: `vault/store.py`, `packs/compiler.py`, `core/contemplation/`, `core/physics/holographic_vault.py` (quarantined).
- **Evidence:**
  - Exact recall is the runtime primitive; `recall`/`recall_batch` in `vault/store.py:224,296` — code-read — would-fail-if-absent: **yes**.
  - Pack-grounded and teaching-grounded composers serve real turns — lanes — `evals/domain_contract_validation`, `evals/fabrication_control` (phantom endpoints, cross-pack non-bridges, sibling collapses all refuse), both pinned in `CLAIMS.md` — would-fail-if-absent: **yes**.
  - Off-serve quarantine of the wave/holographic modules is AST-pinned — pin — `tests/test_third_door_cohesion.py` — would-fail-if-absent: **yes**.
  - Five Tier-1 domains hold ratified packs with zero open gaps — `CLAIMS.md`.

---

## Capacity

- **Designed:** exact, verifiable recall over a curated manifold, with standing attached to every claim.
- **Measured:** 5 ratified domains (2 `reasoning-capable`, 3 `audit-passed`); packs across en / he / grc / el; `docs/gaps.md` shows all 26 historical coverage gaps closed.
- **Ceilings:** **the vocabulary manifold is finite and curated by design.** Extending to a new domain requires constructing pack vocabulary, establishing coherence with reviewed claims, and passing an eval lane. The position paper states the honest limit: whether this scales to the breadth of human knowledge is an open question; whether it can be done without confabulation is not. T1 vault contents are discarded on process exit (ADR-0146; see M6).

---

## Dependencies & provenance

**feeds** → M3 (recall, packs, vocabulary), M4 (lexicon, register packs); **written-by** → M5 (the single reviewed path); **built-on** → M0 (CGA distance is the recall primitive); **residency-gated-by** → M6.

---

## Stage coverage

| Stage | Verdict | Evidence |
|---|---|---|
| recall | **covered** | Exact CGA recall serving live; fabrication-control lane pinned |
| comprehend / articulate (as source) | **covered** | Compiled packs are the only serve authority (INV-33 pinned) |
| *(consolidation — straddles M5)* | **covered, flag-gated** | CLOSE consolidation is proof-gated and defaults OFF |

**Zone roster:** `L2-vault`, `L3-packs`, `vocab-manifold` (live-serving), `morphology` (live-internal), `alignment-resonance` (live-internal), `L8-memory-contemplation` ✱ (straddles M5; owned here, cross-referenced there).

**Rollup note:** weakest-link rollup. `vocab-manifold` is confirmed live-serving; the layer label understates it.

---

## Judgment

**Fitness: `fit`.** The exactness commitment and the epistemic-status regime are mutually reinforcing: exact recall makes a hit verifiable, and typed standing makes it *interpretable*. The non-hardening invariant is a genuinely unusual and, in this assessor's reading, correct design choice — most systems acquire an axiom flag eventually, and forbidding it structurally is what keeps the revision graph honest.

**Honest wrinkles:**
- **The knowledge that compounds and the knowledge that resets are different sets.** Packs and reviewed corpora persist; the T1 vault does not survive process exit. So "memory" in M1 means two very different things depending on tier, and the distinction is invisible in the layer name. This is the M6 residency question seen from the other side.
- `FALSIFIED` claims are **retained**, not deleted — correct and easy to misread as clutter. Any future cleanup pass must not treat falsified rows as dead data.
- The holographic standing-wave vault (ADR-0241) is real, uses the INV-21 writer, and is **hard-quarantined off-serve** by AST pin. It is a substantial built capability that no serving path may touch — legitimate research quarantine, but worth Phase 4 attention as capacity that exists and cannot be used.
- The exact-recall prohibition (no ANN/cosine/HNSW) is stated in `AGENTS.md` as law; I did not individually verify a mechanical pin that would *fail* if someone added a cosine ranker. Doctrine-enforced-by-review is weaker than doctrine-enforced-by-test. Flagged for Phase 3.

**Open questions:**
- Is there a failing-when-violated pin for the no-approximate-recall invariant, or is it review-enforced? (→ Phase 3)
- Should the holographic vault's quarantine have an exit criterion? (→ ruling)
- Does the identity-divergence curriculum still bypass formation's gates? (→ Phase 3, from M5)
