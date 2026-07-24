# Lane-Pin Drift Investigation — miner / curriculum / demo_composition

**Date:** 2026-07-24 · **Worktree:** `core-wt-gen` off main @ `5224b5e0`
**Verdict:** two distinct causes; no determinism bug; one **real serving
regression found and fixed** (register axis stripped from pipeline-served
turns).

Context: during the Band v4-CM arc (2026-07-23), a `verify_lane_shas.py
--update` dry run showed three lanes' pins stale. This investigation
root-causes all three before any re-pin (generalization-arc Phase 0.1).

## Determinism check

Each drifted lane was run twice in a fresh worktree (fresh
`uv sync --locked` venv, hermetic `CORE_ENGINE_STATE_DIR`): byte-identical
SHAs across runs for `miner_loop_closure` (`537094fe…`) and
`curriculum_loop_closure` (`cb94ca00…`). **Not a determinism bug.**

## Cause 1 — content-digest widening (miner + curriculum): benign, stale pins

Commit `5c69b741` (2026-07-17, ADR-0244 Phase 5a "§2.7 content-id
semantic rigor") widened `core/contemplation/schema.py::_content_digest`
from 16-hex truncation to the full 64-hex sha256 (birthday-collision
rigor). Both lanes' reports embed `finding_id` / derived `proposal_id`
values from that digest: the fresh `finding_id` is the 64-hex extension
of the exact pinned 16-hex prefix (`4d6b8b5e1d46eb60` →
`4d6b8b5e1d46eb60ea7a…`), and every downstream `proposal_id` cascades.
The commit re-pinned nothing. **Intentional, ADR-tracked, benign → both
pins re-pinned surgically in this branch** (single-line edits; never
`--update`, which rewrites every lane and silently drops erroring
lanes' pins).

## Cause 2 — demo_composition: a REAL serving regression (found via the drift)

The fresh lane report flipped `register-tour` `all_claims_supported`
true→false (plus `composite_supported`, which is `audit ∧ register`).
Isolation showed the register tour's two substantive-differentiation
claims failing while the three invariance claims held: **terse/convivial
registers no longer differed from neutral on pack-grounded definitions**
— the entire register axis (ADR-0077 R6 substantive + ADR-0071 R4
decoration) was missing from pipeline-served surfaces.

Mechanism (three commits, each individually defensible):

1. `ff1dcb25` (2026-05-20, #76) introduced `resolve_surface` with a
   `_base_runtime_surface` precedence of **canonical-first** — the
   trace-hash identity capture preferred over the runtime's served bytes.
   Dormant at first.
2. `e0d1b475` (2026-07-20, #96 fail-closed linguistic governance) routed
   pipeline turns through the resolver with `canonical_surface` populated
   → pipeline-served turns began serving the pre-R6 canonical. The
   runtime's own `chat()` path stayed correct; `warmed_session`
   telemetry-consistency went red (0.9444) because TurnEvent (correct
   bytes) disagreed with pipeline (stripped bytes).
3. `5a343b49` (2026-07-22, T13) "fixed" the telemetry red by
   back-stamping the pipeline's (stripped) surface onto TurnEvent —
   making telemetry consistent with the *regressed* serving. The register
   tour's claims — the falsifiable contract for the register axis —
   then failed, which is exactly the byte drift the lane pin caught.

Why no gate caught it: the e2e tests that pin this behavior
(`tests/test_register_substantive_consumption.py::test_e2e_terse_*`)
are red on main but are not in the curated smoke suite; the lane-shas CI
job is the only gate that runs the demo lanes, and its failures were
conflated with the known `public_demo` env flake.

### Fix (this branch)

`core/cognition/surface_resolution.py` + `core/cognition/pipeline.py`:

- `_base_runtime_surface` precedence corrected to **response-first**
  (served bytes = post-guard, post-R6, post-R4), canonical demoted to
  last-resort fallback.
- New `SurfaceResolution.hash_surface`: the truth-path
  (canonical-precedence) bytes, kept in lockstep through substrate
  overrides, folds, hedge prefix, logos-morph override, and the
  speculative marker. `compute_trace_hash` now folds `hash_surface`,
  so **trace_hash stays register-invariant (ADR-0069 inv C) while the
  served surface carries the register**. `_prior_surface` (correction
  binding) also stays on the truth path so register packs cannot perturb
  teaching.
- Removed dead `FailureClass` import + `_assessment_residual` (repo-wide
  unreferenced).

Verification: register tour **6/6 claims** (both substantive-differs
claims restored AND `all_trace_hashes_identical` held);
`tests/test_surface_resolution.py` (updated precedence tests + 2 new
fallback tests), `test_register_substantive_consumption.py` (previously
red e2e tests now green), `test_grounded_open_hedge_arm.py`,
`test_cognitive_turn_pipeline.py`, `test_warmed_session_lane.py` (T13
consistency) — all green; smoke suite via pre-push gate.

### demo_composition pin disposition (measured)

After the fix, every claims-supported flag in the lane report matches
the committed report again (`all_claims_supported_a/b` true,
`composite_supported` true). The only residual delta vs the 2026-07-14
pin is the two tours' *inner payload* `sha256` values — those payloads
embed per-prompt `trace_hash` values whose format legitimately changed
post-pin (`e7d116c9`, 2026-07-20: Phase-B graph-topology inclusion in
`compute_trace_hash`). Semantics restored, embedded hash format
evolved → re-pinned to `f0611a2c…` with this diff as the audit trail.

## public_demo (not one of the three, for completeness)

Unchanged: its known failure mode is the env-timeout flake
(`all_claims_supported=False` under cold/slow runs), documented in
memory and the lane-shas remediation text. Do not re-pin from a laptop
run; adjudicate on the Act runner.

## Bonus latent break found while re-pinning

`scripts/generate_claims.py` raised on every run since the
`deduction_serve_v1` pin landed (2026-07-23): the pin was added to
`PINNED_SHAS` without the required `_LANE_ADR` entry, so the lane-shas
CI's `generate_claims.py --check` step has been red since then. Fixed
here (ADR-0256 row added; CLAIMS.md regenerated, check green).

## Follow-ups (assigned in the generalization-arc plan)

- Tier S: add `tests/test_register_substantive_consumption.py` e2e
  tests to the curated smoke suite so this axis can never silently
  regress again (small, mechanical).
- Tier S: document the lane-shas CI expectation that a red lane job is
  triaged per-lane, never assumed to be the public_demo flake.
