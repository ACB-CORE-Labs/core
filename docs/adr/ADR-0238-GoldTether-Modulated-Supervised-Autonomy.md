# ADR-0238: GoldTether-Modulated Supervised Autonomy + Dynamic Pseudoscalar Floor

**Status:** Proposed  
**Date:** 2026-07-11  
**Branch:** `r&d/generalized-agent`  
**Parent tracking:** [#10](https://core-gitquarters.acbcontent.org/core-labs/core/issues/10) · Issue [#11](https://core-gitquarters.acbcontent.org/core-labs/core/issues/11)  
**Owners:** CORE Labs / R&D  
**Canonical path:** `docs/adr/` (not historical `docs/decisions/`)

**Related:**

- ADR-0010 Identity Physics
- ADR-0006 Field Energy (distinct residual namespace)
- ADR-0055 / ADR-0056 / ADR-0080 Contemplation + reviewed promotion
- ADR-0175 Calibrated Attempt-and-Eliminate
- ADR-0199 Cross-Domain Learning Arena (`GoldTether` *protocol* — different contract)
- ADR-0239 Conformal Procrustes + Surprise Dual
- ADR-0240 Analogical Transfer + Biography Holonomy

**Depends on:** Cl(4,1) closure (`algebra/versor.py`), manifold slerp (`algebra/rotor.py`)

**Acceptance path:** green `tests/test_adr_0238_goldtether.py` + smoke/algebra lanes + Josh review.

---

## 1. Context

CORE needs a **coherence tether** that modulates autonomy without violating HITL defaults, one-mutation-path review, or algebraic closure. Issue #10/#11 name this the GoldTether-modulated supervised autonomy envelope with a dynamic grade-5 pseudoscalar floor.

### Dual ontology (mastery refinement)

| Name | ADR | Contract |
|---|---|---|
| **Arena GoldTether** | ADR-0199 | `is_correct` / `gold_answer` — independent truth for practice scoring |
| **Coherence GoldTether** | **this ADR** | residual + dynamic floor + practice/serve autonomy bands |

Shared metaphor (gold as anchor). **Different types, different modules.** Implementation lives in `core/physics/goldtether.py` as `GoldTetherMonitor` / `CoherenceResidual` — never shadows `core.learning_arena.protocols.GoldTether`.

### Problem

Without a geometric autonomy envelope, either:

1. autonomy is premature (unsafe serve-path self-action), or  
2. supervision is unstructured (no residual, no floor, no dual-correction blend).

---

## 2. Decision

### 2.1 Harmonized residual

```text
drift            = |ps(current) − ps(reference)|  (grade-5 / magnitude)
geometric_distance = || reverse(ref) * current − 1 ||_F
combined         = w_drift * drift + (1 − w_drift) * normalize(geo)
kappa            = 1 / (1 + combined / floor)     # monotone; scales blend only
```

Named config only: `decay_N`, `w_drift`, `floor_init`, `critical_ratio`, `practice_autonomy_enabled`, `serve_supervised_blend_authorized`.

**Residual namespaces (non-negotiable):**

- ADR-0006 `EnergyProfile.coherence_residual` — thermodynamic class input  
- ADR-0238 `CoherenceResidual.combined` — autonomy tether  
- ADR-0239 `procrustes_residual` / surprise residual — structural transfer  

Do not conflate.

### 2.2 Dynamic pseudoscalar floor

- Initialized at `floor_init` (primal retained forever under decay).
- Updated **only** on practice successes with residual &lt; current floor.
- Decay window `decay_N` keeps recent residuals; floor never drops below half primal.
- Serve mode never promotes the floor.
- Telemetry schema: `goldtether_coherence_v1` (value, sign, n_samples, recent_residuals, config).

### 2.3 Autonomy envelope

| Band | Condition | Practice | Serve |
|---|---|---|---|
| `AUTONOMOUS` | R &lt; floor | only if `practice_autonomy_enabled` | **never** |
| `SUPERVISED_BLEND` | R ≤ critical | default below/mid band | only if `serve_supervised_blend_authorized` |
| `FAIL_CLOSED` | R &gt; critical or serve default | yes | **default** |

HITL phase-out is a **measured curve**, not a flag flip. Self-review gates are documented; they are not auto-proven by this ADR.

### 2.4 Supervised blend (dual-correction)

```text
R = word_transition_rotor(source, target)   # = target * reverse(source)
R^α = rotor_power(R, α)
out = R^α * source                          # Spin left-composition
assert versor_condition(out) < 1e-6
# α=0 → source; α=1 → target (unit versors)
```

**Mastery correction:** sandwich conjugation `R^α * source * reverse(R^α)` is the wrong geodesic for *state* interpolation (it maps the identity to itself). Left composition on the rotor group is the dual-correction surface that lands exactly on the endpoints.

No Euclidean lerp on multivector coefficients. No hot-path unitize repair.

### 2.5 Implementation surface

- Module: `core/physics/goldtether.py`
- Types: `GoldTetherConfig`, `CoherenceResidual`, `AutonomyBand`, `AutonomyDecision`, `PseudoscalarFloorState`, `GoldTetherMonitor`, `OperatingMode`
- Proof tests: `tests/test_adr_0238_goldtether.py`

---

## 3. Consequences

### Positive

- Geometry-first autonomy modulation without stochastic fallback.
- Serve remains fail-closed by default (HITL preserved).
- Pseudoscalar floor is a first-class telemetry channel for lifelong coherence curves.
- Explicit dual ontology prevents Arena vs Coherence confusion under review.

### Risks / mitigations

| Risk | Mitigation |
|---|---|
| Residual conflation with energy residual | Distinct type names + ADR text + tests |
| Premature autonomy | `practice_autonomy_enabled=False` default; serve never autonomous |
| Drift repair disguised as blend | Blend only via `rotor_power` / transition rotors |

### Non-goals

- Auto-promotion of SPECULATIVE → COHERENT
- Replacing ADR-0199 arena GoldTether
- Approximate recall or sampling

---

## 4. Proof obligations

- **G-1** Replay: identical (current, reference, config, sequence) → identical residual/floor/decision telemetry.
- **G-2** Closure: every `supervised_blend` output has `versor_condition < 1e-6`.
- **G-3** Serve never returns `AUTONOMOUS`.
- **G-4** Floor updates only on practice success below floor.
- **G-5** Arena GoldTether protocol tests remain green unchanged.
