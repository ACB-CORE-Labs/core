# ADR-0246 Preflight Brief — Induced Identity Action and Path Integrity

**Status:** Draft preflight (not yet an ADR; not authorized for implementation until D4 closes)  
**Date:** 2026-07-17  
**Authors:** Joshua Shay + multi-model R&D assessment  
**Working title for future ADR:** *Induced Identity Action and Path Integrity*  
**Depends on:** ADR-0244 (operator-preservation identity gate), ADR-0245 (mechanical sympathy + semantic rigor), D4 completion (Phases 2c–6)  
**Does not interrupt:** live D4 work on `feat/adr-0244-d4` / worktree `core-adr0244d4`

> **Authority of this document.** This brief freezes the post-D4 thin-slice design agreed in the R&D implementation assessment. It is the planning baseline for the next identity ADR series. It is **not** a status flip of ADR-0244/0245, not a license to expand D4 mid-flight, and not an Accepted ADR. Implementation of ADR-0246 begins only after D4 Phase 6 acceptance packets exist (or an explicit Shay waiver).

---

## 0. Why this preflight exists

D4 answers a narrow, foundational question:

> Does the live cognitive versor \(F\) preserve the frozen identity frame \(I\) sufficiently to proceed this turn?

That is operator-preservation via sandwich \(F a_i \widetilde{F}\), leakage \(\ell_i\), and signed self-alignment \(s_i\).

ADR-0246 must answer the next, different questions:

1. Even if action stays inside \(I\), is it a **lawful** action on that frame?
2. Even if each turn is locally admissible, is lawful action **accumulating** over a path in a way that violates session budgets?

Without these, a per-turn leakage gate can pass while identity is reshuffled in-plane or slowly rotated across many turns.

**Sequencing (locked):**

```text
Ring 0  D4 / ADR-0244 + ADR-0245   integrity floor (in flight)
Ring 1  ADR-0246                  induced action + path integrity   ← this brief
Ring 2  later ADR(s)              multi-port residual protocol
Ring 3  later program             composition / world-model / governed learning
```

Do **not** insert Rings 1–3 into active D4 commits.

---

## 1. Authority documents

| Doc | Role |
|-----|------|
| `docs/adr/ADR-0244-wave-field-identity-manifold-and-inalienable-geometric-alignment.md` | Identity consumer; §4a + governance annotation items 1–12 govern |
| `docs/adr/ADR-0245-cga-unification-mechanical-sympathy-and-semantic-rigor.md` | Mechanical sympathy + digest rigor foundation |
| `docs/handoff/ADR-0244-D4-IMPLEMENTATION-PLAN.md` | Live D4 phases, ratified decisions #1–#10, resume dashboard |
| `core/physics/identity_manifold.py` | Grade-1 lift, Gram, sandwich, Euclidean leakage, normalized axis_response |
| `core/physics/identity.py` | Dual-mode gate, admit-or-abstain `conjugate_correct`, `IdentityGateRefusal` |
| `AGENTS.md` | `versor_condition`, no ANN, teaching/mutation standing, local-first CI |
| Post-D4 R&D assessment (session 2026-07-17) | Ring plan; Smith as control grammar not second algebra |

---

## 2. Problem statement (what D4 deliberately leaves open)

D4 measures:

\[
a_i' = F a_i \widetilde{F},\qquad
\ell_i = \frac{\|a_i' - P_I(a_i')\|_2}{\|a_i'\|_2},\qquad
s_i = \frac{\langle a_i, a_i'\rangle_0}{\|a_i\|_2\,\|a_i'\|_2}
\]

with aggregate `leakage_rms` and (today) a weak self-alignment floor at \(0\).

**Gaps this ADR closes:**

| Gap | Failure mode if left open |
|-----|---------------------------|
| No full induced action \(A(F)\) | In-plane permutations/rotations partially invisible |
| No \(d_{\mathrm{orth}}\) | Non-isometric / numerical corruption confusable with policy |
| No \(d_{\mathrm{stab}}\) / \(H_{\mathrm{id}}\) | “Inside the span” treated as “authorized” |
| No path ledger | Slow multi-turn drift evades per-turn thresholds |
| Raw path product of all \(A_t\) | Numerical contamination treated as identity holonomy |
| No typed alien residual channels | Boost-like (e5) vs spatial foreign (e4) vs other collapsed |

