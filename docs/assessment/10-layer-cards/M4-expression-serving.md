# M4 — Expression & Serving

**Kind:** layer · **Parent:** CORE · **Assessor:** Opus 5 (Phase 2)
**Verified at:** `8927c563` (2026-07-27)
**Liveness:** `live-serving` · **Fitness:** `strained` · **Topology role:** runtime boundary

> Field → world. M4 owns the only bytes a user ever sees, which makes it the layer where the project's central discipline — `wrong=0` or refuse — either holds or fails. Everything upstream can be correct and M4 can still serve a falsehood by selecting the wrong surface; everything upstream can refuse and M4 must render that refusal honestly rather than filling it. Its philosophical charge is that *saying* is a distinct act from *knowing*, governed separately.

**Telos stages:** articulate (primary); replay/determinism (trace emission)
**Macro role:** Selects, governs, decorates, and emits the served surface; emits the telemetry that makes the turn auditable.

---

## What it is / What it does

`chat/runtime.py` (3364 lines) is the layer's centre of mass, with `core/cognition/pipeline.py` (1381) wrapping it for the full cognitive turn, and `generate/realizer.py` + `generate/surface.py` producing the articulation. Around them: the register axis (`chat/register_variation.py`, `chat/register_substantive.py`), response governance (`core/response_governance/`: `govern_response`, `shape_surface`), grounding composers (`chat/pack_grounding.py`, `chat/teaching_grounding.py`, `chat/deduction_surface.py`, `chat/curriculum_surface.py`), the refusal surface (`chat/refusal.py`), safety and ethics checks, and telemetry (`chat/telemetry.py`, `chat/verdicts.py`).

The load-bearing behavior is **surface selection**, contracted in `runtime_contracts.md`: `surface = determination_surface` when a turn determined an answer over realized knowledge; `= [approximate] estimate` under a genuine SERVE license; `= _UNKNOWN_DOMAIN_SURFACE` when the unknown-domain gate fires; `= articulation_surface` otherwise. `walk_surface` and `articulation_surface` are both *always* retained as evidence — a determination or a gate is a **selection**, never a rewrite. This is the layer's best design property: the honest artifact survives even when it is not what was served.

Three distinct surfaces exist for three distinct invariants, and conflating them is a documented hazard: `surface` (what the user read), `walk_surface` (manifold/token-walk evidence), and `hash_surface` (the register-invariant truth-path capture that `compute_trace_hash` folds). Because `TurnEvent` carries the served surface but never `hash_surface`, **`trace_hash` is not reconstructable from telemetry** — a contract, not a defect. Verify a hash by replaying the pipeline, never by rebuilding it from a turn record.

---

## Contract

- **Inputs:** `ArticulationTarget` / `PropositionGraph` from M3, determination or entailment results, mounted register/safety/ethics/identity packs (M1, MG), session context.
- **Outputs:** `ChatResponse` (`surface`, `walk_surface`, `articulation_surface`), `TurnEvent`, `TurnVerdicts`, `trace_hash`, `CognitivePipelineRecord`, `grounding_source`, `epistemic_state`.
- **Invariants:**
  - Register must not move `trace_hash` (ADR-0069 inv C) — pin: register lane tests — status: running (register suites present).
  - Unknown-domain gate honoured — the realizer's fallback must not override the gate's stub — pin: contract tests in the cognition suite.
  - Realizer slot-type guard / C1 coherence floor (ADR-0075), with a **documented** exemption for deduction's quoted templates at both guard sites (`chat/runtime.py:2371-2375`, `:3007-3010`).
  - Grounding-source registration is a three-part atomic change (enum + `enum-snapshot.json` + UI badge contract) — pin: `workbench-ui/enumCoverage.test.ts` fails the build on divergence; `tests/test_workbench_deduction_provenance.py`.
  - A live `/chat/turn` with a trace hash but no `status="recorded"` pipeline record fails before journal append; pre-widening rows must show `missing_evidence`, never a synthesized green pipeline.

---

## Design vs build

- **Design:** `docs/specs/runtime_contracts.md` (the frozen surface-selection policy, the `trace_hash` contract, audit-ledger R7); ADR-0069/0071/0075/0077 (register axis and guards); ADR-0206 (response-governance bridge); ADR-0039 (audit completeness); ADR-0153 (trace-hash back-stamp); ADR-0254 (grounded-open hedge arm); ADR-0265 (negation reaches the surface); ADR-0024/0025/0026 (typed refusal, rotor and margin admissibility).
- **Build:** `live-serving`.
- **Evidence:**
  - Deduction serving is ratified ON and reaches served output — measurement — `core/config.py:397 deduction_serving_enabled=True`; verified by execution 2026-07-25 (`_run_chat_turn` on a modus-ponens prompt returns the entailment surface) — would-fail-if-absent: **yes**.
  - Surface selection honours the unknown-domain gate — contract + pin — `runtime_contracts.md` §"Unknown-domain gate honour" — would-fail-if-absent: **yes**.
  - Provenance falsification (a proved deduction answer recorded as `grounding_source='none'`) is **closed** — the registration requirement and its pin are now documented in `runtime_contracts.md` §"Grounding-source registration" — would-fail-if-absent: **yes**.
  - Negation reaches the surface (ADR-0265, merged `8927c563`): under `realizer_grounded_authority`, "evidence does not support truth" and "evidence supports truth" previously served **byte-identical** surfaces — would-fail-if-absent: **yes**.
  - Register decoration does not move `trace_hash` — pin — would-fail-if-absent: **yes**.

