# Phase 0 — Ground Truth and Phase 1 Handoff

**Executor:** Opus 5, 2026-07-27. **Base:** `forgejo/main` @ `8927c563`.
**Charter:** ingest the canonical corpus, recover the existing macro→micro artifacts, triage the decision record, and hand Phase 1 the raw material plus the tensions it must resolve.

**What Phase 0 deliberately did not do:** build the taxonomy, fill any card, or judge any component. Those are Phases 1–3. Findings below are recorded as *evidence and tension*, not as verdicts. Where a finding looks like a gap or a hindrance, it is flagged for the Phase 4 registers rather than adjudicated here.

---

## 1. The canonical corpus — what is authoritative, and as of when

| Document | Role | Dated | Status |
|---|---|---|---|
| `AGENTS.md` | Canonical governance. Wins over all provider files. | live | Authoritative |
| `docs/specs/runtime_contracts.md` | Frozen runtime contracts; INV-21…INV-34 | live (1089 lines) | Authoritative |
| `docs/adr/MASTER-BLUEPRINT-2026-07-20-ADR-MAPPING.md` | Blueprint↔registry collision reconciliation | 2026-07-20 | **Governing** |
| `docs/adr/ADR-0252` | **The governing problem-solving paradigm** | 2026-07-19 | **Accepted / ratified** |
| `docs/position_paper.md` | Thesis and philosophical intent | — | Reference |
| `docs/Whitepaper.md` / `docs/Yellowpaper.md` | Architecture narrative / formal Cl(4,1) spec | — | Reference |
| `docs/architecture/MIND-PHYSICS-BLUEPRINT.md` | Three-physics-layer cognitive cycle | 2026-05-12 | **Draft**, never advanced |
| `docs/master-plan-post-substrate-audit.md` | Phase plan, W-* cascade | 2026-05-24 (+ amendments) | Largely superseded |
| `docs/audit/substrate-liveness-ratchet.md` | Wiring-debt registry (v5) | ~2026-05-24 | 7 OPEN, stale |
| `docs/gaps.md` | Capability-gap register | — | **All 26 entries closed** |
| `CLAIMS.md` | Machine-generated claim ledger: 5 Tier-1 domains, 11 Tier-2 pinned lanes | auto | Authoritative |
| `.system-map/` | 33 zones / 205 subsystems / 246 edges / 10 bands | 2026-06-09 | Local-only, gitignored, 48 days stale |

Validation surface: 21 CLI suites (`fast, smoke, runtime, cognition, teaching, packs, algebra, sensorium, pulse, formation, proof, refusal, margin, rotor, inner-loop, phase5, phase6, adr-0024, math, deductive, full`).

Code topology: `generate/` 219 modules, `core/` 171 (largest subpackages `physics/` 37, `capability/` 14, `contemplation/` 13, `cognition/` 13), `sensorium/` 59, `packs/` 48, `teaching/` 46, `chat/` 29, `formation/` 23, `workbench/` 22, `algebra/` 9, `recognition/` 7, `vault/` 5, `field/` 4. Tests 881, evals 375.

---

## 2. Finding 0-A — CORE has five different macro articulations of its own cognitive cycle, and none reconcile to the others

This is the central Phase 0 finding and the reason Phase 1 exists. Each articulation below is authoritative inside its own document. No document maps any of them onto any other.

**(1) The north star — `AGENTS.md`, 7 stages:**
`listen → comprehend → recall → think → articulate → learn from reviewed correction → replay deterministically`

**(2) The live path — `AGENTS.md`, 9 steps:**
`CognitiveTurnPipeline → tokenize / OOV policy / inject → intent classification → PropositionGraph → ArticulationTarget → deterministic realizer → telemetry/trace → reviewed teaching capture → deterministic replay/eval/calibration`

**(3) The three physics layers — `MIND-PHYSICS-BLUEPRINT.md`, Draft 2026-05-12:**
`FieldState → Allocation Physics (Salience/Attention/Inhibition, ADR-0008) → Compositional Physics (Binding/Digest/Trajectory/ArticulationPlanner, ADR-0009) → Identity Physics (IdentityCheck/DriveGradientMap/ExertionMeter, ADR-0010) → Renderer (TBD, "ADR-0011 planned")`

