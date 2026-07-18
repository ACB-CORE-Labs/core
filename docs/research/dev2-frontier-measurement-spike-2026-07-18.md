# dev-holdout-2 / Frontier-Measurement Spike — verdict

**Status**: SPIKE VERDICT — for ruling before any build
**Date**: 2026-07-18
**Base**: `forgejo/main @ b87cd46c` (ADR-0249 + ADR-0250 Accepted; compiler solves the authored dev/public corpus)
**Branch**: `feat/dev2-frontier-spike`
**Charge (Shay)**: public-seal + floors; the Reader A answer; the raw-incidence measurement with an
(a)/(b)/(c) verdict; the draw-protocol trace — before building anything.

---

## 0. Headline correction (load-bearing — read first)

**`evals/gsm8k_math/dev` (50) and `public` (150) are NOT real GSM8K.** ADR-0119.2 authors them as
200 **CORE-original, GSM8K-*style*** problems written in CORE's own vocabulary/grammar to a chosen
operation distribution (case notes: "Generated public case exercising divide operations"). My
ADR-0249/0250 evidence called these "the real GSM8K dev holdout" — that is inaccurate and should be
corrected to "CORE-authored GSM8K-style." The compiler's verified result is **200/200 wrong=0 on
authored, grammar-matched, mostly depth-1 problems** — a real validation of the *mechanism*, not of
real-GSM8K capability.

## 1. Draw-protocol trace (Shay's ask: was the draw annotability-conditioned?)

| Slice | Real GSM8K? | How drawn |
| :--- | :--- | :--- |
| `train_sample` (50) | **Real** | `openai/gsm8k` main/train, rev `740312a…`; deterministic `sha256(f"{i}:SALT")` rank, top 50. What the grammar was hand-built against (overfit). |
| `holdout_dev/v1` (500) | **Real** | train split minus train_sample, sorted by `sha256(question)`, first 500. "Real GSM8K CORE was NOT built on." |
| sealed test (1,319) | **Real** | GSM8K test split, sealed (`.age`). |
| **`dev` (50), `public` (150)** | **Authored** | **CORE-authored** (ADR-0119.2), CORE grammar, chosen op/depth distribution. |

So (b) is not subtle "selection bias in a real draw" — it is **authoring**: dev/public are synthetic
and their frontier-freeness is an authoring choice, carrying zero information about real GSM8K's
distribution. The real draws (train_sample, holdout_dev) are unbiased and were the right place to
measure all along.

## 2. The real measurement (end-to-end on 500 real holdout_dev cases)

Pipeline: real text → `parse_and_solve` (Reader A) → my compiler (Tier-1/Tier-2) → execute → gold.

| Metric | Value |
| :--- | :--- |
| Reader A parses a graph | **5 / 500 (1%)** — refuses **495** |
| Reader A own solver correct | 5 / 500 (1%) |
| **My compiler solved** | **0 / 500** |
| …compiler wrong | 0 (fail-closed held) |
| The 5 parsed graphs' op kinds | **all `compare_multiplicative`** (a frontier kind) |

Corroborates the holdout_dev README's 2026-06-04 baseline ("real GSM8K capability 0%"). The compiler
solves 0 real cases — not because it is wrong, but because the reader feeds it only 5 graphs and those
5 are a frontier kind the affine compiler refuses.

## 3. Censored-incidence fix — the parse-independent measurement

The 500-run's op-kind incidence (§2) is **censored data**: it reads kinds only from the 5 graphs the
reader produced, so it says nothing about what the 495 refusals *need*. To answer (b)-vs-(c) honestly,
frontier incidence must be measured **around** the refusing reader. Protocol: the first **100** of the
sha256-ordered holdout_dev (deterministic), classified by **keyword/pattern markers in the raw text**
— parse-independent, multi-label, imperfect (a marker need not mean the op is required; over/under-count
possible), but the *scale* is robust to that noise.

| Frontier kind (marker) | Incidence /100 |
| :--- | :--- |
| `apply_rate` ("per", "each … costs", "every …") | **31** |
| `fraction_portion` ("half", "third", "%", "a/b") | **28** |
| `compare_multiplicative` ("twice", "N times as many") | **20** |
| `compare_additive` ("more/fewer than") | 9 |
| `unit_partition` ("split into", "divided among") | 1 |
| **basic-only (no frontier marker)** | **30 / 100** |
| **≥1 frontier marker** | **70 / 100** |

