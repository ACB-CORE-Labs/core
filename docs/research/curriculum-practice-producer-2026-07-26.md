# Curriculum practice producer — what building it measured (Phase C)

**Date:** 2026-07-26 · **Arc:** curriculum-license-loop-2026-07 · **Unit:** Phase C
**Code:** `evals/curriculum_serve/practice/{generator,runner}.py`,
`tests/test_curriculum_practice.py`
**Governs:** ADR-0262 §5 (what a curriculum band can earn), ADR-0264 R9 (volume honesty)

The producer named by `chat/curriculum_serve_license.py`'s own docstring —
`evals.curriculum_serve.practice.runner.seal_ledger`, declared "the only writer"
of the ledger that module reads — did not exist. It does now. Building it
measured three things, two of which correct records I wrote earlier in this arc.

Reproduce everything below with:

```bash
uv run python -m evals.curriculum_serve.practice.runner          # capped corpus
uv run python -m evals.curriculum_serve.practice.runner --full    # every atom (~75s)
```

---

## 0. What the producer is

A band's case space is **enumerated, not authored**: every exam question that
routes to that subject (`chat.curriculum_surface.resolve_domain`) whose relation
falls in that family. One committed case per distinct query atom, so
`committed == distinct` is not a property the generator maintains — it is the same
fact twice. This is the structural version of what ADR-0264 R9 asks for, and it is
why the curriculum producer cannot develop the deduction producer's exposure
(`CASES_PER_BAND = 720` filled by cycling spaces as small as 28).

`CASES_PER_BAND = 660` follows `evals/determination_estimation`, per
`DIVISION-OF-WORK.md` §4. It is a **ceiling on committed volume, not a quota**: a
band with a smaller space emits its whole space and reports a number below the
floor. Selection above the cap is every taught edge plus a fixed stride across the
rest — a lexicographic prefix of 660 out of 45,300 would cover about five subject
terms of 151 and report one corner of a band as the band.

Result over the capped corpus: **11 bands, wrong = 0, inflation 1.0 everywhere.**

---

## 1. Finding — a committed ledger is necessarily an *earning* ledger

The plan of record's Phase-1 exit criterion asks that
`curriculum_serve_license()` read "a real (still-unearned) ledger instead of an
absent one."

**That state is unreachable.** Reliability is commitment precision, and a correct
UNKNOWN is a commitment. `conservative_floor(660, 660) = 0.990046 ≥ 0.99`, so any
band with ≥657 routable atoms clears θ_SERVE on non-commitments alone, whatever its
curriculum says. Sealing today licenses **four** bands:

| band | committed | refused | reliability | SERVE | entailed | entailed share |
|---|---:|---:|---:|:---:|---:|---:|
| `curriculum_philosophy_theology_modal` | 45,188 | 112 | 0.99985 | **yes** | 8 | 0.0177% |
| `curriculum_philosophy_theology_contrast` | 22,598 | 52 | 0.99971 | **yes** | 8 | 0.0354% |
| `curriculum_physics_causal` | 720 | 0 | 0.99087 | **yes** | 7 | 0.9722% |
| `curriculum_systems_software_causal` | 720 | 0 | 0.99087 | **yes** | 7 | 0.9722% |
| `curriculum_physics_modal` | 480 | 0 | 0.98636 | no | 9 | 1.8750% |
| `curriculum_mathematics_logic_modal` | 480 | 0 | 0.98636 | no | 4 | 0.8333% |
| `curriculum_systems_software_modal` | 480 | 0 | 0.98636 | no | 6 | 1.2500% |
| `curriculum_mathematics_logic_contrast` | 240 | 0 | 0.97309 | no | 8 | 3.3333% |
| `curriculum_mathematics_logic_evidential` | 240 | 0 | 0.97309 | no | 8 | 3.3333% |
| `curriculum_mathematics_logic_sequence` | 240 | 0 | 0.97309 | no | 4 | 1.6667% |
| `curriculum_systems_software_sequence` | 240 | 0 | 0.97309 | no | 3 | 1.2500% |

(Exhaustive sweep: 71,790 atoms, `wrong = 0`, 164 refusals.)

A licensed band would therefore be certified on evidence that is **99.0%–99.98%
correct non-commitment**. ADR-0262 §5.1 explicitly rules that unacceptable. The
gate cannot see it: `ClassTally` carries `correct`/`wrong`/`refused` and **no
verdict axis**, so a correct UNKNOWN is indistinguishable from a correct ENTAILED
once tallied. Mix can only be enforced at the producer, which is exactly the
open outcome-mix ruling recorded in
`docs/research/distinct-evidence-audit-2026-07-25.md`.

