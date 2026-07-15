# ADR-0241/0242 + core_ha + Fibonacci — Blueprint↔Codebase Integration Plan

**Purpose:** audit **all four authority blueprints** against the current codebase and plan how each mechanism is masterfully worked into the implemented design — retiring or re-shaping old work that doesn't fit the R&D vision **without ever losing the capability it provided**.
**Author:** Claude (fresh-eyes). **Date:** 2026-07-15. **Base:** `feat/adr-0241-0242-mastery-close` off `forgejo/main @ 4853a55c`.
**Companion:** `adr-0241-0242-adversarial-and-fidelity-findings.md` (the W1 hostile-verification results this plan builds on).

**Authority docs & availability:**
| Doc | Read | Status |
|---|---|---|
| ADR-0241 wave-field hyperbolic atlas + resonant cognition | ✅ full | audited deep |
| core_ha unification & deprecation plan | ✅ full | audited |
| fibonacci_applications_in_core_substrate | ✅ full | audited |
| ADR-0242 deterministic-fibonacci-operators + evidence-gated-optimization | ✅ full (read 2026-07-15 via Drive connector; committed copy at `docs/research/ADR-0242-deterministic-fibonacci-operators-and-evidence-gated-optimization.md`) | **slice CLOSED** — no new defects; see acceptance-packet addendum |

---

## 1. The governing reconciliation

The recurring pattern across all four docs: the blueprints were written when the **wave-field was speculative**, so they hedged it as "off-serving / separate database / optional." The implementation then made the wave substrate **load-bearing** (Third-Door serve operators delegate to it). Where an old boundary or claim no longer fits, we **retire it and re-develop the capability in the shape the R&D actually validated** — matching your "field = electricity" principle: the field is the substrate everything runs on.

**Already landed this session (first instance):** the serve-quarantine reconciliation — one substrate, two tiers (T1 sanctioned serve = `wave_manifold`; T2 evidence-gated off-serving = holographic vault, Fibonacci/energy research). De-barreled `core/physics/__init__.py`, added the transitive `sys.modules` guard, corrected A-04 + ledger. 179 affected tests green.

---

## 2. Per-mechanism disposition (every clause, 5 buckets)

### ✅ FAITHFUL — built and verified
| Blueprint clause | Landed | Evidence |
|---|---|---|
| ADR-0241 §2 ψ transport (sandwich + left-spinor) | `wave_manifold.sandwich_step`/`left_spinor_step` | unitary residual <1e-6, determinism pinned |
| §2.4B surprise = non-resonant spectral leakage | `compute_spectral_leakage` (metric-exact) | delegates from `surprise_residual` |
| §2.4C chiral grade-5 charge (readout) | `chiral_charge` | **Q=−2.5 non-vacuous, conserved exactly** (executed) |
| §2.4D GoldTether unitary residual | `measure_unitary_residual` | dual-checked ‖ψψ̃−1‖ |
| §2.2 holographic recall / standing-wave spectrum | `resonant_recall`/`resonant_reconstruct` + `HolographicVaultStore` | I-01/I-02 suite |
| core_ha runtime_memory → Field Energy E0–E1 deep / E2–E3 active | `energy.py EnergyClass` | E0/E1 `is_deep` ✓ |
| core_ha steward → GoldTether drift gating | `goldtether.py` | ✓ |
| core_ha §5.1 unitary <1e-6 fail-closed | `versor_condition`/`measure_unitary_residual` gates | behavior present |
| core_ha §5.3 Hamiltonian energy boundary `E_exertion ≤ κ·E_sensory` | `trajectory_invariants.energy_boundary_ok` | **exact, +refuses negative energy** |
| Fibonacci §2.1 golden-spiral phyllotaxis packing | `atlas_packing.golden_angle_pack` (`golden_angle_v1`, 137.5°) | V1/V3 |
| Fibonacci §2.3 evidence-gated section search | `fibonacci_section_search` → `FibonacciSearchCertificate` | **budget-exact + digest-stable** (executed) |
| Fibonacci §4 multi-scale `τ_n=F_n·τ_0` | `multi_scale_energy`, `wave_energy_boundary.fibonacci_tau_schedule` | V2 pins |

