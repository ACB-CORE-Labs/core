# B6 — Pack-Grounded Cold-Start Surfaces & Intent

**Zone / stack:** B6 (macro layers M3/M1) | **Tier:** B | **Batch:** 1 (ADR-0001–0050)
**Members:** ADR-0047, ADR-0048, ADR-0049, ADR-0050 | **Card author:** Claude (Tier B audit agent, Sonnet 5)
**`verified_at` SHA:** `cbfc8ccb` (`cbfc8ccbf7fe503ab31abe7aedbb1973ba7d7b4d`, 2026-07-28)

All four ADRs date from a single day (2026-05-18) and read as one causal chain rather than four independent decisions: ADR-0047 wires ADR-0046's forward-admissibility primitive into the live chat hot path and, in doing so, isolates a finding — narrowing the walk's candidate pool does not change the *surface* the runtime emits, because the real cognition-lane gap sits downstream of propagation, in cold-start surface assembly. ADR-0048 closes that gap for DEFINITION/RECALL by teaching the runtime a second grounding source (the ratified `en_core_cognition_v1` pack, not just the empty session vault); ADR-0049 fixes the intent-classifier subject-extraction bug that was silently suppressing part of ADR-0048's lift; ADR-0050 extends the same pack-grounded pattern to COMPARISON. Verified against the current tree (not just the ADRs' own prose): ADR-0047's flag is real, wired, tested — and confirmed by its own direct sequel, ADR-0058 ("Engaged but Inert"), to still default off with zero production adoption and no recorded closure criterion, a live instance of the "transition windows that never close" pattern named in `docs/plans/2026-07-28-perception-arc.md`. ADR-0048 and ADR-0050 are **not** independent parallel reimplementations of cold-start grounding — `chat/runtime.py:_maybe_pack_grounded_surface`'s own docstring states plainly that "ADR-0048 / ADR-0050 / ADR-0052 — three reviewed sources of cold-start grounding share this dispatcher," and that dispatcher has since grown into the general cold-start-surface router for nearly every intent shape in the system. ADR-0049 turns out to be narrower than its title suggests: it is a lemma-cleaning post-processor consumed by the DEFINITION/RECALL/CAUSE/VERIFICATION paths, not the branch-selecting router itself (that role belongs to the pre-existing `_RULES`/`IntentTag` classifier from ADR-0018). All four ADRs' code artifacts were found live and their dedicated test suites (109 tests across the four `test_*` files) pass at the verified SHA.

---

## ADR-0047 — Wire the Forward Graph Constraint into the Chat Hot Path

**Audit ID (if a numbering collision):** — | **Family (if phased):** — (direct sequel: ADR-0058, not a B6 member)
**Zone / stack:** B6 — Pack-Grounded Cold-Start Surfaces & Intent (M3/M1) | **Tier:** B
**ADR status (as recorded in the file):** Accepted | **ADR date:** 2026-05-18
**Card author:** Claude (Tier B audit agent) | **`verified_at` SHA:** `cbfc8ccb`

---

### 1. Content summary

- **Decision made:** Wire ADR-0046's `build_graph_constraint` (which turns a `PropositionGraph` into an `AdmissibilityRegion`) into the live chat hot path, behind a new opt-in `RuntimeConfig.forward_graph_constraint` flag (default `False`). When the flag is `True` and `output_language == "en"`, build the graph from the raw input text *before* `generate()` runs and pass the resulting region into the walk.
- **Alternatives explicitly rejected:** Always-on wiring — tried first, produced 15 test failures via `InnerLoopExhaustion` because many benign inputs' graph-derived admissibility region does not intersect the walk's `top_k=8` candidate pool. Rejected in favor of opt-in so the honest-refusal contract (ADR-0024) stays intact and operators can characterize the behavior before any default change.
- **Artifacts the ADR claims will exist:**
  - `generate/intent_bridge.py:build_graph_from_input(text, plan) -> PropositionGraph`
  - `RuntimeConfig.forward_graph_constraint: bool = False`
  - `chat/runtime.py` pre-`generate()` call to `build_graph_from_input` + `build_graph_constraint`, gated on the flag and `output_language == "en"`
  - `tests/test_forward_graph_constraint_wiring.py` (5 tests)

### 2. Implementation cross-reference

| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `build_graph_from_input` | yes | `generate/intent_bridge.py:205` | Public helper, matches decision |
| `RuntimeConfig.forward_graph_constraint` default `False` | yes | `core/config.py:64` | Matches |
| Pre-`generate()` wiring in `chat/runtime.py` | yes | `chat/runtime.py:2821–2824` (guard at `:2823`) | `pre_gen_graph = build_graph_from_input(...)`; `forward_region = build_graph_constraint(...)` passed into `generate()` |
| `tests/test_forward_graph_constraint_wiring.py` | yes | `tests/test_forward_graph_constraint_wiring.py` | Ran locally at verified SHA — all green |

**Build axis:** full — every claimed artifact is present and structurally unchanged from the decision.

### 3. Liveness / integration

