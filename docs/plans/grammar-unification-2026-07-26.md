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

### 1.7 A ratified band serves malformed English today

This was found while designing Phase 1's projection, and it is the most
consequential item in §1 because it is **user-visible on a ratified, flag-ON
band**.

`generate/proof_chain/render.py`:

```python
_CATEGORICAL_PHRASE = {
    "A": "all {s} are {p}",     # plural syntax…
    "E": "no {s} are {p}",
    "I": "some {s} are {p}",
    "O": "some {s} are not {p}",
}
```

…but `{s}` / `{p}` are filled with the **singularized entity ids** the
MeaningGraph reader produces (`_chunk_class` → `_singularize`). There is no
re-pluralization step, because the reader and the renderer are on opposite sides
of the seam described in §1.3. Result, live through `deduction_grounded_surface`:

```
in : All dogs are mammals. All mammals are animals. Therefore all dogs are animals.
out: Given: all dog are mammal; all mammal are animal. That's valid — all dog are animal follows.

in : No dogs are cats. All cats are animals. Therefore no dogs are animals.
out: Given: no dog are cat; all cat are animal. That doesn't follow — …

in : All wolves are mammals. All mammals are animals. Therefore all wolves are animals.
out: Given: all wolve are mammal; … — all wolve are animal follows.
```

Scope, measured two ways:

- **Synthetically: every plural noun**, regular or irregular. `all dog are
  mammal`, `all cat are mammal`, `all student are mammal`, `all child are
  mammal`, `all man are mammal`.
- **In the ratified corpus: 4 of 47** cases that serve a categorical clause —
  `ds-v1-0023`, `ds-v1-0024`, `ds-v1-0026`, `ds-v1-0028`, all band v1. The corpus
  under-represents the defect only because band routing sends most arguments to
  renderers that echo the user's original text.

**`wrong=0` is not threatened.** Every verdict above is correct; this is purely a
surface defect. Two distinct causes compound in it:

1. **No re-pluralization at render time** — affects *all* nouns. This is the
   dominant cause.
2. **The reader's plural table is 8 entries** where the v3-MEM band's is 29, so
   `wolves → wolve`, `knives → knive`, `leaves → leave`, `lives → live`,
   `halves → halve`, `loaves → loave`, `thieves → thieve`, `elves → elve`
   — **8 silently wrong singulars**, and 4 more (`cacti`, `dice`, `fungi`,
   `oxen`) that refuse outright. **CORE's two readers disagree on 12 of 20
   plurals.**

The wrong singulars do *not* break soundness, because `_singularize` is a
deterministic function applied uniformly to premises and conclusion, so the
lowering stays a consistent bijection. They are label defects — and they are the
reason cause (2) must be fixed with a *shared* table rather than by patching one
side.

### 1.8 The models are not type-compatible

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

### 1.9 §1.3 re-measured during Phase 2A — mostly subsets, not contradictions

§1.3 was counted by name and by table size. Reading the actual values while
building `generate/lexicon.py` changed the picture materially, and in CORE's
favour: **almost nothing contradicts.**

| §1.3 claim | measured | correction |
|---|---|---|
| irregular plurals: 3 copies, all diverge | 1 pluralizer + 2 singularizers | **direction confusion.** `templates` is singular→plural; `member`/`reader` are plural→singular. Comparing them as copies is a category error. |
| — | `reader` ⊂ `member`, difference empty | **no disagreement.** The reader's 8 values all agree; only its coverage is short. |
| quantifier tokens: 5 copies, 3-way divergence | 3 *distinct facts* | `QUANTIFIER_LEAD` (can lead a clause), `QUANTIFIER_TOKENS` (⊃ lead, adds pronouns), `PLURAL_QUANTIFIERS` (forces plural agreement). `every`/`each` lead but take singular nouns, so their absence from the third is **correct**. |
| connectives: 4 copies, `english` adds `therefore` | 3 identical + 1 derived | confirmed; the 4th is `english._STRUCTURAL`, exactly `CONNECTIVES ∪ {therefore}`. |
| negation-bearing: 2, diverge by `'not'` | `english` ⊂ `member` | confirmed, and the difference is **principled**: v2-EN normalizes `<copula> not`, v3-MEM refuses all non-copular `not`. |
| copula forms: 2 copies | **5 copies** | undercounted. The structural test found `realizer_guard._BE_AUX` and `chat/runtime._BE_FORMS` — same four words, auxiliary role, invisible to a `COPULA`-shaped grep. |

Exactly **one** genuine contradiction exists in the whole inventory:
`discourse_planner._PREDICATE_HUMANIZE` maps `is_defined_as` → `"is"` where the
other two map it to `"is defined as"`. Preserved as a deliberate register choice
(the short copula reads as prose mid-paragraph), pinned by test.

