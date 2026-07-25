"""Serving-side SERVE license for deduction (deduction-serve arc, Phase 3, ADR-0256).

Reads the **ratified, committed** deduction-serve ledger
(``chat/data/deduction_serve_ledger.json``) and exposes, per propositional
shape-band, whether the FULL serving pipeline (reader → projector → ROBDD
engine) has earned ``Action.SERVE`` under the safe default ceilings
(θ_SERVE=0.99). The engine READS this artifact; it never writes it. The
artifact is the sealed-practice output of
``evals.deduction_serve.practice.runner.seal_ledger`` — its ``content_sha256``
is verified on load, so a hand-edited (un-ratified) ledger is rejected rather
than silently trusted.

The load/verify/gate mechanics live in ``core.ratified_ledger`` (ADR-0263) —
this module is the deduction-serve ADAPTER over that bridge: it names the
artifact, keeps the memoization, and preserves its own public API. Ceilings
stay at the safe defaults (invariant #4 — the engine cannot raise its own bar).
"""

from __future__ import annotations

from functools import lru_cache

from core.ratified_ledger import (
    RatifiedLedgerError,
    ledger_spec,
    load_capability_ledger,
    serve_license,
)
from core.reliability_gate import Ceilings, ClassTally, LicenseDecision

_LEDGER_CAPABILITY = "deduction_serve"
_LEDGER_PATH = ledger_spec(_LEDGER_CAPABILITY).path


@lru_cache(maxsize=1)
def load_ratified_ledger() -> dict[str, ClassTally]:
    """Load + verify the ratified deduction-serve ledger → per-band ``ClassTally``.

    Raises :class:`RatifiedLedgerError` if the file is absent/malformed or its
    recomputed ``content_sha256`` does not match the committed one (tamper-evidence:
    only the sealed-practice output is trusted, never a hand-edited ledger).

    This capability is registered ``missing_ok=False`` in ``CAPABILITY_LEDGERS``
    — it ships with its ledger, so absence is a broken deployment, and that
    verdict is the manifest's rather than this call's (ADR-0263 rule 5).
    """
    return load_capability_ledger(_LEDGER_CAPABILITY)


def deduction_serve_license(
    shape_band: str,
    *,
    ledger: dict[str, ClassTally] | None = None,
    ceilings: Ceilings | None = None,
) -> LicenseDecision | None:
    """The ``Action.SERVE`` license for a propositional ``shape_band``, or ``None``.

    ``None`` means the band is absent from the ratified ledger (no committed
    evidence → never licensed; the caller serves a disclosed/hedged surface, the
    safe default). Otherwise the deterministic ``license_for`` verdict under the
    safe default ceilings.
    """
    ledger = ledger if ledger is not None else load_ratified_ledger()
    return serve_license(shape_band, ledger, ceilings=ceilings)


__all__ = ["RatifiedLedgerError", "deduction_serve_license", "load_ratified_ledger"]
