# Vocab-Trigger Instrument — Baseline Measurement

**Tier S3** (generalization-arc-2026-07-24 §6). Implements the measurable
test named in `docs/handoffs/COMPREHENSION-READER-AUDIT.md` (§Q5) — a
refusal histogram split mechanism-vs-coverage plus an admissions-per-batch
counter — generalized from the math reader (the audit's original subject)
to the two composers this arc actually ships: `chat/deduction_surface.py`
and `chat/curriculum_surface.py`. Implementation:
`evals/vocab_trigger_instrument.py`; tests:
`tests/test_vocab_trigger_instrument.py` (11, registered in the
`deductive` suite).

This document does not propose any pack/curriculum expansion. It reports
where the two composers stand today and hands over a rerunnable
instrument, per the standing doctrine
([[project-base-knowledge-pack-expansion-trigger]]): pack/base-knowledge
expansion becomes load-bearing exactly when refusals shift from mechanism
scope to vocabulary scope — surface that shift, don't act on it here.

## 1. The rule (closed, not invented)

A decline is one of three classes:

- **mechanism** — the reader/gate cannot parse the SHAPE (a closed-grammar
  gap: `sentence_shape_out_of_band`, `quantifier_out_of_band`, ...).
- **coverage** — a term or relation the ratified content never taught
  (`untaught_vocabulary`, `out_of_curriculum` — the curriculum composer's
  own naming, taken verbatim, not reinterpreted).
- **engine_refused** — a fully-read, well-formed argument the ROBDD engine
  itself declines (`inconsistent_premises`, `out_of_regime_or_malformed`
  from `generate/proof_chain/entail.py`). Neither a shape gap nor a
  vocabulary gap; no lexicon or curriculum batch moves this bucket.

This third bucket was not in the brief's two-way framing and was found
while building the instrument: an early version misattributed
engine-declined arguments (read successfully, but self-contradictory) to
whichever reader band happened to be tried last in the fallback cascade —
a real bug, not a design choice, caught by `test_deduction_refusal_reason_recovers_engine_level_decline`
pinning `"p. Not p. Therefore q."` to `(band="v1", reason="inconsistent_premises")`
rather than a v6-EX shape reason it never actually hit.

## 2. Baseline measurement (2026-07-24, committed lane corpora)

Run: `uv run python -m evals.vocab_trigger_instrument`. Deterministic —
pure over `evals/deduction_serve/*/cases.jsonl`,
`evals/curriculum_serve/*/cases.jsonl`, and the same production decision
paths the lanes score against (`test_build_report_is_deterministic` pins
byte-identical output across repeat runs).

| composer | n | admitted | declined | mechanism | coverage | engine_refused |
|---|---:|---:|---:|---:|---:|---:|
| deduction | 166 | 126 | 40 | 35 | **0** | 5 |
| curriculum | 32 | 26 | 6 | 2 | 4 | 0 |
| **combined** | 198 | 152 | 46 | 37 | 4 | 5 |

### 2.1 Deduction: zero coverage-class refusals, and why that's correct

Every one of the 40 declined deduction cases is mechanism (35, closed-shape
gates — the largest single bucket is `v6_exist:mixed_structure_out_of_band`
at 11) or engine_refused (5, all `inconsistent_premises` — 4 pinned
Band-v1 contradiction probes plus one natural-English contradiction admitted
by Band v2-EN). **Zero coverage refusals is the honest count, not a gap in
this instrument**: none of the seven deduction bands read open vocabulary —
they read a small closed set of connective/quantifier words
(`generate/proof_chain/{english,member,cond_member,verb,exist}.py`), so
there is no vocabulary axis for them to refuse on. A future band that reads
open English prose (rather than a closed relation grammar) would be the
first one this instrument could ever show a nonzero coverage count for.

### 2.2 Curriculum: the coverage axis is real and already exercised

4 of the physics split's 6 declines are coverage (3 `untaught_vocabulary`,
1 `out_of_curriculum`); the other 2 are mechanism
(`question_shape_out_of_band`). This is the axis
[[project-curriculum-grounded-serving]] and S6's volume quantification
already describe from the ratified-chain-count side; this instrument
confirms it from the refusal side using the SAME production decision path,
independently.

## 3. How to use this for a future batch

```
uv run python -m evals.vocab_trigger_instrument --report before.json
# ... ratify new curriculum content or widen a band's grammar ...
uv run python -m evals.vocab_trigger_instrument --report after.json
uv run python -m evals.vocab_trigger_instrument --compare before.json --report after.json
```

The last command prints the admitted-count delta per composer — the
falsifiable measurement Option A of the audit's Q5 calls for, generalized:
a real batch should move `admitted` up and the matching declined-class
count down. No claim is made here about what that delta *should* be for
any specific batch; that is content strategy, not this instrument's job.

## 4. Non-goals

- Does not run against live chat traffic — only the committed, sealed lane
  corpora (adding a live-traffic feed would be a different, larger
  instrument and is not requested here).
- Does not add a new SHA-pinned CI lane; the report is deterministic and
  could be pinned later if a gate on this split is wanted, but nothing
  requested that for Tier S.
- Does not reclassify `ambiguous_reading` / `empty_curriculum` as coverage
  even though they are vocabulary-adjacent — only the two reasons the
  brief named explicitly are coverage-class (§1).

Relates to [[project-base-knowledge-pack-expansion-trigger]],
[[project-curriculum-grounded-serving]], [[project-generalization-arc]].
