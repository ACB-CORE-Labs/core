"""FA-1 — the pre-registered holonomy-gate experiment.

Criterion, corpus rules, negative classes and anti-gaming rules are registered in
`docs/analysis/fa1-holonomy-gate-preregistration.md` — committed at `94f05ba8`, and amended
once (A1, the corpus bound) before any discrimination number existed. This module executes
that registration; every threshold it applies is quoted from it, and none is computed here.

Run:  ``uv run python -m evals.logos.fa1_gate``
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from itertools import combinations, permutations

import numpy as np

from algebra.cl41 import geometric_product, reverse as cl_reverse
from algebra.versor import unitize_versor
from alignment.graph import load_alignment
from evals.logos.manifold_collapse import _census
from evals.logos.repaired_ground import IDENTITY, LOGOS_MOUNT, forward_walk, repaired_compiler
from packs.compiler import load_mounted_packs, load_pack_entries

#: Packs whose alignment.jsonl is read. Every edge they author participates; none is dropped
#: by hand. An edge whose endpoints do not resolve inside LOGOS_MOUNT is counted and reported.
ALIGNED_PACKS = ("he_logos_micro_v1", "grc_logos_micro_v1", "he_core_cognition_v1", "grc_logos_cognition_v1")

#: Three content words is ADR-0015's own canonical clause shape ("Logos, beginning, truth"),
#: and the shortest length at which word order can be broken in more than one way.
CLAUSE_LEN = 3

#: Pre-registered thresholds — anti-gaming rule 1 forbids editing these after numbers exist.
G1_AUC = 0.80
G2_AUC = 0.75
G3_ORDER_SENSITIVITY = 0.90

#: Amendment A1: cross-pair negatives per aligned pair, drawn deterministically from the
#: sorted enumeration. Classes 1 and 2 stay complete.
CROSS_NEGATIVES_PER_PAIR = 5


@dataclass(frozen=True)
class Concept:
    """One aligned meaning and its realisation in each language that carries it."""

    key: str
    surfaces: tuple[tuple[str, str], ...]  # (language, surface), sorted — hashable

    @property
    def by_language(self) -> dict[str, str]:
        return dict(self.surfaces)

    @property
    def languages(self) -> frozenset[str]:
        return frozenset(language for language, _ in self.surfaces)


def _relation_stem(relation: str) -> str:
    """`cross_lang.logos.illumination.pointed.en` → `cross_lang.logos.illumination`."""
    return relation.replace(".pointed", "").replace(".en_collapse", "").replace(".en", "")


def build_concepts() -> tuple[list[Concept], dict]:
    """Group every resolvable alignment edge into meanings. Mechanical; nothing hand-picked.

    Where a language offers several surfaces for one meaning (`אור` / `אוֹר`), the
    lexicographically first is taken — one rule, applied uniformly, fixed before the run.
    """
    surface_of: dict[str, tuple[str, str]] = {}
    for pack_id in LOGOS_MOUNT:
        for entry in load_pack_entries(pack_id):
            surface_of[entry.entry_id] = (entry.language, entry.surface)

    grouped: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    edges = unresolved = 0
    for pack_id in ALIGNED_PACKS:
        for edge in load_alignment(pack_id).aligned_pairs("cross_lang"):
            edges += 1
            source, target = surface_of.get(edge.source_id), surface_of.get(edge.target_id)
            if source is None or target is None:
                unresolved += 1
                continue
            stem = _relation_stem(edge.relation)
            grouped[stem][source[0]].add(source[1])
            grouped[stem][target[0]].add(target[1])

    concepts = [
        Concept(key=stem, surfaces=tuple(sorted((lang, sorted(surfaces)[0]) for lang, surfaces in langs.items())))
        for stem, langs in sorted(grouped.items())
        if len(langs) >= 2
    ]
    census = {
        "edges_authored": edges,
        "edges_unresolved_under_R3": unresolved,
        "concepts": len(concepts),
        "trilingual_concepts": sum(1 for concept in concepts if len(concept.languages) >= 3),
        "clause_sets": len(list(combinations(range(len(concepts)), CLAUSE_LEN))),
    }
    return concepts, census


def _auc(positive: list[float], negative: list[float]) -> float:
    """P(a random aligned pair deviates LESS than a random negative). Ties count a half.

    Computed by sorting rather than by the O(n·m) double loop — the corpus is ~10^5 negatives
    and the naive form is the difference between seconds and an hour.
    """
    if not positive or not negative:
        return float("nan")
    pos = np.sort(np.asarray(positive, dtype=np.float64))
    neg = np.asarray(negative, dtype=np.float64)
    strictly_less = np.searchsorted(pos, neg, side="left").sum()  # positives below each negative
    less_or_equal = np.searchsorted(pos, neg, side="right").sum()
    ties = less_or_equal - strictly_less
    return float((strictly_less + 0.5 * ties) / (len(pos) * len(neg)))


def run() -> dict:
    concepts, census = build_concepts()
    index_of = {concept: position for position, concept in enumerate(concepts)}

    with repaired_compiler(LOGOS_MOUNT):
        manifold = load_mounted_packs(LOGOS_MOUNT)
        surfaces, distinct, groups = _census(manifold)

        walk_cache: dict[tuple[tuple[str, ...], str], np.ndarray | None] = {}

        def walk(sequence: tuple[Concept, ...], language: str) -> np.ndarray | None:
            """`F(X)` for one clause, memoised — the same ordered tuple recurs constantly."""
            key = (tuple(concept.key for concept in sequence), language)
            if key not in walk_cache:
                try:
                    versors = [manifold.get_versor(concept.by_language[language]) for concept in sequence]
                except KeyError:
                    walk_cache[key] = None
                else:
                    walk_cache[key] = forward_walk(versors)
            return walk_cache[key]

        def deviation(sequence_a: tuple[Concept, ...], la: str, sequence_b: tuple[Concept, ...], lb: str) -> float | None:
            """`d(A,B) = ‖unitize(F(A)·reverse(F(B))) − 1‖`, versor sign-ambiguity resolved."""
            forward, backward = walk(sequence_a, la), walk(sequence_b, lb)
            if forward is None or backward is None:
                return None
            holonomy = unitize_versor(geometric_product(forward, cl_reverse(backward)))
            return float(min(np.linalg.norm(holonomy - IDENTITY), np.linalg.norm(holonomy + IDENTITY)))

        # ---- the aligned corpus: every C(24,3) concept set, every language pair carrying it
        aligned: list[float] = []
        pairs: list[tuple[tuple[Concept, ...], str, str]] = []
        clause_sets = list(combinations(concepts, CLAUSE_LEN))
        for concept_set in clause_sets:
            shared = sorted(frozenset.intersection(*(concept.languages for concept in concept_set)))
            for position, la in enumerate(shared):
                for lb in shared[position + 1 :]:
                    value = deviation(concept_set, la, concept_set, lb)
                    if value is None:
                        continue
                    aligned.append(value)
                    pairs.append((concept_set, la, lb))

        # ---- class 1, lexical substitution (complete: every position × every replacement)
        n_lexical: list[float] = []
        for concept_set, la, lb in pairs:
            for position in range(CLAUSE_LEN):
                for replacement in concepts:
                    if replacement in concept_set or lb not in replacement.languages:
                        continue
                    broken = concept_set[:position] + (replacement,) + concept_set[position + 1 :]
                    value = deviation(concept_set, la, broken, lb)
                    if value is not None:
                        n_lexical.append(value)

        # ---- class 2, word order (complete: every non-identity permutation of the return clause)
        n_order: list[float] = []
        order_sensitive = order_total = 0
        for index, (concept_set, la, lb) in enumerate(pairs):
            base = aligned[index]
            for permuted in permutations(concept_set):
                if permuted == concept_set:
                    continue
                value = deviation(concept_set, la, permuted, lb)
                if value is None:
                    continue
                n_order.append(value)
                order_total += 1
                order_sensitive += int(value > base)

        # ---- class 3, cross-pairing (Amendment A1: first 5 disjoint sets in sorted order)
        n_cross: list[float] = []
        cross_offered = 0
        for concept_set, la, lb in pairs:
            start = max(index_of[concept] for concept in concept_set)
            taken = 0
            for other in clause_sets:
                if taken >= CROSS_NEGATIVES_PER_PAIR:
                    break
                if min(index_of[concept] for concept in other) <= start:
                    continue
                if set(other) & set(concept_set):
                    continue
                cross_offered += 1
                value = deviation(concept_set, la, other, lb)
                if value is None:
                    continue
                n_cross.append(value)
                taken += 1

        # ---- controls, reported regardless of outcome (anti-gaming rule 4)
        self_loops = [
            value
            for value in (deviation(concept_set, la, concept_set, la) for concept_set, la, _ in pairs)
            if value is not None
        ]

    negatives = n_lexical + n_order + n_cross
    g1 = _auc(aligned, negatives)
    g2 = _auc(aligned, n_cross)
    g3 = order_sensitive / order_total if order_total else float("nan")
    g4_lost = surfaces - distinct

    verdict: dict = {
        "corpus": census,
        "ground_after_repair": {
            "mount": list(LOGOS_MOUNT),
            "surfaces": surfaces,
            "distinct_coordinates": distinct,
            "coordinates_lost": g4_lost,
            "collision_groups": len(groups),
        },
        "controls": {
            "max_self_loop_deviation": max(self_loops) if self_loops else float("nan"),
            "aligned_pairs": len(aligned),
            "negatives_generated": {
                "lexical_substitution": len(n_lexical),
                "word_order": len(n_order),
                "cross_pair": len(n_cross),
                "cross_pair_candidates_offered": cross_offered,
            },
        },
        "measurements": {
            "median_aligned": float(np.median(aligned)) if aligned else float("nan"),
            "median_negative": float(np.median(negatives)) if negatives else float("nan"),
            # Per-class, for diagnosis. These are the pre-registered classes reported
            # separately; no criterion is attached to them that is not already in §4.
            "median_lexical": float(np.median(n_lexical)) if n_lexical else float("nan"),
            "median_word_order": float(np.median(n_order)) if n_order else float("nan"),
            "median_cross_pair": float(np.median(n_cross)) if n_cross else float("nan"),
            "auc_vs_lexical": _auc(aligned, n_lexical),
            "auc_vs_word_order": _auc(aligned, n_order),
            "auc_vs_cross_pair": _auc(aligned, n_cross),
        },
        "criterion": {
            "G1_separation": {"required": f"AUC >= {G1_AUC}", "observed": g1, "pass": bool(g1 >= G1_AUC)},
            "G2_cross_pair": {"required": f"AUC >= {G2_AUC}", "observed": g2, "pass": bool(g2 >= G2_AUC)},
            "G3_word_order": {"required": f">= {G3_ORDER_SENSITIVITY}", "observed": g3, "pass": bool(g3 >= G3_ORDER_SENSITIVITY)},
            "G4_no_collapse": {"required": "coordinates_lost == 0", "observed": g4_lost, "pass": bool(g4_lost == 0)},
        },
    }
    verdict["VERDICT"] = "GO" if all(gate["pass"] for gate in verdict["criterion"].values()) else "NO-GO"
    return verdict


def main() -> int:
    print(json.dumps(run(), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
