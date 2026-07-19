# GSM8K reader — overfit inventory (2026-07-19)

**Status**: Inventory only — descriptive, not prescriptive. Nothing on this list is being deleted,
disabled, or modified by this document or the recalibration it accompanies (ADR-0251). Every pattern
below keeps serving unmodified; the reader must keep working until a proven replacement exists.

## Purpose

A read-only survey of `generate/*.py` and `evals/refusal_taxonomy/shape_categories.py` on `main` @
`854ce023`, identifying regex constants, extractor functions, and closed-vocabulary lists whose shape or
motivating comment reads as tailored to one specific GSM8K case (or a small named cluster of cases) rather
than a general grammatical class. This gives the geometric surface→canonical normalization spike proposed
in ADR-0251 §5 — if a human ruling authorizes it — a concrete target list of what "one general operator
replacing N bespoke regexes" would need to subsume before it could claim a positive generalization ratio.
Two entries were spot-checked directly against source during this recalibration and confirmed accurate
(see the underlying commits for full context); the rest were produced by a dedicated read-only survey
citing exact file:line locations.

## Group 1 — mechanisms built to admit one named case (case ID in comment)

| # | File:Line | Name | Why it's bespoke |
|---|---|---|---|
| 1 | `generate/recognizer_match.py:557-599` | `_CROSS_SENTENCE_COMPOSITION_RE` | Section header: "ME-2 — cross-sentence subject binding (**admits case 0019**)"; quotes the exact source sentence ("John adopts a dog from a shelter...requires 3 vet appointments, which cost $400 each") as the spec. |
| 2 | `generate/recognizer_match.py:602-660` | `try_extract_cross_sentence_composition_anchor` | Exists solely to thread the case-0019 discourse subject through to #1. |
| 3 | `generate/recognizer_match.py:2123-2191` (esp. 2136-2148) | `match()` dispatcher's ME-2 branch | Docstring explicitly names case 0019 as the shape being admitted. |
| 4 | `generate/math_candidate_graph.py:676-703`, `:1107-1123` | RAT-1 discourse-subject pre-pass | Comment cites case 0019 ("John adopts a dog") by name as the motivating example for the whole pre-pass. |
| 5 | `generate/recognizer_match.py:1377-1460` | `_MULT_AGG_EACH_WEIGHING_RE` / `_try_extract_each_weighing_anchor` | Header: "Targets the canonical...shape (**case 0047** in the train_sample audit)" — long verb alternation built to cover one problem's wording variants. |
| 6 | `generate/math_candidate_parser.py:2693-2797` | `_COND_OP_Q_RE` / `extract_conditional_op_question_candidates` (ADR-0136.S.2) | Comment: "**Target shape (gsm8k-0042)**" — a whole candidate type + short-circuit solve path built for one case ID. |
| 7 | `generate/recognizer_match.py:1125-1140` | `_COMPOUND_REFUSE_SUBSTRINGS` (ADR-0250 widening entries) | Widening tokens (`" twice the "`, `" thrice the "`, etc.) justified by one verbatim confabulation example quoted in the comment. |

## Group 2 — "Gate A2b/A2c/A2d" question extractors (each is one exact question phrasing)

| # | File:Line | Name | Why it's bespoke |
|---|---|---|---|
| 8 | `generate/math_candidate_parser.py:2872-2877`, `3177-3200` | `_Q_KEEP_ON_HAND_RE` / `_pattern_d_keep_on_hand_candidates` (Gate A2b) | Matches only the literal idiom "keep on hand" — no generalization beyond that exact wording. |
| 9 | `generate/math_candidate_parser.py:2896-2906`, `3149-3174` | `_YIELD_RATE_RE` / `_Q_YIELD_RE` (Gate A2c) | "used to make one X" / "be able to make" is a single idiom, not a grammar class. |
| 10 | `generate/math_candidate_parser.py:2909-2919`, `3121-3146` | `_PEER_PICK_CONDITIONAL_RE` / `_Q_PEER_PICK_RE` (Gate A2d) | Literal phrase match ("friends pick the same amount as her/him"..."pick in all") — reads as built for one specific problem. |
| 11 | `generate/math_candidate_parser.py:985-993`, `1040-1068` | `_FRACTION_GIVE_RE` / `_fraction_give_candidates` (Gate A2b) | Fixed verb ("give") + fixed closed referent set (`that/it/them`). |
| 12 | `generate/math_candidate_parser.py:995-1003`, `1071-1087` | `_HALF_REST_RE` / `_half_rest_candidates` (Gate A2b) | Matches the literal phrase "half of the rest" — a single-sentence idiom, not a generalizable partition rule. |

## Group 3 — entity/label-specific initial-possession shapes