⇒ The §1.3 framing "tables that should agree and do not" overstated the disease.
The accurate diagnosis is **coverage asymmetry plus three facts sharing one
name**, which is a better problem to have: subsets can be derived from their
superset with zero behaviour change, which is why Phase 2A came back 11/11
byte-identical.

**Worse than §1.7 stated, though.** `reader._singularize` does not refuse
uncovered plurals despite a comment claiming it does — it falls through to a
bare `-s` strip. So `news` → `new` and `species` → `specy`: precisely the
corruptions `member.py`'s table comment says its table exists to prevent. Same
fact, one file guarded, the other not. Pinned as current behaviour in
`tests/test_lexicon_single_source.py`; Phase 2B must flip it.

### 1.10 The destination for morphology already exists and is disconnected

ADR-0258 §5 decided that the number table "moves from module constants to a
ratified pack" **when a `grc_*`/`he_*` member band is built.** That trigger has
not fired (no such band exists in `generate/proof_chain/`), so the promotion is
correctly deferred — `generate/lexicon.py` is a staging area, not a competing
home, and no new ADR is warranted.

The destination's measured state, so the promotion is not planned on a guess:

- `packs/en/morphology.jsonl` = **9 records.** Seven are forms of *be*; two are
  noun plurals (`word`, `beginning`) that are **regular** and exist to support
  John 1:1. **Zero irregular English plurals exist as pack data.**
- **`features.number` has no consumer.** No code reads it.
- The only reader of `morphology.jsonl` is
  `chat/pack_resolver.py::_pack_morph_roots_for`, which extracts a top-level
  `root` key. **0 of 31 records across all four packs define `root`**, so it
  returns `{}` on every call while its docstring claims it "enables root-level
  depth (Hebrew triconsonantal, Greek stems)". A dead path, not a slow one.
- The pack is *richer* than the code on one point: it has `am`
  (`en:be:present:1sg`), which all five Python be-form copies lack.

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
- **Not a graph-model merge.** §1.8 says that may be needed; §6 makes it a
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
falsifiable exit test.

**Serving-risk classification — corrected 2026-07-26 after §1.7.** An earlier
draft of this plan asserted "Phases 1–3 cannot change serving behaviour." That
was **wrong**, and the error is worth recording because it is the same shape as
the mistakes this arc exists to fix: I classified a table as off-serving without
asking which callers reach it. `generate/meaning_graph/reader.py::_IRREGULAR_PLURALS`
**is** on the serving path — `comprehend` → `to_syllogism` → band v1b →
`deduction_grounded_surface`. Unifying it changes entity ids, which moves
trace hashes and served surfaces.

The corrected rule for this arc: **a table is off-serving only when every caller
is proven to be eval-only.** Phase 2 is therefore split by that test, not by
topic.

**Second correction, same session — the static test is not sufficient.** I then
computed the serving import closure (227 first-party modules from `chat/runtime.py`,
`core/cognition/pipeline.py`, `chat/deduction_surface.py`,
`chat/curriculum_surface.py`, `chat/pack_grounding.py`,
`chat/teaching_grounding.py`) and **all 13 table-owning modules are in it —
13 of 13**, including `generate/templates.py` via
`pipeline.py` → `realizer.py` → `templates.py`. A static import test therefore
returns "everything is serving" and discriminates nothing.

**Import-reachable is not call-reachable.** Importing a module executes its
table literals (pure data) but not its functions. The call chain
`realize_target` → `render_step` → `_inflect_predicate` → `base_form` is
closed and small enough to verify exhaustively, and `realize_target` has **zero
non-eval, non-test callers** — so that subtree is genuinely call-unreachable
from serving, and §1.2/§1.4 stand.

But Python call-reachability is not statically decidable in general, so the
arbiter for this arc is **empirical, not analytical**: make the change, run the
11 pinned lanes, and let byte-identity decide. That is stronger than a static
claim because it tests behaviour rather than predicting it, and it is the
doctrine the lane pins already encode.

⇒ **The 2A/2B split is therefore a *result*, not a prediction.** A change is 2A
if the pins come back byte-identical and 2B if they move. Work the changes in
the order below, run the pins, and let the split fall out. Do not argue a change
into 2A.

| phase | changes served output? | gate |
|---|---|---|
| 1 — instrument | no (new files only) | local smoke/deductive |
| 2A — changes the pins prove inert | no (**measured**, not predicted) | byte-identical lane SHAs |
| 2B — changes that move a pin | **yes** | **explicit authorization** |
| 3 — agreement defect | no (`realize_target` has zero serving callers) | 26/26 oracle |
| 4 — which realizer serves | **yes** | **explicit authorization** |
| 5 — round-trip + diversity | **yes** | **explicit authorization** |

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
4. Reproduction scripts for §1.3–§1.7 so every number in this plan is re-runnable.

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

### Phase 2A — One source of linguistic truth (the hash-inert subset)