### 🟢 HONEST DEVIATION — the impl is *more correct than the blueprint*; keep, document for Joshua
| Blueprint said | Impl did | Why it's forward, not backward |
|---|---|---|
| §2.4A analogical = closed-form Clifford polar `C=RS` | numerical sandwich conjugacy (SVD+Spin-GN) | `test_true_clifford_polar_fails_on_multigrade_field` **proves** `~C C` non-scalar → analytic polar ill-posed for multigrade fields (P7; #19-RETIRE precedent). **Headline for ruling.** |
| §4 prototype `np.outer` + `la.svd` | exact `geometric_product`/`cga_inner` | rejects the blueprint's own Euclidean-matrix proxy |
| Fibonacci §2.3 "avoids division, addition-only" | uses `f_{n-1}/f_{n+1}` float division | the "no-division" micro-claim only holds on an integer lattice; real-bracket subdivision needs division. Dubious perf claim correctly filtered. |
| core_ha §5.1 `ClosureViolationException` (named) | `ValueError`/`WaveSpectralLeakageError` + versor gate | equivalent fail-closed behavior, different type name |
| §2.2 "exact recall / zero thaw loss" | float32-honest (I-02 tol 1e-6, not 1e-12) | honest about storage precision instead of over-claiming bit-exactness |

### 🔨 MISSING PIECE — capability the vision specifies but the code does **not** yet enforce; **build anew** so we don't go backwards
| Missing invariant | Current state | Build |
|---|---|---|
| **Chiral SIGN-preservation gate** (ADR-0241 §2.4C + core_ha §5.2: `sgn(∫⟨ψIψ̃⟩₀)=const`, mirror-inversion protection) | ✅ **BUILT** (`feat/chiral-sign-preservation-gate`, stacked on PR #40): `core/physics/chiral_gate.py` — `ChiralOrientationGate` latches `sgn(Q)` on the first non-vacuous reading, fails closed (`ChiralOrientationError`) on a materially re-emerging flip; wired at the enforcement point (`goldtether_residual` now feeds the *signed* charge to the gate; residual keeps magnitude semantics byte-identical). Even serve fields stay vacuous → inert on today's serve path (no #19 revival). Pins: `tests/test_chiral_orientation_gate.py` (7). | — (was: latch initial sign + fail closed on flip; wire signed charge) |
| **CRDT delta-sync semilattice** (core_ha §2/§3 tombstone → "commutative/associative/idempotent Delta-CRDT in `core/sync/`") | ✅ **RESOLVED by decision dossier** (`docs/analysis/crdt-vs-bitexact-determinism-decision-2026-07.md`, PR #42 merged `ccc42c18`): Python `core/sync/` is object-store only, but real Delta-CRDT semilattice machinery exists in `core-rs/src/vault.rs`, and `test_audio_crdt_merge.py` exercises genuine CRDT properties in that sub-domain. Ruling: single-writer bit-exact (`array_codec` + VaultStore) serves the one-continuous-life telos today; **CRDT rollout deferred behind an explicit multi-writer/multi-agent gate**. | — (Joshua ratification rides the acceptance packet) |

### ⛔ SCRAP / DO-NOT-BUILD — correctly rejected over-claims
| Blueprint clause | Disposition |
|---|---|
| Fibonacci §2.2 **anyons** "immune to float32 drift" | Most speculative claim in the corpus; **not built** (no package, no test). Correct call — "float32-immune topological logic" is an over-promise. **Action:** downgrade the ledger's `V5 anyons 🟢` row to "not built / claim-quarantined" (namesake-green, Finding #5). Revisit only if non-abelian braiding is explicitly greenlit. |

### 🕗 STAGED / GATED — deferred by design, not regression
- Rust wave kernels (bivector exp-map, `C_AB`, `versor_unit_residual`) in `core-rs/{lib,versor,diffusion,vault}.rs` — files exist; f64 GP parity **deferred (D9)**; Python is truth via `algebra.backend` (P11a).
- Sensorium §2.3 continuous multimodal — staged/fake packets + real ρ (`sensorium_wave_feed`); real compilers open.
- Continuous field integrals — mode samples today.
- T2 serve promotion — evidence-gated (ADR-0242 cert discipline).

---

## 3. Invariant preservation (your named guardrails)

| Requirement | Held? | How the reconciliation protects it |
|---|---|---|
| **Determinism** | ✅ | T1 wave ops closed-by-construction, no RNG; Fibonacci cert bit-stable; T2 gating = "evidence-gated optimization" (never promote without replayable cert). The one open item (CRDT vs bit-exact) is a *determinism-mechanism* clarification, not a hole. |
| **Safety + alignment** | ✅/🔨 | GoldTether stays the alignment gate on the real substrate (strengthened). **The missing chiral sign-gate is an alignment capability to restore** — mirror-orientation is part of "topologically secure alignment." Safety/ethics/refusal packs untouched. |
| **core_logos** | ✅ | Articulation layer above physics; unaffected by substrate boundary moves. |
| **Substrate goals: memory / logic-topology / thermodynamics** | ✅ | Memory = holographic vault (T2, persistence-gated). Logic-topology = Cl(4,1) ψ field promoted to live substrate (T1). Thermodynamics = `energy.py` + `energy_boundary_ok` (faithful) + gated multi-scale research (T2). |

---

## 4. Sequenced build plan (no capability regression)

1. **DONE** — Finding #2 serve-boundary reconciliation (de-barrel + transitive guard + A-04/ledger correction). Green.
2. **Next fix-forward (LOW, batch):** downgrade anyon ledger row; `EpistemicStatus` boundary note (or relocate to shared kernel); Fibonacci `minimizer` docstring; `ClosureViolationException` naming note.
3. **DONE** — chiral **sign-preservation gate** (§5.2) built TDD (RED→GREEN) on `feat/chiral-sign-preservation-gate`: gate primitive + goldtether wiring + 7 pins; 99 goldtether-consumer tests green.
4. **Decision + build/doc:** CRDT-vs-bit-exact determinism story for `core/sync` (affects multi-agent "one continuous life").
5. **Get ADR-0242 memo export** → close its fidelity slice (evidence-gated-optimization vs the cert impl; confirm no further deviations).
6. Staged/gated items (Rust parity D9, sensorium compilers, continuous integrals) remain post-Accept backlog.

**Acceptance framing:** ADR-0241/0242 are Accept-ready on the FAITHFUL + HONEST-DEVIATION set once #2 lands green (in progress). The MISSING-PIECE items (chiral sign-gate, CRDT clarification) are **new capability work**, not blockers — but they must be tracked so the vision's safeguards aren't quietly dropped.
