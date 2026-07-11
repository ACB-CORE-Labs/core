# ADR-0237: GeometricDelta ABI and Boundary Verification

- Status: Draft
- Date: 2026-07-11
- Owners: CORE Labs / Sopher R&D
- Related:
  - ADR-0021-epistemic-grade-policy.md (CORE Truth-Seeking)
  - ADR-0029-safety-packs.md (CORE Safety Packs)
  - ADR-0025-rotor-frame-admissibility-design-note.md (CORE)
  - ADR-0025-hard-closure-and-master-substrate.md (Sopher)
  - ADR-0025.1-hard-closure-implementation-findings.md (Sopher)
  - BI-HEMISPHERE-CHARTER.md

## 1. Context

In cognitive systems built on Conformal Geometric Algebra Cl(4,1) fields (such as Sopher and the CORE engine), updates represent mutations or physical shifts in the underlying state. Previously, the interface for these updates was ad-hoc and defined locally within the client (e.g. Sopher's Callosum compiled tokens into multivectors directly).

This created two critical issues:
1. **Geometric Drift**: Naive updates could bypass hard Cl(4,1) closure verification, causing residuals to drift beyond numerical floors.
2. **Epistemic Entanglement**: Clients could invent alternative claim states or fail to pass proper provenance tags, violating the co-equal Truth-Seeking Schema.

To enforce physical and epistemic boundaries, we define `GeometricDelta` as the canonical, cross-CORE/Sopher ABI.

## 2. Decision

We will define `GeometricDelta` as a first-class, modality-agnostic type in CORE. Any compiler (like Sopher's Callosum, or future audio/vision compilers) must target this structure directly. 

### 2.1 ABI Struct definition

```python
@dataclass(frozen=True)
class GeometricDelta:
    id: str                      # content-addressed ID (hash)
    parents: Set[str]            # CRDT frontier IDs
    modality: str                # e.g., "lh_text", "sensor", "tool"
    compiler_id: str             # name+version of compiler
    semantic: Dict[str, Any]     # typed primitive (enum + payload)
    amr_scope: Dict[str, Any]    # resolution + region (time, space, mode indices)
    delta_versor: List[float]    # Cl(4,1) multivector (32 floats)
    inverse_ref: str | None      # optional ID of inverse/corrective delta
    provenance: Dict[str, Any]   # source, time, adr_refs, hash
    epistemic: EpistemicState    # CORE truth-seeking state (SPECULATIVE, etc.)
```

### 2.2 Boundary Invariants & Contracts

At the Right Hemisphere (RH) boundary, the `GeometricDelta` is subject to strict verification:

1. **Closure Verification**:
   - `delta_versor` must represent a valid Cl(4,1) versor.
   - It is verified against the guarded projector (scalar rescale + monotone Newton iterations) under tolerance $\epsilon$ (default $10^{-6}$).
2. **Reject-and-Retain**:
   - If verification fails or blows up, the delta is rejected at the boundary. 
   - The system preserves the last closed state and logs the failure to Meta-RH telemetry. Under no circumstances may the boundary silently "fix" semantics or accept a broken closure.
3. **Causal Convergence (CRDT)**:
   - Updates are linked via `parents` to construct a causal graph (event frontier). Merge conflicts are resolved on the event graph rather than state-level mutation.
4. **Epistemic Isolation**:
   - The `epistemic` state must inherit from CORE's `EpistemicState` enum.
   - By default, all incoming deltas are treated as `SPECULATIVE` until promoted by Vault coherence evidence.

### 2.3 Epistemic and Safety Adherence

All `GeometricDelta` instances are subject to the same truth-seeking and safety packs as any other CORE claim. No delta can bypass these by virtue of being geometric. Specifically:
- **epistemic** state validation rules defined in `ADR-0021` apply fully to all admitted deltas.
- **safety** pack constraints outlined in `ADR-0029` govern the allowable transformations represented by the `delta_versor`. If a delta represents an unsafe rotation/boost permutation, it must be rejected under the same refuse-to-emit mechanics.

## 3. Consequences

- **Client Refactoring**: Sopher's Callosum must import `GeometricDelta` from CORE and construct it as the sole admission path into Sopher's RH.
- **Unified Telemetry**: Boundary violations (residual drift, malformed metadata) will be dispatched to CORE's telemetry sinks and monitored by Meta-RH, avoiding duplicate telemetry layers in Sopher.
- **Multimodal Scaling**: Audio, vision, or motor controllers are now isolated from the cognitive loops. They simply target this same abstract ABI.
