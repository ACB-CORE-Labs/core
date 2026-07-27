"""Single source of truth for CORE's closed English lexical tables.

Before this module the same linguistic facts were encoded up to five times
across the reading and writing paths, each copy written independently as a
successive deduction band landed. Measured on ``main`` @ ``0948f7cd``:
35 word-tables on the reading path vs 9 on the writing path, sharing 43 of
518 distinct words (Jaccard 0.083).

Every table here is **closed** — a finite enumeration, not a rule. Where two
call sites need different content, this module defines one literal and
*derives* the other, so a divergence is stated once and cannot drift.

Naming convention: a name is the linguistic fact, not the consumer. When a
consumer needs a narrower view, the narrow name says whose view it is
(``STRUCTURAL``, ``READER_SINGULAR_KEYS``).

**Deliberate non-goal:** this module does not decide anything. It holds
tables and derivations; the refusal/agreement logic stays with each band.
Consumers and their serving status are recorded in
``tests/test_lexicon_single_source.py``, which fails when a new consumer
appears. Phase 2A of ``docs/plans/grammar-unification-2026-07-26.md``.

**This module is a staging area, not the final home.** ADR-0258 §5 already
decided where number morphology belongs:

    the number-linking table is CORE's first morphology table, and it is
    exactly the artifact class the tri-language doctrine says must
    eventually enter through pack ratification (ADR-0253). [...] When a
    ``grc_*``/``he_*`` member band is built, the table moves from module
    constants to a ratified pack; no premature parameterization now.

That trigger has **not** fired — ``packs/{grc,he,el}/`` exist, but no
``grc``/``he`` member band does, so the promotion is correctly deferred and
this module does not pre-empt it. Consolidating five disagreeing copies into
one is a prerequisite for promotion either way: you cannot ratify a fact as
a pack row while the tree holds several answers to it.

Measured state of the destination, for whoever picks the promotion up:
``packs/en/morphology.jsonl`` holds **9 records** (7 forms of *be*, plus
``word``/``beginning`` — both regular plurals, present to support John 1:1),
so **no irregular English plural exists as pack data**. Neither end of the
pipe is connected: ``features.number`` has no consumer anywhere, and the only
code that opens ``morphology.jsonl``
(``chat/pack_resolver.py::_pack_morph_roots_for``) extracts a top-level
``root`` key that **0 of 31 records across all four packs** define, so it
returns ``{}`` every call.
"""

from __future__ import annotations

from typing import Final

# --------------------------------------------------------------------------
# Connectives
# --------------------------------------------------------------------------

#: Connective structure the member/verb/conditional bands do not compose.
#: Was three byte-identical copies: ``proof_chain/member.py::_CONNECTIVES``,
#: ``proof_chain/verb.py::_CONNECTIVES``,
#: ``proof_chain/cond_member.py::_CONNECTIVE_TOKENS``.
CONNECTIVES: Final[frozenset[str]] = frozenset({"if", "then", "or", "and", "either"})

#: The v2-EN band's structural-function-word set. Identical to
#: :data:`CONNECTIVES` plus ``therefore`` — that band consumes ``therefore``
#: as the conclusion marker, so a leftover one signals an unconsumed parse.
#: Derived, not duplicated: the two sets can no longer drift apart.
STRUCTURAL: Final[frozenset[str]] = CONNECTIVES | {"therefore"}

# --------------------------------------------------------------------------
# Copulas and negation
# --------------------------------------------------------------------------

#: The finite forms of *be* that CORE recognizes, in canonical order.
#:
#: **One inventory, four roles.** This was four separate literals — a copula
#: set (``english.py``), a copula tuple (``member.py``), an auxiliary set for
#: negation lookahead (``realizer_guard.py::_BE_AUX``), and an auxiliary set
#: for prompt-anchor filtering (``chat/runtime.py::_BE_FORMS``). Copula and
#: auxiliary are different syntactic *roles*, but the token inventory is one
#: fact, and all four copies held the same four words. The role views below
#: are derived, so a fifth role cannot introduce a fifth answer.
#:
#: Known-incomplete: ``am``, ``be``, ``been``, ``being`` are absent from all
#: four original copies and remain absent here — widening the inventory
#: changes what every consumer recognizes, so it is not a 2A change.
#: ``packs/en/morphology.jsonl`` already carries ``am`` as
#: ``en:be:present:1sg``, which is one reason the eventual home for this fact
#: is the pack rather than this module.
BE_FINITE_FORMS: Final[tuple[str, ...]] = ("is", "are", "was", "were")

#: Set view of :data:`BE_FINITE_FORMS` for membership tests.
BE_FINITE: Final[frozenset[str]] = frozenset(BE_FINITE_FORMS)

#: Copular role view, ordered. ``proof_chain/member.py`` relies on ordered
#: iteration for dispatch, so this stays a tuple.
COPULA_FORMS: Final[tuple[str, ...]] = BE_FINITE_FORMS

#: Copular role view, as a set.
COPULAS: Final[frozenset[str]] = BE_FINITE

