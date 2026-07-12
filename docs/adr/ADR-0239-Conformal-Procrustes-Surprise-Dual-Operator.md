# ADR-0239: Conformal Procrustes / Analogical Versor Search + Surprise Residual Dual

**Status**: Proposed (acceptance path: tests green + Josh review)  
**Date**: 2026-07-11  
**Deciders**: Joshua Shay + multi-model R&D  
**Traceability**: Issue #12, parent #10  
**Related**: ADR-0238, dynamic_manifold, surprise residual, Cartan-Iwasawa, ADR-0013, ADR-0209  
**Canonical path**: `docs/adr/`

## Context

Generalized intelligence requires the ability to transfer solutions across domains by structural analogy, not surface similarity. Statistical embedding nearest-neighbors are forbidden (they violate reconstruction-over-storage and introduce non-determinism).  

We need a pure geometric operator that:

1. Finds the best versor \( V \) that maps a solved problem multivector set \( P \) onto a novel problem set \( Q \) (Conformal Procrustes).
2. Simultaneously surfaces the residual that cannot be explained by any admissible versor (Surprise Residual) so the system can detect its own knowledge boundary and propose new blades.

These two operators are dual: Procrustes seeks the best explanation; Surprise quantifies the unexplained and seeds new discovery.

## Decision

1. **Signature-Aware Conformal PCA**  
   Metric-preserving principal axes on Cl(4,1) with signature `(+,+,+,+,-)`.  
   **Genuine null vectors are CLASSIFIED and retained** — never silently skipped (Terra + Grok mastery fix).

2. **Conformal Procrustes**  
   Solve \( \min_V \sum_i \| V \cdot p_i \cdot \widetilde{V} - q_i \|_F \) subject to \( V \) being a versor (or motor) in Cl(4,1).  
   Implementation uses signature-aware structure + Cartan-Iwasawa factorization so that the search stays on the versor manifold.

3. **Cartan-Iwasawa extraction**  
   Factor a conformal versor into Rotor · Translator · Dilator (BCH-free constructive path). Public API: `cartan_iwasawa_extract`.

4. **Surprise Residual Operator**  
   \( S(x) = x - \mathrm{proj}_{B_{\text{union}}}(x) \) where \( B_{\text{union}} \) is the current admissible blade span (Minkowski-aware when operating on conformal 5-vectors).  
   Residual grade and magnitude become the geometric curiosity signal and the seed for new DiscoveryCandidates in the contemplation loop.

5. **Dual Operator**  
   `dual_procrustes_surprise(P, Q, current_basis)` always runs both. A successful Procrustes transfer that leaves residual below ε is eligible for teaching-chain / biography holonomy update (ADR-0240). Residual above threshold becomes a first-class contemplation object.

### Residual namespace discipline

`procrustes_residual` and surprise residual are **not** ADR-0006 energy residual and **not** ADR-0238 GoldTether residual. Distinct names; distinct tests.

## Consequences

- CORE gains true analogical transfer without any statistical memory.
- The system can now "see its own boundaries" as geometric residual.
- Direct feed into ADR-0240 (validation harness + biography holonomy).
- All operators remain pure, deterministic, dual-corrected.

## Implementation

- `core/physics/dynamic_manifold.py` — signature_aware_pca + conformal_procrustes + cartan_iwasawa_extract
- `core/physics/surprise.py` — surprise_residual + dual_procrustes_surprise

Wired to live `algebra/*` (no scipy, no placeholder identity motors as the only path).

## Validation

- Exact residual measurement on known solvable pairs (structural transfer).
- Null residual only when the target is in the versor orbit of the source.
- Null axes appear in PCA classification counts when present.
- Replay identity of the entire dual operator.
