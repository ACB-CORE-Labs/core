# ADR-0251: Reader-Arc Recalibration — Halt Bespoke-Per-Case Regex Work; Clean-Base Reset; Proposed Geometric Surface→Canonical Normalization Spike

**Status**: §§1–4 (the recalibration decision — halt, reset, debt eradication, knowledge preservation) are
**executed**, verified by command, 2026-07-19. §5 (the geometric-normalization spike) is **Proposed —
awaiting ruling**. This ADR does not authorize any build; §5 is a direction proposal only.
**Date**: 2026-07-19
**Deciders**: Joshua Shay (ruling authority) + Claude (recalibration executor, this pass)
**Depends on**: `#77`/`#78`/`#79` (compare-multiplicative compiler tier + `NEUTRAL_COUNT_VERBS`
positive-polarity allowlist — the foundations this recalibration preserves), ADR-0136 family
(statement-layer corridor), ADR-0175 (calibrated attempt-and-eliminate learning — serving `wrong=0` vs.
sealed practice), ADR-0191 (candidate-graph completeness guard), ADR-0249 (reader→Hamiltonian compiler
composition frontier), ADR-0250 (tier-2 multi-entity arithmetic)
**Related (for §5's building blocks)**: ADR-0239 (Conformal Procrustes / analogical versor search — the
general primitive this spike would apply), ADR-0245 (CGA unification, mechanical sympathy and semantic
rigor), ADR-0246 (§6 explicitly disclaims Smith-chart algebra — honored here, not re-litigated)
**Supersedes**: `feat/reader-inc2-caseband` (PR #80) — **abandoned, not merged**
**Companion docs**: `docs/research/reader-arc-recalibration-preserved-knowledge-2026-07-19.md`,
`docs/research/0148-first-conversion-proof.md`, `docs/research/reader-arc-overfit-inventory-2026-07-19.md`

---

## 1. Context — why bespoke-per-case regex work is being halted

The GSM8K math reader (`generate/math_candidate_parser.py`, `generate/recognizer_match.py`,
`generate/recognizer_anchor_inject.py`, `generate/math_roundtrip.py`, `generate/math_candidate_graph.py`)
has advanced case-by-case: each new held-out case that needed a new surface form got a new, narrow regex
tailored to that case's exact wording. This has produced real, `wrong=0`-safe progress (the `#77`/`#78`/
`#79` compiler tier and positive-polarity substrate are sound and stay on `main`), but the *shape* of the
growth is overfitting-shaped: one bespoke pattern per case does not generalize, and the inventory in
§4 shows the pattern accumulating.

