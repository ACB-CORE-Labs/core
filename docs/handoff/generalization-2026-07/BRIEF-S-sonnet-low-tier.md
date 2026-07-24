# Handoff Brief — Tier S (Sonnet 5, LOW risk)

**Read first:** `docs/plans/generalization-arc-2026-07-24.md` §6
(constraint set is binding) and the Tier-O brief's constraints block —
they apply verbatim. Opus will have updated this brief with actual state
at its exit checkpoint; trust that update over anything stale below.

**You own (independent items, any order unless noted):**

1. **S1 — ratification packet for `deduction_serving_enabled`.**
   Evidence collation only — the flip is Shay's decision, never yours.
   Contents: 17+-band sealed ledger stats
   (`chat/data/deduction_serve_ledger.json`), serve-lane results
   (`evals/deduction_serve/report.json`), byte-identical-when-off proof
   (cite ADR-0256 + `tests/test_deduction_surface.py` flag tests), blast
   radius (exact dispatch point `chat/runtime.py` deduction branch), and
   rollback (flip back, zero residue). One markdown doc in
   `docs/research/`, PR'd.
2. **S2 — lane re-pins + flake documentation.** Only AFTER the Phase-0.1
   drift findings doc exists and says re-pin is safe. Surgical
   single-line edits in `scripts/verify_lane_shas.py` — NEVER `--update`
   (it rewrites every lane and silently drops erroring lanes' pins).
   Document the `public_demo` env-timeout flake where the findings doc
   says.
3. **S3 — vocab-trigger instrument.** Implement the measurable test
   specified in `docs/handoffs/COMPREHENSION-READER-AUDIT.md`
   (§measurable-test, lines ~163–166 and ~231–238): refusal histogram
   split mechanism-vs-coverage + Phase-2-admissions-per-lexicon-batch
   counter. CLI or lane runner per the spec; do not invent policy — the
   spec decides, you implement.
4. **S4 — HITL proposal-queue CLI.** A `core` CLI surface listing +
   reviewing pending proposals from the existing sinks
   (`teaching/proposals/`, contemplation/idle sinks). Read + review-state
   transitions only; NO ratification automation, NO corpus mutation, NO
   flag flips.
5. **S5 — housekeeping.** Promotion sweeps Opus's checkpoint notes call
   for; capability-index entries for new subject lanes; docs/memory
   updates; dead-code removal only when unambiguous.

**Constraints:** identical to Tier O (worktrees, fresh venv, pre-push
gate, compare-URL PRs, Shay merges, wrong=0, flags stay off, no
timelines). When any item's scope turns out larger than described here —
stop and flag it in the PR/handoff notes rather than improvising.

**Arc close:** all Tier-S PRs pushed; memory updated; note whether the
Phase-5 articulation trigger (multi-step decided content exists) has
fired, for the next arc's scoping.
