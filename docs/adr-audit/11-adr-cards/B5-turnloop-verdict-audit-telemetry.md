# B5 — Turn-Loop Verdict Surfacing & Audit Telemetry

**Zone:** B5 (macro layers MV/M4) · **Tier:** B · **Batch:** 1 (ADR-0001–0050) · **Card author:** Tier-B audit subagent · **`verified_at` SHA:** `cbfc8ccb`

This zone is a single sequential arc, not five independent decisions: ADR-0035 auto-invokes `SafetyCheck`/`EthicsCheck` at end-of-turn and attaches the two verdicts to `ChatResponse`/`TurnEvent`; ADR-0039 bundles them (plus remediation flags) into one `TurnVerdicts` type, completes the previously-stubbed stub-path `TurnEvent` emission, and adds the `hedge_injected` signal; ADR-0040 gives the bundle a deterministic JSONL sink (`chat/telemetry.py`); ADR-0041 adds the operator-facing `core chat --show-verdicts` CLI flag and a `FanOutSink`; ADR-0042 assembles all four into a single demo, `core demo audit-tour`. Each ADR's own "Open questions deferred to a future ADR" section names the next ADR in the chain almost verbatim, and the code confirms the same order landed with no drift: `chat/verdicts.py` (`TurnVerdicts`), `core/physics/identity.py::TurnEvent`, `chat/runtime.py::_stub_response`/`chat`, `chat/telemetry.py` (serializer + three sink types + CLI formatter), `core/cli.py` (`--show-verdicts`, `core demo audit-tour`), and `evals/audit_tour/run_tour.py` all exist, are wired on the live serving path, and were exercised live during this audit (`core chat --show-verdicts` printed a real verdict line to stderr; `core demo audit-tour --json` returned `all_claims_supported: true`). The one substantive finding across the zone is not in the ADRs' own claims but in their tests: all five ADRs' verification test files (80 tests total, all green when run directly) are declared `full`-only in `tests/full_only_baseline.txt` and appear in no curated suite (`smoke`, `runtime`, `cognition`) — the audit-telemetry system's own falsifiability tests never run on the pre-push gate that AGENTS.md's local-first CI doctrine treats as the real gate.

---

## ADR-0035 — Turn-Loop Verdict Surfacing for SafetyCheck and EthicsCheck

**Audit ID (if a numbering collision):** — | **Family (if phased):** — (part of the B5 sequential arc)
**Zone / stack:** B5 — Turn-Loop Verdict Surfacing & Audit Telemetry (macro layers MV/M4)
**ADR status (as recorded in the file):** Accepted (2026-05-17) | **ADR date:** 2026-05-17
**Card author:** Tier-B audit subagent | **`verified_at` SHA:** `cbfc8ccb`

### 1. Content summary

- **Decision made:** `ChatRuntime` auto-invokes both `SafetyCheck.check(...)` and `EthicsCheck.check(...)` at the end of every chat turn (main articulation path and `_stub_response`), attaching the resulting `SafetyVerdict`/`EthicsVerdict` to new optional fields on `ChatResponse` and `TurnEvent`. Deliberately observational — no refusal, no re-articulation, no logging integration, no CLI surface, no cross-surface bundle. Those five omissions are each named explicitly as "what this ADR does NOT do" and each becomes a later ADR in this zone (0036/0037, 0039, 0040, 0041, 0039 again).
- **Alternatives explicitly rejected:** Option 2 ("Surfacing + refusal") — rejected because the runtime has evidence for only ~3 of ~10 predicate fields at v1, so wiring refusal now would refuse on a tiny fraction of theoretical violations while letting the rest slip silently through; the ADR chose to land the invocation point first and decide refusal policy from observed data.
- **Artifacts the ADR claims will exist:**
  - `ChatRuntime` end-of-turn invocation of `self.safety_check.check(...)` / `self.ethics_check.check(...)` on both the main path and `_stub_response`.
  - `ChatResponse.safety_verdict`, `ChatResponse.ethics_verdict` (new optional fields, default `None`).
  - `TurnEvent.safety_verdict`, `TurnEvent.ethics_verdict` (new optional fields, default `None`).
  - `_FieldStateWithVersor` adapter exposing `versor_condition` for `SafetyContext`.
  - `_hash_identity_manifold(manifold)` — deterministic SHA-256 of load-bearing manifold fields, captured at `__init__` and recomputed each turn.
  - `tests/test_turn_loop_verdicts.py` — 14 tests.

### 2. Implementation cross-reference

| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| End-of-turn `safety_check.check`/`ethics_check.check` invocation, main + stub paths | yes | `chat/runtime.py:2423` (`safety_ctx = SafetyContext(...)`), `chat/runtime.py:2974` (main-path mirror) | Both `_stub_response` and the main `chat()` path construct contexts and call `.check`. |
| `ChatResponse.safety_verdict` / `.ethics_verdict` | yes | `chat/runtime.py:451-452` | Present, typed `object`, defaulting `None`, with an ADR-0035 comment citing the design. |
| `TurnEvent.safety_verdict` / `.ethics_verdict` | yes | `core/physics/identity.py:628-629` | Present on the frozen dataclass, comment cites ADR-0035 directly. |
| `_FieldStateWithVersor` adapter | yes | `chat/runtime.py:315` | Frozen one-field dataclass, used at both invocation sites. |
| `_hash_identity_manifold` | yes | `chat/runtime.py:329` | Called at `__init__` and recomputed per turn; used for `no_identity_override` evidence. |
| `tests/test_turn_loop_verdicts.py` | yes | `tests/` | Ran directly: passes (part of the 80/80 combined run for the zone — see §8/§9). |

**Build axis:** full — every named artifact exists verbatim, at the call sites the ADR describes, with comments in the source citing the ADR number.

### 3. Liveness / integration

- Reached on the live serving path: confirmed by direct execution. `echo "light is" | core chat --show-verdicts --no-load-state` printed `[identity=- safety=ok ethics=VIOLATED:acknowledge_uncertainty refusal=- hedge=-]` to stderr — a verdict derived from a live `EthicsCheck.check()` call on a real cold-start turn, not a canned string.
- **Sabotage test:** if `SafetyCheck.check`/`EthicsCheck.check` were stubbed to always return an unconditionally-upheld verdict, the observable that would change is exactly what ADR-0039's audit-completeness (`hedge_injected`, `refusal_emitted`), ADR-0040's JSONL sink fields (`safety_upheld`, `ethics_violated`, etc.), and ADR-0041's `--show-verdicts` line all read. `gap-register.md` G-9(b) independently pins this non-bypass property: "every function in `chat/runtime.py` that constructs a `TurnVerdicts` must also invoke `safety_check.check`... Measured at close: two verdict-constructing functions, both governed." Removing the invocation is not decoration — it is the exact failure mode a sibling audit finding already tested for and closed.
- **Liveness axis:** live — reached on every chat turn (main and stub), independently confirmed both by direct CLI execution and by the gap-register's own governance-bypass pin.

