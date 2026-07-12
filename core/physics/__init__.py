"""core.physics — Mind-physics layer for CORE cognitive architecture.

Three physics sublayers:
  allocation   — salience, attention, inhibition, coherence budget (ADR-0008)
  compositional — binding, digest, reasoning, articulation (ADR-0009)
  identity     — identity manifold, drives, exertion, character (ADR-0010)

Third-Door Horizon (ADR-0238–0240):
  coherence GoldTether, dynamic manifold (Procrustes/PCA), surprise dual,
  biography holonomy, temporal gate, self-authorship miner.

All operators are stateless and frozen where possible.
State lives in the FieldState; operators are pure transformations.
"""

from core.physics.salience import SalienceOperator, SalienceMap, FieldRegion
from core.physics.energy import EnergyClass, EnergyProfile, FieldEnergyOperator
from core.physics.valence import ValenceBundle
from core.physics.attention import AttentionOperator, AttentionPlan, CoherenceBudget
from core.physics.inhibition import InhibitionOperator, InhibitionMask
from core.physics.binding import BindingFrame, BindingOperator
from core.physics.digest import DigestCycle, DigestOperator
from core.physics.reasoning import ReasoningTrajectory, TrajectoryOperator
from core.physics.articulation import ArticulationPlan, ArticulationPlanner, OutputModality
from core.physics.drive import DriveGradientMap, GradientField, ValueAxis
from core.physics.exertion import ExertionMeter, FatigueIndex, CycleCost
from core.physics.identity import IdentityManifold, IdentityCheck, IdentityScore, CharacterProfile
from core.physics.learning import PromotionDecision, VaultPromotionPolicy
from core.physics.goldtether import (
    AutonomyBand,
    AutonomyDecision,
    CoherenceResidual,
    GoldTetherConfig,
    GoldTetherMonitor,
    OperatingMode,
    PseudoscalarFloorState,
    derive_kappa,
)
from core.physics.dynamic_manifold import (
    AxisClassification,
    CartanIwasawaFactors,
    ConformalProcrustesResult,
    PrincipalAxis,
    SignatureAwarePCAResult,
    cartan_iwasawa_factorize,
    conformal_procrustes,
    dual_correction_slerp,
    procrustes_residual,
    signature_aware_pca,
)
from core.physics.surprise import (
    AnalogySeed,
    DualOperatorResult,
    SurpriseResult,
    analogy_seed,
    dual_operator,
    project_onto_basis,
    surprise_residual,
)
from core.physics.biography import (
    BiographyHolonomyBlade,
    biography_telemetry,
    integrate_biography,
    reconstruct_biography,
)
from core.physics.temporal_gate import (
    TemporalAdmissibilityGate,
    TemporalContext,
    TemporalDecision,
    TemporalVerdict,
)
from core.physics.self_authorship import AuthorshipProposal, SelfAuthorshipMiner

__all__ = [
    "SalienceOperator", "SalienceMap", "FieldRegion",
    "EnergyClass", "EnergyProfile", "FieldEnergyOperator", "ValenceBundle",
    "AttentionOperator", "AttentionPlan", "CoherenceBudget",
    "InhibitionOperator", "InhibitionMask",
    "BindingFrame", "BindingOperator",
    "DigestCycle", "DigestOperator",
    "ReasoningTrajectory", "TrajectoryOperator",
    "ArticulationPlan", "ArticulationPlanner", "OutputModality",
    "DriveGradientMap", "GradientField", "ValueAxis",
    "ExertionMeter", "FatigueIndex", "CycleCost",
    "IdentityManifold", "IdentityCheck", "IdentityScore", "CharacterProfile",
    "PromotionDecision", "VaultPromotionPolicy",
    # ADR-0238
    "AutonomyBand",
    "AutonomyDecision",
    "CoherenceResidual",
    "GoldTetherConfig",
    "GoldTetherMonitor",
    "OperatingMode",
    "PseudoscalarFloorState",
    "derive_kappa",
    # ADR-0239
    "AxisClassification",
    "CartanIwasawaFactors",
    "ConformalProcrustesResult",
    "PrincipalAxis",
    "SignatureAwarePCAResult",
    "cartan_iwasawa_factorize",
    "conformal_procrustes",
    "dual_correction_slerp",
    "procrustes_residual",
    "signature_aware_pca",
    "AnalogySeed",
    "DualOperatorResult",
    "SurpriseResult",
    "analogy_seed",
    "dual_operator",
    "project_onto_basis",
    "surprise_residual",
    # ADR-0240
    "BiographyHolonomyBlade",
    "biography_telemetry",
    "integrate_biography",
    "reconstruct_biography",
    "TemporalAdmissibilityGate",
    "TemporalContext",
    "TemporalDecision",
    "TemporalVerdict",
    "AuthorshipProposal",
    "SelfAuthorshipMiner",
]
