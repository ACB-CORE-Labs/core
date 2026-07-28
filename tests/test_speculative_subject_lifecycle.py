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


# The pipeline calls the cache once per source string and lets the cache do its
# own token indexing (H-13).  These helpers mirror that exactly — a test that
# split tokens itself would be testing a call pattern production no longer uses,
# which is how the first attempt at this fix passed while the bug survived.


def _teach_speculative(pipeline: CognitiveTurnPipeline, subject: str) -> None:
    """One SPECULATIVE proposal lands (pipeline.py 10b, SPECULATIVE arm)."""
    pipeline._remember_speculative_subject(subject)


def _teach_coherent(pipeline: CognitiveTurnPipeline, subject: str) -> None:
    """One COHERENT proposal lands (pipeline.py 10b, COHERENT arm).

    Note this arm is reached by proposals that were **never seeded** — review
    returns COHERENT on the same turn the correction is captured.  So a release
    routinely names tokens this subject never claimed.
    """
    pipeline._forget_speculative_subject(subject)


def test_coherent_proposal_does_not_unmark_an_unrelated_subject(
    pipeline: CognitiveTurnPipeline,
) -> None:
    """The load-bearing case: the COHERENT proposal never seeded anything.

    An unreviewed ``wisdom`` is outstanding.  A *different* correction about
    ``practical wisdom`` passes review on its own turn — it was never
    SPECULATIVE, so it holds no claim on the token ``wisdom``.  Releasing it
    must leave the unreviewed subject marked.
    """
    _teach_speculative(pipeline, "wisdom")
    _teach_coherent(pipeline, "practical wisdom")

    assert "wisdom" in pipeline._speculative_subjects, (
        "a COHERENT proposal released a token it never claimed, stripping the "
        "marker from an unrelated proposal that is still unreviewed"
    )
    assert pipeline._should_mark_speculative(
        text="Tell me about wisdom",
        surface="Wisdom is the application of knowledge.",
    ), "unreviewed material must keep its speculative marker"


def test_promoting_one_proposal_keeps_a_sibling_token_live(
    pipeline: CognitiveTurnPipeline,
) -> None:
    """Both taught speculatively; reviewing one must not clear the other."""
    _teach_speculative(pipeline, "wisdom")
    _teach_speculative(pipeline, "practical wisdom")

    _teach_coherent(pipeline, "practical wisdom")

    assert "wisdom" in pipeline._speculative_subjects
    # The reviewed subject's own exclusive tokens are gone.
    assert "practical wisdom" not in pipeline._speculative_subjects
    assert "practical" not in pipeline._speculative_subjects


def test_token_clears_once_its_own_claimant_is_reviewed(
    pipeline: CognitiveTurnPipeline,
) -> None:
    """Eviction must still happen — no marker that can never clear."""
    _teach_speculative(pipeline, "wisdom")
    _teach_speculative(pipeline, "practical wisdom")

    _teach_coherent(pipeline, "practical wisdom")
    _teach_coherent(pipeline, "wisdom")

    assert "wisdom" not in pipeline._speculative_subjects
    assert not pipeline._should_mark_speculative(
        text="Tell me about wisdom",
        surface="Wisdom is the application of knowledge.",
    )


def test_claim_is_idempotent_per_subject(
    pipeline: CognitiveTurnPipeline,
) -> None:
    """Re-teaching one subject speculatively does not require two reviews.

    The claimant is the subject, so the same subject claiming twice is one
    claim — a single review clears it.  (Distinct subjects sharing a token is
    the case that needs both reviewed, pinned above.)
    """
    _teach_speculative(pipeline, "wisdom")
    _teach_speculative(pipeline, "wisdom")

    _teach_coherent(pipeline, "wisdom")
    assert "wisdom" not in pipeline._speculative_subjects


def test_release_of_an_unheld_subject_is_a_noop(
    pipeline: CognitiveTurnPipeline,
) -> None:
    """Releasing a subject nobody claimed must not disturb live claims."""
    _teach_speculative(pipeline, "wisdom")

    _teach_coherent(pipeline, "entirely unrelated topic")
    _teach_coherent(pipeline, "practical")  # shares no claim on "wisdom"

    assert pipeline._speculative_subjects["wisdom"] == {"wisdom"}


def test_index_tokens_are_shared_by_claim_and_release(
    pipeline: CognitiveTurnPipeline,
) -> None:
    """Both sides derive tokens from one helper, so they cannot disagree."""
    owner, tokens = pipeline._speculative_index_tokens("  Correction: Practical WISDOM ")
    assert owner == "correction: practical wisdom"
    # "correction" is a subject stopword — indexing it would match every
    # correction turn, so it is filtered out of the token set.
    assert set(tokens) == {"correction: practical wisdom", "practical", "wisdom"}
    # The owner is always indexed, even when it is shorter than the token floor.
    owner_short, tokens_short = pipeline._speculative_index_tokens("ash")
    assert owner_short == "ash"
    assert tokens_short == ("ash",)
