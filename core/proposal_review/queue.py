"""core/proposal_review/queue.py — generic multi-sink proposal queue (Tier S4).

**Read + review-state transitions only.** NEVER ratification, NEVER corpus
mutation, NEVER flag flips — those stay `teaching/proposals.py`'s own
`accept_proposal`/`reject_proposal` path over a DIFFERENT sink
(`teaching/proposals/proposals.jsonl`, already CLI-exposed via
``core teaching proposals`` / ``core teaching review``, ADR-0057).

This module covers the other two proposal sinks the generalization-arc
brief calls "contemplation/idle sinks" — populated by background passes,
not by the ratification corridor, and until now readable only through a
Python API with no CLI surface at all:

- ``comprehension_failures`` (the N5 contemplation pass) — already has a
  hardened typed reader and an independent safety dry-check:
  :mod:`core.proposal_review` (``scan`` / ``dry_check``). Reused here, not
  duplicated.
- ``derived_close_facts`` (the idle_tick PR-2 bridge,
  :mod:`generate.determine.derived_close_proposals`) — emitter only, no
  reader existed before this module. Its own docstring says it is
  "reviewable by the same HITL tooling" as ``comprehension_failures`` —
  this is that tooling. Read GENERICALLY here (the shared minimal
  ``status``/``mounted``/``requires_review`` contract every proposal-only
  artifact carries), not via a new typed dataclass: the sink is currently
  empty and default-off (``review_derived_close_proposals``), so committing
  to a schema-specific reader now would be speculative in a way the
  populated ``comprehension_failures`` sink is not.

"Reviewing" here means recording that a HUMAN looked at an artifact — an
append-only sidecar log (``teaching/proposals/review_log.jsonl``), never a
write to the artifact itself. The artifact's own ``status`` / ``mounted`` /
``requires_review`` fields stay exactly what the emitter wrote; nothing in
this module can change what a proposal ratifies to.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.proposal_review.scan import DEFAULT_SINK as _COMPREHENSION_SINK
from core.proposal_review.scan import scan as _scan_comprehension
from generate.determine.derived_close_proposals import DEFAULT_SINK as _DERIVED_CLOSE_SINK

_REPO_ROOT = Path(__file__).resolve().parents[2]

#: The append-only human-review sidecar. Lives beside the sinks it reviews,
#: not inside either of them — a review record is metadata ABOUT an
#: artifact, never a mutation of it.
REVIEW_LOG_PATH = _REPO_ROOT / "teaching" / "proposals" / "review_log.jsonl"

#: Fields every proposal-only artifact in EITHER sink carries, regardless of
#: family-specific schema (verified against both emitters:
#: `core/comprehension_attempt/proposal.py`,
#: `generate/determine/derived_close_proposals.py`).
_SHARED_REQUIRED: tuple[str, ...] = ("status", "requires_review", "mounted")


@dataclass(frozen=True, slots=True)
class QueueEntry:
    """One proposal artifact, sink-agnostic. ``family`` is a short label for
    display only (``failure_family`` for comprehension-failures, ``source``
    for derived-close-facts) — it carries no safety meaning here."""

    sink: str
    content_hash: str
    family: str
    status: str
    requires_review: bool
    mounted: bool
    path: str


@dataclass(frozen=True, slots=True)
class MalformedEntry:
    sink: str
    path: str
    reason: str


@dataclass(frozen=True, slots=True)
class SinkSpec:
    name: str
    path: Path
    label: str


#: The two contemplation/idle sinks this queue reads. Order is display order.
SINKS: tuple[SinkSpec, ...] = (
    SinkSpec(
        "comprehension_failures",
        _COMPREHENSION_SINK,
        "comprehension-failure proposals (N5 contemplation pass)",
    ),
    SinkSpec(
        "derived_close_facts",
        _DERIVED_CLOSE_SINK,
        "derived CLOSE-fact proposals (idle_tick PR-2 bridge)",
    ),
)

_SINKS_BY_NAME: dict[str, SinkSpec] = {spec.name: spec for spec in SINKS}


def _scan_derived_close(root: Path) -> tuple[list[QueueEntry], list[MalformedEntry]]:
    """Generic reader for ``derived_close_facts`` — no typed dataclass (module
    docstring): validates only the shared minimal contract, tolerating the
    family's own extra fields (``predicate``/``subject``/``object``/...)."""
    if not root.exists():
        return [], []
    entries: list[QueueEntry] = []
    malformed: list[MalformedEntry] = []
    for path in sorted(root.glob("*.json")):
        try:
            raw: Any = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            malformed.append(MalformedEntry("derived_close_facts", str(path), f"invalid_json: {exc}"))
            continue
        if not isinstance(raw, dict):
            malformed.append(MalformedEntry("derived_close_facts", str(path), "not_a_json_object"))
            continue
        missing = [key for key in _SHARED_REQUIRED if key not in raw]
        if missing:
            malformed.append(
                MalformedEntry("derived_close_facts", str(path), f"missing_fields: {missing}")
            )
            continue
        predicate = str(raw.get("predicate", ""))
        subject = str(raw.get("subject", ""))
        obj = str(raw.get("object", ""))
        family = f"{predicate}:{subject}:{obj}" if predicate else str(raw.get("source", "unknown"))
        entries.append(
            QueueEntry(
                sink="derived_close_facts",
                content_hash=path.stem,
                family=family,
                status=str(raw["status"]),
                requires_review=bool(raw["requires_review"]),
                mounted=bool(raw["mounted"]),
                path=str(path),
            )
        )
    return entries, malformed


