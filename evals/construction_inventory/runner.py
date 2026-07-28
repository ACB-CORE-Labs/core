"""Construction-inventory eval lane.

Sizes Phase 5 by measuring the reader's construction set against the writer's,
in both directions, on the criterion that matters: **faithfulness, not
acceptance**.

Why acceptance is the wrong criterion
-------------------------------------
``grammar_roundtrip`` reports ``g_read_rate`` alongside ``g_args_rate`` for
exactly this reason, and the two disagree: on ``main`` the G-direction reads
1 of 293 surfaces and recovers **0** argument pairs. The single surface that
"reads" is ``all molecules are defined as compounds``, which the reader accepts
as ``subset(molecule, defined_as_compound)`` — a class it invented from the
writer's verb phrase. Counting that as overlap would have Phase 5 growing an
inventory toward a number that rewards mis-reading.

So this lane splits acceptance three ways:

``faithful``
    the reader recovered the proposition the writer emitted, and minted nothing
    else. This is the only bucket that counts as overlap.
``fabricating``
    the reader accepted the surface and minted at least one argument the writer
    never wrote. This is a ``wrong=0`` hazard on a serving path
    (``chat/runtime.py`` realizes declarative turns into the held self;
    ``chat/deduction_surface.py`` recites premises back to the user), and it is
    ratcheted **downward**.
``refused``
    the honest outcome — the reader has no template and says so.

Framework contract: ``run_lane(cases, config=None) -> LaneReport``.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Any

from generate.meaning_graph.reader import Refusal, comprehend

from evals.construction_inventory.corpora import (
    COUNT_FILLERS,
    MASS_FILLER,
    SECONDARY,
)
from evals.construction_inventory.reader_space import (
    READER_CONSTRUCTIONS,
    LexicalFiller,
    render_instance,
)
from evals.construction_inventory.skeleton import skeleton
from evals.construction_inventory.writer_space import writer_cells

@dataclass(frozen=True, slots=True)
class LaneReport:
    metrics: dict[str, Any] = field(default_factory=dict)
    case_details: list[dict[str, Any]] = field(default_factory=list)


FAITHFUL = "faithful"
FABRICATING = "fabricating"
REFUSED = "refused"


@dataclass(frozen=True, slots=True)
class Verdict:
    """What the reader did with one writer construction."""

    bucket: str
    detail: str


def _classify(surface: str, filler: LexicalFiller, secondary: str) -> Verdict:
    """Read *surface* back and decide whether the reading is faithful.

    The writer emitted a proposition over ``{x, y}`` (or ``{x, secondary}`` for
    the frame intents). Any argument outside that set is something the reader
    invented — a discourse connective promoted to a proposition, a verb phrase
    chunked into a class, a determiner glued onto an entity. Any *query* is also
    invention: the writer never emits an interrogative, so a question can only
    have been manufactured.
    """
    reading = comprehend(surface)
    if isinstance(reading, Refusal):
        return Verdict(REFUSED, reading.reason)

    permitted = {filler.x, filler.y, secondary}
    relations = reading.meaning_graph.relations

    if reading.queries:
        minted = ",".join(q.predicate for q in reading.queries)
        return Verdict(FABRICATING, f"query_from_declarative:{minted}")

    invented = sorted(
        {arg for rel in relations for arg in rel.arguments if arg not in permitted}
    )
    if invented:
        return Verdict(FABRICATING, f"invented_args:{'|'.join(invented)}")

    recovered = any(
        tuple(rel.arguments) in ((filler.x, filler.y), (filler.x, secondary))
        for rel in relations
    )
    if not recovered:
        return Verdict(FABRICATING, "proposition_lost")
    return Verdict(FAITHFUL, ",".join(sorted({r.predicate for r in relations})))


def _sweep_filler(filler: LexicalFiller) -> dict[str, Any]:
    """Sweep the whole writer space under one vocabulary."""
    secondary = SECONDARY[filler.name]
    by_skeleton: dict[str, str] = {}
    cells_per_skeleton: Counter[str] = Counter()
    # Negation sentinel (ADR-0265): key each parameter point WITHOUT its polarity
    # so the two polarities land in one bucket. A point whose negated surface is
    # byte-identical to its affirmative is a proposition served as its own denial.
    polarity: dict[str, dict[bool, str]] = {}
    n_cells = 0

    for cell in writer_cells(filler.x, filler.y, secondary):
        n_cells += 1
        sk = skeleton(cell.surface)
        by_skeleton.setdefault(sk, cell.surface)
        cells_per_skeleton[sk] += 1
        point = f"{cell.entry}|{cell.label.replace('neg=True', '').replace('neg=False', '')}"
        polarity.setdefault(point, {})[cell.negated] = cell.surface

    negation_collapsed = sorted(
        point for point, both in polarity.items()
        if len(both) == 2 and both[True] == both[False]
    )

    verdicts = {sk: _classify(s, filler, secondary) for sk, s in by_skeleton.items()}
    return {
        "filler": filler.name,
        "cells": n_cells,
        "skeletons": by_skeleton,
        "cells_per_skeleton": cells_per_skeleton,
        "verdicts": verdicts,
        "negation_collapsed": negation_collapsed,
    }


def _reader_direction(writer_skeletons: frozenset[str]) -> dict[str, Any]:
    """Which of the reader's constructions can the writer emit at all?"""
    rows = []
    for construction in READER_CONSTRUCTIONS:
        instance = render_instance(construction, COUNT_FILLERS[0])
        sk = skeleton(instance)
        reading = comprehend(instance)
        rows.append({
            "construction_id": construction.construction_id,
            "mint_site": construction.mint_site,
            "instance": instance,
            "skeleton": sk,
            "writer_can_emit": sk in writer_skeletons,
            "reader_reads_own": not isinstance(reading, Refusal),
            "interrogative": construction.interrogative,
        })
    return {"rows": rows}


