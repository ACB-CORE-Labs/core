# Hebrew and Koine Greek Logos Pack Capability Roadmap

**Date:** 2026-07-19  
**Type:** No-implementation audit / planning dossier  
**Authority tree:** `feat/deterministic-relational-operator-ablation`  
**Companion docs:**

- `docs/analysis/relational-operator-ablation-cartography-2026-07-19.md` — Phase 1 cartography + go/no-go  
- `docs/analysis/relational-operator-ablation-dossier-2026-07-19.md` — English `fraction_decrease` ablation (IMPLEMENTED AND MEASURED)  
- This file — separate HE/GRC Logos capability audit (planning only)

**Boundary:** The relational-operator ablation remains closed. English-only `fraction_decrease` depth was intentionally inert (no observed-morphology basis). That result must not be generalized to “Hebrew/Greek never help,” nor used to authorize English→pseudo-depth. This roadmap does **not** authorize a giant pack build.

---

## 1. Executive verdict

**READY ONLY FOR PREREQUISITE WIRING OR MIGRATION**

| Label | Why |
|-------|-----|
| Not ready for broad Logos implementation | Dual pack systems; sparse morph tags; holonomy crown proof not robust; no executable morph→canonical-relation mapping with provenance |
| Not architecturally blocked | Canonical language-independent seams exist (`BoundRelation`, teaching operators, pack checksum/OOV, `resolve_entry` / `node_depths`) |
| Broader “Logos improves all domains” thesis | Scientifically under-specified until a narrow **observed-HE/GRC** constraint ablation exists |

### Ablation boundary (preserve)

English-only `fraction_decrease` sealed n=8: depth **intentionally inert**. Do not reopen ablation fixtures/results except for demonstrated defects. Do not claim HE/GRC help arithmetic without observed morph input.

---

## 2. Hebrew capability matrix

Status: **LIVE** | **EVALUABLE** | **DIAGNOSTIC** | **TEST-ONLY** | **DORMANT** | **SCAFFOLD** | **SPECIFIED** | **ABSENT** | **CONTRADICTED**

| Capability | Exact evidence | Compiler | Runtime | Proof/tests | Gap | Overclaim risk | Priority |
|------------|----------------|----------|---------|-------------|-----|----------------|----------|
| Structured morphology schema | `packs/schema.py` `MorphologyEntry`; `packs/data/he_*` | LIVE `_apply_morphology` | Manifold via `load_pack` | `test_morphology_registry`, holonomy morph | No paradigm generator | Medium if “full morph” | P0 (tags live) |
| Legacy triliteral / romanized root | `packs/compiler.py` `_is_hebrew_root`, `_triliteral_root` | LIVE feature | Manifold | holonomy same-root | Dual encodings | Low | P1 document/migrate |
| Root identity on resolve | `chat/pack_resolver.py` `resolve_entry`, `resolve_token_depths` | Lookup | LIVE PropGraph / recognition | `test_3lang_depth_capability`, `test_oov_pipeline` | Exact surface match only | Medium | P0 observed-HE |
| Root-sense disambiguation | Multi-surface rare; no sense graph | ABSENT | First-match | — | Homographs silent | **Critical** | **P0 prerequisite** |
| Binyan as licensed semantics | Sparse `binyan` tags (qal/piel) | LIVE as infl rotor | Manifold only | sparse data | No root-specific licensing | **Critical** if universalized | P2 after sense model |
| Verbal aspect | Sparse `aspect: perfect` | Tags only | Not clause-level | source DRAFT notes | Not temporal operators | High | P2–P3 |
| Voice / reflexive / passive | Essentially ABSENT in compiled HE | — | — | — | Niphal/Hithpael not systematic | High | P3 |
| Construct state | 1× construct tag; source `he:construct-chain` frame | Tag only | Frames DISCONNECTED | — | Not executable possession | High if genitive-universalized | P1 candidate |
| Nominal gender/number | LIVE tags | LIVE rotors | Tags | registry | No agreement checker | Medium | P2 |
| Pronominal suffixes | Sparse `suffix_chain` | LIVE | Ingest OOV decomp | ingest gate | Not full paradigm | Medium | P3 |
| Lexical valency / frames | `packs/he/frames.jsonl` (4 frames) | **DISCONNECTED** from `packs/data` | Not in `load_pack` | CLI validate only | No LIVE frame→BoundRelation | High | **P1 migration** |
| Semantic domains | lexicon `semantic_domains` | LIVE | Manifold | domain contracts | Not morph-derived | Low | Keep |
| Alignment edges | `alignment.jsonl` | Load nudge | Geometry | alignment tests | Data ≠ reasoning | Medium | Honest limits |
| Readback HE | `_assemble_he`, ADR-0030 hedges; no `readback_rules.py` | — | Limited assembly | identity depth tests | Fluency C01 only | High if “full readback” | See fluency honesty |
| Correction / contradiction | Teaching chains ADR-0102 | N/A | Teaching/eval | domain tests | Not morph-triggered | Medium | Tie morph to existing ops |
| OOV fail-closed | `gate_engaged=true`, `fail_closed` | Enforced | LIVE | pack runtime tests | OK | Low | Preserve |
| Fluency eval | `evals/hebrew_fluency` | — | Articulation | contract.md C01 | Not morph-constraint eval | High if misused | Separate lane |
| Executable morph→canonical relation | — | ABSENT | ABSENT | ABSENT | Core Logos gap | Critical | Next vertical slice |

