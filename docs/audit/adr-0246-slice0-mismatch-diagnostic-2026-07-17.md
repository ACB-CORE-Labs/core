# ADR-0246 Slice 0 — Benign Nominal-Frame Mismatch Diagnostic (Evidence Packet)

**Date:** 2026-07-17
**Branch:** `feat/adr-0246-slice0-diagnostic` (fresh worktree off post-D4 `main @ 5027adf8`)
**Scope ruling:** diagnostic-only. This slice does **not** retune γ_id, relax the
D4 admission surface, enlarge `H_id` beyond `{I}`, change identity axes, enable
`identity_wave_gate`, or add any geometric corrector. No serving code was modified.
**Instruments:** ADR-0246 preflight brief §3 primitives — induced action `A(F)`,
`d_orth`, `d_stab` against the locked singleton stabilizer `H_id={I}`, per-axis
leakage/self-alignment (D4 primitives), and typed residual channels pinned to
explicit blade indices (e4=grade-1 index 4, e5=grade-1 index 5).
**Code:** `evals/adr_0246_mismatch_diagnostic/` (eval-only; A-04 quarantine intact)
· pins: `tests/test_adr_0246_mismatch_diagnostic.py` (16 green)
· raw packet: `docs/audit/artifacts/adr-0246-slice0-evidence-packet.json`.

---

## 1. Question

D4 Phase 3 measured that real benign `final_state.F` versors do not preserve the
declared value subspace `span(e1,e2,e3)` (leakage 0.14–0.81, best balanced error
0.346) and hypothesized the root cause as "nominal axes, not dynamically-preserved
eigenmodes." This slice **tests** that hypothesis against the full candidate list:

1. lawful in-span action (rotation/permutation invisible to leakage)?
2. genuine foreign leakage (axes leave the span)?
3. precision / f64↔f32 transport behavior?
4. path accumulation (small per-turn, compounding)?
5. absence of semantic coupling between the declared placeholder frame and live cognition?

## 2. Method

Four trace classes were decomposed identically:

| Class | Source | n |
|---|---|---|
| synthetic | brief §6.1 constructions (identity, in-span rotations incl. 90° permutation and π inversion, e14/e24 tilts, e15/e25 boosts, mild drift) | 9 |
| adversarial | D4 calibration attack set + π inversion | 5 |
| benign | live `ChatRuntime` wave-path versors over the D4 `LIVE_PROBE_SEQUENCE` (same probe set as the Phase-3 leakage pin; instance-local recording wrapper, serving untouched) | 13 |
| paraphrase | live versors over a paraphrased probe set | 12 |

Per trace: `A(F)` (3×3 induced action), `d_orth = ‖AᵀGA−G‖_F`,
`d_stab = ‖A−I‖_F` (G = I₃ exactly for the default pack), per-axis
leakage/self-alignment, residual energy typed into
`null_or_conformal` (e4) / `boost_like` (e5) / `spatial_foreign` (structurally
empty for the default pack) / `unclassified` (higher-grade or numerical, fail-closed),
bivector-plane occupancy of F itself, and an f64→f32→f64 transport delta on `A`.
Suite-level: raw-path composition curve and a semantic-coupling control comparing
declared-frame leakage against 3 named alternative frames and 32 seeded random
orthonormal 3-frames inside the positive-definite grade-1 block `span(e1..e4)`.

Classifier ground truth: all 9 synthetic constructions land in their intended
mechanism class (pinned by tests) — the instrument distinguishes lawful action,
in-span-unlawful action, e4-typed tilt, and e5-typed boost before it is pointed
at live traffic.

## 3. Results

### 3.1 Mechanism classification (the headline)

**All 25 live benign/paraphrase turns classify as `foreign_leakage`.** Zero
classify as lawful-in-span, zero as in-span-unlawful, zero as numerical.

| Candidate mechanism | Verdict | Evidence |
|---|---|---|
| Lawful in-span action | **No** | no live turn has ℓ_rms ≤ 0.02; the mismatch is not a hidden rotation/permutation within the span |
| Foreign leakage | **Yes — the mechanism** | every live turn; residual energy is 100% typed onto grade-1 e4/e5 (unclassified ≤ 1e-9 on all 25 turns) |
| Precision / transport | **No** | max f64→f32→f64 induced-action delta = 3.6e-5 across every trace — 4+ orders below the observed effect |
| Path accumulation | **No** | per-turn `d_stab` is already 0.15–813.8 (mean 71.9); no lawful chain exists to accumulate. This is not slow drift evading a per-turn threshold |
| Semantic coupling absent | **Yes — confirmed** | declared-frame mean leakage 0.572 sits inside the random-control-frame distribution [0.552, 0.655] (mean 0.596); 34% of random frames leak *less* than the declared frame; `frame_e1e2e4` also leaks less (0.537). The dynamics do not prefer the declared frame over arbitrary alternatives |