**Honesty constraint (from D4 progress log):** default pack axes are still placeholder orthonormal R³ labels (`truthfulness→e1`, `coherence→e2`, `reverence→e3`). ADR-0246 instruments **lawfulness relative to the declared frame**. It does **not** by itself prove those labels have independent semantic geometry. Semantic axis grounding is a separate later workstream (see §11).

---

## 3. Locked decisions (preflight freezes)

### 3.1 Induced action matrix \(A(F)\)

For frozen grade-1 axes \(\{a_j\}\) and Gram \(G_{ij}=\langle a_i,a_j\rangle_0\):

\[
A_{ij}(F)
=
\bigl(G^{-1}\bigr)_{ik}\,
\langle a_k,\; F a_j\widetilde{F}\rangle_0
\]

Properties:

- When \(F\) preserves \(I\) isometrically, \(A\) is \(G\)-orthogonal: \(A^\mathsf{T} G A = G\).
- Captures **all in-subspace action**, including permutations and rotations that leakage misses.
- Built only from existing D4 primitives (Gram, signed inner product, sandwich). No new algebra package.

### 3.2 Two distinct diagnostics (never collapsed)

\[
d_{\mathrm{orth}}(F)
=
\bigl\| A(F)^\mathsf{T} G A(F) - G \bigr\|_F
\]

\[
d_{\mathrm{stab}}(F)
=
\min_{H\in H_{\mathrm{id}}}
\| A(F) - H \|_G
\]

| Diagnostic | Detects | Must not be mistaken for |
|------------|---------|---------------------------|
| \(\ell_i\) | Departure from frozen subspace \(I\) | In-subspace permutation/rotation |
| \(s_i\) | Opposition/inversion of a single axis | Full relational action between axes |
| \(d_{\mathrm{orth}}\) | Numerical failure or non-isometric action on \(I\) | Semantic authorization policy |
| \(d_{\mathrm{stab}}\) | Departure from explicitly permitted identity action | Merely a conditioning check |

**Norm conventions (inherit D4):**

- Projection geometry / Gram: indefinite Cl(4,1) metric \(\langle\cdot,\cdot\rangle_0\).
- Leakage **magnitude** and residual energy channels: positive-definite coefficient-Euclidean norm.
- Signed overlaps: never `abs()`'d.

### 3.3 Lawful stabilizer \(H_{\mathrm{id}}\) (default pack)

**Locked for default identity pack:**

\[
H_{\mathrm{id}} = \{ I \}
\]

where \(I\) is the identity matrix in the axis basis (not Cl(4,1) identity multivector).

**Explicitly excluded from default \(H_{\mathrm{id}}\):**

- \(-I\) (global inversion) — algebraically clean, **not** semantically lawful
- Axis permutations
- Continuous rotations in \(O(n)\) or \(SO(n)\)
- Arbitrary reweightings

Rationale: algebraic cleanliness ≠ identity lawfulness. Enlarging \(H_{\mathrm{id}}\) is a **future, explicit, reviewed** pack/policy change — never an implicit implementation convenience.

**Nearest-lawful projection rule under singleton stabilizer:**

When \(H_{\mathrm{id}}=\{I\}\), there is **no continuous projection that invents a lawful action**. The policy is pass/fail:

\[
d_{\mathrm{stab}}(F) = \|A(F)-I\|_G \le \epsilon_{\mathrm{turn}}
\quad\text{or refuse}
\]

Do **not** soft-project \(A\) onto \(I\) and then compose the projection as if the turn were lawful.

### 3.4 Path integrity — lawful-only composition (mandatory)

**Forbidden:**

\[
A_{\mathrm{path}} = A(F_T)\cdots A(F_1)
\quad\text{over raw }A(F_t)\text{ unconditionally}
\]

Raw products mix refused, ill-conditioned, and leaked actions into “identity holonomy.” That is a category error.

**Required protocol per turn \(t\):**

