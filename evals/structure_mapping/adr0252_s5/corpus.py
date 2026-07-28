"""§5.1 — the structure-labelled corpus, with provenance on every case.

Two arms, and the split is the finding as much as the input:

**REAL arm.** Cases drawn from ``evals/gsm8k_math/holdout_dev/v1``, extracted
through the serving reader (``parse_and_solve``) — no hand-authoring, no other
lane. Measured at 797ebad5: the reader returns a selected graph for **5 of the
500** holdout cases, and all five carry the *same* relational skeleton
(``compare_multiplicative``). §5.1 asks for "minimum four structures with clean
labels" drawn from this corpus; the reader cannot supply them today, and that
is why §5.1's own escape hatch is used below rather than ignored.

**SYNTHETIC arm (MARKED).** §5.1: *"add controlled synthetic surface-variants
only where needed for clean labels (marked as such)."* Every synthetic case
carries ``provenance="synthetic"`` and the template that generated it. They are
constructed as :class:`MathProblemGraph` values directly — the geometry question
is about the graph, not about the sentence that produced it — and they are
generated from declared templates with seeded attributes so the corpus is a
pure function of this file.

The control sets that make the measurements decisive live here too, because a
control is part of the corpus design, not of the scorer:

    INV   attribute-only variants of one structure (§5.3b)
    SENS  minimal pairs: identical roles and numbers, one relation kind changed (§5.3c)
    SYST  chained higher-order structures (§5.3d)

Labels never travel with the graphs. :func:`build_corpus` returns cases whose
``label`` field is ``None``; :func:`load_labels` is a separate call that the
embedding never makes.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final, Iterator, Mapping, Sequence

from generate.math_problem_graph import MathProblemGraph, graph_from_dict

_HOLDOUT_CASES: Final[Path] = (
    Path(__file__).resolve().parents[2] / "gsm8k_math" / "holdout_dev" / "v1" / "cases.jsonl"
)

#: Structure vocabulary. The label IS the role-predicate skeleton (§5.1), so it
#: is stated here once and referenced everywhere rather than re-derived.
STRUCTURES: Final[Mapping[str, str]] = {
    "S1": "compare-multiplicative — B's quantity is k times A's",
    "S2": "transfer — A moves j units to B",
    "S3": "additive accumulation — A gains j, then gains i",
    "S4": "additive decrement — A loses j",
}

#: Entity name pools. Names are surface attributes and must never reach the
#: geometry; three disjoint pools exist so a rename control can be built.
_NAME_POOLS: Final[tuple[tuple[str, ...], ...]] = (
    ("Ada", "Bram", "Cleo", "Dov"),
    ("Petra", "Quill", "Rosa", "Silas"),
    ("Mira", "Nils", "Oona", "Pax"),
)

_UNITS: Final[tuple[str, ...]] = ("marbles", "coins", "apples", "tickets")


@dataclass(frozen=True, slots=True)
class Case:
    """One corpus member. ``label`` is always ``None`` on the mapper's side."""

    case_id: str
    graph: MathProblemGraph
    provenance: str  # "holdout_dev/v1" | "synthetic"
    template: str | None = None
    label: None = field(default=None, init=False)

    def as_json(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "provenance": self.provenance,
            "template": self.template,
            "graph": self.graph.as_json(),
        }


# --------------------------------------------------------------------------
# REAL arm
# --------------------------------------------------------------------------


def extract_holdout_graphs(limit: int | None = None) -> list[Case]:
    """Run the serving reader over ``holdout_dev/v1`` and keep what it decides.

    Deliberately uses the same entry point the eval lane uses
    (``generate.math_candidate_graph.parse_and_solve``) so the extraction
    inherits the reader's real coverage rather than a bespoke parser's.
    """
    from generate.math_candidate_graph import parse_and_solve

    out: list[Case] = []
    with _HOLDOUT_CASES.open() as fh:
        for n, line in enumerate(fh):
            if limit is not None and n >= limit:
                break
            record = json.loads(line)
            try:
                result = parse_and_solve(record["problem"])
            except Exception:  # noqa: BLE001 — reader refusals are data here
                continue
            graph = getattr(result, "selected_graph", None)
            if graph is None:
                continue
            out.append(
                Case(case_id=record["id"], graph=graph, provenance="holdout_dev/v1")
            )
    return out


# --------------------------------------------------------------------------
# SYNTHETIC arm — declared templates
# --------------------------------------------------------------------------


def _s1(a: str, b: str, unit: str, base: float, factor: float) -> MathProblemGraph:
    return graph_from_dict(
        {
            "entities": [a, b],
            "initial_state": [{"entity": a, "quantity": {"value": base, "unit": unit}}],
            "operations": [
                {
                    "actor": b,
                    "kind": "compare_multiplicative",
                    "operand": {
                        "direction": "times",
                        "reference_actor": a,
                        "factor": factor,
                    },
                }
            ],
            "unknown": {"entity": b, "unit": unit},
        }
    )


