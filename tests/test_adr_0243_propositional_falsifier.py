"""ADR-0243 Phase 4 — decisive falsifier test (field decoder vs ROBDD gold).

The load-bearing evidence of the arc: the Cl(4,1) field relaxation decoder must
agree with the independent ROBDD gold on every satisfiable-premise propositional
problem in the enumerated panel (``wrong == 0``), match its refusal on
inconsistent premises, and honestly refuse out-of-regime (> 5-atom) problems the
gold still decides. A single ID divergence would confirm the field engine is not
the reasoner on this domain.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

from evals.adr_0243_cognitive_lifecycle.propositional_falsifier import (
    render_clause,
    run_propositional_falsifier,
)
from generate.proof_chain.entail import Entailment, evaluate_entailment

_ROOT = Path(__file__).resolve().parents[1]


def test_render_clause_matches_gold_syntax():
    assert render_clause((("a", True),)) == "a"
    assert render_clause((("a", False),)) == "~a"
    assert render_clause((("a", True), ("b", False), ("c", True))) == "a | ~b | c"


def test_field_decoder_matches_robdd_gold_wrong_zero():
    """Decisive falsifier: zero field-vs-gold divergence over the panel."""
    artifact = run_propositional_falsifier()
    # Both comparison lanes are actually exercised (not a vacuous pass).
    assert artifact["id_case_count"] > 0
    assert artifact["refusal_parity_count"] > 0
    # The load-bearing assertion.
    assert artifact["wrong"] == 0, (
        f"field decoder diverged from ROBDD gold: "
        f"id_disagreements={artifact['id_disagreements'][:3]} "
        f"refusal_mismatches={artifact['refusal_parity_mismatches'][:3]}"
    )
    assert artifact["id_disagreements"] == []
    assert artifact["refusal_parity_mismatches"] == []


def test_out_of_regime_is_field_refused_but_gold_decidable():
    """ID/OOD scope boundary: > 5 atoms → field refuses, gold still decides."""
    artifact = run_propositional_falsifier()
    assert artifact["ood_field_refused"] is True
    assert artifact["ood_gold_decided"] is True


def test_falsifier_artifact_is_deterministic_and_json_safe():
    a = json.dumps(run_propositional_falsifier(), sort_keys=True)
    b = json.dumps(run_propositional_falsifier(), sort_keys=True)
    assert a == b
    assert json.loads(a)["wrong"] == 0


def test_gold_is_a_genuinely_independent_mechanism():
    """Sanity that the gold decides these canonical patterns as expected —
    it is the ROBDD tautology check, not the field decoder in disguise."""
    # modus ponens: (a→b) i.e. (~a | b), and a  ⊨ b
    assert evaluate_entailment(("~a | b", "a"), "b").outcome is Entailment.ENTAILED
    # p ∨ q ⊭ p
    assert evaluate_entailment(("a | b",), "a").outcome is Entailment.UNKNOWN
    # inconsistent premises refuse (no ex-falso)
    assert evaluate_entailment(("a", "~a"), "b").outcome is Entailment.REFUSED


def test_falsifier_is_not_serve_wired():
    """Off-serving: chat/runtime.py must never import this eval package."""
    runtime_src = (_ROOT / "chat" / "runtime.py").read_text(encoding="utf-8")
    tree = ast.parse(runtime_src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            assert "adr_0243_cognitive_lifecycle" not in node.module
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert "adr_0243_cognitive_lifecycle" not in alias.name
