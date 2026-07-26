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


def cmd_proposal_queue_ratify(args: argparse.Namespace) -> int:
    """The ratification ceremony (Lane 2) — a reviewed decision becomes artifacts.

    Deliberately a sibling of ``review`` rather than a flag on it: ``review``
    records that a human looked and must stay incapable of ratifying. This
    command is the separate, explicit act, and it still ratifies nothing on its
    own judgement — the operator supplies the edge, the identity, and the
    rationale, and the ceremony only enforces that the result is *routable*.
    """
    from teaching.ratification import (
        RatificationError,
        build_chain_record,
        ratify_chain,
    )

    try:
        record = build_chain_record(
            domain=args.domain,
            subject=args.subject,
            connective=args.connective,
            obj=args.object,
            reviewer=args.reviewer,
            rationale=args.rationale,
            intent=args.intent,
            polarity=args.polarity,
        )
        receipt = ratify_chain(record, dry_run=args.dry_run)
    except RatificationError as exc:
        print(f"REFUSED: {exc}")
        return 1

    if args.json:
        print(json.dumps(receipt.as_dict(), indent=2, sort_keys=True))
        return 0

    verb = "would ratify" if args.dry_run else "RATIFIED"
    print(f"{verb} {receipt.chain.chain_id}: "
          f"{record.subject} {record.connective} {record.object}")
    print(f"  corpus        : {receipt.corpus_id}")
    print(f"  domain chains : {receipt.chains_before} -> {receipt.chains_after}")
    print(f"  {record.operator_family} band  : "
          f"{receipt.family_chains_before} -> {receipt.family_chains_after}")
    if not args.dry_run:
        print(f"  still pending : {', '.join(receipt.pending_stages)}")
        # Wiring the receipt's `ledger_reseal` stage to the verb that performs
        # it. Naming a pending stage without naming its command is how this one
        # stayed unperformed since the ceremony was written.
        if "ledger_reseal" in receipt.pending_stages:
            print(
                "  next          : core proposal-queue reseal curriculum_serve "
                "--dry-run   (the ledger is stale until you do)"
            )
    return 0


def cmd_proposal_queue_reseal(args: argparse.Namespace) -> int:
    """The ``ledger_reseal`` stage of the ceremony — explicit, never automatic.

    ``ratify_chain`` grows the corpus and names this stage in its receipt's
    ``pending_stages``; nothing performed it until now, so a sealed ledger went
    stale the moment curriculum changed. This is the verb a human runs.

    It refuses by default to grant a license. A band can clear θ_SERVE on correct
    NON-COMMITMENTS alone, so "regenerate the artifact" and "make four bands
    authoritative" would otherwise be the same keystroke.
    """
    from teaching.ledger_reseal import ReadyToReseal, apply_reseal, plan_reseal

    try:
        plan = plan_reseal(args.capability)
    except ReadyToReseal as exc:
        print(f"REFUSED: {exc}")
        return 2

    payload: dict[str, object] = {
        "capability": plan.capability,
        "path": str(plan.path),
        "licensed_before": list(plan.licensed_before),
        "licensed_after": list(plan.licensed_after),
        "newly_licensed": list(plan.newly_licensed),
        "revoked": list(plan.revoked),
        "committed": plan.committed,
        "mix": plan.mix,
        "is_housekeeping": plan.is_housekeeping,
        "written": False,
    }
    if not args.json:
        print(f"reseal plan for {plan.capability}:")
        print(f"  artifact      : {plan.path}")
        for band in sorted(plan.committed):
            mix = ", ".join(f"{k}={v}" for k, v in sorted(plan.mix.get(band, {}).items()))
            lic = "SERVE" if band in plan.licensed_after else "     "
            print(f"  {lic} {band:44s} committed={plan.committed[band]:6d}  {mix}")
        print(f"  licensed now  : {len(plan.licensed_before)}")
        print(f"  licensed after: {len(plan.licensed_after)}")
        if plan.newly_licensed:
            print(f"  NEWLY LICENSED: {', '.join(plan.newly_licensed)}")
        if plan.revoked:
            print(f"  revoked       : {', '.join(plan.revoked)}")

    if args.dry_run:
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print("  (dry run — nothing written)")
        return 0

    try:
        path = apply_reseal(plan, allow_new_licenses=args.allow_new_licenses)
    except ReadyToReseal as exc:
        if args.json:
            payload["refused"] = str(exc)
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(f"REFUSED: {exc}")
        return 1

    if args.json:
        payload["written"] = True
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"  SEALED -> {path}")
    return 0


def register(subparsers: argparse._SubParsersAction) -> None:
    from teaching.curriculum_premises import AFFIRMATIVE, POLARITIES

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

    ratify = sub.add_parser(
        "ratify",
        help="ratify one reviewed edge into the domain chain corpus (writes)",
        description=(
            "The ratification ceremony: validate -> append -> CONFIRM the "
            "curriculum loader admits the chain -> receipt. Refuses, and rolls "
            "back, if the appended row would be silently dropped. Does not "
            "write a ledger (bridge rule 1) or queue an arena entry; the "
            "receipt names those stages, and `reseal` performs the first."
        ),
    )
    ratify.add_argument("domain")
    ratify.add_argument("subject")
    ratify.add_argument("connective")
    ratify.add_argument("object")
    ratify.add_argument("--reviewer", required=True, help="who ratified this")
    ratify.add_argument("--rationale", required=True, help="why it is ratified")
    ratify.add_argument("--intent", default="cause")
    ratify.add_argument(
        "--polarity", choices=list(POLARITIES), default=AFFIRMATIVE,
        help=(
            "ADR-0264 R1. `negative` ratifies an explicitly TAUGHT refutation: "
            "the atom compiles under the sentential-negation prefix and the "
            "question answers `refuted`, which is different from an absent edge "
            "(UNKNOWN, the open-world reading). Must reuse the AFFIRMATIVE "
            "connective (R3) — `causes`, never `does not cause` — or it mints a "
            "different atom and silently fails to refute. Refused if the atom is "
            "already taught with the other polarity (R4)."
        ),
    )
    ratify.add_argument("--dry-run", action="store_true",
                        help="report the band delta without writing")
    ratify.add_argument("--json", action="store_true")
    ratify.set_defaults(func=cmd_proposal_queue_ratify)

    from teaching.ledger_reseal import resealable_capabilities

    reseal = sub.add_parser(
        "reseal",
        help="re-run sealed practice and rewrite a capability's committed ledger",
        description=(
            "The `ledger_reseal` stage `ratify_chain` names but never performs. "
            "Ratifying a chain grows the corpus without re-running practice, so "
            "the ledger the serving gate reads goes stale. This rebuilds it from "
            "sealed practice. REFUSES by default if the reseal would newly "
            "license a band: reliability is commitment precision, so a band can "
            "clear theta_SERVE on correct NON-COMMITMENTS alone, and granting a "
            "serving license is a ratification rather than housekeeping."
        ),
    )
    reseal.add_argument("capability", choices=resealable_capabilities())
    reseal.add_argument(
        "--dry-run", action="store_true",
        help="report the license delta without writing",
    )
    reseal.add_argument(
        "--allow-new-licenses", action="store_true",
        help="authorize bands that would become newly licensed (a RATIFICATION)",
    )
    reseal.add_argument("--json", action="store_true")
    reseal.set_defaults(func=cmd_proposal_queue_reseal)


__all__ = ["register"]