## 4. The (a)/(b)/(c) verdict (de-censored)

- **(a) — DOMINANT. Real GSM8K is reader-gated.** Reader A refuses 495/500 at parse; text does not
  become graphs. A *mechanism* gap in the reader, not the compiler's affine scope.
- **(b) — CONFIRMED as authoring bias.** dev/public are authored frontier-free; they carry zero
  information about real GSM8K's distribution. Every "real GSM8K" claim on them needs the correction.
- **(c) — REFUTED, now with parse-independent evidence.** The frontier is **common, not rare**:
  **70/100** official problems carry frontier markers; rate + fraction alone appear in ~55%. Widening
  off-serving capability against this frontier does NOT fail the decidable-done-when test — the reader
  reaching it does.

**Bonus: this table is the reader arc's curriculum, ordered by real-world frequency** — rate (31) →
fraction (28) → compare_multiplicative (20) → compare_additive (9) → partition (1). Practice earns the
most real coverage by attacking rate/fraction/comparison first.

## 5. Two instruments, cleanly named, both kept (ruling)

The finding is a **reframe, not a retraction** — nothing measured is thrown away, it is relabeled.

- **Authored corpus = the mechanism-correctness instrument.** A controlled curriculum that proved the
  compiler end-to-end. Its **200/200 wrong=0 stands, as exactly that** — evidence the mechanism
  (versor transport + chained certified relaxation + conservation + atomicity + chain-of-custody) is
  correct on clean inputs.
- **Official holdout = the generalization instrument.** `holdout_dev` (500), sealed test (1,319) —
  real GSM8K, never authored.

**The scoreboard, never blended:**

| Instrument | Slice | Score | Reads as |
| :--- | :--- | :--- | :--- |
| Mechanism-correctness | authored (200) | **200/200 wrong=0** | the compiler is correct |
| Generalization | official holdout_dev (500) | **5/500 Reader-A-symbolic · 0/500 corridor** | real reach is ~0 |

Seal `public` and pin both floors (dev-1 50/50, public 150/150) — but **label them mechanism floors,
not coverage claims**, each carrying an op-kind histogram + ops-per-case depth + the authored-not-real
flag (public: depth-1, divide 53 + transfer 97). A regression floor that guards mechanism correctness;
it says nothing about real-GSM8K coverage, and the record must say so.

## 6. Sequencing verdict (resolved by the data)

The three-branch skeleton doesn't fire: the frontier is common (§3), so "frontier-rare → serve
landing" is out; and the biggest bucket isn't a compiler tier — **it's the reader** (495/500). Stated
plainly: **corridor real end-to-end capability is 0/500, so serve-landing of corridor arithmetic loses
priority — there is nothing real-reaching to serve.** §3.7 calibration stays queued; the **reader
practice volume is what eventually generates §3.7's calibration data.** Order unchanged:
**capability → practice → calibration → serve** — and the reader arc is now the **critical path for all
three**.

## 7. The arc (RULED) — reader, design-first: per-family increments in lockstep

Superseding §10's practice-loop recommendation: the frontier being **common, formulaic, and
frequency-ordered** (§3) argues *for* designed grammar-family extensions, not against — a formulaic
frontier is exactly what designed grammar eats efficiently, each increment cheaply measurable.
**Learning earns its complexity only when design stops paying — decided by number, not feel.** The
practice loop is the paper-designed backup (§7.4), not the arc.

### 7.1 Increment = a grammar family + its compiler tier, landed together
Reader and compiler move in **lockstep**. §2 is the proof they cannot move separately: the 5 real
`compare_multiplicative` parses **die at the affine compiler today** (reader emits, compiler refuses →
0/500). A reader family with no compiler tier produces graphs nothing solves; a compiler tier with no
reader family has no inputs — that is the *only* thing §10.2 de-prioritizes. **Paired, they are the
arc.** Each increment is its own smoke-gated PR carrying a measured `holdout_dev` delta (new correct),
the `wrong=0` floor held, and the sealed test untouched.

### 7.2 Increment order
1. **`compare_multiplicative` FIRST** — jumps the §3 frequency queue because the reader *already emits
   real parses for it* (the 5/500), so pairing a compare compiler tier moves corridor real-reach from
   **0/500 → >0 immediately** — the cheapest possible end-to-end proof the increment loop works on
   official data.
