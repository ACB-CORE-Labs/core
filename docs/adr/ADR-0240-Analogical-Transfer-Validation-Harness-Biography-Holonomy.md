# ADR-0240: Analogical Transfer Validation Harness + Biography Holonomy Blade

**Status**: Proposed (acceptance path: tests green + Josh review)  
**Date**: 2026-07-11  
**Deciders**: Joshua Shay + multi-model R&D  
**Traceability**: Issue #13, parent #10  
**Related**: ADR-0238, ADR-0239, inter-session memory (0055), contemplation (0056), ADR-0151 proposal corridor  
**Canonical path**: `docs/adr/`

## Context

We now have GoldTether (autonomy modulation) and the Procrustes+Surprise dual (analogical transfer + boundary sensing).  

We still lack:

1. A rigorous, replayable **validation harness** that proves a transfer actually raised epistemic level and did not overfit or fabricate.
2. A first-class geometric object that records the lifelong holonomy of the identity motor (the Biography Holonomy Blade). This is the "single forever-lived life" made concrete.

Without these two, the system cannot safely grow wisdom or ever phase out HITL.

## Decision

### 1. Analogical Transfer Validation Harness

A sealed, deterministic harness that:

- Takes a solved problem (source multivector + proof trace) and a novel target domain.
- Runs the dual operator (ADR-0239).
- Measures residual, epistemic elevation posture, and GoldTether residual before/after.
- Only accepts the transfer if:
  - residual < ε
  - dual-correction passes
  - GoldTether residual does not increase (when monitor supplied)
- Records accepted transfer metadata for teaching-chain / biography update (proposal path).

**Location**: `evals/analogical_transfer/harness.py`

### 2. Biography Holonomy Blade

A grade-appropriate multivector that records the cumulative holonomy of the identity motor across the entire lived trajectory.  

It is updated only on successful, validated, dual-corrected experiences. It is the geometric embodiment of "I have lived this life and these are the transformations I have undergone."

It is the substrate that later self-authorship miners will read.

**Location**: `core/physics/biography.py` — reconstructible via `holonomy_encode` (reconstruction-over-storage; no raw experience dump). Vault field wiring remains one-mutation-path / proposal-gated.

### 3. Temporal Admissibility Gate + Self-Authorship Miner (scaffold)

- Temporal gate: typed `ADMIT` / `NOT_YET` / `REFUSE` (wisdom as geometry).
- Self-authorship miner: emits **SPECULATIVE** proposals only with drift residual + closure proof; never writes vault COHERENT.

## Consequences

- CORE now has a complete closed loop for lifelong learning: experience → dual operator → validation → GoldTether update → biography holonomy update.
- HITL phase-out becomes a measurable geometric condition (high biography coherence + low residual + high floor + `may_relax_hitl()`).
- Full audit trail of every wisdom gain.

## Implementation Notes

- Harness: `evals/analogical_transfer/`
- Biography: `core/physics/biography.py`
- Temporal: `core/physics/temporal_gate.py`
- Miner: `core/physics/self_authorship.py`
- All durable mutations go through the one-mutation-path.

## Validation

- End-to-end lifelong coherence curve test (GoldTether history + telemetry).
- Transfer fixture with residual below threshold (wrong=0).
- Biography blade remains closed under reverse product after every update.
- Miner proposals all SPECULATIVE; deterministic ordering.
