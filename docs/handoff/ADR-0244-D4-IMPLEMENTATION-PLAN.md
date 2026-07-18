# ADR-0244 D4 — Wave-Field Identity Manifold: Implementation Plan & Progress Tracker

**Owner:** Shay (sole worker on this arc) · **Authored:** 2026-07-17
**Arc base:** `main @ ee38c976` (== `forgejo/main`) · **Worktree:** `/Users/kaizenpro/Projects/core-adr0244d4` · **Branch:** `feat/adr-0244-d4`
**Companion ADRs:** [ADR-0244](../adr/ADR-0244-wave-field-identity-manifold-and-inalienable-geometric-alignment.md) (identity consumer) · **ADR-0245** (mechanical-sympathy + semantic-rigor foundation — *to be committed in Phase 0*)
**Prior audit:** [adr-0244-cohesion-directive-audit-2026-07-17.md](../analysis/adr-0244-cohesion-directive-audit-2026-07-17.md) · **Q_top proof:** `evals/adr_0244_qtop_vacuity/`

> **This document is the resume anchor.** It is committed to `main` and updated at every phase boundary. On a cold start: read §0 → §10 status dashboard → the first phase whose status is not ✅, then its Resume notes. Everything needed to continue is here; do not re-derive from the relays or Google-Drive docs (see §3 for why).

---

## 0. Purpose & how to resume

This is a **multi-phase, multi-commit arc** expected to span rate-limit interruptions. Progress is tracked two ways:
1. **This committed doc** (durable; survives new sessions) — the source of truth. §10 dashboard + per-phase Status/Resume notes.
2. The in-session harness task list (convenience; lost across sessions).

**Resume procedure:**
- `cd /Users/kaizenpro/Projects/core-adr0244d4` (create the worktree from `forgejo/main` if gone: see §8).
- Read §10 dashboard. Find the first phase not ✅ DONE. Read its **Resume notes**.
- Continue from there. Update Status + append to §9 Progress log at each phase boundary.

---

## 1. Scope: the two ADRs and what's already done

ADR-0244 is the **identity-layer consumer**; ADR-0245 is the **mechanical-sympathy + semantic-rigor foundation** it sits on. Measured against `main @ ee38c976`:

| ADR-0244 § | Mechanism | Status entering D4 |
|---|---|---|
| 2.1 | Gram-subspace identity projection | ❌ unbuilt (identity.py is legacy ADR-0010 heuristic) |
| 2.2 | Spectral-leakage **fail-closed** gate + `C_id` + `IdentityGateRefusal` | ❌ unbuilt as gate (call site exists at `chat/runtime.py:2679`, but **advisory** only) |
| 2.3 | `Q_top` topological charge | ✅ resolved → **retire from egress** (proven vacuous, `evals/adr_0244_qtop_vacuity`) |
| 2.4 | Bracketed-local Fibonacci search + `γ_id` calibration | ◐ search-honesty done (D3); calibration half unbuilt |
| 2.5 | Serving-boundary f64→f32 cast contract | ❌ unbuilt (== ADR-0245 §2.2; the one genuinely-absent seam) |
| 2.6 | Rust GP fast-path + parity gate | ✅ done (f32 pre-existing + f64 D2, bit-identical) |
| 2.7 | Full digests / no `default=str` / byte-order guard | ◐ hot-path done (D1); contemplation content-ids residual |
| 2.8 | `eigh` memoization | ✅ done (`_cached_eigh`, D2) |
| 2.9 | Low-discrepancy mode-centroid allocator | ✅ primitive built (`atlas_packing.py`); **adoption unwired** — needs routing |
| 2.10 | Fibonacci-word background scheduler | ✅ built + spec-satisfying (`fibonacci_word_schedule.py`); audit-confirm only |

| ADR-0245 § | Mechanism | Status entering D4 |
|---|---|---|
| 2.1 | PyO3 Rust `geometric_product` f32 fast-path | ✅ done (`algebra/backend.py`) |
| 2.2 | Gated f64→f32 serving boundary | ❌ unbuilt (== 0244 §2.5) |
| 2.3 | Semantic rigor in content addressing | ◐ hot-path done (D1); residual |
| 2.4 | `_cached_eigh` memoization | ✅ done |
| 3 | Acceptance gate (parity, ≥10× f32 speedup, 0-LAPACK-on-repeat, collision-resistance) | ◐ parity ✓, 0-LAPACK partial (`test_adr_0244_mechanical_sympathy.py`); f32-speedup + collision proofs **missing** |

**Net remaining build = ADR-0244 §2.1 + §2.2 (the identity gate rebuild), §2.4 calibration, §2.5/0245§2.2 cast, §2.7 residual, §2.9 wiring, + the ADR-0245 §3 gaps.**

---

## 2. Ratified decisions (LOCKED — Shay signed off 2026-07-17)

