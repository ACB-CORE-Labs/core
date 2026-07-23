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

Mirrors ``generate.determine.estimation_license`` exactly: immutable ratified
data parsed once and cached; the gate (``license_for``) is pure; ceilings stay
at the safe defaults (invariant #4 — the engine cannot raise its own bar).
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from core.reliability_gate import Action, Ceilings, ClassTally, LicenseDecision, license_for
from formation.hashing import sha256_of

_LEDGER_PATH = Path(__file__).resolve().parent / "data" / "deduction_serve_ledger.json"


class RatifiedLedgerError(ValueError):
    """The committed deduction-serve ledger is missing, malformed, or tampered with."""


@lru_cache(maxsize=1)
def load_ratified_ledger() -> dict[str, ClassTally]:
    """Load + verify the ratified deduction-serve ledger → per-band ``ClassTally``.

    Raises :class:`RatifiedLedgerError` if the file is absent/malformed or its
    recomputed ``content_sha256`` does not match the committed one (tamper-evidence:
    only the sealed-practice output is trusted, never a hand-edited ledger).
    """
    try:
        artifact = json.loads(_LEDGER_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:  # pragma: no cover - defensive
        raise RatifiedLedgerError(f"cannot read ratified ledger: {exc}") from exc

    classes = artifact.get("classes")
    if not isinstance(classes, dict):
        raise RatifiedLedgerError("ratified ledger has no 'classes' table")
    if sha256_of(classes) != artifact.get("content_sha256"):
        raise RatifiedLedgerError(
            "ratified ledger content_sha256 mismatch — not the sealed-practice output"
        )

    ledger: dict[str, ClassTally] = {}
    for cls, counts in classes.items():
        ledger[cls] = ClassTally(
            class_name=cls,
            correct=int(counts.get("correct", 0)),
            wrong=int(counts.get("wrong", 0)),
            refused=int(counts.get("refused", 0)),
            t2_verified=int(counts.get("t2_verified", 0)),
            t2_agrees_gold=int(counts.get("t2_agrees_gold", 0)),
        )
    return ledger


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
    tally = ledger.get(shape_band)
    if tally is None:
        return None
    ceilings = ceilings if ceilings is not None else Ceilings.default()
    return license_for(tally, Action.SERVE, ceilings)


__all__ = ["RatifiedLedgerError", "deduction_serve_license", "load_ratified_ledger"]
