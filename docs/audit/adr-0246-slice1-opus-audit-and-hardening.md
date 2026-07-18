# ADR-0246 Slice-1 — Opus 4.8 Audit, Hardening & Discrimination Report

**Reviewer:** Opus 4.8. **Branch:** `feat/adr-0246-slice1-hardened` (stacked on
`feat/adr-0246-slice1-scaffold`, unmerged). **Not a PR, not merged, no status
flip.** Review gate only — ratification is human (Shay).
**Audited artifact:** Fable 5's `feat/adr-0246-slice1-scaffold`.

---

## 1. Step-1 adversarial audit — VERDICT: PASS (one documentation finding)

Nothing was trusted from Fable's run log; every claim was reproduced.

| Check | Method | Result |
|-------|--------|--------|
| D4 closed (hard gate) | independent `git cat-file`/status on `main` | ✅ both acceptance packets on `main`; ADR-0244 Accepted/ratified; `main @ 04d67ca5` |
| `A(F)`, `d_orth`, `d_stab`, typed channels correct | **re-derived from §3.1/3.2/3.6 from scratch** (independent sandwich/Gram/projection) and diffed vs impl | ✅ **bit-exact, max discrepancy 0.00e+00** |
| `H_id={I}` genuinely locked in code | read `IdentityStabilizer`, `advance_identity_path` | ✅ singleton hardcoded in the path; **no enlargement parameter or path**; grep found no enlargement/permutation/soft-projection code |
| Path composes lawful only, never raw, no soft-`I` | read composition; grep | ✅ lawful turns compose; refused turns → `path_break`, excluded; `a_path` untouched on refuse |
| Placeholders logged, not baked | read policy/eval | ✅ `PLACEHOLDER_*` marked; `PathBudget` always caller-supplied |
| §7 scope creep / serve byte-identity | full `git diff main..scaffold`; per-function diff | ✅ **no `chat/runtime.py`, `identity.py`, or flag change**; serve-called geometry functions untouched (additions only) |
| §6.1/§6.2 matrix reproduced | ran from clean tree | ✅ 14/14 eval cases; 64 tests |

### Finding F1 (documentation, NOT a code bug)
`advance_identity_path` composes the **raw certified action** `A_t`
(`a_path = A_t @ a_path`), not a literal `I`. This is **required and correct** —
composing `I`s would make `A_path ≡ I` and defeat the slow-drift detection that is
the ledger's whole purpose (§2 gap). But it departs from a literal reading of
§3.4-step-4's `H_t ∈ H_id` notation and was undocumented. **Correction applied:**
an explicit "Composition semantics (ratification-relevant)" paragraph now states
the reading in the docstring; the ADR body should ratify it (see §4 handoff).

No locked decision (§3) or non-goal (§7) was violated to make anything pass.

---

## 2. Hardening & additions (this branch) — diff-style note

Every change vs Fable's scaffold, and why:

| File | Change | Why |
|------|--------|-----|
| `identity_action.py` | **F1 docstring** on `advance_identity_path` | ratify the raw-certified-action composition (audit finding) |
| `identity_action.py` | **§3.7 admit surface**: `CERTIFIED_GAMMA_ID`, `PLACEHOLDER_*`, `AdmissionPolicy` (`calibrated=False`), `AdmissionResult`, `evaluate_admission` | pure, testable admit-or-abstain surface (§3.7) — the reusable core for the discrimination report and the future serve wiring. No corrector. |
| `evals/adr_0246_discrimination/` | **§6.3 discrimination report** (new) | honest benign-vs-adversarial numbers with bootstrap-CI AUC (§6.3/§10) |
| `tests/test_adr_0246_admission.py` | pins for `evaluate_admission` + the honest verdict + γ_id-drift guard | fail loudly if the surface or the honesty claim regresses |
| `tests/test_adr_0246_path_ledger.py` | **raw-sneak hardening test** | fails if a raw product ever enters `A_path_lawful` (Step 2.3) |

Nothing here touches serve, flags, `H_id`, or adds a corrector. `evaluate_admission`
lives in the pure `identity_action.py`; γ_id is pinned equal to
`identity._WAVE_LEAKAGE_BOUND` by a test so it cannot drift.

---

## 3. §6.3 Discrimination report — HONEST numbers (no inflation)

Full artifact: `docs/audit/artifacts/adr-0246-slice1-discrimination-report.json`
(live benign cohort n=13, adversarial n=8, synthetic-near-identity control n=5;
policy = placeholder, `calibrated=False`).

| Metric | Value |
|--------|-------|
| benign pass rate | **0.00** |
| false refusal rate | **1.00** |
| adversarial detection rate | 1.00 |
| synthetic-near-identity pass rate (control) | **1.00** |
| `d_stab` AUC (adversarial vs benign) | **0.375**, 95% CI [0.15, 0.62] |
| `leakage_rms` AUC | 0.18, 95% CI [0.04, 0.39] |
| benign `d_stab` (min/mean/max) | 0.15 / **27.8** / 228 |
| adversarial `d_stab` (min/mean/max) | 0.46 / **1.55** / 2.83 |

