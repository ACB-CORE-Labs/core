# Handoff Brief — Tier S (Sonnet 5, LOW risk)

**Read first:** `docs/plans/generalization-arc-2026-07-24.md` §6 (constraint
set is binding) and the Tier-O brief's constraints block — they apply verbatim.

---

## STATE AT THE OPUS → SONNET CHECKPOINT (updated 2026-07-24)

**Tier O is complete.** Four units, all committed, all with local gates green:

| unit | branch @ commit | what |
|---|---|---|
| O1 | `feat/existential-band` @ `e84c0e84` | Band v6-EX existentials (ADR-0261) + a wrong-answer fix in Band v1b |
| O2 | `feat/curriculum-serve-physics` @ `44e78aa4` | curriculum-grounded serving (ADR-0262), physics lane 32/32 wrong=0 |
| O3 | same branch @ `0a17c496` | ratified-ledger bridge (ADR-0263) |
| O4 | same branch @ `353a52b8` | math Phase 4.1 measured status — null result, documented |

Branch stack (each on the previous): `main` → `feat/verb-predicate-band`
(PR #111, Shay's, still open) → `feat/existential-band` →
`feat/curriculum-serve-physics`.

### ⛔ BLOCKER — pushes to core-labs/core are failing server-side

The Forgejo repo has a **corrupt object**: `refs/heads/feat/verb-predicate-band`
(= PR #111 head, `e41a3e2a`) points at a **zero-length object file** on the
server. Symptoms:

```
remote: error: object file .../objects/e4/1a3e2a...  is empty
remote: fatal: bad object refs/heads/feat/verb-predicate-band
! [remote rejected] <your-branch> (missing necessary objects)
```

This blocks **every** push to the repo, not just the Opus branches — the
server fails its own connectivity check before accepting any ref. Reads
(`git fetch`, `ls-remote`, MCP) still work. Nothing local is damaged: the
identical content exists locally as `d181ae30`.

Repair needs filesystem access on the Forgejo VM (remove the empty object,
then reset or delete `refs/heads/feat/verb-predicate-band` and
`refs/pull/111/head`, `git fsck`). **This is Shay's call — do not delete or
force-push someone else's PR branch.** Until it is fixed, work locally and
commit; push when the server is repaired.

### Corrections to the plan's ground truth (verified — act on these)

1. **There is no biology domain-chain corpus.** `evals/foundational_biology_ood`
   is a *fluency* lane (its own contract says so) and no `biology_chains_*.jsonl`
   exists. The subjects with ratified chains AND mounted packs are physics,
   mathematics_logic, systems_software, philosophy_theology. Pick the second
   subject from those, or author biology's chains first.
2. **Phase 4.1 (seeding-sentence injection) was already built** before this
   arc and converts 0 cases; the frozen-500 baseline re-measured today is
   `correct=5 wrong=0 refused=495`. See
   `docs/research/math-reader-phase-4-1-status-2026-07-24.md`. Phase 4 should
   be re-pointed at the reader arc's own live recommendation (increment-2
   case-first on cases 0000/0001/0148/0082).
3. **No curriculum band can earn a SERVE license from present data.** A band
   needs n≥657 with a real outcome mix; physics teaches 7 causal + 9 modal
   relations, so at most 16 questions in the whole subject can ever come back
   ENTAILED. A balanced band needs ≈219 taught relations per subject × family.
   Phase 2's blocker is **ratified curriculum volume**, not machinery
   (ADR-0262 §5.1). Every curriculum answer is served DISCLOSED until that
   changes — which is the license working, not a workaround.

---

## You own (independent items, any order unless noted)

1. **S1 — ratification packet for `deduction_serving_enabled`.**
   Evidence collation only — the flip is Shay's decision, never yours.
   Contents: the **25-band** sealed ledger stats
   (`chat/data/deduction_serve_ledger.json`, all 25 at 720/720 wrong=0),
   serve-lane results (`evals/deduction_serve/report.json`, **166/166 across
   six splits**), byte-identical-when-off proof (cite ADR-0256 +
   `tests/test_deduction_surface.py` flag tests), blast radius (the deduction
   branch in `chat/runtime.py`), and rollback (flip back, zero residue).
   **Add a second section for `curriculum_serving_enabled`** (ADR-0262): same
   shape, noting explicitly that every curriculum band is unearned, so the
   flip enables a *disclosed* capability. One markdown doc in `docs/research/`.

2. **S2 — lane re-pins + the `public_demo` drift.** The Phase-0.1 findings doc
   exists (`docs/research/lane-drift-investigation-2026-07-24.md`).
   **Correct the standing note: `public_demo` is NOT a timing flake here.** It
   reproduces deterministically. Measured this session:
   - pinned: `7d8ba0db…` (last set at commit `7f6c497a`, long before this arc)
   - content with the register-axis fix reverted: `c6596e11…`
   - content today: `da7fad65…` (3 identical runs, incl. on the base commit)

   So there are **two** drifts: one predating PR #110 (unexplained — find it
   before re-pinning) and one caused by PR #110's register-axis fix (expected,
   intended). `all_passed` stays `true` throughout; only the demo payload
   digest moved. Do the archaeology, then re-pin surgically — **never
   `--update`** (it rewrites every lane and silently drops erroring lanes'
   pins). Three arcs now depend on that rule.

3. **S3 — vocab-trigger instrument.** Implement the measurable test specified
   in `docs/handoffs/COMPREHENSION-READER-AUDIT.md` (§measurable-test):
   refusal histogram split mechanism-vs-coverage + admissions-per-lexicon-batch
   counter. Two ready-made feeds now exist: the curriculum path's
   `untaught_vocabulary` / `out_of_curriculum` refusals
   (`chat/curriculum_surface.py`) are literally coverage-class refusals, and
   the deduction bands' typed refusals are mostly mechanism-class. Do not
   invent policy — the spec decides, you implement.

4. **S4 — HITL proposal-queue CLI.** A `core` CLI surface listing + reviewing
   pending proposals from the existing sinks (`teaching/proposals/`,
   contemplation/idle sinks). Read + review-state transitions only; NO
   ratification automation, NO corpus mutation, NO flag flips.

5. **S5 — housekeeping.**
   - Add `tests/test_register_substantive_consumption.py`'s e2e tests to the
     curated smoke suite (a red test outside every gate is a silent red — the
     lesson from the #96 regression).
   - Capability-index entries for the new lanes (`curriculum_serve_v1`, the
     `v2_exist` split).
   - Promotion sweep: `ds-mem-0020` was promoted declined→unknown by v6-EX
     (already done); check nothing else in the older splits is now decidable.
   - Memory/doc updates; dead-code removal only when unambiguous.

6. **S6 (new) — quantify the curriculum-volume ask.** From ADR-0262 §5.1:
   produce a short doc stating, per served subject × relation family, how many
   ratified chains exist and how many a balanced 657-case band would need.
   Evidence only — authoring or ratifying curriculum content is Shay's.

**Constraints:** identical to Tier O (worktrees, fresh venv, pre-push gate,
compare-URL PRs, Shay merges, wrong=0, flags stay off, no timelines). When any
item's scope turns out larger than described here — stop and flag it in the
PR/handoff notes rather than improvising.

**Arc close:** all Tier-S PRs pushed; memory updated; note whether the Phase-5
articulation trigger (multi-step decided content exists) has fired. Evidence
for it now exists on both sides: the deduction bands produce multi-premise
decided chains, and the curriculum path produces answers that state how much
curriculum they were decided from.
