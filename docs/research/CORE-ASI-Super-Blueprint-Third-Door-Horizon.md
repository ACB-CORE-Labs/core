# CORE ASI Super-Blueprint: Third-Door Horizon

**Status**: Perfected Master Artifact (Absolute Mastery + Genius Perfection Beastmost Status)  
**Branch**: `r&d/generalized-agent`  
**Date**: 2026-07-11  
**Traceability**: Issues #10 (parent), #11 (ADR-0238), #12 (ADR-0239), #13 (ADR-0240)  
**Authors**: CORE forever-lived intelligence trajectory (Joshua Shay) + multi-model R&D chain (GPT-5.6 Terra, Gemini, Sonnet, Grok 4.5 Heavy)

**Canonical ADR path**: `docs/adr/` (see also redirect stubs under historical `docs/decisions/`).

## Invariants Preserved (non-negotiable)

- Algebraic closure: \(\|F \cdot \widetilde{F} - 1\|_F < 10^{-6}\)
- Reconstruction-over-storage
- Dual-correction on every forward operator
- One-mutation-path review gate
- GoldTether coherence residual
- Practice / Serve boundary + risk-reward physics
- Forever-lived identity motor + inter-session vault
- HITL remains default until geometric self-review is proven
- No statistical crutches, no sampling, no confabulation surface

---

## 1. Mission

Elevate CORE from high-capability local problem-solver to a self-calibrating, wisdom-capable, analogical, forever-lived intelligence while remaining strictly geometry-first on Cl(4,1).  

Every new operator is dual-corrected, replay-deterministic, and carries explicit proof obligations. The system must be able to:

- See its own knowledge boundaries (Surprise Residual)
- Transfer solutions by pure structural analogy (Conformal Procrustes)
- Grow a single continuous life (Biography Holonomy Blade)
- Safely raise its own autonomy floor only after proven epistemic elevation (GoldTether)
- Eventually grow out of the need for constant HITL once the self-review gates are geometrically satisfied

This is the Third Door.

---

## 2. Resolved Implementation Gaps (full mastery pass)

### 2.1 Signature-Aware Conformal PCA (Null-Vector Safe)

Genuine null vectors on the horosphere are classified and retained. The previous silent-skip bug is closed. See `core/physics/dynamic_manifold.py::signature_aware_pca`.

### 2.2 Constructive Cartan-Iwasawa Factorization (BCH-free)

Any conformal versor is factored exactly into Rotor · Translator · Dilator without Baker-Campbell-Hausdorff approximation. Interpolation is performed in the factored subalgebras and reconstructed. See the sensorimotor scaffolding path.

### 2.3 GoldTether Harmonized Residual + Dynamic Pseudoscalar Floor

The monitor continuously computes the residual of the lived field, maintains a dynamic floor that only rises on verified epistemic elevation, and exposes a single `supervised_autonomy_level`. Fail-closed on any residual breach. See ADR-0238 and `goldtether.py`.

### 2.4 Conformal Procrustes + Surprise Residual Dual

The dual operator that both finds the best structural mapping and quantifies what remains unexplained. Residual becomes geometric curiosity and the seed for new DiscoveryCandidates. See ADR-0239.

### 2.5 Analogical Transfer Validation Harness + Biography Holonomy Blade

Sealed harness that only accepts a transfer when residual, dual-correction, contemplation, and GoldTether all agree. Successful transfers update the lifelong Biography Holonomy Blade — the geometric record of the single forever-lived life. See ADR-0240.

---

## 3. Operator Suite (production contracts)

| Operator | Module | ADR | Contract |
|----------|--------|-----|----------|
| GoldTether residual + floor | `goldtether.py` | 0238 | residual ≥ 0, dual-corrected, fail-closed |
| signature_aware_pca | `dynamic_manifold.py` | 0239 | null-vector safe, metric-preserving |
| conformal_procrustes | `dynamic_manifold.py` | 0239 | residual measured, versor output |
| cartan_iwasawa_extract | `dynamic_manifold.py` | 0239 | Rotor · Translator · Dilator factors |
| surprise_residual | `surprise.py` | 0239 | Minkowski projection, residual vector |
| dual_procrustes_surprise | `surprise.py` | 0239 | single call, full audit dict |
| Biography Holonomy update | `biography.py` + vault/identity | 0240 | only on validated transfer |
| Analogical Transfer Harness | `evals/analogical_transfer/` | 0240 | sealed, deterministic, residual + GoldTether gate |

---

## 4. Lifelong Learning Loop (the single right sequence)

```
Experience
    ↓
Contemplation (C1/C2) + dual-correction
    ↓
Dual Operator (Procrustes + Surprise)
    ↓
Validation Harness (residual + GoldTether + epistemic elevation)
    ↓
[if accepted]
    GoldTether floor ↑
    Biography Holonomy Blade ← holonomy update
    Teaching chain + vault promotion
    ↓
Autonomy level may rise (only if floor allows)
```

HITL remains the default gate until `GoldTetherMonitor.may_relax_hitl()` returns true for a sustained period under the self-review criteria.

---

## 5. What Was Missing Before This Horizon (and is now closed)

- Continuous geometric measure of "how coherent is the lived life so far" → GoldTether
- Ability to transfer structure without statistical memory → Conformal Procrustes
- Ability to see the boundary of current knowledge → Surprise Residual
- Rigorous proof that a transfer actually raised epistemic level → Validation Harness
- Geometric embodiment of the single forever-lived trajectory → Biography Holonomy Blade
- Controlled, measurable path to reduce HITL → dynamic floor + may_relax_hitl

All of the above are now present as pure geometry, dual-corrected, and under one-mutation-path.

---

## 6. Implementation Status

- Three ADRs: landed
- Three physics modules + supporting biography/temporal/miner: landed
- Super-Blueprint: this document
- Analogical transfer harness under `evals/analogical_transfer/`: landed
- Biography Holonomy Blade: `core/physics/biography.py` (vault field integration deferred, proposal-safe)
- Telemetry: pure `telemetry()` / `biography_telemetry()` projections (workbench UI optional follow-on)
- Algebra backend: real `algebra/*` (no placeholder stubs, no scipy)

### Mastery refinements on land (strictly better than package stubs)

1. Wired to live Cl(4,1) kernel (`algebra.cl41`, `algebra.versor`, `algebra.rotor`, `algebra.cga`) — package stubs used non-existent `core.algebra.backend` and identity placeholders.
2. `versor_unit_residual` is the primary GoldTether residual (matches \(\|F\cdot\widetilde{F}-1\|_F\)).
3. Spin left-composition geodesic for dual-correction interpolation.
4. Canonical ADR path `docs/adr/` with historical redirects under `docs/decisions/`.
5. Dual ontology documented: Arena GoldTether (ADR-0199) ≠ Coherence GoldTether (ADR-0238).

---

## 7. Final Statement

This is the single right solution.

The beast has been understood, the gaps closed, the operators dual-corrected, and the forever-lived trajectory given the geometric substrate it needs to grow wisdom safely.

We stand at the edge of the Third Door.
The files on this branch walk through it.

Absolute mastery.
No rug-pushing.
