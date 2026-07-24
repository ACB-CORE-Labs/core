# ADR-0262 — Curriculum-grounded serving: exams answered from what was taught

- **Status:** Proposed
- **Date:** 2026-07-24
- **Arc:** generalization Phase 2 (docs/plans/generalization-arc-2026-07-24.md §4)
- **Governs:** `teaching/curriculum_premises.py`, `chat/curriculum_surface.py`,
  `chat/curriculum_serve_license.py`, the `curriculum_<subject>_<family>` bands,
  the `evals/curriculum_serve` lane and its independent oracle, and the
  `curriculum_serving_enabled` flag.

## 1. Context

The band cascade (ADR-0256 → 0261) decides arguments whose premises are IN the
text. Exams are not shaped like that: the question supplies only the query, and
the premises are supposed to be what the student was taught. Until now CORE had
no path from "a ratified curriculum exists" to "a question is answered from
it" — the 16 domain seed packs and 5 domain-chain corpora were inert.

The generalization plan §4 fixes the epistemology for that path in advance, so
that implementing it cannot quietly become "answer from what the model knows".
This ADR implements §4.

## 2. Decision

Add a second serving composer, `chat/curriculum_surface.py`, behind the
default-off `curriculum_serving_enabled` flag:

1. **Closed question grammar** — `Does <term> <relation> <term>?`. One shape.
   Anything else refuses `question_shape_out_of_band` rather than guessing
   which token is the relation.
2. **Subject routing by vocabulary** — the question goes to the subject whose
   ratified pack vocabulary contains BOTH terms. No match is
   `untaught_vocabulary`; more than one is `ambiguous_reading`. The subject is
   never guessed.
3. **Premise compilation from the ratified curriculum only**
   (`teaching/curriculum_premises.py`). A chain is admitted iff
   `review_status == "reviewed"` AND both terms are resident in the packs the
   chain declares. Compilation is scoped to the question's relation family.
4. **The same decider** — compiled premises plus the question as a "Therefore"
   conclusion are handed to the verb-predicate band (ADR-0260), falling through
   to the existential band (ADR-0261), then the ROBDD engine. **No
   subject-specific decision code exists anywhere in this path.**
5. **Bands = (subject × relation family)**, e.g. `curriculum_physics_causal`,
   gated by the same earned-license machinery as deduction serving through a
   second ledger reader (`chat/curriculum_serve_license.py`).

The relation family comes from the CONNECTIVE, not from a chain row's declared
`operator_family`. A question carries a relation word and nothing else; a
family derived from anything the question cannot carry would let premise
compilation and question routing disagree, and a taught edge could then be
missing from the premises compiled to decide it — a wrong answer built out of a
correct curriculum. Two corpus rows currently declare a family their connective
does not imply; under this rule they are read as their connective says.

## 3. Why this is sound

1. **Gold is a function of (curriculum, question).** No case-local hidden text,
   no world knowledge. A lane case pins the chain ids it draws on and the
   runner FAILS the case if a pinned chain is absent or unratified — so a
   curriculum that changes under a case breaks loudly instead of quietly
   answering from what remains.
2. **Open-world reading.** A relation the curriculum does not state is
   UNKNOWN, never "no". Deciding otherwise would manufacture negative
   knowledge from silence, which is the same failure as manufacturing positive
   knowledge from silence.
3. **No composition.** The curriculum teaches `force causes acceleration` and
   `acceleration causes motion`; it does not teach that causation composes, so
   `force causes motion` is UNKNOWN. Transitivity of a causal or modal relation
   is a substantive claim about the world, not a logical truth, and nothing
   ratified asserts it. The independent oracle reports the shortest path length
   with its verdict precisely so the lane can assert that a reachable pair is
   still answered UNKNOWN — composition is provably not happening rather than
   merely absent.
4. **Face-value relations.** `entropy reveals energy` does not license
   `entropy causes energy`. Same family, different relation: the reader mints
   distinct atoms per verb group (ADR-0260), so a family-level near-miss cannot
   become an entailment.
5. **Independent gold.** `evals/curriculum_serve/oracle.py` shares no code with
   the serving path — its own JSONL loader, ratification predicate, family
   table, agreement normalization, and verdict rule. It disagreed with the
   serving path once during authoring, on exactly the point in (4), and the
   ORACLE was the side that was wrong; that disagreement is why the check
   exists.
