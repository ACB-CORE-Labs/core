# ADR index, keyed by domain

`docs/adr/` holds 312 files under a flat, purely sequential numbering. Sequence
records *when* a decision was made and nothing about *what it governs*, so
answering "which ADRs constrain the serving flag contract?" or "what governs
the register axis?" currently means grepping. Past ~300 files that is how a
decision corpus becomes a write-only archive.

This index is the lightweight fix: a maintained table keyed by capability
domain and cross-referenced by the files each ADR actually governs. It is **not**
a renumbering, and it does not replace `README.md` (which owns the
Master-Blueprint collision reconciliation and the binding non-ADR notes).

## Scope, stated honestly

This index covers the **live serving, telemetry, and governance surfaces** — the
domains a Phase 5 / next-arc session needs to query. It is not a complete index
of all 312 ADRs, and it does not pretend to be: an index asserting coverage it
does not have is worse than none, because it converts "I should grep" into "I
already checked."

**Maintenance rule: index on mint.** Adding a row when you write an ADR is
cheap; back-filling 300 is not. Rows below carry the files each ADR governs so
a reader can jump from a decision to its enforcement site.

---

## Deduction serving (the deduction-serve arc)

| ADR | Decision | Governs |
|---|---|---|
| [0256](./ADR-0256-deduction-serve-earned-license.md) | Deduction serving governed by an **earned** reliability license; flag ratified ON 2026-07-24 | `chat/deduction_serve_license.py`, `chat/data/deduction_serve_ledger.json`, `core/config.py::deduction_serving_enabled` |
| [0257](./ADR-0257-english-clause-argument-band.md) | Band v2-EN — English-clause opaque-atom propositional serving; realizer-guard exemption for quoted templates | `generate/proof_chain/english.py`, `chat/runtime.py` (guard exemption sites) |
| [0258](./ADR-0258-member-chain-band.md) | Band v3-MEM — singular membership + universal premises | `generate/proof_chain/categorical.py` |
| [0259](./ADR-0259-conditional-membership-fusion-band.md) | Band v4-CM — conditional-membership fusion | `generate/proof_chain/cond_member.py` |
| [0260](./ADR-0260-verb-predicate-band.md) | Band v5-VP — verb-predicate arguments | `generate/proof_chain/verb.py` |
| [0261](./ADR-0261-existential-witness-band.md) | Band v6-EX — existential witnesses; anonymous witness never transfers to a named individual | `generate/proof_chain/exist.py` |

Engine underneath all six: `generate/proof_chain/entail.py` (ROBDD tautology
check). Surfaces: `generate/proof_chain/render.py`, `chat/deduction_surface.py`.

## Curriculum serving

| ADR | Decision | Governs |
|---|---|---|
| [0262](./ADR-0262-curriculum-grounded-serving.md) | Exams answered from the ratified curriculum, read OPEN-world; §5 records that curriculum **volume** is the binding constraint (~25× gap) | `chat/curriculum_surface.py`, `chat/curriculum_serve_license.py`, `evals/curriculum_serve/runner.py` |

## Reliability licensing and the ledger bridge

| ADR | Decision | Governs |
|---|---|---|
| [0175](./ADR-0175-calibrated-attempt-and-eliminate-learning.md) | Two regimes under wrong=0; θ_SERVE Wilson floor; an engine cannot raise its own bar | `core/reliability_gate.py`, `generate/determine/estimation_license.py` |
| [0263](./ADR-0263-ratified-ledger-bridge.md) | Seal → ratify → SHA-verify → serve-gate, extracted from three instances. **Rule 5** (2026-07-25): absence policy is declared in `CAPABILITY_LEDGERS`, not passed at the call site | `core/ratified_ledger.py`, all three license adapters |
| [0206](./ADR-0206-response-governance-bridge.md) | Response governance bridge (`govern_response` / `shape_surface`) | `generate/determine/` |

## Grounding sources and the epistemic taxonomy

| ADR | Decision | Governs |
|---|---|---|
| [0142](./ADR-0142-epistemic-state-taxonomy.md) | Epistemic state as first-class vocabulary | `core/epistemic_state.py` |
| [0048](./ADR-0048-pack-grounded-surface.md) / [0050](./ADR-0050-pack-grounded-comparison.md) | Pack-grounded cold-start DEFINITION / RECALL / COMPARISON | `chat/pack_grounding.py` |
| [0052](./ADR-0052-teaching-grounded-surface.md) | Teaching-grounded cold-start CAUSE / VERIFICATION | `chat/teaching_grounding.py` |
| [0064](./ADR-0064-cross-pack-teaching-chains.md) | Cross-pack residency + cross-corpus chain lookup for the discovery gate | `teaching/discovery.py` |

The closed set itself lives at `core/epistemic_state.py::GroundingSource`.
Registration is a three-part cross-stack change — see
`docs/specs/runtime_contracts.md` § "Grounding-source registration".

