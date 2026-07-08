"""Graph planner — converts a PropositionGraph into an ArticulationTarget.

The planner walks the graph in topological order and emits an ordered
sequence of articulation steps that the downstream generation pipeline
can execute. Each step carries the proposition node ID, the rhetorical
move, and any constraints inherited from intent classification.
"""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from enum import Enum, unique

from generate.intent import DialogueIntent, IntentTag


@unique
class Relation(Enum):
    ELABORATION = "elaboration"
    CAUSE = "cause"
    CONTRAST = "contrast"
    SEQUENCE = "sequence"
    CORRECTION = "correction"
    CONJUNCTION = "conjunction"
    DISJUNCTION = "disjunction"
    COMPLEMENT = "complement"
    RELATIVE = "relative"


@unique
class RhetoricalMove(Enum):
    ASSERT = "assert"
    ELABORATE = "elaborate"
    CONTRAST = "contrast"
    SEQUENCE = "sequence"
    CORRECT = "correct"


@dataclass(frozen=True, slots=True)
class GraphEdge:
    source: str
    target: str
    relation: Relation

    def as_dict(self) -> dict[str, str]:
        return {
            "source": self.source,
            "target": self.target,
            "relation": self.relation.value,
        }


@dataclass(frozen=True, slots=True)
class GraphNode:
    """Core node in the PropositionGraph.

    The shared substrate for comprehension (grounding), articulation
    (realization), and internal reasoning/contemplation.

    Optional 3-language depth fields allow Hebrew root density and
    Koine Greek precision (plus English base) to travel with the node
    through the entire spine without duplication.
    """
    node_id: str
    subject: str
    predicate: str
    obj: str
    source_intent: IntentTag
    language: str | None = None
    root: str | None = None
    morphology_id: str | None = None
    # 3-lang depth support for PropGraph spine (comprehend/articulate/think via roots)

    def as_dict(self) -> dict[str, object]:
        d = {
            "node_id": self.node_id,
            "subject": self.subject,
            "predicate": self.predicate,
            "object": self.obj,
            "source_intent": self.source_intent.value,
        }
        if self.language is not None:
            d["language"] = self.language
        if self.root is not None:
            d["root"] = self.root
        if self.morphology_id is not None:
            d["morphology_id"] = self.morphology_id
        return d


