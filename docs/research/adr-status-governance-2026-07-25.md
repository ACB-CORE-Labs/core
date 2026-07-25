# ADR Status Governance — Nine Stamps and an Enforcement Pin

**Date:** 2026-07-25 · Follow-on to the assessment-verification arc (PR #113).
Evidence + mechanism only. No flag was touched; no ADR's *content* was changed.

## 1. What was wrong

Nine ADRs were merged into `main` and left stamped `Proposed`:

| ADR | ratifying merge | why the stamp was contradictory |
|---|---|---|
| 0254 | PR #103 → `da3447e9` (2026-07-23) | its own status line said *"ratify on PR #103 merge"* |
| 0256 | `1a6ccaf9` (2026-07-23) | its own status line said *"ratify-on-merge"*, **and** it governs `deduction_serving_enabled`, ratified `True` on 2026-07-24 |
| 0257 | PR #107 → `9405cf19` | Band v2-EN, live in the serving cascade |
| 0258 | PR #108 → `dd2245a7` | Band v3-MEM, live |
| 0259 | PR #109 → `5224b5e0` | Band v4-CM, live |
| 0260 | PR #111 → `2a82c8a3` | Band v5-VP, live |
| 0261 | `a8488e9c` | Band v6-EX, live |
| 0262 | `0ae54ebb` | curriculum-grounded serving (flag still OFF — see §3) |
| 0263 | `0ae54ebb` | ratified-ledger bridge, consumed by three capabilities |

Every merge above was verified an ancestor of `main` before stamping
(`git merge-base --is-ancestor`), and each ADR's ratifying merge was derived
from the commit that *added* the file, not assumed.

ADR-0256 is the sharp case. It governs a flag that was ratified ON and serving
live traffic, so the governance record asserted "this decision is not yet made"
about a decision already in force. That is the same asymmetry the arc that just
closed found in `workbench/api.py`: **the honest path degrades, the stale
record lies.** An unregistered grounding label reported
`epistemic_state_needed`; a hand-copied whitelist reported `none`. Here, an
unwritten ADR would have been a visible gap; a `Proposed` one that is actually
in force is a false statement.

## 2. What the stamps say

Status lines now record the *actual* ratifying act rather than inventing a
ceremony: `Accepted — ratified by Joshua Shay via <the merge> (<sha>, <date>)`.
Merge authority in this repo is Shay's alone (`AGENTS.md`: no merge automation;
green PRs sit until explicit authorization), so the merge **is** the ratifying
act and naming it is traceable rather than decorative.

## 3. Accepting an ADR is not flipping its flag

ADR-0262's stamp says so explicitly. `curriculum_serving_enabled` stays
`False`; its blocker is ratified curriculum volume (§5.1), and eleven live
bands remain 24×–73× short of the entailed-bucket floor — re-measured
2026-07-25 against the live loader, unchanged from the Tier-S S6 figures
(physics `causal` 7, `modal` 9, `systems_software` `sequence` 3,
`mathematics_logic` `modal` 4). An accepted ADR records a decision about
*mechanism*; a flipped flag records a decision about *earned evidence*. Two
different rulings, and this document conflates neither.

## 4. The pin

`tests/test_adr_status_governance.py`, registered in the `smoke` suite (the
pre-push gate). Two independent invariants, both mutation-checked — reverting
ADR-0256 to `Proposed` fails each one separately:

1. **A default-ON flag is not governed by a `Proposed` ADR.** The
   flag → ADR mapping is **derived** by walking `core/config.py` for
   `<name>: bool = True` and reading the ADR references out of the preceding
   comment block. Deliberately not a hand-written table: a second copy of a
   closed set that falls behind the original in silence is the exact defect
   ADR-0256's arc fixed one file over.
2. **A `ratify-on-merge` predicate cannot coexist with `Proposed`.** Self
   discharging and needs no bookkeeping: the file being present on `main` *is*
   the merge having happened, so the two states are contradictory by
   construction.

Plus `test_config_flag_parse_is_not_vacuous`, because a derivation that silently
parses zero flags would make every other assertion pass on an empty set —
silence reading as success.

Measured: **314 passed in 1.18s** standalone; 2 failed / 312 passed under
mutation.

Current binding scope is exactly one flag/ADR pair
(`deduction_serving_enabled` → 0256), because only one of the 32 runtime bool
flags is both default-True and ADR-citing. Narrow today by construction, and it
widens automatically the moment another earned path is ratified ON — which is
the point.

## 5. Two orphaned test files, registered in passing

`tests/test_adr_index.py` (5 tests) and `tests/test_ratification_ceremony.py`
(14) landed in PR #113 in **no** curated suite. `full` is the directory
`tests/`, so they ran there and nowhere that gates. Nineteen tests outside every
gate — including the ceremony, the one mechanism that can move the
curriculum-volume constraint, and an index test whose whole purpose is catching
staleness.

That is the **fifth** instance of this shape: a stale suite tuple (S5), a stale
lane roster (#113), a masked lane pin (S2), an unregistered grounding label
(#113), and now unregistered test files. Registered `test_adr_index.py` into
`smoke` alongside the new pin, and `test_ratification_ceremony.py` into
`teaching` beside `test_proposal_queue.py`.

## 6. Deliberately NOT fixed — recorded so it is not re-found

The ADR corpus is 312 files and its status vocabulary has real drift:

| status token | files |
|---|---:|
| `accepted` | 201 |
| `proposed` | 67 |
| *(status line unparseable)* | **27** |
| `draft` | 4 |
| `ratified` | 3 |
| `accepted.` / `active` / `phase` | 2 each |
| `implemented` / `empirical` / `superseded` | 1 each |

A closed-vocabulary assertion over all 312 would fail on ~35 pre-existing files
and get muted or `xfail`ed, which is worse than no check — a muted gate reads as
coverage. So the pin's scope is exactly the ADRs whose status is load-bearing
*now*, and it fails loudly on any of *those* it cannot parse rather than
skipping it.

**The open item:** normalize the 27 unparseable status lines and collapse
`ratified`/`draft`/`active`/`implemented` into the intended lifecycle, then
widen the pin to a closed vocabulary. Sizeable, mechanical, and a good
delegation candidate — it is a docs sweep with a test as its acceptance
criterion, not a design question.

Relates to [[project-generalization-arc]], `docs/adr/INDEX-by-domain.md`,
`docs/handoff/BRIEF-CLOSE-assessment-verification-2026-07-25.md`.
