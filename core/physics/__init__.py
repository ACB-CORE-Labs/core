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
    propose_kappa_line_search,
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
from core.physics.trajectory_invariants import (
    TrajectoryAssessment,
    TrajectoryInvariantError,
    assess_trajectory,
    energy_boundary_ok,
    relative_holonomy,
    trajectory_divergence,
)
# --- Off-serving (Tier-2) LAZY exports — serve quarantine (ADR-0241/0242) --------
# These are OFF-SERVING extensions: durable memory (holographic_vault) and
# evidence-gated optimization / research thermodynamics (fibonacci_search,
# wave_energy_boundary, multi_scale_energy). Eager-importing them here would drag
# the whole substrate into the serve process (chat.runtime) via this package barrel
# — the A-04 transitive breach documented in
# docs/research/adr-0241-0242-adversarial-and-fidelity-findings.md (Finding #2).
# They stay importable as `from core.physics import X` via PEP 562 __getattr__, but
# resolve lazily only on explicit off-serving access. Guarded by
# tests/test_serve_quarantine_transitive.py.
#
# NOTE (Joshua ruling 2026-07-15): wave_manifold is Tier-1 sanctioned serve
# substrate (goldtether/surprise/biography delegate to it) and stays eager above.
_LAZY_EXPORTS: dict[str, str] = {
    # holographic_vault — durable memory (L10 / persistence gate)
    "HolographicVaultError": "core.physics.holographic_vault",
    "HolographicVaultStore": "core.physics.holographic_vault",
    "SealedMode": "core.physics.holographic_vault",
    # wave_energy_boundary — P10 Trace B energy/τ gate (never serve)
    "CrystallizationDecision": "core.physics.wave_energy_boundary",
    "assess_wave_trajectory": "core.physics.wave_energy_boundary",
    "crystallization_for_holographic_seal": "core.physics.wave_energy_boundary",
    "energy_profile_from_wave": "core.physics.wave_energy_boundary",
    "fibonacci_tau_schedule": "core.physics.wave_energy_boundary",
    "recency_band_index": "core.physics.wave_energy_boundary",
    "wave_unitary_residual": "core.physics.wave_energy_boundary",
    # fibonacci_search — V1 evidence-gated optimization (never serve)
    "BASELINE_KAPPA": "core.physics.fibonacci_search",
    "BoundedUnimodalObjective": "core.physics.fibonacci_search",
    "FibonacciSearchCertificate": "core.physics.fibonacci_search",
    "OptimizationFailure": "core.physics.fibonacci_search",
    "fibonacci_number": "core.physics.fibonacci_search",
    "fibonacci_section_search": "core.physics.fibonacci_search",
    "propose_kappa_from_search": "core.physics.fibonacci_search",
    # multi_scale_energy — V2 research multi-band E_n(t) (never serve)
    "comparative_residual_separation": "core.physics.multi_scale_energy",
    "dyadic_tau_schedule": "core.physics.multi_scale_energy",
    "multi_scale_energy_for_schedule": "core.physics.multi_scale_energy",
    "multi_scale_energy_vector": "core.physics.multi_scale_energy",
    "schedule_mid_span_fraction": "core.physics.multi_scale_energy",
    # cognitive_lifecycle — ADR-0243 ingress→relaxation→egress (never serve)
    "CognitiveLifecycleEngine": "core.physics.cognitive_lifecycle",
    "CognitiveLifecycleError": "core.physics.cognitive_lifecycle",
    "CrystallizationProposal": "core.physics.cognitive_lifecycle",
    "EgressValidationError": "core.physics.cognitive_lifecycle",
    "EgressVerdict": "core.physics.cognitive_lifecycle",
    "HamiltonianCompileError": "core.physics.cognitive_lifecycle",
    "IngressDegenerate": "core.physics.cognitive_lifecycle",
    "IngressWavePacket": "core.physics.cognitive_lifecycle",
    "LifecycleOutcome": "core.physics.cognitive_lifecycle",
    "ProblemHamiltonian": "core.physics.cognitive_lifecycle",
    "PropositionalEntailmentVerdict": "core.physics.cognitive_lifecycle",
    "PropositionalProblem": "core.physics.cognitive_lifecycle",
    "RelaxationCertificate": "core.physics.cognitive_lifecycle",
    "RelaxationInputError": "core.physics.cognitive_lifecycle",
    "RelaxationNotConverged": "core.physics.cognitive_lifecycle",
    "RelaxationNumericalFailure": "core.physics.cognitive_lifecycle",
    "RelaxationResult": "core.physics.cognitive_lifecycle",
    "assignment_component_index": "core.physics.cognitive_lifecycle",
    "compile_propositional": "core.physics.cognitive_lifecycle",
    "compile_quadratic_well": "core.physics.cognitive_lifecycle",
    "egress_gate": "core.physics.cognitive_lifecycle",
    "ingest_context": "core.physics.cognitive_lifecycle",
    "propositional_entails": "core.physics.cognitive_lifecycle",
    "relax_to_ground": "core.physics.cognitive_lifecycle",
    "uniform_assignment_state": "core.physics.cognitive_lifecycle",
    # biography_wiring — ADR-0243 §2.5 validated-PASS → biography integration (never serve)
    "BiographyIntegrationError": "core.physics.biography_wiring",
    "BiographyProvenanceRecord": "core.physics.biography_wiring",
    "biography_provenance_record": "core.physics.biography_wiring",
    "integrate_validated_biography": "core.physics.biography_wiring",
}

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # static-analysis only — never imported at runtime (serve quarantine)
    from core.physics.holographic_vault import (
        HolographicVaultError,
        HolographicVaultStore,
        SealedMode,
    )
    from core.physics.wave_energy_boundary import (
        CrystallizationDecision,
        assess_wave_trajectory,
        crystallization_for_holographic_seal,
        energy_profile_from_wave,
        fibonacci_tau_schedule,
        recency_band_index,
        wave_unitary_residual,
    )
    from core.physics.fibonacci_search import (
        BASELINE_KAPPA,
        BoundedUnimodalObjective,
        FibonacciSearchCertificate,
        OptimizationFailure,
        fibonacci_number,
        fibonacci_section_search,
        propose_kappa_from_search,
    )
    from core.physics.multi_scale_energy import (
        comparative_residual_separation,
        dyadic_tau_schedule,
        multi_scale_energy_for_schedule,
        multi_scale_energy_vector,
        schedule_mid_span_fraction,
    )
    from core.physics.cognitive_lifecycle import (
        CognitiveLifecycleEngine,
        CognitiveLifecycleError,
        CrystallizationProposal,
        EgressValidationError,
        EgressVerdict,
        HamiltonianCompileError,
        IngressDegenerate,
        IngressWavePacket,
        LifecycleOutcome,
        ProblemHamiltonian,
        PropositionalEntailmentVerdict,
        PropositionalProblem,
        RelaxationCertificate,
        RelaxationInputError,
        RelaxationNotConverged,
        RelaxationNumericalFailure,
        RelaxationResult,
        assignment_component_index,
        compile_propositional,
        compile_quadratic_well,
        egress_gate,
        ingest_context,
        propositional_entails,
        relax_to_ground,
        uniform_assignment_state,
    )
    from core.physics.biography_wiring import (
        BiographyIntegrationError,
        BiographyProvenanceRecord,
        biography_provenance_record,
        integrate_validated_biography,
    )

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
    "TrajectoryAssessment", "TrajectoryInvariantError",
    "assess_trajectory", "energy_boundary_ok",
    "relative_holonomy", "trajectory_divergence",
    "HolographicVaultError", "HolographicVaultStore", "SealedMode",
    "CrystallizationDecision",
    "assess_wave_trajectory",
    "crystallization_for_holographic_seal",
    "energy_profile_from_wave",
    "fibonacci_tau_schedule",
    "recency_band_index",
    "wave_unitary_residual",
    "fibonacci_number",
    "BASELINE_KAPPA",
    "BoundedUnimodalObjective",
    "FibonacciSearchCertificate",
    "OptimizationFailure",
    "fibonacci_section_search",
    "propose_kappa_from_search",
    "propose_kappa_line_search",
    "comparative_residual_separation",
    "dyadic_tau_schedule",
    "multi_scale_energy_for_schedule",
    "multi_scale_energy_vector",
    "schedule_mid_span_fraction",
    "CognitiveLifecycleEngine",
    "CognitiveLifecycleError",
    "CrystallizationProposal",
    "EgressValidationError",
    "EgressVerdict",
    "HamiltonianCompileError",
    "IngressDegenerate",
    "IngressWavePacket",
    "LifecycleOutcome",
    "ProblemHamiltonian",
    "PropositionalEntailmentVerdict",
    "PropositionalProblem",
    "RelaxationCertificate",
    "RelaxationInputError",
    "RelaxationNotConverged",
    "RelaxationNumericalFailure",
    "RelaxationResult",
    "assignment_component_index",
    "compile_propositional",
    "compile_quadratic_well",
    "egress_gate",
    "ingest_context",
    "propositional_entails",
    "relax_to_ground",
    "uniform_assignment_state",
    "BiographyIntegrationError",
    "BiographyProvenanceRecord",
    "biography_provenance_record",
    "integrate_validated_biography",
]


def __getattr__(name: str):  # PEP 562 — lazy off-serving (Tier-2) exports
    module = _LAZY_EXPORTS.get(name)
    if module is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    import importlib

    return getattr(importlib.import_module(module), name)


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(_LAZY_EXPORTS))
