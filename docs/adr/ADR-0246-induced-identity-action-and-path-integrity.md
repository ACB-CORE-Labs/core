# ADR-0246: Induced Identity Action and Path Integrity

**Status**: **Accepted**
**Date**: 2026-07-18
**Authors**: Joshua Shay + multi-model R&D (Fable 5 scaffold → Opus 4.8 adversarial audit + hardening → Sonnet 5/Fable 5 completion; per-model provenance in §9)
**Preflight**: `docs/briefs/ADR-0246-induced-identity-action-and-path-integrity-preflight.md` (locked decisions §3, non-goals §7 — all honored; execution log §0a)
**Depends on**: ADR-0244 (operator-preservation identity gate, Accepted), ADR-0245 (mechanical sympathy + semantic rigor, Accepted)
**Related**: slice-0 evidence `docs/audit/adr-0246-slice0-mismatch-diagnostic-2026-07-17.md` (merged, quarantined diagnostic); Opus audit `docs/audit/adr-0246-slice1-opus-audit-and-hardening.md`

---

## 1. Context and problem

D4 (ADR-0244) built the per-turn operator-preservation floor: does the live
cognitive versor `F` preserve the frozen identity frame `I = span(a₁…aₙ)`,
measured by per-axis subspace leakage `ℓᵢ` and signed self-alignment `sᵢ`? Two
gaps were deliberately left open (preflight §2):

1. **Lawfulness inside the span** — leakage is blind to in-span reshuffles: a
   rotor permuting `e1→e2` or inverting `e1→−e1` has `ℓ≈0` yet is not the
   identity-preserving action.
2. **Accumulation across turns** — per-turn thresholds cannot see slow drift:
   many individually-admissible small rotations compose into a large one.

This ADR closes both with the **induced action** `A(F)` on the frame, two
never-collapsed diagnostics (`d_orth`, `d_stab`), a locked lawful-stabilizer
policy `H_id={I}`, typed residual channels, a lawful-only path ledger with hard
breaks, a per-turn admit surface, and full per-turn/per-session telemetry — all
flag-gated default-off at serve.

