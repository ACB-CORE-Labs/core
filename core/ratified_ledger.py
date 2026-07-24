"""The ratified-ledger bridge — seal → ratify → SHA-verify → serve-gate.

ADR-0175 Phase 5's consumption bridge (generalization plan Phase 3.3),
extracted from three working instances rather than designed ahead of them:

- ``generate/determine/estimation_license.py``   (ADR-0175, the first)
- ``chat/deduction_serve_license.py``            (ADR-0256, the second)
- ``chat/curriculum_serve_license.py``           (ADR-0262, the third)

All three had converged on the same artifact and the same four rules, which is
what makes this an extraction and not a speculation. The rules, stated once:

1. **The engine reads; only sealed practice writes.** A ledger is the output
   of a practice run over a gold corpus, never of a serving turn. Nothing in a
   serving path may call :func:`write_sealed_ledger`.
2. **Tamper-evidence is structural.** The artifact carries
   ``content_sha256`` over its ``classes`` table; a load that cannot reproduce
   it REFUSES. A hand-edited ledger is not a slightly-wrong ledger, it is an
   unratified one.
3. **Ceilings are not negotiable at the call site.** The gate always runs at
   the safe defaults unless a caller passes ceilings explicitly, and no
   production path does — ADR-0175 invariant #4: an engine cannot raise its own
   bar.
4. **Absent evidence is never a license.** A class missing from the ledger
   yields ``None``, and every caller's ``None`` branch serves the disclosed
   (hedged) surface. A capability with no track record is served honestly, not
   withheld and not asserted.

Byte-compatibility is deliberate: :func:`seal_artifact` and
:func:`write_sealed_ledger` reproduce the exact bytes the three existing
sealers wrote, so adopting the bridge re-seals every committed ledger
identically and no lane pin moves.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.reliability_gate import (
    Action,
    Ceilings,
    ClassTally,
    LicenseDecision,
    license_for,
)
from formation.hashing import sha256_of


class RatifiedLedgerError(ValueError):
    """A committed ledger is malformed or does not verify against its own hash."""


def tally_dict(tally: ClassTally) -> dict[str, Any]:
    """The committed per-class row. The field set is the contract — a reader
    of an older ledger must be able to name every field it finds."""
    return {
        "correct": tally.correct,
        "wrong": tally.wrong,
        "refused": tally.refused,
        "t2_verified": tally.t2_verified,
        "t2_agrees_gold": tally.t2_agrees_gold,
    }


def seal_artifact(
    ledger: dict[str, ClassTally], *, schema: str, note: str, provenance: str
) -> dict[str, Any]:
    """The self-verifying sealed-ledger dict for *ledger*.

    Classes are sorted, so the artifact is a pure function of the practice
    result: the same corpus and solver seal byte-identically, which is what
    makes a committed ledger reviewable as a diff.
    """
    classes = {name: tally_dict(tally) for name, tally in sorted(ledger.items())}
    return {
        "schema": schema,
        "classes": classes,
        "content_sha256": sha256_of(classes),
        "note": note,
        "provenance": provenance,
    }


def write_sealed_ledger(path: Path, artifact: dict[str, Any]) -> dict[str, Any]:
    """Write *artifact* to *path* in the committed formatting."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return artifact


def load_sealed_ledger(path: Path, *, missing_ok: bool = False) -> dict[str, ClassTally]:
    """Load + verify a sealed ledger → per-class ``ClassTally``.

    ``missing_ok`` distinguishes two genuinely different situations. A ledger
    that a capability *ships with* is required: its absence means the
    deployment is broken, and refusing is right. A ledger for a capability
    whose practice volume is still being built is legitimately absent, and the
    honest reading of "no file" is "no class has earned anything yet" — an
    empty table, every answer disclosed. Neither case may be answered by
    guessing a license.
    """
    if not path.exists():
        if missing_ok:
            return {}
        raise RatifiedLedgerError(f"ratified ledger not found: {path}")
    try:
        artifact = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RatifiedLedgerError(f"cannot read ratified ledger: {exc}") from exc

    classes = artifact.get("classes") if isinstance(artifact, dict) else None
    if not isinstance(classes, dict):
        raise RatifiedLedgerError("ratified ledger has no 'classes' table")
    if sha256_of(classes) != artifact.get("content_sha256"):
        raise RatifiedLedgerError(
            "ratified ledger content_sha256 mismatch — not the sealed-practice output"
        )

    return {
        name: ClassTally(
            class_name=name,
            correct=int(counts.get("correct", 0)),
            wrong=int(counts.get("wrong", 0)),
            refused=int(counts.get("refused", 0)),
            t2_verified=int(counts.get("t2_verified", 0)),
            t2_agrees_gold=int(counts.get("t2_agrees_gold", 0)),
        )
        for name, counts in classes.items()
    }


def serve_license(
    class_name: str,
    ledger: dict[str, ClassTally],
    *,
    ceilings: Ceilings | None = None,
) -> LicenseDecision | None:
    """The ``Action.SERVE`` verdict for *class_name*, or ``None`` when the
    class has no committed evidence (never a license — rule 4)."""
    tally = ledger.get(class_name)
    if tally is None:
        return None
    return license_for(tally, Action.SERVE, ceilings or Ceilings.default())


__all__ = [
    "RatifiedLedgerError",
    "load_sealed_ledger",
    "seal_artifact",
    "serve_license",
    "tally_dict",
    "write_sealed_ledger",
]
