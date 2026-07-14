"""ADR-DAG conformal embedding (R&D-Revised §2.4 / issue #21).

Deterministic embedding of ADR markdown into Cl(4,1) bivector space and
master-blade drift checks for proposal coherence.
"""

from core.adr.validator import (
    AdrDagValidationError,
    embed_adr_markdown,
    master_architecture_blade,
    proposal_drift,
    simple_bivector_project,
    validate_proposal_against_master,
)

__all__ = [
    "AdrDagValidationError",
    "embed_adr_markdown",
    "master_architecture_blade",
    "proposal_drift",
    "simple_bivector_project",
    "validate_proposal_against_master",
]
