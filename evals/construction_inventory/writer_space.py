"""The writer's construction space, enumerated from live source.

Every axis below is pulled from the table or enum the writer actually consults,
so the space grows the moment the writer grows. Nothing here is a hand-copied
list of what the writer "can say" — that is the failure mode this lane exists to
avoid, and the reason ``docs/plans/grammar-unification-2026-07-26.md`` §6 could
report a rate without knowing what the rate was about.

Two axes cannot be read off a table because the writer does not keep one:

* **quantifier** — ``render_step`` accepts any string. ``PLURAL_QUANTIFIERS`` is
  authoritative for the plural half; the singular determiners are a *probe set*,
  labelled as such, not an inventory claim.
* **tense / aspect** — these are literals in ``_inflect_predicate``'s ``match``
  arms. They are declared here for readability and pinned against the source by
  ``test_construction_inventory.py``, which AST-scans those arms and fails if a
  value appears there and not here.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import Iterator

from generate.graph_planner import RhetoricalMove
from generate.intent import IntentTag
from generate.lexicon import PLURAL_QUANTIFIERS, PREDICATE_DISPLAY, PREDICATIVE_NOMINAL
from generate.semantic_templates import render_semantic
from generate.templates import render_step

#: Every predicate the writer can humanize. ``PREDICATIVE_NOMINAL`` contributes
#: ``is_a``, which has no ``PREDICATE_DISPLAY`` entry (it humanizes by the
#: underscore rule) and is the *only* predicate that reaches the reader's
#: membership template, so omitting it would erase the overlap being measured.
WRITER_PREDICATES: tuple[str, ...] = tuple(
    sorted(set(PREDICATE_DISPLAY) | set(PREDICATIVE_NOMINAL))
)

#: Singular determiners — a probe, not an inventory (see module docstring).
SINGULAR_DETERMINER_PROBES: tuple[str, ...] = ("the", "every", "each", "a")

WRITER_QUANTIFIERS: tuple[str | None, ...] = (
    None,
    *sorted(PLURAL_QUANTIFIERS),
    *SINGULAR_DETERMINER_PROBES,
)

#: Pinned against ``_inflect_predicate``'s match arms by AST scan.
WRITER_TENSES: tuple[str | None, ...] = (None, "past", "future")
WRITER_ASPECTS: tuple[str | None, ...] = (None, "perfective", "imperfective")


@dataclass(frozen=True, slots=True)
class WriterCell:
    """One point in the writer's parameter space, and the surface it emits."""

    entry: str
    surface: str
    negated: bool
    predicate: str
    quantifier: str | None
    label: str


def _step_cells(subject: str, obj: str) -> Iterator[WriterCell]:
    for move, predicate, negated, quant, tense, aspect in itertools.product(
        tuple(RhetoricalMove),
        WRITER_PREDICATES,
        (False, True),
        WRITER_QUANTIFIERS,
        WRITER_TENSES,
        WRITER_ASPECTS,
    ):
        surface = render_step(
            move, subject, predicate, obj,
            negated=negated, quantifier=quant, tense=tense, aspect=aspect,
        )
        yield WriterCell(
            entry="render_step",
            surface=surface,
            negated=negated,
            predicate=predicate,
            quantifier=quant,
            label=f"{move.name}/{predicate}/neg={negated}/q={quant}/{tense}/{aspect}",
        )


def _semantic_cells(subject: str, obj: str, secondary: str) -> Iterator[WriterCell]:
    for intent, predicate, negated in itertools.product(
        tuple(IntentTag), WRITER_PREDICATES, (False, True)
    ):
        surface = render_semantic(
            intent, subject, predicate, obj, secondary=secondary, negated=negated,
        )
        yield WriterCell(
            entry="render_semantic",
            surface=surface,
            negated=negated,
            predicate=predicate,
            quantifier=None,
            label=f"{intent.name}/{predicate}/neg={negated}",
        )


def writer_cells(subject: str, obj: str, secondary: str) -> Iterator[WriterCell]:
    """Every surface the writer emits for one lexical filler triple.

    Both public entry points are swept. ``render_semantic`` is the **serving**
    writer (``core/cognition/pipeline.py``); ``render_step`` is the clause owner
    it delegates to and is also reached directly by the eval-only
    ``realize_target``. Measuring only the serving entry would understate the
    grammar's reach; measuring only the clause owner would overstate what ships.
    The lane reports both and keeps ``entry`` on every cell.
    """
    yield from _step_cells(subject, obj)
    yield from _semantic_cells(subject, obj, secondary)


__all__ = (
    "SINGULAR_DETERMINER_PROBES",
    "WRITER_ASPECTS",
    "WRITER_PREDICATES",
    "WRITER_QUANTIFIERS",
    "WRITER_TENSES",
    "WriterCell",
    "writer_cells",
)
