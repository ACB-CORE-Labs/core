# B1 — Ingest & Multimodal Boundary

**Zone:** B1 (macro layer M2 — Afferent Boundary) | **Tier:** B | **Members:** ADR-0002, ADR-0012, ADR-0013
**Card author:** Claude (Tier B audit pass) | **`verified_at` SHA:** `cbfc8ccbf7fe503ab31abe7aedbb1973ba7d7b4d`

All three ADRs govern the same seam: the point where untrusted external reality (text, code, scripture, and — designed but not yet live — vision/audio/motor signal) becomes admissible CORE structure. ADR-0002 and ADR-0012 are one continuous decision arc — ADR-0012 explicitly supersedes ADR-0002, both reject an LLM (or general NLP library) as the extraction engine feeding the single normalization site and replace it with a deterministic, form-only `StructuralSegmenter` plus a three-gate governance compiler (`core_ingest/`), upstream of and never touching the pre-existing transient injection gate (`ingest/gate.py::inject`). ADR-0013 defines the parallel non-text lane (`sensorium/`), designed to sit upstream of both `core_ingest/` and `ingest/gate.py` for *every* modality, text included, via a single `ProjectionHead` → `(32,) Cl(4,1)` versor boundary. All three share the same founding move against the same two visible options (an external interpreting model, or a general-purpose NLP library) in service of Semantic Rigor and Third Door — and all three are, as built, split across a genuinely live hot path (`ingest/gate.py`) and a substantially built but not-request-reached governance/multimodal lane (`core_ingest/`, `sensorium/`). The central finding of this card is that the split is *partly* the intentional dual-path architecture the ADRs describe, and *partly* an unreconciled duplication: the live text path never actually routes through the universal boundary ADR-0013 designed for it.

---

## ADR-0002 — Ingest Layer Architecture

**Audit ID (if a numbering collision):** — | **Family (if phased):** —
**Zone / stack:** B1 — Ingest & Multimodal Boundary (M2) | **Tier:** B
**ADR status (as recorded in the file):** Accepted | **ADR date:** 2026-05-12
**Card author:** Claude | **`verified_at` SHA:** `cbfc8ccb`

---

### 1. Content summary

- **Decision made:** Port the structural elements of the `core-ai` repo's `core_ingest` design into `AssetOverflow/core`, but replace its LLM-based extraction engine with a deterministic `StructuralSegmenter` that carves source documents at *form* boundaries (headings, verse markers, code fences, LaTeX delimiters) rather than semantic ones — interpretation stays inside the field, not before injection.
- **Alternatives explicitly rejected:** LLM extraction with human review of all output ("scales to zero"); general-purpose NLP library (spaCy, stanza) for SVO extraction ("external libraries define the semantics — Third Door"); scrapping the ingest layer entirely ("the boundary is necessary").
- **Artifacts the ADR claims will exist:**
  - `CandidateGeometricPressure` — canonical pre-injection envelope
  - Dual-path architecture: runtime ingest (transient) vs. durable ingest (governed)
  - Content addressing via SHA-256 `pressure_id` and `semantic_key`
  - `IngestCompiler` with three sequential gates: Provenance, Semantic, Governance
  - `DeterminismClass` (D0–D4) and `ReviewLevel` embedded in packet type contracts
  - `LearningArtifact` as the durable export form
  - `StructuralSegmenter` (D0/D1-class, per-modality)
  - `SegmentManifold` (semantic_key → structural position index)

### 2. Implementation cross-reference

| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `CandidateGeometricPressure` | yes | `core_ingest/types.py:120` | Frozen/slotted dataclass; every field named in the ADR present, plus `__post_init__` invariants |
| Dual-path (transient vs. durable) | yes | `ingest/gate.py` (transient) vs. `core_ingest/` (durable) | Confirmed by grep: `core_ingest/compiler.py:22` and `core_ingest/pipeline.py:24` both state explicitly "`ingest/gate.py` is NOT imported or called here" — no cross-import in either direction |
| SHA-256 `pressure_id` / `semantic_key` | yes | `core_ingest/pressure.py:45,92` | Rust-accelerated (`core_ingest_rs`) with a pure-Python fallback of identical behavior |
| `IngestCompiler` (3 gates) | yes | `core_ingest/compiler.py:196` (`ProvenanceGate:48`, `SemanticGate:77`, `GovernanceGate:134`) | Gate order matches: provenance → semantic → governance |
| `DeterminismClass` D0–D4 | yes | `core_ingest/types.py:33` | `auto_accept_eligible` property restricted to D0/D1 exactly as the ADR's rationale requires |
| `ReviewLevel` | yes | `core_ingest/types.py:58` | 4 levels, matches |
| `LearningArtifact` | yes | `core_ingest/types.py:300` | Carries packet + `ValidationResult`, neither mutated |
| `StructuralSegmenter` | yes | `core_ingest/segmenter.py:52` | `prose`/`scripture`/`code`/`math` sub-segmenters, all regex/byte-offset based, D0 by construction |
| `SegmentManifold` | yes | `core_ingest/manifold.py:46` | Append-only `semantic_key → ManifoldEntry` index |
| LLM extraction genuinely absent | confirmed absent | — | grep across `core_ingest/`, `ingest/` for any LLM/external-API call: none found; `core_ingest/pipeline.py:21` states this as a design constraint in its own docstring |

**Build axis: full** — every artifact named in §1 exists under the exact names claimed, with behavior matching the ADR's description; the negative claim (no LLM) is also confirmed by its absence in the code.

### 3. Liveness / integration

