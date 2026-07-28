"""
CognitiveTurnPipeline — the cognitive spine.

Architecture:
    listen -> ingest -> understand -> recall -> think -> articulate
           -> learn_proposal -> trace

This first-pass implementation delegates to ChatRuntime internals so
future intelligence modules (IntentPropositionGraph, ArticulationRealizerV2,
ReviewedTeachingLoop, CognitiveEvalHarness) have a clean plug-in surface
without requiring a full ChatRuntime rewrite.

Constraint: ChatRuntime.chat() and ChatResponse contract are unchanged.
"""

from __future__ import annotations

import json
from collections import OrderedDict

import numpy as np

from algebra.backend import versor_condition
from algebra.cl41 import geometric_product, reverse, scalar_part
from field.state import FieldState
from core.cognition.geometric_coherence import evaluate_geometric_coherence
from core.cognition.inductive_closure import expand_relation_closure
from core.cognition.leeway import build_leeway_record
from core.cognition.result import CognitiveTurnResult
from core.cognition.surface_resolution import resolve_surface
from core.cognition.trace import compute_trace_hash, hash_admissibility_trace
from core.physics.goldtether import coherence_residual
from core.physics.wave_manifold import multivector_content_digest
from core.reasoning.adapters import evidence_from_entailment_trace
from generate.intent import classify_compound_intent
from generate.intent_bridge import _is_useful_surface
from generate.intent_ratifier import ratify_intent
from generate.graph_planner import (
    GraphNode,
    PropositionGraph,
    graph_from_intent,
    ground_graph,
    plan_articulation,
)
from recognition.anti_unifier import DerivedRecognizer, recognize
from recognition.carrier import EpistemicGraph, EpistemicNode
from recognition.connector import epistemic_node_to_graph_node
from recognition.depth_canonical import build_node_depths
from generate.realizer import realize_semantic
from generate.intent import IntentTag
from generate.operators import (
    FrameComposeResult,
    WalkResult,
    compose_relations,
    multi_relation_walk,
    transitive_walk,
)
from generate.proof_chain import EntailmentTrace, evaluate_entailment_with_trace
from teaching.correction import CorrectionCandidate, extract_correction
from teaching.epistemic import EpistemicStatus
from teaching.review import ReviewedTeachingExample, review_correction
from teaching.store import PackMutationProposal, TeachingStore


# ADR-0021 §Articulation: surfaces backed by SPECULATIVE teaching material
# carry an explicit status marker.  Wording must match SPECULATIVE_MARKERS in
# evals/articulation_of_status/runner.py: "speculative" and "not yet reviewed"
# are both checked.
_SPECULATIVE_SURFACE_MARKER = "(speculative, not yet reviewed) "

# Reflexive query shapes that almost always refer back to the immediately
# prior speculative teaching even when the subject token is not repeated:
# "Has this been reviewed?", "Is your answer about X confirmed?".  Used to
# extend the marker beyond exact subject-token matches.
_REFLEXIVE_PROBE_MARKERS: tuple[str, ...] = (
    "your answer",
    "this answer",
    "has this",
    "is that",
    "confirmed",
    "reviewed",
    "verified",
)

# Splitter for extracting individual subject tokens from a parsed-triple
# subject like "correction: wisdom" → ("correction", "wisdom") — so probes
# about "wisdom" still match a SPECULATIVE proposal whose triple parser
# included a clarifying prefix.
import re as _re
_SUBJECT_SPLIT_RE = _re.compile(r"[^a-z0-9]+")
_SUBJECT_STOPWORDS: frozenset[str] = frozenset({
    "actually", "correction", "really", "indeed", "instead",
    "the", "this", "that", "these", "those",
    "is", "are", "was", "were", "been", "being",
    "of", "for", "with", "and", "but", "from",
    "your", "their", "answer",
})

# Conformal atom unification (dossier Subsystem C.1).
# Absolute "score > 1−ε" is only meaningful for normalized null-cone points
# with self-inner ≈ 1. Pack versors can have cross-inner > 1, so we unify when
# the mutual reverse-product matches both self-products within ε (exact same
# geometric atom), else content-address by SHA-256 of components.
_UNIFY_EPS = 1e-4

# Finding 5 (audit 2026-05-20) — cap the speculative-subjects cache so a
# long teaching session cannot grow it without bound.  64 is large enough
# to cover every distinct teaching subject a single session realistically
# emits and small enough that the per-turn substring scan in
# ``_should_mark_speculative`` stays trivially cheap.  LRU eviction: a
# subject re-encountered as SPECULATIVE refreshes its position; coherent
# promotion decrements its claim and removes it at zero.
_MAX_SPECULATIVE_SUBJECTS = 64