### 4. Design fidelity — pillars and axioms

| Pillar | Honors / Tension / Violates | Citation (ADR clause + pillar text) |
|---|---|---|
| I. Mechanical Sympathy | Honors | Cheap by construction: "two predicate-registry passes per turn... no measurable cost." |
| II. Semantic Rigor | Honors | `runtime_checkable=False` vs `upheld=True` distinguishes "no evidence" from "verified clean" — refuses to conflate absence of a check with passing it. |
| III. Third Door | Honors | Rejected the binary "wire refusal now" vs "do nothing" in favor of surfacing-only-then-decide-from-data. |

| Axiom | Honors / Tension / Violates | Citation |
|---|---|---|
| 1. Geometry-First | Honors | `preserve_versor_closure`/`no_identity_override` predicates read geometric quantities (`versor_condition`, manifold hash) rather than surface text. |
| 2. Field-State | n/a | Verdicts are per-turn scalars/booleans over an existing field-derived state, not a new field representation. |
| 3. Propagation-over-Mutation | Honors | Verdicts are read off state that already propagated (`final_state`, `walk_surface`); nothing is stepwise-mutated to produce them. |
| 4. Dual-Correction | n/a | No forward operator introduced here; this ADR is purely observational. |
| 5. Reconstruction-over-Storage | Tension | `identity_manifold_hash_before`/`_after` stores a hash rather than reconstructing identity continuity from the manifold each time — a deliberate, cheap tradeoff the ADR itself justifies ("the underlying manifold never mutates... equal by construction"), so tension rather than violation. |
| 6. Compilation-Last | n/a | No loop/kernel/table structure introduced. |
| 7. Reality-over-Inheritance | Honors | The ADR explicitly declines to inherit the "refuse immediately" pattern from prior packs (ADR-0032/0034) until real evidence justifies it. |

### 5. Build fidelity — does the code match the decision?

Matches. The evidence-availability gradient described in the ADR's tables (`versor_condition`, `last_refusal_was_typed`, manifold hashes, `alignment_score`, `hedge_threshold_soft`, `hedge_emitted`, `grounded_in_evidence`/`disclosure_emitted` runtime-checkable; citation/high-stakes/prescriptiveness fields `runtime_checkable=False`) is exactly what `SafetyContext`/`EthicsContext` construction populates at both call sites (`chat/runtime.py:2423-2447`, `:2974+`). No divergence found.

**Build-fidelity axis:** matches.

### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs

- Does not contradict `Whitepaper.md` or `Yellowpaper.md`.
- Companion/superseding chain is clean: ADR-0035 explicitly names five deferred items, and ADR-0036, ADR-0037, ADR-0038, ADR-0039, ADR-0040, ADR-0041 each pick up exactly one. No silent overlap found — MG-governance-identity.md's card corroborates the same chain (`TurnVerdicts` output listed under MG's contract).
- **Continuity axis:** clean.

### 7. Necessity / generality

1. **Necessity:** Irreducible at the surfacing layer — without an explicit end-of-turn invocation, the pack-layer's own MG card states plainly that "an observation surface that no caller invokes is a label without a verdict" (quoting the ADR's own framing). The system could run without it, but audit/safety-floor accountability would regress to silent.
2. **Reducibility:** No L0/L1 algebra/field operator already performs "invoke two predicate registries and attach the result to a turn record" — this is glue/wiring at the runtime-boundary layer, not a duplicate of a geometric primitive.
3. **Extensibility:** This ADR is itself the generalization seed that ADR-0039 (bundle), ADR-0040 (sink), ADR-0041 (CLI/fan-out) each build on directly — no cross-stack pairing candidate outside this zone was found.

**Necessity/generality axis:** irreducible.

### 8. Fitness / value

`docs/assessment/10-layer-cards/MG-governance-identity.md` lists `TurnVerdicts` under MG's Outputs and cites the safety/identity invocation as live-serving evidence (`chat/runtime.py:93,104-105`). `docs/assessment/30-gap-register.md` G-9(b) independently measured and closed the governance-non-bypass property this ADR's invocation sites make possible to test ("two verdict-constructing functions, both governed"). `tests/test_turn_loop_verdicts.py` (14 tests) passes directly. No evidence this specific ADR's test file runs on any curated CI gate (see zone-level finding AA-B5-1).

**Fitness axis:** cited evidence — `docs/assessment/10-layer-cards/MG-governance-identity.md` (Outputs, Evidence rows); `docs/assessment/30-gap-register.md` G-9(b).

### 9. Findings raised

- 🟢 `AA-B5-2` — ADR-0035 built and live exactly as specified; independently corroborated by a sibling audit's governance-bypass pin (gap-register G-9b). No repair action implied.

### 10. Evidence sources actually consulted

- `docs/adr/ADR-0035-turn-loop-verdict-surfacing.md` (full text).
- `chat/runtime.py` (`_FieldStateWithVersor`, `_hash_identity_manifold`, `_stub_response`, main `chat()` path — read directly, line numbers cited above).
- `core/physics/identity.py::TurnEvent` (read directly).
- `docs/assessment/10-layer-cards/MG-governance-identity.md`, `docs/assessment/10-layer-cards/M4-expression-serving.md` (read in full).
- `docs/assessment/30-gap-register.md` G-9(b) (read in context).
- Live execution: `core chat --show-verdicts --no-load-state` with piped input, observed real stderr verdict line.
- `tests/test_turn_loop_verdicts.py` executed directly (part of the 80-test combined run, all green).

---

## ADR-0039 — Audit Completeness — `TurnVerdicts` Bundle, Stub-Path `TurnEvent`, `hedge_injected` Signal

**Audit ID (if a numbering collision):** — | **Family (if phased):** — (part of the B5 sequential arc)
**Zone / stack:** B5 — Turn-Loop Verdict Surfacing & Audit Telemetry (macro layers MV/M4)
**ADR status (as recorded in the file):** Accepted (2026-05-17) | **ADR date:** 2026-05-17
**Card author:** Tier-B audit subagent | **`verified_at` SHA:** `cbfc8ccb`

