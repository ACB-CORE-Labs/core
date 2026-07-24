"""E — the serving-side SERVE license for the converse-guess.

Reads the **ratified, committed** estimation ledger (``data/estimation_ledger.json``)
and exposes, per predicate, whether the converse-guess has earned ``Action.SERVE``
under the safe default ceilings (θ_SERVE=0.99). The engine READS this artifact; it
never writes it. The artifact is the sealed-practice output of
``evals.determination_estimation.build_ledger`` — its ``content_sha256`` is verified on
load, so a hand-edited (un-ratified) ledger is rejected rather than silently trusted.

Determinism: the ledger is immutable ratified data, parsed once and cached; the gate
is pure. No engine self-authorization — ceilings stay at the safe defaults (raising
one's own bar is structurally impossible, ADR-0175 invariant #4).

The load/verify/gate mechanics live in ``core.ratified_ledger`` (ADR-0263), the
bridge extracted from this module and its two successors; this is the estimation
ADAPTER over it, preserving its own public API (including the predicate →
converse-class naming, which is the one thing genuinely local to estimation).
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from core.ratified_ledger import RatifiedLedgerError, load_sealed_ledger
from core.ratified_ledger import serve_license as _serve_license
from core.reliability_gate import Ceilings, ClassTally, LicenseDecision
from generate.determine.estimate import converse_class_name

_LEDGER_PATH = Path(__file__).resolve().parent / "data" / "estimation_ledger.json"


@lru_cache(maxsize=1)
def load_ratified_ledger() -> dict[str, ClassTally]:
    """Load + verify the ratified estimation ledger → per-class ``ClassTally``.

    Raises :class:`RatifiedLedgerError` if the file is absent/malformed or its
    recomputed ``content_sha256`` does not match the committed one (tamper-evidence:
    only the sealed-practice output is trusted, never a hand-edited ledger).
    """
    return load_sealed_ledger(_LEDGER_PATH)


def serve_license(
    predicate: str,
    *,
    ledger: dict[str, ClassTally] | None = None,
    ceilings: Ceilings | None = None,
) -> LicenseDecision | None:
    """The ``Action.SERVE`` license for ``predicate``'s converse-guess, or ``None``.

    ``None`` means the predicate-class is absent from the ratified ledger (no committed
    evidence → never licensed; the caller refuses, the safe default). Otherwise the
    deterministic ``license_for`` verdict under the safe default ceilings.
    """
    ledger = ledger if ledger is not None else load_ratified_ledger()
    return _serve_license(converse_class_name(predicate), ledger, ceilings=ceilings)


__all__ = ["RatifiedLedgerError", "load_ratified_ledger", "serve_license"]
