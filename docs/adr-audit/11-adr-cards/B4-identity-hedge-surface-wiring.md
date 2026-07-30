# B4 — Identity/Hedge Surface Wiring (M4/MG)

**Tier:** B · **Members:** ADR-0028, ADR-0030, ADR-0031, ADR-0038 · **Verified against:** `main` @ `cbfc8ccb` (2026-07-29)

All four ADRs in this zone concern the same user-visible phenomenon — how CORE prepends a hedge phrase to a served surface when its confidence or its ethics posture says the claim should be softened — but from four different angles: ADR-0028 makes an identity pack's `surface_preferences` drive the English hedge band/phrase choice (replacing two hardcoded constants); ADR-0030 extends the same band algorithm to Hebrew and Koine Greek; ADR-0031 extends it again to select a phrase keyed by *which* identity axis deviated, not just the generic band; ADR-0038 adds a structurally separate ethics-verdict-driven hedge **prepend** at the runtime layer, siblinged to ADR-0037's refusal opt-in. ADR-0028 itself is downstream of ADR-0027 (Identity Packs — swappable, ratified manifolds), which is audited elsewhere (A5 zone) and is not re-carded here; every claim below that depends on identity packs being load-bearing takes ADR-0027 as a given. All four code artifacts were located and read in full (`generate/surface.py`, `core/physics/identity.py`, `packs/identity/loader.py`, `chat/refusal.py`, `packs/ethics/loader.py`, `chat/runtime.py`), and the four associated test modules (69 tests total) were re-run fresh at the verification SHA — all pass. The central cross-cutting question this zone was asked to answer — whether ADR-0028/0030/0031 and ADR-0038 are four call-sites into one general hedge-injection operator, or four distinct mechanisms — has a precise, code-grounded answer: **two mechanisms, not four and not one.** ADR-0028/0030/0031 are three sequential extensions of a *single* function, `generate/surface.py::_apply_hedge` (0028 builds the four-band algorithm and the pack-preference plumbing, 0030 adds a `lang` dispatch over the same bands, 0031 adds an axis-keyed phrase override consulted before the generic phrase) — this is genuinely one evolving assembler-side operator. ADR-0038 is a second, independent mechanism (`chat/refusal.py::inject_hedge`) that runs later in the turn, on the runtime layer, gated by ethics-verdict violations rather than the identity-alignment scalar, and does **not** call `_apply_hedge` or consult its band/axis logic — it borrows only two of the eight `SurfacePreferences` fields (`preferred_hedge_soft`/`_strong`) as its phrase source. ADR-0038's own "Open questions deferred to a future ADR" §5 names this gap explicitly and defers reconciling it. A later, out-of-zone ADR-0254 (2026-07-23, not a member of this stack) adds a *third* independent hedge site (`core/cognition/surface_resolution.py::_grounded_open_hedge_resolution`, geometric-coherence-gated) — cited here only as corroborating evidence that the fragmentation this zone flags is a live, growing pattern, not a one-off.

---

## ADR-0028 — Identity Surface Wiring — Pack-Driven Hedge & Claim Strength

**Audit ID (if a numbering collision):** — | **Family (if phased):** —
**Zone / stack:** B4 — Identity/Hedge Surface Wiring (M4/MG) | **Tier:** B
**ADR status (as recorded in the file):** Accepted (2026-05-17) | **ADR date:** 2026-05-17
**Card author:** Tier-B audit agent | **`verified_at` SHA:** `cbfc8ccb`

---

### 1. Content summary

- **Decision made:** identity packs carry an optional `surface_preferences` block; the assembler's hedge logic reads pack-supplied thresholds and phrases instead of two hardcoded module constants, so swapping identity packs produces a visibly different English hedge decision on the same alignment scalar.
- **Alternatives explicitly rejected:** none named — the ADR frames this as closing a documented gap ("known limit 1" in `docs/identity_packs.md`), not as a choice among competing designs.
- **Artifacts the ADR claims will exist:**
  - `core/physics/identity.py::SurfacePreferences` dataclass
  - `IdentityManifold.surface_preferences` field (default-constructed)
  - `packs/identity/loader.py::_build_surface_preferences()` (parses + bounds-checks; enforces `strong <= soft <= qualified_high`; constrains `claim_strength`)
  - `generate/surface.py::SurfaceContext` — seven new fields
  - `generate/surface.py::_apply_hedge` — reworked to the four-band algorithm, takes the full context
  - `chat/runtime.py::ChatRuntime._build_surface_context` — lifts `identity_manifold.surface_preferences` into `SurfaceContext`
  - `packs/identity/*.json` — three v1 packs (`default_general_v1`, `precision_first_v1`, `generosity_first_v1`) gain tuned `surface_preferences` blocks
  - `tests/test_identity_surface_divergence.py`, in particular `TestPackSwapDivergence::test_same_alignment_different_surfaces`
  - Legacy `HEDGE_STRONG_THRESHOLD = 0.4` / `HEDGE_SOFT_THRESHOLD = 0.5` retained as defaults

### 2. Implementation cross-reference

| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `SurfacePreferences` dataclass | yes | `core/physics/identity.py:275` | Fields match ADR table exactly (`hedge_threshold_strong=0.40`, `_soft=0.50`, `qualified_band_high=0.75`, etc.) |
| `IdentityManifold.surface_preferences` | yes | `core/physics/identity.py:315` | Default-constructed, as specified |
| `_build_surface_preferences()` | yes | `packs/identity/loader.py:334` | Threshold-ordering check and `claim_strength` allow-list both present (`:364`, `:371`) |
| `SurfaceContext` +7 fields | yes | `generate/surface.py:57-` (`hedge_threshold_strong`, `_soft`, `preferred_hedge_strong`, `_soft`, `claim_strength`, `qualified_band_high`, `preferred_qualifier`) | Defaults reproduce pre-ADR constants |
| `_apply_hedge` four-band algorithm | yes | `generate/surface.py:148` | Confirmed strong/soft/marginal/above-marginal bands, `claim_strength` branch inside marginal band |
| `ChatRuntime._build_surface_context` | yes | `chat/runtime.py:1803` | Lifts all seven pref fields plus `deviation_axes`/`axis_hedges` (ADR-0031, see below) |
| Three v1 packs carry `surface_preferences` | yes | `packs/identity/{default_general_v1,precision_first_v1,generosity_first_v1}.json` | Verified via direct JSON parse: `surface_preferences` present in all three |
| Legacy threshold constants retained | yes | `generate/surface.py:24-25` (`HEDGE_STRONG_THRESHOLD`, `HEDGE_SOFT_THRESHOLD`) | Comment explicitly ties them to pre-ADR-0028 byte-parity |
| `tests/test_identity_surface_divergence.py` | yes | 15 tests, all pass (re-run fresh at `cbfc8ccb`) | Includes `test_same_alignment_different_surfaces` |