### 3.2 The foreign leakage has two distinct benign sub-populations

The typed channels + plane occupancy of F resolve structure D4's scalar leakage
could not see:

**Population A — boost-involved (18/25 turns; the high-leakage cluster).**
ℓ_rms 0.47–0.81, `boost_like` (e5) channel 0.17–0.50, F carrying substantial
grade-2 energy in the **e5-mixing planes** (e15/e25/e35, often ≈ 0.5 of grade-2
energy), `d_orth` from 0.84 up to 6.6×10⁵ — the action is non-isometric,
cosh-stretching from boost content — and self-alignment frequently driven
negative (to −0.71). Several of these versors also carry O(1) grade-4 energy
(up to 11.1) — general even-grade versors, not simple rotors.

**Population B — pure e4 tilt (7/25 turns; the moderate cluster).**
ℓ_rms 0.14–0.33, `null_or_conformal` (e4) channel fires with `boost_like`
**exactly 0**, e4-mixing plane occupancy up to 0.98, `d_orth` small (0.06–0.26 —
the action is near-isometric), self-alignment positive (0.80–0.89). These are
genuine conformal/null-direction tilts, not stretches.

**In both populations the residual is fully accounted for by the typed e4/e5
channels** — `unclassified` ≤ 1e-9 everywhere. The sandwich output stays exactly
grade-1; there is no numerical contamination. The mismatch is a *lawful property
of the dynamics acting in conformal/boost planes*, not corruption.

### 3.3 What this pins down mechanistically

The live cognitive versor's generators live substantially in the spatial↔e4/e5
mixing planes (e14/e24/e34, e15/e25/e35, e45). Any spatial 3-frame — the declared
one or a random one — gets tilted toward e4 and stretched along e5 by ordinary
benign cognition. That is why:

- leakage is large and broadband on benign traffic (D4's measurement),
- no threshold separates benign from geometric attacks (D4's 0.346 balanced error),
- and the declared frame is statistically unspecial (this slice's control ensemble).

The D4 root-cause hypothesis is **confirmed and sharpened**: the failure is not
that the frame is merely mislabeled within the spatial block (an in-span rotation
of labels would show `in_span_unlawful` with ℓ≈0 — observed zero times); it is
that *no fixed spatial grade-1 frame is dynamically stabilized at all*. Identity
preservation as posed by ADR-0244 §2.1 is not a property the current field
evolution possesses with respect to any nominal spatial frame.

## 4. Consequences for ADR-0246 proper (no decisions taken here)

Measurement-driven implications, recorded for the ADR-0246 design — explicitly
**not** acted on in this slice:

1. **An induced-identity action must couple to what the dynamics actually
   stabilize, not to a declared spatial frame.** Candidate identity carriers
   should be sought among structures the evolution preserves (e.g. invariant
   subspaces/eigenmodes of the observed `A(F)` family), then given semantic
   assignment — the reverse of the current nominal-label direction.
2. **The e5/boost channel is the dominant benign departure mode** and is
   non-isometric (huge `d_orth`); any future lawfulness metric that assumes
   isometric action on a fixed frame will misclassify ordinary cognition.
   The brief's separation of `d_orth` from `d_stab` is validated by live data.
3. **Path integrity is not the missing piece for the benign story** — per-turn
   action is already far from I. The §3.4 ledger remains right for its own
   threat model (slow drift), but it will not explain or fix benign refusal.
4. **Precision transport is immaterial** at the current scale (3.6e-5 ceiling);
   the f32 serving cast is not implicated in the mismatch.
5. The typed-channel + plane-occupancy instruments transfer directly into the
   future `IdentityActionRecord` (brief §4.1) with zero unaccounted residual on
   real traffic — the fail-closed `unclassified` channel is empirically quiet.

## 5. Verification

- `tests/test_adr_0246_mismatch_diagnostic.py` — 16 passed (ground-truth
  classification pins, blade-index pins, A-04 non-import pin, gate-surface
  untouched pin: `identity_wave_gate` default off, `_WAVE_LEAKAGE_BOUND`
  unchanged at 0.2126624458513829).
- Live capture via instance-local `IdentityCheck` recording subclass on a fresh
  empty-vault `ChatRuntime(identity_wave_gate=True, no_load_state=True)` —
  measurement-only; the flag remains default-off in `RuntimeConfig`.
- Raw JSON packet: `docs/audit/artifacts/adr-0246-slice0-evidence-packet.json`
  (schema `adr_0246_slice0_diagnostic_v1`).
