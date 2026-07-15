# ADR-0241 / Cohesion Mastery Plan (P0–P12)

**Plan ID:** Plan A — Cohesion entity mastery  
**Status:** Implementation complete on Forgejo PR #37 (P0–P8 substrate) + PR #38 (P9–P12 + later Drive work). Human **Accepted** flip remains Joshua-only.  
**Branch lineage:** `feat/adr-0241-0242-implementation` (#37) → `feat/adr-0241-p9-contemplation-trace-a` (#38)  
**Date (plan authored):** 2026-07-14  
**Date (archived to docs):** 2026-07-15  
**Policy:** Entity cohesion over module greenness; fail-closed residual doctrine; Gemini/Antigravity design stops for pure math.

## Framing

ADR-0241 local wave operators are green. The cohesion master plan reframes "done" as **Hyperbolic Atlas absorbed into a single living Cl(4,1) entity** with Trace A/B, entity invariants I-01…I-05, Golden-Angle packing, Fibonacci optimization (ADR-0242), multimodal algebraic resonance, formal Phase 0 deprecation safety, and mechanical-sympathy Rust depth. This plan makes those facts load-bearing, keeps AGENTS.md fail-closed doctrine (reject silent dual-correction repair), and gates deepest math through Gemini/Antigravity design stop-points.

### Authority sources used to author this plan

| # | Document | Path / origin |
|---|----------|----------------|
| 1 | ADR-0241 wave-field hyperbolic atlas | `docs/adr/ADR-0241-wave-field-driven-hyperbolic-atlas-and-resonant-cognition.md` (+ Drive export) |
| 2 | ADR-0242 Fibonacci / packing (then draft) | `docs/adr/ADR-0242-atlas-packing-and-fibonacci.md` (+ Drive export) |
| 3 | Cohesion master plan | `docs/analysis/core_cohesion_master_plan.md` |
| 4 | core_ha unification / deprecation | `docs/analysis/core_ha_unification_and_deprecation_plan.md` |

Supporting: `docs/research/third-door-blueprint-fidelity.md`, Fibonacci applications memo (later D8).

---

### Entity-Level Invariants (success criteria)

| ID | Requirement | Current gap |
|----|-------------|-------------|
| **I-01** | Biography holonomy closed + **reboot-invariant** from content-addressed ledger | Session-only registry; no durable bio ledger pin |
| **I-02** | Wave ψ vaulted via CRDT/teaching chain reconstructs with \(\\|\psi_2-\psi_1\\|_F < 10^{-12}\) | No end-to-end bit-stable pin |
| **I-03** | Self-authorship never mutates active manifold / never writes COHERENT | Pattern exists; must pin against holographic seal abuse |
| **I-04** | Multimodal match via \(\langle \psi_A\widetilde{\psi}_B + \psi_B\widetilde{\psi}_A\rangle_0\) only (no cosine/ANN) | Operator + sensorium seam missing |
| **I-05** | GoldTether unitary residual \(< 10^{-6}\) on every wave transition | Local dual-check exists; not entity-wide boundary suite |

### Hyperbolic Atlas facts (under-specified before)

| Atlas concern | Cohesion / Fibonacci requirement | Implementation surface |
|---------------|----------------------------------|------------------------|
| Thaw loss | Resonant lock-in / reconstruct, not coordinate thaw | `WaveManifold` + `HolographicVaultStore` |
| Node eviction rigidity | Continuous mode spectrum + packing, not discrete node IDs | Standing-wave modes; **no** `atlas_id` resurrection |
| Mode packing | Golden-Angle / hyperbolic phyllotaxis on horosphere | New: `atlas_packing` or methods on `WaveManifold` |
| Separation | Pairwise geodesic \(d_{\min}=0.12\) or reject | Benchmark + allocator fail-closed |
| Insertion cost | CPU/alloc metric for mode registration | `evals/` / calibration only (R-04 gated observability) |
| Coordinate dissolution (ADR-0003) | Poincaré may be used **only as a construction lift** into Cl(4,1); never as runtime memory truth | Construction boundary only |

### Tension with AGENTS.md (resolve explicitly)

| Cohesion text | Risk vs CORE doctrine | Resolution in this plan |
|---------------|----------------------|-------------------------|
| R-01 “dual-correction fallback to nearest exact versor” on drift | Forbidden **hot-path drift repair** / unitize outside owned boundaries | **Fail-closed** on residual breach in propagate-like paths; any close/unitize only at **construction / admit** boundaries (`wave_manifold` exp construction, holographic `_admit`, biography construction). No silent nearest-versor repair in field/generate/vault hot paths. |
| Sketch tests use `np.random` + Euclidean norm of ψ | Non-deterministic, non-algebraic | Deterministic fixtures; CGA/reverse-product norms |
| `sup_X` continuous field residual | API is still pointwise 32-vec | Document progressive meaning: residual on registered mode samples / manifold sample set until continuous field representation exists |

---

## Recommended approach

Treat mastery as **entity cohesion**, not module greenness.

1. **Land the cohesion master plan** in-repo as the dual authority beside ADR-0241.  
2. **Phase 0 audits first** (A-01…A-04 + pre-deprecation grep) — already mostly true, must become **CI-pinned**.  
3. **Trust + entity invariant suite** (I-01…I-05 RED→GREEN) as the definition of “cohesive.”  
4. **Atlas packing + Fibonacci (ADR-0242 track)** as first-class under dual branch scope, with Antigravity/Gemini design stops for pure math.  
5. **True polar / chiral** remain algebraic mastery upgrades with design handoffs.  
6. **Rust FFI** after Python authority exists for exp/residual (mechanical sympathy), not before.  
7. Continuous adversarial audits after every GREEN package.

---

## Work package map (revised)

```text
P0  Land cohesion plan + Phase 0 audits (A-01…A-04) + honesty ledger
P1  Trust hardening (Vault public ABI, serve+Fibonacci quarantine, I-03 pins)
P2  Entity suite I-01…I-05  (tests/test_third_door_cohesion.py + entity invariants)
P3  Superposition reconstruction  ∑ c_k ψ_k
P4  Hyperbolic Atlas packing (Golden-Angle / d_min) ── STOP → Gemini design brief
P5  Fibonacci search + GoldTether κ (ADR-0242 slice A) ── STOP → Gemini design brief
P6  Multimodal phase correlation (I-04) sensorium-facing pure algebra
P7  True C_AB + Clifford polar ── STOP → Gemini design brief
P8  Non-vacuous chiral (spinor path) ── STOP → Gemini design brief
P9  Cognition seam Trace A (contemplation SPECULATIVE → teaching corridor)
P10 Energy boundary + multi-scale τ (Trace B + Fibonacci τ_n optional)
P11 Rust/MLX FFI (wedge / expm / versor_unit_residual) after P7 authority
P12 Governance close (CLAIMS, runtime_contracts, ADR-0241 Accepted, draft ADR-0242)
```

**Minimum for “ADR-0241 + cohesion complete”:** P0–P3, P6, P9, P12 (with P4–P5 honesty: either implement or demote claims).  
**Absolute mastery / genius bar:** all P0–P12 with P7–P8 math landed (not demoted).

---

## Critical files

### New
| Path | Purpose |
|------|---------|
| `docs/analysis/core_cohesion_master_plan.md` | Canonical cohesion authority (from Downloads) |
| `tests/test_third_door_cohesion.py` | Unified entity + Fibonacci + deprecation suite |
| `tests/test_entity_invariants_i01_i05.py` (or section of cohesion suite) | I-01…I-05 pins |
| `core/physics/fibonacci_search.py` | Bounded unimodal Fibonacci section search (ADR-0242) |
| `core/physics/atlas_packing.py` (or WaveManifold methods) | Golden-Angle mode packing + \(d_{\min}\) |
| `docs/briefs/ADR-0241-cross-spectral-polar-brief.md` | Gemini handoff |
| `docs/briefs/ADR-0241-chiral-spinor-brief.md` | Gemini handoff |
| `docs/briefs/ADR-0242-atlas-packing-and-fibonacci-brief.md` | Gemini handoff |
| `docs/adr/ADR-0242-*.md` | Draft after P5/P4 design acceptance |

### Modify
| Path | Purpose |
|------|---------|
| `vault/store.py` | Public versor/entry read ABI |
| `core/physics/holographic_vault.py` | Drop `_versors`; I-02 reload path |
| `core/physics/wave_manifold.py` | Reconstruct, packing hooks, phase correlation, residual samples |
| `core/physics/biography.py` | I-01 durable reconstruct path (ledger/holographic) |
| `core/physics/goldtether.py` | κ search integration surface (eval-only by default) |
| `core/physics/energy.py` | Crystallization Trace B; optional Fibonacci τ schedule |
| `core/physics/self_authorship.py` | I-03 pins vs holographic COHERENT |
| `core/physics/surprise.py` / `dynamic_manifold.py` | Remain delegates; polar upgrade post-P7 |
| `tests/test_architectural_invariants.py` | Containment + INV-21 + grep-like hygiene |
| `docs/adr/ADR-0241-...md` | Entity traces + I-* cross-links; honest status |
| `docs/research/third-door-blueprint-fidelity.md` | Cohesion rows; demote thin 🟢 |
| `CLAIMS.md`, `docs/specs/runtime_contracts.md` | After pins hold |

### Reuse
| Primitive | Path |
|-----------|------|
| Algebra product / reverse / scalar | `algebra/cl41.py` |
| `cga_inner`, null points | `algebra/cga.py`, `algebra/null_point.py` |
| Versor residual / apply / condition | `algebra/versor.py` |
| Holonomy encode | `algebra/holonomy.py` |
| Metric project / leakage | `wave_manifold._metric_project` |
| VaultStore.store / iter_metadata | `vault/store.py` |
| EpistemicStatus | `teaching.epistemic` |
| Trajectory energy bound | `trajectory_invariants.py` |
| Existing ADR-0241 tests | `tests/test_adr_0241_*.py` |
| Rust surfaces | `core-rs/src/{cl41,diffusion,versor,vault,lib}.rs` |

---

## Package detail

### P0 — Land cohesion plan + Phase 0 (mandatory first)

1. Copy/normalize Downloads master plan → `docs/analysis/core_cohesion_master_plan.md` (fix escaped LaTeX/markdown; keep meaning).  
2. Cross-link from ADR-0241, deprecation plan, fidelity ledger.  
3. Execute **A-01…A-04** as a written checklist artifact in `docs/audit/` or test-pinned notes:  
   - **A-01** branch parity (this worktree vs `main` / third-door branches)  
   - **A-02** WaveManifold bindings present in `dynamic_manifold.py` / `surprise.py`  
   - **A-03** no Euclidean-only projection as truth in active invariant tests (metric-exact already pinned for leakage; extend scan)  
   - **A-04** serve-path quarantine for wave **and** Fibonacci  
4. Pre-deprecation grep as **automated test** (not manual one-off):
   - no `import core_ha` / `from core_ha`
   - no `hyperbolic_primitives`
   - flag bare `poincare` / Poincaré **runtime** fixtures (construction-lift tests may whitelist)
5. Honesty pass on fidelity §12: mark thin polar/chiral/atlas-packing as 🟡 until P4/P7/P8.

**Agents:** orchestrator + `doc-updater`.  
**Adversarial audit:** skeptic — every prior 🟢 must map to either entity invariant or local pin.

**Exit:** cohesion plan in-repo; Phase 0 suite green.

---

### P1 — Trust hardening

1. **Public VaultStore read ABI**; remove `holographic_vault` private `_versors`.  
2. **Serve containment** AST/import tests: `chat/runtime.py` (and wrong=0 serve entry) must not import `wave_manifold`, `holographic_vault`, or future `fibonacci_search` / `atlas_packing`.  
3. **I-03 pin:** self-authorship + holographic path cannot write COHERENT without explicit review gate; SPECULATIVE only.  
4. COHERENT seal remains non-self-authorizing; document ADR-0092 still deferred.  
5. Dual residual checks stay fail-closed (I-05 local).

**Agents:** `tdd-guide` → implement → `security-reviewer` + `python-reviewer` → adversarial `code-reviewer`.

**Exit:** restart holographic tests green without private ABI; containment + I-03 green.

---

### P2 — Entity invariant suite (definition of cohesion)

Implement `tests/test_third_door_cohesion.py` (and/or dedicated entity file) with **deterministic** fixtures (reject random-norm sketch as authority):

| Test | Invariant |
|------|-----------|
| Biography holonomy closed + reconstruct after vault-backed mode reload | I-01 |
| Seal ψ₁ SPECULATIVE → reload spectrum → \(\\|\psi_2-\psi_1\\|_F < 10^{-12}\) (float64 path; document float32 store policy if dtype differs) | I-02 |
| Self-authorship / miner cannot COHERENT-seal holographic modes | I-03 |
| Phase-correlation API rejects cosine path; algebraic symmetry pin | I-04 (stub until P6 full multimodal) |
| Schrödinger/sandwich step residual < 1e-6 dual-checked | I-05 |
| `core_ha` import raises / find_spec None | Deprecation |
| Fibonacci search stub xfail until P5 | ADR-0242 placeholder |

**Float32 note:** VaultStore may store float32; I-02’s \(10^{-12}\) may require float64 path or a dual tolerance (float64 exact / float32 ≤ 1e-6). Pin **honestly** — do not fake bit-identity across dtype cast.

**Agents:** `tdd-guide` → implement missing glue only → `code-reviewer`.

**Exit:** entity suite exists and fails closed on regressions; I-02 dtype policy documented.

---

### P3 — Superposition reconstruction

Realize \(\hat\psi = \sum_k c_k \psi_k\) from reverse-product overlaps (not only argmax).

- RED: partial-combo query reconstructs closer to combo than pure modes.  
- Empty refuse preserved.  
- Keep `resonant_recall` as lock-in index API for biography compatibility.

**Exit:** W5 upgraded from argmax-only to interference-capable.

---

### P4 — Hyperbolic Atlas packing (Golden-Angle)  

**STOP → Antigravity/Gemini brief:** `docs/briefs/ADR-0242-atlas-packing-and-fibonacci-brief.md` (section A).

Must specify:
1. Lift of Golden Angle \(\theta_k = 2\pi k\phi^{-1}\), \(r_k=\tanh(\alpha\sqrt{k})\) into **Cl(4,1) horosphere points** (null vectors / CGA), without making Poincaré runtime truth (ADR-0003).  
2. Geodesic separation metric on horosphere and fail if \(d_{\min}<0.12\).  
3. Insertion cost measurement only in `evals/` / `calibration/` (R-04).  
4. How modes register into `WaveManifold` / holographic vault.  
5. Non-goals: resurrecting `core_ha` package, node IDs, thaw coordinates.

**After design return:** TDD allocator + rejection threshold + packing determinism.

**Exit:** packing pins green; insertion-cost benchmark in evals quarantine.

---

### P5 — Fibonacci section search + GoldTether κ (ADR-0242 slice)

**STOP → same Gemini brief (section B)** or resume from P4 brief.

1. `core/physics/fibonacci_search.py`: `BoundedUnimodalObjective`, `fibonacci_section_search`, certificate/trace (eval sequence length = budget).  
2. Integration test: minimize synthetic unimodal residual for κ (cohesion sketch, deterministic).  
3. Optional later: real Procrustes residual line search under fixed N evals (Fidelity Score metric).  
4. **Never** import into `chat/runtime.py` (A-04).  
5. Unimodality violation → fail-closed (cohesion §4.2).  
6. Draft **ADR-0242** from Fibonacci + packing decisions.

**Exit:** cohesion Fibonacci test green; ADR-0242 draft ready for review.

---

### P6 — Multimodal phase correlation (I-04)

Implement pure algebra helper:

\[
\rho(\psi_A,\psi_B)=\langle \psi_A\widetilde{\psi}_B + \psi_B\widetilde{\psi}_A\rangle_0
\]

1. On `WaveManifold` (or `wave_resonance.py`).  
2. Tests: symmetry, no cosine imports, deterministic.  
3. Thin adapter at sensorium boundary for text/audio/vision/motor **ψ packets** if already compilable; else pin operator + fake multimodal vectors until sensorium compilers feed real packets.  
4. Forbidden: sklearn neighbors, faiss, cosine ranking as truth.

**Exit:** I-04 fully behavioral (not stub).

---

### P7 — True \(\mathcal{C}_{AB}\) + Clifford polar  

**STOP → Gemini brief** `docs/briefs/ADR-0241-cross-spectral-polar-brief.md`.

Same bar as prior plan: algebra-native only; tests that thin wrap fails; `wave_analogical_polar` becomes truth; Procrustes field path delegates.

---

### P8 — Non-vacuous chiral  

**STOP → Gemini brief** `docs/briefs/ADR-0241-chiral-spinor-brief.md`.

Preserve even-versor honesty (#19); spinor path informative conserved Q; Trace B topological charge real.

---

### P9 — Contemplation / teaching seam (Trace A)

1. Contemplation or sealed-practice path may **SPECULATIVE-seal** standing-wave modes.  
2. Proposals only; teaching corridor for COHERENT.  
3. Resonant reconstruct available as hypothesis, never as evidence without `min_status=COHERENT`.  
4. Serve still quarantined.

**Agents:** `architect` for seam choice → `tdd-guide` → `security-reviewer`.

---

### P10 — Energy boundary + multi-scale τ (Trace B)

1. Wire wave unitary residual into energy / trajectory boundary checks.  
2. Optional \(\tau_n = F_n \tau_0\) recency hierarchy (Fibonacci memo §4) as **constants table**, not dogma.  
3. Crystallization E0–E1 → vault candidate aligns with holographic seal policy.

---

### P11 — Rust / mechanical sympathy

Only after Python math authority for exp residual:

| Binding | Role |
|---------|------|
| `cl41::wedge` | Exterior product / PCA blades |
| `diffusion.rs::expm` | Unitarity-aware \(R=\exp(B\Delta t)\) |
| `versor_unit_residual` | SIMD GoldTether residual |

Parity tests: Rust == Python within tol; no scipy truth.  
**Hand off optional** to Antigravity for Rust micro-optim if Python contracts frozen.

---

### P12 — Governance close

1. CLAIMS pins for I-01…I-05 (or subset landed).  
2. `runtime_contracts.md`: off-serve wave + SPECULATIVE holographic kind + Fibonacci quarantine.  
3. ADR-0241 → Accepted path after Joshua review.  
4. ADR-0242 draft → Proposed.  
5. Fidelity ledger truth.  
6. Cohesion checklist boxes I-* and A-* reflected as tests, not prose.

---

## Antigravity / Gemini mandatory stop-points

| When | Brief | Resume when |
|------|-------|-------------|
| Before P4/P5 | `docs/briefs/ADR-0242-atlas-packing-and-fibonacci-brief.md` | Horosphere lift + d_min + Fibonacci search contracts review-passed |
| Before P7 | `docs/briefs/ADR-0241-cross-spectral-polar-brief.md` | Algebra-native polar design; thin-wrap-failing RED tests listed |
| Before P8 | `docs/briefs/ADR-0241-chiral-spinor-brief.md` | Non-vacuous spinor Q without reviving #19 |
| Optional P11 | Rust expm/residual micro-arch brief | Python parity suite frozen |

Each brief must include: ADR citations, AGENTS.md invariant compliance, non-goals, RED tests current code cannot pass, numerical thresholds from cohesion plan.

---

## Agent orchestration

```text
Orchestrator
  P0  docs + Phase 0 automation
  P1  tdd → impl → security + python review → adversarial code-review
  P2  tdd entity suite → impl glue → adversarial
  P3  tdd reconstruct → impl → review
  ⏸  Gemini: atlas packing + Fibonacci (P4/P5)
  P4–P5 implement after design
  P6  multimodal ρ
  ⏸  Gemini: polar (P7)
  ⏸  Gemini: chiral (P8)
  P9  cognition seam (architect + security)
  P10 energy
  P11 rust (optional Antigravity)
  P12 governance + human Joshua acceptance
```

**Adversarial review after every package:**  
(1) namesake-green? (2) entity invariant covered? (3) serve quarantine held? (4) docs/ledger/code agree?

---

## Success definition

### Cohesion-complete (dual-ADR branch minimum)

| # | Criterion |
|---|-----------|
| C0 | Cohesion master plan in-repo; Phase 0 A-01…A-04 automated/pinned |
| C1 | I-01…I-05 suite green under honest tolerances |
| C2 | Vault public ABI; no private `_versors` |
| C3 | Serve + Fibonacci quarantine AST-green |
| C4 | Superposition reconstruct behavioral pins |
| C5 | Multimodal ρ operator (I-04) green |
| C6 | Contemplation SPECULATIVE holographic seam (Trace A) without serve |
| C7 | Pre-deprecation grep CI-green |
| C8 | CLAIMS + runtime_contracts + ADR-0241 acceptance path |

### Absolute mastery

All of the above **plus**: Golden-Angle packing \(d_{\min}\); Fibonacci κ search + ADR-0242 draft; true polar; non-vacuous chiral; energy boundary; optional Rust parity.

### Explicit non-goals for “complete”

- Wiring wave/Fibonacci into wrong=0 serve  
- Resurrecting `core_ha`  
- Cosine/ANN multimodal matching  
- Hot-path silent unitize “nearest versor” repair (reject R-01 as written; use fail-closed)  
- Claiming continuous \(\psi(X,t)\) continuum solver before packing+modes give progressive field semantics  

---

## Verification lanes

```bash
# Phase 0 / hygiene
python3 -m pytest tests/test_third_door_cohesion.py tests/test_adr_0241_*.py -q
python3 -m pytest tests/test_architectural_invariants.py -q -k "INV21 or vault or wave or holographic or core_ha or poincare"

# Third-Door regression
python3 -m pytest tests/test_adr_0238*.py tests/test_adr_0239*.py tests/test_adr_0240*.py tests/test_third_door*.py -q

# Broader
core test --suite algebra -q
core test --suite runtime -q
core test --suite smoke -q
```

**Quantifiable thresholds (from cohesion plan, adjusted for honesty):**

| Metric | Threshold |
|--------|-----------|
| Unitary residual (I-05) | \(< 10^{-6}\) |
| Vault round-trip float64 (I-02) | \(< 10^{-12}\) (or documented float32 ≤ 1e-6) |
| Biography closure (I-01) | `versor_condition < 1e-6` post-reboot reconstruct |
| Horosphere packing (P4) | pairwise geodesic \(\ge 0.12\) or reject |
| Fibonacci search (P5) | best point within 1e-3 of known unimodal min; eval count = budget |
| Phase correlation (I-04) | algebraic identity pins; no banned imports |
| Serve imports | zero illegal modules |

---

## Execution order after plan approval

1. P0 land cohesion plan + Phase 0 automation  
2. P1 trust ABI + quarantine  
3. P2 entity suite (RED → GREEN)  
4. P3 reconstruct  
5. **STOP:** emit ADR-0242 packing+Fibonacci brief to Antigravity/Gemini  
6. P6 multimodal ρ (can parallel while Gemini works)  
7. On brief return → P4 packing, P5 Fibonacci + draft ADR-0242  
8. **STOP:** polar brief → P7  
9. **STOP:** chiral brief → P8  
10. P9 Trace A seam  
11. P10 energy  
12. P11 Rust only if needed  
13. P12 governance + Joshua acceptance