@dataclass(frozen=True, slots=True)
class PropositionGraph:
    nodes: tuple[GraphNode, ...] = ()
    edges: tuple[GraphEdge, ...] = ()

    def add_node(self, node: GraphNode) -> PropositionGraph:
        return PropositionGraph(nodes=(*self.nodes, node), edges=self.edges)

    def add_edge(self, edge: GraphEdge) -> PropositionGraph:
        return PropositionGraph(nodes=self.nodes, edges=(*self.edges, edge))

    def roots(self) -> tuple[str, ...]:
        targets = frozenset(e.target for e in self.edges)
        return tuple(n.node_id for n in self.nodes if n.node_id not in targets)

    def get_node_depths(self) -> dict[str, dict]:
        """Return nid -> {language, root, morphology_id} for nodes carrying 3-lang depth.

        Delegates to the canonical pure extractor in recognition.depth_canonical
        (single source of truth; avoids duplication with build_node_depths).
        Enables graph-level consumers (anti-unif, framing, realizer)
        to operate on root forms for he/grc without string hacks.
        """
        from recognition.depth_canonical import build_node_depths
        return build_node_depths(self.nodes)

    def topo_order(self) -> tuple[str, ...]:
        """Kahn's topological sort over the graph's edges.

        Comb pass 2026-05-21 — pre-fix this implementation had two
        compounding inefficiencies:

          * ``queue.pop(0)`` on a list is O(N) per pop ⇒ O(N²) total
          * The inner ``for e in self.edges`` rescanned every edge on
            every iteration ⇒ O(N × E) overall

        Properly implemented Kahn's is O(N + E) and produces the same
        deterministic order for the same input (queue seeded with
        sorted zero-in-degree nodes; ties on later iterations break
        by insertion order, identical to the pre-fix list).

        Today's graphs are 1–2 nodes so cost is invisible — but
        ADR-0089 Phase C2 (compound-intent multi-node dispatch) and
        ADR-0088 Phase B (grounded realizer) both make multi-node
        graphs realistic on the hot path.  Fix lands before the
        usage scales.
        """
        # Build out-edge adjacency once: O(E).
        out_edges: dict[str, list[str]] = defaultdict(list)
        in_degree: dict[str, int] = {n.node_id: 0 for n in self.nodes}
        for e in self.edges:
            out_edges[e.source].append(e.target)
            in_degree[e.target] = in_degree.get(e.target, 0) + 1
        # Seed with sorted zero-in-degree nodes (deterministic).
        queue: deque[str] = deque(
            sorted(nid for nid, deg in in_degree.items() if deg == 0)
        )
        order: list[str] = []
        while queue:
            nid = queue.popleft()  # O(1) on a deque
            order.append(nid)
            # Decrement in-degree of direct successors only: O(deg(nid))
            # amortised to O(E) total across the loop.
            for target in out_edges[nid]:
                in_degree[target] -= 1
                if in_degree[target] == 0:
                    queue.append(target)
        return tuple(order)

    def as_dict(self) -> dict[str, object]:
        return {
            "nodes": tuple(n.as_dict() for n in self.nodes),
            "edges": tuple(e.as_dict() for e in self.edges),
        }

    def to_json(self) -> str:
        import json
        return json.dumps(self.as_dict(), sort_keys=True)

    def is_fully_grounded(self) -> bool:
        """True iff every node has a concrete object referent (no <pending>).

        This predicate is the geometric/substrate half of the Shadow Coherence
        Gate. It is deliberately structural and cheap.

        - Mechanical Sympathy: pure tuple walk; zero allocation in hot path;
          maps to the same CPU domain as the rest of cognition orchestration.
        - Semantic Rigor: "fully grounded" has one precise meaning — the
          recall step (or direct construction) supplied a non-sentinel object
          for every proposition node. The sentinel "<pending>" is the lexical
          marker that exact CGA recall did not bind a referent.
        - Third Door: we refuse to paper over missing referents with
          similarity, defaults, or post-hoc repair. If any slot remains
          pending the substrate withholds authority and emits a precise
          bypass hazard for the data-driven backlog.

        The continuous versor_condition < 1e-6 remains enforced exclusively
        at owned construction boundaries (algebra/versor._close_applied_versor,
        VersorBinding.__post_init__, ingest gate, etc.). This method never
        mutates or "fixes" geometry.
        """
        if not self.nodes:
            return False
        for n in self.nodes:
            obj = getattr(n, "obj", None)
            if obj in (None, "", "<pending>"):
                return False
            if isinstance(obj, str) and "..." in obj:
                return False
        return True

    def get_unresolved_topology(self) -> tuple[str, ...]:
        """Node IDs that remain ungrounded.

        Used exclusively for SUBSTRATE_BYPASS_HAZARD telemetry so that
        the exact missing structure (not a score) drives Layer 1/2/3 work.
        """
        unresolved: list[str] = []
        for n in self.nodes:
            obj = getattr(n, "obj", None)
            if obj in (None, "", "<pending>") or (isinstance(obj, str) and "..." in obj):
                unresolved.append(n.node_id)
        return tuple(unresolved)


@dataclass(frozen=True, slots=True)
class ArticulationStep:
    node_id: str
    move: RhetoricalMove
    predicate: str
    subject: str
    negated: bool = False
    quantifier: str | None = None
    tense: str | None = None
    aspect: str | None = None

    def as_dict(self) -> dict[str, str]:
        return {
            "node_id": self.node_id,
            "move": self.move.value,
            "predicate": self.predicate,
            "subject": self.subject,
        }


@dataclass(frozen=True, slots=True)
class ArticulationTarget:
    steps: tuple[ArticulationStep, ...]
    source_intent: IntentTag

    def as_dict(self) -> dict[str, object]:
        return {
            "steps": tuple(s.as_dict() for s in self.steps),
            "source_intent": self.source_intent.value,
        }


_RELATION_TO_MOVE: dict[Relation, RhetoricalMove] = {
    Relation.ELABORATION: RhetoricalMove.ELABORATE,
    Relation.CAUSE: RhetoricalMove.ELABORATE,
    Relation.CONTRAST: RhetoricalMove.CONTRAST,
    Relation.SEQUENCE: RhetoricalMove.SEQUENCE,
    Relation.CORRECTION: RhetoricalMove.CORRECT,
}


_INTENT_PREDICATES: dict[IntentTag, str] = {
    IntentTag.DEFINITION: "is_defined_as",
    IntentTag.CAUSE: "is_caused_by",
    IntentTag.PROCEDURE: "has_steps",
    IntentTag.COMPARISON: "contrasts_with",
    IntentTag.CORRECTION: "corrects",
    IntentTag.RECALL: "recalls",
    IntentTag.VERIFICATION: "is_verified_as",
}


