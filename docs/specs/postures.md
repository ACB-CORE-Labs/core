# Posture Statements

**Authority:** R-1, R-5, R-6, R-11 (`docs/assessment/50-rulings.md`), ruled 2026-07-28.
**What this file is for:** four decisions that cost nothing to make and something real to leave silent. Each names a **criterion** — the evidence that would change the posture — because an unstated boundary reads as an unexamined one, and a future reader cannot tell a deliberate limit from an accident.

None of these flips a flag. Three record where CORE deliberately stops; the fourth records a proposal **withdrawn because measurement dissolved its premise**.

---

## P-1 · Efferent action is deferred, with an entry criterion (R-1, ruled A · G-12)

CORE's telos ends at *articulate / learn / replay*. AGI-grade generality ordinarily implies acting on the world, and no system-level statement existed either way.

**Posture: deferred, in scope eventually, and nothing moves until the criterion is met.**

> **Entry criterion.** No efferent surface beyond typed, trace-folded tool operators (ADR-0018) until **(i)** the chooser (G-4) exists and is governed, and **(ii)** an efferent falsification bench exists at the standard `docs/specs/` sets for M2.

Both halves are load-bearing. Without (i) CORE would act with no principled account of *what it should do next* — the Candidate Register's open seat. Without (ii) it would act with no way to be shown wrong, which is the one thing this architecture never permits of a serving capability.

*Why deferral rather than exclusion:* declaring efferent action out of telos is coherent and cheap, but it forecloses a scope decision on a system whose chooser has not been designed. Deferral costs nothing exclusion saves and preserves the option. **ADR-0211's prohibition on motor/efferent units in the falsification bench v1 is narrower than this and remains in force** — it is a bench-level rule, not the system-level statement recorded here.

---

## P-2 · Identity enforcement stays scoring-only until a discrimination bar is cleared (R-5, ruled A · G-11)

`identity_wave_gate` is off; `identity_action_surface` is off and documented **"NOT authorized for live activation."** That is a deliberate, well-reasoned posture. What was missing was the criterion, and a posture with no criterion decays into an unexamined default.

**Posture: scoring without blocking, until live refusal is authorized by measured discrimination.**

> **Authorization bar.** Live identity *refusal* requires a discrimination report on a **named, held-out** corpus of benign and adversarial traffic, showing a separation between the two on the certified metric, at a **floor named before the run**. γ_id is the only certified metric today; `identity_action_surface`'s thresholds are uncertified placeholders and ADR-0246 §6.3 shows it refuses benign and adversarial traffic alike on the declared placeholder frame.

*Why the bar is stated in advance:* the pre-registration discipline that made ADR-0252 §5's NO-GO full credit applies here for the same reason. A refusal gate authorized on a floor chosen after seeing the numbers is not evidence, and identity refusal is a surface where being wrong is expensive in both directions — a false refusal is a denial of service to a legitimate user, a false accept is the attack succeeding.

**Scoring-without-blocking stays honest only while the path to blocking exists.** This is that path.

---

## P-3 · Non-text ingest is deferred, with the falsification bench as its standard (R-6, ruled A · G-17)

59 sensorium modules exist and reach no serving path; projection heads do not exist. The position paper is honest about this. It was neither built nor deliberately postponed — which reads as drift.

**Posture: explicitly deferred. Not a gap; a decision.**

> **Entry criterion.** A non-text modality enters serving when it meets the **same falsification standard as text**: a named held-out corpus, a falsifiable predicate set with holds/bites pairs, and `wrong=0`-or-refuse on the serving path. No modality is admitted on the strength of the substrate being able to represent it.

*Why this criterion and not a roadmap:* the sensorium's existence is not evidence that it works, and the arc that produced this file spent its length distinguishing *built* from *proven*. Naming the bench as the standard makes non-text ingest earn its way in on exactly the terms text did, and makes the 59 modules a **capability awaiting evidence** rather than an unexplained absence.

---

## P-4 · The interim fabrication gate is WITHDRAWN — measurement dissolved its premise (R-11, ruled B → second ruling)

R-11 ruled **B: measure first, then re-ask.** The instrumentation ran on 2026-07-28. It did not return a rate; it returned a reason the question could not be asked in that form, which is the more valuable outcome and exactly what an instrumentation step is for.

**The proposal.** While the G-2 fabrication fixes are held for their ADR, serve an interim posture: *refuse to hold a reading outside the verified 19-construction inventory.*

**What the measurement found.**

| | |
|---|---|
| distinct serving-path inputs measured | **11,199** (deduction + curriculum practice corpora) |
| clauses, at the reader's own sentence split | **23,562** |
| clauses outside the verified inventory | **0** |

That zero is **not** a clean bill of health, and reporting it as one would be the error this file exists to avoid. It is an artifact with a cause:

> **One of the 19 verified constructions is `atom_fact`, whose template is `{p}` — a single slot with no literal anchor. It matches any string.**

So **"outside the verified inventory" is not a well-defined syntactic property.** Nothing is outside it. The proposed gate would refuse nothing while appearing to be a safety mechanism — a mechanism whose failure state is indistinguishable from its success state, which is this repository's dominant defect class.

**This reframes G-2, and the reframing is the finding.** `every dog is a mammal` → `member(every_dog, mammal)` is **not** the reader admitting an out-of-inventory construction. The surface is admissible; the reader assigns it the **wrong relation**. Likewise `asserted(furthermore)`. The defect is in the **mapping**, not in the admissibility set — and no gate over the admissibility set can catch it.

**Second ruling (DELEGATED, 2026-07-28): option A is WITHDRAWN as unimplementable as specified — not deferred.** A deferred option is one that could be built later; this one cannot be built at all against the inventory as it stands, and recording it as "deferred" would leave a future reader to rediscover why. Option **C** (no interim gate; the fixes stay held for the fabrication ADR) is the operative posture.

**What the fabrication ADR inherits, stated so it is not lost.** It must define the admissibility boundary itself, because the verified inventory does not supply one. Specifically: either `atom_fact` is narrowed so that admissibility is decidable, or the guarantee is relocated from *admissibility* to *mapping correctness* — a check that the relation assigned to an admissible surface is the one that surface licenses. The second is the shape the evidence points at.

*Method note, recorded because the number nearly shipped wrong.* The first two passes of this measurement were both invalid — one matched templates against whole multi-sentence inputs (reporting 100% out-of-inventory, when every clause was in-inventory), the other misread the sentence-splitter's tuple and measured `"."` 23,562 times. Both produced confident, plausible, wrong numbers. The catch-all was found only by a **non-vacuity check** — asserting the matcher could still say *no* to `"most birds can fly"` — and it could not. A measurement that cannot fail is not a measurement.
