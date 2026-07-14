# Third-Door Blueprint Fidelity Ledger

**Status:** authoritative gap analysis for the ADR-0238/0239/0240 skeleton (PR #15).
**Audience:** whoever implements the Third Door *for real*.
**Verdict in one line:** what landed is a **safe, off-serving namesake scaffold** — it adopts the blueprints' vocabulary and file layout and makes its own tests green, but it does **not** implement the mathematics the two source blueprints specify. This document details every gap precisely enough to close it.

> This replaces the "absolute mastery / single right solution" framing of the original landing (Mastery Report / PR #14 body). The blueprints are the rigorous artifact; the code is the loose one. That is the honest inversion of the landing claim.

---

## 0. Source-of-truth artifacts

| Artifact | Role |
|---|---|
| `CORE ASI Super-Blueprint_ Third-Door Horizon.docx` (mirror: `docs/research/CORE-ASI-Super-Blueprint-Third-Door-Horizon.md`) | Specifies signature-aware PCA (§2.1), Cartan–Iwasawa (§2.2), GoldTether scale harmonization (§2.3), Conformal Procrustes (§3.1), Surprise (§3.2), grade-5 pseudoscalar invariant (§3.3). **"Super §x"** below. |
| `CORE Advanced AGI_ASI R&D Blueprint (Revised).docx` | Specifies blade induction (§2.1), trajectory invariants + zero-fabrication (§2.2), GoldTether-modulated transition surface + α control law (§2.3), ADR-DAG embedding (§2.4), bootstrapping (§5). **"R&D §x"** below. |
| `docs/adr/ADR-0241-wave-field-driven-hyperbolic-atlas-and-resonant-cognition.md` | Wave-field substrate \(\psi\): unitary propagation, spectral leakage, polar analogy, chiral charge. **"ADR-0241"** below. |
| `docs/analysis/core_ha_unification_and_deprecation_plan.md` | Deprecate standalone `core_ha` pointwise atlas; absorb into wave + energy + GoldTether + CRDT vault. |
| `core/physics/{goldtether,dynamic_manifold,surprise,biography,temporal_gate,self_authorship}.py` | The landed Third-Door code (pointwise). Wave module: `wave_manifold.py` (Proposed). |
| `tests/test_adr_023{8,9}_*.py`, `test_adr_0240_*.py` | Landed Third-Door tests (see §7 for why green ≠ faithful historically). |
| `tests/test_adr_0241_wave_manifold.py` | Wave-field behavioral contract (RED until Slice 1 GREEN). |
| `tests/test_third_door_blueprint_fidelity.py` | The living gap ledger (this document, executable). |

**Containment fact (why this is safe to land):** nothing in serving / runtime / cognition imports `core.physics.*` — only the package `__init__`, the eval harness, and tests. `chat/runtime.py` is untouched on this branch. The autonomy `decide()` is fail-closed and never `AUTONOMOUS` in `SERVE`. The self-authorship miner is proposal-only and never writes the vault. None of the defects below can reach the `wrong=0` serving path.

---

## 1. Scorecard

| # | Operator | Blueprint | Fidelity | Issue |
|---|---|---|---|---|
| 1 | Signature-aware PCA | Super §2.1 / R&D §2.1 | 🟢 faithful (one untested add-on) | — |
| 2 | Cartan–Iwasawa decomposition | Super §2.2 | 🟢 faithful (null-point peel + Spin remainder) | #16 |
| 3 | Conformal Procrustes | Super §3.1 | 🟢 faithful (Kabsch + field conjugacy) | #17 |
| 4 | GoldTether residual + α law | Super §2.3, R&D §2.3/§5 | 🟢 residual+α + bootstrap gates + principal-axis prune (#24+#18) | #18 |
| 5 | Grade-5 pseudoscalar invariant | Super §3.3 | ⚪ RETIRED — vacuous in odd-dim Cl(4,1) | #19 (closed) |
| 6 | Surprise residual operator | Super §3.2 | 🟢 math + DiscoveryCandidate wiring landed (#26 + #31) | #20 |
| 7 | Trajectory invariants + zero-fabrication | R&D §2.2 | 🟢 Python geometry surface (`trajectory_invariants.py`) | #21 |
| 8 | ADR-DAG conformal embedding | R&D §2.4 | 🟢 Python surface (`core/adr/validator.py`) | #21 |
| W1 | WaveManifold unitary / sandwich step | ADR-0241 §2 | 🟢 | ADR-0241 |
| W2 | Spectral leakage surprise | ADR-0241 §2.4B | 🟢 subsumed into `surprise_residual` | ADR-0241 |
| W3 | Wave polar + multi-pair conjugacy | ADR-0241 §2.4A | 🟢 sandwich conjugacy (`_field_conjugacy_versor`); analytic multi-grade polar ⚪ RETIRED | ADR-0241 |
| W4 | Unitary residual + chiral charge readout | ADR-0241 §2.4C–D | 🟢 (Q structural 0 in real Cl(4,1); see §12) | ADR-0241 / #18 |
| W5 | Biography resonant lock-in + durable holographic vault | ADR-0241 + ADR-0240 | 🟢 session registry + `HolographicVaultStore` (VaultStore-backed) | ADR-0241 |
| W6 | `core_ha` deprecation / absorption | deprecation plan | 🟢 no live tree + hygiene pin | ADR-0241 |
| — | Biography holonomy | (ADR-0240; not in blueprints) | 🟢 sound (pointwise) | — |
| — | Temporal admissibility gate | (ADR-0240; not in blueprints) | 🟢 sound | — |
| — | Self-authorship miner | (ADR-0240; not in blueprints) | 🟢 sound (proposal-only) | — |

---

## 2. Cartan–Iwasawa decomposition — 🟢 faithful (#16)

### Blueprint spec (Super §2.2)
Factor a conformal versor `V = R·T·D` by acting on the conformal null points `n_o` (origin) and `n∞` (infinity). Explicitly "mathematically exact, non-iterative, guarantees perfect decomposition":
1. **Dilation** — `V n∞ Ṽ = λ² n∞`; `λ = √|V n∞ Ṽ|`; `D = exp(log(λ)·e_o∧e∞)`; peel: `V' = V·D⁻¹`.
2. **Translation** — `V' n_o Ṽ' = n_o + a + ½a²n∞`; recover `a ∈ ℝ³` by projecting the Euclidean vector part; `T = exp(½ a∧e∞)`; peel: `R = V'·T⁻¹`.
3. **Rotor** — the remainder `R` satisfies `R Ṙ = 1`, `R n_o Ṙ = n_o`, `R n∞ Ṙ = n∞`.

### What landed (`dynamic_manifold.py::cartan_iwasawa_factorize`)
Null-point peel via `algebra.null_point.recover_dilation` / `recover_translation` (right-peel D then T for reconstruction order `R·T·D`). **Strict** construction-boundary close (rescale true versors only — never seed-to-rotor fabrications). On `NullPointRecoveryError` (non-similarity — e.g. multi-plane products that do not fix `n∞`) fall through to honest **remainder-as-rotor**: `R=V`, `T=I`, `D=I`. Peel path that fails reconstruction residual falls back to Spin remainder. Every returned factor is closed (`versor_condition < 1e-6`); non-versor input raises `ValueError` (fail-closed). No grade-projection fabrication of R/D seeds.

**Dual-correction follow-on:** `rotor_power` now implements exact null-bivector power `(a+B)^α = a^α + α a^{α-1} B` so `dual_correction_slerp` no longer silently zeros the translation leg.

### Acceptance (pinned)
- Composed multi-plane versors never raise; residual `‖R·T·D − V‖ < 1e-6` (often ~0 for Spin remainder).
- Pure similarities `V = R_euc·T·D` peel with residual < 1e-6 **and** peel-content pins (nontrivial D with recovered scale, nontrivial T, `R·T ≈ V·D⁻¹`).
- Pure dilator / translator / identity round-trip with factor-content asserts (not residual alone).
- `test_cartan_iwasawa_should_reconstruct_composed_motion` passes (xfail removed).
- Translator half-slerp: `dual_correction_slerp(I, translator([2,0,0]), 0.5)` recovers displacement `[1,0,0]`.

---

## 3. Conformal Procrustes — 🟢 faithful (#17)

### Blueprint spec (Super §3.1)
Two fields `F_A`, `F_B` are structurally analogous iff a single versor `V` maps one to the other under the sandwich `V·F_A·Ṽ = F_B`. Solve as a metric-aware **Kabsch on null-vector point sets** `P={p_i}`, `Q={q_i}`:
`K = Σ p_i q_iᵀ η` → signature-aware SVD `K = UΣVᵀ` → `R = V Uᵀ`; translation + dilation from null-cone centroids. Verified by margin `|V·F_A·Ṽ − F_B| < ε_analogy`. Enables zero-shot transport of `F_A`'s solution path to `F_B`.

### What landed (`dynamic_manifold.py::conformal_procrustes`)
- **(5,K) path**: dehomogenize (`w=e5−e4`), Umeyama scale + Kabsch `R` with `det=+1`, `t = μ_y − s R μ_x`, assemble `V = T(t)·D(s)·R` via `null_point.translator/dilator` + `so3_matrix_to_rotor`, return grade-1 sandwich adjoint `M` (5×5) with **weight-normalized** residual (dilation changes homogeneous weight; Euclidean images still match to ~1e-15).
- **Null-point 32-lists**: extract (5,K), Kabsch, return **V32** with sandwich residual.
- **Field conjugacy** (non-null 32-vecs): stacked linear `W F_A − F_B W = 0` nullspace candidates + multiplicative Lie GN on Spin; residual is **sandwich** (`versor_apply`), not left-composition. `word_transition_rotor` averaging **deleted** from this path.
- Analogical harness fixture learns from probe null-point clouds under a known similarity (no longer I→I).

### Acceptance (pinned)
- Multiplane `F_B = versor_apply(W, F_A)` → sandwich residual < 1e-5.
- Known rotation / full similarity (s,R,t) clouds → residual < 1e-6, mapped points match.
- Null-point list of 32-vecs → sandwich residual < 1e-6.

---

## 4. GoldTether residual + α control law — 🟡 partial (#18)

### Blueprint spec (Super §2.3, R&D §2.3/§5)
- **Residual (scale-harmonized — Super §2.3, the blueprint's stated mission #1):**
  `R = w·(‖F·F̃−1‖/ε_drift) + (1−w)·(min_{I∈𝓘_gold} ‖F−I‖ / ‖F‖_F)`, `w=0.5`, `ε_drift=1e-6`. Both terms scaled to `[0, O(1)]` so drift isn't masked by the raw O(1) L2 distance.
- **α control law (R&D §2.3):** `α(t) = Φ(R; R_floor, R_critical)` — a smooth-step of the **instantaneous** residual. `α=0` (autonomous) when `R < R_floor`; linear ramp in between; `α=1` (full human override / fail-closed) when `R > R_critical`. α is the *constraint weight*; the supervised transition is the Cartan–Iwasawa factor-wise slerp of §2.3.
- **Bootstrapping (R&D §5):** `𝓘_gold` primed with `n_o, n∞, 1`; audit-passed replay-deterministic state versors promoted into it by signed review vote (ADR-0092); decay/pruning to principal axes.

### What landed (`goldtether.py`) — residual+α path (#24)
- `coherence_residual(F)` remains the fail-closed **closure** gate (dual-checked unit residual).
- `gold_invariants` seeded with identity + `n_o` + `n∞` (`_primal_gold_invariants`).
- `goldtether_residual(F)` = scale-harmonized two-term residual (drift/ε + dist-to-gold / ‖F‖).
- `alpha_constraint(F, mode=…)` = `Φ(R_gt; r_floor, r_critical)` composed with earned-autonomy floor; **SERVE always α=1**.
- `supervised_transition` / `supervised_blend` on the Spin geodesic (`word_transition_rotor` + `rotor_power`).
- `promote_gold_invariant(..., authorized=True)` is **caller-gated** (no self-authorize); `prune_gold_invariants` is a size bound retaining the three primals — **not** full principal-axis decay.

### Bootstrap / prune (#18 — landed)
- `GoldPromotionProof` + `promote_gold_invariant(..., proof=, require_proof=)`: proposal-only without `authorized=True`; live **closure drift** gate (not geo-to-gold); refuses non-closed / high-drift even when authorized; never trusts proof fields as truth.
- `promotion_eligible(F)`: closed ∧ drift ≤ ε_drift (does not self-authorize).
- `prune_gold_invariants(mode="fifo"|"principal_axes")`: primals immovable; PCA ranks non-primals by principal-subspace energy (differs from last-N FIFO); `max_size < 3` clamped.
- Unitary residual path still via wave (`measure_unitary_residual`); SERVE never autonomous.

### Explicit non-goals still open
- Full signed ADR-0092 *reviewer service* wiring (physics stays caller-gated only).
- Durable vault-backed gold set (session monitor field only).

---

## 5. Grade-5 pseudoscalar invariant — ⚪ RETIRED as vacuous (#19)

> **Resolution (2026-07-12):** three-agent R&D convergence (Opus 4.8 / Grok-4.5-HEAVY / GPT-5.6-Terra), ratified. The §3.3 gate is not "missing" — it is **mathematically vacuous in odd-dimensional Cl(4,1)** and cannot be built as specified. Issue #19 is closed. The namesake was removed from `goldtether.py` in the same change (see "What changed" below).

### Blueprint spec (Super §3.3)
The pseudoscalar `I₅ = e1∧e2∧e3∧e4∧e5` is the orientation of CORE's integrity. Every transition `F' = V·F·Ṽ` must preserve pseudoscalar sign **and** magnitude: `⟨F'·F̃'⟩₅ = ⟨F·F̃⟩₅`. Any optimization / contemplation promotion / autonomous self-authorship that would flip `sgn(I₅)` is **blocked at the boundary**. Called "the ultimate mathematical anchor for alignment."

### Why it is vacuous (the proof that retired it)
The spec presumes a spacetime-like even-dimensional intuition. CORE's algebra is Cl(4,1) — **odd** total dimension (5) — where the grade-5 pseudoscalar behaves degenerately for exactly the quantities the gate inspects:

1. **`I₅` is central.** In odd dimension the pseudoscalar commutes with every element, so for *any* versor `V` (including odd reflections, where `V·Ṽ = ±1`), the sandwich collapses: `V·I₅·Ṽ = I₅·(V·Ṽ) = ±I₅`. Orientation is invariant by construction — there is no map in the versor group that flips it, so there is nothing to "block."
2. **Field-state versors are even ⇒ `F[31] ≡ 0`.** Every state the monitor sees is built by the sanctioned constructors (`make_rotor_from_angle`, `word_transition_rotor`, geometric products thereof) which live in the **even subalgebra**. The grade-5 (odd) coefficient of an even multivector is identically zero. Reading `F[31]` returns a structural `0.0`, always.
3. **The gated quantity is identically zero.** For an even unit versor, `F·F̃ = 1` (a scalar), so `⟨F·F̃⟩₅ = 0` for the source **and** the target of every transition. The gate `⟨F'·F̃'⟩₅ = ⟨F·F̃⟩₅` compares `0 == 0`. It can never fire.
4. **The "even-versor parity gate" fix is also vacuous.** The natural repair — "reject any transition that injects odd-grade mass" — was *invalidated in the same review*: the even subalgebra is closed under the sandwich, so odd-grade mass `≡ 0` on every value the sanctioned path can produce. Parity guards nothing a versor could reach. (Empirically confirmed: on a composed 5-plane field versor, `‖⟨F·F̃⟩₅‖ = 0`, and total odd-grade mass `= 0`.)

The single **real** residual gap in this neighborhood is unrelated to grade-5: `algebra/versor.py::versor_condition` *accepts* an odd reflection such as `e1` (returns `0.0`), i.e. it gates "is a unit versor," not "is an even/orientation-preserving versor." That is a boundary-hardening concern about **admitting odd generators at all**, not about a grade-5 transition invariant, and it is out of scope for #19.

### What changed (this PR)
The namesake was removed, not left masking an absence:
- Deleted `_PSEUDOSCALAR_IDX` and every `F[31]` read (the dead `ps` history element and `CoherenceResidual.pseudoscalar`, both structural zeros).
- Renamed the telemetry channel `pseudoscalar_floor → autonomy_floor` (it was always `self.floor`, the earned-autonomy ceiling — never a pseudoscalar).
- Bumped the telemetry schema `goldtether_coherence_v1 → v2` (the shape changed: key renamed, dead `ps` dropped).
- Updated the module/class docstrings to state the retirement inline.

### Where the integrity-anchor role actually lives (subsumption)
The alignment intent behind §3.3 is real and is **already carried, non-vacuously**, by three built mechanisms:
1. **Versor closure** — `versor_condition(F') < 1e-6` is enforced on every transition (`supervised_blend` raises on breach). This is the genuine "the state stayed on the group" gate, checked at ~1e-13 over a 100k-step walk (see `project-l10-closure-by-construction`).
2. **GoldTether harmonized residual + α control (#24)** — drift term + distance-to-`𝓘_gold` + `α = Φ(R)`, the actual alignment-pressure signal, replacing the vacuous orientation check with a metric one that *can* move.
3. **Biography / identity holonomy (ADR-0240 + `engine_identity`)** — order-sensitive trajectory encoding + content-derived identity lineage: the "same continuous life, no confabulated self" anchor. This is where a *real* topological integrity invariant lives.

Grade-5 objects remain non-vacuous **only in the incidence layer** (5-blades as conformal geometric objects under meet/join in `algebra/cga.py`), never as a transition/promotion gate.

### Reusable meta-criterion (the session's key output)
> **"Would this gate ever fire on a value produced by the sanctioned construction path? If no → it is a namesake gate, not an anchor."**

This diagnostic is what killed §3.3, and it should be applied to every remaining `§-N` claim before any implementation effort is spent. Acceptance for #19 is therefore **negative**: no gate is built; the namesake is gone; the intent is shown to be subsumed.

---

## 6. Surprise residual operator — 🟢 math + DiscoveryCandidate wiring (#20 closed)

> **Resolution (2026-07-12):** the two operator-math defects are fixed (#26) — exact metric-orthogonal projection and reconciled productivity polarity.
>
> **Resolution (2026-07-14, PR #31 / issue #30):** high surprise now raises a proposal-only `DiscoveryCandidate` (`trigger=high_surprise`) into the existing discovery sink stream. Contemplation consumes that JSONL unchanged. No vault/self-install; physics never imports teaching.

### Blueprint spec (Super §3.2)
`S(x) = x − proj_{B_union}(x)`, where `proj_B(x) = (x·B)·B⁻¹` is the **geometric blade contraction**. `|S(x)|²` measures the epistemic frontier; high surprise (`> γ`) raises a `DiscoveryCandidate` in the contemplation loop (self-directed learning).

### The defects (as landed)
1. Projection was **Euclidean Gram-Schmidt on flat 32-coefficient vectors** — metric-blind: it ignored the (+,+,+,+,−) signature and the blade grade structure, so "inside the admissible span" was judged by the wrong geometry. (The 5-vec path already used η.)
2. `dual_operator`: `productive = proc_r <= thr and sur_norm >= 0.0` — the second conjunct is **always true**, so surprise never gated.
3. Not wired: nothing raises a `DiscoveryCandidate`.

### What changed (this PR)
- **Exact metric-orthogonal projection.** `surprise_residual` now solves the metric normal equations `G c = r` (`G_ij = ⟨b_i,b_j⟩`, `r_i = ⟨b_i,x⟩`) via `lstsq`, under `cga_inner` (32-vec) / η (5-vec). The residual magnitude is the reversion (metric) norm, and grade-support containment is asserted (fail-closed on leakage).
- **Fail-closed on a metric-degenerate span.** Typed `SurpriseResidualError` when `rank(G) < rank(B)` — a null direction with no reciprocal (e.g. a lone `n_o`). *Refinement over the original "rank(G) < k" spec:* mere linear dependence among **non-null** columns is ADMITTED (`lstsq` projects onto the actual span), so a merely-redundant live basis (`[1, source]`, which the analogical-transfer harness can produce) is not spuriously refused, the non-degenerate null-pair `{n_o, n_∞}` is admitted, and only a lone `n_o` is refused. This is what the geometry — not column-vector algebra — actually requires.
- **Reconciled productivity polarity.** `productive` (and `transfer_accepted`) now both mean **productive TRANSFER = low Procrustes ∧ low surprise** (a structural match found AND the query inside the admissible span). This **corrects** §6's earlier "high surprise ∧ low procrustes = productive" phrasing, which conflated *transfer* with *discovery*: HIGH surprise is a **discovery** signal, not a productive transfer, and routes to the (split-out) `DiscoveryCandidate` path.
- Tests: `tests/test_adr_0239_surprise_metric_projection.py` — metric-vs-Euclidean divergence (the load-bearing proof), null refusal, null-pair admission, redundant-basis admission, in/out-of-span, grade purity, polarity, determinism.

### Wiring landed (PR #31 / issue #30) — acceptance
High surprise routes to a proposal-only `DiscoveryCandidate`:
- Physics (`dual_operator` / `dual_procrustes_surprise`) sets `discovery_eligible` when `sur_norm > γ` and transfer is not productive (`is_discovery_eligible`; default `γ = 0.35`). **No teaching import** in `core.physics.surprise`.
- Teaching factory: `candidate_from_surprise_dual` / `emit_surprise_discovery` produce `trigger=high_surprise`, `review_state=unreviewed`, `domain=math`. Opt-in `DiscoveryCandidateSink` emit (same stream contemplation already consumes). **Never** vault/store/self-install.
- Tests: `tests/test_third_door_surprise_discovery_wiring.py` + dual suite.

No remaining #20 follow-up.

---

## 7. Signature-aware PCA — 🟢 faithful (one untested add-on)

### Blueprint spec (Super §2.1 / R&D §2.1)
`A = XXᵀ/k`; `M = ηA`; `eig(M)`; sort by `Re(λ)` desc; real eigenvectors; Minkowski Gram-Schmidt to a pseudo-orthonormal basis on the (4,1) null cone. (R&D §2.1 phrases it as the generalized problem `Av = λ η v`.)

### What landed (`dynamic_manifold.py::signature_aware_pca`)
Exactly this, minus `scipy` (uses `np.linalg.eig` on `M = ηA` — the Super §2.1 alternative formulation; correct and dependency-free). **Plus** a null-retention branch that keeps genuine null axes instead of skipping them ("Terra + Grok mastery fix").

### The one wrinkle
The null add-on is **untested**: `test_signature_aware_pca_keeps_nulls` classifies `n_null = 0` in its own scenario and only asserts `total == 4` + enum-ness. The branch that gives the fix its name never demonstrably fires. Low severity; add a scenario that actually produces a retained null axis.

---

## 8. Sound modules not in the blueprints — 🟢

`biography.py` (delegates to `algebra.holonomy.holonomy_encode`; refuses empty trajectories — "no confabulated self"; order-sensitive; reconstruct == integrate), `temporal_gate.py` (a clean typed `ADMIT/NOT_YET/REFUSE` predicate — no geometry despite the "wisdom as geometry" docstring), and `self_authorship.py` (proposal-only, `SPECULATIVE`-stamped, no vault import — test-enforced; catches the Procrustes `ValueError` and records it) are the healthiest modules **because they delegate to real primitives or stay pure instead of reinventing geometry.** They are ADR-0240 additions, not specified in either blueprint.

---

## 9. Trajectory invariants + ADR-DAG — 🟢 Python surfaces (#21)

> **Landed (2026-07-14):** geometry-first Python authorities. Rust Ring-1 port remains optional acceleration, not a second truth.

### Trajectory invariants (R&D §2.2 → `core/physics/trajectory_invariants.py`)
- Relative holonomy `H = V_i · reverse(V_{i+1})`
- Divergence `D = Σ log(1 + ‖H reverse(H) − 1‖) · Δt`; bound `D < ε_trajectory`
- Energy boundary `E_exertion ≤ κ · E_sensory`
- Zero-fabrication: empty / short / non-closed steps refused
- Tests: `tests/test_third_door_trajectory_invariants.py`

### ADR-DAG conformal embedding (R&D §2.4 → `core/adr/validator.py`)
- `Ψ(M)`: SHA-256 → 10×3-byte → `c_k ∈ [−1,1]` → planes 6..15 → simple-bivector project
- Master blade = successive wedge of load-bearing ADR embeddings
- Proposal drift = `‖B_p ∧ A_master‖`
- Does **not** parallel `core/abi/geometric_delta_validator.py` (that validates GeometricDelta ABI envelopes)
- Tests: `tests/test_third_door_adr_dag_embedding.py`

---

## 10. Why "34/34 green" did not catch any of this

The landed suite measures properties that hold **by construction**, not spec-fidelity:
- **Tautologies:** `residual >= 0`, `reconstruction_residual >= 0` (norms are non-negative).
- **Closure-only:** `versor_condition(out) < 1e-6` proves the output is *a* unit versor, not the *correct* one. §4's blend passes closure at ~1e-16 while being a no-op.
- **Trivial regime:** every geometry test feeds `identity` + a single-plane `make_rotor_from_angle` — the one input class where `rotor_power` doesn't hit its non-simple-bivector identity fallback.
- **One vacuous test:** §3's identity→identity Procrustes.

The lesson: closure is necessary, not sufficient. Fidelity tests must feed **composed** versors and assert **behavioral** properties (interpolation moves; reconstruction matches; transport lands on target).

---

## 11. Reproduction

From a checkout of this branch (worktree on `PYTHONPATH`):
```bash
# Fidelity ledger (2 characterizations pass, 2 spec tests xfail):
python -m pytest tests/test_third_door_blueprint_fidelity.py -v -rx

# Blend degeneration on a composed pair (interior alpha == source):
python - <<'PY'
import numpy as np
from algebra.cl41 import geometric_product
from algebra.rotor import make_rotor_from_angle
from core.physics.goldtether import GoldTetherMonitor
def _id():
    v=np.zeros(32); v[0]=1.0; return v
def comp(planes,s):
    v=_id()
    for k,i in enumerate(planes): v=geometric_product(v, make_rotor_from_angle(0.3+0.13*k+0.05*s, bivector_idx=i))
    return v
A,B=comp((6,7,8,10,11),1.0),comp((6,7,8,10,11),2.0)
for a in (0.25,0.5,0.75):
    o=GoldTetherMonitor().supervised_blend(A,B,a)
    print(a, "||o-A|| =", float(np.linalg.norm(o-A)))   # -> 0.0 (no-op)
PY
```

---

## 12. Wave-field substrate (ADR-0241) — 🟢 local operators / 🟡 entity mastery

> **Status (2026-07-14, honesty pass):** Local Slice 1–3 + holographic vault
> behavioral suites are **GREEN**. Entity cohesion (I-01…I-05, Trace A/B,
> Golden-Angle packing, true \(\mathcal{C}_{AB}\) polar, non-vacuous chiral,
> multimodal \(\rho\)) is the remaining mastery surface — see
> `docs/analysis/core_cohesion_master_plan.md` and
> `tests/test_third_door_cohesion.py`.

### Spec (ADR-0241) — contract
- Continuous multivector wave-field \(\psi \in Cl(4,1)\) (32-coeff) under Cartan/Procrustes, Surprise, GoldTether, Biography.
- **Transport pin:** multivector fields → sandwich \(R\psi\widetilde{R}\); spinor/chiral → left multiply \(R\psi\). No silent mix.
- Spectral leakage = metric proj onto resonant modes (definite Euclidean energy after metric-exact proj).
- Unitary residual \(\|\psi\widetilde{\psi}-1\|_F\) dual-checked. Chiral \(\langle\psi I\widetilde{\psi}\rangle_0\) structurally ~0 in real Cl(4,1) (honest; #19 family).
- Standing-wave registry + `resonant_recall` (session-local; durable via `HolographicVaultStore`).
- `core_ha` standalone atlas: **deprecated** (no live tree; hygiene pin + Phase 0 grep).

### Acceptance (behavioral)
| Pin | Status |
|-----|--------|
| Unitary / sandwich step residual \(< 10^{-6}\) | 🟢 |
| Spectral leakage zero on-span / positive off-span / metric-exact | 🟢 |
| Wave polar recovers known sandwich rotor | 🟢 (single-pair conjugacy) |
| Multi-pair `wave_field_conjugacy` + Procrustes sequence path | 🟢 thin wrap over `_field_conjugacy_versor` (true \(\mathcal{C}_{AB}\) polar proven mathematically ill-posed for multigrade fields) |
| Chiral conserved under left \(R\); even versor ~0 | 🟡 honest vacuous Q on real Cl(4,1) |
| Resonant recall picks registered mode; empty refused | 🟢 |
| Superposition reconstruct \(\sum c_k\psi_k\) | 🟢 `resonant_reconstruct` |
| Phase correlation \(\rho\) (I-04 algebra) | 🟢 `phase_correlation` (sensorium feed still open) |
| Surprise / GoldTether / biography delegate to wave | 🟢 |
| No teaching import in `wave_manifold`; no `core_ha` package | 🟢 |
| Serve path not wired to wave / Fibonacci (containment) | 🟢 (AST-pinned in cohesion suite) |
| Entity I-01…I-05 cohesion suite | 🟢 progressive pins in `test_third_door_cohesion.py` (I-02 float32-honest) |
| Vault public `get_versor` ABI | 🟢 |
| Golden-Angle atlas packing \(d_{\min}=0.12\) | 🟢 ADR-0242 (`atlas_packing`; CGA null-point \(d\)) |
| Fibonacci κ search | 🟢 ADR-0242 (`fibonacci_search`) |

### Subsumption map (Slice 2–3)
| Operator | Delegation |
|----------|------------|
| `surprise_residual` (32-vec) | `WaveManifold.compute_spectral_leakage` |
| `conformal_procrustes` single non-null pair | `wave_analogical_polar` |
| `conformal_procrustes` multi non-null pairs | `wave_field_conjugacy` (thin wrap) |
| Null-point / (5,K) clouds | Kabsch retained (compatibility) |
| `coherence_residual` / GoldTether drift | `measure_unitary_residual` (+ chiral term) |
| `integrate_biography` | unitary lock-in + mode register + resonant_recall; encode `holonomy_encode` |

### Deferred (explicit, not namesake green)
- Durable holographic memory **vault store** — 🟢 `core/physics/holographic_vault.py` (VaultStore-backed SPECULATIVE spectrum; restart lock-in; public `get_versor` ABI).
- Analytic vector-style Clifford polar \(R=C(\widetilde{C}C)^{-1/2}\) for **general multi-grade** fields — ⚪ RETIRED (ill-posed; sandwich conjugacy via `_field_conjugacy_versor` is authority). Grade-1-only polar remains theoretically valid but is not the wave-field API.
- Non-vacuous pair-spinor chiral charge (P8).
- Rust/MLX acceleration of exp-map (ADR-0235 later).
- Full ADR-0092 reviewer-service integration (promote remains caller-gated).
- Optional Rust Ring-1 port of trajectory invariants (Python is authority today).

---

## 13. Tracked follow-ups

| Gap | Issue |
|---|---|
| Real Cartan–Iwasawa via `n_o`/`n∞` — 🟢 done (null-point peel + Spin remainder) | #16 (closed via #29) |
| Kabsch-conformal Procrustes on point sets — 🟢 done | #17 (closed via #29) |
| GoldTether gold-set + harmonized residual + α=Φ(R) + bootstrap/prune — 🟢 | #18 |
| Grade-5 pseudoscalar preservation gate — ⚪ RETIRED (vacuous; see §5) | #19 (closed) |
| Surprise: metric projection + productivity polarity + DiscoveryCandidate wiring — 🟢 done | #20 (math #26; wiring #31) |
| Trajectory invariants + ADR-DAG embedding — 🟢 Python surfaces | #21 |
| Wave-field local operators + subsumption (W1–W6) — 🟢 local / 🟡 entity mastery | ADR-0241 |
| `core_ha` deprecation — 🟢 no live tree + hygiene + Phase 0 grep | ADR-0241 / deprecation plan |
| Durable holographic vault spectrum — 🟢 HolographicVaultStore | ADR-0241 |
| Entity cohesion I-01…I-05 + Trace A/B | cohesion master plan |
| Atlas packing + Fibonacci κ (ADR-0242) — 🟢 packing + search | PR #37 / ADR-0242 |

Closing a gap = flip its `xfail` in `tests/test_third_door_blueprint_fidelity.py` (or the ADR-0241 / cohesion suite) to a passing behavioral test and delete the matching characterization lock. That is the definition of "done right" here.
