"""Phase 2A pins: ``generate/lexicon.py`` is the only owner of its tables.

Three kinds of test here, and the distinction matters:

1. **Structural** — no module outside the lexicon may define a second copy of
   an owned table. Goes red if a duplicate is reintroduced.
2. **Caller provenance** — the set of modules importing each owned symbol is
   recorded. Goes red when a new consumer appears, forcing a decision rather
   than a silent widening.
3. **Recorded decisions** — every divergence the lexicon preserves on purpose
   is pinned here with its reason, so "unify these" becomes a test change
   someone has to justify.

A fourth group pins **current defective behaviour** that Phase 2B will fix.
Those tests are *supposed* to change; they exist so the fix cannot land
silently.

Why provenance is recorded rather than computed: PR #129 measured the serving
import closure at 227 first-party modules containing **all 13** table-owning
modules, so a static import test returns "everything is serving" and
discriminates nothing. Import-reachable is not call-reachable. The empirical
arbiter for behaviour is the 11 pinned lane SHAs, not this file.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from generate import lexicon

REPO_ROOT = Path(__file__).resolve().parents[1]

#: Packages scanned for duplicate table literals. ``evals/`` is deliberately
#: excluded: ``evals/grammar_roundtrip/projection.py`` keeps its own copy of
#: the quantifier map so the lane never consumes the thing it measures, and
#: that copy is pinned by its own test.
SCANNED_PACKAGES = ("generate", "chat", "core", "teaching")

#: Owned table -> the modules that may import it. Curated, not computed.
RECORDED_CONSUMERS: dict[str, frozenset[str]] = {
    "CONNECTIVES": frozenset({
        "generate.proof_chain.member",
        "generate.proof_chain.verb",
        "generate.proof_chain.cond_member",
    }),
    "STRUCTURAL": frozenset({"generate.proof_chain.english"}),
    "COPULAS": frozenset({"generate.proof_chain.english"}),
    "COPULA_FORMS": frozenset({"generate.proof_chain.member"}),
    # Auxiliary-role consumers of the same be-form inventory. Found by the
    # duplicate scanner below, not by grepping for COPULA-ish names — which is
    # precisely why the structural test exists.
    "BE_FINITE": frozenset({"generate.realizer_guard", "chat.runtime"}),
    "SENTENTIAL_NOT": frozenset({
        "generate.proof_chain.english",
        "generate.proof_chain.member",
    }),
    "NEGATION_BEARING": frozenset({"generate.proof_chain.english"}),
    "NEGATION_BEARING_WITH_NOT": frozenset({"generate.proof_chain.member"}),
    "QUANTIFIER_LEAD": frozenset({"generate.proof_chain.english"}),
    "QUANTIFIER_TOKENS": frozenset({"generate.proof_chain.member"}),
    "PLURAL_QUANTIFIERS": frozenset({"generate.templates"}),
    "PREDICATE_DISPLAY": frozenset({
        "generate.templates",
        "generate.semantic_templates",
    }),
    "DISCOURSE_PREDICATE_DISPLAY": frozenset({"generate.discourse_planner"}),
    "IRREGULAR_PLURALS": frozenset({"generate.templates"}),
    "IRREGULAR_SINGULARS": frozenset({"generate.proof_chain.member"}),
    "READER_IRREGULAR_SINGULARS": frozenset({"generate.meaning_graph.reader"}),
}

#: The tables a duplicate literal would be a duplicate *of*. Frozen as
#: comparable values (dicts -> sorted item tuples, sets -> frozensets).
OWNED_TABLES: dict[str, object] = {
    "CONNECTIVES": lexicon.CONNECTIVES,
    "STRUCTURAL": lexicon.STRUCTURAL,
    # COPULAS / COPULA_FORMS / BE_FINITE are all views of one inventory, so a
    # single entry covers them; the report names the fact, not every alias.
    "BE_FINITE_FORMS": lexicon.BE_FINITE,
    "NEGATION_BEARING": lexicon.NEGATION_BEARING,
    "NEGATION_BEARING_WITH_NOT": lexicon.NEGATION_BEARING_WITH_NOT,
    "QUANTIFIER_LEAD": lexicon.QUANTIFIER_LEAD,
    "QUANTIFIER_TOKENS": lexicon.QUANTIFIER_TOKENS,
    "PLURAL_QUANTIFIERS": lexicon.PLURAL_QUANTIFIERS,
    "PREDICATE_DISPLAY": tuple(sorted(lexicon.PREDICATE_DISPLAY.items())),
    "IRREGULAR_PLURALS": tuple(sorted(lexicon.IRREGULAR_PLURALS.items())),
    "IRREGULAR_SINGULARS": tuple(sorted(lexicon.IRREGULAR_SINGULARS.items())),
}


def _python_files() -> list[Path]:
    out: list[Path] = []
    for pkg in SCANNED_PACKAGES:
        root = REPO_ROOT / pkg
        if root.is_dir():
            out.extend(p for p in root.rglob("*.py") if "__pycache__" not in p.parts)
    return out


def _module_name(path: Path) -> str:
    return ".".join(path.relative_to(REPO_ROOT).with_suffix("").parts)


def _frozen_literal(node: ast.AST) -> object | None:
    """A comparable value for a set/dict/frozenset(...) literal, else None."""
    target = node
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "frozenset"
        and len(node.args) == 1
    ):
        target = node.args[0]
    if not isinstance(target, (ast.Dict, ast.Set)):
        return None
    try:
        value = ast.literal_eval(target)
    except (ValueError, SyntaxError, TypeError):
        return None
    if isinstance(value, dict):
        if not all(isinstance(k, str) for k in value):
            return None
        return tuple(sorted(value.items()))
    if isinstance(value, (set, frozenset)):
        return frozenset(value)
    return None


# --------------------------------------------------------------------------
# 1. Structural — one definition per fact
# --------------------------------------------------------------------------


def test_no_module_outside_the_lexicon_defines_an_owned_table() -> None:
    """A second copy of an owned table anywhere in the scanned packages is a
    regression of the whole phase. Mutation check: paste any owned literal
    back into its old home and this goes red."""
    lexicon_path = REPO_ROOT / "generate" / "lexicon.py"
    # Keyed by (file, line) so one literal is reported once — a
    # ``frozenset({...})`` call and its inner set are two AST nodes.
    hits: dict[tuple[str, object], set[str]] = {}
    for path in _python_files():
        if path == lexicon_path:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            frozen = _frozen_literal(node)
            if frozen is None:
                continue
            for name, owned in OWNED_TABLES.items():
                if frozen == owned:
                    key = (str(path.relative_to(REPO_ROOT)), getattr(node, "lineno", "?"))
                    hits.setdefault(key, set()).add(name)
    duplicates = [
        f"{file}:{line} redefines lexicon.{'/'.join(sorted(names))}"
        for (file, line), names in sorted(hits.items())
    ]
    assert not duplicates, "duplicate linguistic tables:\n  " + "\n  ".join(duplicates)


def test_the_duplicate_scanner_can_actually_find_a_duplicate(tmp_path: Path) -> None:
    """The scanner above is worthless if it cannot detect the thing it forbids.
    Feed it a known duplicate and require a hit."""
    planted = tmp_path / "planted.py"
    planted.write_text(
        'X = frozenset({"if", "then", "or", "and", "either"})\n', encoding="utf-8"
    )
    tree = ast.parse(planted.read_text(encoding="utf-8"))
    hits = [
        name
        for node in ast.walk(tree)
        for name, owned in OWNED_TABLES.items()
        if (frozen := _frozen_literal(node)) is not None and frozen == owned
    ]
    assert "CONNECTIVES" in hits


# --------------------------------------------------------------------------
# 2. Caller provenance
# --------------------------------------------------------------------------


def _actual_consumers() -> dict[str, set[str]]:
    found: dict[str, set[str]] = {}
    for path in _python_files():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == "generate.lexicon":
                for alias in node.names:
                    found.setdefault(alias.name, set()).add(_module_name(path))
    return found


def test_every_lexicon_consumer_is_recorded() -> None:
    """A new importer of an owned table must be added to RECORDED_CONSUMERS.
    That is the point: widening a table's reach becomes a decision with a
    diff, not a side effect."""
    actual = _actual_consumers()
    unexpected = {
        name: sorted(mods - RECORDED_CONSUMERS.get(name, frozenset()))
        for name, mods in actual.items()
        if mods - RECORDED_CONSUMERS.get(name, frozenset())
    }
    assert not unexpected, f"unrecorded lexicon consumers: {unexpected}"


def test_every_recorded_consumer_still_imports_what_it_claims() -> None:
    """The other direction — a stale record is also a defect, because it makes
    the provenance table lie about who depends on what."""
    actual = _actual_consumers()
    stale = {
        name: sorted(mods - actual.get(name, set()))
        for name, mods in RECORDED_CONSUMERS.items()
        if mods - actual.get(name, set())
    }
    assert not stale, f"recorded consumers that no longer import: {stale}"


# --------------------------------------------------------------------------
# 3. Recorded decisions — derivations that can no longer drift
# --------------------------------------------------------------------------


def test_structural_is_connectives_plus_therefore() -> None:
    assert lexicon.STRUCTURAL == lexicon.CONNECTIVES | {"therefore"}
    assert "therefore" not in lexicon.CONNECTIVES


def test_copulas_is_exactly_the_set_view_of_copula_forms() -> None:
    assert lexicon.COPULAS == frozenset(lexicon.COPULA_FORMS)
    assert lexicon.COPULA_FORMS == ("is", "are", "was", "were"), "order is load-bearing"


def test_the_two_negation_sets_differ_by_exactly_bare_not() -> None:
    """v2-EN normalizes ``<copula> not`` and so must let ``not`` reach that
    rule; v3-MEM refuses every non-copular ``not``. Both bands serve, so
    unifying them changes what CORE refuses — Phase 2B, not 2A."""
    assert lexicon.NEGATION_BEARING_WITH_NOT - lexicon.NEGATION_BEARING == {"not"}
    assert "not" not in lexicon.NEGATION_BEARING


def test_quantifier_lead_is_a_strict_subset_of_quantifier_tokens() -> None:
    """Measured before the migration: member's 25 tokens were a strict
    superset of english's 8, agreeing on all 8. Derivation preserves that."""
    assert lexicon.QUANTIFIER_LEAD < lexicon.QUANTIFIER_TOKENS
    assert lexicon.QUANTIFIER_TOKENS - lexicon.QUANTIFIER_LEAD == lexicon.QUANTIFIER_NON_LEAD


