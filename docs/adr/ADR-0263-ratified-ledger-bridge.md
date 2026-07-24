# ADR-0263 — The ratified-ledger bridge

- **Status:** Proposed
- **Date:** 2026-07-24
- **Arc:** generalization Phase 3.3 (docs/plans/generalization-arc-2026-07-24.md §2)
- **Governs:** `core/ratified_ledger.py` and the three adapters over it —
  `generate/determine/estimation_license.py`, `chat/deduction_serve_license.py`,
  `chat/curriculum_serve_license.py` — plus the sealed-artifact writer in
  `evals/deduction_serve/practice/runner.py`.

## 1. Context

Three capabilities had independently converged on the same four-step pattern:
sealed practice writes a per-class tally table → the table is committed as a
ratified artifact → serving verifies its `content_sha256` on load → a per-class
gate decides SERVE against fixed ceilings.

Three near-identical implementations is the point at which a shared component
is an extraction rather than a guess. It matters now because the generalization
plan puts a per-subject arena behind every new subject: without a bridge, each
subject copies fifty lines of verification, and the copies drift.

## 2. Decision

`core/ratified_ledger.py` owns the mechanics — `seal_artifact`,
`write_sealed_ledger`, `load_sealed_ledger`, `serve_license`, `tally_dict` —
and states the four rules once:

1. **The engine reads; only sealed practice writes.**
2. **Tamper-evidence is structural** — a load that cannot reproduce
   `content_sha256` REFUSES. A hand-edited ledger is not a slightly-wrong
   ledger; it is an unratified one.
3. **Ceilings are not negotiable at the call site** (ADR-0175 invariant #4).
4. **Absent evidence is never a license** — a missing class yields `None`, and
   every caller's `None` branch serves the disclosed surface.

Each capability keeps a thin adapter that names its artifact, keeps its
memoization, and preserves its public API. One genuine difference is now
declared rather than implied: `load_sealed_ledger(..., missing_ok=True)`
distinguishes a ledger a capability *ships with* (absence = broken deployment,
refuse) from one whose practice volume is still being built (absence = no class
has earned anything, serve disclosed). Curriculum serving is the second kind
today (ADR-0262 §5.1).

## 3. Why this is safe

The extraction's safety property is byte-identity: `seal_artifact` and
`write_sealed_ledger` reproduce exactly what the bespoke sealers wrote, so
re-sealing through the bridge leaves every committed artifact and every lane
pin unmoved. That is asserted, not assumed —
`test_committed_deduction_ledger_reseals_byte_identically` re-derives the
committed 25-band ledger through the bridge and compares the bytes.

## 4. What this unblocks

A new subject arena now needs a gold corpus and a band key. It does not need to
re-implement ratification — which is what the plan meant by "so each subject
arena plugs in without bespoke wiring", and why §3 sequenced this ahead of the
second subject.

## 5. Scope-outs

- **The estimation adapter keeps its predicate → converse-class naming.** That
  mapping is genuinely local to estimation; the bridge gates a class name and
  does not know how one is derived.
- **No ledger migration.** All three artifacts already share the schema shape;
  nothing is rewritten, versioned, or moved.
- **`core/learning_arena`'s practice engine is untouched.** The bridge covers
  the consumption half (seal → serve); the production half (run practice, tally)
  is already shared.

## 6. Verification

`tests/test_ratified_ledger_bridge.py` — 8 tests: round-trip, hand-edit
rejection, required-vs-optional absence, absent class never licensed, the
Wilson volume floor, a single `wrong` costing the license, committed-ledger
byte-identity, and a guard that all three adapters read through the bridge
(they no longer import a hashing module of their own). Plus the existing
consumers unchanged: `core test --suite deductive` 252 passed; the estimation
and license test set 355 passed.
