"""Speculative-subject cache lifecycle (Finding 5, audit 2026-05-20).

Pre-fix ``CognitiveTurnPipeline._speculative_subjects`` was an unbounded
``set[str]`` that only grew over a session.  Two correctness gaps:

  * A subject promoted to ``EpistemicStatus.COHERENT`` via the teaching
    review loop kept appearing with the "(speculative, not yet reviewed)"
    marker forever.
  * Long teaching sessions widened the per-turn substring scan inside
    ``_should_mark_speculative`` without bound.

These tests pin the lifecycle so the fix cannot silently regress.
"""

from __future__ import annotations

from collections import OrderedDict

import pytest

from chat.runtime import ChatRuntime
from core.cognition import CognitiveTurnPipeline
from core.cognition.pipeline import _MAX_SPECULATIVE_SUBJECTS


@pytest.fixture()
def pipeline() -> CognitiveTurnPipeline:
    return CognitiveTurnPipeline(runtime=ChatRuntime())


def test_storage_is_bounded_ordereddict(pipeline: CognitiveTurnPipeline) -> None:
    assert isinstance(pipeline._speculative_subjects, OrderedDict)
    assert _MAX_SPECULATIVE_SUBJECTS == 64


def test_remember_inserts_and_normalizes(pipeline: CognitiveTurnPipeline) -> None:
    pipeline._remember_speculative_subject("  TRUTH  ")
    assert "truth" in pipeline._speculative_subjects
    pipeline._remember_speculative_subject("")
    pipeline._remember_speculative_subject("   ")
    # Empty / whitespace inputs are silently dropped
    assert list(pipeline._speculative_subjects) == ["truth"]


def test_remember_refreshes_lru_position(pipeline: CognitiveTurnPipeline) -> None:
    pipeline._remember_speculative_subject("alpha")
    pipeline._remember_speculative_subject("beta")
    pipeline._remember_speculative_subject("alpha")
    # alpha was re-touched after beta, so alpha is now the MRU entry
    assert list(pipeline._speculative_subjects) == ["beta", "alpha"]


def test_cache_caps_at_max(pipeline: CognitiveTurnPipeline) -> None:
    for i in range(_MAX_SPECULATIVE_SUBJECTS + 10):
        pipeline._remember_speculative_subject(f"subj{i:03d}")
    assert len(pipeline._speculative_subjects) == _MAX_SPECULATIVE_SUBJECTS
    # Oldest 10 entries (subj000..subj009) evicted; newest survive
    keys = list(pipeline._speculative_subjects)
    assert "subj000" not in keys
    assert "subj009" not in keys
    assert "subj010" in keys
    assert keys[-1] == f"subj{_MAX_SPECULATIVE_SUBJECTS + 9:03d}"


def test_forget_removes(pipeline: CognitiveTurnPipeline) -> None:
    pipeline._remember_speculative_subject("truth")
    pipeline._remember_speculative_subject("light")
    pipeline._forget_speculative_subject("Truth")  # case-insensitive
    assert "truth" not in pipeline._speculative_subjects
    assert "light" in pipeline._speculative_subjects


def test_forget_missing_is_noop(pipeline: CognitiveTurnPipeline) -> None:
    pipeline._remember_speculative_subject("truth")
    pipeline._forget_speculative_subject("never-added")
    pipeline._forget_speculative_subject("")
    assert list(pipeline._speculative_subjects) == ["truth"]


def test_should_mark_speculative_still_iterates_correctly(
    pipeline: CognitiveTurnPipeline,
) -> None:
    """The marker decision still triggers on stored subjects."""
    pipeline._remember_speculative_subject("wisdom")
    assert pipeline._should_mark_speculative(
        text="Tell me about wisdom",
        surface="Wisdom is the application of knowledge.",
    )
    pipeline._forget_speculative_subject("wisdom")
    assert not pipeline._should_mark_speculative(
        text="Tell me about wisdom",
        surface="Wisdom is the application of knowledge.",
    )


# ---------------------------------------------------------------------------
# H-13 (external-assessment triage, 2026-07-28) — sibling eviction
# ---------------------------------------------------------------------------
# Seeding splits a subject into tokens, so two independent proposals can seed
# the SAME token ("wisdom" from both "wisdom" and "practical wisdom").  Under
# the pre-fix flat cache, promoting EITHER proposal to COHERENT popped the
# shared token outright — and the other proposal, still unreviewed, lost its
# marker.  The failure direction is the expensive one: unreviewed material
# served WITHOUT the "(speculative, not yet reviewed)" prefix.
#
# These pin the reference-counted lifecycle: a token stays live while any
# unpromoted proposal still claims it.


