"""Focused integration tests for the Stage 2 served ASK slice.

Covers the 6 required test cases ensuring gated served ASK, fallback preservation,
unrenderable ask safety, distinct sinks/paths, no prose construction, and governance bus usage.

Additional tests added per reviewer requirements:
  - Artifact rejection tests: status, served, requires_review, answer_binding, blank text
  - Exact-text consumption test proving bypass is safe
  - Disposition telemetry tests: default stability, backward-compat, ASK branch, no reclassification
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any

import pytest

from chat.runtime import ChatRuntime, ChatResponse
from core.config import RuntimeConfig
from core.epistemic_disclosure.ask_serving import evaluate_served_ask, ServedAskDecision
from core.epistemic_disclosure.disposition import choose_served_disposition, ServedDisposition
from generate.contemplation.pass_manager import ContemplationResult
from generate.contemplation.findings import Terminal
from field.state import FieldState
import numpy as np


class DummyTerminal:
    def __init__(self, value: str):
        self.value = value


class DummyContemplationResult:
    def __init__(
        self,
        terminal: str,
        question_path: str | None = None,
        proposal_path: str | None = None,
        family: str | None = None,
    ):
        self.terminal = DummyTerminal(terminal) if isinstance(terminal, str) else terminal
        self.question_path = question_path
        self.proposal_path = proposal_path
        self.family = family


def _write_valid_artifact(path: Path, text: str = "How many chickens are there in total?") -> None:
    data = {
        "status": "question_only",
        "blocking_reason": "missing_total_count",
        "owner_organ": "r2_constraint",
        "question": {
            "text": text,
            "reason": "missing_total_count",
            "slot_name": "total_count",
        },
        "requires_review": True,
        "served": False,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def _get_dummy_field_state() -> FieldState:
    from field.state import FieldState
    # Create a dummy array of appropriate size for FieldState
    return FieldState(np.zeros((32,), dtype=np.float32))


def _get_mocked_runtime(config: RuntimeConfig, monkeypatch: pytest.MonkeyPatch) -> ChatRuntime:
    runtime = ChatRuntime(config=config, no_load_state=True)
    # Mock safety check to prevent dummy field state from failing versor condition checks
    monkeypatch.setattr(
        runtime.safety_check,
        "check",
        lambda *args, **kwargs: type(
            "Verdict",
            (),
            {"upheld": True, "violated_boundaries": (), "runtime_checkable_count": 0},
        )(),
    )
    monkeypatch.setattr(
        runtime.ethics_check,
        "check",
        lambda *args, **kwargs: type(
            "Verdict",
            (),
            {"upheld": True, "violated_commitments": (), "runtime_checkable_count": 0},
        )(),
    )
    return runtime


# 1. test_ask_serving_disabled_preserves_existing_proposal_signal
def test_ask_serving_disabled_preserves_existing_proposal_signal(monkeypatch, tmp_path) -> None:
    config = RuntimeConfig(ask_serving_enabled=False)
    q_path = tmp_path / "questions" / "q1.json"
    p_path = tmp_path / "proposals" / "p1.json"
    _write_valid_artifact(q_path)

    # Case A: Terminal is QUESTION_NEEDED but serving is disabled
    res = DummyContemplationResult(
        terminal="QUESTION_NEEDED",
        question_path=str(q_path),
        proposal_path=str(p_path),
    )
    decision = evaluate_served_ask(config, res, "fallback_surface")
    assert not decision.served
    assert decision.disposition == ServedDisposition.REFUSE

    # Case B: Check that stub response maps correctly and preserves signals
    runtime = _get_mocked_runtime(config, monkeypatch)
    stub = runtime._stub_response(
        field_state=_get_dummy_field_state(),
        contemplation_result=res,
        pack_grounded_surface="fallback_surface",
    )
    assert stub.surface == "fallback_surface"
    assert stub.disposition == "refuse"

    # Case C: Terminal is PROPOSAL_EMITTED
    res_proposal = DummyContemplationResult(
        terminal="PROPOSAL_EMITTED",
        question_path=str(q_path),
        proposal_path=str(p_path),
    )
    decision_p = evaluate_served_ask(config, res_proposal, "fallback_surface")
    assert not decision_p.served
    assert decision_p.disposition == ServedDisposition.PROPOSE

    stub_p = runtime._stub_response(
        field_state=_get_dummy_field_state(),
        contemplation_result=res_proposal,
        pack_grounded_surface="fallback_surface",
    )
    assert stub_p.surface == "fallback_surface"
    assert stub_p.disposition == "propose"


# 2. test_ask_serving_enabled_surfaces_question_needed_from_artifact
def test_ask_serving_enabled_surfaces_question_needed_from_artifact(monkeypatch, tmp_path) -> None:
    config = RuntimeConfig(ask_serving_enabled=True)
    q_path = tmp_path / "questions" / "q1.json"
    p_path = tmp_path / "proposals" / "p1.json"
    question_text = "How many chickens are there in total?"
    _write_valid_artifact(q_path, text=question_text)

    res = DummyContemplationResult(
        terminal="QUESTION_NEEDED",
        question_path=str(q_path),
        proposal_path=str(p_path),
    )
    decision = evaluate_served_ask(config, res, "fallback_surface")
    assert decision.served
    assert decision.surface == question_text
    assert decision.disposition == ServedDisposition.ASK

    # Check runtime stub response integration
    runtime = _get_mocked_runtime(config, monkeypatch)
    stub = runtime._stub_response(
        field_state=_get_dummy_field_state(),
        contemplation_result=res,
        pack_grounded_surface="fallback_surface",
    )
    assert stub.surface == question_text
    assert stub.disposition == "ask"
    assert stub.epistemic_state == "undetermined"


# 3. test_unrenderable_ask_never_serves_question_needed
def test_unrenderable_ask_never_serves_question_needed(monkeypatch, tmp_path) -> None:
    config = RuntimeConfig(ask_serving_enabled=True)
    q_path = tmp_path / "questions" / "q1.json"
    p_path = tmp_path / "proposals" / "p1.json"

    runtime = _get_mocked_runtime(config, monkeypatch)

    # Sub-case A: Artifact file does not exist
    res_missing = DummyContemplationResult(
        terminal="QUESTION_NEEDED",
        question_path=str(tmp_path / "nonexistent.json"),
        proposal_path=str(p_path),
    )
    decision = evaluate_served_ask(config, res_missing, "fallback_surface")
    assert not decision.served
    stub = runtime._stub_response(
        field_state=_get_dummy_field_state(),
        contemplation_result=res_missing,
        pack_grounded_surface="fallback_surface",
    )
    assert stub.surface == "fallback_surface"
    assert stub.disposition == "refuse"

    # Sub-case B: Malformed JSON
    q_path.parent.mkdir(parents=True, exist_ok=True)
    q_path.write_text("{malformed json", encoding="utf-8")
    res_malformed = DummyContemplationResult(
        terminal="QUESTION_NEEDED",
        question_path=str(q_path),
        proposal_path=str(p_path),
    )
    decision = evaluate_served_ask(config, res_malformed, "fallback_surface")
    assert not decision.served
    stub = runtime._stub_response(
        field_state=_get_dummy_field_state(),
        contemplation_result=res_malformed,
        pack_grounded_surface="fallback_surface",
    )
    assert stub.surface == "fallback_surface"

    # Sub-case C: Question text empty/missing
    data = {
        "status": "question_only",
        "question": {"text": "   "}  # whitespace only
    }
    q_path.write_text(json.dumps(data), encoding="utf-8")
    res_empty = DummyContemplationResult(
        terminal="QUESTION_NEEDED",
        question_path=str(q_path),
        proposal_path=str(p_path),
    )
    decision = evaluate_served_ask(config, res_empty, "fallback_surface")
    assert not decision.served
    stub = runtime._stub_response(
        field_state=_get_dummy_field_state(),
        contemplation_result=res_empty,
        pack_grounded_surface="fallback_surface",
    )
    assert stub.surface == "fallback_surface"


# 4. test_question_only_not_proposal_only
def test_question_only_not_proposal_only(tmp_path) -> None:
    config = RuntimeConfig(ask_serving_enabled=True)
    q_path = tmp_path / "questions" / "q1.json"
    p_path = tmp_path / "proposals" / "p1.json"

    _write_valid_artifact(q_path)

    # Sub-case A: question_path is missing
    res_no_q = DummyContemplationResult(
        terminal="QUESTION_NEEDED",
        proposal_path=str(p_path),
    )
    decision = evaluate_served_ask(config, res_no_q, "fallback_surface")
    assert not decision.served

    # Sub-case B: question_path equals proposal_path
    res_same = DummyContemplationResult(
        terminal="QUESTION_NEEDED",
        question_path=str(q_path),
        proposal_path=str(q_path),
    )
    decision = evaluate_served_ask(config, res_same, "fallback_surface")
    assert not decision.served

    # Sub-case C: physically distinct paths
    assert q_path.parent != p_path.parent


# 5. test_served_ask_does_not_construct_question_prose
def test_served_ask_does_not_construct_question_prose() -> None:
    # AST Guard: check that ask_serving.py does not import render or render_question, and contains no question templates
    adapter_path = Path(__file__).resolve().parents[1] / "core" / "epistemic_disclosure" / "ask_serving.py"
    runtime_path = Path(__file__).resolve().parents[1] / "chat" / "runtime.py"

    forbidden_modules = ("core.epistemic_questions.render",)
    forbidden_templates = ("What ", "Which ", "How many", "Please provide")

    for path in (adapter_path, runtime_path):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                assert not any(
                    node.module == m or node.module.startswith(m + ".") for m in forbidden_modules
                ), f"{path.name} imports forbidden render module {node.module}"
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    assert not any(
                        alias.name == m or alias.name.startswith(m + ".") for m in forbidden_modules
                    ), f"{path.name} imports forbidden render module {alias.name}"
            # Ensure render_question is not called directly
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                assert node.func.id != "render_question", f"{path.name} calls render_question directly"

    # Ensure no ad-hoc question prose template is defined in ask_serving.py
    content = adapter_path.read_text(encoding="utf-8")
    for template in forbidden_templates:
        assert template not in content, f"ask_serving.py contains forbidden prose template: {template!r}"


# 6. test_served_ask_uses_governance_bus_not_parallel_runtime_path
def test_served_ask_uses_governance_bus_not_parallel_runtime_path(monkeypatch, tmp_path) -> None:
    config = RuntimeConfig(ask_serving_enabled=True)
    q_path = tmp_path / "questions" / "q1.json"
    p_path = tmp_path / "proposals" / "p1.json"
    _write_valid_artifact(q_path)

    res = DummyContemplationResult(
        terminal="QUESTION_NEEDED",
        question_path=str(q_path),
        proposal_path=str(p_path),
    )

    # Monkeypatch choose_served_disposition to trace calls and assert it is called on the governance bus path
    calls = []
    def traced_choose_served_disposition(*args, **kwargs):
        calls.append((args, kwargs))
        return choose_served_disposition(*args, **kwargs)

    monkeypatch.setattr(
        "core.epistemic_disclosure.ask_serving.choose_served_disposition",
        traced_choose_served_disposition,
    )

    runtime = _get_mocked_runtime(config, monkeypatch)
    stub = runtime._stub_response(
        field_state=_get_dummy_field_state(),
        contemplation_result=res,
        pack_grounded_surface="fallback_surface",
    )

    assert stub.surface == "How many chickens are there in total?"
    assert len(calls) == 1
    assert calls[0][1]["epistemic_state"] == "undetermined"  # maps to EpistemicState.UNDETERMINED
    assert calls[0][1]["limitation"].resolution_action == "ask_question"


# ──────────────────────────────────────────────────────────────────────────────
# REVIEWER-REQUIRED REJECTION TESTS (Q1-D artifact contract violations)
# ──────────────────────────────────────────────────────────────────────────────

def _write_artifact(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def _question_needed_result(q_path: Path, p_path: Path) -> DummyContemplationResult:
    return DummyContemplationResult(
        terminal="QUESTION_NEEDED",
        question_path=str(q_path),
        proposal_path=str(p_path),
    )


def _base_valid_data() -> dict:
    """Return a fully-valid DeliveredQuestion artifact payload."""
    return {
        "status": "question_only",
        "requires_review": True,
        "served": False,
        "question": {
            "text": "How many crates are left?",
            "slot_name": "remaining_crates",
        },
    }


def test_reject_status_proposal_only(tmp_path) -> None:
    """Artifact with status='proposal_only' must not be served."""
    config = RuntimeConfig(ask_serving_enabled=True)
    q_path = tmp_path / "q" / "q.json"
    p_path = tmp_path / "p" / "p.json"
    data = _base_valid_data()
    data["status"] = "proposal_only"
    _write_artifact(q_path, data)
    decision = evaluate_served_ask(config, _question_needed_result(q_path, p_path), "fallback")
    assert not decision.served, "status='proposal_only' must not be served"
    assert decision.surface == "fallback"


def test_reject_served_true(tmp_path) -> None:
    """Artifact with served=True must not be served (already delivered)."""
    config = RuntimeConfig(ask_serving_enabled=True)
    q_path = tmp_path / "q" / "q.json"
    p_path = tmp_path / "p" / "p.json"
    data = _base_valid_data()
    data["served"] = True
    _write_artifact(q_path, data)
    decision = evaluate_served_ask(config, _question_needed_result(q_path, p_path), "fallback")
    assert not decision.served, "served=True in artifact must not be served"


def test_reject_requires_review_false(tmp_path) -> None:
    """Artifact with requires_review=False must not be served."""
    config = RuntimeConfig(ask_serving_enabled=True)
    q_path = tmp_path / "q" / "q.json"
    p_path = tmp_path / "p" / "p.json"
    data = _base_valid_data()
    data["requires_review"] = False
    _write_artifact(q_path, data)
    decision = evaluate_served_ask(config, _question_needed_result(q_path, p_path), "fallback")
    assert not decision.served, "requires_review=False must not be served"


def test_reject_non_null_answer_binding(tmp_path) -> None:
    """Artifact with answer_binding != None must not be served."""
    config = RuntimeConfig(ask_serving_enabled=True)
    q_path = tmp_path / "q" / "q.json"
    p_path = tmp_path / "p" / "p.json"
    data = _base_valid_data()
    data["answer_binding"] = {"slot": "remaining_crates", "value": 42}
    _write_artifact(q_path, data)
    decision = evaluate_served_ask(config, _question_needed_result(q_path, p_path), "fallback")
    assert not decision.served, "non-null answer_binding must not be served"


def test_reject_missing_question_text(tmp_path) -> None:
    """Artifact with question.text absent must not be served."""
    config = RuntimeConfig(ask_serving_enabled=True)
    q_path = tmp_path / "q" / "q.json"
    p_path = tmp_path / "p" / "p.json"
    data = _base_valid_data()
    del data["question"]["text"]
    _write_artifact(q_path, data)
    decision = evaluate_served_ask(config, _question_needed_result(q_path, p_path), "fallback")
    assert not decision.served, "missing question.text must not be served"


def test_reject_blank_question_text(tmp_path) -> None:
    """Artifact with question.text blank/whitespace-only must not be served."""
    config = RuntimeConfig(ask_serving_enabled=True)
    q_path = tmp_path / "q" / "q.json"
    p_path = tmp_path / "p" / "p.json"
    data = _base_valid_data()
    data["question"]["text"] = "   "
    _write_artifact(q_path, data)
    decision = evaluate_served_ask(config, _question_needed_result(q_path, p_path), "fallback")
    assert not decision.served, "blank question.text must not be served"


def test_reject_missing_slot_name(tmp_path) -> None:
    """Artifact with question.slot_name absent must not be served (Q1-C contract)."""
    config = RuntimeConfig(ask_serving_enabled=True)
    q_path = tmp_path / "q" / "q.json"
    p_path = tmp_path / "p" / "p.json"
    data = _base_valid_data()
    del data["question"]["slot_name"]
    _write_artifact(q_path, data)
    decision = evaluate_served_ask(config, _question_needed_result(q_path, p_path), "fallback")
    assert not decision.served, "missing slot_name must not be served (Q1-C contract)"


def test_reject_empty_slot_name(tmp_path) -> None:
    """Artifact with question.slot_name = '' must not be served."""
    config = RuntimeConfig(ask_serving_enabled=True)
    q_path = tmp_path / "q" / "q.json"
    p_path = tmp_path / "p" / "p.json"
    data = _base_valid_data()
    data["question"]["slot_name"] = ""
    _write_artifact(q_path, data)
    decision = evaluate_served_ask(config, _question_needed_result(q_path, p_path), "fallback")
    assert not decision.served, "empty slot_name must not be served"


# ──────────────────────────────────────────────────────────────────────────────
# BYPASS SAFETY: exact-text consumption test
# Proves the served ASK branch consumes artifact text exactly — no register/
# decorator mutation is applied to the pre-rendered Q1-C/Q1-D question prose.
# ──────────────────────────────────────────────────────────────────────────────

def test_served_ask_surface_is_consumed_exactly_from_artifact(monkeypatch, tmp_path) -> None:
    """Served question text must equal the artifact text exactly, no mutation."""
    config = RuntimeConfig(ask_serving_enabled=True)
    question_text = "How many units remain in the holding area?"
    q_path = tmp_path / "q" / "q.json"
    p_path = tmp_path / "p" / "p.json"
    _write_valid_artifact(q_path, text=question_text)

    res = _question_needed_result(q_path, p_path)
    decision = evaluate_served_ask(config, res, "fallback")
    assert decision.served
    # decision.surface must be exactly the stripped artifact text
    assert decision.surface == question_text

    runtime = _get_mocked_runtime(config, monkeypatch)
    stub = runtime._stub_response(
        field_state=_get_dummy_field_state(),
        contemplation_result=res,
        pack_grounded_surface="fallback_surface",
    )
    # The stub surface must equal the artifact text without any register/decorator mutation
    assert stub.surface == question_text, (
        f"Served ASK surface was mutated: expected {question_text!r}, got {stub.surface!r}"
    )
    # Realizer guard must be set to 'ok' (pre-rendered Q1-C prose bypasses structural check)
    assert stub.realizer_guard_status == "ok"
    # Disposition must be 'ask'
    assert stub.disposition == "ask"


# ──────────────────────────────────────────────────────────────────────────────
# DISPOSITION TELEMETRY TESTS
# ──────────────────────────────────────────────────────────────────────────────

def test_disposition_default_main_path_is_stable(monkeypatch, tmp_path) -> None:
    """Normal non-ASK stub paths must emit stable disposition values."""
    config = RuntimeConfig(ask_serving_enabled=False)
    runtime = _get_mocked_runtime(config, monkeypatch)
    field_state = _get_dummy_field_state()

    # No contemplation_result: should default to fallback (refuse for unknown grounding)
    stub_none = runtime._stub_response(
        field_state=field_state,
        pack_grounded_surface=None,
        contemplation_result=None,
    )
    assert stub_none.disposition == "refuse"

    # Pack-grounded surface with no contemplation_result: commit
    stub_pack = runtime._stub_response(
        field_state=field_state,
        pack_grounded_surface="Some grounded answer.",
        grounded_source_tag="pack",
        contemplation_result=None,
    )
    assert stub_pack.disposition == "commit"


def test_disposition_proposal_emitted_not_reclassified(monkeypatch, tmp_path) -> None:
    """PROPOSAL_EMITTED terminal must emit disposition='propose', not 'ask' or 'commit'."""
    config = RuntimeConfig(ask_serving_enabled=True)  # even with ASK enabled
    q_path = tmp_path / "q" / "q.json"
    p_path = tmp_path / "p" / "p.json"
    _write_valid_artifact(q_path)
    res = DummyContemplationResult(
        terminal="PROPOSAL_EMITTED",
        question_path=str(q_path),
        proposal_path=str(p_path),
    )
    runtime = _get_mocked_runtime(config, monkeypatch)
    stub = runtime._stub_response(
        field_state=_get_dummy_field_state(),
        contemplation_result=res,
        pack_grounded_surface="proposal surface",
    )
    assert stub.disposition == "propose", (
        "PROPOSAL_EMITTED terminal must not be reclassified to ask or commit"
    )


def test_disposition_ask_branch_emits_ask(monkeypatch, tmp_path) -> None:
    """The ASK branch must emit disposition='ask' when serving succeeds."""
    config = RuntimeConfig(ask_serving_enabled=True)
    q_path = tmp_path / "q" / "q.json"
    p_path = tmp_path / "p" / "p.json"
    _write_valid_artifact(q_path)
    res = _question_needed_result(q_path, p_path)

    runtime = _get_mocked_runtime(config, monkeypatch)
    stub = runtime._stub_response(
        field_state=_get_dummy_field_state(),
        contemplation_result=res,
        pack_grounded_surface="fallback",
    )
    assert stub.disposition == "ask"


def test_disposition_refused_known_boundary_not_reclassified(monkeypatch, tmp_path) -> None:
    """REFUSED_KNOWN_BOUNDARY must emit disposition='refuse', not 'ask'."""
    config = RuntimeConfig(ask_serving_enabled=True)
    res = DummyContemplationResult(
        terminal="REFUSED_KNOWN_BOUNDARY",
        question_path=None,
        proposal_path=None,
    )
    runtime = _get_mocked_runtime(config, monkeypatch)
    stub = runtime._stub_response(
        field_state=_get_dummy_field_state(),
        contemplation_result=res,
        pack_grounded_surface=None,
    )
    assert stub.disposition == "refuse"


def test_disposition_serialization_backward_compat() -> None:
    """ChatResponse.disposition defaults to '' for pre-disposition callers (byte-identity)."""
    from generate.articulation import ArticulationPlan
    from generate.proposition import Proposition
    from core.physics.identity import CharacterProfile
    import numpy as np

    zero = np.zeros((32,), dtype=np.float32)
    prop = Proposition(
        subject="", predicate="", object_=None,
        surface="", frame_id="",
        subject_versor=zero, predicate_versor=zero, object_versor=None, relation=zero,
    )
    art = ArticulationPlan(
        subject="", predicate="", object=None, surface="",
        output_language="en", frame_id="",
    )
    # Use the correct CharacterProfile fields (traits, drive_summaries, fatigue_index,
    # boundary_commitments, theological_grounding)
    char = CharacterProfile(
        traits={},
        drive_summaries={},
        fatigue_index=0.0,
        boundary_commitments=(),
        theological_grounding={},
    )
    # Construct without disposition field to prove default is ""
    resp = ChatResponse(
        surface="hello",
        proposition=prop,
        articulation=art,
        articulation_surface="hello",
        dialogue_role="assert",
        versor_condition=0.0,
        output_language="en",
        frame_pack="",
        walk_surface="",
        salience_top_k=None,
        candidates_used=None,
        vault_hits=0,
        identity_score=None,
        character_profile=char,
        flagged=False,
    )
    assert resp.disposition == "", (
        "Default ChatResponse.disposition must be '' for backward compatibility"
    )

