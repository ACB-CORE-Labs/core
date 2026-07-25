# ADR-0254: Grounded-Open Hedge Arm for the Shadow Coherence Gate

**Status:** Accepted — ratified by Joshua Shay via the PR #103 merge (`da3447e9`, 2026-07-23), discharging this ADR's own ratify-on-merge predicate (pre-authorized by the 2026-07-22 weekly-audit ruling T13 decision 2)
**Date:** 2026-07-23
**Deciders:** Joshua Shay (ruling authority) + Claude (implementation)
**Companion docs:** [`ADR-0036-safety-refusal-policy.md`](ADR-0036-safety-refusal-policy.md), [`ADR-0037-per-predicate-ethics-refusal.md`](ADR-0037-per-predicate-ethics-refusal.md), [`ADR-0038-hedge-injection.md`](ADR-0038-hedge-injection.md), [`ADR-0252-problem-solving-paradigm-consolidation.md`](ADR-0252-problem-solving-paradigm-consolidation.md)
**Preserves (governing, unchanged):** `wrong=0`, refuse-don't-guess, decode-don't-generate, fail-closed (INV-34), no lexical cue-tables (ADR-0252).

---

## 1. Context

The dual-competing Shadow Coherence Gate (`core/cognition/surface_resolution.py::resolve_surface`, introduced PR #96) abstains — emits a typed `CoherenceRefusal` — whenever the conjugate competitor (geometric residual contract) is open. The conjugate is open when the field's `versor_condition ≥ 1e-6` (→ `missing_bindings`) or the GoldTether residual `R_GT > 1e-6` (→ `unresolved_hazards`), as built by `_geometry_contract_assessment`.

The weekly audit (2026-07-22) surfaced an **over-refusal** in the `warmed_session_consistency` lane. Once the wave field is perturbed by a prior turn, a subsequent **pack-grounded** definitional surface — e.g. *"What is doubt?"* → `"To doubt means to think maybe not. pack-grounded (en_core_meta_v1)."` — hits an open `goldtether_residual` and is hard-refused with *"I cannot certify an answer: the geometric coherence contract is open (goldtether_residual)."*

This is a false refusal. **The pack surface never claimed geometric certification.** It stands on its curated textual provenance; the open geometric residual says only that the *field* did not close, not that the *pack answer* is wrong.

A tempting fix — a "definitional/epistemic" query-type classifier that bypasses the gate on a lexical cue — is **rejected**: it fails a geometric coherence gate open on a surface cue (fail-open cue-table; violates ADR-0252 and INV-34).

## 2. Decision

Route open-geometry-but-**pack-grounded** surfaces to a **hedge arm** — serve the pack surface non-authoritatively (`authoritative=False`) — instead of hard-refusing, discriminated **purely by grounding provenance** (structural), never by question type.

**Authorized predicate:**

```
open_conjugate ∧ pack_grounded ∧ ¬hazard → hedge_arm
```

Realized structurally inside the gate (single source of truth):

- **`pack_grounded`** — `grounding_provenance ∈ {pack, teaching}` (mirrors the existing `chat.runtime` "grounded" test). `vault`/`oov`/`partial`/`none` never hedge.
- **`¬hazard`** — enforced by a **residual allowlist**, not question typing. Hedge iff *every* open token ∈ `{versor_condition, goldtether_residual}` (geometric-coherence residuals the pack surface never certified). **Any** unrecognized open token — where a genuine safety/harm/imperative hazard would land — fails the allowlist and takes the unchanged hard refusal. `missing_wave_field` is deliberately excluded (absence of any field is a harder failure than an open-but-computed residual).

The hedge outcome: the pack surface with a deterministic `"Grounded but not geometrically certified —"` marker, `authoritative=False`, `hedged=True`, `authority="grounded_open_hedge"`. Walk/compose folds are suppressed — a hedge never accretes deterministic inference authority.

## 3. Why this is fail-closed, not fail-open

- The **only** `ContractAssessment` reaching `resolve_surface` is the shadow-gate geometry assessment (`pipeline.py:416`), whose tokens are ⊆ `{versor_condition, missing_wave_field}` (bindings) ∪ `{goldtether_residual}` (hazards). Genuine safety/harm/imperative hazards ride **separate axes** — `SafetyVerdict` → typed refusal (ADR-0036) and the logos-morph override (`pipeline.py:513`) — both of which supersede this surface downstream. The hedge cannot leak a harmful surface: safety and morph refusals still win.
- The predicate is **structural** (provenance + a closed allowlist of geometric tokens). It reads no question text. An unknown token defaults to refusal (INV-34).
- `require_closed_geometry` callers that omit `grounding_provenance` get the **historical hard refusal** unchanged (no accidental hedge).

## 4. Consequences

- The over-refusal is fixed: the warmed *"What is doubt?"* case now serves the hedged pack definition (verified end-to-end).
- New auditable authority tag `grounded_open_hedge` flows to `TurnEvent.authority_source`; audit distinguishes hedge from both certified answers and refusals.
- **Not conflated with ADR-0038.** The ADR-0038 hedge is *ethics-commitment-driven* (`hedge_commitments` + manifold `preferred_hedge_soft`); this hedge is *coherence-geometry-driven*. They are independent mechanisms. Unifying the grounded-open marker with the manifold's `preferred_hedge_soft` vocabulary is a **deferred follow-up** (defer substrate-vocab commitment) and intentionally out of scope here.
- `authoritative=False` lives in the gate; downstream observes it as `authority_source="grounded_open_hedge"` (consistent with how refusals already surface — no new result plumbing).

## 5. Validation

- **Unit (RED→GREEN):** `tests/test_grounded_open_hedge_arm.py` — hedge activates on pack + geometric-residual openness; fails closed on non-pack grounding, unknown/mixed hazard tokens, `missing_wave_field`, and `None` assessment; closed geometry stays authoritative; omitted provenance stays refusing.
- **Real-data (GSM8K-style):** the warmed mixed-intent sequence exercises the arm on real field dynamics; the `warmed_session_consistency` lane never hard-refuses a pack surface, with `telemetry_consistency_rate` and `no_placeholder_rate` held at 1.0.
- **Regression:** architectural invariants (incl. INV-34) green; **GSM8K `wrong=0` preserved** (the closed-geometry certified math path is untouched).