| # | File:Line | Name | Why it's bespoke |
|---|---|---|---|
| 13 | `generate/math_candidate_parser.py:267-285` | `_INITIAL_HAS_LABELED_RE` (ADR-0194) | Comment names three exact source sentences ("Jar A has 28 marbles.", "Section G has 10 cars.", "District 2 has 19 voters.") as the spec. |
| 14 | `generate/math_candidate_parser.py:287-304` | `_INITIAL_THERE_ARE_PREFIX_RE` (ADR-0136.S.4 Shape B) | Built around one quoted example ("In a building, there are a hundred ladies on the first-floor studying.") — optional clauses shaped to that sentence. |
| 15 | `generate/math_candidate_parser.py:1957-1964` | `_CONJ_BAGS_OF_RE` (Gate A2c conjoined) | Hardcoded two-clause "N bags of X and M bags of Y" shape. |

## Group 4 — closed-vocabulary lists sourced from named individual cases

| # | File:Line | Name | Why it's bespoke |
|---|---|---|---|
| 16 | `generate/math_candidate_parser.py:2986-3012` | `_FEMALE_NAMES` / `_MALE_NAMES` | Comment: "Closed-set whitelists **sourced from GSM8K train_sample observation**. Adding a name requires evidence from a refused case." Pronoun resolution by literal name enumeration, not general NER/gazetteer. |
| 17 | `generate/math_candidate_parser.py:2854-2861` | `_PATTERN_C_VERBS` | Closed verb whitelist "observed in GSM8K train_sample," grown one refused case at a time. |
| 18 | `generate/math_roundtrip.py:96-117`, `generate/math_candidate_parser.py:1192-1205` | `NEUTRAL_COUNT_VERBS` / `_COMPARISON_ANCHOR_VERBS` (ADR-0250 increment 1 — **the #78 allowlist**) | Curated verb frozensets, each vetted against one refusal — legitimate and load-bearing (this recalibration keeps it), but still individually case-grown rather than derived from a POS/semantic class. |

## Group 5 — `evals/refusal_taxonomy/shape_categories.py`: category rules justified by 1-4 named cases

Each rule's docstring cites specific `case NNNN` numbers from the 50-case train sample. Spot-checked
directly against source: `_is_unit_partition` (row 19) is explicitly a single-case-justified category —
"the 50-case sample carries **one instance** (case 0002); the rule is retained as a reserve."

| # | File:Line | Rule | Cases cited in docstring |
|---|---|---|---|
| 19 | `:296-311` | `_is_unit_partition` | Only case 0002 — kept as "reserve" |
| 20 | `:264-277` | `_is_nested_question_target` | 0009, 0042 |
| 21 | `:279-293` | `_is_conditional_quantity` | 0009, 0042 (docstring admits it "may return `False` for the entire current corpus") |
| 22 | `:314-325` | `_is_rate_with_currency` | 0001, 0011, 0022 |
| 23 | `:328-352` | `_is_currency_amount` | 0019, 0026, 0028 |
| 24 | `:355-368` | `_is_comparative_with_unit` | 0015, 0016, 0033 |
| 25 | `:371-387` | `_is_fractional_rate_of_change` | 0005, 0012, 0041 (explicitly excludes 0044 by name) |
| 26 | `:390-412` | `_is_temporal_aggregation` | 0013, 0014, 0024, 0050 |
| 27 | `:415-428` | `_is_indefinite_quantity` | 0004, 0040, 0043 |
| 28 | `:431-458` | `_is_multiplicative_aggregation` | 0025, 0045, 0047 |
| 29 | `:461-488` | `_is_discrete_count_statement` | 0023, 0027, 0046 |
| 30 | `:491-500` | `_is_descriptive_setup_no_quantity` | 0003, 0008, 0019 |

These are the taxonomy layer's version of the same pattern: one predicate per small case cluster, with the
literal source sentences quoted as the specification, instead of one regex per case.

## Bonus — non-regex decision heuristic shaped by one scenario

| # | File:Line | Name | Why it's bespoke |
|---|---|---|---|
| 31 | `generate/math_candidate_graph.py:452-467` | `_slot_count` (per-sentence ambiguity tiebreaker) | Docstring: implements "**the give-with-target case**" by name — a general-sounding "most-grounded-slots-wins" rule whose actual justification is one named scenario shape. |

## Explicitly excluded — general/closed, not bespoke

Reviewed and judged to cover broad closed grammatical classes rather than one sentence's literal wording,
so not listed as candidates: `_DAY_ENUM_RE`/`_day_enumeration_candidates` (day-of-week enumeration,
`math_candidate_parser.py:1823-1882`); `_INITIAL_HAS_RE`/`_INITIAL_THERE_ARE_RE` (standard "A has N X" /
"There are N X" shapes, `:145-247`); the `_CAPACITY_RE` family (ADR-0136.S.1 rate/event, `:2397-2508`);
and the currency-grounding logic in `math_roundtrip.py:323-433` (covers multiple currencies/time units
generically). `generate/math_completeness.py` and `evals/refusal_taxonomy/runner.py` were reviewed in
full and contain no case-pinned patterns.

## What this inventory does not claim

This list does not claim every pattern on it is wrong to have, nor that the reader should be rewritten.
The `#77`/`#78` foundations (compare-multiplicative compiler tier, `NEUTRAL_COUNT_VERBS` allowlist) are
sound, reviewed, and stay exactly as they are. This is a map of where the reader's growth has been
case-shaped rather than grammar-shaped, for whoever picks up the geometric-normalization question next.