def graph_from_intent(
    intent: DialogueIntent,
    *,
    prior_node_id: str | None = None,
) -> PropositionGraph:
    """Build a minimal proposition graph from a classified intent.

    Uses structural pattern matching for exhaustive, readable dispatch
    over IntentTag – modern, clear, and easier to extend without
    hidden fallthroughs.
    """
    graph = PropositionGraph()

    match intent.tag:
        case IntentTag.COMPARISON:
            predicate = _INTENT_PREDICATES[IntentTag.COMPARISON]
            left = GraphNode(
                node_id="p0",
                subject=intent.subject,
                predicate=predicate,
                obj=intent.secondary_subject or "<pending>",
                source_intent=intent.tag,
                # depth fields populated later via resolve_entry + grounding enrichment
            )
            right = GraphNode(
                node_id="p1",
                subject=intent.secondary_subject or "<pending>",
                predicate=predicate,
                obj=intent.subject,
                source_intent=intent.tag,
            )
            edge = GraphEdge(source="p0", target="p1", relation=Relation.CONTRAST)
            return graph.add_node(left).add_node(right).add_edge(edge)

        case IntentTag.CORRECTION:
            predicate = _INTENT_PREDICATES[IntentTag.CORRECTION]
            root = GraphNode(
                node_id="p0",
                subject=intent.subject,
                predicate=predicate,
                obj=prior_node_id or "<prior>",
                source_intent=intent.tag,
            )
            graph = graph.add_node(root)
            if prior_node_id is not None:
                graph = graph.add_edge(
                    GraphEdge(source="p0", target=prior_node_id, relation=Relation.CORRECTION)
                )
            return graph

        case _:
            predicate = _INTENT_PREDICATES.get(intent.tag, "addresses")
            root = GraphNode(
                node_id="p0",
                subject=intent.subject,
                predicate=predicate,
                obj="<pending>",
                source_intent=intent.tag,
            )
            return graph.add_node(root)


def ground_graph(
    graph: PropositionGraph,
    recalled_words: tuple[str, ...],
    *,
    depth: dict[str, tuple[str | None, str | None, str | None]] | None = None,
) -> PropositionGraph:
    """Fill <pending> obj slots with recalled words from vault recall.

    Each node whose obj is '<pending>' gets the next available recalled
    word. If there are more nodes than words, remaining slots stay as
    '<pending>'. Comparison nodes get paired words when available.

    depth: optional node_id -> (language, root, morphology_id) to attach
    alongside recalled_words. Supports passing 3-lang depth without
    requiring pre-enrichment of the input graph. Falls back to any
    depth already on the input node.
    """
    words = deque(recalled_words)
    new_nodes: list[GraphNode] = []
    for node in graph.nodes:
        if node.obj == "<pending>" and words:
            obj = words.popleft()
            lang, rt, mid = node.language, node.root, node.morphology_id
            if depth and node.node_id in depth:
                dlang, drt, dmid = depth.get(node.node_id, (None, None, None))
                lang = dlang or lang
                rt = drt or rt
                mid = dmid or mid
            new_nodes.append(GraphNode(
                node_id=node.node_id,
                subject=node.subject,
                predicate=node.predicate,
                obj=obj,
                source_intent=node.source_intent,
                language=lang,
                root=rt,
                morphology_id=mid,
            ))
        else:
            new_nodes.append(node)
    return PropositionGraph(nodes=tuple(new_nodes), edges=graph.edges)


def plan_articulation(graph: PropositionGraph) -> ArticulationTarget:
    """Walk *graph* in topological order and emit an articulation target."""
    node_map = {n.node_id: n for n in graph.nodes}
    incoming: dict[str, Relation | None] = {n.node_id: None for n in graph.nodes}
    for edge in graph.edges:
        if edge.target in incoming:
            incoming[edge.target] = edge.relation

    source_intent = IntentTag.UNKNOWN
    if graph.nodes:
        source_intent = graph.nodes[0].source_intent

    steps: list[ArticulationStep] = []
    for node_id in graph.topo_order():
        node = node_map.get(node_id)
        if node is None:
            continue
        relation = incoming.get(node_id)
        match relation:
            case None:
                move = RhetoricalMove.ASSERT
            case _:
                move = _RELATION_TO_MOVE.get(relation, RhetoricalMove.ASSERT)
        steps.append(
            ArticulationStep(
                node_id=node_id,
                move=move,
                predicate=node.predicate,
                subject=node.subject,
            )
        )

    return ArticulationTarget(steps=tuple(steps), source_intent=source_intent)
