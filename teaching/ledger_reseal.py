"""teaching/ledger_reseal.py — the ``ledger_reseal`` stage of the ceremony.

``RatificationReceipt.pending_stages`` has named ``ledger_reseal`` since the
ratification ceremony was written, and nothing performed it. Ratifying a chain
grows the corpus; it does not re-run practice, so the sealed ledger the serving
gate reads goes stale the moment curriculum changes. This module is that stage,
and it is deliberately **not** reachable from ``ratify_chain``.

Why it is a separate, human-run act
-----------------------------------
``AGENTS.md`` forbids ratification automation, and an auto-reseal on every
``ratify`` would churn the ledger's ``content_sha256`` once per row. But the
stronger reason is what Phase C measured: **resealing can grant licenses.**
Reliability is commitment precision and a correct UNKNOWN is a commitment, so
any band with ≥657 routable atoms clears θ_SERVE on non-commitments alone. A
plain "regenerate the artifact" verb would therefore flip four curriculum bands
from disclosed to authoritative as a side effect of housekeeping, on evidence
that is ~99% non-entailed — which ADR-0262 §5.1 rules unacceptable
(``docs/research/curriculum-practice-producer-2026-07-26.md`` §1).

So :func:`plan_reseal` computes the license DELTA before writing anything, and
the caller must opt in explicitly to any band that would become newly licensed.
The default is refusal. Regenerating an artifact is housekeeping; changing what
the engine will assert authoritatively is a ratification, and the two must not
share a keystroke.

Scope: this module writes a ledger and nothing else. It has no opinion on
whether curriculum content is true, cannot ratify a chain, and cannot flip a
serving flag.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from core.ratified_ledger import (
    CAPABILITY_LEDGERS,
    load_capability_ledger,
    write_sealed_ledger,
)
from core.reliability_gate import Action, Ceilings, ClassTally, license_for


class ReadyToReseal(ValueError):
    """A reseal was requested that cannot proceed as asked."""


@dataclass(frozen=True, slots=True)
class ResealPlan:
    """What a reseal would do, computed before it does it."""

    capability: str
    path: Path
    #: Bands licensed by the ledger currently on disk (empty when absent).
    licensed_before: tuple[str, ...]
    #: Bands the freshly-built artifact would license.
    licensed_after: tuple[str, ...]
    #: Per-band committed volume in the new artifact.
    committed: dict[str, int]
    #: Per-band gold verdict mix — the axis ``ClassTally`` cannot carry.
    mix: dict[str, dict[str, int]]
    artifact: dict[str, Any]

    @property
    def newly_licensed(self) -> tuple[str, ...]:
        """Bands this reseal would grant SERVE that do not hold it today.

        The figure that decides whether the operation is housekeeping or a
        ratification.
        """
        before = set(self.licensed_before)
        return tuple(b for b in self.licensed_after if b not in before)

    @property
    def revoked(self) -> tuple[str, ...]:
        """Bands that would LOSE a license — always allowed, never gated.

        Losing a license is the gate becoming more conservative, which needs no
        authorization. Only granting one does.
        """
        after = set(self.licensed_after)
        return tuple(b for b in self.licensed_before if b not in after)

    @property
    def is_housekeeping(self) -> bool:
        return not self.newly_licensed


#: capability -> (build artifact, build ledger, build mix).
#:
#: ``deduction_serve`` is deliberately ABSENT. Its ledger is SHA-sealed,
#: ratified, and gating a live flag, and 21 of its 25 bands do not clear
#: θ_SERVE on distinct evidence (``tests/test_volume_honesty.py``). Re-sealing it
#: is Shay's ratification, not a CLI verb's, and a reseal that silently
#: regenerated it would erase the exposure this arc measured. ``estimation``
#: ships sealed with its gate and has no reason to move.
_RESEALABLE: dict[str, tuple[Callable[[], dict[str, Any]], Callable[[], dict[str, ClassTally]], Callable[[], dict[str, dict[str, int]]]]] = {}


def _register_curriculum() -> None:
    from evals.curriculum_serve.practice.runner import (
        build_ledger,
        build_mix,
        build_sealed_artifact,
    )

    _RESEALABLE["curriculum_serve"] = (build_sealed_artifact, build_ledger, build_mix)


def resealable_capabilities() -> tuple[str, ...]:
    """Capabilities this stage will rebuild, in a stable order."""
    if not _RESEALABLE:
        _register_curriculum()
    return tuple(sorted(_RESEALABLE))


def _licensed_bands(ledger: dict[str, ClassTally], ceilings: Ceilings) -> tuple[str, ...]:
    return tuple(
        sorted(
            band
            for band, tally in ledger.items()
            if license_for(tally, Action.SERVE, ceilings).licensed
        )
    )


def plan_reseal(capability: str, *, ceilings: Ceilings | None = None) -> ResealPlan:
    """Compute the reseal and its license delta — writing nothing.

    The read of the CURRENT ledger goes through :func:`load_capability_ledger`,
    the same production entry point the serving adapters use, so two properties
    come for free. A hand-edited ledger refuses here rather than being silently
    overwritten (losing the evidence that it was tampered with), and this stage
    inherits the capability's DECLARED absence policy instead of choosing its own
    — bridge rule 5: ``missing_ok`` is a fact about the capability, not about the
    call, and no production path may pass it.
    """
    if capability not in resealable_capabilities():
        raise ReadyToReseal(
            f"{capability!r} is not resealable — known: {list(resealable_capabilities())}. "
            "Ledgers absent from that list are sealed by deliberate ratification only."
        )
    spec = CAPABILITY_LEDGERS[capability]
    ceilings = ceilings if ceilings is not None else Ceilings.default()
    build_artifact, build_ledger, build_mix = _RESEALABLE[capability]

    current = load_capability_ledger(capability)
    fresh_ledger = build_ledger()
    artifact = build_artifact()

    return ResealPlan(
        capability=capability,
        path=spec.path,
        licensed_before=_licensed_bands(current, ceilings),
        licensed_after=_licensed_bands(fresh_ledger, ceilings),
        committed={band: t.committed for band, t in sorted(fresh_ledger.items())},
        mix=build_mix(),
        artifact=artifact,
    )


def apply_reseal(plan: ResealPlan, *, allow_new_licenses: bool = False) -> Path:
    """Write the planned artifact, refusing to grant a license by accident.

    ``allow_new_licenses`` is the ratification. Without it, a plan that would
    newly license any band refuses and names them — the operator then either
    authorizes the grant or fixes the producer, but never discovers afterwards
    that a serving surface became authoritative.
    """
    if plan.newly_licensed and not allow_new_licenses:
        detail = ", ".join(
            f"{band} (committed={plan.committed.get(band, 0)}, "
            f"entailed={plan.mix.get(band, {}).get('entailed', 0)})"
            for band in plan.newly_licensed
        )
        raise ReadyToReseal(
            f"{plan.capability}: this reseal would newly license {len(plan.newly_licensed)} "
            f"band(s) — {detail}. That is a ratification, not a reseal: those bands "
            "would begin serving authoritatively. Re-run with --allow-new-licenses "
            "only if the grant is intended, and read the `entailed` counts first — a "
            "band can clear theta_SERVE on correct NON-COMMITMENTS alone (ADR-0262 §5.1)."
        )
    write_sealed_ledger(plan.path, plan.artifact)
    return plan.path


__all__ = [
    "ReadyToReseal",
    "ResealPlan",
    "apply_reseal",
    "plan_reseal",
    "resealable_capabilities",
]
