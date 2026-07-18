"""ADR-0244 §2.4 / D4 Phase 3 — pins the γ_id leakage-bound calibration.

Verifies the bracketed-local Fibonacci search certifies a leakage bound that
separates the geometric attack signal, that the certified γ* is the value pinned
as ``identity._WAVE_LEAKAGE_BOUND``, and — the honest part — that the same bound
does NOT separate real benign traffic, so ``flag_flip_authorized`` is False and
``identity_wave_gate`` stays OFF.
"""

from __future__ import annotations

import json
import subprocess
import sys

import pytest

from core.physics.fibonacci_search import FibonacciSearchCertificate
from core.physics.identity import _WAVE_LEAKAGE_BOUND
from evals.adr_0244_gamma_calibration import (
    LIVE_BENIGN_LEAKAGE_REFERENCE,
    calibrate_leakage_bound,
    collect_live_benign_leakages,
    leakage_separation_objective,
    reference_leakages,
    run_gamma_calibration,
)


def test_search_returns_a_certificate_not_a_failure():
    # The logistic-separation objective is convex → the sampled sequence is
    # down-then-up → no sampled_unimodality_violation.
    result = calibrate_leakage_bound()
    assert isinstance(result, FibonacciSearchCertificate), getattr(
        result, "reason", result
    )
    assert result.objective_id == "gamma_id_leakage"


def test_certified_gamma_matches_the_pinned_constant():
    # Lock: the wave-gate constant IS the certified minimiser (no drift between
    # the calibration and the pinned bound the live gate would use).
    result = calibrate_leakage_bound()
    assert isinstance(result, FibonacciSearchCertificate)
    assert result.minimizer == pytest.approx(_WAVE_LEAKAGE_BOUND, abs=1e-9)


def test_gamma_separates_the_geometric_reference_set():
    art = run_gamma_calibration()
    geo = art["geometric_reference"]
    assert geo["aligned_all_admitted"] is True
    assert geo["attacks_all_flagged"] is True
    assert geo["separates"] is True
    assert art["verdict"]["geometric_calibration_valid"] is True


def test_objective_is_convex_unimodal_shape():
    id_leaks, adv_leaks = reference_leakages()
    cost = leakage_separation_objective(id_leaks, adv_leaks)
    gamma = _WAVE_LEAKAGE_BOUND
    # the minimiser sits below every attack and at/above every aligned leakage
    assert max(id_leaks) <= gamma < min(adv_leaks)
    # cost rises on both sides of the certified minimiser (local unimodality)
    assert cost(gamma) < cost(gamma - 0.1)
    assert cost(gamma) < cost(gamma + 0.1)


def test_live_traffic_is_not_separable_flag_flip_blocked():
    art = run_gamma_calibration()
    live = art["live_evaluation"]
    # benign leakage overlaps the attack range and most benign turns would be
    # false-refused at γ* — the honest Phase-3 finding.
    assert live["benign_overlaps_attacks"] is True
    assert live["benign_false_refused_at_gamma_star"] >= len(LIVE_BENIGN_LEAKAGE_REFERENCE) - 1
    assert live["best_achievable_balanced_error"] > 0.2
    assert live["live_separation"] is False
    assert art["verdict"]["flag_flip_authorized"] is False


def test_run_is_deterministic():
    assert run_gamma_calibration() == run_gamma_calibration()


def test_cli_exit_zero_and_reports_flip_not_authorized():
    proc = subprocess.run(
        [sys.executable, "-m", "evals.adr_0244_gamma_calibration"],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    # exit 0 == certificate valid, but the payload must not claim a live flip.
    assert payload["verdict"]["geometric_calibration_valid"] is True
    assert payload["verdict"]["flag_flip_authorized"] is False


def test_eval_is_off_serving():
    import inspect

    import chat.runtime

    src = inspect.getsource(chat.runtime)
    assert "adr_0244_gamma_calibration" not in src


@pytest.mark.slow
def test_live_probe_matches_pin_and_still_overlaps_attacks():
    # Drift guard: if the engine ever starts preserving span(e1,e2,e3), the live
    # benign leakage would fall and this fails — signalling "re-calibrate and
    # reconsider the flag flip". Slow: it spins up a fresh ChatRuntime.
    measured = collect_live_benign_leakages()
    assert measured == list(LIVE_BENIGN_LEAKAGE_REFERENCE)
    _, adv_leaks = reference_leakages()
    assert max(measured) >= min(adv_leaks)  # benign still overlaps attacks
