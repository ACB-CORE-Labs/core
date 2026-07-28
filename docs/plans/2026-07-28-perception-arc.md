# The Perception Arc — why capability has not moved, and the plan that moves it

**Author:** Fable 5 · 2026-07-28 · measured at `0e1be8be`
**Supersedes:** Track B's "widen from 19 constructions" (G-3, as previously specified) — see §4.
**Governed by:** `AGENTS.md` standing philosophy; the pre-registration discipline that produced the §5 NO-GO.

---

## 0. The question this answers

Everything is implemented. The gate is 4 suites / 1,441 tests, `wrong=0` holds everywhere it is claimed, twelve rulings executed, every register clean. **And capability has not moved.** The reader decides ~1% of the held-out corpus, four deduction bands hold the only earned licences, and nothing else serves. Why?

This document answers with measurements, not opinion. Every claim below was verified against the source at `0e1be8be` on 2026-07-28.

---

## 1. The diagnosis, in five measured findings

### F-A · The serving path is 100% symbolic — the geometry never touches it

| Serving-path module | Lines | Geometric refs |
|---|---|---|
| `generate/meaning_graph/reader.py` | 490 | **0** |
| `generate/meaning_graph/model.py` | 229 | **0** |
| `generate/proof_chain/` (15 files) | 3,916 | **0** |
| `chat/deduction_surface.py` | 298 | **0** |
| `chat/curriculum_surface.py` | 406 | **0** |

Comprehension is a hand-written template parser (1 regex, 35 string ops) feeding an ROBDD boolean entailment engine. That is classical symbolic AI, and it is the source of **all** served capability. The Cl(4,1) substrate — 76 modules, concentrated in `core/physics` (24) — runs identity continuity, persistence, and the soak invariants. The two systems intersect on the serving path in exactly **one** place (F-D), and the licensed lanes bypass it.

### F-B · The reader inverts its own ratified design — this is the root cause

**ADR-0252 §2 stage 1** (ratified 2026-07-19) prescribes, verbatim:

> *"Reduce surface text to the primitives the substrate represents: quantities (the Number core-system), entities (the Object core-system), and their **relational roles — containment / transfer / accumulation / comparison** (two-argument relational predicates). **Not surface-slot regexes.**"*

**What was built:** surface-slot templates over **categorical / member / ordering / propositional** relations — Aristotelian syllogistic plus propositional logic. The banned mechanism, over the wrong relation set.

The corpus measurement confirms the inversion independently. On `holdout_dev/v1` (500 problems → 1,798 sentences):

| Feature in real English | Share | Reader constructions for it |
|---|---|---|
| numerals (quantity) | 64.7% | — |
| coordination / relative clause | 48.3% | — |
| `how many` questions | 24.4% | 0 |
| possession (`has/have`) | 18.4% | **0** |
| transfer verbs (`bought`, `gave`, `ate`) | 14.6% | **0** |
| quantitative comparison (`twice as many`) | 10.0% | 2 (ordering only) |
| explicit `if/then` | **0.1%** | **4 — 21% of the inventory** |

**Read rate: 1.28%** (23 of 1,798 sentences; 93.16% fail as `no_template_match` — upstream of vocabulary, upstream of every flag). The relation kinds the ADR prescribes are precisely the ones missing. Not packs (0.67%; `unknown_morphology` never fires). Not wiring (the failure is before any flag is consulted). **Design-to-implementation inversion.**

### F-C · The template architecture cannot produce chunk lifts — only overfit slivers

An enumerative parser generalizes by exactly zero: each new construction is a hand-fitted rule matching one surface shape. 19 constructions → 1.28%. Reaching 50% coverage this way means hundreds of hand rules, each an overfit. **Chunk-sized lifts are architecturally unavailable from this front end** — which is why none have appeared despite everything downstream working.

### F-D · Geometry participates in exactly two cognitive mechanisms — and both are stranded

1. **Attention.** `use_salience` (default ON) computes field curvature (`SalienceOperator`) → `AttentionOperator` → allowed vocabulary indices, on the generic pipeline lane. But `deduction_surface` and `curriculum_surface` **intercept before generic dispatch** — so the only lanes that ever earned licences bypass the one serving-path mechanism the geometry has. (Also: `use_salience` is one of the two default-ON flags with no recorded rationale — flag register §1.)
2. **The relation compiler.** `core/physics/relation_compiler.py` compiles an affine relation into a `ProblemHamiltonian` whose **ground state is the answer as a null point** — deliberately never evaluating `scale·input + offset` in Python. This is real geometric computation: a relation encoded as an **operator acting on state**. It is off-serving, Tier-1-only (single affine relation), and fed by a math reader that decides **5 of 500** holdout cases (G-21).

