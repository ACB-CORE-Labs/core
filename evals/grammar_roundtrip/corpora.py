"""Corpora for the grammar round-trip lane.

Three corpora, and all three are load-bearing:

* :func:`positive_graph_cases` — writing-side graphs, for the **G-round-trip**
  ``read(write(g))``.  Sourced from the committed ``english_fluency_ood`` and
  ``grammatical_coverage`` case files so the lane measures the same graphs the
  existing fluency lanes score.
* :func:`positive_surface_cases` — reading-side surfaces inside the reader's
  demonstrated envelope, for the **S-round-trip** ``write(read(s))``.  This is
  the direction that produces a non-zero signal today, which is what makes the
  lane diagnostic rather than a flat zero.
* :func:`negative_surface_cases` — word salad that MUST be rejected.  Without
  this corpus the lane is decoration: ``evals/deterministic_fluency`` reports
  1.00 on all six predicates and still passes ``"banana does the."``.  A lane
  that scores only positives cannot tell "understands English" from "accepts
  anything".

The negative corpus is deliberately built two ways — hand-authored salad plus
mechanical token shuffles of the positive surfaces — so it cannot be satisfied
by pattern-matching a fixed list of bad strings.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]

_GRAPH_CASE_GLOBS = (
    "evals/english_fluency_ood/public/v1/cases.jsonl",
    "evals/english_fluency_ood/holdouts/v1/cases.jsonl",
    "evals/grammatical_coverage/public/v1/cases.jsonl",
    "evals/grammatical_coverage/public/v2/cases.jsonl",
    "evals/grammatical_coverage/holdouts/v1/cases.jsonl",
)


@dataclass(frozen=True, slots=True)
class GraphCase:
    """One writing-side case: an id plus the raw proposition-graph dict."""

    case_id: str
    nodes: tuple[dict[str, object], ...]


@dataclass(frozen=True, slots=True)
class SurfaceCase:
    """One reading-side case: a surface plus why it is in the corpus."""

    case_id: str
    surface: str
    note: str = ""


def positive_graph_cases() -> tuple[GraphCase, ...]:
    """Writing-side graphs harvested from the committed fluency case files."""
    out: list[GraphCase] = []
    for rel in _GRAPH_CASE_GLOBS:
        path = _REPO_ROOT / rel
        if not path.exists():
            continue
        for line in path.read_text().splitlines():
            if not line.strip():
                continue
            case = json.loads(line)
            nodes = case.get("proposition_graph", {}).get("nodes", [])
            if not nodes:
                continue
            out.append(
                GraphCase(case_id=str(case.get("id", "?")), nodes=tuple(nodes))
            )
    return tuple(out)


#: The lane's own committed corpus.  Authored surfaces live HERE and only here
#: — not duplicated in module tables — because a second copy of a corpus is the
#: same defect this arc exists to remove.  The derived shuffles below are
#: generated at run time rather than committed, so they cannot drift away from
#: the positives they are derived from.
_SURFACE_CASES_PATH = Path(__file__).resolve().parent / "public" / "v1" / "cases.jsonl"

_KIND_POSITIVE = "positive_surface"
_KIND_NEGATIVE = "negative_surface"


def _load_surface_cases(kind: str) -> tuple[SurfaceCase, ...]:
    if not _SURFACE_CASES_PATH.exists():
        raise FileNotFoundError(
            f"grammar_roundtrip corpus missing: {_SURFACE_CASES_PATH}"
        )
    out: list[SurfaceCase] = []
    for line in _SURFACE_CASES_PATH.read_text().splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        if record.get("kind") != kind:
            continue
        out.append(
            SurfaceCase(
                case_id=str(record["id"]),
                surface=str(record["surface"]),
                note=str(record.get("note", "")),
            )
        )
    return tuple(out)


def positive_surface_cases() -> tuple[SurfaceCase, ...]:
    """Reading-side surfaces inside the reader's demonstrated envelope.

    Each was verified comprehensible by probe before being committed — a case
    the reader refuses belongs in a coverage note, not here, because a refusal
    would measure the reader's envelope rather than the round-trip.
    ``tests/test_grammar_roundtrip.py`` enforces that.
    """
    return _load_surface_cases(_KIND_POSITIVE)


def _shuffle_tokens(surface: str, seed: int) -> str:
    """Deterministically permute *surface*'s tokens into a non-identity order.

    Uses a fixed rotation rather than a PRNG so the corpus is byte-stable
    across runs and machines — a shuffled negative case that varies per run
    would make the lane's ``reject_rate`` irreproducible.
    """
    body = surface.rstrip(".!?")
    tokens = body.split()
    if len(tokens) < 3:
        return surface
    shift = 1 + (seed % (len(tokens) - 1))
    rotated = tokens[shift:] + tokens[:shift]
    return " ".join(rotated) + "."


def negative_surface_cases() -> tuple[SurfaceCase, ...]:
    """Word salad: hand-authored plus mechanical shuffles of the positives.

    The shuffles matter because they are *lexically identical* to positive
    cases — same vocabulary, same length, only the order destroyed.  A lane
    that rejects the hand-authored salad but accepts the shuffles is doing
    vocabulary checking, not grammar checking.
    """
    positives = positive_surface_cases()
    out = list(_load_surface_cases(_KIND_NEGATIVE))
    for i, case in enumerate(positives):
        shuffled = _shuffle_tokens(case.surface, i)
        if shuffled.rstrip(".!?").lower() == case.surface.rstrip(".!?").lower():
            continue
        out.append(
            SurfaceCase(
                case_id=f"neg-shuf-{case.case_id}",
                surface=shuffled,
                note=f"token shuffle of {case.case_id}",
            )
        )
    return tuple(out)


__all__ = (
    "GraphCase",
    "SurfaceCase",
    "negative_surface_cases",
    "positive_graph_cases",
    "positive_surface_cases",
)