def _seed_proposal(pipeline: CognitiveTurnPipeline, subject: str) -> None:
    """Mirror the seeding the pipeline performs for one SPECULATIVE proposal."""
    pipeline._remember_speculative_subject(subject)
    for tok in subject.lower().split():
        if len(tok) >= 4:
            pipeline._remember_speculative_subject(tok)


def _promote_proposal(pipeline: CognitiveTurnPipeline, subject: str) -> None:
    """Mirror the eviction the pipeline performs when that proposal goes COHERENT."""
    pipeline._forget_speculative_subject(subject)
    for tok in subject.lower().split():
        if len(tok) >= 4:
            pipeline._forget_speculative_subject(tok)


def test_promoting_one_proposal_keeps_a_sibling_token_live(
    pipeline: CognitiveTurnPipeline,
) -> None:
    """Promoting 'practical wisdom' must not un-mark an unreviewed 'wisdom'."""
    _seed_proposal(pipeline, "wisdom")
    _seed_proposal(pipeline, "practical wisdom")

    _promote_proposal(pipeline, "practical wisdom")

    assert "wisdom" in pipeline._speculative_subjects, (
        "the independent 'wisdom' proposal is still SPECULATIVE — promoting a "
        "different proposal that merely shares the token must not evict it"
    )
    # The promoted proposal's own exclusive tokens are gone.
    assert "practical wisdom" not in pipeline._speculative_subjects
    assert "practical" not in pipeline._speculative_subjects


def test_sibling_survives_at_the_served_surface(
    pipeline: CognitiveTurnPipeline,
) -> None:
    """The consequence that matters: the marker still fires for the sibling."""
    _seed_proposal(pipeline, "wisdom")
    _seed_proposal(pipeline, "practical wisdom")
    _promote_proposal(pipeline, "practical wisdom")

    assert pipeline._should_mark_speculative(
        text="Tell me about wisdom",
        surface="Wisdom is the application of knowledge.",
    ), "unreviewed material must keep its speculative marker"


def test_token_clears_once_every_claimant_is_promoted(
    pipeline: CognitiveTurnPipeline,
) -> None:
    """Reference counting must still reach zero — no marker that never clears."""
    _seed_proposal(pipeline, "wisdom")
    _seed_proposal(pipeline, "practical wisdom")

    _promote_proposal(pipeline, "practical wisdom")
    _promote_proposal(pipeline, "wisdom")

    assert "wisdom" not in pipeline._speculative_subjects
    assert not pipeline._should_mark_speculative(
        text="Tell me about wisdom",
        surface="Wisdom is the application of knowledge.",
    )


def test_repeated_speculative_teaching_needs_matching_promotions(
    pipeline: CognitiveTurnPipeline,
) -> None:
    """Two unreviewed proposals on one subject take two promotions to clear."""
    _seed_proposal(pipeline, "wisdom")
    _seed_proposal(pipeline, "wisdom")

    _promote_proposal(pipeline, "wisdom")
    assert "wisdom" in pipeline._speculative_subjects, (
        "one proposal reviewed, one still outstanding — still speculative"
    )

    _promote_proposal(pipeline, "wisdom")
    assert "wisdom" not in pipeline._speculative_subjects


def test_unmatched_forget_never_underflows(
    pipeline: CognitiveTurnPipeline,
) -> None:
    """A promotion whose seeding never happened must not push a count negative.

    Seeding and eviction derive their token sets from the proposal object at
    two different moments, so they can disagree.  When they do, the safe
    direction is to keep marking (a stale marker is honest-conservative; a
    missing one is not) — never a negative count that would let a later
    promotion strip a live sibling.
    """
    pipeline._remember_speculative_subject("wisdom")
    pipeline._forget_speculative_subject("wisdom")
    pipeline._forget_speculative_subject("wisdom")  # unmatched
    pipeline._remember_speculative_subject("wisdom")

    assert "wisdom" in pipeline._speculative_subjects
    assert pipeline._speculative_subjects["wisdom"] == 1