### 1. Content summary

- **Decision made:** Three changes land together: (1) a frozen `TurnVerdicts` bundle type (`chat/verdicts.py`) grouping identity/safety/ethics verdicts plus `refusal_emitted`/`hedge_injected`, attached to both `ChatResponse.verdicts` and `TurnEvent.verdicts`; (2) `_stub_response` gains an optional `tokens` kwarg that, when non-empty, constructs and appends a `TurnEvent` to `turn_log` for stub turns (closing the gap ADR-0035 flagged); (3) a `hedge_injected` signal computed by comparing pre/post-hedge-injection surface identity rather than inferred from text.
- **Alternatives explicitly rejected:** none named explicitly; the ADR frames the three changes as closing "rough edges" rather than choosing among alternatives.
- **Artifacts the ADR claims will exist:**
  - `chat/verdicts.py::TurnVerdicts` — frozen dataclass with `identity_score`, `safety_verdict`, `ethics_verdict`, `refusal_emitted`, `hedge_injected`.
  - `ChatResponse.verdicts`, `TurnEvent.verdicts` fields.
  - `_stub_response(..., tokens=...)` — appends `TurnEvent` to `turn_log` when `tokens` is truthy; the `correct()` fallback path deliberately calls without `tokens`.
  - `hedge_injected` computed as `response_surface != before` around `inject_hedge`.
  - `tests/test_turn_verdicts_bundle.py` — 16 tests, including `test_refusal_and_hedge_never_both_true`.

### 2. Implementation cross-reference

| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `chat/verdicts.py::TurnVerdicts` (frozen, slots, 5 fields) | yes | `chat/verdicts.py:26-51` | Docstring explicitly attributes design to ADR-0039; fields typed `object` per the ADR's stated rationale. |
| `ChatResponse.verdicts` / `TurnEvent.verdicts` | yes | `chat/runtime.py:453-457`; `core/physics/identity.py:632-635` | Both carry inline comments citing ADR-0039. |
| Stub-path `TurnEvent` emission gated on `tokens` | yes | `chat/runtime.py:2389` (signature `tokens: tuple[str, ...] = ()`), `chat/runtime.py:2564` (`if tokens:` block constructing and appending `stub_event`) | **This is the "Stub-Path `TurnEvent`" claim the audit brief flagged for explicit scrutiny — see §3.** |
| `correct()` fallback calls `_stub_response` without `tokens` | yes | `chat/runtime.py:3321`, `:3367` | Both call sites (`_unknown_domain_response`, `correct()`'s no-regen-tokens fallback) omit `tokens`, exactly as the ADR specifies ("a defensive call where no real 'turn' happened"). |
| Main-path callers pass `tokens` | yes | `chat/runtime.py:2769` (`tokens=tuple(filtered)`), `:2869` (exhaustion-path stub, `tokens=tuple(filtered)`) | Both real-turn stub invocations pass non-empty tokens. |
| `hedge_injected` before/after comparison | yes | `chat/runtime.py` main path (verified via `TurnVerdicts` construction reading `hedge_injected` flag) | Bundle field present and distinct from surface-substring inference. |
| `tests/test_turn_verdicts_bundle.py` | yes | `tests/` | Ran directly: passes. |

**Build axis:** full — all three sub-decisions are implemented exactly as described, including the one sub-clause (the `correct()`-fallback exemption) that is easy to get wrong and wasn't.

### 3. Liveness / integration

- **The stub-path `TurnEvent` is NOT still a stub.** This was flagged by name in the audit brief as a claim to sabotage-test explicitly, given the ADR's own title calls it "Stub-Path `TurnEvent`." Direct code read of `chat/runtime.py:2389-2610` shows the `if tokens:` branch is fully implemented: it builds a complete `TurnEvent` (surface, walk_surface, articulation_surface, versor_condition, the full `TurnVerdicts` bundle, plus register/anchor-lens/realizer-guard/epistemic-state fields added by later ADRs), appends it to `turn_log`, and calls `self._emit_turn_event(stub_event)` — the same telemetry hook the main path uses. It is reached on the live serving path: every cold-start / unknown-domain turn with real input tokens goes through this branch. Confirmed live: `core chat --show-verdicts` on a cold-start turn ("light is") produced a real verdict summary, which only exists because the stub path executes the full verdict-construction sequence.
- **Sabotage test:** if the `if tokens:` guard were flipped to always-false (silently reverting to ADR-0035's pre-fix behavior), the observable that disappears is exactly the gap ADR-0039 names: stub/cold-start turns would vanish from `turn_log`, and any consumer iterating the turn stream (the telemetry sink, `core demo audit-tour` Scene 4's replay check, a future dashboard) would silently undercount turns with no error raised — a decoration-shaped defect that this ADR closes correctly rather than one it introduces.
- **Liveness axis:** live — the stub-path completion is real, reached on every cold-start turn, and independently exercised by this audit's own CLI runs.

### 4. Design fidelity — pillars and axioms

| Pillar | Honors / Tension / Violates | Citation |
|---|---|---|
| I. Mechanical Sympathy | Honors | "Cheap" claim in Consequences; verified — combined suite grew from 154→170 tests with no CLI-suite runtime regression cited in the ADR's own Verification section. |
| II. Semantic Rigor | Honors | Distinguishes "didn't fire" from "would have fired but idempotent" explicitly as a named, acknowledged limitation rather than conflating them silently. |
| III. Third Door | Honors | Rejects "infer remediation from surface text" (brittle) vs "leave stub turns unaudited" (incomplete) in favor of a structured bundle + explicit stub emission. |

| Axiom | Honors / Tension / Violates | Citation |
|---|---|---|
| 1. Geometry-First | n/a | Bundle aggregates existing verdict/flag values; introduces no new geometric structure. |
| 2. Field-State | n/a | Same. |
| 3. Propagation-over-Mutation | Honors | `hedge_injected` is derived by comparing before/after surface identity — a read of what already propagated, not a new mutation path. |
| 4. Dual-Correction | n/a | Not applicable to an audit-bundle ADR. |
| 5. Reconstruction-over-Storage | Tension | The bundle duplicates per-field state already on `ChatResponse`/`TurnEvent` ("the bundle duplicates per-field state" — the ADR's own Negative/risks section) — an explicit, acknowledged storage-over-reconstruction tradeoff for back-compat. |
| 6. Compilation-Last | n/a | No loop/table/kernel structure. |
| 7. Reality-over-Inheritance | Honors | Corrects ADR-0035's actual gap (stub-path silence) rather than inheriting it as a permanent limitation. |

### 5. Build fidelity — does the code match the decision?

Matches, including the one clause most likely to drift silently: the ADR specifies the `correct()` fallback must call `_stub_response` *without* `tokens` "that's a defensive call where no real 'turn' happened, and appending a `TurnEvent` would mis-record the audit stream" — and the code (`chat/runtime.py:3321`, `:3367`) honors that exemption precisely. No divergence found.

**Build-fidelity axis:** matches.

### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs

- No contradiction with `Whitepaper.md`/`Yellowpaper.md` found.
- Extends ADR-0035 cleanly (all five of ADR-0035's "does NOT do" items are addressed either here or in later zone ADRs); companion docs list ADR-0036/0037/0038 as prerequisite context, consistent with the citation graph.
- **Continuity axis:** clean.

### 7. Necessity / generality

1. **Necessity:** Irreducible — the stub-path gap this ADR closes is a genuine completeness defect (audit consumers "couldn't see stub turns at all"), not a duplicate of anything upstream.
2. **Reducibility:** No L0/L1 primitive already performs "bundle three verdicts plus two derived booleans into one record." This is audit-surface plumbing, correctly scoped to M4/MV.
3. **Extensibility:** `TurnVerdicts` is itself the generalization point later ADRs in this zone consume (ADR-0040's serializer reads `event.verdicts`; ADR-0041's `format_verdict_summary` reads the bundle directly). No further consolidation candidate found outside the zone.

**Necessity/generality axis:** irreducible.

### 8. Fitness / value

`docs/assessment/10-layer-cards/M4-expression-serving.md` lists `TurnVerdicts` among M4's Outputs and documents the one honest asymmetry in this area (`TurnEvent` carries the served surface but never `hash_surface`, so `trace_hash` is deliberately not reconstructable from telemetry — "a contract, not a defect," per that card, and orthogonal to this ADR's own scope). `tests/test_turn_verdicts_bundle.py` (16 tests) passes directly, including the mutual-exclusion pin (`test_refusal_and_hedge_never_both_true`). Not in any curated CI suite (zone-level finding AA-B5-1).

**Fitness axis:** cited evidence — `docs/assessment/10-layer-cards/M4-expression-serving.md` (Outputs row, `hash_surface` note); direct test execution.

### 9. Findings raised

- 🟢 `AA-B5-3` — the "Stub-Path `TurnEvent`" claim in the ADR's own title is fully discharged in code, not a residual stub; explicitly verified per the audit brief's sabotage-test instruction (§3 above).
- 🟡 `AA-B5-4` — the `correct()`-fallback exemption (`_stub_response` without `tokens`) is correct today but is a manually-maintained convention (any new call site that constructs a stub without deliberately deciding the `tokens` question could silently mis-record the audit stream, or silently omit a real turn) — no test found that would catch a *new* call site getting this wrong (only the two existing sites are pinned). Consider a lint/pin that enumerates all `_stub_response(` call sites and asserts each is deliberately tagged rather than defaulting silently.

### 10. Evidence sources actually consulted

- `docs/adr/ADR-0039-audit-completeness.md` (full text).
- `chat/verdicts.py` (full read).
- `chat/runtime.py` — `_stub_response` full body (`:2389-2660`), all five `_stub_response(` call sites located and individually inspected (`:2769`, `:2869`, `:3321`, `:3367`).
- `core/physics/identity.py::TurnEvent` (full field list read).
- `docs/assessment/10-layer-cards/M4-expression-serving.md` (full read).
- Live execution: `core chat --show-verdicts` cold-start turn (confirms stub-path verdict construction fires).
- `tests/test_turn_verdicts_bundle.py` executed directly (part of the 80-test combined run, all green).

---

## ADR-0040 — Structured-Logging Sink for Turn-Event Audit

**Audit ID (if a numbering collision):** — | **Family (if phased):** — (part of the B5 sequential arc)
**Zone / stack:** B5 — Turn-Loop Verdict Surfacing & Audit Telemetry (macro layers MV/M4)
**ADR status (as recorded in the file):** Accepted (2026-05-17) | **ADR date:** 2026-05-17
**Card author:** Tier-B audit subagent | **`verified_at` SHA:** `cbfc8ccb`

### 1. Content summary

- **Decision made:** `chat/telemetry.py` introduces a pure serializer (`serialize_turn_event`), a deterministic JSONL formatter (`format_turn_event_jsonl`), a minimal `TurnEventSink` protocol, and two sink implementations (`JsonlBufferSink`, `JsonlFileSink`). `ChatRuntime` gains `attach_telemetry_sink(sink, *, include_content=False)` and an internal `_emit_turn_event` hook called after every `turn_log.append` (both main and stub paths). Default stance is redact-by-default (metadata only; surface text/input tokens opt-in via `include_content=True`); errors are not swallowed (a failing sink raises out of `chat()`); no implicit wall-clock (timestamps are caller-provided).
- **Alternatives explicitly rejected:** an error-tolerant/resilient sink wrapper was considered and deliberately excluded from this ADR's scope ("intentionally not included... its own future ADR if needed at scale").
- **Artifacts the ADR claims will exist:**
  - `serialize_turn_event(event, **kwargs) -> dict`.
  - `format_turn_event_jsonl(event, **kwargs) -> str` (deterministic: `sort_keys=True`, compact separators, no trailing newline).
  - `TurnEventSink` Protocol (`emit(line)`), `JsonlBufferSink`, `JsonlFileSink`.
  - `ChatRuntime.attach_telemetry_sink`, `_emit_turn_event`, `_telemetry_sink`, `_telemetry_include_content` state.
  - Documented wire-format field table (23 metadata fields + 4 content fields + optional `timestamp`).
  - `tests/test_telemetry_sink.py` — 29 tests.

### 2. Implementation cross-reference

| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `serialize_turn_event` | yes | `chat/telemetry.py:45-` | Matches the ADR's boundary discipline: `getattr(..., default)` fallbacks on every field, exactly as documented. |
| `format_turn_event_jsonl` | yes | `chat/telemetry.py:197` | — |
| `TurnEventSink`, `JsonlBufferSink`, `JsonlFileSink` | yes | `chat/telemetry.py:371`, `:386`, `:399` | — |
| `FanOutSink` (ADR-0041, listed here for completeness of the grep) | yes | `chat/telemetry.py:435` | Confirms zone continuity — see ADR-0041 card. |
| `attach_telemetry_sink`, `_emit_turn_event` | yes | `chat/runtime.py:1513`, `:1691` | `_emit_turn_event` called at both `turn_log.append` sites: `:2599` (stub) and `:3266` (main). |
| Wire format field set | partial (superset) | `chat/telemetry.py:60-120` (approx.) | The *documented ADR-0040 field set* is present, but the module has grown substantially beyond it: fields for ADR-0072 (register), ADR-0073d (anchor-lens), ADR-0075 (realizer guard) are appended in the same function, all following the same `getattr(...)`-with-default discipline the ADR established. This is fidelity to the *pattern*, not literal field-set stasis — see §5. |
| `tests/test_telemetry_sink.py` | yes | `tests/` | Ran directly: passes. |

**Build axis:** full — every named artifact exists and is exercised on the live path (confirmed via `attach_telemetry_sink`/`_emit_turn_event` call-site trace).

### 3. Liveness / integration

- Reached on the live serving path: `_emit_turn_event` is called unconditionally after both `turn_log.append` sites (main-path `:3266`, stub-path `:2599`), and is a no-op absent a sink (per the ADR: "no-op without sink"). This was independently confirmed by `core demo audit-tour`'s Scene 4, which attaches a real sink and checks byte-identical JSONL output across two fresh `ChatRuntime` instances — a genuine sink-emission path, not a mock.
- **Sabotage test:** if `_emit_turn_event` were stubbed to a no-op, `core demo audit-tour --json`'s Scene 4 (`byte_identical` check) would either report `false` or crash outright (no lines to compare), and would fail its own test gate (`tests/test_audit_tour.py` asserts `all_claims_supported is True`). This is a case where a sibling ADR (0042) already built the exact sabotage-test artifact this card's discipline calls for — confirmed live during this audit (`scene_4_deterministic_replay.byte_identical: true`).
- **Liveness axis:** live.

### 4. Design fidelity — pillars and axioms

| Pillar | Honors / Tension / Violates | Citation |
|---|---|---|
| I. Mechanical Sympathy | Honors | "~7 µs/turn for the metadata-only path on warm cache; one fsync per emit" — measured, not asserted. |
| II. Semantic Rigor | Honors | Redact-by-default with an explicit, single, per-attachment opt-in (`include_content=True`) — a precise trust boundary rather than an implicit one. |
| III. Third Door | Honors | Rejects both "no sink" (unauditable outside the process) and "always include raw content" (PII risk) for a default-safe, explicit-opt-in middle path. |

| Axiom | Honors / Tension / Violates | Citation |
|---|---|---|
| 1. Geometry-First | n/a | Pure serialization/IO layer. |
| 2. Field-State | n/a | Same. |
| 3. Propagation-over-Mutation | n/a | Same. |
| 4. Dual-Correction | n/a | Same. |
| 5. Reconstruction-over-Storage | Honors | "Field set is fixed... missing or differently-typed `TurnEvent` attributes fall back to safe defaults" — an explicit reconstruction-tolerant contract rather than a brittle exact-shape dependency. |
| 6. Compilation-Last | n/a | No loop/kernel/table structure choice at stake. |
| 7. Reality-over-Inheritance | Honors | Declines to inherit an error-swallowing telemetry pattern common elsewhere; "sink errors propagate" is a deliberate, justified departure. |

### 5. Build fidelity — does the code match the decision?

Matches for everything the ADR specifies; the wire format has since grown (ADR-0072/0073d/0075 fields appended) beyond the table documented in ADR-0040 itself. This is expected, ADR-scoped growth (each addition cites its own ADR number inline) rather than undocumented drift — but it does mean ADR-0040's own field table, read in isolation, is now stale relative to the running system. No `schema_version` field was ever added despite ADR-0040's own "Open questions" naming it (item 4) and ADR-0041 re-deferring it (item 4 again) — two ADRs in the same zone name the same open question and neither closes it.

**Build-fidelity axis:** partial drift — the *mechanism* matches exactly; the *documented field table* in the ADR text is stale against the current wire format, and no schema-version field exists to let a downstream consumer detect that drift itself.

### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs

- No contradiction with `Whitepaper.md`/`Yellowpaper.md` found.
- Extends ADR-0039 cleanly (consumes `TurnEvent.verdicts` directly). Superseded-in-part by nothing found; ADR-0041 extends it (fan-out, CLI formatter) without contradiction.
- **Continuity axis:** clean (the field-table staleness noted in §5 is a build-fidelity finding, not a continuity contradiction — no other document or ADR asserts something the code now contradicts).

### 7. Necessity / generality

1. **Necessity:** Irreducible — a deterministic, redact-by-default, machine-readable audit line is not something any other CORE mechanism already provides.
2. **Reducibility:** No L0/L1 primitive duplicates "serialize a turn's audit-relevant fields to JSONL." Correctly scoped as MV infrastructure.
3. **Extensibility:** The `schema_version` gap (named twice, closed never) is itself the generalization candidate: a versioned schema would let the field-table drift noted in §5 become self-describing rather than requiring an auditor to diff the ADR text against the source.

**Necessity/generality axis:** irreducible.

### 8. Fitness / value

`docs/assessment/10-layer-cards/M4-expression-serving.md` names `chat/telemetry.py` explicitly as part of M4's centre of mass. `tests/test_telemetry_sink.py` (29 tests) passes directly, including the deterministic-JSONL and redaction-default assertions. No evidence found that this ADR's test file runs on any curated CI gate (zone-level finding AA-B5-1).

**Fitness axis:** cited evidence — `docs/assessment/10-layer-cards/M4-expression-serving.md` (module listed under "What it is / What it does"); direct test execution; live `core demo audit-tour` Scene 4 execution.

### 9. Findings raised

- 🟡 `AA-B5-5` — the wire-format field table documented in ADR-0040's own text is stale against the running `serialize_turn_event` (ADR-0072/0073d/0075 fields added later, undocumented in this ADR); `schema_version` was named as an open question in both ADR-0040 and ADR-0041 and closed in neither — a downstream consumer has no self-describing way to detect the field-set has grown since either ADR was written.

### 10. Evidence sources actually consulted

- `docs/adr/ADR-0040-telemetry-sink.md` (full text).
- `chat/telemetry.py` (full read, 522 lines).
- `chat/runtime.py` — `attach_telemetry_sink`, `_emit_turn_event`, both call sites (`:1513`, `:1691`, `:2599`, `:3266`).
- `docs/assessment/10-layer-cards/M4-expression-serving.md` (full read).
- Live execution: `core demo audit-tour --json` Scene 4 (byte-identical replay via a real sink).
- `tests/test_telemetry_sink.py` executed directly (part of the 80-test combined run, all green).

---

## ADR-0041 — `core chat --show-verdicts` + Sink Fan-Out

**Audit ID (if a numbering collision):** — | **Family (if phased):** — (part of the B5 sequential arc)
**Zone / stack:** B5 — Turn-Loop Verdict Surfacing & Audit Telemetry (macro layers MV/M4)
**ADR status (as recorded in the file):** Accepted (2026-05-17) | **ADR date:** 2026-05-17
**Card author:** Tier-B audit subagent | **`verified_at` SHA:** `cbfc8ccb`

### 1. Content summary

- **Decision made:** Two additions bundled together: (1) `core chat --show-verdicts`, a new CLI flag that prints a dense, human-readable per-turn `TurnVerdicts` summary to **stderr** (response stays on stdout); (2) `FanOutSink`, a composable sink that forwards `emit(line)` to N child sinks, fail-fast (first error propagates, subsequent sinks NOT called). A new pure formatter, `format_verdict_summary`, is explicitly declared human-stable but not machine-stable — the JSONL sink (ADR-0040) remains the only machine contract.
- **Alternatives explicitly rejected:** a `ResilientSink` wrapper (swallows per-sink errors) was considered and deliberately excluded, for the same "telemetry failures should be visible" doctrine ADR-0040 established.
- **Artifacts the ADR claims will exist:**
  - `chat` subparser `--show-verdicts` flag.
  - `format_verdict_summary(verdicts) -> str` in `chat/telemetry.py` — dense one-line format (`identity=`, `safety=`, `ethics=`, `refusal=`, `hedge=`).
  - `FanOutSink` dataclass in `chat/telemetry.py`.
  - `tests/test_telemetry_fanout_and_summary.py` — 13 tests.

### 2. Implementation cross-reference

| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `chat --show-verdicts` CLI flag | yes | `core/cli.py:2497-2504` | `action="store_true"`, help text cites ADR-0041 by name. |
| Flag actually printed to stderr per turn in the REPL loop | yes | `core/cli.py:149` (`show_verdicts = bool(getattr(args, "show_verdicts", False))`), `:173-178` (`if show_verdicts: ... print(summary, file=sys.stderr)`) | Confirmed live: `echo "light is\nquit" \| core chat --show-verdicts --no-load-state` printed `[identity=- safety=ok ethics=VIOLATED:acknowledge_uncertainty refusal=- hedge=-]` to stderr for a real cold-start turn. |
| `format_verdict_summary` | yes | `chat/telemetry.py:460` | — |
| `FanOutSink` | yes | `chat/telemetry.py:435` | Frozen-shape fail-fast forwarder matches the ADR's description. |
| `tests/test_telemetry_fanout_and_summary.py` | yes | `tests/` | Ran directly: passes. |

**Build axis:** full.

### 3. Liveness / integration

- Reached on the live serving path: independently confirmed by direct CLI execution during this audit (see table above) — not inferred from the ADR's own "CLI smoke (manual)" transcript, a fresh run against the current tree.
- **Sabotage test:** if `format_verdict_summary` were stubbed to always return `""`, the observable that disappears is the entire stderr readout — an operator running `--show-verdicts` would see nothing after each turn with no error raised. This is a real, user-visible sabotage surface (unlike some decoration findings elsewhere in this audit), so the flag is load-bearing for the operator-facing half of the audit story, not decorative.
- **Liveness axis:** live.

### 4. Design fidelity — pillars and axioms

| Pillar | Honors / Tension / Violates | Citation |
|---|---|---|
| I. Mechanical Sympathy | Honors | Stdout/stderr split keeps piped-tooling behavior (`core chat \| grep ...`) unaffected by the audit readout — respects the Unix content/metadata convention explicitly. |
| II. Semantic Rigor | Honors | Explicit, documented distinction between "human-stable, not machine-stable" (the summary) and "machine-stable" (the JSONL sink) — precise rather than conflated. |
| III. Third Door | Honors | Rejects both "no operator readout" and "make the JSONL line itself double as the operator readout" for two purpose-built formatters sharing one bundle. |

| Axiom | Honors / Tension / Violates | Citation |
|---|---|---|
| 1. Geometry-First | n/a | Presentation/composition layer only. |
| 2. Field-State | n/a | Same. |
| 3. Propagation-over-Mutation | n/a | Same. |
| 4. Dual-Correction | n/a | Same. |
| 5. Reconstruction-over-Storage | n/a | Same. |
| 6. Compilation-Last | n/a | Same. |
| 7. Reality-over-Inheritance | Honors | Declines to inherit a "swallow sink errors" pattern; `FanOutSink` is fail-fast by explicit choice, consistent with ADR-0040's precedent rather than a new one invented ad hoc. |

### 5. Build fidelity — does the code match the decision?

Matches. The fail-fast semantics ("first sink that raises propagates the exception; subsequent sinks are NOT called") is a specific, testable claim; `tests/test_telemetry_fanout_and_summary.py`'s pass (13/13, including a named fail-fast case per the ADR's own Verification section) corroborates it directly rather than by inference from prose.

**Build-fidelity axis:** matches.

### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs

- No contradiction with `Whitepaper.md`/`Yellowpaper.md` found.
- Extends ADR-0040 cleanly; both formatters (`format_turn_event_jsonl`, `format_verdict_summary`) share the same underlying `TurnVerdicts` bundle "no risk of drift" — verified true in code (both read off `response.verdicts`/`event.verdicts`, no separate derivation path found).
- **Continuity axis:** clean.

### 7. Necessity / generality

1. **Necessity:** Irreducible for the operator-facing half of the story — no other CORE surface gives a human a per-turn audit summary without parsing JSONL by hand.
2. **Reducibility:** No L0/L1 duplicate found.
3. **Extensibility:** `FanOutSink` is itself a small, generic composition primitive (any `Iterable[TurnEventSink]`) that other zones' sink-consuming ADRs could reuse without modification — flagged here as a positive generalization already achieved, not a pending candidate.

**Necessity/generality axis:** irreducible.

### 8. Fitness / value

No dedicated layer-card or gap-register citation found specific to `--show-verdicts` or `FanOutSink` beyond this zone's own ADR chain (MG/M4 cards cite `TurnVerdicts` and the telemetry module generally, not this ADR's specific additions by name). `tests/test_telemetry_fanout_and_summary.py` (13 tests) passes directly; this audit's own live CLI run is itself a fresh, independent fitness data point.

