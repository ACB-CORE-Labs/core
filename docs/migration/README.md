# The legacy shrink-ratchet

The migration's other half. `../coreai` records what it **admits**; this records what that admission does to the surface **here**.

The keel's migration protocol makes it step 7, and makes it same-day:

> **The retirement entry.** Same day, in `../core`: the superseded path enters the legacy shrink-ratchet (or its dark modules are deleted outright when nothing served them). An admission that doesn't shrink the old surface is growth, not migration.

Without this ledger that sentence has nowhere to land, and "the legacy surface shrinks under ratchet" (`docs/plans/2026-07-28-foundations-audit.md`) stays an intention rather than a measurement. The migration ends when the keel serves everything worth serving and the remainder here is explicitly **retired, archived-with-reason, or deleted** — target end-state **zero unexplained modules**, not zero modules.

## The rule

**Ratchet, not log.** `surface_delta` is the count of files this repository loses at the admission. It may be negative or zero; over the migration its cumulative sum must trend down and may never be silently reversed. A row that removes nothing must say why, and must name the condition that will let it.

## `status` vocabulary

| status | meaning |
|---|---|
| `retired` | the path is gone here; the keel serves its job |
| `carried_not_retired` | the keel has admitted it, but this repository still serves it — the path stays, and `retires_when` names the condition |
| `archived_with_reason` | kept here deliberately and permanently; the reason is the record |
| `deleted_dark` | removed outright because nothing served it (the 373/666 case) |

`carried_not_retired` is not a loophole, it is the honest shape of a bottom-up migration: the foundation is admitted to the keel long before anything in the keel consumes it, so its copy here must keep serving. It is countable precisely so it cannot become permanent by inattention.

## Files

- `legacy-shrink-ratchet.jsonl` — one row per keel admission, append-only.