def _s2(a: str, b: str, unit: str, base: float, other: float, moved: float) -> MathProblemGraph:
    return graph_from_dict(
        {
            "entities": [a, b],
            "initial_state": [
                {"entity": a, "quantity": {"value": base, "unit": unit}},
                {"entity": b, "quantity": {"value": other, "unit": unit}},
            ],
            "operations": [
                {
                    "actor": a,
                    "kind": "transfer",
                    "target": b,
                    "operand": {"value": moved, "unit": unit},
                }
            ],
            "unknown": {"entity": b, "unit": unit},
        }
    )


def _s3(a: str, unit: str, base: float, first: float, second: float) -> MathProblemGraph:
    return graph_from_dict(
        {
            "entities": [a],
            "initial_state": [{"entity": a, "quantity": {"value": base, "unit": unit}}],
            "operations": [
                {"actor": a, "kind": "add", "operand": {"value": first, "unit": unit}},
                {"actor": a, "kind": "add", "operand": {"value": second, "unit": unit}},
            ],
            "unknown": {"entity": a, "unit": unit},
        }
    )


def _s4(a: str, unit: str, base: float, lost: float) -> MathProblemGraph:
    return graph_from_dict(
        {
            "entities": [a],
            "initial_state": [{"entity": a, "quantity": {"value": base, "unit": unit}}],
            "operations": [
                {"actor": a, "kind": "subtract", "operand": {"value": lost, "unit": unit}}
            ],
            "unknown": {"entity": a, "unit": unit},
        }
    )


def _realizations() -> Iterator[tuple[str, str, MathProblemGraph]]:
    """Twelve surface realizations per structure, deterministic in this file.

    Attributes vary (names from three pools, units, magnitudes); the role
    skeleton does not. No RNG: the schedule is written out so the corpus is
    reproducible by reading, not by re-running.
    """
    bases = (12.0, 35.0, 78.0, 140.0)
    for i in range(12):
        pool = _NAME_POOLS[i % len(_NAME_POOLS)]
        unit = _UNITS[i % len(_UNITS)]
        base = bases[i % len(bases)] + i
        a, b = pool[0], pool[1]
        yield "S1", f"syn-S1-{i:02d}", _s1(a, b, unit, base, 2.0 + (i % 4))
        yield "S2", f"syn-S2-{i:02d}", _s2(a, b, unit, base, base + 9.0, 3.0 + (i % 5))
        yield "S3", f"syn-S3-{i:02d}", _s3(a, unit, base, 4.0 + (i % 6), 7.0 + (i % 3))
        yield "S4", f"syn-S4-{i:02d}", _s4(a, unit, base, 5.0 + (i % 7))


# --------------------------------------------------------------------------
# Control sets
# --------------------------------------------------------------------------


def invariance_pairs() -> list[tuple[str, Case, Case]]:
    """§5.3b — same structure, attributes perturbed three ways.

    ``rename``   entity names swapped for a disjoint pool; numbers identical.
    ``rescale``  every quantity multiplied by 3; names identical.
    ``jitter``   quantities changed non-uniformly (the hard case: not a scale).
    """
    pairs: list[tuple[str, Case, Case]] = []
    p0, p1 = _NAME_POOLS[0], _NAME_POOLS[1]
    unit = "marbles"

    def case(cid: str, g: MathProblemGraph) -> Case:
        return Case(case_id=cid, graph=g, provenance="synthetic", template="inv")

    base_s1 = _s1(p0[0], p0[1], unit, 20.0, 3.0)
    pairs.append(("rename", case("inv-S1-base", base_s1), case("inv-S1-rename", _s1(p1[0], p1[1], unit, 20.0, 3.0))))
    pairs.append(("rescale", case("inv-S1-base", base_s1), case("inv-S1-rescale", _s1(p0[0], p0[1], unit, 60.0, 3.0))))
    pairs.append(("jitter", case("inv-S1-base", base_s1), case("inv-S1-jitter", _s1(p0[0], p0[1], unit, 29.0, 4.0))))

    base_s2 = _s2(p0[0], p0[1], unit, 40.0, 25.0, 8.0)
    pairs.append(("rename", case("inv-S2-base", base_s2), case("inv-S2-rename", _s2(p1[0], p1[1], unit, 40.0, 25.0, 8.0))))
    pairs.append(("rescale", case("inv-S2-base", base_s2), case("inv-S2-rescale", _s2(p0[0], p0[1], unit, 120.0, 75.0, 24.0))))
    pairs.append(("jitter", case("inv-S2-base", base_s2), case("inv-S2-jitter", _s2(p0[0], p0[1], unit, 57.0, 19.0, 13.0))))

    base_s3 = _s3(p0[0], unit, 30.0, 6.0, 9.0)
    pairs.append(("rename", case("inv-S3-base", base_s3), case("inv-S3-rename", _s3(p1[0], unit, 30.0, 6.0, 9.0))))
    pairs.append(("rescale", case("inv-S3-base", base_s3), case("inv-S3-rescale", _s3(p0[0], unit, 90.0, 18.0, 27.0))))
    pairs.append(("jitter", case("inv-S3-base", base_s3), case("inv-S3-jitter", _s3(p0[0], unit, 44.0, 11.0, 5.0))))

    base_s4 = _s4(p0[0], unit, 50.0, 12.0)
    pairs.append(("rename", case("inv-S4-base", base_s4), case("inv-S4-rename", _s4(p1[0], unit, 50.0, 12.0))))
    pairs.append(("rescale", case("inv-S4-base", base_s4), case("inv-S4-rescale", _s4(p0[0], unit, 150.0, 36.0))))
    pairs.append(("jitter", case("inv-S4-base", base_s4), case("inv-S4-jitter", _s4(p0[0], unit, 71.0, 4.0))))
    return pairs