def scan_all(
    sink_names: tuple[str, ...] | None = None,
    *,
    roots: dict[str, Path] | None = None,
) -> tuple[list[QueueEntry], list[MalformedEntry]]:
    """Scan the requested sinks (default: all). Pure read, sorted by
    ``(sink, content_hash)`` for a deterministic listing order. ``roots``
    overrides a sink's directory by name — test isolation, never used by the
    CLI (which always reads the real sinks)."""
    names = sink_names or tuple(spec.name for spec in SINKS)
    entries: list[QueueEntry] = []
    malformed: list[MalformedEntry] = []
    for name in names:
        spec = _SINKS_BY_NAME[name]
        root = (roots or {}).get(name, spec.path)
        if name == "comprehension_failures":
            proposals, bad = _scan_comprehension(root)
            entries.extend(
                QueueEntry(
                    sink=name,
                    content_hash=p.content_hash,
                    family=p.failure_family,
                    status=p.status,
                    requires_review=p.requires_review,
                    mounted=p.mounted,
                    path=p.path,
                )
                for p in proposals
            )
            malformed.extend(MalformedEntry(name, m.path, m.reason) for m in bad)
        elif name == "derived_close_facts":
            good, close_bad = _scan_derived_close(root)
            entries.extend(good)
            malformed.extend(close_bad)
        else:  # pragma: no cover - closed SINKS tuple above
            raise ValueError(f"unknown proposal-queue sink: {name!r}")
    entries.sort(key=lambda e: (e.sink, e.content_hash))
    malformed.sort(key=lambda m: (m.sink, m.path))
    return entries, malformed


@dataclass(frozen=True, slots=True)
class ReviewRecord:
    sink: str
    content_hash: str
    note: str
    reviewed_at: str


def _load_review_log(path: Path | None = None) -> list[ReviewRecord]:
    log_path = path or REVIEW_LOG_PATH
    if not log_path.exists():
        return []
    records: list[ReviewRecord] = []
    for line in log_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        records.append(
            ReviewRecord(
                sink=row["sink"],
                content_hash=row["content_hash"],
                note=row.get("note", ""),
                reviewed_at=row["reviewed_at"],
            )
        )
    return records


def reviewed_keys(path: Path | None = None) -> frozenset[tuple[str, str]]:
    """``(sink, content_hash)`` pairs that have at least one review record."""
    return frozenset((r.sink, r.content_hash) for r in _load_review_log(path))


def record_review(
    sink: str,
    content_hash: str,
    *,
    note: str = "",
    path: Path | None = None,
    roots: dict[str, Path] | None = None,
) -> ReviewRecord:
    """Append one human-review record. Does NOT touch the artifact itself,
    does not ratify, does not mount, does not flip any flag — purely an
    append to the sidecar log. Raises ``KeyError`` if ``(sink, content_hash)``
    does not resolve in a fresh scan, so a typo cannot silently log a review
    of nothing."""
    entries, _malformed = scan_all((sink,), roots=roots)
    if not any(e.content_hash == content_hash for e in entries):
        raise KeyError(f"no pending entry {content_hash!r} in sink {sink!r}")
    log_path = path or REVIEW_LOG_PATH
    log_path.parent.mkdir(parents=True, exist_ok=True)
    record = ReviewRecord(
        sink=sink,
        content_hash=content_hash,
        note=note,
        reviewed_at=datetime.now(timezone.utc).isoformat(),
    )
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(asdict(record), sort_keys=True) + "\n")
    return record


def queue_status(
    sink_names: tuple[str, ...] | None = None,
    *,
    roots: dict[str, Path] | None = None,
    log_path: Path | None = None,
) -> dict[str, Any]:
    """Per-sink counts: total, pending_review (requires_review AND not yet
    human-reviewed), reviewed (has a review record), no_review_needed
    (requires_review is False — not currently emitted by either sink, kept
    distinct rather than folded into "reviewed" for correctness if that ever
    changes), malformed. Not a safety verdict — for ``comprehension_failures``,
    use :func:`core.proposal_review.dry_check` for that; this is a triage
    summary only."""
    entries, malformed = scan_all(sink_names, roots=roots)
    reviewed = reviewed_keys(log_path)
    by_sink: dict[str, dict[str, int]] = {}
    for spec in SINKS:
        if sink_names is not None and spec.name not in sink_names:
            continue
        sink_entries = [e for e in entries if e.sink == spec.name]
        no_review_needed = sum(1 for e in sink_entries if not e.requires_review)
        has_review = sum(
            1 for e in sink_entries if (e.sink, e.content_hash) in reviewed
        )
        pending = sum(
            1 for e in sink_entries
            if e.requires_review and (e.sink, e.content_hash) not in reviewed
        )
        by_sink[spec.name] = {
            "total": len(sink_entries),
            "pending_review": pending,
            "reviewed": has_review,
            "no_review_needed": no_review_needed,
            "malformed": sum(1 for m in malformed if m.sink == spec.name),
        }
    return by_sink


__all__ = [
    "REVIEW_LOG_PATH",
    "MalformedEntry",
    "QueueEntry",
    "ReviewRecord",
    "SINKS",
    "SinkSpec",
    "queue_status",
    "record_review",
    "reviewed_keys",
    "scan_all",
]
