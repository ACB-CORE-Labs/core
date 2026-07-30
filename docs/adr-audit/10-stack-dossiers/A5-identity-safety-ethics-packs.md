# Stack dossier — A5 · Identity/Safety/Ethics Packs & Checks

**Zone(s):** MG — Governance & Identity (cross-cutting) · zone `governance-identity-safety` (per `docs/assessment/02-layer-taxonomy.md`) | **Tier:** A
**Member ADRs:** ADR-0027 (identity packs), ADR-0029 (safety packs), ADR-0032 (SafetyCheck), ADR-0033 (ethics packs), ADR-0034 (EthicsCheck), ADR-0036 (safety-only typed refusal), ADR-0037 (per-predicate ethics refusal opt-in) — read in that order; 0032/0033/0034 build directly on 0027/0029's contracts, and 0036/0037 build on 0032/0034.
**Dossier author:** Opus 5 (ADR Audit, Batch 1 Phase 3) | **`verified_at` SHA:** `cbfc8ccb`
**Prior evidence adopted, not re-derived:**
- `docs/assessment/10-layer-cards/MG-governance-identity.md` (Phase 2, verified `8927c563`) — MG rated `live-serving` / `fit` with the *enforcement* region `strained`; three open questions, two of which this dossier answers.
- `docs/assessment/30-gap-register.md` **G-9** (CLOSED 2026-07-28, PR-6) — parts (b) governance-bypass pin and (c) safety-pack non-swappability reach. Both adopted as given; §3 records where their closure stops short.
- `docs/assessment/30-gap-register.md` **G-11** (open) — identity enforcement has no stated authorization bar. Adopted; not re-argued.
- `AGENTS.md` **INV-32/INV-34** and `docs/specs/runtime_contracts.md` §wave-only identity — adopted as ratified constraints, not audited here.
- `docs/adr-audit/02-stack-taxonomy.md` row A5 — stack membership as assigned.

---

## 0. Why this is one stack

These seven ADRs are the whole of CORE's *pack-layer governance*: the mechanism by which "who the system is" and "what it will not do" become loadable, ratified data rather than hardcoded Python, and by which that data acquires teeth. The chain is strictly sequential and each link cites its predecessor by number:

- **0027** makes the identity manifold a swappable, ratified pack, and explicitly defers safety axes to a follow-up.
- **0029** takes that deferral: safety packs, always-loaded, never-swappable, fail-closed, composed by set union so an identity pack can add boundaries but never remove one. It in turn defers a *checking* surface ("No safety scoring... a separate ADR").
- **0032** takes *that* deferral: `SafetyCheck`, a registry of per-boundary predicates producing a `SafetyVerdict`. Observational only — refusal deferred again.
- **0033** adds the third pack layer, ethics — swappable like identity, propositional like safety — and defers its check surface.
- **0034** takes that deferral: `EthicsCheck`, deliberately built as a *parallel* surface to `SafetyCheck` rather than a shared one.
- **0036** finally converts observation into behavior: a runtime-checkable safety violation replaces the surface with a deterministic typed refusal. Ethics stays audit-only.
- **0037** reopens ethics narrowly: a pack may opt individual commitments into refusal via `refusal_commitments`, source-tagged in the refusal string.

Read as one arc: *three parallel pack families with deliberately asymmetric mutability, two structurally identical check surfaces, and one refusal policy that only one of the three families can trigger by default.* Nothing in this stack is comprehensible in isolation — 0032's `runtime_checkable` flag only matters because 0036 makes it the refusal gate; 0037 only matters because 0033 chose fallback-not-fail-closed semantics.

## 1. Stack-level claim

> **CORE's alignment posture is structural, not filtered: safety boundaries load unconditionally and fail closed, compose monotonically with swappable identity and ethics layers so no downstream pack can weaken them, and a runtime-checkable violation of a safety boundary deterministically replaces the user-facing surface with a typed refusal.**

Three parts of that sentence are falsifiable against the code. Each is treated FA-1 style below.

### Criterion 1 — fail-closed load

- **Pre-registered criterion:** with `packs/safety/core_safety_axes_v1.json` unreachable, `ChatRuntime` construction must raise and no degraded runtime may be produced.
- **Measurement performed:** direct probe at this SHA (monkeypatched `packs.safety.loader._DEFAULT_SEARCH_PATHS` to an empty directory — repo untouched; script in the session scratchpad, not committed). Result: `SafetyPackError: safety pack 'core_safety_axes_v1' not found ... — refusing to start without an operative safety pack`, raised from `chat/runtime.py:655` and **uncaught** through `ChatRuntime.__init__`. Both CLI catch sites either re-raise (`core/cli.py:140-148`) or `_die` (`core/cli.py:380-386`).
- **Verdict:** **GO** — the never-replaceable/fail-closed claim is true as written, mechanically, end to end.

### Criterion 2 — monotone composition

- **Pre-registered criterion:** for every shipping identity pack, `runtime.identity_manifold.boundary_ids ⊇ safety_pack.boundary_ids`, with no removal path.
- **Measurement performed:** `chat/runtime.py:690-699` computes the union in one expression with no subtraction anywhere; `tests/test_safety_pack.py::TestRuntimeComposition` walks all three identity packs; the pack-swap surface (`--identity`) cannot reach the safety directory (`packs/safety/loader.py:113-124` rejects `/` and `..` in pack ids and `load_safety_pack()` is called with no arguments).
- **Verdict:** **GO**.

### Criterion 3 — refusal is load-bearing

- **Pre-registered criterion:** a runtime-checkable safety violation must actually change `ChatResponse.surface`, and at least one of the five v1 boundaries must be capable of producing that violation from live evidence.
- **Measurement performed:** live turn probe at this SHA. A forced versor breach yields exactly `I cannot proceed — boundary violated: safety:preserve_versor_closure`. But the per-turn verdict on an ordinary turn reads:

  | boundary | `upheld` | `runtime_checkable` | reason (verbatim) |
  |---|---|---|---|
  | `no_fabricated_source` | True | **False** | `allowed_source_shas is empty (allowlist not in use)` |
  | `no_hot_path_repair` | True | **False** | `code-path boundary; enforced by static analysis + code review` |
  | `no_identity_override` | True | True | `identity manifold unchanged` |
  | `no_silent_correction` | True | True | `last refusal was typed` |
  | `preserve_versor_closure` | True | True | `versor_condition=3.709e-08 < threshold=1e-06` |

  Of the three reported runtime-checkable, `no_identity_override` compares two hashes of the same never-reassigned object (`chat/runtime.py` states this in its own docstring: *"the runtime never mutates `identity_manifold` after composition, so before- and after-turn hashes are equal by construction"*), and `no_silent_correction` reads `_last_refusal_was_typed`, which is initialized `True` and assigned `True` at both of its two write sites and **`False` nowhere in the repository**. Neither can fail.
- **Verdict:** **partial GO / NO-GO on generality.** The refusal *machinery* is genuine and reachable. But exactly **one of five** v1 safety boundaries can produce a live violation, and it is a numerical-geometry guard already independently enforced (`formation/runner.py:76`) rather than a behavioral safety property. The stack's headline — "safety boundaries stop bad output" — is, at runtime today, "the versor-closure invariant stops bad output." The other four boundaries are labels with either an honest `runtime_checkable=False` (two) or a dishonest `runtime_checkable=True` (two).

## 2. Per-ADR sections

---

### ADR-0027 — Identity Packs — Load-Bearing, Swappable, Ratified

**Audit ID (if a numbering collision):** none | **Family (if phased):** none
**Zone / stack:** MG · `governance-identity-safety` / A5 | **Tier:** A
**ADR status (as recorded in the file):** Accepted (2026-05-17) — Phases 1–7 complete | **ADR date:** 2026-05-17
**Card author:** Opus 5 | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary

- **Decision made:** replace the hardcoded `_default_identity_manifold()` with a content-addressed pack format at `packs/identity/<pack_id>.json` loaded through `packs.identity.loader.load_identity_manifold`, ship three ratified v1 packs, expose a `--identity` CLI flag, and route all pack mutation through the reviewed teaching path.
- **Alternatives explicitly rejected:** leave identity hardcoded; adopt the `axis_a.yaml` descriptive schema as the pack format; allow runtime identity mutation via the chat surface; multi-purpose language-as-identity packs.
- **Artifacts the ADR claims will exist:**
  - `packs/identity/<pack_id>.json` schema (`value_axes`, `boundary_ids`, `alignment_threshold`, `pack_id`, `version`, `description`, `mastery_report_sha256`)
  - `packs.identity.loader.load_identity_manifold(pack_id, *, search_paths=None)`
  - `core.config.DEFAULT_IDENTITY_PACK = "default_general_v1"`
  - three v1 packs: `default_general_v1`, `precision_first_v1`, `generosity_first_v1`
  - `--identity <pack_id>` on `core pulse`, `core chat`, `core trace`
  - `<pack_id>.mastery_report.json` companions + load-time seal verification
  - `scripts/ratify_identity_packs.py`
  - removal of all hardcoded `ValueAxis` from `chat/runtime.py`
  - identity-pack mutation via `teaching/review.py`

#### 2. Implementation cross-reference

| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| Pack JSON schema + bounds | yes | `packs/identity/loader.py:169-260+` | envelope, `schema_version` pin, `_MIN_AXES`, per-axis bounds |
| `load_identity_manifold` | yes | `packs/identity/loader.py` (494 L) | signature matches, `search_paths` present |
| `DEFAULT_IDENTITY_PACK` | yes | `core/config.py` → imported `chat/runtime.py:653` | |
| Three v1 packs | yes | `packs/identity/{default_general_v1,precision_first_v1,generosity_first_v1}.json` | each with `.mastery_report.json` |
| `--identity` on `core chat` | yes | `core/cli.py:2461` via `_add_runtime_policy_args`, attached at `:2485` | also `always_on`, `trace`, `oov` |
| `--identity` on `core trace` | yes | `core/cli.py:2622` | |
| **`--identity` on `core pulse`** | **no** | `core/cli.py:3444-3461`; `scripts/run_pulse.py:277-285` | `pulse` subparser does **not** call `_add_runtime_policy_args`; neither entry point accepts the flag |
| Mastery-report seal verification | yes | `packs/identity/loader.py:198-245` | SHA match + `verify_seal` + `ratified` flag |
| `scripts/ratify_identity_packs.py` | yes | `scripts/ratify_identity_packs.py` | |
| No hardcoded `ValueAxis` in runtime | yes | `chat/runtime.py` — zero matches for `ValueAxis` or `_default_identity_manifold` | ADR's own verification bullet 1 satisfied |
| Identity mutation via `teaching/review.py` | yes | `teaching/review.py:36,198,294-296` (`_IDENTITY_MARKERS` → `REJECTED_IDENTITY`) | |
| `--list-identity-packs` | yes | `core/cli.py:2487` | (an ADR-0029 aside, satisfied here) |

**Build axis:** **full** — every claimed artifact exists and is bounds-checked, with one exception (the `core pulse` flag row), which is a surface omission rather than a missing mechanism.

#### 3. Liveness / integration

- On the live serving path: `chat/runtime.py:654` calls `load_identity_manifold(identity_pack_id)` in `ChatRuntime.__init__`, uncaught. The resulting manifold drives `PersonaMotor`/`CharacterProfile` (`:714`), `drive_gradients` (`:712`), `IdentityCheck` scoring every turn (`:2914,2929,2945`), and `surface_preferences` (`:1811`). Verified by construction, not docstring.
- **Sabotage test:** stub the loader to return a zero-axis manifold and `_build_axes` refuses (`_MIN_AXES` bound); delete the pack file and `IdentityPackError` propagates out of `__init__`. Swapping `default_general_v1` → `precision_first_v1` measurably changes `identity_manifold.boundary_ids` (adds `no_overstatement`, pinned in `tests/test_safety_pack.py`) and the axis set. Removal is observable. **Not decoration.**
- **Liveness axis:** **live**.

#### 4. Design fidelity — pillars and axioms

