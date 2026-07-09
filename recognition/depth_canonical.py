"""Pure depth canonicalization helpers for 3-lang root-aware unification.

Extracted per strategy to enable slot-precise, node_id-keyed canonicalization
without heuristics in callers. All functions pure, side-effect free, immutable.

Used by derive_recognizer, recognize (for matching), and assessment enrichment.

Connects to cognitive path: listen/comprehend (depth from packs) -> think (anti-unif canonical) -> articulate.
Preserves exact recall, no drift repair.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any, Sequence, Tuple

from recognition.outcome import EvidenceSpan, FeatureBundle

# For type in tests, import GraphNode when needed
try:
    from generate.graph_planner import GraphNode
except ImportError:
    GraphNode = Any  # type: ignore


def canonicalize_token(token: str, node_id: str | None, depths: dict[str, dict] | None) -> str:
    """Wrap root_normalize keyed on node_id from depths dict.

    depths: {node_id: {"language": , "root": , ...}, ...}
    If node_id in depths and lang he/grc and root, return root, else token.
    Caller must pass the token associated with that node_id.
    """
    if not depths or not node_id:
        return token
    d = depths.get(node_id)
    if not d:
        return token
    lang = d.get("language")
    root = d.get("root")
    if lang in ("he", "grc") and root:
        return root
    return token


def canonicalize_agent_slot(
    tokens: Sequence[str], bundle: FeatureBundle | None, depths: dict[str, dict] | None,
    *, agent_node_id: str | None = None, start_idx: int | None = None
) -> Tuple[str, ...]:
    """Return copy of tokens with agent slot canonicalized using EvidenceSpan.start + node_id if available.

    Single lookup by agent_node_id (node-keyed, requires explicit nid or no-op; no first-key proxy).
    If bundle use its start, else start_idx.
    Pure.
    """
    if not depths:
        return tuple(tokens)
    start = start_idx
    if bundle and start is None:
        agent_feat = bundle.get("agent")
        if agent_feat and isinstance(agent_feat.evidence, EvidenceSpan):
            start = agent_feat.evidence.start
    if start is None or start < 0 or start >= len(tokens):
        return tuple(tokens)
    new_tokens = list(tokens)
    nid = agent_node_id
    if nid is None or nid not in depths:
        return tuple(new_tokens)  # require explicit nid, no first-key proxy
    d = depths[nid]
    if d.get("language") in ("he", "grc") and d.get("root"):
        orig = new_tokens[start]
        new_tokens[start] = canonicalize_token(orig, nid, depths)
    return tuple(new_tokens)


def build_node_depths(nodes: Sequence[Any]) -> dict[str, dict]:
    """Lift the node_depths dict from list of GraphNode (or objects with .node_id, .language etc).

    Pure extraction of the comprehension in pipeline.
    """
    return {
        n.node_id: {
            k: v for k, v in {
                "language": getattr(n, "language", None),
                "root": getattr(n, "root", None),
                "morphology_id": getattr(n, "morphology_id", None),
            }.items() if v is not None
        }
        for n in nodes
        if getattr(n, "language", None) or getattr(n, "root", None)
    }


def enrich_assessments_with_depth(assessments: Tuple[Any, ...], depth: dict | None) -> Tuple[Any, ...]:
    """Immutable enrichment of assessments with root note using dataclasses.replace if possible.

    Returns new tuple, no mutation of input.
    """
    if not depth:
        return assessments
    roots = [d.get("root") for d in depth.values() if d.get("root")]
    if not roots:
        return assessments
    note = f" [root:{roots[0]}]"
    new_ass = []
    for a in assessments:
        if hasattr(a, "explanation") and getattr(a, "runnable", False):
            try:
                new_a = replace(a, explanation=(getattr(a, "explanation", "") or "") + note)
            except Exception:
                # create copy for annotation (avoid mutate original/frozen)
                try:
                    if hasattr(a, '__dict__'):
                        new_a = type(a)(**a.__dict__)
                        if hasattr(new_a, 'explanation'):
                            new_a.explanation = (getattr(new_a, 'explanation', '') or '') + note
                    else:
                        new_a = a
                except Exception:
                    new_a = a
            new_ass.append(new_a)
        else:
            new_ass.append(a)
    return tuple(new_ass)
