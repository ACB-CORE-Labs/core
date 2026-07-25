# HITL Proposal-Queue CLI — `core proposal-queue`

**Tier S4** (generalization-arc-2026-07-24 §6). A `core` CLI surface for
listing and reviewing pending proposals from the contemplation/idle sinks —
`teaching/proposals/comprehension_failures/` (the N5 contemplation pass) and
`teaching/proposals/derived_close_facts/` (the idle_tick PR-2 bridge). Read +
review-state transitions only: no command here ratifies, mutates the
teaching corpus, mounts anything, or flips a flag. That corridor
(`teaching/proposals.py`'s `accept_proposal`/`reject_proposal`, a DIFFERENT
sink — `teaching/proposals/proposals.jsonl`, ADR-0057) already has its own
CLI (`core teaching proposals` / `core teaching review`) and is untouched.

## What shipped

- `core/proposal_review/queue.py` — a sink-agnostic scanner
  (`scan_all`), an append-only human-review sidecar log
  (`teaching/proposals/review_log.jsonl`, via `record_review` /
  `reviewed_keys`), and a triage summary (`queue_status`).
- `core/cli_proposal_queue.py` — `core proposal-queue {status,list,show,review}`,
  registered via the same `register(subparsers)` pattern
  `core/cli_ingest.py` and `formation/cli.py` use.
- `tests/test_proposal_queue.py` (13 tests, registered in the `teaching`
  suite), fully isolated from the real sinks via `roots=`/`path=`
  overrides — never touches the real `teaching/proposals/review_log.jsonl`.

```
core proposal-queue status [--sink NAME] [--json]
core proposal-queue list [--sink NAME] [--pending-only] [--json]
core proposal-queue show <sink> <content-hash>
core proposal-queue review <sink> <content-hash> [--note TEXT]
```

`review` only appends a `{sink, content_hash, note, reviewed_at}` record to
the sidecar log after confirming the hash resolves in a fresh scan (a typo
cannot silently "review" nothing); it never opens the artifact file for
writing. `test_record_review_does_not_touch_the_artifact` pins that
byte-for-byte.

## A real bug found while building the second sink's reader

`generate/determine/derived_close_proposals.py::DEFAULT_SINK` computed
`Path(__file__).resolve().parents[3] / "teaching" / "proposals" /
"derived_close_facts"`. From `<repo>/generate/determine/derived_close_proposals.py`,
`parents[2]` is the repo root (0=`determine/`, 1=`generate/`, 2=`<repo>`) —
`parents[3]` is one directory **above** the repository. Confirmed live: a
`core proposal-queue list` run before the fix listed an entry at
`/Users/kaizenpro/Projects/teaching/proposals/derived_close_facts/…` — a
directory sitting outside `core/` entirely, containing one stray artifact
dated 2026-06-16, untracked by git, invisible to anything that searches
inside the repository. Fixed to `parents[2]`
(`test_derived_close_default_sink_resolves_inside_the_repo` pins it).

**Why nothing caught this before:** the sink is gated by a default-off flag
(`review_derived_close_proposals`) and no existing test asserted
`DEFAULT_SINK` resolves inside the repo — its own tests, where they exist,
pass an explicit `sink=` override. The bug was silent because the feature
has essentially never run in its default configuration. The stray file
outside the repo was left as-is (it is not tracked by git and this session
has no standing to delete files outside the repository without being
asked); a future real run of `emit_derived_close_proposals` will now write
to the correct, in-repo location.

## Design choices, made explicit

- **No typed dataclass for `derived_close_facts`.** Unlike
  `comprehension_failures` (which has a hardened `PendingProposal` reader
  and an independent safety `dry_check`, both reused unchanged here), this
  queue reads `derived_close_facts` generically — only the shared minimal
  contract (`status`/`requires_review`/`mounted`) is validated. Committing
  to a schema-specific reader for a sink that is currently empty and
  default-off would be speculative; the generic reader is honest about
  that and will not silently misclassify whatever the emitter's schema
  settles into.
- **No new safety dry-check for `derived_close_facts`.** The existing
  `core/proposal_review/safety.py::dry_check` is scoped to
  `comprehension_failures`'s specific content-address formula. Extending
  it to the second sink's different dedupe-key formula would be a real
  design decision about what "inert" means for that family — out of
  scope for a read/review CLI, and not requested.
- **Review vocabulary stays minimal: a note, not a state machine.** No spec
  exists for review-state vocabulary (accept/flag/defer/etc.); inventing
  one would risk becoming ratification-adjacent policy. `record_review`
  answers exactly one question — "has a human looked at this?" — with an
  optional free-text note, which is the smallest thing that satisfies
  "review-state transitions" without overstepping into ratification.

## Non-goals

- Does not touch `teaching/proposals.py`, `accept_proposal`, or
  `core teaching proposals`/`review` — that corridor is unchanged.
- Does not run `emit_derived_close_proposals` or otherwise populate either
  sink; both are read as they currently stand (one real
  `comprehension_failures` entry, zero `derived_close_facts` entries once
  read from the corrected path).
- Does not wire `core proposal-queue` into `idle_tick` or any automated
  loop — operator-invoked only, per the brief's HITL framing.

Relates to [[project-generalization-arc]].
