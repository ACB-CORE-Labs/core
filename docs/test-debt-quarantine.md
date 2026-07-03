# Test debt quarantine

Current quarantined tests: 0.

The `QUARANTINE` set in [`/conftest.py`](../conftest.py) is the sole
authorized registry for known-failing pytest nodeids. It is currently empty,
so `pytest -m "not quarantine"` runs the same test population as plain pytest
with respect to quarantine.

The `full-pytest` CI gate at
[`.github/workflows/full-pytest.yml`](../.github/workflows/full-pytest.yml)
runs `pytest -m "not quarantine"`. If a quarantine entry is ever added, the
suite remains a **ratchet**: a test removed from `QUARANTINE` must pass on its
own merits in CI from that PR onward.

## Current Policy

Adding a test to `QUARANTINE` is strongly discouraged. If a new failure
surfaces:

- The default is to fix it in the PR that caused it.
- If the failure is genuinely orthogonal to the PR's intent, open a small
  fix-PR first, then resume the original work.
- A legitimate addition must include a tracked follow-up issue and a
  one-sentence justification in the adding PR.
- The current count in this document must be updated in the same PR as any
  `QUARANTINE` registry change.

To remove a test from quarantine:

1. Land a PR that makes the test pass.
2. Delete its entry from `QUARANTINE` in `conftest.py` in the same PR.
3. Update "Current quarantined tests" above.
4. The `full-pytest` CI gate now requires the test to keep passing.

## Historical Origin

A full `pytest --durations=30` run on 2026-05-24 surfaced **45 failures
+ 3 errors** in a 30-minute suite. Bisect against commit `c1a1b7a`
(the commit immediately before the first W-* PR of the audit sequence)
showed **all 49 failed identically on baseline**; the W-* work introduced
zero new failures.

Those historical failures had accumulated because CI only verified the lane
SHA pin job plus per-suite slices (`core test --suite smoke|teaching|...`).
The full `pytest` lane was not gated, so feature evolution silently broke
assertions without surfacing. The full-pytest gate closed that loop, and the
quarantine registry was used as a temporary IOU until those contracts were
made to pass. The registry is now empty.

## Historical Cluster Diagnoses

The 49 historical failures fell into five shape-clusters. This section is
retained for archaeology only; it is not the current registry.

### Cluster A — ADR ledger row status drift (4 tests)

ADR-0091's contract predicates moved certain domain rows through
status promotions (`reasoning-capable` → `audit-passed` → `expert`).
Tests pinning the *old* status string fail. Same shape as W-002
(PR #240), which extended `test_status_meets_reasoning_capable_at_minimum`
to accept `"expert"`.

Affected:
- `test_adr_0110_math_expert_demo`
- `test_adr_0121_math_expert_deferred`
- `test_capability_cli::test_capability_ledger_json`
- `test_capability_reports::test_ledger_status_is_predicate_derived`

**Fix shape**: extend the accepted-status set in each assertion, or
add a parametrize entry. One-token extensions per file.

### Cluster B — Surface decoration drift (15 tests)

The surface realizer now appends a `"pack-grounded (<pack_id>)"`
suffix to grounded surfaces (and similar decorations elsewhere).
Assertions written before that suffix existed compare against the
old format.

Example failure (from `test_cross_pack_grounding`):
```
AssertionError: assert 'spouse' in 'Spouse is one of a pair in a family. pack-grounded (en_core_relations_v1).'
```
The lemma IS in the surface — the assertion just doesn't expect the
trailing suffix.

Affected:
- `test_articulation::test_chat_surface_is_walk_surface`
- `test_correction_topic_lemma::test_correction_with_no_pack_lemma_still_grounds`
- `test_cross_pack_chains` (2)
- `test_cross_pack_grounding` (10, including 8 parametrized kinship)
- `test_en_collapse_anchors_v1_pack`

**Fix shape**: update assertions to use `in` containment against the
substantive content, or update expected-string fixtures to include
the suffix.

### Cluster C — Lane / runner metric drift (27 tests)

Lane runner reports drifted (thresholds, schema keys, or metric
values) without updating the pinned pytest assertions. This is the
largest cluster.

Example failure (from `test_cold_start_grounding_lane`):
```
assert 0.9167 >= 0.95
```
Real metric value `0.9167` is below the assertion threshold `0.95`.
Either:
- (a) An actual quality regression worth investigating, or
- (b) An aspirational threshold that was never met and never re-pinned

**Fix shape**: case-by-case. Some will be threshold updates; others
will be content fixes that move the metric back above threshold.
This cluster needs the most thought.

Affected lanes/runners:
- `test_adr_0122_rate_per_unit` (2)
- `test_adr_0126_train_sample_runner` (4 — includes 3 ERROR-shape)
- `test_adr_0131_G3_numerics` + `test_adr_0131_G_gsm8k_coverage_probe` (8)
- `test_cold_start_grounding_lane` (2)
- `test_composed_surface`
- `test_compound_walkthrough_eval_lanes`
- `test_en_core_action_v1_pack` (4)
- `test_gsm8k_math_runner`
- `test_ood_surface_generator` (2)
- `test_perturbation_suite`
- `test_relations_chains_v1`

### Cluster E — pytest-xdist parallel-execution incompatibilities (1 test)

The gate runs `pytest -n 4`. Some tests measure system-wide resources
(memory RSS, wall-clock timing) and become flaky under concurrent
worker pressure even though they pass single-threaded.

Affected:
- `test_articulation_bench::test_footprint_emits_samples_and_bounds`
  (asserts per-turn ΔRSS < 1 MiB; total system memory pressure under
  `-n 4` exceeds the ceiling)

**Fix shape**: either rewrite the test to measure only its own
allocations (not system RSS), or mark for serial-only execution via
pytest-xdist's `--dist loadgroup` + `@pytest.mark.xdist_group("serial")`.

### Cluster D — CLI / internal API drift (2 tests)

Mixed minor drift in CLI argument parsing and intent-classification
hot path.

Affected:
- `test_cli_test_suites::test_core_test_suite_accepts_pytest_flags_without_separator`
- `test_comb_pass_hot_path::test_classify_compound_intent_called_once_per_turn`

## Cross-references

- [`conftest.py`](../conftest.py) — the QUARANTINE registry
- [`.github/workflows/full-pytest.yml`](../.github/workflows/full-pytest.yml) — the CI gate
- [substrate-liveness-ratchet](audit/substrate-liveness-ratchet.md) — the W-* wiring debt registry (same shape, different domain)