**Both readers — logic (1.28%) and math (1.0%) — are enumerative front ends starving engines that work.**

### F-E · The §5 NO-GO killed the alignment bridge; the composition bridge was never tested

§5 refuted structure-as-**point-positions** aligned by conformal Procrustes **under similarity**: the quotient that delivers attribute-invariance annihilates structural contrast. Its own scope note excludes other Cl(4,1) representations — and the untested branch is the one the relation compiler already embodies in miniature: **relations as operators, meaning as composition.** A transfer is a versor acting on a state, not a point pair. Composition ("what operator sequence produces this state?") lives in a different quotient than alignment ("do these configurations match?"), and the §5 argument does not reach it.

**Summary sentence:** the engines work, the substrate works, the discipline works; the perception layer violates its own ratified design, feeds <2% of real input to the engines, and cannot generalize by construction. Fix perception once, compositionally, per the design that was already ratified — and every downstream engine's capability multiplies instead of crawling.

---

## 2. The plan

Sequenced per `docs/conceptualizing_engineering_mastery.md`: measure → decide the paradigm → build once → reconnect → delete. Nothing is built before its paradigm question is answered; nothing survives that the new layer supersedes.

### Phase 0 · Pin the ground truth · **S**

- **G-24** in the gap register: findings F-A…F-E, Tier A (it re-scopes Track B and Track C's entry conditions).
- **The read-rate lane** (discharges G-21's open ask): `evals/perception/read_rate.py` measuring sentence-level read rate on `holdout_dev/v1` — logic reader and math reader, refusal taxonomy included. Pinned as a **floor ratchet** (1.28% / 1.0% at `0e1be8be`): the number may only rise, and a rise is a reviewed decision. This is the metric the arc is accountable to — capability, not machinery.

### Phase 1 · The §2 experiment — compositional core-primitive reading · **M** · *pre-registered, GO/NO-GO*

The §5-shaped experiment for the untested branch. **Hypothesis H2:** a reader that (a) maps text onto the **four ratified primitives** — containment, transfer, accumulation, comparison — plus the Number and Object core-systems; (b) encodes each relation as an **operator** (the `relation_compiler` pattern, generalized); and (c) derives sentence meaning by **composition** of operators — generalizes **multiplicatively**: built from *k* atomic constructions, it reads novel compositions it was never shown.

**Pre-registered criterion, committed before the run** (same discipline as `299c92be`):
- **Coverage:** ≥ an order of magnitude over the enumerative ceiling on held-out `holdout_dev/v1` sentences — target ≥ 30% sentence read-rate from ≤ 30 declared primitives (vs 19 templates → 1.28%).
- **Honesty:** zero wrong readings. A mis-read is strictly worse than a refusal (G-2's whole lesson); every reading is checked against a gold role-assignment on a labelled slice.
- **Compositionality proof:** held-out *compositions* (novel primitive sequences) must read correctly with **zero per-composition rules** — the assertion that separates a compositional mechanism from a bigger template pile.

**NO-GO branch, declared now:** if composition over geometric operators does not generalize, the honest conclusion is that Cl(4,1) is a state substrate, not a comprehension mechanism — and the reader is rebuilt as a principled **symbolic compositional grammar** (small combinator core + declared lexicon) instead. Either verdict exits the template treadmill; a well-controlled NO-GO is full credit, as §5 proved.

### Phase 2 · Build the perception layer per the winner · **L**

One front end replacing both readers, structured as the repo's own governing pattern (ADR-0263 rule 5 — declared in the table, not the call site):

- **A small combination core** (code): role binding, operator composition, quantity/entity tracking. This is the only part that is code, and it does not grow with coverage.
- **A construction lexicon** (data): constructions and lexical mappings as declared tables. **Growth = adding rows, not writing parsers.** The gate cost of new coverage is a table diff, reviewable in one glance — the anti-overfit property, made structural.
- Wired to both engines: role-predicate graphs → `proof_chain` (logic); quantity relations → `relation_compiler` corridor (math). `quantity_kernel` (Number) and entity tracking (Object) as the two core-systems the ADR names.

### Phase 3 · Reconnect the corridor to serving · **M**

`parse_and_solve` → Hamiltonian corridor is off-serving today. When the new perception layer feeds it, it goes through the **now-honest** licence machinery (post-R-13/R-8: distinct evidence, split outcome mix, `wrong=0`-or-refuse). Capability target measured on the pinned lane: holdout decision rate 1% → tracked leaps as primitive coverage composes. Lifts arrive in chunks or the paradigm is wrong — that is the falsifiable commitment.

### Phase 4 · The deletion wave · **S** — *the "scrap what earned scrapping" half*

- **G-3's template-widening program: superseded.** No more hand constructions in the enumerative reader; it stays serving for the logic bands it already handles until Phase 2 supersedes it in place (nothing torn out before its replacement proves out — §6's own discipline, applied honestly this time).
- **Curriculum-serve machinery: parked.** It licenses nothing (R-8 measured: zero bands), and its earnable capability is *declining to answer*. The corpus is kept; the lane sleeps until the new layer gives it something to license.
- **`sensorium/` stays parked** behind P-3's criterion, which is now honest: no modality enters while text perception is at 1%.
- The 15 gate-unreachable suites get re-examined as lanes consolidate — deletion first, promotion second, per philosophy 1.

### Phase 5 · Governance · **S** — *Shay's, prepared to cost one word each*

- **ADR-0252 amendment:** record that §2 stage 1 was implemented in inversion of its own text (banned mechanism, wrong primitives), and bind the §6 build clause to Phase 1's pre-registered verdict.
- **`use_salience` ruling:** it is default-ON with no recorded rationale and the licensed lanes bypass it. Phase 2 makes attention either load-bearing on the new lane (keep, document, measure) or decorative (off). The flag register's "no criterion recorded" entry gets its criterion.
- **Ratchet:** the read-rate floor may only rise; every phase reports against it.

---

## 2b. Pass-3 amendments — from the third external audit (2026-07-28), verified in-tree

A red-team audit was cross-examined against the source. Three of its six faults were stale or mis-attributed (see the triage in `31-hindrance-audit.md`), **but its direction flushed out two subsystems this plan's own author had missed** — and they change Phases 1–2 from "build" to "connect and test":

- **The faithful §2 reader already exists, dark.** `core/semantic_primitives/` (typed `Container`, `ConservationLaw`, `DimensionalType` — *"linguistic → field compilation"*) feeds `generate/linguistic_pipeline/` (layers A/B/C + `field_integration.py`, **51 geometric refs**): surface text → typed constraints → **conformal points / composed rotors** → `versor_condition` + GoldTether closure. **Nothing on the serving side calls it.** So F-B sharpens: the ratified design was not merely inverted by the serving reader — it was *also implemented faithfully* in a parallel pipeline that never reached dispatch. Two readers: the wrong one serving, the right one dark.
- **The recognizer junction is built, not blocked.** `core/cognition/pipeline.py` step 0b (ADR-0144) attaches `DerivedRecognizer` (anti-unification) and can derive the articulation graph from the admitted `EpistemicNode` — behind `recognition_grounded_graph = False`, one of the flag register's four *"waiting on a transition window that has not been closed"* entries.

**The pattern, named once:** `linguistic_pipeline`, the ADR-0144 recognizer step, and `relation_compiler` are three instances of one class — **correct mechanisms built dark behind unruled flags while enumerative stopgaps serve.** The flag register's §3a hesitancy cluster (`recognition_grounded_graph`, `realizer_grounded_authority`, `forward_graph_constraint`, `unified_ingest`) is this same unfinished migration, seen flag-side. The disease is not "never built"; it is **transition windows that never close.**

**Consequences for the phases:**
1. **Phase 1 (H2) runs on existing machinery, not new scaffolding** — extend `layer_a_english` to the four ratified primitives and encode relations as operators through `field_integration`'s composed-rotor path. Adopted from the audit verbatim into the pre-registration: an explicit **non-collapse criterion** — the §5 `add`-vs-`subtract` minimal pair (residual exactly 0.0 under similarity alignment) must show non-zero relational contrast under operator composition, as a named must-pass case.
2. **Phase 2 starts from the dark-bridge inventory** (the four §3a flags + the linguistic pipeline), wiring and measuring before writing anything new — "less machinery" made concrete.
3. **The `use_salience` ruling moves from Phase 5 to before Phase 3** — the read-rate lane (Phase 0) is pre-salience and unconfounded, but serving evals are not; an undocumented default-ON attention mask must be ruled before licences are measured through it.

## 3. What this plan deliberately does not do

- It does not touch `core/physics`, the algebra, the reliability gate, or the ledger discipline. Those are correct and load-bearing.
- It does not delete the enumerative reader before its replacement proves out — supersession-in-place, per the ADR's own preserved rule.
- It does not promise the geometric branch wins Phase 1. It promises the question is **decided** the way §5 was: pre-registered, cheap, and honest either way.

## 4. Relationship to the executed assessment arc

The 2026-07-28 arc (30 commits, `797ebad5..0e1be8be`) built the instruments this plan depends on: honest licences (R-13, R-8), the flag register, the reachability ratchets, the pre-registration precedent, and the eleven standing philosophies. None of it moved capability — and F-C explains why nothing could have: the arc hardened a system whose perception layer cannot generalize. This plan is the capability half the enforcement half was for.
