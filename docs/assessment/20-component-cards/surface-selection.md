# surface-selection — the arms and the resolver

**Kind:** component (mechanism spanning `chat/runtime.py` + `core/cognition/surface_resolution.py`) · **Parent:** M4 · **Assessor:** Fable 5 (Phase 3)
**Re-verified:** `39331dbc` (2026-07-28) — see the arc note below.
**Verified at:** `8927c563` (2026-07-27)
**Liveness:** `live-serving` · **Fitness:** `strained` — refined from Phase 2 · **Topology role:** runtime boundary


**Arc note — 2026-07-28 (`39331dbc`).** H-13: the speculative-marker cache over-evicted. A COHERENT proposal released index tokens it never claimed, stripping the marker from an unrelated proposal still awaiting review — unreviewed material served without its disclosure prefix. Now claimant-tracked; a token dies only when the subject that claimed it is reviewed.

> The mechanism that decides which of several candidate surfaces the user actually reads. Every truth property CORE claims converges here.

## Correction/refinement to the Phase 2 M4 card

Phase 2 recorded "no single place states the precedence order as an executable rule." **Partially wrong.** `core/cognition/surface_resolution.py` (494 lines) *is* a declared-precedence resolver — `resolve_surface` plus `_base_runtime_surface` ("select the runtime-owned base surface by declared precedence": served `response_surface` always wins; then `pre_decoration_surface`; then `canonical_surface`), `_truth_path_base` (canonical-first, the register-invariant identity folded into `trace_hash` — deliberately the *reverse* preference of the served base, each serving its own invariant), `_abstention_resolution`, `_grounded_open_hedge_resolution` (with an explicit admissibility predicate), and `_substrate_supreme`. The historical note in its docstring says why it exists: "historically these mutated one string in evaluation order."

**What remains true:** the resolver governs the *pipeline seam* (base/truth-path/abstention/hedge/fold axes). The **composer arms** upstream in `ChatRuntime.respond` are still ordered branches, verified at their call sites:

| Arm | Site | Gate |
|---|---|---|
| deduction_grounded_surface | `chat/runtime.py:1834` | `deduction_serving_enabled` (**ON**, ratified) |
| curriculum_grounded_surface | `:1850` | `curriculum_serving_enabled` (OFF) |
| pack_grounded_comparison | `:1871` | pack-grounding conditions |
| narrative_grounded_surface | `:1898` | — |
| example_grounded_surface | `:1915` | — |
| pack relation-confirmation | `:1936` | — |
| determination override (Step B-2) | `_surface_determination` → `:1303` | `accrue_realized_knowledge` (OFF) |
| disclosed estimate (Step E) | `_surface_estimate` → `:1312–1340` | `estimation_enabled` (OFF) + earned SERVE license |
| unknown-domain gate stub | `:188` `_UNKNOWN_DOMAIN_SURFACE` | gate fires |
| grounded-open hedge (ADR-0254) | via resolver admissibility | — |
| register decoration (ADR-0071/0077) | post-selection | never moves `trace_hash` |
| logos-morph override | pipeline `:526` | answer-authority seam |

So the true architecture is **two strata**: ordered composer branches choose the *candidate*; the declared-precedence resolver reconciles *runtime vs pipeline vs abstention vs hedge*. The Phase 2 Third-Door candidate refines to: **extend the resolver's declared-precedence pattern upstream to the composer stratum**, rather than "create a resolver" — half the work is already done and proves the pattern fits this codebase.

## Contract & evidence

- Served-bytes-wins and its rationale are documented *with the falsifiable contract that catches regression*: preferring canonical would strip the register axis while `trace_hash` stays green — "the register-tour claims are the falsifiable contract that catches it" (`surface_resolution.py:113–116`). This is the sabotage test applied prospectively, in-code — worth naming as a model.
- Estimate arm: `govern_response` returns STRICT for an unlicensed class → surface unchanged; `shape_surface` guarantees the `[approximate]` prefix because a converse guess is `UNVERIFIED_POSSIBLE`, never in APPROXIMATE's admissible set — "a wrong estimate is always a DISCLOSED wrong" (`:1312–1340`).
- Selection-not-rewrite: determination and gate arms `replace(response, surface=…)`, retaining articulation/walk surfaces as evidence.

## Judgment

**Fitness: `strained`** — but more tractably than Phase 2 suggested. The resolver stratum is well-designed and self-documenting; the composer stratum is where arms accrete. With only deduction ON today, the *live* branch complexity is modest; the strain is prospective (each new capability adds an arm ahead of any declared order).

**Honest wrinkles:** the composer arms and the resolver are in different packages with different owners (`chat/` vs `core/cognition/`), so nothing structurally prevents a new arm from bypassing the resolver's disciplines. The M4 empty-string refusal wrinkle (typed refusal discarded at the public `str` boundary) sits in this same mechanism and remains the sharpest single dishonesty on the serving path — not because anything lies, but because the truth that exists goes unserved.

**Open questions:** declarative composer-arm precedence (→ Phase 4 Third-Door, refined); materialise `refusal_reason` (→ ruling, plumbing already landed).
