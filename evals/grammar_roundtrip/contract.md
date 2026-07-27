# Grammar Round-Trip Eval Lane — Contract

**Lane:** `grammar_roundtrip`
**Version:** v1
**Created:** 2026-07-26
**Plan:** `docs/plans/grammar-unification-2026-07-26.md` (Phase 1)

## What this lane measures

Whether CORE can **read what it writes** and **write what it reads** — and,
critically, whether it *refuses* word salad.

## Why it exists

`evals/deterministic_fluency` reports **1.00 on all six of its predicates**
and still passes every one of these:

| candidate | passes deterministic_fluency? |
|---|---|
| `"banana does the."` | yes |
| `"wet ground rains the is."` | yes |
| `"is is is is."` | yes |

It checks terminal punctuation, presence of a verb-shaped token, and two
anti-shape regexes. It cannot distinguish English from word salad, so its 100%
carries no information about fluency.

Heuristic predicates will always have that failure mode, because
**grammaticality cannot be measured without a grammar.** This lane therefore
measures agreement between the two halves of CORE that already encode grammar —
the reader and the writer — and requires the measurement to *fail* on salad.
Round-trip is falsifiable with no judge, no embedding, and no gold aesthetic.

## The two directions

| direction | pipeline | what a failure means |
|---|---|---|
| **G-round-trip** | graph → `realize_target` → surface → `comprehend` → graph | CORE cannot read its own writing |

> **`realize_target` is eval-only** (Phase 4). `core/cognition/pipeline.py` calls
> `realize_semantic`, never `realize_target`, so `g_read_rate` is a measurement of
> the grammar *library* and not of served English. Run through the serving writer
> instead, the G-direction reads back **nothing** (0.0 vs 0.003413) — see
> `tests/test_phase4_realizer_resolution.py`. Any claim made from this metric must
> say which writer it is about.

| **S-round-trip** | surface → `comprehend` → graph → categorical renderer → surface | CORE cannot reproduce what it just understood |

Both are reported because they fail for different reasons and have different
remedies.

## Metrics

| metric | definition |
|---|---|
| `g_write_rate` | fraction of graph cases the writer produced any surface for |
| `g_read_rate` | fraction of written surfaces the reader comprehended |
| `g_args_rate` | fraction of expected propositions whose **argument pair** was recovered |
| `g_predicates_rate` | fraction whose **predicate name** was recovered *on the same arguments* |
| `g_exact_rate` | fraction recovered exactly (predicate + arguments + polarity) |
| `s_read_rate` | fraction of positive surfaces comprehended |
| `s_renderable_rate` | fraction whose projection the categorical renderer can express at all |
| `s_surface_match_rate` | fraction that render back to the input surface |
| `reject_rate` | fraction of the **negative** corpus refused or reduced to zero propositions |

`g_args_rate` and `g_predicates_rate` are reported separately on purpose. High
argument agreement with low predicate agreement means the grammars align and
only the *vocabulary* is split — a materially different remedy from both being
low. Collapsing them into one boolean would hide the distinction that decides
this arc's direction (plan §6).

## Corpora

| corpus | source | size |
|---|---|---|
| positive graphs | committed `english_fluency_ood` + `grammatical_coverage` case files | 293 |
| positive surfaces | in-module, each verified comprehensible by probe | 8 |
| negative surfaces | hand-authored salad + deterministic token shuffles of the positives | 16 |

The shuffles are load-bearing: they are **lexically identical** to positive
cases — same vocabulary, same length, order destroyed. A lane that rejects
hand-authored salad but accepts the shuffles is doing vocabulary checking, not
grammar checking. Shuffling uses a fixed rotation rather than a PRNG so
`reject_rate` is byte-reproducible.

## Thresholds

| metric | v1 requirement | rationale |
|---|---|---|
| `reject_rate` | **1.00, always** | the guarantee; regression is a hard failure |
| `g_read_rate` | recorded baseline, revised **upward only** | currently a measured defect |
| `s_surface_match_rate` | recorded baseline, revised **upward only** | currently a measured defect |

## v1 baseline — measured on `main` @ `9696443a`

```
graph_cases              293
g_write_rate             1.000
g_read_rate              0.000     <-- CORE reads 0% of what it writes
g_propositions_expected  370
g_args_rate              0.000
g_predicates_rate        0.000
g_exact_rate             0.000

surface_cases              8
s_read_rate              1.000
s_renderable_rate        0.625
s_surface_match_rate     0.000     <-- nothing renders back to its input

negative_cases            16
reject_rate              1.000     <-- the guarantee holds
```

Two of these are **pins on known defects**, not goals. They are expected to be
revised upward by plan Phases 2B and 5, and must never be revised downward to
accommodate a regression.

`s_renderable_rate = 0.625` is not a defect: 3 of the 8 positive surfaces
project to `member` / `less` predicates, which have no `all X are Y` categorical
surface at all. Those are reported as unrenderable rather than as match
failures, because "cannot write this" and "wrote this wrongly" need different
fixes.

## What this lane does NOT prove

Round-trip is **necessary, not sufficient** for fluency. It measures *mutual
intelligibility* — both halves agreeing about a surface. Two halves can agree
on an impoverished construction: `english_fluency_ood` accepts `"river flows
valley"` as a correct surface, and round-trip would be perfectly happy with it.

So a high round-trip rate licenses **"CORE means what it says"**, never
**"CORE writes well"**. The negative corpus is what prevents the first failure
mode. Nothing in this lane prevents the second, and no metric here should ever
be cited as evidence of prose quality.

## Mutation guarantees

Every guarantee is paired with a test proving it can break
(`tests/test_grammar_roundtrip.py`):

- `test_reject_rate_goes_red_when_the_reader_accepts_everything` — an
  accept-everything reader must drive `reject_rate` to **0.0**. Without this,
  `reject_rate == 1.0` would be unfalsifiable, which is precisely the defect
  that makes the existing fluency lane decoration.
- `test_shuffled_negatives_reuse_positive_vocabulary` — closes the
  vocabulary-checking escape hatch.
- `test_positive_surfaces_are_all_inside_the_reader_envelope` — a refused
  positive would silently measure reader coverage instead of round-trip.
- `test_quantifier_map_matches_reader` — the lane keeps a deliberate local copy
  of the reader's quantifier map so it never becomes a consumer of the thing it
  measures; this test fails loudly if the reader's map changes.
