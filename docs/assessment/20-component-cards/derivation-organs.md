# derivation-organs — `generate/derivation/`

**Kind:** component group · **Parent:** M3 (gsm8k-math zone) · **Assessor:** Fable 5 (Phase 3)
**Verified at:** `8927c563` (2026-07-27)
**Liveness:** `live-internal` (math lanes; not on the chat serving path) · **Fitness:** `superseded-in-place` (by ADR-0252 ruling) · **Topology role:** runtime boundary (math reader)

> The "novice surface piles" of ADR-0252's diagnosis: per-shape derivation organs that turn recognized problem statements into typed solver state. Ruled superseded by the structure-mapping paradigm — and ruled to keep serving until a proven replacement exists.

## The 34-vs-18 discrepancy — RESOLVED (basis mismatch, not paydown)

Phase 2 flagged that ADR-0252's "34 bespoke surface organs" did not reproduce (18 found). Verified against the tree **at the ratification commit itself** (`1ccef491`):

| Measure | At ratification | Now (`8927c563`) |
|---|---|---|
| `def resolve_promotable_*` entry organs | **18** | **18** |
| `generate/derivation/` tree entries | 33 | 32 (`.py` files) |

The count was 18 entry organs *on the day ADR-0252 was ratified*. So "34" never counted `resolve_promotable_*` functions — its plausible basis is the module count (~32–33: the 18 entry organs plus support modules — `accumulate`, `clauses`, `comparatives`, `compose`, `extract`, `verify`, `calendar_grounding`, …), or an earlier-generation organ inventory. Two consequences:

1. **No consolidation has occurred since ratification** (18 → 18; one module removed). The debt is *not* being paid down — Phase 2's alternative hypothesis is eliminated.
2. **The governing ADR's central quantitative claim is unreproducible as stated.** The diagnosis stands regardless of whether the pile is 18 or 34 — but a ratified document whose headline number has no stated basis is exactly the documentation-debt class Finding F-4 tracks. The fix is one sentence in an ADR-0252 amendment stating the basis.

## What it is / What it does

32 modules, 6,765 lines. Each entry organ (`resolve_promotable_affine_fraction_delta`, `…goal_residual`, `…temporal_tariff`, etc.) recognizes one problem *shape* and publishes pre-composed candidates that the registry gates; support modules provide clause extraction, comparatives, composition, and verification. Governed by ADR-0251's standing prohibition: **no new bespoke per-case regex work** — new shape coverage that does not generalize is refused as debt (ADR-0252 §4: generalization ratio > 1 or it is a surface pile).

## Contract & evidence

- Misparse rate must be zero on the adversarial suite (refusal may be arbitrarily high — the safe failure mode) — contract: `runtime_contracts.md` §Adversarial suite; the `subtle_in_grammar` family (4 cases, all correct) proves the gate is not satisfied by refusing everything.
- GSM8K lane shape `wrong == 0` with outcome-accounting completeness — pinned lane `math_teaching_corpus_v1` in `CLAIMS.md`; `math` suite exists.
- Serving isolation: these organs feed math lanes; the chat serving path does not import them (deduction and curriculum serve through `proof_chain`/`curriculum_surface`, verified in Phase 2).

## Judgment

**Fitness: `superseded-in-place`** — the ruling is explicit and this card does not relitigate it. The schema's liveness ⊥ fitness separation exists for exactly this state.

**Honest wrinkles:** the replacement is gated on the ADR-0252 §5 SME experiment, which has never returned a verdict — so "superseded" currently has no successor timeline at all; the organs are condemned and load-bearing indefinitely. GSM8K's demotion to diagnostic makes this pile low-urgency, which is presumably why the experiment stalled — but the *paradigm* the experiment validates governs all future comprehension, not just math. The stakes are mispriced by the demotion.

**Open questions:** amend ADR-0252 with the organ-count basis (→ ruling, one sentence); run §5 (→ ruling; the assessment's top open item).
