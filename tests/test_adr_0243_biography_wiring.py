"""ADR-0243 §2.5 Lane C — ADR-0240 harness PASS → integrate_biography wiring.

Covers: live-harness PASS drives a real integration with I-01 asserts and a
provenance record; non-PASS reports must not integrate (fail-closed typed
refusals); the direct-integration ruling is structurally pinned (wiring module
imports no vault store and no evals package).
"""

from __future__ import annotations

import dataclasses
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from algebra.rotor import make_rotor_from_angle
from algebra.versor import versor_condition
from core.physics.biography import BiographyHolonomyBlade, integrate_biography
from core.physics.biography_wiring import (
    BiographyIntegrationError,
    integrate_validated_biography,
)
from evals.analogical_transfer.harness import (
    AnalogicalTransferReport,
    TransferResult,
    make_fixture_pair,
    run_analogical_transfer,
)

_CLOSURE = 1e-6
_ROOT = Path(__file__).resolve().parents[1]


def _trajectory() -> list[np.ndarray]:
    return [make_rotor_from_angle(0.1 * (i + 1), bivector_idx=6 + (i % 3)) for i in range(4)]


def _result(
    case_id: str = "c1",
    *,
    correct: bool = True,
    refused: bool = False,
    reason: str = "transfer_ok",
    residual: float = 0.01,
) -> TransferResult:
    return TransferResult(
        case_id=case_id,
        residual=residual,
        goldtether_before=0.0,
        goldtether_after=0.0,
        correct=correct,
        refused=refused,
        reason=reason,
    )


def _report(results: list[TransferResult]) -> AnalogicalTransferReport:
    counts = {
        "correct": sum(1 for r in results if r.correct),
        "wrong": sum(1 for r in results if not r.correct and not r.refused),
        "refused": sum(1 for r in results if r.refused),
    }
    finite = [r.residual for r in results if np.isfinite(r.residual)]
    return AnalogicalTransferReport(
        results=tuple(results),
        counts=counts,
        max_residual=float(max(finite, default=0.0)),
        wrong=counts["wrong"],
    )


# --- PASS path ----------------------------------------------------------------


def test_live_harness_pass_drives_integration():
    """A real ADR-0240 harness PASS report drives a live integrate_biography call."""
    report = run_analogical_transfer([make_fixture_pair()])
    assert report.wrong == 0 and report.all_correct_or_refused

    traj = _trajectory()
    blade, record = integrate_validated_biography(report, traj)

    # I-01 at the wiring seam (same asserts as test_third_door_cohesion I-01)
    assert blade.closure < _CLOSURE
    assert versor_condition(blade.blade) < _CLOSURE

    assert record.record_id.startswith("bioprov-")
    assert record.schema_version == "biography_provenance_v2"
    assert record.wrong == 0
    assert record.n_cases == 1
    assert record.counts["correct"] == 1
    assert record.case_outcomes == (
        ("fixture-nullcloud-similarity-transfer-v2", "transfer_ok"),
    )
    # Record binds the report to the exact trajectory that was integrated
    assert record.trajectory_hash == integrate_biography(traj).trajectory_hash
    assert record.n_steps == blade.n_steps
    assert record.adr_refs == ("ADR-0240", "ADR-0241", "ADR-0243")
    assert record.closure_proof["blade_closure"] == blade.closure
    # §S2 chiral composition: disclosed, and vacuous-by-theorem on closed versors
    assert record.chiral_proof["latched_sign"] == 0
    assert set(record.chiral_proof["trajectory_verdicts"]) == {"vacuous"}
    assert record.chiral_proof["blade_verdict"] == "vacuous"


def test_provenance_record_deterministic():
    report = run_analogical_transfer([make_fixture_pair()])
    traj = _trajectory()
    _, rec1 = integrate_validated_biography(report, traj)
    _, rec2 = integrate_validated_biography(report, traj)
    assert rec1.record_id == rec2.record_id
    assert rec1.as_dict() == rec2.as_dict()
    assert json.dumps(rec1.as_dict(), sort_keys=True)  # JSONL-serializable


# --- must-reject paths --------------------------------------------------------


def test_wrong_report_refuses():
    report = _report([_result(), _result("c2", correct=False, reason="residual_above_threshold", residual=9.0)])
    assert report.wrong == 1
    with pytest.raises(BiographyIntegrationError) as exc_info:
        integrate_validated_biography(report, _trajectory())
    assert exc_info.value.reason == "report_not_pass"


def test_live_harness_wrong_refuses():
    """A real harness run that produces a wrong must not integrate."""
    case = make_fixture_pair()
    bad = dataclasses.replace(
        case, expected_novel=make_rotor_from_angle(2.0, bivector_idx=8)
    )
    report = run_analogical_transfer([bad])
    assert report.wrong >= 1
    with pytest.raises(BiographyIntegrationError) as exc_info:
        integrate_validated_biography(report, _trajectory())
    assert exc_info.value.reason == "report_not_pass"


