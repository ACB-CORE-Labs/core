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
    # Phase 2B: generate.morphology became the single owner of the number
    # RULES, so it is now the consumer of the number tables. The reader no
    # longer imports a table of its own — it calls morphology.singularize —
    # which is why READER_IRREGULAR_SINGULARS/READER_SINGULAR_KEYS were deleted
    # rather than left behind documenting a coverage gap that no longer exists.
    "IRREGULAR_PLURALS": frozenset({"generate.morphology", "generate.templates"}),
    "IRREGULAR_SINGULARS": frozenset({
        "generate.morphology",
        "generate.proof_chain.member",
    }),
    "INVARIANT_NUMBER": frozenset({"generate.morphology"}),
    "MASS_NOUNS": frozenset({"generate.morphology"}),
    # Phase 3: the closed f/fe -> ves set, derived from the singularizer's own
    # ves-rows so the rule cannot claim a word the table does not know.
    "VES_PLURAL_SINGULARS": frozenset({"generate.morphology"}),
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


def test_invariant_number_is_derived_from_the_singularizer() -> None:
    """Invariants must not be a second hand-written list.

    A hand-written list is exactly how the directions drifted: the pluralizer
    lacked ``aircraft``/``means``/``offspring`` and produced "aircrafts",
    "meanses", "offsprings" while the singularizer knew all three. Deriving
    from the ``key == value`` rows makes that class of gap unrepresentable."""
    expected = {p for p, s in lexicon.IRREGULAR_SINGULARS.items() if p == s}
    assert lexicon.INVARIANT_NUMBER == expected
    for word in ("sheep", "aircraft", "means", "offspring", "species", "series"):
        assert word in lexicon.INVARIANT_NUMBER


# --------------------------------------------------------------------------
# 4. Defects Phase 2B must fix — pinned so the fix cannot land silently
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("plural", "singular"),
    [
        # Phase 2A pinned these as WRONG (wolve / leave / knive). Phase 2B
        # flipped them by routing the reader through the shared 29-entry
        # singularizer.
        ("wolves", "wolf"),
        ("leaves", "leaf"),
        ("knives", "knife"),
        ("halves", "half"),
        ("thieves", "thief"),
        ("children", "child"),
        ("men", "man"),
        # Genuinely inflected irregulars the reader could not read before.
        ("cacti", "cactus"),
        ("fungi", "fungus"),
        ("oxen", "ox"),
    ],
)
def test_reader_singularizes_irregulars_correctly(plural: str, singular: str) -> None:
    """The defect Phase 2A pinned, now fixed.

    ``reader.py``'s comment always claimed an unrecognized plural "REFUSES
    rather than guessing a wrong singular (wrong=0)". Until 2B the code did
    not implement it — ``_singularize`` fell through to a bare ``-s`` strip
    and minted corrupted ids that reached served text ("all wolve are
    mammal"). The comment is now true of the code.
    """
    from generate.meaning_graph.reader import _singularize

    assert _singularize(plural) == singular


@pytest.mark.parametrize(
    "invariant", ["fish", "sheep", "deer", "species", "series", "news", "means"]
)
def test_reader_declines_number_invariant_forms(invariant: str) -> None:
    """Invariants are AMBIGUOUS in number and must be declined, not resolved.

    "fish are mammals" is plural; "a fish is a mammal" is singular; the token
    cannot tell you which. Two independent reasons this must decline:

    1. **Honesty** — resolving it is a guess about number, and 2A measured what
       guessing costs: the old ``-s`` strip turned ``news`` into ``new`` and
       ``species`` into ``specy``.
    2. **Soundness** — the serving composer tries the categorical band (v1b)
       first. Resolving an invariant makes v1b *accept* a sentence it cannot
       decide, stealing the case from a band that can. Measured: resolving
       ``fish`` made ds-ex-0012 ("No fish are mammals. Therefore some fish are
       mammals.") answer ``invalid`` instead of ``refuted`` — **wrong=1 on a
       ratified band.** Declining restores the fall-through.
    """
    from generate.meaning_graph.reader import _singularize

    assert _singularize(invariant) is None


@pytest.mark.parametrize("not_a_plural", ["child", "evidence", "wolf", "", "ss"])
def test_reader_declines_rather_than_guessing(not_a_plural: str) -> None:
    """The other half of wrong=0: a singular, a mass noun, or anything the
    closed rules do not confidently cover returns ``None`` so the caller can
    refuse instead of minting a corrupted id. Without this, ``child`` would
    become ``chil``."""
    from generate.meaning_graph.reader import _singularize

    assert _singularize(not_a_plural) is None


def test_regular_plurals_still_singularize() -> None:
    """Control: widening the irregular table must not break the regular rule
    that handles the overwhelming majority of real input."""
    from generate.meaning_graph.reader import _singularize

    assert _singularize("cars") == "car"
    assert _singularize("glasses") == "glass"
    assert _singularize("cities") == "city"


def test_the_two_number_directions_are_mutual_inverses() -> None:
    """Every irregular the singularizer knows, the pluralizer can produce.

    This is the law that makes read/write agreement possible at all: if CORE
    can read ``cacti`` but writes ``cactuses``, no round trip can close. Phase
    2B added the three missing inverses (cactus/fungus/die) and derived
    :data:`lexicon.INVARIANT_NUMBER` from the singularizer's own invariant
    rows, so ``aircraft``/``means``/``offspring`` stop becoming "aircrafts",
    "meanses", "offsprings".
    """
    from generate.morphology import pluralize

    broken = {
        singular: (pluralize(singular), plural)
        for plural, singular in lexicon.IRREGULAR_SINGULARS.items()
        if pluralize(singular) != plural
    }
    assert not broken, f"singular -> plural does not round-trip: {broken}"


def test_mass_nouns_and_compounds_inflect_correctly() -> None:
    """Two cases the categorical renderer depends on: mass nouns must not take
    a plural ("all evidence", not "all evidences"), and an English compound
    inflects on its HEAD ("guard dogs", not "guards dog")."""
    from generate.morphology import pluralize

    assert pluralize("evidence") == "evidence"
    assert pluralize("knowledge") == "knowledge"
    assert pluralize("guard_dog") == "guard_dogs"
    assert pluralize("guard dog") == "guard dogs"
