# Curriculum-Volume Quantification — ADR-0262 §5.1

**Tier S6** (generalization-arc-2026-07-24 §6). Evidence only. This
document does not propose ratifying curriculum content or flipping
`curriculum_serving_enabled` — both are Shay's decisions
([[project-curriculum-serving-ratified]] doctrine: a flag flips on earned
evidence, not proximity to it). It answers one question precisely: *how
short of a SERVE license is each served `(subject × relation family)` band
today, measured against the actual ratified corpora, not an estimate.*

Method: `teaching.curriculum_premises.load_curriculum(domain)` — the same
loader the curriculum composer uses in serving — run against each of the
four subjects `chat.curriculum_surface.SERVED_DOMAINS` currently routes to.
Counts below are chain counts (ratified, vocabulary-resident, `review_status
== "reviewed"`), i.e. exactly the population `compile_premises` would draw
premises from; nothing here touches unmounted or unratified content.

## 1. The floor, restated precisely (§1.2 of the ratification packet)

`Action.SERVE` needs a one-sided Wilson lower bound ≥ θ=0.99
(`core/reliability_gate/ceilings.py`, `core/reliability_gate/floor.py`). For
a perfect record this reduces to `committed / (committed + z²)` with
`z = 2.576`, which crosses 0.99 at **committed ≥ 657**.

657 committed cases alone is not sufficient — the plan (§6) and the
ratification packet both require a **genuine outcome mix**, not 657
restatements of the same fact padded with paraphrase (repetition-padding
was already considered and rejected as dishonest earlier in this arc:
`conservative_floor` cannot distinguish "657 independent facts" from "16
facts asked 41 times each," but a ledger that gamed the floor that way
would not have *earned* anything). Treating "genuine mix" as roughly a
three-way split across `entailed` / `refuted` / `unknown` (the plan's own
working assumption, not a formally ratified policy — flagged here as an
assumption, not fact) puts the **entailed bucket's floor at ≈219 distinct
taught relations** — `⌈657 / 3⌉`. That is where the plan's "≈219 per
subject × family" figure comes from; this document supplies the measured
`n` for every currently-served band to compare against it.

## 2. Measured ratified-chain counts, per subject × family (2026-07-24)

| domain | family | ratified chains (n) | 657÷n | 219÷n |
|---|---|---:|---:|---:|
| physics | causal | 7 | 94× | 31× |
| physics | modal | 9 | 73× | 24× |
| mathematics_logic | modal | 4 | 164× | 55× |
| mathematics_logic | sequence | 4 | 164× | 55× |
| mathematics_logic | contrast | 8 | 82× | 27× |
| mathematics_logic | evidential | 8 | 82× | 27× |
| systems_software | causal | 7 | 94× | 31× |
| systems_software | modal | 6 | 110× | 37× |
| systems_software | sequence | 3 | 219× | 73× |
| philosophy_theology | modal | 8 | 82× | 27× |
| philosophy_theology | contrast | 8 | 82× | 27× |

11 bands are live (a subject × family pair with ≥1 ratified chain routes
questions today, per `chat.curriculum_surface.band_for`); every one is
between 24× and 73× short of the entailed-bucket floor alone, before even
authoring the matching refuted/unknown volume. **No served subject has a
family close enough to flag as "next."** Systems-software `sequence` (n=3)
is the thinnest; mathematics_logic `modal`/`sequence` (n=4 each) are tied
for second-thinnest; physics `modal` (n=9) is the closest of the eleven,
still 24× short.

Total ratified chains per subject (all families, informational context —
not a band-level floor since bands are scored per family, not per subject):
physics 16, mathematics_logic 24, systems_software 16,
philosophy_theology 16.

## 3. Vocabulary is not the constraint

`Curriculum.vocabulary` (every lemma the subject's mounted packs teach) is
16 lemmas for physics/mathematics_logic/systems_software and **151** for
philosophy_theology — an order of magnitude more vocabulary than chains in
every subject. The gate `untaught_vocabulary` (§4.6) is not what is holding
any band back; the terms are taught, the *relations between them* are not
authored in ratified volume. This confirms ADR-0262 §5.1's framing: the
blocker is curriculum content authorship, not reader/vocabulary coverage —
see also S3's mechanism-vs-coverage instrument
(`docs/research/vocab-trigger-instrument-2026-07-24.md`), which finds the
curriculum path's own refusals are overwhelmingly coverage-class for a
different reason (relation, not term, absent) while carrying zero
`untaught_vocabulary` refusals in the committed lane corpus.

## 4. What one subject fully reaching the floor would look like

Taking physics `modal` (the closest band, n=9) as an illustration only: it
would need roughly 210 more ratified `requires`/`enables` relations,
authored and reviewed through the existing curriculum ratification
pipeline, before an entailed bucket alone could support a 657-committed
band — and that is before authoring the matching refuted/unknown volume
this document is not attempting to size (refuted questions need explicit
negative curriculum content the corpora do not currently carry at all;
unknown questions are comparatively cheap to author from
in-vocabulary-but-untaught pairings, so they are not expected to be the
binding constraint).

## 5. Non-goals of this document

- Does not recommend which subject or family to grow first — that is
  content strategy, Shay's call.
- Does not estimate authoring effort/time (no clock-time estimates per
  standing convention).
- Does not touch `curriculum_serving_enabled` or any corpus file.

Relates to [[project-curriculum-grounded-serving]],
[[project-generalization-arc]], `docs/adr/ADR-0262-curriculum-grounded-serving.md` §5.1.