**(4) The governing paradigm — `ADR-0252`, Accepted 2026-07-19, five stages:**
`Perceive → core primitives · Comprehend → Structure-Map · Reconstruct → Quinian bootstrap · Solve → predictive processing / means-ends · Select → overlapping waves`

**(5) The system map — `.system-map/`, 10 bands / 33 zones:**
`L0 algebra → L1 field → L2 vault → L3 packs → L4 recognition → L5 cognition → L6 chat-runtime → L7 teaching → L8 memory/contemplation → L9 epistemic verdicts → L10/L11 runtime+identity (unbuilt)`, plus cross-cutting bands for ingest, lexical substrate, infra, reasoning, learning, afferent, governance, tooling.

**Why this matters, concretely.** Articulation (3) names an entire **allocation/attention layer** — salience, attention budget, inhibition — that appears nowhere in (1), (2), or the system map's telos ordering. Either attention allocation is a real layer that the live path silently omits, or it is a 2026-05 draft that was superseded and never retracted. Phase 2 must determine which; the answer changes whether CORE is missing a layer or carrying a stale blueprint. `MIND-PHYSICS-BLUEPRINT.md` also lists a Renderer as "TBD / ADR-0011 planned" while `generate/realizer.py` has been the shipping renderer for months — that line alone is stale.

Similarly, articulation (4) is **ratified and governing** but is a paradigm for *problem-solving*, while (2) is a *turn pipeline*. Nothing states how ADR-0252's five stages map onto the nine pipeline steps. Phase 1 must decide whether the taxonomy is built on the pipeline, on the paradigm, on the band/zone layering, or on a reconciliation of all three — and must say explicitly which articulations the chosen spine subsumes and which it retires.

**Recorded for Phase 4:** an architecture with five unreconciled self-descriptions cannot answer "is anything missing" for any of them, because a component absent from one is present in another and no document adjudicates. This is a design-layer gap, not an implementation gap.

---

## 3. Finding 0-B — the system map is the best existing macro→micro artifact, and it is stale, invisible, and partially hollow

`.system-map/` (2026-06-09) is a 33-zone / 205-subsystem / 246-edge layered map with per-zone greppable cards, built by a four-wave multi-agent sweep with coverage critics. It is the closest thing CORE has to the artifact this assessment is meant to produce, and Phase 1 should treat it as a prior rather than start from scratch.

Three qualifications:

- **48 days stale.** Built before the entire deduction-serve arc (ADR-0256 through ADR-0265), the curriculum-serving arc, the two-grammars work, and PRs #98–#138. Its liveness labels predate all of it.
- **Local-only and gitignored** by deliberate choice. It is not a project artifact, is invisible to every fresh clone and every agent that does not know to look, and cannot be reviewed in a PR. Whether the assessment's own output should inherit that property is a Phase 1 question.
- **Four zones carry zero subsystems** — `comprehend-organ`, `determine-phase`, `realize-phase`, `sensorium-falsification`. These were added in the final wave as zone headers without descent. Three of the four sit directly on the serving path, which makes them the least-mapped parts of the most load-bearing region.

**Zone liveness rollup (2026-06-09, verify before relying on any row):**

| Liveness | Count | Zones |
|---|---|---|
| `live-serving` | 6 | L0-algebra, vocab-manifold, governance-identity-safety, comprehend-organ, determine-phase, realize-phase |
| `live-internal` | 5 | morphology, alignment-resonance, capability, engine-state, sensorium-falsification |
| `partial-wiring-debt` | **18** | L1-field, L2-vault, L3-packs, L4-recognition, L5-cognition, L6-chat-runtime, L7-teaching, L8-memory-contemplation, L9-epistemic-verdicts, L10-11-runtime-identity, ingest-boundary, ingest-compiler, reasoning-deductive, gsm8k-math, reliability-calibration, formation-curriculum, evals-determinism, tooling-cli-workbench-rs |
| `spike` | 1 | core-protocol-ctp |
| `inert` | 2 | edge-sync, sensorium-afferent |
| `research-negative` | 1 | field-wedge-research |