def test_plural_quantifiers_excludes_the_singular_taking_leads() -> None:
    """``every``/``each`` lead a categorical reading but take a SINGULAR noun
    ("each dog is"), so their absence from PLURAL_QUANTIFIERS is correct, not
    a coverage gap. This is why the two sets are different facts rather than
    divergent copies."""
    for singular_taking in ("every", "each"):
        assert singular_taking in lexicon.QUANTIFIER_LEAD
        assert singular_taking not in lexicon.PLURAL_QUANTIFIERS


def test_discourse_display_diverges_from_the_shared_table_on_exactly_one_key() -> None:
    """``is_defined_as`` -> "is" is a deliberate register choice (the short
    copula reads as prose mid-paragraph). ``belongs_to`` is derived, so it
    cannot drift."""
    shared, discourse = lexicon.PREDICATE_DISPLAY, lexicon.DISCOURSE_PREDICATE_DISPLAY
    differing = {k for k in discourse if shared.get(k) != discourse[k]}
    assert differing == {"is_defined_as"}
    assert discourse["is_defined_as"] == "is"
    assert discourse["belongs_to"] == shared["belongs_to"]


def test_discourse_display_scope_is_two_entries_on_purpose() -> None:
    """Widening this to the full 26 would silently change paragraph rendering
    for 24 predicates that currently fall through to
    ``predicate.replace("_", " ")``. Scope is preserved exactly."""
    assert set(lexicon.DISCOURSE_PREDICATE_DISPLAY) == {"is_defined_as", "belongs_to"}
    assert len(lexicon.PREDICATE_DISPLAY) == 26


