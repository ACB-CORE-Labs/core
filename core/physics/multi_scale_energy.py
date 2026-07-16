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

from dataclasses import dataclass
from math import exp, isfinite, log
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


def log_tau_schedule(
    tau0: float = _DEFAULT_TAU0,
    *,
    levels: int = 8,
) -> tuple[float, ...]:
    """Logarithmic comparison baseline τ_n = τ_0 · ln(n + 1) for n = 1..levels.

    ADR-0242 V2 third comparative baseline (with Fibonacci and dyadic).
    Research-only — not a production default. ln(n+1) is strictly positive
    and monotone for n ≥ 1.
    """
    t0 = _validate_tau0(tau0)
    n = _validate_levels(levels)
    return tuple(float(t0 * log(i + 1)) for i in range(1, n + 1))


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


def comparative_three_way(
    e0: float,
    age: float,
    *,
    tau0: float = _DEFAULT_TAU0,
    levels: int = 8,
) -> dict[str, object]:
    """Fixed-replay Fibonacci vs dyadic vs log multi-scale comparison.

    Pure research helper — no I/O, no production promotion. Extends the
    two-way residual separation with the logarithmic baseline. Joshua gate
    required before any of these schedules becomes a FieldEnergyOperator default.
    """
    t0 = _validate_tau0(tau0)
    n = _validate_levels(levels)
    two = comparative_residual_separation(e0, age, tau0=t0, levels=n)
    log_taus = log_tau_schedule(t0, levels=n)
    log_e = multi_scale_energy_for_schedule(e0, age, log_taus)
    fib_e = two["fibonacci_energies"]
    assert isinstance(fib_e, tuple)
    return {
        **two,
        "log_taus": log_taus,
        "log_energies": log_e,
        "energy_gap_fib_minus_log": tuple(
            float(f - lg) for f, lg in zip(fib_e, log_e, strict=True)
        ),
        "schedules": ("fibonacci", "dyadic", "log"),
        "promotion_status": "research_only",
        "joshua_gate_required": True,
    }


def fixed_replay_compare_artifact(
    *,
    e0: float = 1.0,
    ages: Sequence[float] = (0.0, 1.0, 3.0, 8.0),
    tau0: float = _DEFAULT_TAU0,
    levels: int = 8,
) -> dict[str, object]:
    """Deterministic multi-age comparative artifact for V2 evidence records.

    Pure: returns a JSON-serializable dict. Callers may write it to disk for
    audit; this function itself performs no I/O and does not touch production
    energy operators.
    """
    rows = [
        comparative_three_way(e0, float(age), tau0=tau0, levels=levels)
        for age in ages
    ]
    return {
        "artifact": "adr_0242_v2_energy_compare",
        "schema_version": 1,
        "e0": float(e0),
        "tau0": float(tau0),
        "levels": int(levels),
        "ages": tuple(float(a) for a in ages),
        "rows": rows,
        "promotion_status": "research_only",
        "joshua_gate_required": True,
        "production_default_unchanged": True,
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


# --- ADR-0242 §5-P2: F5–F7 cross-band surprise persistence gate ---------------
#
# "Emits a DiscoveryCandidate in the contemplation loop *only* when the
# surprise signal persists across multiple Fibonacci-scaled temporal bands
# (F5 to F7), preventing transient noise from triggering ungrounded updates."
#
# Pure verdict function for the contemplation loop — PROPOSAL-side only.
# Lives here (Tier-2, serve-quarantined) so the gate can never touch serving.

_DISCOVERY_BANDS: tuple[int, int, int] = (5, 8, 13)  # F_5, F_6, F_7


@dataclass(frozen=True, slots=True)
class CrossBandVerdict:
    """Typed persistence verdict; never emits or promotes anything itself."""

    eligible: bool
    bands: tuple[int, int, int]
    band_energies: tuple[float, float, float]
    gamma: float
    reason: str  # "eligible" | "insufficient_span" | "band_below_gamma"


def cross_band_discovery_gate(
    events: Sequence[tuple[float, float]],
    *,
    now: float,
    tau0: float = _DEFAULT_TAU0,
    gamma: float,
) -> CrossBandVerdict:
    """Persistence gate over a surprise-event history.

    ``events`` are ``(t, energy)`` samples with ``t <= now`` and
    ``energy >= 0``. Each band accumulates decay-weighted surprise

        E_band(now) = Σ_i energy_i · exp(-(now - t_i) / (F_band · τ0))

    Eligible ⇔ the history spans at least the shortest band (F_5·τ0 —
    a single fresh spike carries full weight in every band but has zero
    temporal persistence) AND every band's accumulation ≥ ``gamma``.
    Deterministic and pure; the caller (contemplation loop) decides whether
    to emit a DiscoveryCandidate.
    """
    if not events:
        raise ValueError("cross_band_discovery_gate: empty event history")
    tau0 = _validate_tau0(tau0)
    if not isfinite(gamma) or gamma <= 0.0:
        raise ValueError("gamma must be finite and > 0")
    times = []
    for t, e in events:
        t = float(t)
        e = float(e)
        if not (isfinite(t) and isfinite(e)):
            raise ValueError("event times/energies must be finite")
        if e < 0.0:
            raise ValueError(f"negative surprise energy {e} at t={t}")
        if t > float(now):
            raise ValueError(f"event at t={t} is after now={now}")
        times.append(t)

    band_energies = tuple(
        sum(
            float(e) * exp(-(float(now) - float(t)) / (band * tau0))
            for t, e in events
        )
        for band in _DISCOVERY_BANDS
    )

    span = max(times) - min(times)
    if span < _DISCOVERY_BANDS[0] * tau0:
        return CrossBandVerdict(
            eligible=False,
            bands=_DISCOVERY_BANDS,
            band_energies=band_energies,  # type: ignore[arg-type]
            gamma=float(gamma),
            reason="insufficient_span",
        )
    if any(e < gamma for e in band_energies):
        return CrossBandVerdict(
            eligible=False,
            bands=_DISCOVERY_BANDS,
            band_energies=band_energies,  # type: ignore[arg-type]
            gamma=float(gamma),
            reason="band_below_gamma",
        )
    return CrossBandVerdict(
        eligible=True,
        bands=_DISCOVERY_BANDS,
        band_energies=band_energies,  # type: ignore[arg-type]
        gamma=float(gamma),
        reason="eligible",
    )


__all__ = [
    "CrossBandVerdict",
    "comparative_residual_separation",
    "comparative_three_way",
    "cross_band_discovery_gate",
    "dyadic_tau_schedule",
    "fixed_replay_compare_artifact",
    "log_tau_schedule",
    "multi_scale_energy_for_schedule",
    "multi_scale_energy_vector",
    "schedule_mid_span_fraction",
]
