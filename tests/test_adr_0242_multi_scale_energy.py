"""ADR-0242 V2 — multi-scale temporal energy basis (research prototype).

Pins Drive form E_n = E0 · exp(-age / (F_n · τ_0)), dyadic baseline comparison,
determinism, and serve quarantine. Does **not** change FieldEnergyOperator defaults.
"""

from __future__ import annotations

import ast
from math import exp
from pathlib import Path

import pytest

from core.physics.fibonacci_search import fibonacci_number
from core.physics.multi_scale_energy import (
    comparative_residual_separation,
    dyadic_tau_schedule,
    multi_scale_energy_for_schedule,
    multi_scale_energy_vector,
    schedule_mid_span_fraction,
)
from core.physics.wave_energy_boundary import fibonacci_tau_schedule

_ROOT = Path(__file__).resolve().parents[1]


# --- Schedules --------------------------------------------------------------


def test_dyadic_tau_schedule_powers_of_two():
    # τ_n = 2^{n-1} · τ_0 for n = 1..5 → 1, 2, 4, 8, 16 when τ_0=1
    assert dyadic_tau_schedule(tau0=1.0, levels=5) == (1.0, 2.0, 4.0, 8.0, 16.0)
    assert dyadic_tau_schedule(tau0=0.5, levels=4) == (0.5, 1.0, 2.0, 4.0)


def test_dyadic_tau_schedule_rejects_bad_inputs():
    with pytest.raises(ValueError):
        dyadic_tau_schedule(tau0=0.0, levels=3)
    with pytest.raises(ValueError):
        dyadic_tau_schedule(tau0=1.0, levels=0)


def test_fibonacci_tau_matches_fibonacci_number():
    taus = fibonacci_tau_schedule(tau0=1.0, levels=6)
    expected = tuple(float(fibonacci_number(i)) for i in range(1, 7))
    assert taus == expected


# --- Drive energy formula ---------------------------------------------------


def test_multi_scale_energy_vector_matches_drive_formula():
    e0, age, tau0, levels = 2.0, 3.0, 1.0, 5
    got = multi_scale_energy_vector(e0, age, tau0=tau0, levels=levels)
    expected = tuple(
        e0 * exp(-age / (fibonacci_number(i) * tau0)) for i in range(1, levels + 1)
    )
    assert len(got) == levels
    for a, b in zip(got, expected, strict=True):
        assert a == pytest.approx(b, rel=0.0, abs=1e-15)


def test_multi_scale_energy_matches_schedule_helper():
    e0, age, tau0, levels = 1.0, 2.5, 0.5, 6
    via_vector = multi_scale_energy_vector(e0, age, tau0=tau0, levels=levels)
    via_schedule = multi_scale_energy_for_schedule(
        e0, age, fibonacci_tau_schedule(tau0=tau0, levels=levels)
    )
    assert via_vector == via_schedule


def test_decay_larger_age_yields_smaller_energy():
    young = multi_scale_energy_vector(1.0, age=1.0, tau0=1.0, levels=5)
    old = multi_scale_energy_vector(1.0, age=10.0, tau0=1.0, levels=5)
    assert all(o < y for o, y in zip(old, young, strict=True))
    # age=0 → full e0 at every scale
    zero = multi_scale_energy_vector(1.25, age=0.0, tau0=1.0, levels=4)
    assert zero == (1.25, 1.25, 1.25, 1.25)


def test_larger_tau_scale_retains_more_energy():
    # Within a Fibonacci vector, coarser scales (larger F_n) decay slower.
    vec = multi_scale_energy_vector(1.0, age=5.0, tau0=1.0, levels=8)
    # F_1=1, F_8=21 → last component strictly larger residual energy
    assert vec[-1] > vec[0]


def test_multi_scale_energy_rejects_bad_inputs():
    with pytest.raises(ValueError):
        multi_scale_energy_vector(1.0, age=-1.0)
    with pytest.raises(ValueError):
        multi_scale_energy_vector(float("nan"), age=1.0)
    with pytest.raises(ValueError):
        multi_scale_energy_for_schedule(1.0, 1.0, ())
    with pytest.raises(ValueError):
        multi_scale_energy_for_schedule(1.0, 1.0, (1.0, 0.0))


# --- Determinism + comparative surface --------------------------------------


def test_deterministic_dual_run():
    kwargs = dict(e0=1.0, age=4.0, tau0=1.0, levels=8)
    a = multi_scale_energy_vector(**kwargs)
    b = multi_scale_energy_vector(**kwargs)
    assert a == b
    ca = comparative_residual_separation(**kwargs)
    cb = comparative_residual_separation(**kwargs)
    assert ca == cb


def test_fibonacci_bands_longer_than_dyadic_mid_scale():
    """Mid-scale Fibonacci bands occupy a larger fraction of total span.

    Absolute τ: F_n grows as ~φ^n while dyadic is 2^{n-1}, so dyadic absolute
    τ is larger late. Comparatively, φ-growth places the mid-index band further
    along the *normalized* hierarchy (span fraction) than pure dyadic — the
    structural property the V2 research pin checks.
    """
    levels = 8
    tau0 = 1.0
    fib = fibonacci_tau_schedule(tau0=tau0, levels=levels)
    dyad = dyadic_tau_schedule(tau0=tau0, levels=levels)
    mid = levels // 2
    fib_frac = schedule_mid_span_fraction(fib, index=mid)
    dyad_frac = schedule_mid_span_fraction(dyad, index=mid)
    assert fib_frac > dyad_frac
    # Absolute mid τ still follows F_5=5 vs 2^4=16
    assert fib[mid] == 5.0
    assert dyad[mid] == 16.0


def test_comparative_residual_separation_shape():
    report = comparative_residual_separation(1.0, age=3.0, tau0=1.0, levels=5)
    assert report["levels"] == 5
    assert len(report["fibonacci_taus"]) == 5
    assert len(report["dyadic_taus"]) == 5
    assert len(report["fibonacci_energies"]) == 5
    assert len(report["dyadic_energies"]) == 5
    assert len(report["energy_gap_fib_minus_dyadic"]) == 5
    # age=0 → identical unit energies regardless of schedule
    zero = comparative_residual_separation(1.0, age=0.0, tau0=1.0, levels=4)
    assert zero["fibonacci_energies"] == (1.0, 1.0, 1.0, 1.0)
    assert zero["dyadic_energies"] == (1.0, 1.0, 1.0, 1.0)
    assert zero["energy_gap_fib_minus_dyadic"] == (0.0, 0.0, 0.0, 0.0)


# --- Serve quarantine (A-04) ------------------------------------------------


def test_serve_runtime_does_not_import_multi_scale_energy():
    tree = ast.parse((_ROOT / "chat/runtime.py").read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            assert "multi_scale_energy" not in node.module
            assert "wave_energy_boundary" not in node.module
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert "multi_scale_energy" not in alias.name


def test_field_energy_operator_untouched_by_multi_scale_module():
    """Production energy operator must not import the research multi-scale path."""
    energy_src = (_ROOT / "core/physics/energy.py").read_text(encoding="utf-8")
    assert "multi_scale_energy" not in energy_src
    assert "fibonacci_tau_schedule" not in energy_src