1. **Record raw** \(A_t = A(F_t)\), leakage vector \(\ell\), signed align \(s\), typed residual channels, digests, gate version.
2. **Admit only if** \(\ell\)-policy, \(d_{\mathrm{orth},t}\), and per-axis policy pass (same fail-closed doctrine as D4).
3. **Lawful action:** with \(H_{\mathrm{id}}=\{I\}\), either certify \(A_t\) within \(\epsilon_{\mathrm{turn}}\) of \(I\), or **do not** mark lawful.
4. **Compose path only from lawful/certified actions:**
   \[
   A_{\mathrm{path}} = H_T \cdots H_1
   \]
   time-forward, left-to-right as successive action on the axis frame. Skipped/refused turns insert a **break marker**, not an identity matrix masquerading as a pass.
5. **Store raw and lawful separately** for replay and forensics. Never overwrite raw with projected values.

**Path budgets (session-scoped defaults; exact numbers calibrated post-D4):**

\[
d_{\mathrm{stab}}(F_t) \le \epsilon_{\mathrm{turn}},\qquad
d_{\mathrm{stab}}(A_{\mathrm{path}}) \le \epsilon_{\mathrm{session}}
\]

### 3.5 Ledger scope and hard breaks

An identity-action ledger is **versioned and scoped**. A new chain **must** start when any of the following change:

| Break condition | Why |
|-----------------|-----|
| Identity pack content digest | Frozen frame redefined |
| Geometry version / `IdentityManifoldGeometry` construction contract | Gram/lift semantics changed |
| Gate / policy version (thresholds, \(H_{\mathrm{id}}\), \(\epsilon\)) | Lawfulness definition changed |
| Session / conversation boundary | Scope of “path” |
| Biography epoch boundary (if/when explicit) | Distinct from identity path; must not merge |

Biography holonomy \(H_{\mathrm{bio}}\) remains a **separate** process (ADR-0244 decision #8). ADR-0246 must never rewrite identity axes or fold biography into \(A_{\mathrm{path}}\).

### 3.6 Typed residual channels (fixed blade map)

Retain Euclidean aggregate leakage for fail-closed detection. Additionally emit **typed residual energy** on the rejection \(r_i = a_i' - P_I(a_i')\):

| Channel | Scope (Cl(4,1) grade-1 slots) | Intent |
|---------|--------------------------------|--------|
| `spatial_foreign_leakage` | components outside span of e1/e2/e3 that are still “spatial foreign” relative to pack axes (implementation: residual energy on grade-1 indices not in the value-axis support; for default pack support = e1/e2/e3) | alien spatial tilt |
| `boost_like_leakage` | e5-associated residual energy (explicit basis index for e5) | noncompact / boost-class departure; 2b proved boost is operationally special |
| `null_or_conformal_leakage` | e4 / null-cone-adjacent residual energy (explicit e4 index) | conformal/null direction departure |
| `unclassified_grade_or_numerical_leakage` | residual energy not accounted for by the above (higher-grade contamination after sandwich, nonfinite, etc.) | fail-closed; **no correction policy** on this channel |

Blade indices must be pinned to `algebra.cl41` basis conventions in the ADR body and tests — no free narrative labels.

### 3.7 Egress policy for ADR-0246 v1

**Remain admit-or-abstain.** No nonzero geometric \(C_{\mathrm{id}}\) displacement.

- D4 v1 `conjugate_correct` stays the model: refuse or pass; never rewrite \(F\) to green the metric.
- Geometric conjugate corrector (rotor \(R_{\mathrm{corr}}=\exp(-B/2)\), bound \(b_{\max}\)) is **out of scope** for ADR-0246; requires a later dedicated ADR after discrimination and calibration evidence exist.

Per-turn admit (illustrative shape; thresholds from Phase 3 / 0246 calibration):

```text
admit iff
  d_orth <= orth_tol
  AND d_stab <= epsilon_turn
  AND leakage_rms <= gamma_id          # or 1 - score style
  AND max_i leakage_i <= tau_max
  AND min_i self_align_i >= s_min
  AND no boundary_id hard breach
  AND no unclassified residual channel firing
else
  IdentityGateRefusal (or typed refusal surface) — live params unchanged
```

Path admit additionally requires \(d_{\mathrm{stab}}(A_{\mathrm{path}}) \le \epsilon_{\mathrm{session}}\) when a lawful composition chain is active.

---

