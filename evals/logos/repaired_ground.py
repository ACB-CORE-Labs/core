"""The repaired semantic ground — R1/R2/R3 of the FA-1 pre-registration.

`docs/analysis/fa1-holonomy-gate-preregistration.md` registers three repairs and the
criterion that judges them. This module implements the repairs; it takes no verdict.

Nothing here modifies the serving compiler. R1 and R3 are applied by *substituting two
module-level functions* inside a context manager, against the real compile path, so the
experiment measures the shipped pipeline with two operations corrected rather than a
re-implementation that could drift from it. The caches are cleared on entry and on exit,
so a repaired ground never leaks into anything else in the process.

  R1  blend on the group instead of overwriting — `algebra/rotor.py`'s geodesic
  R2  close the loop around the *pair* — `loop_deviation` below
  R3  resolve alignment edges against the packs actually mounted, not an id-prefix table
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

import numpy as np

from algebra.cl41 import geometric_product, reverse as cl_reverse
from algebra.rotor import rotor_power, word_transition_rotor
from algebra.versor import unitize_versor
from packs import compiler as _compiler

#: The six packs that carry logos data. The serving path grounds Hebrew and Greek against
#: the `*_cognition_v1` pair (`chat/pack_grounding.py:56-57`); the micro packs are the
#: ADR-0015 seed. R3 exists so both participate — 63 of the 83 authored edges live in the
#: cognition packs and currently resolve to nothing.
LOGOS_MOUNT: tuple[str, ...] = (
    "en_minimal_v1",
    "en_core_cognition_v1",
    "he_logos_micro_v1",
    "he_core_cognition_v1",
    "grc_logos_micro_v1",
    "grc_logos_cognition_v1",
)

#: `en_collapse_anchors_v1` is DELIBERATELY ABSENT and cannot be added: its manifest declares
#: `role: "collapse_anchor"`, which is not a member of `packs.schema.LanguageRole`, so
#: `load_pack()` raises before the lexicon is read. `chat/pack_grounding.py` consumes it by
#: opening `lexicon.jsonl` on a raw path — bypassing the loader that would reject it — and 24
#: alignment edges point into it, all of which therefore resolve to nothing. The enum carries
#: a comment recording this exact failure once before (ADR-0097, `domain_seed`); a registry
#: widened by hand falls behind by hand. Reported by the gate as `edges_unresolved_under_R3`
#: rather than silently excluded.

#: Identity of Cl(4,1): the scalar 1. A closed loop returns here.
IDENTITY = np.zeros(32, dtype=np.float64)
IDENTITY[0] = 1.0


# ---------------------------------------------------------------------------
# R1 — interpolation that stays on the versor group
# ---------------------------------------------------------------------------

def geodesic_blend(source: np.ndarray, target: np.ndarray, strength: float) -> np.ndarray:
    """Move `source` a fraction `strength` along the group geodesic toward `target`.

    The operation the compiler's `_blend_feature_versors` was named and parametrised for.
    A linear combination of two versors is not a versor — the group is not closed under
    addition — which is why `VocabManifold.update()` refuses one, and why returning the
    target verbatim became the escape. `R^t · source`, with `R` the transition rotor, is
    lawful at every `t`: it stays on the group by construction.

    Endpoints are exact: `t=0` returns the source, `t=1` the target.
    """
    strength = max(0.0, min(1.0, float(strength)))
    src = np.asarray(source, dtype=np.float64)
    if strength <= 0.0:
        return np.asarray(source, dtype=np.float32).copy()
    tgt = np.asarray(target, dtype=np.float64)
    if strength >= 1.0:
        return np.asarray(target, dtype=np.float32).copy()
    moved = geometric_product(rotor_power(word_transition_rotor(src, tgt), strength), src)
    return np.asarray(unitize_versor(moved), dtype=np.float32)


def _clear_pack_caches() -> None:
    _compiler._load_pack_cached.cache_clear()
    _compiler._load_mounted_packs_cached.cache_clear()
    _compiler._load_pack_entries_cached.cache_clear()


@contextmanager
def repaired_compiler(pack_ids: tuple[str, ...] = LOGOS_MOUNT) -> Iterator[None]:
    """Compile with R1 (geodesic blending) and R3 (mount-wide edge resolution) in force.

    R3 replaces the hardcoded `{"he": …, "grc": …, "en": …}` prefix table with the packs
    actually being mounted. Entry ids are pack-local, so a global prefix table can only
    ever address the three packs it names; every edge belonging to any other pack of the
    same language resolves to a pack that has never heard of it and is dropped in silence.
    """
    original_blend = _compiler._blend_feature_versors
    original_infer = _compiler._infer_foreign_pack_ids

    def _infer_from_mount(home_pack_id: str, _graph) -> list[str]:  # noqa: ANN001 - private type
        # The graph is ignored on purpose: membership of the mount, not the shape of the
        # edge ids, decides which packs an edge may address.
        return [pack_id for pack_id in pack_ids if pack_id != home_pack_id]

    _compiler._blend_feature_versors = geodesic_blend
    _compiler._infer_foreign_pack_ids = _infer_from_mount
    _clear_pack_caches()
    try:
        yield
    finally:
        _compiler._blend_feature_versors = original_blend
        _compiler._infer_foreign_pack_ids = original_infer
        _clear_pack_caches()


# ---------------------------------------------------------------------------
# R2 — the loop, closed around a pair of representations
# ---------------------------------------------------------------------------

def forward_walk(versors: list[np.ndarray]) -> np.ndarray:
    """`F(X) = v₁ · v₂ · … · vₙ` — the ordered geometric product of a clause's versors.

    No per-token position rotor. The shipped encoder conjugates each token by its absolute
    index, which was introduced so path order would survive degenerate scalar/vector test
    fixtures; across languages, clauses differ in length, so that schedule injects a length
    artefact into every cross-language comparison (RQ2 of the 2026-06-14 finding). Order
    sensitivity does not depend on it: the geometric product is non-commutative.
    """
    if not versors:
        raise ValueError("cannot walk an empty clause")
    walk = unitize_versor(np.asarray(versors[0], dtype=np.float64))
    for versor in versors[1:]:
        walk = geometric_product(walk, unitize_versor(np.asarray(versor, dtype=np.float64)))
        walk = unitize_versor(walk)
    return walk


def closed_holonomy(clause_a: list[np.ndarray], clause_b: list[np.ndarray]) -> np.ndarray:
    """`H(A,B) = unitize(F(A) · reverse(F(B)))` — transport out along A, return along B."""
    return unitize_versor(geometric_product(forward_walk(clause_a), cl_reverse(forward_walk(clause_b))))


def loop_deviation(clause_a: list[np.ndarray], clause_b: list[np.ndarray]) -> float:
    """`d(A,B) = ‖H(A,B) − 1‖` — the single declared metric of the FA-1 criterion.

    Zero when the loop closes. The null hypothesis is the identity, so there is no
    similarity threshold to calibrate and no metric to select after seeing the numbers —
    the failure mode of the June measurement, forbidden here by construction.

    Sign note: `H` and `−H` describe the same transport (versors are defined up to sign),
    so the deviation is taken to the nearer of `±1`.
    """
    holonomy = closed_holonomy(clause_a, clause_b)
    return float(min(np.linalg.norm(holonomy - IDENTITY), np.linalg.norm(holonomy + IDENTITY)))