**Consequence for this arc:** that ruling is no longer academic — it is the last
thing between a built loop and four unearned licenses. Phase C therefore ships the
writer and **does not commit the artifact**; `chat/data/curriculum_serve_ledger.json`
stays absent, `missing_ok=True` stays true, and every band stays DISCLOSED. Writing
it is a ratification, so it belongs to the explicit `core proposal-queue reseal`
verb a human runs (Phase D), and it should not be run before the mix ruling.

`tests/test_curriculum_practice.py::test_curriculum_ledger_is_not_committed` pins
the absence, and `test_sealing_would_license_exactly_the_bands_that_reach_the_floor`
pins the consequence, so neither can be lost and re-derived wrongly.

### Recommendation (still Shay's call)

Enforce mix **at the producer**, as a per-verdict-class floor rather than a ratio:
a band earns SERVE only when each verdict class it can express independently
reaches the volume the floor requires. Under that rule no band earns anything today
(max entailed volume is 9), which is the honest reading, and it makes ADR-0262 §5.1
mechanical instead of advisory. It also keeps the deduction bands' aggregate
licenses intact, since imposing a per-class 657 retroactively would fail all 25.

---

## 2. Correction — ADR-0264 §4.2's ceiling table understates every band

I sized bands from **per-term exclusivity** (a term taught by only one subject).
The router's actual predicate is **per-pair**: `resolve_domain` routes a question
iff exactly one served subject holds *both* terms. A term taught in two subjects
can still appear in a pair only one subject holds both halves of, so per-term
exclusivity is a strictly tighter bound and under-counts.

| band | ADR-0264 §4.2 | true | verdict change |
|---|---:|---:|---|
| `curriculum_systems_software_causal` | 630 | **720** | **cannot reach 657 → CAN** |
| `curriculum_philosophy_theology_modal` | 44,104 | 45,300 | — |
| `curriculum_philosophy_theology_contrast` | 22,052 | 22,650 | — |
| `curriculum_mathematics_logic_modal` | 420 | 480 | — |
| `curriculum_mathematics_logic_{sequence,contrast,evidential}` | 210 | 240 | — |
| `curriculum_systems_software_modal` | 420 | 480 | — |
| `curriculum_systems_software_sequence` | 210 | 240 | — |
| `curriculum_physics_{causal,modal}` | 720 / 480 | 720 / 480 | — |

So **4 of 11 bands can reach 657, not 3**, and **7 cannot, not 8**. The retarget
conclusion is unaffected — `philosophy_theology · modal` is still the largest space
by two orders of magnitude, and `physics · modal` (480) is still impossible at any
authoring volume. The numbers are now pinned in
`tests/test_curriculum_practice.py::BAND_ATOM_SPACE`, measured rather than derived,
so this class of error cannot recur silently.

---

## 3. Finding — two taught lemmas collide with the argument reader's grammar

`then` and `therefore` are lemmas `philosophy_theology`'s packs teach **and**
control words of the argument reader: `therefore` is literally the conclusion
marker in `". Therefore <conclusion>."`, and `then` is the conditional consequent
marker. An atom using either as a term compiles an argument the reader cannot parse
back, so it refuses `compiled_premises_unreadable`.

- **164 routable atoms** affected (112 modal + 52 contrast) out of 71,790.
- All 164 are **coverage misses, not wrongs** — excluded from reliability's
  denominator (ADR-0175 §4), never a confabulation. `wrong = 0` holds.
- Exactly two lemmas are responsible; every other implicated term is only ever the
  *partner* of one of them.
- It is in the band Phase F retargets to.

The narrow cost is small. The mechanism is not: **the vocabulary boundary and the
reader's grammar are never screened against each other.** A future pack teaching
`and`, `or`, `not`, or `if` would open a much larger hole the same way, and it would
present as a coverage dip rather than an error. A reserved-word check at pack mount
or at chain ratification would close it.

Not fixed here — outside Phase C's unit (`DIVISION-OF-WORK.md` §6.5). Pinned as a
bound by `test_the_collision_is_bounded_to_two_lemmas`, so a third reserved word
entering the curriculum fails loudly instead of quietly enlarging the gap.

---

## 4. What did not move

- `evals/curriculum_serve` lane: `[physics] n=32 correct=32 wrong=0 declined_mismatch=0
  anti_recall=5`, unchanged; `report.json` bytes and the `curriculum_serve_v1` SHA
  pin unchanged. The producer reads the same solver the lane does and writes nothing
  the lane reads.
- No serving behaviour change of any kind: no ledger committed, so
  `curriculum_serve_license()` still returns `None` for every band and every
  curriculum answer is still served DISCLOSED.
- `refuted` remains unreachable — no corpus row can express a negative until
  ADR-0264 R1–R4 is implemented. `test_gold_mix_has_no_refuted_class` pins that as a
  red test for the polarity unit to turn green.
