"""Focused integration tests for the Stage 2 served ASK slice.

Covers the 6 required test cases ensuring gated served ASK, fallback preservation,
unrenderable ask safety, distinct sinks/paths, no prose construction, and governance bus usage.
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