*Touches:* the word-tables in §1.3 whose unification the lane pins prove inert, plus
new single-owner modules. *Serving risk:* none, and proven by byte-identity.

Deliver:

1. One module owning each linguistic fact: plurals, quantifiers, connectives,
   copulas, negation-bearing tokens, predicate display.
2. The **identical** duplicate groups collapsed — 3 connective tables, 2
   `_SENTENTIAL_NOT`, 2 predicate-display tables — with byte-identical lane
   hashes as the proof of zero behaviour change.
3. Each divergence among off-serving tables resolved by an explicit recorded
   decision (not by picking the larger table), with a test pinning the answer.
4. A structural test asserting no module defines a second copy — same discipline
   as `tests/test_volume_honesty.py`, which must fail if a duplicate is
   reintroduced.
5. **A caller-provenance test**: for every table the new module owns, assert
   whether it is serving-reachable. This is the check whose absence produced the
   error corrected above, so it belongs in the tree, not in a reviewer's head.

**Exit criteria:**

| criterion | measure |
|---|---|
| duplication removed | one table per fact; structural test green and mutation-red |
| identical collapses are inert | 11/11 lane SHA pins **byte-identical** |
| divergences decided, not averaged | each has a recorded decision + pinning test |
| agreement | Jaccard → 1.00 for facts that should agree (from 0.083 overall) |
| serving reachability is known | caller-provenance test covers every owned table |

**Failure / stop condition:** if collapsing an "identical" pair moves a lane
hash, the tables were not actually identical — stop, treat it as a divergence
requiring a decision, and move it to Phase 2B.

**RESULT — the split fell entirely on the 2A side.** `generate/lexicon.py` owns
the tables; **11/11 lane SHA pins came back byte-identical**, so by the #129
rule every change in this unit is 2A and nothing spilled into 2B. Smoke 621
unchanged, deductive 383 (364 + 19 new).

Two exit criteria needed re-definition rather than just measuring, and both
re-definitions are recorded here because the original wording was unmeasurable:

- **"Jaccard → 1.00"** cannot be the measure. `measure_grammar_seam.py` scans
  *source literals*, so unifying a fact **removes** it from those files and
  Jaccard **fell**, 0.083 → 0.023. That is the success direction, reported by a
  metric shaped to read like failure. Replaced with an **object-identity**
  count: distinct underlying objects behind the consumer names, which is what
  "one source of truth" actually asserts. Comparing by value cannot distinguish
  a shared object from two equal copies, so identity is the only honest test.
  Measured: **3 distinct objects behind 8 names**, from 8-behind-8.
- **"one table per fact"** presumed the §1.3 fact inventory was right. §1.9
  shows it was not, so the report now separates `_SHOULD_AGREE` (must be one
  object → all **UNIFIED**) from `_RELATED_BUT_DISTINCT` (six expected
  relations, all **HOLD**: derived-plus-`therefore`, strict-superset,
  distinct-fact, differ-by-`not`, subset, inverse-direction).

**The structural test earned its place immediately**: it found two copies of the
be-form inventory (`realizer_guard._BE_AUX`, `chat/runtime._BE_FORMS`) that a
name-based grep missed because neither is named like a copula. §1.3's "2 copies"
was really 5.

### Phase 2B — Serving-path tables and the categorical render defect — **authorization gate**

*Touches:* `generate/meaning_graph/reader.py::_IRREGULAR_PLURALS`,
`generate/proof_chain/render.py::_CATEGORICAL_PHRASE`, the band readers' tables.
**Changes served surfaces and trace hashes.** Depends on 2A's shared pluralizer.

Deliver:

1. Re-pluralization at categorical render time, fixing `all dog are mammal` →
   `all dogs are mammals` (§1.7 cause 1 — affects *all* nouns).
2. The reader's 8-key view (`lexicon.READER_SINGULAR_KEYS`) widened to the full
   29-entry singularizer. **Corrected framing (§1.9):** the reader's 8 *values*
   are already right — they agree with the full table entry for entry — so this
   is a **coverage** fix, not a correctness fix, and there are no "8 silently
   wrong singulars." The silent wrongness is in the *fallback*:
   `reader._singularize` guesses via a bare `-s` strip instead of refusing, so
   `wolves`→`wolve`, `news`→`new`, `species`→`specy`. Its own comment claims it
   refuses; it does not. Those five are pinned as current behaviour in
   `tests/test_lexicon_single_source.py` and this phase must flip them.

   *Delivered differently than written:* the reader no longer holds a table at
   all. `generate/morphology.py` became the single owner of the number **rules**
   (2A owned the tables), and the reader calls `singularize`. That removed a
   second copy of the regular suffix rules, which was the actual reason the two
   sides disagreed about coverage.
3. Updated lane SHA pins — **surgical single-line edits only**, never
   `--update` — with the old and new hash recorded per lane.

**Exit criteria:**

