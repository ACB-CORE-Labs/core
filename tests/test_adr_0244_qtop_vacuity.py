"""ADR-0244 §2.3 Q_top vacuity pins — the proof that ΔQ_top is a hollow gate.

Turns the "likely vacuous" annotation on ADR-0244 §2.3 into a re-runnable proof:
Q_top is identically 0 on the valid versor manifold, only echoes the closure
residual off it, is conserved but empty, and is blind to a versor-preserving
identity attack. Therefore ΔQ_top = 0 must not be an egress admit condition.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import numpy as np

from algebra.rotor import make_rotor_from_angle
from evals.adr_0244_qtop_vacuity import q_top, run_qtop_vacuity_probe

_ROOT = Path(__file__).resolve().parents[1]


def test_qtop_is_identically_zero_on_all_versors() -> None:
    artifact = run_qtop_vacuity_probe()
    assert artifact["versor_count"] >= 20  # rotors + boosts + a product
    # Not "approximately" zero — the grade-5 part of a versor's ψψ̃ is exactly 0.
    assert artifact["versor_worst_abs_qtop"] < artifact["vacuity_tol"]


def test_qtop_only_echoes_grade5_of_the_norm_on_non_versors() -> None:
    artifact = run_qtop_vacuity_probe()
    assert artifact["nonversor_qtop_equals_neg_grade5"] is True
    # The non-versor states that make Q_top nonzero are exactly the ones the
    # closure residual already flags (large, not ~0).
    for case in artifact["nonversor_cases"]:
        assert case["closure_resid"] > 1.0


def test_qtop_is_conserved_under_spin41_conjugation() -> None:
    c = run_qtop_vacuity_probe()["conservation"]
    assert abs(c["versor_before"] - c["versor_after"]) < 1e-12
    assert abs(c["nonversor_before"] - c["nonversor_after"]) < 1e-10


def test_gate_is_blind_to_a_versor_preserving_identity_attack() -> None:
    hg = run_qtop_vacuity_probe()["hollow_gate"]
    # aligned and attacked identity both have Q_top ~ 0 → ΔQ_top = 0 passes...
    assert abs(hg["aligned_qtop"]) < 1e-12
    assert abs(hg["attacked_qtop"]) < 1e-12
    assert hg["delta_qtop"] < 1e-12
    # ...even though the identity demonstrably moved (a leakage check would catch it).
    assert hg["identity_overlap_after_attack"] < 1.0
    assert hg["gate_passes_attack"] is True


def test_overall_verdict_is_proven_vacuous() -> None:
    artifact = run_qtop_vacuity_probe()
    assert artifact["proven_vacuous"] is True
    assert artifact["verdict"] == "hollow_gate_retire_from_egress"


def test_q_top_matches_the_central_pseudoscalar_identity() -> None:
    # Direct sanity: for a versor, Q_top == 0 by centrality of I5; a specific rotor.
    r = make_rotor_from_angle(1.1, 7)
    assert abs(q_top(r)) < 1e-12
    # Non-unit-versor scalar+pseudoscalar carrier: Q_top picks up the grade-5 part.
    psi = np.zeros(32, dtype=np.float64)
    psi[0] = 0.6
    psi[31] = 0.8  # scalar + pseudoscalar (not a versor)
    assert abs(q_top(psi)) > 0.1  # nonzero — it is the pseudoscalar carrier


def test_probe_is_deterministic_and_json_safe() -> None:
    a = json.dumps(run_qtop_vacuity_probe(), sort_keys=True)
    b = json.dumps(run_qtop_vacuity_probe(), sort_keys=True)
    assert a == b
    assert json.loads(a)["proven_vacuous"] is True


def test_probe_is_not_serve_wired() -> None:
    runtime_src = (_ROOT / "chat" / "runtime.py").read_text(encoding="utf-8")
    tree = ast.parse(runtime_src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            assert "adr_0244_qtop_vacuity" not in node.module
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert "adr_0244_qtop_vacuity" not in alias.name
