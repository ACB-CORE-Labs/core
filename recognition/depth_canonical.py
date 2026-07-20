"""Pure depth canonicalization helpers for 3-lang root-aware unification.

Extracted per strategy to enable slot-precise, node_id-keyed canonicalization
without heuristics in callers. All functions pure, side-effect free, immutable.

Used by derive_recognizer, recognize (for matching), and assessment enrichment.

Connects to cognitive path: listen/comprehend (depth from packs) -> think (anti-unif canonical) -> articulate.
Preserves exact recall, no drift repair.

Stage 3 (Master Blueprint / ADR-0256 reserve): multi-root Hebrew/Greek
depth must fail closed — never silently commit ``roots[0]``.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Sequence, Tuple

from recognition.outcome import EvidenceSpan, FeatureBundle

# For type in tests, import GraphNode when needed
try:
    from generate.graph_planner import GraphNode
except ImportError:
    GraphNode = Any  # type: ignore


@dataclass(frozen=True, slots=True)
class RootSenseAmbiguity:
    """Typed multi-root / multi-sense ambiguity (fail-closed).

    Carries every observed candidate root with node provenance. Downstream
    must not emit a single canonical constraint unless an authored
    ``disambiguation_rule_id`` resolves the set.
    """

    candidates: tuple[str, ...]
    node_ids: tuple[str, ...]
    languages: tuple[str, ...]
    disambiguation_rule_id: str | None = None

    @property
    def resolved(self) -> bool:
        return self.disambiguation_rule_id is not None and len(self.candidates) == 1

    def as_dict(self) -> dict[str, Any]:
        return {
            "kind": "root_sense_ambiguity",
            "candidates": list(self.candidates),
            "node_ids": list(self.node_ids),
            "languages": list(self.languages),
            "disambiguation_rule_id": self.disambiguation_rule_id,
            "resolved": self.resolved,
        }


def observed_roots(depth: dict[str, dict] | None) -> tuple[str, ...]:
    """Stable unique roots observed across depth entries (order of first appearance)."""
    if not depth:
        return ()
    seen: list[str] = []
    for nid, d in depth.items():
        del nid  # provenance via observe_root_ambiguity
        roots_field = d.get("roots")
        if isinstance(roots_field, (list, tuple)):
            for r in roots_field:
                if r and r not in seen:
                    seen.append(str(r))
        r = d.get("root")
        if r and r not in seen:
            seen.append(str(r))
    return tuple(seen)


def observe_root_ambiguity(
    depth: dict[str, dict] | None,
    *,
    disambiguation_rule_id: str | None = None,
) -> RootSenseAmbiguity | None:
    """Return typed ambiguity when ≥2 distinct roots are observed without resolution.

    A single authored ``disambiguation_rule_id`` alone does **not** collapse
    candidates — that would be the forbidden "one authored mapping" shortcut.
    Resolution requires the rule id *and* a single remaining candidate
    (caller must filter candidates before calling).
    """
    if not depth:
        return None
    cands = observed_roots(depth)
    if len(cands) <= 1:
        return None
    node_ids: list[str] = []
    langs: list[str] = []
    for nid, d in depth.items():
        rset = set()
        if d.get("root"):
            rset.add(str(d["root"]))
        if isinstance(d.get("roots"), (list, tuple)):
            rset.update(str(x) for x in d["roots"] if x)
        if rset:
            node_ids.append(nid)
            langs.append(str(d.get("language") or ""))
    amb = RootSenseAmbiguity(
        candidates=cands,
        node_ids=tuple(node_ids),
        languages=tuple(langs),
        disambiguation_rule_id=disambiguation_rule_id,
    )
    if amb.resolved:
        return None
    return amb


def canonicalize_token(token: str, node_id: str | None, depths: dict[str, dict] | None) -> str:
    """Root-normalize keyed on node_id from depths dict.

    depths: {node_id: {"language": , "root": , "roots": optional multi, ...}, ...}
    If the node carries multiple roots (``roots`` len>1), fail closed: return
    the surface token unchanged (no silent first-root commit).
    If global depth is multi-root ambiguous, also refuse cross-node first-match.
    """
    if not depths or not node_id:
        return token
    d = depths.get(node_id)
    if not d:
        return token
    lang = d.get("language")
    if lang not in ("he", "grc"):
        return token
    multi = d.get("roots")
    if isinstance(multi, (list, tuple)) and len({str(x) for x in multi if x}) > 1:
        return token  # fail closed: multi-root on this node
    root = d.get("root")
    if root:
        return str(root)
    if isinstance(multi, (list, tuple)) and len(multi) == 1 and multi[0]:
        return str(multi[0])
    return token


def canonicalize_agent_slot(
    tokens: Sequence[str], bundle: FeatureBundle | None, depths: dict[str, dict] | None,
    *, agent_node_id: str | None = None, start_idx: int | None = None
) -> Tuple[str, ...]:
    """Return copy of tokens with agent slot canonicalized using EvidenceSpan.start + node_id if available.

    Single lookup by agent_node_id (node-keyed, requires explicit nid or no-op; no first-key proxy).
    Pure. Multi-root nodes fail closed (surface token retained).
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
    if d.get("language") in ("he", "grc") and (d.get("root") or d.get("roots")):
        orig = new_tokens[start]
        new_tokens[start] = canonicalize_token(orig, nid, depths)
    return tuple(new_tokens)


