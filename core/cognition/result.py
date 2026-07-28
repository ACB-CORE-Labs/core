"""
CognitiveTurnResult — the complete record of one cognitive turn.

This is the canonical output of CognitiveTurnPipeline.run().  It is
frozen and slot-based so it can be passed safely across module boundaries
without mutation risk.
"""

from __future__ import annotations

from dataclasses import dataclass

from core.cognition.geometric_coherence import GeometricCoherenceVerdict
from core.cognition.leeway import LeewayRecord
from field.state import FieldState
from generate.articulation import ArticulationPlan
from generate.dialogue import DialogueRole
from generate.graph_planner import ArticulationTarget, PropositionGraph
from generate.intent import DialogueIntent
from generate.proposition import Proposition
from core.physics.identity import IdentityScore
from recognition.carrier import EpistemicGraph
from teaching.correction import CorrectionCandidate
from teaching.review import ReviewedTeachingExample
from teaching.store import PackMutationProposal
from chat.dispatch_trace import DispatchTrace


@dataclass(frozen=True, slots=True)
class CognitiveTurnResult:
    """Full observability record for a single pipeline turn.

    Includes the Shadow Coherence Gate evidence (authority_source +
    substrate_hazard) so that the migration from hybrid legacy spine to
    the unified PropositionGraph substrate is completely inspectable and
    replay-diagnosable without ever breaking determinism or the 74 invariants.

    3-lang depth fields (node_depths, graph_anti_unify) are populated for
    he/grc PropGraph turns from the same data used for oov_geometric_context.
    They are read-only / observational and never affect trace_hash or behavior.
    The depth propagation contract (pipeline -> runtime _last_node_depths ->
    contemplate(..., depth=) -> teaching) is documented alongside the code.
    """

    # --- input layer ---
    input_text: str
    input_tokens: tuple[str, ...]
    filtered_tokens: tuple[str, ...]

    # --- field layer ---
    field_state_before: FieldState | None   # None on the very first turn
    field_state_after: FieldState

    # --- understanding / recall layer ---
    proposition: Proposition
    articulation: ArticulationPlan

    # --- output surfaces ---
    surface: str                # final voiced surface (what the user sees)
    walk_surface: str           # sentence-assembled walk surface
    articulation_surface: str   # bare articulation surface before assembly

    # --- dialogue ---
    dialogue_role: DialogueRole

    # --- identity telemetry ---
    identity_score: IdentityScore | None

    # --- vault / memory ---
    vault_hits: int
    recall_energy_class: str | None = None

    #: The register-INVARIANT truth-path bytes — what ``compute_trace_hash``
    #: actually folds (ADR-0069 inv C, ADR-0077 R6). Distinct from ``surface``,
    #: which is the served, register-decorated string the user reads.
    #:
    #: Exposed 2026-07-25. It was pipeline-local before that, which made the
    #: truth-path-isolation invariant unobservable from a turn result — so
    #: ``test_register_matrix_canonical_surface_byte_identical`` asserted it on
    #: ``surface`` instead, and went red across all 99 registers the moment
    #: Phase 0 flipped ``resolve_surface`` to response-first precedence and
    #: moved the invariant here. The contract was never broken; it just could
    #: not be seen. Empty string ⇒ identical to ``surface`` (no divergence).
    hash_surface: str = ""

    # --- intent / graph telemetry ---
    intent: DialogueIntent | None = None
    proposition_graph: PropositionGraph | None = None
    articulation_target: ArticulationTarget | None = None

    # --- teaching loop ---
    teaching_candidate: CorrectionCandidate | None = None
    reviewed_teaching_example: ReviewedTeachingExample | None = None
    pack_mutation_proposal: PackMutationProposal | None = None

    # --- inference operators (ADR-0018) ---
    # Deterministic serialisation of any typed operator invoked during the
    # turn (e.g. transitive_walk over the teaching-store typed-relation
    # graph).  Empty string when no operator ran.  Folded into trace_hash
    # so operator invocation is a load-bearing part of replay equality.
    operator_invocation: str = ""

    # --- forward semantic control evidence (ADR-0023) ---
    # ``admissibility_trace`` is the per-transition record produced by
    # ``generate()`` (empty tuple when no admissibility ran).
    # ``admissibility_trace_hash`` is its canonical SHA-256, folded
    # into ``trace_hash`` only when non-empty so pre-ADR-0023 turn
    # hashes are byte-preserved.
    # ``ratification_outcome`` is the enum value ("ratified" /
    # "demoted" / "passthrough") from the field ratifier; empty
    # string when no ratification ran.
    # ``region_was_unconstrained`` records whether forward semantic
    # control was active on this turn — observation only, no
    # production fail-closed yet (see ADR-0023 §Out of scope).
    admissibility_trace: tuple = ()
    admissibility_trace_hash: str = ""
    ratification_outcome: str = ""
    region_was_unconstrained: bool = True

    # --- inner-loop refusal evidence (ADR-0024 Phase 2) ---
    # ``refusal_reason`` is the stable string value of a
    # ``generate.exhaustion.RefusalReason`` when the walk refused this
    # turn, or the empty string otherwise.  Empty-string default is
    # the contract for "no refusal materialised"; folding into
    # trace_hash is gated on non-emptiness so non-refused turns keep
    # byte-identical hashes relative to pre-Phase-2 (CLAUDE.md
    # determinism invariant).  Phase 2 leaves the materialisation site
    # in chat/runtime.py untouched per the ADR-0024 Phase 2 scope
    # decision — this field exists so the trace contract is already
    # in place when a future ADR wires the materialisation path.
    refusal_reason: str = ""

    # --- recognition / epistemic carrier (ADR-0144) ---
    # None when no DerivedRecognizer is attached, when recognition refused,
    # or on the very first turn before any recognizer is configured.
    # Non-None only when recognition admitted (state == EVIDENCED).
    # NOT folded into trace_hash in Phase 1 (observability only).
    epistemic_graph: EpistemicGraph | None = None

    # --- grounding dispatcher trace (ADR-0142) ---
    # None when no dispatch trace is collected or on pre-dispatch-trace turns.
    # NOT folded into trace_hash (observability only).
    dispatch_trace: DispatchTrace | None = None

    # --- compound intent observability (ADR-0089 Phase C1) ---
    # Finding 4 (audit 2026-05-20).  ``classify_compound_intent`` returns
    # multiple parts for inputs like "What is X and how does it relate
    # to Y?" but the pipeline still routes only the dominant clause
    # through the existing single-intent path.  Pre-fix the secondary
    # clauses were silently dropped — no observability, no telemetry,
    # no trace evidence.
    #
    # Phase C1 surfaces the dropped clauses here so operators can see
    # the lost signal without changing any current behaviour.  Phase
    # C2 (opt-in, flag-gated) will route the secondary clauses through
    # a multi-node graph; that wiring is deliberately scoped to a
    # separate PR per ADR-0089 because it widens
    # ``compute_trace_hash`` and the surface resolver contract.
    #
    # Empty tuple == this turn was single-clause OR the compound
    # classifier was not consulted; ``len > 0`` == this turn dropped
    # secondary clauses that were classified but not routed.
    dropped_compound_clauses: tuple[DialogueIntent, ...] = ()

    # --- invariant bookkeeping ---
    versor_condition: float = 0.0   # must be < 1e-6
    # Stage 3A — geometry-native turn coherence (orthogonal to vault EpistemicStatus).
    # None only on pre-Stage-3 artifacts; live pipeline always populates.
    geometric_coherence: GeometricCoherenceVerdict | None = None
    trace_hash: str = ""            # SHA-256 over deterministic key fields

    # --- response-governance leeway evidence (B4; observational, not in trace_hash) ---
    leeway: LeewayRecord | None = None

    # --- Shadow Coherence Gate / substrate authority (Phase A) ---
    # ``authority_source`` is the value from SurfaceResolution.authority:
    # "runtime_canonical" | "runtime_pre_decoration" | "runtime" | "realizer" | "substrate_realizer".
    # It is the single source of truth for which spine actually spoke.
    #
    # ``substrate_hazard`` is the machine-readable list of reasons the
    # geometric substrate was *not* granted authority on this turn even
    # though a PropositionGraph was produced. Populated only on bypass
    # paths. Observational (not folded into trace_hash in Phase A) so that
    # every existing turn keeps byte-identical hashes while the hazard
    # ledger illuminates the exact work remaining for Layers 1-3.
    #
    # These two fields turn the "Authority Flip Cliff" into a controlled,
    # data-driven strangler migration.
    authority_source: str = ""
    substrate_hazard: tuple[str, ...] = ()

    # --- Phase C instrumentation: Geometric Anti-Unification hook for OOV (read-only telemetry) ---
    # When an OOV subject is encountered in the context of a PropositionGraph
    # (i.e. a "hole" in S-P-[OOV] or similar), this carries the discrete
    # structural context (unresolved topology + intent) plus a placeholder
    # for exact CGA neighbor probe results (via vault.recall + cga_inner on
    # surrounding realized facts).
    #
    # Today: purely structural (from effective_graph.get_unresolved_topology()
    # when grounding_source indicates oov or pending slots on OOV-shaped
    # intents). No vault call yet (keeps change atomic + zero side effects).
    #
    # Future: perform *exact* geometric anti-unification here (sub-graph
    # match on conformal space) to propose SPECULATIVE algebraic variable
    # or relation type for the hole, without ever affecting user surface,
    # trace_hash (observational), or durable state. Must emit SPECULATIVE,
    # respect teaching boundary for any promotion.
    #
    # Pillars: Mechanical Sympathy (cheap structural + optional exact recall),
    # Semantic Rigor (exact CGA only, no approx), Third Door (graph structure
    # as first-class for inference instead of lexical substring).
    #
    # Never folded into trace_hash in this phase. Never mutates field/vault.
    oov_geometric_context: dict | None = None

    # --- 3-lang depth PropGraph unification observability (read-only, not in trace_hash) ---
    # Extracted from the same source as oov_geometric_context["node_depths"] / ["graph_anti_unify"]
    # (or the pre-context data) during pipeline construction for he/grc root-aware paths.
    # First-class optional fields so callers do not need to reach into the context dict.
    # Never folded into trace_hash (observational only, like oov_geometric_context).
    node_depths: dict | None = None
    graph_anti_unify: dict | None = None

    # --- Logos morph authority (observational + outcome-affecting when non-pass) ---
    # Populated when observed HE surface is present in the turn input and the
    # shared ``evaluate_logos_on_text`` path runs. Empty kind == not consulted.
    # Never folded into trace_hash as a separate key (surface/refusal already
    # capture the user-visible effect when morph blocks certification).
    logos_decision_kind: str = ""
    logos_decision_reason: str = ""
    logos_rule_id: str = ""
    logos_constraint_id: str = ""
    #: PR-9 (H-11) — ``repr`` of the exception the logos backstop absorbed, or
    #: "" when it did not fire. The guard stays deliberately broad (narrowing it
    #: would turn a malformed decision into a turn-spine crash); this is what
    #: stops it being silent. An empty ``logos_decision_kind`` used to mean
    #: either "not consulted" or "raised", which are very different facts about
    #: a turn. Observational; never folded into trace_hash.
    logos_error: str = ""