**Build axis: full** — every claimed artifact exists, at the claimed location, matching the claimed shape; nothing scaffolded or partial.

### 3. Liveness / integration

- Traced the live call chain: `ChatRuntime._build_surface_context` (`chat/runtime.py:1803`) constructs `SurfaceContext` from `self.identity_manifold.surface_preferences` on every turn (`chat/runtime.py:2959`) → passed as `context=` into `SentenceAssembler().assemble(...)` (`:2963-2968`) → dispatches by `plan.output_language` to `_assemble_en`/`_assemble_he`/`_assemble_grc` (`generate/surface.py:343-`) → each calls `_apply_hedge(surface, ctx, lang=...)` when `ctx is not None`, which it always is on this path. The resulting `sentence_plan.surface` becomes `walk_surface` (`chat/runtime.py:2969`), and `response_surface = walk_surface` (`:3034`) is the default candidate for the served surface unless a pack-grounded/deduction/refusal composer arm overrides it upstream. This is unconditional main-serving-path code, not test-only or feature-flagged.
- **Sabotage test:** remove `_apply_hedge` (or stub it to identity) and every identity-pack swap collapses back to producing byte-identical English surfaces regardless of which manifold is loaded, at any alignment — exactly the pre-ADR-0028 defect this ADR was written to close. `test_same_alignment_different_surfaces` would fail immediately. The observable (assembled string differs by pack at fixed alignment) is real and specifically constructed to be falsifiable.
- **Liveness axis: live.**

### 4. Design fidelity — pillars and axioms