def build_node_depths(nodes: Sequence[Any]) -> dict[str, dict]:
    """Lift the node_depths dict from list of GraphNode (or objects with .node_id, .language etc).

    Pure extraction of the comprehension in pipeline. Includes optional
    multi-root ``roots`` when present on the node.
    """
    out: dict[str, dict] = {}
    for n in nodes:
        if getattr(n, "language", None) not in ("he", "grc") and not getattr(n, "root", None) and not getattr(n, "roots", None):
            continue
        payload: dict[str, Any] = {}
        lang = getattr(n, "language", None)
        root = getattr(n, "root", None)
        roots = getattr(n, "roots", None)
        mid = getattr(n, "morphology_id", None)
        if lang is not None:
            payload["language"] = lang
        if root is not None:
            payload["root"] = root
        if roots is not None:
            payload["roots"] = tuple(roots) if not isinstance(roots, tuple) else roots
        if mid is not None:
            payload["morphology_id"] = mid
        if payload:
            out[n.node_id] = payload
    return out


def enrich_assessments_with_depth(assessments: Tuple[Any, ...], depth: dict | None) -> Tuple[Any, ...]:
    """Immutable enrichment of assessments with root note using dataclasses.replace.

    * **0 roots** — assessments unchanged.
    * **1 unique root** — append `` [root:…]`` to runnable explanations.
    * **≥2 unique roots** — **fail closed**: do not pick ``roots[0]``; mark
      runnable assessments non-runnable with ``AMBIGUOUS_ROOTS`` provenance
      listing every candidate (Master Blueprint Stage 3 HE policy).

    Returns a new tuple. Enrichment is best-effort for non-dataclass items.
    """
    if not depth:
        return assessments
    amb = observe_root_ambiguity(depth)
    roots = observed_roots(depth)
    if not roots:
        return assessments
    if amb is not None:
        note = (
            f" [AMBIGUOUS_ROOTS candidates={list(amb.candidates)} "
            f"nodes={list(amb.node_ids)} — fail-closed; no silent first-root commit]"
        )
        new_ass = []
        for a in assessments:
            if hasattr(a, "explanation"):
                try:
                    kwargs: dict[str, Any] = {
                        "explanation": (getattr(a, "explanation", "") or "") + note,
                    }
                    if hasattr(a, "runnable"):
                        kwargs["runnable"] = False
                    if hasattr(a, "unresolved_hazards"):
                        hazards = tuple(getattr(a, "unresolved_hazards", ()) or ())
                        if "ambiguous_hebrew_roots" not in hazards:
                            kwargs["unresolved_hazards"] = hazards + ("ambiguous_hebrew_roots",)
                    new_a = replace(a, **kwargs)
                except Exception:
                    new_a = a
                new_ass.append(new_a)
            else:
                new_ass.append(a)
        return tuple(new_ass)

    # Single unambiguous root
    note = f" [root:{roots[0]}]"
    new_ass = []
    for a in assessments:
        if hasattr(a, "explanation") and getattr(a, "runnable", False):
            try:
                new_a = replace(a, explanation=(getattr(a, "explanation", "") or "") + note)
            except Exception:
                new_a = a
            new_ass.append(new_a)
        else:
            new_ass.append(a)
    return tuple(new_ass)
