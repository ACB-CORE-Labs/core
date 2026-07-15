# ADR-0241/0242 — Adversarial Verification & Blueprint-Fidelity Findings (W1)

**Author:** Claude (fresh-eyes adversary; did not author the code under attack — P7/P8/cert/seal are Gemini/Grok-session work).
**Date:** 2026-07-15
**Base under attack:** `forgejo/main @ 4853a55c` (post #38 merge + debug-print revert), worktree `feat/adr-0241-0242-mastery-close`.
**Method:** line-level read **plus hostile execution** (grade decomposition, live func-call counters, `sys.modules` import-graph trace, `-X importtime` ancestry), not read-only inspection. All 3 dedicated suites independently re-run green (46 passed).

**Yardstick:** the 4 authority blueprints in `docs/research/*.gdoc`. ADR-0241 read in full; core_ha + fibonacci_applications read; **ADR-0242 "deterministic-fibonacci-operators-and-evidence-gated-optimization" memo not yet available as a local export** — its fidelity slice is partial (noted below).

---

## Verdict summary

| # | Attack target | Verdict | Severity |
|---|---------------|---------|----------|
| 1 | Chiral non-vacuity (P8) | ✅ **CONFIRMED SOLID** — genuinely non-vacuous, exactly conserved | — |
| 3 | Fibonacci cert: budget exactness + digest stability (V1) | ✅ **CONFIRMED SOLID** | — |
| 4 | P9 seal discipline (SPECULATIVE-only) | ✅ **SOLID** + one precision wrinkle | LOW |
| 5 | Fidelity-ledger spot-check | 🟡 mostly honest, **one prose-only green row** | LOW |
| 2 | Serve-quarantine transitivity (A-04) | 🔴 **LIVE BREACH — not a coverage gap** | **HIGH** |

---

## 🔴 Finding #2 (HIGH) — the serve quarantine is breached transitively

**Claimed invariant.** A-04 (`test_phase0_a04_serve_path_quarantines_wave_and_fibonacci`) + ledger §12 row *"Serve path not wired to wave / Fibonacci (containment) 🟢"* + module docstrings (`wave_manifold`: "Off-serving until explicit gates"; `wave_energy_boundary`/`multi_scale_energy`: **"never serve"**). The stated invariant is **process-level**: the serve path must not pull in the wave/fibonacci substrate.

**What is actually true.** Importing `chat.runtime` transitively loads **five** banned modules into `sys.modules`:
`core.physics.wave_manifold`, `core.physics.holographic_vault`, `core.physics.fibonacci_search`, `core.physics.multi_scale_energy`, `core.physics.wave_energy_boundary`.

**Exact chain (`-X importtime` ancestry):**
```
chat.runtime → chat.pack_grounding → packs.anchor_lens.loader → formation.smelter
  → teaching.correction → generate.intent → generate.proposition
  → field.state → field.propagate → core.physics.energy → [core/physics/__init__.py barrel]
      → goldtether            → wave_manifold
      → wave_energy_boundary  → fibonacci_search
      → multi_scale_energy
      → holographic_vault
```

**Root cause.** `core/physics/__init__.py` is a **barrel init that eagerly imports the entire physics surface**, including `wave_manifold` (line 72), `goldtether` (line 28, which itself hard-imports `WaveManifold` at `goldtether.py:35`), `holographic_vault`, `wave_energy_boundary`, `multi_scale_energy`. `field/propagate.py` needs only `from core.physics.energy import FieldEnergyOperator` — one lightweight submodule — but importing any `core.physics.*` submodule runs the barrel and drags in everything.

**Why the pin missed it.** The A-04 test walks only `chat/runtime.py`'s **own** AST import nodes → catches **direct** imports only. A 2+-hop chain through a package barrel is invisible to it. Demonstrated: direct `import wave_manifold` → flagged `True`; transitive chain → flagged `False`. No complementary `sys.modules` guard exists anywhere in the suite.

**Severity = HIGH.** This directly falsifies a 🟢 acceptance-checklist row Joshua would rely on to Accept, loads modules explicitly labeled "never serve" into the serve process (startup cost + memory + containment-doctrine violation), and — because the guarding pin stays green — a future edit to `energy.py`/`goldtether` could begin *invoking* wave functions on the hot path with nothing to catch it.

### Design-intent fork (Joshua's call — not mine to decide)
`wave_manifold` sits on **both** sides: the subsumption map says `goldtether`/`surprise`/`biography` (Third-Door serve operators) **delegate to** `WaveManifold` (`goldtether.coherence_residual` → `WaveManifold().measure_unitary_residual`), yet `wave_manifold` is on the A-04 **ban** list. Both cannot be true. Two honest resolutions:

- **(A) Quarantine wave_manifold for real:** de-barrel the off-serving modules (PEP 562 lazy `__getattr__` in `core/physics/__init__.py`) **and** make `goldtether`'s `WaveManifold` import lazy (2 call sites). Restores the letter of A-04. Only coherent if serving never calls `coherence_residual` on the hot path.
- **(B) Accept wave_manifold as serve substrate:** remove `wave_manifold` from the A-04 ban list, correct the ledger row, and keep only the genuinely-off-serving research modules quarantined (`multi_scale_energy`, `wave_energy_boundary`, `holographic_vault`, `fibonacci_search`, `wave_seam`, `sensorium_wave_feed`, `atlas_packing`).

**Unambiguous either way:** the modules labeled *"never serve"* must leave the barrel's eager path, and a **transitive `sys.modules` guard test** must replace/augment the direct-AST pin so this can never regress silently.

---

## ✅ Finding #1 — Chiral non-vacuity (P8): CONFIRMED SOLID

Blueprint ADR-0241 §2.4C: `Q = ⟨ψ I₅ ψ̃⟩₀`, non-vacuous for odd-capable mixed-parity spinors, conserved under `ψ → Rψ`.

Executed with the algebra's **graded-lexicographic** convention (grade-1 = idx 1–5; my first probe's bit-count grade map was wrong and is discarded):
- Fixture `psi = v + v·I₅`, `v = e1 + 0.5·e3` → grades **{1: 1.118 (odd), 4: 1.118 (even)}** — genuinely mixed parity, **not** a pure even field-state.
- `Q(psi) = −2.5` (|Q| ≫ 0.1 threshold — comfortably non-zero, not borderline).
- Conserved under `left_spinor_step`: drift `|q0 − q1| = 0.000e+00` (exact).
- Even unit versor → `Q = 0.000e+00` (honest; does **not** revive the retired-#19 vacuous gate).

**Fidelity win:** the blueprint's own §4 prototype used `np.outer(psi_B, psi_A)` + `la.svd` (Euclidean matrix proxies). The implementation correctly rejected that in favor of exact `geometric_product`/`cga_inner`. The impl is *more faithful to the algebra than the blueprint's reference code.*

---

## ✅ Finding #3 — Fibonacci cert (V1): CONFIRMED SOLID

- **Budget exactness** via a live func-call counter across budgets **8/15/20/21**: actual `func` calls == `cert.evaluations` == `budget` == `len(ordered_points)` in every case. No off-by-one at bracket init. (Structurally: 2 initial evals + `(n−2)` single-eval loop iterations = `n`.)
- **Digest stability:** dual independent runs → identical `cert_id` (64-hex) and identical `as_dict()`. Pure arithmetic (no RNG / set-ordering), so bit-stable by construction.
- Typed `Certificate | Failure` surface; fail-closed on nonfinite / unimodality / bounds; never a bare float.

**Precision nit (LOW):** the certificate's `minimizer` returns `best_x` (a sampled point) when it lies inside the final bracket, else the midpoint — but the docstring says *"Drive cert uses midpoint of final bracket."* Code prefers the better sample; harmless, but doc and code disagree. One-line doc fix.

---

## ✅ Finding #4 — P9 seal discipline: SOLID (one precision wrinkle, LOW)

- `HolographicVaultStore.seal_mode` sets `EpistemicStatus.SPECULATIVE` by construction (`holographic_vault.py:153`); COHERENT lives only in `seal_mode_reviewed(authorized=True)` (refuses without authorization). `speculative_seal_from_contemplation` calls **only** `seal_mode`, with a defensive re-check that raises on any non-SPECULATIVE return. Contemplation can never emit COHERENT. ✅
- `reconstruct_as_evidence` excludes SPECULATIVE (min_status=COHERENT) and refuses on empty spectrum. ✅

**Precision wrinkle:** the stated invariant is *"physics never imports teaching,"* but `core/physics/holographic_vault.py:30` imports `teaching.epistemic.EpistemicStatus`. The **tested** invariant (`test_wave_manifold_module_does_not_import_teaching`) guards only `wave_manifold.py`, which is clean. Not a live breach — `EpistemicStatus` is boundary vocabulary — but the clean "physics ⊥ teaching" story has one sanctioned seam. Design note: consider relocating `EpistemicStatus` to a shared non-teaching kernel (e.g. `core/epistemic_state.py`) so the boundary is literal.

---

## 🟡 Finding #5 — Fidelity-ledger spot-check: mostly honest, one prose-only green

Mapped 4 §12 rows → named pins:
1. *"Chiral non-vacuous … conserved … even ~0"* → `test_chiral_charge_{nonzero,conserved,honest}` — fails if Q=0 / not conserved. ✅ real behavioral pin.
2. *"Fibonacci cert/failure (V1)"* → `test_fibonacci_search_eval_count_equals_budget` + `test_certificate_digest_stable_dual_run` — fails on off-by-one / digest drift. ✅ real.
3. *"Serve path not wired (containment)"* → `test_phase0_a04…` — maps to a real pin, **but the prose "not wired" overstates a direct-import-only test** (see Finding #2). Downgrade the claim or strengthen the pin.
4. *"Fibonacci anyons (V5) 🟢 quarantine package only; zero production imports"* → **no anyon package exists in the repo and no test references "anyon."** A 🟢 row with no code and no pin — the "namesake-green" trap §7 warns about. "Zero production imports" is vacuously true of a nonexistent module. **Downgrade to "not built / claim-quarantined"** (consistent with the R&D-memo anyon "immune to float32 drift" claim being deliberately not implemented).

Other V-vectors (V2 `multi_scale_energy`, V4 `fibonacci_word_schedule`, sensorium, `wave_energy_boundary`, `atlas_packing`) each carry 2–4 real test files.

---

## Blueprint fidelity (ADR-0241) — deviations for the acceptance packet

| Blueprint clause | Implementation | Fidelity |
|---|---|---|
| §2.4A analogical = **closed-form Clifford polar** `C=RS`, extract R directly | **Demoted** to numerical sandwich conjugacy (SVD + Spin GN); `test_true_clifford_polar_fails_on_multigrade_field` proves `~C C` is non-scalar for multigrade fields → analytic polar **ill-posed** | **Honest deviation** — recommend accept-as-honest per the #19 RETIRE precedent. **P7 headline for Joshua.** |
| §2.4C chiral grade-5 charge | Faithful + non-vacuous (Finding #1) | ✅ |
| §2.4D GoldTether = unitary amplitude residual | `measure_unitary_residual` dual-checks `‖ψψ̃−1‖` | ✅ |
| §2.2 holographic recall = **exact reconstruction, zero thaw loss** | `resonant_recall`/`resonant_reconstruct` + durable `HolographicVaultStore`, but **float32 storage** (I-02 honest tol 1e-6, not bit-exact 1e-12) | Softened to "float32-honest" — already flagged in-suite; note for ruling |
| §2.3 continuous multimodal / sensorium | **Staged/fake sensorium packets** + real ρ (`sensorium_wave_feed`) | Open by design (W5) |
| §5.2 MLX/UMA + Rust exact GP | `algebra.backend` P11a (Rust-ready; Python is truth); f64 GP parity deferred (D9) | Staged |

**ADR-0242 memo slice — partial:** the "deterministic-fibonacci-operators-and-evidence-gated-optimization" R&D memo is not yet available as a local export, so the memo-vs-impl fidelity check is incomplete. What is verifiable: the implementation's Fibonacci cert is solid (Finding #3), and the memo's flagged-dubious claims appear correctly filtered — the **anyon** claim is not built (Finding #5), and the "Fibonacci division-cost" R&D claim did not land as a production optimization. Full slice pending the memo export.

---

## Recommended actions

1. **Finding #2 (HIGH)** — resolve before Accept. Unambiguous part: de-barrel the "never serve" modules from `core/physics/__init__.py` (lazy `__getattr__`) + add a transitive `sys.modules` guard test. Design fork (A vs B on `wave_manifold`) → Joshua.
2. **Finding #4 / #5 / #3 nits (LOW)** — batch: relocate `EpistemicStatus` (or document the sanctioned seam); downgrade the anyon ledger row; fix the Fibonacci `minimizer` docstring.
3. Everything else verified solid — no other fix-forward required.