---

## 3. Greek capability matrix

| Capability | Exact evidence | Compiler | Runtime | Proof/tests | Gap | Overclaim risk | Priority |
|------------|----------------|----------|---------|-------------|-----|----------------|----------|
| Lemma inventory | `packs/data/grc_*` (11 / 38) | LIVE | `resolve_entry` | registry, 3lang | Micro seed | Medium | P0 honesty |
| Sense disambiguation | No compiled `senses.jsonl` on data packs | ABSENT | First-match | — | Colwell needs sense+syntax | **Critical** | **P0 prerequisite** |
| Case tags | Nearly all **nominative** only | LIVE rotors | Tags only | registry order | No productive case paradigm | **Critical** if case→role | P1 observed forms only |
| Number/gender/agreement | Tags present | LIVE | No agreement engine | — | No S-V check | High | P2 |
| Prep + case | Source `el:relational-pros` | DISCONNECTED | ABSENT | — | Not enforced | High | After case diversity |
| Valency / frames | `packs/grc\|el/frames.jsonl` | DISCONNECTED | ABSENT | — | Dual-system gap | High | **P1 migration** |
| Aspect / tense-form | Present indicative dominant | Tags | Not operators | — | Aorist/perfect system ABSENT | High | P2–P3 licensed tables |
| Voice / mood | Sparse active/middle; indicative | Tags | — | — | No full mood system | High | P3 |
| Participles / infinitives | ABSENT as productive class | — | — | — | Out of seed scope | Medium | Defer |
| Semantic domains | `logos.core`, etc. | LIVE | Manifold | ADR-0102 | OK | Low | Keep |
| Alignment | grc↔he↔en edges | Load nudge | Geometry | alignment tests | Not robust holonomy | Medium | Honest limits |
| Colwell / anarthrous | Source frame + notes | DISCONNECTED | ABSENT | — | Not runtime | High if claimed LIVE | P2 fail-closed |
| Readback GRC | `_assemble_grc` | — | Limited | depth tests | Fluency-class | Medium | `evals/koine_greek_fluency` |
| Geometric signature for GRC | `resolve_geometric_signature` needs `senses.jsonl` | ABSENT for depth packs | EN math when present | fraction EN | HE/GRC cannot supply scale signatures | Medium | Domain concern |
| Executable morph→canonical relation | ABSENT | ABSENT | ABSENT | ABSENT | Core gap | Critical | Observed-GRC later |

---

## 4. Shared Logos substrate matrix

