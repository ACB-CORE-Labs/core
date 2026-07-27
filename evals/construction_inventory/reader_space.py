"""The reader's construction inventory, with a structural guard against rot.

A hand-written table of "what the reader reads" is worth nothing on its own —
it drifts the first time someone adds a template, and then the overlap number
silently measures a stale list. So the table is paired with a guard keyed on
something the reader cannot add a construction without touching: a **mint
site**, one of the ``relations.append`` / ``queries.append`` calls that are the
only ways a proposition or query enters a ``Comprehension``.

Every construction below names the mint site it flows through. The guard
(``test_construction_inventory.py``) AST-scans ``reader.py``, counts mint sites,
and requires that count to equal the number of distinct sites named here — so a
new template breaks the test until it is entered in this table. That is the
``feedback-pin-registered-in-no-suite`` lesson applied one level up: a table
that cannot go stale beats a table someone promises to update.

Constructions are keyed on SHAPE, not on predicate: ``all Xs are Ys`` and ``no
Xs are Ys`` are two constructions through one mint site, because the reader
dispatches on the quantifier token and a writer must emit that token to reach
either.
"""

from __future__ import annotations

from dataclasses import dataclass

#: The reader's mint sites — the only routes into a ``Comprehension``.
#: Named, not numbered, so a diff shows which route a change touched.
MINT_RELATION_CATEGORICAL = "relations:categorical"
MINT_RELATION_MEMBER = "relations:member"
MINT_RELATION_LESS = "relations:less"
MINT_RELATION_PROPOSITIONAL = "relations:propositional"
MINT_QUERY_COMPARE = "queries:compare"
MINT_QUERY_SORT = "queries:sort"
MINT_QUERY_MEMBER = "queries:member"
MINT_QUERY_SUBSET = "queries:subset"
MINT_QUERY_THEREFORE_CATEGORICAL = "queries:therefore_categorical"
MINT_QUERY_THEREFORE_PROPOSITIONAL = "queries:therefore_propositional"


@dataclass(frozen=True, slots=True)
class ReaderConstruction:
    """One surface shape the reader claims to read, plus a canonical instance.

    ``instance`` is a template over the lane's lexical fillers, so the same
    construction is probed with several vocabularies and a morphology refusal
    shows up as filler-dependence rather than as a missing construction.
    """

    construction_id: str
    instance: str
    mint_site: str
    interrogative: bool = False


#: The inventory. Order is stable so report diffs are readable.
READER_CONSTRUCTIONS: tuple[ReaderConstruction, ...] = (
    # --- categorical facts: one mint site, four dispatch tokens -------------
    ReaderConstruction("subset_fact", "all {plural_x} are {plural_y}", MINT_RELATION_CATEGORICAL),
    ReaderConstruction("disjoint_fact", "no {plural_x} are {plural_y}", MINT_RELATION_CATEGORICAL),
    ReaderConstruction("intersects_fact", "some {plural_x} are {plural_y}", MINT_RELATION_CATEGORICAL),
    ReaderConstruction("some_not_fact", "some {plural_x} are not {plural_y}", MINT_RELATION_CATEGORICAL),
    # --- membership facts ---------------------------------------------------
    ReaderConstruction("member_fact", "{x} is a {y}", MINT_RELATION_MEMBER),
    ReaderConstruction("member_fact_definite", "the {x} is a {y}", MINT_RELATION_MEMBER),
    # --- ordering facts: one mint site, two comparator directions -----------
    ReaderConstruction("less_fact", "{x} is below {y}", MINT_RELATION_LESS),
    ReaderConstruction("greater_fact", "{x} is above {y}", MINT_RELATION_LESS),
    # --- propositional facts ------------------------------------------------
    ReaderConstruction("implies_fact", "if {p} then {q}", MINT_RELATION_PROPOSITIONAL),
    ReaderConstruction("negated_atom_fact", "not {p}", MINT_RELATION_PROPOSITIONAL),
    ReaderConstruction("or_fact", "{p} or {q}", MINT_RELATION_PROPOSITIONAL),
    ReaderConstruction("atom_fact", "{p}", MINT_RELATION_PROPOSITIONAL),
    # --- queries ------------------------------------------------------------
    ReaderConstruction("member_query", "is {x} a {y}?", MINT_QUERY_MEMBER, interrogative=True),
    ReaderConstruction("subset_query", "are all {plural_x} {plural_y}?", MINT_QUERY_SUBSET, interrogative=True),
    ReaderConstruction("compare_query", "compare {x} with {y}", MINT_QUERY_COMPARE),
    ReaderConstruction("sort_query", "sort ascending", MINT_QUERY_SORT),
    ReaderConstruction("sort_range_query", "order from lowest to highest", MINT_QUERY_SORT),
    ReaderConstruction(
        "therefore_categorical", "therefore all {plural_x} are {plural_y}",
        MINT_QUERY_THEREFORE_CATEGORICAL,
    ),
    ReaderConstruction(
        "therefore_propositional", "therefore {q}", MINT_QUERY_THEREFORE_PROPOSITIONAL,
    ),
)

#: Distinct mint sites named above — the quantity the AST guard checks.
READER_MINT_SITES: frozenset[str] = frozenset(c.mint_site for c in READER_CONSTRUCTIONS)


def render_instance(construction: ReaderConstruction, filler: "LexicalFiller") -> str:
    """Instantiate a construction's canonical surface with *filler*'s vocabulary."""
    return construction.instance.format(
        x=filler.x, y=filler.y,
        plural_x=filler.plural_x, plural_y=filler.plural_y,
        p=filler.p, q=filler.q,
    )


@dataclass(frozen=True, slots=True)
class LexicalFiller:
    """One vocabulary for probing constructions.

    Held separate from the constructions so that a refusal caused by *morphology*
    (an unrecognized plural) is distinguishable from a refusal caused by the
    *construction*. A construction counts as readable only when every filler
    agrees; disagreement is reported as ``filler_dependent`` rather than being
    averaged away.
    """

    name: str
    x: str
    y: str
    plural_x: str
    plural_y: str
    p: str
    q: str


__all__ = (
    "LexicalFiller",
    "READER_CONSTRUCTIONS",
    "READER_MINT_SITES",
    "ReaderConstruction",
    "render_instance",
)
