"""Deduction-serve arc, Phase 4 / Band v1b (ADR-0256) — categorical decider.

The production categorical decider (`generate/proof_chain/categorical.py`) lowers
a syllogism to the propositional regime and rides the verified ROBDD engine.
These tests pin:

  - it agrees, case-for-case, with the INDEPENDENT finite-model syllogism oracle
    (`evals/syllogism/oracle.py`) across the committed gold lane — two disjoint
    mechanisms converging is the soundness evidence (the decider never imports
    the oracle; INV-25 independence);
  - the modern/Boolean reading (universals lack existential import): valid forms
    are valid, existential-import-only forms are INVALID;
  - inconsistent premises and malformed input are refused, never guessed.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from evals.syllogism.oracle import oracle_answer
from generate.proof_chain.categorical import (
    CategoricalError,
    decide_syllogism,
    syllogism_is_valid,
)
from generate.proof_chain.entail import Entailment

_GOLD = Path(__file__).resolve().parents[1] / "evals" / "syllogism" / "v1" / "cases.jsonl"


def _gold_cases() -> list[dict]:
    return [json.loads(l) for l in _GOLD.read_text(encoding="utf-8").splitlines() if l.strip()]


def test_agrees_with_independent_oracle_on_gold_lane() -> None:
    """Case-for-case agreement with the finite-model oracle AND the committed
    gold — the decider shares no code with either (independent convergence)."""
    cases = _gold_cases()
    assert cases, "syllogism gold lane must not be empty"
    for c in cases:
        mine = syllogism_is_valid(c["structure"], c["query"])
        oracle = oracle_answer(c["structure"], c["query"])["valid"]
        gold = c["gold"]["valid"]
        assert mine == oracle == gold, (
            f"{c['id']}: decider={mine} oracle={oracle} gold={gold} text={c['text']!r}"
        )


def test_barbara_valid() -> None:
    s = {"terms": ["s", "m", "p"], "premises": [
        {"form": "A", "subject": "m", "predicate": "p"},
        {"form": "A", "subject": "s", "predicate": "m"}]}
    q = {"kind": "validity", "conclusion": {"form": "A", "subject": "s", "predicate": "p"}}
    assert syllogism_is_valid(s, q) is True


def test_darapti_invalid_modern_reading() -> None:
    """Darapti (all M are P, all M are S, therefore some S are P) is valid only
    with existential import; in the modern reading it is INVALID (M may be empty)."""
    s = {"terms": ["s", "m", "p"], "premises": [
        {"form": "A", "subject": "m", "predicate": "p"},
        {"form": "A", "subject": "m", "predicate": "s"}]}
    q = {"kind": "validity", "conclusion": {"form": "I", "subject": "s", "predicate": "p"}}
    assert syllogism_is_valid(s, q) is False
    assert decide_syllogism(s, q).outcome is Entailment.UNKNOWN


def test_inconsistent_premises_refused() -> None:
    s = {"terms": ["s", "p"], "premises": [
        {"form": "A", "subject": "s", "predicate": "p"},
        {"form": "E", "subject": "s", "predicate": "p"},
        {"form": "I", "subject": "s", "predicate": "p"}]}
    q = {"kind": "validity", "conclusion": {"form": "A", "subject": "p", "predicate": "s"}}
    assert decide_syllogism(s, q).outcome is Entailment.REFUSED


@pytest.mark.parametrize("bad_structure,bad_query", [
    ({"terms": ["a"], "premises": [{"form": "A", "subject": "a", "predicate": "b"}]},
     {"kind": "validity", "conclusion": {"form": "A", "subject": "a", "predicate": "b"}}),
    ({"terms": ["a", "b"], "premises": [{"form": "Z", "subject": "a", "predicate": "b"}]},
     {"kind": "validity", "conclusion": {"form": "A", "subject": "a", "predicate": "b"}}),
    ({"terms": ["a", "b"], "premises": [{"form": "A", "subject": "a", "predicate": "b"}]},
     {"kind": "sort", "conclusion": {"form": "A", "subject": "a", "predicate": "b"}}),
])
def test_malformed_input_refused(bad_structure, bad_query) -> None:
    with pytest.raises(CategoricalError):
        decide_syllogism(bad_structure, bad_query)
