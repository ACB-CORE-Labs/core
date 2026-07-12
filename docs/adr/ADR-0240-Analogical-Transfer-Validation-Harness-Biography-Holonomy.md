# ADR-0240: Analogical Transfer Harness + Biography Holonomy + Temporal Gate + Self-Authorship Miner

**Status:** Proposed  
**Date:** 2026-07-11  
**Branch:** `r&d/generalized-agent`  
**Parent:** [#10](https://core-gitquarters.acbcontent.org/core-labs/core/issues/10) · Issue [#13](https://core-gitquarters.acbcontent.org/core-labs/core/issues/13)  
**Canonical path:** `docs/adr/`

**Related:** ADR-0010 Identity · ADR-0055/0080 Contemplation · ADR-0150/0151 Proposal corridor · ADR-0199 Arena · ADR-0238/0239 Third Door operators

**Acceptance path:** green `tests/test_adr_0240_*.py` + harness wrong=0 on fixture pair + Josh review.

---

## 1. Context

Operators alone do not prove generalized agency. This ADR lands the **genius layer** that binds them to lifelong identity and safe proposal discipline:

1. **Analogical Transfer Validation Harness** — solved domain → novel domain under residual measurement + wrong=0  
2. **Biography Holonomy Blade** — forever-lived individuality as reconstructible holonomy  
3. **Temporal Admissibility Gate** — wisdom as geometry (`ADMIT` / `NOT_YET` / `REFUSE`)  
4. **Self-Authorship Miner** — geometry-guided **proposal-only** extensions  

### Mastery refinements

- Biography is **recompute-from-trajectory**, not raw experience storage (reconstruction-over-storage).  
- Temporal gate never confabulates early — typed `NOT_YET` disclosures.  
- Miner emits `epistemic_status=SPECULATIVE` only; zero vault writes; stable proposal_id ordering.  
- Harness is pytest-first; Tier-2 CLAIMS pin deferred until green history exists (do not hand-edit `CLAIMS.md`).

---

## 2. Decision

### 2.1 Analogical transfer harness

Path: `evals/analogical_transfer/harness.py`

```text
learn V = conformal_procrustes(source → target)
mapped = V * novel_query * reverse(V)
residual = ||mapped − expected||
wrong++ if residual > threshold and not refused
```

Fixture pair: rotation structural transfer across domains (`make_fixture_pair`).

### 2.2 Biography Holonomy Blade

Path: `core/physics/biography.py`

- `integrate_biography(trajectory)` → `BiographyHolonomyBlade` via `holonomy_encode`  
- Order is load-bearing; empty trajectory refused  
- Telemetry schema `biography_holonomy_v1` (hash, steps, closure, scalar/pseudoscalar projections)

### 2.3 Temporal Admissibility Gate

Path: `core/physics/temporal_gate.py`

Pure predicate over `TemporalContext` (step, min_step, evidence counts, residual ceiling, prerequisites). Returns typed disclosure payloads suitable for epistemic surfaces.

### 2.4 Self-Authorship Miner

Path: `core/physics/self_authorship.py`

- Inputs: current/reference versors, optional basis + analogs  
- Outputs: ordered `AuthorshipProposal` tuples with `drift_residual` + `closure_proof`  
- **Never** calls `VaultStore.store`; promotion remains ADR-0151 / review corridor  

---

## 3. Consequences

### Positive

- Lifelong identity strengthened via reconstructible holonomy.  
- Transfer claims become falsifiable (wrong=0 harness).  
- Self-extension stays proposal-only (INV-21/22/23 spirit).  

### Risks

| Risk | Mitigation |
|---|---|
| Biography used as memory dump | hash + holonomy only; no raw transcript storage |
| Miner auto-serve | SPECULATIVE only; no serving path import |
| Premature claim emission | Temporal gate NOT_YET |

### Non-goals

- Physical motor decode  
- Auto-accept proposals  
- CLAIMS Tier-2 pin in this PR  

---

## 4. Proof obligations

- **H-1** Fixture transfer wrong=0 under threshold.  
- **H-2** Biography reconstructible and order-sensitive.  
- **H-3** Temporal NOT_YET before min_step / insufficient evidence.  
- **H-4** Miner proposals all SPECULATIVE; deterministic id order.  
- **H-5** No module imports vault store for mutation.
