# Construction-Inventory Eval Lane — Contract

**Lane:** `construction_inventory`
**Version:** v1
**Created:** 2026-07-27
**Plan:** `docs/plans/grammar-unification-2026-07-26.md` (Phase 5, item 1)

## What this lane measures

How many **constructions** the reader and the writer share — the quantity §6's
RESULT identified as the arc's frontier, and asked to be measured directly
"rather than by growing corpora blindly."

## Why `grammar_roundtrip` could not answer this

`grammar_roundtrip` measures a **corpus**. Its G-direction reports
`g_read_rate = 1/293`, and §6 read that one case as the shared construction,
concluding the overlap was "one construction wide."

Both halves of that were wrong, and the lane's own metrics already said so:

- **`g_args_rate` is `0.0`.** The one surface that "reads" —
  `all molecules are defined as compounds` — is comprehended as
  `subset(molecule, defined_as_compound)`. The reader chunked the writer's verb
  phrase into a class name. It is a **mis-read**, so on that corpus the faithful
  overlap is **zero**, not one.
- **The true overlap is six**, and the corpus never exercised five of them.
  293 cases cannot report the size of an inventory; only the inventory can.

The lesson generalises: *acceptance is not comprehension*. A lane that counts
`read` without counting `args` will reward a reader for guessing.

## The construction quotient

A construction is defined by the reader's own dispatch. `reader.py` reads
"STRUCTURE symbolically ... via templates keyed on FUNCTION WORDS + ORDER", so
replacing every non-function word with `*` yields a form that is, by the
reader's design, indistinguishable to its parser. The function-word set is read
off `reader._RESERVED` — the lane cannot pick a quotient that flatters a number,
and it widens automatically when the reader learns a word.

**Known limit:** `_chunk_class` refuses on unrecognized plurals, which depends on
the token rather than the shape. So the skeleton determines the verdict *up to
morphology*. The lane sweeps three count-noun vocabularies (regular, `-f/-ves`,
suppletive) and counts a construction as shared only when all three agree;
disagreement is reported as `w2r_filler_dependent`, currently **0**.

## The two directions

| direction | question | how |
|---|---|---|
| **W → R** | of everything the writer can emit, what does the reader read *truly*? | sweep the writer's whole parameter space, quotient to constructions, comprehend each |
| **R → W** | of everything the reader can read, what can the writer emit? | instantiate each reader construction, quotient, test membership in the writer's construction set |

The writer's space is enumerated from live source — `RhetoricalMove`,
`IntentTag`, `PREDICATE_DISPLAY`, `PREDICATIVE_NOMINAL`, `PLURAL_QUANTIFIERS`,
and the tense/aspect literals in `_inflect_predicate`'s match arms (AST-pinned).
Nothing is a hand-copied list of "what the writer can say."

Both writer entry points are swept: `render_semantic` (the **serving** writer,
called by `core/cognition/pipeline.py`) and `render_step` (the clause owner it
delegates to, also reached by the eval-only `realize_target`).

## Acceptance is split three ways

| bucket | meaning |
|---|---|
| `faithful` | the reader recovered the writer's proposition and minted **nothing else** — the only bucket that counts as overlap |
| `fabricating` | accepted, but minted an argument the writer never wrote, or manufactured a query from a declarative |
| `refused` | the honest outcome: no template, and the reader says so |

## Metrics

| metric | definition |
|---|---|
| `writer_constructions` | distinct constructions the writer can emit |
| `overlap_constructions` | shared **and faithful** under every count-noun filler — the Phase 5 number |
| `w2r_fabricating` | writer constructions the reader mis-reads — a `wrong=0` hazard, ratcheted **down** |
| `w2r_filler_dependent` | shared under some vocabularies but not others (morphology gaps) |
| `reader_constructions` | the reader's inventory, guarded against rot by mint-site AST count |
| `r2w_expressible` | reader constructions the writer can emit |
| `negation_collapsed_points` | writer parameter points whose denial is byte-identical to its assertion — ADR-0265 sentinel, ratcheted **down** |

## v1 baseline — measured on `main` @ `8927c563`

```
writer_cells                  32292
writer_constructions           1739
w2r_faithful                      6
w2r_fabricating                  22
w2r_refused                    1711
w2r_filler_dependent              0
w2r_faithful_rate            0.00345
cells_faithful                   12
cells_fabricating               150

reader_constructions             19
r2w_expressible                   6
r2w_rate                     0.315789
reader_interrogative_constructions 2

overlap_constructions             6     <-- the Phase 5 number
negation_collapsed_points     10530     <-- defect, see below
```

## What this lane found

**1. The overlap is six, and all six are set-theoretic.**
`X is a Y`, `the X is a Y`, `all Xs are Ys`, `no Xs are Ys`, `some Xs are Ys`,
`some Xs are not Ys`. The writer cannot express a single ordering, propositional
or interrogative construction; the reader has no template for the bare
transitive clause (`X supports Y`) that is the writer's entire default output.
The two halves meet only on set membership and subsumption.

**2. Three of the reader's constructions are unreachable by SHAPE, not by
vocabulary.** `member_query` and `subset_query` require `?`; no writer template
contains one. Corpus work cannot close that gap — a template can.

**3. The reader fabricates on 22 constructions, and it is on a serving path.**
Three distinct leaks, one root cause: `_RESERVED` does not contain the
function-word vocabulary the writer actually emits.

| leak | example | minted |
|---|---|---|
| determiner glued to entity | `every dog is a mammal` | `member(every_dog, mammal)` |
| verb phrase chunked as class | `all dogs are defined as mammals` | `subset(dog, defined_as_mammal)` |
| connective promoted to proposition | `furthermore, all dogs are mammals` | `asserted(furthermore)` |

The first and third are **ordinary user English**, not writer artefacts. And the
third reaches served output:

```
"if p then q. p. therefore q."               -> Given: p implies q; p. ...
"furthermore, if p then q. p. therefore q."  -> Given: furthermore; p implies q; p. ...
```

CORE recites a premise the user never stated. `chat/runtime.py` additionally
*realizes* declarative turns into the held self, so `asserted(furthermore)` is
writable to the vault.

**4. ADR-0265's defect class survives in the module ADR-0265 named as the single
owner of clause grammar.** The four aspect arms of `_inflect_predicate` bind
`negated` to a wildcard and never read it:

```
aspect=perfective    affirm: dog has been defined as mammal
                     denied: dog has been defined as mammal   <-- identical
```

10530 of 16146 writer parameter points collapse this way. It is **not reachable
today** — no producer sets `aspect` on the serving path — so it is a loaded gun,
not a casualty. It survived because ADR-0265's invariant is *structural* (is
`negated` threaded to the call?) and cannot see an arm that receives the flag and
ignores it. This lane's sentinel is behavioural, and does.

## What this lane does NOT prove

The overlap is a count of **shapes**, not a quality judgement. Six shared
constructions that are all set-theoretic is a narrow grammar, and nothing here
says the shared six are *well* written — `render_step` could emit stilted
English inside every one of them and this lane would be satisfied.

It also says nothing about `MeaningGraph`/`PropositionGraph` type compatibility
(§1.8). That question is still open and still un-forced: no case measured here
fails for that reason and no other.

## Mutation guarantees

Every pin in `tests/test_construction_inventory.py` has been run against a
mutation of its own subject and observed RED — 12 of 12, recorded in the Phase 5
RESULT block of the plan. The two fabrication fixes (`every`/`each` into
`_RESERVED`; discourse connectives stripped in `_split_clauses`) are among the
mutations, so the defect pins are known to move when the defect is fixed.