def test_the_two_number_tables_are_inverse_directions_not_copies() -> None:
    """§1.3 counted "3 copies of irregular plurals, all diverging." Measured,
    one is a PLURALIZER (singular -> plural) and the others SINGULARIZERS
    (plural -> singular). Comparing them as copies is a category error."""
    assert lexicon.IRREGULAR_PLURALS["child"] == "children"
    assert lexicon.IRREGULAR_SINGULARS["children"] == "child"
    # Non-invariant entries present in both go opposite ways.
    round_trips = [
        (sing, plur)
        for sing, plur in lexicon.IRREGULAR_PLURALS.items()
        if sing != plur and plur in lexicon.IRREGULAR_SINGULARS
    ]
    assert round_trips, "expected overlap between the two directions"
    for sing, plur in round_trips:
        assert lexicon.IRREGULAR_SINGULARS[plur] == sing, f"{sing}/{plur} not inverse"


def test_reader_number_table_is_a_derived_subset_that_cannot_drift() -> None:
    """The reader's 8 values were measured to AGREE with the 29-entry table
    entry for entry — the set difference in the reader's favour was empty. So
    only its key list is local; the values are derived."""
    assert set(lexicon.READER_IRREGULAR_SINGULARS) == set(lexicon.READER_SINGULAR_KEYS)
    assert len(lexicon.READER_SINGULAR_KEYS) == 8
    for key, value in lexicon.READER_IRREGULAR_SINGULARS.items():
        assert lexicon.IRREGULAR_SINGULARS[key] == value
    assert set(lexicon.READER_IRREGULAR_SINGULARS) < set(lexicon.IRREGULAR_SINGULARS)


