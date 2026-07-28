# The Foundations Audit — bottom-up, inside-out, logos-first

**Charter** · 2026-07-28 · opened at `339bfd37` · **precedes and re-gates the Perception Arc**
**Standing question:** for every part of the cognitive design — is it masterfully implemented *intrinsically*, in *the role it plays in its subsystem*, in *the role its subsystem plays in the system*, and at *every seam it is supposed to share with other organs, packs, and components*? Nothing is "understood" until all four can be articulated with evidence.

---

## 0. Why this audit, and why it starts at the bottom

Five independent investigations this session converged on one disease: **layers assuming connections that were never made.** The serving path assumed geometry it never touched (G-24); the faithful §2 reader sat dark while its inversion served; three operator experiments were run and forgotten; the mirror assumed a sync direction nobody verified. Every one was found by *opening the layer below the claim*.

The corollary is the audit's method: **verify from the foundation upward**, because a defect at layer N silently invalidates the mastery of everything at N+1 — and this repo's record proves the invalidations are real, not hypothetical. The always-on daemon consolidated an empty set for six weeks because one foundational flag was absent; every layer above it looked correct.

**Exit criterion:** every layer below the perception boundary carries a verdict — `MASTERFUL` (intrinsic + role + seams all evidenced), `SOUND-BUT-STRANDED` (correct, unwired), or `DEFECTIVE` — and every seam between layers is either *proven live* or *explicitly declared dark with an owner*. The Perception Arc's Phase 1+ does not run until Layers 0–2 have verdicts.

## 1. The first finding, and why logos is the entry point — **FA-1**

The suspicion that CORE-Logos is not integrated as designed was tested against the source before this charter was written. It is **correct**, and the evidence is exact:

**What ADR-0005/0015 design.** Three languages as charts on one semantic manifold: Hebrew roots as **depth anchors**, Greek as **relational depth**, English as **articulation surface**. Alignment edges carry **resonance** (*"Alignment is resonance. These must not be collapsed into one multiplication"*), and the validation gate of meaning is **cross-language holonomy closure**: *"holonomy(hebrew clause) ≈ holonomy(koine greek clause) ≈ holonomy(english clause)… Word-order changes should change holonomy. This is the CORE-Logos proof."* The pillar is not decoration in the design — it is the design's **criterion for meaning**.

**What exists, measured at `339bfd37`:**

| Layer | State | Evidence |
|---|---|---|
| Substrate grounding | **Real** | `packs/compiler.py` folds HE roots into vectors as `triliteral:` tokens — logos shapes the geometry at compile time |
| Holonomy machinery | **Live** | `core/physics/digest.py`, referenced from `core/cognition/pipeline.py` |
| Alignment data | **Seed-scale: 11 edges, 9 HE morphology rows** | `he_logos_micro_v1/alignment.jsonl` — evidence_ids `John1:1, Gen1:1`, exactly ADR-0015's prescribed *first* cases, never grown beyond them |
| EN lexicon tagging | Present | 91 entries carrying `logos.core` semantic domains |
| Serving-path role | **Veto only, no-ops on English** | `pipeline.py:544-583` — `evaluate_logos_on_text` can force a refusal against observed HE plural morphology; *"English-only turns with no HE surface → no-op"* |
| Recall bridge | **ON, undocumented** | `allow_cross_language_recall` — one of the two default-ON flags with no recorded rationale (flag register §1) — gates `recall_top_k=3 vs 0`. **The pillar's own switch was mystery flag #1** |
| Curriculum | Registered, bandless | `hebrew_greek_textual_reasoning` in `DOMAIN_PACKS` with corpora; produced **zero** curriculum bands at the PR-14 measurement |
| Validation-gate role | **Never assumed** | ADR-0015 §"Establishes holonomy-level resonance as the validation gate" — no serving or licensing path consults cross-language holonomy; template match became the de-facto gate instead |

**FA-1 verdict: the pillar is architected and seeded exactly as designed, then left at seed scale, wired at three mutually-unaware points (vector folding · HE veto · recall top-k), and load-bearing nowhere.** The same disease named in the Perception Arc §2b — *transition windows that never close* — but at the foundation, which is why everything above (comprehension, articulation, contemplation, learning) could at best be correct *about an ungrounded semantic space*. Registered as **G-25**.

