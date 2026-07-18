"""Omni Compiler for transduced signals to GeometricDelta."""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from typing import Any, Set

import numpy as np

from core.abi.geometric_delta import GeometricDelta
from core.epistemic_state import EpistemicState


class OmniCompiler:
    """Compiles Omni signals into GeometricDelta."""

    def __init__(self, compiler_id: str = "omni_compiler_v1"):
        self.compiler_id = compiler_id

    def compile(
        self,
        modality: str,
        semantic: dict[str, Any],
        amr_scope: dict[str, Any],
        versor: np.ndarray,
        parents: Set[str] = None,
        epistemic: EpistemicState = EpistemicState.UNVERIFIED_POSSIBLE,
    ) -> GeometricDelta:
        """Compile a GeometricDelta from transduced inputs."""
        if parents is None:
            parents = set()

        # Enforce exactly 32-dim array for Cl(4,1)
        if versor.shape != (32,):
            raise ValueError(f"versor shape must be (32,), got {versor.shape}")

        delta_id = str(uuid.uuid4())
        timestamp = time.time()
        
        # Provenance hash computation
        prov_payload = {
            "source": "google_omni_eos",
            "time": timestamp,
            "adr_refs": ["ADR-0237", "ADR-0211"],
        }
        blob = json.dumps(prov_payload, sort_keys=True).encode("utf-8")
        prov_payload["hash"] = hashlib.sha256(blob).hexdigest()

        return GeometricDelta(
            id=delta_id,
            parents=parents,
            modality=modality,
            compiler_id=self.compiler_id,
            semantic=semantic,
            amr_scope=amr_scope,
            delta_versor=versor.tolist(),
            inverse_ref=None,
            provenance=prov_payload,
            epistemic=epistemic,
        )
