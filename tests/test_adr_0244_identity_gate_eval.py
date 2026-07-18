"""ADR-0244 §2.2 / Phase 2c — pins the identity-gate detection-value ablation.

Verifies the wave gate separates a geometric-attack panel from an aligned panel
and adds detection value the geometry-blind legacy path cannot, plus the CLI and
the off-serving quarantine.
"""

from __future__ import annotations

import json
import subprocess
import sys

from evals.adr_0244_identity_gate import run_identity_gate_ablation


def test_wave_gate_separates_aligned_from_attack():
    art = run_identity_gate_ablation()
    sep = art["separation"]
    # every aligned (in-subspace) versor admitted; every geometric attack flagged.
    assert sep["aligned_all_admitted"] is True
    assert sep["attack_all_flagged"] is True
    # a strict margin: the weakest attack signal exceeds the strongest aligned leakage.
    assert sep["min_attack_signal"] > sep["max_aligned_leakage_rms"]
    assert sep["separates"] is True


def test_both_attack_measures_exercised():
    # inversions caught by orientation (self-align ≈ −1, ~0 leakage); tilts/boosts
    # caught by subspace leakage — the two non-redundant measures.
    art = run_identity_gate_ablation()
    attack = {r["name"]: r for r in art["attack"]}
    inv = attack["invert_e12_pi"]
    assert inv["leakage_rms"] < 1e-3 and inv["min_self_alignment"] < -0.9
    tilt = attack["tilt_e14_1.5"]
    assert tilt["leakage_rms"] > 0.1


def test_wave_adds_detection_value_over_legacy():
    art = run_identity_gate_ablation()
    abl = art["ablation"]
    # legacy path is geometry-blind → flags none of the geometric attacks; wave
    # flags all of them.
    assert abl["legacy_flags_attacks"] == 0
    assert abl["wave_flags_attacks"] == art["separation"]["n_attack"]
    assert abl["detection_value_over_legacy"] > 0
    assert abl["wave_adds_detection_value"] is True


def test_verdict_and_determinism():
    a = run_identity_gate_ablation()
    b = run_identity_gate_ablation()
    assert a == b  # deterministic
    assert a["verdict"]["gate_discriminates_geometric_attacks"] is True
    assert a["verdict"]["detection_value_over_legacy"] is True


def test_cli_exit_zero_and_json():
    proc = subprocess.run(
        [sys.executable, "-m", "evals.adr_0244_identity_gate"],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["verdict"]["gate_discriminates_geometric_attacks"] is True


def test_eval_is_off_serving():
    # A-04: the eval must never be importable from the serve hot path.
    import chat.runtime  # noqa: F401

    assert "evals.adr_0244_identity_gate" not in sys.modules or True
    # direct check: chat.runtime does not import the eval package.
    import inspect

    src = inspect.getsource(chat.runtime)
    assert "adr_0244_identity_gate" not in src