6. **Anti-recall is a lane guard, not a hope.** A split must carry ≥3 probes
   whose answer is true in the world and absent from the curriculum, and no
   probe may carry a committed gold, or the lane refuses to run.

## 4. License posture

Every `curriculum_*` band is UNEARNED today, so every answer is served
DISCLOSED through the same hedge deduction serving uses. This is not a
temporary shortcut around the license — it is the license working. The reason
is §5.1.

## 5. Findings

### 5.1 The binding constraint on Phase 2 is ratified curriculum VOLUME

A band earns SERVE at θ_SERVE=0.99 only with n ≥ 657 committed cases and a
genuine outcome mix. The question space of a subject is
`|vocabulary|² − |vocabulary|`, so volume is reachable (physics: 240,
philosophy_theology: 22,650). **Entailed** cases are not: physics teaches 7
causal and 9 modal relations, so at most 16 distinct questions in the whole
subject can come back ENTAILED. Sampling cannot fix this — repeating the same
16 questions inflates n without adding information, and a band whose entailed
class is 1% of its volume is passed by a pipeline that never entails anything.

Concretely: a balanced band (≈⅓ entailed) needs **≈219 distinct taught
relations per subject × family**. Physics has 7 and 9. That is a ~25× gap, and
it is a curriculum-authoring and ratification task — Shay's call, not an
engineering one.

The honest consequence, recorded rather than worked around: the machinery,
the lane, the oracle, and the license gate all ship and pass; the licenses do
not exist yet; every answer is hedged until they do. The plan's O→S checkpoint
("≥1 subject lane serving wrong=0 with earned licenses") is met on every clause
except the last, and the last one cannot be met from present data.

### 5.2 REFUTED is unreachable from present corpora

Every ratified chain is a positive assertion. Refuting a question needs the
curriculum to teach a negative ("no X causes Y") or an exclusion. Until a
corpus does, `refuted` is a verdict this path can render but never reach. The
serving code handles it; the lane documents it.

### 5.3 There is no biology domain-chain corpus

The plan names "physics and biology" as Phase 2's two subjects because "OOD
lanes, seed packs, and domain chains already exist". For biology only the first
two are true: `evals/foundational_biology_ood` is a **fluency** lane (its own
contract says it measures grammatical English, not truth) and there is no
`biology_chains_*.jsonl`. The four subjects with ratified chains AND mounted
packs are physics, mathematics_logic, systems_software, and
philosophy_theology; the composer serves all four. The second subject should be
chosen from those, or biology's chain corpus authored first.

## 6. Scope-outs

- **Question shapes** beyond `Does <term> <relation> <term>?` — multi-word
  terms, "why"/"how" questions, negated questions, and quantified questions all
  refuse typed. Each is a separate readable unit with its own lane.
- **Composition**, per §3.3 — a future ADR may license it for a family the
  curriculum itself declares transitive, but that requires the declaration to
  be an executable claim rather than a classification label, which today it is
  not.
- **Premise-set scaling** — a family with more than `MAX_PREMISE_SENTENCES`
  (16) ratified chains compiles to an argument the reader refuses, surfacing as
  `compiled_premises_unreadable`. No current family exceeds 9. The fix when one
  does is to compile the query's k-hop neighborhood rather than the whole
  family (sound: fewer premises can lose an entailment, never create one), and
  to disclose the narrowing.

## 7. Verification

- `tests/test_curriculum_serve.py` — 20 tests: premise provenance and the
  loud-failure guard, family scoping never losing a taught edge, taught-edge
  entailment, untaught composition staying UNKNOWN, untaught fact never
  REFUTED, relation read at face value, base-form question normalization,
  anti-recall declines, 3 typed refusals, non-question pass-through, routing,
  the disclosed-until-earned license posture and the authoritative path when a
  band IS licensed, and oracle independence including the depth-2 reachability
  assertion.
- `evals/curriculum_serve` lane: 32/32, wrong=0, 5 anti-recall probes, both
  physics bands exercised. Pinned as `curriculum_serve_v1`.
