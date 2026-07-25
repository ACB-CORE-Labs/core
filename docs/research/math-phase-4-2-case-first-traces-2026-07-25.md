# Math Phase 4.2 — case-first traces for 0000 / 0001 / 0148 / 0082

**Baseline reproduced:** `holdout_dev: correct=5 wrong=0 refused=495 (n=500)` —
unchanged from the 2026-07-24 measurement, five days and one arc later.

**Deliverable:** the per-case trace `math-reader-phase-4-1-status-2026-07-24.md`
asked for, plus a corpus-frequency measurement that **changes the
recommendation**. All four named cases are blocked by surface gaps that are
among the *rarest* in the 500. Building for them is the overfit move ADR-0251
prohibits — and this document is the first time that has been quantified rather
than argued.

**Nothing was changed in the reader.** See §5.

## 1. Where all four refuse — one seam

Every one of the four fails at the same place, with the same shape of message:

```
candidate_graph: recognizer matched but produced no injection for statement:
  '<first statement>'  (category=...)
```

Traced through `generate.recognizer_match.match(statement, registry)`:

| case | category assigned | `parsed_anchors` | injection |
|---|---|---|---|
| 0000 | `DISCRETE_COUNT_STATEMENT` | `()` | `()` |
| 0001 | `DISCRETE_COUNT_STATEMENT` | `()` | `()` |
| 0148 | `DESCRIPTIVE_SETUP_NO_QUANTITY` | `()` | `()` |
| 0082 | `DISCRETE_COUNT_STATEMENT` | `()` | `()` |

So the recognizer **classifies** each statement and then extracts **no grounded
anchor**. `_is_comparative_multiplicative_v1_surface` is `False` for all four,
so none of them ever reaches `inject_comparative_multiplicative` — the injector
that would handle "twice as many X as Y". The gate is
`_COMPARE_MULT_ANCHOR_RE` (`generate/math_candidate_parser.py:1229`), anchored
`^…$`, so it must match the **whole** statement:

```
^(?P<actor>ENTITY)\s+VERB\s+(?:a\s+)?(?P<anchor>twice|thrice|half|quarter|third)
 \s+as\s+many\s+(?P<unit>\w+(?:\s+\w+)?)\s+as\s+(?P<reference>REF)\s*\.?$
```

## 2. Gap isolation — one variable at a time

Each gap isolated by mutating a known-good baseline in exactly one dimension.
This is the evidence, not the regex reading:

| probe | matches | isolates |
|---|---|---|
| `Aria has twice as many credits as Emily.` | **YES** | baseline |
| `… as many school credits as …` (2-word unit) | **YES** | unit slot admits 2 |
| `… as many high school credits as …` (3-word) | no | **unit slot caps at 2 words** |
| `… as many pounds of lobster as …` | no | **`of`-headed unit phrase** |
| `… as many credits than Emily.` | no | **`than` connector** |
| `… as Emily, who has twice … as Spencer.` | no | **trailing relative clause** |
| `At a station, Aria has twice …` | no | **leading adjunct** |
| `The number of people was twice the total number counted.` | no | **copula + bare `twice the N`** |
| `Mary has twice the amount of carrots as green beans.` | no | **`twice the amount of X as Y`** |
| `… as many credits as the two other students combined.` | no | **aggregate reference** |

## 3. Per-case traces

### Case 0000 — `expected 140.0`
> Aria has twice as many high school credits as Emily, who has twice the number
> of high school credits as Spencer. If Emily has 20 credits, what's twice the
> total number of high school credits the three have?

Blocked by **two** gaps in one sentence: a 3-word unit (`high school credits`)
and a trailing relative clause carrying a *second* comparative. Solving needs a
chained resolution (Emily=20 → Spencer=10, Aria=40), a summation (70), and a
final ×2 on the aggregate. **Four capabilities.**

### Case 0001 — `expected 480.0`
> Hooper Bay has twice as many pounds of lobster than the two other harbors
> combined. If the other two harbors have 80 pounds of lobster each, how many
> pounds of lobster are the three harbors holding?

Blocked by **four** gaps: `than` where the template requires `as`; an
`of`-headed unit (`pounds of lobster`); an aggregate reference (`the two other
harbors combined`); and a multi-token proper name —
`extract_proper_noun_subject` returns `'Hooper'`, not `'Hooper Bay'`, which
alone would fail the injector's narrow actor binding (`actor != actor_token`).

