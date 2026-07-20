"""Layer A — English surface constraint extraction (candidates only).

Forbidden: selecting an arithmetic operation; fabricating omitted context.
Ambiguity is preserved — no premature collapse to a single parse.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Sequence

from core.semantic_primitives import ProvenanceSpan, ValidationError

_ENTITY_RE = re.compile(
    r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b"
)
_NUMBER_RE = re.compile(
    r"(?P<num>\d+(?:\.\d+)?)\s*(?P<unit>apples?|oranges?|dollars?|hours?|kg|items?|books?)?",
    re.IGNORECASE,
)
_RELATION_CUES: tuple[tuple[str, str], ...] = (
    ("gave", "transfer_cue"),
    ("sold", "transfer_cue"),
    ("bought", "transfer_cue"),
    ("has", "possession_cue"),
    ("have", "possession_cue"),
    ("more than", "comparison_cue"),
    ("less than", "comparison_cue"),
    ("each", "partition_cue"),
    ("per", "rate_cue"),
)


@dataclass(frozen=True, slots=True)
class CandidateEntity:
    candidate_id: str
    surface: str
    confidence: float
    provenance: ProvenanceSpan
    kind_hint: str = "entity"

    def __post_init__(self) -> None:
        if not (0.0 <= float(self.confidence) <= 1.0):
            raise ValidationError("CandidateEntity.confidence must be in [0, 1]")
        if not self.candidate_id:
            raise ValidationError("CandidateEntity.candidate_id must be non-empty")


@dataclass(frozen=True, slots=True)
class CandidateRelation:
    candidate_id: str
    cue: str
    relation_hint: str
    confidence: float
    provenance: ProvenanceSpan
    left_surface: str = ""
    right_surface: str = ""

    def __post_init__(self) -> None:
        if not (0.0 <= float(self.confidence) <= 1.0):
            raise ValidationError("CandidateRelation.confidence must be in [0, 1]")


@dataclass(frozen=True, slots=True)
class NumericToken:
    token_id: str
    raw: str
    value_text: str
    unit: str
    confidence: float
    provenance: ProvenanceSpan


@dataclass(frozen=True, slots=True)
class SurfaceConstraintSet:
    """Layer A output — constraints and candidates, never a chosen op."""

    source_text: str
    entities: tuple[CandidateEntity, ...]
    relations: tuple[CandidateRelation, ...]
    numerics: tuple[NumericToken, ...]
    # When multiple relation cues apply, all are retained (ambiguity preserved).
    ambiguity_notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for e in self.entities:
            if not isinstance(e, CandidateEntity):
                raise ValidationError("entities must be CandidateEntity instances")
        for r in self.relations:
            if not isinstance(r, CandidateRelation):
                raise ValidationError("relations must be CandidateRelation instances")


def extract_english_surface(text: str) -> SurfaceConstraintSet:
    """Extract surface candidates without selecting arithmetic operations."""
    if not isinstance(text, str):
        raise ValidationError("Layer A input must be a str")
    source = text
    entities: list[CandidateEntity] = []
    seen_ent: set[str] = set()
    for i, m in enumerate(_ENTITY_RE.finditer(source)):
        surface = m.group(1)
        # Skip sentence-initial function words that look capitalized mid-stream poorly
        if surface.lower() in {"the", "a", "an", "if", "when"}:
            continue
        key = surface.lower()
        if key in seen_ent:
            continue
        seen_ent.add(key)
        span = ProvenanceSpan(start=m.start(1), end=m.end(1), text=surface)
        entities.append(
            CandidateEntity(
                candidate_id=f"ent:{i}:{key}",
                surface=surface,
                confidence=0.7,
                provenance=span,
                kind_hint="entity",
            )
        )

    numerics: list[NumericToken] = []
    for i, m in enumerate(_NUMBER_RE.finditer(source)):
        unit = (m.group("unit") or "").lower()
        raw = m.group(0).strip()
        span = ProvenanceSpan(start=m.start(), end=m.end(), text=raw)
        numerics.append(
            NumericToken(
                token_id=f"num:{i}",
                raw=raw,
                value_text=m.group("num"),
                unit=unit or "count",
                confidence=0.9 if unit else 0.75,
                provenance=span,
            )
        )
        # Unit nouns are entity candidates (items possessed / transferred).
        if unit:
            key = unit.rstrip("s")
            if key not in seen_ent:
                seen_ent.add(key)
                entities.append(
                    CandidateEntity(
                        candidate_id=f"ent:unit:{i}:{key}",
                        surface=unit,
                        confidence=0.8,
                        provenance=span,
                        kind_hint="quantity_item",
                    )
                )

    relations: list[CandidateRelation] = []
    lower = source.lower()
    for i, (cue, hint) in enumerate(_RELATION_CUES):
        idx = lower.find(cue)
        if idx < 0:
            continue
        span = ProvenanceSpan(start=idx, end=idx + len(cue), text=source[idx : idx + len(cue)])
        relations.append(
            CandidateRelation(
                candidate_id=f"rel:{i}:{hint}",
                cue=cue,
                relation_hint=hint,
                confidence=0.65,
                provenance=span,
            )
        )

    notes: list[str] = []
    transferish = [r for r in relations if r.relation_hint == "transfer_cue"]
    if len(transferish) > 1:
        notes.append("multiple_transfer_cues_retained")
    if len(relations) > 1:
        notes.append("multi_relation_candidates_retained")

    return SurfaceConstraintSet(
        source_text=source,
        entities=tuple(entities),
        relations=tuple(relations),
        numerics=tuple(numerics),
        ambiguity_notes=tuple(notes),
    )
