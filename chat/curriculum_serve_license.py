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

A deliberate near-copy of ``chat.deduction_serve_license``: the second
instance of the seal → ratify → SHA-verify → serve-gate pattern in this arc,
kept explicit here so the shared bridge (generalization plan Phase 3.3) is
extracted from two working instances rather than designed from one.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from core.reliability_gate import Action, Ceilings, ClassTally, LicenseDecision, license_for
from formation.hashing import sha256_of

_LEDGER_PATH = Path(__file__).resolve().parent / "data" / "curriculum_serve_ledger.json"


class RatifiedCurriculumLedgerError(ValueError):
    """The committed curriculum-serve ledger is missing, malformed, or tampered with."""


@lru_cache(maxsize=1)
def load_ratified_ledger() -> dict[str, ClassTally]:
    """Load + verify the ratified curriculum-serve ledger → per-band tallies.

    An ABSENT ledger is not an error: it means no curriculum band has earned
    anything yet, and every answer is served DISCLOSED. That is the honest
    default for a capability whose practice volume is still being built, and
    it keeps the composer usable before any license exists.
    """
    if not _LEDGER_PATH.exists():
        return {}
    try:
        artifact = json.loads(_LEDGER_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:  # pragma: no cover - defensive
        raise RatifiedCurriculumLedgerError(f"cannot read ratified ledger: {exc}") from exc

    classes = artifact.get("classes")
    if not isinstance(classes, dict):
        raise RatifiedCurriculumLedgerError("ratified ledger has no 'classes' table")
    if sha256_of(classes) != artifact.get("content_sha256"):
        raise RatifiedCurriculumLedgerError(
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
    tally = ledger.get(band)
    if tally is None:
        return None
    ceilings = ceilings if ceilings is not None else Ceilings.default()
    return license_for(tally, Action.SERVE, ceilings)


__all__ = [
    "RatifiedCurriculumLedgerError",
    "curriculum_serve_license",
    "load_ratified_ledger",
]