#: The "it is not the case that <X>" sentential-negation prefix. Was two
#: byte-identical copies (``english.py``, ``member.py``).
SENTENTIAL_NOT: Final[tuple[str, ...]] = ("it", "is", "not", "the", "case", "that")

#: Negation-bearing tokens a band cannot normalize away. Leaving one inside
#: an opaque atom would hide a negation from the engine, so the bands refuse.
NEGATION_BEARING: Final[frozenset[str]] = frozenset(
    {"never", "cannot", "nor", "neither", "nothing", "none", "no"}
)

#: :data:`NEGATION_BEARING` plus bare ``not``.
#:
#: **Recorded divergence (Phase 2A decision).** ``english.py`` (v2-EN) uses
#: the 7-token set and ``member.py`` (v3-MEM) uses this 8-token one. The
#: difference is not an oversight: v2-EN normalizes ``<copula> not`` into
#: ``~atom`` and so must let ``not`` through to that rule, while v3-MEM
#: normalizes only the copular slot and the sentential prefix and refuses
#: every other ``not``.
#:
#: Both bands serve, so **unifying them changes what CORE refuses** and is
#: deferred to Phase 2B under the authorization gate. Deriving the larger
#: set from the smaller removes the duplication now without changing any
#: behaviour, which is the whole point of the 2A/2B split.
NEGATION_BEARING_WITH_NOT: Final[frozenset[str]] = NEGATION_BEARING | {"not"}

# --------------------------------------------------------------------------
# Quantifiers — three distinct facts, previously conflated
# --------------------------------------------------------------------------

#: Quantifiers that can *lead* a clause, making it categorical
#: ("all whales are mammals"). Used to detect internal structure a band
#: must not flatten.
QUANTIFIER_LEAD: Final[frozenset[str]] = frozenset(
    {"all", "every", "each", "no", "some", "none", "any", "most"}
)

#: What ``member.py`` recognizes beyond :data:`QUANTIFIER_LEAD`.
#:
#: This is a **provenance grouping, not a linguistic category** — it mixes
#: determiners (``few``, ``many``, ``both``) with pronouns (``everyone``,
#: ``nothing``). It is named for what it is (the delta) rather than given a
#: category name it would not earn. Splitting it into real categories needs
#: a linguistic decision, not a refactor.
QUANTIFIER_NON_LEAD: Final[frozenset[str]] = frozenset(
    {
        "few", "many", "several", "both", "either", "neither",
        "everyone", "everybody", "everything",
        "someone", "somebody", "something",
        "anyone", "anybody", "anything",
        "nobody", "nothing",
    }
)

#: Every quantifier token ``member.py`` refuses to lower. Measured to be a
#: strict superset of :data:`QUANTIFIER_LEAD`, so it is derived rather than
#: re-listed: the two sets agreed on all 8 shared tokens and can no longer
#: disagree.
QUANTIFIER_TOKENS: Final[frozenset[str]] = QUANTIFIER_LEAD | QUANTIFIER_NON_LEAD

#: Quantifiers that force **plural agreement** on the subject and verb.
#:
#: A genuinely different fact from :data:`QUANTIFIER_LEAD`, not a divergent
#: copy of it. ``every`` and ``each`` are quantifier-leads yet take a
#: *singular* noun by English rule ("each dog is"), so their absence here is
#: correct; ``few``/``many``/``several``/``various`` take plurals but cannot
#: lead a categorical reading. Overlap is 4 of 8 in each direction, which is
#: what made these look like a divergence in the §1.3 count.
PLURAL_QUANTIFIERS: Final[frozenset[str]] = frozenset(
    {"all", "some", "many", "few", "most", "several", "various", "no"}
)

# --------------------------------------------------------------------------
# Predicate display
# --------------------------------------------------------------------------

#: Machine predicate id -> human display phrase. Was two byte-identical
#: 26-entry copies: ``semantic_templates.py::_PREDICATE_HUMANIZE`` (the
#: serving writer) and ``templates.py::_PREDICATE_DISPLAY`` (the eval-only
#: realizer).
PREDICATE_DISPLAY: Final[dict[str, str]] = {
    "is_defined_as": "is defined as",
    "is_caused_by": "is caused by",
    "has_steps": "has the following steps",
    "contrasts_with": "contrasts with",
    "corrects": "corrects",
    "recalls": "recalls",
    "is_verified_as": "is verified as",
    "addresses": "addresses",
    "defines": "defines",
    "means": "means",
    "grounds": "grounds",
    "supports": "supports",
    "causes": "causes",
    "reveals": "reveals",
    "precedes": "precedes",
    "follows": "follows",
    "belongs_to": "belongs to",
    "answers": "answers",
    "is_grounded_in": "is grounded in",
    "is_distinguished_from": "is distinguished from",
    "implies": "implies",
    "entails": "entails",
    "requires": "requires",
    "verifies": "verifies",
    "evidences": "evidences",
    "orders": "orders",
}

