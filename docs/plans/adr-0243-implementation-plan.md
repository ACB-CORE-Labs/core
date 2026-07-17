# ADR-0243 Implementation Plan — Wave-Field Cognitive Lifecycle

**Status**: Approved by Shay 2026-07-16 (plan-of-record for the 0243 arc)
**Authority docs**: `docs/adr/ADR-0243-wave-field-cognitive-lifecycle-comprehension-reasoning-and-resonant-learning.md` (Proposed), `docs/analysis/core_cohesion_master_plan.md` (canonical, doctrine-annotated)
**Related**: ADR-0006, ADR-0055, ADR-0145, ADR-0238, ADR-0239, ADR-0240, ADR-0241, ADR-0242
**Prior-arc record**: `docs/plans/adr-0241-0242-mastery-close-status.md`

---

## 1. Inputs carried from the ADR-0241/0242 close audit (2026-07-16)

The independent audit of PR #55 confirmed the 0241/0242 close as genuine, with three
seam-vs-integration caveats that this arc must resolve or consciously inherit:

1. **D9 "f64 GP parity" is a Python-SOT freeze, not cross-implementation parity.**
   No Rust f64 geometric product exists. All f64 wave-field math stays in Python
   until a `geometric_product_f64` PyO3 export is built *and* parity-gated.
   Consequence here: the ADR-0243 relaxer is pure-Python f64 by doctrine, and the
   master plan's §5 Rust bindings are **deferred** (see §7 below).
2. **The ADR-0242 §5 carry seams have zero live call sites.** `kappa_search_event`
   (goldtether) and `cross_band_discovery_gate` (multi_scale_energy) are tested
   primitives that nothing live invokes. Phase 3 Lane A wires them.
3. **The I-04 real-compiler sensorium feed is test-only** (correct per A-04
   quarantine) and the audio versor is float32-origin upcast to f64. Phase 3
   Lane B gives the feed its first (off-serving) consumer.

## 2. Substrate inventory — what exists vs. what this arc builds

Already landed (verified on `main` @ `19819194`):

| Lifecycle stage | Existing organ |
| --- | --- |
| §2.1 ingress superposition | `core/physics/sensorium_wave_feed.py` (`ModalityPacket`, `compile_packet_to_psi`, `superpose_packets`, `phase_correlate`) |
| §2.1 resonant projection R_k | `WaveManifold.phase_correlation` / `resonant_recall` / `resonant_reconstruct` |
| §2.3 energy classes E0–E4 | `core/physics/energy.py` (`EnergyClass`, `FieldEnergyOperator`; ADR-0006) |
| §2.3 readback rules | `packs/en/readback_rules.py` (ADR-0145 energy-modulated readback) |
| §2.3 GoldTether residual | `core/physics/goldtether.py` (`coherence_residual`, `GoldTetherMonitor`) + `WaveManifold.measure_unitary_residual` |
| §2.4 surprise + γ check | `core/physics/surprise.py` (`surprise_residual`, `is_discovery_eligible`, `dual_operator`; ADR-0239) |
| §2.4 discovery plumbing | `core/contemplation/runner.py` already accepts a `DiscoveryCandidateSink`; `teaching/discovery.py` `DiscoveryCandidate` (ADR-0055 Phase B) |
| §2.4 self-authorship | `core/physics/self_authorship.py` (`SelfAuthorshipMiner`, I-03 pinned speculative-only) |
| §2.5 biography holonomy | `core/physics/biography.py` (`integrate_biography`, `reconstruct_biography`) — **no live call sites yet** |
| I-01…I-05, A-02/A-04, `core_ha` absence | `tests/test_third_door_cohesion.py` (master plan §3/§8 already pinned; §7 `core_ha` migration is **moot** — package absent and test-pinned) |

Genuinely unbuilt: the §2.2 relaxation reasoner (`cognitive_lifecycle.py`), the
inter-organ wiring (three lanes), and the §4 falsifiability benchmarks.

## 3. Sketch-defect ledger (ADR §3 reference prototype)

