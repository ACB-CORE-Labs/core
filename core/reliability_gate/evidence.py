"""ADR-0264 R9 — distinct-evidence audit: the precondition :func:`conservative_floor` assumes.

:func:`core.reliability_gate.floor.conservative_floor` is a one-sided Wilson lower
bound on a success proportion. Wilson assumes **independent trials**. CORE's
pipeline is deterministic by construction — that is the whole thesis — so
replaying an identical input yields the identical outcome with certainty. Two
identical cases in a practice ledger are therefore perfectly correlated, not
independent, and contribute one trial's worth of evidence between them, not two.

So a ledger's ``committed`` count is an upper bound on its evidence, and the
honest figure is the count of *distinct decisions* it exercised. This module
computes both and reports the gap. It is deliberately a pure measurement with no
authority: it never edits a ledger, never gates anything, and nothing in the
serving path imports it. What to do about a gap is a ratification decision.

Why this exists as code rather than a note: S6 predicted the exposure in the
abstract (`docs/research/curriculum-volume-quantification-2026-07-24.md` §1 —
``conservative_floor`` cannot distinguish "657 independent facts" from "16 facts
asked 41 times"). It was then measured in the *live, ratified* deduction ledger,
where 21 of 25 bands do not clear θ_SERVE on distinct evidence. A prediction that
has come true needs an instrument, not a second warning.

**The key is supplied by the caller, and must be conservative.** A decision key
identifies what the pipeline actually decided. Case *text* is the safe default:
two cases with identical text are indisputably the same decision. A tighter key
(e.g. the normalized propositional atom, which collapses spelling variants of one
question) reports *more* inflation. Text-identity therefore under-reports, which
is the correct direction for a claim of this kind — the measured gap is a floor on
the real gap, never an exaggeration of it.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Hashable, Iterable
from dataclasses import dataclass

from core.reliability_gate.floor import conservative_floor

#: The committed volume a *perfect* record needs to clear θ=0.99 under the pinned
#: ``WILSON_Z``. Derived, not chosen: the bound for ``successes == committed``
#: reduces to ``n / (n + z²)``, so ``n / (n + 6.635776) ≥ 0.99`` ⟺ ``n ≥ 656.93``.
#: Recomputed by :func:`volume_for_theta` rather than trusted as a constant.
SERVE_VOLUME_AT_THETA_099: int = 657


def volume_for_theta(theta: float) -> int:
    """Smallest perfect-record volume whose conservative floor reaches *theta*.

    Derives the figure from :func:`conservative_floor` itself instead of
    restating it, so a change to ``WILSON_Z`` cannot leave a stale number behind
    in a docstring or a test. Search, not algebra, because the bound is rounded
    to 1e-9 and the comparison downstream is the rounded one.
    """
    if not 0.0 < theta < 1.0:
        raise ValueError(f"theta must lie in (0, 1); got {theta!r}")
    n = 1
    while conservative_floor(n, n) < theta:
        n *= 2
        if n > 1 << 40:  # pragma: no cover - unreachable for theta < 1
            raise ValueError(f"no finite volume reaches theta={theta!r}")
    low, high = n // 2, n
    while low < high:
        mid = (low + high) // 2
        if conservative_floor(mid, mid) >= theta:
            high = mid
        else:
            low = mid + 1
    return low


@dataclass(frozen=True, slots=True)
class EvidenceAudit:
    """What one band's practice volume is worth as evidence.

    ``claimed`` is the floor the ledger's own ``committed`` count produces —
    what the gate sees today. ``honest`` is the floor over distinct decisions —
    what a bound assuming independent trials is entitled to claim.
    """

    band: str
    committed: int
    distinct: int
    max_repeat: int

    def __post_init__(self) -> None:
        if self.committed < 0 or self.distinct < 0 or self.max_repeat < 0:
            raise ValueError("counts must be non-negative")
        if self.distinct > self.committed:
            raise ValueError(
                f"{self.band}: distinct ({self.distinct}) cannot exceed "
                f"committed ({self.committed})"
            )
        if self.committed and not self.distinct:
            raise ValueError(f"{self.band}: committed cases with no distinct keys")

    @property
    def claimed(self) -> float:
        """Floor from ``committed`` — assumes every case was a fresh trial."""
        return conservative_floor(self.committed, self.committed)

    @property
    def honest(self) -> float:
        """Floor from distinct decisions — the defensible figure."""
        return conservative_floor(self.distinct, self.distinct)

    @property
    def inflation(self) -> float:
        """``committed / distinct``. 1.0 means every case was a distinct decision."""
        return round(self.committed / self.distinct, 9) if self.distinct else 0.0

    def clears(self, theta: float) -> bool:
        """Does the *honest* floor reach *theta*? The question the gate should ask."""
        return round(self.honest, 9) >= round(theta, 9)


def audit_band(band: str, keys: Iterable[Hashable]) -> EvidenceAudit:
    """Audit one band from the decision keys of its committed cases.

    *keys* is one entry per committed case — repeats are the point, so this
    takes an iterable of keys rather than a set.
    """
    counts = Counter(keys)
    committed = sum(counts.values())
    return EvidenceAudit(
        band=band,
        committed=committed,
        distinct=len(counts),
        max_repeat=max(counts.values()) if counts else 0,
    )


def audit_bands(cases_by_band: dict[str, Iterable[Hashable]]) -> tuple[EvidenceAudit, ...]:
    """Audit every band, ordered by band name for replay-stable reporting."""
    return tuple(audit_band(band, cases_by_band[band]) for band in sorted(cases_by_band))


def below_floor(
    audits: Iterable[EvidenceAudit], theta: float
) -> tuple[EvidenceAudit, ...]:
    """The audits whose honest floor does not reach *theta*, worst gap first."""
    failing = [a for a in audits if not a.clears(theta)]
    return tuple(sorted(failing, key=lambda a: (a.honest, a.band)))


def format_report(audits: Iterable[EvidenceAudit], theta: float) -> str:
    """A fixed-width report — the text a failing pin should print.

    Assertion messages are the whole value of an audit that fails months from
    now, so the numbers are formatted here rather than at each call site.
    """
    rows = sorted(audits, key=lambda a: a.band)
    need = volume_for_theta(theta)
    lines = [
        f"theta={theta}  perfect-record volume needed={need}",
        f"{'band':30s} {'committed':>9s} {'distinct':>8s} {'x':>6s} "
        f"{'claimed':>8s} {'honest':>7s}  clears",
    ]
    for a in rows:
        lines.append(
            f"{a.band:30s} {a.committed:9d} {a.distinct:8d} {a.inflation:6.1f} "
            f"{a.claimed:8.4f} {a.honest:7.4f}  {'yes' if a.clears(theta) else 'NO'}"
        )
    return "\n".join(lines)


__all__ = [
    "SERVE_VOLUME_AT_THETA_099",
    "EvidenceAudit",
    "audit_band",
    "audit_bands",
    "below_floor",
    "format_report",
    "volume_for_theta",
]
