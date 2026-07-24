# Band v6-EX — existential witnesses, and a wrong-answer path found on the way

**Date:** 2026-07-24 · **ADR:** ADR-0261 · **Arc:** deduction-serve /
generalization Phase 1.2 (Tier O)

## What shipped

`some` is decided. The band cascade now reads the whole square of opposition:
"All mammals are vertebrates. Some whales are mammals. Therefore some whales
are vertebrates." comes back **entailed**, and "All unicorns are horned.
Therefore some unicorns are horned." comes back **unsettled** — with the
reason disclosed, not silently assumed.

Four new bands (`en_exist_negative` / `_chain` / `_universal` / `_witness`)
earned SERVE at 720 × wrong=0 on the first arena seal (25-band ledger). The
hand-authored `v2_exist` split passed 32/32 on its first full run; the whole
deduction-serve lane is 166/166 wrong=0 across six splits.

## The mechanism, and the one place it could have been unsound

An existential premise is easy: mint a witness nobody else names and assert
the conjunction about it. An existential *conclusion* is where the design
decision lives, because asking "is ∃x(P(x) ∧ Q(x)) refuted?" means asking
whether ∀x ¬(P(x) ∧ Q(x)) is *derivable* — and a propositional lowering over
the individuals the argument happens to mention cannot tell "derivable" from
"true of everything I bothered to name".

Concretely, the obvious lowering gets this wrong:

> Rex is a wolf. Rex is not tame. Therefore some wolves are tame.

Lower `some wolves are tame` as a disjunction over the named individuals and
the only disjunct is Rex, who is not tame — so the disjunction is refuted, and
the system announces that *no wolf anywhere is tame*. From one wolf. That is a
wrong answer of exactly the kind this arc exists to prevent, and it would have
been invisible: sound-looking machinery, confidently wrong.

The fix is an old one — an eigenvariable. Every existential conclusion mints
one **arbitrary element**: a domain member no premise mentions, at which every
universal is still instantiated. Because it is arbitrary, anything the
premises force about it they force about everything, so the refutation
direction derives a genuine universal instead of assuming domain closure. And
because domains are non-empty, including it in the entailment direction stays
sound too. One extra domain element buys both directions.

With it, the Rex argument is **unknown**, which is the truth. The test that
pins this is named `test_arbitrary_element_keeps_the_domain_open`.

## No existential import — a reading choice, disclosed

"All C are P. Therefore some C are P." is UNKNOWN here. A universal is
vacuously true over an empty class, so it cannot by itself produce a member.
That is the modern first-order reading; the traditional square (Darapti,
Felapton, Bamalip) assumes otherwise. Both readings are defensible — but only
one of them declines to claim something exists that no premise asserted, and
that is the one this engine takes. The UNKNOWN surface says so in words
("reading … 'some' as claiming a member exists (so 'all' does not)"), because
a user who expects the traditional square would otherwise read the answer as a
bug. A user who wants the classical inference can state the existential
premise; the band will use it.

## The finding: a licensed band with an unmeasured wrong-answer path

Authoring the lane turned up something that was not part of the assignment.
Two arguments came back **"That doesn't follow"** when they plainly do:

> Aristotle is a philosopher. All philosophers are scholars. Therefore some
> scholars are philosophers.

> Every mineral is a solid. Some quartzes are minerals. Therefore some
> quartzes are solids.

Both were being answered by Band v1b, the categorical band, which holds an
earned SERVE license. Its projector (`to_syllogism`) built its premise list by
*filtering* the meaning graph down to the categorical relations — quietly
dropping anything else and answering from the remainder. In the first
argument the dropped relation was the singular fact `member(aristotle,
philosopher)`: the argument's only witness. In the second it was a `member`
relation produced by a separate reader gap (the shared reader parses "every
mineral" as an individual named `every_mineral`). Either way, the band decided
a strictly weaker argument than the user wrote, and served the answer as if it
had decided theirs.

Three things are worth keeping from this:

1. **Refuse, don't drop.** The propositional sibling `to_deductive_logic` has
   always returned `None` the moment it meets a relation it cannot express.
   `to_syllogism` now does the same. That is the whole fix — six lines — and
   the two arguments above now fall through to v6-EX, which decides both
   correctly.
2. **An earned license covers the corpus, not the input space.** The
   CATEGORICAL band passed 720/720 because every one of its templates is a
   purely categorical two-premise syllogism in the synthetic lexicon — a
   family in which nothing is ever dropped. The band's license was honest
   about what it measured and silent about what it didn't. When a band's
   practice corpus is narrower than its reachable inputs, the gap is exactly
   where a wrong answer lives.
3. **The cheapest way to find it was to build the next band.** Nothing in the
   existing suite exercised these shapes; they surfaced because authoring
   `v2_exist` meant asking, case by case, "which band actually answers this,
   and is that answer right?" The band-boundary audit is not bureaucracy — it
   is the test.

The categorical band re-earned SERVE at 720/720 after the change, so no
coverage was lost. Both arguments are pinned as regression cases
(`ds-ex-0008`, `ds-ex-0011`), plus a projector unit test and an e2e test.

## Wrinkles worth surfacing

- **The shared reader still misreads "every mineral" as an individual.** Post
  fix this is harmless (v1b refuses, v6-EX reads the sentence correctly), so
  it is recorded rather than patched — repairing `comprehend`'s template set
  is its own unit with its own lane. But it is a live example of the same
  class of defect: a reader that produces *something* for input it does not
  actually understand.
- **v1b still owns categorical some-syllogisms in its lexicon.** Where every
  term is known and the argument is purely categorical, v1b answers first, in
  `valid`/`invalid` vocabulary. That is correct precedence, but it means the
  `v2_exist` corpus had to be authored deliberately off that path (three
  practice templates were rewritten for the same reason). Documented in
  `contract.md`; the two vocabularies coexisting for structurally similar
  arguments is a seam a future arc may want to close.
- **The atom cap now binds on the query.** An existential conclusion mints up
  to two atoms per domain element, so a wide argument can hit `MAX_ATOMS`
  where an equivalent v5-VP argument would not. It refuses rather than
  truncating — a dropped disjunct is precisely how a false REFUTED would
  reappear.
- **Only `some`.** `most`, `few`, `several`, "at least two", and "there is a
  C that…" all refuse. Proportional quantifiers are not a lowering problem,
  they are a counting problem, and this substrate does not count.

## Where this leaves Phase 2

The reading generalization the plan called for is done: subject matter states
its rules as verb sentences (v5-VP) about classes quantified with all / no /
some (v3-MEM, v6-EX), and the cascade now reads all of it under one earned
license discipline. Physics and biology serve lanes are next, and they need no
further reading work before the curriculum-entailment contract can be built on
top.
