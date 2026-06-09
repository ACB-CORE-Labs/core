"""Stage 2 ASK serving/disclosure bus adapter.

Determines whether a pre-rendered question artifact can be served to the user
based on runtime configuration, contemplation result, and artifact validity.

Artifact validation enforces the Q1-D DeliveredQuestion contract:
  - top-level JSON object only;
  - status == "question_only";
  - requires_review is True;
  - served is False;
  - answer_binding is None (key absent or explicitly null);
  - question is an object;
  - question.text is a non-empty string;
  - question.slot_name is present (required by Q1-C/DeliveredQuestion schema);
  - question_path exists on the filesystem and differs from proposal_path.

Any validation failure causes the adapter to fail closed and return a fallback
decision that preserves the existing proposal/refusal surface unchanged.
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

# Sentinel used only in _validate_artifact to distinguish "key absent" from
# "key present with value None".  Having a sentinel avoids treating a missing
# served/answer_binding field as a passing None check.
_MISSING = object()


@dataclass(frozen=True, slots=True)
class ServedAskDecision:
    """The decision made by the served ASK disclosure bus adapter."""

    served: bool
    terminal: str
    surface: str
    disposition: ServedDisposition


def _validate_artifact(data: Any, q_path: Path, p_path_attr: Any) -> str | None:
    """Validate the DeliveredQuestion artifact against the Q1-D contract.

    Returns the validated question text on success, or None on any violation.
    Every check is explicit so reviewers can trace each contract clause to code.
    """
    # Contract: top-level must be a JSON object (dict)
    if not isinstance(data, dict):
        return None

    # Contract: status == "question_only"
    if data.get("status") != "question_only":
        return None

    # Contract: requires_review is True (must be present and strictly True)
    if data.get("requires_review") is not True:
        return None

    # Contract: served is False (must be present and strictly False)
    served_val = data.get("served", _MISSING)
    if served_val is _MISSING or served_val is not False:
        return None

    # Contract: answer_binding is None (key must be absent or explicitly null)
    answer_binding_val = data.get("answer_binding", _MISSING)
    if answer_binding_val is not _MISSING and answer_binding_val is not None:
        return None

    # Contract: question is an object (dict)
    question_data = data.get("question")
    if not isinstance(question_data, dict):
        return None

    # Contract: question.text is a non-empty string
    question_text = question_data.get("text")
    if not isinstance(question_text, str) or not question_text.strip():
        return None

    # Contract: question.slot_name is present (Q1-C/DeliveredQuestion schema requirement)
    # An empty string is treated as absent since a slot name must be meaningful.
    slot_name = question_data.get("slot_name")
    if not slot_name:
        return None

    # Contract: question_path must differ from proposal_path (separate sinks)
    # Already checked upstream (q_path_attr != p_path_attr), but re-checked here
    # at the artifact boundary to make validation self-contained.
    if p_path_attr is not None and str(q_path) == str(p_path_attr):
        return None

    return question_text.strip()


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

    # Refuse to serve when question_path is missing or equals proposal_path.
    # This enforces the Q1-D separate-sinks requirement: question artifacts must
    # never reside under proposal_path.
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

    # 5. Full Q1-D contract validation.  _validate_artifact is intentionally
    # explicit (no single-dict-access shortcut) so each contract clause is
    # individually testable and auditable.
    question_text = _validate_artifact(data, q_path, p_path_attr)
    if question_text is None:
        return _make_fallback_decision(contemplation_result, fallback_surface)

    # 6. Use choose_served_disposition to map the ASK resolution
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
