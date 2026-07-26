"""Independent curriculum oracle — the gold for the curriculum-serve lane.

This is **deliberately a second, independent decision procedure** (plan §4.4).
It shares no code with the serving path: its own JSONL loader, its own
ratification predicate, its own connective→family table, its own agreement
normalization, and its own verdict rule. Two independently-written procedures
agreeing on every case is real evidence the serving path reads the curriculum
correctly; a shared-code "oracle" would only prove the compiler agrees with
itself.

It is intentionally simple: a closed-world reachability oracle over the chain
graph. "Closed-world" describes only what the ORACLE can see — the ratified
corpus and nothing else. It does NOT mean untaught facts are false: an edge
absent from the corpus is UNKNOWN, never refuted, because a curriculum that
does not mention something has said nothing about it. The oracle also reports
the shortest path length between the two terms, which is what lets the lane
assert the property that matters most here — that a reachable-but-untaught
pair is answered UNKNOWN rather than composed into a claim.
"""

from __future__ import annotations

import json
from collections import deque
from dataclasses import dataclass
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_CHAIN_DIR = _REPO_ROOT / "teaching" / "domain_chains"
_PACK_DIR = _REPO_ROOT / "packs" / "data"

#: Independently restated (the serving path has its own copy — that is the point).
_FAMILY_OF_CONNECTIVE = {
    "causes": "causal",
    "reveals": "causal",
    "grounds": "causal",
    "requires": "modal",
    "enables": "modal",
    "precedes": "sequence",
    "opposes": "contrast",
    "supports": "evidential",
}

#: Which corpora and packs each subject is taught from — restated, not imported.
_DOMAIN_SOURCES: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {
    "physics": (("physics_chains_v1",), ("en_physics_v1",)),
    "mathematics_logic": (("mathematics_logic_chains_v1",), ("en_mathematics_logic_v1",)),
    "systems_software": (("systems_software_chains_v1",), ("en_systems_software_v1",)),
    "philosophy_theology": (
        ("philosophy_theology_chains_v1",),
        ("en_core_cognition_v1", "en_core_meta_v1"),
    ),
}


@dataclass(frozen=True, slots=True)
class OracleVerdict:
    """The gold verdict, plus the evidence the lane asserts against."""

    verdict: str          # entailed | unknown | declined
    reason: str           # typed reason when declined, else ""
    family: str           # "" when the relation is not taught anywhere
    depth: int            # 1 = taught edge, >1 = reachable in n hops, 0 = no path


def _lemmas(pack_id: str) -> set[str]:
    path = _PACK_DIR / pack_id / "lexicon.jsonl"
    out: set[str] = set()
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        lemma = row.get("lemma")
        if isinstance(lemma, str):
            out.add(lemma)
    return out


#: ADR-0264 R1/R8, restated independently — the serving path has its own copy of
#: this vocabulary and the two must not share a polarity helper. Code-level
#: independence is the whole evidentiary value of this oracle: if it imported the
#: compiler's notion of polarity, agreement would only prove the compiler agrees
#: with itself, and a polarity bug would be invisible on both sides at once.
_AFFIRMATIVE = "affirmative"
_NEGATIVE = "negative"
_POLARITIES = (_AFFIRMATIVE, _NEGATIVE)


def _row_polarity(row: dict) -> str | None:
    """This oracle's own reading of a row's polarity.

    Absent ⇒ affirmative. An unrecognized token ⇒ ``None``, and the caller drops
    the row: reading an unknown value as affirmative would let a row someone
    wrote to refute be scored as an assertion.
    """
    value = str(row.get("polarity") or _AFFIRMATIVE).strip().lower()
    return value if value in _POLARITIES else None


def _edges(domain: str) -> list[tuple[str, str, str, str, str]]:
    """``(subject, connective, object, chain_id, polarity)`` per ratified row."""
    corpora, packs = _DOMAIN_SOURCES[domain]
    vocabulary = set()
    for pack in packs:
        vocabulary |= _lemmas(pack)
    out: list[tuple[str, str, str, str, str]] = []
    for corpus in corpora:
        path = _CHAIN_DIR / f"{corpus}.jsonl"
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if row.get("review_status") != "reviewed":
                continue
            if row.get("domain") != domain:
                continue
            subject, obj = row.get("subject"), row.get("object")
            connective = row.get("connective")
            if subject not in vocabulary or obj not in vocabulary:
                continue
            if connective not in _FAMILY_OF_CONNECTIVE:
                continue
            polarity = _row_polarity(row)
            if polarity is None:
                continue
            out.append(
                (subject, connective, obj, row.get("chain_id", ""), polarity)
            )
    return out