| Capability | Evidence | Compiler | Runtime | Proof/tests | Gap | Overclaim risk | Priority |
|------------|----------|----------|---------|-------------|-----|----------------|----------|
| Roles DEPTH_ROOT / DEPTH_RELATION | `LanguageRole`; manifests | Schema LIVE | Load | ADR-0015 | Source `el` vs runtime `grc` | Medium | Prefer `grc` |
| Checksum + OOV | `load_pack` | LIVE | ChatRuntime | pack tests | Source ADR-0005 gates never true | Low | Keep |
| Ordered morph composition | `_apply_morphology` | LIVE | Manifold | holonomy morph | Not semantic licensing | Medium | Keep |
| Alignment graph | `alignment/graph.py` | Load nudge | Geometry | alignment tests | Not clause reasoning | High if “reasoning” | Data + local geometry |
| Holonomy encode | `algebra/holonomy.py` | LIVE encode | Ingest path | **Honest-fail crown** | Crown **not robust** | **Critical** | Do not claim trilingual proof |
| PropGraph depth spine | `GraphNode` language/root/morphology_id | N/A | LIVE he/grc | 3lang tests | No BoundRelation emission | Medium | Bridge for constraints |
| Depth decorate vs decide | `enrich_assessments_with_depth` vs anti_unifier | — | Match LIVE; math decorate | 3lang, oov | EN math correctly inert | Low if labeled | Preserve |
| Canonical roles | `BoundRelation`, `RoleObligation` | N/A | Math LIVE (fraction) | problem_frame tests | Language-independent | Low | **Reuse only** |
| Teaching causal/contradiction | `hebrew_greek_textual_reasoning_chains_v1.jsonl` | N/A | Teaching/domain | ADR-0102 | Lexeme-level, not morph | Medium | Constraint consumer |
| GrammarAttractor | schema | Thin | DORMANT | — | Not hot path | Medium | Defer |
| `packs.evidence` | holonomy helpers | — | TEST-ONLY / dormant | holonomy tests | Not production | Medium | Don’t build runtime on it |
| Sensorium HE/GRC | `gate_engaged=False` default | Scaffold | Divergent from data True | — | Dual truth | Medium | Align or drop fiction |
| Domain contract | ADR-0091/0102 four packs | Manifest | Ledger reasoning-capable | ratification tests | Fluency ≠ morph-constraint | Medium | Keep honesty |

**Trilingual alignment:** curated alignment data + local manifold geometry; **clause holonomy crown proof is CONTRADICTED as robust** (`docs/analysis/holonomy-resonance-proof-not-robust-2026-06-14.md`, honest-fail tests).

---

## 5. Pack taxonomy (strict)

| Tier | Contents | Must not smuggle |
|------|----------|------------------|
| Universal canonical Logos primitives | `BoundRelation`, RoleObligations, epistemic status, VersorBinding/CGA, teaching operator families, shared `semantic_domains` | HE/GRC-only hidden reasoners |
| Hebrew surface + mapping rules | Observed surfaces, roots, tags, **authored** mapping rules + provenance | English→HE inference; universal binyan→semantics |
| Greek surface + mapping rules | Observed lemmas/forms, attested case tags, **authored** prep+case rules | Nominative=agent; English→case |
| English articulation | Operational base, realizer, fluency | Treating EN as depth proof |
| Domain packs | math/physics/etc. organs | Domain-private morph ontology |
| Anchor / lens / register | `packs/anchor_lens/he_*`, `grc_*` | Lens as morphology engine |
| Safety / identity | identity/safety/ethics; ADR-0030 hedges | Identity as role solver |
| Evaluation / mastery | fluency, fabrication_control, inference_closure, ablations | Fluency pass as morph-constraint pass |

---

## 6. Phased vertical-slice roadmap

### Phase 0 — Prerequisites (no bulk pack growth)

1. Freeze dual-system map: LIVE = `packs/data/*`; source `packs/{he,grc,el}` = draft/disconnected.  
2. Sense/ambiguity policy: first-match is fail-open for meaning → multi-candidate or refuse on collision.  
3. Entrypoint already LIVE: HE `resolve_entry` / `define אמת` path (or GRC lemma path).  
4. No lexicon expansion until Phase 1 ablation.

### Phase 1 — Smallest observed-morphology constraint (separate implementation PR)

| Condition | Behavior |
|-----------|----------|
| Canonical only | Teaching operator/chain without morph constraint |
| Executable morph constraint | Authored rule with provenance → constraint or refuse |
| Metadata-only | `node_depths` / root notes; **must not** change outcome |
| Invalid / ambiguous | Homograph without sense rule → **refuse** |