1. **Drop `∧ ΔQ_top = 0` from the §2.2 egress condition.** Proven vacuous (`Q_top ≡ 0` on every versor; hollow gate). Egress becomes `score ≥ threshold` (leakage-based). Scope the §2.3 conservation claim to versors only; keep `Q_top` as a diagnostic, never an admit condition.
2. **§2 governs §4.** §4's illustrative per-axis-resonance code is rewritten to the §2.1/2.2 Gram/leakage formulation. Remove the (formerly phantom) "ADR-0245" reference by pointing it at the **now-real** ADR-0245. Replace the bare `assert` byte-order guard with a typed guard.
3. **Commit ADR-0245 as a real companion ADR** (currently untracked in `~/Downloads`). Cross-link 0244 ↔ 0245.
4. **Grade-1 axis lift.** Pack `direction` vectors are **dim-3** (verified); lift them to Cl(4,1) 32-vectors by placing the 3 components at the grade-1 `e1/e2/e3` blade slots (NOT `embed_point`, which would make Gram a distance table). Orthonormal axes ⇒ `G = I`.
5. **Signed overlap** — never `abs()` the per-axis inner product; a large negative overlap is anti-alignment (opposition), tracked distinctly from orthogonality.
6. **Euclidean leakage norm** — `‖S_id‖` is the positive-definite coefficient-Euclidean norm `sqrt(Σ S_id[k]²)`, explicitly **not** the indefinite `⟨S_id, reverse(S_id)⟩₀` (which can be 0 for nonzero leakage under signature (+,+,+,+,−)). Projection geometry uses the indefinite metric Gram; leakage *magnitude* uses the Euclidean norm.
7. **Activate `boundary_ids`** — hard-boundary evaluation, currently dormant (`check()` iterates `value_axes` only).
8. **Frozen identity manifold** — axis eigenmodes are fixed at pack load and never mutated within a session. Biography holonomy (`H_bio ← H_bio·R`) accumulates **separately** and does not rewrite the identity subspace. This preserves inalienability-by-construction.
9. **Bounded, abstaining `C_id`** — the corrector may make a bounded corrective displacement toward the manifold; if it cannot recover alignment within the bound it **abstains** (emits `IdentityGateRefusal`, live params unchanged). It must NOT arbitrarily rewrite reasoning to force a low leakage score ("good-metric / bad-cognition" guard).
10. **Paraphrase-invariance is empirical, not automatic.** ADR wording reworded to: *"invariant under transformations that preserve the represented trajectory's identity-relevant field geometry; paraphrase robustness is measured across the encoder+propagation pipeline."* The eval must measure it, not assert it.

---

## 3. Ground-truth facts (code-verified against `main @ ee38c976`)

Verified by reading the tree, **not** the relays (which contain at least one hallucination — LanceDB — and a false "identity.py already refactored on the VM" claim; disk shows identity.py **unchanged legacy**).

