# ADR-0241 / ADR-0242 Drive-Complete Plan (Post-Cohesion Gap Close)

**Plan ID:** Plan B — Drive-complete gap close  
**Status (archive 2026-07-15):** Macro implementation **landed on PR #38** (D0–D8, D3–D7 vectors, plus P11a backend hygiene). Remaining: **D9** optional Rust f64 GP parity / second runner (P11a partial), **D10** Joshua Accept. PR #38 tip `015c9fac` — smoke green; lane-shas red on Act (local pins 9/9).  
**Branch:** `feat/adr-0241-p9-contemplation-trace-a` (PR #38 only — no micro-PRs)  
**Date (plan authored):** 2026-07-15  
**Date (archived to docs):** 2026-07-15  
**Policy:** PRs only at macro-phase completion for life of this plan.

## Authority sources (Drive = design truth)

The **four Drive documents** that authored this plan:

| # | Source | Drive doc_id | In-repo mirror |
|---|--------|--------------|----------------|
| 1 | **ADR-0241** wave-field hyperbolic atlas | `1F_7QYtPysBP4qMbLGlGPnXgYx9IXug8nUYrpiCGSunE` | `docs/adr/ADR-0241-wave-field-driven-hyperbolic-atlas-and-resonant-cognition.md` |
| 2 | **ADR-0242** deterministic Fibonacci + evidence-gated optimization | `15_NECCPy-tEWGfYi_BNqawm8GytUTMkz1DsOqGVMXhI` | `docs/adr/ADR-0242-atlas-packing-and-fibonacci.md` |
| 3 | **core_ha** unification / deprecation | `1eFNoXQl5BbUo6g4GBzRXi5tyIhT5RUGZQG6afaVXTg4` | `docs/analysis/core_ha_unification_and_deprecation_plan.md` |
| 4 | **Fibonacci applications** R&D memo | `1wcuxwfxk6AW6du4SgKe4AuRxMaE5tipxG2VbrXeWM6c` | `docs/analysis/fibonacci_applications_in_core_substrate.md` |

Supporting (not the Drive quartet, but load-bearing):

| Source | Path |
|--------|------|
| Cohesion master plan (entity I-*) | `docs/analysis/core_cohesion_master_plan.md` |
| Fidelity ledger | `docs/research/third-door-blueprint-fidelity.md` §12 |
| Acceptance checklist | `docs/audit/adr_0241_cohesion_acceptance_checklist.md` |

**Critical discovery (2026-07-15):** Cohesion packages **P0–P12 are implemented**. That is **not** full fidelity to the Drive ADR-0242 five-vector thesis or the Fibonacci applications memo. In-repo ADR-0242 was scoped as packing + section search only; Drive ADR-0242 is broader (evidence-gated operators + five vectors + sovereignty invariant).

---

## Phase A — Already landed (do not re-open)

### A1. Cohesion plan P0–P12 (PR #37 + PR #38)

| Pkg | Deliverable | Proof |
|-----|-------------|--------|
| P0–P3 | Cohesion plan, vault ABI, I-01…I-05, reconstruct | `tests/test_third_door_cohesion.py`, holographic vault |
| P4–P5 | Golden-Angle packing, Fibonacci section search core | `atlas_packing.py`, `fibonacci_search.py`, ADR-0242 draft |
| P6 | \(\rho\) algebra (I-04) | `phase_correlation` |
| P7–P8 | Polar honesty (conjugacy authority); chiral non-vacuous spinor path | wave_manifold tests + briefs |
| P9 | Trace A wave_seam SPECULATIVE seal / hypothesis vs evidence | `core/contemplation/wave_seam.py` |
| P10 | Wave residual → energy/trajectory; \(\tau_n=F_n\tau_0\) table; crystallization gate | `wave_energy_boundary.py` |
| P12 | runtime_contracts wave section; acceptance checklist; ADRs Proposed+ready | governance tests |

### A2. ADR-0241 local operators (Drive core math, progressive continuous field)

| Requirement | Status |
|-------------|--------|
| \(\psi\) multivector field, sandwich/left transport | 🟢 |
| Spectral leakage → surprise | 🟢 |
| Resonant recall / reconstruct | 🟢 |
| Holographic vault SPECULATIVE + public ABI | 🟢 |
| GoldTether unitary residual | 🟢 |
| Chiral \(\mathcal{Q}\) (spinor path) | 🟢 |
| Continuous \(\int_M\) / \(\sup_X\) continuum | 🟡 progressive (mode samples / pointwise) |
| True multi-grade \(\mathcal{C}_{AB}\) polar | ⚪ retired honestly (conjugacy = polar for sandwich) |
| Sensorium \(\psi_\text{total}=\sum\psi_\text{mod}\) | 🔴 open (feed) |

### A3. core_ha deprecation (Python path)

| Item | Status |
|------|--------|
| No live `core_ha` / hygiene pins | 🟢 |
| Absorption into wave / GoldTether / energy / biography | 🟢 |
| Rust expm / SIMD residual hot path | 🔴 (Step 2 — optional mechanical sympathy) |

### A4. Explicit non-goals (all plans)

- Serve-path wiring of wave / Fibonacci / packing / seams  
- Resurrecting `core_ha` or Poincaré as runtime memory truth  
- Cosine / ANN multimodal ranking  
- Hot-path silent unitize / nearest-versor drift repair  
- Fibonacci dictating proposition truth, safety, identity, or auto-promotion (**Drive sovereignty invariant**)  
- V5 anyons entering production without proofs  

---

## Phase B — Drive gaps (new work packages)

Authority: **Drive ADR-0242 five vectors** + Fibonacci memo + residual ADR-0241 progressive items + core_ha Step 2.

```text
D0  Align in-repo docs to Drive ADR-0242 scope (no silent scope shrink)
D1  V1: FibonacciSearchCertificate + OptimizationFailure + evidence gate
D2  V1b: GoldTether κ optional path — cert-only, fail → baseline κ=1.0
D3  V2: Multi-band E_n(t) temporal basis (research → evals quarantine first)
D4  V3 polish: reconstruction-over-storage allocator identity + packing honesty pins
D5  V4: Fibonacci-word observability scheduler (telemetry only)
D6  V5: topological_reasoning research scaffold (isolated, blocked from prod)
D7  Sensorium → ψ packets thin feed (I-04 boundary; no cosine)
D8  Land Fibonacci applications memo in-repo + fidelity honesty pass
D9  Optional P11 Rust/MLX parity (core_ha Step 2) — only after Python authority frozen
D10 Governance re-close: ADR-0242 rewrite, CLAIMS if needed, Joshua Accept path
```

### Priority / leverage order

| Rank | Pkg | Why |
|------|-----|-----|
| 1 | **D0** | Stop docs lying about scope |
| 2 | **D1** | Highest fidelity gap to Drive ADR-0242 production Phase 1 |
| 3 | **D2** | Makes V1 load-bearing (κ) without dogma |
| 4 | **D8** | Canonical memo path for agents |
| 5 | **D4** | Cheap honesty / reconstruction-over-storage |
| 6 | **D3** | Research prototype; do not promote without benchmark |
| 7 | **D5** | Outside truth path; scheduling only |
| 8 | **D7** | Closes I-04 “feed still open” |
| 9 | **D6** | Explicit pre-research quarantine |
| 10 | **D9** | Mechanical sympathy after freeze |
| 11 | **D10** | Human Accept after D1–D2 (minimum) or full vector set |

---

## Package detail

### D0 — Doc alignment (mandatory first)

1. Rewrite / expand `docs/adr/ADR-0242-*.md` to match Drive title thesis:
   - **Deterministic Fibonacci operators and evidence-gated optimization**
   - Five vectors + sovereignty invariant + phase order  
2. Keep packing + section search as **V1/V3 landings**, not the whole ADR.  
3. Cross-link Fibonacci memo, cohesion plan, fidelity §12.  
4. Honesty table: what is GREEN vs RESEARCH vs RETIRED.

**Exit:** In-repo ADR-0242 no longer understates Drive.

---

### D1 — V1 certificate discipline (production-ready)

Drive API surface (freeze):

```text
BoundedUnimodalObjective          # exists
fibonacci_section_search(...)  → FibonacciSearchCertificate | OptimizationFailure
  # never raw float; never silent accept
FibonacciSearchCertificate:
  minimizer, final_interval, evaluations,
  ordered_points, ordered_values,
  objective_id, objective_version
  # content-addressed / replayable (hash of ordered trace + ids)
OptimizationFailure:
  reason, final_interval, evaluations, objective_id, objective_version
```

Implementation notes vs current code:

| Current | Required |
|---------|----------|
| `SearchTrace` + raise `ValueError` | Typed cert **or** failure return (or exception that maps 1:1 to failure reasons) |
| partial `certificate` dict | Full frozen dataclass + deterministic `cert_id` / digest |
| unimodality fail raises | `OptimizationFailure(reason="unimodality_violation_...")` |

Tests (RED first):

- Success path returns cert; digest stable across dual-run  
- Budget too low → typed failure  
- Nonfinite / bounds → typed failure  
- Multi-extrema unimodality → typed failure  
- Never returns bare float as public API  
- Serve quarantine still holds  

**Exit:** Drive Phase 1 API green; `SearchTrace` either deprecated or thin adapter over cert.

---

### D2 — GoldTether κ cert gate (optional path)

Drive Phase 1 integration seam:

1. Bounded κ line search may use `fibonacci_section_search`.  
2. On **cert success**: telemetry records cert; caller may *propose* κ (not auto-mutate identity).  
3. On **OptimizationFailure**: default `κ = 1.0`, log failure; no silent use of half-search.  
4. Must not authorize COHERENT / pack mutation / serve autonomy change.

**Exit:** Integration test with synthetic unimodal residual; failure path forced.

---

### D3 — V2 multi-scale temporal basis (research → evals)

Drive formula:

\[
E_n(t) = E_n(t_0)\,\exp\bigl(-(t-t_0)/(F_n\tau_0)\bigr)
\]

1. Implement pure helper (e.g. `multi_scale_energy_vector`) — **not** dogmatic production default.  
2. Comparative harness in `evals/` or `calibration/`: Fibonacci vs dyadic \(2^n\tau_0\) vs log under fixed replay.  
3. Promote into `FieldEnergyOperator` **only** with written benchmark win + Joshua gate.  
4. Optional: surprise persistence across bands \(F_5\)–\(F_7\) → DiscoveryCandidate (contemplation), SPECULATIVE only.

**Exit:** Research prototype + benchmark artifact; production energy path unchanged until gate.

---

### D4 — V3 allocator polish

Already: Golden-Angle packing + \(d_{\min}\).

Add:

1. Explicit **allocator identity + version** in metadata (`golden_angle_v1`) so layout is reconstructible from ordinal sequence.  
2. Document honest metric: CGA null-point Euclidean \(d\), not full \(H^2\) geodesic.  
3. Optional insertion-cost metric only in evals quarantine (R-04).  

**Exit:** Reconstruction-over-storage pin; no opaque mutable layout table as truth.

---

### D5 — V4 Fibonacci-word observability scheduler

Drive:

\[
W_0=B,\; W_1=A,\; W_{n+1}=W_n W_{n-1}
\]

- **A** = low-cost local measurement  
- **B** = high-cost cross-band check  

Constraints:

- **Outside cognitive truth path**  
- Cannot mutate field / vault COHERENT / packs  
- Module e.g. `core/physics/fibonacci_word_schedule.py` or `telemetry/`  
- AST pin: not imported by `chat/runtime.py`  

**Exit:** Deterministic word generator + schedule iterator tests; no serve import.

---

### D6 — V5 topological reasoning scaffold (pre-research)

1. Create isolated package path `algebra/topological_reasoning/` (or `docs/research/` + empty module stub).  
2. README: fusion \(\tau\otimes\tau=1\oplus\tau\), blocked from FFI / production imports.  
3. Architectural test: production packages must not import it.  

**Exit:** Quarantine exists; zero production coupling.

---

### D7 — Sensorium → ψ feed (I-04 boundary)

1. Thin adapter: modality packet → 32-vec \(\psi\) at construction boundary only.  
2. Superposition \(\psi_\text{total}=\sum\psi_i\) for available packets.  
3. Use `phase_correlation` only — ban cosine/ANN.  
4. If compilers incomplete: fake deterministic packets + real algebra (honest).  

**Exit:** I-04 “feed open” closed or explicitly staged with fake packets + real \(\rho\).

---

### D8 — Land Fibonacci applications memo

1. Export Drive memo → `docs/analysis/fibonacci_applications_in_core_substrate.md`.  
2. Cross-link ADR-0241/0242, energy, packing.  
3. Mark anyons / braid as research (align D6).  

**Exit:** Canonical path matches Drive “Canonical path” field.

---

### D9 — Optional Rust hot path (core_ha Step 2 / P11)

Only after D1 Python cert authority frozen:

| Binding | Role |
|---------|------|
| `diffusion.rs::expm` | Unitarity-aware \(R=\exp(B\Delta t)\) |
| `versor_unit_residual` | SIMD GoldTether residual |
| Optional `cl41::wedge` | Exterior product |

Parity tests: Rust ≈ Python within tol; no scipy as truth.

**Exit:** Optional; not required for ADR-0242 Phase 1 Accept.

---

### D10 — Governance re-close + Joshua Accept

Minimum for **Drive Phase 1 Accept** (ADR-0242 production slice):

- D0 + D1 (+ D2 preferred)  
- Fidelity ledger V1/V3 honest  
- Sovereignty invariant documented + test-pinned  

Full Drive multi-vector Accept later:

- D3–D5 as landed or explicit RESEARCH  
- D6 quarantine  
- ADR-0241 remaining progressive items called out  

**Never self-Accept** — Joshua only.

---

## Success definitions

### Minimum Drive-complete (Phase 1)

| # | Criterion |
|---|-----------|
| M0 | In-repo ADR-0242 matches Drive five-vector thesis (scope honesty) |
| M1 | V1 typed cert/failure API + dual-run stable digest |
| M2 | No silent raw-float public minimizer |
| M3 | Optional κ path fail-closed to baseline |
| M4 | Serve quarantine unchanged |
| M5 | Sovereignty: fib never sets truth / COHERENT / identity |

### Full Drive-complete (all five vectors)

M0–M5 **plus** V2 research artifact, V3 allocator identity, V4 scheduler, V5 isolated scaffold, sensorium feed staged, fidelity/governance updated.

### Absolute mastery (stretch)

+ continuous field integrals, Rust parity, comparative V2 promotion into production energy with evidence.

---

## Verification lanes

```bash
# After D1
python3 -m pytest tests/test_adr_0242_fibonacci.py tests/test_adr_0242_*cert* -q

# Cohesion regression (must stay green)
python3 -m pytest tests/test_third_door_cohesion.py tests/test_adr_0241_*.py -q

# Serve quarantine
python3 -m pytest tests/test_third_door_cohesion.py -k serve_path -q

# Optional later
python3 -m pytest tests/test_adr_0242_fibonacci_word*.py -q
core test --suite algebra -q
```

**Do not** run full `verify_lane_shas` unless demos/showcase touched.

---

## Execution order after plan approval

1. **D0** doc align ADR-0242 + land Fibonacci memo (D8 can parallel)  
2. **D1** TDD cert/failure API  
3. **D2** GoldTether κ cert gate (optional path)  
4. **D4** allocator identity polish  
5. **D3** multi-scale energy research harness (no production flip without evidence)  
6. **D5** Fibonacci-word scheduler  
7. **D7** sensorium feed thin adapter  
8. **D6** anyon research quarantine  
9. **D9** Rust only if requested  
10. **D10** fidelity + Joshua Accept package  

---

## Agent orchestration

```text
Orchestrator
  D0/D8  docs (doc-updater discipline)
  D1     tdd-guide → implement → python-reviewer → security-reviewer
  D2     tdd → goldtether integration (fail-closed)
  D3     evals quarantine first; no production promote without benchmark
  D4–D5  small pure modules + AST quarantine pins
  D6     isolation + import hygiene test
  D7     sensorium boundary + I-04 pins
  D9     rust-build-resolver only if greenlit
  D10    governance tests + human Joshua
```

Adversarial checklist after each package:

1. Namesake-green?  
2. Evidence-gated (cert/failure) where Drive requires?  
3. Serve quarantine held?  
4. Sovereignty invariant held?  
5. Docs / fidelity / code agree?  

---

## Branch strategy

- Prefer continue **PR #38** branch if still open, **or** fresh `feat/adr-0242-evidence-gated-fibonacci` from post-merge `main` after #38 lands.  
- Keep changes small: D0/D1 first PR if #38 is already large.  
- Forgejo only; no GitHub.  

---

## Summary

| Layer | Status |
|-------|--------|
| Cohesion living-entity (P0–P12) | 🟢 done |
| Drive ADR-0241 operators | 🟢 / progressive continuous field + sensorium feed open |
| Drive ADR-0242 V1 cert discipline | 🟢 landed on PR #38 (`FibonacciSearchCertificate` / `OptimizationFailure`) |
| Drive ADR-0242 V2–V5 | 🟢 research/scaffold landed (V2 multi-scale, V3 allocator id, V4 word schedule, V5 quarantine) |
| core_ha Python deprecation | 🟢; Rust Step 2 optional — **P11a** backend dispatch landed |
| Fibonacci memo in-repo | 🟢 `docs/analysis/fibonacci_applications_in_core_substrate.md` |

**This plan’s job:** close the gap between “cohesion complete” and “Drive ADR-0242 evidence-gated Fibonacci operators complete,” without re-litigating polar/chiral/packing or opening serve.