def _rate(num: int, den: int) -> float:
    return round(num / den, 6) if den else 0.0


def run_lane(cases: Any = None, config: Any = None) -> LaneReport:  # noqa: ARG001
    """Measure the two construction inventories against each other."""
    sweeps = [_sweep_filler(f) for f in COUNT_FILLERS]
    mass = _sweep_filler(MASS_FILLER)

    # A construction is shared only if EVERY count-noun filler agrees it is.
    per_filler_faithful = [
        {sk for sk, v in s["verdicts"].items() if v.bucket == FAITHFUL} for s in sweeps
    ]
    per_filler_fabricating = [
        {sk for sk, v in s["verdicts"].items() if v.bucket == FABRICATING} for s in sweeps
    ]
    faithful_all = set.intersection(*per_filler_faithful)
    faithful_any = set.union(*per_filler_faithful)
    fabricating_any = set.union(*per_filler_fabricating)
    filler_dependent = faithful_any - faithful_all

    base = sweeps[0]
    all_skeletons = frozenset(base["skeletons"])
    reader_dir = _reader_direction(frozenset().union(*(frozenset(s["skeletons"]) for s in sweeps)))

    n_constructions = len(all_skeletons)
    refusal_census = Counter(
        v.detail for v in base["verdicts"].values() if v.bucket == REFUSED
    )
    fabrication_census = Counter(
        v.detail.split(":")[0] for v in base["verdicts"].values() if v.bucket == FABRICATING
    )

    cells_fabricating = sum(
        base["cells_per_skeleton"][sk] for sk in fabricating_any if sk in base["cells_per_skeleton"]
    )
    cells_faithful = sum(
        base["cells_per_skeleton"][sk] for sk in faithful_all if sk in base["cells_per_skeleton"]
    )

    reader_rows = reader_dir["rows"]
    expressible = [r for r in reader_rows if r["writer_can_emit"]]
    unreadable_own = [r for r in reader_rows if not r["reader_reads_own"]]
    interrogative = [r for r in reader_rows if r["interrogative"]]

    metrics: dict[str, Any] = {
        # --- W -> R: the writer's space, judged by the reader ---------------
        "writer_cells": base["cells"],
        "writer_constructions": n_constructions,
        "w2r_faithful": len(faithful_all),
        "w2r_fabricating": len(fabricating_any),
        "w2r_refused": n_constructions - len(faithful_any) - len(fabricating_any),
        "w2r_filler_dependent": len(filler_dependent),
        "w2r_faithful_rate": _rate(len(faithful_all), n_constructions),
        "w2r_fabricating_rate": _rate(len(fabricating_any), n_constructions),
        "cells_faithful": cells_faithful,
        "cells_fabricating": cells_fabricating,
        # --- R -> W: the reader's inventory, judged by the writer ------------
        "reader_constructions": len(reader_rows),
        "r2w_expressible": len(expressible),
        "r2w_rate": _rate(len(expressible), len(reader_rows)),
        "reader_constructions_unreadable_by_reader": len(unreadable_own),
        "reader_interrogative_constructions": len(interrogative),
        # --- the headline -----------------------------------------------------
        "overlap_constructions": len(faithful_all),
        # --- sentinels --------------------------------------------------------
        "negation_collapsed_points": len(base["negation_collapsed"]),
        "mass_noun_faithful": len(
            [1 for v in mass["verdicts"].values() if v.bucket == FAITHFUL]
        ),
    }

    details: list[dict[str, Any]] = [
        {
            "kind": "writer_construction",
            "skeleton": sk,
            "example": base["skeletons"][sk],
            "cells": base["cells_per_skeleton"][sk],
            "bucket": base["verdicts"][sk].bucket,
            "detail": base["verdicts"][sk].detail,
            "shared_by_all_fillers": sk in faithful_all,
        }
        for sk in sorted(all_skeletons, key=lambda s: -base["cells_per_skeleton"][s])
    ]
    details.extend({"kind": "reader_construction", **row} for row in reader_rows)
    details.append({"kind": "refusal_census", **dict(refusal_census)})
    details.append({"kind": "fabrication_census", **dict(fabrication_census)})

    return LaneReport(metrics=metrics, case_details=details)


__all__ = ("FABRICATING", "FAITHFUL", "REFUSED", "LaneReport", "Verdict", "run_lane")