`feat/reader-inc2-caseband` (PR #80) is the branch that surfaced this concretely. It pursued case 0148
(the first real held-out conversion of this arc) and, per the PR's own review thread, succeeded at the
narrow goal — `report.json` shows exactly one case flipped (`0148: refused → correct`), `correct 5→6`,
`wrong=0` held — but introduced debt in the process:

1. **A shared grounding primitive was loosened fail-open.** `_token_in()` in `generate/math_roundtrip.py`
   — used by every candidate's roundtrip-admissibility check, not just mass-noun ones — was widened to
   accept a multi-word phrase whenever all of its component words appear *anywhere* in the source's token
   set (order- and position-independent), rather than requiring the phrase to be a contiguous substring.
   That weakens a shared safety gate to admit one family. This is the same "don't loosen a shared gate to
   admit one case" failure the `#77` split was already built to avoid.
2. **A committed "proof" artifact was left empty.** `docs/research/0148-first-conversion-proof.md` was
   committed at 0 bytes while the branch's own session-break summary claimed a graph dump had been
   recorded there. It had not been. See the preserved-knowledge doc §3 for the verified discrepancy.
3. **Commits bundled provenance** — prior uncommitted WIP and `report.json` landed under one message,
   muddying the record of what was reviewed.

None of this reached `main` — the branch was never merged (verified in §2). But the pattern it exhibits
(one more bespoke regex, one more case) is the thing being halted, independent of this specific branch's
debt. Per the ruling recorded here: **no further bespoke-per-case regex work proceeds on this reader.**
The existing regex reader is not being torn out — it keeps serving as-is (§2) — but it is not being
extended case-by-case going forward. The forward direction is proposed in §5, gated on a human ruling.

## 2. Decision — halt + clean-base reset (executed and verified)

All of the following were verified by direct command against the repository, not asserted:

- **Local `main` == canonical tip.** `git rev-parse` on `refs/heads/main`, `origin/main` (GitHub mirror),
  and `forgejo/main` (source of truth per this project's routing doctrine) all resolve to
  `854ce023d9cd58663ce9c9af0d62f92684ffb277` — the merge commit for PR #79 (increment-1 BAND plan:
  seed + comparison `#78` + question-arithmetic). Local `main` had drifted to this tip via an earlier
  `git reset: moving to forgejo/main` (from a stale `920695bd`); `git merge-base --is-ancestor 920695bd
  854ce023` confirms that reset was fast-forward-equivalent — `854ce023` is a strict descendant, no
  history was rewritten or lost.
- **`feat/reader-inc2-caseband` / PR #80 is abandoned, not merged.** `merged: false`,
  `merge_commit_sha: null` on the PR; the branch's tip (`e3da148d`) is not an ancestor of `main`. The PR
  is closed (not merged) with a comment referencing this ADR (see the PR thread). The branch ref itself
  is left intact on the remote as an archived reference — no force-delete, no history rewrite.
- **Main is free of the branch's specific debt.** `grep -rn "_COMPARE_MASSNOUN_RE"` and a grep for the
  loosened multi-word `_token_in` signature (`source_span: str | None = None`) both return zero matches
  under `generate/`. No empty `*proof*.md` exists anywhere in `docs/` (`0148-first-conversion-proof.md`
  is the one populated fresh in this recalibration, §3 below — 4.6 KB, not empty).
- **The legitimate foundations are intact and unmodified.** `compare_multiplicative` (the `#77` compiler
  tier) and `NEUTRAL_COUNT_VERBS` / the positive-polarity allowlist (`#78`) are both present across
  `generate/math_candidate_parser.py`, `generate/math_roundtrip.py`, `generate/recognizer_match.py`, and
  related modules — these are sound, reviewed, and load-bearing, and this recalibration does not touch
  them.
- **Smoke and the holdout baseline are green on this exact state.** `uv run core test --suite smoke -q`
  → 176 passed, 0 failed. `uv run python -m evals.gsm8k_math.holdout_dev.v1.runner` →
  `correct=5 wrong=0 refused=495 (n=500)` — matching the committed `evals/gsm8k_math/holdout_dev/v1/
  report.json` baseline exactly (the pre-branch state, before 0148's one-case flip). `wrong=0` holds.

No scope beyond the abandoned branch's own additions was removed. This recalibration is a reset to the
already-correct `main`, not a rollback of anything reviewed and merged.

## 3. Preserved knowledge (not lost)

Two facts of genuine, general value were extracted from the abandoned branch before it was set aside, and
are now captured — independently re-verified, not copied from the branch's own claims — in
`docs/research/reader-arc-recalibration-preserved-knowledge-2026-07-19.md`:

1. **The `has_numeric_token` multiplier-blindness bug** (`generate/math_candidate_parser.py:2374`) — the
   closed word-number set the reader uses to decide whether a statement sentence carries parseable
   numeric state does not include multiplicative comparatives (`twice`, `thrice`, `double`, `triple`).
   This is real and reproducible (verified against 23 real cases in `holdout_dev/v1` where it matters),
   but — also verified — it has not been a `wrong=0` hazard, because the independent ADR-0191
   completeness guard (`generate/math_completeness.py`) already resolves multipliers correctly via the
   `en_numerics_v1` pack and refuses rather than confabulates. Net effect: missed conversions, not wrong
   answers. A minimal, general fix idea is documented (extend `has_numeric_token` to recognize the closed
   `_ANCHOR_TO_FACTOR` multiplier set) but is **explicitly not landed** — per this project's floor, a
   shared-primitive change lands only with full-500 `wrong=0` proof and paired with whatever downstream
   op consumes it, never in isolation.
2. **Case 0148 solves correct-for-the-right-reason.** The real (non-empty) graph dump —
   `docs/research/0148-first-conversion-proof.md` — shows the conditional-seed binding the *named*
   reference (second day = 500), the compare op reading forward (first day = 2×second day, not an
   inverted guess), and the summation covering exactly both registers to reach 1500. This is a validation
   target for a future increment, not code being landed now.

## 4. Overfit inventory (a list, not a deletion)

A read-only survey of `generate/*.py` and `evals/refusal_taxonomy/*.py` on `main` identified bespoke,
single-case-shaped surface patterns — regexes and extractors that encode one sentence's exact wording
rather than a general grammatical class. The full, file:line-cited list lives in
`docs/research/reader-arc-overfit-inventory-2026-07-19.md`. This is **inventory, not a removal list** —
every pattern on it keeps serving unmodified; the reader must keep working until a proven replacement
exists (§7 of the task guardrails). Its purpose is to give the geometric-normalization spike (§5), if
ruled to proceed, a concrete target list of what "one general operator replacing N bespoke regexes" would
need to subsume before it could claim a positive generalization ratio.

## 5. Proposed forward direction — geometric surface→canonical normalization spike (AWAITING RULING)

**This section is a proposal. Nothing in it is authorized to be built by this ADR.** It is recorded so
the design-first gate has a concrete direction to rule on, per the task that produced this recalibration.

### 5.1 Thesis

Instead of hand-writing one new regex per newly-encountered surface shape, normalize a statement's surface
text into a canonical geometric representation and let a single general operator align novel surface forms
to already-known canonical forms — replacing N bespoke regex families with one normalization step plus a
small, closed set of canonical forms the solver already understands.

### 5.2 Building blocks — already implemented, off-serving; to be *wired*, not invented

Verified present in the repo, all currently off-serving/telemetry-only for this purpose:

- **`conformal_procrustes`** (`core/physics/dynamic_manifold.py:634`) — Kabsch-conformal Procrustes /
  field conjugacy: finds the best versor (or grade-1 sandwich adjoint) mapping a source point-set onto a
  target point-set. Docstring is explicit: *"Off-serving geometry; not wired into chat/runtime."* This is
  the general primitive ADR-0239 (Proposed) already scopes for analogical transfer; this spike would be
  one concrete application of it, not a new mechanism.
- **`VocabManifold`** (`vocab/manifold.py:68`) — the geometric vocabulary: every word is a unit versor in
  Cl(4,1); `nearest(F)` finds the closest word by CGA inner product (no cosine similarity, no ANN index,
  per the module's own normalization doctrine).
- **The cognition pipeline's "conformal anti-unifier" intent** (`core/cognition/pipeline.py:472-478`,
  "Phase C — Geometric Anti-Unification") — currently read-only telemetry that captures graph-structural
  context around OOV/pending holes "so that a future exact-CGA sub-graph anti-unifier can operate on
  conformal neighbors rather than lexical token match." Explicitly observational only today ("never
  affects surface, hash (yet), or any durable mutation").

The spike, if ruled to proceed, would be the work of *assembling* these three already-accepted-or-proposed
primitives into a reader-normalization path — not inventing new geometric machinery.

### 5.3 Proposed measurement — generalization ratio, `wrong=0`-gated

Define **generalization ratio** = (real `holdout_dev/v1` cases newly converted refused→correct) ÷ (new
concepts/parameters added to the normalizer to achieve that). Contrast baseline: the bespoke-regex era's
own ratio is ~1 case per bespoke regex family (0148's mass-noun frame converted exactly one case for one
new regex + one actor-binding relaxation + one Gate-A1 widening). The spike's burden of proof is a ratio
durably **greater than 1** — one normalization concept lifting more than one case — before it is allowed
to replace any existing regex path. Every measurement runs on `holdout_dev/v1` (open, 500 cases, no key
needed) via `uv run python -m evals.gsm8k_math.holdout_dev.v1.runner`; the sealed 1,319-case test is never
touched by this spike's iteration loop, per this project's train/dev/test discipline (ADR-0175 and the
`holdout_dev/v1` README's own doctrine). `wrong=0` is non-negotiable at every measurement — any
correct→wrong regression kills the spike's claim regardless of lift elsewhere.

### 5.4 Explicit disclaimers

- **Smith-chart algebra is NOT proposed and stays disclaimed.** ADR-0246 §6 already rules this out by
  name ("no Smith-chart algebra") alongside a list of other non-goals (no analytic cast reactance, no
  VSWR/atlas work). This spike does not revisit that ruling. Where an "impedance-matching" intuition might
  be reached for, the equivalent capability is `conformal_procrustes` (§5.2) — an already-accepted
  primitive — not a new Smith-chart library.
- **No "Fibonacci dimensional cascade" is proposed.** The only Accepted Fibonacci work in this repo
  (ADR-0242, deterministic evidence-gated operators for optimization/scheduling/multi-scale allocation) is
  unrelated to reader surface normalization, and nothing here proposes extending it into a new cascade
  mechanism for this purpose.
- **This spike does not touch the sealed test, does not modify the existing regex reader, and does not
  start with this ADR.** It requires a separate, explicit ruling before any code is written.

### 5.5 Scope boundary if ruled to proceed

Off-serving spike only, measured against `holdout_dev/v1`, `wrong=0`-gated at every step, with the
existing regex reader continuing to serve unmodified for the duration. Promotion of any spike output to
serving code would itself require its own review and ruling — this ADR does not pre-authorize that step
even conditionally.

## 6. What's ready to build next

Nothing is authorized to start building yet. What exists, verified, at the close of this recalibration:
a clean `main` at the canonical tip with the `#77`/`#78`/`#79` foundations intact and unmodified; the
abandoned branch's debt provably absent; two preserved, re-verified validation targets (the
`has_numeric_token` bug and the 0148 decomposition) waiting for whichever future increment picks them up;
a descriptive (non-deletion) overfit inventory scoping what a normalizer would need to subsume; and a
proposed — not started — geometric surface→canonical normalization spike with its building blocks
verified present, its measurement contract (`wrong=0`-gated generalization ratio on `holdout_dev/v1`)
defined, and its non-goals (Smith-chart algebra, any Fibonacci "dimensional cascade") explicitly
disclaimed. The next action is a human ruling on §5 — whether to authorize the spike, in what scope, and
against what acceptance bar — not further implementation.
