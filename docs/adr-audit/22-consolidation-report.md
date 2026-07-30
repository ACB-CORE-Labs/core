# Phase 4 — Consolidation & Parsimony Report

Every ADR marked `reducible-to-<X>` or `generalization-candidate` on the necessity/generality axis, clustered. Per `00-scope-and-method.md`'s charter: distinguish **true redundancy** (two mechanisms doing the same thing — one should go) from **legitimate specialization** (the narrower mechanism earns its keep for a reason the general one structurally can't cover). These clusters are strong candidates for ruling, not settled conclusions. **Verified against:** `main` @ `cbfc8ccb`.

## Cluster 1 — The rotor operator is real, and four sites bypass it anyway (true redundancy)

**General mechanism:** `algebra.rotor.rotor_power` ∘ `word_transition_rotor` (ADR-0004, confirmed the stack's cleanest member — full build, live, zero design-fidelity tension, the closest thing this batch found to "the one general mechanism" the physics-efficiency argument is looking for).

**Narrower duplicates found:**
- `packs/compiler.py::_blend_feature_versors` (live, ignores its own `strength` parameter — the defect already ratified as `G-25`) — `AA-5`
- `packs/compiler.py::_alignment_nudge_rotor` (dead code, and mathematically wrong for non-simple rotors) — `AA-5`
- `field/operators.py::_incremental_correction_rotor` and `GraphDiffusionOperator.forward` (live via `core pulse`, lerp-then-repair instead of the rotor composition) — `AA-5`
- `packs/compiler.py::_feature_rotor` (duplicates `make_rotor_from_angle` exactly, modulo half-angle, minus the range check) — `AA-6`
- Four production sites hand-roll the raw sandwich `V·X·rev(V)` to bypass `versor_apply`'s closure, each for a locally-valid reason but with no shared `algebra.versor.raw_sandwich` primitive to express that reason in — `AA-15`

**The correct replacement already exists** — written and tested at `evals/logos/repaired_ground.py:60-79` — but lives only as an eval monkeypatch, not a library function anything production imports.

**A likely contributing cause, cheap to fix:** `algebra/__init__.py` exports only `word_transition_rotor`; `rotor_power` and `make_rotor_from_angle` — the two most-reinvented operators above — are reachable only via direct submodule import. (`AA-14`)

**Verdict:** true redundancy, not specialization. Recommend: promote `rotor_power`/`make_rotor_from_angle` to the package's top-level export, then route the five duplicate sites through it one at a time (each has an existing test to hold it to).

## Cluster 2 — The semantic-ground layer reinvented the algebra layer, worse (true redundancy, largest blast radius)

This is `AA-84`, and it is the single most important consolidation finding Batch 1 produced, because it's independently corroborated from both ends: stack A1 (auditing the algebra layer, ADR-0001/0003/0004) and stack A3 (auditing the semantic-ground layer, ADR-0005/0015/0021, under the FA-1 cascade) reached the same conclusion without seeing each other's work.

**General mechanisms that already shipped:** `rotor_power`/`word_transition_rotor` (composition), `geometric_product` (the algebra's native binding operator).

**Narrower, worse duplicates:** "alignment" (ADR-0005's cross-pack blending, which `AA-2` and the A3 cascade show discards 34-37 of the coordinates it's supposed to preserve) and "holonomy" (ADR-0015's Crown Proof, whose reverse-walk closure was deleted at `fca6216e` — `AA-51` — and which measured at AUC 0.557 against a required 0.80, per FA-1). Neither imports the general operator it duplicates.

**Verdict:** true redundancy at the design level, not just the code level — this is not "two functions that happen to overlap," it's "a whole layer's central mechanism re-derived from scratch, badly, when the layer below already had a working version." Highest-priority item for the 🔴 Block bucket in `40-triage-queue.md`. Recommend the re-verdict work on the FA-1 cascade (`21-drift-report.md` §1) be scoped from the start as "replace with the L0 operator," not "repair the L2-native version."

## Cluster 3 — SafetyCheck and EthicsCheck are one mechanism built twice (true redundancy, but ship the semantic distinction as data, not code)

`AA-110`: normalized diff of the two classes' bodies is two comment lines and one field name. ADR-0034's own justification for a parallel surface ("floor vs. pledge") is a real semantic distinction — but it's a distinction a generic `Check` class with a `verdict_kind: Literal["boundary","commitment"]` field would preserve exactly as well, without the duplicate maintenance surface.

**Related, same layer:** `AA-111` — five-plus pack loaders (identity 494 lines, safety 259, ethics 409, register 608, anchor-lens 422, rhetorical-style 425) duplicate the same `_resolve_search_paths`/`_find_pack`/`_read_json`/`_validate_envelope`/`_validate_ratification` skeleton, each with its own `CORE_ALLOW_UNRATIFIED_<X>` env var and error class. This is a bigger, higher-effort consolidation than Cluster 1 or 3's headline (six call sites, ~2,600 lines of near-duplicate loader logic) but the same shape.

**Verdict:** true redundancy for the loader skeleton; the Check-class distinction is legitimate *semantically* but not legitimate *structurally* — recommend a generic `PackLoader[T]`/`Check` base with the per-family specifics as configuration, not separate classes.

## Cluster 4 — The admissibility/attention/identity triad (unresolved — feeds an existing open ruling, not a new one)

Stack A4 flagged two internal clusters:
- **A4-C1** (`AA-90`, `AA-94`, `AA-99`, `AA-102`): `PropositionGraph`'s undocumented second role as a constraint *producer* (ADR-0046, inverting the ADR-0009 lineage), `AttentionOperator.plan`'s structurally-identical-to-`check_margin` score/cut/budget shape with an underived threshold where admissibility has a falsifiably-derived one, ADR-0022's still-open `IDENTITY` region source (a natural producer for admissibility's unproduced `frame_versor`), and the doctrinal contradiction at `AA-102`. These four, plus stack A2's `AttentionOperator`/`SalienceMap` findings (`AA-30`, name-collision hazard) and MG's identity-manifold work, all touch the same unresolved question the existing assessment already registered as **CR-1** (Candidate Register: "is attention a first-class layer, or an emergent property of admissibility that should stay distributed?").
- **A4-C2** (`AA-89`): threshold and margin admissibility modes coexist as parallel branches with duplicated rotor-check logic, after the stack's own design work established no static threshold is geometrically valid. This one is a clean within-stack merge (fold threshold into margin with `delta=0`), independent of the CR-1 question.

**Verdict:** A4-C2 is actionable now (true redundancy, low risk). A4-C1 is not yet a consolidation recommendation — it's evidence that should inform CR-1's ruling, which this audit does not have standing to make (per the charter: flag for ruling, never unilateral). Recommend: attach this cluster to CR-1 explicitly when that ruling is next revisited.

## Cluster 5 — Two variations of hedging that should probably be one (unresolved, self-acknowledged by the code)

`AA-142`: ADR-0028/0030/0031 correctly consolidated into one operator (`generate/surface.py::_apply_hedge`) across three separate ADRs — a genuine success story, not a defect. But ADR-0038's `inject_hedge()` is a second, independent mechanism triggered by a different signal (ethics verdict vs. alignment band), sharing only 2 of 8 `SurfacePreferences` fields, kept from double-firing only by an incidental string check. ADR-0038's own text names this as an open question and defers it — it's still open. A later ADR-0254 (outside Batch 1) adds a *third* independent hedge site without resolving either gap.

**Verdict:** legitimate specialization is plausible (different trigger signals could be a real reason for two mechanisms) but unproven — nobody has stated the invariant that would make two-mechanisms-by-design a decided architecture rather than an accumulated one. Recommend: either generalize both into one operator parameterized by trigger-signal, or ratify the invariant ADR-0038 §5 already proposes but never ratified.

## Cluster 6 — Confirmed non-redundancies (the audit found matches, not just mismatches)

Worth recording explicitly, since a report that only ever finds problems is a report nobody trusts: two places in Batch 1 asked "is this duplicated?" and the honest answer was no.

- **`AA-157`, and B6's zone-level verdict**: ADR-0048 (DEFINITION/RECALL) and ADR-0050 (COMPARISON) share one dispatcher (`_maybe_pack_grounded_surface`) and one resolution primitive (`resolve_lemma`) by explicit in-code citation — confirmed, not assumed. One small, already-acknowledged gap remains (the comparison composer doesn't yet route through the shared `PackSurfaceCandidate` type), but this is the audit finding a team that already did the consolidation work correctly.
- **B3's Rust-dispatch pattern** (`AA-138`): the opt-in bit-identity dispatch technique from ADR-0020 is sound on its own terms and is already being generalized toward a Zig substrate (ADR-0196) — a case where a narrow mechanism earning promotion to general infrastructure is the system working as intended, not a gap to close.

## Deferred to Batch 2+

Two candidates flagged but not independently verified within Batch 1, carried forward:
- `AA-123`: `DeterminismClass`/`ReviewLevel` (ADR-0012, ingest layer) and ADR-0021's Epistemic Grade Policy both grade a claim's trust before admission — possible overlap, not yet checked against each other directly.
- `AA-132`: ADR-0019's Stage-1 vectorization technique (vault recall, confirmed ~4,000–5,000× speedup) as a template for the other unvectorized `cga_inner`/`geometric_product` hot loops CR-1 already flags as ~73% of turn time. This is a performance-consolidation candidate (Pillar I, Mechanical Sympathy), distinct from the design-consolidation clusters above.

## Cluster 7 — Batch 2 & Batch 3 Consolidation Clusters

- **`AA-210` / `AA-292`** — 6+ implementations of the pack-id boundary guard / loader skeleton (`packs/compiler.py`, `rhetorical_style`, `units`, `numerics`, etc.) duplicating `_resolve_search_paths`/`_find_pack`/`_read_json`/`_validate_envelope` (`AA-111` pattern). Recommend generic `PackLoader[T]`.
- **`AA-228` / `AA-239`** — Re-derives weaker inline versions of domain contract predicates P1/P2/P5/P6/P7 in `reporting.py`; status ladder and 9 predicates validate same claim independently.
- **`AA-286`** — ADR-0056 and ADR-0080 ship parallel "Contemplation Loop" implementations without cross-reference.
- **`AA-318`** — `from_miner.py` and `from_curriculum.py` are near-duplicate modules for translating candidates into `PackMutationProposal` records.
- **`AA-342`** — ADR-0136 regex sentence-template patterns explicitly superseded by ADR-0164 incremental comprehension reader while preserving empirical seed taxonomies.
- **`AA-363`** — ADR-0183 stub path for lawful audio-to-lexeme resolution consolidated directly into Audio compiler (`ADR-0181`).
- **`AA-366`** — Candidate-graph completeness guard (`ADR-0191`) consolidates wrong=0 leg across candidate extractors.
- **`AA-437`** — Grounded-open hedge arm (`ADR-0254`) consolidates shadow coherence gate hedging with ADR-0038/0054/0080/0174.