| Pillar | Verdict | Citation |
|---|---|---|
| I. Mechanical Sympathy | Honors | Pack is read once at startup into an immutable manifold; no per-turn I/O. |
| II. Semantic Rigor | Honors | §Decision 7 draws a hard line — "Safety axes are NOT identity packs" — before the safety ADR existed; the term "identity pack" is given one meaning and kept. |
| III. Third Door | Honors | Rejects both visible options (hardcode / let users edit Python) for reviewed, ratified, content-addressed data. |

| Axiom | Verdict | Citation |
|---|---|---|
| 1. Geometry-First | Honors | Pack carries `direction` vectors and `weight`, not prose — identity stays a subspace of the versor field. |
| 2. Field-State | Honors | Manifold is consumed as a field constraint (`GradientField`, `PersonaMotor`), not an object registry. |
| 3. Propagation-over-Mutation | Honors | §Decision 6 + Alternative 3 rejected: no runtime write path to `packs/identity/`. |
| 4. Dual-Correction | n/a | No forward operator introduced. |
| 5. Reconstruction-over-Storage | Honors | §Governance Cross-Reference: axes loaded into structured runtime manifolds from verified checksums. |
| 6. Compilation-Last | Honors | JSON → dataclass at load; no premature kernel. |
| 7. Reality-over-Inheritance | Tension | Alternative 2's rejection is correct, but the ADR itself concedes (§Negative) that `--identity X` "will not yet produce a measurably different surface" — the abstraction shipped ahead of the capability it justifies. ADR-0028 closed most of this. |

#### 5. Build fidelity — does the code match the decision?

Matches on substance. Two divergences:

1. **`core pulse --identity` was never wired.** ADR-0027 Decision §4 names `core pulse` first; Phase 4's exit criterion is literally *"`core pulse --identity precision_first_v1 "..."` runs without error"*; and two of the six §Verification bullets are `core pulse --identity` invocations. The `pulse` subparser (`core/cli.py:3444`) omits `_add_runtime_policy_args`. Two ratified verification criteria are therefore untestable as written.
2. `ratified: false` tagging — §Decision 5 says unratified packs "are loadable but tagged `ratified: false` in the resulting manifold and excluded from production deployments by the runtime's startup gate." The loader instead **refuses** unratified packs in production mode outright (`packs/identity/loader.py:206-212`). Stricter than specified, which is the right direction, but the ADR text no longer describes the code.

**Build-fidelity axis:** **partial drift** — mechanism matches, two named verification criteria do not.

#### 6. Continuity

- **Whitepaper:** no contradiction. §III axioms 1/2 are honored by the direction-vector schema.
- **Yellowpaper:** no contradiction found.
- **Other ADRs:** cleanly extended by ADR-0028 (surface wiring — its own explicitly-named P3 follow-up) and ADR-0029 (its explicitly-deferred safety layer). Superseded in part by **ADR-0244 §3 / INV-32** (wave-only fail-closed identity scoring) and **ADR-0246** — but that supersession is about `IdentityCheck`, not the pack format, and `docs/assessment/02-layer-taxonomy.md:48` already records it. ADR-0033's three-layer table misdescribes this ADR's failure mode (see AA-A5-10).
- **Continuity axis:** **clean**.

#### 7. Necessity / generality