def vocabulary(domain: str) -> set[str]:
    """Every lemma the subject's packs teach."""
    out: set[str] = set()
    for pack in _DOMAIN_SOURCES[domain][1]:
        out |= _lemmas(pack)
    return out


def _base_forms(word: str) -> set[str]:
    """The spellings a question's relation word may take — independently
    written, covering the same +s/+es/y↔ies agreement the serving path
    normalizes with its own table."""
    forms = {word}
    forms.add(word + "s")
    forms.add(word + "es")
    if word.endswith("y"):
        forms.add(word[:-1] + "ies")
    if word.endswith("s"):
        forms.add(word[:-1])
    if word.endswith("es"):
        forms.add(word[:-2])
    if word.endswith("ies"):
        forms.add(word[:-3] + "y")
    return forms


def _connective_for(relation: str) -> str | None:
    candidates = _base_forms(relation)
    for connective in _FAMILY_OF_CONNECTIVE:
        if connective in candidates or relation == connective:
            return connective
    return None


def oracle_answer(domain: str, subject: str, relation: str, obj: str) -> OracleVerdict:
    """The gold verdict for one exam question against *domain*'s curriculum."""
    vocab = vocabulary(domain)
    if subject not in vocab or obj not in vocab:
        return OracleVerdict("declined", "untaught_vocabulary", "", 0)
    connective = _connective_for(relation)
    if connective is None:
        return OracleVerdict("declined", "out_of_curriculum", "", 0)
    family = _FAMILY_OF_CONNECTIVE[connective]
    edges = [e for e in _edges(domain) if _FAMILY_OF_CONNECTIVE[e[1]] == family]
    if not edges:
        return OracleVerdict("declined", "empty_curriculum", family, 0)
    # Entailment needs the SAME relation, not merely the same family: the
    # curriculum teaching "entropy reveals energy" has not thereby taught
    # "entropy causes energy". Family scoping decides which premises are in
    # play; the connective decides what was actually said.
    #
    # ADR-0264 R1/R8 — and the POLARITY decides which way. A taught negative row
    # is a taught refutation: the curriculum has said something about this atom,
    # and what it said is "no". That is categorically different from an absent
    # edge, which stays UNKNOWN under the open-world reading. Both are checked at
    # depth 1, against the same atom, so the two cannot be confused.
    for s, c, o, _id, polarity in edges:
        if s == subject and c == connective and o == obj:
            if polarity == _NEGATIVE:
                return OracleVerdict("refuted", "", family, 1)
            return OracleVerdict("entailed", "", family, 1)
    # No taught edge. Report the shortest path so the lane can prove the
    # serving path does NOT compose a chain into a claim.
    #
    # NEGATIVE rows are EXCLUDED from the adjacency (ADR-0264 R8). Reachability
    # here exists to measure whether an untaught pair is *composable* from taught
    # edges, and "a does not X b" supplies no step from a to b — treating it as
    # one would report a path built out of a denial.
    adjacency: dict[str, list[str]] = {}
    for s, _c, o, _id, polarity in edges:
        if polarity == _NEGATIVE:
            continue
        adjacency.setdefault(s, []).append(o)
    seen = {subject}
    queue: deque[tuple[str, int]] = deque([(subject, 0)])
    while queue:
        node, dist = queue.popleft()
        for nxt in adjacency.get(node, ()):
            if nxt == obj:
                # ``dist`` counts edges already traversed to reach ``node``;
                # this one closes the path, so the shortest path is dist + 1.
                return OracleVerdict("unknown", "", family, dist + 1)
            if nxt not in seen:
                seen.add(nxt)
                queue.append((nxt, dist + 1))
    return OracleVerdict("unknown", "", family, 0)


def taught_edges(domain: str) -> list[tuple[str, str, str, str, str]]:
    """Public view for the lane's provenance assertions.

    Each row carries its polarity as the fifth element (ADR-0264 R1).
    """
    return _edges(domain)


__all__ = ["OracleVerdict", "oracle_answer", "taught_edges", "vocabulary"]