#: The discourse planner's two-entry display table.
#:
#: **Recorded divergence (Phase 2A decision).** Two deliberate differences
#: from :data:`PREDICATE_DISPLAY`, both preserved:
#:
#: 1. ``is_defined_as`` renders as ``"is"``, not ``"is defined as"``. Inside
#:    a flowing paragraph the short copula reads as prose; the long form
#:    reads as a schema dump. This is a register choice.
#: 2. The table is **two entries, not 26**, on purpose. Every other
#:    predicate falls through to ``predicate.replace("_", " ")``. Widening it
#:    to the full table would silently change paragraph rendering for 24
#:    predicates, so scope is preserved exactly.
#:
#: ``belongs_to`` agreed with :data:`PREDICATE_DISPLAY` and is therefore
#: derived from it — the one entry that can drift no longer can.
DISCOURSE_PREDICATE_DISPLAY: Final[dict[str, str]] = {
    "is_defined_as": "is",
    "belongs_to": PREDICATE_DISPLAY["belongs_to"],
}

# --------------------------------------------------------------------------
# Number morphology — two inverse maps, not two divergent copies
# --------------------------------------------------------------------------
#
# §1.3 of the plan counted "irregular plurals: 3 copies, all three diverge."
# Measured against source, that count conflates two directions:
#
#   * ``templates.py``  singular -> plural  (a PLURALIZER, 25 entries)
#   * ``member.py``     plural -> singular  (a SINGULARIZER, 29 entries)
#   * ``reader.py``     plural -> singular  (a SINGULARIZER, 8 entries)
#
# and the two singularizers do **not** contradict each other: reader's 8
# entries are a *strict subset* of member's 29 (set difference in the
# reader's favour is empty). So there is no disagreement to arbitrate here —
# only a coverage asymmetry, plus one direction's knowledge being
# unavailable in the other direction.

#: Singular -> plural. The pluralizer, from ``templates.py``.
IRREGULAR_PLURALS: Final[dict[str, str]] = {
    "child": "children", "ox": "oxen", "foot": "feet", "tooth": "teeth",
    "man": "men", "woman": "women", "person": "people",
    "mouse": "mice", "louse": "lice", "goose": "geese",
    # invariant
    "sheep": "sheep", "fish": "fish", "deer": "deer", "moose": "moose",
    "series": "series", "species": "species",
    # latin/greek-origin domain vocabulary
    "datum": "data", "criterion": "criteria", "phenomenon": "phenomena",
    "analysis": "analyses", "axis": "axes", "basis": "bases",
    "thesis": "theses", "hypothesis": "hypotheses",
    "mitochondrion": "mitochondria",
}

#: Plural -> singular, including invariants that map to themselves. The
#: singularizer, from ``member.py``, which is the widest number table CORE
#: has. Consulted BEFORE any suffix rule: if either token of a candidate
#: pair appears here, this table is the only authority for that pair — which
#: is what keeps ``species``/``specie`` and ``news``/``new`` unlinked.
IRREGULAR_SINGULARS: Final[dict[str, str]] = {
    "men": "man", "women": "woman", "people": "person",
    "children": "child", "mice": "mouse", "geese": "goose",
    "feet": "foot", "teeth": "tooth", "oxen": "ox",
    "wolves": "wolf", "knives": "knife", "lives": "life",
    "leaves": "leaf", "halves": "half", "elves": "elf",
    "loaves": "loaf", "thieves": "thief", "cacti": "cactus",
    "fungi": "fungus", "dice": "die",
    # invariants (plural == singular)
    "sheep": "sheep", "fish": "fish", "deer": "deer",
    "species": "species", "series": "series", "means": "means",
    "offspring": "offspring", "aircraft": "aircraft", "news": "news",
}

#: The 8 keys ``meaning_graph/reader.py`` currently covers.
#:
#: **Recorded divergence (Phase 2A decision).** The reader's values are all
#: *correct* — they agree with :data:`IRREGULAR_SINGULARS` entry for entry —
#: so the values are derived below and only the key list is local. What is
#: wrong is the **coverage**, and the consequence is not a refusal:
#: ``reader._singularize`` falls through to a bare ``-s`` strip, so an
#: uncovered plural is silently mis-singularized rather than declined
#: (``wolves`` -> ``wolve``, ``news`` -> ``new``, ``species`` -> ``specy``).
#: The reader's own comment claims it "REFUSES rather than guessing a wrong
#: singular (wrong=0)"; the code does not implement that.
#:
#: Widening this to the full table changes minted entity ids and therefore
#: served surfaces and trace hashes, so it is **Phase 2B** work behind the
#: authorization gate. Recorded here, with the gap named, rather than fixed
#: silently.
READER_SINGULAR_KEYS: Final[tuple[str, ...]] = (
    "people", "men", "women", "children", "feet", "teeth", "mice", "geese",
)

#: The reader's view of :data:`IRREGULAR_SINGULARS`, restricted to
#: :data:`READER_SINGULAR_KEYS`. Derived, so the reader's 8 values cannot
#: drift from the 29-entry table they are a subset of.
READER_IRREGULAR_SINGULARS: Final[dict[str, str]] = {
    key: IRREGULAR_SINGULARS[key] for key in READER_SINGULAR_KEYS
}