**Fitness axis:** no dedicated assessment-layer citation found; corroborated by direct test execution and this audit's own live CLI run.

### 9. Findings raised

- 🟢 `AA-B5-6` — both claimed additions (`--show-verdicts`, `FanOutSink`) are built, wired, and were independently confirmed live during this audit, not merely trusted from the ADR's own transcript.

### 10. Evidence sources actually consulted

- `docs/adr/ADR-0041-cli-verdicts-and-fanout.md` (full text).
- `core/cli.py` — `cmd_chat` (`:120-178`), `--show-verdicts` argparse definition (`:2497-2504`).
- `chat/telemetry.py` — `format_verdict_summary` (`:460`), `FanOutSink` (`:435`).
- Live execution: `core chat --help` (flag present in `--help` output); `core chat --show-verdicts --no-load-state` with piped input (real stderr verdict line observed).
- `tests/test_telemetry_fanout_and_summary.py` executed directly (part of the 80-test combined run, all green).

---

## ADR-0042 — Audit Tour Demo — `core demo audit-tour`

**Audit ID (if a numbering collision):** — | **Family (if phased):** — (part of the B5 sequential arc)
**Zone / stack:** B5 — Turn-Loop Verdict Surfacing & Audit Telemetry (macro layers MV/M4)
**ADR status (as recorded in the file):** Accepted (2026-05-17) | **ADR date:** 2026-05-17
**Card author:** Tier-B audit subagent | **`verified_at` SHA:** `cbfc8ccb`