**Claims language (binding, §10 #9 of the preflight):** everything this ADR
instruments is **lawfulness relative to the declared frozen frame**. It does
NOT establish, and must never be quoted as establishing, any semantic
inalienability of the value labels themselves — the shipped axes
(`truthfulness=e1`, `coherence=e2`, `reverence=e3`) remain placeholder
orthonormal directions with no demonstrated dynamical or semantic grounding
(see §6, §7).

## 2. Decisions (as implemented; preflight §3 locked decisions honored)

### 2.1 Induced action matrix `A(F)`

`A_kj(F) = (G⁻¹)_km ⟨a_m, F a_j F̃⟩₀` — the full in-subspace action of the
versor on the frame (`core/physics/identity_manifold.py::IdentityManifoldGeometry.induced_action`).
Raw/unnormalized: a boost's cosh-stretch shows in column norms and in `d_orth`,
never hidden. Bit-exactness against an independent re-derivation was verified
in the Opus audit (max discrepancy 0.00e+00).

### 2.2 Two diagnostics, never collapsed

- `d_orth(F) = ‖A(F)ᵀ G A(F) − G‖_F` (`orthogonality_defect`) — G-isometry /
  numerical-integrity check. **Not** an authorization policy.
- `d_stab(F) = min_{H∈H_id} ‖A(F) − H‖_G` (`identity_action.py::stabilizer_defect`)
  — the lawfulness distance from the permitted identity actions.

**Norm convention (ruling requested — §7 item 1):** `‖M‖_G ≡ ‖G^{1/2} M G^{-1/2}‖_F`,
computed via `eigh` of the SPD Gram; reduces exactly to Frobenius at `G=I`
(the only shipped pack). This is the metric-consistent choice (invariant under
G-orthogonal reparameterization of the axes); ratifying this ADR ratifies the
convention.

### 2.3 Lawful stabilizer — locked singleton

`H_id = {I}` (`IdentityStabilizer.singleton`), hardcoded in the path-advance
(no enlargement parameter exists). `−I`, permutations, `O(n)`/`SO(n)`
rotations, and reweightings are excluded; enlarging `H_id` is a future explicit
reviewed pack/policy change. No soft-projection of an unlawful `A` onto `I`
exists anywhere (grep-audited; pinned by tests).

### 2.4 Path integrity — lawful-only composition (F1 semantics, ratification-relevant)

`advance_identity_path` (§3.4/§3.5) composes the session path
`A_path = A_T ⋯ A_1` from **only** the turns certified lawful, where lawful ≡
**admitted by the per-turn policy (§3.4 step 2)** AND `d_stab(A_t) ≤ ε_turn`.
Refused or ill-conditioned turns insert a **break marker** and are excluded —
never a soft-projected `I` masquerading as a pass; the raw product is exposed
only as `raw_path_product` (forensic; a test fails if it ever equals the lawful
path in a mixed sequence).

**F1 composition semantics (audit finding, hereby put to ratification):** a
lawful turn composes its *actual certified action* `A_t`, not a literal element
of `H_id`. This is required, not convenience — composing literal `I`s would
make `A_path ≡ I` and blind the ledger to exactly the slow drift it exists to
catch. "Compose lawful `H_t`" in preflight §3.4-step-4 is READ as "compose the
per-turn actions that were certified lawful."

**Hard breaks (§3.5):** a new chain (fresh `chain_id`, path not continued)
starts on any change of pack content digest / geometry version / gate+policy
version / session — each dimension is pinned by a test. **Turn ownership at a
hard break (ruling requested — §7 item 3):** the boundary turn belongs to the
NEW chain (it composes into the fresh path if lawful). Biography holonomy stays
a separate process; nothing here rewrites identity axes.

**Budgets:** `d_stab(A_t) ≤ ε_turn` per turn and `d_stab(A_path) ≤ ε_session`
per session — both ε are **UNCERTIFIED placeholders** (§5), so the session
verdict (`session_admit`) is telemetry only.

### 2.5 Typed residual channels — pinned blade map

On each axis rejection `r = F a F̃ − P_I(F a F̃)` (`typed_residual_energy`),
energy splits into: `null_or_conformal` (e4 = grade-1 index **4**),
`boost_like` (e5 = grade-1 index **5**), `spatial_foreign` (grade-1 spatial
slots **1/2/3** outside the pack's axis support), `unclassified` (everything
else — fail-closed, **no correction policy ever attaches to it**). Blade
indices are pinned against `algebra.cl41.basis_vector` in tests
(`test_blade_index_constants_match_algebra`). For the default full-span pack,
`spatial_foreign` is **tautologically zero** (the rejection is orthogonal to
the whole spatial block); it fires correctly for reduced-support packs —
resolved and pinned (§7 item 2).

### 2.6 Per-turn admit surface (§3.7) — admit-or-abstain only

`evaluate_admission(geometry, F, policy)` admits iff `d_orth ≤ orth_tol` AND
`d_stab ≤ ε_turn` AND `leakage_rms ≤ γ_id` AND `max ℓᵢ ≤ τ_max` AND
`min sᵢ ≥ s_min` AND no boundary breach AND no unclassified-channel firing;
otherwise refuses naming every failed condition. **No geometric `C_id`
corrector exists** — the egress model remains D4's
`conjugate_correct(refuse=True)` abstention. A malformed versor raises
`MalformedVersorError` (fail-closed; never a silent legacy fallback when a
wave field was supplied).

### 2.7 Serve wiring — flag-gated, default-off, byte-identical off

- New `RuntimeConfig.identity_action_surface: bool = False` (separate from
  `identity_wave_gate`; acts only when the wave gate is also on).
- `chat/runtime.py → IdentityCheck.check(admission_policy=…) → _wave_field_score`:
  a §3.7 refusal folds into `flagged`, so the existing `would_violate` egress
  abstains. `IdentityScore` gains `action_surface_active`/`d_orth`/`d_stab`/
  `action_record` with legacy defaults — flag-off is byte-identical (all D4
  gate surfaces green unchanged; smoke green post-wiring).
- The session path ledger is advanced per wave-path turn under the same flags,
  **observe-only** (`advance_session_identity_path`): `session_admit` is
  telemetry, never an egress decision, because `ε_session` is uncertified and
  live activation remains unauthorized.

### 2.8 Telemetry (§4.1/§4.2/§4.3)

- `IdentityActionRecord` (schema `identity_action_v1`): turn/trajectory/pack
  ids, **full-SHA-256** pack-content digest + `field_digest` (LE f64 bytes) +
  `record_digest` (canonical JSON, no `default=str`), geometry/gate/policy
  versions (`policy_version = AdmissionPolicy.version_id()`, full SHA-256 of
  the exact threshold set), `A_raw`, `d_orth`, `d_stab`, leakage/self-align
  vectors, typed channels, `admitted`, `refusal_reason` (all failed conditions
  joined with `;` — a deliberate widening of the preflight's singular field so
  multi-condition refusals lose nothing), `lawful_action ∈ {"I","none"}`
  (never a matrix), `path_break`.
- `IdentityPathLedger` (schema `identity_path_v1`): `chain_id` (full SHA-256
  of scope + chain index), lawful path, `d_stab_path`, composed/break counts,
  `session_admit`, `ledger_digest`.
- The JSONL turn serializer emits `identity_d_*`/`identity_action_*`/
  `identity_path_*` keys **only when the respective path ran** — the flag-off
  wire format is byte-identical (pinned by tests).

## 3. Evidence — §6 eval matrix (all green) and the honest discrimination result

- **§6.1 synthetic geometric suite** (9 cases) + **§6.2 path/holonomy suite**
  (5 cases): `evals/adr_0246_geometric_suite` — 14/14; every construction in
  the preflight tables pinned individually (identity versor, π-inversion
  `s=−1`, 90° permutation `s=0`, mild drift, e14 tilt, e15 boost,
  near-singular Gram → `ManifoldConditioningError`, malformed F → typed error;
  lawful sequence, accumulation-to-session-refusal, interleaved breaks,
  pack-change hard break, raw≠lawful forensic).
- **§6.3 discrimination report** (`evals/adr_0246_discrimination`;
  live benign n=13, adversarial n=8, synthetic-near-identity control n=5;
  artifact `docs/audit/artifacts/adr-0246-slice1-discrimination-report.json`):

  | benign pass | false refusal | adversarial detect | control pass | d_stab AUC (95% CI) |
  |---|---|---|---|---|
  | **0.00** | **1.00** | 1.00 | **1.00** | **0.375** [0.15, 0.62] |

  **Honest finding:** on the declared placeholder frame the admit surface
  refuses benign and adversarial versors **alike** — benign cognition sits
  ~18× farther from the frame (mean `d_stab` 27.8) than the crafted attacks
  (1.55), so `d_stab` discriminates *below chance*. The near-identity control
  passing 100% proves the mechanism is sound; the failure is entirely that
  benign cognition does not live near the declared frame. A refuse-everything
  gate trivially "detects" attacks but is **not a discriminator**.
- **§11 grounding-feasibility study** (`evals/adr_0246_grounding_feasibility`;
  artifact `docs/audit/artifacts/adr-0246-grounding-feasibility-report.json`):
  fixed TRAIN (live benign, n=13) / HELD-OUT (independent paraphrase cohort,
  n=12) / ADVERSARIAL (n=8) splits; bivector-block generator proxy (numpy-only;
  exact for simple rotors/boosts, first-order otherwise); sample-size-calibrated
  null distribution (200 trials of independent pure-noise cohort pairs at the
  real n) with a shared-basis positive recovery control; precision pairs
  (f64↔f32) and per-plane generator-energy analysis.

  **Result: NULL, with the method itself validated.** The positive control
  (two independent cohorts sharing one true rank-2 subspace) recovers at
  cosine 0.9995 — the 100th percentile of the same-sample-size null (p95 =
  0.60) — so the instrument can find real structure at n=12. The real cohorts
  do not show it: TRAIN→HELD-OUT top-2 cosine 0.52 sits at only the **87th
  percentile of pure chance** (need ≥ 95th); residual-based discrimination is
  AUC **0.49** (chance; CI [0.21, 0.77]); generator energy is spread across
  all 10 bivector planes in both cohorts; precision transport is immaterial
  (max bivector delta 6.9e-7). Benign cognition has no small, stable,
  cohort-independent generator subspace detectable at this sample size — the
  D4/slice-0/§6.3 finding now holds at the GENERATOR level too. Threshold
  tuning cannot produce a discriminating gate; a revised implementation
  contract is not justified on this evidence. The full `honest_finding` text
  in the artifact is binding for any downstream claim; a much larger,
  pre-registered cohort would be needed to rule out a subtle real effect.

## 4. Operational status (machine-readable)

```yaml
identity_action_surface:
  implementation: proposed        # this ADR; code merged flag-off
  live_activation: not_authorized # D4 ratified limitation carries over
  default: off
  blocker: >
    §6.3 shows no benign/adversarial separation on the declared frame
    (AUC 0.375, benign false-refusal 1.00); thresholds beyond gamma_id
    are uncertified placeholders.
  activation_requires:
    - held-out-stable, safety-relevant grounding result (§11 programme)
    - calibrated epsilon_turn/epsilon_session/tau_max/s_min certificates
    - renewed discrimination evidence with acceptable benign refusal rate
    - explicit human ratification
identity_wave_gate:
  unchanged: true  # ADR-0244 Accepted-with-limitation posture untouched
```

## 5. Uncertified placeholders (enumerated; never live defaults)

| Constant | Value | Status |
|---|---|---|
| `gamma_id` | 0.2126624458513829 | **CERTIFIED** (D4 Phase 3 Fibonacci certificate `0079b5f2…`); pinned equal to `identity._WAVE_LEAKAGE_BOUND` by test |
| `epsilon_turn` | 0.1 | placeholder |
| `epsilon_session` | 0.3 | placeholder |
| `tau_max` | = γ_id | placeholder |
| `s_min` | 0.0 | matches D4's fixed orientation floor (geometric invariant, not tuned) |
| `orth_tol` | 1e-6 | placeholder |
| `unclassified_tol` | 1e-6 | placeholder |

`AdmissionPolicy.placeholder_default()` carries `calibrated=False`; a serve
gate must never treat an uncalibrated policy as license to activate.

## 6. What this ADR does NOT do (preflight §7 non-goals — all honored)

No geometric `C_id`/corrector; no Ring-2 residual protocol; no semantic axis
grounding or pack redesign; no biography-holonomy merge; no atlas/VSWR work;
no analytic cast reactance; no grade-1 versor projection (proven vacuous); no
indefinite-norm leakage; no `H_id` enlargement; no soft-projection; no
default-on serve gate; no Smith-chart algebra; no status flip of ADR-0244/0245.

## 7. Resolved and open questions

1. **`‖·‖_G` convention** — implemented as `‖G^{1/2}MG^{-1/2}‖_F`; **ratify
   with this ADR** (§2.2).
2. **`spatial_foreign` channel** — RESOLVED: tautologically zero for the
   default full-span pack; fires correctly for reduced-support packs (pinned:
   `test_spatial_foreign_channel_fires_for_reduced_support_pack`).
3. **Hard-break turn ownership** — implemented as new-chain; **ratify with
   this ADR** (§2.4).
4. **Malformed-F/gate routing** — the D4 wave-path validator raises before the
   admission surface runs; `MalformedVersorError` from the pure primitives
   propagates fail-closed. No silent legacy fallback exists when a wave field
   was supplied. Unifying the two typed errors is left to a future cleanup.
5. **OPEN (future ADR):** semantic axis grounding — blocked on a positive §11
   result at adequate sample size; `ε` calibration; `H_id` policy products.

## 8. Consequences

- The identity organ now measures *everything* the preflight demanded —
  in-span lawfulness, isometry integrity, typed foreign leakage, and
  path accumulation — with serve byte-identity preserved and zero live policy
  change. What it measures says, honestly: the declared frame is not the
  structure live cognition preserves, so the gate stays off and the next
  investment belongs to grounding, not thresholds.
- All future identity work inherits content-addressed, full-digest telemetry
  (records + ledger) and a single pure source of truth for the §3 primitives.

## 9. Provenance

Fable 5: slice-0 diagnostic; §3 primitives + §3.4/3.5 ledger + §6.1/6.2 suites
(RED-first); this completion pass. Opus 4.8: adversarial audit (bit-exact math
re-derivation; H_id/soft-projection/scope-creep verification), F1 finding,
§3.7 surface + serve wiring, §6.3 discrimination report. Sonnet 5: §4.1/§4.2
telemetry records, `admitted` gate on the ledger (F1-adjacent §3.4-step-2
compliance), path serve integration (observe-only), §11 feasibility study
design. Every stage: local-first CI (smoke + targeted suites) before commit;
no self-Accept at any point.
