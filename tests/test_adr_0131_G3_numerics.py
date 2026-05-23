from __future__ import annotations

import json
from pathlib import Path
import pytest

from generate.math_candidate_parser import (
    extract_initial_candidates,
    _resolve_currency_and_value,
)
from generate.math_candidate_graph import parse_and_solve
from evals.math_capability_axes.G3_numerics.v1.runner import build_report, load_cases

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
_CASES_PATH = _REPO_ROOT / "evals" / "math_capability_axes" / "G3_numerics" / "v1" / "cases.jsonl"


def test_money_literal_parsing() -> None:
    s = "Tina has $18.00."
    candidates = extract_initial_candidates(s)
    assert len(candidates) == 1
    assert candidates[0].initial.quantity.value == 18.0
    assert candidates[0].initial.quantity.unit == "dollars"


def test_fraction_literal_parsing() -> None:
    s = "Jan has 3/4 of a cake."
    candidates = extract_initial_candidates(s)
    assert len(candidates) == 1
    assert candidates[0].initial.quantity.value == 0.75
    assert candidates[0].initial.quantity.unit == "cakes"


def test_word_number_composition_parsing() -> None:
    s = "Francine has five full boxes of crayons."
    candidates = extract_initial_candidates(s)
    assert len(candidates) == 1
    assert candidates[0].initial.quantity.value == 5.0
    assert candidates[0].initial.quantity.unit == "full boxes of crayons"


def test_hyphenated_compound_parsing() -> None:
    s = "Allison has 10 one-hour videos."
    candidates = extract_initial_candidates(s)
    assert len(candidates) == 1
    assert candidates[0].initial.quantity.value == 10.0
    assert candidates[0].initial.quantity.unit == "one-hour videos"


def test_refusal_probes() -> None:
    with pytest.raises(ValueError, match="Too many decimal places"):
        _resolve_currency_and_value("$18.0000")
        
    res = parse_and_solve("Jan has 1/0 of a cake. How many cake does Jan have?")
    assert res.answer is None

    res = parse_and_solve("Sam has one-hour-old baby. How many babies does Sam have?")
    assert res.answer is None
    
    res = parse_and_solve("Marc has 10% of a pizza. How many pizzas does Marc have?")
    assert res.answer is None


def test_runner_and_report_invariants() -> None:
    cases = load_cases(_CASES_PATH)
    report = build_report(cases)
    
    assert report["metrics"]["wrong"] == 0
    assert report["metrics"]["overall_pass"] is True
    
    r1 = build_report(cases)
    r2 = build_report(cases)
    s1 = json.dumps(r1, sort_keys=True, separators=(",", ":"))
    s2 = json.dumps(r2, sort_keys=True, separators=(",", ":"))
    assert s1 == s2