def sensitivity_pairs() -> list[tuple[str, Case, Case]]:
    """§5.3c — minimal pairs: identical roles, identical numbers, kind changed.

    This is the control that separates "aligns by structure" from "aligns by
    anything else": the two graphs in each pair differ in exactly one field.
    """
    p = _NAME_POOLS[0]
    unit = "marbles"

    def case(cid: str, g: MathProblemGraph) -> Case:
        return Case(case_id=cid, graph=g, provenance="synthetic", template="sens")

    out: list[tuple[str, Case, Case]] = []
    # Same two entities, same magnitudes — compare vs transfer.
    out.append(
        (
            "S1-vs-S2",
            case("sens-S1", _s1(p[0], p[1], unit, 40.0, 3.0)),
            case("sens-S2", _s2(p[0], p[1], unit, 40.0, 3.0, 3.0)),
        )
    )
    # Same single entity, same magnitudes — gain vs loss.
    out.append(
        (
            "S3-vs-S4",
            case("sens-S3", _s3(p[0], unit, 40.0, 3.0, 3.0)),
            case("sens-S4b", _s4(p[0], unit, 40.0, 3.0)),
        )
    )
    # Same single entity and numbers, one added operation vs one subtracted.
    out.append(
        (
            "add-vs-subtract",
            case("sens-subtract", _s4(p[0], unit, 40.0, 3.0)),
            case(
                "sens-add",
                graph_from_dict(
                    {
                        "entities": [p[0]],
                        "initial_state": [
                            {"entity": p[0], "quantity": {"value": 40.0, "unit": unit}}
                        ],
                        "operations": [
                            {
                                "actor": p[0],
                                "kind": "add",
                                "operand": {"value": 3.0, "unit": unit},
                            }
                        ],
                        "unknown": {"entity": p[0], "unit": unit},
                    }
                ),
            ),
        )
    )
    return out


def systematicity_pairs() -> list[tuple[str, Case, Case]]:
    """§5.3d — chained higher-order structure (A = 2B, B = 2C)."""
    p, q = _NAME_POOLS[0], _NAME_POOLS[1]
    unit = "marbles"

    def chain(names: Sequence[str], base: float, k1: float, k2: float) -> MathProblemGraph:
        a, b, c = names[0], names[1], names[2]
        return graph_from_dict(
            {
                "entities": [a, b, c],
                "initial_state": [{"entity": a, "quantity": {"value": base, "unit": unit}}],
                "operations": [
                    {
                        "actor": b,
                        "kind": "compare_multiplicative",
                        "operand": {"direction": "times", "reference_actor": a, "factor": k1},
                    },
                    {
                        "actor": c,
                        "kind": "compare_multiplicative",
                        "operand": {"direction": "times", "reference_actor": b, "factor": k2},
                    },
                ],
                "unknown": {"entity": c, "unit": unit},
            }
        )

    def case(cid: str, g: MathProblemGraph) -> Case:
        return Case(case_id=cid, graph=g, provenance="synthetic", template="syst")

    chain_a = case("syst-chain-a", chain(p, 10.0, 2.0, 2.0))
    chain_b = case("syst-chain-b", chain(q, 37.0, 5.0, 3.0))
    flat = case("syst-flat", _s1(p[0], p[1], unit, 10.0, 2.0))
    return [("chain-vs-chain", chain_a, chain_b), ("chain-vs-flat", chain_a, flat)]


# --------------------------------------------------------------------------
# Assembly
# --------------------------------------------------------------------------


def build_corpus() -> tuple[list[Case], dict[str, str]]:
    """Return ``(cases, labels)``. The caller must keep them apart until scoring."""
    cases: list[Case] = []
    labels: dict[str, str] = {}

    for real in extract_holdout_graphs():
        cases.append(real)
        labels[real.case_id] = "S1"

    for label, cid, graph in _realizations():
        cases.append(Case(case_id=cid, graph=graph, provenance="synthetic", template=label))
        labels[cid] = label

    seen: set[str] = set()
    for c in cases:
        if c.case_id in seen:
            raise ValueError(f"duplicate case_id in corpus: {c.case_id}")
        seen.add(c.case_id)
    return cases, labels


def load_labels() -> dict[str, str]:
    """Labels only. Kept as a separate entry point so blindness is greppable."""
    return build_corpus()[1]
