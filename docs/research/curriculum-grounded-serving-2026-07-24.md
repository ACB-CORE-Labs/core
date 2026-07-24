# Curriculum-grounded serving — the first exam answered from what was taught

**Date:** 2026-07-24 · **ADR:** ADR-0262 · **Arc:** generalization Phase 2 (Tier O)

## What shipped

"Does force cause acceleration?" is now answered — from the ratified physics
chain corpus and nothing else. "Does gravity cause acceleration?" is declined,
because *gravity* is not in any pack CORE has been taught. "Does force cause
motion?" comes back unsettled, even though the curriculum contains both links
in that chain, because nothing ratified says causation composes.

That third answer is the one worth staring at. It is the difference between a
system that decodes a curriculum and one that pattern-matches over it.

The lane: 32 hand-authored physics cases, wrong=0, five anti-recall probes, an
independent oracle re-deriving every gold, and three contract guards that fail
the LANE (not the case) if provenance, soundness, or anti-recall coverage
lapses. 20 unit tests. Zero subject-specific decision code: the composer routes
by vocabulary, compiles premises from ratified chains, and hands the result to
the same argument bands that decide "All philosophers teach. Socrates is a
philosopher."

## The design decision that carried the weight

The plan fixed the epistemology in §4 before any code existed, and that turned
out to matter more than any implementation choice. Three of its clauses did
real work:

- **Gold is a function of (curriculum, question).** No hidden premises in the
  case file. A case pins chain ids; the runner reconstructs premises from the
  corpus and fails loudly if a pinned chain is absent or unratified. A
  curriculum that moves under a case breaks the case instead of quietly
  changing its answer.
- **Untaught ⇒ UNKNOWN, never "no".** Open-world reading. Manufacturing a
  negative from silence is the same error as manufacturing a positive from it,
  and it is the more tempting one because it feels like rigor.
- **Anti-recall probes are mandatory.** The runner refuses to score a split
  that does not contain questions whose answers are true in the world and
  absent from the curriculum. Without them the lane cannot distinguish
  decoding from recall, so it must not ship.

## Where the independent oracle earned its keep

The oracle disagreed with the serving path exactly once during authoring:
"Does entropy cause energy?" The curriculum teaches *entropy reveals energy*.
The serving path said UNKNOWN — different relation, different atom. The oracle
said ENTAILED, because I had written its edge lookup to match on relation
*family* rather than the relation itself.

The oracle was wrong, and the serving path was right. That is the useful shape
of the result: an independent check is worth building even when — especially
when — you expect it to agree, because the thing it catches is the assumption
you did not notice you had made. Family scoping decides which premises are in
play; the connective decides what was actually said.

A second authoring error surfaced the same way: two lane cases claimed both
directions of `field requires charge` were taught. Only one is. The provenance
and soundness guards caught it before the case file was committed.

## The finding: Phase 2's blocker is curriculum volume, not machinery

Every `curriculum_*` band is unearned, so every answer is served hedged. That
is not a shortcut around the license — it is the license working, and the
reason is arithmetic.

A band earns SERVE at θ_SERVE=0.99 with n ≥ 657 committed cases and a genuine
outcome mix. The question space is large enough (physics: 240 distinct
questions per family; philosophy_theology: 22,650). The *entailed* space is
not: physics teaches 7 causal and 9 modal relations, so at most 16 questions in
the entire subject can come back ENTAILED. Repeating them to reach 657 inflates
n without adding information, and a band whose entailed class is 1% of its
volume is passed by a pipeline that never entails anything at all.

A balanced band needs roughly **219 distinct taught relations per subject ×
family**. Physics has 7 and 9 — a ~25× gap. No sampling scheme closes it. What
closes it is ratified curriculum content, which is an authoring and
ratification decision, not an engineering one.

So the honest state of Phase 2: the lifecycle is ported and provably correct on
real curriculum data; the earned-license half is blocked on how much has been
taught. That is a much better problem to have than the reverse, and it is the
one the plan's own doctrine (capability → practice → calibration → serve)
predicts you would hit here.

## Two corrections to the plan's ground truth

- **There is no biology domain-chain corpus.** The plan names physics and
  biology as Phase 2's subjects on the basis that "OOD lanes, seed packs, and
  domain chains already exist". For biology the first two are true; the third
  is not, and `evals/foundational_biology_ood`'s own contract says it measures
  fluency, not truth. The subjects with ratified chains AND mounted packs are
  physics, mathematics_logic, systems_software, and philosophy_theology. The
  composer serves all four; the second subject should come from that list, or
  biology's chains should be authored first.
- **`operator_family` and `connective` disagree in the corpora.** Two rows
  declare a family their connective does not imply. The serving path reads the
  connective, because that is the only thing an exam question carries — and if
  routing and compilation disagreed about a row's family, a taught edge could
  go missing from the premises compiled to decide it. That would be a wrong
  answer assembled from a correct curriculum, which is the exact failure mode
  ADR-0261 §5.1 found in the categorical band a day earlier.

## What is deliberately not built

Composition, negation, question shapes beyond `Does <term> <relation> <term>?`,
and premise-set scaling past the reader's 16-sentence honesty cap. Each is
scoped in ADR-0262 §6 with the condition that would unblock it. None of them
is a prerequisite for the next subject: adding one is a data operation now.