## 4. Telemetry / record contract (minimum fields)

### 4.1 Per-turn identity action record

Emitted when wave-mode identity path runs (flag-gated; flag-off remains byte-identical for non-wave keys).

```text
IdentityActionRecord:
  schema_version: "identity_action_v1"
  turn_id / trajectory_id
  pack_id
  pack_content_digest          # full 256-bit where machine-key
  geometry_version
  gate_version
  policy_version               # H_id id + epsilon set
  wave_mode_active: bool

  # Raw measurements
  A_raw: float[n][n]           # induced action
  d_orth: float
  d_stab: float
  leakage: float[n]
  leakage_rms: float
  max_leakage: float
  self_align: float[n]
  min_self_alignment: float
  typed_residual_energy:
    spatial_foreign: float
    boost_like: float
    null_or_conformal: float
    unclassified: float

  # Policy outcome
  admitted: bool
  refusal_reason: str | null
  lawful_action: "I" | "none"  # under H_id={I}; never a soft projection matrix
  path_break: bool             # true if this turn does not compose

  # Digests
  field_digest                 # of F (or certified serve F)
  record_digest                # content-id of this record
```

### 4.2 Session identity path ledger

```text
IdentityPathLedger:
  schema_version: "identity_path_v1"
  session_id
  pack_content_digest
  geometry_version
  gate_version
  policy_version
  chain_id                     # new on hard break
  A_path_lawful                # product of lawful H_t only; identity matrix if empty chain
  d_stab_path: float
  composed_turn_count: int
  break_count: int
  max_axis_excursion: float    # optional derived
  ledger_digest
```

### 4.3 Serialization rules

- Machine merge keys / digests: full SHA-256 hex (ADR-0245 §2.3).
- No `default=str` silent coercion in content-id paths.
- Telemetry keys for wave/action path emitted only when `wave_mode_active` (preserve flag-off wire format).
- `compute_trace_hash` / replay contracts: follow D4 precedent — path forensic fields must not break flag-off byte-identity.

---

## 5. Module sketch (implementation shape — not authorized yet)

Suggested layout (adjust only if serve-quarantine or package boundaries force it):

| Module | Responsibility |
|--------|----------------|
| `core/physics/identity_manifold.py` | Keep geometry; add pure helpers: `induced_action(versor)`, `d_orth`, typed residual energy; keep f64, deterministic |
| `core/physics/identity_action.py` *(new, pure)* | \(H_{\mathrm{id}}\) policy objects, \(d_{\mathrm{stab}}\), lawful-only path composition, break markers |
| `core/physics/identity.py` | Wire measurements into `IdentityScore` / gate; still admit-or-abstain |
| `chat/runtime.py` | Flag-gated only; no new off-serve imports that violate A-04 |
| `evals/adr_0246_*` | Slow-drift, permutation, rotation, orth-failure, path-break suites |
| `tests/test_adr_0246_*` | Unit + integration pins |

**A-04:** pure geometry stays serve-safe if imported as today; eval-only harnesses stay under `evals/`.

---

## 6. Eval matrix (must earn claims)

### 6.1 Synthetic geometric suite (unit / offline)

| Test intent | Construction | Expected |
|-------------|--------------|----------|
| Identity versor | \(F \approx 1\) | \(A\approx I\), \(\ell\approx 0\), \(s\approx +1\), \(d_{\mathrm{orth}}\approx 0\), \(d_{\mathrm{stab}}\approx 0\) |
| In-plane π inversion of one axis | rotor e.g. e12-style invert e1 | \(\ell\approx 0\), that \(s\approx -1\), \(d_{\mathrm{stab}}>0\), refuse |
| In-plane 90° permutation/rotation | rotate e1→e2 etc. within \(I\) | \(\ell\approx 0\), diagonal \(s\) weak/zero, \(d_{\mathrm{stab}}>0\), refuse under \(H_{\mathrm{id}}=\{I\}\) |
| Mild in-plane drift step | small rotation \(\epsilon\) in plane | per-turn may pass \(\epsilon_{\mathrm{turn}}\); path product fails \(\epsilon_{\mathrm{session}}\) after enough steps |
| Alien tilt e14 / e15 | known D4 discriminators | \(\ell>0\); typed channels fire appropriately; refuse if above γ |
| Boost component | unit versor with e5 content | normalized \(\ell,s\) in range (2b fix); boost channel energy nonzero when residual present |
| Near-singular Gram | synthetic near-parallel axes | `ManifoldConditioningError` at geometry build — fail closed |
| Malformed \(F\) | NaN / wrong shape / nonfinite | typed error; never silent legacy when wave field was supplied |

