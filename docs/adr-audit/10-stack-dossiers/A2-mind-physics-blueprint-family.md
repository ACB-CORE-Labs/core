# Stack dossier — A2 · Mind-Physics Blueprint Family

**Zone(s):** M0/M1 · `L1-field` (+ Candidate Register **CR-1** attention/allocation, **CR-2** agenda/drive) — per `docs/assessment/02-layer-taxonomy.md` | **Tier:** A
**Member ADRs:** 0006, 0007, 0008, 0009, 0010, 0011 (read order = numeric; the blueprint's own composition order is 0008 → 0009 → 0010, with 0006/0007 as the field-state companions beneath them and 0011 as the terminal seam)
**Dossier author:** Tier-A subagent, ADR Audit Batch 1 | **`verified_at` SHA:** `cbfc8ccb`

**Prior evidence adopted, not re-derived:**
- `docs/assessment/02-layer-taxonomy.md` §1.1 — the blueprint disposition table (four of six members already adjudicated) and §5 CR-1/CR-2.
- `docs/assessment/20-component-cards/attention-allocation.md` (`verified_at 8927c563`) — the definitive read of the live CR-1 mechanism; **adopted wholesale**, spot-checked and re-confirmed at `cbfc8ccb` (§2/ADR-0008 below).
- `docs/assessment/31-hindrance-audit.md` **H-2** (decoration in the runtime constructor), **H-5** (underived constants at the semantic center of generation).
- `docs/assessment/30-gap-register.md` **G-4** (CR-2 — the continuous life has no chooser), **G-14** (CR-1 attention governance — the one-page ADR).
- `docs/assessment/10-layer-cards/M0-substrate.md` — `core/physics/` (37 modules) sits atop the algebra; M0 build `live-serving`.
- `docs/architecture/MIND-PHYSICS-BLUEPRINT.md` staleness banner (2026-07-27) — the blueprint is Draft, stale, non-authoritative, kept for intent.

**Discipline note.** Per the charter's "verify against code, not against documents," every adopted disposition below was spot-checked against `cbfc8ccb`. **Two of the adopted claims were found stale and are revised in this dossier** (AA-A2-4, AA-A2-5) — both concerning artifacts §1.1 recorded as "never built" that in fact exist. The assessment's own later phases had already corrected both; §1.1 was never amended. That is recorded here as a document-fidelity finding, not as a reversal of the assessment's substantive judgment, which stands.

---

## 0. Why this is one stack

These six ADRs are the **complete ADR surface of one document**: `docs/architecture/MIND-PHYSICS-BLUEPRINT.md` (Draft, 2026-05-12), CORE's proposal to govern the cognitive cycle by three composed "physics layers" plus their field-state substrate and output seam. They were authored on a single day (0006–0010 on 2026-05-12; 0011 on 2026-05-13) by a single decision arc, and they cite each other as a closed ring: 0007 opens by naming 0006 as its orthogonal companion; 0008 is the entry layer; 0009 opens "Allocation physics (ADR-0008) governs which field regions are foregrounded — compositional physics governs what happens *after*"; 0010 sits beneath both, shaping the field 0008 then measures salience over; 0011 terminates the chain that 0009's `ArticulationPlanner` explicitly defers to ("the actual surface realization is the responsibility of a downstream renderer").

The arc, one line each:

| ADR | What it added over the last |
|---|---|
| **0006** Field Energy | A scalar `H : FieldState → R≥0` companion to the versor field — *how activated* a region is, discretized to classes E0–E4 |
| **0007** Valence | The orthogonal vector companion to 0006's scalar — *what kind* of force, in five independent channels |
| **0008** Allocation Physics | Layer 1 of 3 — salience as field curvature, attention as traversal schedule, inhibition as its conjugate, all under an explicit `CoherenceBudget` |
| **0009** Compositional Physics | Layer 2 of 3 — what happens after foregrounding: binding → digest → trajectory → articulation plan |
| **0010** Identity Physics | Layer 3 of 3 — the manifold, drive gradients, and exertion/fatigue that shape the field the other two operate on |
| **0011** Renderer | The terminal seam 0009 defers to — a deliberately thin, stateless, caller-provided `Renderer` protocol |

The stack is also the natural unit for the audit's **necessity** question, because it is the repository's single clearest case of the failure mode the charter names: a *layer* proposed as a first-class architectural stratum, where the capability actually landed distributed across other modules under other names. Four of six members are already adjudicated on exactly that basis; this dossier's central contribution is (a) auditing the two unadjudicated members, and (b) asking whether the stack as a whole is a consolidation cluster.

---

## 1. Stack-level claim

**The single sentence:** *CORE's cognitive cycle is governed by three composed physics layers — allocation, composition, identity — operating over a field state that carries, at every point, a scalar energy and an orthogonal valence vector, and terminating in a thin stateless renderer.*

**Is anything here falsifiable in the FA-1 sense?** Mostly no — and that is itself the stack's defining property. Five of the six member ADRs state *mechanism proposals* with no measurable discriminating criterion: no ADR in this stack pre-registers a number that a measurement could return and thereby refute, the way ADR-0005/0015's holonomy-closure claim pre-registered discrimination and FA-1 measured AUC 0.557 against a required 0.80. They are architectural assertions, not empirical ones.

One member is a partial exception, and it is worth stating precisely because it is the stack's only testable claim:

- **Pre-registered criterion (ADR-0007, derived not stated):** the ADR's own rejection of sentiment analysis is explicitly grounded in a discrimination claim — that a five-channel valence bundle preserves distinctions ("a catastrophic lossy projection of this multi-dimensional structure onto a single axis") that a scalar destroys. The falsifiable form: *does any two-valence-bundle pair that differs in force, affect, polarity, emphasis, or orientation produce a different served surface?*
- **Measurement performed / already available:** **performed in this audit**, directly against `cbfc8ccb`. The valence bundle's only serving-path consumer is `chat/runtime.py:2958`, which passes the `ValenceBundle` to `_energy_scalar()` (`chat/runtime.py:229`). That function has no `ValenceBundle` branch: `isinstance(..., EnergyProfile)` is False, `float(bundle)` raises `TypeError`, and the `except (TypeError, ValueError)` arm returns the fallback `1.0`. Executed at `cbfc8ccb`, three structurally distinct bundles (performative/awe/toward; jussive/absolute-negation; None) all returned exactly `1.0`.
- **Verdict:** **NO-GO on the built path.** The distinction ADR-0007 exists to preserve is destroyed at the one place it would have to survive to matter. This is not a lossy projection onto a single axis — it is a projection onto a **constant**, which is strictly worse than the sentiment analysis the ADR rejects. The design claim is not refuted (the lift and propagation genuinely preserve the five channels); the *integration* claim is. See AA-A2-1.

---

## 2. Per-ADR sections

### ADR-0006 — The Field Energy Operator (Hamiltonian Companion Field)

**Audit ID (if a numbering collision):** none | **Family (if phased):** mind-physics blueprint (non-phased ring)
**Zone / stack:** M0 · `L1-field` / A2 | **Tier:** A
**ADR status (as recorded in the file):** Implemented (2026-05-12, implemented 2026-05-14) | **ADR date:** 2026-05-12
**Card author:** Tier-A subagent | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary

- **Decision made:** introduce a scalar field energy operator `H : FieldState → R≥0` as an additional dimension of field state (not a separate system), computed as a fixed weighted sum of convergence density, recency-weighted activation, coherence residual, and morphological aspect-class weight; expose it to consumers as a discrete five-tier energy class E0–E4 rather than a raw scalar, with E4 escalating governance.
- **Alternatives explicitly rejected:** sentiment scoring (one-dimensional, lossy, imports model bias); transformer attention weights (query-relative, ephemeral, cannot drive vault decisions); simple recency timestamp (discards three of four inputs).
- **Artifacts the ADR claims will exist:**
  - `core/physics/energy.py` — `EnergyClass`, `EnergyProfile`, `FieldEnergyOperator`, `aspect_weight()`
  - `field/state.py` — `FieldState.energy: EnergyProfile | None` slot
  - `field/propagate.py` — `propagate_step()` recomputes `EnergyProfile` after each versor step
  - `tests/test_energy.py` — thresholds, aspect weights, governance, propagation
  - Operator weights `0.35/0.25/0.20/0.20` and the six-row class-threshold table
  - Readback integration: `en/readback_rules.py`, `he/readback_rules.py`, `el/readback_rules.py` receive energy class
  - Recall integration: active (E2–E3) vs deep (E0–E1) vs tip-of-tongue
  - Vault integration: E2→E1 + low residual ⇒ vault candidate; vault recall re-activates to E2 transiently
  - Phase transition: E4 on anchor-adjacent region ⇒ `ARCHITECT_REVIEW_REQUIRED`
  - Rust: `core_ingest_rs` exposes energy class alongside `compute_semantic_key`
  - An index of anchor-adjacent field regions initialized at field construction time

#### 2. Implementation cross-reference

| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `EnergyClass` (E0–E4) | yes | `core/physics/energy.py:16` | plus `vault_candidate` / `governance_critical` properties not in the ADR |
| `EnergyProfile` | yes | `core/physics/energy.py:33` | frozen+slots; all eight fields present |
| `FieldEnergyOperator` | yes | `core/physics/energy.py:77` | `.compute()` keyword-only, matches spec inputs |
| `aspect_weight()` | yes | `core/physics/energy.py:66` | table-driven over `aspect`/`tense`/`mood`, 12 entries |
| `FieldState.energy` slot | yes | `field/state.py:114` | `EnergyProfile \| None`, serialized by `_encode_energy` (`:32`) |
| `propagate_step()` recompute | yes | `field/propagate.py:47-71` | policy matches the ADR's stated recomputation rules exactly |
| `tests/test_energy.py` | yes | `tests/test_energy.py` | present, covers thresholds/aspect/governance/propagation |
| Operator weights `0.35/0.25/0.20/0.20` | yes | `core/physics/energy.py:97` | exact match |
| Class thresholds | **partial** | `core/physics/energy.py:98-109` | E4/E3 anchor logic exact; **E1/E2 boundary is `0.37` in code vs `0.38` in the ADR table** — unpinned by any test |
| `{en,he,el}/readback_rules.py` | **no** | — | packs carry `lift_rules.py` only (`packs/he/`, `packs/el/`, `packs/en/`); readback landed as `generate/realizer.py` + `packs/common/runtime_rules.py` |
| Energy-modulated readback | yes (relocated) | `generate/realizer.py:30-39` | `_ENERGY_SURFACE_PREFIX` maps E0→"From memory: ", E1→"I seem to recall: ", E2→"I recall: ", E3/E4→"" |
| Recall active/deep split | yes | `vault/store.py:24,47-49,365-398` | `_VAULT_RECALL_RETHAW_ENERGY` at `EnergyClass.E2` — the ADR's "transient re-activation to E2", built verbatim |
| Vault candidacy criterion | yes | `core/physics/energy.py:24`, `vault/store.py:365` | `EnergyClass.vault_candidate` = {E0,E1}; consumed by `promote_eligible_entries` |
| E4 ⇒ `ARCHITECT_REVIEW_REQUIRED` | **partial** | `core_ingest/compiler.py:154-160` | wired — but keyed on the packet's *declared* `energy_class_hint == "E4"`, not on the operator's *computed* class |
| `EnergyProfile.requires_architect_review` | yes (unreached) | `core/physics/energy.py:44` | referenced only by `tests/test_energy.py:217-256`; no serving path reads it |
| Rust energy alongside `compute_semantic_key` | **no** | — | zero `.rs` files reference energy |
| Anchor-adjacent region index | **no** | `core/physics/energy.py:41` | `anchor_adjacent` is a per-profile bool carried from injection; no index structure exists |

**Build axis:** **full** — every file and symbol in the ADR's own `## Implementation` section exists with the exact declared names, weights, and (bar one threshold digit) thresholds. The unbuilt items are all Decision-section *integration points*, not Implementation-section artifacts; that split is recorded as build-fidelity drift in §5 rather than as a lower build score.

#### 3. Liveness / integration

Traced, not inferred. Energy reaches the serving path by **four independent routes**, any one of which would suffice:

1. **Propagation** — `field/propagate.py:47` recomputes `EnergyProfile` on every versor step of every walk. This is the generation heartbeat.
2. **Salience (the hot path)** — `generate/salience.py:44-47` reads `vocab.energy_for_word(...).raw` as the `baseline` of every `FieldRegion`'s `pressure_magnitude`, which is then the input to the curvature kernel that gates every token walk. Energy is therefore an input to CR-1's ~73%-of-turn-time hot path.
3. **Surface** — `generate/realizer.py:39` `energy_modulated_surface()` prefixes recalled surfaces by class; `chat/runtime.py:3143` calls it; pinned by `tests/test_adr_0145_energy_modulated_surface.py`.
4. **Vault** — `vault/store.py:365-398` reconstructs `EnergyProfile` from stored metadata and feeds `policy.decide()` for promotion.

Compilation is upstream too: `packs/compiler.py:72,339` bakes energy at pack-compile time via `_ENERGY = FieldEnergyOperator()`, matching the ADR's "baked at gate, not re-derived."

**Sabotage test:** stub `FieldEnergyOperator.compute` to return a constant `EnergyProfile` and the observable changes in at least three places: every recall surface loses its class-appropriate prefix (E0 "From memory: " vs E2 "I recall: "), every `FieldRegion.pressure_magnitude` in the salience map collapses to a uniform baseline (changing the curvature ranking and therefore the candidate set of every walk), and vault promotion loses its criterion. **Not decoration** — this is the most genuinely load-bearing ADR in the stack.

One sub-mechanism *is* decoration and must be named separately: `EnergyProfile.requires_architect_review` (`core/physics/energy.py:44`) is read by nothing but its own test. The E4 governance escalation that shipped (`core_ingest/compiler.py:154-160`) is a different mechanism reading a *declared hint* on the packet. Deleting the property changes one test file and nothing else. See AA-A2-6.

**Liveness axis:** **live** — four independent serving-path routes, each failing-if-absent; with one contained decoration sub-finding.

#### 4. Design fidelity — pillars and axioms

| Pillar | Honors / Tension / Violates | Citation (ADR clause + pillar text) |
|---|---|---|
| I. Mechanical Sympathy | **Tension** | The ADR names the cost honestly ("must be updated on every field write… must be profiled") and specifies a Rust hot-path obligation — but the four mixing weights and six thresholds are asserted with no derivation, the same class of underived constant H-5 flags two config lines away. Naming a cost is not measuring it. |
| II. Semantic Rigor | **Honors** | The class vocabulary E0–E4 is defined once, exhaustively, with a stated meaning per tier, and the ADR explicitly refuses to expose the raw scalar ("rather than exposing a raw continuous scalar to all consumers") — one term, one meaning, one surface. |
| III. Third Door | **Honors** | Rejects both visible options by name — sentiment scoring *and* transformer attention weights — and derives energy from structural inputs (convergence, residual, morphology) instead of from either. |

| Axiom | Honors / Tension / Violates | Citation |
|---|---|---|
| 1. Geometry-First | **Honors** | Energy is defined as a property *of the field state at every point*, not a side table keyed by token id. |
| 2. Field-State | **Honors** | Explicit: "It is not a separate system — it is an additional dimension of the field state itself." Realized literally at `field/state.py:114`. |
| 3. Propagation-over-Mutation | **Honors** | `propagate_step` returns a new `FieldState` with a new `EnergyProfile`; nothing is mutated in place (`field/propagate.py:64`). |
| 4. Dual-Correction | **Tension** | Coherence residual is an *input* from the corrective pass, so energy consumes the conjugate rather than having one. There is no operator that corrects energy; a mis-assigned class simply cools out by the `exp(-age/12)` term. |
| 5. Reconstruction-over-Storage | **Honors** | `EnergyProfile` stores the eight structural inputs, not a history of activations; the class is recomputed from them (`field/state.py:32-61` round-trips the inputs, not the outputs). |
| 6. Compilation-Last | **Honors** | The ADR specifies the operator and its output vocabulary; the table (`_ASPECT_WEIGHTS`) is an implementation choice made in code, not in the decision. |
| 7. Reality-over-Inheritance | **Tension** | The Hamiltonian framing is borrowed from physics and carries connotations (conserved quantity, generator of time evolution) that the implementation does not honor — `H` here is a weighted sum, not a Hamiltonian. The metaphor survives on evocation, not structural merit. |

#### 5. Build fidelity — does the code match the decision?

Close, with three specific divergences:

1. **Numeric drift.** The ADR's class-threshold table gives `[0.16, 0.38)` → E1 and `[0.38, 0.62)` → E2. `core/physics/energy.py:104-106` implements `raw >= 0.37` → E2. The boundary moved by 0.01 and no test pins it (`tests/test_energy.py` asserts class membership at safely interior points only, `:133,:143`). A record-vs-reality divergence of exactly the kind `AGENTS.md` Standing Philosophy #5 rates as a defect. (AA-A2-9)
2. **Integration relocated, not built as specified.** The readback integration the ADR routes through three per-pack `readback_rules.py` files landed instead in `generate/realizer.py` + `packs/common/runtime_rules.py`. The *capability* is present and live; the *seam* named in the ADR is not, and the pack directories contain `lift_rules.py` only. This is honest architectural evolution recorded nowhere.
3. **Two consequences never delivered.** The Rust energy path and the anchor-adjacent index are both absent; `anchor_adjacent` survives as a carried boolean, which satisfies the E4 escalation logic but not the ADR's "bounded, static structure… initialized at field construction time."

**Build-fidelity axis:** **partial drift** — the operator matches its spec almost exactly; the integration surface drifted to different files and the governance property split from the governance mechanism.

#### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs

- **Contradicts `Whitepaper.md`?** No. Axiom 2 (Field-State) is arguably this ADR's cleanest instantiation in the corpus.
- **Contradicts `Yellowpaper.md`?** No.
- **Other ADRs:** extended, not superseded. `ADR-0145` (energy-modulated surface) built on it and is pinned; `ADR-0241` (wave energy boundary, `core/physics/wave_energy_boundary.py:22` imports all three energy symbols) and `ADR-0242` (multi-scale energy, `core/physics/multi_scale_energy.py`) are later, larger energy constructions that **compose over** ADR-0006 rather than replacing it. `ADR-0007` cites it as its orthogonal companion. No ADR contradicts it.
- **One unreconciled item:** `docs/assessment/02-layer-taxonomy.md` §1.1 lists five blueprint elements and their dispositions; ADR-0006 and ADR-0007 are **absent from that table entirely**. The blueprint's own staleness banner likewise names only ADR-0008 as "what this document uniquely contributed." Both records silently omit the stack's two most load-bearing members. Not a contradiction — an omission, but one that would lead a reader to under-rate the stack.
- **Continuity axis:** **clean** — extended by 0145/0241/0242, contradicted by nothing.

#### 7. Necessity / generality

1. **Necessity.** Genuinely necessary *as built*, though not for the reason the ADR gives. The ADR justifies energy thermodynamically (articulation "wants" to be said); what actually makes it irreducible is more prosaic and more solid — it is the `pressure_magnitude` baseline of the salience curvature kernel (`generate/salience.py:44-47`) and the vault promotion criterion. Remove it and both break. The system would lose capability.
2. **Reducibility.** No L0/L1 operator subsumes it. The algebra layer (A1: `algebra/`, `cga_inner`, versor apply) supplies *geometric* quantities; energy is a *history-and-provenance* quantity (convergence count, activation age, residual, source morphology) that no geometric operator on `F` can recover, because those inputs are not in `F`. Checked directly: `EnergyProfile`'s eight fields are all extrinsic to the multivector. **This is the one member of the stack that is not reducible to the field/algebra layer** — and the honest reading is that it is a *state annotation carried alongside* the field, correctly implemented as such (`FieldState.energy`), rather than a physics layer.
3. **Extensibility.** Already extended twice, and that is the consolidation signal: `ADR-0241` (wave energy boundary) and `ADR-0242` (multi-scale energy) are both later energy constructions in `core/physics/`. Whether three coexisting energy mechanisms are one generalizable operator or three narrow ones is a real cross-stack question — flagged for `22-consolidation-report.md` as a **pairing candidate: ADR-0006 ⊕ ADR-0241 ⊕ ADR-0242**, to be resolved when Batch 5 audits the latter two. Not resolvable from within this stack.

**Necessity/generality axis:** **irreducible** — no L0/L1 operator can produce its inputs; live on four routes; the only member of this stack that earns its place. Carries one open cross-stack consolidation question (0241/0242).

#### 8. Fitness / value

- `docs/assessment/10-layer-cards/M0-substrate.md:16,37` — `field/` and `core/physics/` recorded `live-serving`; energy is inside that verdict.
- `docs/assessment/20-component-cards/attention-allocation.md:11` — establishes that the salience path (which consumes energy) is the measured hot path, default-ON.
- `tests/test_energy.py` — full operator coverage, present and current.
- `tests/test_adr_0145_energy_modulated_surface.py` — pins the surface-modulation consumer.
- `tests/test_fieldstate_codec.py:17` — pins energy/valence round-trip through the persistence codec.
- No eval in `evals/obligation_*/` isolates energy's contribution to answer quality; its value is established by structural indispensability, not by a measured delta.

**Fitness axis:** **live and load-bearing, value structurally established but never measured** — cited: M0 layer card, attention-allocation component card, three test pins. No eval isolates its contribution; that is a gap in evidence, not in the mechanism.

#### 9. Findings raised

- **AA-A2-6** 🔵 — `EnergyProfile.requires_architect_review` is decoration: read only by `tests/test_energy.py`; the E4 escalation that ships (`core_ingest/compiler.py:154-160`) keys on a declared packet hint, not the computed class. (§3)
- **AA-A2-9** 🟢 — E1/E2 threshold is `0.37` in code vs `0.38` in the ADR table, unpinned by any test. (§5)
- **AA-A2-11** 🟢 — Two ADR-0006 consequences never delivered: the Rust energy path in `core_ingest_rs`, and the anchor-adjacent region index. (§2, §5)
- **AA-A2-12** 🟢 — ADR-0006 and ADR-0007 are absent from `02-layer-taxonomy.md` §1.1's blueprint-disposition table and from the blueprint's own staleness banner, which credits only ADR-0008. The stack's two most load-bearing members are invisible in both governing records. (§6)

#### 10. Evidence sources actually consulted

- ADR-0006 in full; `core/physics/energy.py` in full; `field/state.py` in full; `field/propagate.py` in full.
- `generate/salience.py` in full (the energy→salience link); `generate/realizer.py:18-39`; `vault/store.py:24,38-49,365-398`; `core_ingest/compiler.py:85-110,150-165`; `packs/compiler.py:14,72,339-355`; `vocab/manifold.py:36-37,74-75,227`.
- `tests/test_energy.py` (threshold pins, `requires_architect_review` coverage); test-file inventory for energy/valence.
- Executed at `cbfc8ccb`: repo-wide `rg` for every claimed symbol; directory listing of `packs/{he,el,en}/` confirming `lift_rules.py` and the absence of `readback_rules.py`; `rg` over all `*.rs` confirming zero energy references.
- `docs/assessment/10-layer-cards/M0-substrate.md`; `docs/architecture/MIND-PHYSICS-BLUEPRINT.md` header.

---

### ADR-0007 — The Valence Layer

**Audit ID (if a numbering collision):** none | **Family (if phased):** mind-physics blueprint (non-phased ring)
**Zone / stack:** M0/M1 · `L1-field` / A2 | **Tier:** A
**ADR status (as recorded in the file):** Accepted | **ADR date:** 2026-05-12
**Card author:** Tier-A subagent | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary

- **Decision made:** attach a five-channel `ValenceBundle` — affective (a *set* of primitives), force (illocutionary class), emphasis (mechanism + degree), polarity (value + kind), orientation (direction + target) — to every field point and every `CandidateGeometricPressure` packet, lifted deterministically from source morphology by pack lift rules rather than inferred by a downstream model; and use it, together with ADR-0006's energy class, to shape surface realization.
- **Alternatives explicitly rejected:** sentiment analysis ("a catastrophic lossy projection… onto a single axis"); emotion classifiers (inferred label vs lifted fact); LLM pragma-linguistic tagging (nondeterministic, D3, cannot be `AUTO_ACCEPT_ELIGIBLE`).
- **Artifacts the ADR claims will exist:**
  - `ValenceBundle` with all five channels
  - `ForceClass` (9 members), `EmphasisProfile`/`EmphasisMechanism`/`EmphasisDegree`, `PolaritySpec`/`PolarityValue`/`PolarityKind`, `OrientationSpec`/`OrientationDirection` (10 members)
  - `AffinePrimitive` set of 15 named affect primitives
  - `packs/common/affect_primitives.jsonl` — the primitive definitions
  - Per-pack lift rules mapping lemmas + morphology → primitives (coarse for `en`, fine for `he`/`el`)
  - `valence` field in every `CandidateGeometricPressure.payload_json`
  - SemanticGate structural validation of the bundle in `IngestCompiler`
  - Valence written into the field alongside the versor update
  - Valence available to the readback layer for surface generation
  - **Articulation behaviors:** `force: performative` ⇒ no hedging; `force: optative` ⇒ softened register; `affective: [grief, longing]` ⇒ slowed syntax/shorter clauses; `emphasis.degree: absolute` ⇒ foregrounded element first; `polarity.kind: absolute` ⇒ unqualified negation; `orientation.direction: toward` ⇒ directional framing
  - A **tension index** alongside the convergence index; valence tension at E4 ⇒ `ARCHITECT_REVIEW_REQUIRED`; tension at E0–E1 ⇒ resting paradox

#### 2. Implementation cross-reference

| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `ValenceBundle` (5 channels) | yes | `core/physics/valence.py:44` | all five channels present, frozen+slots |
| `ForceClass` | yes | `core/physics/valence.py:11` | all 9 members exact |
| `EmphasisProfile` | **partial** | `core/physics/valence.py:24` | fields present but `mechanism`/`degree` are bare `str`, not the ADR's closed enums |
| `PolaritySpec` | **partial** | `core/physics/valence.py:31` | `value`/`kind` are bare `str \| None`; `PolarityValue`/`PolarityKind` enums absent |
| `OrientationSpec` | **partial** | `core/physics/valence.py:37` | `direction` is bare `str`; `OrientationDirection` enum absent |
| `AffinePrimitive` (15 members) | **no** | `core/physics/valence.py:45` | `affective: frozenset[str]` — untyped strings; `lift_valence` can only ever emit 3 of the 15 (`awe`, `peace`, `exultation`, `:118-124`) |
| `packs/common/affect_primitives.jsonl` | **no** | — | does not exist anywhere in the repo |
| Per-pack lift rules (he/el fine-grained) | **partial** | `core/physics/valence.py:92-156` | one shared `lift_valence()` in `core/physics/`, not per-pack; ~8 hardcoded lemmas + 2 preposition/particle tables. `packs/{he,el,en}/lift_rules.py` exist but do not produce valence |
| `valence` in `payload_json` | yes | `packs/common/runtime_rules.py:11,55` | emitted alongside `energy_class_hint` (`:63`) |
| SemanticGate structural validation | yes | `core_ingest/compiler.py:104-107,185` | `_validate_valence_payload`; structural only, as specified |
| Valence written into field | yes | `ingest/gate.py:429` | `FieldState(..., valence=_field_valence(tokens, vocab))` |
| Valence propagated | yes | `field/propagate.py:71`, `field/state.py:115,159`, `generate/stream.py:127,190,222,629`, `session/context.py:85,100,194,238,317,336` | carried unchanged through every step and every session hop |
| Valence serialized | yes | `field/state.py:64-105` | full five-channel round-trip; pinned by `tests/test_fieldstate_codec.py:17` |
| Valence available to readback | **no** | — | no readback/surface module imports `ValenceBundle` |
| `force: performative` ⇒ no hedge | **no** | — | no consumer of `.force` downstream of `ingest/gate.py:401` |
| `affective` ⇒ slowed syntax | **no** | — | no consumer of `.affective` downstream of `ingest/gate.py:390` |
| `polarity.kind: absolute` ⇒ unqualified | **no** | — | no consumer of `.polarity` downstream of `ingest/gate.py:403` |
| `orientation.direction` ⇒ framing | **no** | — | no consumer of `.orientation` downstream of `ingest/gate.py:404` |
| `emphasis.degree` ⇒ fronting | **no** | — | `.emphasis` read only at `ingest/gate.py:395` for bundle *ranking*, never for surface |
| Tension index | **no** | — | no tension index, no tension tracking, no valence-tension escalation anywhere |

**Build axis:** **partial** — the bundle, its lift, its gate validation, its field carriage and its serialization are all genuinely built and correct. Everything from the field outward — the entire "How Valence Drives Articulation" section, the affect-primitive vocabulary, and the tension index — is absent. The ADR is built up to the field boundary and stops.

#### 3. Liveness / integration

The bundle is genuinely produced and genuinely carried. `packs/compiler.py:15,345` lifts it at pack-compile time; `vocab/manifold.py:231` serves it per word; `ingest/gate.py:381-405` aggregates the per-token bundles into one field-level bundle by a documented ranking (non-declarative force > strong/absolute emphasis > affect count, `:394-396`); `field/propagate.py:71` and `generate/stream.py` carry it unchanged through every propagation step; `field/state.py:64-105` round-trips all five channels through persistence.

**And then it stops.** Repo-wide search for consumers of `.force`, `.affective`, `.polarity`, `.orientation`, `.emphasis` downstream of the gate returns nothing in any serving module. (The `polarity` hits in `teaching/contemplation.py:350-373` and `sensorium/vision_event/` are unrelated homonyms — evidence-affirms/falsifies and vision-event sign respectively; checked and excluded.)

The single serving-path link is `chat/runtime.py:2958`:

```python
current_valence = _energy_scalar(getattr(result.final_state, "valence", None))
```

`FieldState.valence` is a `ValenceBundle` (`field/state.py:115`). `_energy_scalar` (`chat/runtime.py:229-237`) branches on `None` → `1.0`, on `EnergyProfile` → `.raw`, else `float(obj)` inside `try/except (TypeError, ValueError)` → `1.0`. A `ValenceBundle` is neither, and is not float-convertible, so **every bundle returns exactly `1.0`**. Confirmed by execution at `cbfc8ccb` against three structurally distinct bundles.

The consequence propagates deterministically. `self._last_valence` initializes to `0.0` (`chat/runtime.py:740`) and is set to `current_valence` after each turn (`:2960`). So `valence_delta` (`:1820`) is `1.0` on turn 1 and **exactly `0.0` on every subsequent turn, forever**. Its two consumers in `generate/surface.py`:

- `_pick_conjunction` (`:122-123`) — `"but" if valence_delta < 0 else "and"` ⇒ can never return `"but"` on the serving path.
- `_apply_contrast` (`:215-216`) — fires only when `valence_delta < -0.3` ⇒ structurally unreachable on the serving path.

Both branches are exercised by `tests/test_dialogue_fluency_regression.py:86`, which constructs `SurfaceContext(valence_delta=-1.0)` directly. The test proves the function; nothing proves the wiring. This is the "identity, not value" discipline exactly: a float of the right type flows to the right place, and its identity is a constant.

**Sabotage test:** replace `lift_valence()` with a function returning a default `ValenceBundle()` for every input. Observable change on the serving path: **none**. Surfaces are byte-identical, because the only consumer discards the bundle's contents. Changes would appear only in `FieldState.to_dict()` payloads and the codec test. By the charter's own words: *this is decoration, not a minor caveat* — for the consumption half. The production and carriage half is real, correct, and would be immediately useful the moment a consumer existed.

**Liveness axis:** **wired-but-unreached** — produced, validated, carried, and persisted on the live path; consumed by nothing. The one nominal consumer is a type-confusion bug that collapses it to a constant.

#### 4. Design fidelity — pillars and axioms

Scoring the decision as written, independent of the build.

| Pillar | Honors / Tension / Violates | Citation (ADR clause + pillar text) |
|---|---|---|
| I. Mechanical Sympathy | **Tension** | The ADR names one cost (tension-index size, "bounded… but must be designed explicitly") but is silent on the per-token lift cost and the bundle's memory footprint on every field point — and it proposes attaching five channels to *every* field point, the hottest data structure in the system. |
| II. Semantic Rigor | **Honors, exemplary** | The strongest instance in this stack: every channel is a closed enumeration with a stated linguistic warrant, and the *lo*/*al* and *ou*/*mē* distinctions are argued as load-bearing rather than decorative. The set-valued affect channel is specifically justified against scalar collapse (*hesed* = `tenderness` ∧ `fierce_loyalty`). |
| III. Third Door | **Honors** | Rejects both visible options by name (sentiment analysis, emotion classifiers) *and* the fashionable third (LLM tagging), then derives the answer from deterministic morphological evidence — the textbook shape of this pillar. |

| Axiom | Honors / Tension / Violates | Citation |
|---|---|---|
| 1. Geometry-First | **Tension** | Valence is a typed record attached to field points, not an intrinsic geometric structure. The ADR calls it a "vector" but never gives it a metric, a composition law, or a direction in the manifold — it is a struct, and calling it a vector is the axiom's own warning about choosing structures before finding the space. |
| 2. Field-State | **Honors** | Explicitly attached to every field point and every pressure packet; realized at `field/state.py:115`. |
| 3. Propagation-over-Mutation | **Honors** | Carried immutably; `field/propagate.py:71` passes the bundle forward without rewriting it. |
| 4. Dual-Correction | **Tension** | The tension mechanism ("the field holds both") is the nearest thing to a conjugate, but the ADR explicitly declines to resolve it ("not automatically resolvable") — which is intellectually honest and simultaneously means no corrective operator is specified. |
| 5. Reconstruction-over-Storage | **Honors** | Lifted from source morphology on demand rather than stored per-utterance; the bundle encodes structure sufficient to regenerate the distinction. |
| 6. Compilation-Last | **Honors** | Specifies channels and their vocabularies; the lookup tables are an implementation choice. |
| 7. Reality-over-Inheritance | **Honors** | The abstraction is derived from Hebrew/Greek morphology as it actually is, not imported from an NLP tradition — and the ADR says so at length. |

#### 5. Build fidelity — does the code match the decision?

Two divergences, one contained and one severe.

1. **Type erosion (contained).** The ADR specifies four closed enumerations — `AffinePrimitive` (15), `EmphasisMechanism` (5), `EmphasisDegree` (4), `PolarityValue` (4), `PolarityKind` (5), `OrientationDirection` (10). Only `ForceClass` survived as an enum (`core/physics/valence.py:11`). The rest are bare `str` fields, so nothing prevents an unlisted value from entering the bundle. Combined with the missing `affect_primitives.jsonl`, the affect channel is not merely untyped — `lift_valence` can only ever emit three of the fifteen specified primitives (`awe`, `peace`, `exultation`), so twelve of the ADR's fifteen affect primitives are unreachable by construction.
2. **The consumption half contradicts the decision (severe).** ADR-0007's entire purpose — stated in its Context ("What distinguishes them is not *how much* force is in play but *what kind*") and operationalized in "How Valence Drives Articulation" — is that the five channels reach the surface layer. The code instead routes the bundle into a function that collapses it to a constant `1.0`. The ADR rejected sentiment analysis for projecting onto a single axis; the implementation projects onto a **single point**. The built system does not merely fall short of the decision, it realizes the specific outcome the decision was written to prevent.

**Build-fidelity axis:** **contradicts** — not on the production side (which matches well), but at the integration point that carries the ADR's entire justification. Recorded as `contradicts` rather than `partial drift` because the divergence is at the load-bearing claim, not at its periphery.

#### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs

- **Contradicts `Whitepaper.md`?** No — Axiom 2 honored; Axiom 1 in tension (§4) but not contradicted.
- **Contradicts `Yellowpaper.md`?** No.
- **Other ADRs:** cites ADR-0006 (companion) and ADR-0005 (language pack contract, lift/readback interfaces) — and the ADR-0005 dependency matters: **FA-1 ruled ADR-0005/0015's cross-language semantic-ground claim `DEFECTIVE` on 2026-07-28** (AUC 0.557 vs required 0.80). ADR-0007's premise that Hebrew/Greek morphology yields discriminating cross-language semantic signal is adjacent to the claim FA-1 refuted. It is not the *same* claim — FA-1 measured holonomy closure across languages, while ADR-0007 claims within-language morphological lift — so this is not an automatic cascade. But it belongs in the cascade-check A3 is running, and the honest note is that nothing in this stack independently establishes the morphological-lift claim either. Flagged, not ruled.
- No later ADR supersedes ADR-0007. No successor articulation of valence exists anywhere in the corpus; unlike ADR-0009/0010, which were superseded by *stronger* implementations, ADR-0007 was simply never continued.
- **Continuity axis:** **clean** (nothing contradicts it) — but with an **orphan** qualifier: Accepted, unsuperseded, half-built, and absent from `02-layer-taxonomy.md` §1.1's disposition table, so no record anywhere says what became of it. That absence is the continuity problem.

#### 7. Necessity / generality

This is the axis the task asks to be pressed hardest, given 4/6 of the stack already carries a superseded/stale/never-landed verdict. **Is ADR-0007 heading the same direction? Yes — but by a different route, and the distinction matters for what should be done about it.**

1. **Necessity.** As currently built: **not necessary**. The sabotage test in §3 is unambiguous — stub the lift, nothing observable changes. The system today would lose no capability if the entire valence layer were deleted, except the codec test and some persisted payload fields. As *designed*: the capability is genuinely absent from CORE and genuinely wanted — nothing else in the repository distinguishes a performative from a declarative, or Hebrew *lo* from *al*, at the surface layer. So this is not the ADR-0011 case (a stale line to retire) nor the ADR-0009/0010 case (superseded by something stronger). It is a **third disposition the assessment's §1.1 table has no row for: built-but-unconsumed, unsuperseded, and still wanted.**
2. **Reducibility.** Not reducible to an L0/L1 operator — checked, and for the same reason as ADR-0006: the algebra/field layer operates on `F`, and valence's inputs (lemma, mood, stem, particle identity) are not in `F`. Neither stack A1's rotor-as-operator (ADR-0004) nor the field layer provides this in more general form. It *is*, however, structurally the same **kind** of thing as ADR-0006: a typed, provenance-derived annotation carried alongside the field state, lifted at compile time, propagated unchanged, and consulted at the surface. That is the consolidation observation, not a reduction: **ADR-0006 ⊕ ADR-0007 are one mechanism — "field-state annotations lifted from source structure" — that landed as two.** ADR-0006's half was consumed and thrived; ADR-0007's half was not and atrophied. The difference in outcome is entirely about whether a consumer existed, which is strong evidence they should have been one construction with one integration contract.
3. **Extensibility.** Generalized slightly, the ADR-0006 `EnergyProfile` pattern — carried on `FieldState`, encoded by a codec, consumed at the realizer via a class→behavior table (`generate/realizer.py:30-39`) — would absorb ADR-0007's bundle wholesale, and would have given it the surface consumer it never got. This is a concrete, cheap consolidation: the realizer already has exactly the dispatch shape valence needs.

**Necessity/generality axis:** **generalization-candidate** — reducible not to an existing L0/L1 operator but to a *merger with ADR-0006* under one "field-state annotation" mechanism with one integration contract. Feeds `22-consolidation-report.md` as the stack's primary consolidation cluster (see §3).

#### 8. Fitness / value

- `tests/test_fieldstate_codec.py:17` — pins the five-channel round-trip. This is the *only* pin that would fail if valence were deleted, and it tests persistence, not behavior.
- `docs/assessment/` — **no layer card, no component card, no gap-register entry, and no hindrance-audit entry mentions valence at all.** Searched all of `30-gap-register.md`, `31-hindrance-audit.md`, and the M0/M1 layer cards: zero hits. The assessment did not see this ADR.
- `evals/obligation_*/` — no eval exercises any valence channel.
- `docs/analysis/`, `docs/PROGRESS.md` — no valence fitness evidence.

**Fitness axis:** **no evidence found** — and per the card template, that is itself the finding. An Accepted ADR, half-built, has produced no measured value, has no card, and appears in no register. It is the least-witnessed member of this stack.

#### 9. Findings raised

- **AA-A2-1** 🟡 — Type-confusion defect: `chat/runtime.py:2958` passes a `ValenceBundle` to `_energy_scalar()` (`:229`), which has no bundle branch and returns the fallback `1.0` for every input. `valence_delta` is therefore `0.0` on every turn after the first, making `_pick_conjunction`'s `"but"` branch (`generate/surface.py:123`) and `_apply_contrast` (`:216`) structurally unreachable on the serving path. Empirically confirmed at `cbfc8ccb`. (§1, §3)
- **AA-A2-2** 🟡 — ADR-0007's entire "How Valence Drives Articulation" section is unimplemented: no consumer of `.force`, `.affective`, `.polarity`, `.orientation`, or `.emphasis` exists downstream of `ingest/gate.py:381-405`. The ADR is built to the field boundary and stops. (§2, §3)
- **AA-A2-3** 🟢 — Claimed artifacts absent: `packs/common/affect_primitives.jsonl` (nonexistent), and four of five channel enums degraded to bare `str`, leaving 12 of 15 specified affect primitives unreachable by construction. (§2, §5)
- **AA-A2-13** 🟡 — ADR-0007 is an unregistered orphan: Accepted, unsuperseded, half-built, with **zero** mentions across the gap register, hindrance audit, layer cards, and the §1.1 disposition table. No record anywhere states its disposition. (§6, §8)
- **AA-A2-14** 🔵 — Consolidation: ADR-0006 and ADR-0007 are one mechanism (field-state annotation lifted from source structure) built as two, and the realizer's existing class→behavior dispatch (`generate/realizer.py:30-39`) would absorb valence directly. (§7)

#### 10. Evidence sources actually consulted

- ADR-0007 in full; `core/physics/valence.py` in full; `field/state.py` in full (codec + slot); `ingest/gate.py:381-429`; `chat/runtime.py:229-237, 740, 1803-1831, 2958-2960`; `generate/surface.py:47, 61, 122-130, 215-216, 266`.
- `packs/common/runtime_rules.py:10-11,55,63`; `packs/compiler.py:15,345,405,558`; `vocab/manifold.py:36-37,74-75,231`; `core_ingest/compiler.py:104-107,185`.
- **Executed at `cbfc8ccb`** (`uv run python`): `_energy_scalar()` applied to three structurally distinct `ValenceBundle`s and to `None` — all four returned `1.0`. This is the load-bearing evidence for AA-A2-1 and was measured, not inferred.
- Repo-wide `rg` for `.force`/`.affective`/`.polarity`/`.orientation`/`.emphasis`/`valence_for_word` with manual exclusion of the `teaching/contemplation.py` and `sensorium/vision_event/` homonyms.
- `rg` for `affect_primitives` and `readback_rules` across the tree (both absent); directory listings of `packs/`, `packs/common/`, `packs/he/`, `packs/el/`.
- Negative searches recorded: `docs/assessment/30-gap-register.md`, `31-hindrance-audit.md`, `10-layer-cards/M0-substrate.md`, `10-layer-cards/M1-knowledge-memory.md` — zero valence hits in all four.

---

### ADR-0008 — Allocation Physics

**Audit ID (if a numbering collision):** none | **Family (if phased):** mind-physics blueprint (non-phased ring)
**Zone / stack:** M3 de facto (unowned; registered **CR-1**) — blueprint-assigned to `L1-field` / A2 | **Tier:** A
**ADR status (as recorded in the file):** Accepted | **ADR date:** 2026-05-12
**Card author:** Tier-A subagent | **`verified_at` SHA:** `cbfc8ccb`

> **Adopted evidence.** `docs/assessment/20-component-cards/attention-allocation.md` is a full component card on exactly this mechanism, verified at `8927c563`. Its findings are adopted rather than re-derived. Every code claim in it was spot-checked at `cbfc8ccb` and **all hold unchanged**; the file:line references below are re-verified at the current SHA.

#### 1. Content summary

- **Decision made:** replace transformer-style attention entirely with a three-operator allocation layer over the versor field — salience as *field curvature* (deflection a region induces in its neighbors), attention as a *traversal schedule* (not a weight distribution) constrained by an explicit `CoherenceBudget`, and inhibition as attention's *conjugate*, an active suppression mask applied before traversal.
- **Alternatives explicitly rejected:** transformer dot-product attention (geometrically meaningless on the versor manifold; opaque to correction); sparse attention (Longformer/BigBird — right structure, wrong foundation); memory-augmented attention (external retrieval on a broken base); learned salience scoring (violates Semantic Rigor — salience must derive from structure).
- **Artifacts the ADR claims will exist:**
  - `core/physics/salience.py` — `SalienceOperator`, `SalienceMap`, `FieldRegion`
  - `core/physics/attention.py` — `AttentionOperator`, `AttentionPlan`, `CoherenceBudget`
  - `core/physics/inhibition.py` — `InhibitionOperator`, `InhibitionMask`
  - `SalienceMap` content-addressed (SHA-256 over region IDs + curvature values)
  - Rust acceleration: curvature kernel in `core_rs::physics::salience`
  - `CoherenceBudget` with `total_capacity` / `committed` / `reserve` / `spent`; inhibition draws from `reserve`, not `committed`

#### 2. Implementation cross-reference

| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `SalienceOperator` | yes | `core/physics/salience.py:51` | curvature kernel, 139 lines |
| `SalienceMap` | yes | `core/physics/salience.py:41` | with `.top(n)` |
| `FieldRegion` | yes | `core/physics/salience.py:18` | |
| `SalienceMap` content-addressed | yes | `core/physics/salience.py:45,129,133-134` | `_salience_address()`, SHA-256 — exactly as specified |
| `AttentionOperator` (physics) | yes (unreached) | `core/physics/attention.py:47` | imported only by `core/physics/__init__.py:18` |
| `AttentionPlan` (physics) | yes (unreached) | `core/physics/attention.py:40` | tuple of `TraversalStep` |
| `CoherenceBudget` | yes (unreached) | `core/physics/attention.py:14` | all four fields; `__post_init__` enforces `committed + reserve <= total_capacity` |
| `InhibitionOperator` | yes (unreached) | `core/physics/inhibition.py:23` | |
| `InhibitionMask` | yes (unreached) | `core/physics/inhibition.py:15` | **exists** — revises the CR-1 text, see AA-A2-5 |
| Rust curvature kernel | **no** | — | no `core_rs::physics::salience`; zero `.rs` salience references |
| **Live** salience operator | yes | `generate/salience.py:25-62` | *composes* the physics kernel as `CurvatureSalienceOperator` (`:8,56`) |
| **Live** attention operator | yes | `generate/attention.py:20-43` | a **different** class of the same name; inhibition is a scalar threshold, not a mask |
| Serving wiring | yes | `generate/stream.py:255-262, 325-327, 637` | `use_salience` default `True` (`core/config.py:35`) |

**Build axis:** **partial** — salience landed fully and is composed into the live path; attention landed *twice*, once as the blueprint's schedule (unreached) and once as a threshold filter (live); inhibition landed as an exported class that no path constructs, its live counterpart being a scalar. `CoherenceBudget` — the ADR's explicit resource-accounting contribution — is entirely unreached.

#### 3. Liveness / integration

Adopted from the attention-allocation card and re-verified at `cbfc8ccb`:

- `core/config.py:35-37` — `use_salience: bool = True`, `salience_top_k: int = 16`, `inhibition_threshold: float = 0.3`. Default ON, confirmed unchanged.
- `generate/stream.py:259-262` — when `use_salience`, `SalienceOperator().compute(state, vocab, top_k=...)` then `AttentionOperator(inhibition_threshold).plan(salience, vocab)`.
- `generate/salience.py:56` — the live operator delegates curvature to `core.physics.salience`. **The physics kernel is genuinely on the hot path**, composed rather than duplicated. This is the key nuance the card established and it holds.
- `generate/stream.py:637` — the salience `budget` feeds back as the next `salience_top_k`: attention self-narrows across a walk. Still undocumented by any ADR.
- Per the card and Finding 0-F, this is the measured hot path (~73% of turn time through `cga_inner`/`geometric_product`).

**Sabotage test, two halves — and they diverge sharply:**

- *Salience + the live attention filter:* removing `_attention_candidates` changes the candidate set of every token walk. **Load-bearing.**
- *The blueprint's own attention/inhibition/budget operators:* `core/physics/attention.py` and `core/physics/inhibition.py` are imported by `core/physics/__init__.py` and nothing else — verified by repo-wide `rg` at `cbfc8ccb`. No serving path, no eval, constructs an `AttentionPlan`, an `InhibitionMask`, or a `CoherenceBudget`. Deleting all three changes no output. **Decoration** — matching H-2 exactly.

**Liveness axis:** **live** for salience and the generation-facing attention filter; **dead** for the blueprint's `AttentionOperator`/`InhibitionOperator`/`CoherenceBudget` as written. One ADR, two liveness verdicts on different halves — which is precisely why the CR-1 ruling is needed.

#### 4. Design fidelity — pillars and axioms

| Pillar | Honors / Tension / Violates | Citation |
|---|---|---|
| I. Mechanical Sympathy | **Tension** | The ADR anticipates the cost honestly ("computing field curvature is more expensive than dot-product attention… the Rust hot-path must cover the curvature kernel") — and the Rust kernel was never built, so the anticipated cost was incurred without the specified mitigation. The prediction was right; the remedy is missing. |
| II. Semantic Rigor | **Honors** | "Salience is not a scalar score attached to a token. It is a curvature property of the versor field" — a precise, non-negotiable redefinition, and the rejection of learned salience is argued from the same principle. |
| III. Third Door | **Honors, exemplary** | Four named alternatives rejected in a table with reasons, including the two fashionable ones, followed by a first-principles construction. Among the clearest instances of this pillar in the corpus. |

| Axiom | Honors / Tension / Violates | Citation |
|---|---|---|
| 1. Geometry-First | **Honors** | Salience *is* curvature — the intrinsic geometric property is found first, and the data structure follows from it. |
| 2. Field-State | **Honors** | Operates on `FieldRegion`s of a populated field; the ADR notes allocation "cannot run on an empty field." |
| 3. Propagation-over-Mutation | **Honors** | Produces a traversal *schedule*; nothing is mutated. |
| 4. Dual-Correction | **Honors (as designed)** | §3 is the corpus's most explicit instantiation: "every forward attention plan is paired with a corrective inhibition pass." Note the irony that this — the axiom-honoring half — is the half that was never built. |
| 5. Reconstruction-over-Storage | **Honors** | `SalienceMap` is content-addressed for cache reuse rather than persisted per-cycle. |
| 6. Compilation-Last | **Honors** | Operator signatures are specified; kernels are named as later acceleration targets. |
| 7. Reality-over-Inheritance | **Honors** | Explicitly refuses a compatibility shim with softmax attention ("There is no compatibility shim"). |

#### 5. Build fidelity — does the code match the decision?

Three divergences, and the third is the governance problem:

1. **Inhibition changed kind.** The ADR specifies a conjugate operator producing a `InhibitionMask` over regions, drawing from `CoherenceBudget.reserve`. The live implementation is a scalar cutoff: `mask = salience.scores >= max_score * 0.3` (`generate/attention.py:37-38`). A threshold is not a conjugate — it prunes a tail, it does not actively suppress interference. The Dual-Correction axiom the ADR honored in design is not honored in the build.
2. **`CoherenceBudget` vanished.** The live "budget" is an integer `top_k` (`generate/salience.py:62`). The four-field resource object with reserve accounting exists and is used by nothing. The ADR's explicit contribution — making resource consumption inspectable and measurable — did not land.
3. **Name collision across namespaces.** `AttentionOperator` and `AttentionPlan` each denote *two different classes* in this repository (`core/physics/attention.py` vs `generate/attention.py`), with different constructors and different semantics. `SalienceMap` likewise (`core/physics/salience.py:41` vs `generate/salience.py:14`). Any reader who greps a name gets two answers. This is a direct Pillar II hazard ("every term has one precise, non-negotiable meaning") created by the build, not by the decision.

**Build-fidelity axis:** **partial drift** — salience matches faithfully (and composes rather than duplicates, which is better than the ADR asked for); attention and inhibition were reimplemented in a different namespace with different semantics under the same names, and the budget was dropped.

#### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs

- **Contradicts `Whitepaper.md`?** No.
- **Contradicts `Yellowpaper.md`?** No.
- **Other ADRs:** ADR-0009 builds directly on it. The ADR's `Related` field cites "ADR-0007 (Ingest Layer)" — but ADR-0007 is *The Valence Layer*; the ingest layer is ADR-0002. A stale cross-reference from an era when numbering was in flux. Minor, but it is a citation that would mislead the citation-graph walk this audit depends on. (AA-A2-15)
- The admissibility chain (ADR-0024/0025/0026, stack A4) governs the *second* allocation stage; per the component card, salience/attention prune candidates and admissibility then judges them — two allocation stages, only the second ADR-governed.
- **Governance status:** the blueprint's staleness banner records ADR-0008's mechanism as "verified live in Phase 2… ungoverned rather than absent," registered as **G-14** awaiting a one-page ADR. So ADR-0008 is not superseded — it is the *only* thing that governs a default-ON serving mechanism, and it is a stale Draft's operator spec.
- **Continuity axis:** **unreconciled contradiction** — the record says three operators under an explicit budget; the running system has one composed kernel, one differently-shaped filter, no budget, and no mask. The mechanism's own ADR does not describe the mechanism that ships, and no amendment reconciles them. G-14 is the open remedy.

#### 7. Necessity / generality

1. **Necessity.** The *capability* is irreducible — CR-1's derivation stands: any bounded cognitive system must select what to process, and this one does, on every token step, at ~73% of turn cost. The *construction as specified* is not: two of three operators and the budget are unreached, and the system serves without them.
2. **Reducibility.** The salience half reduces cleanly to L0: `generate/salience.py:46` computes deflection via `cga_inner` — stack A1's algebra layer — and the curvature kernel is a composition over it. That is the correct relationship (a named cognitive operator built from the general algebraic primitive), not a duplication. The attention half reduces to something much smaller: a top-k selection plus a relative threshold, which needs no physics vocabulary at all. **The honest reading is that ADR-0008 named three operators and the system needed one and a half.**
3. **Extensibility.** Two pairings for `22-consolidation-report.md`: (a) **ADR-0008 ⊕ ADR-0024/0025/0026** (stack A4) — two allocation stages governed by two unconnected decision families, exactly the seam CR-1's ruling must cut; (b) `InhibitionMask` ⊕ the live threshold — H-2's recommendation is deletion, and this audit's evidence supports it (no path constructs a mask, and the live threshold does the pruning the mask was for).

**Necessity/generality axis:** **generalization-candidate** — the capability is irreducible and live, but the three-operator construction is not: one operator composes correctly over L0, one was replaced by something simpler, and one plus the budget are decoration. The generalization worth making is a single governed allocation contract spanning ADR-0008 and the admissibility family, which is G-14's job.

#### 8. Fitness / value

- `docs/assessment/20-component-cards/attention-allocation.md` — the full fitness verdict: **`strained`** — "sound mechanism, absent governance." Adopted.
- `tests/test_salience.py`, `tests/test_salience_vectorize_parity.py` — behavioral pin and vectorization parity pin; both present at `cbfc8ccb`.
- `docs/assessment/31-hindrance-audit.md` **H-5** — `salience_top_k=16` and `inhibition_threshold=0.3` gate every walk with no recorded derivation, against an in-repo counterexample (`admissibility_margin δ=0.4`, empirically derived) two config lines away.
- `docs/assessment/31-hindrance-audit.md` **H-2** — `InhibitionMask`/`InhibitionOperator` constructed on no path.
- `docs/assessment/30-gap-register.md` **G-14** — the CR-1 one-page ADR, with the card as its drafted evidence base.
- Finding 0-F — ~73% of turn time through `cga_inner`/`geometric_product`.

**Fitness axis:** **`strained`** — cited: attention-allocation component card (verdict adopted), H-2, H-5, G-14, two test pins. Mechanism sound and measurably load-bearing; governance absent and its constants underived.

#### 9. Findings raised

- **AA-A2-5** 🟡 — Revises adopted evidence: `02-layer-taxonomy.md` §5 CR-1 states "the blueprint's `InhibitionMask` appears never to have been built." It **is** built — `core/physics/inhibition.py:15,23`, 54 lines, both `InhibitionMask` and `InhibitionOperator`. The substantive judgment (nothing constructs it) is correct and unchanged; the phrasing is factually wrong and the assessment's own H-2 already said so. §1.1/§5 were never amended. (§2, §3)
- **AA-A2-7** 🔵 — `core/physics/{attention,inhibition}.py` are imported by nothing but `core/physics/__init__.py`; deleting them changes no output. Confirms H-2 at `cbfc8ccb`. (§3)
- **AA-A2-15** 🟢 — ADR-0008's `Related` field cites "ADR-0007 (Ingest Layer)"; ADR-0007 is *The Valence Layer* and the ingest layer is ADR-0002. Stale cross-reference that misdirects a citation-graph walk. (§6)
- **AA-A2-16** 🟡 — Name collision: `AttentionOperator`, `AttentionPlan`, and `SalienceMap` each denote two different classes across `core/physics/` and `generate/`. Direct Pillar II hazard. (§5)
- **AA-A2-17** 🔵 — `CoherenceBudget` — the ADR's explicit resource-accounting contribution — is unreached; the live budget is an integer `top_k`. Inhibition-draws-from-reserve was never built. (§2, §5)
- *(Carried, not re-raised: H-5's underived constants, G-14's missing ADR, and the absent Rust curvature kernel are already registered in the assessment.)*

#### 10. Evidence sources actually consulted

- ADR-0008 in full; `core/physics/salience.py`, `core/physics/attention.py`, `core/physics/inhibition.py` in full; `generate/salience.py`, `generate/attention.py` in full.
- `generate/stream.py:255-262, 276-278, 325-327, 637`; `core/config.py:35-37`.
- `docs/assessment/20-component-cards/attention-allocation.md` in full (adopted, then spot-checked line-by-line against `cbfc8ccb` — all claims hold).
- `docs/assessment/31-hindrance-audit.md` H-2, H-5; `docs/assessment/30-gap-register.md` G-14; `docs/architecture/MIND-PHYSICS-BLUEPRINT.md` staleness banner.
- Repo-wide `rg` at `cbfc8ccb` for `AttentionOperator|AttentionPlan|CoherenceBudget|InhibitionOperator|InhibitionMask|TraversalStep` across `*.py`, `*.rs`, `*.md`, confirming the import-only status of the physics trio and the absence of any Rust salience kernel.

---

### ADR-0009 — Compositional Physics

**Audit ID (if a numbering collision):** none | **Family (if phased):** mind-physics blueprint (non-phased ring)
**Zone / stack:** M3/M4 de facto — blueprint-assigned to `L1-field` / A2 | **Tier:** A
**ADR status (as recorded in the file):** Accepted | **ADR date:** 2026-05-12
**Card author:** Tier-A subagent | **`verified_at` SHA:** `cbfc8ccb`

> **Adopted disposition** (`02-layer-taxonomy.md` §1.1): "Landed as the proposition-graph lineage: `PropositionGraph → ArticulationTarget → realizer` — **Superseded**." Spot-checked at `cbfc8ccb`: **confirmed**, with one refinement — one of the four operators (`TrajectoryOperator`) did *not* get superseded; it is live on the turn path, feeding the identity check.

#### 1. Content summary

- **Decision made:** define the layer that converts field activation into cognition, in four stages — temporal binding of co-activated regions into a `BindingFrame` (threshold-triggered, not clock-triggered), digest cycles that integrate frames by propagating a coherence wave rather than rewriting regions, reasoning trajectories as ordered frame sequences with explicit transition records, and articulation planning that produces a structured `ArticulationPlan` (explicitly *not* generation, which is deferred to a downstream renderer).
- **Alternatives explicitly rejected:** chain-of-thought prompting ("string concatenation masquerading as reasoning; no field provenance"); scratchpad/working-memory tokens (flat buffer, no binding); neural-symbolic integration (imposes external symbolic grammar); tree-of-thought (right intuition, wrong substrate).
- **Artifacts the ADR claims will exist:**
  - `core/physics/binding.py` — `BindingFrame`, `BindingOperator`
  - `core/physics/digest.py` — `DigestCycle`, `DigestOperator`
  - `core/physics/reasoning.py` — `ReasoningTrajectory`, `TrajectoryOperator`
  - `core/physics/articulation.py` — `ArticulationPlan`, `ArticulationPlanner`, `OutputModality`
  - `BindingFrame` frozen and content-addressed (SHA-256)
  - `ReasoningTrajectory` append-only, no in-place mutation
  - Digest cycles bounded by `CoherenceBudget.reserve`
  - Rust acceleration: coherence wave kernel, trajectory delta computation

#### 2. Implementation cross-reference

| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `BindingFrame`, `BindingOperator` | yes (unreached) | `core/physics/binding.py` | imported only by `core/physics/__init__.py:20` |
| `DigestCycle`, `DigestOperator` | yes (unreached) | `core/physics/digest.py` | imported only by `core/physics/__init__.py:21`; `:24` comments "drawn from CoherenceBudget.reserve" — a budget nothing constructs |
| `ReasoningTrajectory` | yes (**live**) | `core/physics/reasoning.py:28` | |
| `TrajectoryOperator` | yes (**live**) | `core/physics/reasoning.py:70` | `.build(frames, trajectory_id)` |
| `ArticulationPlan` (physics) | yes (unreached) | `core/physics/articulation.py` | imported only by `core/physics/__init__.py:23` |
| `ArticulationPlanner`, `OutputModality` | yes (unreached) | `core/physics/articulation.py` | no constructor anywhere |
| `BindingFrame` used on live path | **no** | `chat/runtime.py:307` | the live path uses `_StubBindingFrame`, a **local 4-field stand-in**, not the physics class |
| **Live** articulation plan | yes (different) | `generate/articulation.py:12` | a *different* `ArticulationPlan` (subject/predicate/object/surface/language/frame_id) |
| Proposition-graph lineage | yes | `generate/realizer.py:22,111,217-219`, `generate/proposition.py` | `PropositionGraph` → `realize_semantic`/`realize_target`; ~20 modules participate |
| Rust coherence-wave / trajectory kernels | **no** | — | absent |

**Build axis:** **partial** — all four modules exist with the exact declared symbols, but three of four are import-only decoration, and the fourth (`reasoning`) is live only via a *stub* frame type rather than the `BindingFrame` the ADR specified. The capability the ADR wanted landed elsewhere entirely, as the proposition-graph lineage.

#### 3. Liveness / integration

One of the four operators is live, and it matters more than its size suggests. `chat/runtime.py:2902` calls `_make_trajectory_from_result(result, turn)` on the main turn path; that function (`:388-402`) imports `TrajectoryOperator`, wraps each field state in a `_StubBindingFrame` (`:307`, `:394`) whose `coherence_magnitude` is `_energy_scalar(fs.energy)` — ADR-0006's raw energy — and builds a `ReasoningTrajectory`. The trajectory is then passed straight to `self._identity_check.check(reasoning_trajectory, ...)` at `:2912`.

So ADR-0009's trajectory abstraction survives as **the input type of the live identity gate** — which is ADR-0010's `IdentityCheck: (ReasoningTrajectory, IdentityManifold) → IdentityScore` signature, still honored verbatim at `cbfc8ccb`. The two ADRs' seam is the one part of the blueprint's composition that is genuinely running.

The other three are dead: repo-wide `rg` confirms `BindingOperator`, `DigestOperator`, `DigestCycle`, `ArticulationPlanner`, and `OutputModality` appear only in `core/physics/__init__.py`'s import/`__all__` block and in their own defining modules.

**Sabotage test:**
- *`TrajectoryOperator`/`ReasoningTrajectory`:* stub to a no-op and `IdentityCheck.check` loses its input — the identity score, `flagged`, and the refusal path at `:3017` all break. **Load-bearing**, though as plumbing: the trajectory is a container the identity check reads, not a reasoning mechanism doing work.
- *`binding`, `digest`, `articulation` (physics):* delete all three, nothing changes. **Decoration.** Note this triples H-2's scope, which named only `DriveGradientMap` and `InhibitionMask`.

**Liveness axis:** **wired-but-unreached** for the layer as decided — one of four operators is live and only as a typed container; the other three are dead exports. Recorded at the ADR level rather than splitting, because the ADR's claim is a four-stage *pipeline*, and no pipeline runs.

#### 4. Design fidelity — pillars and axioms

| Pillar | Honors / Tension / Violates | Citation |
|---|---|---|
| I. Mechanical Sympathy | **Tension** | Names the cost ("digest propagation cost scales with field density; the Rust hot-path must cover the coherence wave kernel") — never built, and unlike ADR-0008's case, the mechanism it would accelerate never ran either. |
| II. Semantic Rigor | **Honors** | "Articulation is **not** generation. The planner produces a structured specification" — a sharp, enforced separation of terms, and the one part of the design that demonstrably shaped what shipped. |
| III. Third Door | **Honors** | Four alternatives rejected by name, including the two dominant industry patterns, with the tree-of-thought critique conceding the intuition while rejecting the substrate. |

| Axiom | Honors / Tension / Violates | Citation |
|---|---|---|
| 1. Geometry-First | **Tension** | Frames and trajectories are structural records (IDs, magnitudes, timestamps) rather than intrinsic geometric objects; the geometry is in what they *point at*, not in what they *are*. |
| 2. Field-State | **Honors** | Every operator's signature takes `FieldState` and binding is defined over co-activated field regions. |
| 3. Propagation-over-Mutation | **Honors, explicitly** | "the digest operator does not rewrite field regions. It propagates a coherence wave outward" — the axiom named and applied. |
| 4. Dual-Correction | **Tension** | Trajectories are inspectable and interruptible ("a wrong trajectory can be interrupted and revised"), but no conjugate operator is specified — correction is an operator affordance, not a dual. |
| 5. Reconstruction-over-Storage | **Honors** | "Every output segment has traceable field provenance — full reconstruction-over-storage from output back to source pressure." |
| 6. Compilation-Last | **Honors** | Operator signatures first; kernels named as later targets. |
| 7. Reality-over-Inheritance | **Honors** | "This layer has no analog in transformer architectures. There is no compatibility mapping." |

#### 5. Build fidelity — does the code match the decision?

The decided pipeline did not get built; a different pipeline delivers the capability.

- **What was decided:** `BindingOperator → DigestOperator → TrajectoryOperator → ArticulationPlanner`, four stages over field regions, terminating in a modality-tagged plan with per-segment field provenance and confidence.
- **What ships:** `PropositionGraph → ArticulationTarget → realize_target/realize_semantic` (`generate/realizer.py:22,111,217`), with `generate/articulation.py`'s own `ArticulationPlan` (subject/predicate/object/surface) carried through `generate/surface.py:346,387` and `chat/runtime.py:2415`. Roughly twenty modules participate in the proposition-graph lineage.
- **The relationship:** supersession, not drift. The successor is *stronger* on the ADR's own stated goal — the proposition graph gives structured articulation targets with provenance, which is what ADR-0009 wanted from `ArticulationPlan` — and it dropped the parts (binding thresholds, digest waves, budget-bounded cycles) that the ADR itself flagged as the risky ones ("binding threshold tuning is non-trivial… initial values must be set empirically per domain"). Those values were never set because those stages were never built.
- **One genuine drift inside the live remnant:** `chat/runtime.py:307`'s `_StubBindingFrame` is named "stub" in the runtime's own vocabulary and carries four fields against `BindingFrame`'s specified set plus content address. The live path uses a stand-in for the ADR's own type while the real type sits unused two modules away.

**Build-fidelity axis:** **contradicts** — the decided four-stage pipeline is not what runs; a different construction delivers the capability, and no record reconciles the two. (Recorded as `contradicts` on the *fidelity* axis while §6 records the continuity as `superseded-cleanly` — the code does not match the decision, but the decision was rightly displaced.)

#### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs

- **Contradicts `Whitepaper.md`?** No. Axioms 3 and 5 are honored explicitly.
- **Contradicts `Yellowpaper.md`?** No.
- **Superseded by:** the proposition-graph lineage. `02-layer-taxonomy.md` §1.1 records this and it is confirmed in code. The supersession is *substantive and complete* for three of four stages, but it is **nowhere recorded in the ADR corpus itself** — ADR-0009 still reads `Status: Accepted` with no superseded-by pointer, and no successor ADR names it. A reader arriving via `docs/adr/` alone would implement the wrong pipeline.
- Depends on ADR-0008 (`AttentionPlan` is `BindingOperator`'s input) — and that dependency is broken in the shipped system, since nothing produces the physics `AttentionPlan`.
- **Continuity axis:** **superseded-cleanly** in substance — the successor is stronger and the assessment recorded the disposition — but the ADR file carries no supersession marker, so the corpus itself is unreconciled. See AA-A2-18.

#### 7. Necessity / generality

1. **Necessity.** The four-stage construction is **not necessary** — the system has served for months without binding, digest, or the physics articulation planner, and the sabotage test on all three returns "no change." The *capability* (structured intermediate representation between field activation and surface, with provenance) is necessary and is delivered by the proposition graph. `TrajectoryOperator` is necessary only as the identity gate's input container, a role any ordered sequence type would fill.
2. **Reducibility.** Reducible to the **proposition-graph lineage** — named explicitly. This is the cleanest reduction in the stack: a general mechanism already in the tree does what the ADR proposed as a four-operator layer, and does more of it. Not reducible to L0/L1 (the algebra layer supplies no composition semantics), which is worth stating so the reduction is not over-claimed: the successor is a *peer-layer* generalization, not a substrate one.
3. **Extensibility.** The proposition graph already absorbed this ADR's `ArticulationPlan` concept. The residual pairing for `22-consolidation-report.md` is narrow and concrete: **`core/physics/reasoning.py` ⊕ `chat/runtime.py:307`'s `_StubBindingFrame`** — either the runtime should use the real `BindingFrame`, or `binding.py` should be deleted and `_StubBindingFrame` promoted to a named type. Currently both exist and the stub wins, which is the worst of the three options.

**Necessity/generality axis:** **reducible-to-the-proposition-graph-lineage** (`PropositionGraph → ArticulationTarget → realizer`) — three of four operators are dead and the fourth is a container. The blueprint's version of the claim should be retired, confirming the adopted disposition.

#### 8. Fitness / value

- `02-layer-taxonomy.md` §1.1 — disposition recorded (adopted, confirmed).
- The successor lineage is extensively pinned: `tests/test_articulation_realizer_v2.py`, `tests/test_forward_graph_constraint_wiring.py`, `tests/test_negation_survives_articulation.py`, `tests/test_oov_pipeline.py`, plus `evals/grammar_roundtrip/runner.py`, `evals/discourse_paragraph/runner.py`, `evals/zero_code_domain_acquisition/runner.py` — all exercising `realize_target`/`realize_semantic`.
- `tests/test_identity_gate.py:19` imports `ReasoningTrajectory`/`TrajectoryOperator` — the live remnant's only direct pin.
- No test or eval anywhere exercises `BindingOperator`, `DigestOperator`, or `ArticulationPlanner`.

**Fitness axis:** **value delivered by the successor, not by this ADR** — cited: seven test/eval artifacts on the proposition-graph lineage, one on the trajectory remnant, zero on the three dead operators.

#### 9. Findings raised

- **AA-A2-7** 🔵 (extended) — `core/physics/{binding,digest,articulation}.py` are import-only decoration alongside `{attention,inhibition}.py`. **Five** blueprint operator modules, not H-2's two. (§3)
- **AA-A2-18** 🟡 — ADR-0009 reads `Status: Accepted` with no supersession marker despite being substantively superseded by the proposition-graph lineage. The assessment recorded the disposition; the ADR corpus did not. A reader using only `docs/adr/` would implement the wrong pipeline. (§6)
- **AA-A2-19** 🟢 — `chat/runtime.py:307` `_StubBindingFrame` stands in for `core/physics/binding.py`'s `BindingFrame` on the live path while the real type sits unused. Either wire it or delete it. (§5, §7)

#### 10. Evidence sources actually consulted

- ADR-0009 in full; `core/physics/reasoning.py` (structure + operator); `core/physics/binding.py`, `digest.py`, `articulation.py` (existence + import graph).
- `chat/runtime.py:307-311, 388-402, 2902, 2912`; `generate/articulation.py:1-30`; `generate/realizer.py:22,111,188,202,217-219`; `generate/surface.py:8,346,387`.
- Repo-wide `rg` at `cbfc8ccb` for `BindingOperator|BindingFrame|DigestOperator|DigestCycle|ArticulationPlanner|OutputModality` (import-only status confirmed) and for `PropositionGraph|ArticulationTarget` (successor lineage, ~20 modules).
- `docs/assessment/02-layer-taxonomy.md` §1.1; test/eval inventory for the realizer lineage.

---

### ADR-0010 — Identity Physics

**Audit ID (if a numbering collision):** none | **Family (if phased):** mind-physics blueprint (non-phased ring)
**Zone / stack:** MG `governance-identity-safety` de facto — blueprint-assigned to `L1-field` / A2; drive half → **CR-2** | **Tier:** A
**ADR status (as recorded in the file):** Accepted | **ADR date:** 2026-05-12
**Card author:** Tier-A subagent | **`verified_at` SHA:** `cbfc8ccb`

> **Adopted disposition** (`02-layer-taxonomy.md` §1.1): "Landed and hardened: wave-only fail-closed identity scoring (ADR-0244 §3, INV-32), identity manifold, identity packs — **Superseded by stronger implementations**, retire the blueprint's version of the claim." Spot-checked at `cbfc8ccb`: **confirmed for the identity half.** The **drive/exertion half is revised** — §1.1 records `DriveGradientMap`/`ExertionMeter` as "Never built"; both are built and both are constructed on the live turn path. See AA-A2-4.

#### 1. Content summary

- **Decision made:** encode CORE's character as geometry rather than prompt — a read-only `IdentityManifold` of value axes, boundary hyperplanes and resonance modes against which every `ReasoningTrajectory` is checked before articulation; drives as additive gradient *fields* that bias traversal without overriding it; an `ExertionMeter` producing a `FatigueIndex` that compresses subsequent `CoherenceBudget`; and a `CharacterProfile` as the human-readable projection of the manifold (explicitly not the identity itself).
- **Alternatives explicitly rejected:** system-prompt personas — "This is not identity. It is a costume." (Not tabulated as a formal alternatives list, but argued at length in Context.)
- **Artifacts the ADR claims will exist:**
  - `core/physics/identity.py` — `IdentityManifold`, `IdentityCheck`, `IdentityScore`, `CharacterProfile`
  - `core/physics/drive.py` — `DriveGradientMap`, `GradientField`, `ValueAxis`
  - `core/physics/exertion.py` — `ExertionMeter`, `FatigueIndex`, `CycleCost`
  - `IdentityCheck: (ReasoningTrajectory, IdentityManifold) → IdentityScore`
  - `IdentityManifold` frozen, instantiated once at init, no mutation path
  - Identity checks run **before articulation, not before attention**
  - Drives create gradients that make favorable traversal energetically preferred; allocation physics operates on top of the drive-shaped landscape
  - High `FatigueIndex` reduces `CoherenceBudget`, compresses attention depth, biases traversal toward low-cost regions

#### 2. Implementation cross-reference

| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `IdentityManifold` | yes | `core/physics/identity.py:310` | plus `identity_manifold.py` (17 KB) and `identity_action.py` (27 KB) — the hardened successor surface |
| `IdentityCheck` | yes (**live**) | `core/physics/identity.py:318` | `chat/runtime.py:719, 2912, 3017` |
| `IdentityScore` | yes (**live**) | `core/physics/identity.py:215` | |
| `CharacterProfile` | yes (**live**) | `core/physics/identity.py:576` | `.from_manifold(...)`, `chat/runtime.py:714, 2944` |
| `IdentityCheck` signature | yes, **extended** | `chat/runtime.py:2912-2919` | takes `(trajectory, manifold, wave_field=, admission_policy=, turn_id=, pack_id=)` — the ADR's two-arg signature is the head of a longer one |
| Frozen, once at init, no mutation | yes | `chat/runtime.py:722, 329-352` | `_hash_identity_manifold` pins immutability; ADR-0035's `no_identity_override` predicate enforces it |
| Checks run before articulation | yes | `chat/runtime.py:2912` vs `:2961-2964` | ordering holds exactly as decided |
| `ValueAxis` | yes | `core/physics/drive.py:15` + `identity.py:196` | **defined twice** — `identity.py:199` notes runtime may also pass the `drive` one |
| `GradientField` | yes (built, unreached) | `core/physics/drive.py:24` | constructed `chat/runtime.py:712` |
| `DriveGradientMap` | yes (built, **written-never-read**) | `core/physics/drive.py:32` | constructed `chat/runtime.py:713`; `_drive_map` read nowhere |
| `DriveGradientMap.combined_bias()` | yes (never called) | `core/physics/drive.py:36` | zero call sites repo-wide |
| `ExertionMeter` | yes (**live, telemetry**) | `core/physics/exertion.py:48` | `chat/runtime.py:711, 2942-2943` |
| `CycleCost` | yes (**live**) | `core/physics/exertion.py:14` | constructed `chat/runtime.py:2935-2941` |
| `FatigueIndex` | yes (**live, telemetry**) | `core/physics/exertion.py:29` | `chat/runtime.py:2943, 2946-2947` |
| Drives bias traversal | **no** | — | `combined_bias` never called; no traversal reads any gradient |
| Fatigue reduces `CoherenceBudget` | **no** | — | `apply_to_budget` (`exertion.py:43`) never called; no `CoherenceBudget` exists on any path |
| Fatigue compresses attention depth | **no** | — | attention depth is `salience_top_k`, unaffected by fatigue |
| Boundary hyperplanes / resonance modes | **partial** | `core/physics/identity.py:310` | `boundary_ids` + `alignment_threshold` (`chat/runtime.py:348-349`); no hyperplane or resonance-mode geometry as described |

**Build axis:** **full** — every claimed module and symbol exists, and the identity half is not merely built but hardened well beyond the ADR (ADR-0244's wave-field manifold, Gram subspace projection, fail-closed wave requirement, session identity-path ledger). The drive/exertion half is built but its *behavioral* claims are not.

#### 3. Liveness / integration

**Identity: live and load-bearing.** `chat/runtime.py:719` constructs `IdentityCheck` once; `:2912` calls `.check()` on the main turn path with the live `ReasoningTrajectory` and `wave_field=result.final_state.F`; `:2934` extracts `flagged`; `:3017` gates the refusal surface on `IdentityCheck.would_violate(identity_score)`. `AGENTS.md` **INV-32** makes this fail-closed: "identity scoring is wave-only: `IdentityCheck.check` requires an…" — a missing wave state raises `MissingWaveStateError` (`identity.py:77`) rather than degrading. ADR-0244 §3 ("Fail-Closed Wave Requirement (Dual-Mode Excised)") records the scalar-L2 fallback's excision at convergence 2026-07-20. Pinned by `tests/test_adr_0244_identity_gate_{eval,runtime,wave}.py`.

**Drive: built, constructed, never read.** `chat/runtime.py:712-713` builds `GradientField`s from the manifold's value axes and composites them into `self._drive_map`. `_drive_map` is then read by nothing — verified repo-wide at `cbfc8ccb`. `combined_bias()`, the method carrying the ADR's entire claim that drives bias traversal, has zero call sites. The `drive_gradients` tuple *is* read, at `:716` and `:2946`, but only to build a `{name: magnitude}` summary dict for `CharacterProfile`.

**Exertion: live as telemetry only.** `:2935-2941` builds a real `CycleCost` from real per-turn quantities (`result.candidates_used`, `config.inhibition_threshold`, `len(result.trajectory)`); `:2942-2943` records it and computes fatigue. Fatigue then scales the same `CharacterProfile` summary (`:2946`) and is stored as `fatigue_index` (`:2947`). `FatigueIndex.apply_to_budget()` is never called. `CharacterProfile` itself flows only into `CognitiveTurnResult` fields (`:2634`, `:3289`) — introspection surface, not a decision input. `scripts/review_trace.py:172` has a `--fatigue` viewer, confirming its intended role is observation.

**Sabotage test, three ways:**
- *Identity:* stub `IdentityCheck.check` → the refusal gate at `:3017` stops firing and `flagged` is always False. **Load-bearing, on the safety path.**
- *Drive:* delete `DriveGradientMap` and `combined_bias` entirely → the only change is that `CharacterProfile.drive_summaries` loses a dict that no decision reads. **Decoration**, exactly H-2.
- *Exertion:* stub `ExertionMeter` to return `FatigueIndex(0.0, n)` → `drive_summaries` values change by a factor and `fatigue_index` reads 0.0 in the turn result. No served surface changes, no decision changes. **Telemetry**, exactly G-4.

**Liveness axis:** **live** for identity (fail-closed, INV-32, on the refusal path); **dead** for drive; **scaffolded/telemetry** for exertion. The ADR's three mechanisms have three different verdicts.

#### 4. Design fidelity — pillars and axioms

| Pillar | Honors / Tension / Violates | Citation |
|---|---|---|
| I. Mechanical Sympathy | **Tension** | The ADR concedes non-stationarity honestly ("the same input may produce different depth of response depending on prior cycle history") — a serious determinism hazard for a system whose north star ends in "replay deterministically," raised but never resolved. That the fatigue coupling was never built is arguably why replay survived. |
| II. Semantic Rigor | **Honors** | The `CharacterProfile` ≠ identity distinction is drawn with unusual care ("the way a map represents terrain without being the terrain") and is respected in code — the profile is a projection, and the manifold is the frozen thing. |
| III. Third Door | **Honors** | Rejects the industry default (system-prompt persona) as "a costume" and builds identity into geometry instead. This is the pillar's clearest instance in the stack, and it is also the one that shipped. |

| Axiom | Honors / Tension / Violates | Citation |
|---|---|---|
| 1. Geometry-First | **Honors** | Identity as a geometric subspace with value axes as directions — the intrinsic space is found before the structure. ADR-0244 took this further into wave-field/Gram-projection territory. |
| 2. Field-State | **Honors** | The manifold is a subspace *of the versor field*, and the live check reads `final_state.F`. |
| 3. Propagation-over-Mutation | **Honors** | `IdentityManifold` frozen, instantiated once, no mutation path — enforced by `_hash_identity_manifold` and ADR-0035's predicate. |
| 4. Dual-Correction | **Tension** | `IdentityCheck` flags and may halt, but there is no conjugate that *restores* a deviating trajectory — the ADR says "may be corrected or halted" without specifying the corrective operator. |
| 5. Reconstruction-over-Storage | **Honors** | Character is reconstructed from manifold + drives + fatigue at each turn (`CharacterProfile.from_manifold`), not stored. |
| 6. Compilation-Last | **Honors** | Specifies operators and their signatures; representation choices left to implementation. |
| 7. Reality-over-Inheritance | **Tension** | The `ExertionMeter`/fatigue construction is imported from human cognitive phenomenology ("this models the natural rhythm of deep work") rather than derived from CORE's structure — an anthropomorphic inheritance. That it landed as telemetry-with-no-consumer is the axiom asserting itself: the abstraction did not survive on structural merit, it survived as a number in a trace. |

#### 5. Build fidelity — does the code match the decision?

- **Identity: exceeded, cleanly.** The signature holds (`ReasoningTrajectory × IdentityManifold → IdentityScore`), the ordering holds (before articulation, not before attention), immutability holds. The successor is *stronger*: wave-only fail-closed scoring, Gram subspace projection, a session identity-path ledger (ADR-0246 §3.4/§3.5), and INV-32 as enforced law. This is what "superseded by stronger implementations" means, and it is accurate.
- **Drive: contradicted.** The ADR's operative claim is that drives *bias traversal* and that "the allocation physics layer operates on top of this landscape — salience is computed against a field that is already shaped by drive gradients." `generate/salience.py` computes curvature over raw versors and per-word energy; no gradient is applied. The stated composition between ADR-0010 and ADR-0008 does not exist.
- **Exertion: contradicted.** All three stated effects (reduce `CoherenceBudget`, compress attention depth, bias toward low-cost regions) are absent, two of them necessarily so since no `CoherenceBudget` is ever constructed. The meter runs and its output modulates a display string.
- **Minor:** `ValueAxis` is defined twice (`drive.py:15`, `identity.py:196`) with `identity.py:199` documenting the ambiguity in a comment rather than resolving it — a Pillar II wrinkle in the same class as AA-A2-16.

**Build-fidelity axis:** **partial drift** — identity matches and exceeds; drive and exertion match structurally (the classes are right) and contradict behaviorally (every stated effect is absent).

#### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs

- **Contradicts `Whitepaper.md`?** No.
- **Contradicts `Yellowpaper.md`?** No.
- **Superseded by:** ADR-0244 (Wave-Field Identity Manifold and Inalienable Geometric Alignment) for the identity half — §2.1 Gram subspace projection, §2.2 metric-exact anomaly detection, §3 fail-closed wave requirement, §4a reconciled implementation spec — plus ADR-0027 (identity packs), ADR-0035 (`no_identity_override`), ADR-0246 (session identity path). Governed by INV-32. This is a genuine, well-recorded, code-confirmed supersession.
- **Not superseded:** the drive and exertion halves. No later ADR names them. §1.1 routed them to **CR-2**, whose ruling is open as **G-4**.
- Depends on ADR-0008's `CoherenceBudget` for the fatigue coupling — a dependency broken by ADR-0008's budget never landing.
- **Continuity axis:** **superseded-cleanly** for identity (ADR-0244 §3 + INV-32, recorded and enforced); **unreconciled** for drive/exertion — Accepted, built, running, and the two records that mention them disagree with each other (§1.1 says "never built", H-2/G-4 say "built, not read"). See AA-A2-4.

#### 7. Necessity / generality

1. **Necessity.** Split. *Identity* is necessary and the successor proves it — it is on the refusal path and fail-closed under INV-32. *Drive* is not necessary: the system loses nothing measurable without it, and CR-2/G-4 already record that the actual gap is a **chooser**, which `DriveGradientMap` is not (a gradient landscape biases traversal within a turn; it does not rank what to do between turns). *Exertion* is not necessary: it produces one number for traces, and its stated purpose — coupling to a budget — has no budget to couple to.
2. **Reducibility.** The identity half reduces to **ADR-0244's wave-field manifold** — named, ratified, stronger, and enforced. The drive half is not reducible to an existing operator; it is reducible to *nothing*, which is the more useful finding — H-2's recommended disposition is deletion with the intent preserved in the CR-2 design. The exertion half reduces to plain telemetry: a per-turn cost accumulator needs no physics vocabulary.
3. **Extensibility.** The one genuinely extensible idea here is the fatigue↔budget coupling, and it is stranded: it requires ADR-0008's `CoherenceBudget`, which is itself decoration. Two dead mechanisms that would only be alive together — a useful pattern for `22-consolidation-report.md`, since **retiring one entails retiring the other**, and building either alone is wasted. Pairing: **ADR-0010 exertion ⊕ ADR-0008 `CoherenceBudget`** — retire or build as a unit, never singly.

**Necessity/generality axis:** **reducible-to-ADR-0244** for identity (retire the blueprint's version of the claim, per the adopted disposition); **generalization-candidate → deletion** for drive and exertion, whose intents belong in the CR-2 design (G-4) rather than in code.

#### 8. Fitness / value

- `docs/assessment/02-layer-taxonomy.md` §1.1 — identity disposition (adopted, confirmed).
- `AGENTS.md` INV-32 — wave-only fail-closed identity scoring, enforced law.
- ADR-0244 §3, §4a — the ratified successor with the dual-mode excision recorded.
- `tests/test_adr_0244_identity_gate_{eval,runtime,wave}.py`, `tests/test_identity_gate.py` — four pins on the live identity path.
- `docs/assessment/31-hindrance-audit.md` **H-2** — `DriveGradientMap` constructed, read nowhere; verdict **decoration**; recommended disposition **deletion**.
- `docs/assessment/30-gap-register.md` **G-4** (leverage 4) — "drive objects exist (`DriveGradientMap` — constructed, never read; `ExertionMeter` — telemetry only)… nothing ranks what matters next."
- `scripts/review_trace.py:172` `--fatigue` viewer — confirms exertion's observational role.

**Fitness axis:** **identity — high, measured and enforced** (INV-32, ADR-0244, four test pins); **drive — negative fitness**, H-2 rates it decoration whose harm is testimony ("Decoration is how architecture lies without anyone lying"); **exertion — telemetry only**, G-4.

#### 9. Findings raised

- **AA-A2-4** 🟡 — Revises adopted evidence: `02-layer-taxonomy.md` §1.1 records `DriveGradientMap`/`ExertionMeter` as "**Never built**; no successor articulation anywhere." Both are built (`core/physics/drive.py`, `core/physics/exertion.py`) and both are constructed on the live turn path (`chat/runtime.py:711-713, 2935-2948`). The assessment's own later phases corrected this (H-2, G-4); §1.1 was never amended, so the ratified taxonomy now contradicts the ratified registers. Per `AGENTS.md` #5, record-vs-reality divergence is a defect of the same severity as a wrong answer. (§2, §3)
- **AA-A2-20** 🟡 — ADR-0010's two operative behavioral claims are unimplemented: `DriveGradientMap.combined_bias()` has zero call sites (so drives do not bias traversal, and ADR-0008's salience is *not* computed over a drive-shaped field as both ADRs state), and `FatigueIndex.apply_to_budget()` has zero call sites (so fatigue does not compress any budget). (§3, §5)
- **AA-A2-21** 🔵 — Consolidation pairing: the fatigue↔budget coupling requires ADR-0008's `CoherenceBudget`, itself decoration. Retire or build as a unit; building either alone is wasted. (§7)
- **AA-A2-22** 🟢 — `ValueAxis` is defined twice (`core/physics/drive.py:15`, `core/physics/identity.py:196`), with the ambiguity documented in a comment rather than resolved. (§5)

#### 10. Evidence sources actually consulted

- ADR-0010 in full; `core/physics/drive.py` and `core/physics/exertion.py` in full; `core/physics/identity.py` (class inventory + `CharacterProfile`); ADR-0244 section headings (§2.1, §2.2, §3, §4, §4a).
- `chat/runtime.py:329-352, 700-729, 2902-2948, 3017, 2634, 3289`; `scripts/review_trace.py:172`.
- `AGENTS.md` INV-32.
- Repo-wide `rg` at `cbfc8ccb` for `_drive_map|combined_bias|drive_gradients|character_profile|fatigue|FatigueIndex|exertion_meter` — establishing zero call sites for `combined_bias` and `apply_to_budget`, and telemetry-only consumption for `CharacterProfile`.
- `docs/assessment/31-hindrance-audit.md` H-2; `docs/assessment/30-gap-register.md` G-4; `docs/assessment/02-layer-taxonomy.md` §1.1, §5 CR-2.

---

### ADR-0011 — Renderer Layer Contract

**Audit ID (if a numbering collision):** none | **Family (if phased):** mind-physics blueprint (non-phased ring)
**Zone / stack:** M4 `L6-chat-runtime` de facto / A2 | **Tier:** A
**ADR status (as recorded in the file):** Accepted | **ADR date:** 2026-05-13
**Card author:** Tier-A subagent | **`verified_at` SHA:** `cbfc8ccb`

> **Adopted disposition** (`02-layer-taxonomy.md` §1.1): "`generate/realizer.py` has been the shipping renderer for months — **Stale line, retire**." Spot-checked at `cbfc8ccb`: **confirmed, and stronger than recorded** — not one stale line but every claimed artifact. Nothing ADR-0011 specifies exists anywhere in the repository.

#### 1. Content summary

- **Decision made:** the renderer layer is exactly one interface — a stateless, deterministic, caller-provided `Renderer` protocol converting `Iterable[VocabEntry]` to `str | bytes` — with a plain-text default implementation. Deliberately thin: not a subsystem, explicitly rejecting the `core_logos` full-subsystem shape from `core-ai` as over-engineering that "solved operational concerns before the underlying generation was correct."
- **Alternatives explicitly rejected:** `core_logos` (the prior system's full readback/trace/authority subsystem); engine-selected renderers ("the engine never selects a renderer — the caller provides one"); non-deterministic output-time transforms ("a property of language models… CORE does not do that").
- **Artifacts the ADR claims will exist:**
  - A `Renderer` Protocol with `render(self, tokens: Iterable[VocabEntry]) -> str | bytes`
  - `generate/render.py` — the default `TextRenderer` (tokens → `.surface` joined by a language-appropriate separator)
  - `generate/stream.py` yields tokens and calls no renderer
  - Externally-registered modality renderers (markdown, Hebrew RTL, Koine polytonic, audio phoneme)
  - No `core_logos` equivalent will be introduced
  - The renderer is the last thing before output leaves; nothing after it touches the field

#### 2. Implementation cross-reference

| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `Renderer` Protocol | **no** | — | repo-wide `rg "Renderer"` across `*.py`: **zero hits** |
| `generate/render.py` | **no** | — | file does not exist |
| `TextRenderer` | **no** | — | repo-wide: zero hits outside `docs/` |
| Caller-provided renderer injection | **no** | — | no call site accepts a renderer |
| Modality renderer implementations | **no** | — | none |
| `generate/stream.py` calls no renderer | yes (**vacuously**) | `generate/stream.py` | true because no renderer exists to call |
| No `core_logos` equivalent | yes | — | honored — nothing resembling it was built |
| **Actual** shipping renderer | yes | `generate/realizer.py` | `realize_semantic` (`:111`), `realize_target` (`:217`), `energy_modulated_surface` (`:39`); ~20 consumers across `chat/`, `core/cognition/`, `evals/`, `scripts/`, `tests/` |

**Build axis:** **ghost** — not one claimed artifact exists. The `render` hits elsewhere in the tree (`formation/templates/*.py:35-74`) are an unrelated template-rendering method on a different protocol, checked and excluded. The two "honored" rows are honored vacuously or negatively (nothing was built, so nothing calls it; no `core_logos` was introduced because no renderer subsystem of any kind was).

#### 3. Liveness / integration

Nothing to trace: there is no `Renderer`, so there is no call chain. The function the ADR describes is performed by `generate/realizer.py`, which is a *different design* — not a stateless protocol over a token iterable, but a semantic realizer taking a `PropositionGraph` and an `ArticulationTarget` and producing surfaces, with an energy-class modulation table (`:30-39`) and a companion guard module (`generate/realizer_guard.py`) that inspects and constrains output. It is neither caller-provided (call sites import it directly: `core/cognition/pipeline.py:49`, `generate/intent_bridge.py:48`, `chat/runtime.py:3143`) nor purely a transcription of a completed token stream.

**Sabotage test:** the mechanism cannot be removed, because it was never added. Removing the ADR itself would change nothing except that a reader would stop being told that `generate/render.py` exists.

**Liveness axis:** **dead** — a ghost decision. The capability it describes is met by a differently-shaped module that the ADR does not mention and that postdates it.

#### 4. Design fidelity — pillars and axioms

Scored as written, independent of the build — and as written it is a good decision, which is worth recording plainly since the verdict below is retirement.

| Pillar | Honors / Tension / Violates | Citation |
|---|---|---|
| I. Mechanical Sympathy | **n/a** | A thin stateless protocol has no meaningful machine-sympathy content, and the ADR makes no performance claim. |
| II. Semantic Rigor | **Honors** | "The field knows what it means. The renderer only knows how to write it down. These are fundamentally different concerns." The `core_logos` critique — that mixing algebra and output format is "a dual responsibility that violates Semantic Rigor" — names the pillar and applies it correctly. |
| III. Third Door | **Honors** | Rejects both the full-subsystem shape (`core_logos`) and the implicit-engine-renderer shape, choosing caller injection instead. |

| Axiom | Honors / Tension / Violates | Citation |
|---|---|---|
| 1. Geometry-First | **n/a** | The renderer is explicitly post-geometric — "nothing after the renderer touches the field." |
| 2. Field-State | **n/a** | Explicitly stateless by design. |
| 3. Propagation-over-Mutation | **Honors** | "Why stateless? Propagation-over-mutation… It does not accumulate, buffer, or modify field state." The axiom is cited by name. |
| 4. Dual-Correction | **n/a** | A pure transcription function has no conjugate, correctly. |
| 5. Reconstruction-over-Storage | **n/a** | No storage. |
| 6. Compilation-Last | **Honors** | The decision is one protocol; every representation choice is deferred to implementations. |
| 7. Reality-over-Inheritance | **Honors, and self-applied** | The ADR *retires an inherited abstraction from the predecessor system* by name, on the grounds that it solved the wrong problems first. The irony is that the same axiom now applies to this ADR. |

#### 5. Build fidelity — does the code match the decision?

§2 found `ghost`, so there is no implementation to compare. The substantive observation is that the ADR's **core architectural bet was not taken**: it bet that renderer thinness was correct and that a subsystem was over-engineering. What shipped (`generate/realizer.py` + `generate/realizer_guard.py` + the energy-modulation table + the register/decoration surface in `chat/runtime.py`) is much closer to the `core_logos` shape the ADR rejected — a realization layer with its own guard, its own governance surface, and its own trace metadata. Not identical, and arrived at by evolution rather than by decision, but the direction is the one ADR-0011 argued against.

That is worth stating precisely because it is the opposite of a stale line: it is a **reversed decision that no record reverses.**

**Build-fidelity axis:** **contradicts** — nothing was built to the contract, and what was built instead moves in the direction the ADR explicitly rejected.

#### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs

- **Contradicts `Whitepaper.md`?** No.
- **Contradicts `Yellowpaper.md`?** No.
- **ADR-0009 depends on it** — "the actual surface realization… is the responsibility of a downstream renderer that operates on the plan." That downstream renderer never existed; ADR-0009's terminal stage was already dangling when written.
- No ADR supersedes ADR-0011, and no ADR governs `generate/realizer.py`. The shipping renderer is, like ADR-0008's mechanism, **ungoverned** — but with a sharper problem: ADR-0008's mechanism is at least *described* by a stale draft, while the realizer is contradicted by the only ADR that claims its territory.
- **Continuity axis:** **unreconciled contradiction** — an Accepted ADR describes a renderer that does not exist and forbids a shape the system has drifted toward, while the actual renderer has no owning decision.

#### 7. Necessity / generality

1. **Necessity.** The *decision* is not necessary — the system renders without it, has for months, and the contract it specifies would today have to be retrofitted onto a realizer built on different premises. The *capability* is trivially necessary and long since delivered.
2. **Reducibility.** Reducible to `generate/realizer.py` — which does strictly more (semantic realization from a proposition graph, energy modulation, guard-checked output) than the token-transcription protocol ADR-0011 specifies. This is the one member of the stack where the successor is not just stronger but *categorically different in kind*, which is why the ADR reads as stale rather than superseded.
3. **Extensibility.** Nothing here to extend. The one live question the ADR raises that is *still open* is worth preserving through retirement: **who provides the renderer, and is output-time transformation deterministic?** The determinism half is now enforced elsewhere (`trace_hash`, replay lanes, `generate/realizer_guard.py`); the caller-injection half was silently abandoned. If ADR-0011 is retired, the retirement note should record that the injection question was answered "no" by drift, not by decision.

**Necessity/generality axis:** **reducible-to-`generate/realizer.py`** — retire, confirming the adopted disposition, with the recommendation upgraded from "stale line" to "retire the whole ADR and write one governing the realizer that actually ships."

#### 8. Fitness / value

- `02-layer-taxonomy.md` §1.1 — disposition recorded (adopted; confirmed and strengthened).
- The successor is heavily witnessed: `tests/test_articulation_realizer_v2.py`, `tests/test_realizer_guard_unit.py`, `tests/test_realizer_grounded_authority_flag.py`, `tests/test_negation_survives_articulation.py`, `tests/test_adr_0145_energy_modulated_surface.py`, plus `evals/grammar_roundtrip/`, `evals/discourse_paragraph/`, `evals/realizer_guard/run_holdout.py`, `evals/zero_code_domain_acquisition/`.
- ADR-0011 itself: no test, no eval, no pin, no consumer.

**Fitness axis:** **no evidence found** for the ADR; substantial evidence for the ungoverned successor (nine test/eval artifacts). The ADR has delivered nothing because nothing was built.

#### 9. Findings raised

- **AA-A2-8** 🟡 — ADR-0011 is a complete ghost: `generate/render.py`, the `Renderer` Protocol, and `TextRenderer` do not exist anywhere in the repository. Strengthens the adopted disposition from "stale line" to "every claimed artifact absent." (§2)
- **AA-A2-23** 🟡 — Reversed-by-drift: what shipped (`generate/realizer.py` + `realizer_guard.py` + energy modulation + register/decoration surface) moves toward the `core_logos` subsystem shape ADR-0011 explicitly rejected. An architectural bet was reversed and no record reverses it. (§5)
- **AA-A2-24** 🟡 — The shipping renderer has **no owning ADR**, and the only ADR claiming its territory contradicts it. Same governance class as G-14/CR-1: a live serving mechanism with no decision behind it. (§6)

#### 10. Evidence sources actually consulted

- ADR-0011 in full (`docs/adr/ADR-0011-renderer.md` — note the filename is `-renderer.md`, not the `-renderer-layer-contract.md` the audit assignment cited; the task's path 404'd and the file was located by glob).
- Repo-wide `rg` at `cbfc8ccb` for `Renderer`, `TextRenderer`, `class Renderer`, `def render(` across `*.py` — zero relevant hits; the six `def render(` hits in `formation/templates/` inspected and excluded as an unrelated protocol.
- `ls generate/render.py` → does not exist. Full `generate/` directory listing (100+ modules) inspected for any renderer module.
- `generate/realizer.py:18-39, 111, 188-219`; repo-wide consumer census for `generate.realizer` (~20 call sites across `chat/`, `core/cognition/`, `evals/`, `scripts/`, `tests/`, `benchmarks/`).
- `docs/assessment/02-layer-taxonomy.md` §1.1.

---

## 3. Stack-level synthesis

### Internal consistency

The six agree with each other as *design*, and that is the stack's most interesting property: it is a genuinely coherent architecture. The composition is stated and consistent — ADR-0010's drive gradients shape the field, ADR-0008 computes salience over that shaped field, ADR-0009 binds what ADR-0008 foregrounds, ADR-0011 renders what ADR-0009 plans, and ADR-0006/0007 supply the scalar and vector annotations all of them read. No member silently contradicts another.

**The contradictions are all between the stack and the system**, and they cluster at the seams:

- ADR-0010 states salience is computed "against a field that is already shaped by drive gradients." It is not — `generate/salience.py` reads raw versors and per-word energy. **The 0010→0008 seam is fictional.**
- ADR-0010's fatigue coupling requires ADR-0008's `CoherenceBudget`. That budget was never constructed. **The 0008→0010 back-edge is fictional.**
- ADR-0009's `BindingOperator` takes ADR-0008's `AttentionPlan`. Nothing produces one. **The 0008→0009 seam is fictional.**
- ADR-0009 defers surface realization to ADR-0011's renderer. It does not exist. **The 0009→0011 seam is fictional.**
- ADR-0007's bundle is written into the field and read by nothing. **The 0007→surface seam is fictional** (and is a type-confusion bug, AA-A2-1).

Five of the stack's seams are fictional. What survives is the *nodes*, not the *edges* — and only some nodes. The one seam that genuinely runs is `TrajectoryOperator → IdentityCheck` (ADR-0009 → ADR-0010), plus energy's own downstream links, which were never part of the blueprint's composition story at all.

There is also one internal citation defect: ADR-0008's `Related` field cites "ADR-0007 (Ingest Layer)" when ADR-0007 is the Valence Layer (AA-A2-15).

### Cumulative build state

Counting the operators the stack names, not the ADRs:

| Operator / artifact | Built? | Live? |
|---|---|---|
| `FieldEnergyOperator` (0006) | yes | **live** — 4 routes |
| `ValenceBundle` + `lift_valence` (0007) | yes | produced & carried; **consumed by nothing** |
| `SalienceOperator` (0008) | yes | **live** — composed into the hot path |
| `AttentionOperator` (0008) | yes | dead (a *different* live class shares the name) |
| `InhibitionOperator`/`InhibitionMask` (0008) | yes | dead |
| `CoherenceBudget` (0008) | yes | dead |
| `BindingOperator`/`BindingFrame` (0009) | yes | dead (a local `_StubBindingFrame` stands in) |
| `DigestOperator`/`DigestCycle` (0009) | yes | dead |
| `TrajectoryOperator`/`ReasoningTrajectory` (0009) | yes | **live** — as the identity gate's input container |
| `ArticulationPlanner`/`OutputModality` (0009) | yes | dead (a *different* live `ArticulationPlan` shares the name) |
| `IdentityCheck`/`IdentityManifold`/`CharacterProfile` (0010) | yes | **live** — fail-closed, INV-32 |
| `DriveGradientMap` (0010) | yes | dead (constructed, never read) |
| `ExertionMeter`/`FatigueIndex` (0010) | yes | telemetry only |
| `Renderer`/`TextRenderer` (0011) | **no** | ghost |

**14 named operators: 4 live, 1 telemetry-only, 1 produced-but-unconsumed, 7 dead-but-built, 1 ghost.**

The striking number is **7 dead-but-built**. This stack's failure mode is not the usual one (decisions that were never implemented); it is the rarer and more misleading one — decisions that *were* implemented, correctly, to spec, and then never wired. `core/physics/__init__.py` exports all of them, so the module's public surface advertises a complete three-layer physics that does not run. H-2 named two instances of this; this audit finds **five modules** (`attention`, `inhibition`, `binding`, `digest`, `articulation`) that are imported by nothing but `__init__.py`, plus `drive` which is imported and constructed but never read.

**The chain stalled at the seams, not at the nodes.** Someone built every box and wired almost none of the arrows.

### Cumulative necessity/generality read

**The stack introduces N narrow mechanisms that happened to get built in sequence, not one coherent generalizable one** — and the evidence is that its survivors ended up in four different places under four different owners:

- Energy → survives in `core/physics/energy.py`, consumed by salience, realizer, vault, propagation.
- Salience → survives *composed into* `generate/salience.py`, governed by nothing (G-14).
- Identity → survives, superseded upward into ADR-0244's wave-field manifold, governed by INV-32.
- Composition → survives displaced into the proposition-graph lineage across ~20 `generate/` modules.
- Valence, drive, exertion, budget, binding, digest, inhibition, renderer → did not survive as mechanisms.

A genuinely general mechanism does not disperse like that. The "three physics layers" framing was a *narrative* imposed on the cognitive cycle, and the parts that were real (a field annotation, a curvature-based candidate filter, a geometric identity check) were real independently of it.

**Consolidation candidates for `22-consolidation-report.md`** — the stack yields five, ranked:

1. **ADR-0006 ⊕ ADR-0007 → one "field-state annotation" mechanism.** Structurally identical: typed record lifted from source structure at compile time, carried immutably on `FieldState`, codec-serialized, consulted at the realizer. Energy got a consumer and thrived; valence did not and atrophied. `generate/realizer.py:30-39`'s class→behavior dispatch table is exactly the shape valence needs and would absorb it directly. **Highest-value pairing in the stack** — it is the only one where consolidation would *add* capability rather than remove dead code.
2. **The five dead `core/physics/` operator modules → one deletion.** `attention`, `inhibition`, `binding`, `digest`, `articulation` (+ `drive`). H-2 already recommends deletion for two of them on mastery-framework grounds ("the best part is no part"); this audit extends the same evidence to all six. They should be retired as a unit, in one PR, with intents preserved in the CR-1 ADR (G-14) and the CR-2 design (G-4).
3. **ADR-0008 ⊕ ADR-0024/0025/0026 (stack A4) → one governed allocation contract.** Two allocation stages — salience/attention prunes candidates, admissibility judges them — governed by two unconnected decision families, only the second of which has ratified ADRs. This is G-14's substance and a cross-stack pairing A4's dossier must be told about.
4. **ADR-0010's exertion ⊕ ADR-0008's `CoherenceBudget` → retire or build as a unit.** Neither is useful alone: fatigue's only specified effect is budget compression, and the budget's only specified consumer is inhibition-from-reserve. Two dead mechanisms that are alive only together.
5. **ADR-0006 ⊕ ADR-0241 ⊕ ADR-0242 (Batch 5) → possible energy-mechanism consolidation.** Three coexisting energy constructions in `core/physics/`. Cannot be resolved from within this stack; flagged for when Batch 5 audits the later two.

The **name-collision hazard** (AA-A2-16) is a cross-cutting consequence of all this: `AttentionOperator`, `AttentionPlan`, `SalienceMap`, and `ValueAxis` each denote two different classes across `core/physics/` and `generate/`. Any consolidation PR should resolve these, since deleting the dead half resolves three of the four for free.

### Blast radius if this stack's central claim is wrong

The stack's central claim — *the cognitive cycle is governed by three composed physics layers* — is, on this audit's evidence, **already false in the built system**, and the useful question is therefore inverted: what depends on the claim still being believed?

- **Direct dependents (this stack):** the five fictional seams enumerated above. Nothing to re-verdict; they were never true.
- **`docs/assessment/02-layer-taxonomy.md` §1.1 and §5:** two rows revised by this audit (AA-A2-4, AA-A2-5) and two members (0006, 0007) absent from the table entirely (AA-A2-12). §1.1 is ratified and is cited as evidence by G-4 and H-2. Amending it is a documentation fix, but it is a **ratified-document** fix and needs the same care as an ADR amendment. **Blast radius: the taxonomy's §1.1/§5, G-4's evidence line, and CR-1's phrasing.**
- **Stack A4 (admissibility, ADR-0022–0026, 0046):** CR-1 names ADR-0024/0025/0026 as the only partial existence of attention/allocation, and this dossier confirms two allocation stages exist with only the second governed. **A4 must be told** that the first stage is ADR-0008's live salience/attention path and that G-14 is the open ruling covering it. **Blast radius: A4's necessity axis and CR-1's ruling framing.**
- **Stack A5 (identity/safety/ethics packs, ADR-0027–0037):** ADR-0010 is the origin of the `IdentityCheck` signature that A5's pack system feeds. This audit confirms the successor (ADR-0244/INV-32) is live and fail-closed, so A5 inherits a *sound* foundation. **Blast radius: none adverse — A5 can treat the identity half as settled.**
- **Stack A3 (semantic ground, ADR-0005/0015/0021):** ADR-0007 cites ADR-0005's lift/readback interface and depends on the claim that Hebrew/Greek morphology yields discriminating semantic signal. FA-1 ruled the *cross-language holonomy* form of that family's claim `DEFECTIVE`. These are not the same claim and this dossier does not extend FA-1's verdict — but ADR-0007 belongs in A3's cascade-check inventory, and nothing in this stack independently establishes the morphological-lift claim. **Blast radius: one row in A3's cascade list.**
- **M4 / `L6-chat-runtime`:** AA-A2-24 (the shipping renderer has no owning ADR, and the only ADR claiming its territory contradicts it) is an M4 governance gap of the same class as G-14. **Blast radius: M4's layer card should carry it.**
- **Determinism/replay (MV):** ADR-0010's fatigue non-stationarity would be a genuine replay hazard *if built*. It is not built — `apply_to_budget` has zero call sites — so replay is currently safe. This is worth recording as a **standing constraint**: any future work that wires fatigue into allocation must be gated against the replay lanes first. **Blast radius: none today; a named tripwire for tomorrow.**

**Nothing outside this stack needs re-verdicting on the strength of this audit.** The stack's failure is inward-facing — it misdescribes itself, and the two ratified records that summarize it are stale in two places. The corrections are documentation-grade, and the code-grade findings (AA-A2-1 chief among them) are local defects, not cascade triggers.

---

## 4. Stack-level findings (`AA-N`)

Placeholder IDs per the numbering discipline; real `AA-N` numbers assigned centrally at rollup.

| ID | Sev | Finding | Source |
|---|---|---|---|
| **AA-A2-1** | 🟡 | `chat/runtime.py:2958` passes a `ValenceBundle` to `_energy_scalar()` (`:229`), which has no bundle branch and returns the fallback `1.0` for every input — empirically confirmed at `cbfc8ccb`. `valence_delta` is therefore `0.0` on every turn after the first, making `generate/surface.py:123`'s `"but"` branch and `_apply_contrast` (`:216`) structurally unreachable on the serving path. | ADR-0007 §1, §3 |
| **AA-A2-2** | 🟡 | ADR-0007's entire "How Valence Drives Articulation" section is unimplemented — no consumer of `.force`, `.affective`, `.polarity`, `.orientation`, `.emphasis` exists downstream of `ingest/gate.py:381-405`. | ADR-0007 §2, §3 |
| **AA-A2-3** | 🟢 | `packs/common/affect_primitives.jsonl` does not exist; four of five valence channel enums degraded to bare `str`, leaving 12 of 15 specified affect primitives unreachable by construction. | ADR-0007 §2, §5 |
| **AA-A2-4** | 🟡 | **Revises adopted evidence.** `02-layer-taxonomy.md` §1.1 records `DriveGradientMap`/`ExertionMeter` as "Never built"; both are built and constructed on the live turn path (`chat/runtime.py:711-713, 2935-2948`). The assessment's own H-2/G-4 already corrected this; §1.1 was never amended, so the ratified taxonomy contradicts the ratified registers. | ADR-0010 §2, §3 |
| **AA-A2-5** | 🟡 | **Revises adopted evidence.** `02-layer-taxonomy.md` §5 CR-1 states `InhibitionMask` "appears never to have been built"; it exists at `core/physics/inhibition.py:15,23`. The substantive judgment (nothing constructs it) stands; the phrasing is wrong. | ADR-0008 §2, §3 |
| **AA-A2-6** | 🔵 | `EnergyProfile.requires_architect_review` is decoration — read only by its own test; the E4 escalation that ships (`core_ingest/compiler.py:154-160`) keys on a declared packet hint, not the computed class. | ADR-0006 §3 |
| **AA-A2-7** | 🔵 | Five `core/physics/` modules (`attention`, `inhibition`, `binding`, `digest`, `articulation`) are imported by nothing but `core/physics/__init__.py`; deleting all five changes no output. Extends H-2 from two instances to five modules (six with `drive`). | ADR-0008 §3, ADR-0009 §3 |
| **AA-A2-8** | 🟡 | ADR-0011 is a complete ghost — `generate/render.py`, the `Renderer` Protocol, and `TextRenderer` do not exist anywhere. Strengthens the adopted "stale line" disposition to "every claimed artifact absent." | ADR-0011 §2 |
| **AA-A2-9** | 🟢 | ADR-0006's E1/E2 threshold is `0.37` in code (`core/physics/energy.py:104`) vs `0.38` in the ADR's table; unpinned by any test. | ADR-0006 §5 |
| **AA-A2-11** | 🟢 | Two ADR-0006 consequences never delivered: the Rust energy path in `core_ingest_rs` and the anchor-adjacent region index. | ADR-0006 §2, §5 |
| **AA-A2-12** | 🟢 | ADR-0006 and ADR-0007 are absent from `02-layer-taxonomy.md` §1.1's disposition table and from the blueprint's staleness banner, which credits only ADR-0008 — the stack's two most load-bearing members are invisible in both governing records. | ADR-0006 §6 |
| **AA-A2-13** | 🟡 | ADR-0007 is an unregistered orphan: Accepted, unsuperseded, half-built, with zero mentions across the gap register, hindrance audit, layer cards, and §1.1. No record states its disposition. | ADR-0007 §6, §8 |
| **AA-A2-14** | 🔵 | Consolidation: ADR-0006 ⊕ ADR-0007 are one mechanism (field-state annotation lifted from source structure) built as two; `generate/realizer.py:30-39`'s dispatch would absorb valence directly. | ADR-0007 §7, §3 |
| **AA-A2-15** | 🟢 | ADR-0008's `Related` field cites "ADR-0007 (Ingest Layer)"; ADR-0007 is the Valence Layer and the ingest layer is ADR-0002. Misdirects citation-graph walks. | ADR-0008 §6 |
| **AA-A2-16** | 🟡 | Name collision: `AttentionOperator`, `AttentionPlan`, `SalienceMap` (and `ValueAxis`) each denote two different classes across `core/physics/` and `generate/`. Direct Pillar II hazard. | ADR-0008 §5, ADR-0010 §5 |
| **AA-A2-17** | 🔵 | `CoherenceBudget` — ADR-0008's explicit resource-accounting contribution — is unreached; the live budget is an integer `top_k`, and inhibition-draws-from-reserve was never built. | ADR-0008 §2, §5 |
| **AA-A2-18** | 🟡 | ADR-0009 reads `Status: Accepted` with no supersession marker despite being substantively superseded by the proposition-graph lineage. A reader using only `docs/adr/` would implement the wrong pipeline. | ADR-0009 §6 |
| **AA-A2-19** | 🟢 | `chat/runtime.py:307`'s `_StubBindingFrame` stands in for `core/physics/binding.py`'s `BindingFrame` on the live path while the real type sits unused. | ADR-0009 §5, §7 |
| **AA-A2-20** | 🟡 | ADR-0010's two operative behavioral claims are unimplemented: `combined_bias()` and `apply_to_budget()` both have zero call sites, so drives do not bias traversal (contradicting both ADR-0010 and ADR-0008's stated composition) and fatigue compresses no budget. | ADR-0010 §3, §5 |
| **AA-A2-21** | 🔵 | Consolidation: ADR-0010's exertion and ADR-0008's `CoherenceBudget` are alive only together — retire or build as a unit, never singly. | ADR-0010 §7 |
| **AA-A2-22** | 🟢 | `ValueAxis` defined twice (`core/physics/drive.py:15`, `core/physics/identity.py:196`), ambiguity documented in a comment rather than resolved. | ADR-0010 §5 |
| **AA-A2-23** | 🟡 | Reversed-by-drift: what shipped (`generate/realizer.py` + `realizer_guard.py` + energy modulation + register surface) moves toward the `core_logos` subsystem shape ADR-0011 explicitly rejected. An architectural bet was reversed and no record reverses it. | ADR-0011 §5 |
| **AA-A2-24** | 🟡 | The shipping renderer (`generate/realizer.py`, ~20 consumers) has no owning ADR, and the only ADR claiming its territory contradicts it. Same governance class as G-14/CR-1. | ADR-0011 §6 |
| **AA-A2-25** | 🔵 | *Stack-level, visible only in aggregate:* 7 of 14 named operators in this stack are **built-to-spec and dead**, and `core/physics/__init__.py` exports all of them — so the module's public surface advertises a complete three-layer physics that does not run. Five of the stack's six composition seams are fictional. This is H-2's "decoration is how architecture lies without anyone lying" at stack scale. | §3 |

**Count: 24 findings** (IDs `AA-A2-1` … `AA-A2-25`; `AA-A2-10` retired during drafting and not reused, to keep per-card cross-references stable).

Severity split: **11 🟡 Repair**, **6 🔵 Consolidate**, **7 🟢 Monitor**, **0 🔴 Block**. No finding blocks — nothing here endangers the serving path's correctness today. AA-A2-1 is the closest to user-visible (two surface-fluency behaviors silently unreachable) and is a contained type-confusion fix.

---

## 5. Evidence sources actually consulted (stack-wide)

**Audit charter and templates**
- `docs/adr-audit/00-scope-and-method.md`, `TEMPLATE-stack-dossier.md`, `TEMPLATE-adr-card.md`, `02-stack-taxonomy.md`, `MANIFEST.md`, `01-adr-census.md` (rows 0006–0011).

**Member ADRs — all six read in full**
- `docs/adr/ADR-0006-field-energy-operator.md`, `ADR-0007-valence-layer.md`, `ADR-0008-allocation-physics.md`, `ADR-0009-compositional-physics.md`, `ADR-0010-identity-physics.md`, `ADR-0011-renderer.md`.
- *Note:* the assignment cited `ADR-0011-renderer-layer-contract.md`; the actual filename is `ADR-0011-renderer.md`. Located by glob after the given path 404'd.

**Prior evidence (read first, per the charter's evidence-source order)**
- `docs/assessment/02-layer-taxonomy.md` in full (§1.1 disposition table, §5 Candidate Register CR-1/CR-2, §6 completeness criteria).
- `docs/assessment/20-component-cards/attention-allocation.md` in full — adopted, then spot-checked line-by-line at `cbfc8ccb`.
- `docs/assessment/31-hindrance-audit.md` H-2, H-5; `docs/assessment/30-gap-register.md` G-4, G-14.
- `docs/assessment/10-layer-cards/M0-substrate.md`; `docs/assessment/10-layer-cards/M1-knowledge-memory.md` (searched — zero energy/valence hits, recorded as a negative result).
- `docs/assessment/README.md` (file inventory); `docs/architecture/MIND-PHYSICS-BLUEPRINT.md` (staleness banner).
- `AGENTS.md` INV-32; `docs/adr/ADR-0244-*.md` section structure (§2.1, §2.2, §3, §4a).

**Code read (all at `cbfc8ccb`)**
- Full: `core/physics/energy.py`, `core/physics/valence.py`, `core/physics/attention.py`, `core/physics/inhibition.py`, `core/physics/drive.py`, `core/physics/exertion.py`, `field/state.py`, `field/propagate.py`, `generate/salience.py`, `generate/attention.py`.
- Partial: `chat/runtime.py` (`:226-252, 295-402, 700-729, 1803-1831, 2895-2964, 3010-3020, 2625-2645, 3280-3300`), `generate/stream.py` (`:255-278, 325-331, 637`), `generate/articulation.py` (`:1-30`), `generate/realizer.py` (`:18-39, 111, 188-219`), `generate/surface.py` (`:47, 61, 122-130, 215-216, 266`), `core/physics/salience.py`, `core/physics/reasoning.py`, `core/physics/identity.py` (class inventory), `core_ingest/compiler.py` (`:85-110, 150-165, 185`), `ingest/gate.py` (`:35, 381-429`), `vault/store.py` (`:24, 38-49, 365-398`), `packs/compiler.py` (`:14-15, 72, 339-355, 405, 558`), `packs/common/runtime_rules.py`, `vocab/manifold.py` (`:36-37, 74-75, 227-231`), `core/config.py` (`:35-37`), `scripts/review_trace.py` (`:172`).

**Executed verification (not read — run)**
- `uv run python` at `cbfc8ccb`: `_energy_scalar()` applied to three structurally distinct `ValenceBundle`s and to `None`; all four returned `1.0`. **This is the load-bearing evidence for AA-A2-1 and for §1's NO-GO verdict** — measured, not inferred from prose.
- Repo-wide `rg` sweeps for every claimed symbol in all six ADRs, across `*.py`, `*.rs`, `*.md`; import-graph checks establishing the import-only status of five `core/physics/` modules; zero-call-site checks for `combined_bias`, `apply_to_budget`, `requires_architect_review`.
- Filesystem existence checks: `generate/render.py` (absent), `packs/common/affect_primitives.jsonl` (absent), `{en,he,el}/readback_rules.py` (absent), `packs/{he,el}/morphology.jsonl` (present), `tests/test_energy.py` (present).
- Test-file inventory for energy/valence/salience/identity pins; `tests/test_energy.py` inspected for threshold-boundary coverage (none at the 0.37/0.38 boundary).

**Explicitly not done** (per the charter's non-goals): FA-1 was not re-run; its ADR-0005/0015 `DEFECTIVE` verdict is adopted as given, and this dossier does not extend it to ADR-0007 — it only flags ADR-0007 for A3's cascade inventory. No ADR, runtime file, or file outside this dossier was edited.