def test_all_refused_validates_nothing():
    """wrong == 0 with zero correct transfers validated nothing — refuse."""
    report = _report(
        [
            _result("c1", correct=False, refused=True, reason="refused:x", residual=float("inf")),
            _result("c2", correct=False, refused=True, reason="closure_failed", residual=0.5),
        ]
    )
    assert report.wrong == 0 and report.all_correct_or_refused
    with pytest.raises(BiographyIntegrationError) as exc_info:
        integrate_validated_biography(report, _trajectory())
    assert exc_info.value.reason == "no_validated_transfers"


def test_empty_report_refused():
    with pytest.raises(BiographyIntegrationError) as exc_info:
        integrate_validated_biography(_report([]), _trajectory())
    assert exc_info.value.reason == "empty_report"


def test_bad_trajectory_rejected():
    report = _report([_result()])
    with pytest.raises(BiographyIntegrationError) as exc_info:
        integrate_validated_biography(report, [np.zeros(32, dtype=np.float64)])
    assert exc_info.value.reason == "trajectory_rejected"


def test_i01_violation_fails_closed_at_call_site(monkeypatch):
    """The wiring's own I-01 gate must trip even if the callee returns a bad blade."""
    open_blade = BiographyHolonomyBlade(
        blade=make_rotor_from_angle(0.3),
        n_steps=1,
        trajectory_hash="deadbeef",
        closure=1.0,
    )
    monkeypatch.setattr(
        "core.physics.biography_wiring.integrate_biography",
        lambda trajectory, *, alpha: open_blade,
    )
    with pytest.raises(BiographyIntegrationError) as exc_info:
        integrate_validated_biography(_report([_result()]), _trajectory())
    assert exc_info.value.reason == "i01_closure_violation"


# --- structural pin of the direct-integration ruling --------------------------


def test_wiring_imports_no_vault_store_and_no_evals():
    """Ruling pin: direct integration is legitimate only while the wiring makes
    no durable write and stays layered below evals. If this test breaks, the
    mutation-vs-proposal question reopens — do not weaken it."""
    probe = (
        "import importlib, sys, json;"
        "importlib.import_module('core.physics.biography_wiring');"
        "banned=['core.physics.holographic_vault','evals'];"
        "leaked=sorted(m for m in sys.modules for b in banned if m==b or m.startswith(b+'.'));"
        "print(json.dumps(leaked))"
    )
    result = subprocess.run(
        [sys.executable, "-c", probe],
        cwd=str(_ROOT),
        capture_output=True,
        text=True,
        env={"PYTHONPATH": str(_ROOT), "PATH": ""},
    )
    assert result.returncode == 0, f"probe failed: {result.stderr[-2000:]}"
    leaked = json.loads(result.stdout.strip().splitlines()[-1])
    assert leaked == [], f"biography_wiring loaded banned modules: {leaked}"


# --- §S2 chiral composition (ADR-0241 §2.4C) ----------------------------------


def test_chiral_charge_vanishes_on_closed_versors_theorem():
    """Honesty theorem pin: I₅ is central in odd-dimensional Cl(4,1), so every
    closed versor has Q = ⟨ψ I₅ ψ̃⟩₀ = ±⟨I₅⟩₀ = 0 — the biography chiral
    precondition is vacuous BY THEOREM on admissible trajectories (observed
    exactly 0.0 in-tree). If this pin breaks, the inertness contract in
    chiral_conservation_precondition's docstring must be re-derived."""
    from algebra.null_point import dilator, translator
    from algebra.versor import unitize_versor
    from algebra.cl41 import geometric_product
    from core.physics.wave_manifold import WaveManifold

    wave = WaveManifold()
    versors = [
        make_rotor_from_angle(0.7, bivector_idx=6),
        translator(np.array([0.3, -0.2, 0.5])),
        dilator(1.4),
        unitize_versor(
            geometric_product(
                translator(np.array([0.1, 0.2, 0.3])),
                geometric_product(dilator(1.2), make_rotor_from_angle(0.9, bivector_idx=8)),
            )
        ),
    ]
    for v in versors:
        assert abs(wave.chiral_charge(np.asarray(v, dtype=np.float64))) < 1e-12


def test_chiral_flip_refuses_before_blade_computation():
    """The precondition is LIVE against raw non-versor trajectories: a material
    sgn(Q_top) flip refuses (typed) before versor validation or any blade math."""
    report = _report([_result()])
    plus = np.zeros(32, dtype=np.float64)
    plus[0], plus[31] = 0.8, 0.6  # material Q < 0 for this orientation
    minus = plus.copy()
    minus[31] = -0.6  # mirror image: opposite material Q
    with pytest.raises(BiographyIntegrationError) as exc_info:
        integrate_validated_biography(report, [plus, minus])
    assert exc_info.value.reason == "chiral_orientation_violation"
    assert exc_info.value.disclosure["stage"] == "trajectory[1]"


def test_trajectory_hash_uses_little_endian_f64_bytes():
    """ADR-0245 §2.3 pin: the biography trajectory digest is computed over
    explicit '<f8' bytes (platform-independent replay determinism)."""
    import hashlib

    from core.physics.biography import _trajectory_hash

    traj = _trajectory()
    h = hashlib.sha256()
    for v in traj:
        h.update(np.asarray(v, dtype=np.dtype("<f8")).tobytes())
    assert _trajectory_hash(traj) == h.hexdigest()
