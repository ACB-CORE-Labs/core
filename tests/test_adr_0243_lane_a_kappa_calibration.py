"""ADR-0243 Phase 3 Lane A — live `propose_kappa_line_search` caller.

`propose_kappa_line_search` (ADR-0242 §5-P1) and its internal
`kappa_search_event` emission had zero live call sites — the seam was
tested but nothing invoked it.  `calibrate_transfer_kappa` gives it a
live caller confined to the ADR-0240 analogical-transfer calibration
pipeline (R-04: trace generation is limited strictly to calibration and
training-loop pipelines; never a hot/serve path).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from evals.analogical_transfer.harness import make_fixture_pair
from evals.analogical_transfer.kappa_calibration import calibrate_transfer_kappa

_ROOT = Path(__file__).resolve().parents[1]


class _CaptureSink:
    def __init__(self) -> None:
        self.lines: list[str] = []

    def emit(self, line: str) -> None:
        self.lines.append(line)


def test_calibration_fires_kappa_search_event_on_sink() -> None:
    sink = _CaptureSink()
    report = calibrate_transfer_kappa(sink=sink)
    assert len(sink.lines) == 1
    event = json.loads(sink.lines[0])
    assert event["kind"] == "fibonacci_kappa_search"
    assert event["kappa"] == pytest.approx(report["proposed_kappa"])
    assert report["event"] == event


def test_calibration_report_shape_and_bounds() -> None:
    report = calibrate_transfer_kappa()
    assert report["kind"] == "analogical_transfer_kappa_calibration"
    assert report["case_count"] == 1
    assert report["refused_case_count"] == 0
    assert report["event"]["result"]["objective_id"] == "analogical_transfer_kappa"
    assert 0.1 <= report["proposed_kappa"] <= 2.0
    assert np.isfinite(report["max_procrustes_residual"])
    # JSONL-ready without custom encoders.
    assert json.loads(json.dumps(report, sort_keys=True)) == report


def test_calibration_without_sink_is_pure() -> None:
    sink = _CaptureSink()
    with_sink = calibrate_transfer_kappa(sink=sink)
    without_sink = calibrate_transfer_kappa()
    assert with_sink == without_sink
    assert len(sink.lines) == 1


def test_calibration_deterministic() -> None:
    assert calibrate_transfer_kappa() == calibrate_transfer_kappa()


def test_empty_cases_fail_closed() -> None:
    with pytest.raises(ValueError):
        calibrate_transfer_kappa(cases=())


def test_all_inadmissible_cases_fail_closed() -> None:
    """Cases whose Procrustes residual is not measurable cannot calibrate."""
    base = make_fixture_pair()
    poisoned = base.__class__(
        case_id="poisoned",
        source_domain=base.source_domain,
        target_domain=base.target_domain,
        source=[np.full(32, np.nan)],
        target=[np.full(32, np.nan)],
        novel_query=base.novel_query,
        expected_novel=base.expected_novel,
    )
    with pytest.raises(ValueError):
        calibrate_transfer_kappa(cases=(poisoned,))


def test_calibration_module_stays_off_serve() -> None:
    """R-04 confinement: chat.runtime never loads the calibration caller."""
    probe = (
        "import importlib, sys;"
        "importlib.import_module('chat.runtime');"
        "print('LEAK' if any(m.startswith('evals.analogical_transfer')"
        " for m in sys.modules) else 'CLEAN')"
    )
    out = subprocess.run(
        [sys.executable, "-c", probe],
        cwd=str(_ROOT),
        capture_output=True,
        text=True,
        env={"PYTHONPATH": str(_ROOT), "PATH": ""},
    )
    assert out.returncode == 0, out.stderr[-500:]
    assert out.stdout.strip().splitlines()[-1] == "CLEAN"