The map's own recorded caveat is important and should be carried forward: **a zone inherits its weakest honest label**, so "partial" at zone level is compatible with most subsystems being live. Zone-level liveness must never be quoted as a system-level completion rate.

---

## 4. Finding 0-C — two load-bearing questions are open, and one of them gates the governing paradigm

### 4.1 The ADR-0252 §5 experiment has never returned a verdict

ADR-0252 is the ratified governing paradigm. Its ruling record is explicit:

> **NOT authorized.** The §6 build (the structure-map comprehension layer and any serving change) is **not** authorized by this ratification. It is gated on §5 returning GO.

§5 is a controlled experiment on exactly one empirical claim: **can Cl(4,1) geometry carry a problem's relational structure faithfully enough that `conformal_procrustes` aligns same-deep-structure problems and separates different-structure ones — driven by relations, invariant to surface attributes?** GO requires separability with margin *and* attribute-invariance *and* structure-sensitivity. A well-controlled NO-GO is defined as full credit.

**Status: unrun.** Two unmerged worktrees exist — `rnd/structure-mapping-experiment` @ `fc9d0c14` ("add SME feasibility research and experimental script") and `rnd/sme-experiment-v2` @ `bed29a09` ("formalize §5 experiment scaffolding — corpus extractor + single-pair probe"). Neither has reached `main`; neither reports a verdict.

The consequence is structural, not procedural. ADR-0252 diagnoses CORE's single architectural error as *"a **novice** comprehender (34 bespoke surface organs) bolted onto an **expert** substrate it never used for comprehension"* — and rules that the 34 surface organs keep serving until a proven replacement exists. So the diagnosis is ratified, the correction is designed, the replacement is gated on an experiment that has not run, and the thing diagnosed as the error is what serves today. **This is the highest-leverage open item Phase 0 found**, and it belongs at the top of the Phase 5 synthesis.

### 4.2 L10 is the single blocking node of the entire wiring-debt registry

All **7 OPEN** entries in `docs/audit/substrate-liveness-ratchet.md` chain to W-008 (the L10 runtime model): W-003 → recognizer-storage ADR → W-007; W-009 → W-017; W-018; each annotated "sized after W-008 commits." The 2026-05-24 master plan named this correctly — *"L10 is the load-bearing decision… wrong shape locks in wrong architecture for the rest of the cascade"* — and the spike it demanded (prove a long-lived process holds field state, vault, and session continuity across 24+ hours without leak or drift) has never been run.

The system map states the consequence in the sharpest available terms: field excitation and the T1 vault are **discarded on process exit**, so only the learned-recognizer layer compounds across reboots. **"One continuous life" today is many short lives sharing a checkpoint.** Given that `project-core-is-one-continuous-life` is the foundational telos, this is the largest single distance between stated purpose and built system.

---

## 5. Finding 0-D — CORE has no live gap register

Three registers exist; none is currently tracking the frontier.

- `docs/gaps.md` — **all 26 entries closed** (`[x]`). A register with nothing open is either a solved system or an abandoned instrument. It is the latter: it tracks pack/threshold gaps from the capability-ledger era and has no entry for anything in the 2026-07 arc.
- `docs/audit/substrate-liveness-ratchet.md` — v5, 7 OPEN, all L10-blocked, untouched since ~2026-05-24.
- `docs/analysis/` — ~130 dated per-arc lookback and ratification documents. This is where the real findings live, but it is a chronological archive, not a register: nothing aggregates it, and a finding recorded in a June lookback is discoverable only by knowing it exists.

**Implication for Phase 4:** the gap register this assessment produces will be the first live one, and Phase 1 should decide whether it supersedes `docs/gaps.md` or sits beside it. Two dead registers plus a live one is a worse outcome than one live one.

---