**Honest finding (verbatim in the report):** the §3.7 admit surface on the declared
placeholder frame refuses benign and adversarial versors **alike** — benign
false-refusal is 100% and `d_stab` does **not** separate the classes (AUC 0.375 is
*below* chance: real benign cognition sits ~18× farther from the identity frame
than the crafted attacks do). A gate that refuses everything trivially "detects"
every attack but **is not a discriminator**. The synthetic-near-identity control
passing at 100% confirms the gate *mechanism* is sound — the failure is entirely
that benign cognition does not live near the declared frame. This reproduces and
sharpens the D4 / slice-0 result at the fuller §3.7 surface.

**Claims language (§10 #9), enforced in code and report:** this supports only
*"lawfulness relative to the declared frozen frame."* It does **not** support any
claim of *"semantic inalienability of the value labels."* The gate must stay
default-off; usable separation requires the §11 dynamics-grounding work — **not**
threshold tuning.

---

## 4. §3.7 egress serve wiring (Steps 2.1/2.2) — DONE (Opus)

Wired the fuller admit surface into the live gate, flag-gated + default-off +
byte-identical:
- New **default-off** flag `identity_action_surface` in `core/config.py`
  `RuntimeConfig` (separate from `identity_wave_gate`; documented as uncalibrated /
  not authorized live).
- Threaded an `AdmissionPolicy` (`placeholder_default()`, `calibrated=False`)
  through `chat/runtime.py` → `IdentityCheck.check(..., admission_policy=)` →
  `_wave_field_score`. Only acts when `identity_wave_gate` is also on (a
  `wave_field` exists).
- On the wave path with the policy present, `evaluate_admission(...)` runs; a
  refusal folds into `flagged`, so the **existing** `would_violate` /
  `conjugate_correct(refuse=True)` egress abstains — **admit-or-abstain, no
  corrector**. `MalformedVersorError` from the primitives propagates as a
  fail-closed refusal.
- `IdentityScore` gained optional `action_surface_active` / `d_orth` / `d_stab`
  with legacy defaults, so flag-off is byte-identical.

Verified: `tests/test_adr_0246_egress_wiring.py` (flag default-off; flag-off
`check()` byte-identical incl. default §3.7 fields; flag-on refuses a tilt and
admits true near-identity) + **all D4 gate surfaces green unchanged** (wave /
runtime / eval / `test_identity_gate`) — serve byte-identity confirmed.
**Guardrail:** `calibrated=False` + flag default-off ⇒ not live-authorized; the §3
discrimination numbers are the evidence it must stay off pending §11 + calibration.

## 4c. Handoff to Sonnet 5 — remaining ADR-0246 work

1. **§4.1 `IdentityActionRecord` per-turn telemetry** — not built (only the §4.2
   `IdentityPathLedger` exists). Add the per-turn record (field/record digests,
   gate/policy versions, the §3.7 measures) and emit it only when the wave/action
   path ran (preserve flag-off wire format, §4.3). Optionally surface `d_orth`/
   `d_stab`/typed channels through the telemetry serializer.
2. **Path-ledger ↔ serve integration** — the ledger (`advance_identity_path`) is
   pure and unit-tested but is not yet driven per-turn from `chat/runtime.py`
   (session-scoped chain, hard-break on pack/geometry/policy/session). Wire it
   flag-gated + off, using the §3.5 scope keys, if a session path budget is wanted.
3. **ADR-0246 body + acceptance packet** — draft `docs/adr/ADR-0246-...md` as
   **Proposed** (no self-Accept — provenance guard). Must: state the F1 composition
   semantics explicitly; use the §10 claims language ("lawfulness relative to the
   declared frozen frame"); carry the honest §6.3 numbers; enumerate the placeholder
   ε's/τ's as uncalibrated. Acceptance packet per §10; §8 RULING PENDING.
4. **§11 grounding-feasibility study** (the larger research workstream) — does a
   held-out-stable, safety-relevant dynamics-invariant structure exist (fixed
   cohort splits, synthetic recovery controls, typed e4/e5 generator analysis,
   precision pairs, adversarial discrimination)? This is the only path to a gate
   that discriminates; the §6.3 report shows threshold tuning cannot get there.
5. **Open uncertainties still needing a ruling** (Fable notes §4, unchanged):
   general-pack `‖·‖_G` convention; structurally-empty `spatial_foreign` channel;
   hard-break turn ownership; malformed-F/gate-routing boundary. Carry into the ADR.

---

## 5. Verification (run log: `docs/audit/artifacts/adr-0246-slice1-hardened-runlog.txt`)
- §6.1/§6.2 eval matrix → 14/14, `all_passed=True`.
- ADR-0246 suites (admission, egress wiring, induced-action, path-ledger incl.
  raw-sneak hardening, geometric suite, mismatch diagnostic) → **80 passed**.
- Egress wiring + all D4 gate surfaces (wave/runtime/eval/`test_identity_gate`) →
  **47 passed** — flag-off byte-identity confirmed (D4 gate unchanged).
- `uv run core test --suite smoke -q` → **176 passed** (post-serve-wiring).
- §6.3 discrimination report → the honest numbers in §3 above.
