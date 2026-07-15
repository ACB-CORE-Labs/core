"""ADR-0242 V2 — multi-scale temporal energy basis (research prototype).

Drive formula:

    E_n(t) = E_n(t_0) * exp(-(t - t_0) / (F_n * τ_0))

with Fibonacci scale factors F_n (n ≥ 1) and base time constant τ_0.

This module is **research-only**:
- pure helpers for comparative study vs a dyadic (2^{n-1} τ_0) baseline
- **not** a production default inside ``FieldEnergyOperator.compute``
- serve-quarantined (A-04): must not be imported from ``chat/runtime.py``

Reuses ``fibonacci_number`` / ``fibonacci_tau_schedule`` — no parallel Fibonacci.
"""

from __future__ import annotations

from math import exp, isfinite
from typing import Sequence

from core.physics.fibonacci_search import fibonacci_number
from core.physics.wave_energy_boundary import fibonacci_tau_schedule

_DEFAULT_TAU0 = 1.0


def _validate_tau0(tau0: float) -> float:
    t0 = float(tau0)
    if not (t0 > 0.0) or not isfinite(t0):
        raise ValueError("tau0 must be a positive finite scalar")
    return t0


def _validate_levels(levels: int) -> int:
    n = int(levels)
    if n < 1:
        raise ValueError("levels must be >= 1")
    return n


def _validate_age(age: float) -> float:
    a = float(age)
    if a < 0.0 or not isfinite(a):
        raise ValueError("age must be a non-negative finite scalar")
    return a


def _validate_e0(e0: float) -> float:
    e = float(e0)
    if not isfinite(e):
        raise ValueError("e0 must be a finite scalar")
    return e


def dyadic_tau_schedule(
    tau0: float = _DEFAULT_TAU0,
    *,
    levels: int = 8,
) -> tuple[float, ...]:
    """Dyadic comparison baseline τ_n = 2^{n-1} · τ_0 for n = 1..levels.

    ADR-0242 Phase 2 comparative hypothesis baseline (not a production default).
    """
    t0 = _validate_tau0(tau0)
    n = _validate_levels(levels)
    return tuple(float(t0 * (2 ** (i - 1))) for i in range(1, n + 1))


def multi_scale_energy_for_schedule(
    e0: float,
    age: float,
    taus: Sequence[float],
) -> tuple[float, ...]:
    """Apply E = e0 · exp(-age / τ) for each positive finite τ in ``taus``.

    ``age`` is (t − t_0). ``e0`` is the shared E_n(t_0) research default.
    """
    e = _validate_e0(e0)
    a = _validate_age(age)
    if not taus:
        raise ValueError("taus must be non-empty")
    out: list[float] = []
    for raw in taus:
        tau = float(raw)
        if not (tau > 0.0) or not isfinite(tau):
            raise ValueError("each tau must be a positive finite scalar")
        out.append(float(e * exp(-a / tau)))
    return tuple(out)


def multi_scale_energy_vector(
    e0: float,
    age: float,
    *,
    tau0: float = _DEFAULT_TAU0,
    levels: int = 8,
) -> tuple[float, ...]:
    """Fibonacci multi-scale energies E_n for n = 1..levels.

    Drive form with shared E_n(t_0) = e0:

        E_n = e0 * exp(-age / (F_n * tau0))

    Equivalent to ``multi_scale_energy_for_schedule`` over
    ``fibonacci_tau_schedule(tau0, levels=levels)``.
    """
    t0 = _validate_tau0(tau0)
    n = _validate_levels(levels)
    # Explicit F_n path keeps the Drive formula visible at the callsite layer.
    e = _validate_e0(e0)
    a = _validate_age(age)
    return tuple(
        float(e * exp(-a / float(fibonacci_number(i) * t0)))
        for i in range(1, n + 1)
    )


def comparative_residual_separation(
    e0: float,
    age: float,
    *,
    tau0: float = _DEFAULT_TAU0,
    levels: int = 8,
) -> dict[str, object]:
    """Deterministic Fibonacci vs dyadic multi-scale energy comparison.

    Pure research helper — no I/O. Returns both schedules, both energy
    vectors, and per-index energy gaps (fib − dyadic). Promotion of
    Fibonacci multi-band energy into production requires evidence from
    this (or richer) comparative surface.
    """
    t0 = _validate_tau0(tau0)
    n = _validate_levels(levels)
    fib_taus = fibonacci_tau_schedule(t0, levels=n)
    dyad_taus = dyadic_tau_schedule(t0, levels=n)
    fib_e = multi_scale_energy_for_schedule(e0, age, fib_taus)
    dyad_e = multi_scale_energy_for_schedule(e0, age, dyad_taus)
    gaps = tuple(float(f - d) for f, d in zip(fib_e, dyad_e, strict=True))
    return {
        "tau0": t0,
        "levels": n,
        "age": float(age),
        "e0": float(e0),
        "fibonacci_taus": fib_taus,
        "dyadic_taus": dyad_taus,
        "fibonacci_energies": fib_e,
        "dyadic_energies": dyad_e,
        "energy_gap_fib_minus_dyadic": gaps,
    }


def schedule_mid_span_fraction(taus: Sequence[float], *, index: int | None = None) -> float:
    """Fraction of max(τ) occupied by τ at mid (or given) index.

    Used by comparative pins: Fibonacci mid-scale bands sit further along
    the normalized span than pure dyadic 2^{n-1} (slower φ-growth).
    """
    if not taus:
        raise ValueError("taus must be non-empty")
    vals = tuple(float(t) for t in taus)
    for t in vals:
        if not (t > 0.0) or not isfinite(t):
            raise ValueError("each tau must be a positive finite scalar")
    peak = max(vals)
    i = len(vals) // 2 if index is None else int(index)
    if i < 0 or i >= len(vals):
        raise ValueError("index out of range for taus")
    return float(vals[i] / peak)


__all__ = [
    "comparative_residual_separation",
    "dyadic_tau_schedule",
    "multi_scale_energy_for_schedule",
    "multi_scale_energy_vector",
    "schedule_mid_span_fraction",
]
