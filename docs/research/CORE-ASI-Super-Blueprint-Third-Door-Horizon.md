# CORE ASI Super-Blueprint — Third-Door Horizon

**Status:** R&D blueprint (programmatic land on `r&d/generalized-agent`)  
**Date:** 2026-07-11  
**Tracking:** Issues #10–#13 · ADR-0238 · ADR-0239 · ADR-0240  
**Mode:** Geometry-first. No statistical crutches. No sampling. No confabulation.

---

## 1. North star

```text
listen → comprehend → recall → think → articulate → learn (reviewed) → replay
```

The Third Door extends this path with **structural analogy**, **coherence-tethered autonomy**, and **lifelong biography holonomy** — without leaving the Cl(4,1) substrate or the review-gated mutation corridor.

---

## 2. Axioms (non-negotiable)

1. Cl(4,1) multivector versors `[f32|f64; 32]`  
2. Algebraic closure: `versor_condition(F) < 1e-6`  
3. Dual-correction (factor slerp / transition rotors — not Euclidean lerp)  
4. Replay-determinism (byte-identical traces)  
5. One-mutation-path + review gates  
6. Reconstruction-over-storage  
7. Forever-lived single trajectory / biography holonomy  

Pillars: **GoldTether coherence**, **Practice vs Serve risk-reward physics**, **Epistemic elevation only through articulate reason + contemplation**.

HITL phase-out only after proven safe self-review — not in this land as a flip switch.

---

## 3. Dual GoldTether ontology

| Sense | Module | Role |
|---|---|---|
| Arena GoldTether (ADR-0199) | `core/learning_arena` | Independent truth for practice scoring |
| Coherence GoldTether (ADR-0238) | `core/physics/goldtether.py` | Residual + dynamic pseudoscalar floor + autonomy bands |

Do not unify the types. Do not shadow names.

---

## 4. Operator algebra (landed modules)

### 4.1 Coherence GoldTether — `core/physics/goldtether.py`

```text
measure → CoherenceResidual(drift, geo, combined, kappa)
update_floor → PseudoscalarFloorState   # practice success only
decide → AutonomyBand                   # serve never AUTONOMOUS by default
supervised_blend → closed versor        # rotor_power slerp
telemetry → goldtether_coherence_v1
```

Bands: `AUTONOMOUS | SUPERVISED_BLEND | FAIL_CLOSED`  
Critical: `floor * critical_ratio`  
Config names only: `decay_N`, `w_drift`, `floor_init`, `critical_ratio`, `practice_autonomy_enabled`, `serve_supervised_blend_authorized`.

### 4.2 Dynamic manifold — `core/physics/dynamic_manifold.py`

```text
signature_aware_pca      # null axes classified, never dropped
conformal_procrustes     # versor map; dedicated residual norm
cartan_iwasawa_factorize # K, A, N dual-correction surface
dual_correction_slerp    # factor-wise power then recompose
```

### 4.3 Surprise dual — `core/physics/surprise.py`

```text
S(x) = x − proj_B(x)
analogy_seed → ordered affinities
dual_operator → productive novelty iff residual ≤ threshold/κ
```

### 4.4 Genius layer — ADR-0240

| Module | Role |
|---|---|
| `core/physics/biography.py` | Biography Holonomy Blade (recompute) |
| `core/physics/temporal_gate.py` | ADMIT / NOT_YET / REFUSE |
| `core/physics/self_authorship.py` | SPECULATIVE proposals only |
| `evals/analogical_transfer/harness.py` | Transfer validation, wrong=0 |

---

## 5. Practice vs Serve physics

```text
PRACTICE: residual learning + optional autonomy when enabled + floor updates
SERVE:    fail-closed default; supervised blend only if explicitly authorized
```

Risk-reward: practice earns evidence; serve may not invent authority.

---

## 6. Lifelong coherence telemetry

Required channels (pure projections; workbench-consumable):

1. **Pseudoscalar floor** — `GoldTetherMonitor.telemetry()`  
2. **Manifold projection** — PCA axis classifications + explained fractions  
3. **Biography holonomy** — `biography_telemetry()`  

Do not break existing workbench contracts; additive only.

---

## 7. Sensorimotor note

Afferent sensorimotor (ADR-0209) and efferent gates (ADR-0198) remain as-is. This land does **not** mount physical decoders. Cartan–Iwasawa paths are zero-fabrication algebraic scaffolds for future trajectory operators.

Rust parity (`core-rs`) deferred until Python operators are sealed.

---

## 8. Invariants preserved

- No cosine/ANN/HNSW as runtime memory truth  
- No stochastic generation on cognitive path  
- No drift-repair unitize outside construction boundaries  
- No unreviewed durable mutation  
- Arena practice engine unchanged  

---

## 9. Validation

```bash
python -m pytest tests/test_adr_0238_goldtether.py tests/test_adr_0239_*.py tests/test_adr_0240_*.py -q
core test --suite smoke -q
core test --suite algebra -q
```

---

## 10. Mastery refinements vs original sandbox artifacts

1. ADR path corrected to `docs/adr/` (canonical); thin redirects under `docs/decisions/` for Issue #10 path compatibility.  
2. Dual GoldTether ontology made explicit and non-colliding.  
3. Residual namespaces separated (energy / coherence / procrustes / surprise).  
4. Null PCA classification mandatory with counts.  
5. Serve autonomy hard-blocked; HITL default documented as curve not switch.  
6. Biography as reconstructible holonomy only.  
7. Miner proposal-only with stable content hashes.  
8. Branch rebased onto current Forgejo `main` before land.  
9. **Supervised blend / dual-correction slerp use Spin left-composition**  
   `out = rotor_power(R, α) * source` (not sandwich conjugation). Sandwich maps the identity to itself and is the wrong geodesic for state interpolation; endpoints are exact (α=0→source, α=1→target).

This is the single right solution for the Third-Door Horizon layer.