### 6.2 Path / holonomy suite

| Test intent | Expected |
|-------------|----------|
| Sequence of lawful near-\(I\) turns | \(A_{\mathrm{path}}\) stays near \(I\); no false path refusal |
| Sequence of small in-plane rotations each under \(\epsilon_{\mathrm{turn}}\) | eventually \(d_{\mathrm{stab}}(A_{\mathrm{path}})>\epsilon_{\mathrm{session}}\) → path refuse |
| Interleaved refuse + admit | refused turns set `path_break`; lawful product excludes them; raw still recorded |
| Pack digest change mid-session | new `chain_id`; old \(A_{\mathrm{path}}\) not continued |
| Raw product ≠ lawful product when mixed fails present | forensic pin |

### 6.3 Discrimination report (not “tests pass”)

Any gate-on or 0246 ratification packet must include:

- benign pass rate  
- adversarial / reshuffle detection rate  
- false refusal rate  
- legacy-only vs wave-only vs dual ablation (if dual remains)  
- per-axis \(\ell,s\) distributions  
- score / \(d_{\mathrm{stab}}\) separation with confidence intervals  
- representative failure examples  
- runtime cost (µs/turn) for \(A(F)\) path  

Placeholder axes may yield weak semantic separation; report that honestly. Do not paper over with marketing claims.

---

## 7. Explicit non-goals (ADR-0246)

**Do not build in ADR-0246:**

1. Nonzero geometric \(C_{\mathrm{id}}\) / conjugate rotor correction / admittance stubs  
2. Multi-port residual protocol (Ring 2) as a unified scheduler  
3. ArticulationCertificate productization (may *consume* 0246 fields later)  
4. Semantic axis grounding / pack redesign for “true” truthfulness vectors  
5. Merging biography holonomy into identity path ledger  
6. Atlas packing, VSWR auto-repack, or golden-angle work (D4 Phase 5 / other ADRs)  
7. Analytic f64→f32 “truncation reactance” \(X_{\mathrm{cast}}\)  
8. Second identity projection path (grade-1 projection of versor — proven vacuous)  
9. Indefinite-norm leakage magnitude  
10. \(H_{\mathrm{id}}\) enlarged to \(O(n)\), permutations, or \(\{-I\}\) “for convenience”  
11. Soft projection of unlawful \(A\) onto \(I\) then composing as if lawful  
12. Default-on serve gate without D4 Phase 3 calibration certificate  
13. Smith Chart as a new algebra or universal scalar controller  
14. Status flip of ADR-0244/0245 without explicit human ratification  

---

## 8. Relationship to D4 completion (Ring 0)

ADR-0246 **starts after** (or explicitly waived past) D4 close-out. Until then, D4 owns:

| D4 phase | Relevance to 0246 |
|----------|-------------------|
| 2c ablation / injection eval | Discrimination honesty; 0246 reuses the report format |
| 3 \(\gamma_{\mathrm{id}}\) (+ optional \(\tau_{\max}, s_{\min}\)) | Feeds 0246 admit surface; 0246 adds \(d_{\mathrm{orth}}, d_{\mathrm{stab}}, \epsilon_{\mathrm{session}}\) |
| 4 cast transport certificate | Separate seam; 0246 may later compare \(A(F_{64})\) vs \(A(F_{32})\) but must not redefine cast |
| 5 packing + digest residuals + 0245 §3 proofs | Orthogonal mechanical/semantic rigor |
| 6 acceptance packets | Gate for starting 0246 implementation |

**While Claude is on D4:** do not open `core-adr0244d4` for 0246 work. Prefer a fresh worktree from post-D4 `main`.

### Optional D4 Phase 4 certificate (still D4, not 0246)

If D4 Phase 4 is still open when this brief is used, prefer this transport certificate (small, no new algebra):