### 1. Content summary

- **Decision made:** Ship `core demo audit-tour` as a new target on `core demo`, running four scenes that each exercise the live pack-layer surface and report a falsifiable result: S1 (identity is geometric — distinct pack thresholds/hedge phrases from JSON, not prompts), S2 (safety is the universal floor — deterministic typed refusal, evidence preserved on `walk_surface`), S3 (ethics commitments choose remediation — pack-driven `should_inject_hedge` differs between two packs via pure-helper evidence, not an end-to-end chat call), S4 (deterministic replay — two fresh `ChatRuntime` instances produce byte-identical JSONL for the same input). Supports both human narration (stdout) and `--json` (structured report, narration suppressed via a module-level `_VERBOSE` flag).
- **Alternatives explicitly rejected:** an earlier draft compared `response.surface` across packs/opt-in states directly — rejected as false on cold start (stub path erases pack-surface differences by design); the shipped version pulls structural evidence instead, an explicit, documented correction from a weaker first draft.
- **Artifacts the ADR claims will exist:**
  - `evals/audit_tour/run_tour.py::run_tour(emit_json=...)`.
  - `core demo audit-tour` / `core demo audit-tour --json` CLI targets.
  - Four scenes (S1–S4) each producing a documented JSON sub-report shape.
  - `all_claims_supported` boolean gate.
  - `tests/test_audit_tour.py` — 8 tests.

