# Tier S Housekeeping (S5)

**Tier S5** (generalization-arc-2026-07-24 §6). Four items; results below.

## 1. `test_register_substantive_consumption.py` promoted into smoke

Added to `core/cli_test.py`'s `TEST_SUITES["smoke"]` (the local pre-push
gate) and `.github/workflows/smoke.yml` (the mirrored CI gate — kept in
parity rather than diverging from the local list). 36 tests, ~4.6s. This
file is the falsifiable contract for the register axis (ADR-0069/0071/0077)
and was red on `main`, outside every gate, for the 2026-07-22→24 window
documented in `docs/research/public-demo-lane-drift-2026-07-24.md` §3.2 and
[[project-register-axis-serving-regression]] — the exact "silent red" class
the lane-drift investigation flagged as a follow-up. It can no longer
regress without blocking a push.

**Found in passing:** `tests/test_cli_test_suites.py::test_core_test_deductive_suite_expands_to_entailment_lane`
was already red on clean `main`, unrelated to any Tier S work — it pinned
the `deductive` suite to an exact single-file tuple from when that suite
had one entry; the suite has since grown to 12 files across the
deduction-serve/curriculum-serve arcs. A leaky-gate case in the same
"pinned list goes stale" family the smoke-coverage pin exists to catch, on
a *different* suite the coverage pin doesn't watch. Fixed to a contains-style
assertion (matching the neighboring `fast`-suite test's own style) so it
cannot go stale the same way again.

## 2. Capability-index entries for `curriculum_serve_v1` and the `v2_exist` split

Two new adapters in `evals/capability_index/adapters.py`:

- `deduction_serve_existential_result()` — Band v6-EX (ADR-0261) alone, not
  the full six-band deduction-serve lane. The other five bands are grammar
  widenings over the same propositional-entailment substrate the existing
  `deductive_logic` adapter already scores; v6-EX is the one that changes
  the decision procedure itself (domain widening with Skolem witnesses / an
  arbitrary element), making it the genuinely new capability worth its own
  index domain.
- `curriculum_serve_result()` — the curriculum-grounded serving lane
  (ADR-0262) as a whole, scored against its independent oracle.

Index breadth: 11 → 13 domains. Re-froze `evals/capability_index/baseline.json`
(a deliberate re-freeze, per the file's own docstring — adding capability
domains is exactly the "accepted improvement" case) and updated
`tests/test_capability_baseline.py`'s implicit dependents
(`tests/test_capability_index.py`'s `breadth == 13` and the explicit
13-domain name set). `not_covered: []`, `wrong_total: 0` on the live run.

## 3. Promotion sweep — nothing beyond `ds-mem-0020`

The mechanism that surfaced `ds-mem-0020` (a case whose committed
`gold="declined"` stopped matching `decide()`'s output the moment Band
v6-EX could read and decide it — caught as a lane `wrong=1` failure,
diagnosed as a promotion, gold corrected) is not a one-time manual check:
it is exactly what `evals/deduction_serve/runner.py`'s `wrong == 0` gate
enforces on every run, over every split, using the CURRENT full band
cascade. Any other currently-`declined`-gold case that a band now decides
differently would show up the same way. This session ran that gate
repeatedly (166/166 wrong=0 both standalone and inside the 279-test
`deductive` suite run, post-S3's vocab-trigger instrument addition) with
zero further mismatches. **The sweep's proof is the passing gate, not a
separate pass** — nothing else in the older splits is decidable that isn't
already reflected in committed gold.

## 4. Dead code

None found unambiguous enough to remove during this sweep beyond what S2
(`public_demo` pin) and S4
(`generate/determine/derived_close_proposals.py::DEFAULT_SINK` off-by-one)
already fixed as part of their own scope — see those PRs' own notes.

Relates to [[project-generalization-arc]].