## 6. Finding 0-E — the decision corpus has outgrown its own index

333 files in `docs/adr/`, flat sequential numbering to ADR-0265. Status is not reliably machine-extractable: a scan for status lines yields roughly 200 `accepted` and 72 `proposed` against 333 files, with the remainder carrying malformed, absent, or prose status lines (`status follows`, `status as`, `Phase`, `Delegated`). Any claim of the form "N ADRs are Accepted" is therefore approximate, and Phase 3 must not build on it without per-file verification.

`INDEX-by-domain.md` is the existing mitigation and is admirably honest about its own limits — it covers only live serving, telemetry, and governance surfaces and states plainly that *"an index asserting coverage it does not have is worse than none."* It was written when the corpus was 312 files; it is now 333, so the index is already 21 files behind and its "index on mint" maintenance rule is not holding.

Two structural hazards are already documented and should be carried into Phase 4: the ADR-0206/ADR-0256 numbering collision that had to be resolved in prose, and the Master Blueprint's wholesale collision with Accepted ADR-0246–0252, which required a governing mapping document to adjudicate and left **numbers 0254–0261 reserved for Blueprint intents that were never materialised** — while ADR-0254 through ADR-0265 were subsequently minted for entirely different decisions. The reservation table in the governing mapping is therefore contradicted by the live registry.

---

## 7. Finding 0-F — the measured performance picture contradicts the intuitive one

Recorded here because Phase 4's hindrance audit will otherwise re-derive it, and because it is a clean instance of the mastery framework's warning against optimizing what shouldn't exist.

- **CGA dominates turn time (~73%)** — but through `cga_inner` → `geometric_product` at ~33,986 calls/turn in nearest-neighbour and salience search, **not** through the versor invariant. `versor_condition` measures **0.448 ms against a 200 ms turn — 0.22%**. An earlier assessment claimed it was "~10× the entire proof latency" by multiplying an isolated microbenchmark by a call count and comparing against a single verdict's latency; that was corrected by direct measurement (`docs/research/cga-hot-path-measurement-2026-07-25.md`).
- **The Rust backend is off by default.** `algebra/backend.py`: pure Python is the deterministic default; Rust is opt-in via `CORE_BACKEND=rust`. Whether `core_rs` still holds bit-exact parity is **an open question, blocked** — `cargo` could not reach `static.crates.io` under the sandbox network policy on 2026-07-25.
- **MLX is in no runtime path.** It appears in exactly two files, both under `benchmarks/`. The Neural Engine claim in `README.md` is a design aspiration explicitly disclaimed by the repo's own measured report.
- **The deduction and curriculum serving paths are pure-Python ROBDD and never touch CGA.** FrameVerdict TTFV is 0.151 ms.

---

## 8. Finding 0-G — a prior assessment exists, and its lesson is methodological

`docs/research/architecture-assessment-verification-2026-07-25.md` verified an external architectural assessment against the tree and found **roughly a third of its work items falsified by the codebase**, one flagship item diagnosed at the wrong layer, and the most urgent live defect named in neither document. The falsified items were not careless — they were plausible readings that no one had checked against code.

Two things follow. First, the precedent validates this assessment's read-the-code rule and raises the bar: a finding without an evidence pointer is a hypothesis. Second, its §7 item 1 (the Workbench provenance falsification, where a proved deduction answer was recorded as `grounding_source = 'none'`) now appears **closed** — `runtime_contracts.md` documents the three-part registration requirement and names the pin `tests/test_workbench_deduction_provenance.py`. Phase 3 should verify rather than assume.

---

## 9. Raw material for Phase 1 — the proto card schema

The system map's node schema is the closest existing thing to what Phase 1 must specify, and it already anticipates several fields a naive schema would miss.

**Existing fields (17):** `zone_id`, `zone_name`, `layer`, `band`, `classification`, `macro_role`, `what_it_is`, `what_it_does`, `inputs`, `outputs`, `invariants`, `key_files`, `owning_adrs`, `relationships`, `subsystems`, `telos_stage`, `liveness`, plus **`honest_wrinkles`** — a field for what is true about the component that its label would otherwise hide. That field should survive into Phase 1's schema under some name; it is the structural defense against decoration.