---

## Capacity

- **Designed:** every served surface is either grounded, disclosed, or an honest refusal; `wrong=0` or refuse.
- **Measured:** `wrong=0` holds across every ratified serving lane (deduction 18,000 cases / 25 bands; curriculum physics 32/32; deductive logic 716/716). Writer-side construction inventory: **1739 constructions emitted**. Refusal is typed and carries a machine-readable reason plus per-step rejection evidence.
- **Ceilings:** a real refusing turn still returns `surface == ""` with `refusal_reason == ""` through `ChatRuntime.respond()`'s `str` contract — the typed evidence is **unread between the raise site and the public return**. The plumbing exists on `CognitiveTurnResult` and `compute_trace_hash`; materialisation awaits a future ADR. Curriculum serving is OFF; `ask` and `verified` serving are OFF.

---

## Dependencies & provenance

**receives** ← M3; **reads** → M1 (packs, register, lexicon), MG (safety, ethics, identity); **feeds** → M5 (correction capture), MV (telemetry, trace, pipeline record), M6 (checkpoint at turn boundary); **governed-by** → MG (safety is fail-closed and never swappable).

---

## Stage coverage

| Stage | Verdict | Evidence |
|---|---|---|
| articulate | **covered** | Live serving with ratified `wrong=0` lanes; typed refusal; disclosed estimates; negation now representable |
| replay/determinism (emission side) | **covered, with a known asymmetry** | `trace_hash` is deliberately register-invariant and deliberately not reconstructable from `TurnEvent`; audit-ledger R7 closed by deferred emission at the serve boundary |

**Zone roster:** `L6-chat-runtime` (partial-wiring-debt per map → **revised to `live-serving` at layer level**: the serving path demonstrably executes end-to-end), `L9-epistemic-verdicts` ✱ (straddles MG; owned here, cross-referenced there).

**Rollup note:** the map's `partial-wiring-debt` label on `L6-chat-runtime` reflects internal wiring debt (dormant modules, unmaterialised refusal strings), not a non-serving path. The layer serves; parts of it are unwired. Weakest-link rollup again understating the serving reality.

---

## Judgment

**Fitness: `strained`.** M4's *architecture* is among the strongest in CORE — the selection-not-rewrite discipline, the three-surface separation, the fail-closed typing, the atomic enum/UI coupling. The strain is that its surface-selection policy has accreted one arm per capability (determination, estimate, unknown-domain, deduction, curriculum, hedge, register decoration, logos-morph override), each individually contracted, with no single place that states the precedence order as an executable rule. `runtime_contracts.md` documents it in prose across several sections; `chat/runtime.py` implements it across 3364 lines. That is the classic shape of a trade-off being split rather than dissolved — and a Third Door candidate for Phase 4 (a declarative resolution table with the precedence pinned, rather than ordered branches).

**Honest wrinkles:**
- **A refusing turn serves the empty string.** `respond()`/`arespond()` convert any `ValueError` to `""` for their public `str` contract, so the typed refusal — reason code, blocking region, per-step evidence — is constructed and then discarded before the caller sees it. The system's honesty machinery is real and, on this path, unread.
- The layer that owns `wrong=0` is also the layer where the PR #138 fabrications *surface*: the reader's fabricated `member(every_dog, mammal)` and the recited `furthermore` premise reach **served output**. The defect is M3's; the blast radius is M4's. Measured and pinned, held for ADR + ratification — recorded, not fixed.
- `epistemic_state` degrades honestly (`epistemic_state_needed`) where hand-copied whitelists degraded dishonestly (`none`). The asymmetry is a reusable design lesson: a coercion that asserts a falsehood is strictly worse than doing nothing.
- Surface selection is documented as "current policy… future realizer work may change it" — a standing invitation to accrete another arm.

**Open questions:**
- Materialise the typed refusal into `ChatResponse.refusal_reason` (→ ruling; ADR already anticipated)
- Should surface precedence become a declarative table? (→ Phase 4 hindrance audit)
- Whether `TurnEvent` should carry `hash_surface` remains an open ruling recorded in `runtime_contracts.md` (→ ruling)