- The code path is real and reachable, but only when an operator explicitly sets `forward_graph_constraint=True`; production default is `False`. ADR-0058 (dated the same day, a direct sequel not itself a B6 member) rules formally that "no production identity pack ... opts into the flag" and promotes the observed zero-effect finding to a CI-enforced invariant (`tests/test_forward_graph_constraint_null_lift.py`, confirmed present and passing at the verified SHA). At the current SHA, `docs/specs/flag_register.md` §3a still lists `forward_graph_constraint` under "waiting on a transition window that has not been closed ... the window's end is not recorded," and `docs/plans/2026-07-28-perception-arc.md` §2b names this exact flag, by number, as part of an "accumulated hesitancy" cluster: "correct mechanisms built dark behind unruled flags ... the disease is not 'never built'; it is transition windows that never close."
- **Sabotage test:** at the flag's shipped default (`False`), removing the entire mechanism would produce a byte-identical production observable — this is not a hypothesis, it is a CI-pinned fact (`test_forward_graph_constraint_null_lift.py` asserts flag-OFF and flag-ON produce pairwise-identical `intent_accuracy` / `surface_groundedness` / `term_capture_rate` / `versor_closure_rate` on the cognition split, and ADR-0047's own A/B table shows Δ=0 on every metric even with the flag flipped ON). The mechanism is real, tested, and reachable via config — not scaffolding — but by the charter's own sabotage-test standard, its *production* configuration is decoration today.
- **Liveness axis:** wired-but-unreached — reachable via config, default off, zero production adoption, own governing ADR (0058) formalizes the null lift rather than treating it as transitional.

### 4. Design fidelity — pillars and axioms

| Pillar | Honors / Tension / Violates | Citation (ADR clause + pillar text) |
|---|---|---|
| I. Mechanical Sympathy | Honors | The opt-in decision responds to measured `InnerLoopExhaustion` behavior at real pack sizes ("A first attempt wired the constraint unconditionally ... produced 15 test failures"), not assumption. |
| II. Semantic Rigor | Honors | Explicit refusal to retune `top_k` "until the failure goes away" because that "would erase the architectural information that the geometry of the graph and the geometry of the walk are not yet co-located." |
| III. Third Door | Tension | Opt-in-behind-a-flag was a genuine third option vs. "always-on" / "don't build it" at the time — but per `flag_register.md`'s own framing this instance has become the pattern it warns against: an unplanned fourth outcome ("flip a flag, never revisit it") the ADR did not anticipate. |

| Axiom | Honors / Tension / Violates | Citation |
|---|---|---|
| 1. Geometry-First | Honors | Builds an `AdmissibilityRegion` (geometric constraint) from the graph before generation rather than filtering post-hoc. |
| 2. Field-State | n/a | No field-state representation change. |
| 3. Propagation-over-Mutation | Honors | The region narrows the walk's candidate pool per-step (a propagation-time constraint), not a one-shot output mutation. |
| 4. Dual-Correction | n/a | — |
| 5. Reconstruction-over-Storage | n/a | — |
| 6. Compilation-Last | n/a | — |
| 7. Reality-over-Inheritance | Tension | The mechanism survives in production purely as an inert, flagged-off feature with no closure criterion — precisely the kind of decoration this axiom's own cited track record (spectral-normalization monitor, grade guard, etc.) says gets deleted; that deletion-or-ratification step has not yet happened here. |

### 5. Build fidelity — does the code match the decision?

The shipped code (`chat/runtime.py:2821–2824`, `core/config.py:64`, `generate/intent_bridge.py:205`) is structurally identical to what ADR-0047 decided: same flag name, same default, same `output_language == "en"` guard, same pre-`generate()` ordering. No drift found.

**Build-fidelity axis:** matches.

### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs

