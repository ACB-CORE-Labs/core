"""Proposal review reporter (RPT) — surfaces contemplation/idle proposals for review.

Observes ``teaching/proposals/comprehension_failures/*.json`` (emitted by the contemplation pass,
N5), validates them, and reports pending review obligations. It does not advance the teaching
loop, ratify, mount, modify readers, or affect serving. It is **not** an ``idle_tick``
(``ChatRuntime.idle_tick`` remains the only one) and **not** L10 — it is the review surface that
keeps proposal artifacts from becoming inert files. A future PR may call this reporter from
``idle_tick`` as a read-only sub-pass.

:mod:`core.proposal_review.queue` (Tier S4) extends this to a second sink
(``derived_close_facts``) and adds human review-STATE tracking — an append-only sidecar log
(``teaching/proposals/review_log.jsonl``) recording that a human looked at an artifact. That sidecar
is the one write anywhere in this package: it never touches a sink artifact's own ``status`` /
``mounted`` / ``requires_review`` fields, never ratifies, and never mounts anything — ratification
stays ``teaching/proposals.py``'s separate ADR-0057 corridor (``core teaching proposals`` / ``core
teaching review``, a different sink entirely).
"""

from __future__ import annotations

from core.proposal_review.model import MalformedArtifact, PendingProposal
from core.proposal_review.queue import (
    MalformedEntry,
    QueueEntry,
    ReviewRecord,
    queue_status,
    record_review,
    reviewed_keys,
    scan_all,
)
from core.proposal_review.report import (
    ProposalReviewReport,
    build_report,
    report_json,
    report_text,
)
from core.proposal_review.safety import SafetyVerdict, dry_check
from core.proposal_review.scan import DEFAULT_SINK, default_sink, scan
from core.proposal_review.summary import ProposalReviewIdleSummary, idle_summary

__all__ = [
    "DEFAULT_SINK",
    "MalformedArtifact",
    "MalformedEntry",
    "PendingProposal",
    "ProposalReviewIdleSummary",
    "ProposalReviewReport",
    "QueueEntry",
    "ReviewRecord",
    "SafetyVerdict",
    "build_report",
    "default_sink",
    "dry_check",
    "idle_summary",
    "queue_status",
    "record_review",
    "report_json",
    "report_text",
    "reviewed_keys",
    "scan",
    "scan_all",
]
