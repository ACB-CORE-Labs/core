# Distinct-evidence audit of the three licensed-ledger producers

**Date:** 2026-07-25 · **Arc:** curriculum-license-loop Phase B ·
**Instrument:** `core/reliability_gate/evidence.py` ·
**Pin:** `tests/test_volume_honesty.py` · **Governing rule:** ADR-0264 R9
**Base:** main @ `6ada6f7a`

## Summary

Phase B set out to write an anti-gaming gate for a curriculum practice producer
that does not exist yet. Running the instrument against the producers that *do*
exist found the exposure already live in one of them.

**21 of the 25 ratified `deduction_serve` bands do not clear θ_SERVE = 0.99 on
distinct evidence.** Three of them inflate **28 distinct cases into 720
committed**. `deduction_serving_enabled` was ratified ON on 2026-07-24 and is
live.

The other two producers are clean. `estimation` (ADR-0175) commits 660 distinct
cases per class with zero repeats — just above the 657 a perfect record needs.
The GSM8K practice corpus is 150 cases, 150 distinct. So this is **a regression
from a standard already established in the repository**, not a gap in the
architecture and not something nobody had thought about.

Nothing was repaired. The deduction ledger is SHA-sealed, ratified, and gating a
live flag; changing it is Shay's ratification. The exposure is measured, pinned
in both directions, and written down here.

## Why replay is not evidence

`conservative_floor` (ADR-0175 §4a) is a one-sided Wilson lower bound on a
success proportion. Wilson assumes **independent trials**.

CORE's pipeline is deterministic — that is the founding property, not an
implementation detail. So submitting an identical case a second time is not a
second trial; it is the same trial with a guaranteed outcome. Two identical cases
in a practice ledger are perfectly correlated, and contribute one trial's worth of
evidence between them.

It follows that a ledger's `committed` count is an **upper bound** on its
evidence, and the defensible figure is its distinct-decision count. For a perfect
record the bound reduces to `n / (n + z²)`, so with `WILSON_Z = 2.576`:

| n distinct | conservative_floor | clears θ=0.99 |
|---|---|---|
| 28 | 0.8084 | no |
| 35 | 0.8406 | no |
| 98 | 0.9366 | no |
| 294 | 0.9779 | no |
| 474 | 0.9862 | no |
| 656 | 0.98999 | no |
| **657** | **0.99001** | **yes** |
| 720 | 0.9909 | yes |

657 is derived, not chosen: `n/(n + 6.635776) ≥ 0.99 ⟺ n ≥ 656.93`.
`volume_for_theta` recomputes it from `conservative_floor` so the figure cannot go
stale in a docstring.

S6 predicted exactly this in the abstract — `conservative_floor` "cannot
distinguish 657 independent facts from 16 facts asked 41 times"
(`docs/research/curriculum-volume-quantification-2026-07-24.md` §1). What is new
is that it is not hypothetical.

## Measurement

Key = the case **text**. Two cases with identical text are indisputably the same
decision. A tighter key — the normalized propositional atom — would additionally
collapse spelling variants of one question and report *more* inflation. So
text-identity **under-reports**, which is the correct direction: every number
below is a floor on the real gap.

```
theta=0.99   perfect-record volume needed=657

band                       committed  distinct     x   claimed   honest  clears
en_condmem_disjunctive           720        28  25.7    0.9909   0.8084     NO
en_exist_chain                   720        28  25.7    0.9909   0.8084     NO
en_exist_negative                720        28  25.7    0.9909   0.8084     NO
en_exist_witness                 720        35  20.6    0.9909   0.8406     NO
en_exist_universal               720        46  15.7    0.9909   0.8739     NO
en_condmem_chain                 720        52  13.8    0.9909   0.8868     NO
en_member_chain                  720        52  13.8    0.9909   0.8868     NO
en_member_negative               720        52  13.8    0.9909   0.8868     NO
en_condmem_conditional           720        60  12.0    0.9909   0.9004     NO
en_condmem_fused                 720        60  12.0    0.9909   0.9004     NO
en_member_atomic                 720        60  12.0    0.9909   0.9004     NO
en_member_single                 720        60  12.0    0.9909   0.9004     NO
atomic                           720        98   7.3    0.9909   0.9366     NO
categorical                      720       294   2.4    0.9909   0.9779     NO
conditional_chain                720       294   2.4    0.9909   0.9779     NO
conditional_single               720       294   2.4    0.9909   0.9779     NO
disjunctive                      720       294   2.4    0.9909   0.9779     NO
en_verb_chain                    720       308   2.3    0.9909   0.9789     NO
en_verb_negative                 720       308   2.3    0.9909   0.9789     NO
en_atomic                        720       474   1.5    0.9909   0.9862     NO
en_conditional_single            720       474   1.5    0.9909   0.9862     NO
en_verb_fact                     720       660   1.1    0.9909   0.9909    yes
en_verb_universal                720       660   1.1    0.9909   0.9909    yes
en_conditional_chain             720       720   1.0    0.9909   0.9909    yes
en_disjunctive                   720       720   1.0    0.9909   0.9909    yes

estimation
converse:parent_of               660       660   1.0    0.9900   0.9900    yes
converse:sibling_of              660       660   1.0    0.9900   0.9900    yes
```