# --------------------------------------------------------------------------
# 4. Defects Phase 2B must fix — pinned so the fix cannot land silently
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("plural", "current_wrong_singular"),
    [
        ("wolves", "wolve"),
        ("leaves", "leave"),
        ("knives", "knive"),
        ("news", "new"),
        ("species", "specy"),
    ],
)
def test_reader_silently_mis_singularizes_uncovered_plurals(
    plural: str, current_wrong_singular: str
) -> None:
    """CURRENT BEHAVIOUR, deliberately pinned as wrong.

    ``reader.py``'s comment claims an unrecognized plural "REFUSES rather
    than guessing a wrong singular (wrong=0)". The code does not implement
    that: ``_singularize`` falls through to a bare ``-s`` strip, so uncovered
    plurals mint corrupted entity ids. ``news`` -> ``new`` and ``species`` ->
    ``specy`` are exactly the corruptions ``member.py``'s table comment says
    its table exists to prevent.

    Phase 2B replaces the reader's 8-key view with the full singularizer and
    must flip these to ``wolf``/``leaf``/``knife``/``news``/``species``.
    Changing minted ids moves trace hashes, which is why it is gated.
    """
    from generate.meaning_graph.reader import _singularize

    assert _singularize(plural) == current_wrong_singular


def test_reader_covered_plurals_are_already_correct() -> None:
    """The control for the test above: where the reader HAS an entry it is
    right. So the defect is coverage, not wrong values — which is why 2A
    could derive the values safely and leave coverage to 2B."""
    from generate.meaning_graph.reader import _singularize

    for plural, singular in lexicon.READER_IRREGULAR_SINGULARS.items():
        assert _singularize(plural) == singular
