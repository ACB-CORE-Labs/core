# CORE Mind-Physics Blueprint

**Version:** 0.1.0  
**Date:** 2026-05-12  
**Status:** Draft — **stale since 2026-05-12; not under active development**

> **Staleness banner — 2026-07-27 (holistic assessment Phase 6).** This blueprint has not moved since its authoring date and was one of CORE's five unreconciled macro articulations of its own cognitive cycle. Those five were dissolved into the two-axis taxonomy in `docs/assessment/02-layer-taxonomy.md` (decision D1) — read that first for the current structural account. What this document uniquely contributed, the allocation/attention physics layer (ADR-0008), was verified **live** in Phase 2 (`generate/stream.py:255-263`, `use_salience` defaults `True`) and is ungoverned rather than absent; it is registered as G-14 awaiting a one-page ADR. Nothing here is authoritative; it is kept for its intent.

---

## The Three Physics Layers

CORE's cognitive cycle is governed by three physics layers that compose in sequence:

```
FieldState (populated by ingest layer, ADR-0007)
       │
       ▼
┌─────────────────────────────┐
│   ALLOCATION PHYSICS        │  ADR-0008
│   SalienceOperator          │  curvature → SalienceMap
│   AttentionOperator         │  SalienceMap + Budget → AttentionPlan
│   InhibitionOperator        │  AttentionPlan + FieldState → InhibitionMask
└─────────────┬───────────────┘
              │  foregrounded field regions
              ▼
┌─────────────────────────────┐
│   COMPOSITIONAL PHYSICS     │  ADR-0009
│   BindingOperator           │  co-activation → BindingFrame
│   DigestOperator            │  BindingFrame → FieldState (updated)
│   TrajectoryOperator        │  [BindingFrame] → ReasoningTrajectory
│   ArticulationPlanner       │  Trajectory + Modality → ArticulationPlan
└─────────────┬───────────────┘
              │  structured output plan
              ▼
┌─────────────────────────────┐
│   IDENTITY PHYSICS          │  ADR-0010
│   IdentityCheck             │  Trajectory × IdentityManifold → IdentityScore
│   DriveGradientMap          │  persistent gradient bias on FieldState
│   ExertionMeter             │  cumulative cost → FatigueIndex
└─────────────┬───────────────┘
              │  validated, identity-consistent ArticulationPlan
              ▼
         RENDERER
         (modality-specific surface realization)
```

---

## Data Flow Summary

| Layer | Input | Output | ADR |
|---|---|---|---|
| Ingest | raw source (any modality) | `CandidateGeometricPressure` → `FieldState` | ADR-0007 |
| Allocation | `FieldState` | `AttentionPlan`, `InhibitionMask` | ADR-0008 |
| Compositional | `AttentionPlan`, `FieldState` | `ReasoningTrajectory`, `ArticulationPlan` | ADR-0009 |
| Identity | `ReasoningTrajectory`, `ArticulationPlan` | `IdentityScore`, validated plan | ADR-0010 |
| Renderer | `ArticulationPlan` | surface output (text, code, data) | TBD |

---

## Next Steps

- [ ] Rust acceleration targets: curvature kernel, coherence wave, trajectory delta
- [ ] `IdentityManifold` bootstrapping protocol (architect-level, deliberate)
- [ ] Renderer interface definition (ADR-0011, planned)
- [ ] Integration tests across the full ingest → allocation → compositional → identity cycle