## Register axis and the realizer guard

| ADR | Decision | Governs |
|---|---|---|
| [0069](./ADR-0069-realizer-register-parameter.md) | Realizer register parameter; **invariant C** — register must not move `trace_hash` | `core/cognition/surface_resolution.py`, `core/cognition/pipeline.py` |
| [0071](./ADR-0071-seeded-surface-variation.md) | Seeded surface variation + discourse markers; `pre_decoration_surface` | `chat/register_variation.py` |
| [0075](./ADR-0075-realizer-slot-type-guard.md) | Realizer slot-type guard (C1 coherence floor). Deduction surfaces are **exempt** — quoted templates are not slot-composed articulations (rationale documented at both guard sites) | `chat/runtime.py` (stub + main guard sites) |
| [0077](./ADR-0077-substantive-register-knobs.md) | Substantive register knobs (R6); `register_canonical_surface` | `chat/register_substantive.py` |

## Telemetry, trace, and audit

| ADR | Decision | Governs |
|---|---|---|
| [0039](./ADR-0039-audit-completeness.md) | `TurnVerdicts` bundle, stub-path `TurnEvent`, `hedge_injected` | `chat/runtime.py` |
| [0153](./ADR-0153-turn-event-trace-hash-backstamp.md) | `TurnEvent` `trace_hash` back-stamp (W-020a) | `core/cognition/pipeline.py`, `chat/runtime.py` |
| [0255](./ADR-0255-discovery-yield-baseline-telemetry.md) | Discovery-yield-per-served-turn baseline; fail-closed on a missing baseline | `teaching/discovery_yield.py` |
| [0018](./ADR-0018-tool-use-scope.md) | Typed deterministic operators folded into `trace_hash` | `core/cognition/trace.py` |

`trace_hash` is **not** reconstructable from `TurnEvent` — see
`docs/specs/runtime_contracts.md`. Audit-ledger **R7** (telemetry sink receives
the pre-override event) is open and recorded there.

## Workbench and the cross-stack UI contract

| ADR | Decision | Governs |
|---|---|---|
| [0160](./ADR-0160-core-workbench-v1.md) | Operator/auditor UI before public chat | `workbench/` |
| [0161](./ADR-0161-hitl-async-queue.md) | HITL async queue | `teaching/proposals.py`, `core proposal-queue` CLI |
| [0162](./ADR-0162-workbench-design-system.md) | Design system v1; **§3d** — engine enums bind to UI badges, enforced by a build-time coverage test | `workbench-ui/src/design/`, `workbench-ui/enum-snapshot.json` |

## Teaching, proposals, and review

| ADR | Decision | Governs |
|---|---|---|
| [0057](./ADR-0057-teaching-chain-proposal-review.md) | Teaching-chain proposal + review + replay-equivalence gate | `teaching/proposals.py`, `teaching/review.py`, `teaching/store.py` |
| [0254](./ADR-0254-grounded-open-hedge-arm.md) | Grounded-open hedge arm for the shadow-coherence gate | `chat/runtime.py` |

## Reader arc / math capability

| ADR | Decision | Governs |
|---|---|---|
| [0251](./ADR-0251-reader-arc-recalibration-geometric-normalization-spike-proposal.md) | **Halt bespoke per-case regex work**; clean-base reset. The prohibition that governs every math reader increment | `generate/math_roundtrip.py`, `generate/math_candidate_parser.py` |

Companion evidence: `docs/research/reader-arc-overfit-inventory-2026-07-19.md`,
`docs/research/math-reader-phase-4-1-status-2026-07-24.md` (Phase 4.1 =
complete-with-null-yield).

## Substrate, field, and packs

| ADR | Decision | Governs |
|---|---|---|
| [0180](./ADR-0180-crdt-sharded-vault-concurrency.md) | Delta-CRDT sharded substrate | `core-rs/src/vault.rs`, `engine_state/` |
| [0243](./ADR-0243-wave-field-cognitive-lifecycle-comprehension-reasoning-and-resonant-learning.md) | Wave-field cognitive lifecycle | `field/` |
| [0244](./ADR-0244-wave-field-identity-manifold-and-inalienable-geometric-alignment.md) | Wave-field identity manifold | `persona/`, `chat/runtime.py` |
| [0253](./ADR-0253-master-blueprint-adr-collision-and-dual-pack-boundary.md) | Blueprint collision resolution + dual-pack serve boundary (INV-33) | `packs/` |

---

## Numbering note

The corpus is at ADR-0263 and minted eight ADRs in roughly 48 hours during the
generalization arc. Sequential numbering is fine and should stay — the cost it
imposes is discoverability, which is what this file pays down. ADR-0300 is a
near-term milestone with no structural meaning; do not treat it as one.

The ADR-0206/ADR-0256 numbering collision that had to be resolved in doc form
is the concrete failure this index is meant to make less likely: a domain-keyed
view shows an in-flight number before it is minted twice.
