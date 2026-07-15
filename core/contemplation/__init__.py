"""Read-only contemplation loop primitives.

ADR-0080: contemplation can emit speculative findings about current
substrate/report evidence, but it cannot ratify, promote, or mutate packs.

ADR-0241 P9: Trace A wave seam may SPECULATIVE-seal standing-wave modes and
emit RESONANT_MODE_CANDIDATE findings — never COHERENT, never serve-wired.
"""

from .runner import contemplate_frontier_reports, run_contemplation
from .schema import (
    ContemplationEvidenceRef,
    ContemplationFinding,
    ContemplationRun,
    FindingKind,
)
from .snapshot import ContemplationSubstrate
from .wave_seam import (
    WaveModeHypothesis,
    WaveReconstructResult,
    reconstruct_as_evidence,
    reconstruct_as_hypothesis,
    speculative_seal_from_contemplation,
)

__all__ = [
    "ContemplationEvidenceRef",
    "ContemplationFinding",
    "ContemplationRun",
    "ContemplationSubstrate",
    "FindingKind",
    "WaveModeHypothesis",
    "WaveReconstructResult",
    "contemplate_frontier_reports",
    "reconstruct_as_evidence",
    "reconstruct_as_hypothesis",
    "run_contemplation",
    "speculative_seal_from_contemplation",
]