### 2. Implementation cross-reference

| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `evals/audit_tour/run_tour.py::run_tour` | yes | `evals/audit_tour/run_tour.py` | — |
| `core demo audit-tour` CLI target | yes | `core/cli.py:1704-1705` (`if target == "audit-tour": from evals.audit_tour.run_tour import run_tour`), `:3539`, `:3563` | Listed in `core demo`'s target enumeration and epilog examples (`core/cli.py:26`). |
| `--json` structured report | yes | confirmed live | `core demo audit-tour --json` returned parseable JSON with the exact top-level keys the ADR documents (`all_claims_supported`, `scene_1_identity_geometric`, ..., `scene_4_deterministic_replay`). |
| `all_claims_supported` gate | yes | live output: `"all_claims_supported": true` | Matches ADR's wire-format sample structurally and semantically. |
| Scene contract (S1–S4 evidence as documented) | yes | live output | S1: 3 distinct alignment thresholds, 2 distinct hedge phrases across `default_general_v1`/`generosity_first_v1`/`precision_first_v1`. S2: `refusal_emitted: true`, typed refusal string, `walk_surface` preserved. S3: `default_fires: false`, `deployment_fires: true`, hedge prefix `"Perhaps"` applied correctly. S4: `byte_identical: true`. |
| `core demo all` includes audit-tour as step 3/8 | yes | `core/cli.py:1995-2004` | `_section("3/8 audit-tour...")`, contributes to `consolidated["audit_tour"]` and the overall `passed` gate. |
| `tests/test_audit_tour.py` | yes | `tests/` | Ran directly: passes. |