- **Fact A — axes are R³ 3-vectors.** `packs/identity/default_general_v1.json` ships `direction` = dim-3 unit vectors; loader enforces `_DIRECTION_LEN`. §2.1 assumes 32-vector eigenmodes → requires the grade-1 lift (decision #4).
- **Fact B — two field surfaces, not one.** §2.2 gate runs on `result.final_state.F` (cognition-pipeline field, `chat/runtime.py:2679`). §2.5 `ψ_steady` cast lives in `core/physics/cognitive_lifecycle.py` (ADR-0243 lifecycle), which `chat/` + `core/cognition/` **do not import** (A-04 off-serve). The ADR conflates them; they are separate contracts in separate files.
- **Fact C — `final_state.F` is a VERSOR (operator), not a state vector** (`field/state.py` invariant `versor_condition(F) < 1e-6`). It is even-grade (grades 0,2,4) with **exactly zero grade-1 content** (verified). This makes §2.1/§2.2's literal "project ψ onto the grade-1 subspace" vacuous (`P_id(F)=0`, flags everything). Resolution (ratified 2026-07-17): **operator-preservation** — measure whether the versor preserves the value subspace via `F aᵢ F̃`. See ADR-0244 governance annotation item 12 + §4a. This is the D4 core-mechanism correction.
- **Advisory, not a gate.** Current identity_score feeds `_build_surface_context` (hedge/claim-strength, `runtime.py:2705`) + telemetry. `would_violate` is never called in runtime. §2.2 converts advisory → fail-closed = a **live-serving behavior change** (highest risk).
- **`psi_traj` is never populated.** `_make_trajectory_from_result` (`runtime.py:385`) builds from `result.trajectory or (result.final_state,)`; no `psi_traj` attr. The wave-field 32-vector *is* available as `final_state.F` (used by `versor_condition(result.final_state.F)`). Phase 2 must thread it.
- **`boundary_ids` dormant** — stored on the manifold, never evaluated (decision #7).
- **Filename drift** — ADR-0245 + relays reference `multimodal_lifecycle.py`; it does **not** exist. The real file is `cognitive_lifecycle.py`.
- **Surrounding substrate already present** — `wave_manifold.py`, `chiral_gate.py`, `trajectory_invariants.py`, `fibonacci_search.py`, `atlas_packing.py`, `fibonacci_word_schedule.py`. identity.py is the one unpromoted file.

---

## 4. Folded-in review considerations (from the external grounded critique)

All code-verified or sound; woven into the phases below.

1. Signed overlap (decision #5) → Phase 1/2.
2. Euclidean leakage norm (decision #6) → Phase 1.
3. Paraphrase-invariance empirical (decision #10) → Phase 0 wording + Phase 2 eval.
4. Bounded/abstaining `C_id` (decision #9) → Phase 2.
5. `boundary_ids` activation (decision #7) → Phase 2.
6. 5-layer inalienability framing (algebraic / runtime / pipeline / operational / semantic) → Phase 0 ADR rigor.
7. Richer identity verification suite: **ablation** (legacy-only vs wave-only vs dual — prove incremental detection value), fail-closed malformed-ψ (NaN / wrong-dim / nonfinite / missing-cert / stale-manifold), near-singular-Gram mode-basis, metamorphic, conservation → Phase 2/3.
8. `TurnEvent` telemetry: `psi_leakage_norm: float = 0.0`, `wave_mode_active: bool = False` → Phase 2.

---

## 5. Phase plan

Dependencies: `0 → {1, 4}` · `1 → 2 → 3` · `5 after 0` · `6 last`. Each phase = its own gated commit (in-worktree smoke → fast lane for code phases → push `feat/adr-0244-d4:main`, per Shay's direct-to-main authorization for this arc). No auto-merge.

### Phase 0 — Governance reconciliation (ADR edits, NO code)
**Objective:** make the spec self-consistent so nothing downstream is built on a contradiction.
**Files:** `docs/adr/ADR-0244-...md`, new `docs/adr/ADR-0245-cga-unification-mechanical-sympathy-and-semantic-rigor.md`, `docs/analysis/adr-0244-cohesion-directive-audit-2026-07-17.md`.
**Steps:**
- Commit ADR-0245 (from `~/Downloads/ADR-0245-*.md`) as **Proposed**; cross-link 0244↔0245; add a status map (0245 §2.1/2.4 done, §2.3 hot-path done, §2.2 open).
- ADR-0244 §2.2: drop `∧ ΔQ_top = 0`; scope §2.3 conservation to versors + cite the proof.
- ADR-0244 §2.1/§2.2: record signed overlap (#5), Euclidean leakage norm (#6), the leakage-ratio score `1 − ‖S_id‖/‖ψ‖`, grade-1 lift (#4); rewrite §4 to Gram/leakage; typed guards + `isfinite` (no bare `assert`); point the `ADR-0245` reference at the real ADR.
- Reword paraphrase-invariance (#10); add 5-layer inalienability framing (#6); label scripture by translation + math-as-analogy disclaimer; note `boundary_ids` activation + frozen-manifold decision + Fact A/B + filename drift.
- Update audit doc: mark Q4 (Q_top) + the §4-vs-§2 blocker RESOLVED; map 0245 status.
**Acceptance:** both ADRs internally consistent; no `ΔQ_top` egress conjunct; no phantom refs; no bare `assert` in normative code blocks; provenance-guard test still green (docs-only, status stays **Proposed** — flips happen in Phase 6).
**Gate:** smoke 176 (docs-only, but run it) + provenance/ADR pins.
**Status:** ✅ DONE — landed `ad37d03b`
**Resume notes:** ADR-0244 governance annotation expanded to 11 items (§4a added, supersedes §4, verbatim R&D body preserved). ADR-0245 committed Proposed at `docs/adr/ADR-0245-cga-unification-mechanical-sympathy-and-semantic-rigor.md` with its own governance annotation + status map. Audit doc wrinkles 1–2 + Q5 line updated to resolved. Gate: smoke 176 passed + provenance/ADR pins (governance_p12, topological_quarantine, third_door_cohesion) 30 passed. Both ADR status lines confirmed still `Proposed` (no flip). Phase 1's `lift_axis` spec confirmed against the real `algebra.cl41.basis_vector` helper (grade-1 lives at component indices 1–5; e1/e2/e3 = `basis_vector(0..2)`) — no further verification needed before Phase 1 starts.

### Phase 1 — §2.1 identity manifold primitive (OPERATOR-PRESERVATION, pure, off-path) — TDD
**Objective:** the metric-exact **operator-preservation** primitive, no runtime wiring. (§2.1/§2.2's literal "project ψ onto I" is vacuous — the trajectory `final_state.F` is a **versor/operator** (grades 0,2,4, zero grade-1); see ADR-0244 governance annotation item 12 + §4a. We measure whether the versor *preserves* the value subspace via `F aᵢ F̃`.)
**Files:** new `core/physics/identity_manifold.py` (keep `identity.py` as compat shell + dual-mode host, wired in Phase 2); `tests/test_adr_0244_identity_manifold.py`.
**Steps (implement §4a verbatim shape):**
- `lift_axis(direction3) → ψ_axis(32)`: grade-1 embedding via `algebra.cl41.basis_vector(0..2)` (e1/e2/e3, component indices 1/2/3). Value subspace `I` lives in spatial grade-1 where `⟨·,·⟩₀ = ` Euclidean ⇒ `G` positive-definite.
- `gram_matrix(axes) → G` (`G_ij = scalar_part(gp(ψ_i, reverse(ψ_j)))`), symmetric PD; `cond(G) > 1e5 → ManifoldConditioningError`.
- `subspace_project(x, axes, Ginv) → P_I(x) = Σ ψ_i (G⁻¹)_ij ⟨ψ_j, x⟩₀` (**signed** coeffs).
- `sandwich(R, x) = gp(gp(R,x), reverse(R))`; `euclidean_norm(s) = ‖s‖₂`.
- `axis_response(R, axes, Ginv) → (leakage[], self_align[])`: per axis `rot=sandwich(R,aᵢ)`, `leakage_i=euclidean_norm(rot − P_I(rot))` (subspace departure), `self_align_i=⟨aᵢ, rot⟩₀` (**signed** orientation). Both required, non-redundant.
**Acceptance (falsifiable, all empirically pre-verified):** orthonormal default pack ⇒ `G=I`; `subspace_project` idempotent (`P_I∘P_I = P_I` to 1e-12); identity versor ⇒ all `leakage≈0`, all `self_align≈+1`; rotor **within** value plane (e12) ⇒ `leakage≈0`; rotor tilting a value axis toward e4/e5 ⇒ `leakage>0` (e.g. e14 θ=0.5 → 0.28, boost e15 θ=0.5 → 0.29); π-rotor inverting a value axis (e1→−e1) ⇒ `leakage≈0` **but** `self_align≈−1`; near-parallel synthetic axes ⇒ `ManifoldConditioningError`. Deterministic (f64).
**Gate:** smoke + fast lane + new tests.
**Status:** ✅ DONE — landed `3c3d2c29`
**Resume notes:** Shipped `core/physics/identity_manifold.py` (`lift_axis`, `gram_matrix`+`ManifoldConditioningError`, `subspace_project`, `sandwich`, `euclidean_norm`, frozen `IdentityManifoldGeometry` with `.project`/`.axis_response`/`.leakage_rms`) + `tests/test_adr_0244_identity_manifold.py` (24 tests). Pure `algebra.cl41`, f64, deterministic; off-serve (serve-quarantine test confirms). Gate: 24 new + smoke 176 + fast lane 11863 passed/109 skipped. NOT yet wired into `identity.py` or the barrel — that's Phase 2.

### Phase 2 — §2.2 fail-closed gate + `C_id` + `boundary_ids` + telemetry + eval — TDD
**Objective:** convert advisory → fail-closed egress gate on `final_state.F`; wire in-path behind a flag.
**Files:** `core/physics/identity.py` (dual-mode `_axis_projection`/`check`, `IdentityGateRefusal`, `C_id`), `chat/runtime.py` (thread `final_state.F` as `psi_traj`; act on verdict behind config flag; `TurnEvent` fields), evals (`evals/adversarial_identity`, `teaching_injection_resistance`, `identity_divergence`), tests.
**Steps:**
- Dual-mode: `psi_traj` present → wave-field projection (Phase 1 primitive); absent → legacy ADR-0010 fallback (back-compat). `psi_traj` present but **malformed** (NaN/nonfinite/wrong-shape) → typed error, **never** silent legacy.
- Score = `1 − leakage_norm/‖ψ‖`; flagged if `< manifold.alignment_threshold`; deviation_axes from signed per-axis contributions (opposition ⇒ deviation).
- `boundary_ids` hard evaluation (design the violation predicate; likely ties to safety-pack boundaries — scope in-phase).
- `C_id`: bounded corrective displacement; abstain (`IdentityGateRefusal`, params unchanged) if unrecoverable.
- Wire `runtime.py:2679` as fail-closed **behind a config flag defaulting to current advisory behavior** until Phase 3 calibrates. Add `TurnEvent.psi_leakage_norm`, `wave_mode_active`.
**Acceptance:** all three identity eval suites still pass; the gate demonstrably catches the injections; ablation shows wave path adds detection value over legacy; fail-closed tests (NaN/dim/nonfinite/missing-cert/stale-manifold) never fall through permissively; `C_id` bounded + abstains on unrecoverable; byte-identity of non-identity turns preserved (flag default off).
**Gate:** smoke + fast lane + eval suites + new tests.
**Decomposition (sub-commits for clean checkpoints):** **2a** pure `identity.py` capability (dual-mode wave path + `IdentityGateRefusal` + boundary predicate + C_id) — no runtime change; **2b** runtime wiring behind `identity_wave_gate` flag + telemetry; **2c** eval suite (ablation / fail-closed / injection-catching).
**Key facts locked from recon:** `final_state.F` is the wave field (versor); `boundary_ids` = union of identity+safety(`no_identity_override`,…)+ethics IDs, so boundary activation is an intersection with the turn's `SafetyVerdict.violated_boundaries` ∪ `EthicsVerdict.violated_commitments` (available only AFTER the verdicts, ~`runtime.py:2740`, not at the `2679` identity call); `compute_trace_hash` excludes telemetry fields (replay-safe); the JSONL serializer is explicit `getattr` per field, so wave telemetry lives on `IdentityScore` and is emitted only when `wave_mode_active` (byte-identical when off); C_id v1 = admit-or-abstain (no silent correction). Deviation from the reviewer's `TurnEvent.psi_leakage_norm` suggestion: telemetry lives on `IdentityScore` instead (serializer already reads it; cleaner + byte-identity-preserving).
**Status:** ✅ DONE — 2a `1c7ea26e`, 2b `c7e2b3b6`, 2c `c0ff4720`.
**Resume notes:** Phase 2 landed in three gated sub-commits. **2a** (`1c7ea26e`): pure `identity.py` capability (dual-mode `check(..., *, wave_field=, violated_boundary_ids=)`, `_validate_wave_field` fail-closed, `_wave_field_score`, extended `IdentityScore`, `IdentityGateRefusal`, admit-or-abstain `conjugate_correct`, `would_violate` extended; 16 tests). **2b** (`c7e2b3b6`): runtime wiring behind `identity_wave_gate` flag (`core/config.py`) — `wave_field=final_state.F` at the identity check + post-verdict boundary supplement + geometric refusal fold in `chat/runtime.py`; wave telemetry in `chat/telemetry.py` (only when `wave_mode_active`). Integration fix: per-axis **normalization** in `identity_manifold.py` (boost/e5 versors break Euclidean-norm preservation) → leakage ∈ [0,1], self-align ∈ [−1,1]. Runtime test seeds state to reach main-path turns. **2c** (`c0ff4720`): `evals/adr_0244_identity_gate/` detection-value ablation — the wave gate separates a geometric-attack panel (tilts/boosts/inversions) from an aligned panel (all attacks flagged, all aligned admitted, margin > 0) and adds detection value 6-vs-0 over the geometry-blind legacy path; 6 tests + CLI. Gate: smoke 176 + fast lane 11883→11889/109. **Carried to Phase 3:** value axes are placeholders (e1/e2/e3); the gate discriminates the *designed geometric* attack signal, but whether *real paraphrased injections* induce such geometry through the live encoder is empirical (governance annotation item 6) — Phase 3 γ_id calibration over reference traces is where that is measured, and the flag stays OFF until it is evidenced.

### Phase 3 — §2.4 `γ_id` calibration
**Objective:** replace the hardcoded threshold with a certifiable, calibrated bound.
**Files:** calibration eval under `evals/`, uses `core/physics/fibonacci_search.py` (bracketed-local, already built); tests.
**Steps:** define a `BoundedUnimodalObjective` over reference traces (ID traces pass, adversarial fail); run the Fibonacci search; emit an audit-logged tuning certificate; pin the calibrated threshold; flip the Phase-2 flag on once evidenced.
**Acceptance:** calibrated threshold separates ID vs adversarial reference sets; certificate reproducible + deterministic; flag-on run keeps eval suites green.
**Gate:** smoke + fast lane + calibration tests.
**Status:** ✅ DONE — landed `323d61c5`. **The flag flip is NOT authorized (honest empirical finding); flag stays OFF.**
**Resume notes:** Shipped `evals/adr_0244_gamma_calibration/` (`run_gamma_calibration`, `calibrate_leakage_bound`, `leakage_separation_objective`, `collect_live_benign_leakages`, CLI) + `tests/test_adr_0244_gamma_calibration.py` (9 tests, 1 slow drift-guard). Pinned `identity._WAVE_LEAKAGE_BOUND = 0.2126624458513829` (cert `0079b5f201fbf616…`, objective `gamma_id_leakage` v1, budget 24, interval [0,1], sharpness 10) and **decoupled the wave path from `alignment_threshold`** (legacy path + hedge bands keep it; wave path now flags on `leakage_rms > _WAVE_LEAKAGE_BOUND`). The self-alignment floor stays 0.0 (geometric invariant, not calibrated).
  - **Two honest results, kept separate:** (1) the bracketed-local Fibonacci search **certifies** γ* separating the *geometric* attack signal — every in-subspace rotor admitted, every axis→e4/e5 tilt/boost flagged (inversions excluded from the leakage set — they're ~0-leakage, caught by the orientation floor); machinery validated + reproducible + deterministic. (2) **The same bound does NOT separate real live traffic.** Measured on the arc engine (`ChatRuntime`, wave flag on, 13 main-path benign turns): benign `final_state.F` leakage spans **0.14–0.81** (mean 0.55), self-alignment swings to **−0.52**; **12/13 benign turns would be false-refused at γ***, benign overlaps the attack range, and the **best achievable balanced error over all thresholds is 0.346**. No leakage bound gates live traffic without mass-refusing benign turns.
  - **Root cause (architectural gap, not an impl defect):** the shipped pack value axes (`truthfulness=e1`, `coherence=e2`, `reverence=e3`) are **nominal basis vectors, not the dynamically-preserved eigenmodes §2.1 presumes**. The current field evolution gives the identity subspace no dynamical anchoring, so an ordinary cognition versor rotates it freely. Closing this = making identity dynamically load-bearing = **the ADR-0246 induced-identity-action programme** (preflight brief already merged, `docs/briefs/ADR-0246-*`). The wave gate is therefore **validated, correctly flag-gated-off scaffolding**, not a live gate. A slow drift-guard test re-measures the live distribution and fails loudly if the engine ever starts preserving identity (→ re-calibrate + reconsider the flip). This resolves the last open question from §7 (`boundary_ids` predicate was Phase 2; the live-separation question was the real Phase-3 crux). The eval's CLI exit-0 means "certificate valid", explicitly **not** "flip the flag".

### Phase 4 — §2.5 / ADR-0245 §2.2 serving-boundary cast (lifecycle-internal, independent)
**Objective:** governed explicit f64→f32 cast at the certified lifecycle egress.
**Files:** `core/physics/cognitive_lifecycle.py` (cast `psi_steady`→f32 at the certified boundary), tests.
**Steps:** add the typed cast contract at the egress hand-off; precision-sufficiency + parity test; keep f64 inside relaxation/eigendecomp.
**Acceptance:** f32 cast only after certification; parity within documented f32 tolerance; f64 preserved upstream; determinism intact. Satisfies **both** 0244 §2.5 and 0245 §2.2.
**Gate:** smoke + fast lane + cast tests.
**Status:** ⬜ NOT STARTED (may run parallel to 1–3; sequence after 0)
**Resume notes:** —

### Phase 5 — §2.7 residual + §2.9 adoption + §2.10 audit + ADR-0245 §3 gate
**Objective:** finish semantic-rigor residuals, wire the allocator, close the 0245 acceptance gate.
**Files:** `core/contemplation/schema.py`, `plan_preflight.py`, `miners/articulation_quality.py` (full 256-bit digests + typed coercion); `core/physics/holographic_vault.py` (route standing-wave-mode centroid via `atlas_packing.golden_angle_pack`, or prove existing registration insertion-order-independent); new benchmark + collision tests.
**Steps:**
- §2.7: full-digest + typed-coercion the three contemplation content-id sites.
- §2.9: wire/verify the allocator into standing-wave-mode registration.
- §2.10: audit-confirm `fibonacci_word_schedule.py` satisfies the spec (no build).
- ADR-0245 §3: add f32 ≥10× speedup benchmark + `_content_id` collision-resistance proof (parity + 0-LAPACK already covered).
**Acceptance:** no truncated machine merge keys in contemplation content-ids; allocator insertion-order-independent + wired; 0245 §3 four assertions all green.
**Gate:** smoke + fast lane + new tests.
**Status:** ⬜ NOT STARTED
**Resume notes:** —

### Phase 6 — Close-out
**Objective:** acceptance packets + ratified status flips + memory + cleanup.
**Files:** `docs/audit/adr-0244-acceptance-packet-*.md`, `docs/audit/adr-0245-acceptance-packet-*.md`; ADR status flips; memory.
**Steps:** D10-pattern acceptance packets for **both** ADRs; **user-ratified** Proposed→Accepted flips (provenance guard: inline `**Accepted** — ratified by Joshua Shay <date>` + packet `## 8. RULING RECORD`); update memory; delete worktree + branch (merge-then-cleanup).
**Acceptance:** both packets complete; provenance-guard green; status flips only on explicit user ratification; worktree/branch swept.
**Gate:** smoke + provenance/ADR pins.
**Status:** ⬜ NOT STARTED
**Resume notes:** —

---

## 6. Out-of-scope backlog (do NOT build in D4)

Forward-looking mechanical-sympathy items from the critique — a separate optimization backlog, not ADR-0244/0245:
- SIMD 64-byte alignment of the Cl(4,1) array.
- Relaxation-propagator precompute cache.
- Columnar `TurnEvent` audit storage.
- `biography.py` holonomy versioned storage.
- Parallel Fibonacci branch exploration.

(Gap-3 psi_digest byte-order is **already** handled by D1's LE guard.)

---

## 7. Open questions

- ✅ **Q_top vacuity** — RESOLVED (proven, `evals/adr_0244_qtop_vacuity`).
- ✅ **§4-vs-§2 reconciliation** — RESOLVED (decision #2; §2 governs).
- ✅ **Identity-continuity (mutate vs frozen)** — RESOLVED (decision #8; frozen manifold).
- ⚠️ **`boundary_ids` violation predicate** — how a trajectory "violates" a stored boundary id is undefined; design in Phase 2 (likely ties to safety-pack boundaries).

---

## 8. Workflow & env notes

- **Worktree:** `/Users/kaizenpro/Projects/core-adr0244d4`, branch `feat/adr-0244-d4`, based on `ee38c976` (== forgejo/main). Recreate if gone: `git worktree add -b feat/adr-0244-d4 /Users/kaizenpro/Projects/core-adr0244d4 forgejo/main` (fetch forgejo first).
- **Push target:** `forgejo` remote; land phases via `git push forgejo feat/adr-0244-d4:main` (Shay authorized direct-to-main for this sole-worker arc), then ff local `main`. Forgejo→GitHub `origin` auto-mirrors.
- **Local-first CI gates (per phase, before push):** in-worktree smoke `uv run core test --suite smoke -q` (176, doctrinal merge gate) → for code phases, fast lane `uv run python -m pytest -n auto -m "not quarantine and not slow"` (~9–10 min). `[Verification]:` line in every commit body.
- **Worktree venv:** real (not symlinked). First code phase: `uv sync` in the worktree. `core_rs` build (if algebra touched): `uv run --project /Users/kaizenpro/Projects/core-adr0244d4 maturin develop --release` (plain `VIRTUAL_ENV`+`PYO3_PYTHON` trips maturin cross-compile detection).
- **A-04 serve quarantine:** new capability code goes in `evals/`; in-place core refactors keep the off-serve quarantine (no imports into `chat/runtime.py` from off-serve modules).
- **No auto-merge / no self-Accept.** Status flips only on explicit Shay ratification.

---

## 9. Progress log (append-only)

- **2026-07-17** — Arc kicked off. Plan doc authored + committed to `main`. Worktree `core-adr0244d4` created off `ee38c976`. Both sign-offs recorded (§2). Next: Phase 0.
- **2026-07-17** — **Phase 0 landed `ad37d03b`.** ADR-0244 reconciled (11-item governance annotation + new §4a superseding §4); ADR-0245 committed as a real companion ADR (Proposed) with its own status map; audit doc updated. Gate green (smoke 176 + provenance/ADR pins 30). Pushed to `forgejo/main`, local `main` fast-forwarded, worktree in sync. Next: Phase 1.
- **2026-07-17** — **Phase 1 core-mechanism correction (ratified), amendment `459280e3`.** Discovered before implementing: `final_state.F` is a versor/operator (grade-1 energy exactly 0), so §2.1/§2.2's literal grade-1 projection is vacuous (flags everything). Ratified switch to **operator-preservation** (sandwich `F aᵢ F̃`): subspace-rejection leakage (catches e4/e5 tilt) + signed self-alignment (catches in-subspace inversion). Both empirically verified necessary + discriminating (identity→0 leak/+1 align; e14/e15 tilt→0.28/0.29 leak; π-invert→0 leak/−1 align). ADR-0244 governance annotation item 12 + §4a rewritten; plan §3 Fact C + §5 Phase 1 updated.
- **2026-07-17** — **Phase 1 landed `3c3d2c29`.** `core/physics/identity_manifold.py` (operator-preservation primitive) + `tests/test_adr_0244_identity_manifold.py` (24 tests). Pure/f64/deterministic, off-serve (quarantine test green). Gate: 24 new + smoke 176 + fast lane **11863 passed, 109 skipped** (9:01). Not yet wired into serve — Phase 2. Next: Phase 2.
- **2026-07-17** — **Phase 2a landed `1c7ea26e`.** Pure `identity.py` capability: dual-mode wave gate + `IdentityGateRefusal` + boundary predicate + admit-or-abstain `C_id` + extended `IdentityScore` + 16 tests. No runtime behavior change (legacy path byte-identical). Gate: 16 new + smoke 176 + fast lane **11879 passed, 109 skipped** (8:39). Next: 2b (runtime wiring behind `identity_wave_gate` flag).
- **2026-07-17** — **Phase 2b landed `c7e2b3b6`.** Runtime wiring: `identity_wave_gate` flag (`core/config.py`), two flag-gated touches in `chat/runtime.py` (`wave_field=final_state.F` at the identity check; post-verdict boundary supplement + geometric refusal fold), wave telemetry in `chat/telemetry.py` (emitted only when `wave_mode_active`). **Integration bug caught + fixed:** the live versor carries boost (e5) components → `F aᵢ F̃` is NOT Euclidean-norm-preserving → un-normalized leakage/self-align ran to 5.16 / −4.75. Fixed with per-axis normalization in `identity_manifold.py` (leakage fraction ∈ [0,1], signed cosine ∈ [−1,1]; Phase-1 unit-rotor results unchanged; boost test added; §4a updated). Gate: 74 targeted + smoke 176 + fast lane **11883 passed, 109 skipped** (8:26) — flag-off byte-identity confirmed. **Open reality for Phase 3:** value axes are placeholders (e1/e2/e3), so whether the geometric gate DISCRIMINATES adversarial vs benign is an empirical question — 2c measures it. Next: 2c (ablation eval).
- **2026-07-17** — **Phase 2c landed `c0ff4720` → Phase 2 COMPLETE.** `evals/adr_0244_identity_gate/` (detection-value ablation) + `tests/test_adr_0244_identity_gate_eval.py` (6 tests) + CLI. Measured: the wave gate separates a geometric-attack panel (2 inversions caught by orientation, 4 tilts/boosts caught by subspace leakage) from an aligned in-subspace panel — all attacks flagged, all aligned admitted, `min_attack_signal 0.35 > max_aligned_leakage 0.0`; wave adds detection value 6-vs-0 over the geometry-blind legacy path. Honest caveat baked in: separation is on the *designed* geometric signal; real-encoder separation is empirical (Phase 3). Additive-only (evals/ + test), off-serving (quarantine green). Gate: smoke 176 + fast lane. Next: Phase 3 (γ_id calibration).
- **2026-07-17** — **Phase 3 landed `323d61c5` → calibration built + certified; live flag flip BLOCKED by empirical non-separation.** `evals/adr_0244_gamma_calibration/` + `tests/test_adr_0244_gamma_calibration.py` (9 tests). The bracketed-local Fibonacci search certifies `γ* = 0.2126624458513829` (cert `0079b5f201fbf616…`) separating the geometric attack signal; pinned as `identity._WAVE_LEAKAGE_BOUND` and **decoupled the wave path from `alignment_threshold`**. **Then measured the crux the whole arc deferred:** real benign live turns do NOT preserve `span(e1,e2,e3)` — leakage 0.14–0.81 (mean 0.55), self-align to −0.52, **12/13 benign false-refused at γ***, best-achievable balanced error **0.346**. So the calibration certifies `flag_flip_authorized=False`; **`identity_wave_gate` stays OFF**. Root cause: the shipped value axes are *nominal basis vectors, not dynamically-preserved eigenmodes* — no dynamical anchoring in the current field evolution; the fix is the **ADR-0246 induced-action programme** (brief already merged). The wave gate is validated, correctly-off scaffolding. A slow drift-guard test canaries any future change that starts preserving identity. Gate: smoke 176 + fast lane + 59 targeted (incl. wave/ablation/runtime unchanged). Next: Phase 4 (§2.5 cast) — independent of 1–3.

---

## 10. Status dashboard

| Phase | Objective | Status | Landed at |
|---|---|---|---|
| 0 | Governance reconciliation (ADR-0244 edits + commit ADR-0245) | ✅ DONE | `ad37d03b` (+ `459280e3` §4a amend) |
| 1 | §2.1 identity manifold primitive (operator-preservation) | ✅ DONE | `3c3d2c29` |
| 2 | §2.2 fail-closed gate + boundary_ids + C_id + telemetry + eval | ✅ DONE | `1c7ea26e`+`c7e2b3b6`+`c0ff4720` |
| 3 | §2.4 γ_id calibration (certified; **live flip BLOCKED — flag stays OFF**) | ✅ DONE | `323d61c5` |
| 4 | §2.5 / 0245 §2.2 serving-boundary cast | ⬜ NOT STARTED | — |
| 5 | §2.7 residual + §2.9 wiring + §2.10 audit + 0245 §3 gate | ⬜ NOT STARTED | — |
| 6 | Close-out (2 acceptance packets + 2 ratified flips) | ⬜ NOT STARTED | — |

**▶ NEXT: Phase 4 — §2.5 / ADR-0245 §2.2 serving-boundary f64→f32 cast** (lifecycle-internal, `core/physics/cognitive_lifecycle.py`; independent of 1–3, depends only on Phase 0). Then Phase 5 (residuals + allocator + 0245 §3 gate), then Phase 6 (close-out).

**Phase 3 headline for resumers:** the γ_id calibration machinery is built + certified, but the empirical finding is that **the live serving flag cannot honestly be flipped on** — real benign traffic doesn't preserve the nominal identity subspace (best balanced error 0.346), so the gate would mass-refuse. `identity_wave_gate` stays OFF; the live gate awaits the ADR-0246 induced-action work. This is a **true architectural-gap discovery**, faithfully honoring the plan's conditional ("flip *once evidenced*"), not a deviation.