| criterion | measure |
|---|---|
| surfaces well-formed | 0 malformed categorical surfaces; `ds-v1-0023/0024/0026/0028` render plurals |
| readers agree | reader-vs-reader singularization agreement **20/20** (from 8/20) |
| soundness preserved | `wrong=0` holds; deduction lane verdicts **unchanged case-for-case** |
| hash movement is intended | every moved pin explained; no pin changed that shouldn't move |

**Why gated:** this changes what users see. Fixing a defect is still a serving
change, and serving changes are Shay's call. *Authorized 2026-07-26.*

**RESULT.**

| criterion | measured |
|---|---|
| surfaces well-formed | **0 malformed of 47** (from 4); `ds-v1-0023/0024/0026/0028` all render plurals |
| readers agree | **20/20**, 0 silently wrong (from 8/20) |
| soundness preserved | `wrong=0` holds on all 7 bands; deductive **403 passed**, smoke **621** |
| round-trip | `s_surface_match_rate` **0.0 → 0.625**, and it now *equals* `s_renderable_rate` — every renderable surface returns its input exactly |
| hash movement is intended | **criterion void — the pins cannot see surfaces.** See below. |

#### The lane SHA pins are blind to served English

2B changed 4 of 47 served surfaces and the pins came back **11/11
byte-identical**. That is not evidence of no change; it is evidence the
instrument cannot see this kind of change.

Verified two ways rather than argued:

1. **By inspection.** The `deduction_serve_v1` hashed report contains only
   `n`, `counts`, `by_gold`, `correct_by_gold`, `all_cases_correct`,
   `mismatch_examples`. **No surface prose at all** — verdict classifications
   only.
2. **By sabotage** (the [[feedback-ask-what-if-the-thing-were-absent]] control).
   Making `render._display_noun` return `"SABOTAGE_" + …`, so every categorical
   clause reads `all SABOTAGE_dogs are SABOTAGE_animals`:

   | guard | caught it? |
   |---|---|
   | 11 lane SHA pins | **no — 11/11 still byte-identical** |
   | `test_deduction_serve_lane` + `_license` (20 tests) | **no — 20 passed** |
   | Phase 1 `grammar_roundtrip` | **yes — 3 tests red** |

⇒ **Correction to #129.** That PR established the arc's arbiter as "make the
change, run the 11 pinned lanes, let byte-identity decide." For *values and
verdicts* that holds. For **surface text it decides nothing**, so the 2A/2B
split it defines is not a partition of "changes users can see." Phase 2A's
11/11 conclusion is still sound — 2A changed no value, confirmed independently
by 24/24 table-equality checks against the pre-migration literals — but the
justification was thinner than claimed, and 2B is what exposed it.

⇒ **Before Phase 1, no test in the tree would have noticed CORE's served prose
turning into word salad.** That is precisely how `all dog are mammal` survived
on a ratified, flag-ON band with `wrong=0` intact for the whole arc. The
round-trip lane is not a nice-to-have measurement; it is the only guard that
reads what the user reads.

**One correction to the sabotage table above.** The runner's own docstring named
`tests/test_deduction_surface.py` as the place wording is covered, and I had not
included that file in the first sabotage run. Tested: **all 41 of its tests pass
under the sabotage too.** So the exclusion's stated justification — "wording is
covered by tests/test_deduction_surface.py" — was false, not merely incomplete.
The claim survived the check that could have refuted it.

#### Closed — the pins now read what the user reads

Fixed in the same arc rather than deferred. `evals/deduction_serve/runner.py`
now puts `surface_sha256` **and** the per-case `surfaces` into the pinned
artifact, via `build_combined_report` (the earlier attempt missed because that
function re-projects five named fields per split and silently dropped the new
one — the payload is not the report).

| | before | after |
|---|---|---|
| pinned artifact | 2,766 bytes, verdict counts only | 37,280 bytes, every served sentence |
| `deduction_serve_v1` under sabotage | ✓ byte-identical (blind) | **✗ `52370b73` vs `c855d55c`** |

Re-pinned surgically — one line, old hash recorded in a comment beside it, never
`--update`. Verdicts are untouched (166/166 correct, `wrong=0`); the hash moved
because the payload grew.

`test_surface_hash_moves_when_the_renderer_is_sabotaged` makes this permanent:
it corrupts the renderer, requires a digest to move, **and** asserts the
aggregate verdict counts are unchanged — proving the digest tracks prose rather
than smuggling in a decision change. A pin that cannot fail guards nothing.

**Accepted cost, stated plainly:** wording-only changes now move this pin. That
is the intent — a wording change *is* a user-visible change and should require a
deliberate re-pin, which is exactly the discipline whose absence let
`all dog are mammal` serve for the whole arc.

The other 10 lanes are untouched. Whether their payloads should also carry
surfaces is a separate question this unit does not answer; `deduction_serve` was
fixed because it is the one demonstrably serving prose to users.