**Build axis:** full — independently re-executed live during this audit (not merely cross-referenced against the ADR's own transcript), and every scene's claimed evidence shape matched exactly.

### 3. Liveness / integration

- Reached on the live serving path via direct CLI invocation (`core demo audit-tour --json`, run during this audit): produced real output, `all_claims_supported: true`, with per-scene evidence structurally matching the ADR's documented wire format. Also wired into `core demo all` as step 3 of 8, contributing to that command's overall pass/fail gate.
- **Sabotage test:** `tests/test_audit_tour.py` itself asserts `all_claims_supported is True` — per the ADR's own Consequences section, this is a genuine regression gate: "if any scene's claim flips to False, the test fails and we catch the regression before it ships." This audit independently re-ran the tour live and got a matching result, rather than trusting the ADR's transcript or the test file alone — a case where the sabotage-test discipline was already self-applied by the ADR's authors (Scene 1's own history — the first draft's surface-comparison claim being caught and corrected — is itself evidence the discipline was followed during development, not just asserted after).
- **Liveness axis:** live.

### 4. Design fidelity — pillars and axioms

| Pillar | Honors / Tension / Violates | Citation |
|---|---|---|
| I. Mechanical Sympathy | Honors | "No external dependencies... runs end-to-end, no external dependencies, in seconds" — confirmed by this audit's own live run (completed well under the default 120s tool timeout with room to spare). |
| II. Semantic Rigor | Honors | The Scene-1 draft correction (surface comparison → structural comparison) is exactly semantic rigor in practice: caught a claim that would have been true-looking but false, and fixed the claim rather than the presentation. |
| III. Third Door | Honors | Scene 3 rejects both "claim hedge injection end-to-end on a cold-start call" (false, per ADR-0038's stub-path exemption) and "skip the claim entirely" for a pure-helper demonstration that is honest about what it does and doesn't cover — documented explicitly in the ADR's own Negative/risks section. |

| Axiom | Honors / Tension / Violates | Citation |
|---|---|---|
| 1. Geometry-First | Honors | Scene 1's corrected form reports "structural pack differences" (loaded manifold fields) rather than surface-level illusions — geometry (the pack's actual JSON-encoded structure) over appearance. |
| 2. Field-State | n/a | Demo/reporting layer, not a new field representation. |
| 3. Propagation-over-Mutation | n/a | Same. |
| 4. Dual-Correction | n/a | Same. |
| 5. Reconstruction-over-Storage | n/a | Same. |
| 6. Compilation-Last | n/a | Same. |
| 7. Reality-over-Inheritance | Honors | The Scene-1 correction is a textbook instance: the first draft's claim was let go because it didn't survive contact with what cold-start actually does, not preserved because it was already written. |

### 5. Build fidelity — does the code match the decision?

Matches — every scene's live output shape and claim matched the ADR's documented wire format exactly (see §2 table), independently re-executed rather than merely cross-referenced.

**Build-fidelity axis:** matches.

### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs

- No contradiction with `Whitepaper.md`/`Yellowpaper.md` found.
- Explicitly built on ADR-0027 → ADR-0041 (companion docs list the full range); no supersession or contradiction found.
- **Continuity axis:** clean.

### 7. Necessity / generality

1. **Necessity:** Irreducible as a demo artifact — no other single command in the repo demonstrates all four pack-layer claims (identity geometry, safety floor, ethics remediation choice, deterministic replay) together with live evidence.
2. **Reducibility:** No L0/L1 primitive duplicates "run four scripted scenes against the live runtime and assert a claims gate." This is intentionally a thin orchestration layer over primitives (`SafetyCheck`, `EthicsCheck`, pack loaders, the telemetry sink) that already exist and are separately audited above — correctly scoped as a consolidation *of* those primitives, not a competing implementation.
3. **Extensibility:** The ADR names its own extension point directly (open question 2: "Per-domain ratified pack demo... the natural extension that completes the BD pitch") — a legitimate, ADR-acknowledged future generalization, not one this audit is originating.

**Necessity/generality axis:** irreducible (as an orchestration/demo layer; its sub-parts are individually audited under ADR-0035/0039/0040/0041 above and found irreducible there too).

### 8. Fitness / value

No dedicated assessment-layer card citation found specific to `audit-tour` by name. Direct, independent re-execution during this audit is itself the primary fitness evidence: `core demo audit-tour --json` returned `all_claims_supported: true` with all four scenes' evidence matching the ADR's documented contract. `tests/test_audit_tour.py` (8 tests) passes directly. `core demo all` step 3/8 wiring confirms this is not an isolated/orphaned demo target.

**Fitness axis:** cited evidence — this audit's own live execution (`core demo audit-tour --json`, `all_claims_supported: true`); `core/cli.py:1995-2004` (`core demo all` integration); direct test execution.

### 9. Findings raised

- 🟢 `AA-B5-7` — `core demo audit-tour` and `core demo audit-tour --json` both work exactly as documented; independently re-executed live during this audit (not merely trusted from the ADR's transcript), with all four scenes' evidence matching.

### 10. Evidence sources actually consulted

- `docs/adr/ADR-0042-audit-tour-demo.md` (full text).
- `core/cli.py` — `audit-tour` target dispatch (`:1704-1705`), `core demo all` integration (`:1995-2004`), epilog/help text (`:26`, `:3539`, `:3563`).
- Live execution: `core demo audit-tour --json`, full JSON output captured and cross-checked field-by-field against the ADR's documented wire format.
- `tests/test_audit_tour.py` executed directly (part of the 80-test combined run, all green).

---

## Zone findings (rollup)

- 🟡 `AA-B5-1` — **The B5 audit-telemetry system's own falsifiability tests are not gated.** All five ADRs' verification files (`tests/test_turn_loop_verdicts.py`, `tests/test_turn_verdicts_bundle.py`, `tests/test_telemetry_sink.py`, `tests/test_telemetry_fanout_and_summary.py`, `tests/test_audit_tour.py` — 80 tests total, confirmed green when run directly during this audit) appear in `tests/full_only_baseline.txt` and in no curated suite (`smoke`, `runtime`, `cognition` — checked directly against `core/cli_test.py::TEST_SUITES`). Per AGENTS.md's local-first CI doctrine, `core test --suite smoke -q` is the real pre-push gate; `full` is not run pre-merge. This is honestly *declared* (the baseline-ratchet mechanism `tests/test_suite_membership.py`/`test_suite_reachability.py` exists precisely to make "full-only" a visible, shrinking number rather than a silent gap — per the N-9 discipline already established for other zones, e.g. `test_safety_pack.py` before its G-9c promotion), so this is not the "hollow gate" pattern the gap register already closed elsewhere — but it does mean the zone whose entire purpose is turn-level audit accountability has none of its own regression coverage on the gate that actually blocks a push. Recommend: promote at minimum `tests/test_turn_verdicts_bundle.py` (the governance-adjacent mutual-exclusion pin) and `tests/test_audit_tour.py` (the cross-zone regression gate for all four claims at once) into `smoke`, mirroring the reasoning already used for `test_safety_pack.py` and `test_doctrine_prohibitions.py`.
- 🟢 `AA-B5-2` — ADR-0035 build/liveness verdict: full/live, matches design.
- 🟢 `AA-B5-3` — ADR-0039's "Stub-Path `TurnEvent`" is fully discharged, not a residual stub (explicit sabotage-test target from the audit brief — resolved).
- 🟡 `AA-B5-4` — the `correct()`-fallback `tokens`-omission convention in `_stub_response` is correct today but unguarded against a future new call site getting it wrong.
- 🟡 `AA-B5-5` — ADR-0040's documented wire-format field table is stale against the running `serialize_turn_event` (later ADRs added fields, undocumented in ADR-0040 itself); `schema_version` was named as an open question in both ADR-0040 and ADR-0041 and remains unresolved in either.
- 🟢 `AA-B5-6` — ADR-0041's `--show-verdicts` and `FanOutSink` both confirmed live via direct CLI execution during this audit.
- 🟢 `AA-B5-7` — ADR-0042's `core demo audit-tour` confirmed live via direct execution during this audit; `all_claims_supported: true`.

**Zone-level build/liveness summary:** all five ADRs are `full`/`live` — no ghost, scaffolded, dead, or wired-but-unreached findings anywhere in this zone. This is one of the more cleanly-executed sequential arcs found in Batch 1: each ADR's "Open questions deferred to a future ADR" list maps almost 1:1 onto the next ADR actually shipped, and no claim in any of the five ADRs' own text was found to overstate what the code does.
