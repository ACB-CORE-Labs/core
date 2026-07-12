# ADR-0239: Conformal Procrustes + Surprise Residual Dual Operator

**Status:** Proposed  
**Date:** 2026-07-11  
**Branch:** `r&d/generalized-agent`  
**Parent:** [#10](https://core-gitquarters.acbcontent.org/core-labs/core/issues/10) · Issue [#12](https://core-gitquarters.acbcontent.org/core-labs/core/issues/12)  
**Canonical path:** `docs/adr/`

**Related:** ADR-0013 Sensorium · ADR-0198/0209 Sensorimotor · ADR-0238 Coherence GoldTether · ADR-0240 Transfer Harness · ADR-0237 GeometricDelta ABI

**Acceptance path:** green `tests/test_adr_0239_*.py` + algebra lane + Josh review.

---

## 1. Context

Generalized agentic intelligence requires **structural analogy** (transport a solved map into a novel domain) and **boundary sensing** (what is not yet spanned by known structure) without statistical crutches, sampling, or confabulation.

Issue #12 specifies:

- Signature-aware Conformal PCA with null-vector classification  
- Conformal Procrustes (versor search for structural analogy)  
- Surprise Residual `S(x) = x − proj_B(x)`  
- Dual: high surprise seeds Procrustes against vault analogs → productive novelty  

### Mastery refinements closed here

1. **Null vectors never silently skipped** — every axis classified (`SPACELIKE|TIMELIKE|NULL|DEGENERATE`) and counted.  
2. **Dedicated `procrustes_residual` norm** — not null-margin, not energy residual, not GoldTether combined residual.  
3. **κ from ADR-0238** scales productive threshold only — never invents content.  
4. **Cartan–Iwasawa constructive factorization** supplies the dual-correction surface for factor-wise slerp.

---

## 2. Decision

### 2.1 Signature-aware PCA

Module: `core/physics/dynamic_manifold.py` → `signature_aware_pca`.

- Metric on grade-1: Cl(4,1) signature `(+,+,+,+,-)`.  
- Higher grades: positive definite on coefficients (classification sense).  
- Metric-rescaled covariance + symmetric `eigh` (deterministic order).  
- Eigenvector sign convention: first nonzero component positive.  
- **All axes returned** including NULL.

### 2.2 Conformal Procrustes

`conformal_procrustes(sources, targets) → ConformalProcrustesResult`

- Single pair: `word_transition_rotor(s, t)`.  
- Multi pair: sequential manifold average (equal-weight geodesic midpoints in input order).  
- Output versor must satisfy `versor_condition < 1e-6`.  
- Residual: `procrustes_residual(s, t, V) = ||V s reverse(V) − t||_F`.

### 2.3 Cartan–Iwasawa factors

`cartan_iwasawa_factorize(V) → K, A, N` with reconstruction residual.

- Simple rotation (`B² < 0`) → K  
- Simple boost (`B² > 0`) → A  
- Null / residual → N  
- `dual_correction_slerp` powers factors independently then recomposes.

### 2.4 Surprise Residual + dual

Module: `core/physics/surprise.py`

```text
S(x) = x − proj_B(x)     # orthonormal span of ordered basis
affinity(analog) = |cos|(S, target−source)
dual: best analog → Procrustes; productive iff residual ≤ threshold/κ
```

No sampling. Ordered analog list; stable sort by affinity desc, id asc.

---

## 3. Consequences

### Positive

- Structural transfer without embeddings-as-truth.  
- Explicit null classification closes a long-standing silent-drop hazard.  
- Dual operator converts surprise into *proposal-grade* novelty only when residual-proven.

### Risks

| Risk | Mitigation |
|---|---|
| PCA treated as memory truth | PCA is analysis/telemetry only; vault recall remains exact CGA |
| Non-simple versor average drift | unitize only at construction boundary; fail residual loudly |
| Confabulated analogy | productive=False → refuse / NOT_YET path (ADR-0240) |

### Non-goals

- ANN / cosine vault recall  
- Stochastic exploration  
- Motor actuation  

---

## 4. Proof obligations

- **P-1** Null axes present in result counts when constructed.  
- **P-2** Procrustes output closed.  
- **P-3** Surprise residual orthogonal to basis span (within tol).  
- **P-4** Dual replay byte-identical for identical inputs.  
- **P-5** Cartan–Iwasawa factors each closed.
