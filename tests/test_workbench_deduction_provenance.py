"""Workbench must record the grounding source it was actually served.

The deduction-serve arc ratified ``deduction_serving_enabled`` ON by default
(ADR-0256, 2026-07-24).  ``workbench/api.py``'s live chat route builds a bare
``ChatRuntime()``, so a deduction-shaped prompt through Workbench is decided by
the ROBDD entailment engine and stamped ``grounding_source="deduction"`` on the
``TurnEvent`` — exactly like the REPL path.

Before this file existed, ``_coerce_grounding_source`` carried a hand-copied
whitelist of the six pre-arc labels and silently rewrote everything else to
``"none"``.  A proved, SERVE-licensed answer was therefore recorded in the
journal, the evidence bundle, and the pipeline record as *ungrounded*.  Not a
crash and not a dropped turn: a durable audit artifact asserting something
false about a turn the engine had decided.

The asymmetry that makes this worth pinning: the *unregistered* path degraded
honestly — ``epistemic_state_for_grounding_source`` returns
``EPISTEMIC_STATE_NEEDED`` for a label it does not know, which reads "this
needs determination".  The *coercion* asserted ``none`` = ungrounded.  A
second, hand-maintained copy of a closed enum is worse than no copy at all,
so the tests here pin both halves: the values are registered, and the
whitelist is derived from the registration rather than restated beside it.
"""

from __future__ import annotations

import pytest

from core.config import DEFAULT_CONFIG
from core.epistemic_state import (
    EpistemicState,
    epistemic_state_for_grounding_source,
)
from workbench.api import _coerce_grounding_source, _run_chat_turn


#: A Band v1 propositional argument: the composer's commit gate
#: (``looks_like_deductive_argument``) fires on the sentence-initial
#: "Therefore", and the ROBDD decides it ENTAILED.
DEDUCTION_PROMPT = (
    "If it rains then the ground is wet. It rains. "
    "Therefore the ground is wet."
)


def test_deduction_serving_is_on_by_default() -> None:
    """The premise of every other test in this file (ADR-0256 ratification)."""
    assert DEFAULT_CONFIG.deduction_serving_enabled is True


def test_workbench_records_deduction_as_its_own_grounding_source() -> None:
    """The regression: a decided answer recorded as ungrounded.

    Drives the same entry point the HTTP chat route uses, so this fails if the
    coercion whitelist, the ``GroundingSource`` registration, or the composer's
    dispatch position regresses.
    """
    result = _run_chat_turn(DEDUCTION_PROMPT)

    assert "entail" in result.surface, (
        f"the deduction composer did not serve this turn: {result.surface!r}"
    )
    assert result.grounding_source == "deduction", (
        "Workbench recorded a ROBDD-decided answer as "
        f"{result.grounding_source!r} — the audit artifact is asserting "
        "something false about how this turn was grounded"
    )


def test_workbench_records_deduction_as_decoded() -> None:
    """A decided answer is DECODED, not UNDETERMINED and not STATE_NEEDED."""
    result = _run_chat_turn(DEDUCTION_PROMPT)
    assert result.epistemic_state == EpistemicState.DECODED.value


@pytest.mark.parametrize(
    "source",
    ["pack", "teaching", "vault", "partial", "oov", "none", "deduction", "curriculum"],
)
def test_coercion_preserves_every_registered_grounding_source(source: str) -> None:
    """No registered label may be rewritten to another label.

    Parametrized over the registration itself rather than a restated list:
    a value added to ``GroundingSource`` without a matching coercion entry
    fails here rather than silently downgrading in production.
    """
    assert _coerce_grounding_source(source) == source


def test_coercion_still_floors_unknown_labels_to_none() -> None:
    """An UNregistered label is not grounding evidence and must not pass."""
    assert _coerce_grounding_source("not_a_grounding_source") == "none"
    assert _coerce_grounding_source(None) == "none"
    assert _coerce_grounding_source("") == "none"


def test_decided_grounding_sources_map_to_decoded() -> None:
    """Deduction and curriculum are decided, so they rank with pack/teaching/vault."""
    for source in ("deduction", "curriculum"):
        assert epistemic_state_for_grounding_source(source) is EpistemicState.DECODED


def test_unknown_grounding_source_still_asks_for_a_state() -> None:
    """The honest-degradation default must survive the registration."""
    assert (
        epistemic_state_for_grounding_source("not_a_grounding_source")
        is EpistemicState.EPISTEMIC_STATE_NEEDED
    )
