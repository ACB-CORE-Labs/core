"""Read-only contemplation loop primitives.

ADR-0080: contemplation can emit speculative findings about current
substrate/report evidence, but it cannot ratify, promote, or mutate packs.

ADR-0241 P9: Trace A wave seam may SPECULATIVE-seal standing-wave modes and
emit RESONANT_MODE_CANDIDATE findings — never COHERENT, never serve-wired.
"""

from typing import TYPE_CHECKING, Any

from .runner import (
    SurpriseDiscoveryOutcome,
    SurpriseObservation,
    contemplate_frontier_reports,
    contemplate_surprise_history,
    run_contemplation,
)
from .schema import (
    ContemplationEvidenceRef,
    ContemplationFinding,
    ContemplationRun,
    FindingKind,
)
from .snapshot import ContemplationSubstrate

if TYPE_CHECKING:
    from .wave_seam import (
        WaveModeHypothesis,
        WaveReconstructResult,
        reconstruct_as_evidence,
        reconstruct_as_hypothesis,
        speculative_seal_from_contemplation,
    )

# A-04 process quarantine: chat/runtime.py's idle_tick lazily imports
# core.contemplation.runner inside the serve process, which imports this
# package __init__ first.  wave_seam eagerly pulls
# core.physics.holographic_vault — a serve-banned Tier-2 module
# (tests/test_serve_quarantine_transitive.py) — so its re-exports are lazy
# (PEP 562): they load only when actually referenced, which never happens on
# the serve path.
_WAVE_SEAM_EXPORTS = frozenset(
    {
        "WaveModeHypothesis",
        "WaveReconstructResult",
        "reconstruct_as_evidence",
        "reconstruct_as_hypothesis",
        "speculative_seal_from_contemplation",
    }
)


def __getattr__(name: str) -> Any:
    if name in _WAVE_SEAM_EXPORTS:
        from core.contemplation import wave_seam

        return getattr(wave_seam, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "ContemplationEvidenceRef",
    "ContemplationFinding",
    "ContemplationRun",
    "ContemplationSubstrate",
    "FindingKind",
    "SurpriseDiscoveryOutcome",
    "SurpriseObservation",
    "WaveModeHypothesis",
    "WaveReconstructResult",
    "contemplate_frontier_reports",
    "contemplate_surprise_history",
    "reconstruct_as_evidence",
    "reconstruct_as_hypothesis",
    "run_contemplation",
    "speculative_seal_from_contemplation",
]
