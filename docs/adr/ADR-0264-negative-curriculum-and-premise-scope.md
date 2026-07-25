# ADR-0264 — Negative curriculum, premise scope, and what a curriculum band can earn

- **Status:** Proposed — awaiting Joshua Shay's ratification. This ADR changes no
  flag and no default; it fixes a schema shape and a compilation rule, and it
  records a blocking finding about ADR-0262 §5.1.
- **Date:** 2026-07-25
- **Arc:** curriculum-license-loop Phase A
  (`docs/plans/curriculum-license-loop-2026-07-25.md` §4)
- **Governs:** the `polarity` field of `teaching/domain_chains/*.jsonl`,
  `teaching/curriculum_premises.py` (`CurriculumChain.sentence`,
  `compile_premises`, `load_curriculum` admission),
  `chat/curriculum_surface.py::decide_curriculum_question`,
  `evals/curriculum_serve/oracle.py`, and
  `teaching/ratification.py::validate_admissible`.
- **Amends:** ADR-0262 §5.1 (its conclusion, not its decision) and §6's
  premise-set-scaling scope-out. Builds on ADR-0261 §5.1 (refuse, don't drop)
  and ADR-0260 (the verb-predicate band that decides these arguments).

## 1. Context

The plan of record asked Phase A one question: how does an explicitly-taught
negative coexist with the open-world reading, where an absent edge must stay
UNKNOWN and never become "no"? Answering it required reading the compilation
path end to end, and that read produced three facts that were not known when the
plan was written. Two of them change what the arc must do next.

Everything below was verified by running the real path in-tree, not by reading
docstrings. Reproduction is in §6.

**Fact 1 — the row field `polarity` is silently ignored, and a negative row
serves a confident wrong "Yes."** `load_curriculum` reads
`review_status`, `domain`, `subject`, `object`, the two `*_pack_id` fields and
`connective`. Nothing else. `CurriculumChain.sentence` is unconditionally
`f"{subject} {connective} {obj}"`. So a row added today with
`"polarity": "negative"` compiles to the *affirmative* sentence, and the question
it was authored to refute comes back `entailed`:

```
+1 negative row (acceleration requires charge, polarity=negative)
  Does acceleration require charge?  ->  verdict='entailed'
```

The user-visible surface for that verdict is *"Yes — my physics curriculum
teaches that acceleration requires charge, directly, among the 10 modal
relations it states."* The curriculum said the opposite.

This is not caught by any gate. `evals/curriculum_serve/oracle.py` is
independent in code but reads the same rows, and it ignores `polarity` for the
same reason. Gold and the serving path agree on the wrong answer, so the lane
stays green and `wrong=0` holds. This is the exact failure class Phase A exists
to prevent, and it is now demonstrated rather than hypothesised.

**Fact 2 — `operator_family` is not the band axis; the connective is.** The plan
of record and the division-of-work both state that bands key on
`(domain, operator_family)` and warn against a `modal_negative` family. The
warning points at a real hazard but names the wrong field. `load_curriculum`
never reads the row's `operator_family`; `CONNECTIVE_FAMILY[connective]` is the
sole family authority, deliberately and as documented in
`teaching/curriculum_premises.py`. Two rows in the corpus already declare a
family their connective contradicts (`physics-causal-008` and one
`systems_software` row, both `requires`/`causal`) and are correctly read as
modal. `physics · modal` therefore holds **9** chains, not 8 — which is where
the plan's `n=9` came from.

The hazard restated correctly: the connective fixes both the band **and the
propositional atom**. A negative expressed as a *new connective* (`precludes`,
`does_not_require`) mints a different atom from the positive question it was
meant to refute, so the ROBDD returns UNKNOWN instead of REFUTED — silently, at
every such row.

**Fact 3 — the premise cap makes ADR-0262 §5.1's own prescribed remedy destroy
the capability it was meant to build.** `compile_premises` emits *every* chain in
the family as a premise sentence, and `read_verb_argument` refuses beyond
`MAX_PREMISE_SENTENCES = 16`. Measured end to end:

```
physics modal chains = 9   (cap = 16)
 +7 rows -> 16 premises: taught positive = 'entailed'   negative pair = 'entailed'
 +8 rows -> 17 premises: taught positive = 'declined'   negative pair = 'declined'
                          reason='compiled_premises_unreadable'
```

At row 17 the band stops answering *anything* — including
`conservation requires symmetry`, which works today. ADR-0262 §5.1 prescribes
authoring **≈219 relations per subject × family** to reach a balanced band.
ADR-0262 §6 scopes premise-set scaling out, on the reasoning that "no current
family exceeds 9" and the fix can wait until one does. Those two sections are in
contradiction: §5.1's remedy triggers §6's deferred fix at row 17 and then
collapses the band for the remaining 202 rows. The scope-out silently blocks the
plan it shares an ADR with.

## 2. Decision

**R1 — Polarity is a row-level `polarity` field.** Values `"affirmative"` and
`"negative"`; **absent means affirmative**, so all 88 existing rows are
unchanged and no migration is required.

It is *not* an `intent` value. `intent` already carries an orthogonal
teaching-intent axis with five values in use
(`cause`/`verification`/`procedure`/`comparison`/`correction`); overloading it
would conflate two independent axes in one column and make each unreadable from
the other. It is *not* a new `operator_family` value and *not* a new
`connective` — see R3.

**R2 — A negative row compiles to the sentential-not form.**

```
affirmative:  f"{subject} {connective} {obj}"
negative:     f"it is not the case that {subject} {connective} {obj}"
```

The `("it","is","not","the","case","that")` prefix is an existing shape in
`generate/proof_chain/english.py` and `member.py`, already read by the verb
band. It is chosen over `"{subject} does not {connective} {obj}"` for one
reason: the `does not` shape wants the base form of the verb (`require`, not
`requires`), which would require a de-inflection table — a new inverse of
`_VERB_IRREGULAR_3SG` — to be invented and maintained. The band happens to read
`"does not requires"` too, but that is ungrammatical English written into a
reasoning trace, and depending on it would be depending on an accident.

Verified: all three shapes reach `REFUTED` with correct atom identity
(premises `('a0','a1','~(a2)')` against query `'a2'`).

**R3 — A negative row MUST reuse the affirmative connective.** Atom identity is
`(subject, normalized-verb, object)`. `REFUTED` is `(⋀P) → ¬Q` being a tautology,
which requires the negated premise and the query to be *the same atom*. A new
connective mints a new atom and yields UNKNOWN. `validate_admissible` must reject
a negative row whose connective is absent from `CONNECTIVE_FAMILY`.

**R4 — Contradiction is rejected at ratification, not discovered at serve
time.** A negative row for a `(domain, subject, connective, object)` that already
holds an affirmative row — or the reverse — is inadmissible.
`teaching/ratification.py::validate_admissible` rejects it. Without this guard
the compiled premise set is inconsistent, `evaluate_entailment_with_trace`
returns `REFUSED`/`INCONSISTENT_PREMISES`, and the surface says *"The curriculum
I have for that is inconsistent"* — an honest answer to a problem that should
never have been ratified. Fail at authoring, where a human is present.

**R5 — Premise compilation is query-scoped, and the scope must be a superset of
the query-atom rows.** The soundness condition is exact:

> For a corpus of atomic rows, every compiled premise mints one independent
> propositional atom. A scope that contains every row whose atom is the query's
> atom decides the query identically to the full family, because no other atom
> appears in the query formula and independent atoms cannot constrain it.

Two consequences worth stating separately, because ADR-0262 §6 conflates them:

- **Sound** (narrowing cannot invent an entailment) is the weaker property §6
  argues for. It is true but insufficient — a narrowing can be sound while
  silently *losing* true entailments, which is coverage loss in exactly the
  class of case the license counts, and is the shape ADR-0261 §5.1 was written
  about.
- **Verdict-identical** is the property R5 requires, and it holds only for a
  scope that is a superset of the query-atom rows.

The default scope is **term incidence**: rows whose subject or object is one of
the query's two terms. This is bounded by vocabulary degree rather than corpus
size, keeps real neighbouring premises in the argument, and is a superset of the
query-atom rows. If term incidence would still exceed the band's cap, narrow to
the query-atom rows — which is verdict-identical, never an arbitrary truncation.
The reader is never asked to refuse for size.

**R6 — An empty scope is UNKNOWN; only an empty family is a refusal.** Today
`compile_premises` returning nothing means "this family has no ratified chains"
and correctly refuses `empty_curriculum`. Under R5 it will much more often mean
"no ratified chain mentions this query", which is UNKNOWN — the open-world
reading. These two must be distinguished at the call site, or 8,463 of the 8,520
questions measured in §6 flip from `unknown` to `declined`.

**R7 — `premise_count` continues to report family size.** It is user-visible
(*"It states 9 modal relations, and none of them decides this one"*). Under R5
the compiled scope is usually 0 or 1, and reporting that number would understate
the curriculum to the user. Report family size in the surface; carry the
compiled-scope size as a separate field for the lane and the audit ledger, and
disclose the narrowing there. This also keeps ADR-0262 §7's existing assertions
stable.

**R8 — The oracle learns polarity independently.** `evals/curriculum_serve/oracle.py`
reads `polarity` with its own default rule and its own restated vocabulary, sharing
no helper with `teaching/curriculum_premises.py`. Its code-level independence is
the entire evidentiary value of the lane; a shared polarity helper would make the
two agree by construction, which is what Fact 1 shows is indistinguishable from
being right. Additionally: **negative edges are excluded from the BFS adjacency**.
A negative edge is not a traversable path, and including it would inflate the
reachability depths the lane asserts against.

**R9 — Earning requires an outcome-mix floor, and a band that cannot reach the
threshold must say so before anyone authors for it.** ADR-0262 §5.1 already
states the acceptability criterion — "a band whose entailed class is 1% of its
volume is passed by a pipeline that never entails anything" — but leaves it as
prose. It becomes a measured precondition: the practice producer reports, per
band, the maximum honest committed volume and the maximum entailed share
achievable from the ratified corpus, and a band whose ceiling is below the
licensing threshold is reported **structurally unable to earn SERVE** rather than
left for authoring effort to discover. Phase B specifies the bound; this ADR
fixes the requirement that the bound exist.

## 3. Why this is sound

R5 is the only rule that changes an existing answer, so it is the only one that
needs evidence rather than argument. Both candidate scopes were compared against
full-family compilation over every routable question in all four served domains
(philosophy_theology sampled to its first 40 lemmas to stay tractable):

```
questions compared           : 8520
term-incidence mismatches    : 0
query-atom mismatches        : 0     (over non-empty scopes)
query-atom EMPTY scopes      : 8463  <- R6 governs these
max premises, full-family    : 9
max premises, term-incidence : 8
```

Zero verdict changes. The physics lane's `entailed 14 / unknown 12 / declined 6`
gold is preserved exactly: taught edges keep a non-empty query-atom scope and
stay `entailed`; untaught pairs get an empty scope and stay `unknown` under R6;
pre-band refusals are untouched.

R1–R4 and R8 add a verdict (`REFUTED`) that the decision path already maps and
already has a surface template for. They do not change any existing answer,
because absent `polarity` means affirmative.

## 4. Findings

### 4.1 No curriculum band can earn a SERVE license under the current architecture

This follows from two facts already in the repository, and it does not depend on
any rule in §2.

- A taught edge makes exactly one question come back `entailed`, so the entailed
  cases available to a band equal the number of ratified chains in its family.
- The premise cap holds a family to **≤16 chains** — beyond that the band
  answers nothing at all (Fact 3).

So a band has at most 16 entailed cases available, against a licensing threshold
of **n ≥ 657 committed**. Reaching 657 therefore requires a ledger that is at
least `1 − 16/657` = **97.6% non-entailed**. ADR-0262 §5.1 already rules that
unacceptable. Its ⅓-entailed target caps committed volume at `3 × 16 = 48`, and
*any* mix floor above 2.44% blocks a license outright.

The conclusion inverts §5.1's: the binding constraint is **not** curriculum
volume, and not "a curriculum-authoring and ratification task — Shay's call, not
an engineering one." Authoring is blocked by an engineering prerequisite. R5 is
that prerequisite: query-scoped compilation removes the 16-chain ceiling, at
which point §5.1's ≈219-relation prescription becomes achievable and its
arithmetic becomes correct again.

### 4.2 Eight of eleven bands cannot reach the threshold even with unlimited authoring

Volume is bounded by *taught vocabulary*, not by corpus size, because a question
must have both terms in exactly one served subject's vocabulary to route at all
(`ambiguous_reading` otherwise). Measured routable question spaces:

| domain | \|V\| | exclusive lemmas | routable ordered pairs |
|---|---|---|---|
| physics | 16 | 16 | 240 |
| mathematics_logic | 16 | 15 | 210 |
| systems_software | 16 | 15 | 210 |
| philosophy_theology | 151 | 149 | 22,052 |

`max_honest_n = routable_pairs × |connectives(family)|`, one committed case per
distinct question:

| band | chains | max honest n | vs 657 |
|---|---|---|---|
| curriculum_physics_causal | 7 | 720 | reachable |
| **curriculum_physics_modal** | **9** | **480** | **impossible** |
| curriculum_mathematics_logic_modal | 4 | 420 | impossible |
| curriculum_mathematics_logic_contrast | 8 | 210 | impossible |
| curriculum_mathematics_logic_evidential | 8 | 210 | impossible |
| curriculum_mathematics_logic_sequence | 4 | 210 | impossible |
| curriculum_systems_software_causal | 7 | 630 | impossible |
| curriculum_systems_software_modal | 6 | 420 | impossible |
| curriculum_systems_software_sequence | 3 | 210 | impossible |
| curriculum_philosophy_theology_contrast | 8 | 22,052 | reachable |
| curriculum_philosophy_theology_modal | 8 | 44,104 | reachable |

**The plan of record's first content target is one of the impossible ones.**
`physics · modal` was chosen for having the most chains (9, "closest of eleven
bands"). Chain count is not the constraint; vocabulary is. Its ceiling is 480 —
below the threshold with every possible question counted, and that ceiling cannot
be raised by authoring chains, only by growing `en_physics_v1`.

`physics · causal` is nominally reachable at 720 but would need 657 of its 720
questions — 91% of the entire space — leaving no held-out room at all.

**The defensible first target is `philosophy_theology · modal`:** 44,104 honest
ceiling (67× the threshold), 8 chains already ratified, and the same 8-chain
starting point as the physics band. This reverses a decision in the plan of
record, on a measurement.

### 4.3 The two unbuilt segments are still unbuilt, and are still not the blocker

Phases C and D stand as written — `evals/curriculum_serve/practice/` and the
`reseal` verb do not exist, and `chat/data/curriculum_serve_ledger.json` has no
writer. That finding survives. What changes is its priority: building the
producer before R5 lands would produce a correct instrument reporting that every
band is at its ceiling.

## 5. What this ADR does not decide

- **The bound in R9.** The specific de-duplication tuple and mix floor are
  Phase B's deliverable. R9 fixes only that a bound must exist and be reported.
- **Raising `MAX_PREMISE_SENTENCES`.** Rejected as an approach, not deferred: it
  is a shared honesty cap that the 25 deduction bands also decide under, raising
  it would move hash-pinned lanes, and a 219-premise argument is not honest at
  any cap. R5 makes the cap irrelevant to curriculum instead.
- **Composition across curriculum edges.** Still scoped out per ADR-0262 §3.3.
  R8's exclusion of negative edges from BFS is a reachability-reporting rule, not
  a licence to chain.
- **Negated questions.** The grammar stays `Does <term> <relation> <term>?`,
  three tokens. Polarity lives in the curriculum, never in the question. "Does X
  not require Y?" is four tokens and refuses typed, as it does today.
- **Growing `en_physics_v1`.** §4.2 says physics bands need vocabulary, not
  chains. Whether to grow the pack is a separate ratified decision.
- **Any flag.** `curriculum_serving_enabled` stays False.

## 6. Verification

All four probes are in
`docs/research/curriculum-premise-scope-2026-07-25.md`, each runnable against a
clean tree; the corpus-mutating one restores the file and asserts byte-identity.

1. **Negation reaches REFUTED** — three shapes, atom identity checked.
2. **Cap collapse** — real negative rows appended to
   `physics_chains_v1.jsonl`; band answers at 16 premises, declines at 17,
   including the previously-working taught positive. Also demonstrates Fact 1:
   at +1 row the negative pair answers `entailed`.
3. **Scope equivalence** — 8,520 routable questions, 0 mismatches for both
   candidate scopes, 8,463 empty query-atom scopes.
4. **Band ceilings** — the §4.2 table, derived from `CONNECTIVE_FAMILY` and the
   loaded vocabularies rather than restated.

No production code changed in this ADR; §2's rules are implemented by Phase C
against Phase B's tests.

## 7. Consequences for the plan of record

1. **New phase, before content: implement R5–R7.** Nothing else in the arc can
   earn anything until the 16-chain ceiling is gone. Loud failure mode (the lane
   pins every physics verdict), so it is a Sonnet unit once the assertion set
   here is fixed — which it now is.
2. **Phase F retargets to `philosophy_theology · modal`** per §4.2, and its
   volume target is recomputed against that band's ceiling.
3. **Phase B additionally specifies R9's ceiling report**, so no future arc
   spends authoring effort on a structurally impossible band.
4. **ADR-0262 §5.1's conclusion is amended** by §4.1 — the constraint is
   engineering-then-content, not content alone. §5.1's *criterion* is upheld and
   promoted to a measured precondition.
