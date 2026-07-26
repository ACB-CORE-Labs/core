# Grammar Unification — Plan of Record

**Date:** 2026-07-26 · **Status:** ACTIVE · **Base:** main @ `9696443a`
(post ADR-0264 ratification, PR #127)

> **One sentence:** CORE cannot read its own writing — measured 0/280 — and this
> arc makes reading and writing share one grammar so that every construction
> taught works in both directions, with round-trip as the falsifiable gate.

---

## 0. Why this arc, and why now

The curriculum-license-loop arc closed on the finding that the outcome-mix
ruling is the binding constraint for *curriculum* serving. That finding stands.
It is not, however, the binding constraint on **delivered capability**, and the
measurements in §1 say what is.

Six ADR-scoped deduction bands (v1, v1b, v2-EN, v3-MEM, v4-CM, v5-VP, v6-EX) are
ratified, flag-ON, and `wrong=0`. They are reachable only through
`looks_like_deductive_argument`, which is *sentence-initial "therefore"*:

```
"If it rains then the ground is wet. It rains. Therefore the ground is wet."
  → Given: if it rains then the ground is wet; it rains.
    Your premises entail: the ground is wet.                    DECIDED

"It rains. So the ground is wet, right?"
  → Pack-resident tokens — pack-grounded (en_core_cognition_v1):
    ground (relation.ground; predicate.support)…                TOKEN DUMP

"All men are mortal and Socrates is a man, so he must be mortal."
  → Pack-resident tokens — pack-grounded (en_core_quantitative_v1):
    all (quantitative.universal.total…)                         TOKEN DUMP
```

Each band widened what CORE can **decide**. None widened what a person can
**ask**. Deepening the room behind the keyhole is not progress in delivered
capability, and the keyhole is a *reading* problem.

This arc is scoped to the reading/writing seam. It does **not** author content,
does **not** move a flag, and does **not** touch the decision layer.

---

## 1. Measured baseline

Every number below was measured on `main` @ `9696443a` by reading source and
running probes, not inferred from docs. Reproduction scripts land in Phase 1.

### 1.1 The writer that serves is eight format strings

`generate/semantic_templates.py::render_semantic` — the function
`core/cognition/pipeline.py` actually calls — is a dict of **8** format strings
keyed on `IntentTag`, plus a predicate-display dict. No morphology, no
agreement, no tense, no negation, no pluralization, no clause joining.

Best-case live output:

> **Q:** Explain knowledge.
> **A:** Knowledge is what a person knows from truth and evidence. Furthermore,
> it belongs to cognition.knowledge. In turn, it requires evidence.

One fact per sentence, uniform subject-predicate-object, connectives from a
fixed bucket, and an internal dotted path (`cognition.knowledge`) leaking into
prose.

### 1.2 The good realizer exists and never serves

`generate/templates.py::render_step` (232 lines) has real linguistics —
quantifier agreement, mass vs count nouns, irregular morphology, tense/aspect,
and via `realize_target` it joins clauses with *and / or / that / which*.

It is called from exactly three places, **all `evals/*/runner.py`**.
`core/cognition/pipeline.py` calls `realize_semantic`, never `realize_target`.
This was deliberate — `core/cognition/surface_resolution.py` records that the
`realize_semantic` path "was granted supremacy by the Shadow Coherence Gate" —
but the consequence is that **`english_fluency_ood` 117/117 + 39/39 scores a
function that never speaks.**

### 1.3 Linguistic knowledge is duplicated 35-vs-9 ways, Jaccard 0.083

| | word-tables | distinct words |
|---|---|---|
| reading path (9 files) | **35** | 202 |
| writing path (6 files) | **9** | 359 |
| shared | — | **43** of 518 union (**Jaccard 0.083**) |

Tables that should agree and do not:

| linguistic fact | copies | status |
|---|---|---|
| irregular plurals | **3** (`member.py` 29, `reader.py` 8, `templates.py` 25) | **all three diverge** |
| quantifier tokens | **5** across both paths | **3-way divergence** |
| connective tokens | **4** (`english`, `member`, `verb`, `cond_member`) | 3 identical, `english` adds `therefore` |
| sentential-negation prefix | 2 (`english`, `member`) | identical |
| negation-bearing tokens | 2 | diverge by `'not'` |
| predicate display | 2 (`semantic_templates`, `templates`) | identical, 26 entries |
| copula forms | 2 | same content, different type (frozenset vs tuple) |

Demonstrated consequences of the plural divergence:

- CORE **reads** `wolves / knives / leaves / thieves / halves / loaves / elves /
  cacti / fungi / dice / aircraft / offspring` and **cannot write** them —
  `pluralize("cactus") → "cactuses"`, `pluralize("die") → "dies"`.
- CORE **writes** `criterion→criteria, phenomenon→phenomena, analysis→analyses,
  hypothesis→hypotheses, axis→axes, basis→bases, thesis→theses` and the reader's
  table knows **none** of those plurals.

Note this duplication is **not only** read-vs-write: two of the three plural
tables are both on the reading side, and four connective tables are all on the
reading side. The six deduction bands were built as successive independent
tiers, each re-encoding English from scratch.

### 1.4 A demonstrated grammar defect: 9 of 26 predicates mis-agree

`_inflect_predicate(display, plural_subject=True)` against a hand-written
English oracle:

```
plural-subject agreement over _PREDICATE_DISPLAY: 17/26 correct, 9 WRONG

  belongs_to             'belongs to'              -> 'belongs to'              want 'belong to'
  causes                 'causes'                  -> 'caus'                    want 'cause'
  contrasts_with         'contrasts with'          -> 'contrasts with'          want 'contrast with'
  has_steps              'has the following steps' -> 'has the following step'   want 'have the following steps'
  is_caused_by           'is caused by'            -> 'is caused by'            want 'are caused by'
  is_defined_as          'is defined as'           -> 'is defined a'            want 'are defined as'
  is_distinguished_from  'is distinguished from'   -> 'is distinguished from'   want 'are distinguished from'
  is_grounded_in         'is grounded in'          -> 'is grounded in'          want 'are grounded in'
  is_verified_as         'is verified as'          -> 'is verified a'           want 'are verified as'
```

Live example: `render_step(ASSERT, "wolf", "is_defined_as", "mammal",
quantifier="all")` → **`"all wolves is defined a mammal"`**.

Two root causes, both single-point:

1. **`base_form()` is written for single verbs and applied to whole humanized
   predicate phrases.** It strips the last character-class of the final word:
   `"is defined as" → "is defined a"`, `"has the following steps" → "has the
   following step"`, `"causes" → "caus"`.
2. **The `copular` flag is computed in `_inflect_predicate` and consulted only
   on the negated-singular branch.** The plural branch
   (`case (_, _, False, True)`) ignores it, so `is/has/belongs` never becomes
   `are/have/belong`.

Singular is clean: 0 of 26 differ. **This defect reaches zero served turns
today** because `render_step` is eval-only (§1.2). It matters because the
fluency suite scores this function, and because Phase 4 would wire it into
serving.

### 1.5 The fluency instrument is decorative

`evals/deterministic_fluency` reports **1.00 on all six predicates**. Control
test (the absence test — a green measurement that would look identical with the
mechanism removed):

| candidate surface | passes all 5 content predicates? |
|---|---|
| `"Truth is what corresponds to reality, and knowledge is belief grounded in it."` | yes |
| `"colorless green ideas sleep furiously."` | yes |
| `"wet ground rains the is."` | **yes** |
| `"is is is is."` | **yes** |
| `"banana does the."` | **yes** |

It checks terminal punctuation, presence of a verb-ish token, and two
anti-shape regexes. **It cannot distinguish English from word salad.**

And the suite cannot see §1.4 either. Across all **280** cases in
`english_fluency_ood` + `grammatical_coverage`:

- 40 use a quantifier — only `all` and `some`
- **0** use any copular predicate
- **0** exercise the quantifier × copular combination that breaks

`english_fluency_ood`'s own `accept_surfaces` include `"river flows valley"` and
`"wind shapes dune"` — token-ordered, not English. The 100% is real against the
lane's contract and says nothing about fluency.

### 1.6 The headline: round-trip is 0/280, and all six readers refuse

Feed each of the 280 writer-produced surfaces to `meaning_graph.comprehend`:

```
surfaces written by CORE : 280
reader COMPREHENDED      : 0/280 = 0.0%
reader REFUSED           : 280/280 = 100.0%
refusal reasons          : {'no_template_match': 280}
```

Control (proves the harness works): the reader comprehends 31/166 = 18.7% of the
`deduction_serve` corpus, and `comprehend("Socrates is a man.")` returns
2 entities + `member(socrates, man)`.

Six readers × four writer outputs, including CORE's own **live served**
surfaces — **24 refusals, 0 comprehensions**:

| writer output | comprehend | english | member | cond_member | verb | exist |
|---|---|---|---|---|---|---|
| `Molecule binds enzyme.` (writer's own accept_surface) | no_template_match | no_conclusion | out_of_band | out_of_band | no_conclusion | no_conclusion |
| `all wolves is defined a mammal` | no_template_match | empty | empty | empty | empty | empty |
| `Knowledge is what a person knows from truth and evidence.` (**live**) | no_template_match | no_conclusion | mixed_structure | out_of_band | mixed_structure | mixed_structure |
| `Wisdom is a good use of knowledge. Furthermore, it belongs to cognition.wisdom.` (**live**) | reserved_word_in_np | membership_shape | out_of_band | out_of_band | out_of_band | out_of_band |

### 1.7 The models are not type-compatible

A literal `read(write(g)) == g` is not expressible today:

- `MeaningGraph` = `Entity(entity_id, name, span, kind)` +
  `Relation(predicate, arguments: tuple[str, ...], span, negated)` — n-ary
  predicate/argument structure with source spans.
- `PropositionGraph` = `GraphNode(node_id, subject, predicate, obj,
  source_intent, language, root, morphology_id)` +
  `GraphEdge(source, target, relation)` — fixed SPO triples with discourse edges.

Round-trip therefore needs a **defined projection**, not identity. Choosing that
projection is Phase 1's first design decision, and §6 records why this matters
for direction.

---

## 2. Goal, non-goals, and the thesis check

**Goal.** One grammar, used in both directions, so that a construction taught
once works for reading and for writing, and so that surface diversity becomes
*verifiable* rather than risky.

**Non-goals — stated so success is not silently redefined:**

- **Not "prettier prose."** Fluidity is a function of construction-inventory
  size, which is content work. This arc builds the mechanism that makes growing
  the inventory safe and measurable.
- **Not an LLM, sampler, or paraphraser.** No stochastic generation enters the
  truth path. See the thesis check below.
- **Not curriculum content.** Scripture/theology content is separately deferred
  (word-for-word verification + a faith-domain evidentiary regime are both
  undesigned).
- **Not a graph-model merge.** §1.7 says that may be needed; §6 makes it a
  measured decision for a *later* arc behind an ADR, not a silent expansion of
  this one.

**Thesis check — "decoding, not generating."** Every ADR must pass this. A
bidirectional grammar is a *decoder run in reverse*: writing selects among
surface forms that the decoder provably maps back to the same graph. Nothing is
sampled, nothing is invented, and every emitted variant carries a proof of
meaning-preservation. Diversity comes from *enumerating verified forms*, not
from generating candidates and hoping. `chat/register_variation.py` already
implements exactly the deterministic seeded selector this needs (uniform,
replay-stable, `variant_id` in the audit stream).

---

## 3. The central design decision: the instrument *is* the fix

An honest fluency measurement cannot be built out of heuristic predicates — §1.5
is what that attempt already produced, and any new heuristic set will be gameable
the same way. **You cannot measure grammaticality without a grammar.**

Therefore the instrument and the remedy are one artifact:

- A grammar that **parses** is a measurement (word salad fails to parse).
- The same grammar used to **generate** is the remedy.
- **Round-trip** forces one artifact to do both, and is falsifiable without a
  judge, an embedding, or a gold aesthetic.

**Necessary, not sufficient — stated up front.** Round-trip measures *mutual
intelligibility*, not English quality. `"river flows valley"` may round-trip
perfectly while remaining un-English, because both sides can share an
impoverished construction. So the lane needs two corpora and both are load-bearing:

- a **positive** corpus (round-trip must succeed), and
- a **negative** corpus of word salad (round-trip must fail, 100%).

If the lane ever reports high scores on both, the lane is broken. That
bidirectional requirement is what keeps this instrument from becoming the next
§1.5.

---

## 4. Phases

Each phase is independently valuable, independently landable, and has a
falsifiable exit test. Phases 1–3 cannot change serving behaviour. Phase 4 is
the first that can, and is gated on explicit authorization.

### Phase 1 — Build the instrument, record the baseline

*Touches:* new `evals/grammar_roundtrip/`, new `generate/grammar/` (smallest
shared construction inventory), reproduction scripts for every §1 number.
*Serving risk:* none (new files + eval lane only).

Deliver:

1. `evals/grammar_roundtrip/` lane reporting, over a positive corpus:
   `write_rate`, `read_rate`, `graph_match_rate` under the chosen projection.
2. Over a **negative** corpus (hand-written word salad + programmatically
   shuffled tokens from positive cases): `reject_rate`.
3. The chosen `MeaningGraph`↔`PropositionGraph` projection, written down with
   what it deliberately discards.
4. Reproduction scripts for §1.3–§1.6 so every number in this plan is re-runnable.

**Exit criteria (all required):**

| criterion | measure |
|---|---|
| baseline recorded | `read_rate` on the 280-case corpus, expected ≈ 0.0% |
| word salad rejected | `reject_rate` = **1.00** on the negative corpus |
| lane is non-vacuous | mutating the reader to accept-everything drives `reject_rate` → 0 (**must go red**) |
| no behaviour change | smoke **621**, deductive **349**, 11/11 lane SHA pins unchanged |

**Failure / stop condition:** if the negative corpus cannot be rejected without
also rejecting the positive corpus, the grammar formulation is wrong. **Stop and
reassess — do not tune a threshold to split them.**

### Phase 2 — One source of linguistic truth

*Touches:* the 44 word-tables in §1.3; new single-owner modules.
*Serving risk:* none intended, and proven by byte-identity.

Deliver:

1. One module owning each linguistic fact: plurals, quantifiers, connectives,
   copulas, negation-bearing tokens, predicate display.
2. The **identical** duplicate groups collapsed — 3 connective tables, 2
   `_SENTENTIAL_NOT`, 2 predicate-display tables — with byte-identical lane
   hashes as the proof of zero behaviour change.
3. Each of the **4 real divergences** resolved by an explicit recorded decision
   (not by picking the larger table), with a test pinning the chosen answer.
4. A structural test asserting no module defines a second copy — same discipline
   as `tests/test_volume_honesty.py`, which must fail if a duplicate is
   reintroduced.

**Exit criteria:**

| criterion | measure |
|---|---|
| duplication removed | one table per fact; structural test green and mutation-red |
| identical collapses are inert | 11/11 lane SHA pins **byte-identical** |
| divergences decided, not averaged | each of the 4 has a recorded decision + pinning test |
| agreement | Jaccard → 1.00 for facts that should agree (from 0.083 overall) |

**Failure / stop condition:** if collapsing an "identical" pair moves a lane
hash, the tables were not actually identical — stop, and treat it as a
divergence requiring a decision.

### Phase 3 — Fix the 9-of-26 agreement defect

*Touches:* `generate/morphology.py::base_form`, `generate/templates.py::_inflect_predicate`,
new eval cases. Depends on Phase 2 (unified tables) and Phase 1 (instrument).
*Serving risk:* none (`render_step` is eval-only).

Deliver:

1. `base_form` no longer applied to multi-word phrases — phrase-head handling.
2. The `copular` flag consulted on the plural branch.
3. Eval cases covering **quantifier × copular**, which is 0 of 280 today.

**Exit criteria:**

| criterion | measure |
|---|---|
| agreement correct | **26/26** against the oracle (from 17/26) |
| the gap is closed for good | new cases exercise quantifier × copular; reverting either fix goes red |
| no regression | `english_fluency_ood` 117/117 + 39/39 holds; smoke/deductive unchanged |

### Phase 4 — Resolve `realize_semantic` vs `realize_target` — **authorization gate**

*Touches:* `core/cognition/pipeline.py` or the eval lanes. **First phase that can
change served output.** Requires explicit authorization before merge.

The current state is untenable in one specific way: 149 green fluency cases
score a function that never serves. Exactly one of these must become true:

- **(a)** `realize_target` earns the serving path, gated on the Phase 1
  round-trip instrument and a `wrong=0` hold; or
- **(b)** the lanes scoring it are retired/re-pointed, and the claim
  "realizer fluency is mechanistic" is restated as a claim about eval-only code.

**Exit criterion:** no eval lane scores a non-serving function. Whichever branch
is taken is recorded with its reasoning.

**Why this is gated:** (a) changes what users see and would move surface hashes.
It is a serving change and belongs to Shay, not to this plan.

### Phase 5 — Raise round-trip, then earn diversity

*Depends on:* Phases 1–3, and on the Phase 1 baseline being non-zero-able.
*Scope: deliberately unestimated* — see §5.

Deliver:

1. Construction inventory grown until `read_rate` clears a floor, with the floor
   ratcheted (never lowered to accommodate a regression).
2. **N > 1** verified surface forms per graph, each proven to round-trip to the
   same graph.
3. Deterministic seeded selection among verified variants, reusing
   `chat/register_variation.py`'s existing selector, with `variant_id` in the
   audit stream.

**Exit criteria:**

| criterion | measure |
|---|---|
| round-trip improved | `read_rate` clears a ratcheted floor, well above the ≈0% baseline |
| diversity is real | mean verified variants per graph > 1, measured |
| diversity is safe | 100% of emitted variants round-trip to the source graph — **zero exceptions** |
| truth path untouched | `wrong=0` holds; variant selection provably cannot alter a verdict |

---

## 5. What is deliberately not estimated

Phase 5's size cannot be estimated before Phase 1 produces real numbers, and
pretending otherwise is how the last arc acquired an unreachable exit criterion.
Phases 1–3 are bounded and specified. **Phase 5 is scoped only after Phase 3
reports.**

I also do not claim Phases 1–4 produce human-like prose. They produce: a
measurement that cannot be faked, a single source of linguistic truth, a fixed
agreement defect, and an honest answer about which realizer serves. That is the
foundation the diversity work needs — and it is worth landing even if Phase 5 is
later judged infeasible.

---

## 6. The decision rule for afterwards

The point of the instrument is that the *next* direction is chosen by a number,
not by argument. After Phase 3, `read_rate` is re-measured on the unified
grammar. That number forks the road:

- **`read_rate` rises materially from unification alone** ⇒ the two grammars were
  closer than they looked, the surface layer was the barrier, and Phase 5
  (diversity) is the right next arc.
- **`read_rate` stays near zero after unification** ⇒ the barrier is **§1.7**:
  `MeaningGraph` and `PropositionGraph` are genuinely different models, and no
  amount of table-sharing bridges them. The next arc is then a **graph-model**
  decision, which is large, touches the decision layer, and **must go to an ADR
  before any code**. It is explicitly *not* an extension of this plan.

Either way we will know which, and why, from a measured quantity — which is the
thing the previous arc could not do until after it had built the machinery.

**One reading of the evidence is worth pre-committing to now:** §1.6's uniform
`no_template_match` across all 280, combined with §1.7's type mismatch, makes
the second fork more likely than the first. If that is where we land, Phases 1–3
are still exactly the right work — they are what makes the graph-model question
answerable instead of speculative — but the arc should be expected to *end* at
the ADR rather than at fluid prose.

---

## 7. Verification protocol

Per `AGENTS.md`, unchanged from prior arcs:

- Every phase, in-worktree on canonical CPython 3.12.13 with `uv sync --locked`,
  before push: `uv run core test --suite smoke -q` then `--suite deductive -q`.
  Baselines: **smoke 621 / deductive 349**.
- Every new gate must **fail under mutation**. A pin that cannot fail is
  worthless — this arc exists because three such pins were found (§1.5, the Rust
  parity lane, and the fluency suite's blind spot).
- Phase 2 additionally requires **byte-identical** 11/11 lane SHA pins.
  Never `scripts/verify_lane_shas.py --update`; surgical single-line edits only.
- One PR per phase, branch + worktree each, Forgejo compare URL,
  `[Verification]:` line. No merge automation — PRs sit until authorized.
- Phase 4 additionally requires explicit serving-change authorization.

## 8. Standing traps carried into this arc

- **`then` / `therefore` are taught `philosophy_theology` lemmas AND the argument
  reader's control words.** The vocabulary boundary is never screened against the
  reader's grammar. A unified grammar makes this screenable for the first time —
  and makes forgetting to screen it a single-point failure. Add the screen in
  Phase 2.
- Corpus-mutating tests must never write committed files: the `full` suite
  injects `-n auto`, so writes race.
- Never "fix" a hash drift or a ledger inventory to make a test pass.
- `PYO3_PYTHON=/opt/homebrew/bin/python3.12` is required for `core-rs` builds.
