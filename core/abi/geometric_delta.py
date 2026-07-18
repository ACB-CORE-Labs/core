"""GeometricDelta ABI Definition.

Single source of truth for the GeometricDelta struct which defines the boundary
between any modality compiler (like Sopher's Callosum) and the Master substrate (CORE).
"""

from dataclasses import dataclass
import random
from typing import Any, Dict, List, Optional, Set

from core.epistemic_state import EpistemicState


@dataclass(frozen=True)
class GeometricDelta:
    """The canonical ABI for field updates to the Master substrate.
    
    All compilers must emit exactly this type, and it must pass the guarded closure 
    projector at the boundary.
    """
    id: str                      # content-addressed hash
    parents: Set[str]            # CRDT frontier IDs
    modality: str                # e.g. "lh_text", "sensor", "tool"
    compiler_id: str             # name+version of compiler
    semantic: Dict[str, Any]     # typed primitive (enum + payload)
    amr_scope: Dict[str, Any]    # resolution + region metadata
    delta_versor: List[float]    # 32 components, Cl(4,1) basis
    inverse_ref: Optional[str]   # optional correction link
    provenance: Dict[str, Any]   # source, time, adr_refs, hash
    epistemic: EpistemicState    # CORE truth-seeking state


def generate_jittered_parents(base_parents: Set[str], drop_prob: float = 0.1, inject_stale_prob: float = 0.1, stale_pool: List[str] = None) -> Set[str]:
    """Generates a randomized CRDT causal parent tree to simulate sensory jitter and latency."""
    jittered = set()
    for parent in base_parents:
        if random.random() > drop_prob:
            jittered.add(parent)
            
    if stale_pool and random.random() < inject_stale_prob:
        jittered.add(random.choice(stale_pool))
        
    return jittered
