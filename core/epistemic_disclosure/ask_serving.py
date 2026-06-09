"""Stage 2 ASK serving/disclosure bus adapter.

Determines whether a pre-rendered question artifact can be served to the user
based on runtime configuration, contemplation result, and artifact validity.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.epistemic_questions.serving_gate import ask_serving_enabled
from core.epistemic_disclosure.disposition import choose_served_disposition, ServedDisposition
from core.epistemic_disclosure.limitation import LimitationAssessment
from core.epistemic_state import EpistemicState


@dataclass(frozen=True, slots=True)
class ServedAskDecision:
    """The decision made by the served ASK disclosure bus adapter."""

    served: bool
    terminal: str
    surface: str
    disposition: ServedDisposition


def evaluate_served_ask(
    config: Any,
    contemplation_result: Any,
    fallback_surface: str,
) -> ServedAskDecision:
    """Evaluate whether to serve a pre-rendered question instead of the fallback surface.

    ASK returns an intake request (pre-rendered question content), which is a request
    for missing state rather than a committed answer or an approximation. Therefore,
    it is governed as an intake request (ServedDisposition.ASK) through
    choose_served_disposition rather than formatted as a statistical/approximate answer
    surface in shape_surface. The standard ADR-0206 governance seam (ReachPolicy,
    govern_response, shape_surface) remains fully preserved for the fallback
    answer/refusal paths.
    """
    # 1. Fail closed when config or helper is disabled/absent
    if not ask_serving_enabled(config):
        return _make_fallback_decision(contemplation_result, fallback_surface)

    # 2. Check if the contemplation terminal is QUESTION_NEEDED
    terminal_val = getattr(contemplation_result, "terminal", None)
    if terminal_val is None:
        return _make_fallback_decision(contemplation_result, fallback_surface)

    terminal_str = getattr(terminal_val, "value", str(terminal_val))
    if terminal_str != "QUESTION_NEEDED":
        return _make_fallback_decision(contemplation_result, fallback_surface)

    # 3. Retrieve question and proposal paths
    q_path_attr = getattr(contemplation_result, "question_path", None)
    p_path_attr = getattr(contemplation_result, "proposal_path", None)

    # Refuse to serve when question_path is missing or equals proposal_path
    if not q_path_attr or q_path_attr == p_path_attr:
        return _make_fallback_decision(contemplation_result, fallback_surface)

    # 4. Attempt to read and parse the DeliveredQuestion artifact
    q_path = Path(q_path_attr)
    if not q_path.is_file():
        return _make_fallback_decision(contemplation_result, fallback_surface)

    try:
        data = json.loads(q_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return _make_fallback_decision(contemplation_result, fallback_surface)

    # Refuse to serve if the artifact is malformed or missing key fields
    if not isinstance(data, dict):
        return _make_fallback_decision(contemplation_result, fallback_surface)

    question_data = data.get("question")
    if not isinstance(question_data, dict):
        return _make_fallback_decision(contemplation_result, fallback_surface)

    question_text = question_data.get("text")
    if not question_text or not isinstance(question_text, str) or not question_text.strip():
        return _make_fallback_decision(contemplation_result, fallback_surface)

    # 5. Use choose_served_disposition to map the ASK resolution
    blocking_reason = data.get("blocking_reason", "")
    owner_organ = data.get("owner_organ", "r2_constraint")

    limitation = LimitationAssessment(
        limitation_kind="missing_information",
        resolution_action="ask_question",
        epistemic_state=EpistemicState.UNDETERMINED,
        owner_organ=owner_organ,
        blocking_reason=blocking_reason,
    )
    disposition = choose_served_disposition(
        epistemic_state=EpistemicState.UNDETERMINED,
        limitation=limitation,
    )

    return ServedAskDecision(
        served=True,
        terminal="QUESTION_NEEDED",
        surface=question_text,
        disposition=disposition,
    )


def _make_fallback_decision(
    contemplation_result: Any,
    fallback_surface: str,
) -> ServedAskDecision:
    """Create a fallback decision preserving the existing proposal/refusal signals."""
    terminal_val = getattr(contemplation_result, "terminal", None)
    terminal_str = getattr(terminal_val, "value", str(terminal_val)) if terminal_val is not None else "NO_PROGRESS"

    # Map the terminal to the correct ServedDisposition for the fallback
    if terminal_str == "PROPOSAL_EMITTED":
        disposition = ServedDisposition.PROPOSE
    elif terminal_str in ("REFUSED_KNOWN_BOUNDARY", "REFUSED_UNSUPPORTED_FAMILY", "AMBIGUOUS_ORGAN", "NO_PROGRESS"):
        disposition = ServedDisposition.REFUSE
    elif terminal_str == "SOLVED_VERIFIED":
        disposition = ServedDisposition.COMMIT
    else:
        disposition = ServedDisposition.REFUSE

    return ServedAskDecision(
        served=False,
        terminal=terminal_str,
        surface=fallback_surface,
        disposition=disposition,
    )
