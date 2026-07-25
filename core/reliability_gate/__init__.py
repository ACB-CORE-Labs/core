"""ADR-0175 Phase 1 — reliability ledger + attempt/refuse gate substrate.

Standalone, deterministic, replay-stable. NOT wired into the serving/eval path
(invariant #1: zero serving change). NOT the `calibration/` module (that is a
grid-search hyperparameter tuner; this is the per-class reliability ledger).

Public surface:
- :func:`conservative_floor`, :data:`WILSON_Z`, :data:`N_MIN` — the pinned floor.
- :class:`ClassTally` — per-class counted ledger; reliability = commitment precision.
- :class:`Action`, :class:`Ceilings` — human-set θ ceilings (engine never mutates).
- :func:`license_for`, :class:`LicenseDecision` — the deterministic gate.
- :class:`EvidenceAudit`, :func:`audit_band` — distinct-evidence audit (ADR-0264
  R9). Measurement only, imported by no serving path: the Wilson floor assumes
  independent trials, and a deterministic pipeline replaying one input N times
  supplies one trial's evidence, not N.
"""

from __future__ import annotations

from core.reliability_gate.ceilings import Action, Ceilings
from core.reliability_gate.evidence import (
    SERVE_VOLUME_AT_THETA_099,
    EvidenceAudit,
    audit_band,
    audit_bands,
    below_floor,
    format_report,
    volume_for_theta,
)
from core.reliability_gate.floor import N_MIN, WILSON_Z, conservative_floor
from core.reliability_gate.gate import LicenseDecision, license_for
from core.reliability_gate.ledger import ClassTally
from core.reliability_gate.propose import RatifiableProposal, propose_from_ledger

__all__ = [
    "Action",
    "Ceilings",
    "ClassTally",
    "EvidenceAudit",
    "LicenseDecision",
    "N_MIN",
    "RatifiableProposal",
    "SERVE_VOLUME_AT_THETA_099",
    "WILSON_Z",
    "audit_band",
    "audit_bands",
    "below_floor",
    "conservative_floor",
    "format_report",
    "license_for",
    "propose_from_ledger",
    "volume_for_theta",
]