```text
PrecisionTransportCertificate:
  source_field_digest
  source_precision: f64
  target_precision: f32
  versor_residual_before
  versor_residual_after
  identity_leakage_delta
  identity_alignment_delta
  trajectory_invariant_delta
  geometry_condition_number
  deterministic_replay_digest
```

\(\kappa(G)\cdot\epsilon_{\mathrm{cast}}\) is a **risk diagnostic** that triggers near-conditioning adversarial tests — not a standalone pass/fail law.

---

## 9. Ring 2 / Ring 3 pointers (out of scope, preserved direction)

### Ring 2 — multi-port residual protocol (future)

Shared control grammar only:

```text
witness → typed residual decomposition → permitted operator selection
  → bounded operation or abstention → re-certification
  → articulation/action decision → append-only replay record
```

Ports retain **non-identical** native geometry (Identity, Atlas, Evidence, Temporal/causal, Precision, Articulation, Action). Smith/conformal language is the interconnect grammar, not a second physics.

### Ring 3 — intelligence content (future)

Composition, bind/infer/counterfactual, epistemic standing, observe→learn under INV-21–30, discourse planning. Integrity coordinates handoffs; it does not replace content-bearing cognition.

---

## 10. Acceptance criteria for the future ADR-0246 packet

Before proposing **Accepted**:

1. All §6 synthetic + path suites green; discrimination report attached.  
2. \(H_{\mathrm{id}}=\{I\}\) enforced; no silent enlargements.  
3. Lawful-only composition proven by tests that fail if raw product is used.  
4. Ledger hard-breaks on pack/geometry/policy/session change.  
5. Flag-off serve path remains byte-identical where applicable.  
6. No geometric \(C_{\mathrm{id}}\); admit-or-abstain only.  
7. Typed residual channels pinned to explicit blade indices.  
8. Smoke + relevant fast/cognition lanes local-first; `[Verification]:` on PR.  
9. Claims language: “lawfulness relative to declared frozen frame,” not unearned “semantic inalienability of value labels.”  
10. Explicit human ratification for status flip (provenance guard).

---

## 11. Open workstreams (explicitly deferred)

| Workstream | Why deferred |
|------------|--------------|
| Semantic axis grounding (replace e1/e2/e3 placeholders with evidence-linked directions) | Instruments ≠ meaning |
| Geometric boundary witnesses beyond pack-id ∩ safety verdicts | D4 v1 registry is thin but acceptable until 0246+ |
| Bounded geometric \(C_{\mathrm{id}}\) | Requires discrimination + calibration + trajectory-fidelity constraint |
| Multi-port residual framework | Ring 2 |
| Articulation routing from residuals | Ring 2/3 consumer |
| Enlarged \(H_{\mathrm{id}}\) for named cognitive modes | Policy product decision, not algebra default |

---

## 12. One-sentence north star

> **D4 is the operational integrity floor; ADR-0246 makes identity lawful action across time on a frozen frame; later multi-port residuals coordinate existing organs; composition and evidence-governed learning complete the intelligence loop.**

---

## 13. Resume checklist (when implementing ADR-0246)

1. Confirm D4 Phase 6 (or waiver) and clean worktree from post-D4 `main`.  
2. Re-read this brief §3 (locked decisions) and §7 (non-goals).  
3. Implement pure \(A(F)\), \(d_{\mathrm{orth}}\), typed residuals in `identity_manifold` / `identity_action` with RED tests first.  
4. Wire path ledger with lawful-only composition + hard breaks.  
5. Extend gate admit surface; keep flag default off until calibrated.  
6. Run §6 eval matrix; attach discrimination report.  
7. Write ADR-0246 body + acceptance packet; **do not** self-Accept.

---

## 14. Document control

| Field | Value |
|-------|--------|
| Location | `docs/briefs/ADR-0246-induced-identity-action-and-path-integrity-preflight.md` |
| Supersedes | Informal post-D4 R&D chat conclusions only (not D4 plan) |
| Next artifact | Full `docs/adr/ADR-0246-...md` after D4 close, same locked decisions |
| Related live work | `docs/handoff/ADR-0244-D4-IMPLEMENTATION-PLAN.md` — do not modify mid-D4 without owner |