2. Then strict §3 frequency order: **rate (31) → fraction (28) → compare_additive (9) → partition (1)**.

### 7.3 Escalation threshold X — PROPOSED (Shay rules with the merge)
Fixed now, before anyone is attached, so "switch when design stops working" cannot drift.
**Proposed X = 15 new-correct on `holdout_dev` per full family increment.** When a completed increment
buys fewer than X, escalate to a practice-lane ruling. Rationale: these families carry 20–31% incidence
(~100–155/500 problems each); a design that is paying converts far more than 15, so falling below
15/500 (3%) means design has stopped efficiently converting known incidence — a number trips the
switch, not a feeling.

### 7.4 Backup lane — the practice loop (PAPER DESIGN only; starts warm if X trips)
Same decidable loop (`attempt-parse → compile → execute → gold-check`, wrong=0-gated). Its leverage —
how it reuses what these arcs already built, so only two things are genuinely new:
- **Verifier** = the Tier-1/Tier-2 compiler stack: a candidate parse is correct **iff**
  `compile → execute → gold` agrees. No separate oracle.
- **Audit** = the certificate chains (`RelaxationCertificate`, `TurnRecord`, chain-of-custody).
- **Consolidation gating** = `prepare → validate → commit` generalized: a candidate consolidates only
  on full success.
- **Holdout hygiene** = ADR-0119 sealing (split discipline; sealed test untouched).
- **Genuinely new** = a **candidate generator** (proposes parses/grammar variants) + a **consolidation
  store** (what survives wrong=0). That is the whole delta the lane adds.

### 7.5 Non-negotiable constraints (bind the increments now; carry to the lane verbatim)
1. Eval/practice signal is **real held-out official data only** — never the authored corpus (§3's
   200/200-vs-5/500 gap is the overfit fingerprint).
2. `wrong=0` gates what consolidates / lands.
3. The sealed test (1,319) is **never touched** — final exam only.
4. `holdout_dev` **splits**: tuned/practiced-against cases disjoint from the measured metric split —
   "getting better" can only mean "generalizes to real problems."

### 7.6 Design-first work IS the backup's curriculum (record, don't discard)
Every increment's refusal taxonomy, tagged incidence, and labeled `(parse, compile, execute, gold)`
tuples are **practice-lane artifacts**, not throwaway — the labeled data + failure map a candidate
generator would train against. Design-first pre-pays the backup's cold-start.

## 8. Errata proposal — ADR-0249 / ADR-0250 (statuses stay Accepted)

A prominent **errata section** (not silent rewording) is added to both ADRs and their acceptance
evidence, and to the PR #74 review record: the mechanism claims all survive; the single correction is
the corpus label — **"real GSM8K dev holdout" → "CORE-authored GSM8K-style corpus (ADR-0119.2)."** The
record thus shows we caught our own mislabel, which is the honest-measurement doctrine working, not a
failure to hide. (Errata text lands in this PR alongside the spike.)

## 9. The generalization reframe (Shay, live)

"Generalize, don't overfit" is right, and the compiler honors it: it is a general *mechanism*, not
memorized answers. The measurement only forces one distinction — **mechanism-generality ≠ real-problem
coverage.** The mechanism is general but starved: 1% reader reach, affine scope. The reader practice
loop is precisely how that value becomes real coverage without re-introducing the overfit.

## 10. Ruling outcome (Shay, on this PR)

The arc is the **reader, design-first**: per-family increments — a grammar family in Reader A plus its
matching compiler tier, landed **in lockstep** (§7) — starting with **`compare_multiplicative`**, then
strict §3 frequency order (rate → fraction → compare_additive → partition). Each increment is its own
smoke-gated PR with a measured `holdout_dev` delta, `wrong=0` held, sealed test untouched.

The **practice loop is the paper-designed backup** (§7.4), not the arc; it starts warm only if a full
increment buys **fewer than X = 15 new-correct on `holdout_dev`** (proposed §7.3, Shay rules with the
merge). §5 (mechanism floors + never-blended scoreboard), §6 sequencing
(capability → practice → calibration → serve; serve-landing deferred at 0/500), the errata (§8), and
the four non-negotiable constraints (§7.5) are affirmed and merge with this.

**Next: the `compare_multiplicative` increment plan as the arc's first PR. Nothing else starts.**
