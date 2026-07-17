"""ADR-0243 Phase 4 — falsifiability benchmark tests (plan §5 Phase 4).

Pins that the lifecycle passes every falsifiable metric, that each metric is
actually exercised (not a vacuous pass), that the f32/f64 drift gap is real
evidence (both are not silently zero), that the CLI dispatcher routes and
signals failure by exit code, and that the eval stays off the serve path.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from evals.adr_0243_cognitive_lifecycle import benchmark as bench
from evals.adr_0243_cognitive_lifecycle.__main__ import main

_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def verdict() -> bench.BenchmarkVerdict:
    return bench.run_benchmark()


def _metric(verdict: bench.BenchmarkVerdict, name: str) -> bench.MetricResult:
    for m in verdict.metrics:
        if m.name == name:
            return m
    raise AssertionError(f"metric {name!r} absent from verdict")


def test_overall_benchmark_passes(verdict: bench.BenchmarkVerdict) -> None:
    """The load-bearing gate: every falsifiable metric passes on the lifecycle."""
    assert verdict.overall_passed is True
    names = {m.name for m in verdict.metrics}
    assert names == {
        "fidelity",
        "surprise_separation",
        "insertion_cost",
        "f32_drift",
        "falsifier",
    }
    assert all(m.passed for m in verdict.metrics)


def test_fidelity_decodes_near_perfect(verdict: bench.BenchmarkVerdict) -> None:
    m = _metric(verdict, "fidelity")
    assert m.detail["n_cases"] > 0
    assert m.detail["min_fidelity"] >= bench.FIDELITY_MIN


def test_surprise_separates_id_from_ood(verdict: bench.BenchmarkVerdict) -> None:
    m = _metric(verdict, "surprise_separation")
    # Strict, margined separation — every OOD field sits above every ID field.
    assert m.detail["separation"] > bench.SURPRISE_MIN_SEPARATION
    assert m.detail["min_ood_energy"] > m.detail["max_id_energy"]
    # The well's ground energy must actually be ~0 (verified, not assumed).
    assert abs(m.detail["lam0"]) <= 1e-9


def test_insertion_cost_bounded_and_certified(verdict: bench.BenchmarkVerdict) -> None:
    m = _metric(verdict, "insertion_cost")
    assert m.detail["all_converged"] is True
    # Real decoding work happened (not a start-already-at-ground no-op)...
    assert m.detail["max_steps_taken"] > 0
    # ...and it stayed bounded.
    assert m.detail["max_steps_taken"] <= bench.INSERTION_STEP_BOUND


def test_f32_drift_gap_is_real_evidence(verdict: bench.BenchmarkVerdict) -> None:
    """f64 holds versor closure tight; f32 truncates measurably (the gap is the point)."""
    m = _metric(verdict, "f32_drift")
    assert m.detail["steps"] == bench.DRIFT_STEPS
    # f64 substrate holds closure to the shipped bound.
    assert m.detail["f64_max_versor_residual"] <= bench.F64_DRIFT_MAX
    assert m.detail["f64_max_norm_dev"] <= bench.F64_DRIFT_MAX
    # f32 is not silently zero — the truncation gap is genuine, motivating the
    # serving-boundary cast (ADR-0244 §2.5) and f64 fast-path (§2.6).
    assert m.detail["f32_max_versor_residual"] > m.detail["f64_max_versor_residual"]
    assert m.detail["f32_over_f64_residual_ratio"] > 1_000.0


def test_falsifier_wrong_zero(verdict: bench.BenchmarkVerdict) -> None:
    m = _metric(verdict, "falsifier")
    assert m.detail["wrong"] == 0
    assert m.detail["id_case_count"] > 0
    assert m.detail["refusal_parity_count"] > 0
    assert m.detail["ood_field_refused"] is True
    assert m.detail["ood_gold_decided"] is True


def test_verdict_is_deterministic_and_json_safe() -> None:
    a = json.dumps(bench.run_benchmark().as_dict(), sort_keys=True)
    b = json.dumps(bench.run_benchmark().as_dict(), sort_keys=True)
    assert a == b
    assert json.loads(a)["overall_passed"] is True


def test_cli_benchmark_default_and_exit_code() -> None:
    # No subcommand → benchmark (default); passing gate → exit 0.
    assert main([]) == 0
    assert main(["benchmark"]) == 0


def test_cli_writes_artifact(tmp_path: Path) -> None:
    out = tmp_path / "artifact.json"
    assert main(["benchmark", "--out", str(out)]) == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["kind"] == "ADR0243BenchmarkVerdict"
    assert payload["overall_passed"] is True


def test_cli_falsifier_and_corridor_subcommands(tmp_path: Path) -> None:
    fout = tmp_path / "falsifier.json"
    assert main(["falsifier", "--out", str(fout)]) == 0
    assert json.loads(fout.read_text(encoding="utf-8"))["wrong"] == 0

    cout = tmp_path / "corridor.json"
    assert main(["corridor", "--out", str(cout)]) == 0
    corridor = json.loads(cout.read_text(encoding="utf-8"))
    assert corridor["outcome_id"]  # non-empty content-addressed id


def test_benchmark_is_not_serve_wired() -> None:
    """Off-serving: chat/runtime.py must never import this eval package."""
    runtime_src = (_ROOT / "chat" / "runtime.py").read_text(encoding="utf-8")
    tree = ast.parse(runtime_src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            assert "adr_0243_cognitive_lifecycle" not in node.module
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert "adr_0243_cognitive_lifecycle" not in alias.name
