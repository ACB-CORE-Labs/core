# ADR-0246 Slice-1 Scaffold — Handoff Notes (Fable 5 bounded autonomous draft)

**Status:** DRAFT SCAFFOLD ONLY — not a PR, not merged, no status flip, no `main`
push. For review by Opus 4.8 + Joshua Shay before anything proceeds toward `main`.
**Branch:** `feat/adr-0246-slice1-scaffold` (unmerged).
**D4 gate (directive stop-condition #3):** PASSED — D4 is closed. Both acceptance
packets are on `main` (`docs/audit/adr-024{4,5}-acceptance-packet-2026-07-17.md`);
ADR-0244 status line is `Accepted — ratified by Joshua Shay 2026-07-17`; `main @
04d67ca5`. Proceeded.
**Stop condition reached:** #1 — all four build steps complete and the full
§6.1 + §6.2 matrix passes locally (smoke + new tests + eval harness), with results
written to `docs/audit/artifacts/adr-0246-slice1-scaffold-runlog.txt` (not asserted
from memory). No §3/§7 non-goal had to be violated; no calibration numbers were
invented into the modules (see Placeholders).

---

## 1. What was built (directive steps 1–4)

| Step | Deliverable | Where |
|------|-------------|-------|
| 1 | `induced_action(F)`, `d_orth`, typed residual energy (§3.1/3.2/3.6), pure f64 | `core/physics/identity_manifold.py` |
| 2 | `H_id={I}` policy (`IdentityStabilizer`), `d_stab`, lawful-only path composition + hard-break ledger (§3.3–§3.5) | `core/physics/identity_action.py` |
| 3 | Runnable §6.1 synthetic geometric suite + §6.2 path/holonomy suite | `evals/adr_0246_geometric_suite/` |
| 4 | Unit pins for every synthetic case (fail loudly on the exact expected) | `tests/test_adr_0246_{induced_action,path_ledger,geometric_suite}.py` |

### Reuse note (transparent for audit)
Steps 1–2 are the **already-verified** work from earlier this session, reused
rather than re-derived (RED-first TDD, off-serving):
- `feat/adr-0246-induced-action-primitives` — §3 primitives (commit `4941cf18`)
- `feat/adr-0246-path-ledger` — §3.4/3.5 ledger (commit `6efe4ad8`, stacked)

`feat/adr-0246-slice1-scaffold` is stacked on top of those, so its history carries
both commits (all descend from `main @ 04d67ca5`). The two earlier branches are
therefore **subsumed** by this scaffold and can be pruned if the reviewers prefer
the single-branch deliverable. This scaffold additionally adds: the malformed-F
guard (`MalformedVersorError`), the §6.1/§6.2 eval harness, the extra §6.1 pins,
the run log, and these notes.

---

## 2. Hard-constraint compliance (directive "Hard constraints while building")

- [x] `H_id = {I}` only — `IdentityStabilizer.singleton`; never enlarged; never
  soft-projects an unlawful `A` onto `I` (refused turns are break markers).
  Pinned: `test_refused_turn_is_break_and_excluded`.
- [x] Path composed from lawful/certified actions only — never raw `A_t`.
  `advance_identity_path` composes only turns with `d_stab ≤ ε_turn`; refused/
  ill-conditioned turns get a `path_break` marker (never an identity stand-in).
  Forensic contrast pinned: `test_raw_product_differs_from_lawful`.
- [x] No nonzero geometric `C_id` / conjugate corrector — admit-or-abstain only.
  Nothing in the modules rewrites `F` or `A`.
- [x] `chat/runtime.py`, flag defaults, and D4 gate wiring **untouched**. Verified:
  `test_gate_flag_and_bound_untouched` (flag default-off, `_WAVE_LEAKAGE_BOUND`
  unchanged); A-04 quarantine pinned by `test_*_is_pure_offserving` /
  `test_suite_is_offserving`.
- [x] No discrimination report, ADR-0246 body, or acceptance-packet language
  written. No "semantic inalienability" / marketing claim drafted — see §5 TODO.
- [x] `docs/handoff/ADR-0244-D4-IMPLEMENTATION-PLAN.md` **not modified**.

---

## 3. Placeholder values used (directive: list every one + why)

| Placeholder | Value | Where | Why it is a placeholder |
|-------------|-------|-------|--------------------------|
| `epsilon_turn` | 0.1 | `evals/adr_0246_geometric_suite` `PLACEHOLDER_EPSILON_TURN`; test fixtures | **UNCERTIFIED.** D4 Phase 3 certified only `γ_id = 0.2126624458513829`. The two-level path budget (§3.4) is not yet calibrated. Value chosen only to exercise the mechanism (small single-turn drift admits; a 90° rotation refuses). NOT baked into any serve/module default — `PathBudget` is always caller-supplied. |
| `epsilon_session` | 0.3 | same | **UNCERTIFIED.** Same status; chosen so ~7 steps of a 0.05-rad rotation accumulate past it, demonstrating the accumulation guard. Not a policy value. |
| `_NONZERO` = 0.05 | 0.05 | eval harness | Not a calibration number — a "clearly nonzero" marker for the ">0" rows of the §6.1 table (d_stab, leakage). |
| test construction angles (0.02, 0.05, 1.0, 1.5, π/2, π) | — | tests/evals | Case constructions, not policy. Chosen to realize the exact §6.1/§6.2 geometric signatures. |

**Explicitly NOT invented:** `γ_id` (already certified, unchanged), `τ_max`,
`s_min`. The per-turn admit surface that would consume these (§3.7) is **not built
in this scaffold** — that is the gate-wiring unit, deliberately out of scope, so no
placeholder was needed for them.

---

## 4. Uncertainties in §5–§7 (directive: list anything you were unsure how to satisfy)

1. **§3.2 general-pack `‖·‖_G` convention.** The brief fixes `d_stab = ‖A−H‖_G`
   but leaves the general-pack weighted-norm convention to "ADR-0246 proper." I
   implemented `‖M‖_G = ‖G^{1/2} M G^{-1/2}‖_F` (metric-consistent; reduces exactly
   to Frobenius at `G=I`, which is the only shipped pack). **Needs review/ratification.**
2. **§3.6 `spatial_foreign` channel.** For the default pack (support = e1/e2/e3) it
   is structurally ~0 (projection removes in-span components). Implemented generally
   (residual energy on grade-1 spatial slots outside the axis support) but it cannot
   fire until a non-default pack exists. Untested against a real non-default pack.
3. **§4.1 `IdentityActionRecord` full telemetry** (per-turn `field_digest`,
   `record_digest`, gate/policy versions, admitted/refusal_reason) is **not built**;
   only the §4.2 `IdentityPathLedger` (with `ledger_digest`, `chain_id`) is. The
   per-turn record belongs to the gate-surface/telemetry unit (§3.7), out of scope
   here. `advance_identity_path` returns a lightweight per-turn dict, not the full record.
4. **§6.1 "Malformed F → never silent legacy when wave field was supplied."** The
   "silent legacy" clause is about the D4 gate's dual-mode fallback in
   `identity.py` (untouched here, owned by D4). This scaffold adds a fail-closed
   `MalformedVersorError` at the *pure primitive* boundary (`induced_action` /
   `typed_residual_energy`). Whether the gate should route malformed-F to this same
   typed error is a gate-wiring decision, deferred.
5. **Path budget semantics under a hard break.** I treated a scope change as: start
   a fresh chain, and the triggering turn is turn 1 of the new chain (its own action
   composes into the fresh `I`). The brief (§3.5) specifies a new `chain_id` and
   that the old path is not continued, but does not pin whether the boundary turn
   belongs to the old or new chain. Chose new-chain. **Confirm.**

---

## 5. Explicitly deferred to Opus/human review (NOT written here)

> **TODO: Opus/human review** — the following were intentionally left undone per
> the directive; do not treat their absence as an oversight:
- The **discrimination report** (§6.3): benign/adversarial rates, false-refusal,
  ablations, CI-bounded separation. Requires the gate-surface + live cohorts.
- The **ADR-0246 body** and any **acceptance-packet** language.
- Any **claim about what the axes mean** ("semantic inalienability", grounding).
  The §11 grounding-feasibility study (fixed cohort splits, synthetic recovery
  controls, generator analysis, precision pairs, adversarial discrimination) is the
  first consumer of these primitives and is **not** part of this scaffold.
- The **gate admit-surface wiring** into `IdentityScore` (§3.7) and the calibration
  of `ε_turn`/`ε_session`.

---

## 6. Verification (see run log for actual output)

`docs/audit/artifacts/adr-0246-slice1-scaffold-runlog.txt`:
- `python -m evals.adr_0246_geometric_suite` → 14/14 cases passed, `all_passed=True`.
- pytest ADR-0246 suites + adjacent D4 identity surfaces → 114 passed.
- `uv run core test --suite smoke -q` → (appended to the run log).

No PR. No merge. No status flip. Report back to Shay/Opus for the audit that
decides what, if anything, proceeds toward `main`.