**FA-1's work order (first in the audit):**
1. **Map the designed logos contract completely** — every ADR-0005/0015 obligation as a row: obligation → implementing site → live/dark → seam partner. No prose without a site.
2. **Decide the holonomy-gate question the way §5 was decided** — pre-registered: on the existing 11 aligned cases plus a small grown set, does cross-language holonomy closure discriminate meaning-preserving from meaning-breaking articulation (word-order sensitivity included, per the ADR's own test)? This is the *designed* validation gate; it has never been measured. Unlike the three failed operator-arithmetic experiments (see Perception Arc Phase 1 correction), this tests the geometry on the job the design actually assigned it — **resonance across representations**, not re-deriving arithmetic.
3. **Rule `allow_cross_language_recall`** — the pillar's switch gets its recorded rationale or gets turned off; measured either way.
4. **Grow-or-declare the alignment corpus** — 11 edges is a proof of concept; either the growth program is scheduled with an owner, or the pillar is formally re-scoped and every design document claiming it is amended. No third state.

## 2. The layer stack and the articulation requirement

Bottom-up. A layer's audit is complete only when each component in it has all four articulations **with evidence**: *(i)* intrinsic correctness, *(ii)* role in its subsystem, *(iii)* subsystem's role in the system, *(iv)* every seam named with its partner and its live/dark status.

| # | Layer | Contents | Prior evidence in hand | Status |
|---|---|---|---|---|
| **L0** | Algebra kernel | `algebra/` (Cl(4,1), versors, CGA embed/readback) | 355 geo refs, fully reachable, exact-recall invariants, `versor_condition` flat across 5,000-beat soak | **Candidate-MASTERFUL — verify seams, then close** |
| **L1** | Physics & field | `core/physics/` (37 files), `field/`, salience, Hamiltonians, digest/holonomy | Soak evidence pinned; salience live-but-bypassed; `relation_compiler` sound-but-stranded | Audit: which operators are load-bearing vs decorative |
| **L2** | Semantic ground — **the logos layer** | packs, vocab, morphology, `semantic_primitives`, alignment, cross-language recall | **FA-1 above** | **DEFECTIVE-BY-ABSENCE at scale; starts first** |
| **L3** | Perception | both readers, `linguistic_pipeline`, `binding_graph`, `structure_mapping`, the comprehension organs | G-24, F-A…F-E, three negative operator experiments, 1.28% read rate | Blocked on L2's verdict — a reader over an ungrounded lexicon inherits the gap |
| **L4** | Cognition | `core/cognition/` pipeline, contemplation, epistemic state/disclosure/questions, vault, recognizer | Pipeline audited pointwise (H-11, H-13); `epistemic_disclosure`/`questions` **fully dark** in census; ADR-0144 recognizer dark | Seam census then role audit |
| **L5** | Serving & articulation | surfaces, licences, articulation/writer, workbench | Licence machinery honest post-R-13/R-8; writer 6 constructions | Last — it is the layer most shaped by all below |
| **X** | Cross-cuts | teaching/learning loop, governance/ledgers, always-on life | Docket executed; teaching gated; daemon profile fixed | Audited per-layer at each seam they touch |

**Instrument** (from the census at `339bfd37`): 666 modules, **293 reachable from serving, 373 dark**. Every dark module gets exactly one of: *seam scheduled* · *deliberately-dark with recorded reason* · *deletion candidate*. The census script becomes a pinned lane so this number is a ratchet, not a snapshot.

## 3. Sequencing

**FA-1 (logos, L2)** → **FA-0 (L0 closure — cheap, likely already masterful, and everything cites it)** → **FA-2 (L1 physics role-audit)** → **FA-3 (L3 perception, absorbing the Perception Arc phases, now on a verified ground)** → **FA-4 (L4)** → **FA-5 (L5)** → close with the full articulable map: every component, four articulations, evidence-linked.

The Perception Arc is **not** discarded — its Phase 0 (read-rate ratchet) runs immediately as instrumentation, its Phase 4 deletions stand, and its Phase 1 is corrected (below) and re-gated behind FA-1's holonomy decision, because the honest experiment order is: *first establish whether the semantic ground carries meaning as designed; then ask what a reader over that ground can do.*

## 4. Phase 1 correction, imported from the systematic sweep

The operator hypothesis ("relations as geometric operators") is **not untested — it has three negative results**, found only when reachability was enumerated instead of grepped:

| Date | Experiment | Encoding | Verdict |
|---|---|---|---|
| 2026-06-04 | Field-reasoner wedge (`docs/analysis/field-wedge-ablation-result-2026-06-04.md`) | relations as **translator versors**, e1 line | **C3 — decoration**: wrong=0 held, caught zero symbolic errors, lost one case, diversity 0 |
| 2026-07-19 | Relational operator ablation (`docs/analysis/relational-operator-ablation-dossier-2026-07-19.md`) | relations as **CGA dilation** (`VersorBinding`) | **Identical to rational baseline** (2/8 both); depth metadata inert; enrich=decoration |
| 2026-07-28 | ADR-0252 §5 (`docs/research/sme-experiment-verdict-797ebad5.md`) | structure as **point configurations**, Procrustes | **NO-GO** at every attribute weight |

**Convergent mechanism:** wherever the geometric operation is isomorphic to the arithmetic it replaces, it reproduces it exactly and adds nothing — zero diversity is near-tautological, not disappointing. And all three hit the same binding constraint: **the reader** (6/8 refused; 5/500 decided; 1.28% read). **Reopening criterion, stated so this is never re-proposed blind:** a domain where the geometric encoding is *not* isomorphic to a trivial symbolic computation — which is precisely what FA-1's holonomy-resonance question is, and why it, not a fourth operator-arithmetic ablation, is the next experiment.

---
*Method note: every claim above carries a path. The audit inherits the standing philosophies — red-before-green for every new pin, measure before ruling, record the error next to the fix — and the census, read-rate, and seam maps become pinned lanes so the audit's own instruments cannot go stale the way the ones it replaces did.*
