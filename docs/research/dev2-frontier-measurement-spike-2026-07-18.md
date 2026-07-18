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

## 3. The (a)/(b)/(c) verdict

- **(a) — DOMINANT. The frontier (and real GSM8K generally) is reader-gated.** Reader A refuses
  495/500 real problems at parse. The binding constraint is not the compiler's affine scope; it is
  that real GSM8K text does not become graphs at all. This is a *mechanism* gap in the reader.
- **(b) — CONFIRMED for dev/public, but as authoring, not draw-filtering.** The frontier-free authored
  corpus tells us nothing about real GSM8K. Every "real GSM8K" coverage claim on dev/public needs the
  denominator correction to "authored corpus."
- **(c) — REFUTED as the binding issue.** Frontier kinds are not rare in real GSM8K: the *very first*
  problems that parse are `compare_multiplicative`, and real problems visibly use comparison / rate /
  fraction language ("twice as many as", "half of"). The frontier is common; the reader just can't
  reach it.

## 4. Public-seal — approved, with the disclosure sharpened

Sealing/pinning `public` (150) buys a **narrow authored regression floor**: 150 cases, **1 op per
case (depth-1)**, **two kinds only** (divide 53 + transfer 97), all CORE-authored. Pin dev-1 (50/50)
and public (150/150) as regression floors, but the coverage record MUST carry, per slice:
- an **op-kind histogram** and **ops-per-case depth**, and
- the **authored-not-real** provenance flag.

Honest headline: **"200/200 wrong=0 on CORE-authored GSM8K-style (depth/kinds disclosed); real-GSM8K
compiler coverage = 0/500 (reader-gated)."** Anything shorter inflates.

## 5. Sequencing verdict (three branches, resolved by the data)

- big coherent bucket → build that tier;
- long-tail fragmentation → serve landing (§3.7 + scoped `generate/`);
- **frontier-rare-in-raw-GSM8K → serve landing** — **does NOT apply**: the frontier is common, not rare.

The data selects a branch the skeleton didn't enumerate: **the biggest bucket is the reader itself**
(495/500). Building more compiler tiers is capability with no inputs; serve-landing is premature
(there is ~nothing real to serve). The decidable next move is to **make the reader parse real GSM8K**.

## 6. Reader-practice-loop — named, not started (per the charge)

The Reader-A answer is **no** — it cannot turn real GSM8K text into graphs at scale — so by the
standing agreement this moves the reader-practice-loop from "eventually" to the **leading next-arc
candidate**. The reader is the first genuinely *learnable* component in the stack: `attempt-parse →
compile → execute → gold-check` is a practice loop with a **decidable, wrong=0-gated reward** on a
held-out real set (`holdout_dev`, never the authored corpus). Crucially, this is the
**generalization-preserving** way to grow real capability — it optimizes parsing *coverage* against
held-out real data, the opposite of authoring more grammar-matched problems (which is the overfit
trap). It is named here for the post-spike ruling; not started.

## 7. The generalization reframe (Shay, live)

"We don't want overfitting; we want generalization" is right, and the compiler honors it: it is a
**general mechanism** (versor transport + chained certified relaxation), not memorized answers —
which is why it holds wrong=0 across authored problems it never saw. But the measurement forces a
distinction: **mechanism-generality ≠ real-problem coverage.** The mechanism is general yet starved —
1% reader coverage, and its affine scope misses the compare/rate/fraction the little real data uses.
"Generalized problem-solving on real inputs" (the original done-when) is therefore **not yet shown**;
what is shown is a general composition substrate validated on clean inputs. The reader-practice-loop
is exactly how that value (generalize, don't overfit) becomes real-problem coverage.

## 8. For the ruling (three arcs on the table, none started)

1. **Reader-practice-loop** — grow real-GSM8K parse coverage off 1%, wrong=0-gated on held-out real
   data. Strongest by the measurement.
2. **More compiler tiers** (compare/rate/fraction) — de-prioritized: the reader feeds them almost
   nothing; capability without inputs.
3. **Serve-landing** (§3.7 + `generate/`) — premature until there is real capability to serve.

Recommendation: reader-practice-loop. Plus the cheap housekeeping: pin the two authored floors
(composition-disclosed) and correct the "real GSM8K" language in the ADR-0249/0250 evidence.
