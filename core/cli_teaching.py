"""Extracted commands."""

from __future__ import annotations
import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from core.cli import _contemplation_runs_dir
from core.cli import _die, _REPO_ROOT


def cmd_teaching_audit(args: argparse.Namespace) -> int:
    """ADR-0055 Phase A — surface load decisions on the reviewed teaching corpus.

    Re-parses the cognition-chains JSONL with the same gates as the
    runtime loader, but keeps drop reasons so silent shrinkage (pack
    skew, supersession, schema drift) is inspectable.  Pure read.
    """
    from teaching.audit import audit_corpus

    report = audit_corpus()
    if args.json:
        print(
            json.dumps(report.as_dict(), ensure_ascii=False, indent=2, sort_keys=True)
        )
        return 0 if not report.dropped else 1
    print(f"corpus_id      : {report.corpus_id}")
    print(f"corpus_path    : {report.corpus_path}")
    print(f"lines_on_disk  : {report.lines_on_disk}")
    print(f"lines_loaded   : {report.lines_loaded}")
    if report.dropped:
        print(f"\ndropped ({len(report.dropped)}):")
        for d in report.dropped:
            cid = d.chain_id or "<unknown>"
            print(f"  L{d.line_no:>4}  {cid:<40}  {d.reason}")
        return 1
    return 0


