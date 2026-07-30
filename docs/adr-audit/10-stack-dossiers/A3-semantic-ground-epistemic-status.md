# Stack dossier — A3 · Semantic Ground & Epistemic Status

**Zone(s):** M1 · `vocab-manifold`, `L3-packs`, `alignment-resonance` (per `docs/assessment/02-layer-taxonomy.md`) | **Tier:** A
**Member ADRs:** ADR-0005 (Language Pack Contract), ADR-0015 (Language Packs as Compiled Linguistic Manifolds), ADR-0021 (Epistemic Grade Policy) — read in that order
**Dossier author:** ADR-Audit Tier-A subagent, Batch 1 | **`verified_at` SHA:** `cbfc8ccb`
**Prior evidence adopted, not re-derived:**

- **FA-1 verdict** — `docs/analysis/fa1-holonomy-gate-verdict-2026-07-28.md` (**NO-GO**, AUC 0.557 vs. required ≥0.80; word-order sensitivity 0.644 vs. required ≥0.90). Adopted as given per the charter's "settled rulings are constraints, not subjects."
- **FA-1 pre-registration** — `docs/analysis/fa1-holonomy-gate-preregistration.md` (criterion + anti-gaming rules committed before the run).
- **FA-1 substrate finding** — `docs/analysis/logos-substrate-collapse-2026-07-28.md` (six code-level defects; the `_blend_feature_versors` overwrite; 37 lost coordinates; 63/83 inert alignment edges; the deleted reverse walk at `fca6216e`).
- **Gap register** — `docs/assessment/30-gap-register.md` **G-25** (three-layer entry: seeded → destroyed-at-compile-time → ruled/retired) and **G-24** (perception layer; the sibling arc that establishes template-match became the de-facto criterion of meaning *because* this stack's gate never fired).
- **Layer card** — `docs/assessment/10-layer-cards/M1-knowledge-memory.md` (zone roster; `vocab-manifold` **live-serving**, `alignment-resonance` **live-internal**; fitness `fit` with named wrinkles).
- **Hindrance audit** — `docs/assessment/31-hindrance-audit.md` (checked; no H-N entry covers this stack — `logos_error` telemetry at `core/cognition/pipeline.py` is the only adjacent line).
- **Prior clause-level negative** — `docs/analysis/holonomy-resonance-proof-not-robust-2026-06-14.md` (the 2026-06 result FA-1 supersedes with a clean ground).
- **Deferred-question record** — `docs/handoffs/ADR-0167-FOLLOWUPS.md` §6, which pre-registered the exact defect FA-1 later measured (see §3, "The forecast that was filed and never collected").

**Not re-run:** FA-1's experiment. **Freshly measured here:** implementation state at `cbfc8ccb` (FA-1 measured at `472fc0a8`/`339bfd37`), the ADR-0021 machinery end-to-end, and the corpus-wide cascade.

---

## 0. Why this is one stack

ADR-0005 and ADR-0015 are one decision written twice, one day apart. ADR-0005 (2026-05-12) specifies the *contract* — what a language pack must contain and the eight gates it must pass to activate. ADR-0015 (2026-05-13) specifies the *object* — that a pack is not a dataset but a compiled linguistic manifold, and that the decisive proof of the three-language design is dynamic cross-language holonomy resonance. ADR-0005's gate 7 ("Alignment gate") and ADR-0015's "Crown Proof: Holonomy Resonance" are the same claim at two strengths: *alignment records exist and verify* (0005) and *alignment establishes resonance strong enough to validate meaning* (0015). FA-1 measured the stronger one and refused it; ADR-0005's amendment records that the weaker one was implemented as destruction.

ADR-0021 (2026-05-16) joins the stack not by subject but by jurisdiction: it defines the `SPECULATIVE`/`COHERENT`/`CONTESTED`/`FALSIFIED` regime under which every claim this stack produces — every lexical row, every alignment edge, every pack ratification — is supposed to be graded and kept revisable. It is the typed surface on which a verdict like FA-1's is supposed to land. Whether it can actually receive that verdict is this dossier's second question, and the answer is no (§2, ADR-0021, and `AA-A3-19`).

Not a phased family — three independent ADRs bound by a shared substrate, which is why the stack-level synthesis (§3) carries more weight here than the per-ADR cards.

## 1. Stack-level claim

> **The three languages — English as articulation base, Hebrew as depth-root, Koine Greek as depth-relation — are three charts on one shared geometric semantic space; a language pack is the compiled manifold that realizes one chart; cross-language holonomy closure over aligned clauses is the proof that the charts agree, and therefore the validation gate of meaning; and every claim admitted through that gate carries a typed, permanently revisable epistemic position rather than a source-trust tier.**

The middle clause is falsifiable and was falsified. The outer clauses are not, and survive.

- **Pre-registered criterion:** `docs/analysis/fa1-holonomy-gate-preregistration.md`, registered at `94f05ba8` before any number existed, with four gates — **G1** separation AUC ≥ 0.80 over all negatives; **G2** hardest class (cross-pair) AUC ≥ 0.75; **G3** word-order sensitivity ≥ 0.90 (ADR-0015's own stated test, *"word-order changes should change holonomy"*); **G4** `coordinates_lost == 0` (no collapse re-entry). Anti-gaming rule 4 required controls to be reported.
- **Measurement performed / already available:** `evals/logos/fa1_gate.py`, deterministic and bit-reproducible, run 2026-07-28 on a repaired ground (`evals/logos/repaired_ground.py`) after `evals/logos/manifold_collapse.py` established the ground was collapsed. Corpus: 83 authored edges, 59 resolved under R3, 24 concepts, 2,024 clause sets, 1,016 aligned pairs, 58,375 mechanically-generated negatives in three classes.
- **Verdict: NO-GO.** G1 **0.557** (chance 0.500), G2 **0.664**, G3 **0.644**, G4 **0** ✓. The instrument is sound — max self-loop deviation `d(A,A) = 3.6e-06` across all 1,016 pairs, so a null result is a measurement and not a broken metric. Diagnosis, adopted verbatim: the encoding reacts more strongly to *reordering* a clause (median 41.2) than to *changing what it is about* (32.2) — it measures path shape, not content. The negative classes order correctly by meaning-distance (aligned 27.20 < lexical 32.17 < word-order 41.17 < cross-pair 53.23), so the geometry is weak signal, not noise. The design asked for a gate; the measurement delivered a correlation.

**A second falsifiable claim in this stack has *not* been measured and is flagged here:** ADR-0005's gate 7 in its weaker token-level form — *do individual aligned versors sit closer than unaligned ones on the repaired ground?* FA-1 §4 explicitly excluded it ("a narrower claim than the clause gate… It is worth measuring honestly. It is not this result and cannot be used to soften it"), and the four tests that nominally proved it are decoration (`logos-substrate-collapse` §3). **Status: not yet measured — flagged for a follow-on FA-style experiment** (`AA-A3-9`).

**A third, also unmeasured:** the coupling-strength question. Cross-language alignment strength is declared `0.10`; FA-1 §4 notes a stronger coupling would raise separation and at `1.0` would reach it trivially by re-collapsing the manifold. Any future test must carry the criterion FA-1 specified — *separation must improve faster than distinctness degrades*, both measured — or the improvement is collapse arriving by a slower road (`AA-A3-10`).

## 2. Per-ADR sections

### ADR-0005 — Language Pack Contract

**Audit ID (if a numbering collision):** none | **Family (if phased):** none
**Zone / stack:** M1 · `L3-packs` (contract surface), `alignment-resonance` (gate 7) | **Tier:** A
**ADR status (as recorded in the file):** Accepted; Validation-Gates section carries a 2026-07-28 amendment | **ADR date:** 2026-05-12
**Card author:** ADR-Audit Tier-A subagent | **`verified_at` SHA:** `cbfc8ccb`

---

#### 1. Content summary

- **Decision made:** Adopt a Language Pack Contract as the canonical template for all CORE language packs — each pack a deterministic, versioned manifold bundle with identity/normalization, lemma-first lexicon, morphology, syntax/frames, semantic lift into CORE-native pressure, readback to surface language, and validation probes/alignment gates. Three canonical packs: `en` (articulation base), `he` (depth 1), `el` (Koine Greek, depth 2). No pack may define private or opaque semantics that bypass the shared field.
- **Alternatives explicitly rejected:** loose plugin API (too weak to enforce invariants); dictionary-only packs (lexicons don't articulate or lift); tokenizer-first packs (tokens are surface artifacts); LLM-as-extraction-engine (introduces a D3 nondeterministic oracle at the normalization site — defers to ADR-0002).
- **Artifacts the ADR claims will exist:**
  - `packs/common/contracts/language-pack.md`
  - `packs/common/schema/{lemma,morphology,frame,sense,probe}.schema.json`
  - `packs/common/anchors/trilingual-anchor-template.json`
  - `packs/{en,he,el}/pack.toml`, `orthography.yaml`, `lemmas.jsonl`, `morphology.jsonl`, `frames.jsonl`, `senses.jsonl`, `lift_rules.py`, **`readback_rules.py`**, `validators.py`, `probes/`, `corpora/manifest.yaml`
  - Pack ids exactly `en`, `he`, `el`
  - **Eight ordered validation gates** — schema, lexical, morphology, lift, readback, determinism, alignment, coverage — a pack "becomes active only when it passes the following gates **in order**"
  - Design Rule 6: packs publish anchor records verifiable against the trilingual anchor template; "cross-language coherence is a probe surface, not an emergent hope"
  - Runtime Boundary Honesty: unspecified semantic boundaries raise `NotImplementedError` at exactly that boundary

#### 2. Implementation cross-reference

| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `packs/common/contracts/language-pack.md` | yes | `packs/common/contracts/language-pack.md` | Present. |
| 5 JSON schemas | yes | `packs/common/schema/{lemma,morphology,frame,sense,probe}.schema.json` | All five present. |
| `trilingual-anchor-template.json` | yes | `packs/common/anchors/trilingual-anchor-template.json` | Present. |
| `packs/en/`, `packs/he/`, `packs/el/` structure | partial | `packs/{en,he,el,grc}/` | Directories exist; **`readback_rules.py` is absent from all four** (`find . -name readback_rules.py` → 0 hits repo-wide). |
| `lemmas.jsonl` (lemma-first inventory) | partial | `packs/en/lemmas.jsonl` (5 lines), `he` (10), `el` (5), `grc` (12) | Seed-scale. `morphology.jsonl`: 9/8/7/7 lines. |
| `lift_rules.py` | yes (thin) | `packs/en/lift_rules.py:13` | 14 lines; delegates to `packs/common/runtime_rules.py::lift_from_pack`. Identical across all four packs modulo the `language=` argument. |
| Pack ids `en` / `he` / `el` | **contradicts** | `packs/el/pack.toml:1` (`pack_id = "el"`), `packs/grc/pack.toml:1` (`pack_id = "grc"`) | **Two directories for one language**, byte-identical rationale comments. Serving and ADR-0015 both use `grc`. See `AA-A3-3`. |
| Eight ordered validation gates | **no** | — | No gate sequencer exists. `gate_engaged` is a single manifest boolean, consulted at `sensorium/registry.py:103,124,165,197`. Seven of the eight gates have no code that runs them. |
| Design Rule 6 — anchor records verifiable | partial | `packs/data/*/alignment.jsonl` (85 rows across 4 packs) | Edges authored. `packs/compiler.py:621` `_PREFIX_TO_PACK` is a frozen three-entry table; `_infer_foreign_pack_ids` splits `target_id` on `"-"`, so **63 of 83 edges resolve to nothing**, silently (`continue`, no warning/counter/test). Confirmed still frozen at `cbfc8ccb`. |
| Runtime Boundary Honesty (`NotImplementedError`) | no | — | Zero `NotImplementedError` in `packs/*/lift_rules.py` or `packs/*/validators.py`. The rule is not implemented as stated; the boundaries were filled by delegation instead. |
| Packs on the serving path | **no** | `chat/runtime.py:113` | Serving imports `packs.{OOVPolicy, load_mounted_packs, load_pack, load_pack_entries}` over `packs/data/<pack_id>/`. `packs/{en,he,el,grc}` are never imported; ADR-0253 §4 rules them draft/source only. Every `pack.toml` still says `status = "draft"`. |

**Build axis: scaffolded.** The *common* surface is real (contracts + 5 schemas + anchor template all present). The *per-language* surface is a seed-scale draft tree that is not on the serving path, is missing an entire named artifact class (`readback_rules.py`, 0 of 4), and carries a duplicate identity for Greek. The gate regime — the ADR's central enforcement mechanism, "a pack is not considered active because files exist" — is one boolean where eight ordered gates were specified. Decided by the gate row and the `readback_rules.py` row.

#### 3. Liveness / integration

The contract's *shape* is live in a different tree than the one this ADR specifies. `packs/data/<pack_id>/` — manifest + lexicon + morphology + glosses + alignment — is the real, compiled, serving artifact, mounted through `packs/compiler.py` and reached from `chat/runtime.py`. `packs/{en,he,el,grc}/` is unreached. So the ADR's *idea* (deterministic checksummed pack bundle, lemma-first, shared field target) survives in the serving tree; the ADR's *specified files* do not run.

Gate 7's mechanism is live and destructive. `_apply_alignment_corrections` (`packs/compiler.py:428`), `_apply_mounted_primary_domain_resonance` (`packs/compiler.py:617`) and `_apply_morphology_cluster_corrections` (`packs/compiler.py:327`) all call `_blend_feature_versors`, which at `cbfc8ccb` still reads:

```python
def _blend_feature_versors(source, target, strength):
    strength = max(0.0, min(1.0, float(strength)))
    if strength <= 0.0:
        return np.asarray(source, dtype=np.float32).copy()
    return np.asarray(target, dtype=np.float32).copy()   # any strength > 0
```

**Sabotage test — three separate answers, which is the finding:**

1. *Remove the `packs/{en,he,el,grc}` draft tree entirely.* Nothing observable changes. Nothing imports it. **Decoration.**
2. *Stub `gate_engaged` to always-true.* Nothing changes for the four logos packs — all four already declare `"gate_engaged": true` in `packs/data/*/manifest.json`. The gate is a constant on the path that matters.
3. *Stub `_blend_feature_versors` to a no-op returning `source`.* **37 coordinates come back.** `evals/logos/manifold_collapse.py` measures 239 surfaces → 202 distinct on the trilingual mount; disabling the mount-time site alone moves it 37 → 3. This mechanism is not decoration — it is live, load-bearing, and doing the opposite of what the ADR decided.

**Liveness axis: live (harmfully) for gate 7's mechanism; dead for the specified pack tree.** The one part of this ADR that is unambiguously live on the serving path is the part FA-1 proved is destroying the distinctions the ADR exists to preserve.

#### 4. Design fidelity — pillars and axioms

Scoring the decision *as written* (2026-05-12), independent of build.

| Pillar | Honors / Tension / Violates | Citation |
|---|---|---|
| I. Mechanical Sympathy | **Honors** | Rationale §: "a small, explicit, cheap-to-validate pack surface." Deterministic NFC normalization, checksummed bundles, D0/D1 determinism gate — all cheap and machine-legible. |
| II. Semantic Rigor | **Tension** | The decision is *about* semantic rigor ("all packs target shared field primitives instead of inventing language-private meanings") and largely achieves it — but it assigns Koine Greek the id `el` in the canonical table while the companion ADR-0015 (next day) and every downstream artifact use `grc`. Pillar II is "every term has one precise, non-negotiable meaning"; the language's own name got two. |
| III. Third Door | **Honors** | Four named alternatives rejected with reasons, including the two obvious industry paths (loose plugin API, tokenizer-first). LLM-as-extraction rejected on determinism grounds with a cross-reference. Textbook Third Door. |

| Axiom | Honors / Tension / Violates | Citation |
|---|---|---|
| 1. Geometry-First | **Honors** | Design Rule 4 "Shared field target": semantic lift must target shared CORE field primitives; "what cannot be expressed in shared primitives must be proposed as a new shared primitive, not hidden inside a pack." The intrinsic space is found before the structure. |
| 2. Field-State | **Honors** | Lift produces `CandidateGeometricPressure` into a field, not records into a table. Gate 5 reads *back from field state*. |
| 3. Propagation-over-Mutation | **Tension (as written) / Violates (as built)** | The ADR is silent on *how* alignment moves a versor, which is the gap the implementation filled with overwrite. An axiom-3-faithful contract would have specified propagation through the versor group; the omission is what let `_blend_feature_versors` be written. The 2026-07-28 amendment now supplies the missing clause: "alignment must be *interpolation on the versor group*, never replacement." |
| 4. Dual-Correction | **Honors** | Lift (gate 4) and readback (gate 5) are specified as a forward/conjugate pair, each with its own gate. This is the axiom stated structurally — and it is precisely the half (`readback_rules.py`) that was never built. |
| 5. Reconstruction-over-Storage | **Honors** | Lemma-first over token-first (Design Rule 1) is exactly reconstruct-from-structure rather than store-every-surface. "Opaque embedding tables" explicitly Forbidden. |
| 6. Compilation-Last | **Honors** | Structure (lemma, morphology, frame, sense) is specified before any file format; `.jsonl`/`.toml` choices are named last, in the Required Structure section. |
| 7. Reality-over-Inheritance | **Honors (in form) / untested (in fact)** | The gate regime is the axiom's enforcement arm — "a pack is not considered active because files exist." That is exactly reality-over-inheritance. Seven of the eight gates were never implemented, so the axiom's own instrument was inherited rather than built. The 2026-07-28 amendment is the axiom finally operating on this ADR. |

#### 5. Build fidelity — does the code match the decision?

Three divergences, in descending severity.

1. **Alignment is implemented as its own negation.** The ADR's Design Rule 6 and gate 7 require alignment to make cross-language coherence a *verifiable probe surface*. The implementation makes an aligned token *become* its partner, bit for bit. FA-1 measured `cga_inner(light, אוֹר) == cga_inner(light, light) == 3.0220894813537598` — the versors are the same array. Nine English question words (`ask/how/question/what/when/where/which/who/why`) occupy one coordinate because one Greek verb `ἐρωτάω` shares their primary semantic domain and drags the group into the multi-language branch. The role assignment inverts: `_apply_mounted_primary_domain_resonance` prefers English as the prototype (`next((surface for language, surface in surfaces if language == "en"), surfaces[0][1])`), so the *depth* languages are deleted into the *articulation* surface — exactly backwards from the ADR's Context, which names Hebrew and Greek as the sources of depth. At pack-load time the foreign packs run in `sorted()` order, so which language a Hebrew token becomes is decided by the alphabetical order of pack ids.

2. **The gate sequence does not exist.** Eight ordered gates, one boolean. All four logos packs declare `"gate_engaged": true` with `"provenance": "adr-0103:reviewed:2026-05-22"`. No code runs the schema, lexical, morphology, lift, readback, determinism, alignment, or coverage gate as a precondition of activation.

3. **The specified tree is draft and off-path.** `readback_rules.py` — one of eight named per-pack artifacts and the conjugate half of the ADR's dual-correction pair — exists nowhere in the repository. Every `pack.toml` says `status = "draft"`. ADR-0253 later ruled this tree non-authoritative for serving, which resolves the ambiguity but leaves the ADR's Required Structure describing files that no longer have a job.

**Build-fidelity axis: contradicts.** Not "partial drift" — the central mechanism (alignment) performs the inverse of the decided operation, and the central enforcement mechanism (the eight-gate sequence) is absent. The 2026-07-28 amendment states this accurately in-file; the code at `cbfc8ccb` is unrepaired, by deliberate disposition (repair admitted to the keel, not patched here — `logos-substrate-collapse` §8).

#### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs

- **Contradicts `Whitepaper.md`?** Not as written. As built, the implementation contradicts Axiom 3 (Propagation-over-Mutation, §III) — overwrite is the purest possible stepwise mutation — and hollows Axiom 5 (Reconstruction-over-Storage), since collapsed coordinates cannot reconstruct what they no longer distinguish.
- **Contradicts `Yellowpaper.md`?** No. The Yellowpaper defers to the Whitepaper for axioms/pillars and does not independently constrain the pack contract.
- **Other ADRs:**
  - **ADR-0015** (next day) — companion, not conflict, except on the Greek pack id (`el` vs `grc`). Their gate-7/Crown-Proof pair is one claim at two strengths; both amended 2026-07-28.
  - **ADR-0253 §4** — *supersedes the Required Structure's serving authority*: "Runtime serve/load of language packs uses `packs.compiler` → `packs/data/<pack_id>/` only. `packs/he`, `packs/grc`, and peer source trees are draft/source material; they are not serve-import authority." Clean supersession, explicitly stated, with architecture tests pinning it — but ADR-0005 was never annotated to say so.
  - **ADR-0007 §Related** cites ADR-0005 for "lift and readback rule interfaces" — an interface that is half-absent.
  - **ADR-0006** builds on pack readback (`en/readback_rules.py`, `he/…`, `el/…` named directly) — same absent interface, and it uses the `el` id.
  - **SESSION-2026-05-12-language-packs-addendum** — the companion session record; restates "Cross-language alignment is an explicit probe surface, not an emergent hope" and "Pack activation is gate-based, not file-existence-based." Both now measured false in implementation.
  - **ADR-0102/0103** ratified the four `packs/data` logos packs as `reasoning-capable` on 2026-05-22, over exactly the alignment machinery FA-1 later measured.
- **Continuity axis: unreconciled contradiction.** Two live, unreconciled items: (a) the Greek pack id (`el` in ADR-0005's canonical table, `grc` everywhere that runs) has never been reconciled by any ADR; (b) ADR-0253's supersession of the Required Structure's authority is recorded only in ADR-0253, not here. The FA-1 amendment is itself a *clean* reconciliation and is the model for how these two should be closed.

#### 7. Necessity / generality

1. **Necessity.** The *contract idea* is irreducible and earned: something must specify what a pack contains, that packs target shared primitives rather than private semantics, and that activation is earned rather than assumed. Remove it and packs become the "opaque embedding tables" the ADR forbids. What is *not* necessary is this ADR's particular eight-gate ordering — seven of the eight were never built and the system shipped, which is the sabotage test answering itself.
2. **Reducibility.** Gate 7's *mechanism* reduces cleanly to L0. The correct alignment operation — geodesic interpolation on Spin(4,1) — has shipped in `algebra/rotor.py` since the algebra layer's first commit: `geometric_product(rotor_power(word_transition_rotor(source, target), strength), source)`. FA-1 measured it: unit residual ~`1e-7` for every `t`, `t=0` returns source exactly, `t=1` target exactly. The pack layer wrote a worse operator over the top of a correct one already present one import away. `_blend_feature_versors` is **reducible-to-`algebra/rotor.py::rotor_power`+`word_transition_rotor`** with no loss. Cross-reference stack **A1 (Algebra & Geometry Foundations, ADR-0001/0003/0004)** — the rotor-as-operator decision is the general mechanism this ADR's alignment nudge is a narrower, incorrect instance of. *A1's dossier should be checked for whether it independently identified `rotor_power` as an under-consumed general operator; this dossier asserts it from the pack side without access to A1's output.*
3. **Extensibility.** The contract generalizes well and already has: `ADR-0091` (Domain Pack Contract v1) is the same shape for non-language packs, `ADR-0027` (identity packs) is explicitly modeled on it ("same as language packs"), and `ADR-0013`'s `ModalityPack[S]` is the multimodal sibling. Candidate consolidation pairing: **ADR-0005 + ADR-0091 + ADR-0027 + ADR-0013 → one pack-contract primitive with role-specific gate sets.** Flag for `22-consolidation-report.md`.

**Necessity/generality axis: irreducible (contract) / reducible-to-`algebra/rotor.py` (alignment mechanism) / generalization-candidate (pack contract itself).** Three different answers for three parts of one ADR, which is itself evidence the ADR bundles separable decisions.

#### 8. Fitness / value

- **Positive, measured:** 24 cross-language concepts across three languages with 59 edges resolving under FA-1's R3 repair, and Hebrew root folding into geometry at compile time (`triliteral:` tokens) — both explicitly preserved by the FA-1 verdict (§5 item 2) as "a smaller, earned role."
- **Positive, structural:** the common contract surface (5 schemas + anchor template + contract doc) is complete and is the shape ADR-0091/0027/0013 successfully reused.
- **Negative, measured:** mounting the depth packs *removes* 37 distinct coordinates (`evals/logos/manifold_collapse.py`; pinned bidirectionally by `tests/test_manifold_collapse_floor.py` in `smoke`). English alone is collision-free (220/220); English mounted with Hebrew and Greek is not (239→202). The operation designed to add depth subtracts it.
- **Negative, measured:** 63 of 83 authored alignment edges are inert, including *all* edges of `he_core_cognition_v1` and `grc_logos_cognition_v1` — the two packs `chat/pack_grounding.py:56–57` actually grounds Hebrew and Greek against in serving.
- **Negative, measured:** four token-level "resonance proof" tests pass because the compared arrays are identical (`logos-substrate-collapse` §3), including one named for an *improvement in resonance* that is green precisely because the distinction it should preserve was destroyed.
- **Layer card:** `M1-knowledge-memory.md` grades the layer `fit`, but on the strength of exact recall + the epistemic-status regime; its zone roster marks `alignment-resonance` **live-internal** (not live-serving), which is consistent with everything above.

**Fitness axis: mixed, net negative on the alignment surface.** Cited: `docs/analysis/logos-substrate-collapse-2026-07-28.md` §1 (37 coordinates, bit-exact), §3 (four decoration tests), §4 (63/83 inert); `docs/analysis/fa1-holonomy-gate-verdict-2026-07-28.md` §5 item 2 (what is earned). The contract surface delivered reuse; the alignment surface delivered measured harm.

#### 9. Findings raised

- **`AA-A3-1` 🔴** The eight-gate activation sequence does not exist — `gate_engaged` is one manifest boolean (`sensorium/registry.py:103,124,165,197`) and all four logos packs declare it `true`; seven of eight gates have no implementing code. The ADR's own enforcement principle ("a pack is not considered active because files exist") is itself unenforced. §2, §5.
- **`AA-A3-2` 🔴** `packs.compiler._blend_feature_versors` still returns the target verbatim at `cbfc8ccb`, unrepaired since FA-1 measured it at `472fc0a8`; 37 coordinates remain lost on the trilingual mount in the tree that serves. Deliberate disposition (keel K3), but the serving ground in `../core` is collapsed *today*. §3, §5.
- **`AA-A3-3` 🟡** Semantic Rigor violation, unreconciled: Koine Greek has two pack ids. ADR-0005's canonical table says `el`; ADR-0015, `packs/data/grc_*`, `sensorium/adapters/text.py:203` and all serving use `grc`; `packs/el/` and `packs/grc/` are near-duplicate draft trees with identical rationale comments. §2, §6.
- **`AA-A3-4` 🟡** `readback_rules.py` exists in no pack (0 of 4) and nowhere in the repository, yet it is a named Required-Structure artifact, the subject of gate 5, the conjugate half of the ADR's dual-correction pair, and is cited as an existing interface by ADR-0006 and ADR-0007. §2, §6.
- **`AA-A3-5` 🟡** Design Rule 6 ("a probe surface, not an emergent hope") holds in form and is void in fact: `_infer_foreign_pack_ids`'s frozen three-entry `_PREFIX_TO_PACK` (`packs/compiler.py:621`) makes any pack beyond the original three unreachable *by construction*, discarding 63 of 83 edges with no warning, counter, or test. §2, §8.
- **`AA-A3-6` 🟢** "Runtime Boundary Honesty" (`NotImplementedError` at every unspecified semantic boundary) is unimplemented — zero occurrences in `packs/*/lift_rules.py` or `packs/*/validators.py`. Low severity: the boundaries were closed by delegation rather than left silently open, so the honesty goal is met by other means; but the ADR's stated mechanism is absent. §2.
- **`AA-A3-7` 🟡** Continuity gap: ADR-0253 §4 superseded the Required Structure's serving authority (`packs/he`, `packs/grc` are draft/source only) and ADR-0005 carries no note of it, so ADR-0005 still reads as the live spec for a tree nothing imports. §6.
- **`AA-A3-8` 🔵** Consolidation candidate: ADR-0005 + ADR-0091 + ADR-0027 + ADR-0013 are four instances of one pack-contract primitive with role-specific gate sets. §7.
- **`AA-A3-9` 🟡** The token-level form of gate 7 is *unmeasured* and its four nominal proofs are decoration; FA-1 explicitly deferred it. Needs its own pre-registration before any claim about aligned-versor proximity is made again. §1, §8.
- **`AA-A3-10` 🟢** The coupling-strength question (alignment strength `0.10`) is open and must carry FA-1's stated anti-trade criterion — *separation must improve faster than distinctness degrades, both measured* — or a "stronger coupling" result is re-collapse. §1.

#### 10. Evidence sources actually consulted

Layer card `M1-knowledge-memory.md`; gap register `30-gap-register.md` (G-25 all three layers, G-24); hindrance audit `31-hindrance-audit.md` (searched, no covering entry); FA-1 pre-registration, verdict, and substrate-collapse docs; `docs/handoffs/ADR-0167-FOLLOWUPS.md` §6. **Code read directly at `cbfc8ccb`:** `packs/compiler.py` (`_blend_feature_versors`, all three call sites, `_infer_foreign_pack_ids`, `_PREFIX_TO_PACK`, `_entry_epistemic_state`), `packs/schema.py`, `packs/common/` tree listing, `packs/{en,he,el,grc}/` tree listings + `pack.toml` + `lift_rules.py` + line counts, `packs/data/*/manifest.json` gate/provenance fields, `packs/data/*/alignment.jsonl` line counts, `sensorium/registry.py`, `sensorium/adapters/text.py`, `chat/runtime.py`, `algebra/holonomy.py`. Repo-wide `find` for `readback_rules.py`. `evals/logos/` listing. **Not consulted:** `docs/census/<sha>/stale-references.jsonl` (uncommitted at audit time — `docs/census/` shows as untracked in `git status`).

---

### ADR-0015 — Language Packs as Compiled Linguistic Manifolds

**Audit ID (if a numbering collision):** none | **Family (if phased):** none
**Zone / stack:** M1 · `vocab-manifold`, `alignment-resonance` | **Tier:** A
**ADR status (as recorded in the file):** "Accepted — **Crown Proof section AMENDED 2026-07-28: measured and not supported**" | **ADR date:** 2026-05-13
**Card author:** ADR-Audit Tier-A subagent | **`verified_at` SHA:** `cbfc8ccb`

---

#### 1. Content summary

- **Decision made:** A CORE language pack is a deterministic, checksummed, **compiled linguistic manifold** — not a dataset, not a translation table — containing a manifest (role, script, normalization, source manifest, determinism class, checksum, gate state, OOV policy), lexical + morphology entries, grammar attractors, cross-language resonance edges, and holonomy alignment cases. Three languages carry distinct architectural roles (English operational/articulation, Hebrew depth-root, Koine Greek depth-relation). **Crown Proof:** aligned clauses' holonomies resonate across languages while unrelated clauses stay distinct and word-order changes change holonomy — "This is the CORE-Logos proof." **Amended 2026-07-28: the Crown Proof is retired.**
- **Alternatives explicitly rejected:** packs as token-lookup wrappers (the `sensorium/adapters/text.py` scaffold's prior state, named as insufficient); packs as datasets or translation tables; LLM extraction feeding the gate ("Structural segmentation only").
- **Artifacts the ADR claims will exist:**
  - `packs/schema.py` — terminology and schema foundation (Implementation Order item 1)
  - Terminology Boundary as enforced types: vocabulary point ≠ transition rotor ≠ persona motor ≠ grammar attractor ("conflating point and operator is an algebraic category error")
  - Pack roles + OOV policy in `sensorium` (item 2) — Hebrew/Greek **fail closed** during and after seeding
  - Text adapters split into English / Hebrew / Koine Greek specializations (item 3)
  - Grammar scaffold artifacts / grammar attractors (item 4)
  - Tri-language resonance graph — "a weighted graph, not a translation table" (item 5)
  - Holonomy resonance proof cases (item 6)
  - Hebrew composition order `V_surface = (((V_root · M_stem) · M_inflection) · M_affix_chain)`
  - Manifest fields: role, script, normalization, source manifest, determinism class, checksum, gate state, OOV policy
  - Aligned clauses resonate **"without flattening their distinctions"**

#### 2. Implementation cross-reference

| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `packs/schema.py` | yes | `packs/schema.py` | Present, 7.4 KB. All frozen slotted dataclasses. |
| Terminology Boundary as types | yes | `packs/schema.py:20,35,44,88,119,149,166,181` | `LanguageRole`, `OOVPolicy`, `LanguagePackManifest`, `MorphologyEntry`, `LexicalEntry`, `GrammarAttractor`, `AlignmentEdge`, `HolonomyAlignmentCase`. Point/operator separation is genuinely honored — no rotor type in the pack layer. |
| `LanguageRole` roles | partial | `packs/schema.py:23–31` | `OPERATIONAL_BASE`, `ARTICULATION_SURFACE`, `DEPTH_ROOT`, `DEPTH_RELATION` — plus `domain_seed` widened by ADR-0097. **G-25's sixth defect stands:** `role: "collapse_anchor"` (`en_collapse_anchors_v1`) is not a member, so that pack cannot be loaded at all yet is registered and consumed via a raw path bypassing the loader — and is the target of all 24 still-unresolved alignment edges. |
| OOV fail-closed for he/grc | yes | `sensorium/adapters/text.py:189–211` | `hebrew_pack` and `koine_greek_pack` both `OOVPolicy.FAIL_CLOSED`. Correct and matches the ADR exactly. |
| Text adapters split 3 ways | yes | `sensorium/adapters/text.py:175,187,201` | `english_pack` / `hebrew_pack` / `koine_greek_pack`. Uses `grc`, not ADR-0005's `el`. |
| Gate state per role | **contradicts across trees** | `sensorium/adapters/text.py:194,209` vs `packs/data/{he,grc}_*/manifest.json` | Adapter mounts he/grc `gate_engaged=False` "until Supervised Seeding Epoch completes" (matching this ADR's Negative consequence). All four `packs/data` logos manifests declare `"gate_engaged": true`, provenance `adr-0103:reviewed:2026-05-22`. Two pack systems, opposite answers, same languages. |
| `GrammarAttractor` | **scaffolded** | `packs/schema.py:149`, `packs/__init__.py:13,40` | Type defined and exported. **Zero runtime constructions** — `rg 'GrammarAttractor' --type py -g '!tests/**'` returns only the definition and the export. No pack data file carries attractors. |
| Tri-language resonance graph | partial | `packs/data/*/alignment.jsonl` (85 rows: grc-cog 42, he-cog 23, he-micro 11, grc-micro 9) | `AlignmentEdge` (`packs/schema.py:166`) carries `weight ∈ [0,1]` — genuinely a weighted graph, as decided. But 63/83 resolve to nothing and the 20 that resolve are applied as overwrites, making it a *translation table applied destructively* — the exact thing the ADR forbids by name. |
| `HolonomyAlignmentCase` | **ghost** | `packs/schema.py:181` | Type exists with two `ValueError` guards. Constructed **only in `tests/test_alignment_graph.py`**. No `packs/data/*` file carries a case; nothing in serving builds one. Docstring still reads *"Crown proof case for the three-language design… aligned canonical clauses produce nearby holonomies without flattening their distinctions"* — the retired claim, live in code at `cbfc8ccb`. |
| Hebrew composition order | partial | — | `triliteral:` root folding into geometry at compile time is real and explicitly preserved by FA-1 §5 item 2. The full four-factor chain `(((V_root · M_stem) · M_inflection) · M_affix_chain)` was not verified as a distinct composition site in this pass. |
| Manifest fields | yes | `packs/data/*/manifest.json` | `determinism_class: "D0"`, `gate_engaged`, `provenance`, checksums present. |
| "without flattening their distinctions" | **contradicts** | `packs/compiler.py:129–133,617` | The mount flattens 37 coordinates. `דבר`, `דברים`, `λόγος` and `word` are bit-identical. |

**Build axis: partial.** The schema/terminology foundation (Implementation Order items 1–3) is genuinely built and genuinely good — the point/operator separation the ADR calls an "algebraic category error" to violate is correctly enforced by the type system, and the OOV fail-closed policy is exactly as decided. Items 4–6 are scaffold-to-ghost: grammar attractors are a type with no instances, the resonance graph is 76% inert, and the holonomy proof cases exist only inside tests. Decided by the `GrammarAttractor` and `HolonomyAlignmentCase` rows.

#### 3. Liveness / integration

The schema layer is live: `packs/compiler.py` builds `LexicalEntry`/`MorphologyEntry` from `packs/data/*`, `chat/runtime.py:113` reaches it, `vocab-manifold` is confirmed live-serving by the M1 layer card. The Crown Proof machinery is not: `holonomy_encode` is reachable from `core/physics/biography.py` (ADR-0240's Biography Blade), **not** from any cross-language validation path. G-25 records it exactly: *"no path consults cross-language holonomy as a gate — template match became the de-facto criterion of meaning instead"* — which is the seam to G-24's perception finding.

**The instrument itself does not compute what it is named for.** `algebra/holonomy.py::holonomy_encode` at `cbfc8ccb`:

- Docstring (lines 56–66) still states: *"Forward walk: F = w1 * … * wn · Reverse walk: R = (1-alpha) * reverse(wn) * … * reverse(w1) · Holonomy: H = F * R · The walk closes."*
- Implementation (lines 72–92) accumulates `F` only and `return _word_versor(F)`. There is no `R`.
- `alpha` is validated (`if not 0.0 <= alpha <= 1.0: raise`) at line 69 and then **never read again**. `holonomy_encode(v, alpha=0.0)` and `holonomy_encode(v, alpha=1.0)` return bit-identical arrays. `core/physics/biography.py:94` passes `alpha=alpha` into it.
- Deleted at commit `fca6216e` ("Stabilize holonomy accumulation", 2026-05-13 — the same day this ADR was written); the original at `b80dd57a` did compute `H = geometric_product(F, R)`. The docstring was kept.

**Sabotage test.** Stub `holonomy_encode` to return its first argument. The cross-language validation gate: **nothing changes** — no serving path consults it, so this half is decoration, and has been since `fca6216e`. The biography path: ADR-0240's Blade changes, so *that* consumer is live (see the cascade, §3). And the `alpha` parameter specifically: stubbing it to a constant changes **nothing at all**, today, because it is already inert — a caller steering a parameter that does nothing.

**Liveness axis: split — live for the schema/terminology layer, dead for the Crown Proof.** The ADR's decisive claim was never wired to a gate, and the object it was supposed to be computed from stopped closing on the day the ADR was written.

#### 4. Design fidelity — pillars and axioms

Scoring the decision *as written* (2026-05-13), pre-amendment, since that is what the charter asks.

| Pillar | Honors / Tension / Violates | Citation |
|---|---|---|
| I. Mechanical Sympathy | **Honors** | "deterministic, checksummed, compiled" — compilation-time work, checksummed artifacts, D0 ingestion with pinned canonical texts (Negative consequence 3). Nothing here asks the machine for anything it is bad at. |
| II. Semantic Rigor | **Honors — exemplary** | The Terminology Boundary table is Pillar II in its purest form: "Vocabulary entries are not transition rotors. Conflating point and operator is an algebraic category error." It also *reserves the right word*: "Morphology is operator composition. Semantic domain is attractor geometry. Alignment is resonance. These must not be collapsed into one multiplication." The implementation then collapsed all three into one multiplication — but the decision named the failure mode in advance. |
| III. Third Door | **Honors** | Rejects both visible options — packs-as-datasets and packs-as-translation-tables — and builds the compiled-manifold path. The Crown Proof is the Third Door's own discipline applied to itself: a falsifiable criterion attached to the novel claim. That is *why* FA-1 could settle it. |

| Axiom | Honors / Tension / Violates | Citation |
|---|---|---|
| 1. Geometry-First | **Honors** | The whole decision is "find the intrinsic space" — three charts on one manifold, before any structure is chosen. |
| 2. Field-State | **Honors** | Grammar attractors seed *structural pressure*, not records; semantic domains are "attractor geometry," explicitly not "opaque morphology factors." |
| 3. Propagation-over-Mutation | **Honors (as written) / Violates (as built)** | "Alignment is resonance" and "cross-language alignment is a weighted graph, **not** a translation table" is the axiom stated precisely. The build is overwrite — the maximal violation. The ADR is not at fault for the build; it is at fault for not specifying the group operation, the same omission as ADR-0005. |
| 4. Dual-Correction | **Violates** | The Crown Proof is a forward operator (`holonomy_encode`) with **no conjugate**. The reverse walk `R` — literally the corrective counterpart, present in the docstring and in the original implementation — was the thing deleted. An axiom-4-faithful design would have made the closure check the gate; instead the gate was defined on a quantity whose closing half was optional enough to delete without anyone noticing for 14 months. This is the sharpest axiom finding in the stack. |
| 5. Reconstruction-over-Storage | **Honors** | "compiled linguistic manifold" over "dataset or translation table" is exactly reconstruct-over-store. OOV policy refuses to collapse unknowns to a shared point — "Returning the same `e1` point for every unknown Hebrew or Greek form erases the distinctions those languages exist to preserve; it is anti-Logos." The implementation then did precisely that to 37 *known* coordinates. |
| 6. Compilation-Last | **Honors** | Implementation Order runs terminology → roles → adapters → scaffolds → graph → proofs. Structure first, artifacts last. |
| 7. Reality-over-Inheritance | **Honors — and is the axiom that closed it** | The Crown Proof was stated as a testable claim with an explicit criterion ("word-order changes should change holonomy"), which is what made the 2026-07-28 amendment possible. The amendment's own line — *"The hypothesis was honestly stated and honestly testable; that is why it could be settled at all"* — is Axiom 7 operating correctly on its own author. |

#### 5. Build fidelity — does the code match the decision?

Two divergences of opposite character.

1. **Where it matches, it matches well.** The Terminology Boundary is enforced by the type system, not by convention: `packs/schema.py` has no rotor type, `LexicalEntry` stores no operator, `GrammarAttractor` is a separate class from both. `OOVPolicy.FAIL_CLOSED` is applied to exactly the two depth languages the ADR names. `AlignmentEdge.weight ∈ [0,1]` with a `__post_init__` guard makes the "weighted graph, not translation table" decision structural. This is high-fidelity work.

2. **Where it diverges, it diverges by deletion with the description left standing.** Three instances of the same pattern, all live at `cbfc8ccb`:
   - `algebra/holonomy.py` — docstring describes `R` and `H = F·R`; code returns `F`. Deleted `fca6216e`, docstring retained.
   - `packs/schema.py:181` `HolonomyAlignmentCase` docstring — *"Crown proof case… nearby holonomies without flattening their distinctions"* — the exact sentence FA-1 retired, still asserted in a live type at HEAD, one day after the amendment landed.
   - `packs/compiler.py:585–600` — a 20-line "ARCHITECTURAL INVARIANT" comment correctly identifying `_apply_mounted_primary_domain_resonance` as "the one place… where DEPTH_ROOT and DEPTH_RELATION packs have their structurally-derived versors blended toward an English prototype," warning that any change "must consider whether the `HolonomyAlignmentCase` proof still demonstrates cross-pack structural divergence rather than blend-induced convergence" — guarding a proof that was blend-induced all along, and citing `docs/handoff/ADR-0167-FOLLOWUPS.md` §6 at a path that does not exist (the file is at `docs/handoffs/`, plural).

3. **The ADR's own Consequences section still lists the retired claim as a Positive.** Line 148: *"Establishes holonomy-level resonance as the validation gate."* The amendment banner at the top strikes it; the bullet is unstruck in place. A reader entering at Consequences — which is where a downstream ADR author looking for what to build on would enter — reads the retired claim as an accepted positive outcome.

**Build-fidelity axis: partial drift, trending to contradicts.** The schema half matches. The proof half contradicts, and does so in the specific mode this repository has named as its own disease: the description of the mechanism outliving the mechanism.

#### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs

- **Contradicts `Whitepaper.md`?** As written: no — it is one of the more axiom-faithful ADRs in Batch 1, with the exception of Axiom 4 (Dual-Correction), where the Crown Proof is a forward operator with no conjugate. As built: yes, on Axiom 3.
- **Contradicts `Yellowpaper.md`?** No.
- **Other ADRs:**
  - **ADR-0005** — companion. Disagrees on the Greek pack id (`el` vs `grc`) and this ADR's usage won. Never reconciled by either.
  - **ADR-0253 §3** explicitly declines to claim the Blueprint's "Holonomy Primacy Rust SIMD" content and reserves **ADR-0261** for it "if implemented later" — an unallocated ADR number reserved for hardening the retired mechanism into Rust SIMD kernels. That reservation now needs a NO-GO annotation (`AA-A3-33`).
  - **ADR-0180 §1** promotes the same mechanism to "the supreme architectural invariant of `core`" in a cross-modal form (see cascade, §3).
  - **ADR-0240/0243/0241/0239** consume `holonomy_encode` for the Biography Blade (see cascade).
  - **ADR-0097** widened `LanguageRole` for `domain_seed`; `collapse_anchor` was never widened (G-25 defect 6).
- **Continuity axis: superseded-cleanly (for the Crown Proof) with one unreconciled residue.** The FA-1 amendment is a model supersession: dated, measured, criterion-cited, tripwire-pinned (`tests/test_fa1_gate_verdict.py`), with an explicit withdrawal condition. The residue is that the supersession stopped at the ADR file — the Consequences bullet, the `HolonomyAlignmentCase` docstring, the `holonomy_encode` docstring, and the compiler's invariant comment all still assert the retired claim in the places a builder would actually read.

#### 7. Necessity / generality

1. **Necessity.** Split cleanly by FA-1's own §5 item 2.
   - **The mechanism — language-pack-as-compiled-manifold — is necessary and salvageable in reduced form.** What survives, unamended by the ADR's own amendment: the three-language architecture with distinct roles, the pack contract, the compiled-manifold discipline, morphology as structure, and Hebrew root folding into geometry at compile time. These are lexical + morphological resources with real cross-language concept alignment (24 concepts, 59 resolved edges). That is a smaller claim than "the validation gate of meaning," and it is earned.
   - **The Crown Proof is not salvageable in this form.** FA-1's diagnosis is structural, not a tuning failure: `F(X)` is an ordered geometric product, so permutation acts on it through non-commutativity — a first-order effect — while substituting one of three factors perturbs it only through that factor's own difference. **Word order is structurally louder than word identity, and meaning lives mostly in identity.** No parameter choice fixes that; it follows from what the encoding *is*. A future meaning gate must come from a construction where content is first-order, not from re-tuning this one.
2. **Reducibility.** Two reductions, both to L0:
   - The alignment operation reduces to `algebra/rotor.py::rotor_power` + `word_transition_rotor` (see ADR-0005 §7 — same finding, same operator).
   - `holonomy_encode`'s *surviving* content is an ordered geometric product with position rotors and periodic renormalization — i.e. `algebra`'s `geometric_product` + `unitize_versor` composed in a loop. Stripped of the deleted reverse walk, it is **reducible-to-`algebra.geometric_product`** and its distinct identity as "holonomy" is now a naming claim rather than a mathematical one. A quantity that never closes is not a holonomy; Pillar II says it should not be called one.
3. **Extensibility.** The *generalization candidate* pointer runs the other way from usual: rather than this mechanism absorbing a narrower one, this mechanism should be **consolidated into whatever the algebra layer measurably delivers**. FA-1's closing register is the map — *"this substrate's value has not been demonstrated in reasoning, while its value in representation (exact recall, versor conditioning, determinism) is measured and holds."* The pack layer's earned role is representation: exact, collision-free, versor-conditioned coordinates for three languages' lexicons and morphologies. **Cross-reference stack A1 (ADR-0001/0003/0004)** — A1 should be checked for (a) whether it independently flagged `rotor_power`/`word_transition_rotor` as under-consumed, and (b) whether the versor-conditioning and exact-recall results it audits are the ones FA-1 names as the measured-and-holding half. *This dossier asserts the pairing from the A3 side without access to A1's output; confirm at rollup.*

**Necessity/generality axis: generalization-candidate — mechanism salvageable in reduced form (lexical/morphological resource + compiled-manifold discipline), Crown Proof irreducibly retired, and both alignment and holonomy reducible to L0 operators in `algebra/`.**

#### 8. Fitness / value

- **Positive, measured:** the terminology/type foundation is reused system-wide and correctly prevents the category error it names — no rotor ever entered the pack layer. The three-role architecture is coherent and referenced by every downstream pack ADR.
- **Positive, measured:** Hebrew `triliteral:` root folding into geometry at compile time — real, working, untouched by the verdict (FA-1 §5 item 2).
- **Positive, methodological — the highest-value item in this stack:** the Crown Proof was stated falsifiably with its own bar ("word-order changes should change holonomy"), which is the sole reason the largest open design question in the system could be closed in one session with a measurement instead of a belief. FA-1 §6 records the accounting. An ADR whose main claim was refuted still delivered more value than an unfalsifiable one that survived.
- **Negative, measured:** AUC 0.557 / G3 0.644 (FA-1). `GrammarAttractor` has zero runtime instances. `HolonomyAlignmentCase` has zero data-file instances. `alpha` inert since `fca6216e`.
- **Negative, measured:** G-25 — "architected, seeded exactly as designed, wired at three mutually-unaware points, load-bearing nowhere," later upgraded to "not under-built, destroyed at compile time."
- **Instruments that now exist because of this ADR's failure, and are assets:** `evals/logos/manifold_collapse.py` (bit-exact, no tolerance to tune), `evals/logos/repaired_ground.py`, `evals/logos/fa1_gate.py`, pinned by `tests/test_manifold_collapse_floor.py` (smoke, bidirectional) and `tests/test_fa1_gate_verdict.py` (tripwire that fires if a future encoding makes the gate real).

**Fitness axis: negative on the claim, positive on the method and the residue.** Cited: `fa1-holonomy-gate-verdict-2026-07-28.md` §1, §3, §5, §6; `logos-substrate-collapse-2026-07-28.md` §5; G-25.

#### 9. Findings raised

- **`AA-A3-11` 🔴** `algebra/holonomy.py::holonomy_encode` docstring still describes the reverse walk and `H = F · R` at `cbfc8ccb`; the code returns `F` only. `alpha` is validated then never read, and `core/physics/biography.py:94` passes it. Docstring-drift defect introduced at `fca6216e` (2026-05-13), unrepaired 14 months later. §3, §5.
- **`AA-A3-12` 🔴** `packs/schema.py:181` `HolonomyAlignmentCase`'s docstring still asserts the retired Crown Proof verbatim — *"aligned canonical clauses produce nearby holonomies without flattening their distinctions"* — in live code, one commit after the amendment. Record/reality divergence per `AGENTS.md` philosophy #5, in the type system rather than the docs. §2, §5.
- **`AA-A3-13` 🟡** ADR-0015's Consequences bullet (line 148) still lists *"Establishes holonomy-level resonance as the validation gate"* as a **Positive**, unstruck. The amendment banner is at the top; a downstream author entering at Consequences reads the retired claim as accepted. §5, §6.
- **`AA-A3-14` 🟡** Two pack systems declare opposite gate states for the same languages: `sensorium/adapters/text.py:194,209` mounts he/grc `gate_engaged=False` "until Supervised Seeding Epoch completes" (matching this ADR's own Negative consequence); all four `packs/data/{he,grc}_*/manifest.json` declare `"gate_engaged": true`. The ADR's stated precondition is simultaneously satisfied and unsatisfied depending on which tree is asked. §2.
- **`AA-A3-15` 🟡** `GrammarAttractor` (Implementation Order item 4) is a ghost — type defined and exported, zero runtime constructions, no pack data file carries attractors. "Semantic domains seed attractors rather than becoming opaque morphology factors" is unbuilt; semantic domains instead drive `_apply_mounted_primary_domain_resonance`, the dominant collapse site (34 of 37 lost coordinates). The attractor path and the collapse path are the same design intent, one built wrong and one not built. §2.
- **`AA-A3-16` 🟡** `HolonomyAlignmentCase` (Implementation Order item 6) exists only in `tests/test_alignment_graph.py`. The "holonomy resonance proof cases" the ADR's Decision names as pack contents are in no pack. §2.
- **`AA-A3-17` 🟡** Axiom 4 (Dual-Correction) violation, design-level: the Crown Proof is a forward operator with no conjugate, and the conjugate that *did* exist (the reverse walk) was deletable without any test noticing. A closure-defined gate should have been unable to pass with the closure removed. §4.
- **`AA-A3-18` 🟢** Stale citation: `packs/compiler.py:598` cites `docs/handoff/ADR-0167-FOLLOWUPS.md` §6; the file is at `docs/handoffs/` (plural — both directories exist, which is why the drift survived). `logos-substrate-collapse-2026-07-28.md` §1 calls it "a file that does not exist" — correct for the cited path, but the content does exist and is materially important (see §3, "The forecast that was filed and never collected"). Correcting the pointer is a one-character fix; the finding is that a real, correct, pre-registered analysis was invisible for want of it. §5.

#### 10. Evidence sources actually consulted

FA-1 verdict + pre-registration + substrate-collapse docs; G-25 (all three layers); M1 layer card; `docs/handoffs/ADR-0167-FOLLOWUPS.md` §6 in full. **Code read directly at `cbfc8ccb`:** `algebra/holonomy.py` (`holonomy_encode` head + body + `holonomy_similarity`), `packs/schema.py` (all eight type definitions, `LexicalEntry` docstring, `HolonomyAlignmentCase` docstring + guards), `packs/compiler.py` (`_apply_mounted_primary_domain_resonance` including its 20-line invariant comment, `_apply_alignment_corrections`, `_apply_morphology_cluster_corrections`, `_infer_foreign_pack_ids`), `sensorium/adapters/text.py:175–211`, `packs/data/*/manifest.json`, `packs/data/*/alignment.jsonl`, `packs/__init__.py`. Repo-wide `rg` for `GrammarAttractor` and `HolonomyAlignmentCase` excluding tests. **Not verified in this pass:** the four-factor Hebrew composition chain as a distinct code site (only `triliteral:` root folding was confirmed via FA-1's evidence) — noted as a gap in this card, not as a clean result.

---

### ADR-0021 — Epistemic Grade Policy

**Audit ID (if a numbering collision):** none | **Family (if phased):** none — but see ADR-0142 (Epistemic State Taxonomy) as the downstream sibling
**Zone / stack:** M1 · `L3-packs` / cross-cuts `L9-epistemic-verdicts` | **Tier:** A
**ADR status (as recorded in the file):** Accepted (no amendment) | **ADR date:** 2026-05-16
**Card author:** ADR-Audit Tier-A subagent | **`verified_at` SHA:** `cbfc8ccb`

---

#### 1. Content summary

- **Decision made:** Adopt an Epistemic Grade Policy with three commitments — (1) `epistemic_status` is a **position in the revision graph, not a trust tier** (`COHERENT`/`CONTESTED`/`SPECULATIVE`/`FALSIFIED`; source labels explicitly excluded from the schema); (2) a **non-hardening invariant** — no claim ever becomes unrevisable, no `final`/`frozen`/`axiom`/`permanent` flag may exist on the runtime data model; (3) **coherence is the only admission signal** — transitions are computed from coherence with the existing reviewed field, never asserted by source authority.
- **Alternatives explicitly rejected:** source-trust tiers (`peer_consensus`, `outsider_empirical`, `established`, `unauthoritative` — named and excluded); removal-instead-of-tagging ("removal loses provenance; uniformity loses revisability"); a censorship layer; a moral filter; language-specific policy.
- **Artifacts the ADR claims will exist:**
  - Four-member status enum
  - `teaching/store.py::PackMutationProposal.epistemic_status: EpistemicStatus = SPECULATIVE`
  - `teaching/review.py` — review outcomes carry the resulting status alongside `ACCEPTED`/`REJECTED_IDENTITY`, "orthogonal and both required"
  - `packs/data/*/lexicon.jsonl` — optional `epistemic_status`, **"default `COHERENT` for the seed vocabulary"**
  - `core/cognition/trace.py` — status folded into `trace_hash`
  - `tests/test_epistemic_invariants.py` — asserts no schema field/relation/flag admits a non-revisable state
  - `docs/specs/runtime_contracts.md` — an *Epistemic surface* section
  - Stage-3 inversion path (versor-conjugate correction) for reviewed claims
  - Curator justification text recorded for a v2 source-authority-smell check
  - **Named v2 gap:** make the coherence test structural, not curator-asserted; candidate recipe `cga_inner(claim_versor, field_state) ≥ τ_admit AND no reviewed_relation R with cga_inner(claim, R) ≤ τ_reject`

#### 2. Implementation cross-reference

| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| Four-member status enum | yes | `teaching/epistemic.py:43` and around | `COHERENT`/`CONTESTED`/`SPECULATIVE`/`FALSIFIED`; docstring cites ADR-0021 §Schema impact verbatim (`teaching/epistemic.py:59`). No source-trust member. |
| `ADMISSIBLE_AS_EVIDENCE` | yes | `teaching/epistemic.py:49`, `vault/store.py:25` | "FALSIFIED is retained for provenance and Stage-3 inversion, not evidence." |
| `PackMutationProposal.epistemic_status` | yes | `teaching/store.py:90` | Present with the ADR citation in the docstring. |
| Review path transitions | yes | `vault/store.py:407,507`, `teaching/contemplation.py:66`, `teaching/discovery.py:85` | Promotion to `COHERENT` only via `apply_certified_promotion`-style paths; `vault/store.py:486` refuses promotion of a non-SPECULATIVE claim. |
| Trace-hash folding | yes | `docs/specs/runtime_contracts.md:660` | `core.cognition.trace.compute_trace_hash` takes `teaching_epistemic_status: str`, default `""`. |
| `tests/test_epistemic_invariants.py` | yes | `tests/test_epistemic_invariants.py` | Exists; cited as the enforcement point at `runtime_contracts.md:640`. |
| `runtime_contracts.md` *Epistemic surface* | yes | `docs/specs/runtime_contracts.md:620–667` | Full section with the four statuses, the non-hardening invariant, the curator rule, and a schema table. Exactly what the Consequences section required. |
| Non-hardening invariant in practice | yes | `runtime_contracts.md:639` | "the field invariant `versor_condition(F) < 1e-6` … never an epistemic seal on a claim." No `final`/`frozen`/`axiom`/`permanent` flag found. |
| INV-29 discipline downstream | yes | `demos/proof_carrying_promotion/authority.py:32,276` | "this module never ASSIGNS an epistemic_status key anywhere" — the invariant is actively policed at a boundary. |
| Lexicon default **`COHERENT`** | **contradicts (correctly)** | `packs/schema.py:145` | `epistemic_status: str = "speculative"`, with a docstring (lines 122–131) explicitly arguing *against* the ADR: "defaulting unmarked rows to COHERENT would re-import the bias ADR-0021 refuses." The code is right and the ADR is the stale record. |
| Lexicon rows declaring status | **partial — 3 of 30 packs** | `packs/data/{en_units_v1,en_core_math_v1,l10_grounding_v1}/lexicon.jsonl` | 27 packs declare nothing → all rows `SPECULATIVE` → `EpistemicState.UNVERIFIED_POSSIBLE` at `packs/compiler.py:90`. **Includes all four logos packs.** |
| `AlignmentEdge.epistemic_status` | **no** | `packs/schema.py:166–177` | Fields are `source_id`, `target_id`, `relation`, `weight`, `evidence_ids`. **No epistemic status of any kind.** The alignment layer sits entirely outside the revision graph. |
| v2 structural coherence metric | **no (declared open)** | — | The ADR names it as an explicit v2 gap; nothing implements it. Honest, not drift. |

**Build axis: full** (for v1 as scoped). Every artifact named in §Schema impact and §Consequences exists, plus an actively-policed boundary invariant (INV-29) the ADR did not ask for. The single divergence — the lexicon default — is the implementation *improving on* the decision with a written argument. This is the best-built ADR in the stack by a wide margin.

#### 3. Liveness / integration

Live on the serving path. `vault/store.py` gates recall admissibility by status (`_status_admits`, `min_status=EpistemicStatus.COHERENT` filtering at lines 229–352), `chat/runtime.py:195` names the trust boundary ("vault entries from SPECULATIVE/CONTESTED/FALSIFIED…"), `session/context.py:125,294,305` births session claims SPECULATIVE, `generate/epistemic_basis.py:29` reads statuses when composing grounds, and `packs/compiler.py:75–91` maps every compiled lexical row into the runtime `EpistemicState` taxonomy.

**Sabotage test.** Stub `epistemic_status` to a constant `COHERENT` everywhere. **Observable change: large and immediate.** `vault/store.py`'s `min_status` filter would admit SPECULATIVE and CONTESTED entries as evidence into recall; `vault/store.py:486`'s promotion guard (`if claim_meta.get("epistemic_status") != SPECULATIVE.value: …`) would stop refusing; `chat/runtime.py`'s trust boundary would dissolve; `core/contemplation/schema.py:126` would stop rejecting non-SPECULATIVE findings at birth; and every compiled pack row would jump from `UNVERIFIED_POSSIBLE` to `DECODED`. This mechanism is unambiguously load-bearing — the strongest sabotage result in this dossier.

**Liveness axis: live.**

#### 4. Design fidelity — pillars and axioms

| Pillar | Honors / Tension / Violates | Citation |
|---|---|---|
| I. Mechanical Sympathy | **Honors** | A four-member string enum folded into a hash. No index, no ranking model, no learned weighting. §"Why this is correct *for this project*". |
| II. Semantic Rigor | **Honors — exemplary** | "No tier carries inherent trust weight. A `COHERENT` claim is not 'more true' than a `CONTESTED` one — it is *currently incident-free*." The ADR spends a full section (§"What this ADR is NOT") fencing four adjacent meanings out of the term. That is Pillar II performed, not cited. |
| III. Third Door | **Honors** | Rejects both visible options — trust tiers (industry default) and removal-on-contradiction — and builds the revision-graph-position path. §1's exclusion of `peer_consensus`/`outsider_empirical` names the doors it refused. |

| Axiom | Honors / Tension / Violates | Citation |
|---|---|---|
| 1. Geometry-First | **Tension (v1) / Honors (v2 intent)** | §3 admits v1's coherence judgment is curator-mediated, i.e. *not* geometric. The named v2 gap is exactly the axiom: bound status by geometric agreement with the reviewed field. Honest tension, declared in-file. |
| 2. Field-State | **Honors** | Status is defined by how a claim "sits in the field right now," not by an intrinsic property of the claim. That is field-state reasoning applied to epistemics. |
| 3. Propagation-over-Mutation | **Honors** | §2: reviewed claims expose "a versor-conjugate correction that geometrically reverses the rotor encoding the wrong relation, rather than appending a contradictory claim alongside it." Correction propagates through the algebra; it does not stepwise-patch a record. |
| 4. Dual-Correction | **Honors** | Stage-3 inversion *is* the conjugate of admission. `FALSIFIED` is not deletion but eligibility for the corrective operator. The axiom that ADR-0015 violated, this ADR builds. |
| 5. Reconstruction-over-Storage | **Honors** | `FALSIFIED` claims are retained with provenance rather than removed — "removal loses provenance." Enough structured state is kept to reconstruct the revision history. |
| 6. Compilation-Last | **Honors** | The *policy* (revision-graph position, non-hardening, coherence-only) is settled before the enum, the dataclass field, or the JSONL key. |
| 7. Reality-over-Inheritance | **Honors — structurally** | §2's ban on `final`/`frozen`/`axiom`/`permanent` flags makes Axiom 7 *unfalsifiable-by-construction* at the data-model level: no abstraction can acquire sacred status because the flag that would grant it may not exist. The M1 layer card independently calls this "genuinely unusual and… correct." |

#### 5. Build fidelity — does the code match the decision?

One divergence, and it runs the right way. ADR-0021 §Schema impact specifies `packs/data/*/lexicon.jsonl` gets "new optional field `epistemic_status` (**default `COHERENT` for the seed vocabulary**; deliberate-curator-reviewed at pack version bumps)." `packs/schema.py:145` defaults to `"speculative"` and the docstring gives the reason in the ADR's own logic:

> "A pack lexicon row that wants to be admissible as evidence must declare `"epistemic_status": "coherent"` explicitly; the declaration is itself the curator's stamp. **Pack authority alone is not coherence judgment — defaulting unmarked rows to COHERENT would re-import the bias ADR-0021 refuses.**"

The implementation caught a self-contradiction in the ADR: §1 forbids source-trust tiers, and "it came from a pack, therefore it is COHERENT" is a source-trust tier. The code is more faithful to the decision than the decision's own schema table. **The ADR was never updated to record this** — so a reader trusting §Schema impact expects seed vocabulary to be `COHERENT` and it is not, for 27 of 30 packs.

Everything else matches, including artifacts the ADR only gestured at (the INV-29 boundary policing in `demos/proof_carrying_promotion/authority.py`).

**Build-fidelity axis: matches, with one recorded divergence in the implementation's favor.**

#### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs

- **Contradicts `Whitepaper.md`?** No. Reinforces Axioms 3, 4, 5 and 7.
- **Contradicts `Yellowpaper.md`?** No.
- **Other ADRs:** Depends-on chain (ADR-0016/0017/0018) is intact. **ADR-0142** (Epistemic State Taxonomy) is the downstream sibling that defines the runtime `EpistemicState` values (`DECODED`/`CONTRADICTED`/`AMBIGUOUS`/`UNVERIFIED_POSSIBLE`) that `packs/compiler.py:75–91` maps ADR-0021's statuses into — a clean two-layer split (revision-graph position vs. runtime state) that ~60 ADRs downstream reference. `MASTER-BLUEPRINT` **BP-0250** ("Autonomous Geometric Promotion SPECULATIVE→COHERENT") is mapped **Covered (vault)** against `vault/store.py` + `teaching.epistemic.EpistemicStatus`, with optional ADR-0258 reserved "if geometric promotion conditions need a dedicated decision" — that reservation is where ADR-0021's v2 gap would land.
- **Continuity axis: clean.** The only continuity defect is internal: §Schema impact's `COHERENT` default is stale against `packs/schema.py`.

#### 7. Necessity / generality

1. **Necessity.** Irreducible. The sabotage test in §3 returns a large observable change across four subsystems. And the *design* necessity is stronger than the liveness necessity: without a typed status the runtime's only way to mark a claim contested is to remove it, which is the exact failure the Context names ("removal loses provenance; uniformity loses revisability"). Nothing at L0/L1 supplies this — the algebra has `versor_condition(F) < 1e-6`, and the ADR is careful to say that is "a *mathematical* closure check on the algebra — not an epistemic seal on a claim." That distinction is correct and is why the mechanism cannot be pushed down a layer.
2. **Reducibility.** Not reducible. No L0/L1 operator carries revision-graph position. The v2 recipe *would* partially reduce the admission decision to `cga_inner` — but see §8 for why that reduction is currently unsafe.
3. **Extensibility.** Already extended correctly (ADR-0142's runtime-state taxonomy; the domain-pack and vault surfaces). The one place it has **not** extended, and should, is the alignment layer — `AlignmentEdge` has no status field, so the 83 alignment edges are the only substantive claim-bearing artifact in the pack system that the policy cannot describe. Candidate pairing for `22-consolidation-report.md`: **ADR-0021 + ADR-0005 Design Rule 6** — give alignment edges an epistemic position, which is the minimum required for FA-1's verdict to be representable in the runtime rather than only in prose.

**Necessity/generality axis: irreducible.**

#### 8. Fitness / value

- **Positive:** the M1 layer card grades the layer `fit` and names this policy as half the reason: *"The exactness commitment and the epistemic-status regime are mutually reinforcing: exact recall makes a hit verifiable, and typed standing makes it interpretable. The non-hardening invariant is a genuinely unusual and, in this assessor's reading, correct design choice."*
- **Positive:** `runtime_contracts.md` §620–667 and the INV-29/INV-30/INV-31 regime around CLOSE-derived facts (lines 229–246) show the policy carrying real architectural weight — it is the vocabulary the closed-world firewall is specified in.
- **Positive:** the implementation improved on the decision (§5), which is Axiom 7 operating in the healthy direction.
- **Negative — the record/reality divergence this dossier was asked to look for, and it is real:**

  **The epistemic-grading machinery cannot express the FA-1 finding.** Three separate ways:

  1. **The alignment layer is ungraded.** `AlignmentEdge` has no `epistemic_status`. The 83 authored edges — 63 inert, 20 applied as overwrites — cannot be marked `CONTESTED` or `FALSIFIED`, because there is no field to mark. The single most thoroughly refuted claim in the system's history has no typed surface to land on. ADR-0021's own Context states the purpose it fails here: *"there is no way to mark a claim as 'currently contested' … except by removing it."*
  2. **The four logos packs carry `"gate_engaged": true`, `"provenance": "adr-0103:reviewed:2026-05-22"` and — via ADR-0102 — a `reasoning-capable` ledger row**, all of which are reviewed-status assertions about packs whose alignment mechanism was measured destructive and whose serving-side edges resolve zero. These are grades in the ADR-0021 sense (positions asserted by review) held in a schema ADR-0021 does not govern, and therefore not revisable through its path.
  3. **The lexicon rows themselves are `SPECULATIVE`, not because anyone judged them so, but because no one declared anything.** All four logos packs are unmarked, so `packs/compiler.py:90` maps every row to `UNVERIFIED_POSSIBLE`. That happens to be the *defensible* grade post-FA-1 — but it is right by accident, not by review, and it sits alongside a `reasoning-capable` ledger row asserting the opposite. Two records, opposite readings, same packs.

- **Negative — a forward hazard:** ADR-0021 §"Named gap" proposes the v2 admission metric `cga_inner(claim_versor, field_state) ≥ τ_admit`. FA-1 supplies the first hard evidence that this metric, specified today, would certify collapse as coherence: on the shipped ground `cga_inner(light, אוֹר) == cga_inner(light, light)` because the versors are the same array, and 37 coordinates are shared. A geometric coherence test over a collapsed ground returns maximal coherence for maximal collapse. **The v2 metric must not be locked before the ground repair lands.**

**Fitness axis: strongly positive as built (`M1-knowledge-memory.md` §Judgment; `runtime_contracts.md` §620–667; sabotage test §3), with a material scope gap — the policy does not reach the alignment layer, which is where this stack's refuted claim lives.**

#### 9. Findings raised

- **`AA-A3-19` 🔴** `AlignmentEdge` (`packs/schema.py:166`) carries no `epistemic_status`, so the alignment layer is outside the revision graph entirely: the 63 inert and 20 destructive edges can be neither `CONTESTED` nor `FALSIFIED`, and FA-1's verdict has no typed runtime surface. ADR-0021's stated purpose — letting the runtime *say* where a claim sits — fails at exactly the claim the system has most thoroughly refuted. §2, §8.
- **`AA-A3-20` 🟡** ADR-0021 §Schema impact is stale: it specifies lexicon default `COHERENT` for seed vocabulary; `packs/schema.py:145` defaults `"speculative"` with a written argument that the ADR's own default would re-import the bias §1 refuses. The code is correct; the ADR is the wrong record and has never been amended. §5.
- **`AA-A3-21` 🟡** Record/reality divergence across two grading systems for the same four logos packs: unmarked lexicon rows → `SPECULATIVE` → `UNVERIFIED_POSSIBLE` (`packs/compiler.py:90`) while `packs/data/*/manifest.json` asserts `gate_engaged: true` + reviewed provenance and ADR-0102's ledger row asserts `reasoning-capable`. The defensible post-FA-1 grade is held by accident, next to two records asserting the opposite. §8.
- **`AA-A3-22` 🟡** Forward hazard: ADR-0021's candidate v2 metric (`cga_inner(claim_versor, field_state) ≥ τ_admit`) would certify collapse as coherence if specified against the current ground — `cga_inner(light, אוֹר) == cga_inner(light, light)`, 37 shared coordinates. The v2 gap must be sequenced *after* the L2 ground repair (keel K1/K3), and that ordering constraint should be recorded on the ADR. §8.
- **`AA-A3-23` 🟢** Only 3 of 30 packs declare `epistemic_status` in `lexicon.jsonl` at all. Not a defect under the corrected default, but it means the field is near-universally absent rather than deliberately set — worth a coverage counter so "unreviewed" and "reviewed as speculative" stay distinguishable (the repo's own defect class: a success state indistinguishable from "it never ran here"). §2.

#### 10. Evidence sources actually consulted

M1 layer card §Judgment; gap register (searched for epistemic entries — G-22/G-23 adjacent, none covering); `docs/specs/runtime_contracts.md` §620–667 plus §202–246 and §479–572. **Code read directly at `cbfc8ccb`:** `teaching/epistemic.py`, `vault/store.py` (status mapping, `_status_admits`, promotion guards at 486–507), `teaching/store.py:90`, `teaching/contemplation.py:66`, `teaching/discovery.py:85`, `packs/schema.py:118–177` (LexicalEntry docstring + AlignmentEdge fields), `packs/compiler.py:75–91` + `:390`, `session/context.py`, `chat/runtime.py:195,214`, `core/contemplation/schema.py:122–199`, `generate/epistemic_basis.py:29`, `demos/proof_carrying_promotion/authority.py:32,276`, `sensorium/environment/scenario.py`. Existence of `tests/test_epistemic_invariants.py` confirmed. **Not done:** reading `tests/test_epistemic_invariants.py`'s body to confirm the non-hardening assertion is non-vacuous — flagged as unverified rather than claimed clean.

---

## 3. Stack-level synthesis

### Internal consistency

**ADR-0005 ↔ ADR-0015** are consistent in substance and inconsistent in two specifics, neither ever reconciled: the Koine Greek pack id (`el` vs `grc` — ADR-0015's usage won everywhere that runs) and the gate-state precondition (ADR-0015's Negative consequence requires a Supervised Seeding Epoch before Hebrew/Greek gates engage; `sensorium/adapters/text.py` honors it, `packs/data/*/manifest.json` does not). Their central claims are one claim at two strengths, and both were amended together on 2026-07-28 — the amendments are consistent with each other and with the verdict.

**ADR-0021** does not contradict either, but it does not reach them. It governs lexical rows and teaching proposals; it does not govern alignment edges, pack manifests, or ledger ratifications — the three artifacts that carry this stack's now-refuted assertions. That is not a contradiction between ADRs; it is a jurisdictional hole between them, and it is why FA-1's verdict lives in prose rather than in the runtime.

**One silent contradiction, and it is in the implementation's favor:** `packs/schema.py:145` overrides ADR-0021's `COHERENT` lexicon default with `"speculative"` and argues the ADR out of its own schema table. Correct, undocumented in the ADR, and therefore currently a drift finding rather than an amendment.

### The forecast that was filed and never collected

The single most important thing found in this stack that is *not* in FA-1: **the repository predicted this failure in writing, with an acceptance criterion, and then lost the note to a directory-name typo.**

`docs/handoffs/ADR-0167-FOLLOWUPS.md` §6 ("HolonomyAlignmentCase — structural-vs-blend convergence isolation") states the question exactly:

> Determine whether the existing `test_holonomy_alignment_case_positive_closer_than_negative` proves *structurally-derived* cross-language convergence or only proves *endpoint similarity under the mount-time blend*… If (2) is doing the work, the three-language architecture is a *claim* that English-anchored geometric averaging produces the right endpoints, not a *proof* that the depth packs are structurally independent operators converging coherently with the articulation surface.

It then specifies acceptance as **(a)** an ablation test with the blend disabled, or **(b)** "reframe the claim… update `HolonomyAlignmentCase`'s contract to reflect what it actually proves (endpoint similarity under blend, not structural-derivation equivalence). **Honest documentation of a weaker property beats a stronger claim that the test can't support.**"

FA-1 answered it: branch (2), and worse than (2) — the "40% blend" is a 100% replacement. Remedy (b) was the correct move and was never executed: `HolonomyAlignmentCase`'s docstring still claims the Crown Proof at `cbfc8ccb` (`AA-A3-12`). Meanwhile `packs/compiler.py:598` points at this analysis via `docs/handoff/…` (singular) while the file lives at `docs/handoffs/…` (plural) — **both directories exist**, so nothing ever flagged the broken link, and `logos-substrate-collapse-2026-07-28.md` §1 concluded the file did not exist. It did. The pre-registration of FA-1's core finding was sitting in the repository, correct, for months, invisible for one character (`AA-A3-18`).

The methodological lesson is worth more than the fix: **this project's deferred-question notes are load-bearing evidence, and they are cited by file path from code comments with no link checker.** Any future audit should treat `docs/handoffs/` as a primary evidence source alongside `docs/analysis/`.

### Cumulative build state

Across the arc, by artifact rather than by ADR:

| Layer | State | Evidence |
|---|---|---|
| Pack contract surface (`packs/common/`) | **full** | contract doc + 5 schemas + anchor template all present |
| Schema/terminology foundation (`packs/schema.py`) | **full** | 8 types; point/operator separation enforced |
| Epistemic grade machinery | **full** | live on 4+ subsystems; sabotage test large |
| Compiled serving packs (`packs/data/`) | **full but harmed** | 30 packs mount; 37 coordinates lost on the trilingual mount |
| Specified per-language tree (`packs/{en,he,el,grc}/`) | **ghost** | 5–12 lemmas, `status = "draft"`, `readback_rules.py` absent, never imported |
| Eight-gate activation sequence | **ghost** | 1 boolean, 7 gates unimplemented |
| Grammar attractors | **ghost** | type + export, 0 constructions |
| Cross-language resonance graph | **scaffolded** | 83 edges authored, 63 unreachable by construction |
| Holonomy alignment cases | **ghost** | type + tests only, 0 pack instances |
| Crown Proof gate | **dead** | no serving path consults it; the object never closed |
| Readback / articulation half | **ghost** | `readback_rules.py` nowhere in repo |

Roughly: **three of eleven surfaces full, one full-but-harmed, one scaffolded, five ghost, one dead.** The pattern is not random — everything on the *lift/ingest/typing* side got built, and everything on the *readback/proof/gate* side did not. That is Axiom 4 (Dual-Correction) failing at the arc level, not just in ADR-0015: the stack built every forward operator and none of the conjugates. `readback_rules.py` (gate 5's conjugate to gate 4's lift) and the reverse walk `R` (the closure conjugate to `F`) are the same omission at two layers.

### Cumulative necessity/generality read

The stack introduces **two** coherent mechanisms and **one** claim, and they should be separated in the record:

1. **The pack-as-compiled-manifold contract** — coherent, generalizable, already generalized four times (ADR-0091 domain packs, ADR-0027 identity packs, ADR-0013 `ModalityPack`, ADR-0029 safety packs). Consolidation cluster candidate: one pack-contract primitive with role-specific gate sets.
2. **The epistemic revision-graph position** — coherent, irreducible, correctly built, and under-scoped (missing the alignment layer).
3. **Cross-language holonomy closure as the validation gate of meaning** — retired by measurement. Its two operative pieces both reduce to L0 operators that already existed: alignment → `algebra/rotor.py::rotor_power` + `word_transition_rotor` (geodesic on Spin(4,1)); "holonomy" minus its deleted reverse walk → `algebra.geometric_product` composed in a loop. Neither needed a new mechanism at L2. **Consolidation flag: the L2 semantic-ground layer built two narrower, worse versions of operators the L0 algebra layer had shipped on day one, and never imported either.** That is `logos-substrate-collapse` §6's thesis and it is the stack's dominant necessity finding.

**Cross-reference to stack A1 (Algebra & Geometry Foundations — ADR-0001/0003/0004), to check at rollup** (this dossier had no access to A1's output): (a) does A1 independently identify `rotor_power`/`word_transition_rotor` as under-consumed general operators? (b) does A1's fitness evidence confirm FA-1's closing register — that the substrate's value is *measured and holds* in representation (exact recall, versor conditioning, determinism) and *not demonstrated* in reasoning? If both hold, A1 + A3 form a single consolidation cluster: **the algebra layer is the general mechanism; the semantic-ground layer's bespoke constructions are narrower duplicates of it.**

### Blast radius if this stack's central claim is wrong — the cascade-check

It is wrong; FA-1 ruled it. This subsection is the corpus-wide impact analysis FA-1 did not perform. **Method:** `rg -l` across all 314 `docs/adr/*.md` for `ADR-0005`, `ADR-0015`, `holonom`, `cross-language`, `trilingual`, `resonance edge`, `alignment gate`, `Logos`, `language pack`, `anchor record`, `gate_engaged`, then each hit opened with context and judged for **dependency, not co-occurrence**. Files that merely mention a term (e.g. ADR-0090's passing "holonomy bookkeeping" in a rejected-alternative, ADR-0242's quarantined braid-holonomy box, ADR-0225's corpus-hygiene reference) are excluded and named at the end.

**19 ADRs (+2 non-ADR docs, +1 reserved number) inherit something from the retired claim, in four dependency classes.**

**Class 1 — Premise: the retired claim is asserted as an architectural given.**

- **ADR-0180** (CRDT Sharded Vault Concurrency) — *premise.* §1 states: *"The supreme architectural invariant of `core` is **Modality Blindness**: all senses must project into a singular, unified CGA Cl(4,1) manifold **to achieve Holonomy Resonance** (cross-modal unification without late-fusion neural networks)."* This promotes ADR-0015's retired cross-**language** resonance to a cross-**modal** law and calls it the system's supreme invariant. The entire CRDT sharding design is justified as the mechanical cost of preserving it. **Highest-severity cascade hit in the corpus.**
- **ADR-0013** (Sensorium Multimodal Protocol) — *premise.* Defines the "Logos-recovery boundary": *"A visual scene, a Hebrew word, an audio waveform — all are recovered as words in the manifold… There is no multimodal fusion problem because there is nothing to fuse."* The "nothing to fuse" conclusion depends on the shared-space claim that FA-1 measured at AUC 0.557 for the two languages it was designed for.
- **ADR-0181** (Audio Compiler Delta-CRDT) — *inherited premise.* §17–18 restates the Logos-recovery boundary; §133 asserts *"cross-modal resonance re-anchors on merged state after the window closes."*
- **ADR-0197** (Vision Compiler Delta-CRDT) — *inherited premise.* Same boundary at §17; §81 the same cross-modal-resonance re-anchoring claim; §168 cites ADR-0013's "Logos-recovery framing" as a dependency by name.

**Class 2 — Implementation: depends on `holonomy_encode`, the object FA-1 found never closes (`alpha` inert, reverse walk deleted at `fca6216e`).**

- **ADR-0240** (Analogical Transfer Harness + Biography Holonomy Blade) — *implementation.* §46: the Blade is *"reconstructible via `holonomy_encode` (reconstruction-over-storage; no raw experience dump)."* FA-1 measured `core/physics/biography.py:94` passing `alpha=alpha` into a parameter that is never read. The Blade's reconstruction-over-storage claim rests on an encoding whose documented closure does not exist. **Highest-severity Class-2 hit.**
- **ADR-0243** (Wave-Field Cognitive Lifecycle) — *implementation.* §2.5 defines the lifelong learning record as `H_bio ← H_bio · R` and calls it *"the ultimate, non-lossy, reconstruction-over-storage compilation of experience"* and §4.1 *"Topologically Protected Wisdom… an untamperable, replayable audit trail."* Replayability survives (it is a deterministic product); *non-lossy reconstruction* and *topological protection* do not follow from an open path product.
- **ADR-0241** (Wave-Field Hyperbolic Atlas) — *implementation.* Its migration table maps *"Biography holonomy | `holonomy_encode` trajectory"* → *"Resonant standing-wave lock-in of unitary propagators"*, i.e. it carries the defective object forward into the wave substrate as a known quantity.
- **ADR-0239** (Conformal Procrustes Surprise Dual Operator) — *downstream.* §5: a successful transfer below ε *"is eligible for teaching-chain / biography holonomy update (ADR-0240)"*; Consequences: *"Direct feed into ADR-0240."* Inherits by being the producer for a defective sink.
- **ADR-0244** (Wave-Field Identity Manifold) and **ADR-0246** (Induced Identity Action) — *boundary assertion, low severity.* Both assert biography-holonomy accumulation is a **separate, non-mutating** process w.r.t. the frozen identity subspace (0244 governance item 8 and §547; 0246 §91). The quarantine is correct and is *strengthened*, not weakened, by the finding — but both assume the quarantined object is well-defined, so both should carry a pointer. Monitor only.
- **ADR-0261 (reserved, unallocated)** — *reserved intent.* `MASTER-BLUEPRINT-2026-07-20-ADR-MAPPING.md` maps BP-0253 *"Holonomy Primacy Enforcement in Rust PyO3 SIMD Kernels"* → **Gap**, reserving ADR-0261 "for holonomy/Rust primacy if needed," and ADR-0253 §3 confirms the reservation. **This number must not be allocated without a NO-GO annotation** — it would harden the retired mechanism into SIMD kernels.

**Class 3 — Mechanism: builds on cross-language alignment / shared `semantic_domains` as a working substrate.**

- **ADR-0073** (Anchor-Lens Substrate) and **ADR-0073a** (Anchor-Lens Content Phase) — *mechanism.* **Highest-severity Class-3 hit, and the one most directly harmed.** ADR-0073 §38 makes the design's foundation explicit: *"Cross-language binding is **shared `semantic_domains` atoms**, not transliteration tables: the same load-bearing tag (e.g. `logos.aletheia.verity`) appears across grc/he/en… This is the deterministic pivot an anchor-lens composer would traverse."* FA-1 measured **that exact pivot as the dominant collapse site**: `_apply_mounted_primary_domain_resonance` groups by shared primary semantic domain and overwrites every member with the English prototype — **34 of the 37 lost coordinates**. Compounding it, both ADRs make *"`alignment.jsonl` on the cognition-tier packs (currently only the micro packs carry it)"* the highest-leverage L1.1 deliverable — and `_infer_foreign_pack_ids`'s frozen `_PREFIX_TO_PACK` makes cognition-tier edges **unreachable by construction**, which is why `he_core_cognition_v1`'s 22 and `grc_logos_cognition_v1`'s 41 edges resolve to zero. ADR-0073a's Greek/Hebrew distinction families (`logos.epignosis.*`, `logos.agape/philia/eros/storge`, `logos.aion/chronos/kairos`) are authored specifically to preserve distinctions English collapses — and the mount-time rule collapses distinct-domain members into the English prototype. **The remedy this ADR prescribes lands on a resolver that cannot reach it, into a mechanism that destroys what it is written to preserve.**
- **ADR-0102** (Hebrew-Greek Reasoning-Capable Ratification) and **ADR-0103** (Fluency-Lane Attachment) — *ratification / fitness.* ADR-0102 ratifies `hebrew_greek_textual_reasoning` as a `reasoning-capable` ledger row over exactly the four packs FA-1 measured: `he_logos_micro_v1` and `grc_logos_micro_v1` (alignment resolves, as overwrites) and `he_core_cognition_v1` and `grc_logos_cognition_v1` (**zero** resolving edges, and the two `chat/pack_grounding.py:56–57` actually grounds serving against). ADR-0103 advances all four manifests' provenance to `adr-0103:reviewed:2026-05-22` — the same string now stamped beside `gate_engaged: true`. G-25's first layer independently records the same domain produced **zero** curriculum bands. A live `reasoning-capable` license rests on a substrate measured destructive on one half and inert on the other.
- **ADR-0007** (Valence Layer) — *interface.* §23 makes valence *"lifted directly from the morphological and syntactic structure of the source material **by the language pack's lift rules**"*, §45 assigns Hebrew/Greek the fine-grained rules, and §Related cites ADR-0005 for *"lift and **readback** rule interfaces."* Half that interface (`readback_rules.py`) does not exist.
- **ADR-0006** (Field Energy Operator) — *interface.* §55 bakes aspect-class weights into the field at pack-lift time; §73–74 routes energy classes to *"`en/readback_rules.py`, `he/readback_rules.py`, `el/readback_rules.py`"* — three files by name, none of which exist, using ADR-0005's superseded `el` id.
- **ADR-0027** (Identity Packs) — *analogy, low severity.* §19 models identity packs *"same as language packs"*; rejected-alternative 4 declines to merge them because *"language packs already do enough."* That premise is now measured. Monitor.
- **ADR-0030** (Depth-Language Hedge) — *deferred option, low severity.* §40 names *"lifting depth-language phrases out of `surface.py` into language packs"* as a deferred architectural move; the target's condition has changed. Monitor.

**Class 4 — Boundary / governance: rulings made about this stack that need re-verdicting.**

- **ADR-0253** (Master Blueprint Collision + Dual-Pack Boundary) — *boundary freeze.* §4 correctly rules `packs/he`/`packs/grc` draft-only and `packs.compiler` → `packs/data/` the sole serve authority, with architecture tests pinning it. The ruling is right; what it froze is the boundary around a compiler whose alignment path was destructive at the time of freezing. Also the custodian of the ADR-0261 reservation. Needs a note, not a reversal.
- **`SESSION-2026-05-12-language-packs-addendum.md`** (non-ADR) — *companion.* Restates both retired assertions: *"Pack activation is **gate-based**, not file-existence-based"* and *"Cross-language alignment is an **explicit probe surface**, not an emergent hope."* Both measured false in implementation.
- **`MASTER-BLUEPRINT-2026-07-20-ADR-MAPPING.md`** (non-ADR) — *mapping.* Holds the BP-0253 → ADR-0261 reservation and the BP-0250 → vault/epistemic mapping. Annotate the former.

**Checked and excluded (co-occurrence, not dependency):** ADR-0090 (holonomy named once inside a *rejected* rollback alternative), ADR-0242 (Vector 5 topological/braid holonomy is an explicitly quarantined box with a production-import ban — unrelated construction), ADR-0225 (corpus hygiene), ADR-0091 (domain-pack contract — the vehicle for ADR-0102's ratification but carries no cross-language or holonomy claim of its own), ADR-0029/0049/0051/0128/0131.x/0165/0174/0199/0234 (all use "language pack"/"pack" generically), ADR-0223/0224 (substrate audits — no holonomy or cross-language claim), ADR-0142 and the ~60 ADRs citing `epistemic_status` (downstream of ADR-0021, which is *not* retired; excluded to keep the cascade about the refuted claim).

**Blast-radius summary.** The retired claim is load-bearing in **one supreme-invariant assertion** (ADR-0180), **one multimodal boundary doctrine** propagating to two compilers (ADR-0013 → 0181, 0197), **one lifelong-learning substrate** and its three dependents (ADR-0240 → 0243, 0241, 0239), **one anchor-lens program** whose prescribed remedy is unreachable by construction (ADR-0073/0073a), and **one live capability license** (ADR-0102/0103). Zones needing re-verdict beyond M1: **M2** (afferent boundary — 0013/0181/0197), **M0/M1 vault** (0180), **M5** (learning/growth — 0239/0240/0243), **MG** (identity — 0244/0246, monitor), **MV** (the capability ledger — 0102/0103).

## 4. Stack-level findings (`AA-N`)

Placeholder namespace `AA-A3-*`; assign final `AA-N` numbers from `20-finding-register.md` at rollup. Severity buckets per `40-triage-queue.md`: 🔴 Block / 🟡 Repair / 🔵 Consolidate / 🟢 Monitor.

**ADR-0005 (rolled up from §2):**
- **`AA-A3-1` 🔴** Eight-gate activation sequence does not exist; `gate_engaged` is one boolean, `true` on all four logos packs; seven gates unimplemented.
- **`AA-A3-2` 🔴** `_blend_feature_versors` still returns the target verbatim at `cbfc8ccb`; 37 coordinates still lost on the trilingual mount in the serving tree.
- **`AA-A3-3` 🟡** Koine Greek has two pack ids (`el` per ADR-0005, `grc` everywhere that runs); `packs/el/` and `packs/grc/` are duplicate draft trees. Pillar II.
- **`AA-A3-4` 🟡** `readback_rules.py` exists nowhere in the repository despite being a Required-Structure artifact, gate 5's subject, and a cited interface for ADR-0006 and ADR-0007.
- **`AA-A3-5` 🟡** `_PREFIX_TO_PACK` frozen at three pack names makes 63 of 83 alignment edges unreachable *by construction*, discarded with no warning, counter, or test.
- **`AA-A3-6` 🟢** "Runtime Boundary Honesty" (`NotImplementedError` at semantic boundaries) unimplemented; goal met by delegation instead.
- **`AA-A3-7` 🟡** ADR-0253 §4 superseded ADR-0005's Required-Structure serving authority; ADR-0005 carries no note of it.
- **`AA-A3-8` 🔵** Consolidation: ADR-0005 + ADR-0091 + ADR-0027 + ADR-0013 are four instances of one pack-contract primitive.
- **`AA-A3-9` 🟡** The token-level form of gate 7 is unmeasured and its four nominal proofs are decoration; needs its own pre-registration.
- **`AA-A3-10` 🟢** Coupling-strength question open; must carry FA-1's anti-trade criterion (separation must improve faster than distinctness degrades, both measured).

**ADR-0015 (rolled up from §2):**
- **`AA-A3-11` 🔴** `holonomy_encode` docstring describes a reverse walk and `H = F·R` that the code does not compute; `alpha` validated then never read, and `core/physics/biography.py:94` passes it. Unrepaired since `fca6216e`.
- **`AA-A3-12` 🔴** `packs/schema.py:181` `HolonomyAlignmentCase` docstring still asserts the retired Crown Proof verbatim in live code at HEAD.
- **`AA-A3-13` 🟡** ADR-0015 Consequences line 148 still lists the retired claim as a **Positive**, unstruck below the amendment banner.
- **`AA-A3-14` 🟡** Contradictory gate state for he/grc between `sensorium/adapters/text.py` (`False`, per the ADR) and `packs/data/*/manifest.json` (`true`).
- **`AA-A3-15` 🟡** `GrammarAttractor` is a ghost (type + export, 0 runtime constructions); the attractor path and the collapse path are the same design intent, one unbuilt and one built wrong.
- **`AA-A3-16` 🟡** `HolonomyAlignmentCase` exists only in tests; no pack carries a case.
- **`AA-A3-17` 🟡** Axiom 4 (Dual-Correction) design violation: the Crown Proof is a forward operator whose conjugate was deletable with no test noticing.
- **`AA-A3-18` 🟢** `packs/compiler.py:598` cites `docs/handoff/…` for a file at `docs/handoffs/…`; both dirs exist so nothing flagged it, and FA-1 concluded the file was missing. See §3 "the forecast that was filed and never collected."

**ADR-0021 (rolled up from §2):**
- **`AA-A3-19` 🔴** `AlignmentEdge` carries no `epistemic_status`; the alignment layer is outside the revision graph, so FA-1's verdict has no typed runtime surface.
- **`AA-A3-20` 🟡** ADR-0021 §Schema impact's `COHERENT` lexicon default is stale against `packs/schema.py:145`'s better-argued `"speculative"`.
- **`AA-A3-21` 🟡** The four logos packs simultaneously grade as `SPECULATIVE`/`UNVERIFIED_POSSIBLE` (unmarked rows) and as reviewed + `gate_engaged: true` + `reasoning-capable`.
- **`AA-A3-22` 🟡** ADR-0021's candidate v2 `cga_inner` admission metric would certify collapse as coherence on the current ground; must be sequenced after the L2 repair.
- **`AA-A3-23` 🟢** Only 3 of 30 packs declare `epistemic_status` at all; "unreviewed" and "reviewed as speculative" are indistinguishable.

**Cascade findings — visible only at stack level (§3):** one per dependent, per the audit charter's cascade instruction.

- **`AA-A3-24` 🔴** **ADR-0180** — *premise.* Asserts Holonomy Resonance as *"the supreme architectural invariant of `core`"* in cross-modal form; the whole CRDT sharding design is justified as its mechanical cost. Re-verdict required.
- **`AA-A3-25` 🟡** **ADR-0013** — *premise.* The Logos-recovery boundary's *"there is nothing to fuse"* conclusion rests on the shared-space claim measured at AUC 0.557.
- **`AA-A3-26` 🟡** **ADR-0181** — *inherited premise.* Logos-recovery boundary + "cross-modal resonance re-anchors on merged state."
- **`AA-A3-27` 🟡** **ADR-0197** — *inherited premise.* Same, and cites ADR-0013's framing as a named dependency.
- **`AA-A3-28` 🔴** **ADR-0240** — *implementation.* The Biography Holonomy Blade's "reconstructible via `holonomy_encode`" rests on an encoding whose documented closure was deleted; `biography.py:94` steers an inert `alpha`.
- **`AA-A3-29` 🟡** **ADR-0243** — *implementation.* "Non-lossy reconstruction-over-storage" and "topologically protected wisdom" do not follow from an open path product; replayability survives.
- **`AA-A3-30` 🟡** **ADR-0241** — *implementation.* Carries `holonomy_encode` forward into the wave substrate as a known quantity.
- **`AA-A3-31` 🟡** **ADR-0239** — *downstream.* Feeds ADR-0240's biography-holonomy update as its acceptance sink.
- **`AA-A3-32` 🟢** **ADR-0244 + ADR-0246** — *boundary assertion.* Both quarantine biography holonomy from the identity subspace; the quarantine is correct and strengthened by the finding, but both assume a well-defined quarantined object. Monitor + pointer.
- **`AA-A3-33` 🔵** **ADR-0261 (reserved, unallocated)** — *reserved intent.* BP-0253 "Holonomy Primacy Enforcement in Rust PyO3 SIMD Kernels" must not be allocated without a NO-GO annotation; it would harden the retired mechanism into SIMD kernels.
- **`AA-A3-34` 🔴** **ADR-0073 + ADR-0073a** — *mechanism.* Cross-language binding via shared `semantic_domains` atoms **is** the dominant collapse site (34 of 37 lost coordinates), and the prescribed remedy (cognition-tier `alignment.jsonl`) is unreachable by `_infer_foreign_pack_ids` by construction. The distinction families authored to preserve what English collapses are collapsed into the English prototype.
- **`AA-A3-35` 🔴** **ADR-0102 + ADR-0103** — *ratification / fitness.* A live `reasoning-capable` ledger license rests on four packs whose alignment is destructive on one half and zero-resolving on the other; G-25 independently records zero curriculum bands produced.
- **`AA-A3-36` 🟡** **ADR-0007** — *interface.* Valence lift depends on pack lift **and readback** rules; readback does not exist.
- **`AA-A3-37` 🟡** **ADR-0006** — *interface.* Names `en/he/el/readback_rules.py` directly; none exist, and it uses the superseded `el` id.
- **`AA-A3-38` 🟢** **ADR-0027** — *analogy.* "Language packs already do enough" is now a measured claim; monitor.
- **`AA-A3-39` 🟢** **ADR-0030** — *deferred option.* Deferred move into language packs; target condition changed; monitor.
- **`AA-A3-40` 🟡** **ADR-0253** — *boundary freeze.* Correct ruling, frozen around a destructive compiler; also custodian of the ADR-0261 reservation. Annotate.
- **`AA-A3-41` 🟢** **`SESSION-2026-05-12-language-packs-addendum.md`** — *companion.* Restates both retired assertions ("gate-based, not file-existence-based"; "explicit probe surface, not an emergent hope"). Annotate as a non-ADR record.
- **`AA-A3-42` 🟢** **`MASTER-BLUEPRINT-2026-07-20-ADR-MAPPING.md`** — *mapping.* Annotate the BP-0253 → ADR-0261 row with the NO-GO.

**Arc-level findings (visible only across all three cards):**
- **`AA-A3-43` 🟡** **Every forward operator in this stack was built and no conjugate was** — `readback_rules.py` (gate 5's conjugate to gate 4's lift) and the reverse walk `R` (closure's conjugate to `F`) are the same Axiom-4 omission at two layers. §3 cumulative build state.
- **`AA-A3-44` 🔵** **The L2 semantic-ground layer built two narrower, worse versions of L0 operators that already shipped** — alignment vs. `rotor_power`/`word_transition_rotor`, and "holonomy" vs. `geometric_product` — and imported neither. Primary feeder for `22-consolidation-report.md`; pair with stack **A1**.
- **`AA-A3-45` 🟡** **`docs/handoffs/` is uncatalogued primary evidence cited by file path from code comments with no link checker.** A correct pre-registration of FA-1's core finding (§6) was invisible for one character for months, and a ratified analysis doc concluded it did not exist. Recommend a link check over code-comment doc citations, and adding `docs/handoffs/` to the audit charter's §4 evidence-source order.

**Count: 45 findings** — 10 (ADR-0005) + 8 (ADR-0015) + 5 (ADR-0021) + 19 cascade + 3 arc-level. Severity: **9 🔴**, **24 🟡**, **3 🔵**, **9 🟢**.

## 5. Evidence sources actually consulted (stack-wide)

**Audit governance:** `docs/adr-audit/00-scope-and-method.md`, `TEMPLATE-stack-dossier.md`, `TEMPLATE-adr-card.md`, `02-stack-taxonomy.md` (including the L0–L5 numbering-scheme disambiguation), `MANIFEST.md`.

**Member ADRs, read in full:** `ADR-0005-language-pack-contract.md`, `ADR-0015-language-packs-and-holonomy-resonance.md` (including the 2026-07-28 amendment banner), `ADR-0021-epistemic-grade-policy.md`.

**Prior verdicts adopted, not re-derived:** `docs/analysis/fa1-holonomy-gate-verdict-2026-07-28.md`, `docs/analysis/fa1-holonomy-gate-preregistration.md` (via the verdict's citations), `docs/analysis/logos-substrate-collapse-2026-07-28.md`, `docs/analysis/holonomy-resonance-proof-not-robust-2026-06-14.md` (via citation).

**Assessment corpus:** `docs/assessment/10-layer-cards/M1-knowledge-memory.md` (zone roster + Judgment), `docs/assessment/30-gap-register.md` (G-25 all three layers, G-24, G-23 for the adjacent defect class), `docs/assessment/31-hindrance-audit.md` (searched; no covering H-N entry).

**Deferred-question record:** `docs/handoffs/ADR-0167-FOLLOWUPS.md` §6 in full — the pre-registration of FA-1's finding.

**Specs:** `docs/specs/runtime_contracts.md` §202–246 (CLOSE/INV-30/INV-31), §479–572, §620–667 (Epistemic surface).

**Code read directly at `cbfc8ccb`** (per "verify against code, not against documents"): `packs/compiler.py` (`_blend_feature_versors` and all three call sites, `_apply_mounted_primary_domain_resonance` + its architectural-invariant comment, `_apply_alignment_corrections`, `_apply_morphology_cluster_corrections`, `_infer_foreign_pack_ids`, `_PREFIX_TO_PACK`, `_entry_epistemic_state`), `packs/schema.py` (all eight types; `LexicalEntry` and `HolonomyAlignmentCase` docstrings), `packs/common/` tree, `packs/{en,he,el,grc}/` trees + `pack.toml` + `lift_rules.py` + line counts, `packs/data/` listing (30 packs) + logos-pack `manifest.json` fields + `alignment.jsonl` line counts + `lexicon.jsonl` `epistemic_status` coverage, `algebra/holonomy.py`, `sensorium/registry.py`, `sensorium/adapters/text.py`, `chat/runtime.py`, `teaching/epistemic.py`, `teaching/store.py`, `teaching/contemplation.py`, `teaching/discovery.py`, `vault/store.py`, `session/context.py`, `core/contemplation/schema.py`, `generate/epistemic_basis.py`, `demos/proof_carrying_promotion/authority.py`. Repo-wide `find` for `readback_rules.py`; repo-wide `rg` (tests excluded) for `GrammarAttractor`, `HolonomyAlignmentCase`, `EpistemicStatus`, `epistemic_status`, `gate_engaged`, `FALSIFIED`.

**Cascade sweep:** `rg -l` over all `docs/adr/*.md` for `ADR-0005`, `ADR-0015`, `holonom`, `cross-language`/`crosslanguage`/`trilingual`/`resonance edge`, `alignment gate`/`anchor record`/`gate_engaged`/`validation gate`, `Logos`, `language pack`/`pack contract`/`pack.toml`/`lemmas.jsonl`, `epistemic.status`/`SPECULATIVE`/`CONTESTED`/`FALSIFIED`; every hit then opened with `-B/-A` context and judged for dependency vs. co-occurrence. ADRs read in relevant part: 0006, 0007, 0013, 0027, 0030, 0073, 0073a, 0090, 0091, 0102, 0103, 0180, 0181, 0197, 0223, 0224, 0239, 0240, 0241, 0242, 0243, 0244, 0246, 0253, plus `MASTER-BLUEPRINT-2026-07-20-ADR-MAPPING.md` and `SESSION-2026-05-12-language-packs-addendum.md`.

**Instruments confirmed present:** `evals/logos/{fa1_gate.py, manifold_collapse.py, repaired_ground.py}`, `tests/test_fa1_gate_verdict.py`, `tests/test_manifold_collapse_floor.py`, `tests/test_epistemic_invariants.py`, `tests/test_alignment_graph.py`, `tests/test_holonomy_resonance.py`.

**Checked and NOT available:** `docs/census/<sha>/stale-references.jsonl` and `docstring-drift.jsonl` — `docs/census/` is untracked in the working tree at audit time, so the charter's evidence-source item (4) could not be consulted. Several findings here (`AA-A3-11`, `AA-A3-12`, `AA-A3-18`) are docstring-drift/stale-reference findings that census output would likely have surfaced mechanically; **recommend re-checking this dossier against `docs/census/` once it lands.**

**Not verified in this pass, recorded as gaps rather than clean results:** the body of `tests/test_epistemic_invariants.py` (non-vacuity of the non-hardening assertion); ADR-0015's four-factor Hebrew composition chain as a distinct code site; ADR-0102's `tests/test_adr_0100_0102_sibling_ratifications.py` predicate bodies.
