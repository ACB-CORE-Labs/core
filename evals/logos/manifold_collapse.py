"""The manifold-collapse instrument — how many distinct meanings the ground still holds.

Foundations Audit FA-1 (L2, the logos layer / G-25).

ADR-0015 states the requirement the three-language design must satisfy: aligned
clauses resonate *"without flattening their distinctions"*, and cross-language
alignment is *"a weighted graph, **not** a translation table"*. This module
measures whether the compiled manifold honours that — by the bluntest possible
test, which is also the exact one: **do two surfaces occupy the same coordinate?**

Coordinates are compared bit-exactly (``ndarray.tobytes()``). There is no
tolerance to tune and no metric to argue about: either two words are the same
point in the semantic ground or they are not. A tolerance would have hidden this
finding — the collisions measured here are exact equality, not near-equality.

The instrument reports both the **mounted** configuration (what the runtime
actually grounds against) and the **per-pack controls**. The controls are what
make it a diagnosis instead of a number: if English alone is collision-free and
English *mounted with the depth packs* is not, then mounting Hebrew and Greek —
the operation designed to add depth — is what removes distinctions.

Deliberately narrow: this measures the compiled ground only. Whether a *corrected*
compiler restores discrimination is a separate, pre-registered experiment
(``docs/analysis/logos-substrate-collapse-2026-07-28.md`` §"What FA-1 asks next").
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass

from packs import load_pack
from packs.compiler import load_mounted_packs

#: The trilingual mount is the CORE-Logos configuration of ADR-0005/0015:
#: English as articulation surface, Hebrew as depth anchor, Greek as relational depth.
TRILINGUAL: tuple[str, ...] = ("en_minimal_v1", "he_logos_micro_v1", "grc_logos_micro_v1")


@dataclass(frozen=True)
class CollapseReport:
    """Exact, deterministic census of coordinate collisions in a compiled ground."""

    config: tuple[str, ...]
    surfaces: int
    distinct_coordinates: int
    #: Each group is the sorted tuple of surfaces sharing one bit-identical coordinate.
    groups: tuple[tuple[str, ...], ...]

    @property
    def surfaces_in_collision(self) -> int:
        return sum(len(group) for group in self.groups)

    @property
    def coordinates_lost(self) -> int:
        """Distinctions the ground can no longer make: surfaces − distinct coordinates."""
        return self.surfaces - self.distinct_coordinates

    def as_dict(self) -> dict:
        return {
            "config": list(self.config),
            "surfaces": self.surfaces,
            "distinct_coordinates": self.distinct_coordinates,
            "coordinates_lost": self.coordinates_lost,
            "collision_groups": len(self.groups),
            "surfaces_in_collision": self.surfaces_in_collision,
            "groups": [list(group) for group in self.groups],
        }


def _census(manifold) -> tuple[int, int, tuple[tuple[str, ...], ...]]:
    by_coordinate: dict[bytes, list[str]] = defaultdict(list)
    for index in range(len(manifold)):
        by_coordinate[manifold.get_versor_at(index).tobytes()].append(manifold.get_word_at(index))
    groups = tuple(
        sorted(
            (tuple(sorted(surfaces)) for surfaces in by_coordinate.values() if len(surfaces) > 1),
            key=lambda group: (-len(group), group),
        )
    )
    return len(manifold), len(by_coordinate), groups


def measure_mounted(pack_ids: tuple[str, ...] = TRILINGUAL) -> CollapseReport:
    """Census the mounted union — the ground the runtime grounds turns against."""
    surfaces, distinct, groups = _census(load_mounted_packs(pack_ids))
    return CollapseReport(config=pack_ids, surfaces=surfaces, distinct_coordinates=distinct, groups=groups)


def measure_pack(pack_id: str) -> CollapseReport:
    """Census one pack compiled alone — the control that isolates the mount-time site."""
    _, manifold = load_pack(pack_id)
    surfaces, distinct, groups = _census(manifold)
    return CollapseReport(config=(pack_id,), surfaces=surfaces, distinct_coordinates=distinct, groups=groups)


def measure_all(pack_ids: tuple[str, ...] = TRILINGUAL) -> dict[str, CollapseReport]:
    """The mounted census plus every per-pack control, keyed for direct comparison."""
    reports = {"mounted": measure_mounted(pack_ids)}
    for pack_id in pack_ids:
        reports[pack_id] = measure_pack(pack_id)
    return reports


def main() -> int:
    print(json.dumps({key: report.as_dict() for key, report in measure_all().items()}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