class CognitiveTurnPipeline:
    """Thin pipeline wrapper over ChatRuntime.

    Phase 1 goal: extract the observability path so downstream modules have
    a place to plug in.  No new intelligence is added here.
    """

    def __init__(
        self,
        runtime,
        teaching_store: TeachingStore | None = None,
        recognizer: DerivedRecognizer | None = None,
    ) -> None:  # runtime: ChatRuntime (no import cycle)
        self.runtime = runtime
        self._last_node_id: str | None = None
        self._current_node_depths: dict = {}
        self._current_agent_node_id: str | None = None
        self._last_node_depths: dict | None = None
        self.teaching_store = teaching_store if teaching_store is not None else TeachingStore()
        if recognizer is not None:
            self._recognizer = recognizer
        elif hasattr(runtime, "first_admitted_recognizer"):
            self._recognizer = runtime.first_admitted_recognizer()
        else:
            self._recognizer = None
        self._prior_surface: str | None = None
        self._turn_number: int = 0
        # ADR-0021 §Articulation: subjects of prior SPECULATIVE teaching
        # proposals.  When a later turn's input references one of these
        # (by subject substring or reflexive query shape), the surface
        # is prefixed with _SPECULATIVE_SURFACE_MARKER so the user can
        # tell ratified knowledge from unreviewed teaching material.
        #
        # Finding 5 (audit 2026-05-20) — backed by an OrderedDict so the
        # cache is bounded (LRU, cap ``_MAX_SPECULATIVE_SUBJECTS``) and
        # supports explicit eviction when a proposal is promoted to
        # COHERENT.  Pre-fix this was a bare ``set`` that only grew,
        # which both leaked speculative markers onto reviewed subjects
        # forever and widened the per-turn substring scan unboundedly.
        # Iteration order matches insertion / refresh order; lookups
        # remain O(1).
        #
        # H-13 (external-assessment triage, 2026-07-28) — the value is the
        # set of SUBJECTS CLAIMING this token, not a placeholder and not a
        # count.  Seeding indexes a subject under itself *and* under each
        # of its ≥4-char tokens, so two independent subjects can land on
        # one token ("wisdom" from both ``wisdom`` and ``practical
        # wisdom``).  While this was a flat set, teaching ``practical
        # wisdom`` coherently popped the shared token and an unrelated,
        # still-unreviewed ``wisdom`` proposal lost its marker — serving
        # speculative material as though reviewed.
        #
        # A reference count does not fix it, and the reason is the branch
        # structure at the call site: a proposal is EITHER seeded (when
        # SPECULATIVE) OR released (when COHERENT), never both, so a
        # release never balances a claim the same proposal made.  A
        # COHERENT proposal always releases claims it never held.
        # Claimants make that a no-op on other subjects' tokens: a token
        # dies only when the subject that actually claimed it is
        # reviewed.  Token derivation lives in these methods rather than
        # at the call site, because ownership is exactly what the call
        # site cannot see.
        self._speculative_subjects: OrderedDict[str, set[str]] = OrderedDict()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self, text: str, max_tokens: int | None = None) -> CognitiveTurnResult:
        """Execute one full cognitive turn and return a complete result record.

        Audit-ledger R7 — this pipeline owns the turn's telemetry emission.
        ``ChatRuntime.chat`` seals the ``TurnEvent`` before the surface
        authority and the canonical ``trace_hash`` are known, so an inline
        emission put a stale record into the durable stream while ``turn_log``
        was back-stamped and correct. The runtime cannot detect that a pipeline
        is wrapping it (the wrapping goes this way, not the other), so the
        deferral is declared here and flushed at the serve boundary below.

        The ``finally`` is load-bearing (I5): if anything between ``chat``
        returning and the serve boundary raises, the staged event must still
        reach the sink. Silently swallowing a telemetry record on the error path
        would be a worse failure than the staleness this repairs.
        """
        self.runtime.begin_deferred_turn_emission()
        try:
            return self._run_turn(text, max_tokens=max_tokens)
        finally:
            self.runtime.flush_deferred_turn_event()

    def _run_turn(self, text: str, max_tokens: int | None = None) -> CognitiveTurnResult:
        """The turn body. Call :meth:`run` — it owns the emission boundary."""

        # 0. TOKENIZE — once at the top; reused by recognition step and trace.
        raw_tokens: tuple[str, ...] = tuple(self.runtime.tokenize(text))

        # 0b. RECOGNIZE — if a DerivedRecognizer is attached (ADR-0144).
        # Admitted → wrap in EpistemicGraph for observability and optional
        # connector-grounded articulation.  Refused or absent → None.
        epistemic_graph: EpistemicGraph | None = None
        # W-011 — recognition refusal_reason, materialized below into
        # CognitiveTurnResult.refusal_reason when non-empty.
        _recognition_refusal_reason: str = ""
        if self._recognizer is not None:
            # Same-turn depth for recognition: resolve he/grc roots from tokens
            # before PropositionGraph exists (plan residual). Prefer early
            # provisional t{i} depths; fall back to current/prior-turn graph
            # depths for multi-turn chaining (AC1).
            from chat.pack_resolver import resolve_token_depths

            _early_depths, _early_agent = resolve_token_depths(raw_tokens)
            _prior_depths = (
                getattr(self, "_current_node_depths", None)
                or getattr(self, "_last_node_depths", None)
                or {}
            )
            _depths = _early_depths if _early_depths else _prior_depths
            _agent_nid = _early_agent or getattr(self, "_current_agent_node_id", None)
            _rec_outcome = recognize(
                self._recognizer, raw_tokens, depths=_depths, agent_node_id=_agent_nid
            )
            if _rec_outcome.admitted:
                _ep_node = EpistemicNode(
                    node_id=f"{self._recognizer.teaching_set_id}:{self._turn_number}",
                    recognition_outcome=_rec_outcome,
                )
                epistemic_graph = EpistemicGraph(
                    nodes=(_ep_node,),
                    recognizer_id=self._recognizer.teaching_set_id,
                )
                # ADR-0154 (W-020b) — producer-side wiring for the
                # DerivedRecognizer registry.  When a recognizer admits a
                # turn, capture (tokens, bundle) so the registry can
                # derive tighter recognizers via anti-unification at the
                # next checkpoint.  Pre-ADR-0154 the producer hook had
                # no production caller (only tests invoked
                # ``record_recognition_example``), so the registry
                # could never grow from live traffic regardless of
                # whether ``recognition_grounded_graph`` was enabled.
                # The producer fires unconditionally; the consumer
                # (``checkpoint_engine_state``'s derive_recognizer
                # call) stays opt-in behind the same flag.
                if (
                    _rec_outcome.proposition is not None
                    and hasattr(self.runtime, "record_recognition_example")
                ):
                    self.runtime.record_recognition_example(
                        raw_tokens, _rec_outcome.proposition
                    )
            elif _rec_outcome.refusal_reason is not None:
                from generate.exhaustion import RefusalReason as _ExhaustionRefusalReason
                _recognition_refusal_reason = _ExhaustionRefusalReason.RECOGNITION_REFUSED.value

        # 1. LISTEN — capture pre-turn field state. If absent, compile turn
        # tokens into an initial Cl(4,1) wave-packet before intent ratification
        # (Geometric Sovereignty — cold-start must compile a field first).
        field_state_before: FieldState | None = self._capture_field_state()
        if field_state_before is None or getattr(field_state_before, "F", None) is None:
            field_state_before = self._compile_turn_wave_packet(raw_tokens)

        # 1b. CLASSIFY — intent and proposition graph (deterministic, pre-chat)
        # ADR-0089 Phase C1 (Finding 4, audit 2026-05-20) — run the
        # compound classifier first and take its dominant clause as
        # the seeded intent.  ``classify_compound_intent`` already
        # invokes ``classify_intent`` on the dominant fragment, so
        # this is one regex cascade per turn instead of two (comb
        # pass 2026-05-21).  Secondary clauses surface on
        # ``CognitiveTurnResult.dropped_compound_clauses`` as
        # observability telemetry; the dominant clause continues to
        # route through the existing single-intent path.
        compound = classify_compound_intent(text)
        seeded_intent = compound.primary
        dropped_compound_clauses: tuple = (
            tuple(compound.parts[1:]) if compound.is_compound() else ()
        )
        # 1b.i FIELD-RATIFY the seeded intent (ADR-0022 §TBD-1).
        #      The regex classifier is the *seed*; the field is the
        #      gate.  A demoted intent routes the rest of the turn
        #      through the existing UNKNOWN-domain surface so the
        #      pipeline never silently relaxes a constraint to produce
        #      a fluent-but-ungrounded surface (§2 honest refusal).
        ratified = self._ratify_intent(seeded_intent, field_state_before)
        intent = ratified.intent
        prior_node_id = self._last_node_id
        graph = graph_from_intent(intent, prior_node_id=prior_node_id)
        target = plan_articulation(graph)

        # 1b.ii RECOGNITION-GROUNDED GRAPH (ADR-0144, opt-in).
        # When recognition admitted and the operator has opted in, replace the
        # intent-derived graph and articulation target with ones derived from
        # the admitted EpistemicNode via the connector.  Default False preserves
        # byte-identity for every existing surface and trace_hash.
        if self.runtime.config.recognition_grounded_graph and epistemic_graph is not None:
            _derived_gn = epistemic_node_to_graph_node(
                epistemic_graph.nodes[0], source_intent=intent.tag
            )
            graph = PropositionGraph().add_node(_derived_gn)
            target = plan_articulation(graph)

        # 1c. REALIZE — semantic realization from graph + intent.
        # Pre-fix (and default today) the realizer fires on the
        # ungrounded graph and emits ``<pending>`` / ``...`` surfaces
        # that ``_is_useful_surface`` rejects.  ADR-0088 Phase B opts
        # operators into grounding the graph BEFORE the realizer so
        # the realizer can compete as a real surface authority.
        realized_plan = realize_semantic(target, graph)

        # 2–7. INGEST / UNDERSTAND / RECALL / THINK / ARTICULATE / LEARN
        #       Delegated to ChatRuntime.chat().
        #       ChatResponse is the stable contract surface.
        response = self.runtime.chat(text, max_tokens=max_tokens)

        # ADR-0088 Phase B (audit Finding 2, 2026-05-20) — opt-in
        # grounded realizer.  When the runtime opts in, fill the
        # graph's <pending> obj slots from the recall step's walk
        # tokens (already alphabetic-filtered by ChatRuntime) and
        # re-invoke ``realize_semantic`` on the grounded graph.  The
        # surface resolver (PR #76) then picks the realizer's
        # grounded output when it clears ``_is_useful_surface`` and
        # the unknown-domain gate did not fire.  Default-off
        # preserves byte-identity for every existing surface and
        # trace_hash — the realizer continues to emit unusable
        # placeholders and lose the resolver to the runtime path.
        # Comb pass 2026-05-21 — direct attribute access; these fields
        # all live on ChatResponse with documented defaults (PR #88 for
        # ``realizer_grounded_authority`` + ``recalled_words``, ADR-0048
        # for ``grounding_source``, ADR-0077 for
        # ``register_canonical_surface``, ADR-0071 for
        # ``pre_decoration_surface``).  The historical ``getattr`` calls
        # were ADR-introduction defensiveness now safe to drop.
        # Grounding (when opted in) produces the effective graph for the
        # supremacy decision + stored result + topological hash. The
        # original intent-derived `graph` is the starting plan; effective
        # is the substrate view after recall grounding (when active).
        # This ensures the graph carried in CognitiveTurnResult and
        # folded into trace_hash reflects the actual reasoning used.
        effective_graph = graph
        recalled_words = response.recalled_words or ()
        # Depth enrichment is now DEFAULT (AC2) for 3-lang mastery on spine.
        # ALWAYS attempt per-subject resolution + GraphNode lang/root enrichment
        # (independent of is_fully_grounded) so node_depths / graph_anti_unify
        # and result fields are populated for both OOV/pending and grounded 3-lang cases.
        # The grounded authority flag only controls the recalled_words fill + re-realize.
        # Collect unique subjects, resolve with depth packs for language/root/gloss.
        # This feeds both recalled_words (for ground_graph) and per-node enrichment.
        if effective_graph:
            subjects = []
            seen = set()
            for n in effective_graph.nodes:
                s = n.subject.strip().lower()
                if s and s not in seen:
                    seen.add(s)
                    subjects.append(s)

            from chat.pack_resolver import (
                DEFAULT_RESOLVABLE_PACK_IDS,
                resolve_entry,
                resolve_gloss,
                resolve_lemma,
            )
            # Master bidirectional entry point: LexicalResolution carries
            # 3-language depth (Hebrew roots, Greek precision) usable for
            # graph grounding (comprehension), later realization (articulation),
            # and contemplation/reasoning on the shared PropositionGraph.
            from chat.pack_resolver import DEPTH_PACK_IDS
            depth_pack_ids = DEFAULT_RESOLVABLE_PACK_IDS + DEPTH_PACK_IDS

            subject_to_res = {}
            for s in subjects:
                res = resolve_entry(s, pack_ids=depth_pack_ids)
                subject_to_res[s] = res

            # Collect glosses for pending nodes in order (feeds ground_graph sequentially)
            # (only when not fully grounded, to preserve prior behavior for gloss fill)
            if not effective_graph.is_fully_grounded():
                recalled_glosses = []
                for n in effective_graph.nodes:
                    obj = n.obj
                    if obj in (None, "", "<pending>", "<prior>") or (isinstance(obj, str) and "..." in obj):
                        s = n.subject.strip().lower()
                        res = subject_to_res.get(s)
                        if res and getattr(res, 'gloss', None):
                            recalled_glosses.append(res.gloss)
                        elif resolve_lemma(n.subject):
                            # legacy fallback per-subject
                            g = resolve_gloss(n.subject)
                            if g:
                                _, _, gloss_text = g
                                if gloss_text:
                                    recalled_glosses.append(gloss_text)
                if recalled_glosses:
                    recalled_words = tuple(recalled_glosses)

            # Enrich every node with its subject's resolution (subject→node map)
            # Immutable; only rebuild if any depth present. ALWAYS for 3-lang depth support.
            if subject_to_res:
                new_nodes = []
                changed = False
                for n in effective_graph.nodes:
                    s = n.subject.strip().lower()
                    res = subject_to_res.get(s)
                    if res and (getattr(res, 'language', None) or getattr(res, 'root', None) or getattr(res, 'morphology_id', None)):
                        enriched = GraphNode(
                            node_id=n.node_id,
                            subject=n.subject,
                            predicate=n.predicate,
                            obj=n.obj,
                            source_intent=n.source_intent,
                            language=getattr(res, 'language', None),
                            root=getattr(res, 'root', None),
                            morphology_id=getattr(res, 'morphology_id', None),
                            # Depth enrichment must not launder a denial away.
                            # This rebuild is on the ADR-0088 Phase B path, the
                            # one where the realizer's surface actually wins.
                            negated=n.negated,
                        )
                        new_nodes.append(enriched)
                        changed = True
                    else:
                        new_nodes.append(n)
                if changed:
                    effective_graph = PropositionGraph(
                        nodes=tuple(new_nodes),
                        edges=effective_graph.edges,
                    )
        if self.runtime.config.realizer_grounded_authority and recalled_words:
            # Ground using recalled_words + depth map (alongside) so
            # 3-lang info propagates even if not pre-enriched on nodes.
            # Flag only gates this recall-fill step for compat.
            depth_map = {}
            for n in effective_graph.nodes:
                if n.language or n.root or n.morphology_id:
                    depth_map[n.node_id] = (n.language, n.root, n.morphology_id)
            grounded_graph = ground_graph(effective_graph, recalled_words, depth=depth_map)
            realized_plan = realize_semantic(target, grounded_graph)
            effective_graph = grounded_graph

        # Physical coherence only (vault_hits bookkeeping is not a gate).
        # gate_fired True ⇒ residual failure ⇒ substrate realizer refused.
        field_for_gate = self._capture_field_state()
        F_gate = getattr(field_for_gate, "F", None) if field_for_gate is not None else None
        if F_gate is None and field_state_before is not None:
            F_gate = field_state_before.F
        contract_assessment = self._geometry_contract_assessment(F_gate)
        gate_fired = bool(
            contract_assessment.missing_bindings
            or contract_assessment.unresolved_hazards
        )
        canonical = response.register_canonical_surface
        pre_decoration = response.pre_decoration_surface

        # Comb pass 2026-05-21 — materialize teaching-store triples once
        # per turn.  Pre-fix both ``_maybe_transitive_walk`` and
        # ``_maybe_compose_relations`` called ``self.teaching_store.triples()``
        # independently, doubling the per-turn O(N) filter+tuple-build
        # cost as the corpus grows.
        triples = self.teaching_store.triples()

        walk_result: WalkResult | None = self._maybe_transitive_walk(intent, triples)
        walk_surface = ""
        if walk_result is not None and len(walk_result.path) > 1:
            walk_surface = CognitiveTurnPipeline._render_walk_surface(walk_result)

        compose_result: FrameComposeResult | None = self._maybe_compose_relations(intent, triples)
        compose_surface = ""
        if compose_result is not None and (
            compose_result.subject_tail is not None
            or compose_result.frame_tail is not None
        ):
            compose_surface = CognitiveTurnPipeline._render_compose_surface(compose_result)

        # Stage 3C — bounded inductive closure over teaching-store relations.
        # Provenance-preserving fixed-point; derived edges require geometric
        # admissibility (closed Cl(4,1) versors when vocab can ground them).
        def _geom_admissible(h: str, r: str, t: str) -> bool:
            del r
            hv = self._resolve_surface_versor(h)
            tv = self._resolve_surface_versor(t)
            if hv is None or tv is None:
                # Ungrounded endpoints cannot be promoted as geometric facts.
                return False
            return (
                float(versor_condition(hv)) < 1e-6
                and float(versor_condition(tv)) < 1e-6
            )

        inductive_closure = expand_relation_closure(
            triples,
            budget=16,
            geometric_admissible=_geom_admissible,
        )

        entailment_trace = self._maybe_entailment_trace(intent, triples)

        # === SHADOW COHERENCE GATE WIRING ===
        # Dual-competing: substrate supremacy requires fully grounded graph
        # AND closed geometric contract (versor_condition + GoldTether residual).
        # Grounding provenance (pack/teaching/vault/oov/…) is read once here and
        # reused for the OOV telemetry below; the gate consumes it to route an
        # open-geometry-but-pack-grounded surface to the hedge arm (T13 dec. 2).
        grounding_src = getattr(response, "grounding_source", "") or ""
        resolved = resolve_surface(
            canonical_surface=canonical,
            pre_decoration_surface=pre_decoration,
            response_surface=response.surface,
            response_articulation_surface=response.articulation_surface,
            realized_surface=realized_plan.surface,
            realizer_useful=_is_useful_surface(realized_plan.surface),
            gate_fired=gate_fired,
            walk_surface=walk_surface,
            compose_surface=compose_surface,
            proposition_graph=effective_graph,
            contract_assessment=contract_assessment,
            grounding_provenance=grounding_src,
        )
        surface = resolved.surface
        # Truth-path bytes for trace_hash (ADR-0069 inv C): the served
        # surface carries register R6/R4 transforms and MUST NOT move the
        # hash; hash_surface is the register-invariant canonical-precedence
        # capture, kept in lockstep with every served-surface mutation below.
        hash_surface = resolved.hash_surface or resolved.surface
        articulation_surface = resolved.articulation_surface
        authority_source = resolved.authority

        # === LOGOS MORPH AUTHORITY (bulk live seam) ===
        # Same pure decision function as teaching store + four-arm ablation.
        # Executable morph may force abstain/refuse; never soft-pass a
        # certified singular-exclusivity claim against observed plural HE.
        # English-only turns with no HE surface → no-op (None).
        logos_decision_kind = ""
        logos_decision_reason = ""
        logos_rule_id = ""
        logos_constraint_id = ""
        logos_decision = None
        try:
            from generate.observed_he_morph_v0.authority import (
                decision_as_coherence_refusal,
                evaluate_logos_on_text,
                first_logos_constraint,
                logos_blocks_certified_answer,
            )

            logos_decision = evaluate_logos_on_text(text=text, mode="executable")
            if logos_decision is not None:
                logos_decision_kind = logos_decision.kind.value
                logos_decision_reason = logos_decision.reason
                logos_rule_id = logos_decision.rule_id or ""
                lc = first_logos_constraint(logos_decision)
                if lc is not None:
                    logos_constraint_id = lc.constraint_id
                if logos_blocks_certified_answer(logos_decision):
                    refusal = decision_as_coherence_refusal(logos_decision)
                    surface = refusal.surface_message or refusal.message
                    hash_surface = surface
                    articulation_surface = surface
                    authority_source = "logos_morph_constraint"
        except Exception:
            # Pack load / catalog failure must not crash the turn spine;
            # English path continues without morph authority.
            logos_decision = None

        # SUBSTRATE_BYPASS_HAZARD telemetry (data-driven roadmap).
        # Only populated when a graph existed yet substrate did not win.
        # This is *observability only* — never used to change control flow
        # after the fact, never folded into trace_hash in Phase A.
        substrate_hazard: tuple[str, ...] = ()
        if effective_graph is not None and authority_source not in (
            "substrate_realizer",
            "realizer",
            "logos_morph_constraint",
        ):
            reasons: list[str] = []
            if not effective_graph.is_fully_grounded():
                reasons.append("unfilled_pending_slots")
                # include the exact nodes for precision (Strangler diagnostic)
                unresolved = effective_graph.get_unresolved_topology()
                if unresolved:
                    reasons.append(f"unresolved_nodes={unresolved}")
            if gate_fired:
                reasons.append("unknown_domain_gate_fired")
            if not _is_useful_surface(realized_plan.surface):
                reasons.append("realizer_surface_not_useful")
            substrate_hazard = tuple(reasons)
        if logos_decision is not None and logos_blocks_certified_answer(logos_decision):
            substrate_hazard = substrate_hazard + (
                f"logos_morph_{logos_decision.kind.value}",
                logos_decision.reason,
            )

        # Phase C (Geometric Anti-Unification) — read-only telemetry instrumentation.
        # Captures the graph-structural context around any OOV/pending "hole"
        # so that a future exact-CGA sub-graph anti-unifier can operate on
        # conformal neighbors rather than lexical token match.
        # Populated observationally; never affects surface, hash (yet), or
        # any durable mutation. Uses only what the substrate already produced.
        oov_geometric_context = None
        # grounding_src is computed above at the gate-wiring seam and reused here.
        has_pending = bool(effective_graph and any(
            (n.obj or "") in ("", "<pending>") or "..." in (n.obj or "")
            for n in effective_graph.nodes
        ))
        # AC2: node_depths in oov_geometric_context by default for all PropGraph paths
        # Use pure build_node_depths for canonical extraction (nid-keyed).
        node_depths = build_node_depths(effective_graph.nodes) if effective_graph else {}
        if grounding_src == "oov" or has_pending:
            # Active conformal neighborhood probe (exact cga_inner over vault).
            probe_performed = False
            probe_neighbors: list[dict[str, object]] = []
            try:
                from algebra.backend import cga_inner as _cga_inner

                F_probe = getattr(self._capture_field_state(), "F", None)
                vault = getattr(getattr(self.runtime, "session", None), "vault", None)
                if F_probe is not None and vault is not None and hasattr(vault, "entries"):
                    scores: list[tuple[float, str]] = []
                    for entry in list(vault.entries())[:64]:
                        versor = getattr(entry, "versor", None)
                        if versor is None and isinstance(entry, (tuple, list)) and entry:
                            versor = entry[0]
                        if versor is None:
                            continue
                        try:
                            s = float(_cga_inner(F_probe, versor))
                        except Exception:
                            continue
                        label = str(getattr(entry, "id", "") or getattr(entry, "key", "") or "")
                        scores.append((s, label))
                    scores.sort(key=lambda item: item[0], reverse=True)
                    probe_neighbors = [
                        {"cga_inner": s, "ref": lab} for s, lab in scores[:5]
                    ]
                    probe_performed = True
            except Exception:
                probe_performed = False
            oov_geometric_context = {
                "unresolved_topology": effective_graph.get_unresolved_topology() if effective_graph else (),
                "intent_tag": getattr(intent, "tag", None).value if intent and getattr(intent, "tag", None) else "unknown",
                "geometric_probe_performed": probe_performed,
                "conformal_neighbors": probe_neighbors,
                "note": "Conformal anti-unification probe: vault neighbors via exact cga_inner.",
                "node_depths": node_depths,
            }
        else:
            # default for PropGraph: at least node_depths
            if effective_graph:
                oov_geometric_context = {
                    "node_depths": node_depths,
                    "note": "default depth context for PropGraph (AC2)",
                }

        # Phase 4: include graph-level anti-unify result (unresolved topo + roots) for observability on spine.
        if node_depths and effective_graph:
            try:
                from recognition.anti_unifier import graph_anti_unify
                topo = tuple(n.node_id for n in effective_graph.nodes)
                if oov_geometric_context is None:
                    oov_geometric_context = {}
                oov_geometric_context["graph_anti_unify"] = graph_anti_unify(topo, node_depths)
            except Exception:
                # Best-effort telemetry only; anti-unify failure must not affect main path.
                pass

        # Capture depths (post-enrich) to attrs for recognize chaining (AC1) + runtime contemplate depth= (real).
        # Propagation contract (3-lang depth on PropGraph spine): pipeline (after OOV/PropGraph construction)
        # writes _last_node_depths (and now also top-level on CognitiveTurnResult) so that
        # runtime.contemplate(...) and teaching/contemplation paths forward depth= without
        # re-resolving packs. Depths originate from pack_resolver + build_node_depths on GraphNode.
        # This is the current minimal cross-component channel (observational). See docs/ and review.

        if node_depths:
            self._current_node_depths = node_depths
            if effective_graph and effective_graph.nodes:
                self._current_agent_node_id = effective_graph.nodes[0].node_id
            self._last_node_depths = node_depths
            # Direct assignment now that runtime explicitly declares the attr (cleanup of hasattr/setattr dance)
            self.runtime._last_node_depths = node_depths

        # Track last node id for correction-intent chaining
        if graph.nodes:
            self._last_node_id = graph.nodes[-1].node_id

        # 8. CAPTURE post-turn field state
        field_state_after: FieldState = self.runtime.session.state

        # 9. Reconstruct input-layer tokens from the turn log
        #    (turn_log is appended inside chat(); last entry matches this turn)
        #    When the unknown-domain gate fires, chat() returns a stub without
        #    appending to turn_log — fall back to raw_tokens (set at step 0).
        if self.runtime.turn_log:
            last_turn = self.runtime.turn_log[-1]
            filtered_tokens = last_turn.input_tokens
        else:
            filtered_tokens = raw_tokens

        # 9b. ARTICULATE STATUS — if any prior turn produced a SPECULATIVE
        # teaching proposal whose subject is referenced by the current
        # input (subject substring or reflexive query shape), prepend a
        # status marker so the user can distinguish reviewed knowledge
        # from unreviewed teaching material.  ADR-0021 §Articulation.
        # Decision uses subjects seeded by prior turns; this turn's own
        # proposal (if any) is added below for FUTURE turns to see.
        if self._speculative_subjects and surface and self._should_mark_speculative(text, surface):
            surface = _SPECULATIVE_SURFACE_MARKER + surface
            hash_surface = _SPECULATIVE_SURFACE_MARKER + hash_surface
            articulation_surface = _SPECULATIVE_SURFACE_MARKER + articulation_surface

        # 10. TEACHING — correction capture, review, and store
        teaching_candidate, reviewed_example, proposal = self._run_teaching(
            text, intent, self._turn_number,
            identity_score=response.identity_score,
        )

        # 10b. TRACK SPECULATIVE SUBJECTS — seed the marker decision for
        # future turns.  Done AFTER the marker check above so the teach
        # turn itself does not self-mark; only subsequent probes do.
        # Prefer the parsed-triple subject (clean: "truth") over the raw
        # proposal.subject (often a fragment of the correction text);
        # also split-and-add each ≥4-char token so prefixed parses like
        # "correction: wisdom" still match a probe about "wisdom".
        if proposal is not None:
            sources: list[str] = []
            if proposal.triple is not None and proposal.triple[0]:
                sources.append(proposal.triple[0])
            if proposal.subject:
                sources.append(proposal.subject)
            if proposal.epistemic_status is EpistemicStatus.SPECULATIVE:
                for src in sources:
                    self._remember_speculative_subject(src)
            elif proposal.epistemic_status is EpistemicStatus.COHERENT:
                # Finding 5 (audit 2026-05-20) — once teaching review
                # returns COHERENT, the subject is no longer speculative;
                # release its claims so the marker stops appearing on
                # subsequent probes about it.
                #
                # H-13 — the split-and-add loop that used to live here has
                # moved inside the cache.  Doing it out here made every
                # token its own claimant, so releasing "practical wisdom"
                # also released the token "wisdom" that an unrelated,
                # still-unreviewed proposal was relying on.
                for src in sources:
                    self._forget_speculative_subject(src)

        # Advance turn counter and remember surface for next correction binding.
        # The truth-path surface (not the served, register-decorated bytes)
        # feeds correction binding so register packs cannot perturb teaching.
        self._turn_number += 1
        self._prior_surface = hash_surface

        # 11. TRACE — deterministic hash (includes teaching IDs and any
        # typed-operator invocation per ADR-0018).
        review_hash = reviewed_example.review_hash if reviewed_example is not None else ""
        proposal_id = proposal.proposal_id if proposal is not None else ""
        epistemic_status = proposal.epistemic_status.value if proposal is not None else ""
        walk_serialised = CognitiveTurnPipeline._serialize_operator(walk_result)
        compose_serialised = CognitiveTurnPipeline._serialize_operator(compose_result)
        entailment_serialised = CognitiveTurnPipeline._serialize_entailment_trace(
            entailment_trace
        )
        # Stage 3C — inductive fixed-point provenance (before hash so replay
        # includes multi-step derivation when teaching store has chains).
        inductive_serialised = ""
        if inductive_closure.derived or inductive_closure.contradictions:
            inductive_serialised = json.dumps(
                {
                    "inductive_closure": {
                        "n_derived": len(inductive_closure.derived),
                        "n_contradictions": len(inductive_closure.contradictions),
                        "steps_taken": inductive_closure.steps_taken,
                        "fixed_point": inductive_closure.fixed_point,
                        "truncated": inductive_closure.truncated,
                        "derived": [d.as_dict() for d in inductive_closure.derived[:8]],
                    }
                },
                sort_keys=True,
                ensure_ascii=False,
            )
        # Deterministic concatenation: walk, compose, entailment, inductive.
        # Empty strings are dropped so unaffected turns keep existing trace bytes.
        operator_invocation = "|".join(
            s
            for s in (
                walk_serialised,
                compose_serialised,
                entailment_serialised,
                inductive_serialised,
            )
            if s
        )
        # ADR-0023 — admissibility trace + ratification provenance.
        # Comb pass 2026-05-21 — direct attribute access; the fields
        # are dataclass-defaulted on ChatResponse, so the prior
        # ``getattr`` guard was dead defensiveness from the ADR
        # introduction window.
        admissibility_trace = response.admissibility_trace
        region_was_unconstrained = response.region_was_unconstrained
        admissibility_trace_hash = hash_admissibility_trace(admissibility_trace)
        # Geometric ratification outcomes only (ratified | demoted).
        ratification_outcome = ratified.outcome.value
        _trace_ratification_outcome = ratification_outcome
        # ADR-0024 Phase 2 + W-011 — refusal_reason precedence:
        # recognition wins (earlier-fail boundary) over generation.
        _generation_refusal_reason = getattr(response, "refusal_reason", "") or ""
        refusal_reason = _recognition_refusal_reason or _generation_refusal_reason
        # Logos morph abstain/fail-closed is answer-authority: surface the reason
        # when morph blocked certification (does not override recognition refuse).
        if not refusal_reason and logos_decision_kind in ("abstain", "fail_closed"):
            refusal_reason = logos_decision_reason

        # Phase B — Quantized Topological Hashing for the cognitive spine.
        # Include the discrete (string-only) topological form of the
        # PropositionGraph that was produced for this turn. This is the
        # Merkle-DAG of the "think" step (nodes + directed relations).
        # - Uses graph.to_json() which is canonical, sort_keys JSON of
        #   the DAG (no floats, no geometry).
        # - Conditional on presence (already is) but the key is only added
        #   in compute_trace_hash when non-empty, preserving byte identity
        #   for any legacy pre-inclusion behavior in other contexts.
        # - Addresses the Trace Equivalence Hazard: same topology on any
        #   hardware/backend produces identical contribution to the SHA.
        # The continuous versor_condition (rounded) is kept only as the
        # runtime guard; actual geometric state lives in field/vault and
        # is never raw-hashed here.
        graph_topo = effective_graph.to_json() if effective_graph is not None else ""
        trace_hash = compute_trace_hash(
            input_text=text,
            filtered_tokens=filtered_tokens,
            surface=hash_surface,
            walk_surface=response.walk_surface,
            articulation_surface=articulation_surface,
            dialogue_role=str(response.dialogue_role),
            versor_condition=response.versor_condition,
            vault_hits=response.vault_hits,
            intent_tag=intent.tag.value,
            teaching_review_hash=review_hash,
            teaching_proposal_id=proposal_id,
            teaching_epistemic_status=epistemic_status,
            operator_invocation=operator_invocation,
            admissibility_trace_hash=admissibility_trace_hash,
            ratification_outcome=_trace_ratification_outcome,
            region_was_unconstrained=region_was_unconstrained,
            refusal_reason=refusal_reason,
            proposition_graph=graph_topo,
        )

        # ADR-0153 (W-020a) — back-stamp the canonical trace_hash onto
        # the runtime's most-recent TurnEvent and any DiscoveryCandidate
        # emitted during this turn.  The runtime cannot compute
        # trace_hash itself (the pipeline owns ``compute_trace_hash``),
        # so candidates were previously persisted with empty
        # ``source_turn_trace``.  See runtime.finalize_turn_trace_hash.
        self.runtime.finalize_turn_trace_hash(trace_hash)

        # Weekly-audit T13 (2026-07-22) — back-stamp the pipeline's final
        # *served* surface onto the same TurnEvent, sibling to the
        # trace_hash back-stamp above.  ``resolve_surface`` + the logos-morph
        # authority (above) can override the runtime-owned surface AFTER
        # ``runtime.chat`` sealed the TurnEvent, so without this the
        # telemetry record disagrees with the served bytes
        # (warmed_session_consistency telemetry_consistency_rate < 1.0;
        # breaks audit/replay trust — Absolute Provenance).
        self.runtime.finalize_turn_surface(surface, articulation_surface)

        # B4 producer: capture the leeway the response path already decided —
        # observational only (reads the runtime's introspection-only accrual and
        # the response's reach level; never alters the surface, never gates).
        accrual = (
            self.runtime.last_turn_accrual()
            if hasattr(self.runtime, "last_turn_accrual")
            else None
        )
        leeway = build_leeway_record(
            reach_level=str(getattr(response, "reach_level", "strict") or "strict"),
            license_decision=getattr(accrual, "license", None),
        )

        # Stage 3A — turn-level geometric coherence (orthogonal to vault COHERENT).
        geo_F = F_gate
        if geo_F is None and field_state_after is not None:
            geo_F = getattr(field_state_after, "F", None)
        geometric_coherence = evaluate_geometric_coherence(
            geo_F,
            identity_score=response.identity_score,
        )

        return CognitiveTurnResult(
            input_text=text,
            input_tokens=raw_tokens,
            filtered_tokens=filtered_tokens,
            field_state_before=field_state_before,
            field_state_after=field_state_after,
            proposition=response.proposition,
            articulation=response.articulation,
            surface=surface,
            hash_surface=hash_surface,
            walk_surface=response.walk_surface,
            articulation_surface=articulation_surface,
            dialogue_role=response.dialogue_role,
            identity_score=response.identity_score,
            vault_hits=response.vault_hits,
            recall_energy_class=response.recall_energy_class,
            intent=intent,
            # Use effective_graph (the post-grounding view when substrate
            # grounding was active) so that the stored PropositionGraph
            # reflects what the Shadow Coherence Gate / realizer actually
            # used for articulation. This makes result.proposition_graph
            # + trace hash (via topo) consistent with the executed spine.
            # For the common case (no grounding) this is identical to the
            # intent-derived graph.
            proposition_graph=effective_graph,
            articulation_target=target,
            teaching_candidate=teaching_candidate,
            reviewed_teaching_example=reviewed_example,
            pack_mutation_proposal=proposal,
            operator_invocation=operator_invocation,
            admissibility_trace=admissibility_trace,
            admissibility_trace_hash=admissibility_trace_hash,
            ratification_outcome=ratification_outcome,
            region_was_unconstrained=region_was_unconstrained,
            refusal_reason=refusal_reason,
            epistemic_graph=epistemic_graph,
            dispatch_trace=getattr(response, "dispatch_trace", None),
            dropped_compound_clauses=dropped_compound_clauses,
            versor_condition=response.versor_condition,
            geometric_coherence=geometric_coherence,
            trace_hash=trace_hash,
            leeway=leeway,
            # Phase A — Shadow Coherence Gate observability.
            # authority_source makes the winner of the substrate vs legacy
            # decision first-class evidence (visible in trace, workbench,
            # evals). substrate_hazard is the precise bypass signal.
            # Logos morph may override to "logos_morph_constraint" when it
            # blocks certified answers (same decision fn as teaching/ablation).
            authority_source=authority_source,
            substrate_hazard=substrate_hazard,
            oov_geometric_context=oov_geometric_context,
            # 3-lang depth unification: surface the same data at top level on result
            # (extracted from pre-computed node_depths var or oov_geometric_context to keep single source)
            node_depths=node_depths if node_depths else None,
            graph_anti_unify=(oov_geometric_context or {}).get("graph_anti_unify") if oov_geometric_context else None,
            logos_decision_kind=logos_decision_kind,
            logos_decision_reason=logos_decision_reason,
            logos_rule_id=logos_rule_id,
            logos_constraint_id=logos_constraint_id,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _compile_turn_wave_packet(self, tokens: tuple[str, ...] | list[str]) -> FieldState:
        """Compile turn tokens into an initial Cl(4,1) field on the manifold.

        Uses the session inject/probe path (holonomy encode + normalize_to_versor
        at the owned ingest boundary). Does not replace session state when
        probe_ingest is available (chat() still owns commit).
        """
        session = getattr(self.runtime, "session", None)
        if session is None:
            raise RuntimeError(
                "CognitiveTurnPipeline cannot compile a wave-packet without a session"
            )
        token_list = [str(t) for t in tokens]
        if not token_list:
            token_list = ["_empty_"]
        if hasattr(session, "probe_ingest"):
            return session.probe_ingest(token_list)
        from ingest.gate import inject

        vocab = getattr(session, "vocab", None)
        if vocab is None:
            raise RuntimeError(
                "CognitiveTurnPipeline cannot compile a wave-packet without session.vocab"
            )
        return inject(token_list, vocab)

    @staticmethod
    def _geometry_contract_assessment(F):
        """Build contract assessment from active versor + GoldTether residuals.

        Closed only when versor_condition(F) < 1e-6 and R_GoldTether ≤ 1e-6.
        Local import avoids chat → cognition → problem_frame_contracts cycles
        (problem_frame_contracts imports chat.pack_resolver).
        """
        from generate.problem_frame_contracts import ContractAssessment

        if F is None:
            return ContractAssessment(
                candidate_organ="shadow_coherence_gate",
                missing_bindings=("missing_wave_field",),
                unresolved_hazards=(),
                runnable=False,
                explanation="no field versor available for geometric contract",
            )
        vc = float(versor_condition(F))
        r_gt = float(coherence_residual(F))
        missing: list[str] = []
        hazards: list[str] = []
        if vc >= 1e-6:
            missing.append("versor_condition")
        if r_gt > 1e-6:
            hazards.append("goldtether_residual")
        return ContractAssessment(
            candidate_organ="shadow_coherence_gate",
            missing_bindings=tuple(missing),
            unresolved_hazards=tuple(hazards),
            runnable=not missing and not hazards,
            explanation=(
                f"versor_condition={vc:.3e}; R_GoldTether={r_gt:.3e}"
            ),
        )

    def _ratify_intent(self, intent, field_state):
        """Field-ratify a seeded intent (ADR-0022 §TBD-1).

        Geometric Sovereignty: field must already be compiled (see :meth:`run`);
        vocab and prompt versor are required for conformal ratification.
        """
        if field_state is None or getattr(field_state, "F", None) is None:
            raise RuntimeError(
                "intent ratification requires a compiled Cl(4,1) field state"
            )
        session = getattr(self.runtime, "session", None)
        vocab = getattr(session, "vocab", None) if session is not None else None
        if vocab is None:
            raise RuntimeError(
                "intent ratification requires session.vocab"
            )
        prompt_versor = field_state.F
        return ratify_intent(intent, prompt_versor, vocab=vocab)

    @staticmethod
    def _speculative_index_tokens(subject: str) -> tuple[str, tuple[str, ...]]:
        """Return ``(owner, tokens)`` — how one subject is indexed.

        The owner is the normalized subject itself; the tokens are the
        owner plus each ≥4-char non-stopword fragment, so a prefixed
        parse like ``"correction: wisdom"`` still matches a probe about
        ``"wisdom"``.  Both the claim and the release derive their
        tokens here, so the two can never disagree about what a subject
        covers.
        """
        owner = subject.lower().strip()
        if not owner:
            return "", ()
        tokens = [owner]
        for tok in _SUBJECT_SPLIT_RE.split(owner):
            if len(tok) >= 4 and tok not in _SUBJECT_STOPWORDS and tok != owner:
                tokens.append(tok)
        return owner, tuple(tokens)

    def _remember_speculative_subject(self, subject: str) -> None:
        """Record ``subject`` as claiming its index tokens (refreshing LRU).

        Finding 5 (audit 2026-05-20).  Caps the cache at
        ``_MAX_SPECULATIVE_SUBJECTS`` via insertion-order eviction.
        Empty / whitespace-only inputs are dropped silently so callers
        can pass raw fragments without guarding.

        H-13 — the subject is recorded as the *claimant* of each token it
        indexes under, so a later release can tell its own tokens from a
        neighbour's.
        """
        owner, tokens = self._speculative_index_tokens(subject)
        if not owner:
            return
        for token in tokens:
            claimants = self._speculative_subjects.get(token)
            if claimants is None:
                self._speculative_subjects[token] = {owner}
            else:
                claimants.add(owner)
            self._speculative_subjects.move_to_end(token)
        while len(self._speculative_subjects) > _MAX_SPECULATIVE_SUBJECTS:
            self._speculative_subjects.popitem(last=False)

    def _forget_speculative_subject(self, subject: str) -> None:
        """Release ``subject``'s claims; evict each token no one still claims.

        Called when teaching review returns a COHERENT proposal, so
        material that has now been reviewed stops being marked
        speculative on later probes.  No-op for subjects that hold no
        claim.

        H-13 — releases only what *this* subject claimed.  A COHERENT
        proposal never seeded anything (the call site's branches are
        mutually exclusive), so it holds no claim on a neighbour's
        token: discarding an absent claimant leaves that token live, and
        the still-unreviewed subject keeps its marker.  A token is
        evicted exactly when its last claimant is reviewed.
        """
        owner, tokens = self._speculative_index_tokens(subject)
        if not owner:
            return
        for token in tokens:
            claimants = self._speculative_subjects.get(token)
            if claimants is None:
                continue
            claimants.discard(owner)
            if not claimants:
                self._speculative_subjects.pop(token, None)

    def _should_mark_speculative(self, text: str, surface: str) -> bool:
        """Decide whether ``surface`` should carry the SPECULATIVE marker.

        Triggers when the input references a subject of a prior SPECULATIVE
        teaching proposal (by substring match) or carries a reflexive query
        shape (e.g. "is your answer about X confirmed?").  Already-marked
        surfaces are not double-marked.
        """
        surface_lower = surface.lower()
        if "speculative" in surface_lower or "not yet reviewed" in surface_lower:
            return False
        text_lower = text.lower()
        for subj in self._speculative_subjects:
            if subj and subj in text_lower:
                return True
        for marker in _REFLEXIVE_PROBE_MARKERS:
            if marker in text_lower:
                return True
        return False

    def _run_teaching(
        self,
        text: str,
        intent: object,
        turn_number: int,
        *,
        identity_score: object = None,
    ) -> tuple[
        CorrectionCandidate | None,
        ReviewedTeachingExample | None,
        PackMutationProposal | None,
    ]:
        """Run correction capture → review → store if this turn is a CORRECTION.

        ``identity_score`` is the trajectory's projection onto the runtime
        IdentityManifold (already computed by ChatRuntime for this turn); the
        review gate uses it as a geometric (paraphrase-invariant) defense
        layer alongside the syntactic check.
        """
        if self._prior_surface is None:
            return None, None, None

        candidate = extract_correction(
            correction_text=text,
            intent=intent,  # type: ignore[arg-type]
            prior_surface=self._prior_surface,
            prior_turn=turn_number - 1,
        )
        if candidate is None:
            return None, None, None

        manifold = getattr(self.runtime, "identity_manifold", None)
        # ADR-0244 honest scope: with ``identity_wave_gate`` off, live
        # final_state.F scores routinely show high leakage and axis inversion
        # because value axes are not yet dynamically load-bearing. Those
        # measures are observational telemetry, not teaching veto authority.
        # Only committed ``boundary_violations`` (safety/ethics ∩ manifold)
        # remain a hard geometric teaching reject while the gate is off.
        # Syntactic identity-override detection remains active regardless.
        review_score = identity_score
        cfg = getattr(self.runtime, "config", None)
        gate_on = bool(getattr(cfg, "identity_wave_gate", False))
        if (
            not gate_on
            and identity_score is not None
            and bool(getattr(identity_score, "wave_mode_active", False))
            and not bool(getattr(identity_score, "boundary_violations", ()) or ())
        ):
            review_score = None
        reviewed = review_correction(
            candidate,
            identity_score=review_score,  # type: ignore[arg-type]
            identity_manifold=manifold if review_score is not None else None,
        )
        proposal = self.teaching_store.add(reviewed)
        return candidate, reviewed, proposal

    def _maybe_transitive_walk(
        self,
        intent,
        triples: tuple[tuple[str, str, str], ...] | None = None,
    ) -> WalkResult | None:
        """Invoke a typed deterministic walk operator when the intent shape
        calls for it (ADR-0018).

        Dispatch order, by precision:
          1. Relation-typed `transitive_walk` if the intent carries a
             relation and a same-relation chain exists from the head.
          2. Cross-relation `multi_relation_walk` fallback when (1)
             returns a singleton — this is what closes the
             mixed_relation / composed_predicate residuals.

        DEFINITION intents only attempt step 1 with the implicit "is"
        relation; they do not fall back to a multi-relation walk
        (which would be too permissive for plain "What is X?").

        ``triples`` may be passed in to avoid a second
        ``teaching_store.triples()`` materialization per turn (comb
        pass 2026-05-21); when omitted, falls back to the live store.
        """
        if triples is None:
            triples = self.teaching_store.triples()
        if not triples:
            return None
        if intent.tag is IntentTag.TRANSITIVE_QUERY and intent.relation:
            result = transitive_walk(triples, intent.subject, intent.relation)
            if len(result.path) > 1:
                return result
            multi = multi_relation_walk(triples, intent.subject)
            if len(multi.path) > 1:
                return multi
            return None
        if intent.tag is IntentTag.DEFINITION:
            result = transitive_walk(triples, intent.subject, "is")
            if len(result.path) > 1:
                return result
        return None

    def _maybe_compose_relations(
        self,
        intent,
        triples: tuple[tuple[str, str, str], ...] | None = None,
    ) -> FrameComposeResult | None:
        """Invoke ``compose_relations`` when the intent is a frame-transfer
        probe ("What does X R in Y?") and the teaching store carries at
        least one R-edge.  Returns the typed result; the caller folds
        non-None tails into the surface.

        ``triples`` may be passed in to avoid a second
        ``teaching_store.triples()`` materialization per turn (comb
        pass 2026-05-21).
        """
        if intent.tag is not IntentTag.FRAME_TRANSFER:
            return None
        if not intent.relation or not intent.frame:
            return None
        if triples is None:
            triples = self.teaching_store.triples()
        if not triples:
            return None
        return compose_relations(
            triples,
            head=intent.subject,
            frame=intent.frame,
            relation=intent.relation,
        )

    def _maybe_entailment_trace(
        self,
        intent,
        triples: tuple[tuple[str, str, str], ...],
    ) -> EntailmentTrace | None:
        """Compile exact verification triples into propositional entailment.

        Telemetry-only v1: the result is folded into ``operator_invocation`` and
        never changes the user-facing surface. Runs only when classification
        exposes a precise positive ``subject relation object`` shape.

        Atoms are content-addressed by Cl(4,1) versor digests and unified by
        conformal reverse-product score (no string ``atom_`` join).
        """
        if intent.tag is not IntentTag.VERIFICATION:
            return None
        if intent.negated or not intent.relation or not intent.object:
            return None
        registry: list[tuple[str, np.ndarray]] = []
        head = self._proof_atom(intent.subject, registry)
        tail = self._proof_atom(intent.object, registry)
        if not head or not tail:
            return None

        relation = intent.relation.strip().lower()
        premises: list[str] = []
        for h, r, t in triples:
            if r.strip().lower() != relation:
                continue
            h_atom = self._proof_atom(h, registry)
            t_atom = self._proof_atom(t, registry)
            if h_atom and t_atom:
                premises.append(f"{h_atom} -> {t_atom}")
        if not premises:
            return None
        return evaluate_entailment_with_trace(tuple(premises), f"{head} -> {tail}")

    @staticmethod
    def _render_compose_surface(compose: FrameComposeResult) -> str:
        """Render a frame-transfer composition suffix without selecting authority."""
        parts: list[str] = []
        if compose.subject_tail is not None:
            parts.append(
                f"{compose.head} {compose.relation.replace('_', ' ')} {compose.subject_tail}"
            )
        if compose.frame_tail is not None:
            parts.append(
                f"in {compose.frame} {compose.relation.replace('_', ' ')} {compose.frame_tail}"
            )
        return "; ".join(parts)

    # Comb pass 2026-05-21 — removed dead ``_fold_compose_into_surface``
    # (no live callers since PR #76 routed all surface composition
    # through the explicit ``resolve_surface`` policy).  The render
    # helper above is still consumed by the resolver path.

    @staticmethod
    def _serialize_operator(op: WalkResult | FrameComposeResult | None) -> str:
        """Deterministic operator-invocation serialisation for trace_hash.

        Comb pass 2026-05-21 — collapsed the parallel ``_serialize_walk`` /
        ``_serialize_compose`` helpers into one.  Both operators expose
        ``as_dict()`` and serialise identically.
        """
        if op is None:
            return ""
        return json.dumps(op.as_dict(), sort_keys=True, ensure_ascii=False)

    @staticmethod
    def _serialize_entailment_trace(trace: EntailmentTrace | None) -> str:
        if trace is None:
            return ""
        return f"entailment:{evidence_from_entailment_trace(trace).canonical_json()}"

    def _resolve_surface_versor(self, text: str) -> np.ndarray | None:
        """Resolve surface text to a vocab-grounded Cl(4,1) versor, or None."""
        session = getattr(self.runtime, "session", None)
        vocab = getattr(session, "vocab", None) if session is not None else None
        if vocab is None or not text:
            return None
        tokens = [p for p in _SUBJECT_SPLIT_RE.split(text.lower()) if p]
        # Prefer last non-stopword content token (subject-like), then any token.
        ordered = [t for t in reversed(tokens) if t not in _SUBJECT_STOPWORDS] + tokens
        for token in ordered:
            try:
                return np.asarray(vocab.get_versor(token), dtype=np.float64)
            except (KeyError, AttributeError):
                continue
        return None

    @staticmethod
    def _unify_score(a: np.ndarray, b: np.ndarray) -> float:
        """⟨a, ~b⟩_0 — scalar part of geometric product with reversion."""
        return float(scalar_part(geometric_product(a, reverse(b))))

    @classmethod
    def _atoms_unify(cls, a: np.ndarray, b: np.ndarray) -> bool:
        """True when a and b are the same geometric atom under reverse-product.

        Requires mutual score to match both self-products within ``_UNIFY_EPS``
        (relative when |self| ≥ 1, absolute otherwise). Exact component match
        short-circuits. Distinct pack versors with large cross-inner do not unify.
        """
        if a.shape != b.shape:
            return False
        if np.allclose(a, b, rtol=0.0, atol=1e-9):
            return True
        sa = cls._unify_score(a, a)
        sb = cls._unify_score(b, b)
        sab = cls._unify_score(a, b)
        scale = max(1.0, abs(sa), abs(sb))
        tol = _UNIFY_EPS * scale
        return abs(sab - sa) <= tol and abs(sab - sb) <= tol

    def _proof_atom(
        self,
        text: str,
        registry: list[tuple[str, np.ndarray]] | None = None,
    ) -> str:
        """Content-addressed conformal atom id for entailment telemetry.

        Two surfaces unify to the same atom iff their grounded versors match
        under :meth:`_atoms_unify`. Ungrounded surfaces fail closed (empty id).
        """
        psi = self._resolve_surface_versor(text)
        if psi is None:
            return ""
        if registry is not None:
            for atom_id, prior in registry:
                if self._atoms_unify(psi, prior):
                    return atom_id
        digest = multivector_content_digest(psi)
        atom_id = f"atom_{digest}"
        if registry is not None:
            registry.append((atom_id, psi.copy()))
        return atom_id

    @staticmethod
    def _render_walk_surface(walk: WalkResult) -> str:
        """Render a chain-aware walk suffix without selecting authority."""
        chain = " ".join(walk.path)
        endpoint = walk.path[-1]
        return (
            f"{walk.head} {walk.relation.replace('_', ' ')} {endpoint} "
            f"(via {chain})"
        )

    @staticmethod
    def _fold_walk_into_surface(
        walk: WalkResult,
        surface: str,
        articulation_surface: str,
    ) -> tuple[str, str]:
        """Compose a chain-aware surface from a non-trivial walk result.

        Deterministic.  Replay-safe: identical (walk, prior surfaces) produce
        identical output.  The chain endpoint is the load-bearing token for
        the inference-closure / multi-step-reasoning eval lanes.
        """
        chain_surface = CognitiveTurnPipeline._render_walk_surface(walk)
        if surface:
            new_surface = f"{surface} — {chain_surface}"
        else:
            new_surface = chain_surface
        if articulation_surface:
            new_articulation = f"{articulation_surface} — {chain_surface}"
        else:
            new_articulation = chain_surface
        return new_surface, new_articulation

    def _capture_field_state(self) -> FieldState | None:
        """Return current session field state, or None if not yet initialised."""
        try:
            state = self.runtime.session.state
            # SessionContext.state may be None before the first ingest
            return state if state is not None else None
        except AttributeError:
            return None
