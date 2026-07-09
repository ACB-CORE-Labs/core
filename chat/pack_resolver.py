"""chat/pack_resolver.py — ADR-0063 cross-pack surface resolver.

The cold-start grounding composers in :mod:`chat.pack_grounding` were
hardcoded to a single lexicon pack (``en_core_cognition_v1``).  That
asymmetry blocked ``en_core_relations_v1`` from being mounted on the
default runtime: mounting it would silently widen vault recall and
intent classification without a corresponding ratified surface
composer for kinship lemmas.

This module supplies the missing abstraction: a *deterministic*,
*first-match-wins* resolver that maps a lemma to ``(pack_id, semantic_domains)``
across an ordered tuple of mounted lexicon packs.  Surface composers
consult the resolver instead of a single pack; the surface trust-boundary
tag follows the *resolving* pack id.

Design constraints (CLAUDE.md / Reconstruction-over-storage):

- The resolver loads each pack lexicon at most once per process via
  :func:`functools.lru_cache`.  Ratified packs are immutable, so caching
  is sound.
- A pack that fails to load (missing file, unreadable JSON) contributes
  an empty index — callers cannot distinguish "pack absent" from "lemma
  absent in mounted packs".  Both produce ``None``.
- First-match-wins on collision.  The orthogonality test in
  ``tests/test_en_core_relations_v1_pack.py`` enforces zero overlap
  today; this rule documents the deterministic resolution if a future
  pack pair collides.
- No mutation of pack data is performed anywhere in this module.  All
  return types are tuples/frozensets/dicts of plain strings.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

# Default mounted lexicon-pack ids that ADR-0063 surface composers
# consult.  Order matters: earlier packs win on lemma collision.  This
# tuple is intentionally narrow — it lists only ratified ``en_core_*``
# *content* packs.  Identity/safety/ethics packs are propositional
# overlays and never carry vocabulary; they are deliberately excluded.
DEFAULT_RESOLVABLE_PACK_IDS: tuple[str, ...] = (
    "en_core_cognition_v1",
    "en_core_meta_v1",
    "en_core_attitude_v1",
    "en_core_temporal_v1",
    "en_core_action_v1",
    "en_core_quantitative_v1",
    "en_core_spatial_v1",
    "en_core_causation_v1",
    "en_core_polarity_v1",
    # Foundation-curriculum syntax substrate.  Mounted AFTER the
    # high-frequency content packs so it is purely additive: every lemma
    # it owns is disjoint from earlier mounted packs.  Two colliders were
    # renamed at authoring time so syntax never steals prior resolution
    # (`agent`→`agent_role`, owned by en_core_meta_v1; `comparison`→
    # `comparison_relation`, owned by en_core_cognition_v1).  `negation`
    # is kept bare: no *mounted* pack owned it, so syntax now grounds it.
    "en_core_syntax_v1",
    "en_core_relations_v1",
    "en_core_relations_v2",
    # ADR-0073c — synthetic English anchor lemmas for cross-lang collapse.
    # Mounted last so cognition / relations content packs win first-match.
    # Carries "love" / "peace" / "justice" entries that exist only as
    # collapse-anchor targets for the he_chesed / he_shalom / he_tzedek
    # anchor lenses.  Composer surfaces here are intentionally minimal —
    # the substantive content lives in the lens annotation.
    "en_collapse_anchors_v1",
)

# 3-core-language (English + Hebrew root density + Koine Greek Logos precision)
# depth packs for LexicalResolution. These are used alongside DEFAULT when
# building PropositionGraph nodes with language/root/morphology_id for
# bidirectional comprehension/articulation/contemplation.
# Sourced to align with anchor-lens substrate packs.
DEPTH_PACK_IDS: tuple[str, ...] = (
    "he_core_cognition_v1",
    "he_logos_micro_v1",
    "grc_logos_cognition_v1",
    "grc_logos_micro_v1",
)


@dataclass(frozen=True, slots=True)
class LexicalResolution:
    """Immutable, shared lexical resolution for masterful bidirectional use.

    Serves comprehension (ingest → grounded PropositionGraph via resolve_gloss
    path), articulation (graph → realize_semantic can consult depth for
    precision), and internal reasoning/contemplation (operations "between"
    read/write on the same substrate).

    Three core languages:
    - English: operational base
    - Hebrew: root density (e.g. ד-ב-ר for utterance/word)
    - Koine Greek: Logos precision (structuring principle, John 1:1)

    The geometric field and PropositionGraph are designed to hold this depth.
    All fields are plain values; no mutation.
    """
    pack_id: str
    lemma: str
    language: str
    pos: str = ""
    gloss: str | None = None
    semantic_domains: tuple[str, ...] = ()
    morphology_id: str | None = None
    root: str | None = None


_PACK_ROOT = Path(__file__).resolve().parent.parent / "packs" / "data"


@lru_cache(maxsize=16)
def _pack_lexicon_for(pack_id: str) -> dict[str, tuple[str, ...]]:
    """Return ``{lemma_lower: semantic_domains}`` for *pack_id*, cached.

    Returns an empty dict if the pack's lexicon file is missing,
    unreadable, or contains no entries with ``semantic_domains``.
    Ratified packs are immutable so the cache survives the process
    lifetime.
    """
    lexicon_path = _PACK_ROOT / pack_id / "lexicon.jsonl"
    if not lexicon_path.exists():
        return {}
    out: dict[str, tuple[str, ...]] = {}
    for line in lexicon_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(entry, dict):
            continue
        lemma = entry.get("lemma") or entry.get("surface")
        if not lemma or not isinstance(lemma, str):
            continue
        domains = entry.get("semantic_domains", ())
        if not isinstance(domains, (list, tuple)) or not domains:
            continue
        out[lemma.lower()] = tuple(str(d) for d in domains)
    return out


def resolve_lemma(
    lemma: str,
    pack_ids: tuple[str, ...] = DEFAULT_RESOLVABLE_PACK_IDS,
) -> tuple[str, tuple[str, ...]] | None:
    """Return ``(pack_id, semantic_domains)`` for the first pack in
    *pack_ids* whose lexicon contains *lemma*, else ``None``.

    First-match-wins on collision.  ``pack_ids`` defaults to
    :data:`DEFAULT_RESOLVABLE_PACK_IDS`.
    """
    if not lemma or not isinstance(lemma, str):
        return None
    key = lemma.strip().lower()
    if not key:
        return None
    for pack_id in pack_ids:
        index = _pack_lexicon_for(pack_id)
        domains = index.get(key)
        if domains:
            return (pack_id, domains)
    return None


def is_resolvable(
    lemma: str,
    pack_ids: tuple[str, ...] = DEFAULT_RESOLVABLE_PACK_IDS,
) -> bool:
    """Return True iff *lemma* resolves in any of *pack_ids*."""
    return resolve_lemma(lemma, pack_ids) is not None


def mounted_lemmas(
    pack_ids: tuple[str, ...] = DEFAULT_RESOLVABLE_PACK_IDS,
) -> frozenset[str]:
    """Return the frozen union of lemmas across *pack_ids*.

    Used by topic extractors that iterate over user-text tokens and
    need an O(1) "is this token any mounted lemma?" check.
    """
    out: set[str] = set()
    for pack_id in pack_ids:
        out.update(_pack_lexicon_for(pack_id).keys())
    return frozenset(out)


@lru_cache(maxsize=16)
def _pack_glosses_for(pack_id: str) -> dict[str, tuple[str, str]]:
    """Return ``{lemma_lower: (pos, gloss)}`` from the pack's optional
    ``glosses.jsonl`` companion file.

    Returns an empty dict when the pack ships no glosses (back-compat
    with the original ratified packs).  Glosses are an additive overlay
    on top of the immutable, checksum-sealed ``lexicon.jsonl`` — they
    intentionally live in a separate file so adding a gloss never
    perturbs the lexicon checksum.

    Each line of ``glosses.jsonl`` must be a JSON object with at least
    ``lemma`` and ``gloss`` fields; ``pos`` (string) is optional and
    drives the natural-language sentence frame in
    :func:`chat.pack_grounding.pack_grounded_surface`.  Lines without
    a non-empty ``lemma`` or ``gloss`` are silently skipped — never
    fabricated.  Malformed JSON lines are also skipped (defensive
    parsing — a single bad line never breaks gloss resolution for the
    rest of the pack).
    """
    path = _PACK_ROOT / pack_id / "glosses.jsonl"
    if not path.exists():
        return {}
    out: dict[str, tuple[str, str]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(entry, dict):
            continue
        lemma = entry.get("lemma")
        gloss = entry.get("gloss")
        if not isinstance(lemma, str) or not lemma.strip():
            continue
        if not isinstance(gloss, str) or not gloss.strip():
            continue
        pos_raw = entry.get("pos")
        pos = pos_raw if isinstance(pos_raw, str) else ""
        out[lemma.strip().lower()] = (pos, gloss.strip())
    return out


def resolve_gloss(
    lemma: str,
    pack_ids: tuple[str, ...] = DEFAULT_RESOLVABLE_PACK_IDS,
) -> tuple[str, str, str] | None:
    """Return ``(pack_id, pos, gloss)`` for the first pack in
    *pack_ids* that BOTH (a) ratifies *lemma* in its ``lexicon.jsonl``
    AND (b) carries a gloss for it in ``glosses.jsonl``.

    First-match-wins on collision, matching :func:`resolve_lemma`'s
    resolution order — so a lemma's lexicon resolution and gloss
    resolution always agree on the resolving pack.

    The lexicon-residency requirement is load-bearing trust-boundary
    discipline (2026-05-19 design review).  Without it, ``glosses.jsonl``
    would become a parallel surface-authoring channel that bypasses the
    checksum-sealed lexicon: someone could ship a gloss for a lemma the
    pack has never ratified, and the runtime would emit that gloss as
    if it were pack content.  This function rejects any (lemma, pack)
    pair where the lemma is not present in the pack's lexicon, even if
    a gloss exists for it.
    """
    if not lemma or not isinstance(lemma, str):
        return None
    key = lemma.strip().lower()
    if not key:
        return None
    for pack_id in pack_ids:
        lex = _pack_lexicon_for(pack_id)
        if key not in lex:
            # Lemma not ratified in this pack's lexicon — refuse to
            # surface any gloss this pack might carry for it.
            continue
        glosses = _pack_glosses_for(pack_id)
        entry = glosses.get(key)
        if entry is not None:
            pos, gloss = entry
            return (pack_id, pos, gloss)
    return None


@lru_cache(maxsize=16)
def _pack_full_lexicon_for(pack_id: str) -> dict[str, dict]:
    """Return richer {lemma_lower: entry} including language, morphology_id,
    semantic_domains for 3-language depth resolution.

    Mirrors _pack_lexicon_for structure but retains the full fields needed
    for LexicalResolution (Hebrew/Greek root-linked entries etc.).
    Immutable packs → safe to cache.
    """
    lexicon_path = _PACK_ROOT / pack_id / "lexicon.jsonl"
    if not lexicon_path.exists():
        return {}
    out: dict[str, dict] = {}
    for line in lexicon_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(entry, dict):
            continue
        lemma = entry.get("lemma") or entry.get("surface")
        if not lemma or not isinstance(lemma, str):
            continue
        key = lemma.strip().lower()
        # retain relevant depth fields
        out[key] = {
            "language": entry.get("language") or "en",
            "morphology_id": entry.get("morphology_id"),
            "semantic_domains": tuple(str(d) for d in entry.get("semantic_domains", ())),
            "pos": entry.get("pos") or "",
        }
    return out


@lru_cache(maxsize=16)
def _pack_morph_roots_for(pack_id: str) -> dict[str, str]:
    """Return {morphology_id: root} for the pack's morphology.jsonl.

    Enables root-level depth (Hebrew triconsonantal, Greek stems) without
    pulling the full MorphologyRegistry into the hot resolver path.
    """
    morph_path = _PACK_ROOT / pack_id / "morphology.jsonl"
    if not morph_path.exists():
        return {}
    out: dict[str, str] = {}
    for line in morph_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(entry, dict):
            continue
        mid = entry.get("morphology_id")
        root = entry.get("root")
        if isinstance(mid, str) and isinstance(root, str) and mid and root:
            out[mid] = root
    return out


def resolve_entry(
    lemma: str,
    pack_ids: tuple[str, ...] = DEFAULT_RESOLVABLE_PACK_IDS,
) -> LexicalResolution | None:
    """Return rich LexicalResolution for the first matching pack.

    This is the canonical entry point for depth-aware resolution usable
    both for comprehension grounding and (symmetrically) articulation /
    contemplation. Falls back gracefully for English-centric packs.
    First-match-wins, same order as resolve_lemma/resolve_gloss.
    """
    if not lemma or not isinstance(lemma, str):
        return None
    key = lemma.strip().lower()
    if not key:
        return None
    for pack_id in pack_ids:
        full = _pack_full_lexicon_for(pack_id)
        if key not in full:
            continue
        info = full[key]
        # gloss is optional but preferred when present
        glosses = _pack_glosses_for(pack_id)
        pos, gloss = glosses.get(key, ("", None))
        if not gloss:
            # fall back to pos from full if no dedicated gloss
            pos = info.get("pos", "") or pos
        morph_id = info.get("morphology_id")
        root = None
        if morph_id:
            roots = _pack_morph_roots_for(pack_id)
            root = roots.get(morph_id)
        return LexicalResolution(
            pack_id=pack_id,
            lemma=lemma,
            language=info.get("language", "en"),
            pos=pos or "",
            gloss=gloss,
            semantic_domains=info.get("semantic_domains", ()),
            morphology_id=morph_id,
            root=root,
        )
    return None


def clear_resolver_cache() -> None:
    """Drop all caches in this module — lexicon AND glosses.

    Test-only escape hatch: enables fixture-based pack mutation
    scenarios.  Production code never calls this — ratified packs are
    immutable.

    Both ``_pack_lexicon_for`` and ``_pack_glosses_for`` are
    ``functools.lru_cache``-wrapped, so the test must clear BOTH or a
    fixture that adds glosses on disk would be invisible to subsequent
    ``resolve_gloss`` calls in the same test process.  Prior versions
    cleared only the lexicon cache.
    """
    _pack_lexicon_for.cache_clear()
    _pack_glosses_for.cache_clear()
    _pack_lemma_to_entry_id.cache_clear()
    _pack_senses_for.cache_clear()


@lru_cache(maxsize=16)
def _pack_lemma_to_entry_id(pack_id: str) -> dict[str, str]:
    """Return ``{lemma_lower: entry_id}`` from the pack's lexicon.jsonl."""
    lexicon_path = _PACK_ROOT / pack_id / "lexicon.jsonl"
    if not lexicon_path.exists():
        return {}
    out: dict[str, str] = {}
    for line in lexicon_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(entry, dict):
            continue
        lemma = entry.get("lemma") or entry.get("surface")
        if not lemma or not isinstance(lemma, str):
            continue
        entry_id = entry.get("entry_id")
        if isinstance(entry_id, str) and entry_id.strip():
            out[lemma.lower()] = entry_id.strip()
    return out


