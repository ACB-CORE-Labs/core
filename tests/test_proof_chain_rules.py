"""ADR-0205 — modus_ponens + disagreement rule (phase 2.3).

The 24 adversarial cases are loaded from the committed contract oracle
(``tests/fixtures/proof_chain/modus_ponens_cases.json``, added in #529) —
GPT-5.5's independent oracle, authored against the ADR-0202/0205 contract and
cross-checked 24/24 against the real rule. This module is the reproducible
cross-check: it runs ``evaluate_modus_ponens`` against the oracle's expected
``(outcome, reason)`` per case. There is no second transcription of the cases
here — the fixture is the single source of truth.

The disagreement cases are the wrong=0 guard — DISAGREE-007/010 in particular
pin the pooling semantics: pool ALL admissible MP derivations and require a
unique key. A filter-to-declared-conclusion-first rule would admit them
(admit-by-assertion); pool-first refuses. Those tests failing under filter-first
is the proof the soundness mechanism is load-bearing.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from generate.proof_chain import (
    CONCLUSION_DISAGREEMENT,
    MP_REASONS,
    Proof,
    ProofNode,
    UNIQUE_CANONICAL_CONCLUSION,
    MPOutcome,
    evaluate_modus_ponens,
    evaluate_proof_conclusion,
)

_CORPUS_PATH = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "proof_chain"
    / "modus_ponens_cases.json"
)


def _load_corpus() -> tuple[dict, list[tuple]]:
    """Load the committed MP oracle into parametrize tuples.

    Each tuple is ``(id, premises, conclusion, expected_outcome, expected_reason)``.
    The corpus's ``expected.reason`` is already the ADR-0205 closed reason set
    (see its ``closed_reasons``), so no label mapping is needed.
    """
    data = json.loads(_CORPUS_PATH.read_text(encoding="utf-8"))
    cases: list[tuple] = []
    for case in data["cases"]:
        sc = case["semantic_content"]
        ex = case["expected"]
        cases.append(
            (
                case["id"],
                tuple(sc["premises"]),
                sc["conclusion"],
                ex["outcome"],
                ex["reason"],
            )
        )
    return data, cases


_CORPUS, CASES = _load_corpus()


def _inputs_for(case_id: str) -> tuple[tuple[str, ...], str]:
    """Return ``(premises, conclusion)`` for a corpus case id.

    Lets the pooling tests below reference oracle cases by id instead of
    re-transcribing their premises — the fixture stays the only source.
    """
    for case in _CORPUS["cases"]:
        if case["id"] == case_id:
            sc = case["semantic_content"]
            return tuple(sc["premises"]), sc["conclusion"]
    raise KeyError(case_id)


def test_corpus_contract_is_the_committed_oracle() -> None:
    """Guard the fixture shape the rest of this file leans on (#529 oracle)."""
    assert len(CASES) == 24, "oracle is the 24-case contract corpus"
    # Every expected reason is in the ADR-0205 closed set, and the corpus's own
    # declared closed set agrees with the rule's MP_REASONS.
    assert {reason for *_, reason in CASES} <= set(MP_REASONS)
    assert set(_CORPUS["closed_reasons"]) == set(MP_REASONS)


@pytest.mark.parametrize(
    "cid,premises,conclusion,outcome,reason",
    CASES,
    ids=[c[0] for c in CASES],
)
def test_corpus_case(cid, premises, conclusion, outcome, reason) -> None:
    v = evaluate_modus_ponens(premises, conclusion)
    assert v.outcome.value == outcome, cid
    assert v.reason == reason, cid
    assert v.reason in MP_REASONS


def test_admit_yields_the_canonical_conclusion_key() -> None:
    from generate.logic_canonical import canonicalize
    v = evaluate_modus_ponens(("P", "P -> Q"), "Q")
    assert v.outcome is MPOutcome.ADMIT
    assert v.conclusion_key == canonicalize("Q").canonical_key


# ---------------------------------------------------------------------------
# The pooling semantics — the wrong=0 mechanism. 007/010 MUST refuse: the premises
# admit deriving a second distinct key, so pool-first refuses. A filter-first rule
# (keep only derivations whose key == declared conclusion, then check uniqueness)
# would admit both — admit-by-assertion. These assertions fail under that mutation.
# Inputs come from the oracle (no re-transcription); the derived_keys counts are
# the extra structural property this corpus case doesn't itself pin.
# ---------------------------------------------------------------------------


def test_pooling_refuses_unrelated_tautology_path() -> None:
    # DISAGREE-007: one path yields T (R or not R), the substantive path yields Q.
    premises, conclusion = _inputs_for("MP-DISAGREE-007")
    v = evaluate_modus_ponens(premises, conclusion)
    assert v.outcome is MPOutcome.REFUSE
    assert v.reason == CONCLUSION_DISAGREEMENT
    assert len(v.derived_keys) == 2  # T and key(Q) — distinct, pooled


def test_pooling_refuses_stronger_conclusion_path() -> None:
    # DISAGREE-010: paths yield Q and (Q and R) — distinct keys.
    premises, conclusion = _inputs_for("MP-DISAGREE-010")
    v = evaluate_modus_ponens(premises, conclusion)
    assert v.outcome is MPOutcome.REFUSE
    assert v.reason == CONCLUSION_DISAGREEMENT
    assert len(v.derived_keys) == 2


def test_equivalent_paths_collapse_not_disagree() -> None:
    # DISAGREE-003: Q->R and (not Q or R) are equivalent → one key → admit.
    premises, conclusion = _inputs_for("MP-DISAGREE-003")
    v = evaluate_modus_ponens(premises, conclusion)
    assert v.outcome is MPOutcome.ADMIT
    assert len(v.derived_keys) == 1


# ---------------------------------------------------------------------------
# Wiring to the ADR-0204 Proof.
# ---------------------------------------------------------------------------


def test_evaluate_proof_conclusion_via_builder_shape() -> None:
    proof = Proof(
        nodes=(
            ProofNode("premise_0", "P", (), "premise"),
            ProofNode("premise_1", "P -> Q", (), "premise"),
            ProofNode("conclusion", "Q", ("premise_0", "premise_1"), "modus_ponens"),
        ),
        conclusion_id="conclusion",
    )
    v = evaluate_proof_conclusion(proof)
    assert v.outcome is MPOutcome.ADMIT
    assert v.reason == UNIQUE_CANONICAL_CONCLUSION
