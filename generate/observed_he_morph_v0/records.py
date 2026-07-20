"""Observed Hebrew morphology records from compiled runtime pack data."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

_REPO_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_PACK = "he_logos_micro_v0"  # may not exist
_DEFAULT_PACK_ID = "he_logos_micro_v1"


@dataclass(frozen=True, slots=True)
class ObservedHebrewSurface:
    """Observed surface form from compiled pack with source-span provenance."""

    surface: str
    lemma: str
    language: str
    morphology_id: str
    root: str
    number: str  # singular | plural | unknown
    source_pack_id: str
    source_span: tuple[int, int]  # byte offsets in morphology.jsonl line stream
    raw_record: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "surface": self.surface,
            "lemma": self.lemma,
            "language": self.language,
            "morphology_id": self.morphology_id,
            "root": self.root,
            "number": self.number,
            "source_pack_id": self.source_pack_id,
            "source_span": list(self.source_span),
        }


@dataclass(frozen=True, slots=True)
class CanonicalConstraint:
    """Language-independent constraint shared across consumers."""

    constraint_id: str
    kind: str  # e.g. plurality_marked
    payload: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "constraint_id": self.constraint_id,
            "kind": self.kind,
            "payload": dict(self.payload),
        }


@dataclass(frozen=True, slots=True)
class AuthoredMappingRule:
    """Authored morph → constraint mapping with preconditions + counterexamples."""

    rule_id: str
    preconditions: tuple[str, ...]
    counterexamples: tuple[str, ...]
    constraint_kind: str

    def matches(self, surface: ObservedHebrewSurface) -> bool:
        raise NotImplementedError

    def to_constraint(self, surface: ObservedHebrewSurface) -> CanonicalConstraint:
        raise NotImplementedError


def load_observed_morphology(
    pack_id: str = _DEFAULT_PACK_ID,
    *,
    repo_root: Path | None = None,
) -> tuple[ObservedHebrewSurface, ...]:
    """Load morphology from compiled ``packs/data/<pack_id>/morphology.jsonl``.

    Fail closed if the pack is missing or contains no HE rows.
    """
    root = repo_root or _REPO_ROOT
    path = root / "packs" / "data" / pack_id / "morphology.jsonl"
    if not path.is_file():
        raise FileNotFoundError(f"compiled HE morphology missing: {path}")
    out: list[ObservedHebrewSurface] = []
    offset = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        raw_line = line
        start = offset
        end = offset + len(raw_line.encode("utf-8"))
        offset = end + 1  # newline
        if not line.strip():
            continue
        rec = json.loads(line)
        if rec.get("language") not in (None, "he"):
            # Only HE surfaces for this vertical slice.
            if rec.get("language") not in ("he",):
                continue
        infl = rec.get("inflection") or {}
        number = str(infl.get("number") or "unknown")
        out.append(
            ObservedHebrewSurface(
                surface=str(rec.get("surface") or ""),
                lemma=str(rec.get("lemma") or ""),
                language="he",
                morphology_id=str(rec.get("morphology_id") or ""),
                root=str(rec.get("root") or ""),
                number=number,
                source_pack_id=pack_id,
                source_span=(start, end),
                raw_record=rec,
            )
        )
    if not out:
        raise ValueError(f"no HE morphology rows in {path}")
    return tuple(out)


def lookup_surface(
    surfaces: Sequence[ObservedHebrewSurface],
    surface: str,
) -> tuple[ObservedHebrewSurface, ...] | None:
    """Exact surface match; multi-hit returns all candidates (ambiguity)."""
    hits = tuple(s for s in surfaces if s.surface == surface)
    return hits if hits else None
