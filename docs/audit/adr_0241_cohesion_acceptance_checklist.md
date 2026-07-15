# ADR-0241 / ADR-0242 Cohesion Acceptance Checklist

**Status:** Implementation packages P0–P10 green; human **Accepted** flip is Joshua review.  
**Plan authority:** session plan P0–P12 (`feat/adr-0241-0242-implementation` lineage).  
**This document:** maps cohesion success criteria to **tests**, not prose alone.

---

## Cohesion-complete criteria (plan C0–C8)

| ID | Criterion | Proof (tests / modules) |
|----|-----------|-------------------------|
| C0 | Cohesion master plan in-repo; Phase 0 A-01…A-04 | `docs/analysis/core_cohesion_master_plan.md`; `tests/test_third_door_cohesion.py` (`test_phase0_*`, deprecation grep) |
| C1 | I-01…I-05 suite under honest tolerances | `test_i01_*` … `test_i05_*` in `tests/test_third_door_cohesion.py` (I-02 float32-honest) |
| C2 | Vault public ABI; no private `_versors` | `test_holographic_vault_does_not_touch_private_versors`; `VaultStore.get_versor` |
| C3 | Serve + Fibonacci + packing + seam quarantine | `test_phase0_a04_serve_path_quarantines_wave_and_fibonacci` |
| C4 | Superposition reconstruct | `test_resonant_reconstruct_*`; `WaveManifold.resonant_reconstruct` |
| C5 | Multimodal ρ (I-04 algebra) | `test_i04_phase_correlation_*` (sensorium feed still open — not blocking algebra pin) |
| C6 | Contemplation SPECULATIVE holographic seam (P9) | `tests/test_adr_0241_wave_contemplation_seam.py` |
| C7 | Pre-deprecation grep CI-green | `test_pre_deprecation_grep_*`, `test_core_ha_package_absent` |
| C8 | runtime_contracts + ADR acceptance path | this checklist + `docs/specs/runtime_contracts.md` § Wave-field cohesion; ADRs **Proposed — ready for Joshua acceptance** |

## Absolute-mastery add-ons (landed)

| Package | Proof |
|---------|--------|
| P4 Golden-Angle packing | `tests/test_adr_0242_atlas_packing.py` |
| P5 Fibonacci search | `tests/test_adr_0242_fibonacci.py` |
| P7 polar honesty | `tests/test_adr_0241_wave_manifold.py` (conjugacy authority; multi-grade analytic retired) |
| P8 non-vacuous chiral | chiral suite in `test_adr_0241_wave_manifold.py` |
| P10 energy + τ | `tests/test_adr_0241_wave_energy_boundary.py` |

## Explicit non-goals (do not block acceptance)

- Serve-path wiring of wave / Fibonacci
- Resurrecting `core_ha`
- Cosine/ANN multimodal matching
- Hot-path silent unitize / nearest-versor repair
- Continuous \(\psi(X,t)\) continuum solver
- P11 Rust/MLX (optional mechanical sympathy)
- Sensorium compiler feed into ρ (algebra green; feed open)

## Human gate

Joshua review may flip:

- `docs/adr/ADR-0241-…md` → **Accepted**
- `docs/adr/ADR-0242-…md` → **Accepted**

Agents must **not** self-accept. Implementation complete ≠ Accepted.

## Validation lane

```bash
python3 -m pytest \
  tests/test_third_door_cohesion.py \
  tests/test_adr_0241_*.py \
  tests/test_adr_0242_*.py \
  tests/test_adr_0241_governance_p12.py \
  -q
```