**Consumer:** existing teaching/contradiction/abstention seams — **not** GSM8K, not new ontology.  
**Inputs:** observed HE/GRC only.  
**Success:** wrong=0; metadata inert; outcome changes only with provenance.

### Phase 2 — One morph phenomenon

- HE: root identity + ambiguity refuse → construct-state candidate → binyan only with license tables  
- GRC: lemma+attested case as evidence only → prep+case after non-nominative data → aspect later  

### Phase 3 — Schema/compiler extensions (only if Phase 1 shows value)

Optional `mapping_rules.jsonl`; sense inventory; compile-time rule validation; constraint readback.

### Phase 4 — Broader domains

Only after Phase 1–2 pass; never by inventing morph for English word problems.

---

## 7. No-go list

- Decorative packs not consumed by runtime/eval  
- Unlicensed morph→semantics (nominative=agent, Hiphil=always cause, aorist=punctual, …)  
- Parallel HE/GRC reasoner outside shared canonical operators  
- English→Greek case / Hebrew binyan pseudo-evidence  
- Coverage via guessing / relaxing refuse  
- Claiming holonomy crown proof is LIVE  
- Fluency C01 or ADR-0102 reasoning-capable as morph-constraint proof  
- Broad lexicon growth before observed-morph ablation  
- Filling all binyanim/case tables as “progress” without rules+eval  
- Building production Logos on dormant `packs.evidence`  
- Reopening English fraction_decrease ablation to “add depth value” without observed morph  

---

## 8. Minimum contract for future domain packs

1. Shared language-independent constraint catalog IDs  
2. Mapping rules: rule_id, language, features, preconditions, counterexamples, validity, fail-closed  
3. Provenance: pack_id, version, morphology_id/entry_id, spans  
4. Deterministic compile → immutable ordered candidates  
5. Readback to surface features + canonical constraint  
6. Contradiction with COHERENT evidence → abstain, never override  
7. Eval: observed-language inputs + metadata-only + sealed holdout  
8. No pack-private geometric meaning space (ADR-0005)  

---

## 9. Future ablation/proof design (not authorized here)

| Arm | HE | GRC | Cross-lang | Canonical |
|-----|----|-----|------------|-----------|
| Input | Observed HE | Observed GRC | Authored paired clauses | Language-agnostic operator |
| Executable | Morph rule → constraint | Morph rule → constraint | Data-checked alignment (not crown holonomy until metric fixed) | Existing operators |
| Metadata-only | Roots on, rule off | Case tags on, rule off | Alignment labels off | N/A |
| Fail | Ambiguous root/sense | Ambiguous lemma/case | Conflicting alignments | Insufficient evidence |

---

## 10. Recommended next implementation unit

| Field | Value |
|-------|--------|
| **Branch** | `feat/observed-he-morph-constraint-v0` |
| **Worktree** | `../core-observed-he-morph-constraint` |
| **Why HE first** | LIVE root resolution + denser depth tests; GRC case inventory nominative-skewed |
| **PR-sized scope** | Ambiguity refuse; one authored mapping-rule type + provenance; consumer = teaching/contradiction/abstention; sealed observed-HE fixture; metadata-only control; no bulk lexicon; no English math; no holonomy crown “fix” |
| **Out of scope** | Pack expansion, GRC case tables, binyan universals, fluency C02–C13, dual ontology |

### Reviewer acceptance criteria (future PR)

- [ ] Observed Hebrew inputs (or explicit OOV refuse)  
- [ ] Mapping rules with rule_id, preconditions, counterexamples, provenance  
- [ ] Metadata-only outcome-identical to rule-off  
- [ ] Ambiguous → refuse; wrong=0  
- [ ] No English→HE morph invention  
- [ ] No holonomy crown proof claim  
- [ ] Does not modify relational-operator ablation fixtures/results  
- [ ] Smoke + targeted tests green  

---

## 11. One-line summary

Hebrew/Greek Logos packs are **LIVE as sparse compiled manifolds + depth recognition + domain teaching chains**, but **not** as executable, falsifiable morph→canonical-constraint systems. Holonomy crown proof is **not robust**. Next work is **prerequisite wiring + one observed-HE constraint ablation**, not a giant pack build.
