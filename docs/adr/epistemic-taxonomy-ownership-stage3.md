# Epistemic taxonomy ownership (Master Blueprint Stage 3A)

**Status**: Binding ownership note (not an ADR renumber)  
**Date**: 2026-07-20  
**Related**: `core/epistemic_state.py`, `teaching/epistemic.py`, `vault/store.py`, `core/cognition/geometric_coherence.py`

## Decision

CORE keeps **three orthogonal axes**. They must not be collapsed into one enum.

| Axis | Type | Owner module | Purpose |
|------|------|--------------|---------|
| Vault / pack standing | `EpistemicStatus` | `teaching/epistemic.py` | Durable SPECULATIVE / COHERENT / CONTESTED / FALSIFIED |
| Turn / dialogue taxonomy | `EpistemicState` | `core/epistemic_state.py` | Observability (perceived, verified, decoded, …) — **no COHERENT member** |
| Field geometric closure | `GeometricCoherenceVerdict` | `core/cognition/geometric_coherence.py` | Turn-level versor + GoldTether closed vs unverified |

## Mapping

- Vault `EpistemicStatus.COHERENT` → surface `EpistemicState.DECODED` via `epistemic_state_for_vault_status` (existing).
- Turn `GeometricCoherenceVerdict.GEOMETRICALLY_VERIFIED` does **not** auto-promote vault rows.
- Vault COHERENT promotion remains `VaultStore.store` / `apply_certified_promotion` / `promote_eligible_entries` only (INV-29).

## Forbidden

- Adding `EpistemicState.COHERENT` as a duplicate label without this ownership split.
- Using a single scalar score or bookkeeping flag as “coherent” without geometric checks on the field axis.
