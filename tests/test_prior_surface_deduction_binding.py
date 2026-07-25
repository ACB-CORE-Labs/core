"""Correction binding anchors to the truth path, including on deduction turns.

``CognitiveTurnPipeline`` remembers one surface per turn so the *next* turn can
be read as a correction of it (``_run_teaching`` → ``extract_correction``).
Which bytes it remembers is an epistemic choice, pinned here:

``pipeline.py`` sets ``self._prior_surface = hash_surface`` — the register-
invariant truth-path capture (ADR-0069 inv C), not the served surface. A
register pack that decorates or terses the served bytes therefore cannot
perturb what a correction binds to, which is what keeps teaching independent
of presentation.

The subtlety worth pinning is that "truth path" is not "pre-correction". The
Phase 0 register fix threads ``hash_surface`` through every *substantive*
override — logos-morph refusal, the speculative marker — so when one of those
fires, ``_prior_surface`` holds the post-override bytes the truth path
actually settled on. It is only the presentation layer that is excluded.

An architectural review of the deduction-serve arc flagged this as an untested
gap and predicted the opposite behaviour (that a correction on a deduction turn
would anchor to stale pre-correction bytes). These tests were written to check
that claim. It does not reproduce — the lockstep holds — so what they pin is
the behaviour that is actually there, on the deduction path that went live with
ADR-0256, so it cannot drift unobserved.
"""

from __future__ import annotations

from dataclasses import replace

import pytest

from chat.runtime import ChatRuntime
from core.cognition.pipeline import (
    _SPECULATIVE_SURFACE_MARKER,
    CognitiveTurnPipeline,
)
from core.config import DEFAULT_CONFIG


DEDUCTION_PROMPT = (
    "If it rains then the ground is wet. It rains. "
    "Therefore the ground is wet."
)


def _pipeline(**config_overrides: object) -> CognitiveTurnPipeline:
    runtime = ChatRuntime(no_load_state=True)
    if config_overrides:
        runtime.config = replace(runtime.config, **config_overrides)  # type: ignore[arg-type]
    return CognitiveTurnPipeline(runtime)


def test_deduction_turn_binds_correction_to_the_served_conclusion() -> None:
    """A deduction turn must leave a bindable anchor, not an empty one.

    If ``_prior_surface`` stayed ``None`` or held a stale disclosure after a
    decided turn, the next turn's correction would silently bind to nothing.
    """
    pipeline = _pipeline()
    result = pipeline.run(DEDUCTION_PROMPT, max_tokens=24)

    assert "entail" in result.surface, f"composer did not serve: {result.surface!r}"
    assert pipeline._prior_surface, "a decided turn left no correction anchor"
    assert "the ground is wet" in pipeline._prior_surface


def test_prior_surface_is_the_hash_surface_not_the_decorated_surface() -> None:
    """The truth-path capture, not the register-decorated served bytes.

    ``trace_hash`` folds ``hash_surface``; binding corrections to the same
    bytes is what keeps a register pack from moving teaching provenance.
    """
    pipeline = _pipeline()
    pipeline.run(DEDUCTION_PROMPT, max_tokens=24)
    assert pipeline._prior_surface is not None
    # No register decoration is configured in this fixture, so the two agree —
    # the assertion that matters is that the anchor is a real truth-path
    # capture rather than the bounded-disclosure fallback.
    assert "I don't know" not in pipeline._prior_surface


@pytest.mark.parametrize("flag", [True, False])
def test_correction_anchor_survives_the_deduction_flag_in_both_positions(
    flag: bool,
) -> None:
    """Flag-off must not regress the anchor either.

    ADR-0256's rollback contract is that flag-off is byte-identical to pre-arc
    dispatch. That includes leaving a bindable correction anchor: the same
    prompt falls through to the pack-token-gloss path, which is a different
    surface but must still be remembered.
    """
    pipeline = _pipeline(deduction_serving_enabled=flag)
    pipeline.run(DEDUCTION_PROMPT, max_tokens=24)
    assert pipeline._prior_surface, (
        f"deduction_serving_enabled={flag} left no correction anchor"
    )


def test_speculative_marker_is_carried_into_the_anchor() -> None:
    """The lockstep property, stated directly.

    ``hash_surface`` is updated alongside every substantive override of the
    served surface — the speculative marker is the cheapest one to exercise.
    This is the mechanism that makes the review's "anchors to pre-correction
    bytes" prediction not reproduce; if someone later mutates ``surface``
    without mutating ``hash_surface``, this is what catches it.
    """
    pipeline = _pipeline()
    pipeline._speculative_subjects = {"rains"}
    result = pipeline.run(DEDUCTION_PROMPT, max_tokens=24)

    assert result.surface.startswith(_SPECULATIVE_SURFACE_MARKER), (
        "fixture did not actually mark the turn, so this pin would be vacuous: "
        f"{result.surface!r}"
    )
    assert pipeline._prior_surface is not None
    assert pipeline._prior_surface.startswith(_SPECULATIVE_SURFACE_MARKER), (
        "served surface was marked but the truth-path anchor was not — "
        "hash_surface fell out of lockstep with surface"
    )


def test_deduction_serving_is_live_for_these_pins() -> None:
    """Documents why this file targets the deduction path specifically."""
    assert DEFAULT_CONFIG.deduction_serving_enabled is True
