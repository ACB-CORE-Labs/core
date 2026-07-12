# ADR-0238: GoldTether-Modulated Supervised Autonomy

**Status**: Proposed (acceptance path: tests green + Josh review)  
**Date**: 2026-07-11  
**Deciders**: Joshua Shay (CORE lead) + multi-model R&D chain  
**Traceability**: Issue #11, parent Issue #10  
**Related**: ADR-0055 (inter-session memory), ADR-0056 (contemplation C1), ADR-0080, GoldTether physics, Practice/Serve boundary, ADR-0199 (Arena GoldTether — distinct contract)  
**Canonical path**: `docs/adr/` (redirect stub under `docs/decisions/`)

## Context

CORE must grow a forever-lived intelligence through experiences while remaining under hard safety control. The current HITL gate is correct but static. We need a continuous, geometry-native modulator that:

1. Measures coherence residual of the lived trajectory (GoldTether).
2. Dynamically raises or lowers the autonomy floor (pseudoscalar floor).
3. Only allows progressive reduction of HITL once the system has proven, through articulate reason + contemplation + successful epistemic elevation, that it can self-review safely.
4. Never permits unsupervised mutation of identity, admissibility regions, or safety invariants.

This is the controlled path from supervised to self-supervised to eventual self-authoring (the "grow out of the need for HITL" trajectory).

### Dual ontology (mastery refinement)

| Name | ADR | Contract |
|---|---|---|
| **Arena GoldTether** | ADR-0199 | independent truth for practice scoring (`is_correct` / `gold_answer`) |
| **Coherence GoldTether** | **this ADR** | field residual + dynamic floor + `supervised_autonomy_level` |

Shared metaphor; different modules. Never shadow `core.learning_arena.protocols.GoldTether`.

## Decision

Introduce a first-class **GoldTetherMonitor** that:

- Continuously computes the coherence residual \( R_{\text{GoldTether}}(t) = \| F(t) \cdot \widetilde{F}(t) - 1 \|_F \) (and higher-grade projections). Implemented as `algebra.versor.versor_unit_residual` dual-checked with `reverse(F)`.
- Maintains a **dynamic pseudoscalar floor** that rises only on proven epistemic elevation (successful contemplation + dual-corrected claim that reaches VERIFIED).
- Exposes a `supervised_autonomy_level ∈ [0.0, 1.0]` that gates B1 / R0 / R1 sequencing and the practice-vs-serve boundary.
- Implements a hard decay schedule and a fail-closed reset if residual ever exceeds ε_drift.
- Exposes `may_relax_hitl()` — hard gate; HITL override can never be disabled by the monitor itself.
- Exposes `force_reset()` for emergency fail-closed (HITL / safety pack only).

The monitor is pure geometry, replay-deterministic, and dual-corrected. It never samples, never uses learned weights for the gate itself.

### Named configuration

`epsilon_drift`, `max_history`, floor step / decay step (documented in module), optional practice/serve envelope helpers.

### Supervised blend (dual-correction geodesic)

When a blended field state is required:

```text
R = word_transition_rotor(source, target)
out = rotor_power(R, α) * source     # Spin left-composition
assert versor_condition(out) < 1e-6
```

Sandwich conjugation is not the state geodesic (maps identity→identity). Left composition lands α=0→source, α=1→target.

## Consequences

### Positive
- Single forever-lived trajectory can now safely accumulate wisdom.
- HITL phase-out becomes measurable and gated by geometry, not calendar or vibes.
- Full auditability of every autonomy increase.
- Compatible with existing vault/CRDT, contemplation loop, and risk-reward physics.

### Negative / Risks
- Incorrect floor calculation could stall progress or (worse) over-grant autonomy. Mitigated by dual-correction + explicit residual tests + HITL override that can never be disabled by the monitor itself.
- Additional telemetry surface. Mitigated by making the channel first-class (`telemetry()` schema `goldtether_coherence_v1`).

### Neutral
- New module `core/physics/goldtether.py`.
- New ADR chain dependency for any future self-authorship work (ADR-0240).

## Implementation Notes

See `core/physics/goldtether.py` for the exact operator suite.
All public methods must enforce algebraic closure before returning.
The monitor is the single source of truth for "how much HITL can be relaxed right now".

## Validation

- Property tests: residual is always ≥ 0 and dual-corrected under reverse.
- Replay tests: identical field sequences produce identical autonomy levels.
- Lifelong curve: epistemic elevation events correctly raise the floor; residual breach forces fail-closed.
- Never allows autonomy > 0 while residual > ε_drift.
- `may_relax_hitl()` false until floor and autonomy thresholds met.