- `ingest/gate.py::inject` (the transient path this ADR references but does not itself define) is confirmed live: imported directly by `chat/runtime.py:112`, `core/cognition/pipeline.py:1011`, `core/cli.py:495`, and `session/context.py:22`.
- The artifacts this ADR actually introduces (`StructuralSegmenter`, `CandidateGeometricPressure`, `IngestCompiler`, `SegmentManifold`, ported into `core_ingest/` per ADR-0012) are **not** reached from the live chat-serving call chain at all. They are reached by: (a) `core/cli_ingest.py`, an operator-facing CLI (`from core_ingest import IngestPipeline, ...`) — a real, non-test caller, invoked by a human operator, not by a request; and (b) `packs/{en,he,grc,el}/lift_rules.py` → `packs/common/validator.py::_gate_lift`, the pack-authoring validation gate — again a real, non-test caller, but a build/QA-time one, not request-time.
- **Sabotage test:** if `core_ingest/` (this ADR's actual deliverable) were deleted, a live chat turn would be completely unaffected — `chat/runtime.py` and `core/cognition/pipeline.py` never import it. The `core ingest` CLI command and the pack-validation `_gate_lift` check would break immediately. This is the intended disposition per the ADR's own "dual-path architecture" clause, not a defect — but it means the artifact is genuinely exercised only off the hot path.
- **Liveness axis: wired-but-unreached** (from live serving) — with the caveat that "unreached" here means "not on the request path by design," not "orphaned": it has real operator/build-time callers and its own 7-file test suite (`tests/test_core_ingest.py`, `test_compiler.py`, `test_manifold.py`, `test_pipeline.py`, `test_segmenter.py`, `test_determinism_proofs.py`, `test_architectural_invariants.py`).

### 4. Design fidelity — pillars and axioms

| Pillar | Honors / Tension / Violates | Citation (ADR clause + pillar text) |
|---|---|---|
| I. Mechanical Sympathy | Honors | "Structural segmentation is deterministic and model-free" — regex/byte-offset carving at the one normalization site is cheap and machine-legible, no inference cost |
| II. Semantic Rigor | Honors | "An LLM doesn't parse — it interprets... violates Semantic Rigor (we own our semantics)" |
| III. Third Door | Honors | Rejects both visible options (LLM extraction, general NLP library) — "External libraries define the semantics. Third Door." — and builds the deterministic form-segmenter instead |

| Axiom | Honors / Tension / Violates | Citation |
|---|---|---|
| 1. Geometry-First | Honors | "Interpretation happens inside the field during propagation, not before injection" — defers all semantic structure-finding to the field, not the boundary |
| 2. Field-State | Honors | Packets are proposed evidence, not direct field mutation; the field remains the sole state-bearer |
| 3. Propagation-over-Mutation | Honors | "incoming claims don't modify state; they are proposed, validated, and either accepted... or rejected with a full audit trail" (ADR's own Rationale) |
| 4. Dual-Correction | n/a | ADR-0002 does not itself specify a corrective/conjugate operator for a rejected packet; see ADR-0012 |
| 5. Reconstruction-over-Storage | Honors | "the `SegmentManifold` stores enough structured state to trace any vault recall back to its exact source provenance span without storing full document copies" |
| 6. Compilation-Last | n/a | No compilation-target decision made at this ADR's level (see ADR-0012's Rust backend) |
| 7. Reality-over-Inheritance | Honors | Explicitly discards the inherited `core-ai` LLM design on structural merit rather than porting it wholesale |

### 5. Build fidelity — does the code match the decision?

Matches cleanly. Every named artifact exists with the described shape and behavior; the dual-path separation is enforced in code (`core_ingest/compiler.py` and `pipeline.py` both assert in their own docstrings that `ingest/gate.py` is never imported); the D0/D1-only `AUTO_ACCEPT_ELIGIBLE` invariant is enforced structurally in `CandidateGeometricPressure.__post_init__` exactly as the ADR's Consequences section promises ("Forbidden... the `__post_init__` invariant... makes this structurally impossible"). The only addition beyond the ADR's text is `core_ingest/pressure.py`'s optional Rust backend (`core_ingest_rs`) with a transparent pure-Python fallback — an unremarked but axiom-consistent (Compilation-Last) extension, not a contradiction.

**Build-fidelity axis: matches** — no drift found.

### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs

- Consistent with `docs/Whitepaper.md` §VIII ("The Ingest Governance Layer" — restates the LLM rejection and `StructuralSegmenter` verbatim) and `docs/Yellowpaper.md` §VII ("The `core_ingest` Governance Layer — Pre-Gate Specification", explicitly citing ADR-0012). No contradiction found in either formal anchor.
- **Superseded cleanly by ADR-0012**, per ADR-0012's own header ("Supersedes: ADR-0002 (Ingest Layer Design — original)"). ADR-0012 fully absorbs and extends this decision (adding the concrete `IngestCompiler`/gate mechanics) without reversing anything ADR-0002 decided — the two form one continuous arc, audited together in this card.
- No contradiction with any other ADR found.
- **Continuity axis: superseded-cleanly** (by ADR-0012, same decision arc, no reversal).

### 7. Necessity / generality

1. **Necessity:** Irreducible. Some boundary must exist between untrusted external bytes and the field; `StructuralSegmenter`'s job (byte/regex-level form-boundary carving per modality) is not performed by anything at L0/L1 (algebra/field layer) — those layers have no concept of "document," "verse," or "code fence."
2. **Reducibility:** No existing L0/L1 operator does form-boundary segmentation; not reducible.
3. **Extensibility:** None found within this ADR's own scope beyond its already-realized absorption into ADR-0012.

**Necessity/generality axis: irreducible.**

### 8. Fitness / value

- `docs/assessment/10-layer-cards/M2-afferent-boundary.md` confirms `inject` (the transient path, established independent of this ADR) is "the live serving entry" with a would-fail-if-absent citation to `chat/runtime.py:115`.
- `docs/PROGRESS.md` records issue #300 ("`ingest/gate.py` versor_condition margin") — evidence the transient path is genuinely monitored and exercised in production — but this issue concerns `ingest/gate.py`, not the `core_ingest/` artifacts this ADR itself introduces.
- No `evals/obligation_*/` suite, gap-register entry, or PROGRESS.md line was found measuring `core_ingest/`'s own governed path delivering an end-to-end outcome (e.g. a pack actually promoted through `IngestCompiler` into production vocabulary). Its exercised value found is confined to: its own test suite (structural correctness) and its role as the pack-authoring QA gate (`packs/common/validator.py::_gate_lift`).
- **Fitness axis: partial** — structurally correct and used as a build-time QA gate (cited above), but **no evidence found** of the durable/governed ingest lane delivering a measured production outcome beyond its own tests and the pack-validation gate.

### 9. Findings raised

- 🟢 AA-B1-1 — ADR-0002's central decision (reject LLM extraction, replace with deterministic `StructuralSegmenter`) is fully and cleanly built with zero drift; no LLM, external API, or nondeterministic instrument found anywhere in `core_ingest/` or `ingest/`. See §2, §5.

### 10. Evidence sources actually consulted

- `docs/adr/ADR-0002-ingest-layer-design.md` (full text), `docs/adr/ADR-0012-core-ingest-governance-layer.md` (full text, for the Supersedes relation)
- `docs/assessment/10-layer-cards/M2-afferent-boundary.md`, `docs/assessment/30-gap-register.md`, `docs/assessment/31-hindrance-audit.md`
- `docs/Whitepaper.md` §VIII, `docs/Yellowpaper.md` §VII
- `docs/PROGRESS.md` (grep for `ingest`/`sensorium`)
- Code (read in full or targeted excerpt): `ingest/gate.py`, `ingest/__init__.py`, `core_ingest/__init__.py`, `core_ingest/types.py`, `core_ingest/segmenter.py`, `core_ingest/compiler.py`, `core_ingest/manifold.py`, `core_ingest/pipeline.py`, `core_ingest/pressure.py`, `core/cli_ingest.py`, `packs/common/runtime_rules.py`, `packs/common/validator.py`
- Repo-wide grep for importers of `ingest.gate` / `core_ingest` (production vs. test-only) and for any LLM/external-model reference inside the ingest boundary
- `docs/adr-audit/01-adr-census.md`, `docs/adr-audit/02-stack-taxonomy.md`

---

## ADR-0012 — `core_ingest` Governance Layer

**Audit ID (if a numbering collision):** — | **Family (if phased):** —
**Zone / stack:** B1 — Ingest & Multimodal Boundary (M2) | **Tier:** B
**ADR status (as recorded in the file):** Accepted | **ADR date:** 2026-05-13 | **Supersedes:** ADR-0002
**Card author:** Claude | **`verified_at` SHA:** `cbfc8ccb`

---

### 1. Content summary

- **Decision made:** Add a `core_ingest/` layer upstream of `ingest/gate.py` (the gate itself is not modified). Every surface source is carved by a deterministic `StructuralSegmenter` (D0), lifted into a `CandidateGeometricPressure` envelope carrying provenance, a `DeterminismClass`, confidence/uncertainty, and content-addressed `pressure_id`/`semantic_key`. A D2–D4 frontend is structurally forbidden from claiming `AUTO_ACCEPT_ELIGIBLE`. Packets pass through a three-gate `IngestCompiler` (Provenance → Semantic → Governance) producing a `ValidationReport` and, for accepted packets, `LearningArtifact` exports; a `SegmentManifold` indexes `semantic_key → source position` for reconstruction.
- **Alternatives explicitly rejected:** LLM extraction (D3 oracle, semantic projections silently embedded); rule-based NLP pipelines (spaCy/stanza — "parse content, not form... still semantic projections"); no pre-gate layer at all ("no provenance tracking, no governance disposition").
- **Artifacts the ADR claims will exist:**
  - `StructuralSegmenter` (D0 extraction)
  - `CandidateGeometricPressure` (with `kind`, `modality`, `provenance`, `frontend_trace`, `confidence`/`uncertainty`, `payload_json`, `pressure_id`, `semantic_key`)
  - `DeterminismClass` (D0–D4) with the auto-accept table
  - `ReviewLevel` (`AUTO_REJECT`/`AUTO_ACCEPT_ELIGIBLE`/`OPERATOR_REVIEW_REQUIRED`/`ARCHITECT_REVIEW_REQUIRED`)
  - `IngestCompiler` with `ProvenanceGate` → `SemanticGate` → `GovernanceGate` → `ValidationReport` → `LearningArtifact`
  - `SegmentManifold`

### 2. Implementation cross-reference

| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `StructuralSegmenter` (D0) | yes | `core_ingest/segmenter.py:52` | Matches exactly |
| `CandidateGeometricPressure` fields | yes | `core_ingest/types.py:119–246` | Every field named in the ADR present, including `pressure_id`/`semantic_key` computed in `__post_init__` |
| `DeterminismClass` table (D0–D4, auto-accept D0/D1 only) | yes | `core_ingest/types.py:33–55` | `auto_accept_eligible` property matches the ADR's table exactly |
| `ReviewLevel` (4 values) | yes | `core_ingest/types.py:58–62` | Matches |
| D2–D4 forbidden from `AUTO_ACCEPT_ELIGIBLE`, enforced at construction | yes | `core_ingest/types.py:199–208` (`__post_init__`) | Raises `ValueError` — cannot be bypassed at construction, as claimed |
| `IngestCompiler` 3-gate pipeline | yes | `core_ingest/compiler.py:48` (`ProvenanceGate`), `:77` (`SemanticGate`), `:134` (`GovernanceGate`), `:196` (`IngestCompiler`) | Sequential order matches; a failed gate short-circuits, matching "does not proceed" |
| `ValidationReport` (not a transformed copy) | yes | `core_ingest/types.py:278–296` | References packets by `pressure_id`; original packet untouched |
| `SegmentManifold` (semantic_key → position) | yes | `core_ingest/manifold.py:46` | Append-only, matches |
| `ingest/gate.py` unmodified | confirmed | `core_ingest/compiler.py:22`, `core_ingest/pipeline.py:24` | Both modules explicitly state (and structurally enforce by omission) that the gate is never imported |

**Build axis: full** — every claimed artifact and invariant verified in code, byte-for-byte consistent with the ADR's own code sketches.

### 3. Liveness / integration

- Same disposition as ADR-0002 (this ADR is the concrete mechanics of that decision): reached by `core/cli_ingest.py` (operator CLI) and `packs/{en,he,grc,el}/lift_rules.py` → `packs/common/validator.py::_gate_lift` (pack-authoring QA gate) — both real, non-test, non-request-path callers.
- **Not** imported by `chat/runtime.py` or `core/cognition/pipeline.py`.
- **Sabotage test:** removing `core_ingest/` changes nothing observable in a live chat turn. It would break `core ingest` CLI invocations and the pack-validation `_gate_lift` check — both genuinely exercised, neither on the serving hot path.
- **Liveness axis: wired-but-unreached** (from live serving), with real operator/build-time callers and a 7-file dedicated test suite — see ADR-0002 §3 for the identical evidence (this is one mechanism, audited across two ADRs).

### 4. Design fidelity — pillars and axioms

| Pillar | Honors / Tension / Violates | Citation |
|---|---|---|
| I. Mechanical Sympathy | Honors | Three-gate pipeline is pure dataclass/string logic; the Rust backend (`core_ingest_rs`) was added as a compilation target without changing the data model, per `core_ingest/pressure.py`'s own docstring |
| II. Semantic Rigor | Honors | `DeterminismClass`/`ReviewLevel` make trust levels explicit and type-enforced, not convention-based: "enforced in `CandidateGeometricPressure.__post_init__` — it cannot be bypassed at construction time" |
| III. Third Door | Honors | Rejects both "LLM extraction with human review" and "rule-based NLP pipelines" as still importing external semantics; builds the D0 form-segmenter + three-gate compiler instead |

| Axiom | Honors / Tension / Violates | Citation |
|---|---|---|
| 1. Geometry-First | n/a | Pre-field governance boundary; no intrinsic-space claim made here |
| 2. Field-State | Honors | Packets are typed evidence proposals, never a direct field mutation |
| 3. Propagation-over-Mutation | Honors | "The compiler produces a `ValidationReport` alongside the original immutable packet. It does not store a transformed copy — `Reconstruction-over-Storage` is observed" (ADR's own text, also serves this axiom) |
| 4. Dual-Correction | Tension | The ADR names a forward gate sequence but no designed corrective/conjugate operator for a rejected packet — `ReviewDecision` exists as a governance override, but it is an escape hatch authorized by an operator, not a structural inverse of the gate check |
| 5. Reconstruction-over-Storage | Honors | `SegmentManifold` extends this explicitly to the pre-injection layer, per the ADR's own §"SegmentManifold" |
| 6. Compilation-Last | Honors | `core_ingest/pressure.py:12`: "The Rust path is a compilation target chosen after the data model was locked — Axiom 6, Compilation-Last" (explicit self-citation in code, verified) |
| 7. Reality-over-Inheritance | Honors | Supersedes ADR-0002/the inherited `core-ai` design on structural merit, not convenience |

### 5. Build fidelity — does the code match the decision?

Matches, with one notable *positive* extension and one governance-consistency point worth recording: (1) the Rust acceleration path in `core_ingest/pressure.py` is unlisted in the ADR but is axiom-consistent and behavior-preserving (identical fallback); (2) the `GovernanceGate` in code (`core_ingest/compiler.py:134`) adds an `energy_class_hint == "E4"` special case requiring `ARCHITECT_REVIEW_REQUIRED` that is not mentioned in the ADR text — a reasonable governance tightening, not a contradiction, but worth noting as build-time elaboration beyond the decision record.

**Build-fidelity axis: matches** (with the two elaborations noted above, neither contradicting the decision).

### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs

- Matches `docs/Whitepaper.md` §VIII and `docs/Yellowpaper.md` §VII almost verbatim (both documents restate the three-gate pipeline, the D-class table, and the `StructuralSegmenter` rationale using the same names this ADR defines).
- Explicitly **supersedes ADR-0002** (declared in its own header) — audited together above; no reversal, pure extension.
- No contradiction found with any other ADR.
- **Continuity axis: clean.**

### 7. Necessity / generality

1. **Necessity:** The boundary itself (some gate must exist between proposed evidence and accepted claim) is irreducible. But the *specific* trust-taxonomy this ADR builds — `DeterminismClass`/`ReviewLevel` grading a claim's admissibility before it is trusted — functionally overlaps with the Epistemic Grade Policy (ADR-0021, zone A3: SPECULATIVE/COHERENT status) audited elsewhere in this corpus. Both mechanisms grade evidentiary trust of a claim before treating it as ground truth, using independently-invented category schemes.
2. **Reducibility:** Not reducible to an L0/L1 algebra/field operator (this is a governance/provenance concern, not a geometric one). But it may be reducible to — or worth unifying with — ADR-0021's epistemic grading regime; this card does not have the evidence to call which subsumes which, only that the pairing is worth checking.
3. **Extensibility:** Flagging the `DeterminismClass`/`ReviewLevel` ↔ Epistemic Grade Policy pairing as a candidate for `22-consolidation-report.md`.

**Necessity/generality axis: generalization-candidate** (paired with ADR-0021's SPECULATIVE/COHERENT epistemic-grade regime — not independently verified in this card; flagged for the consolidation pass).

### 8. Fitness / value

- `packs/common/validator.py::_gate_lift` is a genuine, non-test consumer: every language pack's `lift_rules.py` is exercised through `IngestCompiler`-adjacent `CandidateGeometricPressure` construction as part of pack QA — measurable use, though scoped to build-time validation, not runtime serving.
- No `evals/obligation_*/` suite or `docs/PROGRESS.md` entry found crediting `core_ingest/`'s governed path with a specific measured production outcome (e.g., a `LearningArtifact` that was actually promoted into served vocabulary through this exact pipeline, as opposed to through the pack build process directly).
- **Fitness axis: partial** — real build-time QA usage cited above; **no evidence found** of end-to-end measured production value for the governed ingest lane as such.

### 9. Findings raised

- 🔵 AA-B1-5 — `DeterminismClass`/`ReviewLevel` (this ADR) and the Epistemic Grade Policy's SPECULATIVE/COHERENT regime (ADR-0021, zone A3) both grade a claim's trustworthiness before admission; flagged as a cross-zone consolidation candidate for `22-consolidation-report.md`. See §7.

### 10. Evidence sources actually consulted

Same as ADR-0002 §10, plus: `core_ingest/compiler.py` (`GovernanceGate.check`'s `energy_class_hint` special case), a repo-wide grep confirming `packs/common/validator.py` and `packs/{en,he,grc,el}/lift_rules.py` are the only non-test, non-CLI production callers of `core_ingest.types.CandidateGeometricPressure`.

---

## ADR-0013 — `sensorium/` Multimodal Protocol Layer

**Audit ID (if a numbering collision):** — | **Family (if phased):** —
**Zone / stack:** B1 — Ingest & Multimodal Boundary (M2) | **Tier:** B
**ADR status (as recorded in the file):** Accepted | **ADR date:** 2026-05-13
**Card author:** Claude | **`verified_at` SHA:** `cbfc8ccb`

---

### 1. Content summary

- **Decision made:** Add a `sensorium/` layer that converts **any** surface signal (text included) into a `(32,)` Cl(4,1) multivector *before* it reaches `core_ingest/` or `ingest/gate.py` — neither of which is modified. Every `ProjectionHead` is "the Logos-recovery boundary" for its modality; once a signal crosses it, the field has no concept of modality, so there is no multimodal-fusion problem. Ports the *protocol shape* (`ModalityPack`, `ProjectionHead`, `SurfaceDecoder`, `ModalityVocabulary`) from `core-ai/core_sensorium`, but re-targets the output geometry from `core-ai`'s `Cl(3,0)`/`(2,2)` complex (Pauli) representation to CORE's own `Cl(4,1)`/`(32,)` f32. Text (`en`/`he`/`grc`) is "Active"; vision/audio/motor are listed as "Planned."
- **Alternatives explicitly rejected:** separate pipelines per modality with late fusion ("creates a fusion problem that doesn't exist... violates Third Door"); modality-specific field spaces merged at generation time ("severs the relational geometry... the same mistake RAG makes with text").
- **Artifacts the ADR claims will exist:**
  - `ModalityPack[S]` (frozen, slotted generic dataclass)
  - `ProjectionHead[S, F]` protocol (`project`, `project_batch`, `verify_unitarity`)
  - `SurfaceDecoder[S]` (optional inverse)
  - `ModalityVocabulary[S]` (bidirectional surface ↔ point map)
  - Grammar scaffold universality (shared attractor geometry across modalities)
  - Modality status table: TEXT (en/he/grc) Active; VISION/AUDIO/MOTOR Planned
  - "Adding a modality" 3-step recipe (adapter file, registry entry, mount-time check)

### 2. Implementation cross-reference

| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `ModalityPack[S]` | yes | `sensorium/protocol.py:184` | Matches the ADR's sketch field-for-field, plus later additions (`language_role`, `oov_policy` — not in the original ADR sketch, added by later work; consistent extension) |
| `ProjectionHead[S, F]` protocol | yes | `sensorium/protocol.py:50` | `project`/`project_batch`/`verify_unitarity` all present, `embedding_dim` must equal `CL41_DIM=32` |
| `SurfaceDecoder[S]` | yes | `sensorium/protocol.py:68` | Matches |
| `ModalityVocabulary[S]` | yes | `sensorium/protocol.py:136` | Bidirectional map, matches |
| Registry / mount point | yes | `sensorium/registry.py:27` (`ModalityRegistry`) | `mount()` runs the unitarity check at mount time only, as the ADR requires ("never in the propagation hot path") |
| Grammar scaffold field | yes | `sensorium/protocol.py:208` (`grammar_scaffold: Any`) | Present in the dataclass; not independently exercised in this card's evidence |
| Text adapters (`en`/`he`/`grc`) — "Active" | yes, but **not on the live serving path** | `sensorium/adapters/text.py:44` (`TextProjectionHead`), `:133` (`make_text_pack`), `:175–213` (`english_pack`/`hebrew_pack`/`koine_greek_pack`) | Built and tested, but the live chat text path (`chat/runtime.py`, `core/cognition/pipeline.py`, `session/context.py`) never calls `sensorium.registry` or `sensorium.adapters.text` — see §3 and §5 |
| Vision adapter — ADR table says "Planned" | **yes, built** — contradicts the ADR's own status table | `sensorium/adapters/vision.py` (`VisionProjectionHead`, `make_vision_pack`), backed by `sensorium/vision/` (11 files: `compiler.py`, `lexer.py`, `parser.py`, `operators.py`, `arena.py`, `canonical.py`, `checksum.py`, `grid.py`, `trace.py`, `types.py`) | Real geometric compiler (own lexer/parser/operator pipeline over `VisionTileSignal → versor`), tested (`tests/test_vision_sensorium_mount.py`, `test_vision_eval_gates.py`), mounts with `gate_engaged=False` by default |
| Audio adapter — ADR table says "Planned" | **yes, built** — contradicts the ADR's own status table | `sensorium/adapters/audio.py` (`AudioProjectionHead`, per ADR-0181), backed by `sensorium/audio/` (12 files) | Same shape: real compiler, D1 determinism class, `gate_engaged=False` "until the eval gates (PR-4) pass" per its own docstring |
| Motor adapter — ADR table says "Planned" | **partial** — matches the ADR's own status | `sensorium/protocol.py:46` (`Modality.MOTOR` enum member exists), no `sensorium/adapters/motor.py` | ADR-0198 ("Motor as Efferent Modality — Design Spike") confirms: "the §3 verdict-lowering and the motor compiler/decoder remain deferred" — Planned is still accurate for motor specifically |

**Build axis: partial** — the protocol/registry abstraction is fully built and, for vision/audio, substantially over-built relative to the ADR's own status table (which the ADR itself has not been amended to reflect); but the one modality the ADR calls "Active," text, is not actually reached through this abstraction in production — see §3/§5.

### 3. Liveness / integration

- Confirmed by repo-wide grep: `sensorium` is imported by neither `chat/runtime.py` nor `core/cognition/pipeline.py` nor `session/context.py`. Every non-test importer of `sensorium.*` is either inside `sensorium/` itself, an `evals/*_sensorium/*` offline eval-report script, or a test file — with one exception, `scripts/run_pulse.py`, which imports only the standalone `deterministic_hash_versor` helper from `sensorium/adapters/text.py` (a hash-to-versor stub for testing, not the `ModalityPack`/`ModalityRegistry` path).
- **Sabotage test:** deleting `sensorium/` entirely changes no observable behavior of a live chat turn — `chat/runtime.py`'s text-injection path runs entirely through `ingest/gate.py::inject`'s own independent OOV-grounding logic (`_lookup_or_ground`/`_ground_unknown_token`, keyed on a `vocab` object with `get_versor`/`insert_transient`), never through `sensorium.registry.ModalityRegistry` or `sensorium.adapters.text.TextProjectionHead` (keyed on a distinct `ModalityVocabulary` with `get_point`). This is a decoration finding for the "Active" text lane specifically: the mechanism the ADR names as the live path for text is not, in fact, in the live path.
- The vision/audio/sensorimotor adapters are exercised — by their own mount tests and by `evals/sensorium/report.py` + `evals/{vision,audio,event_vision,sensorimotor}_sensorium/*` — but only in an offline eval-harness context, never from a live request.
- Per `docs/assessment/30-gap-register.md`'s PIN 3 note: the `sensorium` test suite (21 files, confirmed by the M2 layer card) is registered curated-suite membership but is **not gate-reachable** — `sensorium` is explicitly named among the suites "in the unreachable set — they have members, and no gate calls them" (pre-push runs only `smoke` + `deductive`). So "the suite runs" should be read as "runs when manually or post-merge invoked," not "runs on every push."
- **Liveness axis: wired-but-unreached** — for all of text (bypassed by design-turned-drift), vision, audio, and sensorimotor. Motor remains genuinely absent (no adapter). None of the four is dead code (all have real mount-time tests and, for vision/audio, real geometric compilers), but none reaches a live conversation turn.

### 4. Design fidelity — pillars and axioms

| Pillar | Honors / Tension / Violates | Citation |
|---|---|---|
| I. Mechanical Sympathy | Tension | The design is machine-sympathetic on paper (one shared 32-float boundary, unitarity checked only at mount time, never in the hot path) — but in production the live text path runs its own separate, non-unified grounding mechanism (`ingest/gate.py`), so the "one boundary" the machine actually executes is not the one this ADR built |
| II. Semantic Rigor | Tension | The `ProjectionHead` protocol enforces one precise meaning for "signal → versor" per modality by construction — but two independent, non-reconciled implementations of that exact mapping exist for text (`ingest/gate.py`'s morphological OOV grounding vs. `sensorium/adapters/text.py`'s `TextProjectionHead`), which can diverge on the same token; see §5, AA-B1-2 |
| III. Third Door | Honors | Explicitly rejects "separate pipelines per modality with late fusion" (the industry standard) and "modality-specific field spaces" (the RAG mistake), building the single-manifold-via-projection-boundary alternative instead |

| Axiom | Honors / Tension / Violates | Citation |
|---|---|---|
| 1. Geometry-First | Honors | "There is one space. There is no multimodal fusion problem because there is nothing to fuse" — finds the intrinsic Cl(4,1) space before choosing any modality-specific structure |
| 2. Field-State | Honors | Once projected, every modality is a point in the same field; no modality-tagged object survives past the boundary |
| 3. Propagation-over-Mutation | Honors | Grammar-scaffold universality: the same attractor structure propagates for every modality rather than being mutated per-modality |
| 4. Dual-Correction | Honors | `SurfaceDecoder` is the explicit corrective/conjugate counterpart to `ProjectionHead` (decode as project's inverse); implemented for text (`TextSurfaceDecoder`) and exercised via roundtrip trace modules for vision/audio (`sensorium/vision/trace.py`, `sensorium/audio/trace.py`) |
| 5. Reconstruction-over-Storage | n/a | Not this ADR's concern (that is `core_ingest/`'s `SegmentManifold`, ADR-0012) |
| 6. Compilation-Last | Honors | The protocol shape (`ModalityPack`/`ProjectionHead`) was ported unchanged while the compilation target (output geometry) was re-derived from `core-ai`'s `Cl(3,0)`/`(2,2)` to CORE's own `Cl(4,1)`/`(32,)` — the shape survived a change in the compiled representation |
| 7. Reality-over-Inheritance | Honors | Explicitly ports only "the protocol shape," not the inherited `core-ai` geometry, re-deriving against CORE's own algebra rather than inheriting Cl(3,0) wholesale |

### 5. Build fidelity — does the code match the decision?

**Partial drift**, on two distinct axes:

1. **Positive over-delivery, undocumented:** vision and audio have real, substantially built `ProjectionHead` implementations (their own lexer/parser/operator/arena/canonical/checksum submodules, 11–12 files each) — the ADR's own status table still reads "Planned" for both, and it has not been amended since ADR-0197 (vision) and ADR-0181 (audio) landed. `docs/assessment/10-layer-cards/M2-afferent-boundary.md` (re-verified `39331dbc`, 2026-07-28) still states "the projection heads do not exist" — that claim is now stale against code; the heads exist, they are simply mount-gated closed (`gate_engaged=False`) pending eval-gate passage, not absent. This is a record/reality divergence per `AGENTS.md`'s Standing Philosophy #5 ("When a record and reality diverge, that is a defect with the same severity as a wrong answer").
2. **The one substantive contradiction:** the decision text says `sensorium/` converts *any* surface signal, text included, "before it reaches `core_ingest/` or `ingest/gate.py`." In production, text does not cross this boundary at all — `chat/runtime.py` calls `ingest.gate.inject` directly, which grounds unknown tokens through its own morphological decomposition logic against a `vocab` object exposing `get_versor`/`insert_transient`/`morphology_entries`. `sensorium/adapters/text.py`'s `TextProjectionHead` grounds tokens through a structurally different `ModalityVocabulary` exposing `get_point`, with much simpler OOV handling (tagged fallback / fail-closed / raise). These are two independent, non-integrated implementations of the same functional slot ("map a text token to a Cl(4,1) versor"), and only one of them — the one this ADR does not define — is actually live.

**Build-fidelity axis: partial drift** — citing the specific divergence above.

### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs

- Matches `docs/Whitepaper.md` §IX ("The Sensorium: All Inputs Are Logos") and `docs/Yellowpaper.md` §VI ("The Sensorium — Modality Protocol Specification") at the doctrinal level — both restate the `ProjectionHead`/Logos-recovery framing and the "before it reaches `ingest/gate.py`" clause verbatim, so the *documented* design is internally consistent across all three formal-anchor-adjacent sources.
- Properly extended by later per-modality ADRs without contradiction: ADR-0181 (audio compiler), ADR-0183 (lawful audio lexeme path), ADR-0197 (vision compiler), ADR-0198 (motor — explicitly still a "design spike," deferred), ADR-0208 (environmental sensorium loop), ADR-0209 (sensorimotor feedback contract), ADR-0210 (L10 grounding pack), ADR-0211 (conformal falsification bench, live-internal per the M2 layer card).
- The unreconciled element is not a document-vs-document contradiction but a document-vs-code one: the ADR (and the Whitepaper/Yellowpaper restating it) describe text as running through `sensorium`; the code does not. No later ADR records this as a deliberate deferral (contrast with `unified_ingest`, ADR-0090, which *is* an explicit flag-gated deferral for a different mechanism).
- **Continuity axis: clean** at the document-citation-graph level (no ADR contradicts another); the build-vs-decision gap is carried in §5, not here.

### 7. Necessity / generality

1. **Necessity:** The `ProjectionHead`/`ModalityPack` abstraction itself is a strong, arguably irreducible instance of Geometry-First — one shared boundary for arbitrary surface signal is the right general primitive, and nothing at L0/L1 already provides "surface signal → field point" for non-numeric modalities.
2. **Reducibility:** The *concrete text implementation* is currently the opposite of irreducible — it is a duplicate. `sensorium/adapters/text.py`'s `TextProjectionHead` occupies the same functional slot as `ingest/gate.py`'s live OOV-grounding logic, with two different vocabulary abstractions and two different OOV policies, unreconciled.
3. **Extensibility:** The natural fix is not "build more" but "unify" — either route `ingest/gate.py`'s live text injection through `sensorium.registry.ModalityRegistry.project("en", ...)` as the ADR's own decision text specifies, or formally retire the `sensorium` text adapter and document `ingest/gate.py` as the permanent, sensorium-bypassing text implementation. Naming this pairing (`ingest/gate.py`'s token grounding ↔ `sensorium/adapters/text.py`'s `TextProjectionHead`) as the consolidation candidate for `22-consolidation-report.md`.

**Necessity/generality axis: generalization-candidate** (the abstraction is sound and irreducible; the text instance under it is a reducible duplicate of the live path — see AA-B1-2).

### 8. Fitness / value

- `docs/assessment/10-layer-cards/M2-afferent-boundary.md`: "59 modules of afferent machinery reach no serving path, which is the largest quantity of built-and-disconnected code the assessment has located." This card's own evidence (§2, §3) corroborates that figure and adds the specific text-duplication mechanism behind part of it.
- `docs/assessment/30-gap-register.md` G-17 ("Non-text ingest"): "59 sensorium modules, no serving path, no entry criterion; projection heads do not exist" — this card's evidence shows the "do not exist" clause is now inaccurate for vision/audio (they exist, gate-closed) though accurate for motor.
- `docs/PROGRESS.md`: "Embodiment (sensorium gates) | Open | Phase 5" — recorded as an explicitly open, not-yet-committed scope decision as of that entry, consistent with the current gated-off disposition.
- `evals/sensorium/report.py` and the per-modality eval directories (`evals/{vision,audio,event_vision,sensorimotor}_sensorium/`) demonstrate the vision/audio/sensorimotor `ProjectionHead`s pass their own mount and eval-gate checks in isolation — measurable correctness of the built mechanism, but entirely within the offline eval harness, never contributing to a served chat outcome.
- **Fitness axis:** partial — isolated correctness is measured and cited above; **no evidence found** of any `sensorium` artifact (text, vision, audio, or sensorimotor) contributing to a live, measured chat-serving outcome.

### 9. Findings raised

- 🟡 AA-B1-2 — `sensorium/adapters/text.py`'s `TextProjectionHead` and `ingest/gate.py`'s own OOV-grounding logic are two independent, non-integrated implementations of "text token → Cl(4,1) versor," using different vocabulary abstractions (`ModalityVocabulary.get_point` vs. `vocab.get_versor`/`insert_transient`) and different OOV policies. Only `ingest/gate.py`'s version is live. This directly contradicts ADR-0013's decision that `sensorium/` sits upstream of `ingest/gate.py` for every modality including the one it calls "Active." See §3, §5, §7.
- 🟡 AA-B1-3 — ADR-0013's own status table ("Vision/Audio/Motor: Planned") and `docs/assessment/10-layer-cards/M2-afferent-boundary.md`'s claim that "the projection heads do not exist" are both stale against code: `VisionProjectionHead` and `AudioProjectionHead` are built, tested, and geometrically substantive (own compiler/lexer/parser/arena submodules), just mount-gated closed pending eval-gate passage. Record/reality divergence per `AGENTS.md` Standing Philosophy #5. See §2, §5, §8.
- 🟢 AA-B1-4 — The `sensorium` test suite (21 files) is real and passing but is one of the 19 curated suites confirmed **not gate-reachable** by `docs/assessment/30-gap-register.md`'s PIN 3 (`tests/test_suite_reachability.py`); "the suite runs" should be read as "runs when manually/post-merge invoked," not "on every push." Already tracked by the gap register; recorded here for cross-reference, not as a new gap. See §3.

### 10. Evidence sources actually consulted

- `docs/adr/ADR-0013-sensorium-multimodal-protocol.md` (full text), `docs/adr/ADR-0181-audio-compiler-delta-crdt.md`, `docs/adr/ADR-0197-vision-compiler-delta-crdt.md`, `docs/adr/ADR-0198-motor-efferent-decoder-spike.md` (headers/status only, for the continuity check)
- `docs/assessment/10-layer-cards/M2-afferent-boundary.md`, `docs/assessment/30-gap-register.md` (G-17, PIN 3), `docs/assessment/31-hindrance-audit.md`
- `docs/Whitepaper.md` §IX, `docs/Yellowpaper.md` §VI
- `docs/PROGRESS.md`
- Code: `sensorium/protocol.py`, `sensorium/registry.py`, `sensorium/adapters/text.py` (full), `sensorium/adapters/vision.py`, `sensorium/adapters/audio.py`, `sensorium/adapters/sensorimotor.py` (headers + key methods), `sensorium/vision/compiler.py` (excerpt), `ingest/gate.py` (full, for the duplicate-grounding comparison), `chat/runtime.py` (import lines + `unified_ingest` branch), `core/cognition/pipeline.py:1011`, `session/context.py:22`, `scripts/run_pulse.py` (grep)
- Repo-wide grep for every non-test importer of `sensorium.*`, and for callers of `english_pack`/`hebrew_pack`/`koine_greek_pack`
- `tests/test_suite_reachability.py` (grep, for the PIN 3 cross-reference)

---

## Zone findings (rollup)

- 🟢 **AA-B1-1** — ADR-0002's core decision (reject LLM extraction, replace with deterministic `StructuralSegmenter`) is fully and cleanly built with zero drift. *(ADR-0002 §2, §5)*
- 🟡 **AA-B1-2** — `sensorium/adapters/text.py`'s `TextProjectionHead` duplicates, rather than replaces, `ingest/gate.py`'s live text-grounding logic; only the latter is on the serving path, contradicting ADR-0013's own "before it reaches `ingest/gate.py`, for every modality" decision. *(ADR-0013 §3, §5, §7)*
- 🟡 **AA-B1-3** — ADR-0013's status table and the M2 assessment layer card both understate what is actually built for vision/audio (`ProjectionHead`s exist, gate-closed) — a record/reality divergence, not just a documentation nit. *(ADR-0013 §2, §5, §8)*
- 🟢 **AA-B1-4** — The `sensorium` test suite exists and passes but is not gate-reachable per the assessment's PIN 3; cross-referenced, not a new gap. *(ADR-0013 §3)*
- 🔵 **AA-B1-5** — `DeterminismClass`/`ReviewLevel` (ADR-0012) and ADR-0021's Epistemic Grade Policy both grade a claim's trust before admission; flagged as a consolidation-report candidate pairing, not independently verified in this card. *(ADR-0012 §7)*

**Finding count: 5** (2 🟡 Repair, 2 🟢 Monitor, 1 🔵 Consolidate; 0 🔴 Block).