### Case 0148 — `expected 1500.0`
> At a people counting station, the number of people counted on the first day
> was twice the total number counted on the second day. If 500 people were
> counted on the second day, how many people were counted on the two days?

The only one classified `DESCRIPTIVE_SETUP_NO_QUANTITY` — the recognizer does
not see a count statement at all. Three gaps: a leading adjunct; a noun-phrase
quantity as subject (`the number of people counted on the first day`) rather
than an entity; and a copula + bare `twice the total number` form with no
`as many … as` at all.

### Case 0082 — `expected 2.0`
> Mary uses plastic grocery bags that can hold a maximum of twenty pounds. She
> buys 4 pounds of green beans, 6 pounds milk, and twice the amount of carrots
> as green beans. How many more pounds of groceries can Mary fit in that bag?

The refusing statement is not the comparative at all — it is the **capacity**
frame (`bags that can hold a maximum of twenty pounds`), a relative-clause
capacity assertion with a spelled-out cardinal. The comparative arrives in the
next sentence in the `twice the amount of X as Y` form. Then the question wants
capacity − Σ(4, 6, 8). **Four capabilities**, none of which is the v1 template.

## 4. The measurement that changes the recommendation

Frequency of each blocking surface feature across all 500 holdout cases:

| surface feature | cases | % of 500 |
|---|---:|---:|
| aggregate reference (`combined` / `together` / `altogether`) | **53** | 10.6% |
| leading adjunct (`At/In/On/During …,`) | **28** | 5.6% |
| `twice/N times as many … as` (any unit width) | 29 | 5.8% |
| `twice the number/amount/total of` | **13** | 2.6% |
| copula + `was/is twice` | **13** | 2.6% |
| capacity frame (`hold` / `maximum of` / `capacity`) | 14 | 2.8% |
| — of the 29, unit is >2 words | **1** | **0.2%** |
| — of the 29, connector is `than` | **2** | **0.4%** |

**The gap blocking case 0000 affects one case in five hundred. The `than` gap
blocking case 0001 affects two.**

That is the whole finding. "Widen the unit slot from two words to three" and
"admit `than` alongside `as`" are precisely the per-case pattern growth ADR-0251
and `reader-arc-overfit-inventory-2026-07-19.md` exist to prohibit — and until
now the prohibition rested on a prior about overfitting. It now rests on a count.

The forms that actually recur are different ones: aggregate reference (53),
leading adjunct (28), `twice the number/amount of` (13), copula-twice (13).

**Honest limit on these numbers.** They are *surface-feature* counts, not
conversion estimates. A case containing `combined` is not thereby convertible —
§3 shows every one of these problems needs three or four capabilities at once,
so a case can carry a frequent feature and still strand on the other three.
The counts bound the opportunity; they do not predict yield. Treating them as
yield is the exact error the arc already made once, when tune-set parse-rate
gain was read as capability and shipped answers that were *wrong* on the exam.

## 5. What was deliberately not done

**No reader change was made.** The plan's Lane 4 exit criterion is the traces
plus `wrong=0` holding, not a shipped extension, and three things argue against
shipping one from this session:

1. §4 shows the named cases' gaps are the rarest in the corpus. Building them
   is the prohibited move, now with a number attached.
2. The sealed 1,319-case test split is the final arbiter and must not be read.
   A change justified only by movement on the open dev set has exactly the
   evidentiary shape ADR-0251 was written against.
3. The four cases are each 3–4 capabilities deep. There is no "minimum reader
   extension" that converts one of them — which is itself the strongest form of
   the arc's own conclusion that *real GSM8K statements are individually
   multi-capability*.

`wrong=0` still holds: `correct=5 wrong=0 refused=495`.

## 6. Recommendation

Phase 4.2 as scoped — case-first on 0000/0001/0148/0082 — should be recorded
as **traced and declined**, not attempted. The tracing was the right
instruction; its result is that these four are the wrong four.

If the reader arc resumes, the measured entry point is **aggregate reference**
(53 cases, 10.6%) — the single most common blocking surface in the corpus, and
the one whose semantics (`the two other harbors combined` → Σ over a named
complement set) is a genuine compositional capability rather than a template
widening. Scope it the same way this document scopes: isolate the gap, count
its reach, and require that the conversion evidence be a *capability* argument,
not a parse-rate delta.

Relates to [[project-generalization-arc]].