- No direct Whitepaper/Yellowpaper contradiction found.
- Cleanly extended by ADR-0058 the same day — a documented, explicit sequel, not a silent one. ADR-0058 is not itself a member of this zone (per `02-stack-taxonomy.md`'s B6 row), which leaves a scoping seam: the flag's full arc (introduce → wire → rule inert) spans A4 (ADR-0046) and B6 (ADR-0047) without the ruling ADR (0058) sitting in either — worth flagging to the audit lead rather than treating as a defect of ADR-0047 itself.
- **Continuity axis:** clean — the transition is explicitly documented (ADR-0058), not a silent contradiction.

### 7. Necessity / generality

1. **Necessity:** In its current (default-off, zero-adoption) configuration the mechanism is not load-bearing for anything the system currently does in production — a dormant capability, not a currently-necessary one (restates §3).
2. **Reducibility:** `AdmissibilityRegion` construction and CGA-neighbourhood filtering already exist as the L0/L1 primitive from ADR-0022/0024/0025/0026 (audited separately, zone A4). ADR-0047 does not introduce new geometry — it supplies a second call site (forward, pre-generation) for a region-construction function that already existed for the post-hoc path. It is a wiring decision over an existing primitive, not a new mechanism to consolidate away.
3. **Extensibility:** `docs/specs/flag_register.md` groups this flag explicitly with `unified_ingest` (0090), `realizer_grounded_authority` (0088), and `recognition_grounded_graph` (0144) as "the same unfinished migration" — a real candidate for one follow-up ADR giving all four flags a shared closure criterion, rather than four separately-open questions.

**Necessity/generality axis:** reducible-to-`AdmissibilityRegion` (ADR-0022/0046's existing primitive) — the hot-path wiring is a legitimate second call site, not a new mechanism; its unresolved status is a governance gap (no closure criterion), not a design flaw.

### 8. Fitness / value

No positive fitness evidence found for the flag in its actual (default, off) production state — nothing in the codebase depends on it being on. The only measurements on file (ADR-0047's own A/B, and the CI-pinned null-lift test) report the *absence* of an effect, honestly. `docs/plans/2026-07-28-perception-arc.md` cites this flag by name as an instance of "accumulated hesitancy," which is the closest thing to a synthesized judgment on file — and it is a named gap, not evidence of positive contribution.

**Fitness axis:** no positive evidence found; one negative/gap finding already on file (`docs/plans/2026-07-28-perception-arc.md`, `docs/specs/flag_register.md`).

### 9. Findings raised

- **AA-B6-1** 🟡 Repair: `forward_graph_constraint` (ADR-0047/0058) is wired, tested, and CI-confirmed to have zero observable production effect while off — ADR-0058 declares this a stable state with no recorded closure criterion, and `docs/specs/flag_register.md` still lists it in the unclosed-transition-window cluster at the current SHA. See §3, §7.
- **AA-B6-2** 🟢 Monitor: independently confirmed (not merely on ADR-0046's say-so) that "wired into the chat hot path" is a true code fact — real, reachable, tested — even though the flag defaults off in production. See §2, §3.

### 10. Evidence sources actually consulted

- Read ADR-0047 and ADR-0058 in full (`docs/adr/`).
- Code read: `core/config.py:64`, `chat/runtime.py:612`, `:2821–2824`, `generate/intent_bridge.py:205`, `generate/graph_constraint.py:109`.
- Ran `tests/test_forward_graph_constraint_wiring.py` and `tests/test_forward_graph_constraint_null_lift.py` locally at `cbfc8ccb` — both green.
- `docs/specs/flag_register.md` §3a; `docs/plans/2026-07-28-perception-arc.md` §2b; `docs/audit/substrate-liveness-registry.md` (ADR-0047/0058 rows).
- `docs/assessment/10-layer-cards/M3-comprehension-reasoning.md`, `M1-knowledge-memory.md` (zone context; no direct ADR-0047/0058 mention).
- `docs/adr-audit/01-adr-census.md`, `02-stack-taxonomy.md`.

---

## ADR-0048 — Pack-Grounded Surface for Cold-Start DEFINITION / RECALL

**Audit ID (if a numbering collision):** — | **Family (if phased):** — (sibling family with ADR-0050/0052, latter not a B6 member)
**Zone / stack:** B6 — Pack-Grounded Cold-Start Surfaces & Intent (M3/M1) | **Tier:** B
**ADR status (as recorded in the file):** Accepted | **ADR date:** 2026-05-18
**Card author:** Claude (Tier B audit agent) | **`verified_at` SHA:** `cbfc8ccb`

---

### 1. Content summary

- **Decision made:** When `UnknownDomainGate` fires with `source="empty_vault"` on an English DEFINITION/RECALL turn whose subject lemma is in the ratified `en_core_cognition_v1` pack, emit a deterministic pack-grounded surface (lemma + verbatim `semantic_domains`) instead of the universal disclosure. Tag provenance via a new `grounding_source` field on `ChatResponse`/`TurnEvent`, valued `{"vault","pack","none"}`.
- **Alternatives explicitly rejected:** None named explicitly; the implicit prior state (treat every cold-start turn as universally ungrounded regardless of pack content) is rejected as eliding real evidence the system holds.
- **Artifacts the ADR claims will exist:**
  - `chat/pack_grounding.py` (new) — `pack_grounded_surface(lemma) -> str | None`
  - `chat/runtime.py:_stub_response` extended with a `pack_grounded_surface` parameter; new helper `_maybe_pack_grounded_surface(text, gate_source)`
  - `ChatResponse.grounding_source`, `TurnEvent.grounding_source` fields
  - `core/cognition/pipeline.py` — `gate_fired` detection switched from string-matching `_UNKNOWN_DOMAIN_SURFACE` to `response.vault_hits == 0 and response.grounding_source != "vault"`
  - `tests/test_pack_grounding.py` (18 tests)

### 2. Implementation cross-reference

| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `chat/pack_grounding.py:pack_grounded_surface` | yes | `chat/pack_grounding.py:500` | Present; gained optional `register`/`anchor_lens` kwargs since 2026-05-18, core contract intact |
| `chat/runtime.py:_maybe_pack_grounded_surface` | yes | `chat/runtime.py:1833` | Present but grown far beyond original scope — now the shared dispatcher for ADR-0048/0050/0052 plus deduction/curriculum/NARRATIVE/EXAMPLE/CAUSE/VERIFICATION/CORRECTION/PROCEDURE/UNKNOWN branches (see §7) |
| `ChatResponse`/`TurnEvent.grounding_source` | yes | `chat/runtime.py:485` | Field docstring explicitly cites "ADR-0048 / ADR-0050" by number; value set widened to include `"teaching"`, `"deduction"`, `"curriculum"` alongside the original three |
| `pipeline.py` `gate_fired` via `grounding_source` | partial | `core/cognition/pipeline.py:515` | Current code reads `grounding_src = getattr(response, "grounding_source", "") or ""`, consumed by a broader `resolve_surface(...)` "shadow coherence gate" (comment: "SHADOW COHERENCE GATE WIRING", T13); the literal expression quoted in the ADR is not found verbatim — absorbed into a more general mechanism, not dropped |
| `tests/test_pack_grounding.py` | yes | `tests/test_pack_grounding.py` | Ran locally at verified SHA — all green |

**Build axis:** full — every claimed artifact exists and is live; the one `partial` row is generalization past the ADR-era description, not drift or absence.

### 3. Liveness / integration

- Reached unconditionally on the live serving path (no opt-in flag) — `_maybe_pack_grounded_surface` is called directly from `ChatRuntime.chat()`'s stub-path handling (`chat/runtime.py:2699`, `:3035`), gated only by `output_language == "en"` and the gate-fired/empty-vault condition itself.
- **Sabotage test:** removing `pack_grounded_surface` and the DEFINITION/RECALL branch would make every cold-start DEFINITION/RECALL turn on a pack-known lemma fall back to the universal disclosure — a directly observable surface-text change. Confirmed both by the ADR's own A/B (`surface_groundedness` 15.4%→46.2%, `term_capture_rate` 0.0%→33.3%) and independently by `evals/cognition/results/v1_public_*.json` (1.0/1.0 on the public split).
- **Liveness axis:** live.

### 4. Design fidelity — pillars and axioms

| Pillar | Honors / Tension / Violates | Citation |
|---|---|---|
| I. Mechanical Sympathy | Honors | Targets the actually-measured failure (empty session vault → 100% universal disclosure) located by ADR-0047's characterization, not a hypothesized gap. |
| II. Semantic Rigor | Honors | "Pack evidence is reviewed/curated memory, the strongest form of grounding short of session vault evidence" — enforces a hard textual boundary ("No session evidence yet.") between grounding tiers rather than blurring them. |
| III. Third Door | Honors | Reframes "gate fires → universal disclosure" as "the system has two grounding sources, not one" — neither widens the gate's threshold nor adds an LLM fallback. |

| Axiom | Honors / Tension / Violates | Citation |
|---|---|---|
| 1. Geometry-First | n/a | Lexicon/string lookup, not a geometric operator. |
| 2. Field-State | n/a | — |
| 3. Propagation-over-Mutation | n/a | — |
| 4. Dual-Correction | n/a | — |
| 5. Reconstruction-over-Storage | Tension | Surface is composed verbatim from stored `semantic_domains` strings (reconstruction-aligned in spirit), but the mechanism is a template-composition function over stored rows — closer to lookup-and-format than the axiom's field/geometry sense. Marked Tension rather than forcing a Honors call the axiom wasn't written for. |
| 6. Compilation-Last | n/a | — |
| 7. Reality-over-Inheritance | Honors | The ADR justifies the mechanism point-by-point against the codebase's fabrication doctrine (not opaque, not stochastic, not hidden normalisation, not hot-path repair, not approximate recall) rather than defaulting to an inherited LLM-fallback pattern. |

### 5. Build fidelity — does the code match the decision?

Matches, with one generalization beyond the literal text: the `gate_fired` expression quoted in the ADR (`response.vault_hits == 0 and response.grounding_source != "vault"`) is not present verbatim at the current SHA — it has been absorbed into a broader `resolve_surface`/"shadow coherence gate" mechanism (`core/cognition/pipeline.py:509–527`) that consumes `grounding_source` as one of several inputs. This is evolution consistent with the decision's intent (`grounding_source` remains the provenance signal consumed downstream), not contradiction.

**Build-fidelity axis:** matches (one flagged citation drift, non-contradictory — see §2).

### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs

- ADR-0048 cites "CLAUDE.md is explicit: Semantic Pack Discipline ...". At the current SHA, the repo-root `CLAUDE.md` has been reduced to a thin pointer ("Do not place architecture, invariants, memory rules ... here. Update AGENTS.md instead.") and no longer carries that passage; the underlying doctrine survives in `AGENTS.md:424` ("avoid hidden normalization, stochastic fallback, approximate recall, and unreviewed mutation"). This is a governance-file consolidation, not a doctrinal reversal — the substance the ADR leaned on is still enforced, just relocated. Non-blocking citation-drift note, not a contradiction.
- No Whitepaper/Yellowpaper contradiction found.
- Cleanly extended by ADR-0049 (subject normalization), ADR-0050 (COMPARISON sibling, this zone), ADR-0052 (CAUSE/VERIFICATION teaching-grounded sibling, not a B6 member), and further by ADR-0061/62/63/64/65/66/69/73c/77/83/85/86 per `docs/audit/substrate-liveness-registry.md` and the code's own accreted dispatcher — a long, explicitly documented lineage.
- **Continuity axis:** clean (one non-blocking citation-drift note re: CLAUDE.md relocation).

### 7. Necessity / generality

1. **Necessity:** Irreducible in its narrow sense — the specific gap it closes (cold-start turns with zero session-vault hits but pack-resident knowledge) has no other mechanism supplying the same evidence tier; §3's sabotage test confirms removal changes served output on real eval cases.
2. **Reducibility:** Does not reduce to an L0/L1 geometric primitive — it is an L1/M1 (pack/vault) lexicon lookup composed at L5/M4 (surface assembly), correctly placed per the M1 layer card's description of packs as "reviewed pack data."
3. **Extensibility — the zone's central question, directly confirmed in code, not inferred:** `chat/runtime.py:_maybe_pack_grounded_surface`'s own docstring states: *"ADR-0048 / ADR-0050 / ADR-0052 — three reviewed sources of cold-start grounding share this dispatcher."* The function has since also absorbed NARRATIVE, EXAMPLE, CORRECTION, PROCEDURE, and UNKNOWN-intent branches. ADR-0048 is the seed of what is now a single, general cold-start-surface dispatcher — resolved: **shared mechanism, not parallel duplicate** (see ADR-0050 §7 for the corresponding half of this finding).

**Necessity/generality axis:** generalization-candidate realized — ADR-0048 is the seed case of a now-general composer-dispatch pattern (`_maybe_pack_grounded_surface`), later explicitly extended (not duplicated) by ADR-0050/0052 and five further ADRs.

### 8. Fitness / value

`evals/cognition/` is a real eval lane with a written contract (`evals/cognition/contract.md`: `term_capture_rate >= 0.80`, `surface_groundedness >= 0.80`) and result artifacts. `v1_public_20260516T053348Z.json` / `...053445Z.json`: 1.0/1.0 (meets contract). `v1_dev_20260518T143412Z.json`: 0.692/0.571 (below contract on both metrics). `v1_holdout_20260518T205459Z.json`: 0.947/0.708 (meets groundedness, misses term-capture). These results are contemporaneous with the ADR (dated 2026-05-16/18) and have not been re-run since — no result file postdates the ADR-0048–0053 family, and `CLAIMS.md` carries no pin for `evals/cognition/` at all. `docs/PROGRESS.md:788` records "[x] ADR-0048..0066 Pack-grounded surface composers for every intent shape" as a completed checklist line — a document, not a measurement.

**Fitness axis:** historical evidence found (`evals/cognition/results/`, dated at ADR-adjacent commits) meeting contract on the public split but missing it on dev/holdout; not re-measured or `CLAIMS.md`-pinned at the current audit SHA.

### 9. Findings raised

- **AA-B6-3** 🔵 Consolidate (confirms, does not newly propose): ADR-0048/0050/0052 share one dispatcher (`chat/runtime.py:_maybe_pack_grounded_surface`) by explicit in-code citation — this zone's necessity/generality question is answered: no duplicate parallel builds. See §7.
- **AA-B6-4** 🟡 Repair: `evals/cognition/` results are stale (last touched at ADR-0048-era commits, no post-hoc re-run, no `CLAIMS.md` pin), and two of three splits (dev, holdout) already missed the lane's own ≥0.80 contract when last measured — current fitness is unverified. See §8.
- **AA-B6-5** 🟢 Monitor: ADR-0048's doctrinal citation ("CLAUDE.md ... Semantic Pack Discipline") points at a file now reduced to a stub; the doctrine survives in `AGENTS.md` but the citation is stale. See §6.

### 10. Evidence sources actually consulted

- Read ADR-0048 in full.
- Code read: `chat/pack_grounding.py:405–620`, `chat/runtime.py:460–495`, `:1833–2130`, `:2699`, `:3035`, `core/cognition/pipeline.py:505–525`.
- Ran `tests/test_pack_grounding.py` locally at `cbfc8ccb` — green.
- `evals/cognition/contract.md`, `evals/cognition/results/*.json`; grepped `CLAIMS.md` for "cognition" (no hits).
- `docs/PROGRESS.md:788`.
- Repo-root `CLAUDE.md` (current), `AGENTS.md:424`.
- `docs/assessment/10-layer-cards/M1-knowledge-memory.md`.

---

## ADR-0049 — Intent Classifier Head-Noun Subject Extraction

**Audit ID (if a numbering collision):** — | **Family (if phased):** —
**Zone / stack:** B6 — Pack-Grounded Cold-Start Surfaces & Intent (M3/M1) | **Tier:** B
**ADR status (as recorded in the file):** Accepted | **ADR date:** 2026-05-18
**Card author:** Claude (Tier B audit agent) | **`verified_at` SHA:** `cbfc8ccb`

---

### 1. Content summary

- **Decision made:** Add a deterministic post-processor `_normalize_subject(phrase, tag)` in `generate/intent.py`, run after the `_RULES` table fires, using closed frozensets `_ARTICLES`/`_AUX_VERBS` to strip leading articles/aux-verbs and trailing punctuation and return a clean lemma — multi-word noun phrases preserved for DEFINITION/RECALL/PROCEDURE, head noun only for CAUSE/VERIFICATION.
- **Alternatives explicitly rejected:** Implicit — each downstream consumer (pack lookup, graph builder, future teaching-store inference) implementing its own article-stripping heuristic, rejected in favor of a single classifier-boundary fix.
- **Artifacts the ADR claims will exist:**
  - `generate/intent.py:_normalize_subject`, `_ARTICLES`, `_AUX_VERBS`
  - `DialogueIntent.subject` becomes a clean lemma for every intent routed through `_RULES`
  - `tests/test_intent_subject_extraction.py` (30 tests)

### 2. Implementation cross-reference

| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `_normalize_subject` | yes | `generate/intent.py:280` | Present; gained a third frozenset `_INFINITIVE_MARKERS` since 2026-05-18 (handles "What is to create?") — additive, not contradicting |
| `_ARTICLES` | yes | `generate/intent.py:266` | Matches exactly |
| `_AUX_VERBS` | yes | `generate/intent.py:267–271` | Matches exactly |
| `DialogueIntent.subject` normalized at `_RULES` call sites | yes | `generate/intent.py:358–457` | Confirmed — `_normalize_subject` invoked at every `_RULES`-routed branch |
| `tests/test_intent_subject_extraction.py` | yes | `tests/test_intent_subject_extraction.py` | Ran locally at verified SHA — all green |

**Build axis:** full.

### 3. Liveness / integration

- `classify_intent` is the live intent classifier, consumed by `generate/intent_bridge.py:classify_intent_from_input`, itself called from `chat/runtime.py:_maybe_pack_grounded_surface` (`~line 1997`) and by the forward-graph-constraint builder (ADR-0047). Every DEFINITION/RECALL/CAUSE/VERIFICATION/CORRECTION/PROCEDURE turn passes through `_normalize_subject` unconditionally — no flag gates it.
- **Sabotage test:** removing `_normalize_subject` reverts `DialogueIntent.subject` to raw regex-captured spans (e.g. `"a procedure"`, `"does light exist"`); ADR-0048's pack lookup keys on exact lemma match, so this directly changes which cold-start turns lift to a pack-grounded surface — confirmed by the ADR's own A/B (`surface_groundedness` 46.2%→61.5%) and its explicit claim that exactly two additional eval cases lift via the article-stripping path.
- **Liveness axis:** live.

### 4. Design fidelity — pillars and axioms

| Pillar | Honors / Tension / Violates | Citation |
|---|---|---|
| I. Mechanical Sympathy | Honors | Traces six named prompts to six named failure reasons before designing the fix, rather than a general-purpose NLP solution. |
| II. Semantic Rigor | Honors | Precise distinction between "subject span" and "subject lemma" as the root cause; fix is a closed, auditable word-list, not a heuristic tagger. |
| III. Third Door | Honors | Rejects both "each consumer implements its own stripping" and "add a full POS tagger"; picks a narrow, closed-set syntactic transform at the classifier boundary. |

| Axiom | Honors / Tension / Violates | Citation |
|---|---|---|
| 1. Geometry-First | n/a | Pure string/dataclass-field transform. |
| 2. Field-State | n/a | — |
| 3. Propagation-over-Mutation | n/a | — |
| 4. Dual-Correction | n/a | — |
| 5. Reconstruction-over-Storage | n/a | — |
| 6. Compilation-Last | n/a | — |
| 7. Reality-over-Inheritance | Honors | Explicitly declines a heavier NLP/POS-tagging abstraction when a closed word-list suffices for the measured failure modes. |

### 5. Build fidelity — does the code match the decision?

Matches — the frozensets and function signature are unchanged from the ADR's description; the one addition (`_INFINITIVE_MARKERS`) is a later, additive extension in the same closed-set, deterministic style, not drift.

**Build-fidelity axis:** matches.

### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs

- No Whitepaper/Yellowpaper contradiction found (pure syntactic transform, no algebra/field claims — verified no `versor`/`rotor`/CGA references in `_normalize_subject`).
- Directly consumed by ADR-0048 (pack lookup keys on the cleaned lemma) and cited by ADR-0047 (graph-node construction via `graph_planner.graph_from_intent`). ADR-0050 explicitly and correctly does **not** consume it — COMPARISON uses its own named-group regex capture, documented as a deliberate choice in ADR-0050's own text and confirmed in code (§ADR-0050 below).
- **Continuity axis:** clean.

### 7. Necessity / generality

1. **Necessity:** Irreducible for its stated purpose — no other component performs article/aux-verb stripping on `DialogueIntent.subject`; removing it demonstrably regresses two confirmed eval cases (§3).
2. **Reducibility:** Does not reduce to an L0/L1 geometric/algebraic primitive — correctly scoped below the geometry layer, matching its own "no algebra changes" claim.
3. **Extensibility / routing role — the task's brief asked this card to verify the routing claim directly:** confirmed that `_normalize_subject`'s output feeds `DialogueIntent.subject`, which `_maybe_pack_grounded_surface` reads to key the DEFINITION/RECALL pack path and the CAUSE/VERIFICATION teaching path. However, **intent-tag routing itself** (which of DEFINITION/RECALL/COMPARISON/CAUSE/VERIFICATION/etc. a turn is) is decided by the `_RULES` regex table and `IntentTag` (pre-existing, ADR-0018), not by ADR-0049's post-processor — ADR-0049 only cleans the *lemma* after a branch is already chosen. COMPARISON, confirmed in code, bypasses `_normalize_subject` entirely (its own regex already produces clean captures).

**Necessity/generality axis:** irreducible (as a lemma-cleaning post-processor). Scoping clarification for the zone brief: the component that actually routes between surfaces (0048 vs. 0050 vs. others) is the pre-existing `_RULES`/`IntentTag` classifier from ADR-0018, not ADR-0049 — a clarification, not a defect.

### 8. Fitness / value

Direct measurement in the ADR itself (A/B on the 13-case cognition split: +15.3pp `surface_groundedness`, +16.7pp `term_capture_rate`), and confirmed as the baseline ADR-0050 builds on ("build on top of ADR-0049's article-stripping"). Same staleness caveat as ADR-0048 applies — no re-run or `CLAIMS.md` pin since 2026-05-18.

**Fitness axis:** historical evidence found (ADR-0049/0050's own chained A/B numbers); not independently re-verified at current SHA.

### 9. Findings raised

- **AA-B6-6** 🟢 Monitor: ADR-0049 is correctly built and live, but its role is narrower than "the routing classifier" — actual branch selection is `_RULES`+`IntentTag` (ADR-0018, not a B6 member); ADR-0049 only cleans the subject lemma after a branch is chosen. See §7.

### 10. Evidence sources actually consulted

- Read ADR-0049 in full.
- Code read: `generate/intent.py:43–70` (`IntentTag`/`DialogueIntent`), `:260–320` (`_normalize_subject` + frozensets), `:343–460` (`classify_intent` call sites).
- Ran `tests/test_intent_subject_extraction.py` locally at `cbfc8ccb` — green.
- `chat/runtime.py:1997–2005` (`classify_intent_from_input` call site inside `_maybe_pack_grounded_surface`).
- ADR-0048, ADR-0050 (cross-read for consumer confirmation).

---

## ADR-0050 — Pack-Grounded Surface for Cold-Start COMPARISON

**Audit ID (if a numbering collision):** — | **Family (if phased):** — (sibling family with ADR-0048/0052)
**Zone / stack:** B6 — Pack-Grounded Cold-Start Surfaces & Intent (M3/M1) | **Tier:** B
**ADR status (as recorded in the file):** Accepted | **ADR date:** 2026-05-18
**Card author:** Claude (Tier B audit agent) | **`verified_at` SHA:** `cbfc8ccb`

---

### 1. Content summary

- **Decision made:** Add `pack_grounded_comparison_surface(a, b)` as a sibling branch of `_maybe_pack_grounded_surface`, engaging when intent is COMPARISON, the empty-vault gate fired, and both `subject`/`secondary_subject` are non-empty, distinct pack lemmas. Surface format: `"{a} (...) contrasts with {b} (...) — pack-grounded ({pack_id}). No session evidence yet."`
- **Alternatives explicitly rejected:** None named explicitly; the implicit alternative of leaving COMPARISON permanently out of ADR-0048's scope is rejected once the structural match ("two pack-known lemmas, no session evidence") was recognized.
- **Artifacts the ADR claims will exist:**
  - `chat/pack_grounding.py:pack_grounded_comparison_surface(lemma_a, lemma_b) -> str | None`
  - `chat/runtime.py:_maybe_pack_grounded_surface` gains a COMPARISON branch, checked before DEFINITION/RECALL
  - `tests/test_pack_grounded_comparison.py` (15 tests)

### 2. Implementation cross-reference

| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `pack_grounded_comparison_surface` | yes | `chat/pack_grounding.py:1038` | Present; gained a `register` kwarg since 2026-05-18, core contract (identical-lemma → `None`, cross-pack tag composition) intact |
| COMPARISON branch precedes DEFINITION/RECALL | yes | `chat/runtime.py:1899–1930` (COMPARISON) before `:2094–2114` (DEFINITION/RECALL) | Order confirmed |
| `tests/test_pack_grounded_comparison.py` | yes | `tests/test_pack_grounded_comparison.py` | Ran locally at verified SHA — all green |

**Build axis:** full.

### 3. Liveness / integration

- Reached unconditionally on the live serving path for English COMPARISON turns with an empty session vault — same call chain as ADR-0048 (`chat/runtime.py:2699`/`:3035`), no separate flag.
- **Sabotage test:** removing the COMPARISON branch reverts pack-known COMPARISON turns to a fallback chain. Current code shows the branch also falls through to `chat/partial_surface.py:partial_comparison_surface` before the universal disclosure (a later addition beyond ADR-0050's original scope) — so the present sabotage picture is `pack_grounded_comparison_surface` removed → falls to `partial_comparison_surface` → falls to disclosure. This confirms live wiring and shows the mechanism has been extended once more since ADR-0050 shipped.
- **Liveness axis:** live.

### 4. Design fidelity — pillars and axioms

| Pillar | Honors / Tension / Violates | Citation |
|---|---|---|
| I. Mechanical Sympathy | Honors | Traced from the actual failing eval case (`comparison_memory_recall_030`), not speculative. |
| II. Semantic Rigor | Honors | Explicit, tested semantics for identical-lemma defer and order-sensitivity (`compare(a,b) ≠ compare(b,a)`), cross-checked against `graph_planner.graph_from_intent`'s own `Relation.CONTRAST` directionality. |
| III. Third Door | Honors | Same "second grounding source, not zero" reframing as ADR-0048, applied to a second intent shape rather than re-derived. |

| Axiom | Honors / Tension / Violates | Citation |
|---|---|---|
| 1. Geometry-First | n/a | String composition over stored pack rows. |
| 2. Field-State | n/a | — |
| 3. Propagation-over-Mutation | n/a | — |
| 4. Dual-Correction | n/a | — |
| 5. Reconstruction-over-Storage | Tension | Same reasoning as ADR-0048 §4 — verbatim reconstruction from stored domains, but a lookup-and-format operator rather than a field/geometry one. |
| 6. Compilation-Last | n/a | — |
| 7. Reality-over-Inheritance | Honors | Same explicit non-fabrication checklist as ADR-0048, applied to the COMPARISON shape. |

### 5. Build fidelity — does the code match the decision?

Matches — the `pack_grounded_comparison_surface` contract (identical-lemma → `None`, ≤2 domains/side, cross-pack tag composition) and branch ordering (COMPARISON before DEFINITION/RECALL) are unchanged. One addition not described in the ADR: a `partial_comparison_surface` fallback now sits between the pack-comparison branch and the universal disclosure (`chat/runtime.py:1908–1917`) — a later, compatible extension from outside this zone, not a contradiction of ADR-0050's own contract.

**Build-fidelity axis:** matches (one downstream extension noted, non-contradictory — see §3).

### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs

- No Whitepaper/Yellowpaper contradiction found.
- Explicitly built as a sibling of ADR-0048. Confirmed in code that COMPARISON does **not** route through ADR-0049's `_normalize_subject` — `intent.subject`/`intent.secondary_subject` are read directly at `chat/runtime.py:1899–1900`, matching ADR-0050's own statement that COMPARISON "uses its own named-group regex, not the post-processor."
- **Continuity axis:** clean.

### 7. Necessity / generality

1. **Necessity:** Irreducible for the COMPARISON shape specifically — no other mechanism composes a two-lemma contrastive surface from pack data; §3's sabotage test confirms observable change on removal.
2. **Reducibility:** Does not reduce to an L0/L1 primitive (same placement rationale as ADR-0048 §7).
3. **Extensibility — this is the zone's central question, answered directly, not inferred:** ADR-0048 and ADR-0050 do **not** independently reimplement cold-start logic. They are two branches — verified at `chat/runtime.py:1899` (COMPARISON) and `:2094` (DEFINITION/RECALL) — of the single `_maybe_pack_grounded_surface` dispatcher, both built on the same underlying `chat/pack_resolver.py:resolve_lemma` pack-resolution primitive (`pack_grounded_comparison_surface` calls `resolve_lemma` twice, `chat/pack_grounding.py:~1075–1076`; `pack_grounded_surface` calls it once via `build_pack_surface_candidate`). The two composers are not *fully* unified, though: `pack_grounded_surface` builds a typed `PackSurfaceCandidate` intermediate (`chat/pack_surface_candidate.py`) in anticipation of a not-yet-landed `SurfaceSelector`, while `pack_grounded_comparison_surface` composes its output string directly, bypassing that candidate type. This gap is **already acknowledged in-code**, not a new audit discovery — the module docstring states: "Until the selector lands, `pack_grounded_surface()` builds and then renders the candidate inline."

**Necessity/generality axis:** reducible-to-`_maybe_pack_grounded_surface` + `resolve_lemma` (shared dispatcher and shared pack-resolution primitive) — confirmed shared mechanism, with one already-flagged (in-code) partial-consolidation gap: the comparison composer does not yet route through the same `PackSurfaceCandidate` intermediate as the single-lemma composer.

### 8. Fitness / value

Same `evals/cognition/` evidence as ADR-0048/0049 — the chained A/B shows +7.7pp `surface_groundedness` / +8.3pp `term_capture_rate`, specifically attributable to `comparison_memory_recall_030` lifting. Same staleness caveat: no re-run or `CLAIMS.md` pin since 2026-05-18.

**Fitness axis:** historical evidence found (chained cognition-split A/B); not independently re-verified at current SHA.

### 9. Findings raised

- **AA-B6-7** 🔵 Consolidate: `pack_grounded_surface` and `pack_grounded_comparison_surface` share `resolve_lemma` but not the `PackSurfaceCandidate` intermediate — an already-acknowledged (in the module's own docstring) partial consolidation gap, worth closing if/when the `SurfaceSelector` lands. See §7.
- **AA-B6-8** 🟢 Monitor: a `partial_comparison_surface` fallback (`chat/partial_surface.py`) now sits between ADR-0050's pack-comparison branch and the universal disclosure — a later extension from outside this zone; not a contradiction, but worth the audit lead tracing which ADR introduced it. See §5.

### 10. Evidence sources actually consulted

- Read ADR-0050 in full.
- Code read: `chat/pack_grounding.py:1038–1094`, `chat/runtime.py:1833–1930`, `:2094–2120`, `chat/pack_surface_candidate.py:1–40`, `chat/partial_surface.py:60–75`.
- Ran `tests/test_pack_grounded_comparison.py` locally at `cbfc8ccb` — green.
- `evals/cognition/results/*.json` (same set as ADR-0048/0049).
- ADR-0048, ADR-0049 (cross-read).

---

## Zone findings rollup

| ID | Severity | ADR | Claim |
|---|---|---|---|
| AA-B6-1 | 🟡 Repair | 0047 | `forward_graph_constraint` is wired/tested/CI-confirmed to have zero production effect while off, with no recorded closure criterion (ADR-0058, `flag_register.md` §3a). |
| AA-B6-2 | 🟢 Monitor | 0047 | "Wired into the chat hot path" is independently confirmed as a real, reachable, tested code fact, distinct from the flag's off-by-default production reality. |
| AA-B6-3 | 🔵 Consolidate | 0048 | ADR-0048/0050/0052 confirmed to share one dispatcher (`_maybe_pack_grounded_surface`) by explicit in-code citation — answers the zone's necessity/generality question: no duplicate parallel builds. |
| AA-B6-4 | 🟡 Repair | 0048 | `evals/cognition/` results are stale (2026-05-era, no `CLAIMS.md` pin); dev/holdout splits already missed the lane's own ≥0.80 contract when last measured. |
| AA-B6-5 | 🟢 Monitor | 0048 | ADR-0048's "CLAUDE.md Semantic Pack Discipline" citation points at a file now reduced to a stub; doctrine survives in `AGENTS.md`, citation is stale. |
| AA-B6-6 | 🟢 Monitor | 0049 | ADR-0049 is a lemma-cleaning post-processor, not the intent-routing mechanism itself; routing belongs to the pre-existing `_RULES`/`IntentTag` classifier (ADR-0018). |
| AA-B6-7 | 🔵 Consolidate | 0050 | `pack_grounded_surface`/`pack_grounded_comparison_surface` share `resolve_lemma` but not the `PackSurfaceCandidate` intermediate — an already in-code-acknowledged partial-consolidation gap. |
| AA-B6-8 | 🟢 Monitor | 0050 | A `partial_comparison_surface` fallback (origin ADR outside this zone) now sits inside the COMPARISON dispatch chain, undocumented by ADR-0050 itself. |

**Zone-level verdict summary:** all four ADRs are `full` build / their claimed artifacts are all present and their dedicated test suites (109 tests total) pass at `cbfc8ccb`. Liveness splits 3-live / 1-wired-but-unreached (ADR-0047's flag). No Whitepaper/Yellowpaper contradictions found in any of the four. The zone's central necessity/generality question — does COMPARISON (0050) reimplement DEFINITION/RECALL's (0048) cold-start logic — resolves cleanly in the code's own words: shared dispatcher, shared pack-resolution primitive, one small and already-acknowledged consolidation gap (the `PackSurfaceCandidate` intermediate). ADR-0049's role is narrower than its title implies (lemma cleaning, not routing) but is correctly built, live, and load-bearing for the DEFINITION/RECALL/CAUSE/VERIFICATION paths that consume it.
