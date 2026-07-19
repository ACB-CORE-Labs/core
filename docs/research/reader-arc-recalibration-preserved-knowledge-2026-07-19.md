# Reader-arc recalibration — preserved knowledge from `feat/reader-inc2-caseband` (PR #80)

**Date**: 2026-07-19
**Status**: Reference notes — validation targets for a future increment, not a build
**Origin**: Extracted before abandoning `feat/reader-inc2-caseband` (PR #80) per the recalibration
decision (see ADR-0251). The branch is **not merged**; nothing below authorizes landing its code.
Everything in this note was re-verified directly against source on `main @ 854ce023` and against the
abandoned branch's tip (`origin/feat/reader-inc2-caseband @ e3da148d`), not copied from the branch's own
claims — see §3 for a place where the branch's own narrative overstated what it verified.

---

## 1. The `has_numeric_token` multiplier-blindness bug (real, general, verified)

### 1.1 Root cause

`classify_sentence()` in `generate/math_candidate_parser.py:2385` (wrapping `has_numeric_token()` at
`:2374`) decides whether a statement sentence is skippable "context" or must carry numeric state:

```python
def has_numeric_token(sentence: str) -> bool:
    if re.search(r"\d", sentence):
        return True
    return bool(_WORD_NUMBER_RE.search(sentence))
```

`_WORD_NUMBER_RE` is built from `WORD_NUMBERS` (`generate/math_roundtrip.py:218-228`) — the closed
cardinal set `zero..ninety, hundred, thousand` plus three ordinal-factor words `half/third/quarter`.
**It does not include multiplicative comparatives**: `twice`, `thrice`, `double`, `triple`,
`quadruple`, etc. A statement sentence whose *only* quantity signal is one of these words — no digit,
no cardinal word — is misclassified `"context"` and therefore treated as safe to drop.

Verified directly on `main`:

```python
>>> from generate.math_candidate_parser import classify_sentence
>>> classify_sentence("Jerry has twice as many apples as Ivan.")
'context'
```

This is the *exact* sentence the existing ADR-0191 comment in `generate/math_candidate_graph.py:670-673`
already names as the risk case ("`Jerry has twice as many … as Ivan` has no digit but a multiplier the
reading must account for") — the comment anticipated the failure mode; `has_numeric_token` does not yet
satisfy it.

### 1.2 Where it bites (and where it doesn't)

`classify_sentence` feeds a filter at `generate/math_candidate_graph.py:704-707`:

```python
numeric_statement_sentences = [s for s in statement_sentences if classify_sentence(s) == "numeric_state"]
if numeric_statement_sentences or not statement_sentences:
    statement_sentences = numeric_statement_sentences
```

The guard (`numeric_statement_sentences or not statement_sentences`) only *replaces* `statement_sentences`
when the numeric-only subset is non-empty. Consequence, verified both ways:

- **Single-statement cases (e.g. case 0148 itself) are NOT affected** — if the multiplier-only sentence
  is the *only* statement sentence, the numeric-only subset is empty, the guard is false, and the
  original sentence (including the multiplier-only one) survives unfiltered. Confirmed: 0148's refusal on
  `main` is **not** caused by this filter (see §2 — it's an actor-binding/surface gap instead).
- **Multi-statement cases ARE affected** — if at least one *other* statement sentence has a literal
  digit/cardinal, the multiplier-only sentence is silently dropped from `statement_sentences` before any
  recognizer/extractor sees it. Verified with a synthetic two-sentence case reproducing the ADR-0191
  comment's own example:
  ```
  'Ivan has 5 apples.'                        -> numeric_state
  'Jerry has twice as many apples as Ivan.'    -> context   (dropped)
  ```
- **Real-corpus incidence, measured against `evals/gsm8k_math/holdout_dev/v1/cases.jsonl` (500 cases)**:
  23 cases have a statement sentence containing only `twice/thrice/double/triple/quadruple` (no digit, no
  cardinal) co-occurring with another statement sentence that does have a literal number — the exact shape
  that triggers the drop. Examples: `0032`, `0060`, `0096`, `0112`, `0161`, `0165`, `0207` (several of
  these — e.g. `0112` "Tim bought twice as many clowns as Rick bought guppies" — are load-bearing compare
  clauses, not incidental frequency phrases like `0012`/`0127`/`0196`'s "twice a day"). This list is
  **not triaged** — some of the 23 may already refuse/resolve correctly for unrelated reasons, or may be
  masked by the completeness guard (§1.3). It is a candidate list for whoever picks this up next, not a
  claimed fix count.

### 1.3 Why this has NOT been a `wrong=0` hazard (verified, not assumed)

`uncovered_quantities()` in `generate/math_completeness.py:194` (the ADR-0191 completeness guard) is a
**separate, already-correct** mechanism: it resolves multiplier anchors via the `en_numerics_v1` pack's
`lookup_multiplier` (`math_completeness.py:36-68`), independent of `has_numeric_token`. So even when the
primary filter silently drops a multiplier-only statement, the completeness guard still knows a "twice"
was present in the source, sees the chosen graph never consumed it, and **refuses** ("incomplete reading")
rather than emitting a wrong answer. This is refusal-only by construction (`math_completeness.py:19-23`),
so the bug's practical effect is **missed conversions (false refusals), not wrong answers**.

### 1.4 Minimal fix idea (NOT landed — do not cherry-pick without full-500 validation)

The abandoned branch's own fix (`generate/math_candidate_parser.py`, diff against `main`) was:

```python
_COMPARE_MULT_ANCHOR_TOKENS_RE: Final[re.Pattern[str]] = re.compile(
    r"\b(?:" + "|".join(re.escape(k) for k in _ANCHOR_TO_FACTOR.keys()) + r")\b",
    re.IGNORECASE,
)

def has_numeric_token(sentence: str) -> bool:
    if re.search(r"\d", sentence):
        return True
    if _COMPARE_MULT_ANCHOR_TOKENS_RE.search(sentence):
        return True
    return bool(_WORD_NUMBER_RE.search(sentence))
```

i.e. extend `has_numeric_token` to also recognize the closed `_ANCHOR_TO_FACTOR` multiplier-word set
(`twice, thrice, half, quarter, third, ...` — the same closed set the compare-multiplicative compiler
already trusts). This is a **general, shared-primitive fix** (unlike the mass-noun regex in §2, which is
case-bespoke) and is plausibly the right minimal change. **It is deliberately not being re-landed now**:
per the recalibration guardrails, a shared-grounding-primitive change must be proven coverage-neutral-or-
positive AND `wrong=0` on the full 500 before it lands, and it belongs together with whatever compare op
actually consumes the newly-admitted statements (landing the classifier fix alone, with nothing downstream
able to extract the now-visible sentence, only changes *which* refusal reason a case gets — not its
correct/wrong/refused bucket). Whoever revisits this should re-run the full 500 with only this isolated
change and confirm zero `correct → refused/wrong` regressions before considering it a candidate for main.

---

## 2. Case 0148 — solves correct-for-the-right-reason (verified target, not landed)

**Case**: `gsm8k-holdout-dev-v1-0148` — *"At a people counting station, the number of people counted on
the first day was twice the total number counted on the second day. If 500 people were counted on the
second day, how many people were counted on the two days?"* — expected answer **1500**.

**Why it refuses on `main` today** (verified): the statement sentence *does* survive the
`has_numeric_token` filter (§1.2 — single-statement case), and the recognizer does match its shape, but
produces no injection:

```
refusal_reason: "recognizer matched but produced no injection for statement: 'At a people counting
station, the number of people counted on the first day was twice the total number counted on the second
day.' (category=descriptive_setup_no_quantity)"
```

The real gap is that `main`'s compare-multiplicative extractor requires a `ProperName` actor
(`extract_proper_noun_subject`), and 0148's actors are mass-noun/temporal descriptions ("the first day" /
"the second day") — not proper nouns, and not covered by any pattern on `main`. This is a genuine surface
gap, not a solver gap.

**Decomposition (the correct-for-the-right-reason target)**:
- seed: **second day = 500** (bound from the conditional clause "If 500 people were counted on the second
  day")
- compare: **first day = 2 × second day** (forward multiplicative compare)
- question: summation over both registers → **500 + 1000 = 1500**

**Verified by running the abandoned branch's code** (`origin/feat/reader-inc2-caseband @ e3da148d`, via a
throwaway detached worktree, `uv run python -c 'from generate.math_candidate_graph import
parse_and_solve; ...'`, worktree since removed) — this is the actual graph dump, not the empty file the
branch committed (see §3):

```json
{
  "answer": 1500.0,
  "is_admitted": true,
  "refusal_reason": null,
  "branches_enumerated": 1,
  "branches_admissible": 1,
  "selected_graph": {
    "entities": ["the first day", "the second day"],
    "initial_state": [
      {"entity": "the second day", "quantity": {"value": 500, "unit": "people"}}
    ],
    "operations": [
      {
        "actor": "the first day",
        "kind": "compare_multiplicative",
        "operand": {"reference_actor": "the second day", "delta": null, "factor": 2.0, "direction": "times"},
        "target": null
      }
    ],
    "unknown": {"entity": null, "unit": "people"}
  }
}
```

This confirms the 3-part correct-for-the-right-reason standard: the conditional-seed bound the *named*
reference (second day = 500, not a nearest/other entity), the compare op reads **forward** (first =
2×second, matching the source's "first day was twice the ... second day" — not an inverted reading), and
the unknown resolves via summation over exactly these two registers — 1500 from *this* graph, not a
coincidental path. On `main` (no mass-noun frame), the same case correctly refuses rather than guessing.

**What produced this conversion on the branch** (for context — not being landed): a bespoke
`_COMPARE_MASSNOUN_RE` regex family (`generate/math_candidate_parser.py`), a relaxation of the
proper-noun-only actor gate in `inject_comparative_multiplicative`
(`generate/recognizer_anchor_inject.py`) to allow mass-noun actors when that regex matches, and Gate A1
quantity-marker widening (`_COMPARATIVE_TOKENS` in `generate/recognizer_match.py` and
`evals/refusal_taxonomy/shape_categories.py`). All of this is bespoke to the 0148 surface shape and is the
kind of pattern the geometric-normalization direction (ADR-0251) is meant to supersede rather than
multiply — see the overfit inventory.

**Full-500 measurement on the branch** (`evals/gsm8k_math/holdout_dev/v1/report.json` diff): exactly one
case flipped, `0148: refused → correct`; counts `correct 5→6, refused 495→494, wrong=0→0` (held). Clean
single-case signature, no compensating regressions — this is genuine evidence, reproduced here for the
record since it lived only in a diff on an abandoned branch.

---

## 3. A correction to the branch's own narrative (why "verify, don't claim" matters here)

The branch's session-break summary (`docs/sessions/session-break-summary-2026-07-19-1310.md`, branch tip)
claimed: *"Graph dump for case 0148 committed to `docs/research/0148-first-conversion-proof.md` as proof
of correct-for-the-right-reason binding."* This is false — the committed file is **0 bytes**
(`git cat-file -s origin/feat/reader-inc2-caseband:docs/research/0148-first-conversion-proof.md` → `0`).
The actual graph dump was never captured to disk on the branch; only the narrative claimed it was. The
real artifact now lives in `docs/research/0148-first-conversion-proof.md` on this recalibration branch
(§2 above, generated fresh from the branch's code and independently re-verified against `main`'s refusal
behavior for the same case).

This is also why the human reviewer's second PR-review pass (PR #80 comment) flagged "commit evidence
before merge" as a blocker rather than accepting the summary's claim at face value — the discrepancy
between claimed and actual state is exactly the failure mode "verify, don't claim" exists to catch.

---

## 4. Disposition

Nothing in this note authorizes building on it. It exists so that a future, non-bespoke increment (the
geometric-normalization spike proposed in ADR-0251, or whatever a human ruling selects) has real,
re-verified targets — the 0148 decomposition and the `has_numeric_token` fix idea — instead of having to
rediscover them from an abandoned branch.
