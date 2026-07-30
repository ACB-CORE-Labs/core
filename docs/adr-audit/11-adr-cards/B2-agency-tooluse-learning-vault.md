# B2 — Agency, Tool Use, Learning Loop & Vault

**Tier:** B · **Macro layers:** M3 (Comprehension & Reasoning) / M5 (Learning & Growth) / M1 (Knowledge & Memory) · **Member ADRs:** ADR-0014, ADR-0017, ADR-0018, ADR-0019 · **`verified_at` SHA:** `cbfc8ccbf7fe503ab31abe7aedbb1973ba7d7b4d` · **Card author:** ADR-Audit subagent (Tier B, Batch 1)

This zone is a phased bundle of four 2026-05-13/05-16 scope decisions that together answer: does CORE learn, does it act with initiative, does it use tools, and can its memory recall fast enough to serve. The four turn out to split cleanly into two very different outcomes. ADR-0017 and ADR-0018 (agency scope, tool-use scope) are same-week companion ADRs that shipped a real, evidenced capability — the `transitive_walk`/`multi_relation_walk`/`compose_relations` operator family closed the inference-closure, multi-step-reasoning, and compositionality eval lanes from a hard `0.0` to `1.0` pass rate — but ADR-0017's own defining claim (axiology as an in-turn candidate-selection gradient) and one of ADR-0018's two named operators (`path_recall`) never landed. ADR-0019 (vault recall acceleration) is the standout: Stage 1 shipped exactly as decided, is bit-identical to the scalar reference by pinned test, and is backed by a directly measured ~4,000–5,000x speedup — genuinely excellent, evidenced engineering, with Stages 2/3 correctly left un-triggered because the gating condition the ADR itself specified was never met. ADR-0014 (`train/` learning loop) is the outlier: the `train/` package it names does not exist anywhere in the repository, its sole upstream artifact (`LearningArtifact`) is produced and then consumed by nothing, and the learning capability CORE actually built (`teaching/`, `formation/`, `reliability_gate/`, `capability/` — M5's real spine, per `docs/assessment/10-layer-cards/M5-learning-growth.md`) never cites ADR-0014 and does not resemble what it specified. The ADR's own status line — "Accepted (Stub)" — has been true, unresolved, and unreconciled since 2026-05-13.

---

# ADR-0014 — `train/` Learning Loop

**Audit ID (if a numbering collision):** — | **Family (if phased):** —
**Zone / stack:** B2 — Agency, Tool Use, Learning Loop & Vault (M3/M5/M1) | **Tier:** B
**ADR status (as recorded in the file):** Accepted (Stub) | **ADR date:** 2026-05-13
**Card author:** ADR-Audit subagent | **`verified_at` SHA:** `cbfc8ccbf7fe503ab31abe7aedbb1973ba7d7b4d`

---

## 1. Content summary

- **Decision made:** add a `train/` layer that receives `LearningArtifact` objects from `core_ingest/` and produces structured field updates (rotor updates, vocabulary-manifold expansions, attractor seeds), under five architectural constraints: no gradient descent on the field, no mutation of existing field state, durable-path-only, a first Supervised Seeding Epoch for Hebrew/Koine Greek depth corpora, and no modification of `ingest/gate.py`.
- **Alternatives explicitly rejected:** none — this ADR records constraints for a not-yet-built layer rather than choosing among named alternatives.
- **Artifacts the ADR claims will exist:**
  - a `train/` package/module
  - a rotor-update mechanism (candidate: geodesic interpolation on the versor manifold)
  - a vocabulary-expansion protocol (null-vector insertion)
  - an attractor-seeding mechanism producing `grammar_scaffold` entries
  - a Supervised Seeding Epoch process with a defined termination condition
  - the `gate_engaged` flag on non-text modality packs, `False` during seeding, `True` after
  - a conflict-resolution rule for competing `LearningArtifact` proposals

## 2. Implementation cross-reference

| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `train/` package | no | — | No such directory or module anywhere in the repository. |
| `LearningArtifact` (producer side) | yes | `core_ingest/types.py:300`, `core_ingest/compiler.py:348` | Real dataclass, really constructed by `IngestCompiler`. |
| `LearningArtifact` (consumer side) | no | — | Grepped repo-wide; only referenced inside `core_ingest/` itself, `core/cli_ingest.py` (prints a report and exits), and tests. No module imports it for a field update. |
| Rotor-update mechanism | no | — | No geodesic-interpolation or rotor-proposal code found anywhere. |
| Vocabulary-expansion protocol | no | — | Vocabulary/pack growth in the live system goes through the formation pipeline (Mine→Smelt→Forge→Compose→Compile→Run→Ratify→Promote, M5), not through `LearningArtifact`. |
| `grammar_scaffold` / attractor seeding | partial | `sensorium/protocol.py:195,208`; `sensorium/adapters/{vision,audio,text,vision_event,sensorimotor}.py` | The field exists on the sensorium packet type, documented as "versor attractor seeds (universal across modalities)" — but every adapter constructs it as `grammar_scaffold=None`. Never populated. |
| `gate_engaged` (Supervised Seeding Epoch flag) | yes (semantics match) | `sensorium/protocol.py:197,212,223,229`; `sensorium/registry.py:103,124,165,197` | Implemented with exactly the described semantics (`False` during seeding, `True` after; `gate_engaged=True` requires `checksum_verified=True`) — but it is a general sensorium-gating primitive, not driven by any Supervised Seeding Epoch tracker, because no such tracker (or `train/`) exists. |
| `GrammarAttractor` type | yes, unrelated | `packs/schema.py:148-163` | A curated, hand-authored pack-schema type ("Structural grammar attractor seeded into the shared manifold") — not the corpus-learned attractor ADR-0014 specifies. |

**Build axis:** ghost — the one artifact this ADR is actually *about* (`train/`, receiving `LearningArtifact` and emitting rotor/vocab/attractor updates) does not exist in any form. The scattered fragments that share its vocabulary (`gate_engaged`, `grammar_scaffold`) are unpopulated infrastructure in an unrelated module (`sensorium/`), not partial construction of the described layer.

## 3. Liveness / integration

- Not reached on the live serving path, and not reached anywhere at all. `core.cli_ingest ingest-compile` is an operator-facing, explicitly read-only diagnostic CLI ("This is read-only: it does not touch the vault or gate") that constructs `LearningArtifact` objects and prints a validation report to stdout, then discards them. There is no code path from there to any field, vault, or pack mutation.
- **Sabotage test:** delete `core_ingest/compiler.py`'s `LearningArtifact` export (or the whole `core_ingest` package) — nothing downstream changes. No test, no eval lane, no serving path, and no other module references it for anything but printing a report. This is a textbook decoration finding, not a minor caveat.
- **Liveness axis:** dead — nothing in the described mechanism runs, and the one piece that does run (the diagnostic CLI) is explicitly documented as a dead end by its own docstring.

## 4. Design fidelity — pillars and axioms

| Pillar | Honors / Tension / Violates | Citation (ADR clause + pillar text) |
|---|---|---|
| I. Mechanical Sympathy | Honors | Constraint 1 forbids gradient descent because it "would break the versor condition and exit the manifold" — the decision is written in terms of what the algebra can and cannot tolerate. |
| II. Semantic Rigor | Honors | The Expected Outputs table gives rotor update / vocab expansion / attractor seed distinct, non-overlapping definitions. |
| III. Third Door | Honors | Rejects both "no learning" and "gradient-descent fine-tuning" (the two visible options for an ML system) in favor of versor-algebraic structural growth. |

| Axiom | Honors / Tension / Violates | Citation |
|---|---|---|
| 1. Geometry-First | Honors | "Updates must be structured as versor products or null vector insertions — algebraically closed operations." |
| 2. Field-State | Honors | Treats learning as a field/manifold-level change (rotor, vocabulary manifold), not object mutation. |
| 3. Propagation-over-Mutation | Honors | Constraint 2, verbatim: "It does not overwrite existing versors. The manifold grows; it does not change in place." |
| 4. Dual-Correction | Tension | No corrective/conjugate counterpart is specified for the forward rotor-update operator (no retraction/undo path is named for a bad `LearningArtifact` proposal that was already promoted). |
| 5. Reconstruction-over-Storage | n/a | Not addressed by this ADR at the decision level. |
| 6. Compilation-Last | n/a | Too architecture-only at this stage to assess a loop/table/kernel-ordering claim. |
| 7. Reality-over-Inheritance | Honors | The entire ADR is written to pre-empt an inherited (gradient-descent) ML paradigm from sneaking in before implementation begins. |

## 5. Build fidelity — does the code match the decision?

Not assessable in the template's normal sense — §2 found `ghost`. There is no implementation to compare against the decision. The only observation available is negative: the fragments that *do* exist under this ADR's vocabulary (`gate_engaged`, `grammar_scaffold`) are unpopulated and belong to `sensorium/`, a module this ADR does not name.

**Build-fidelity axis:** n/a (ghost build — no implementation exists to compare against the decision).

## 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs

- No contradiction with `Whitepaper.md` or `Yellowpaper.md` found — the decision as written is axiom-consistent (§4).
- No later ADR formally supersedes, retires, or reconciles ADR-0014. It is not on the census's phased-family list and no other ADR in the corpus names it as superseded.
- **The record has silently diverged from reality.** CORE's actual learning mechanism — `teaching/`, `formation/`, `core/reliability_gate/`, `core/capability/` (M5, per `docs/assessment/10-layer-cards/M5-learning-growth.md`) — was built, ratified, and evidenced (25 sealed bands, 18,000 cases, `wrong=0`) under a completely different design lineage (ADR-0021, ADR-0057, ADR-0175, ADR-0263, ADR-0262/0264, ADR-0091/0106/0109, ADR-0218). **M5's card does not cite ADR-0014 anywhere.** `docs/audit/substrate-liveness-registry.md` (lines 411, 1288) still lists ADR-0014 as "Accepted (Stub)" belonging at L2/L7 with no update noting the divergence. Per `AGENTS.md`'s Standing Philosophy #5, "when a record and reality diverge, that is a defect with the same severity as a wrong answer" — this is exactly that case, just never flagged.
- **Continuity axis:** unreconciled contradiction — not a contradiction of content, but of *record versus reality*: an unretired, unsuperseded "Accepted (Stub)" ADR sits beside a fully different, independently-built mechanism that answers the same telos need.

## 7. Necessity / generality

1. **Necessity:** the underlying need (a durable, reviewed path from ingested material to standing knowledge) is genuinely necessary — CORE must have some way to grow. But *this ADR's specific construction* (a `train/` package consuming `LearningArtifact`, producing rotor updates) is not what satisfies that need today.
2. **Reducibility:** yes — the need is already fully served by the teaching/formation/reliability-gate/capability pipeline (M5), which is proposal→review→ratify rather than rotor-mechanics, and is live, evidenced, and ratified.
3. **Extensibility:** this is a consolidation candidate, not an extension one: ADR-0014 should either be formally retired/superseded by the ADR-0057/0263 family, or its one genuinely distinct idea — the Hebrew/Koine Supervised Seeding Epoch as a first-class curriculum phase — should be explicitly folded into formation's curriculum stages if still wanted.

**Necessity/generality axis:** reducible-to-M5-teaching/formation-pipeline — the telos need is real; this ADR's construction of it is not what shipped.

## 8. Fitness / value

No evidence found. `docs/assessment/10-layer-cards/M5-learning-growth.md` and `M1-knowledge-memory.md` do not cite ADR-0014. No `evals/` lane references `train/` or `LearningArtifact`. The one live artifact under this ADR's umbrella (`core.cli_ingest`) is explicitly documented as read-only/diagnostic, not a delivery path.

**Fitness axis:** no evidence found.

## 9. Findings raised

- 🟡 **AA-B2-1** — the `train/` layer this ADR specifies was never built; `LearningArtifact` objects are produced by `core_ingest/compiler.py` and consumed by nothing — confirmed dead output. (§2, §3)
- 🟡 **AA-B2-2** — ADR-0014 remains "Accepted (Stub)," uncontradicted and unsuperseded, while the system's actual learning path (M5: teaching/formation/reliability_gate/capability) satisfies the same telos need through an entirely unrelated mechanism that never cites it — record and reality have silently diverged and this needs a ruling (retire, or reconcile). (§6, §7)
- 🟢 **AA-B2-3** — vestigial fragments of ADR-0014's vocabulary (`gate_engaged`, `grammar_scaffold`) survive in `sensorium/` and `packs/schema.py` but are either unpopulated (`grammar_scaffold` is always `None`) or serve a different, curated (not learned) purpose — worth checking whether these are leftovers of an abandoned build attempt. (§2)

## 10. Evidence sources actually consulted

- `docs/adr/ADR-0014-train-learning-loop.md` (full read).
- Repo-wide search for a `train/` directory/module (absent) and for `LearningArtifact` (found only in `core_ingest/`, `core/cli_ingest.py`, tests).
- `core_ingest/__init__.py`, `core_ingest/compiler.py`, `core/cli_ingest.py` (full/partial reads).
- Grep for `grammar_scaffold`, `gate_engaged`, `GrammarAttractor` repo-wide.
- `docs/assessment/10-layer-cards/M5-learning-growth.md` and `M1-knowledge-memory.md` (full reads; no ADR-0014 mention in either).
- `docs/audit/substrate-liveness-registry.md` (grep for ADR-0014 rows).
- `docs/assessment/30-gap-register.md`, `31-hindrance-audit.md` (grepped for `train/`/agency/tool-use/vault terms — no hits).

---

# ADR-0017 — Agency Scope: Responsive-with-Axiology

**Audit ID (if a numbering collision):** — | **Family (if phased):** —
**Zone / stack:** B2 — Agency, Tool Use, Learning Loop & Vault (M3/M5/M1) | **Tier:** B
**ADR status (as recorded in the file):** Accepted | **ADR date:** 2026-05-16
**Card author:** ADR-Audit subagent | **`verified_at` SHA:** `cbfc8ccbf7fe503ab31abe7aedbb1973ba7d7b4d`

---

## 1. Content summary

- **Decision made:** CORE is "responsive-with-axiology" — every cognitive turn is externally triggered (no background loop, no autonomous initiative), but the `IdentityManifold`/`ValueAxis` set is first-class *within* a turn: when the proposition-graph planner produces multiple valid completions, the articulator should choose the one that scores highest against the manifold's value axes. No goal-stack (`Goal`/`Plan`/`Pursuit`) data structure is added.
- **Alternatives explicitly rejected:** pure responsive (no axiology) — rejected because `IdentityManifold` was already an architectural commitment (ADR-0010) and the adversarial-identity defense needs axes to *shape* behavior, not just measure it; pure agentic — rejected because it breaks the `trace_hash` deterministic-replay contract and is "not what CORE claims to be."
- **Artifacts the ADR claims will exist:**
  - no `loop()` or `pursue(goal)` entry point
  - no `Goal`/`Plan`/`Pursuit` typed object
  - articulator candidate selection that consults `ValueAxis` scores to choose among multiple valid completions
  - `core/cognition/explain.py`, invoked per turn-id, not autonomously
  - `persona/motor.py`, shaping articulation within the turn, not between turns
  - the `trace_hash` contract in `core/cognition/trace.py` as a deterministic function of (input, prior-state)
  - `tests/test_determinism_proofs.py` continuing to pass for multi-turn scenarios

## 2. Implementation cross-reference

| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| No `loop()`/`pursue(goal)` entry point | yes (absence confirmed) | — | Repo-wide grep for `def loop(`/`def pursue(` returns nothing. |
| No `Goal`/`Plan`/`Pursuit` typed object | yes (absence confirmed) | — | Repo-wide grep for `class Goal`/`class Plan`/`class Pursuit` returns nothing. |
| `ValueAxis` type | yes | `core/physics/identity.py:196`, `core/physics/drive.py:15` | Real dataclass; loaded from identity packs via `packs/identity/loader.py:248-302`; carried on `IdentityManifoldGeometry.value_axes` (`core/physics/identity.py:312`). |
| Articulator candidate selection consulting `ValueAxis` to choose among completions | no | `generate/graph_planner.py:405` (`plan_articulation`) | `plan_articulation` is a deterministic single-path topological walk over one graph — there is no set of "multiple valid completions" being scored at all, let alone against value axes. |
| `identity_score` used downstream | yes, different role | `chat/runtime.py:2912-3017` | `identity_score` is computed and used to build surface context, detect boundary violations, and gate refusal (`IdentityCheck.would_violate`) — a post-hoc measurement/gate, not a pre-hoc candidate selector. |
| `core/cognition/explain.py` | yes | `core/cognition/explain.py:1-16` | Exists, and its own docstring explicitly self-documents conformance: "Per ADR-0017 (Responsive-with-Axiology), this is a per-turn operation invoked on a turn-id... introspection never runs autonomously between turns." |
| `persona/motor.py` | yes | `persona/motor.py:1-30` | Exists; a pure versor-product (`M = T*R`) applied to the field, no loop, matches "shapes articulation output within the responsive turn." |
| `trace_hash` deterministic-replay contract | yes | `core/cognition/trace.py` (`compute_trace_hash`) | Confirmed present and load-bearing. |
| `tests/test_determinism_proofs.py` | yes | `tests/test_determinism_proofs.py` | File exists. |

**Build axis:** partial — every negative/structural claim (no loop, no goal-stack, turn-triggered-only, `explain.py`/`persona/motor.py` as per-turn-only modules) is built and verified. The one positive, defining claim in the ADR's own name — axiology as an in-turn candidate-selection gradient — is not built at all.

## 3. Liveness / integration

- The "no autonomous initiative" boundary is live by construction (there is genuinely nothing to remove — the absence is the mechanism, and it holds). The `trace_hash`/replay-determinism machinery it depends on is live and tested.
- The axiology-selection claim is a different story: `IdentityManifold`/`ValueAxis` are computed every turn and threaded through `CognitiveTurnResult.identity_score`, but nothing reads them to choose among candidate completions — `plan_articulation` never branches on identity score, and `chat/runtime.py` only consults `identity_score` after the fact, as a violation/refusal gate.
- **Sabotage test:** delete `ValueAxis`/`IdentityManifold` entirely from the candidate-generation path (leave the post-hoc violation check as-is, sourced some other way) — articulation output would not change, because nothing in candidate generation reads it today. This part of the ADR is decoration relative to its own stated purpose. By contrast, removing the "no loop()" discipline (i.e., adding one) would be immediately observable — that boundary is genuinely load-bearing.
- **Liveness axis:** wired-but-unreached — `IdentityManifold`/`ValueAxis` are computed and carried through the result object (wired) but never consulted for the decision they were meant to shape (unreached), while the negative/boundary half of the ADR is fully live.

## 4. Design fidelity — pillars and axioms

| Pillar | Honors / Tension / Violates | Citation (ADR clause + pillar text) |
|---|---|---|
| I. Mechanical Sympathy | Honors | Ties the scope choice directly to what the machine can guarantee: "pure agentic loops break deterministic replay... Adding non-input-triggered internal actions would put state changes between turns that replay cannot reconstruct." |
| II. Semantic Rigor | Honors | Draws a crisp, non-negotiable line between "responsive" and "agentic" rather than leaving the boundary implicit. |
| III. Third Door | Honors | Textbook instance: rejects both named extremes (pure responsive, pure agentic) for the named third position. |

| Axiom | Honors / Tension / Violates | Citation |
|---|---|---|
| 1. Geometry-First | Tension | The "value gradient" language gestures at a geometric mechanism, but the decision never operationalizes it geometrically — it defers that to "the next refinement of articulator candidate selection," which (§2, §3) never landed. |
| 2. Field-State | Honors | `IdentityManifold` is itself a field/manifold object, consistent with the axiom. |
| 3. Propagation-over-Mutation | n/a | Not directly addressed by this scope decision. |
| 4. Dual-Correction | n/a | Not addressed. |
| 5. Reconstruction-over-Storage | n/a | Not addressed. |
| 6. Compilation-Last | n/a | Not addressed. |
| 7. Reality-over-Inheritance | Honors | Explicitly rejects the industry-common "autonomous agent loop" pattern on structural (replay) grounds rather than adopting it by default. |

## 5. Build fidelity — does the code match the decision?

Partial drift. The structural/negative constraints match cleanly and are verified (§2). The positive claim — "the choice is the one that scores highest against the manifold's value axes... goal-directedness within a single responsive turn" — does not match the build: `plan_articulation()` (`generate/graph_planner.py`) has no candidate-scoring step, and `identity_score` (`chat/runtime.py`) is used only as a post-hoc gate. This is corroborated independently by `docs/PROGRESS.md`'s own "Identity-override defense — fix #2 + fix #3" investigation (lines ~255-284), which measured `identity_score.alignment` as "1.000 universally" and concluded "fix #3 cannot be made load-bearing in place" because the upstream work (encoding token semantics into specific blade coordinates, then redefining the axes with a real inner-product projection) is "a scoped multi-PR effort, not a single sharpening exercise" — i.e., the exact gap this ADR named as its own next step is independently documented as still open.

**Build-fidelity axis:** partial drift — negative/structural half matches; positive axiology-selection half does not, and a separate document (`docs/PROGRESS.md`) independently confirms the gap.

## 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs

- No contradiction with `Whitepaper.md` or `Yellowpaper.md` found.
- Cleanly supersedes the "Agency (responsive vs. goal-directed)" row in `docs/PROGRESS.md`'s Open Scope Decisions, as declared.
- Consistent with, and extends, ADR-0010 (IdentityManifold as prior architectural commitment) and is depended on by ADR-0018 (tool-use scope, invoked synchronously inside one turn — matches).
- **Continuity axis:** clean — the supersession is real and undisputed; the standing gap is a build-fidelity issue (§5), not a document contradiction.

## 7. Necessity / generality

1. **Necessity:** the turn-triggered, no-background-loop boundary is necessary — it is what makes the `trace_hash` replay-determinism contract enforceable, which is load-bearing to CORE's core value proposition. Irreducible as an architectural boundary.
2. **Reducibility:** n/a — this is a scope/boundary decision, not an operator; nothing at L0/L1 reduces it.
3. **Extensibility:** ADR-0244 (wave-field identity manifold / Gram-based alignment, cited in `core/physics/identity.py`) is the natural completion path — it already replaced the old universal-1.0 `alignment` defect with a real Gram-projection score, and is the most plausible geometric substrate on which a future candidate-selection step could finally consult the axes as this ADR intended.

**Necessity/generality axis:** irreducible.

## 8. Fitness / value

For the built half (turn-triggered boundary, no autonomous loop, replay determinism): indirect but real evidence — ADR-0018's operator bundle (built as a synchronous, per-turn call per this ADR's shape) is exactly what closed `evals/inference_closure` from `0.0` to `1.0` pass rate (see ADR-0018's card, §8), which validates that the responsive-per-turn shape can carry real capability. For the axiology-selection half specifically: no positive evidence found, and one piece of *negative* evidence — `docs/PROGRESS.md`'s "fix #3 cannot be made load-bearing" conclusion is a documented finding that axis-consultation could not be made to carry signal with the data available at the time.

**Fitness axis:** partial — cited evidence for the responsive/no-loop shape (via ADR-0018's downstream success); no evidence, plus one documented negative result (`docs/PROGRESS.md`), for the axiology-selection claim.

## 9. Findings raised

- 🟡 **AA-B2-4** — the ADR's defining "axiology" clause (articulator candidate selection scored against `ValueAxis`) is unbuilt: `plan_articulation()` has no candidate-scoring step, and `identity_score` is used only as a post-hoc violation/refusal gate (`chat/runtime.py`). `docs/PROGRESS.md`'s own "fix #3 cannot be made load-bearing" finding independently confirms the same gap. (§2, §3, §5, §8)

## 10. Evidence sources actually consulted

- `docs/adr/ADR-0017-agency-scope.md` (full read).
- Repo-wide grep for `ValueAxis`/`IdentityManifold` usage; `core/physics/identity.py`, `core/physics/drive.py`, `packs/identity/loader.py` (reads).
- `generate/graph_planner.py` (`plan_articulation`, full function read).
- `chat/runtime.py` (`identity_score` usage sites, grep + targeted reads).
- `core/cognition/explain.py`, `persona/motor.py` (docstring/header reads).
- Repo-wide grep for `def loop(`/`def pursue(`, `class Goal`/`Plan`/`Pursuit` (absence confirmed).
- `docs/PROGRESS.md` "Identity-override defense — fix #2 + fix #3" section (read in full).
- `docs/assessment/10-layer-cards/M3-comprehension-reasoning.md` (read; no direct ADR-0017 mention).
- `docs/assessment/30-gap-register.md`, `31-hindrance-audit.md` (grepped — no hits for agency/axiology terms).

---

# ADR-0018 — Tool Use Scope: Typed Deterministic Operators

**Audit ID (if a numbering collision):** — | **Family (if phased):** —
**Zone / stack:** B2 — Agency, Tool Use, Learning Loop & Vault (M3/M5/M1) | **Tier:** B
**ADR status (as recorded in the file):** Accepted | **ADR date:** 2026-05-16
**Card author:** ADR-Audit subagent | **`verified_at` SHA:** `cbfc8ccbf7fe503ab31abe7aedbb1973ba7d7b4d`

---

## 1. Content summary

- **Decision made:** CORE adopts typed deterministic operators — a small, curated, ADR-gated set of pure functions over CORE's typed state (proposition graph, vault, field versors), no external IO, invoked synchronously inside one turn, with every invocation folded into `trace_hash`. Initial set: `transitive_walk(graph, head, relation, max_hops) -> list[Node]` and `path_recall(vault, entity, relation_chain) -> list[VaultEntry]` (the latter using "the existing exact-CGA inner product for entity matching").
- **Alternatives explicitly rejected:** no tools (inline reasoning only); external tools (generic/MCP-style tool-use protocol, LLM-as-judge/LLM-as-tool patterns, approximate/ANN search operators).
- **Artifacts the ADR claims will exist:**
  - `transitive_walk` operator
  - `path_recall` operator, over the vault, using exact-CGA matching
  - a `trace_hash` extension folding operator-invocation records
  - an articulator operator-call site in `generate/realizer.py` and/or `generate/graph_planner.py`
  - unit tests showing replay-bit-stability
  - re-scored inference-closure / multi-step-reasoning / compositionality / cross-domain-transfer eval lanes

## 2. Implementation cross-reference

| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `transitive_walk` | yes | `generate/operators.py:54-114` | Pure function, bounded `max_hops`, deterministic, cycle-safe. Live-wired via `core/cognition/pipeline.py::_maybe_transitive_walk` (`:1223-1262`), called from `:473`. |
| `path_recall` | partial | `generate/operators.py:243-278` | Built and unit-tested (`tests/test_inference_operators.py:186-213`) — but (a) never invoked anywhere outside tests (grepped repo-wide), and (b) its built substrate contradicts the decided one: the decision names `path_recall(vault, entity, relation_chain) -> list[VaultEntry]` using "the existing exact-CGA inner product," but the built function is `path_recall(triples, entity, relation_chain, ...) -> tuple[str, ...]` over plain `(head, relation, tail)` string triples from the teaching store — it never touches the vault or CGA algebra at all. |
| `trace_hash` operator-invocation folding | yes | `core/cognition/trace.py::compute_trace_hash(operator_invocation=...)`; `core/cognition/pipeline.py:822-831` | Confirmed: walk/compose/entailment/inductive-closure results are serialized and `"|"`-joined into `operator_invocation`, which is a hashed field. |
| Articulator operator-call site | partial (location drift) | `core/cognition/pipeline.py:1223,1264` (`_maybe_transitive_walk`, `_maybe_compose_relations`) | The ADR names `generate/realizer.py`/`generate/graph_planner.py`; the actual call site is `core/cognition/pipeline.py`. The behavioral contract (deterministic decide-whether-to-invoke, based on intent + graph shape) is honored; the named module is not. |
| `multi_relation_walk`, `compose_relations` (operators beyond the named two) | yes (unrequested by name) | `generate/operators.py:117-240` | Landed the same week as ADR-0018, closing `evals/compositionality` and `evals/multi_step_reasoning`. Not individually backed by a distinct ADR-level decision — the ADR's own clause 3 says "adding an operator is a deliberate design act with an ADR-level decision," though its "Future extensions" section does anticipate operators landing "under this ADR's operator umbrella." |
| Unit tests for replay-bit-stability | yes | `tests/test_inference_operators.py` | Present, covers all four operators. |
| Re-scored eval lanes | yes | `evals/inference_closure/gaps.md`, `evals/multi_step_reasoning/gaps.md`, `evals/compositionality/gaps.md` | All three document a `0.0` → `1.0` pass-rate jump explicitly attributed to "the typed operators + pipeline wiring" landing. |

**Build axis:** partial — the walk/compose family (3 of 4 operators) is fully built, live-wired, and directly evidenced by re-scored eval lanes. The ADR's own second named operator, `path_recall`, is built but unreached and drifted from its decided vault/CGA substrate to a symbolic-triples substrate.

## 3. Liveness / integration

- `transitive_walk`, `multi_relation_walk`, and `compose_relations` are reached on the live serving path: `CognitiveTurnPipeline` calls `_maybe_transitive_walk`/`_maybe_compose_relations` on every turn whose intent shape qualifies, and the result is folded into the served surface and into `trace_hash`.
- `path_recall` is scaffolded, not reached: it exists and is tested but has no call site anywhere in `core/cognition/pipeline.py`, `generate/realizer.py`, or `generate/graph_planner.py`.
- **Sabotage test (walk/compose family):** remove the `_maybe_transitive_walk`/`_maybe_compose_relations` calls from the pipeline — the `inference_closure`, `multi_step_reasoning`, and `compositionality` lanes would regress from their current `1.0` pass rate back to their documented pre-fix baselines (`0.0` on the inference/multi-step signal). This is directly measured, not hypothetical — both states are recorded in the same `gaps.md` files.
- **Sabotage test (`path_recall`):** delete the function entirely — zero observable change anywhere, because nothing calls it. Decoration by the same test.
- **Liveness axis:** live for the walk/compose subsystem (transitive_walk, multi_relation_walk, compose_relations); scaffolded for `path_recall` specifically.

## 4. Design fidelity — pillars and axioms

| Pillar | Honors / Tension / Violates | Citation (ADR clause + pillar text) |
|---|---|---|
| I. Mechanical Sympathy | Honors | Pure functions, bounded `max_hops`, no external IO — deliberately cheap and predictable cost shape. |
| II. Semantic Rigor | Honors | The "What this rules out" section draws sharp, explicit lines (no MCP-style plugins, no LLM-as-tool, no approximate search). |
| III. Third Door | Honors | Explicitly rejects both "no tools" and "external tools" for the typed-deterministic third path. |

| Axiom | Honors / Tension / Violates | Citation |
|---|---|---|
| 1. Geometry-First | Tension | The decision frames operators as acting over "proposition-graph nodes, vault entries, field versors" — but every operator that actually ships (walk/compose family, and even the unwired `path_recall`) operates purely on symbolic `(head, relation, tail)` string triples. None of the live operators touch the vault, CGA inner product, or field versors at all. |
| 2. Field-State | Tension | Same gap — the live operators never read or produce field state; they are a purely symbolic layer sitting beside the geometric substrate, not built on it. |
| 3. Propagation-over-Mutation | Honors | All four operators are pure functions with no global state and no mutation (verified by code read). |
| 4. Dual-Correction | n/a | No forward/conjugate pair applies to a graph-walk operator. |
| 5. Reconstruction-over-Storage | n/a | Not addressed. |
| 6. Compilation-Last | Honors | Operators are plain functions, not a registry/kernel/table — "operator lookup is at the import-time level, not the per-turn level," exactly as decided. |
| 7. Reality-over-Inheritance | Honors | Explicit, reasoned rejection of the MCP-style plugin pattern and LLM-as-tool pattern common elsewhere, justified on replay-determinism grounds, not by default. |

## 5. Build fidelity — does the code match the decision?

Partial drift, three distinct points: (a) `path_recall`'s decided substrate (vault + CGA inner product entity matching) does not match its built substrate (plain string-triple matching, no vault/CGA touch at all) — this is a real, substantive drift, not cosmetic; (b) the operator-call site is `core/cognition/pipeline.py`, not the `generate/realizer.py`/`generate/graph_planner.py` the ADR names — a location drift with the behavioral contract otherwise intact; (c) two operators (`multi_relation_walk`, `compose_relations`) were added under the ADR's own forward-looking "operator umbrella" clause rather than each getting its own named ADR-level decision, a looser reading of clause 3's letter than its text suggests.

**Build-fidelity axis:** partial drift — justified above.

## 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs

- No contradiction with `Whitepaper.md` or `Yellowpaper.md` found.
- Depends on ADR-0017 (agency scope) — consistent: operators are invoked synchronously inside one turn, exactly as ADR-0017 requires.
- **CR-3 cross-check (per this audit's brief):** `docs/assessment/02-layer-taxonomy.md` §5 cites ADR-0018 by number as CR-3 ("Efferent action")'s only partial existence — "typed deterministic tool operators folded into `trace_hash` (ADR-0018)." **This audit's code-level verification confirms that claim is true**: `operator_invocation` is a real, populated field threaded into `compute_trace_hash` (`core/cognition/trace.py`; `core/cognition/pipeline.py:822`). One nuance worth carrying into CR-3's eventual ruling: the operators that are folded into `trace_hash` are symbolic-graph functions, never the vault or field-versor state the ADR's own framing groups them with (§4) — CR-3's "partial existence" characterization is accurate, but understates how partial: the mechanism folded into `trace_hash` is further from "efferent action on world/field state" than the ADR's prose implies.
- `docs/adr/INDEX-by-domain.md` independently records the same trace_hash-folding claim, corroborating the code read.
- **Continuity axis:** clean.

## 7. Necessity / generality

1. **Necessity:** the walk/compose operator family is irreducible relative to inline articulator logic — it is a genuinely new, bounded, replay-safe capability the system lacked, evidenced directly by the `0.0`→`1.0` eval-lane jump.
2. **Reducibility:** the operators do not reduce to, or build on, the L0/L1 CGA algebra at all — they are a self-contained symbolic-triple traversal utility that sits beside the geometric substrate rather than generalizing it, despite the ADR's own text implying they operate over "field versors" among other things (§4).
3. **Extensibility:** `path_recall` (unwired) and `vault_recall`/ADR-0019 (wired, live, exact-CGA) are the natural pairing this ADR itself proposed but never delivered — today they are two disconnected "recall" mechanisms with different substrates. A future revision genuinely unifying `path_recall` with the vault's real CGA-based recall, rather than leaving `path_recall` as an unreached, differently-substrated stub, is the clearest consolidation candidate in this zone.

**Necessity/generality axis:** irreducible (walk/compose subsystem); generalization-candidate (`path_recall` ↔ `vault_recall` convergence).

## 8. Fitness / value

Strong, directly cited evidence — the cleanest before/after fitness story found in this zone:
- `evals/inference_closure/gaps.md`: `derived_recall_rate` 0.0 → 1.0 on public/v1 (n=20) and holdouts/v1 (n=12), explicitly attributed to "the typed deterministic operators (ADR-0018: `transitive_walk`, `multi_relation_walk`, `path_recall` in `generate/operators.py`) and their pipeline wiring."
- `evals/multi_step_reasoning/gaps.md`: `endpoint_recall_rate`, `intermediate_hop_visible_rate` both 0.0 → 1.0 on both splits, "same architectural fix that closed inference_closure."
- `evals/compositionality/gaps.md`: `composed_predicate` and `novel_relation_on_seen_pair` closed via `multi_relation_walk`/`compose_relations`.

**Fitness axis:** cited — `evals/inference_closure/gaps.md`, `evals/multi_step_reasoning/gaps.md`, `evals/compositionality/gaps.md` (all three, 0.0→1.0 pass-rate evidence).

## 9. Findings raised

- 🟡 **AA-B2-5** — `path_recall` is built and unit-tested but unreached on any serving path (dead per sabotage test), and its built substrate (plain string triples) contradicts the decision's literal text (vault + exact-CGA inner product entity matching). (§2, §3, §4, §5)
- 🟢 **AA-B2-6** — the operator registry grew from the named 2-operator bundle to 4 (`multi_relation_walk`, `compose_relations` added) without a distinct ADR-level decision for either, relying on ADR-0018's own forward-looking "operator umbrella" clause as implicit cover — worth a ruling on whether that satisfies clause 3's stated governance intent. (§2, §5)
- 🟢 **AA-B2-7** — CR-3 cross-check: "folded into `trace_hash`" is confirmed true in code, but the operators actually live are pure symbolic-graph functions that never touch the vault or field-versor state the ADR's own framing describes — worth noting explicitly when CR-3 is finally ruled. (§4, §6)

## 10. Evidence sources actually consulted

- `docs/adr/ADR-0018-tool-use-scope.md` (full read).
- `generate/operators.py` (full read — all four operators).
- `core/cognition/pipeline.py` (`_maybe_transitive_walk`, `_maybe_compose_relations`, `operator_invocation` construction — targeted reads).
- `core/cognition/trace.py` (`compute_trace_hash` signature and `operator_invocation` param — targeted read).
- `tests/test_inference_operators.py` (existence + coverage check).
- `evals/inference_closure/gaps.md`, `evals/multi_step_reasoning/gaps.md`, `evals/compositionality/gaps.md` (full reads).
- `docs/assessment/02-layer-taxonomy.md` §5, CR-3 entry (full read, per this audit's specific brief).
- `docs/adr/INDEX-by-domain.md` (grep, corroborating trace_hash claim).
- Repo-wide grep for `multi_relation_walk`/`compose_relations` in `docs/adr/*.md` (no dedicated ADR found for either).
- `docs/assessment/30-gap-register.md`, `31-hindrance-audit.md` (grepped — no hits for tool-use terms).

---

# ADR-0019 — Exact Vault Recall Acceleration

**Audit ID (if a numbering collision):** — | **Family (if phased):** —
**Zone / stack:** B2 — Agency, Tool Use, Learning Loop & Vault (M3/M5/M1) | **Tier:** B
**ADR status (as recorded in the file):** Accepted | **ADR date:** 2026-05-16
**Card author:** ADR-Audit subagent | **`verified_at` SHA:** `cbfc8ccbf7fe503ab31abe7aedbb1973ba7d7b4d`

---

## 1. Content summary

- **Decision made:** a three-stage, semantics-preserving acceleration plan for vault recall, each stage gated on evidence from the previous one, no stage ever permitting approximate recall. Stage 1 (commit immediately): vectorize the per-element Python scan in `algebra/backend.py::vault_recall` into a single batched matrix-vector inner product, bit-identical to the scalar path. Stage 2 (gated on Stage 1 evidence): norm-bucketed exact pre-filter using Cauchy–Schwarz. Stage 3 (gated on Stage 2 evidence): a layered store with deterministic promotion.
- **Alternatives explicitly rejected:** HNSW/NSW/annoy/FAISS-IVF or any nearest-neighbour approximation, cosine fallback or any non-CGA metric, learned indexes/embeddings/projections, hot-path drift repair inside recall. Blade-signature indexing is explicitly deferred, not rejected.
- **Artifacts the ADR claims will exist:**
  - Stage 1: vectorized `vault_recall` in `algebra/backend.py`, bit-identical to the scalar reference, signature/shape/ordering/top-K semantics preserved, no new state
  - a correctness test asserting per-element equality across a fixture vault
  - Stage 2 (conditional): norm-bucketed pre-filter, cached norm vector, checksum hashes
  - Stage 3 (conditional): layered store, deterministic promotion counters as replay state
  - the Rust backend port inheriting the vectorized contract
  - `tests/test_trace_hash.py` and the eval replay suite continuing to pass bit-for-bit after each stage

## 2. Implementation cross-reference

| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| Stage 1 vectorized `vault_recall` | yes | `algebra/backend.py:156-222` | Batched `M @` diagonal-metric scan, docstring explicitly cites "ADR-0019 Stage 1"; signature, return shape, and stable top-k tie-break order all preserved as decided. |
| Bit-identity correctness test | yes | `tests/test_vault_recall_vectorised.py` | Asserts `_CGA_INNER_METRIC` is diagonal ±1, and per-versor scores/ordering match the scalar `cga_inner` path across multiple seeds. |
| Stage 2 (norm-bucketed pre-filter) | no | — | Grepped for `norm_bucket`/norm-caching in `vault/store.py` — absent. Correctly gated/unbuilt: the trigger condition ("Stage 1 leaves recall super-linear past N≈10⁵") was never measured to occur — see §8. |
| Stage 3 (layered store) | no | — | No promotion/tiering code found. Also correctly gated/unbuilt on the same basis. |
| Rust backend port | yes (beyond scope) | `algebra/backend.py:186-196` (`_rs.vault_recall`, zero-copy `(N,32)` f32) | Landed already — ahead of the ADR's own framing of it as "the next axis after Phase 4." |
| `vault_recall_batch` (batched API) | yes (ADR-0054, adjacent) | `algebra/backend.py:225-` | Not this ADR's own artifact, but the same file, consistent extension. |
| `tests/test_trace_hash.py` | no | — | Cited in the ADR's own Verification section; does not exist at this path (also independently flagged by the corpus-wide stale-reference sweep). Real determinism coverage lives in `tests/test_vault_recall_vectorised.py`, `tests/test_vault_recall_rust_parity.py`, `tests/test_determinism_proofs.py`. |

**Build axis:** full — for Stage 1, which is what the ADR designates as committing "immediately." Stages 2/3 are correctly, deliberately un-built because their own stated gating conditions were never triggered (§8) — this is fidelity to the ADR's design, not a build gap.

## 3. Liveness / integration

- `vault/store.py` imports and calls `vault_recall`/`vault_recall_batch` directly from `algebra.backend` on the real recall path (`vault/store.py:20-21,256,322`). `docs/assessment/10-layer-cards/M1-knowledge-memory.md` independently pins `vault/store.py:224,296` (`recall`/`recall_batch`) as "would-fail-if-absent: yes."
- **Sabotage test:** revert `vault_recall` to the pre-vectorization scalar Python loop — recall latency would balloon back to the documented pre-fix baseline (≈870 ms at N=10³, extrapolated ≈87 s at N=10⁵ per `evals/long_context_cost/gaps.md`), a directly observable regression on every recall call. Bit-identity tests would still pass (Stage 1 changes cost, not result, by design) but the "unfit for per-turn runtime" performance defect this ADR exists to fix would return immediately.
- **Liveness axis:** live.

## 4. Design fidelity — pillars and axioms

| Pillar | Honors / Tension / Violates | Citation (ADR clause + pillar text) |
|---|---|---|
| I. Mechanical Sympathy | Honors | The entire ADR is a mechanical-sympathy diagnosis: "the cost shape is dominated by per-iteration NumPy dispatch, not by the algebra." |
| II. Semantic Rigor | Honors | "Exactness" is defined precisely as bit-identical, not approximately close, and tested as such. |
| III. Third Door | Honors | Rejects both "stay slow" and "go approximate" for a third path: exact-but-fast via better data organization. |

| Axiom | Honors / Tension / Violates | Citation |
|---|---|---|
| 1. Geometry-First | Honors | Exploits an actual geometric fact — the CGA inner product's metric is diagonal ±1 under Cl(4,1) — rather than bolting on an external index. |
| 2. Field-State | Honors | Versors remain the stored unit; recall remains a field-consistent read. |
| 3. Propagation-over-Mutation | Honors | Stage 1: "no new state, no new mutable cache." |
| 4. Dual-Correction | n/a | Not addressed by this ADR. |
| 5. Reconstruction-over-Storage | Tension (deferred stages only) | Stage 2's norm cache and Stage 3's tier/promotion state are additional *stored* derived state rather than reconstructed on demand — moot today since both are unbuilt, but worth flagging if either is ever triggered. |
| 6. Compilation-Last | Honors | Explicit, deliberate discipline: "the right first step because it dissolves the artefact without committing the codebase to an index design" — structure (buckets, tiers) is added only if evidence later demands it. |
| 7. Reality-over-Inheritance | Honors | Blade-signature indexing explicitly deferred "because... norm-bucketing is simpler and likely sufficient" — a structural-merit judgment, not habit. |

## 5. Build fidelity — does the code match the decision?

Matches, with one minor caveat. Stage 1 as built matches the decision precisely: same function signature, same return shape/ordering, no new state, bit-identical by pinned test. The one mismatch is a forward-looking sentence in the ADR's own Consequences section — "`vault.store()` gains an O(1) per-call cost: append norm to a pre-allocated buffer" — which describes Stage 2 norm-caching machinery that has not landed (§2), because Stage 2 itself has not triggered. This is the ADR's own text getting ahead of a conditional stage, not a Stage-1 delivery gap.

**Build-fidelity axis:** matches.

## 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs

- Directly implements the `AGENTS.md`/`CLAUDE.md` "exact recall only" invariant cited in the ADR's own Context section; no contradiction with `Whitepaper.md` or `Yellowpaper.md` found.
- Consistent with, and complemented by, ADR-0054 (Vault Recall: Matrix-Cache Indexing + Batched API), which supplies `vault_recall_batch` and the `prebuilt_matrix` caching that `vault_recall` (Stage 1) explicitly accepts as an optional parameter. Both are cited together in `docs/assessment/10-layer-cards/M1-knowledge-memory.md`.
- **Continuity axis:** clean.

## 7. Necessity / generality

1. **Necessity:** irreducible. Exact recall itself is dictated by the `AGENTS.md` invariant and the L0 algebra; once exactness is fixed as policy, some mechanically-sympathetic realization of it is necessary for it to be usable per-turn at all (the pre-vectorization ~870ms-plus latency was explicitly "unfit for a per-turn runtime call").
2. **Reducibility:** the acceleration technique is, by the ADR's own honest framing, not a new capability but a correct, efficient realization of a fact already latent in L0 — the CGA inner product's bilinearity and diagonal metric. This is the intended relationship (compilation-last, geometry-first), not a violation: Stage 1 invented no new machinery, it stopped failing to exploit existing algebra.
3. **Extensibility:** generalization-candidate. The same diagonal-metric vectorization technique is a plausible template for other unvectorized per-element CGA loops elsewhere in the system — `docs/assessment/02-layer-taxonomy.md`'s Candidate Register (CR-1) already names `cga_inner`/`geometric_product` as roughly 73% of turn time, the system's hottest path. Whether that hot path uses the same vectorization trick, or still runs the un-accelerated scalar form outside of vault recall specifically, is worth a direct check in a future pass.

**Necessity/generality axis:** irreducible, with a generalization-candidate note on the technique's applicability elsewhere (CR-1's hot path).

## 8. Fitness / value

Some of the strongest, most directly quantified fitness evidence found in this audit zone. `evals/long_context_cost/gaps.md` + `evals/long_context_cost/results/v1_metrics.json`:

| N | pre-vectorization median | post-Stage-1 median | speedup |
|---|---:|---:|---:|
| 1,000 | 874.774 ms | 0.217 ms | ~4,030x |
| 10,000 | 8,727.420 ms | 1.701 ms | ~5,130x |
| 100,000 | (extrapolated ≈87 s) | 20.795 ms | ~4,200x |

Post-vectorization log-log slope is measured at 0.99 ("linear" asymptotic class) — the gating condition for Stage 2 ("recall super-linear past N≈10⁵") was checked and not met, so Stage 2/3 correctly never triggered. Bit-identity is pinned by `tests/test_vault_recall_vectorised.py`.

**Fitness axis:** cited — `evals/long_context_cost/gaps.md`, `evals/long_context_cost/results/v1_metrics.json`, `tests/test_vault_recall_vectorised.py`.

## 9. Findings raised

- 🟢 **AA-B2-8** — ADR-0019's own Verification section cites `tests/test_trace_hash.py`, which does not exist at this path; the real coverage lives in differently-named files (`tests/test_vault_recall_vectorised.py`, `tests/test_vault_recall_rust_parity.py`, `tests/test_determinism_proofs.py`) — citation drift only, already independently flagged by the corpus-wide stale-reference sweep. (§6, §10)
- 🔵 **AA-B2-9** — Stage 1's diagonal-metric vectorization technique is a consolidation candidate for other unvectorized per-element CGA hot loops elsewhere in the system, given CR-1 already names `cga_inner`/`geometric_product` as ~73% of measured turn time — worth a Phase-4 check on whether the same technique generalizes beyond `vault_recall`. (§7)

## 10. Evidence sources actually consulted

- `docs/adr/ADR-0019-exact-vault-recall-acceleration.md` (full read).
- `algebra/backend.py` (full read of `vault_recall`, `vault_recall_batch`, Rust dispatch path).
- `vault/store.py` (grep for `vault_recall` call sites, `_matrix_cache`; grep for norm/bucket-related code — absent).
- `evals/long_context_cost/gaps.md`, `contract.md` (full/partial reads); `results/v1_metrics.json` (referenced, not individually re-parsed).
- `tests/test_vault_recall_vectorised.py` (read — bit-identity contract).
- `docs/assessment/10-layer-cards/M1-knowledge-memory.md` (cites `vault/store.py:224,296` as would-fail-if-absent: yes).
- `docs/assessment/02-layer-taxonomy.md` §5, CR-1 entry (cga_inner/geometric_product hot-path figure).
- `docs/census/cbfc8ccb.../stale-references.jsonl` (checked for ADR-0019 rows — confirmed `tests/test_trace_hash.py` flagged there too).

---

## Zone findings — rollup

- 🟡 **AA-B2-1** — ADR-0014's `train/` layer was never built; `LearningArtifact` objects are produced by `core_ingest/compiler.py` and consumed by nothing anywhere in the repository — confirmed dead output.
- 🟡 **AA-B2-2** — ADR-0014 remains "Accepted (Stub)," uncontradicted and unsuperseded, while the system's actual learning path (M5: teaching/formation/reliability_gate/capability) satisfies the same telos need through an entirely unrelated mechanism that never cites it. Record and reality have silently diverged since 2026-05-13; needs a ruling.
- 🟢 **AA-B2-3** — vestigial ADR-0014 vocabulary (`gate_engaged`, `grammar_scaffold=None`) survives, unpopulated, in `sensorium/` and `packs/schema.py` — worth checking whether these are leftovers of an abandoned build attempt.
- 🟡 **AA-B2-4** — ADR-0017's defining axiology clause (candidate selection scored against `ValueAxis`) is unbuilt; `identity_score` is only a post-hoc violation/refusal gate. `docs/PROGRESS.md`'s "fix #3 cannot be made load-bearing" finding independently confirms the same gap.
- 🟡 **AA-B2-5** — ADR-0018's `path_recall` is built and unit-tested but unreached on any serving path, and its built substrate (plain string triples) contradicts the decided substrate (vault + exact-CGA inner product).
- 🟢 **AA-B2-6** — ADR-0018's operator registry grew from the named 2-operator bundle to 4 without a distinct ADR-level decision for the two extra operators, relying on the ADR's own forward-looking "operator umbrella" clause as implicit cover.
- 🟢 **AA-B2-7** — CR-3 cross-check: "folded into `trace_hash`" (ADR-0018) is confirmed true in code, but the live operators never touch the vault or field-versor state the ADR's own framing groups them with — worth noting when CR-3 is ruled.
- 🟢 **AA-B2-8** — ADR-0019's Verification section cites a nonexistent `tests/test_trace_hash.py`; real coverage lives in differently-named files (citation drift only).
- 🔵 **AA-B2-9** — ADR-0019 Stage 1's diagonal-metric vectorization technique is a consolidation candidate for other unvectorized CGA hot loops (CR-1's `cga_inner`/`geometric_product`, ~73% of turn time).

**Zone-level pattern:** the two same-week companion ADRs that shipped together (ADR-0017/ADR-0018) show the same shape twice — a well-evidenced, live mechanical core (responsive-turn boundary; walk/compose operators) paired with an unbuilt or drifted headline claim (axiology-driven selection; vault/CGA-backed `path_recall`). ADR-0019 is the zone's clean outlier — decided, built, tested, and evidenced exactly as specified, with its conditional stages correctly left untriggered. ADR-0014 is the zone's structural outlier — not partially built, but entirely absent, with its telos need quietly satisfied by a parallel system that never reconciles with it.
