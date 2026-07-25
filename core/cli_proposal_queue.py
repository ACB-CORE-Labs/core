"""core/cli_proposal_queue.py — ``core proposal-queue`` CLI (Tier S4).

Operator-facing surface over :mod:`core.proposal_review.queue`: list and
review pending proposals from the contemplation/idle sinks
(``comprehension_failures``, ``derived_close_facts``). Read + review-state
transitions ONLY — no command here can ratify, mutate the teaching corpus,
mount anything, or flip a flag. Ratification stays ``core teaching
proposals`` / ``core teaching review`` over the separate ADR-0057 sink.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from core.proposal_review.queue import (
    SINKS,
    QueueEntry,
    record_review,
    reviewed_keys,
    scan_all,
    queue_status,
)

_SINK_NAMES = tuple(spec.name for spec in SINKS)


def _print_entry(entry: QueueEntry, *, reviewed: bool) -> None:
    mark = "reviewed" if reviewed else ("pending" if entry.requires_review else "no-review-needed")
    print(f"[{entry.sink}] {entry.content_hash}  {mark:<17} status={entry.status} family={entry.family}")


def cmd_proposal_queue_status(args: argparse.Namespace) -> int:
    sinks = (args.sink,) if args.sink else None
    status = queue_status(sinks)
    if args.json:
        print(json.dumps(status, indent=2, sort_keys=True))
        return 0
    for name, counts in status.items():
        print(
            f"{name}: total={counts['total']} pending_review={counts['pending_review']} "
            f"reviewed={counts['reviewed']} malformed={counts['malformed']}"
        )
    return 0


def cmd_proposal_queue_list(args: argparse.Namespace) -> int:
    sinks = (args.sink,) if args.sink else None
    entries, malformed = scan_all(sinks)
    reviewed = reviewed_keys()
    if args.pending_only:
        entries = [
            e for e in entries
            if e.requires_review and (e.sink, e.content_hash) not in reviewed
        ]
    if args.json:
        payload = {
            "entries": [
                {**asdict(e), "reviewed": (e.sink, e.content_hash) in reviewed}
                for e in entries
            ],
            "malformed": [asdict(m) for m in malformed],
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    if not entries:
        print("(no pending proposals)")
    for entry in entries:
        _print_entry(entry, reviewed=(entry.sink, entry.content_hash) in reviewed)
    for m in malformed:
        print(f"[{m.sink}] MALFORMED {m.path}: {m.reason}")
    return 1 if malformed else 0


def cmd_proposal_queue_show(args: argparse.Namespace) -> int:
    entries, _malformed = scan_all((args.sink,))
    match = next((e for e in entries if e.content_hash == args.content_hash), None)
    if match is None:
        print(f"error: no entry {args.content_hash!r} in sink {args.sink!r}")
        return 2
    with open(match.path, encoding="utf-8") as fh:
        raw = json.load(fh)
    print(json.dumps(raw, indent=2, sort_keys=True))
    return 0


def cmd_proposal_queue_review(args: argparse.Namespace) -> int:
    try:
        record = record_review(args.sink, args.content_hash, note=args.note or "")
    except KeyError as exc:
        print(f"error: {exc}")
        return 2
    print(f"recorded review: {args.sink}/{args.content_hash} at {record.reviewed_at}")
    return 0


def register(subparsers: argparse._SubParsersAction) -> None:
    """Attach the ``core proposal-queue`` subcommand tree to a top-level parser."""
    queue = subparsers.add_parser(
        "proposal-queue",
        help="list and review pending contemplation/idle proposals (HITL, read-only)",
        description=(
            "Read-only listing plus human-review-state tracking over the "
            "comprehension_failures and derived_close_facts proposal sinks. "
            "Never ratifies, mutates the teaching corpus, mounts anything, or "
            "flips a flag — that stays `core teaching proposals`/`review`."
        ),
    )
    sub = queue.add_subparsers(
        dest="proposal_queue_command",
        metavar="proposal-queue-command",
        required=True,
    )

    status = sub.add_parser("status", help="per-sink pending/reviewed/malformed counts")
    status.add_argument("--sink", choices=_SINK_NAMES, default=None)
    status.add_argument("--json", action="store_true")
    status.set_defaults(func=cmd_proposal_queue_status)

    list_cmd = sub.add_parser("list", help="list proposal-queue entries")
    list_cmd.add_argument("--sink", choices=_SINK_NAMES, default=None)
    list_cmd.add_argument(
        "--pending-only", action="store_true",
        help="only entries that require review and have no review record yet",
    )
    list_cmd.add_argument("--json", action="store_true")
    list_cmd.set_defaults(func=cmd_proposal_queue_list)

    show = sub.add_parser("show", help="print one entry's full artifact JSON")
    show.add_argument("sink", choices=_SINK_NAMES)
    show.add_argument("content_hash")
    show.set_defaults(func=cmd_proposal_queue_show)

    review = sub.add_parser(
        "review",
        help="record that a human reviewed one entry (append-only; no ratification)",
    )
    review.add_argument("sink", choices=_SINK_NAMES)
    review.add_argument("content_hash")
    review.add_argument("--note", default=None, help="optional free-text note")
    review.set_defaults(func=cmd_proposal_queue_review)


__all__ = ["register"]