@lru_cache(maxsize=16)
def _pack_senses_for(pack_id: str) -> dict[str, dict]:
    """Return ``{lemma_id: geometric_signature}`` from the pack's optional
    ``senses.jsonl`` file. Also maps ``lemma`` as a fallback key.
    """
    path = _PACK_ROOT / pack_id / "senses.jsonl"
    if not path.exists():
        return {}
    out: dict[str, dict] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(entry, dict):
            continue
            
        geometric_signature = entry.get("geometric_signature")
        if not isinstance(geometric_signature, dict):
            continue
            
        lemma_id = entry.get("lemma_id")
        if isinstance(lemma_id, str) and lemma_id.strip():
            out[lemma_id.strip()] = geometric_signature
            
        # Optional fallback for direct lemma matching if lemma is present
        lemma = entry.get("lemma")
        if isinstance(lemma, str) and lemma.strip():
            out[lemma.strip().lower()] = geometric_signature
            
    return out


def resolve_geometric_signature(
    lemma: str,
    pack_ids: tuple[str, ...] = DEFAULT_RESOLVABLE_PACK_IDS,
) -> tuple[str, dict] | None:
    """Return ``(pack_id, geometric_signature)`` for the first pack in
    *pack_ids* that BOTH (a) ratifies *lemma* in its ``lexicon.jsonl``
    AND (b) carries a geometric_signature for it in ``senses.jsonl``.
    """
    if not lemma or not isinstance(lemma, str):
        return None
    key = lemma.strip().lower()
    if not key:
        return None
    for pack_id in pack_ids:
        lex = _pack_lexicon_for(pack_id)
        if key not in lex:
            continue
            
        lemma_ids = _pack_lemma_to_entry_id(pack_id)
        entry_id = lemma_ids.get(key)
        
        senses = _pack_senses_for(pack_id)
        
        if entry_id and entry_id in senses:
            return (pack_id, senses[entry_id])
            
        if key in senses:
            return (pack_id, senses[key])
            
    return None
