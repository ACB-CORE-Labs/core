"""core.physics — Mind-physics layer for CORE cognitive architecture.

Three physics sublayers:
  allocation   — salience, attention, inhibition, coherence budget (ADR-0008)
  compositional — binding, digest, reasoning, articulation (ADR-0009)
  identity     — identity manifold, drives, exertion, character (ADR-0010)

Third-Door Horizon (ADR-0238–0240):
  GoldTether, dynamic manifold, surprise dual, biography holonomy.

Wave-field substrate (ADR-0241):
  WaveManifold — continuous ψ, spectral leakage, polar analogy, chiral charge.
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
    GoldPromotionProof,
    GoldTetherMonitor,
    OperatingMode,
    coherence_residual,
)
from core.physics.dynamic_manifold import (
    AxisClassification,
    CartanIwasawaFactors,
    ConformalProcrustesResult,
    PrincipalAxis,
    SignatureAwarePCAResult,
    cartan_iwasawa_extract,
    cartan_iwasawa_factorize,
    conformal_procrustes,
    dual_correction_slerp,
    procrustes_residual,
    signature_aware_pca,
    signature_aware_pca_report,
)
from core.physics.surprise import (
    DEFAULT_DISCOVERY_GAMMA,
    dual_operator,
    dual_procrustes_surprise,
    is_discovery_eligible,
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
from core.physics.wave_manifold import WaveManifold

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
    "AutonomyBand", "AutonomyDecision", "CoherenceResidual",
    "GoldPromotionProof", "GoldTetherMonitor", "OperatingMode", "coherence_residual",
    "AxisClassification", "CartanIwasawaFactors", "ConformalProcrustesResult",
    "PrincipalAxis", "SignatureAwarePCAResult",
    "cartan_iwasawa_extract", "cartan_iwasawa_factorize",
    "conformal_procrustes", "dual_correction_slerp", "procrustes_residual",
    "signature_aware_pca", "signature_aware_pca_report",
    "DEFAULT_DISCOVERY_GAMMA",
    "dual_operator", "dual_procrustes_surprise", "is_discovery_eligible",
    "surprise_residual",
    "BiographyHolonomyBlade", "biography_telemetry",
    "integrate_biography", "reconstruct_biography",
    "TemporalAdmissibilityGate", "TemporalContext",
    "TemporalDecision", "TemporalVerdict",
    "AuthorshipProposal", "SelfAuthorshipMiner",
    "WaveManifold",
]