Note the `claimed` column: **identical for every deduction band**, because every
band commits 720 with a perfect record. The gate sees 25 indistinguishable
passes. The `honest` column spans 0.8084 to 0.9909.

The sealed artifact matches the producer band-for-band
(`test_deduction_sealed_ledger_matches_the_producer_it_names`), so this is a fact
about `chat/data/deduction_serve_ledger.json` — the file the engine actually
reads — and not only about the generator.

`CASES_PER_BAND = 720` is a constant applied uniformly to bands whose template ×
vocabulary space ranges from 28 to 720 distinct instances. The producer fills the
quota by cycling. That is the mechanism, and it is a single constant, which is
part of why it went unnoticed.

## What this does and does not establish

**Established.** `wrong = 0` still holds — no band answered anything
incorrectly, and none of the pinned lanes were wrong about the answers they gave.
What is not established is *reliability at the volume claimed*. A band that
decided 28 distinct questions correctly has earned the floor for 28 distinct
questions (0.8084), not the floor for 720 (0.9909). The licences on 21 bands
rest on a bound whose independence precondition does not hold.

**Not established.** That any served answer was wrong. That the bands cannot
reach 657 distinct — most of them plainly can, by widening the template
vocabulary the way `en_conditional_chain` and `en_disjunctive` already do. The
remedy looks mechanical; it is the *authority to re-seal a ratified ledger* that
is not.

## Open ruling for Shay — outcome mix

Separate from distinctness, and deliberately **not** pinned by
`tests/test_volume_honesty.py`.

`ClassTally` has no verdict axis: `correct` and `wrong` are its only outcome
fields, so a case answered correctly as UNKNOWN is indistinguishable from one
answered correctly as ENTAILED. The gate therefore cannot see mix at all, which
is why any mix rule has to live in the producer.

The deduction producer already handles this well by construction — every band is
exactly 240 entailed / 240 refuted / 240 unknown, and `gold.py` says so
explicitly ("each band mixes entailed/refuted/unknown gold so reliability
measures decision quality"). ADR-0262 §5.1's "≈⅓ entailed" target is that
practice, restated.

The open question is whether each verdict class needs **its own** volume. The
claim a SERVE licence makes covers entailed, refuted and unknown answers alike,
yet the smallest per-band verdict-class count across the deduction ledger is
**120** (`en_atomic`), and the largest is 240 — every one of them below 657.

- Imposing a per-class floor would retroactively fail all 25 deduction bands on a
  criterion no ADR has ratified. This audit does not do that.
- Not imposing one means a licence's aggregate floor can rest on a mixture where
  one class is thinly sampled.

Recorded for a ruling, with the numbers, rather than decided here. This is the
same shape as the ADR-0199 per-class-vs-Wilson-floor question and should probably
be answered once for both.

## Reproduction

```bash
uv run python -m pytest tests/test_volume_honesty.py -q
```

Ad hoc, against any tree:

```python
from collections import Counter
from core.reliability_gate.evidence import audit_band, format_report
from evals.deduction_serve.practice.gold import all_gold_problems

by = {}
for p in all_gold_problems():
    by.setdefault(p.class_name, []).append(p.payload["text"])
print(format_report([audit_band(b, k) for b, k in sorted(by.items())], 0.99))
```