Pinned executable in `tests/test_adr_0243_sketch_defect_pins.py`; the reference
prototype must **never** be ported verbatim (precedent: PR #52 sketch-defect pins).

- **SD-A — the sketch egress gate always rejects.** It computes
  `drift = |ψᵀIᵀψ − 1|` with `I` antisymmetric; `ψᵀIᵀψ ≡ 0` identically, so
  `drift ≡ 1 > ε` for *every* state, valid or not. A fail-always gate is the
  inverse of a hollow gate and equally worthless. The real residual already
  exists: `WaveManifold.measure_unitary_residual` / `goldtether.coherence_residual`.
- **SD-B — the sketch "relaxation" cannot relax.** Iterating
  `R = expm(H·I·dt)` with renormalization does not settle into the minimum-energy
  eigenmode: the generator's spectrum is (block-wise) purely imaginary, so the
  iterates oscillate and preserve mode magnitudes; nothing dissipates. Relaxation
  to the ground state requires the **dissipative (imaginary-time) semigroup**
  `ψ ← normalize(exp(−H·dt)·ψ)` — deterministic power iteration converging at a
  rate set by the spectral gap of H.
- **SD-C — the sketch's block matrix "I" is not the Cl(4,1) pseudoscalar action.**
  It shares the property I² = −Id but is a different operator from
  left-multiplication by e₀e₁e₂e₃e₄ in the real algebra. All algebra goes
  through `algebra/` — no bespoke component-shuffling proxies.

## 4. Deviations ledger (implementation vs. ADR prose — for the acceptance packet)

- **D-1 imaginary-time relaxer** replaces the sketch's `exp(H·I·t)` loop (SD-B).
  Implemented via `np.linalg.eigh` on symmetric H: `exp(−H·dt) = Q·exp(−Λ·dt)·Qᵀ`,
  pure numpy f64, no scipy dependency added.
- **D-2 honest guarantee restatement.** The ADR's "mathematically guaranteed …
  zero room for intermediate fabrication" is conditional: it holds only insofar
  as (a) the Hamiltonian compiler encodes the constraints faithfully, (b) the
  ground state is separated by a positive spectral gap, and (c) the iteration has
  converged (certified, not assumed). The acceptance packet states it this way.
- **D-3 I-05 reconciliation.** Relaxation is *deliberately non-unitary* inside
  the off-serving solver — that is what dissipation is. I-05 (amplitude
  conservation) governs live serve-path transitions; the relaxer's terminal
  normalize is an **owned construction boundary** per the master plan's
  doctrine note (no hot-path drift repair; breaches at the boundary fail closed).
- **D-4 R-02 premise retired at v1 scale.** `expm` of a 32×32 symmetric matrix
  in numpy is trivial; no Rust port is needed or permitted (caveat 1) for v1.
- **D-5 E0/E1 crystallization is proposal-only.** No vault writes from the
  lifecycle; cold states emit a typed crystallization *proposal artifact*
  through the one-mutation-path (I-03), never a direct `COHERENT` write.

## 5. Phases

- **Phase 0 — Governance + doc hygiene** (this PR): commit ADR-0243 verbatim as
  Proposed; sketch-defect pins; `*.gdoc` gitignored; stale prior-arc status line
  fixed; this plan committed. Local strays (research-copy duplicates,
  `core-rs/uv.lock`) removed from the working tree.
- **Phase 1 — merged into Phase 0** (pins land with the plan).
- **Phase 2 — flagship `core/physics/cognitive_lifecycle.py`** (1 PR): Tier-2
  off-serving (A-04 list + lazy barrel + transitive guard). Typed
  content-addressed `ProblemHamiltonian` compiler for two checkable domains only
  (propositional penalty projectors; convex quadratic). Imaginary-time relaxer
  (D-1) with convergence certificate (eigen-residual + gap estimate) and typed
  fail-closed errors. Egress verdict composing `measure_unitary_residual` +
  `coherence_residual` + `EnergyClass` routing (E0/E1 → proposal artifact per
  D-5; E3/E4 → readback-eligible). Ingress delegates to `sensorium_wave_feed` /
  `WaveManifold` — no duplication. TDD; ground-state property test vs. direct
  eigensolve; determinism digests.
  - *Phase 2 verification record:* adversarial finder/verifier workflow over
    the module (most verify agents were lost to a session limit; every
    surviving finding was reproduced in-tree before acting). Two hardenings
    landed beyond the plan text: (1) `RelaxationCertificate.psi_digest` binds
    convergence evidence to the exact certified state and `egress_gate`
    refuses borrowed certificates (`certificate_state_mismatch`) — closes a
    false-provenance `CrystallizationProposal`; (2) certification additionally
    requires the spectral gap be resolvable at the requested tolerance
    (excited weight ≤ (E−λ0)/gap ≤ tol, refusal
    `spectral_gap_below_tolerance`), and the degeneracy cluster is capped at
    the acceptance window so the certificate reports the honest rate-limiting
    gap — closes a zero-ground-overlap mis-certification reachable at loose
    `tol`. Dense-branch refusals, the E2 hold route, iterate-collapse, and
    hardcoded canonical entailment verdicts are pinned in tests.
- **Phase 3 — wiring lanes** (three independent PRs after Phase 2 API lands):
  - **Lane A (§2.4; closes caveat 2):** wire `is_discovery_eligible` +
    `cross_band_discovery_gate` into the contemplation runner's existing sink;
    high-surprise speculative packets emit `DiscoveryCandidate`s
    (proposal-only). Give `kappa_search_event` its live telemetry call site at
    the κ line-search (calibration-gated per R-04).
  - **Lane B (§2.1→§2.3; closes caveat 3):** off-serving corridor in `evals/`:
    real Audio/Vision compilers → ψ_in → relaxation → E-class → `en` readback
    rules → GoldTether gate. First live consumer of the I-04 feed.
  - **Lane C (§2.5):** ADR-0240 validation-harness PASS →
    `integrate_biography`, with I-01 closure asserts and provenance recording.
- **Phase 4 — falsifiability benchmarks** (1 PR):
  `evals/adr_0243_cognitive_lifecycle/` fixed-replay eval
  (`adr_0242_v2_energy_compare` pattern): fidelity score, surprise separation
  (ID vs OOD), insertion cost, f32 drift over T=1000, typed failure thresholds.
  **Decisive falsifier:** a propositional slice scored against
  `evals/deductive_logic` ROBDD gold with wrong=0 accounting. "Field engine is
  NOT the reasoner today" stands unless this evidence says otherwise.
- **Phase 5 — acceptance packet** (1 PR): D10-pattern packet — claims vs.
  evidence, deviations D-1…D-5, deferred items — for Joshua's ruling. Status
  flip via governance commit only (provenance-guard compliant).

## 6. Dependencies and process

Phase 2 precedes 3/4; Lanes A/B/C are mutually independent; Phase 5 last.
Every PR: dedicated worktree off `forgejo/main`, in-worktree smoke gate
(`uv run core test --suite smoke -q`) before push, `[Verification]:` line in the
PR description, Forgejo MCP for PR operations (no `gh`, no `tea`), stacked
merges substrate-first, merged branches + worktrees deleted immediately.
Lane briefs for Phase 3 are written at Phase 2 completion (production-line
pattern, `docs/handoff/`); dispatch is Shay's call.

## 7. Explicitly deferred (not in this arc)

- Master plan §5 Rust bindings (`cl41::wedge` exists; `expm`/`versor_unit_residual`
  SIMD do not) — blocked on a Rust f64 GP + D9-style parity gate (caveat 1).
- MLX / Apple-UMA lanes — aspirational prose; no benchmark evidence.
- Delta-CRDT multi-writer vault — behind the multi-writer gate (PR #42 ruling).
- `he`/`el` readback rules — packs are skeletal; `en` only for the corridor.
- Any serve-path activation of lifecycle machinery — A-04 quarantine holds
  until ratification.

## 8. Risks

- **H-compiler scope explosion** → v1 fixed at two typed domains; extensions
  require new evidence, not new matchers (ADR-0175 discipline).
- **Reasoner overclaim / thesis drift** → the Phase 4 wrong=0 ROBDD cross-check
  is the gate; disagreements fail the run and go in the packet verbatim.
- **Hollow gates in egress wiring** → every gate ships with a must-reject test
  (and SD-A shows the dual failure mode: a gate that rejects everything).
- **I-05 doctrinal tension** → D-3 reconciliation text; normalize only at the
  owned construction boundary; boundary breaches fail closed, never repaired.