| Pillar | Honors / Tension / Violates | Citation (ADR clause + pillar text) |
|---|---|---|
| I. Mechanical Sympathy | Honors | `SurfaceContext` stays `frozen+slots`; ADR §"Negative/risks" explicitly reasons about the added-field cost ("the cost is small") rather than ignoring it |
| II. Semantic Rigor | Tension | `claim_strength` is a bare string constrained only at pack-load time to `{"balanced","qualified","affirmative"}`, not a typed enum in `SurfacePreferences` itself; separately, `alignment` as a term is reused across the codebase for a structurally unrelated concept (FA-1's cross-language holonomy alignment) — see AA-B4-4 |
| III. Third Door | Tension | The ADR frames itself as closing a documented gap, not choosing between two visible options; the fix is an extension of the existing threshold-scalar mechanism (more thresholds, more phrases) rather than a reconceived hedge model — same shape, more parameters |

| Axiom | Honors / Tension / Violates | Citation |
|---|---|---|
| 1. Geometry-First | n/a | Consumes a pre-computed alignment scalar; does no geometry itself |
| 2. Field-State | n/a | `identity_alignment` arrives as a scalar snapshot at the surface boundary; the field-state work is upstream in `IdentityCheck` (ADR-0027 territory) |
| 3. Propagation-over-Mutation | Tension | The four-band algorithm (`generate/surface.py:148-`) is an `if/elif` threshold-branch lookup over a scalar, not propagation through a structured medium — intentionally scoped as surface-only per the ADR, but the shape is exactly the discrete branch-table axiom 3 cautions against |
| 4. Dual-Correction | n/a | No forward operator introduced; nothing here has (or needs) a conjugate |
| 5. Reconstruction-over-Storage | Honors | ADR's own Governance Cross-Reference: "surface preferences are derived at runtime from pack manifests" — nothing is cached per-turn |
| 6. Compilation-Last | n/a | No loop/tensor/table/class/kernel infrastructure introduced — a small dataclass plus branches |
| 7. Reality-over-Inheritance | Honors | The pre-ADR two-constant hedge is replaced outright, not inherited unexamined; old constants are kept only as compat defaults, not as load-bearing structure |

### 5. Build fidelity — does the code match the decision?

Exact match. The four-band algorithm, the schema shape (`surface_preferences` block with the seven named keys), the three pack profiles' numeric thresholds and phrases, and the backward-compatibility guarantees (packs without the block reproduce byte-identical pre-ADR output; `SurfaceContext()` bare construction reproduces pre-ADR defaults) were all verified directly in code and match the ADR's prose with no observed drift.

**Build-fidelity axis: matches.**

### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs

- No contradiction found against `Whitepaper.md` or `Yellowpaper.md`.
- Builds cleanly on ADR-0027 (identity packs — audited separately in zone A5; treated here as a given per this zone's brief). Explicitly extended by ADR-0030 (depth-language) and ADR-0031 (axis-specific phrases) — both cite ADR-0028 as a companion doc and both were verified to route through the same `_apply_hedge` function ADR-0028 introduced, not a fork of it.
- Minor citation drift, not a substantive contradiction: ADR-0028's own "Governance Cross-Reference (ADR-0225)" section cites `chat/surface.py` as the file implementing surface-context shaping; that file does not exist — the real module is `generate/surface.py`. See AA-B4-1.
- **Continuity axis: clean** (the citation drift is cosmetic, not a design or build contradiction).

### 7. Necessity / generality

1. **Necessity:** the *problem* ADR-0028 solves (identity packs being provably inert at the surface layer) is real and the sabotage test in §3 confirms the fix is load-bearing, not decorative. Whether a *pack-driven threshold-band prepend* is the necessary shape for solving it is separate — see below.
2. **Reducibility:** no L0/L1 algebra/field-layer operator already does threshold-banded string prepending; this is inherently a surface-layer, not substrate-layer, concern. Not reducible to an existing geometric primitive.
3. **Extensibility / generalization-candidate:** `_apply_hedge` is itself the shared trunk for ADR-0030 and ADR-0031 — that consolidation already happened correctly within this zone. The open pairing is with ADR-0038: both ADR-0028's assembler-side `_apply_hedge` and ADR-0038's runtime-side `inject_hedge` do "prepend a hedge phrase sourced from the identity manifold," gated by different signals (alignment-band vs ethics-verdict), and neither calls the other. ADR-0038 itself names this exact gap as an open question. See AA-B4-3 — the zone-level finding.

**Necessity/generality axis: generalization-candidate** — irreducible as a surface-layer concern, but the specific operator boundary between "assembler hedge" and "runtime hedge" is not yet the one general hedge-injection operator ADR-0038's title claims to be.

### 8. Fitness / value

- `docs/assessment/10-layer-cards/M4-expression-serving.md` names "hedge" as one of the composer arms that have "accreted one arm per capability... with no single place that states the precedence order" — corroborating, team-ratified evidence that this mechanism is real and live but architecturally strained, matching this card's own finding.
- `docs/assessment/20-component-cards/surface-selection.md` independently lists "hedge" (both the assembler band and, separately, ADR-0254's later geometric-coherence hedge) among the arms in the two-strata composer/resolver architecture, and recommends "extend the resolver's declared-precedence pattern upstream to the composer stratum" — directly relevant to the consolidation candidate raised in §7.
- `docs/identity_packs.md` records "known limit 1... Closed by ADR-0028 + ADR-0030" — a first-party fitness claim, corroborated by the passing divergence tests.
- Fresh verification: `tests/test_identity_surface_divergence.py` — 15/15 pass at `cbfc8ccb` (re-run 2026-07-29 as part of this audit).

**Fitness axis:** cited artifacts above; mechanism confirmed live and delivering its stated purpose (visible pack-driven English hedge divergence).

### 9. Findings raised

- 🟢 AA-B4-1 — ADR-0028's Governance Cross-Reference section cites a nonexistent file (`chat/surface.py`); the real module is `generate/surface.py`. Cosmetic doc drift, no behavior impact. (§6)
- 🔵 AA-B4-3 — (zone-level, primary detail under ADR-0038 below) `_apply_hedge` (ADR-0028/0030/0031) and `inject_hedge` (ADR-0038) are two independent hedge mechanisms sharing only a phrase source, not an operator; ADR-0038 defers reconciling this. (§7)
- 🟢 AA-B4-4 — `alignment` names two computationally unrelated quantities across the codebase: `IdentityScore.alignment` (Gram-computed per-axis deviation scalar, drives this ADR's hedge bands) vs. FA-1's cross-language holonomy "alignment" (ruled NO-GO, unrelated code path). Verified the two are independent — no cascading contamination from the FA-1 ruling — but the shared name is a Pillar II (Semantic Rigor) risk worth a corpus-wide glossary note. (§4)

### 10. Evidence sources actually consulted

- `docs/adr/ADR-0028-identity-surface-wiring.md` (full read), `docs/adr/ADR-0027-identity-packs.md` (context only, not carded), `docs/identity_packs.md` (grep for "known limit 1" context)
- Code: `core/physics/identity.py`, `packs/identity/loader.py`, `generate/surface.py`, `chat/runtime.py` (all read directly, not inferred from ADR prose)
- `packs/identity/{default_general_v1,precision_first_v1,generosity_first_v1}.json` — parsed directly to confirm `surface_preferences` presence
- `tests/test_identity_surface_divergence.py` — re-run fresh (15/15 pass)
- `docs/assessment/10-layer-cards/M4-expression-serving.md`, `docs/assessment/20-component-cards/surface-selection.md` — read in full
- `docs/analysis/fa1-holonomy-gate-verdict-2026-07-28.md` — grepped for "alignment" to confirm the term-overload finding is not a substantive contamination
- `docs/census/cbfc8ccbf7fe503ab31abe7aedbb1973ba7d7b4d/{stale-references,docstring-drift}.jsonl` — checked for this ADR's claimed artifacts; most flagged relative-path hits were false positives from the census tool's path resolution (`docs/identity_packs.md` does exist), except the genuine `chat/surface.py` miss

---

## ADR-0030 — Depth-Language Hedge Wiring

**Audit ID (if a numbering collision):** — | **Family (if phased):** —
**Zone / stack:** B4 — Identity/Hedge Surface Wiring (M4/MG) | **Tier:** B
**ADR status (as recorded in the file):** Accepted (2026-05-17) | **ADR date:** 2026-05-17
**Card author:** Tier-B audit agent | **`verified_at` SHA:** `cbfc8ccb`

---

### 1. Content summary

- **Decision made:** extend ADR-0028's four-band hedge algorithm to Hebrew and Koine Greek surfaces, using the same pack-supplied thresholds/`claim_strength` but canonical (non-pack-overridable) per-language hedge phrases.
- **Alternatives explicitly rejected:** two larger moves are named and explicitly declined for this ADR — (a) extending the pack schema with a `languages` block, (b) lifting depth-language phrases out of `surface.py` into language packs. Both deferred as "larger architectural moves; neither belongs in this ADR."
- **Artifacts the ADR claims will exist:**
  - `generate/surface.py::_DEPTH_HEDGE_PHRASES` — `dict[str, tuple[str, str, str]]` keyed `"he"`/`"grc"`
  - `_apply_hedge` gains a `lang: str = "en"` parameter
  - `_assemble_he` / `_assemble_grc` gain `ctx: SurfaceContext | None` and call `_apply_hedge(..., lang=...)`
  - `tests/test_identity_surface_divergence_depth.py` — 15 tests

### 2. Implementation cross-reference

| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `_DEPTH_HEDGE_PHRASES` | yes | `generate/surface.py:35-` | Hebrew and Greek strong/soft/qualifier phrases match the ADR's table exactly (including transliterations in comments) |
| `_apply_hedge(..., lang="en")` | yes | `generate/surface.py:148` | `lang` dispatches to `_DEPTH_HEDGE_PHRASES[lang]` when present, else falls back to `ctx.preferred_hedge_*` |
| `_assemble_he` calls `_apply_hedge(..., lang="he")` | yes | `generate/surface.py:301` | Guarded by `if ctx is not None` |
| `_assemble_grc` calls `_apply_hedge(..., lang="grc")` | yes | `generate/surface.py:339` | Same guard |
| `tests/test_identity_surface_divergence_depth.py` | yes | 15 tests, all pass (re-run fresh at `cbfc8ccb`) | — |

**Build axis: full.**

### 3. Liveness / integration

- Same call chain as ADR-0028 (§3 above), confirmed to reach `_assemble_he`/`_assemble_grc` through `SentenceAssembler.assemble` dispatching on `plan.output_language == "he"`/`"grc"` (`generate/surface.py:362-369`). Live whenever a turn's output language is Hebrew or Greek — not gated behind a feature flag.
- **Sabotage test:** stub `_apply_hedge`'s depth-language branch back to a no-op and Hebrew/Greek surfaces stop varying by identity pack at any alignment, while English continues to vary (per ADR-0028) — the asymmetry ADR-0030 was written to close would silently return. `TestDepthPackSwapDivergence::test_hebrew_pack_swap_visible_at_alignment_0p45` would fail.
- **Liveness axis: live.**

### 4. Design fidelity — pillars and axioms

| Pillar | Honors / Tension / Violates | Citation (ADR clause + pillar text) |
|---|---|---|
| I. Mechanical Sympathy | Honors | Pure addition; `lang` defaults to `"en"` so existing callers pay zero cost; `TestBackwardCompatibility` asserts byte-identical legacy output |
| II. Semantic Rigor | Honors | Explicit, careful phrase-ownership boundary: English phrases live on the pack (mutable), depth-language phrases are canonical module constants (immutable at v1) — the ADR states this distinction and its rationale precisely, rather than blurring it |
| III. Third Door | Tension | Explicitly declines two larger architectural moves (pack `languages` block; phrase-lifting into language packs) in favor of the minimal patch — a defensible scoping decision, but the chosen shape is "the smaller of two rejected options," not a third path |

| Axiom | Honors / Tension / Violates | Citation |
|---|---|---|
| 1. Geometry-First | n/a | Same consumption of a pre-computed scalar as ADR-0028 |
| 2. Field-State | n/a | Same |
| 3. Propagation-over-Mutation | Tension | Extends the same branch-table shape via a `dict` keyed on `lang` — same critique as ADR-0028 §4 |
| 4. Dual-Correction | n/a | — |
| 5. Reconstruction-over-Storage | Honors | Phrases are canonical constants read at call time, not stored per-manifold |
| 6. Compilation-Last | n/a | — |
| 7. Reality-over-Inheritance | Honors | Explicitly preserves Hebrew VSO / Greek SOV word order verbatim rather than retrofitting grammar to accommodate the hedge — "ADR-0030 only prefixes a hedge phrase to whatever the existing assembler produced" |

### 5. Build fidelity — does the code match the decision?

Exact match, including the specific Hebrew/Greek phrase strings, the `lang` parameter default, and the backward-compatibility guarantee for `ctx=None` callers.

**Build-fidelity axis: matches.**

### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs

- No contradiction against `Whitepaper.md`/`Yellowpaper.md` found. CORE's three-language foundation (English/Hebrew/Koine Greek) is treated as an architectural commitment per the ADR's own context section, consistent with the Whitepaper's framing.
- Cleanly extends ADR-0028 (explicit companion-doc citation, verified in code to share `_apply_hedge`).
- **Continuity axis: clean.**

### 7. Necessity / generality

1. **Necessity:** genuinely closes a real asymmetry (identity load-bearing in English only) that the ADR's own predecessor flagged as a known gap. Not decorative — the sabotage test in §3 confirms.
2. **Reducibility:** not reducible to an L0/L1 primitive; this is a surface-layer language-dispatch concern.
3. **Extensibility:** this ADR is itself the extensibility case for ADR-0028 — `_apply_hedge` absorbed the depth-language requirement via a `lang` parameter rather than forking. That is the correct shape and the model the zone's broader consolidation question (ADR-0038, see AA-B4-3) should be measured against.

**Necessity/generality axis: irreducible** (as a language-dispatch extension of an already-necessary mechanism; no further reduction available at the surface layer).

### 8. Fitness / value

- `docs/identity_packs.md` records the gap as closed by "ADR-0028 + ADR-0030" jointly.
- Fresh verification: `tests/test_identity_surface_divergence_depth.py` — 15/15 pass at `cbfc8ccb`; `tests/test_identity_surface_divergence.py` (ADR-0028 regression) also still 15/15 pass, confirming no English-path drift was introduced.

**Fitness axis:** cited artifacts above; mechanism confirmed live and delivering the stated cross-language parity.

### 9. Findings raised

- None beyond the zone-level findings already raised under ADR-0028 (AA-B4-1, AA-B4-4) and ADR-0038 (AA-B4-3), which this ADR is downstream of but does not itself introduce new instances of.

### 10. Evidence sources actually consulted

- `docs/adr/ADR-0030-depth-language-hedge.md` (full read), `docs/adr/ADR-0028-identity-surface-wiring.md` (cross-reference)
- Code: `generate/surface.py` (full relevant sections read directly)
- `tests/test_identity_surface_divergence_depth.py`, `tests/test_identity_surface_divergence.py` — both re-run fresh (15/15 + 15/15 pass)
- `docs/identity_packs.md` — grepped for closure claim

---

## ADR-0031 — Score-Decomposition Surface — Per-Axis Hedge Phrases

**Audit ID (if a numbering collision):** — | **Family (if phased):** —
**Zone / stack:** B4 — Identity/Hedge Surface Wiring (M4/MG) | **Tier:** B
**ADR status (as recorded in the file):** Accepted (2026-05-17) | **ADR date:** 2026-05-17
**Card author:** Tier-B audit agent | **`verified_at` SHA:** `cbfc8ccb`

---

### 1. Content summary

- **Decision made:** when the English hedge band fires and `IdentityScore.deviation_axes` names an axis the pack has an `axis_hedges` entry for, use that axis's phrase instead of the generic ADR-0028 phrase — so the hedge names *what* deviated, not just *that* something deviated.
- **Alternatives explicitly rejected:** "Interpretation A — Dominance-driven phrasing" (every assertion's character shifts by which axis *leads* the manifold) is named and explicitly rejected for this ADR: "requires new dominance scoring, changes confident assertions too (large blast radius), and isn't structurally connected to anything already computed." "Interpretation B — Deviation-driven hedge phrasing" (this ADR) is chosen because the needed data (`deviation_axes`) already exists.
- **Artifacts the ADR claims will exist:**
  - `core/physics/identity.py::AxisHedge` frozen dataclass (strong/soft/qualifier)
  - `SurfacePreferences.axis_hedges: Tuple = ()` (tuple of `(axis_id, AxisHedge)` pairs, lex order)
  - `packs/identity/loader.py::_build_axis_hedges()` — parses, bounds-checks via `_validate_hedge_phrase` (length 1-64), emits lex order
  - `generate/surface.py::SurfaceContext` gains `deviation_axes: frozenset[str]` and `axis_hedges: tuple[...]`
  - `generate/surface.py::_axis_specific_phrase(ctx)` helper — lex-smallest matching axis's phrase or `None`
  - `chat/runtime.py::ChatRuntime._build_surface_context` lifts `identity_score.deviation_axes` and `prefs.axis_hedges`
  - Three v1 packs gain `axis_hedges` blocks with specific new `pack_source_sha`/`mastery_report_sha256` values (given explicitly in the ADR)
  - `tests/test_identity_score_decomposition.py` — 17 tests

### 2. Implementation cross-reference

| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `AxisHedge` dataclass | yes | `core/physics/identity.py:261` | — |
| `SurfacePreferences.axis_hedges` | yes | `core/physics/identity.py:306` | `Tuple = ()` as specified |
| `_build_axis_hedges()` | yes | `packs/identity/loader.py:398` | Calls `_validate_hedge_phrase` per phrase (`:433,437,441`) |
| `SurfaceContext.deviation_axes` / `.axis_hedges` | yes | `generate/surface.py:81-82` | `frozenset[str]` and flattened quadruple tuple, matching the "hashability" rationale in the ADR |
| `_axis_specific_phrase(ctx)` | yes | `generate/surface.py:196` | Linear scan, first match on lex-ordered tuple — matches ADR's "lex-smallest" selection rule |
| `_build_surface_context` lifts both fields | yes | `chat/runtime.py:1806-1815` | `deviation_axes` from `identity_score`, `axis_hedges` flattened from `prefs.axis_hedges` |
| Three v1 packs carry `axis_hedges` | yes | `packs/identity/{default_general_v1,precision_first_v1,generosity_first_v1}.json` | Verified via direct JSON parse |
| Claimed re-ratification SHAs | yes | `packs/identity/*.mastery_report.json` `report_sha256`, cross-checked against `*.json`'s `mastery_report_sha256` | All three SHAs match the ADR's table exactly, e.g. `default_general_v1` → `2ab7d469...4f5d3` in both the mastery report and the pack file |
| `tests/test_identity_score_decomposition.py` | yes | 17 tests, all pass (re-run fresh at `cbfc8ccb`) | — |

**Build axis: full** — including the unusually specific and independently-verifiable SHA claims, which matched exactly.

### 3. Liveness / integration

- Traced: `_build_surface_context` (`chat/runtime.py:1803`) reads `identity_score.deviation_axes` (computed live by `IdentityCheck.check()`, ADR-0027 territory) every turn and flattens `prefs.axis_hedges` into `SurfaceContext`. `_apply_hedge` (`generate/surface.py:148`) calls `_axis_specific_phrase(ctx)` before falling back to the ADR-0028 generic phrase — confirmed at `generate/surface.py:177`. Same unconditional main-path reach as ADR-0028/0030.
- **Sabotage test:** stub `_axis_specific_phrase` to always return `None` and every hedge collapses back to the generic ADR-0028 phrase regardless of which axis deviated — axis-specific wording disappears, though the band/strength decision is unaffected (that's ADR-0028's mechanism, still intact). `TestAxisHedgeSelection`-style tests (17 in the module, covering lex tie-break, band gating, and pack-swap-with-deviation) would fail.
- **Liveness axis: live.**

### 4. Design fidelity — pillars and axioms

| Pillar | Honors / Tension / Violates | Citation (ADR clause + pillar text) |
|---|---|---|
| I. Mechanical Sympathy | Honors | "No new scoring infrastructure... this ADR is purely plumbing + a phrase table"; reuses an already-computed field (`deviation_axes`) rather than adding new computation |
| II. Semantic Rigor | Honors | Makes the hedge legible — the user reads *why* the system hedged ("Evidence is thin that…" for a truthfulness deviation) rather than a generic disclaimer; the schema field is deliberately named `axis_hedges` (not `axis_phrasing`) specifically to avoid colliding with a future, semantically distinct concept |
| III. Third Door | Honors | The ADR names two real interpretations (dominance-driven vs deviation-driven), gives a substantive reason to reject the first (new scoring infra, large blast radius, no structural connection to existing state), and picks the second because the data already exists — genuine first-principles minimality reasoning, not a coin-flip between two off-the-shelf options |

| Axiom | Honors / Tension / Violates | Citation |
|---|---|---|
| 1. Geometry-First | n/a | Consumes `deviation_axes`, already computed upstream by the geometric `IdentityCheck` |
| 2. Field-State | n/a | Same — the field-state computation is ADR-0027's, not this ADR's |
| 3. Propagation-over-Mutation | Tension | `_axis_specific_phrase` is a linear scan / first-match lookup over a lex-ordered tuple — same branch/table shape critiqued in ADR-0028 §4, applied one layer deeper |
| 4. Dual-Correction | n/a | — |
| 5. Reconstruction-over-Storage | Honors | `axis_hedges` parsed from the pack at load time; nothing duplicated or cached separately from the manifest |
| 6. Compilation-Last | n/a | Lex-ordering exists "for hashability + determinism," a reasonable minimal data shape, not a premature compiled structure |
| 7. Reality-over-Inheritance | Honors | Does not retrofit or reinterpret `IdentityScore.deviation_axes`'s existing meaning; purely plumbs it to a new consumer |

### 5. Build fidelity — does the code match the decision?

Exact match, including the lex-tie-break rule ("assembler does a linear scan and takes the first match, which is the lex-smallest" — confirmed verbatim in `_axis_specific_phrase`), the three pack profiles' distinct phrase sets, and the independently-verified re-ratification SHAs (§2).

**Build-fidelity axis: matches.**

### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs

- No contradiction against `Whitepaper.md`/`Yellowpaper.md` found.
- Cleanly extends ADR-0028 and ADR-0030 (both cited as companion docs; both verified in code to share `_apply_hedge`/`SurfaceContext`). Interpretation A (dominance-driven phrasing) is explicitly left open for a future ADR without foreclosing it — a clean deferral, not a contradiction.
- English-only at v1 is an explicit, named scope limit (depth languages still use ADR-0030's canonical phrases regardless of axis deviation) — consistent with, not contradicting, ADR-0030's own stated scope.
- **Continuity axis: clean.**

### 7. Necessity / generality

1. **Necessity:** genuinely adds information the user did not previously have access to (which axis is driving the hedge); not a cosmetic rewording, confirmed live per §3.
2. **Reducibility:** not reducible to an L0/L1 primitive.
3. **Extensibility:** this ADR is a third consolidation instance within `_apply_hedge` (after ADR-0030's language dispatch) — reinforcing that ADR-0028/0030/0031 are correctly unified as one operator. The unresolved pairing remains the same one raised under ADR-0028/0038: ADR-0038's runtime `inject_hedge` does not consult `axis_hedges` at all, even when an ethics-driven hedge fires for a turn whose `deviation_axes` would otherwise motivate a specific phrase — a second surface where the two mechanisms' non-unification is directly visible (an ADR-0038-triggered hedge is always generic, never axis-specific, even when axis information exists on the same turn).

**Necessity/generality axis: irreducible** as an extension of the already-established `_apply_hedge` operator; see AA-B4-3 for the cross-ADR consolidation candidate this reinforces.

### 8. Fitness / value

- `tests/test_identity_score_decomposition.py` — 17/17 pass (re-run fresh at `cbfc8ccb`).
- Independently-verifiable SHA claims in the ADR matched exactly against the live pack/mastery-report files (§2) — a stronger-than-usual fitness signal, since these are cryptographic hashes an author could not have fabricated without the actual re-ratification having occurred.
- `docs/assessment/20-component-cards/surface-selection.md` treats "hedge" as a single arm in its composer-stratum table without distinguishing the generic-vs-axis-specific distinction this ADR introduces — i.e., the team-level assessment did not need to special-case ADR-0031's contribution, consistent with it being a clean internal extension rather than a new composer arm.

**Fitness axis:** cited artifacts above; mechanism confirmed live and delivering its stated purpose.

### 9. Findings raised

- None beyond the zone-level AA-B4-3 (cross-referenced above, detailed under ADR-0038).

### 10. Evidence sources actually consulted

- `docs/adr/ADR-0031-score-decomposition-surface.md` (full read), cross-referenced against ADR-0028 and ADR-0030
- Code: `core/physics/identity.py`, `packs/identity/loader.py`, `generate/surface.py`, `chat/runtime.py` (all read directly)
- `packs/identity/*.json` and `packs/identity/*.mastery_report.json` — parsed directly to independently verify the claimed SHAs
- `tests/test_identity_score_decomposition.py` — re-run fresh (17/17 pass)
- `docs/assessment/20-component-cards/surface-selection.md` — read in full

---

## ADR-0038 — Hedge Injection as a Runtime-Level Affordance

**Audit ID (if a numbering collision):** — | **Family (if phased):** —
**Zone / stack:** B4 — Identity/Hedge Surface Wiring (M4/MG) | **Tier:** B
**ADR status (as recorded in the file):** Accepted (2026-05-17) | **ADR date:** 2026-05-17
**Card author:** Tier-B audit agent | **`verified_at` SHA:** `cbfc8ccb`

---

### 1. Content summary

- **Decision made:** add an optional `hedge_commitments` field to the ethics-pack schema, sibling to ADR-0037's `refusal_commitments`; when a runtime-checkable violation of an opted-in commitment fires, the runtime prepends the identity manifold's preferred hedge phrase to `ChatResponse.surface` — a softer remediation tier than full typed refusal, mutually exclusive with refusal at the pack-schema level.
- **Alternatives explicitly rejected:** ADR-0036 (cited, not re-decided here) already rejected conflating refusal with hedging for safety violations, reasoning that "the same surface change could mean two different things. Audit becomes ambiguous." ADR-0038 accepts that boundary for safety and instead opens a second, schema-enforced-exclusive remediation tier for ethics commitments specifically.
- **Artifacts the ADR claims will exist:**
  - Ethics pack JSON schema: optional `hedge_commitments: list[str]`
  - Load-time mutual-exclusion check: `commitment cannot appear in both refusal_commitments and hedge_commitments`
  - `chat/refusal.py::should_inject_hedge(ethics_verdict, ethics_pack) -> bool`
  - `chat/refusal.py::build_hedge_prefix(identity_manifold) -> str` (prefers soft, falls back to strong)
  - `chat/refusal.py::inject_hedge(surface, hedge_prefix) -> str` (idempotent-on-prefix, case-insensitive)
  - `ChatRuntime` — single conditional after the refusal branch, refusal supersedes hedge
  - Hedge injection does not set `_last_refusal_was_typed`
  - `tests/test_hedge_injection.py` — 22 tests

### 2. Implementation cross-reference

| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `hedge_commitments` field + mutual-exclusion check | yes | `packs/ethics/loader.py:82,130-134` | `overlap = set(refusal_commitments) & set(hedge_commitments)` raises on non-empty |
| `should_inject_hedge` | yes | `chat/refusal.py:125` | Matches ADR description exactly, including the `runtime_checkable=True, upheld=False` gating via `_iter_violated_ids` |
| `build_hedge_prefix` | yes | `chat/refusal.py:146` | Prefers `preferred_hedge_soft`, falls back to `_strong`, empty string if neither |
| `inject_hedge` | yes | `chat/refusal.py:163` | Idempotent-on-prefix via `surface.casefold().startswith(hedge_prefix.casefold())` |
| `ChatRuntime` single conditional, refusal-supersedes-hedge | yes | `chat/runtime.py:3105-3109` | Runs strictly after the refusal-surface branch; only executes on the code path where no refusal fired |
| No `_last_refusal_was_typed` mutation | yes | Confirmed no reference to `_last_refusal_was_typed` near the hedge-injection block (`chat/runtime.py:3105-3109`) | — |
| Default pack ships `hedge_commitments: []` | yes | `packs/ethics/default_general_ethics_v1.json:23` | Confirmed empty by default |
| Domain packs opt commitments in | yes | `packs/ethics/{medical_clinical,engineering,legal,research}_ethics_v1.json` | e.g. medical: `["defer_diagnosis_to_clinician", "surface_evidence_grade"]` |
| `tests/test_hedge_injection.py` | yes | 22 tests, all pass (re-run fresh at `cbfc8ccb`) | — |

**Build axis: full** — every claimed artifact exists and matches exactly, including the more subtle claims (idempotency, mutual exclusion, no refusal-bookkeeping side effect).

### 3. Liveness / integration

- Traced: `should_inject_hedge(ethics_verdict, self.ethics_pack)` (`chat/runtime.py:3105`) runs unconditionally on every main-path turn (not behind a feature flag) after the ethics check has already produced a verdict for the turn. It returns `False` immediately whenever `ethics_pack.hedge_commitments` is empty — which is the case for the *shipped default* ethics pack (`packs/ethics/default_general_ethics_v1.json`). It fires only when a deployment has loaded a non-default ethics pack (via the `RuntimeConfig.ethics_pack` field) that both opts a commitment into `hedge_commitments` *and* that commitment is violated this turn. **No CLI-level affordance exists to select an ethics pack** — `core/cli.py` exposes `--identity <pack_id>` (confirmed at `core/cli.py:2461`) but no equivalent `--ethics`/`--ethics-pack` flag; `ethics_pack` is reachable only by constructing `RuntimeConfig` programmatically. The demo path (`evals/audit_tour/run_tour.py::_scene_3_ethics_hedge_opt_in`) exercises the pure helper functions directly against a synthetic verdict and an in-process manifold mutation — it explicitly does not drive the mechanism through the live `chat()`/`respond()` turn loop ("We do not depend on the stub/main path of `chat()` here").
- **Sabotage test:** stub `should_inject_hedge` to always return `False` — under the *shipped default configuration*, nothing observable changes (the default pack's empty `hedge_commitments` means it already never fires). Under a deployment with a non-default ethics pack and an opted-in, violated commitment, the served surface would lose its hedge prefix while the ethics verdict still records the violation — a real, observable divergence, confirmed by the 22-test suite (in particular the "opt-in pack injects on violation" integration test).
- **Liveness axis: live** — the code path is unconditionally reached every turn and is genuinely load-bearing whenever a non-default ethics pack with `hedge_commitments` is loaded, confirmed by passing integration tests that drive `ChatRuntime` end to end (not just the pure helpers). The caveat is that this configuration has no operator-facing CLI surface and no evidence of exercise beyond the domain example packs, which the audit's own Tier-C triage of the sibling ADR-0044 (medical ethics pack) already characterizes as "a worked-example domain pack (single instance, not a mechanism)."

### 4. Design fidelity — pillars and axioms

| Pillar | Honors / Tension / Violates | Citation (ADR clause + pillar text) |
|---|---|---|
| I. Mechanical Sympathy | Honors | "Three helper functions... all pure. ChatRuntime adds a single conditional" — minimal, deterministic, idempotent footprint |
| II. Semantic Rigor | Tension | The ADR's own §"Negative/risks" flags that "hedge phrase source is the identity manifold, not the ethics pack" — an ethics-driven decision (whether/when to hedge) is phrased using an identity-driven vocabulary (what to say), a genuine cross-pack semantic seam the ADR names but does not resolve; more broadly, "hedge" now names two structurally distinct mechanisms in the codebase (this ADR's ethics-verdict prepend vs. ADR-0028's alignment-band selection) without a shared definition — see AA-B4-3 |
| III. Third Door | Honors | ADR-0036 rejected conflating refusal and hedging outright; ADR-0038 does not simply reopen that question — it builds a genuinely separate, schema-enforced-mutually-exclusive remediation tier, rejecting both "no soft option" and "hedge-as-refusal-adjacent" |

| Axiom | Honors / Tension / Violates | Citation |
|---|---|---|
| 1. Geometry-First | n/a | Pack/ethics-verdict-driven textual operation; no geometry involved |
| 2. Field-State | n/a | Same |
| 3. Propagation-over-Mutation | Tension | `inject_hedge` is a late-stage, explicit string-prepend mutation applied to an already-finalized `response_surface` after every composer arm has run (`chat/runtime.py:3105-3109`) — a textbook instance of the stepwise-mutate-after-the-fact shape axiom 3 cautions against, more pronounced than ADR-0028's case because it operates on an already-produced artifact rather than during assembly |
| 4. Dual-Correction | n/a | — |
| 5. Reconstruction-over-Storage | Honors | Hedge phrase and opt-in commitments are both read from their respective packs at call time; nothing is cached or duplicated |
| 6. Compilation-Last | n/a | — |
| 7. Reality-over-Inheritance | Honors | Deliberately declines to reuse or extend the refusal mechanism (ADR-0036/0037) even though structurally adjacent, because the two serve different audit meanings — a considered, not inherited, choice, explicitly reasoned in the ADR's context section |

### 5. Build fidelity — does the code match the decision?

Exact match on every claim in §1/§2, including subtle ones: the "stub path does not hedge" claim (hedge injection is scoped to the block following the main-path dispatch, confirmed structurally inside the same `if` region that also handles warm-pack/planner surfaces — not reachable from the stub-path branch earlier in the function), and the "evidence preservation" claim (only `response_surface`/`ChatResponse.surface` is mutated; `walk_surface` was already captured earlier at `chat/runtime.py:2969`, before the hedge-injection block runs, so it is structurally unaffected).

**Build-fidelity axis: matches.**

### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs

- No contradiction against `Whitepaper.md`/`Yellowpaper.md` found.
- Explicitly sibling to ADR-0037 (`refusal_commitments`) and downstream of ADR-0036's refusal-vs-hedge boundary decision — both correctly cited and both verified consistent in code (mutual exclusion enforced at load time; refusal supersedes hedge in code-path order).
- Cites ADR-0028 as the canonical owner of hedge *phrasing* while this ADR owns hedge *triggering* — a real, load-bearing distinction, but one the ADR's own "Open questions deferred to a future ADR" §5 flags as not yet made explicit at the architecture level ("a future ADR could make the relationship explicit... assembler is responsible for alignment-score-driven hedges; runtime is responsible for ethics-violation-driven hedges; never both fire on the same turn" — note this framing is itself only a proposed future clarification, not a currently-enforced invariant; nothing in the code today prevents both firing on the same turn, since `_apply_hedge` can already have hedged `walk_surface` before `inject_hedge` runs on `response_surface`, with only the idempotent-on-prefix check preventing a visible double-hedge, and only when the two would produce byte-identical phrases).
- A later, out-of-zone ADR-0254 (2026-07-23) adds a third, independent hedge mechanism (`_grounded_open_hedge_resolution`, geometric-coherence-gated) and cites ADR-0038 as a companion doc, but does not resolve ADR-0038's own deferred §5 question — the hedge concept has continued to fragment past this ADR's writing without the promised reconciling ADR yet appearing.
- **Continuity axis: clean** on this ADR's own terms (no contradiction of anything it commits to), but the multi-ADR hedge landscape it sits in has silently grown rather than converged — see AA-B4-3.

### 7. Necessity / generality

1. **Necessity:** the *soft-remediation-tier* problem is real — ADR-0036 correctly ruled out conflating hedge and refusal for safety, leaving exactly the gap ADR-0038 fills for ethics commitments. Confirmed load-bearing under a non-default configuration by §3's sabotage test.
2. **Reducibility:** not reducible to an L0/L1 geometric primitive — this is inherently a pack-policy/runtime-remediation concern.
3. **Extensibility / generalization-candidate — this is the central finding of the zone.** ADR-0038's own title claims to be "the runtime-level affordance" for hedge injection, but its `inject_hedge()` does not route through, call, or share state with `_apply_hedge()` (ADR-0028/0030/0031's operator). The two mechanisms:
   - are gated by different signals (ethics-verdict violation vs. identity-alignment threshold band);
   - run at different times in the turn (after all composer arms, vs. during sentence assembly);
   - consume different slices of `SurfacePreferences` (2 of 8 fields — soft/strong only — vs. all 8, including `axis_hedges` and per-language phrases);
   - are only prevented from double-hedging by an incidental idempotent-on-prefix string check, not by a shared "has this turn already been hedged" signal.
   ADR-0038 itself names this gap as an explicit open question ("Interaction with assembler hedges (ADR-0028)") and defers it. The team's own `docs/assessment/20-component-cards/surface-selection.md` independently corroborates the pattern, describing "hedge" as one of several accreted composer arms with no declared cross-arm precedence rule, and a later ADR-0254 has since added a *third* independent hedge site without resolving either gap. This is a strong, multiply-corroborated case for treating "hedge injection" as a genuine generalization candidate: one operator, parameterized by trigger-signal (alignment band / ethics verdict / geometric coherence) and phrase source, rather than three-to-four independently-maintained call sites.

**Necessity/generality axis: generalization-candidate** — see AA-B4-3.

### 8. Fitness / value

- `tests/test_hedge_injection.py` — 22/22 pass (re-run fresh at `cbfc8ccb`), including the ChatRuntime-integration subset (default pack does not inject; opt-in pack injects on violation; refusal supersedes hedge).
- `evals/audit_tour/run_tour.py::_scene_3_ethics_hedge_opt_in` demonstrates the pure-helper behavior for an operator audience, but explicitly bypasses the live turn loop — weaker evidence than the integration tests, cited as such.
- No evidence found of `hedge_commitments` being exercised by any shipped, non-worked-example deployment configuration; the four domain packs that opt commitments in (`medical_clinical_ethics_v1`, `engineering_ethics_v1`, `legal_ethics_v1`, `research_ethics_v1`) are referenced only in `docs/pack_inventory_2026-05-21.md` and their own ADRs/tests — no eval, CLI default, or production config path was found loading them. This audit's own Tier-C triage of ADR-0044 (`docs/adr-audit/12-triage-log.md`) independently reaches the same characterization for the medical pack specifically: "a worked-example domain pack (single instance, not a mechanism)."

**Fitness axis:** code-level mechanism confirmed live and correct by 22 passing tests including integration coverage; real-world/deployment fitness evidence beyond tests is "no evidence found," and the mechanism has no CLI-exposed operator affordance today.

### 9. Findings raised

- 🟡 AA-B4-2 — ADR-0038's `hedge_commitments` channel has no CLI-exposed operator affordance in `core chat` (only `--identity` exists; no `--ethics`/pack-select flag), and the shipped default ethics pack ships `hedge_commitments: []`, so in the out-of-the-box product the mechanism is fully wired, tested, and unconditionally reachable in code, but structurally never fires. (§3, §8)
- 🔵 AA-B4-3 — the "hedge" concept has fragmented into at least two independently-implemented, non-unified mechanisms within this zone (`_apply_hedge` — ADR-0028/0030/0031; `inject_hedge` — ADR-0038), plus a third outside the zone (ADR-0254's `_grounded_open_hedge_resolution`), none of which route through a shared operator despite ADR-0038 explicitly billing itself as "Hedge Injection as a Runtime-Level Affordance." ADR-0038's own §"Open questions" names this gap; it remains unresolved as of `cbfc8ccb`. Corroborated independently by `docs/assessment/20-component-cards/surface-selection.md`'s composer/resolver-arm analysis. (§6, §7)
- 🟢 AA-B4-1 — (cross-referenced, see ADR-0028's card) minor citation drift: ADR-0038's own Companion docs line links to `ADR-0028-surface-preferences.md`, a filename that does not exist (the real file is `ADR-0028-identity-surface-wiring.md`).

### 10. Evidence sources actually consulted

- `docs/adr/ADR-0038-hedge-injection.md` (full read), `docs/adr/ADR-0036-safety-refusal-policy.md` and `docs/adr/ADR-0037-per-predicate-ethics-refusal.md` (context, not carded — out of zone), `docs/adr/ADR-0254-grounded-open-hedge-arm.md` (skimmed for the third-mechanism corroboration, out of zone, not carded)
- Code: `chat/refusal.py`, `packs/ethics/loader.py`, `chat/runtime.py` (all read directly, including the exact call site at `:3105-3109` and the confirmation that `response_surface = walk_surface` at `:3034` shows the two hedge mechanisms can act on the same string sequentially)
- `packs/ethics/{default_general_ethics_v1,medical_clinical_ethics_v1,engineering_ethics_v1,legal_ethics_v1,research_ethics_v1}.json` — parsed directly to confirm `hedge_commitments` contents
- `core/cli.py` — grepped for `--identity`/`--ethics` flags to confirm the CLI-affordance gap
- `evals/audit_tour/run_tour.py` — read the `_scene_3_ethics_hedge_opt_in` function in full
- `tests/test_hedge_injection.py` — re-run fresh (22/22 pass)
- `docs/assessment/20-component-cards/surface-selection.md`, `docs/assessment/10-layer-cards/M4-expression-serving.md` — read in full
- `docs/adr-audit/12-triage-log.md` — grepped for ADR-0044 (medical ethics pack) disposition
- `docs/pack_inventory_2026-05-21.md` — grepped for domain-pack usage references

---

## Zone findings

- 🟢 **AA-B4-1** — Citation drift, cosmetic. ADR-0028's Governance Cross-Reference cites `chat/surface.py` (nonexistent; real file is `generate/surface.py`); ADR-0038's Companion docs line cites `ADR-0028-surface-preferences.md` (nonexistent; real file is `ADR-0028-identity-surface-wiring.md`). No runtime or design impact — documentation-only.
- 🟡 **AA-B4-2** — Reachability gap. ADR-0038's `hedge_commitments` channel is fully wired, live, and test-covered, but (a) has no CLI-exposed operator affordance (`core chat` exposes `--identity` but no ethics-pack-select flag) and (b) ships with `hedge_commitments: []` on the default pack, so it structurally never fires in the out-of-the-box product. Worth a follow-up ADR or CLI change if this remediation tier is meant to be operator-reachable in practice, not just programmatically reachable in tests.
- 🔵 **AA-B4-3** — Consolidation candidate (the zone's central finding). ADR-0028/0030/0031 correctly consolidate into one operator (`generate/surface.py::_apply_hedge`) across three ADRs. ADR-0038 does not join that consolidation despite its title's framing as "the runtime-level affordance" for hedge injection — it is a second, independent mechanism (`chat/refusal.py::inject_hedge`) triggered by a different signal (ethics verdict vs. alignment band), running at a different pipeline stage, consuming only 2 of `SurfacePreferences`' 8 fields, and prevented from double-firing only by an incidental idempotent-on-prefix string check. ADR-0038 itself names this gap as an open question and defers it; it remains open as of `cbfc8ccb`. A later, out-of-zone ADR-0254 adds a third independent hedge site without resolving either gap. Recommend routing to the triage queue as a 🔵 Consolidate candidate: either (a) generalize `_apply_hedge`/`inject_hedge` into one operator parameterized by trigger-signal and phrase source, or (b) if kept separate, ratify an explicit invariant (not just a proposed one) governing which mechanism owns which turns, per ADR-0038's own §5 suggestion.
- 🟢 **AA-B4-4** — Term overload, not a functional defect. `alignment` names two independently-computed, unrelated quantities in the codebase: `IdentityScore.alignment` (this zone's Gram-computed per-axis deviation scalar) and FA-1's cross-language holonomy "alignment" (ruled NO-GO, `docs/analysis/fa1-holonomy-gate-verdict-2026-07-28.md`). Verified computationally independent — no cascading contamination from the FA-1 ruling reaches this zone's mechanisms — but the shared name is a Pillar II (Semantic Rigor) risk worth a corpus-wide glossary note at Phase 4/5 synthesis.

**Summary verdicts:** ADR-0028 — Build: full, Liveness: live, Continuity: clean, Necessity: generalization-candidate. ADR-0030 — Build: full, Liveness: live, Continuity: clean, Necessity: irreducible (clean extension). ADR-0031 — Build: full, Liveness: live, Continuity: clean, Necessity: irreducible (clean extension). ADR-0038 — Build: full, Liveness: live (unconditionally reached; fires only under non-default, CLI-unreachable configuration), Continuity: clean (on its own terms; landscape has fragmented since), Necessity: generalization-candidate.