The Phase 1 instrument moved on its own, having been built with no knowledge of
this fix. That is the whole argument for building the instrument first.

**The near-miss worth recording — widening a reader can break soundness.**
Routing the reader through the full 29-entry singularizer initially produced
**wrong=1 on band v6-EX**: `ds-ex-0012` ("No fish are mammals. Therefore some
fish are mammals.") answered `invalid` where gold is `refuted`.

Cause: `_singularize` returning `None` makes the reader *refuse*, and the
serving composer tries the categorical band **first**, falling through to later,
more capable bands. `fish` previously returned `None` (it matches no suffix
rule), so v6-EX got the case and decided it correctly. Resolving `fish` made
**v1b accept a sentence it cannot decide** and answer wrongly.

Fix, and it is a principle rather than a patch: **a number-invariant form is
ambiguous in number** — "fish are mammals" is plural, "a fish is a mammal" is
singular, and the token cannot tell you which — so a reader that must not guess
number declines it. That simultaneously restores the fall-through *and* is the
honest reading. `lexicon.INVARIANT_NUMBER` is derived from the singularizer's
own `key == value` rows, so the rule cannot drift from the table.

⇒ **Coverage and correctness are different axes.** Fixing a corrupted *value*
(`wolves`→`wolve`) is safe; widening *acceptance* changes which band answers,
and in a first-match composer that can convert a right answer into a wrong one.
Same family as ADR-0261 §5.1 refuse-don't-drop. Bundling the two is how a
plural fix silently becomes a soundness regression.

**Also fixed, found by testing the inverse law:** the two number tables were not
mutual inverses — the pluralizer lacked `cactus→cacti`, `fungus→fungi`,
`die→dice` and the invariants `aircraft`/`means`/`offspring`, so CORE could
*read* `cacti` but wrote `cactuses`, and would have written "aircrafts",
"meanses", "offsprings". No round trip can close across a table that is not
invertible. Pinned by `test_the_two_number_directions_are_mutual_inverses`.

**Deliberately not fixed:** mass-noun verb agreement. "all evidence are truth"
should be "all evidence **is** truth", but the copula is fixed text inside the
A/E/I/O templates, so agreeing it changes the template shape rather than a slot.
No mass noun reaches a categorical clause in any serve corpus today. Recorded in
`render.py::_display_noun` rather than silently left.

### Phase 3 — Fix the 9-of-26 agreement defect

*Touches:* `generate/morphology.py::base_form`, `generate/templates.py::_inflect_predicate`,
new eval cases. Depends on Phase 2A (unified tables) and Phase 1 (instrument).
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

**RESULT — all three met.** Agreement **26/26** (from 17/26). `english_fluency_ood`
**117/117 + 39/39** (+ dev 13/13) unchanged. New construction **C14
`quantified_copular`**, 13 cases, `grammatical_coverage` v1 **49/49**.

Root causes, both single-point as §1.4 predicted:

1. `base_form` is a **single-verb** function and was applied to whole phrases,
   stripping the final word's last character-class. Fixed by
   `morphology.agree_plural_phrase`, which inflects the **head** (the finite
   verb is the first token of every humanized predicate) and carries the rest
   through. `base_form` itself is left single-verb and **pinned as still wrong
   on a phrase**, so nobody "fixes" the symptom in the wrong place.
2. The plural branch never consulted `copular` — it returned the bare base. Now
   it agrees the phrase. The plural **negated** branch had the same defect
   (`do not is defined a`) and is fixed with it: a plural copula takes a bare
   `not`, everything else takes do-support.

**Two further defects found while writing the cases**, both genuine and both
fixed here:

- `base_form("causes")` → **`"caus"`**. The `-es` sibilant rule fired on a
  stem ending in a single `s`; it should require a doubled `ss` ("passes" →
  "pass") because a single `s` is nearly always a stem ending in `e` that took a
  plain `-s` ("causes" → "cause").
- `pluralize("proof")` → **`"prooves"`**. `f`/`fe` → `ves` is **not productive
  in English** (proof→proofs, chief→chiefs, roof→roofs); it applies to a closed
  set. Now derived as `lexicon.VES_PLURAL_SINGULARS` from the `ves` rows of
  `IRREGULAR_SINGULARS`, so the rule cannot claim a word the table does not
  know. **Phase 2B had put `pluralize` on the serving path**, so this one was
  live.

**The first draft of the C14 cases could not fail.** `must_contain` and
`word_order` listed quantifier, subject and object — but *not the verb* — so
`all molecules is defined a compound` passed. Reverting the fix left 47/47 green.
Rewritten with the agreed verb in both constraints plus `reject_surfaces`
carrying the **actual** pre-fix output (computed by running the reverted code,
not guessed). Mutation now:

| reverted fix | C14 |
|---|---|
| baseline | 13/13 |
| phrase-head plural agreement | **4/13** |
| `-es` stem rule | **12/13** |
| closed `ves` set | **12/13** |

> **Correction (Phase 4).** The `ves` row was first recorded here as 11/13. Re-run
> against merged `main` by reverting the hunk in source — not by monkeypatch — it
> is **12/13**, and the single sensitive case is `gram_C14_p06` (`proofs`). The
> pin is still load-bearing; the recorded number was wrong. Corrected rather than
> left standing, because a mutation matrix nobody can reproduce is worth less
> than no matrix at all.

The 4 survivors of the first mutation are the mass-noun and unchanged controls,
which is the correct behaviour — `all evidence is grounded in truth` must *not*
pluralize. Same lesson as the lane pins in #133: a pin that cannot fail guards
nothing, and the only way to know is to break the thing on purpose.

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

**RESULT — (b), and the framing of the choice was wrong.**

The plan posed this as "which realizer is better". Reading the source says it is
not a quality question. `render_semantic`'s signature is
`(intent, subject, predicate, obj, secondary, language, root)` — there is **no
`negated`, `quantifier`, `tense` or `aspect` parameter**, and `realize_semantic`
never reads them off the step. So the serving writer does not merely inflect
worse; it cannot express content the `ArticulationStep` is carrying:

```
negated=False -> 'Knowledge is defined as opinion.'
negated=True  -> 'Knowledge is defined as opinion.'    <-- byte-identical
```

**It serves the affirmative of a negated proposition.** That is not a fluency
defect. It is the ADR-0261 §5.1 family — v1b served WRONG by dropping premises
it could not express — and it is pinned here as a defect, not fixed, because
fixing it changes served output.

Scored on the identical contract across all seven corpora that a lane runs
through `realize_target`:

| bucket | n | `realize_target` | `realize_semantic` |
|---|---|---|---|
| feature-bearing, single node | 214 | 207 | **49** |
| no features, multi-node | 100 | 100 | **3** |
| no features, single node — **CONTROL** | 33 | 33 | **33** |
| total | 347 | **340** | **85** |

The control is what makes the rest mean anything. Every corpus hardcodes
`IntentTag.UNKNOWN`, so "the serving writer scores badly" could have been an
artifact of never giving it a real intent. On the 33 cases carrying nothing it
cannot express, the two realizers are **identical** — so the gap on the other
314 is the dropped features (214) and clause joining (100), not the intent.

**What was delivered.** `grammatical_coverage/runner.py` now reports
`serving_accuracy` beside `accuracy`, computed by re-scoring the same cases
through `realize_semantic`; `english_fluency_ood` delegates to that `run_lane`
and gains it for free. The claim is restated at both places it was made — the
lane docstring and `grammar_roundtrip/contract.md` — as a claim about
**eval-only code**. Zero served bytes change, so this needed no serving
authorization.

**What was not delivered, deliberately.** (a) is still open and still Shay's.
The difference now is that it can be decided against a measured cost: promoting
`realize_target` buys 340/347 over 85/347 and the ability to say "not", and
costs a move in every surface hash plus whatever the Shadow Coherence Gate
ruling in `core/cognition/surface_resolution.py` was protecting.

### Phase 5 — Raise round-trip, then earn diversity

*Depends on:* Phases 1–3 plus 2B, and on the Phase 1 baseline being non-zero-able.
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

**RESULT (first unit) — the realizer question resolved, and it was a truth bug.**
See **ADR-0265**. Phase 4 ruled option (b) and pinned "`render_semantic` cannot
express negation" as a defect. Sizing the exposure before acting on it — the
step this plan's own §7 requires — showed the pin was correct and *incomplete*:
the defect is **two drops in series**, and the first is in the graph.

`intent.negated` has always been parsed from the user's words. `GraphNode` had
no field for it, so `graph_from_intent`, `ground_graph`, the pipeline's depth
enrichment, `intent_bridge` and `plan_articulation` each discarded it — five
constructors, each silently defaulting to the affirmative. Measured live under
`realizer_grounded_authority`:

```
"evidence does not support truth"  -> 'Evidence is verified: what supports truth.'
"evidence supports truth"          -> 'Evidence is verified: what supports truth.'
```

**Byte-identical — CORE affirmed what the user denied.** Live, not latent.
Default config was safe only by accident: the ungrounded realizer emits `...`,
`_is_useful_surface` rejects it, and the runtime echo (which contains the
user's own "does not") wins. Grounding removes the accident.

Delivered: `negated` threaded end to end, and the four intent "templates" that
were never frames delegated to `render_step`, the one owner of clause grammar.
Delegation measured **192/192 byte-identical** on affirmatives, so the only
surfaces that moved are ones that were wrong. `negated` serializes only when
True ⇒ no `trace_hash` and **no lane pin** moves.

The exhaustive control found five further intents — TRANSITIVE_QUERY,
FRAME_TRANSFER, NARRATIVE, EXAMPLE, DEDUCTION — each serving a denial as its
own assertion, because an intent without a frame fell back to the UNKNOWN
*template* rather than the UNKNOWN *clause*. Found by the control, not by
inspection.

**Deliberately still unexpressed:** `quantifier`, `tense`, `aspect`. No
producer sets them anywhere on the serving path, so threading them now would be
machinery with no caller. The clause owner already handles all three the moment
a producer exists.

Phase 5's *diversity* work (items 1–3 above) remains open and is now correctly
scoped by §6's RESULT: the frontier is **construction-inventory overlap**.

**RESULT (second unit) — the inventories measured against each other.**
New lane `evals/construction_inventory` (contract + 14 pins, 13 mutations
observed red). It sweeps the writer's whole parameter space — every
`RhetoricalMove` × `IntentTag` × predicate × quantifier × tense × aspect, both
public entry points, 32292 cells — quotients it by the reader's own function-word
skeleton, and comprehends each construction under three vocabularies.

| | |
|---|---|
| writer constructions | **1739** |
| reader constructions | **19** (mint-site AST-guarded) |
| **overlap, faithful** | **6** |
| reader accepts but mis-reads | **22** |
| reader refuses | 1711 |
| vocabulary-dependent | **0** |

The overlap is the same six from both sides — `X is a Y`, `the X is a Y`, and
the four categoricals — and it is **entirely set-theoretic**. The writer cannot
express one ordering, propositional or interrogative construction; the reader
has no template for the bare transitive clause that is the writer's whole
default output. Two of the reader's constructions need a `?`, which no writer
template contains, so they are unreachable **by shape** — corpus work cannot
close that gap, only a template can.

Three findings change what item 1 should be:

1. **Growing the inventory is not the first move — the reader fabricates.** On
   22 constructions it neither reads nor refuses: it invents. `every dog is a
   mammal` → `member(every_dog, mammal)`; `all dogs are defined as mammals` →
   `subset(dog, defined_as_mammal)`; `furthermore, all dogs are mammals` →
   `asserted(furthermore)`. One root cause: `_RESERVED` does not contain the
   function words the writer emits, and `_parse_propositional` accepts any
   single token as a fact. **The first and third are ordinary user English.**

2. **It reaches served output.** `chat/deduction_surface.py` recites
   `Given: furthermore; p implies q; p.` — a premise the user never stated —
   and `chat/runtime.py` *realizes* declarative turns into the held self, so a
   fabricated atom is vault-writable. Widening the inventory before closing this
   widens the fabrication surface with it.

3. **ADR-0265's defect class survives inside ADR-0265's own designated owner of
   clause grammar.** The four aspect arms of `_inflect_predicate` bind `negated`
   to a wildcard and never read it, so `dog has been defined as mammal` is
   emitted for both the assertion and the denial — 10530 of 16146 parameter
   points. Not reachable today (no producer sets `aspect`), so a loaded gun, not
   a casualty. It survived because ADR-0265's invariant is *structural* — does
   `negated` reach the call? — and cannot see an arm that receives the flag and
   ignores it. **A behavioural sweep catches what a threading invariant cannot.**

**Item 1 is therefore re-ordered: close the fabrications first, then widen.**
Both fixes are small and both are already written as mutations that turn the
defect pins red (`every`/`each` into `_RESERVED`; discourse connectives stripped
in `_split_clauses`). But they change what CORE *comprehends* from user input,
which is a serving change on the truth path — **authorization-gated, and an ADR
before any code**, on the ADR-0261 §5.1 precedent that a reader must refuse
rather than drop or invent.

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
- **`read_rate` stays near zero after unification** ⇒ the barrier is **§1.8**:
  `MeaningGraph` and `PropositionGraph` are genuinely different models, and no
  amount of table-sharing bridges them. The next arc is then a **graph-model**
  decision, which is large, touches the decision layer, and **must go to an ADR
  before any code**. It is explicitly *not* an extension of this plan.

Either way we will know which, and why, from a measured quantity — which is the
thing the previous arc could not do until after it had built the machinery.

**One reading of the evidence is worth pre-committing to now:** §1.6's uniform
`no_template_match` across all 280, combined with §1.8's type mismatch, makes
the second fork more likely than the first. If that is where we land, Phases 1–3
are still exactly the right work — they are what makes the graph-model question
answerable instead of speculative — but the arc should be expected to *end* at
the ADR rather than at fluid prose.

---

### RESULT — measured after Phase 4. **Neither fork. The pre-commitment above was wrong.**

`g_read_rate` did not stay at zero, and it did not rise materially either. It
went to **1 of 293** (`0.003413`) — the first non-zero in the arc — and the one
case tells you more than the rate does.

The unblocked case is `gram_C14_p01`. What was blocking it: the writer emitted
`all molecules are defined as compound`, a predicate nominal that does not agree
with its subject. The reader **accepts** `...as compounds` and **refuses**
`...as compound`. So the blocker was a one-line *writer* defect — not §1.8.

The other 292 decompose, and not one of them is a model mismatch either:

| refusal reason | n | whose problem |
|---|---|---|
| `no_template_match` | 289 | reader has no SUBJ-VERB-OBJ template at all |
| `unknown_morphology` | 2 | prepositional objects (`reserved_word_in_np`) |
| `unsupported_negation` | 1 | reader has no negated-categorical template |
| read | 1 | — |

Every one is the reader declining a **construction it has no template for**, not
a projection disagreeing about a graph it successfully parsed. And where a
construction *is* in both inventories the round trip closes exactly —
`s_surface_match_rate == s_renderable_rate` — while the reader independently
reads `all dogs are mammals`, `all wolves are canines`, and
`all molecules are defined as compounds`.

**So the barrier is the overlap of the two construction inventories, which is
currently one construction wide.** That is Phase 5's item 1 — grow the
inventory until `read_rate` clears a ratcheted floor — and it is tractable work,
not an ADR-scale model decision.

**Why the pre-commitment was wrong, kept here rather than quietly edited out:**
§1.6 read "uniform `no_template_match` across all 280" as evidence *for* the
type mismatch. It is not evidence for it. `no_template_match` is the reader
saying it has no template — a coverage fact — and §1.8's type mismatch was
inferred from it rather than measured. The corpus was 289/293 bare transitives,
a construction the reader has never claimed to read, so the measurement was
mostly reporting the corpus's composition. The one construction the corpus *did*
share with the reader (Phase 3's C14) was blocked by a writer bug, and until
that was fixed there was no case in the whole corpus capable of testing the
graph-model question at all.

**Consequence for Phase 5.** Its scope is now decidable. The inventory question
is the arc's live frontier, and it should be sized by measuring the reader's
construction set against the writer's rather than by growing corpora blindly.
The graph-model ADR is **not** cancelled — §1.8's type mismatch is still real —
but nothing measured here obliges it, and it should not be opened until a case
exists that fails for that reason and no other.

#### CORRECTION to the block above, from the Phase 5 measurement it asked for

Two claims made here are wrong, and the metric that disproves both was already
on the page when they were written.

**"the reader independently reads `all molecules are defined as compounds`" —
no, it mis-reads it.** `g_read_rate` is `1/293` but **`g_args_rate` is `0.0`**.
The reader comprehends that surface as `subset(molecule, defined_as_compound)`:
it chunked the writer's verb phrase into a class name. It accepted, it did not
comprehend. The contract for this lane separates `read` from `args` for exactly
this reason and the separation did its job; the RESULT above simply put its
weight on the wrong one of the two.

**"one construction wide" — wrong in both directions.** On this corpus the
*faithful* overlap is **zero**, because the one case that reads is the mis-read
above. Measured over the writer's whole output space instead of a 293-case
corpus, the true overlap is **six** — the corpus never exercised five of them.
A corpus cannot report the size of an inventory. Only the inventory can, which
is what §Phase 5's RESULT now does.

The generalisable lesson, and the reason this is kept rather than edited away:
**acceptance is not comprehension.** A reader scored on whether it returned a
graph, rather than on whether the graph is the one it was given, is rewarded for
guessing — a `wrong=0` hazard wearing a green metric. `g_read_rate` should never
again be quoted without `g_args_rate` beside it.

---

## 7. Verification protocol

Per `AGENTS.md`, unchanged from prior arcs:

- Every phase, in-worktree on canonical CPython 3.12.13 with `uv sync --locked`,
  before push: `uv run core test --suite smoke -q` then `--suite deductive -q`.
  Baselines: **smoke 621 / deductive 349**.
- Every new gate must **fail under mutation**. A pin that cannot fail is
  worthless — this arc exists because three such pins were found (§1.5, the Rust
  parity lane, and the fluency suite's blind spot).
- Phase 2A additionally requires **byte-identical** 11/11 lane SHA pins.
  Never `scripts/verify_lane_shas.py --update`; surgical single-line edits only.
- One PR per phase, branch + worktree each, Forgejo compare URL,
  `[Verification]:` line. No merge automation — PRs sit until authorized.
- Phase 4 additionally requires explicit serving-change authorization.

## 8. Standing traps carried into this arc

- **`then` / `therefore` are taught `philosophy_theology` lemmas AND the argument
  reader's control words.** The vocabulary boundary is never screened against the
  reader's grammar. A unified grammar makes this screenable for the first time —
  and makes forgetting to screen it a single-point failure. Add the screen in
  Phase 2A.
- Corpus-mutating tests must never write committed files: the `full` suite
  injects `-n auto`, so writes race.
- Never "fix" a hash drift or a ledger inventory to make a test pass.
- `PYO3_PYTHON=/opt/homebrew/bin/python3.12` is required for `core-rs` builds.