**Existing liveness vocabulary (7 values, ordered):**
`live-serving` → `live-internal` → `partial-wiring-debt` → `spike` → `inert` → `unbuilt` → `research-negative`

This is richer than the four-value scale proposed in the approach plan and distinguishes things that matter: serving versus merely-executing, never-built versus built-and-disconnected, and research that returned a negative result (`field-wedge-research`) — a category a naive schema would misfile as failure rather than as knowledge.

**What the existing schema lacks, measured against what Shay asked for:**

| Required dimension | Present? | Note |
|---|---|---|
| Philosophical intent — what the component is *for* in the cognitive model | Partial | `macro_role` / `what_it_is` are functional, not teleological |
| Functional contract — inputs/outputs/invariants | **Yes** | Strongest part of the existing schema |
| Design shape vs implementation detail | Partial | `key_files` only; no design-vs-built distinction |
| Implementation status | **Yes** | The 7-value liveness vocabulary |
| **Evidence pointer** — the test/lane/pin proving the status | **No** | Liveness is asserted, not evidenced. Highest-priority addition |
| **Capacity** — to what degree, at what limit | **No** | "To what capacity" has no field at all |
| Dependencies | **Yes** | `relationships`, `inputs`, `outputs` |
| Governing ADRs | **Yes** | `owning_adrs` |
| Known hazards | **Yes** | `honest_wrinkles` |
| **Fitness judgment** — is this the right solution here? | **No** | Required by Phase 4; no field exists |

---

## 10. Handoff to Phase 1

**Deliverables:** `docs/assessment/02-layer-taxonomy.md` and `docs/assessment/03-card-schema.md`.

**The five decisions Phase 1 must make explicitly, with reasoning recorded:**

1. **Which articulation is the spine?** Choose among the turn pipeline (2), the ratified paradigm (4), the band/zone layering (5), or a reconciliation — and state which of the five articulations the choice subsumes, which it retires, and what happens to the allocation/attention layer from (3) that exists in no other articulation.
2. **Adopt, extend, or replace the system map's schema and its 7-value liveness vocabulary?** Extension is the recommended default: the vocabulary encodes distinctions already earned. The four missing dimensions — evidence pointer, capacity, design-vs-built, fitness — must be added regardless.
3. **What is the completeness criterion?** Per Pillar I this must be fixed before any card is filled: by what test does a layer get called complete, and by what test does a *missing* layer get identified as missing rather than as out of scope? Without this, question 2 of the charter cannot be answered rigorously.
4. **Where do candidate layers live?** The taxonomy needs an explicit section for layers CORE's own documents do not name — beginning with whatever the always-on L10 PROCESS requires that no current zone owns, and whatever an AGI/ASI-grade system requires that CORE's telos implies but no document has articulated. This section is where charter question 2 actually gets answered.
5. **Is the assessment output committed or local-only?** The system-map precedent is gitignored. This assessment is currently on a branch intended for a Forgejo PR. These are incompatible defaults; pick one and state why.

**Reference documents for Phase 1** (keep to these two plus this file; do not re-ingest the corpus): `AGENTS.md` and `docs/adr/ADR-0252-problem-solving-paradigm-consolidation.md`. The system map's zone cards are greppable at `.system-map/zones/*.md` in the **main** worktree (`/Users/kaizenpro/Projects/core`), not in `core-wt-assess` — it is gitignored and does not travel with the branch. Query `data.json` with `jq`; never slurp it.

**Standing cautions for every downstream phase:**

- Apply the sabotage test to every `live` claim. `g_args_rate` was `0.0` while a section claimed the reader read it.
- Zone-level liveness is a weakest-link rollup and must not be quoted as a completion rate.
- Everything in the system map is 48 days old and predates the entire deduction-serve and two-grammars arc.
- The PR #138 fabrication findings are **measured and pinned, held for ADR + ratification** — record, never re-discover, never fix.
