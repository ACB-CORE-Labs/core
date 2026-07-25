"""Serving-side SERVE license for curriculum-grounded answers (ADR-0262).

Reads the **ratified, committed** curriculum-serve ledger
(``chat/data/curriculum_serve_ledger.json``) and exposes, per *(subject ×
relation family)* band, whether the FULL serving pipeline (curriculum
compiler → argument reader → ROBDD engine) has earned ``Action.SERVE`` under
the safe default ceilings (θ_SERVE=0.99). The engine READS this artifact; it
never writes it — the sealed-practice output of
``evals.curriculum_serve.practice.runner.seal_ledger`` is the only writer, and
its ``content_sha256`` is verified on load so a hand-edited ledger is rejected
rather than silently trusted.

The third instance of the seal → ratify → SHA-verify → serve-gate pattern, and
the one that made the shared bridge worth extracting: this module is now an
ADAPTER over ``core.ratified_ledger`` (ADR-0263). It names the artifact, keeps
the memoization, and declares the one thing that genuinely differs — this
ledger is legitimately ABSENT, because no curriculum band has earned anything
yet (ADR-0262 §5.1: the binding constraint is ratified curriculum volume). An
absent ledger reads as an empty table, so every answer is served DISCLOSED.
"""

from __future__ import annotations

from functools import lru_cache

from core.ratified_ledger import (
    RatifiedLedgerError as RatifiedCurriculumLedgerError,
    ledger_spec,
    load_capability_ledger,
    serve_license,
)
from core.reliability_gate import Ceilings, ClassTally, LicenseDecision

_LEDGER_CAPABILITY = "curriculum_serve"
_LEDGER_PATH = ledger_spec(_LEDGER_CAPABILITY).path


@lru_cache(maxsize=1)
def load_ratified_ledger() -> dict[str, ClassTally]:
    """Load + verify the ratified curriculum-serve ledger → per-band tallies.

    An ABSENT ledger is not an error *for this capability*: no curriculum band
    has earned anything yet, and the honest reading of "no file" is "no
    committed evidence", which the gate turns into a disclosed answer rather
    than a withheld one.

    That policy is declared once in ``CAPABILITY_LEDGERS``, not asserted here —
    this module names the capability and inherits its registered absence
    contract, so it cannot grant itself a softer failure mode than the bridge
    recorded (ADR-0263 rule 5).
    """
    return load_capability_ledger(_LEDGER_CAPABILITY)


def curriculum_serve_license(
    band: str,
    *,
    ledger: dict[str, ClassTally] | None = None,
    ceilings: Ceilings | None = None,
) -> LicenseDecision | None:
    """The ``Action.SERVE`` license for a curriculum band, or ``None``.

    ``None`` means the band has no committed evidence → never licensed; the
    caller serves a disclosed (hedged) surface, the safe default.
    """
    ledger = ledger if ledger is not None else load_ratified_ledger()
    return serve_license(band, ledger, ceilings=ceilings)


__all__ = [
    "RatifiedCurriculumLedgerError",
    "curriculum_serve_license",
    "load_ratified_ledger",
]