1. **Necessity:** irreducible as a *concept*. Without a loadable identity manifold the geometric alignment story has no per-deployment surface at all, and the identity-divergence eval reverts to a mock (the ADR's own problem #2, now genuinely fixed — `evals/identity_divergence/pack_runner.py:23,27` loads the three real packs).
2. **Reducibility:** the manifold itself reduces to L0 geometry (`ValueAxis` directions in the versor field) — that is by design and correct. The *loader* does not reduce to anything at L0/L1.
3. **Extensibility:** the loader is one of at least five in `packs/` carrying the identical `_resolve_search_paths` / `_find_pack` / `_read_json` / `_validate_envelope` / `_validate_ratification` quintet plus a bespoke `CORE_ALLOW_UNRATIFIED_<X>` env var and error class (identity 494 L, safety 259 L, ethics 409 L, register 608 L; anchor-lens and rhetorical-style carry a two-function subset). See AA-A5-8.

**Necessity/generality axis:** **irreducible** (the decision) / **generalization-candidate** (the loader implementation).

#### 8. Fitness / value

- `docs/assessment/10-layer-cards/MG-governance-identity.md` §Design vs build cites `packs/identity/loader.py` on the confirmed live-serving path.
- `evals/identity_divergence/pack_runner.py` runs all three ratified pack ids — the ADR's stated purpose (make the divergence claim testable against real packs) is discharged.
- `evals/adversarial_identity/` (contract + six result sets, v1–v3) measures identity-override rejection deterministically — though via `teaching/review.py`, not the pack loader.
- `docs/PROGRESS.md` records the ADR-0027–0044 pack block as landed.

**Fitness axis:** **evidenced** — `evals/identity_divergence/pack_runner.py`, `evals/adversarial_identity/results/`, MG layer card.

#### 9. Findings raised

- **AA-A5-15 🟡** — `core pulse --identity` does not exist; two of ADR-0027's six ratified verification criteria are untestable as written (§2, §5).
- **AA-A5-10 🟢** — ADR-0033's comparison table records identity's failure mode as "fall back to default"; the code fails closed (§6, and see ADR-0033's card).
- **AA-A5-8 🔵** — pack-loader duplication across ≥5 families (§7).

#### 10. Evidence sources actually consulted

`docs/adr/ADR-0027-identity-packs.md` (full); `packs/identity/loader.py`; `chat/runtime.py:600-740, 2900-3020`; `core/cli.py:2396-2500, 2622, 3444-3461`; `scripts/run_pulse.py:270-290`; `teaching/review.py`; `packs/identity/*.json`; `evals/identity_divergence/pack_runner.py`; `evals/adversarial_identity/contract.md` + `results/`; MG layer card; `docs/PROGRESS.md`; live probe of `ChatRuntime` construction and one turn.

---

### ADR-0029 — Safety Packs — Always-Loaded, Never-Replaceable Boundaries

**Audit ID:** none | **Family:** none
**Zone / stack:** MG · `governance-identity-safety` / A5 | **Tier:** A
**ADR status:** Accepted (2026-05-17) | **ADR date:** 2026-05-17
**Card author:** Opus 5 | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary

- **Decision made:** a separate `packs/safety/` layer holding exactly one pack that loads unconditionally at startup, cannot be swapped by CLI/config/env, composes into the runtime manifold by set union only, and fails closed on every error path — a CORE installation without an operative safety pack refuses to start.
- **Alternatives explicitly rejected:** none named as a numbered list; the ADR argues against a `--safety-pack` flag in §Negative ("a runtime that lets you swap the safety layer is not a safety layer") and against putting `value_axes` in the safety schema.
- **Artifacts the ADR claims will exist:**
  - `packs/safety/core_safety_axes_v1.json` with the five closed boundaries
  - `packs.safety.loader.load_safety_pack` + `SafetyPackError(RuntimeError)`
  - composition at `ChatRuntime` startup: `boundary_ids = identity ∪ safety`
  - fail-closed on: missing file, malformed JSON, empty `boundary_ids`, duplicate id, path-traversal id, and (production) empty/missing/mismatched/unsealed mastery report
  - `CORE_ALLOW_UNRATIFIED_SAFETY=1` bypassing *only* seal verification
  - `scripts/ratify_safety_pack.py` (idempotent)
  - shipping SHA `ee1249acdf8c273aeb656d803c37ef915e536d85f177f5cc18c6e2f6c995ce29`
  - no new CLI flag; `--list-identity-packs` excludes safety
  - `tests/test_safety_pack.py::TestRuntimeComposition` walking all three identity packs

#### 2. Implementation cross-reference

| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `core_safety_axes_v1.json`, five boundaries | yes | `packs/safety/core_safety_axes_v1.json` | boundary set verified identical to the ADR table |
| `SafetyPackError(RuntimeError)` | yes | `packs/safety/loader.py:23-29` | docstring names the fail-closed rationale |
| `load_safety_pack` | yes | `packs/safety/loader.py:57-99` | `require_ratified=None` → production unless env |
| Composition = union | yes | `chat/runtime.py:690-699` | `identity | safety | ethics`, no subtraction |
| Missing file fails closed | yes | `packs/safety/loader.py:120-124` | probe-confirmed |
| Malformed JSON fails closed | yes | `:127-139` | |
| Empty `boundary_ids` fails closed | yes | `:213-217` | |
| Duplicate boundary fails closed | yes | `:226-229` | |
| Path-traversal id rejected | yes | `:113-115` | |
| Ratification: empty/missing/mismatch/unsealed | yes | `:161-210` | uses `formation.hashing.verify_seal` |
| `CORE_ALLOW_UNRATIFIED_SAFETY` bypasses only the seal | yes | `:164-171` | the other five failure paths run before/after it regardless |
| `scripts/ratify_safety_pack.py` | yes | `scripts/ratify_safety_pack.py` | |
| Shipping SHA matches ADR | yes | pack `mastery_report_sha256` == report `report_sha256` == `ee1249ac…ce29`, `ratified: true` | ADR §Shipping pack SHA is accurate |
| No `--safety-pack` flag | yes (absent, as decided) | `core/cli.py` — no match | |
| `TestRuntimeComposition` over 3 identity packs | yes | `tests/test_safety_pack.py:127-168` | 15 tests total |

**Build axis:** **full** — every claimed artifact exists, including the recorded SHA, which still verifies at this SHA fourteen months of commits later.

#### 3. Liveness / integration

- `chat/runtime.py:655` — `self.safety_pack = load_safety_pack()`, no arguments, no `try`. Consumed at `:694` (composition) and at both `safety_check.check(..., self.safety_pack)` call sites (`:2431`, `:2981`).
- Two mechanical pins guard the wiring, both from the G-9 closure: `tests/test_doctrine_prohibitions.py:169-188` (AST — every function constructing a `TurnVerdicts` must also invoke `safety_check.check`) and `:190-199` (every `safety_check.check` call must pass `self.safety_pack`, so a bypass cannot substitute a pack). `tests/test_doctrine_prohibitions.py:255-266` keeps `tests/test_safety_pack.py` on the smoke gate.
- **Sabotage test (executed, not reasoned):** with the safety-pack search path emptied, `ChatRuntime(config=RuntimeConfig())` raises `SafetyPackError` out of `__init__`. **The system genuinely refuses to start.** It does not silently degrade, does not fall back, does not construct a runtime with `safety_pack=None`. This closes MG's open question *"Is safety-pack non-swappability mechanically enforced or loader-conventional?"* — it is mechanically enforced at the load site and pinned at the call sites.
- **Liveness axis:** **live**.

#### 4. Design fidelity — pillars and axioms

| Pillar | Verdict | Citation |
|---|---|---|
| I. Mechanical Sympathy | Honors | One startup read; the per-turn cost is a frozenset union already materialized. |
| II. Semantic Rigor | Honors | The exception-base choice is itself a semantic statement — `RuntimeError` not `ValueError` — and the loader docstring says why. |
| III. Third Door | Honors | §Negative: "a runtime that lets you swap the safety layer is not a safety layer." Rejects both configurable-safety and hardcoded-safety. |

| Axiom | Verdict | Citation |
|---|---|---|
| 1. Geometry-First | n/a | Explicitly propositional; the ADR says so and keeps `value_axes` out of the schema. |
| 2. Field-State | Tension | Boundaries land in `IdentityManifold.boundary_ids`, a set of opaque strings — the one place in MG where state is a label registry rather than a field. The ADR is honest about it. |
| 3. Propagation-over-Mutation | Honors | Union, never replace; no runtime write path. |
| 4. Dual-Correction | n/a | |
| 5. Reconstruction-over-Storage | Honors | Boundaries reconstructed from a verified manifest each boot. |
| 6. Compilation-Last | Honors | |
| 7. Reality-over-Inheritance | Honors | The abstraction earns its place: the union rule is what makes downstream identity packs safe to accept. |

#### 5. Build fidelity

Matches, with one honest gap the ADR itself pre-declares: `CORE_ALLOW_UNRATIFIED_SAFETY=1` is "operational discipline, not enforced by code." At this SHA there is still no pin, startup assertion, telemetry field, or verdict evidence entry recording that the runtime booted on an unratified safety pack — an operator who sets it gets a fully-functioning runtime with a silently unverified floor, and nothing downstream can tell.

**Build-fidelity axis:** **matches** (the escape hatch is disclosed in the decision, so it is not drift — but see AA-A5-12).

#### 6. Continuity

- **Whitepaper / Yellowpaper:** no contradiction. The five boundaries restate `AGENTS.md` doctrine (`no_hot_path_repair`, `no_identity_override`, `no_silent_correction` map to the Teaching-safety and typed-failure sections; `preserve_versor_closure` to Architecture Invariant I).
- **Prior/later ADRs:** takes ADR-0027 §Decision 7's explicit deferral. Its own deferral ("No safety scoring... a separate ADR") is taken by ADR-0032; the refusal deferral by ADR-0036. Extended by ADR-0033 (ethics joins the union). Clean chain, every link cited by number in both directions.
- **`no_silent_correction` vs INV-34:** the boundary and the invariant state the same law. INV-34 is enforced in `core/cognition/fail_closed.py` and cited across `chat/deduction_surface.py:54`, `chat/curriculum_surface.py:23,108`, `core/cognition/surface_resolution.py:48,192`. The safety-pack *predicate* for the same law is inert (see ADR-0032's card) — the law is enforced, just not here.
- **Continuity axis:** **clean**.

#### 7. Necessity / generality

1. **Necessity:** irreducible. This is the one mechanism in the stack whose removal is immediately observable (probe above) and whose invariant — monotone composition — is what makes ADR-0027's swappability safe to ship at all. Without 0029, 0027 is a hole.
2. **Reducibility:** nothing at L0/L1 provides "an always-present, non-overridable constraint set." Set union over a frozenset is trivially available; the *governance* is not.
3. **Extensibility:** the loader shares the duplicated quintet (AA-A5-8). The *schema* is deliberately and correctly distinct from identity's.

**Necessity/generality axis:** **irreducible**.

#### 8. Fitness / value

- G-9(c), CLOSED 2026-07-28: the fail-closed contract was already well-pinned; PR-6 fixed its *reach* by promoting `tests/test_safety_pack.py` onto the pre-push gate. Four sabotages observed red.
- G-9(b), CLOSED: the AST bypass pin. Both adopted, not re-derived.
- MG card §Evidence: "would-fail-if-absent: **yes**."
- `docs/PROGRESS.md:769` records the ADR as landed.

**Fitness axis:** **evidenced** — G-9(b)(c) closure record, `tests/test_doctrine_prohibitions.py`, `tests/test_safety_pack.py` (on the gate), plus this dossier's own startup probe.

#### 9. Findings raised

- **AA-A5-12 🟢** — `CORE_ALLOW_UNRATIFIED_SAFETY=1` leaves no trace: no pin, no startup assert, no telemetry, no verdict evidence field records that the floor booted unverified (§5).
- **AA-A5-8 🔵** — loader duplication (§7).

#### 10. Evidence sources actually consulted

`docs/adr/ADR-0029-safety-packs.md` (full); `packs/safety/loader.py` (full); `packs/safety/core_safety_axes_v1.json` + `.mastery_report.json` (SHA re-verified); `chat/runtime.py:600-740`; `tests/test_safety_pack.py` (full); `tests/test_doctrine_prohibitions.py:150-266`; `core/cli.py:126-148, 373-386`; `core/cli_test.py:237`; `docs/assessment/30-gap-register.md` G-9; MG layer card; **executed startup sabotage probe** (safety pack unreachable → `SafetyPackError` from `ChatRuntime.__init__`).

---

### ADR-0032 — SafetyCheck — Structural Surface for Safety-Pack Boundaries

**Audit ID:** none | **Family:** none
**Zone / stack:** MG · `governance-identity-safety` / A5 | **Tier:** A
**ADR status:** Accepted (2026-05-17) | **ADR date:** 2026-05-17
**Card author:** Opus 5 | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary

- **Decision made:** `SafetyCheck` is a registry of named predicates, one per boundary id, producing a `SafetyVerdict`. Observational only — it does not refuse and is not auto-invoked in the turn loop at v1. Predicates that cannot be evaluated from runtime evidence must report `runtime_checkable=False` rather than passing silently.
- **Alternatives explicitly rejected:** a predicate that "*silently* reported `upheld=True` for `no_hot_path_repair`… would be a small lie, exactly the kind of thing CLAUDE.md forbids." Also rejected: making unknown boundaries an error at v1 (deferred to a deployment `require_runtime_checkable=True` flag).
- **Artifacts the ADR claims will exist:** `SafetyContext` (7 fields), `SafetyCheckResult`, `SafetyVerdict`, `SafetyCheck.__init__/register/check`, five default predicates, unknown-boundary fallback, defensive boundary-id rebinding, `ChatRuntime.safety_check`, `tests/test_safety_check.py` (20 tests).

#### 2. Implementation cross-reference

| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `SafetyContext` — 7 fields | yes | `packs/safety/check.py:38-75` | field-for-field identical to the ADR's API block |
| `SafetyCheckResult` | yes | `:78-86` | |
| `SafetyVerdict` | yes | `:89-97` | lex order enforced at `:144` |
| `SafetyCheck.register` | yes | `:126-128` | |
| `SafetyCheck.check` | yes | `:130-176` | |
| `_predicate_versor_closure` | yes | `:182-211` | genuinely runtime-checkable |
| `_predicate_no_fabricated_source` | yes | `:214-250` | **never runtime-checkable in practice** — see §3 |
| `_predicate_no_silent_correction` | yes | `:253-265` | **cannot fail** — see §3 |
| `_predicate_no_identity_override` | yes | `:268-293` | **cannot fail** — see §3 |
| `_predicate_no_hot_path_repair` | yes | `:296-314` | honest `runtime_checkable=False` |
| Unknown-boundary fallback | yes | `:146-152` | exact reason string as specified |
| Defensive rebinding | yes | `:155-164` | |
| `ChatRuntime.safety_check` | yes | `chat/runtime.py:720` | |
| `tests/test_safety_check.py` | yes | 20 tests, as claimed | **in `tests/full_only_baseline.txt:673` — no curated suite** |

**Build axis:** **full** — the surface is built exactly as specified, field for field.

#### 3. Liveness / integration

- **Auto-invocation:** ADR-0032 says the turn loop "does not auto-invoke it at v1." That is no longer true — ADR-0035 wired both surfaces in, and at this SHA `safety_check.check` runs on **both** runtime response paths (`chat/runtime.py:2431`, `:2981`). Neither 0032 nor 0034 carries a supersession banner.
- **Sabotage test — per predicate, measured on a live turn:**
  - `preserve_versor_closure`: `field_state` is populated with a real `versor_condition(result.final_state.F)` (`:2974-2976`, `:2424-2426`). Forcing `versor_condition=1.0` yields `I cannot proceed — boundary violated: safety:preserve_versor_closure`. **Live and load-bearing.**
  - `no_hot_path_repair`: `runtime_checkable=False` by design and honestly reported. **Correctly inert.**
  - `no_fabricated_source`: `allowed_source_shas` is **not populated at either call site**. The predicate short-circuits at `packs/safety/check.py:216-222` to `runtime_checkable=False` on every turn. Removing it changes nothing. **Decoration** — though its `runtime_checkable=False` reporting keeps it honest in the audit trail.
  - `no_identity_override`: both hashes derive from `self.identity_manifold`, which is assigned exactly once (`chat/runtime.py:690`) and never reassigned. The runtime's own docstring (`:329-337`) states the hashes are "equal by construction." Reports `runtime_checkable=True`. **Cannot fail; reports live evidence it does not have.**
  - `no_silent_correction`: reads `self._last_refusal_was_typed`, initialized `True` (`:725`) and assigned `True` at `:2448` and `:3029` — **`False` appears at no site in the repository** (grep across `*.py`). Reports `runtime_checkable=True`. **Cannot fail.**
- Net: `SafetyVerdict.runtime_checkable_count` reads **3** on every ordinary turn; the honest count is **1**.
- **Liveness axis:** **live** as a surface (auto-invoked, feeds `TurnVerdicts` and the refusal builder) / **wired-but-unreached** for four of its five predicates.

#### 4. Design fidelity — pillars and axioms

| Pillar | Verdict | Citation |
|---|---|---|
| I. Mechanical Sympathy | Honors | Five pure predicates over a frozen context; O(boundaries) per turn. |
| II. Semantic Rigor | **Honors as written / violated as built** | The ADR's §"What's runtime-checkable" is the single clearest statement of the discipline in the corpus — "A predicate that *silently* reported `upheld=True`… would be a small lie." Two shipped predicates do precisely that, one row above in the same table. |
| III. Third Door | Honors | Neither "check everything" nor "check nothing" — check what is checkable and say so. |

| Axiom | Verdict | Citation |
|---|---|---|
| 1. Geometry-First | n/a | Explicitly acknowledged: "the parallel is shape-only, not mechanism." |
| 2. Field-State | Tension | Verdict is a tuple of booleans over string ids — the least field-like structure in MG. |
| 3. Propagation-over-Mutation | Honors | `check` is pure; the only mutation is `register`. |
| 4. Dual-Correction | Tension | The surface is forward-only by decision (observational). ADR-0036 supplies the conjugate later; at 0032's own scope there is none. |
| 5. Reconstruction-over-Storage | Honors | Verdict recomputed per turn, never stored. |
| 6. Compilation-Last | Honors | |
| 7. Reality-over-Inheritance | **Tension** | The five predicates were built because the pack declares five boundaries, not because five runtime observables existed. Four had no evidence source and were shipped anyway; two of those were dressed as if they did. |

#### 5. Build fidelity

The API matches the ADR byte-for-byte. The *semantics* of `runtime_checkable` do not: the ADR defines it as "did we observe a real violation" (a definition ADR-0036 then makes the refusal gate), and the code reports `True` for two predicates whose negative branch no runtime path can reach. The ADR's own table anticipated `no_silent_correction` as "bookkeeping by the runtime" — the bookkeeping was built one-directional.

**Build-fidelity axis:** **partial drift** — structure matches; the honesty contract that is the ADR's central argument is broken by two of its own five defaults.

#### 6. Continuity

- **Whitepaper / Yellowpaper:** no contradiction.
- **ADRs:** extends ADR-0029 (takes its "No safety scoring" deferral) and cites ADR-0010's `IdentityCheck` as the shape precedent. **Superseded in part by ADR-0035** on the auto-invocation point, with no banner in 0032. Consumed by ADR-0036 (`runtime_checkable` becomes the refusal gate) and mirrored by ADR-0034.
- **Continuity axis:** **superseded-cleanly, unannotated** — the supersession is real, correct, and recorded only in the superseding document.

#### 7. Necessity / generality

1. **Necessity:** the *surface* is necessary — ADR-0036 could not exist without a typed verdict to gate on. The *predicate set* is not: one of five carries evidence.
2. **Reducibility:** `preserve_versor_closure` duplicates a check the substrate already owns — `formation/runner.py:27,76` hard-halts on `versor_condition >= VERSOR_HALT_THRESHOLD` with the same 1e-6 constant, and `core/cognition/geometric_coherence.py:46` states the same law. The safety-pack predicate is a third statement of an L0 invariant. `no_identity_override` duplicates `teaching/review.py::_IDENTITY_MARKERS`, which is where identity-override attacks are actually rejected (`evals/adversarial_identity/contract.md`). `no_silent_correction` duplicates INV-34, enforced in `core/cognition/fail_closed.py`. **Three of five boundaries restate constraints already enforced elsewhere, more strongly.**
3. **Extensibility:** `SafetyCheck` and `EthicsCheck` are the same class twice (AA-A5-7).

**Necessity/generality axis:** **reducible-to-{`formation/runner.py` versor halt, `teaching/review.py` identity rejection, `core/cognition/fail_closed.py` INV-34}** for three of five predicates; the *registry surface itself* is a **generalization-candidate** jointly with `EthicsCheck`.

#### 8. Fitness / value

- No eval lane measures safety-boundary violations. The typed-refusal string appears in **no** file under `evals/`, no results JSON, and no telemetry — only in `docs/adr/ADR-0036`, `ADR-0037`, `ADR-0042`.
- MG card §Capacity credits "five safety boundaries present in every manifold" — presence, not firing.
- `tests/test_safety_check.py` (20 tests) exercises every predicate's negative branch *at the unit level*, which is why the tautology is invisible: the unit tests construct `SafetyContext(last_refusal_was_typed=False)` directly (`tests/test_safety_check.py:122`), a state the runtime never produces.

**Fitness axis:** **no evidence found** beyond unit tests — no lane, no result, no recorded firing.

#### 9. Findings raised

- **AA-A5-1 🟡** — `no_silent_correction` reports `runtime_checkable=True` but cannot fail: `_last_refusal_was_typed` is never assigned `False` anywhere (§3).
- **AA-A5-2 🟡** — `no_identity_override` reports `runtime_checkable=True` but is tautological by the runtime's own docstring (§3).
- **AA-A5-3 🟡** — `no_fabricated_source` never runs: `allowed_source_shas` unpopulated at both call sites (§3).
- **AA-A5-6 🟡** — `tests/test_safety_check.py` is in no curated suite (§2).
- **AA-A5-7 🔵** — `SafetyCheck`/`EthicsCheck` mechanical duplication (§7).
- **AA-A5-11 🟢** — "does not auto-invoke" is superseded by ADR-0035 without a banner (§6).
- **AA-A5-13 🟢** — no recorded firing of a safety verdict or typed refusal outside unit tests (§8).

#### 10. Evidence sources actually consulted

`docs/adr/ADR-0032-safety-check-surface.md` (full); `packs/safety/check.py` (full); `chat/runtime.py:318-360, 2390-2460, 2960-3035`; repo-wide grep for `_last_refusal_was_typed` and `allowed_source_shas`; `tests/test_safety_check.py`; `tests/full_only_baseline.txt`; `core/cli_test.py`; `formation/runner.py:27,76`; `core/cognition/fail_closed.py`; `teaching/review.py`; `evals/adversarial_identity/contract.md`; repo-wide grep for the typed-refusal string; **executed live-turn verdict dump**.

---

### ADR-0033 — Ethics Packs — Swappable Domain Commitments

**Audit ID:** none | **Family:** none
**Zone / stack:** MG · `governance-identity-safety` / A5 | **Tier:** A
**ADR status:** Accepted (2026-05-17) | **ADR date:** 2026-05-17
**Card author:** Opus 5 | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary

- **Decision made:** a third pack layer at `packs/ethics/`, swappable like identity but propositional like safety, contributing `commitment_ids` monotonically to the manifold's `boundary_ids`. Failure semantics follow *identity*, not safety: a missing/malformed requested pack falls back to the default; only if both fail does `EthicsPackError` (a `ValueError`) propagate.
- **Alternatives explicitly rejected:** cramming commitments into the identity pack (identity is geometric); smuggling them into application code (unauditable). Fail-closed ethics is explicitly rejected: "A deployment that mis-specifies its ethics pack should land on the general default, not refuse to start."
- **Artifacts the ADR claims will exist:** the v1 schema (`domain` from a closed 6-set, `commitment_ids`, `commitment_descriptions`), `packs/ethics/default_general_ethics_v1.json` with five commitments, `load_ethics_pack`, `EthicsPackError(ValueError)`, `CORE_ALLOW_UNRATIFIED_ETHICS=1`, `DEFAULT_ETHICS_PACK`, runtime composition, `scripts/ratify_ethics_pack.py`, `tests/test_ethics_packs.py` (20 tests), default pack SHA `81fc9b61c828…`.

#### 2. Implementation cross-reference

| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `EthicsPack` dataclass | yes | `packs/ethics/loader.py:58-82` | plus ADR-0037's `refusal_commitments` and ADR-0038's `hedge_commitments` |
| `EthicsPackError(ValueError)` | yes | `:37-45` | docstring names the identity-not-safety analogy |
| `load_ethics_pack` | yes | `:84-120+` | |
| `_ALLOWED_DOMAINS` 6-set | yes | `:52-54` | `{general, medical, legal, financial, robotics, custom}` |
| `DEFAULT_ETHICS_PACK` | yes | `:48` | |
| `default_general_ethics_v1.json`, 5 commitments | yes | verified: 5 `commitment_ids`, ratified, `refusal_commitments: []` | |
| Runtime composition (union) | yes | `chat/runtime.py:695` | |
| Fallback-to-default semantics | yes | `chat/runtime.py:657-663` | re-raises only when the requested id *is* the default |
| `CORE_ALLOW_UNRATIFIED_ETHICS` | yes | `packs/ethics/loader.py:259-268` | |
| `scripts/ratify_ethics_pack.py` | yes | | |
| `tests/test_ethics_packs.py` | yes | 20 tests as claimed | **in `full_only_baseline.txt:403` — no curated suite** |
| `config.ethics_pack` | yes | `core/config.py:52-53` | |
| **`--ethics` CLI flag** | **no** | `core/cli.py` — zero matches | `ethics_pack` is reachable only programmatically; contrast `--identity` at `core/cli.py:2461` and `--list-identity-packs` at `:2487` |

Additionally found (not claimed by this ADR, but material to it): four *domain* packs beyond the default — `engineering_ethics_v1`, `legal_ethics_v1`, `medical_clinical_ethics_v1` (ADR-0044), `research_ethics_v1`.

**Build axis:** **full** for the mechanism; the per-deployment *selection surface* the ADR's central claim depends on is **absent** from the CLI.

#### 3. Liveness / integration

- `chat/runtime.py:656-664` loads the pack; `:695` unions its commitments into the manifold; `ethics_check.check(..., self.ethics_pack)` runs at `:2441` and `:2991`; `build_refusal_surface(..., self.ethics_pack)` at `:2442`, `:2992`; `should_inject_hedge(..., self.ethics_pack)` at `:3105`.
- **Sabotage test — measured, and this is the stack's most serious result.** Of the five shipped ethics packs, **three cannot load in production mode**: `engineering_ethics_v1`, `legal_ethics_v1`, `research_ethics_v1` all have `mastery_report_sha256: ""` and no companion report. All three declare non-empty `refusal_commitments` (`legal`: `no_legal_advice`, `no_outcome_prediction`; `research`: `no_fabrication`, `no_plagiarism`; `engineering`: `no_sign_off`) and non-empty `hedge_commitments`. Executed probe:

  ```
  requested=legal_ethics_v1     -> loaded=default_general_ethics_v1  refusal=[]
  requested=research_ethics_v1  -> loaded=default_general_ethics_v1  refusal=[]
  requested=medical_clinical_ethics_v1 -> loaded=medical_clinical_ethics_v1
                                          refusal=['no_dosing_recommendation',
                                                   'no_emergency_triage_authority']
  ```

  A deployment that configures `ethics_pack="legal_ethics_v1"` — intending refusals on legal advice and outcome prediction — receives, **with no exception, no log line, no warning, and no telemetry field**, the general default with zero refusal commitments. ADR-0033 says the runtime "warns implicitly via the `ethics_pack_id` attribute"; "implicitly" here means an attribute nobody reads. Nothing on the serving path, in `TurnVerdicts`, or in `core chat --show-verdicts` distinguishes "you got the pack you asked for" from "you got the floor."

  This is a **silent correction** — the exact failure mode `core_safety_axes_v1`'s `no_silent_correction` boundary exists to forbid, and the boundary reports `upheld=True, runtime_checkable=True` on every turn of the degraded session (AA-A5-1).
- Secondary defect, currently masked: `engineering` and `research` are **not** in `_ALLOWED_DOMAINS`; both packs would fail `_validate_domain` even after ratification. The ratification check fires first, so the domain error is never seen.
- **Liveness axis:** **live**.

#### 4. Design fidelity — pillars and axioms

| Pillar | Verdict | Citation |
|---|---|---|
| I. Mechanical Sympathy | Honors | Startup load, frozenset union. |
| II. Semantic Rigor | Honors as written | §Schema's "commitment vs boundary" paragraph is careful and correct; §Negative even records the residual vocabulary risk (both end up in one `boundary_ids` set). |
| III. Third Door | Tension | The third layer is a genuine third door for domain pledges — but §Negative's own "Three layers is more than two" concedes the cost, and the failure-mode asymmetry it defends (fall back, not fail closed) is exactly what produced §3's silent degradation. |

| Axiom | Verdict | Citation |
|---|---|---|
| 1. Geometry-First | n/a | Explicitly propositional. |
| 2. Field-State | Tension | Same string-set critique as ADR-0029. |
| 3. Propagation-over-Mutation | Honors | Monotone composition; no runtime write path. |
| 4. Dual-Correction | n/a | |
| 5. Reconstruction-over-Storage | Honors | |
| 6. Compilation-Last | Honors | |
| 7. Reality-over-Inheritance | **Tension** | The layer was built parallel to safety's structure *by analogy* — same loader shape, same ratification quintet, same env-var pattern — rather than because ethics demanded a different structure. The one structural difference chosen (fallback-not-fail-closed) is the one that produced a defect. |

#### 5. Build fidelity

Mechanism matches the decision. Two divergences:

1. **The comparison table's Identity row is wrong about the code.** ADR-0033 §"Position in the three-layer hierarchy" records Identity's failure mode as "Fall back to default." The runtime does **not** fall back for identity: `chat/runtime.py:654` calls `load_identity_manifold` with no `try`, so `IdentityPackError` propagates out of `__init__` exactly as `SafetyPackError` does. Identity fails closed; only ethics falls back. The table's central asymmetry argument is therefore stated against a fictional identity behavior.
2. **"Swappable per deployment" has no deployment-facing switch.** No `--ethics`, no `--list-ethics-packs`, no `CORE_ETHICS_PACK` env var. Identity got all three affordances; ethics got a dataclass field.

**Build-fidelity axis:** **partial drift**.

#### 6. Continuity

- **Whitepaper / Yellowpaper:** no contradiction.
- **ADRs:** extends 0027 and 0029 by explicit citation; its own "No EthicsCheck surface" deferral is taken by ADR-0034; `refusal_commitments` added by ADR-0037; `hedge_commitments` by ADR-0038; `medical_clinical_ethics_v1` is ADR-0044's worked example.
- **Against ADR-0029:** no contradiction — the union is monotone and ethics cannot displace a safety boundary. But the two layers now sit in one `boundary_ids` set with no provenance tag, which the ADR itself flags (§Negative, "vocabulary risk… deferred to a future ADR") and which is still deferred at this SHA.
- **Continuity axis:** **clean**, with one unreconciled document/code divergence (the Identity row) recorded as AA-A5-10.

#### 7. Necessity / generality

1. **Necessity:** the *niche* is real — the ADR's argument that domain pledges fit neither the geometric identity layer nor the universal safety floor is sound. But at this SHA the layer's only load-bearing output is the two `medical_clinical_ethics_v1` refusal commitments; the default pack contributes five commitment strings to a set and one live-firing observational predicate.
2. **Reducibility:** structurally, an ethics pack **is** a safety pack with a different mutability policy and a `domain` string. Compare the schemas: both are `{pack_id, version, description, schema_version, domain?, mastery_report_sha256, <ids>, <descriptions>}`; both compose by union into the same field; both ratify through the *same* `identity_anchor` template with the same canned override counters. The genuine differences are three: the exception base class, the fallback-vs-fail-closed branch, and the opt-in refusal subset. All three are *policy fields*, not structural distinctions.
3. **Extensibility:** a single `PropositionalPack` type carrying `{ids, descriptions, domain, mutability: FAIL_CLOSED|FALLBACK, refusal_optin, hedge_optin}` would subsume `SafetyPack` and `EthicsPack` without weakening safety — safety would simply be the pack whose `mutability=FAIL_CLOSED` and whose `refusal_optin` is "all". That framing would also have made §3's defect structurally impossible to express as an accident.

**Necessity/generality axis:** **generalization-candidate** — the layer's *concept* is justified; its *implementation* is a policy variant of ADR-0029's, built as a separate mechanism.

#### 8. Fitness / value

- `tests/test_ethics_packs.py` (20) + `tests/test_medical_clinical_ethics_pack.py` (8) — all off the curated gate.
- `docs/PROGRESS.md:770,780` records ADR-0033 and ADR-0044 as landed.
- MG card names `packs/ethics/check.py` on the live path.
- No eval lane measures commitment violations or pack-selection correctness. Nothing would have caught §3's silent downgrade.

**Fitness axis:** **no evidence found** beyond unit tests and the PROGRESS ledger.

#### 9. Findings raised

- **AA-A5-4 🔴** — requesting an unratified domain ethics pack silently downgrades to the no-refusal default; three shipped packs carrying real `refusal_commitments` are in this state (§3).
- **AA-A5-5 🟡** — no `--ethics` / `--list-ethics-packs` CLI surface; "swappable per deployment" is programmatic-only (§2, §5).
- **AA-A5-10 🟢** — ADR-0033's three-layer table misstates identity's failure mode (§5).
- **AA-A5-14 🟢** — `engineering` / `research` are outside `_ALLOWED_DOMAINS`; masked by the ratification check firing first (§3).
- **AA-A5-6 🟡** — ethics test files in no curated suite (§2).

#### 10. Evidence sources actually consulted

`docs/adr/ADR-0033-ethics-packs.md` (full); `packs/ethics/loader.py`; all five `packs/ethics/*_v1.json` (parsed: ratification state, domain, opt-in lists); `chat/runtime.py:653-700, 2430-2445, 2980-2995, 3100-3110`; `core/config.py:52-53`; `core/cli.py` (grep for `--ethics`); `tests/full_only_baseline.txt`; `docs/PROGRESS.md`; MG layer card; **executed pack-selection probe across all five shipped packs, at loader and `ChatRuntime` level**.

---

### ADR-0034 — EthicsCheck — Structural Surface for Ethics-Pack Commitments

**Audit ID:** none | **Family:** none
**Zone / stack:** MG · `governance-identity-safety` / A5 | **Tier:** A
**ADR status:** Accepted (2026-05-17) | **ADR date:** 2026-05-17
**Card author:** Opus 5 | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary

- **Decision made:** `EthicsCheck`, a registry of per-commitment predicates producing an `EthicsVerdict`, observational at v1, not auto-invoked — **built as a parallel surface rather than folded into `SafetyCheck`**, on the grounds that safety verdicts are floor violations and ethics verdicts are pledge failures, and "conflating them in a single surface would obscure the structural difference."
- **Alternatives explicitly rejected:** folding ethics into `SafetyCheck` (§"Why a parallel surface rather than a shared one"); a unified cross-surface verdict object (scope limit).
- **Artifacts the ADR claims will exist:** `EthicsContext` (9 fields), `EthicsCheckResult`, `EthicsVerdict`, `EthicsCheck.__init__/register/check`, five default predicates, unknown-commitment fallback, defensive rebinding, `ChatRuntime.ethics_check`, `tests/test_ethics_check.py` (27 tests).

#### 2. Implementation cross-reference

| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `EthicsContext` — 9 fields | yes | `packs/ethics/check.py:41-86` | matches the ADR's API block |
| `EthicsCheckResult` / `EthicsVerdict` | yes | `:88-97` / `:99-116` | |
| `EthicsCheck.register` / `.check` | yes | `:118-186` | |
| `_predicate_acknowledge_uncertainty` | yes | `:191-229` | **fires live** — see §3 |
| `_predicate_defer_high_stakes` | yes | `:230-276` | flags never supplied → inert |
| `_predicate_disclose_limitations` | yes | `:277-321` | runtime-checkable, supplied |
| `_predicate_no_manipulation` | yes | `:322-341` | honest `runtime_checkable=False` |
| `_predicate_respect_user_autonomy` | yes | `:342-392` | flags never supplied → inert |
| Unknown-commitment fallback | yes | `:146-152`-equivalent | |
| Defensive rebinding | yes | | |
| `ChatRuntime.ethics_check` | yes | `chat/runtime.py:721` | |
| `tests/test_ethics_check.py` | yes | 27 tests as claimed | **`full_only_baseline.txt:402` — no curated suite** |

**Build axis:** **full**.

#### 3. Liveness / integration

- Auto-invoked on both runtime paths (`chat/runtime.py:2441`, `:2991`) — again contradicting this ADR's own "does not auto-invoke," superseded by ADR-0035 without a banner.
- **Sabotage test — measured on an ordinary turn** ("what is a triangle", unknown term, ungrounded surface):

  | commitment | `upheld` | `runtime_checkable` | reason (verbatim) |
  |---|---|---|---|
  | `acknowledge_uncertainty` | **False** | **True** | `alignment_score=0.000 below hedge_threshold_soft=0.500 but no hedge emitted` |
  | `defer_high_stakes_to_human_review` | True | False | `high_stakes_topic flag not supplied` |
  | `disclose_limitations` | True | True | `ungrounded response disclosed its limitation` |
  | `no_manipulation` | True | False | `aggregate commitment; enforced by realizer design…` |
  | `respect_user_autonomy` | True | False | `prescribed_single_answer flag not supplied` |

  Two of five carry live evidence; one of those **fires a violation on an ordinary turn**, giving `EthicsVerdict.upheld=False` as the *normal* state for the most common turn shape (ungrounded / unknown term). Because `refusal_commitments` is empty in the default pack and `hedge_commitments` likewise, the violation has no consequence — precisely ADR-0037's designed default. Removing `EthicsCheck` entirely would change no user-visible byte under the shipping configuration.
- **Liveness axis:** **live** as a surface / **wired-but-unreached** as an enforcement mechanism under every shipping pack except `medical_clinical_ethics_v1`.

#### 4. Design fidelity — pillars and axioms

| Pillar | Verdict | Citation |
|---|---|---|
| I. Mechanical Sympathy | Honors | Pure predicates, O(commitments). |
| II. Semantic Rigor | Honors | The floor-vs-pledge distinction is precisely drawn and worth keeping. |
| III. Third Door | **Violates** | §"Why a parallel surface" names the temptation ("same shape, same registry pattern, same fallback semantics") and resolves it by *building the second copy*. Neither visible option was rejected in favor of a first-principles third: parameterize the mechanism, keep the verdict types distinct. The stated goal — "an auditor benefits from reading two distinct verdicts" — is a property of the *verdict types*, which one generic registry would preserve unchanged. |

| Axiom | Verdict | Citation |
|---|---|---|
| 1. Geometry-First | n/a | |
| 2. Field-State | Tension | Same string/boolean critique. |
| 3. Propagation-over-Mutation | Honors | |
| 4. Dual-Correction | Tension | Observational-only by decision; the conjugate arrives in ADR-0037. |
| 5. Reconstruction-over-Storage | Honors | |
| 6. Compilation-Last | Honors | |
| 7. Reality-over-Inheritance | **Violates** | "The shape of the surface is already known and tested (SafetyCheck is the precedent). Building the parallel keeps the architecture coherent." That is inheritance-by-symmetry as the stated justification — the axiom's exact target. The measured result: with `Safety→Ethics` and `boundary→commitment` renamed, the two class bodies differ by **two comment lines and one field name** (`violated_boundaries` / `violated_items`). |

#### 5. Build fidelity

The code matches the decision exactly, including the duplication the decision chose. The one drift is that four of five default predicates depend on `EthicsContext` flags (`high_stakes_topic`, `recommended_human_review`, `prescribed_single_answer`, `presented_options_count`) that **no runtime call site populates** — `chat/runtime.py:2432-2440` and `:2982-2990` supply only `alignment_score`, `hedge_threshold_soft`, `hedge_emitted`, `grounded_in_evidence`, `disclosure_emitted`. The ADR's per-commitment table promises "Yes (when flags supplied)"; the flags are never supplied.

**Build-fidelity axis:** **partial drift**.

#### 6. Continuity

- **Whitepaper §III axiom 7 / README pillar III:** in tension as scored above — this is the one member ADR whose *rationale section* argues against a pillar rather than merely failing to honor it.
- **ADRs:** extends 0033 (takes its "No EthicsCheck surface" deferral); mirrors 0032; superseded on auto-invocation by ADR-0035 (unannotated); consumed by 0037.
- **Continuity axis:** **superseded-cleanly, unannotated**.

#### 7. Necessity / generality

1. **Necessity:** the *verdict* is necessary for ADR-0037 to have a gate. The *second registry implementation* is not.
2. **Reducibility:** measured — normalized diff of `EthicsCheck` (`packs/ethics/check.py:118-190`) against `SafetyCheck` (`packs/safety/check.py:109-177`) with `Safety↔Ethics` and `boundary↔commitment` substituted yields three hunks: one docstring word, one comment pair, one field name. The `check()` loop, the lex ordering, the unknown-id fallback, the rebinding branch, and the aggregate construction are character-identical.
3. **Extensibility:** one `PackCheck` generic over `(item_field_name, ids_accessor)` returning a parameterized verdict absorbs both, at roughly 45% of the combined 740 lines, with `SafetyVerdict`/`EthicsVerdict` retained as distinct types so ADR-0034's auditor argument survives intact. Pairs directly with AA-A5-8 (the loader quintet) into a single MG consolidation cluster.

**Necessity/generality axis:** **generalization-candidate** (strongest in the stack; the ADR's own §"Why a parallel surface" is the evidence).

#### 8. Fitness / value

- 27 unit tests, off the gate. No eval lane. No recorded ethics verdict outside tests.
- The one live-firing predicate fires on the most common turn shape with no consequence — measurable, but measuring nothing anyone acts on.

**Fitness axis:** **no evidence found**.

#### 9. Findings raised

- **AA-A5-7 🔵** — `SafetyCheck` and `EthicsCheck` are the same mechanism twice; ADR-0034 §"Why a parallel surface" argues a semantic case and delivers a mechanical duplication (§4, §7).
- **AA-A5-9 🟡** — `acknowledge_uncertainty` violates on ordinary ungrounded turns; four of five predicates' flags are never populated (§3, §5).
- **AA-A5-11 🟢** — auto-invocation claim superseded without a banner (§6).
- **AA-A5-6 🟡** — off the curated gate (§2).

#### 10. Evidence sources actually consulted

`docs/adr/ADR-0034-ethics-check-surface.md` (full); `packs/ethics/check.py`; `packs/safety/check.py`; **normalized textual diff of the two `Check` class bodies**; `chat/runtime.py:2432-2445, 2982-2995`; `tests/full_only_baseline.txt`; **executed live-turn ethics verdict dump**.

---

### ADR-0036 — Safety-Only Typed Refusal Policy

**Audit ID:** none | **Family:** none
**Zone / stack:** MG · `governance-identity-safety` / A5 | **Tier:** A
**ADR status:** Accepted (2026-05-17) | **ADR date:** 2026-05-17
**Card author:** Opus 5 | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary

- **Decision made:** a `SafetyVerdict` containing at least one `runtime_checkable=True, upheld=False` result replaces `ChatResponse.surface` with a deterministic typed refusal carrying the violated boundary ids in lex order. Ethics violations remain audit-only. `walk_surface` and `articulation_surface` are preserved as evidence.
- **Alternatives explicitly rejected:** hedge injection (would blur alignment-driven hedging against predicate-driven refusal, making audit ambiguous); re-articulation via planner retry (no refusal-bias hint surface exists; retry with unchanged inputs is a no-op); wiring ethics into refusal (would let pack-swappers change refusal behavior by editing JSON — "exactly the coupling we want to avoid"); refusing on `runtime_checkable=False` results (would refuse on architectural absence, not behavioral violation).
- **Artifacts the ADR claims will exist:** `chat/refusal.py` with `TYPED_REFUSAL_PREFIX`, `build_refusal_surface`, `violated_runtime_checkable`, `is_typed_refusal`; invocation on both the main turn path and `_stub_response`; `_last_refusal_was_typed = True` bookkeeping; `TurnEvent.surface` carrying the refusal on the main path; `tests/test_safety_refusal.py` (20 tests).

#### 2. Implementation cross-reference

| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `chat/refusal.py` | yes | 177 L | |
| `TYPED_REFUSAL_PREFIX` | yes (**changed**) | `chat/refusal.py:31` | now `"I cannot proceed — boundary violated: "` — ADR-0036's `"…safety boundary violated: "` was generalized by ADR-0037, which says so explicitly |
| `build_refusal_surface` | yes | `:71-102` | signature widened to `(safety_verdict, ethics_verdict=None, ethics_pack=None)` by ADR-0037; the single-arg ADR-0036 form still works |
| `violated_runtime_checkable` | yes | `:36-43` | lex-sorted |
| `is_typed_refusal` | yes | `:117-119` | |
| Main-path invocation | yes | `chat/runtime.py:2992-2994` | |
| Stub-path invocation | yes | `chat/runtime.py:2442-2444` | |
| `_last_refusal_was_typed = True` | yes | `:2448`, `:3029` | never set `False` (AA-A5-1) |
| `walk_surface` / `articulation_surface` preserved | yes | `:3027-3034` reassigns only `response_surface` | evidence discipline honored |
| `TurnEvent.surface` = refusal | yes | `:2655` `refusal_reason=refusal_surface if refusal_emitted else ""` + `:3206-3208` | |
| Only `runtime_checkable=True` refuses | yes | `chat/refusal.py:105-110` | the gate is exactly `runtime_checkable and not upheld` |
| `tests/test_safety_refusal.py` | yes | 20 tests as claimed | **`full_only_baseline.txt:674` — no curated suite** |

**Build axis:** **full**.

#### 3. Liveness / integration

- Reached on the live serving path on every turn, both paths. `build_refusal_surface` is a pure function with no I/O, as specified.
- **Sabotage test:** forcing `versor_condition=1.0` through a real `SafetyCheck` against the shipping pack produces exactly `I cannot proceed — boundary violated: safety:preserve_versor_closure` (executed). If `build_refusal_surface` were stubbed to return `None`, that output would revert to the walk surface — **a real, observable behavioral difference**. This is the one place in the stack where the pack layer can stop output.
- **But:** the *only* reachable trigger is `preserve_versor_closure` (per ADR-0032's card, §3). Under every shipping ethics pack except `medical_clinical_ethics_v1`, and with the other four safety predicates unable to fail, the refusal path fires **only** when the Cl(4,1) versor invariant breaks — a numerical-substrate fault, not a content-safety event. The ADR's framing ("a way to actually stop the runtime from emitting bad output") is true of the mechanism and not yet true of any behavioral boundary.
- **Liveness axis:** **live** (mechanism) / **wired-but-unreached** (as a content-safety control).

#### 4. Design fidelity — pillars and axioms

| Pillar | Verdict | Citation |
|---|---|---|
| I. Mechanical Sympathy | Honors | "Cheap. One pure function call per turn." Accurate. |
| II. Semantic Rigor | Honors | Constant prefix + lex-ordered ids: "Audit consumers detect refusals by prefix… not by NLP." Determinism is stated as a contract and holds. |
| III. Third Door | Honors | Rejects both visible options (hedge / re-articulate) with a specific reason each, and picks typed refusal because it is the only one that preserves replay-equivalence. |

| Axiom | Verdict | Citation |
|---|---|---|
| 1. Geometry-First | n/a | |
| 2. Field-State | n/a | |
| 3. Propagation-over-Mutation | Honors | The refusal changes *selection*, not evidence — `walk_surface`/`articulation_surface` are untouched. This is the cleanest expression of the evidence-preservation discipline in the stack. |
| 4. Dual-Correction | **Honors** | This ADR *is* the conjugate that ADR-0032/0034 lacked: observation gains its corrective counterpart. |
| 5. Reconstruction-over-Storage | Honors | Refusal is recomputed from the verdict, never stored. |
| 6. Compilation-Last | Honors | |
| 7. Reality-over-Inheritance | Honors | §Negative names the missing `audit_only` flag and declines to build it before it is needed. |

#### 5. Build fidelity

Matches, with the prefix constant and the function arity both changed by ADR-0037 — changes 0037 documents explicitly, so this is clean supersession, not drift. One ADR-declared limit persists: stub-path refusal emits no `TurnEvent` (`chat/runtime.py:2442-2448` has no turn-log write), still open as ADR-0036's deferred question 3.

**Build-fidelity axis:** **matches**.

#### 6. Continuity

- **Whitepaper / Yellowpaper:** no contradiction; the replay-equivalence argument aligns with ADR-0225's replay clause.
- **ADRs:** consumes 0032's `runtime_checkable`, 0034's verdict, 0035's wiring. **Amended by ADR-0037** (prefix generalized, ethics admitted under opt-in) — 0037 states this and back-compat is preserved. The `no_silent_correction` bookkeeping it introduces is the one-directional flag behind AA-A5-1.
- **Continuity axis:** **superseded-cleanly** (by 0037, explicitly and correctly).

#### 7. Necessity / generality

1. **Necessity:** irreducible. This is the stack's only forward operator with behavioral consequence; without it the entire pack layer is annotation. The MG card's `strained` enforcement verdict is exactly about how narrow its trigger set is, not about whether it exists.
2. **Reducibility:** nothing at L0/L1 provides "replace the selected surface deterministically on a typed verdict." Adjacent but distinct: `core/cognition/fail_closed.py` (INV-34) refuses *inside* the cognition pipeline with its own typed reasons; `RefusalReason`/`InnerLoopExhaustion` (ADR-0024) refuse on exhaustion. Three refusal vocabularies now coexist — `chat/refusal.py`'s prefix strings, `core/cognition/fail_closed.py`'s conditions, and `RefusalReason` — with `docs/refusal-taxonomy.md` and `evals/refusal_taxonomy/` as the reconciliation surface. Worth a cross-stack look with B5/ADR-0024, not a finding here.
3. **Extensibility:** ADR-0037 already generalized it once (source tags); ADR-0038 reuses the same opt-in validator for hedging. The design absorbed two extensions without a shape change — evidence the surface was cut at the right joint.

**Necessity/generality axis:** **irreducible**.

#### 8. Fitness / value

- 20 unit tests, off the gate.
- `core eval cognition` baseline preserved (ADR §Verification) — i.e. the refusal path fires zero times across the cognition lane, which is the intended no-regression result and also the fitness ceiling.
- Repo-wide grep: the typed-refusal string occurs in **no** eval fixture, result file, telemetry sample, or handoff — only in ADR-0036/0037/0042 prose. No recorded firing outside unit tests at any SHA in the tree.
- ADR-0036's deferred question 5 (`core chat --show-verdicts`) **did** land (`core/cli.py:2495+`), so an operator can at least see verdicts interactively.

**Fitness axis:** **no evidence found** of a real firing; mechanism verified by unit test and by this dossier's forced-violation probe.

#### 9. Findings raised

- **AA-A5-13 🟢** — no recorded typed refusal anywhere in `evals/`, results, or telemetry (§8).
- (Inherits **AA-A5-1** — the `no_silent_correction` bookkeeping this ADR introduces is write-True-only.)

#### 10. Evidence sources actually consulted

`docs/adr/ADR-0036-safety-refusal-policy.md` (full); `chat/refusal.py` (full); `chat/runtime.py:2440-2460, 2990-3035, 3200-3215`; `tests/test_safety_refusal.py`; `tests/full_only_baseline.txt`; `core/cli.py:2495`; repo-wide grep for the refusal prefix across `*.json`/`*.jsonl`/`*.md`; **executed forced-violation probe**.

---

### ADR-0037 — Per-Predicate Ethics Refusal Opt-In

**Audit ID:** none | **Family:** none
**Zone / stack:** MG · `governance-identity-safety` / A5 | **Tier:** A
**ADR status:** Accepted (2026-05-17) | **ADR date:** 2026-05-17
**Card author:** Opus 5 | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary

- **Decision made:** an optional `refusal_commitments` field on the ethics pack schema. A commitment contributes to typed refusal only when its predicate fired `runtime_checkable=True, upheld=False` **and** its id appears in `refusal_commitments`. The default pack ships empty — "Audit-only is the floor; opt-in is the ceiling." The refusal prefix is generalized and ids become source-tagged (`safety:` / `ethics:`).
- **Alternatives explicitly rejected:** a global ethics-refuses switch (ADR-0036's stated objection); maintaining a parallel API for the old prefix ("no in-tree consumer existed").
- **Artifacts the ADR claims will exist:** `EthicsPack.refusal_commitments`; loader validation (optional, list-of-strings, subset of `commitment_ids`, no duplicates) via a shared `_validate_opt_in_subset`; generalized `TYPED_REFUSAL_PREFIX`; source tags; `violated_runtime_checkable_ethics`; re-ratified default pack; `tests/test_ethics_refusal_opt_in.py` (16 tests).

#### 2. Implementation cross-reference

| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `EthicsPack.refusal_commitments` | yes | `packs/ethics/loader.py:81` | `frozenset[str] = frozenset()` |
| `_validate_opt_in_subset` (shared) | yes | `packs/ethics/loader.py:117-120+` | also used for ADR-0038's `hedge_commitments` at `:82` |
| Generalized prefix | yes | `chat/refusal.py:31` | `"I cannot proceed — boundary violated: "` |
| Source tags | yes | `chat/refusal.py:32-33, 99-102` | `safety:` / `ethics:`, lex-sorted **after** tagging |
| `violated_runtime_checkable_ethics` | yes | `:46-68` | returns `()` immediately when the opt-in set is empty |
| Both conditions required | yes | `:57-68` | `runtime_checkable and not upheld` **and** `cid in opt_in` |
| Default pack empty opt-in | yes | verified: `refusal_commitments: []` | |
| Re-ratified default pack | yes | pack `mastery_report_sha256` set, companion report present and self-sealing | |
| ADR-0036 back-compat | yes | `build_refusal_surface(safety_verdict)` still valid — `chat/refusal.py:71-96` defaults both new params | |
| `tests/test_ethics_refusal_opt_in.py` | yes | 16 tests as claimed | **`full_only_baseline.txt:404` — no curated suite** |

**Build axis:** **full**.

#### 3. Liveness / integration

- Live on both runtime paths via `build_refusal_surface(safety_verdict, ethics_verdict, self.ethics_pack)` (`chat/runtime.py:2442`, `:2992`).
- **Sabotage test:** under the shipping default pack, `refusal_commitments` is empty, so `violated_runtime_checkable_ethics` returns `()` at its first branch (`chat/refusal.py:60-61`) and the ethics arm contributes nothing. Removing the entire ADR-0037 arm would produce byte-identical output under the default configuration — **decoration by design**, which is precisely the decision ("Audit-only remains the default. An operator who clones the default pack and deploys gets ADR-0036 behavior unchanged"). The mechanism only becomes load-bearing under `medical_clinical_ethics_v1` (`no_dosing_recommendation`, `no_emergency_triage_authority`) — the single shipping pack that both ratifies and opts in.
- **The three unratified domain packs (§ADR-0033 card, AA-A5-4) are exactly the case where this ADR's mechanism is silently defeated:** each declares refusal opt-ins, none can load, and the fallback delivers an empty opt-in set with no signal.
- **Liveness axis:** **wired-but-unreached** under the default pack; **live** under `medical_clinical_ethics_v1`.

#### 4. Design fidelity — pillars and axioms

| Pillar | Verdict | Citation |
|---|---|---|
| I. Mechanical Sympathy | Honors | Early return on empty opt-in; no per-turn cost added in the default case. |
| II. Semantic Rigor | Honors | Source tags exist specifically to prevent id-namespace collision between two sibling pack types — a precise fix for a precise ambiguity. |
| III. Third Door | Honors | Rejects both "ethics never refuses" (ADR-0036) and "ethics refuses" (a global switch) for per-commitment opt-in validated at load time. |

| Axiom | Verdict | Citation |
|---|---|---|
| 1. Geometry-First | n/a | |
| 2. Field-State | n/a | |
| 3. Propagation-over-Mutation | Honors | Opt-in list is load-time data; no runtime mutation. |
| 4. Dual-Correction | Honors | Completes ADR-0034's missing conjugate for the ethics layer. |
| 5. Reconstruction-over-Storage | Honors | |
| 6. Compilation-Last | Honors | |
| 7. Reality-over-Inheritance | Honors | The shared `_validate_opt_in_subset` was *actually* generalized and reused by ADR-0038 rather than copied — the one place in this stack where a second use produced a shared abstraction instead of a parallel one. Worth naming as the counter-example to AA-A5-7. |

#### 5. Build fidelity

Matches. Load-time typo rejection ("silent typos would be catastrophic given the behavioral consequences") is implemented as specified. §Negative's own risk statement — "the opt-in list is JSON, which means it sits inside the swappable layer… an operator can flip refusal on/off by editing a file" — is accurate and mitigated exactly as claimed (ratification round-trip + schema validation + load-time unknown-id error).

What the ADR did not anticipate: the ratification round-trip it relies on as the mitigation is also the thing that **silently disables** the opt-in when a pack ships unratified, because ADR-0033's fallback semantics swallow the failure. The mitigation and the defect share a mechanism.

**Build-fidelity axis:** **matches**.

#### 6. Continuity

- **Whitepaper / Yellowpaper:** no contradiction.
- **ADRs:** amends ADR-0036 (prefix, arity) explicitly and preserves back-compat; extends ADR-0033's schema and ADR-0034's verdict; its own deferred question 1 is taken by ADR-0038 (`hedge_commitments`, with mutual exclusion validated at load time — `chat/refusal.py:125-143` reads the sibling field). Its deferred question 3 ("should the medical pack ship with `defer_high_stakes_to_human_review` opted in?") is now answerable — ADR-0044's medical pack exists and opts in two *different* commitments.
- **Continuity axis:** **clean**.

#### 7. Necessity / generality

1. **Necessity:** irreducible given ADR-0033's swappability. If ethics packs can refuse at all, per-commitment opt-in is the minimum granularity that keeps a pack author from silently changing global refusal behavior. The alternative ADR-0036 rejected is strictly worse.
2. **Reducibility:** the opt-in-subset validator is genuinely shared (`_validate_opt_in_subset` serves both `refusal_commitments` and `hedge_commitments`) — no duplication to consolidate here.
3. **Extensibility:** the same pattern would extend to safety if a future pack ever needed an `audit_only` boundary (ADR-0036 §Negative's open item) — and the fact that safety's version doesn't exist is correct, since opting a safety boundary *out* is what ADR-0029 forbids.

**Necessity/generality axis:** **irreducible**.

#### 8. Fitness / value

- 16 unit tests, off the gate. `tests/test_medical_clinical_ethics_pack.py` (8) exercises the one shipping pack that uses the mechanism — also off the gate.
- ADR-0037's own §Context premises the opt-in on "empirical violation rates for individual ethics commitments" becoming available. **No such calibration exists at this SHA** — no eval lane counts commitment violations. Meanwhile the one commitment that fires live (`acknowledge_uncertainty`) violates on ordinary ungrounded turns, so a pack author following the ADR's guidance without data would produce near-universal refusal.
- `docs/PROGRESS.md:773` records the ADR as landed.

**Fitness axis:** **no evidence found**; the empirical premise the ADR names as its own precondition is unmet.

#### 9. Findings raised

- **AA-A5-4 🔴** — (raised on ADR-0033, lands here) the unratified-domain-pack fallback silently empties this ADR's opt-in set with no signal (§3, §5).
- **AA-A5-9 🟡** — the "empirical violation rates" premise is unmet, and the one live-firing commitment has a near-1 violation rate on the commonest turn shape (§8).
- **AA-A5-6 🟡** — off the curated gate (§2).

#### 10. Evidence sources actually consulted

`docs/adr/ADR-0037-per-predicate-ethics-refusal.md` (full); `chat/refusal.py` (full); `packs/ethics/loader.py:58-125, 250-275`; all five `packs/ethics/*_v1.json`; `chat/runtime.py:2442, 2992, 3105`; `tests/full_only_baseline.txt`; `docs/PROGRESS.md`; **executed pack-selection and live-verdict probes**.

---

## 3. Stack-level synthesis

### Internal consistency

The seven ADRs are unusually well-linked: every member cites its predecessor by number, every deferral is explicitly named and then explicitly taken by the next ADR, and no member silently contradicts an earlier one. Three seams:

1. **ADR-0032 and ADR-0034 both assert "the turn loop does not auto-invoke."** ADR-0035 wired both in; at this SHA both surfaces run on both runtime paths. Neither ADR carries a supersession banner, so a reader who consults 0032/0034 for the current contract gets a false picture — the H-8 failure mode (`31-hindrance-audit.md`) applied to two safety-relevant documents. **AA-A5-11.**
2. **ADR-0033's three-layer table misstates ADR-0027's failure mode.** The table's whole point is the mutability asymmetry, and its Identity row ("Fall back to default") describes behavior the code does not have — identity fails closed, exactly like safety. **AA-A5-10.**
3. **ADR-0032's central honesty argument is contradicted by two of its own five predicates.** The ADR's most quotable line ("A predicate that *silently* reported `upheld=True`… would be a small lie") is stated one row above two predicates that do exactly that. Not a contradiction *between* ADRs — a contradiction between an ADR and its own build. **AA-A5-1, AA-A5-2.**

### Cumulative build state

Every claimed artifact in all seven ADRs exists in code. There are no ghosts. But *built* and *reachable* diverge sharply:

| Layer | Built | Reachable / load-bearing today |
|---|---|---|
| Identity pack load + composition | full | **live** — swapping packs changes the manifold, scoring, and drives |
| Safety pack load + fail-closed | full | **live** — verified by executed startup sabotage |
| Monotone union composition | full | **live** — pinned across all three identity packs |
| `SafetyCheck` surface | full | **live**, but 1 of 5 predicates can produce a violation |
| Ethics pack load + composition | full | **live**, with a silent-downgrade path (AA-A5-4) |
| `EthicsCheck` surface | full | **live**, 2 of 5 predicates evidenced, 0 consequential under the default pack |
| Typed refusal (0036) | full | **live**, single reachable trigger (versor closure) |
| Ethics refusal opt-in (0037) | full | **inert under 4 of 5 shipping packs**, live under 1 |

So: **8/8 built, 8/8 wired, and roughly 2/8 doing observable work under the shipping configuration.** The chain did not stall — it completed, and then most of its predicates turned out to have no evidence source. That is a different pathology from a half-built stack, and it is the one the sabotage test is designed to find.

The single sharpest number: `SafetyVerdict.runtime_checkable_count` reads **3** on every ordinary turn. The honest count is **1**.

### Cumulative necessity/generality read

**The stack introduces one coherent mechanism and builds it three times.**

Measured, not asserted:

- **The two `Check` surfaces are the same class.** Normalized for `Safety↔Ethics` and `boundary↔commitment`, `SafetyCheck` (`packs/safety/check.py:109-177`) and `EthicsCheck` (`packs/ethics/check.py:118-190`) differ in **two comment lines and one field name**. Registry, lex ordering, unknown-id fallback, defensive rebinding, aggregate construction: character-identical.
- **The loaders share a five-function skeleton.** `_resolve_search_paths` / `_find_pack` / `_read_json` / `_validate_envelope` / `_validate_ratification` appear in identical form in identity (494 L), safety (259 L), ethics (409 L) and register (608 L) loaders, with anchor-lens (422 L) and rhetorical-style (425 L) carrying a subset — each with its own `CORE_ALLOW_UNRATIFIED_<X>` env var, its own `<X>PackError`, and its own copy of the SHA-match + `verify_seal` + `ratified` triple.
- **The three pack *schemas* are two schemas.** Identity is genuinely different (geometric: `value_axes` with directions and weights). Safety and ethics are the same propositional envelope differing in three *policy fields*: the exception base class, the fallback-vs-fail-closed branch, and the presence of opt-in subsets.

**Answer to the consolidation question posed for this stack:** the three pack types do **not** all share enough structure for one mechanism — identity is geometric and belongs apart. **Safety and ethics do.** One `PropositionalPack` carrying `{ids, descriptions, domain, mutability: FAIL_CLOSED|FALLBACK, refusal_optin, hedge_optin}` plus one `PackCheck` generic over the item-id field would subsume ADR-0029+0033's loaders and ADR-0032+0034's surfaces at roughly half the current line count — **without weakening safety**, because safety is simply the instance with `mutability=FAIL_CLOSED` and no opt-out. ADR-0034 pre-empted this consolidation with an argument ("safety verdicts are floor violations; ethics verdicts are pledge failures") that defends keeping the *verdict types* distinct — which a generic registry preserves — not the *mechanism*. It is the clearest Reality-over-Inheritance (Axiom 7) violation found in Batch 1: the ADR names the symmetry ("same shape, same registry pattern, same fallback semantics"), calls building the second copy "keeps the architecture coherent," and ships it.

Counter-example worth recording so the consolidation report is fair: **ADR-0037 did it right.** `_validate_opt_in_subset` was written once and reused by ADR-0038 for `hedge_commitments`. The stack is capable of generalizing; 0034 chose not to.

Two further consolidation observations that reach outside this stack:

- **Three of the five v1 safety boundaries restate constraints enforced more strongly elsewhere.** `preserve_versor_closure` duplicates `formation/runner.py:27,76` (same 1e-6 constant) and `core/cognition/geometric_coherence.py:46`; `no_identity_override` duplicates `teaching/review.py::_IDENTITY_MARKERS` (which is what `evals/adversarial_identity/` actually measures); `no_silent_correction` duplicates INV-34 in `core/cognition/fail_closed.py`. The safety pack is, in three of five cases, a *label registry pointing at enforcement that lives elsewhere* — which is defensible as an audit surface but should be described that way rather than as enforcement.
- **Three refusal vocabularies now coexist**: `chat/refusal.py`'s tagged prefix strings, `core/cognition/fail_closed.py`'s typed conditions (INV-34), and ADR-0024's `RefusalReason`/`InnerLoopExhaustion`. `docs/refusal-taxonomy.md` + `evals/refusal_taxonomy/` are the reconciliation surface. Flagged for a cross-stack look with B5 and the ADR-0024 chain; not a finding against A5.

### Blast radius if this stack's central claim is wrong

The claim has three parts (§1) and they fail independently:

- **If fail-closed load were wrong** (it is not — verified): catastrophic. G-9(c), the MG card's `live-serving` rating, ADR-0225's governance cross-references on 0027/0029, and every downstream deployment claim would need re-verdicting. **Verified GO, so no cascade.**
- **If monotone composition were wrong** (it is not — verified): ADR-0027's entire swappability premise collapses, plus B4 (0028/0030/0031/0038 surface wiring) and ADR-0044's medical pack. **Verified GO, so no cascade.**
- **The part that is weak — "safety boundaries stop bad output"** — has a real blast radius, and it is documentary rather than architectural:
  - **MG layer card** (`10-layer-cards/MG-governance-identity.md`) §Capacity says "five safety boundaries present in every manifold." *Present* is exact and defensible; any downstream summary that reads it as *enforced* is wrong for four of the five. The card's Judgment already rates enforcement `strained` and warns "the distinction between scoring and refusing must be stated precisely wherever this capability is described externally" — this dossier extends that warning from identity scoring to safety predicates. **Recommend a note on the MG card, not a re-verdict.**
  - **B5 (ADR-0035/0039/0040/0041/0042 — turn-loop verdict surfacing and audit telemetry)** consumes `SafetyVerdict.runtime_checkable_count` and the per-result `runtime_checkable` flags as audit evidence. If that count is inflated 3:1, every verdict readout, telemetry sink, and audit-tour demo built on it (ADR-0042 quotes the refusal string directly) inherits the inflation. **B5 should be re-checked against AA-A5-1/2 when it is audited.**
  - **B4 (ADR-0028/0030/0031/0038)** depends on identity/ethics surface preferences and hedge injection, which share `EthicsCheck`'s unpopulated-flag problem (`hedge_commitments` reads the same verdict). **Flag for the B4 card.**
  - **G-9's closure** is not undermined — its (b) and (c) claims are exactly true as stated. But its scope was *reach and bypass*, not *predicate substance*. AA-A5-6 (the refusal tests still off the gate) is the natural next increment of the same work, and AA-A5-1/2/3 are a class of defect G-9 did not look for.
  - **No FA-style experiment is owed.** Unlike ADR-0005/0015's holonomy claim, nothing here needs a new measurement to adjudicate — the criteria in §1 were decidable by direct probe at this SHA, and two of three came back GO.

The stack's foundation is sound. What is wrong sits one layer up, in the predicates, and it is repairable without touching the load or composition contracts.

## 4. Stack-level findings (`AA-N`)

*Placeholder ids; renumber into `20-finding-register.md` at rollup.*

- **AA-A5-1 🟡 Repair** — `no_silent_correction` reports `runtime_checkable=True` on every turn but cannot fail: `ChatRuntime._last_refusal_was_typed` is initialized `True` (`chat/runtime.py:725`) and assigned `True` at `:2448` and `:3029`, with no `False` assignment anywhere in the repository. The honest report is `runtime_checkable=False`. (ADR-0032 §3)
- **AA-A5-2 🟡 Repair** — `no_identity_override` reports `runtime_checkable=True` but is tautologically upheld: both hashes derive from `self.identity_manifold`, assigned once at `chat/runtime.py:690` and never reassigned; the runtime's own docstring (`:329-337`) states the hashes are "equal by construction." Real identity-override defense lives in `teaching/review.py::_IDENTITY_MARKERS`. (ADR-0032 §3)
- **AA-A5-3 🟡 Repair** — `no_fabricated_source` never evaluates: `SafetyContext.allowed_source_shas` is unpopulated at both call sites (`chat/runtime.py:2423-2430`, `:2973-2980`), so the predicate short-circuits to `runtime_checkable=False` every turn. Combined with AA-A5-1/2, only 1 of 5 v1 safety boundaries can produce a live violation. (ADR-0032 §3)
- **AA-A5-4 🔴 Block** — requesting an unratified domain ethics pack silently downgrades to the no-refusal default. `legal_ethics_v1`, `research_ethics_v1`, `engineering_ethics_v1` all ship with `mastery_report_sha256: ""`, no companion report, and non-empty `refusal_commitments`/`hedge_commitments`. `chat/runtime.py:657-663` catches `EthicsPackError` and substitutes `default_general_ethics_v1` (empty opt-ins) with no log, no warning, no telemetry, no verdict field. Verified by executed probe. This is a silent correction inside the layer whose own `no_silent_correction` boundary reports `upheld=True` throughout. (ADR-0033 §3; ADR-0037 §3)
- **AA-A5-5 🟡 Repair** — no `--ethics` or `--list-ethics-packs` CLI surface; `RuntimeConfig.ethics_pack` (`core/config.py:52-53`) is reachable only programmatically, while identity has `--identity` and `--list-identity-packs`. ADR-0033's "swappable per deployment" is undelivered at the operator surface. (ADR-0033 §2, §5)
- **AA-A5-6 🟡 Repair** — the enforcement half of this stack is off the pre-push gate. G-9(c) promoted `tests/test_safety_pack.py` to `smoke`; `test_safety_check.py`, `test_safety_refusal.py`, `test_ethics_packs.py`, `test_ethics_check.py`, `test_ethics_refusal_opt_in.py`, `test_identity_packs.py`, `test_turn_loop_verdicts.py` all remain in `tests/full_only_baseline.txt`. The loader's fail-closed contract is gated; the refusal that consumes it is not. (all cards §2)
- **AA-A5-7 🔵 Consolidate** — `SafetyCheck` and `EthicsCheck` are one mechanism built twice: normalized for `Safety↔Ethics` / `boundary↔commitment`, the two class bodies differ by two comment lines and one field name. ADR-0034 §"Why a parallel surface" argues a semantic case (floor vs pledge) that a generic registry with distinct verdict types would fully preserve. (ADR-0034 §4, §7)
- **AA-A5-8 🔵 Consolidate** — five-plus pack loaders duplicate the same `_resolve_search_paths`/`_find_pack`/`_read_json`/`_validate_envelope`/`_validate_ratification` skeleton with per-family `CORE_ALLOW_UNRATIFIED_<X>` env vars and error classes (identity 494 L, safety 259 L, ethics 409 L, register 608 L, anchor-lens 422 L, rhetorical-style 425 L). Pairs with AA-A5-7 as one MG consolidation cluster. (ADR-0027 §7; ADR-0029 §7)
- **AA-A5-9 🟡 Repair** — `acknowledge_uncertainty` fires `upheld=False, runtime_checkable=True` on ordinary ungrounded turns (measured), making `EthicsVerdict.upheld=False` the normal state; and four of five ethics predicates depend on `EthicsContext` flags no call site populates. ADR-0037 premises its opt-in on "empirical violation rates from real corpora" that do not exist; a pack author following that guidance today would produce near-universal refusal. (ADR-0034 §3, §5; ADR-0037 §8)
- **AA-A5-10 🟢 Monitor** — ADR-0033's three-layer comparison table records Identity's failure mode as "Fall back to default"; the code fails closed (`chat/runtime.py:654`, no `try`). The table's central asymmetry is argued against a behavior identity does not have. (ADR-0033 §5)
- **AA-A5-11 🟢 Monitor** — ADR-0032 and ADR-0034 both state the turn loop "does not auto-invoke"; ADR-0035 wired both in and both now run on both runtime paths. Neither carries a supersession banner — the H-8 pattern on two safety-relevant documents. (ADR-0032 §6; ADR-0034 §6)
- **AA-A5-12 🟢 Monitor** — `CORE_ALLOW_UNRATIFIED_SAFETY=1` leaves no trace: no pin, no startup assertion, no telemetry field, no verdict evidence entry records that the runtime booted on an unverified safety floor. ADR-0029 §Negative names this as accepted operational discipline; nothing has changed at this SHA. (ADR-0029 §5)
- **AA-A5-13 🟢 Monitor** — no recorded firing of a typed refusal: the prefix string appears in no file under `evals/`, no results JSON, and no telemetry — only in ADR-0036/0037/0042 prose. Fitness for the stack's only enforcement path is unit-test-only. (ADR-0032 §8; ADR-0036 §8)
- **AA-A5-14 🟢 Monitor** — `engineering` and `research` are not members of `packs/ethics/loader.py::_ALLOWED_DOMAINS`; two shipped packs would fail `_validate_domain` even after ratification. Currently masked because the ratification check fires first. (ADR-0033 §3)
- **AA-A5-15 🟡 Repair** — `core pulse --identity <pack_id>` does not exist: the `pulse` subparser (`core/cli.py:3444-3461`) omits `_add_runtime_policy_args`, and `scripts/run_pulse.py:277-285` has no such flag. ADR-0027 Decision §4 names `core pulse` first and two of its six ratified §Verification criteria are `core pulse --identity` invocations. (ADR-0027 §2, §5)

**Answers to the MG layer card's open questions**, recorded here so Phase 3 does not re-derive them:

- *"Is safety-pack non-swappability mechanically enforced or loader-conventional?"* — **mechanically enforced**, and verified by executed sabotage at this SHA (§ADR-0029 card §3).
- *"Is there a pin that fails when a layer bypasses governance entirely?"* — **yes**, `tests/test_doctrine_prohibitions.py:169-199` (AST-based, both the call and the pack argument). Closed by G-9(b); adopted, not re-derived.
- *"Under what evidence should `identity_wave_gate` be authorized live?"* — still open (**G-11**). Not adjudicated here; A5's finding set adds a prerequisite the ruling should consider: at least one *behavioral* safety predicate should carry live evidence before identity refusal is authorized, or the gate would be the system's first content-safety block with no peer.

## 5. Evidence sources actually consulted (stack-wide)

**Charter and prior evidence (read first, per the plan's source order):**
`docs/adr-audit/00-scope-and-method.md`; `docs/adr-audit/TEMPLATE-stack-dossier.md`; `docs/adr-audit/TEMPLATE-adr-card.md`; `docs/adr-audit/MANIFEST.md`; `docs/adr-audit/02-stack-taxonomy.md` (row A5); `docs/assessment/10-layer-cards/MG-governance-identity.md`; `docs/assessment/30-gap-register.md` (G-9 full closure record, G-11); `docs/assessment/31-hindrance-audit.md` (H-8 pattern); `docs/assessment/02-layer-taxonomy.md:48`; `AGENTS.md` §invariants INV-21…INV-34 + §teaching/mutation safety; `docs/specs/runtime_contracts.md` §506 (INV-32).

**ADRs (all seven read in full):** `ADR-0027`, `ADR-0029`, `ADR-0032`, `ADR-0033`, `ADR-0034`, `ADR-0036`, `ADR-0037`.

**Runtime code:** `chat/runtime.py` (constructor `:600-740`; hash/versor adapters `:318-360`; stub path `:2390-2470`; main turn path `:2960-3110`; verdict assembly `:3200-3215`); `chat/refusal.py` (full); `packs/safety/loader.py` (full); `packs/safety/check.py` (full); `packs/identity/loader.py`; `packs/ethics/loader.py`; `packs/ethics/check.py`; `core/config.py:52-53`; `core/cli.py:125-148, 368-386, 2396-2500, 2622, 3444-3461`; `core/cli_test.py:13-30, 237`; `scripts/run_pulse.py:270-290`; `formation/runner.py:27,76`; `teaching/review.py:30-40, 198, 294-296`; `core/cognition/fail_closed.py`; `core/cognition/geometric_coherence.py:46`.

**Pack data (parsed, not assumed):** `packs/safety/core_safety_axes_v1.json` + `.mastery_report.json` (SHA re-verified against ADR-0029's recorded `ee1249ac…ce29`); `packs/identity/{default_general_v1,precision_first_v1,generosity_first_v1}.json` + companions; all five `packs/ethics/*_v1.json` (ratification state, `domain`, `refusal_commitments`, `hedge_commitments`).

**Tests and gate membership:** `tests/test_safety_pack.py` (full); `tests/test_safety_check.py`; `tests/test_safety_refusal.py`; `tests/test_ethics_packs.py`; `tests/test_ethics_check.py`; `tests/test_ethics_refusal_opt_in.py`; `tests/test_identity_packs.py`; `tests/test_turn_loop_verdicts.py`; `tests/test_medical_clinical_ethics_pack.py`; `tests/test_doctrine_prohibitions.py:150-266`; `tests/full_only_baseline.txt`.

**Evals and fitness:** `evals/identity_divergence/pack_runner.py`; `evals/adversarial_identity/contract.md` + `results/` (6 files); `evals/refusal_calibration/`; `evals/refusal_taxonomy/`; `docs/PROGRESS.md:769-780`; repo-wide grep for the typed-refusal prefix across `*.json`/`*.jsonl`/`*.md`.

**Repo-wide greps run:** `_last_refusal_was_typed` (all `*.py`); `allowed_source_shas`; `self.identity_manifold =`; `load_safety_pack` call sites; `SafetyPackError` catch sites; `CORE_ALLOW_UNRATIFIED*`; `INV-32` / `INV-34` / `INV-07` citations in code and tests; `--ethics` in `core/cli.py`.

**Executed probes (read-only; scratchpad scripts, nothing written to the repo, no repo file modified):**
1. **Fail-closed startup sabotage** — `packs.safety.loader._DEFAULT_SEARCH_PATHS` monkeypatched to an empty temp dir; `ChatRuntime(config=RuntimeConfig())` raised `SafetyPackError` from `chat/runtime.py:655`, uncaught. **The runtime genuinely refuses to start without a safety pack.**
2. **Live-turn verdict dump** — full `SafetyVerdict` and `EthicsVerdict` per-result table on an ordinary turn (reproduced verbatim in §1 and the ADR-0032/0034 cards).
3. **Forced safety violation** — `versor_condition=1.0` through the real `SafetyCheck` + `build_refusal_surface` → `I cannot proceed — boundary violated: safety:preserve_versor_closure`.
4. **Ethics pack-selection probe** — all five shipped packs at loader level and through `ChatRuntime(config=RuntimeConfig(ethics_pack=...))`, establishing AA-A5-4.
5. **Normalized structural diff** of `SafetyCheck.check` against `EthicsCheck.check`, establishing AA-A5-7.

**Discipline note (per §"verify against code, not against documents"):** every liveness, fail-closed, and predicate claim in this dossier was established by reading the code and, where the claim was behavioral, by executing it at `cbfc8ccb`. Claims sourced only from documents are labeled as such inline (the G-9 closure record, INV-32/34, and the MG card's Phase-2 ratings are adopted as prior evidence and were not re-derived).