def cmd_teaching_gaps(args: argparse.Namespace) -> int:
    """Phase 1.1 — rank (subject, intent) cells the runtime would have
    grounded but couldn't, aggregated from emitted DiscoveryCandidates.

    Reads JSONL files written by
    :class:`teaching.discovery_sink.DiscoveryMonthlyFileSink` under
    *root* (default ``teaching/discovery_log``) and emits a ranked
    table of cells ordered by emission count.

    Pure read — never mutates the sink.
    """
    from teaching.gaps import _DEFAULT_ROOT, aggregate_gaps

    root = Path(args.root) if args.root else _DEFAULT_ROOT
    try:
        rows = aggregate_gaps(
            root=root,
            since=args.since,
            sample_limit=max(1, int(args.sample_limit)),
        )
    except ValueError as exc:
        _die(str(exc), code=2)

    if args.top is not None and args.top > 0:
        rows = rows[: args.top]

    if args.json:
        payload = {
            "root": str(root) if root is not None else None,
            "since": args.since,
            "total_cells": len(rows),
            "gaps": [g.as_dict() for g in rows],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if rows else 1

    if not rows:
        print("No discovery candidates found.")
        if root is not None and not root.exists():
            print(f"  (root path does not exist: {root})")
        return 1

    print(
        f"{'rank':>4}  {'subject':<24}{'intent':<14}{'count':>6}  {'clean':>6}  months"
    )
    print("-" * 80)
    for i, gap in enumerate(rows, 1):
        months = ",".join(gap.months_seen) if gap.months_seen else "—"
        print(
            f"{i:>4}  {gap.subject[:24]:<24}{gap.intent[:14]:<14}"
            f"{gap.count:>6}  {gap.boundary_clean_count:>6}  {months}"
        )
    return 0


def cmd_teaching_oov_gaps(args: argparse.Namespace) -> int:
    """Phase 2.3 — rank OOV tokens emitted by the runtime's
    OOV "teach me" surface.

    Reads JSONL files written by
    :class:`teaching.oov_sink.OOVMonthlyFileSink` under *root*
    (default ``teaching/oov_log``) and emits a ranked table of
    tokens ordered by emission count.

    Pure read — never mutates the sink.
    """
    from teaching.oov_gaps import _DEFAULT_ROOT, aggregate_oov_gaps

    root = Path(args.root) if args.root else _DEFAULT_ROOT
    try:
        rows = aggregate_oov_gaps(
            root=root,
            since=args.since,
            sample_limit=max(1, int(args.sample_limit)),
        )
    except ValueError as exc:
        _die(str(exc), code=2)

    if args.top is not None and args.top > 0:
        rows = rows[: args.top]

    if args.json:
        payload = {
            "root": str(root),
            "since": args.since,
            "total_tokens": len(rows),
            "oov_gaps": [g.as_dict() for g in rows],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if rows else 1

    if not rows:
        print("No OOV candidates found.")
        if root is not None and not root.exists():
            print(f"  (root path does not exist: {root})")
        return 1

    print(f"{'rank':>4}  {'token':<28}{'count':>6}  {'clean':>6}  intents")
    print("-" * 80)
    for i, gap in enumerate(rows, 1):
        intents = ",".join(gap.intents) if gap.intents else "—"
        print(
            f"{i:>4}  {gap.token[:28]:<28}{gap.count:>6}  "
            f"{gap.boundary_clean_count:>6}  {intents}"
        )
    return 0


def cmd_teaching_oov_queue(args: argparse.Namespace) -> int:
    """Phase 2.3 — show the auto-promoted OOV-token queue.

    Same shape as ``core teaching queue`` but for vocabulary gaps:
    tokens whose boundary-clean emission count meets ``--threshold``
    are surfaced as PackMutationProposal candidates that an operator
    can author via the reviewed ADR-0027 path.

    Never auto-mutates a pack — operator-visible signal only.
    """
    from teaching.oov_gaps import _DEFAULT_ROOT, aggregate_oov_gaps
    from teaching.oov_promotion import promote_oov_gaps

    root = Path(args.root) if args.root else _DEFAULT_ROOT
    try:
        gaps = aggregate_oov_gaps(root=root, since=args.since, sample_limit=5)
    except ValueError as exc:
        _die(str(exc), code=2)

    if args.threshold < 1:
        _die(f"--threshold must be >= 1 (got {args.threshold})", code=2)

    promoted = promote_oov_gaps(
        gaps,
        threshold=args.threshold,
        include_tainted=args.include_tainted,
    )

    if args.json:
        payload = {
            "root": str(root),
            "since": args.since,
            "threshold": args.threshold,
            "include_tainted": args.include_tainted,
            "total_promoted": len(promoted),
            "queue": [p.as_dict() for p in promoted],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if promoted else 1

    if not promoted:
        print(f"No OOV tokens met threshold {args.threshold}.")
        return 1

    print(f"{'rank':>4}  {'queue_id':<40}{'count':>6}  {'clean':>6}  intents")
    print("-" * 96)
    for i, p in enumerate(promoted, 1):
        intents = ",".join(p.intents) if p.intents else "—"
        print(
            f"{i:>4}  {p.queue_id[:40]:<40}{p.count:>6}  "
            f"{p.boundary_clean_count:>6}  {intents}"
        )
    print()
    print(
        f"Add each token to one of: {', '.join(promoted[0].suggested_packs)}.  "
        f"Use a reviewed PackMutationProposal — never auto-applies."
    )
    return 0


def cmd_teaching_queue(args: argparse.Namespace) -> int:
    """Phase 1.2 — show the auto-promoted gap queue.

    Reads the discovery sink (same path as ``core teaching gaps``),
    aggregates by cell, and emits cells whose boundary-clean
    emission count meets ``--threshold``.

    Boundary-tainted emissions (refusal/hedge fired during the
    contributing turn) are excluded by default; ``--include-tainted``
    counts every emission toward the threshold.  Operators reach for
    that flag deliberately, not by accident.
    """
    from teaching.gaps import _DEFAULT_ROOT, aggregate_gaps
    from teaching.promotion import promote_gaps

    root = Path(args.root) if args.root else _DEFAULT_ROOT
    try:
        gaps = aggregate_gaps(
            root=root,
            since=args.since,
            sample_limit=5,
        )
    except ValueError as exc:
        _die(str(exc), code=2)

    if args.threshold < 1:
        _die(f"--threshold must be >= 1 (got {args.threshold})", code=2)

    promoted = promote_gaps(
        gaps,
        threshold=args.threshold,
        include_tainted=args.include_tainted,
    )

    if args.json:
        payload = {
            "root": str(root),
            "since": args.since,
            "threshold": args.threshold,
            "include_tainted": args.include_tainted,
            "total_promoted": len(promoted),
            "queue": [p.as_dict() for p in promoted],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if promoted else 1

    if not promoted:
        print(f"No cells met threshold {args.threshold}.")
        return 1

    print(f"{'rank':>4}  {'queue_id':<48}{'count':>6}  {'clean':>6}  months")
    print("-" * 96)
    for i, p in enumerate(promoted, 1):
        months = ",".join(p.months_seen) if p.months_seen else "—"
        print(
            f"{i:>4}  {p.queue_id[:48]:<48}{p.count:>6}  {p.boundary_clean_count:>6}  {months}"
        )
    print()
    print(
        "Author chains with: core teaching propose <candidate-jsonl> "
        "(or hand-author + supersede)."
    )
    return 0


def cmd_teaching_hitl_queue_list(args: argparse.Namespace) -> int:
    """List queue items in the human-in-the-loop review queue."""
    from teaching.proposals import DEFAULT_PROPOSAL_LOG_PATH, ProposalLog
    from teaching.queue import derive_queue

    log_path = Path(args.log_path) if args.log_path else DEFAULT_PROPOSAL_LOG_PATH
    runs_dir = _contemplation_runs_dir(args.contemplation_runs_dir)

    log = ProposalLog(log_path)
    if not log.path.exists():
        return 0

    items = derive_queue(log, contemplation_runs_dir=runs_dir)

    if args.state and args.state != "all":
        items = tuple(item for item in items if item.state == args.state)

    if args.json:
        import dataclasses

        payload = [dataclasses.asdict(item) for item in items]
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return 0

    if not items:
        return 0

    header = ("proposal_id", "source_kind", "state", "age", "replay")
    rows = []
    for item in items:
        if item.replay_evidence is None:
            replay_status = "?"
        elif item.replay_evidence.get("replay_equivalent") is True:
            replay_status = "ok"
        elif item.replay_evidence.get("replay_equivalent") is False:
            replay_status = "regressed"
        else:
            replay_status = "?"

        rows.append(
            (
                item.proposal_id[:12],
                item.source_kind,
                item.state,
                str(item.age_proposals),
                replay_status,
            )
        )

    col_widths = [len(h) for h in header]
    for row in rows:
        for idx, val in enumerate(row):
            col_widths[idx] = max(col_widths[idx], len(val))

    header_str = "  ".join(f"{h:<{col_widths[idx]}}" for idx, h in enumerate(header))
    print(header_str)
    print("  ".join("-" * w for w in col_widths))
    for row in rows:
        row_str = "  ".join(f"{val:<{col_widths[idx]}}" for idx, val in enumerate(row))
        print(row_str)

    return 0


def cmd_teaching_hitl_queue_show(args: argparse.Namespace) -> int:
    """Show details of a specific queue item in the human-in-the-loop review queue."""
    from teaching.proposals import DEFAULT_PROPOSAL_LOG_PATH, ProposalLog
    from teaching.queue import derive_queue

    log_path = Path(args.log_path) if args.log_path else DEFAULT_PROPOSAL_LOG_PATH
    runs_dir = _contemplation_runs_dir(args.contemplation_runs_dir)

    log = ProposalLog(log_path)
    if not log.path.exists():
        _die(f"no proposal log at {log.path}", code=1)

    items = derive_queue(log, contemplation_runs_dir=runs_dir)

    # 1. Search for exact match
    exact_matches = [item for item in items if item.proposal_id == args.proposal_id]
    if len(exact_matches) == 1:
        item = exact_matches[0]
    else:
        # 2. Search for prefix match
        prefix_matches = [
            item for item in items if item.proposal_id.startswith(args.proposal_id)
        ]
        if len(prefix_matches) == 1:
            item = prefix_matches[0]
        elif len(prefix_matches) == 0:
            _die(
                f"proposal_id prefix {args.proposal_id!r} matches zero queue items",
                code=1,
            )
        else:
            _die(
                f"proposal_id prefix {args.proposal_id!r} is ambiguous (matches multiple items)",
                code=1,
            )

    if args.json:
        import dataclasses

        print(
            json.dumps(
                dataclasses.asdict(item), ensure_ascii=False, indent=2, sort_keys=True
            )
        )
        return 0

    print(f"Proposal ID: {item.proposal_id}")
    print(f"Source Kind: {item.source_kind}")
    print(f"Source ID  : {item.source_id or '—'}")
    print(f"State      : {item.state}")
    print(f"Age        : {item.age_proposals}")

    if item.replay_evidence is None:
        replay_status = "?"
    elif item.replay_evidence.get("replay_equivalent") is True:
        replay_status = "ok"
    elif item.replay_evidence.get("replay_equivalent") is False:
        replay_status = "regressed"
    else:
        replay_status = "?"
    print(f"Replay     : {replay_status}")
    print(f"Report Path: {item.contemplation_report_path or '—'}")
    print()
    print("Proposed Chain:")
    chain = item.proposed_chain or {}
    print(f"  subject   : {chain.get('subject', '—')}")
    print(f"  intent    : {chain.get('intent', '—')}")
    print(f"  connective: {chain.get('connective', '—')}")
    print(f"  object    : {chain.get('object', '—')}")
    print()
    print("Review History:")
    if item.review_history:
        for ev in item.review_history:
            note = ev.get("note", "")
            to_state = ev.get("to", "")
            review_date = ev.get("review_date", "")
            actor = ev.get("actor", "")
            print(
                f"  - [{review_date or '—'}] transitioned to {to_state} by {actor or '—'}"
            )
            if note:
                print(f"    Note: {note}")
    else:
        print("  (no review history)")
    print()
    print("ADR References:")
    print("  - Queue contract: docs/adr/ADR-0161-hitl-async-queue.md")
    print(
        "  - Proposal/review state machine: docs/adr/ADR-0057-teaching-chain-proposal-review.md"
    )

    return 0


def cmd_teaching_propose(args: argparse.Namespace) -> int:
    """ADR-0057 Phase C2 — build a proposal from an enriched candidate JSONL."""
    from teaching.proposals import (
        ProposalError,
        ProposalLog,
        RefusedAsDependent,
        RefusedAsDuplicate,
        RefusedAtCapacity,
        propose_from_candidate,
    )

    candidate = _load_candidate_jsonl(args.candidate_path)
    log_path = Path(args.log) if args.log else None
    log = ProposalLog(log_path)
    try:
        proposal = propose_from_candidate(
            candidate,
            log=log,
            allow_evaluative=args.allow_evaluative,
        )
    except ProposalError as exc:
        _die(f"ineligible: {exc}", code=1)

    if isinstance(proposal, RefusedAtCapacity):
        try:
            rel_path = proposal.report_path.relative_to(_REPO_ROOT)
        except ValueError:
            try:
                rel_path = proposal.report_path.relative_to(Path.cwd())
            except ValueError:
                rel_path = proposal.report_path
        print(f"queue_full: pending={proposal.pending_count}, cap={proposal.cap}")
        print("candidates_skipped: 1")
        print(f"report_written: {rel_path}")
        return 1

    if isinstance(proposal, RefusedAsDuplicate):
        print(
            f"duplicate: proposal_id={proposal.proposal_id} existing_state={proposal.existing_state}"
        )
        return 1

    if isinstance(proposal, RefusedAsDependent):
        print(f"dependent_on_pending: dependent_on={list(proposal.dependent_on)}")
        print(f"overlapping_lemmas={list(proposal.overlapping_lemmas)}")
        return 1

    rec = log.find(proposal.proposal_id)
    print(f"proposal_id    : {proposal.proposal_id}")
    print(f"state          : {rec['state']}")
    if rec.get("replay_evidence"):
        ev = rec["replay_evidence"]
        print(f"replay_equivalent: {ev['replay_equivalent']}")
        if ev.get("regressed_metrics"):
            print(f"regressed       : {', '.join(ev['regressed_metrics'])}")
    if rec.get("operator_note"):
        print(f"note           : {rec['operator_note']}")
    return 0 if rec["state"] in ("pending", "accepted") else 1


def cmd_teaching_propose_from_exemplars(args: argparse.Namespace) -> int:
    """ADR-0163 Phase C — propose recognizers from admissibility exemplar corpora.

    Loads one or more Phase B exemplar JSONLs, runs the contemplation
    synthesis to produce a :class:`DiscoveryCandidate` per corpus, and
    routes each candidate through :func:`teaching.proposals.propose_from_candidate`
    with the admissibility replay gate substituted for the cognition-only
    replay-equivalence gate.  Proposals land as ``pending``; operator
    ratifies via ``core teaching review`` (existing path).
    """
    from datetime import datetime, timezone

    from teaching.contemplation import contemplate_exemplar_corpus
    from teaching.exemplar_ingest import (
        ExemplarIngestError,
        list_corpora,
        load_exemplar_corpus,
    )
    from teaching.proposals import (
        DEFAULT_PROPOSAL_LOG_PATH,
        ProposalError,
        ProposalLog,
        propose_from_candidate,
    )
    from teaching.replay import run_admissibility_replay_gate
    from teaching.source import ProposalSource

    review_date = args.review_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")

    log_path = Path(args.log) if args.log else DEFAULT_PROPOSAL_LOG_PATH
    log = ProposalLog(log_path)

    # Resolve corpora: --all loads every JSONL; otherwise the single path.
    try:
        if args.all:
            root = Path(args.exemplar_path) if args.exemplar_path else None
            corpora = list_corpora(root)
        else:
            if not args.exemplar_path:
                _die(
                    "exemplar_path is required unless --all is passed",
                    code=2,
                )
            corpora = (load_exemplar_corpus(Path(args.exemplar_path)),)
    except ExemplarIngestError as exc:
        _die(f"exemplar ingest failed: {exc}", code=1)

    # Resolve current git revision once for the ProposalSource stamp.
    from teaching.proposals import _current_revision

    revision = _current_revision()

    results: list[dict[str, Any]] = []
    for corpus in corpora:
        candidate = contemplate_exemplar_corpus(corpus)
        source = ProposalSource(
            kind="exemplar_corpus",
            source_id=corpus.corpus_digest,
            emitted_at_revision=revision,
        )

        # Bind active_corpus_path=None so the gate reads the live corpus.
        def _gate(chain: dict[str, Any]) -> Any:
            return run_admissibility_replay_gate(
                candidate.proposed_chain.get("recognizer_spec"),
            )

        try:
            proposal = propose_from_candidate(
                candidate,
                log=log,
                run_replay=_gate,
                source=source,
            )
        except ProposalError as exc:
            _die(
                f"ineligible candidate for {corpus.shape_category.value}: {exc}",
                code=1,
            )

        from teaching.proposals import (
            RefusedAsDependent,
            RefusedAsDuplicate,
            RefusedAtCapacity,
        )

        if isinstance(proposal, RefusedAtCapacity):
            try:
                rel_path = proposal.report_path.relative_to(_REPO_ROOT)
            except ValueError:
                try:
                    rel_path = proposal.report_path.relative_to(Path.cwd())
                except ValueError:
                    rel_path = proposal.report_path
            print(f"queue_full: pending={proposal.pending_count}, cap={proposal.cap}")
            print("candidates_skipped: 1")
            print(f"report_written: {rel_path}")
            return 1

        if isinstance(proposal, RefusedAsDuplicate):
            print(
                f"duplicate: proposal_id={proposal.proposal_id} existing_state={proposal.existing_state}"
            )
            return 1

        if isinstance(proposal, RefusedAsDependent):
            print(f"dependent_on_pending: dependent_on={list(proposal.dependent_on)}")
            print(f"overlapping_lemmas={list(proposal.overlapping_lemmas)}")
            return 1

        rec = log.find(proposal.proposal_id)
        result = {
            "shape_category": corpus.shape_category.value,
            "corpus_path": str(corpus.path),
            "corpus_digest": corpus.corpus_digest,
            "proposal_id": proposal.proposal_id,
            "review_date": review_date,
            "state": rec["state"] if rec else "unknown",
        }
        replay = (rec or {}).get("replay_evidence") or {}
        if replay:
            result["replay_equivalent"] = bool(replay.get("replay_equivalent"))
            result["regressed_metrics"] = list(replay.get("regressed_metrics") or ())
            result["wrong_count_delta"] = int(replay.get("wrong_count_delta", 0))
        results.append(result)

    if args.json:
        print(json.dumps({"proposals": results}, indent=2, sort_keys=True))
    else:
        for r in results:
            print(f"shape_category   : {r['shape_category']}")
            print(f"corpus_path      : {r['corpus_path']}")
            print(f"corpus_digest    : {r['corpus_digest'][:16]}...")
            print(f"proposal_id      : {r['proposal_id']}")
            print(f"state            : {r['state']}")
            if "replay_equivalent" in r:
                print(f"replay_equivalent: {r['replay_equivalent']}")
                if r.get("regressed_metrics"):
                    print(f"regressed_metrics: {', '.join(r['regressed_metrics'])}")
                print(f"wrong_count_delta: {r['wrong_count_delta']}")
            print(f"review_date      : {r['review_date']}")
            print("--")
    # Exit nonzero if any proposal auto-rejected.
    if any(r["state"] != "pending" for r in results):
        return 1
    return 0


def cmd_teaching_propose_miner(args: argparse.Namespace) -> int:
    """W-019: build PackMutationProposals from miner ContemplationFinding JSONL."""
    from teaching.from_miner import MinerProposalError, from_findings

    findings = _load_findings_jsonl(args.findings)
    if not findings:
        _die(f"no findings in {args.findings}", code=1)

    revision = args.revision or _current_git_revision()
    try:
        batch = from_findings(
            findings,
            miner_id=args.miner_id,
            emitted_at_revision=revision,
        )
    except MinerProposalError as exc:
        _die(f"batch construction failed: {exc}", code=1)

    out_path = Path(args.out) if args.out else None
    _write_miner_curriculum_batch(batch.proposals, batch.rejections, out_path)
    return 0 if batch.proposals else 1


def cmd_teaching_propose_curriculum(args: argparse.Namespace) -> int:
    """W-019: build PackMutationProposals from curriculum ContemplationFinding JSONL."""
    from teaching.from_curriculum import CurriculumProposalError, from_findings

    findings = _load_findings_jsonl(args.findings)
    if not findings:
        _die(f"no findings in {args.findings}", code=1)

    revision = args.revision or _current_git_revision()
    try:
        batch = from_findings(
            findings,
            curriculum_id=args.curriculum_id,
            emitted_at_revision=revision,
        )
    except CurriculumProposalError as exc:
        _die(f"batch construction failed: {exc}", code=1)

    out_path = Path(args.out) if args.out else None
    _write_miner_curriculum_batch(batch.proposals, batch.rejections, out_path)
    return 0 if batch.proposals else 1


def cmd_teaching_proposals(args: argparse.Namespace) -> int:
    from teaching.proposals import ProposalLog

    log_path = Path(args.log) if args.log else None
    log = ProposalLog(log_path)
    state = log.current_state()
    if args.state:
        state = {pid: rec for pid, rec in state.items() if rec["state"] == args.state}
    if args.json:
        print(json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if not state:
        print("(no proposals)")
        return 0
    for pid, rec in state.items():
        chain = rec["proposal"]["proposed_chain"]
        print(
            f"{pid}  {rec['state']:<10}  "
            f"{chain.get('subject')} {chain.get('connective')} {chain.get('object')} "
            f"({chain.get('intent')})"
        )
    return 0


def cmd_teaching_review(args: argparse.Namespace) -> int:
    from teaching.proposals import (
        ProposalError,
        ProposalLog,
        accept_proposal,
        reject_proposal,
        withdraw_proposal,
    )

    log_path = Path(args.log) if args.log else None
    log = ProposalLog(log_path)
    try:
        if args.accept:
            if not args.review_date:
                _die("--accept requires --review-date YYYY-MM-DD", code=2)
            from chat.teaching_grounding import _CORPUS_PATH

            chain_id = accept_proposal(
                args.proposal_id,
                log=log,
                corpus_path=_CORPUS_PATH,
                review_date=args.review_date,
                operator_note=args.note,
            )
            print(f"accepted; appended chain_id = {chain_id}")
        elif args.reject:
            reject_proposal(args.proposal_id, log=log, operator_note=args.note)
            print(f"{args.proposal_id} rejected")
        elif args.withdraw:
            withdraw_proposal(args.proposal_id, log=log, operator_note=args.note)
            print(f"{args.proposal_id} withdrawn")
    except ProposalError as exc:
        _die(str(exc), code=1)
    return 0


def cmd_teaching_supersessions(args: argparse.Namespace) -> int:
    """Pair each retired chain with its active replacement.

    Derived view over ``teaching.audit.audit_corpus`` — pure, read-only.
    Surfaces orphan supersessions (retired chain with no live replacement
    carrying the matching ``superseded_by``) so silent corpus drift is
    inspectable.
    """
    from teaching.audit import audit_corpus, supersession_history

    report = audit_corpus()
    records = supersession_history(report)

    if args.json:
        print(
            json.dumps(
                {
                    "corpus_id": report.corpus_id,
                    "corpus_path": report.corpus_path,
                    "supersessions": [r.as_dict() for r in records],
                },
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    if not records:
        print("(no supersessions)")
        return 0

    has_orphan = False
    for r in records:
        if r.replacement is None:
            has_orphan = True
            print(
                f"retired: {r.retired_chain_id}  (line {r.retired_line_no})\n"
                f"  replaced_by: <ORPHAN — no live entry carries this superseded_by>"
            )
            continue
        rep = r.replacement
        prov = rep.provenance.raw or "(unknown)"
        print(
            f"retired: {r.retired_chain_id}  (line {r.retired_line_no})\n"
            f"  replaced_by: {rep.chain_id}  (line {rep.line_no})\n"
            f"    {rep.subject} {rep.connective} {rep.object}  [{rep.intent}]\n"
            f"    provenance: {prov}"
        )
    return 1 if has_orphan else 0


def cmd_teaching_supersede(args: argparse.Namespace) -> int:
    """ADR-0057 follow-up — retire an active corpus chain by appending
    a new chain marked ``superseded_by``.

    Distinct from accept-a-proposal (no replay gate; this is a direct
    operator action).  Validates pack-consistency / intent / completeness
    before the append, and rolls back the corpus byte-identically on any
    post-audit failure.
    """
    from chat.teaching_grounding import _CORPUS_PATH
    from teaching.supersede import SupersessionError, supersede_chain

    cross_pack = bool(getattr(args, "cross_pack", False))
    subj_pack = (getattr(args, "subject_pack_id", "") or "").strip()
    obj_pack = (getattr(args, "object_pack_id", "") or "").strip()

    if cross_pack or subj_pack or obj_pack:
        # ADR-0067 — cross-pack supersede.  Both pack ids are required
        # when any cross-pack flag is set.
        if not subj_pack or not obj_pack:
            _die(
                "cross-pack supersede requires --subject-pack-id and --object-pack-id",
                code=2,
            )
        from teaching.cross_pack_supersede import supersede_cross_pack_chain

        try:
            new_chain_id = supersede_cross_pack_chain(
                old_chain_id=args.old_chain_id,
                subject=args.subject,
                intent=args.intent,
                connective=args.connective,
                object_=args.object,
                subject_pack_id=subj_pack,
                object_pack_id=obj_pack,
                review_date=args.review_date,
                new_chain_id=args.new_chain_id,
            )
        except SupersessionError as exc:
            _die(str(exc), code=1)
    else:
        try:
            new_chain_id = supersede_chain(
                old_chain_id=args.old_chain_id,
                subject=args.subject,
                intent=args.intent,
                connective=args.connective,
                object_=args.object,
                review_date=args.review_date,
                corpus_path=_CORPUS_PATH,
                operator_note=args.note,
                new_chain_id=args.new_chain_id,
            )
        except SupersessionError as exc:
            _die(str(exc), code=1)

    print(f"superseded     : {args.old_chain_id}")
    print(f"new chain_id   : {new_chain_id}")
    print(f"review_date    : {args.review_date}")
    if args.note:
        print(f"note           : {args.note}")
    return 0


def cmd_teaching_compile_pack(args: argparse.Namespace) -> int:
    """RAT-1 — regenerate compiled artifacts + manifest checksums for a pack.

    Reads ``{pack}/frames/*.jsonl`` and ``{pack}/compositions/*.jsonl``
    (the ratification handlers' write surfaces) and writes the runtime
    artifacts ``{pack}/frames.jsonl`` + ``{pack}/compositions.jsonl``
    plus the matching manifest checksum fields. Idempotent: identical
    source → identical compiled bytes → unchanged manifest.

    Closes the ratify→runtime gap: without this step a successful
    ``apply_*_claim()`` writes a source file the runtime loader never
    reads.
    """
    from pathlib import Path

    from language_packs.compile_pack import compile_pack

    pack_root = (
        Path(args.pack)
        if args.pack
        else (
            Path(__file__).resolve().parent.parent
            / "language_packs"
            / "data"
            / "en_core_math_v1"
        )
    )
    receipt = compile_pack(pack_root.resolve())

    if args.json:
        print(
            json.dumps(
                {
                    "pack_path": str(receipt.pack_path),
                    "frame_checksum": receipt.frame_checksum,
                    "composition_checksum": receipt.composition_checksum,
                    "frame_bytes_written": receipt.frame_bytes_written,
                    "composition_bytes_written": receipt.composition_bytes_written,
                    "manifest_updated": receipt.manifest_updated,
                },
                indent=2,
                sort_keys=True,
            )
        )
    else:
        print(f"pack                 : {receipt.pack_path}")
        print(f"frame_checksum       : {receipt.frame_checksum[:24]}...")
        print(f"composition_checksum : {receipt.composition_checksum[:24]}...")
        print(f"frame bytes          : {receipt.frame_bytes_written}")
        print(f"composition bytes    : {receipt.composition_bytes_written}")
        print(f"manifest_updated     : {receipt.manifest_updated}")
    return 0


def cmd_teaching_seed_recognizer(args: argparse.Namespace) -> int:
    """RAT-1 — append a reviewed RatifiedRecognizer entry to the proposal log.

    Operator-explicit seeding for new ``anchor_kind`` values that the
    contemplation pipeline hasn't yet produced via exemplar harvest.
    Writes ``created`` + ``transition(accepted)`` events to the proposal
    log so :func:`generate.recognizer_registry.load_ratified_registry`
    picks it up on next load.

    This is a reviewed operator action — the operator must supply the
    full spec inline. There is no inference, no auto-fill from
    exemplars, no fallback. Every call appends one proposal pair.
    """
    import datetime
    import hashlib
    from pathlib import Path

    from teaching.proposals import ProposalLog

    log_path = Path(args.log) if args.log else None
    log = ProposalLog(log_path)

    review_date = args.review_date or datetime.date.today().isoformat()

    canonical_pattern: dict[str, Any] = {
        "anchor_kind": args.anchor_kind,
        "shape_category": args.shape_category,
        "outcome": "admissible",
    }
    if args.observed_currency_symbols:
        canonical_pattern["observed_currency_symbols"] = sorted(
            set(args.observed_currency_symbols)
        )
    if args.observed_per_units:
        canonical_pattern["observed_per_units"] = sorted(set(args.observed_per_units))
    if args.observed_units:
        canonical_pattern["observed_units"] = sorted(set(args.observed_units))
    if args.anchor_count_min is not None:
        canonical_pattern["anchor_count_min"] = args.anchor_count_min
    if args.anchor_count_max is not None:
        canonical_pattern["anchor_count_max"] = args.anchor_count_max
    if args.graph_intent:
        canonical_pattern["graph_intent"] = args.graph_intent
    if getattr(args, "extract_values", False):
        canonical_pattern["extract_values"] = True

    recognizer_spec = {
        "shape_category": args.shape_category,
        "canonical_pattern": canonical_pattern,
        "exemplar_count": 0,
        "exemplar_digest": "",
        "coverage": {},
    }

    # Build a deterministic proposal_id from the canonical pattern bytes.
    spec_bytes = json.dumps(
        canonical_pattern, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    spec_digest = hashlib.sha256(spec_bytes).hexdigest()
    proposal_id = f"rat1-seed-{spec_digest[:16]}"
    recognizer_spec["exemplar_digest"] = spec_digest

    proposal_payload = {
        "proposal_id": proposal_id,
        "polarity": "affirms",
        "claim_domain": "factual",
        "evidence": [],
        "proposed_chain": {
            "subject": args.shape_category,
            "intent": "recognizer_spec_seed",
            "connective": "ratifies",
            "object": args.anchor_kind,
            "recognizer_spec": recognizer_spec,
        },
        "source": {
            "kind": "exemplar_corpus",
            "source_id": spec_digest,
            "emitted_at_revision": "rat1-cli-seed",
        },
    }

    # Append created + transition events directly via the log's writer.
    log._append({"event": "created", "proposal": proposal_payload})
    log._append(
        {
            "event": "transition",
            "proposal_id": proposal_id,
            "to": "accepted",
            "note": args.note or "RAT-1 CLI seed",
            "review_date": review_date,
        }
    )

    print(f"seeded proposal_id   : {proposal_id}")
    print(f"shape_category       : {args.shape_category}")
    print(f"anchor_kind          : {args.anchor_kind}")
    print(f"log_path             : {log.path}")
    print(f"review_date          : {review_date}")
    return 0


def cmd_teaching_coverage(args: argparse.Namespace) -> int:
    """Brief D — per-shape admission histogram with deltas vs committed baseline.

    Reads (or runs, if ``--run``) the lane's ``report.json`` and emits
    a clean histogram of counts + refusal taxonomy. Pure read by default.
    Useful for measuring the effect of ratifications + matcher
    extensions without re-eyeballing report.json.
    """
    from pathlib import Path

    from teaching.coverage import (
        build_coverage_report,
        fetch_committed_baseline,
    )

    lane = args.lane or "gsm8k_math"
    split = args.split or "train_sample"
    version = args.version or "v1"

    # Validate inputs against a strict whitelist before any path
    # construction or subprocess invocation. The runner module name is
    # built from these tokens (``f"evals.{lane}.{split}.{version}.runner"``)
    # and passed to ``python -m``. Python's module loader would reject
    # most malicious payloads, but a strict whitelist is the defense-in-
    # depth response to the Sourcery security advisory: reject
    # everything except ``[a-z0-9_]+``.
    import re as _re

    _safe_token_re = _re.compile(r"^[a-z0-9_]+$")
    for label, value in (("lane", lane), ("split", split), ("version", version)):
        if not _safe_token_re.match(value):
            print(
                f"ERROR: {label}={value!r} must match ^[a-z0-9_]+$",
                file=sys.stderr,
            )
            return 1

    repo_root = Path(__file__).resolve().parent.parent
    lane_dir = repo_root / "evals" / lane / split / version
    if not lane_dir.is_dir():
        print(f"ERROR: lane directory not found: {lane_dir}", file=sys.stderr)
        return 1
    report_path = lane_dir / "report.json"

    if args.run or not report_path.exists():
        import subprocess

        runner_module = f"evals.{lane}.{split}.{version}.runner"
        runner_args = [sys.executable, "-m", runner_module]
        try:
            subprocess.run(
                runner_args,
                cwd=repo_root,
                check=True,
                capture_output=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            print(f"ERROR: runner failed: {exc}", file=sys.stderr)
            return 1

    baseline_path = None
    if args.delta:
        report_relpath = f"evals/{lane}/{split}/{version}/report.json"
        baseline_path = fetch_committed_baseline(report_relpath, repo_root)

    report = build_coverage_report(
        report_path,
        lane=lane,
        split=split,
        version=version,
        baseline_path=baseline_path,
    )

    if args.json:
        print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
    else:
        print(f"Lane: {report.lane}/{report.split}/{report.version}")
        if report.delta:
            print(
                f"Counts: correct={report.counts.correct} "
                f"refused={report.counts.refused} "
                f"wrong={report.counts.wrong}  "
                f"(Δ from HEAD: correct={report.delta['correct']:+d} "
                f"refused={report.delta['refused']:+d} "
                f"wrong={report.delta['wrong']:+d})"
            )
        else:
            print(
                f"Counts: correct={report.counts.correct} "
                f"refused={report.counts.refused} "
                f"wrong={report.counts.wrong}"
            )
        print()
        if report.refusal_taxonomy:
            print("Refusal taxonomy:")
            for bucket, n in report.refusal_taxonomy.items():
                print(f"  {n:>3}  {bucket}")
            print()
        wrong_ok = "✓" if report.counts.wrong == 0 else "✗"
        hazard = report.case_0050_verdict
        print(f"Wrong=0: {wrong_ok}")
        if hazard is not None:
            hazard_ok = "✓" if hazard == "refused" else "✗"
            print(f"Case 0050 hazard pin: {hazard} {hazard_ok}")
    return 0


def cmd_teaching_refusal_taxonomy(args: argparse.Namespace) -> int:
    """ADR-0163 Phase A — categorise refused statements by shape.

    Read-only.  Reads a JSONL of refused cases (defaults to the v1
    refusal_taxonomy case set) and emits a histogram of shape categories.
    Per ADR-0163, the categorizer is rules-only: no LLM call, no
    embedding, no learned model.  --save writes the report to
    ``evals/refusal_taxonomy/v1/report.json``.
    """
    import json
    from pathlib import Path

    from evals.framework import load_cases
    from evals.refusal_taxonomy.runner import run_lane
    from scripts.build_refusal_taxonomy_cases import build_cases

    input_path = (
        Path(args.input)
        if args.input
        else (
            _REPO_ROOT / "evals" / "refusal_taxonomy" / "public" / "v1" / "cases.jsonl"
        )
    )
    if not input_path.exists():
        print(f"input not found: {input_path}", file=sys.stderr)
        return 2

    # Accept either a cases JSONL (one record per line) or a GSM8K-style
    # eval report.json with a top-level ``per_case`` list of refusals.
    if input_path.suffix == ".jsonl":
        cases = load_cases(input_path)
    else:
        cases = build_cases(input_path)
    report = run_lane(cases)
    metrics = report.metrics

    if args.json:
        payload = {
            "lane": "refusal_taxonomy",
            "input": str(input_path),
            "metrics": metrics,
            "cases": report.case_details,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"input              : {input_path}")
        print(f"total              : {metrics['total']}")
        print(f"categorized_rate   : {metrics['categorized_rate']:.3f}")
        print(f"uncategorized      : {metrics['uncategorized']}")
        print(f"case_digest        : {metrics['case_digest']}")
        print("histogram:")
        for category, count in sorted(
            metrics["by_category"].items(),
            key=lambda kv: (-kv[1], kv[0]),
        ):
            print(f"  {count:3d}  {category}")

    if args.save:
        out = _REPO_ROOT / "evals" / "refusal_taxonomy" / "v1" / "report.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "lane": "refusal_taxonomy",
            "version": "v1",
            "split": "public",
            "source_cases": str(input_path),
            "metrics": metrics,
            "cases": report.case_details,
        }
        out.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        )
        print(f"saved              : {out}", file=sys.stderr)

    return 0


def _safe_pack_id(pack_id: str) -> str:
    """Reject pack IDs containing path traversal or separator characters."""
    if not pack_id:
        _die("pack_id is required", code=2)

    path = Path(pack_id)

    if path.is_absolute():
        _die("pack_id must not be an absolute path", code=2)

    if pack_id in {".", ".."}:
        _die("pack_id must name a pack, not a relative path", code=2)

    if any(part in {"", ".", ".."} for part in path.parts):
        _die("pack_id must not contain path traversal", code=2)

    if "/" in pack_id or "\\" in pack_id:
        _die("pack_id must be a simple pack id, not a path", code=2)

    return pack_id


def _load_candidate_jsonl(path: str) -> Any:
    """Read one enriched DiscoveryCandidate JSONL line from *path*."""
    from teaching.discovery import DiscoveryCandidate, EvidencePointer, SubQuestion

    p = Path(path)
    if not p.exists():
        _die(f"candidate file not found: {path}", code=2)
    raw = p.read_text(encoding="utf-8").strip()
    if not raw:
        _die("candidate file is empty", code=2)
    first = raw.splitlines()[0].strip()
    try:
        payload = json.loads(first)
    except json.JSONDecodeError as exc:
        _die(f"invalid JSON: {exc}", code=2)
    try:
        evidence = tuple(EvidencePointer(**e) for e in payload.get("evidence", []))
        sub_questions = tuple(
            SubQuestion(
                sub_id=s["sub_id"],
                proposed_subject=s["proposed_subject"],
                proposed_intent=s["proposed_intent"],
                outcome=s["outcome"],
                evidence=tuple(EvidencePointer(**e) for e in s.get("evidence", [])),
            )
            for s in payload.get("sub_questions", [])
        )
        return DiscoveryCandidate(
            candidate_id=payload["candidate_id"],
            proposed_chain=payload["proposed_chain"],
            trigger=payload["trigger"],
            source_turn_trace=payload.get("source_turn_trace", ""),
            pack_consistent=bool(payload.get("pack_consistent", True)),
            boundary_clean=bool(payload.get("boundary_clean", True)),
            review_state=payload.get("review_state", "unreviewed"),
            domain=payload.get("domain", "cognition"),
            polarity=payload.get("polarity", "undetermined"),
            claim_domain=payload.get("claim_domain", "factual"),
            evidence=evidence,
            sub_questions=sub_questions,
            contemplation_depth=int(payload.get("contemplation_depth", 0)),
            recursion_overflow=bool(payload.get("recursion_overflow", False)),
        )
    except (KeyError, TypeError) as exc:
        _die(f"candidate JSON missing required field: {exc}", code=2)


def _load_findings_jsonl(path: str) -> list:
    """Load ContemplationFinding objects from a JSONL file (W-019)."""
    from core.contemplation.schema import (
        ContemplationEvidenceRef,
        ContemplationFinding,
        FindingKind,
    )
    from teaching.epistemic import EpistemicStatus

    findings = []
    for raw in _read_jsonl_file(Path(path)):
        evidence_refs = tuple(
            ContemplationEvidenceRef(
                source_type=e["source_type"],
                source_id=e["source_id"],
                pointer=e["pointer"],
                summary=e.get("summary", ""),
            )
            for e in raw.get("evidence_refs", [])
        )
        findings.append(
            ContemplationFinding(
                kind=FindingKind(raw["kind"]),
                subject=raw["subject"],
                predicate=raw["predicate"],
                object=raw.get("object"),
                evidence_refs=evidence_refs,
                proposed_action=raw["proposed_action"],
                substrate_hash=raw.get("substrate_hash", ""),
                epistemic_status=EpistemicStatus(
                    raw.get("epistemic_status", EpistemicStatus.SPECULATIVE.value)
                ),
                finding_id=raw.get("finding_id", ""),
            )
        )
    return findings


def _read_jsonl_file(path: Path) -> list:
    """Read a JSONL file and return a list of parsed dicts."""
    lines = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                lines.append(json.loads(line))
    return lines


def _current_git_revision() -> str:
    """Return the current git HEAD SHA (first 12 chars) or 'unknown'."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short=12", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip() or "unknown"
    except Exception:  # noqa: BLE001
        return "unknown"


def _write_miner_curriculum_batch(
    proposals: tuple,
    rejections: tuple,
    out_path: Path | None,
) -> None:
    """Write PackMutationProposal batch to JSONL and print summary."""
    lines = [
        json.dumps(p.as_dict(), sort_keys=True, ensure_ascii=False) for p in proposals
    ]
    if out_path is not None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(
            "\n".join(lines) + ("\n" if lines else ""), encoding="utf-8"
        )
        print(f"wrote {len(proposals)} proposal(s) → {out_path}")
    else:
        for line in lines:
            print(line)
    print(f"proposals : {len(proposals)}", file=sys.stderr)
    print(f"rejections: {len(rejections)}", file=sys.stderr)
    for rej in rejections:
        print(
            f"  rejected {rej.get('finding_id', '?')}: {rej.get('reason', '?')}",
            file=sys.stderr,
        )
