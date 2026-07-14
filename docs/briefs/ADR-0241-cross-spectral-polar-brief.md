# Brief: ADR-0241 True Cross-Spectral \(\mathcal{C}_{AB}\) + Clifford Polar (P7)

**For:** Antigravity / Gemini design + TDD implementation  
**From:** CORE ADR-0241 mastery (PR #37, `feat/adr-0241-0242-implementation`)  
**Status:** STOP POINT — largest remaining namesake-green gap on wave polar

---

## Takeoff

- Forgejo: `core-labs/core` — **not** GitHub  
- Branch: `feat/adr-0241-0242-implementation`  
- Pull latest (includes ADR-0242 packing/Fibonacci):  
  `git fetch forgejo && git checkout feat/adr-0241-0242-implementation && git pull forgejo feat/adr-0241-0242-implementation`  
- PR: https://core-gitquarters.acbcontent.org/core-labs/core/pulls/37  

### Read first (order)

1. `AGENTS.md`  
2. `docs/adr/ADR-0241-wave-field-driven-hyperbolic-atlas-and-resonant-cognition.md` § Decision table (Procrustes → cross-spectral polar)  
3. `docs/research/third-door-blueprint-fidelity.md` §12 (W3 marked 🟡 thin wrap)  
4. `core/physics/wave_manifold.py` — `wave_analogical_polar`, `wave_field_conjugacy`  
5. `core/physics/dynamic_manifold.py` — `_field_conjugacy_versor` (current engine under the thin wrap)  
6. Existing green pins: `tests/test_adr_0241_wave_manifold.py` polar / multi-pair tests  

### Already GREEN (do not redesign)

| Surface | Status |
|---------|--------|
| Sandwich / left-spinor / Schrödinger step | GREEN |
| Spectral leakage → surprise | GREEN |
| Unitary residual → GoldTether | GREEN |
| `resonant_reconstruct`, `phase_correlation` | GREEN |
| Holographic vault + public `get_versor` | GREEN |
| Atlas packing + Fibonacci (ADR-0242) | GREEN |
| Serve quarantine | GREEN |

---

## Problem (why this is not green mastery yet)

ADR-0241 claims:

> Cross-spectral correlation \(\mathcal{C}_{AB}\) → Clifford polar decomposition for analogy rotor

**Current code:** `wave_analogical_polar` / `wave_field_conjugacy` are a **lazy thin wrap** over `_field_conjugacy_versor` (SVD nullspace + multiplicative Gauss–Newton residual minimizer). That is pre-ADR pointwise conjugacy, **not** a spectral correlation matrix + polar factor.

Goal: make polar **algebraically faithful** so at least one RED test fails on thin wrap alone and passes on true polar.

---

## Hard constraints

| Rule | Detail |
|------|--------|
| Algebra-native only | `algebra/*` only — **no scipy as algebraic truth** |
| Transport pin | Multivector field path = sandwich \(R\psi\widetilde{R}\); do not silently mix left-spinor |
| Closure | Construction-boundary close only; `versor_condition < 1e-6`; no hot-path unitize |
| No dual permanent path | `conformal_procrustes` field path must keep calling wave polar (no parallel residual engine) |
| Determinism | No random; fixed fixtures |
| Off-serve | Do not wire into `chat/runtime.py` |
| Exact recall | No cosine/ANN |

---

## Design deliverables (do these first if math is non-obvious)

Write a short design note (can live in PR body or `docs/briefs/` update) covering:

1. **Definition of \(\mathcal{C}_{AB}\)** on multivector fields in Cl(4,1) 32-vectors (not Euclidean feature matrices).  
2. **Polar decomposition path** that yields sandwich rotor \(R\) with \(\psi_B \approx R\psi_A\widetilde{R}\).  
3. **Multi-pair aggregation**: how N pairs become one \(R\) (spectral aggregate then polar vs joint residual).  
4. **Relation to `_field_conjugacy_versor`**: replace, fallback, or residual-check only.  
5. **Global sign ambiguity** of rotors (tests already allow ±R).  

If design requires multi-model debate, return the design note for human/Grok review **before** large GREEN implementation. If design is clear and RED tests fail thin wrap, proceed TDD.

---

## Implementation targets

| API | Expected change |
|-----|-----------------|
| `WaveManifold.wave_analogical_polar(ψ_A, ψ_B) -> R` | True polar / \(\mathcal{C}_{AB}\) path |
| `WaveManifold.wave_field_conjugacy(sources, targets) -> (R, residual)` | Multi-pair true path |
| `dynamic_manifold.conformal_procrustes` field path | Remains wave delegate |
| Kabsch null-point / (5,K) clouds | **Unchanged** compatibility path |

---

## RED tests that must not pass for free on thin wrap

Add / extend `tests/test_adr_0241_wave_manifold.py` (or `tests/test_adr_0241_wave_polar.py`):

```text
test_wave_polar_recovers_known_sandwich_rotor          # already green — keep
test_wave_polar_multi_grade_packet_beats_thin_wrap    # NEW: case where residual-minimizer
                                                      # conjugacy diverges from true polar
test_wave_field_conjugacy_multi_pair_true_polar       # multi-pair fidelity pin
test_conformal_procrustes_still_delegates_to_wave     # no dual path regression
test_polar_construction_closed_versor_condition       # versor_condition < 1e-6
test_no_scipy_as_algebraic_truth_in_wave_polar_module # AST/import pin optional
```

**Critical:** invent at least one multi-grade or multi-pair fixture where current `_field_conjugacy_versor` residual is acceptable under loose tol but **true polar** is required by ADR math. If no such fixture exists after honest design, document why thin wrap **is** the polar for Cl(4,1) sandwich conjugacy and demote ADR language instead of shipping namesake-green — **honesty over theater**.

---

## Out of scope (this task)

- Non-vacuous chiral / pair-spinor (P8 — separate brief)  
- Contemplation Trace A wiring (P9)  
- True \(H^2\) geodesic packing refinement (ADR-0242 packing already green with CGA null-point \(d\))  
- Rust/MLX acceleration  
- Serve-path wiring  
- CLAIMS.md / ADR Accepted flip  

---

## Validation

```bash
python3 -m pytest tests/test_adr_0241_wave_manifold.py tests/test_adr_0242_*.py tests/test_third_door_cohesion.py tests/test_adr_0241_holographic_vault.py -q
# plus any new polar tests
# Third-Door Procrustes / surprise / goldtether must stay green
python3 -m pytest tests/test_adr_0239*.py tests/test_adr_0238*.py -q
```

## Success

1. Polar path is either **algebraically true \(\mathcal{C}_{AB}\)+polar** with thin-wrap-failing RED tests, **or** ADR/fidelity language demoted with proof that conjugacy **is** the polar in this algebra.  
2. No dual permanent residual path.  
3. Serve quarantine + versor_condition held.  
4. Fidelity W3 flipped only under the honest criterion above.  
5. Commit on `feat/adr-0241-0242-implementation` and push Forgejo (updates PR #37) — or open stacked PR if preferred.
