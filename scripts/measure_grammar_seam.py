#!/usr/bin/env python3
"""Reproduce every measurement in the grammar-unification plan's §1.

Usage:
    uv run python scripts/measure_grammar_seam.py            # all sections
    uv run python scripts/measure_grammar_seam.py --section tables

Each section corresponds to a numbered subsection of
``docs/plans/grammar-unification-2026-07-26.md``.  The plan quotes these
numbers; this script is how a reader checks them instead of trusting them.

Read-only: imports and probes, no mutation, no writes.
"""

from __future__ import annotations

import argparse
import ast
import collections
import importlib
import json
import pathlib
import sys

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

# --- §1.3 inventory inputs ------------------------------------------------- #

_READ_PATH_FILES = (
    "generate/meaning_graph/reader.py",
    "generate/meaning_graph/projectors.py",
    "generate/meaning_graph/relational.py",
    "generate/proof_chain/english.py",
    "generate/proof_chain/member.py",
    "generate/proof_chain/cond_member.py",
    "generate/proof_chain/verb.py",
    "generate/proof_chain/exist.py",
    "generate/proof_chain/categorical.py",
)
_WRITE_PATH_FILES = (
    "generate/semantic_templates.py",
    "generate/templates.py",
    "generate/morphology.py",
    "generate/realizer.py",
    "generate/discourse_planner.py",
    "chat/register_variation.py",
)

#: Groups of tables that encode the SAME linguistic fact and should agree.
#: Groups that are ONE fact and must therefore be ONE object.
#:
#: Corrected 2026-07-26 (plan §1.9). The original grouping asserted that the
#: three plural tables and the three quantifier sets were each one fact. They
#: are not: the plural tables are a pluralizer plus two singularizers (inverse
#: directions), and the quantifier sets are three distinct facts — "can lead a
#: clause", "is a quantifier token", "forces plural agreement". Reporting those
#: as DIVERGE was a correct answer to a wrong question, so they moved to
#: :data:`_RELATED_BUT_DISTINCT` below.
_SHOULD_AGREE = {
    "connective tokens": (
        ("generate.proof_chain.member", "_CONNECTIVES"),
        ("generate.proof_chain.verb", "_CONNECTIVES"),
        ("generate.proof_chain.cond_member", "_CONNECTIVE_TOKENS"),
    ),
    "predicate display": (
        ("generate.semantic_templates", "_PREDICATE_HUMANIZE"),
        ("generate.templates", "_PREDICATE_DISPLAY"),
    ),
    "be-form inventory": (
        ("generate.proof_chain.english", "_COPULAS"),
        ("generate.realizer_guard", "_BE_AUX"),
        ("chat.runtime", "_BE_FORMS"),
    ),
}

#: Tables that are RELATED but genuinely distinct, with the relation that must
#: hold between them. Each is pinned by ``tests/test_lexicon_single_source.py``;
#: this table exists so the report states the relation instead of crying
#: divergence. ``relation`` is a predicate over the two loaded values.
_RELATED_BUT_DISTINCT = (
    (
        "STRUCTURAL = CONNECTIVES + therefore",
        ("generate.proof_chain.english", "_STRUCTURAL"),
        ("generate.proof_chain.member", "_CONNECTIVES"),
        lambda a, b: frozenset(a) - frozenset(b) == {"therefore"},
    ),
    (
        "QUANTIFIER_TOKENS strictly contains LEAD",
        ("generate.proof_chain.member", "_QUANTIFIER_TOKENS"),
        ("generate.proof_chain.english", "_QUANTIFIER_LEAD"),
        lambda a, b: frozenset(b) < frozenset(a),
    ),
    (
        "PLURAL_QUANTIFIERS is a different fact (excludes every/each)",
        ("generate.templates", "_PLURAL_QUANTIFIERS"),
        ("generate.proof_chain.english", "_QUANTIFIER_LEAD"),
        lambda a, b: {"every", "each"} <= frozenset(b) and not ({"every", "each"} & frozenset(a)),
    ),
    (
        "member negation = english negation + not",
        ("generate.proof_chain.member", "_NEGATION_BEARING"),
        ("generate.proof_chain.english", "_NEGATION_BEARING"),
        lambda a, b: frozenset(a) - frozenset(b) == {"not"},
    ),
    (
        "reader singulars are a subset of the full table",
        ("generate.meaning_graph.reader", "_IRREGULAR_PLURALS"),
        ("generate.proof_chain.member", "_IRREGULAR_PLURALS"),
        lambda a, b: set(a.items()) < set(b.items()),
    ),
    (
        "pluralizer is the inverse direction of the singularizer",
        ("generate.templates", "_IRREGULAR_PLURALS"),
        ("generate.proof_chain.member", "_IRREGULAR_PLURALS"),
        lambda a, b: all(b[p] == s for s, p in a.items() if s != p and p in b),
    ),
)

#: Plural-subject agreement oracle for §1.4 — hand-written English, not derived
#: from the code under test (deriving it from the code would make it agree by
#: construction and measure nothing).
_AUX_PLURAL = {"is": "are", "are": "are", "has": "have", "have": "have", "belongs": "belong"}
_BARE_BASE = {
    "causes": "cause", "evidences": "evidence", "means": "mean",
    "addresses": "address", "answers": "answer", "corrects": "correct",
    "defines": "define", "entails": "entail", "follows": "follow",
    "grounds": "ground", "implies": "imply", "orders": "order",
    "precedes": "precede", "recalls": "recall", "requires": "require",
    "reveals": "reveal", "supports": "support", "verifies": "verify",
    "contrasts with": "contrast with",
}


def _word_tables(path: str) -> dict[str, frozenset[str]]:
    """Module-level assignments holding >=3 lowercase english-ish literals."""
    source = (_REPO_ROOT / path).read_text()
    out: dict[str, frozenset[str]] = {}
    for node in ast.parse(source).body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        names = [t.id for t in targets if isinstance(t, ast.Name)]
        if not names:
            continue
        words = {
            sub.value.strip()
            for sub in ast.walk(node)
            if isinstance(sub, ast.Constant)
            and isinstance(sub.value, str)
            and sub.value.strip()
            and sub.value.strip().replace("_", "").replace(" ", "").replace("-", "").isalpha()
            and sub.value.strip().islower()
        }
        if len(words) >= 3:
            out[names[0]] = frozenset(words)
    return out


def section_tables() -> None:
    """§1.3 — duplication and Jaccard across the reading/writing paths."""
    print("=" * 74)
    print("§1.3  Linguistic knowledge duplicated across reading vs writing")
    print("=" * 74)
    read_tables: dict[str, frozenset[str]] = {}
    write_tables: dict[str, frozenset[str]] = {}
    for rel in _READ_PATH_FILES:
        if (_REPO_ROOT / rel).exists():
            for name, words in _word_tables(rel).items():
                read_tables[f"{pathlib.Path(rel).name}::{name}"] = words
    for rel in _WRITE_PATH_FILES:
        if (_REPO_ROOT / rel).exists():
            for name, words in _word_tables(rel).items():
                write_tables[f"{pathlib.Path(rel).name}::{name}"] = words

    read_words = frozenset().union(*read_tables.values()) if read_tables else frozenset()
    write_words = frozenset().union(*write_tables.values()) if write_tables else frozenset()
    union = read_words | write_words
    shared = read_words & write_words

    print(f"  reading path: {len(read_tables):3d} word-tables, {len(read_words):3d} distinct words")
    print(f"  writing path: {len(write_tables):3d} word-tables, {len(write_words):3d} distinct words")
    print(f"  shared      : {len(shared):3d} of {len(union)} union")
    print(f"  JACCARD     : {len(shared) / len(union):.3f}" if union else "  JACCARD: n/a")
    print(
        "  NOTE: these counts scan SOURCE LITERALS, so after Phase 2A they\n"
        "        measure how much table text still lives in these files, not\n"
        "        how many answers exist. A unified fact leaves the file as an\n"
        "        import and DROPS out of the count — Jaccard falling is the\n"
        "        expected direction, not a regression. Read the ownership\n"
        "        block below for the number the 2A exit criterion actually means."
    )

    print("\n  tables that encode the same fact (by OBJECT IDENTITY):")
    owners_total = 0
    views_total = 0
    for label, refs in _SHOULD_AGREE.items():
        loaded = []
        for module_name, attr in refs:
            try:
                value = getattr(importlib.import_module(module_name), attr)
            except (ImportError, AttributeError):
                continue
            keys = frozenset(value) if not isinstance(value, tuple) else frozenset(value)
            loaded.append((f"{module_name.split('.')[-1]}.{attr}", keys, id(value)))
        if len(loaded) < 2:
            continue
        # Distinct underlying OBJECTS, not distinct names. After unification a
        # band attribute is the lexicon object itself, so N names backed by one
        # object is one answer — which is what "unified" means. Comparing by
        # value alone cannot tell a shared object from two equal copies.
        distinct_objects = {oid for _, _, oid in loaded}
        distinct_values = {keys for _, keys, _ in loaded}
        owners_total += len(distinct_objects)
        views_total += len(loaded)
        if len(distinct_objects) == 1:
            verdict = "UNIFIED"
        elif len(distinct_values) == 1:
            verdict = "EQUAL-COPY"  # same content, still two objects
        else:
            verdict = "DIVERGE"
        sizes = ", ".join(f"{n}={len(k)}" for n, k, _ in loaded)
        print(
            f"    {verdict:10s} {label:26s} "
            f"({len(distinct_objects)} owner(s) behind {len(loaded)} view(s): {sizes})"
        )
    if views_total:
        print(
            f"\n  OWNERSHIP   : {owners_total} distinct objects behind {views_total} names"
            f"  (1 owner per fact is the 2A goal)"
        )

    print("\n  related but DISTINCT facts — the relation that must hold:")
    for label, ref_a, ref_b, relation in _RELATED_BUT_DISTINCT:
        try:
            a = getattr(importlib.import_module(ref_a[0]), ref_a[1])
            b = getattr(importlib.import_module(ref_b[0]), ref_b[1])
        except (ImportError, AttributeError):
            continue
        try:
            ok = bool(relation(a, b))
        except Exception:  # a broken relation is a red flag, not a crash
            ok = False
        print(f"    {'HOLDS' if ok else 'BROKEN':10s} {label}")


def section_agreement() -> None:
    """§1.4 — plural-subject agreement over the predicate-display table."""
    print("\n" + "=" * 74)
    print("§1.4  Plural-subject agreement in the (eval-only) realizer")
    print("=" * 74)
    from generate.templates import _PREDICATE_DISPLAY, _inflect_predicate

    def expected(display: str) -> str:
        head = display.split(" ", 1)[0]
        if head in _AUX_PLURAL:
            rest = display.split(" ", 1)[1] if " " in display else ""
            return (_AUX_PLURAL[head] + (" " + rest if rest else "")).strip()
        return _BARE_BASE.get(display, display)

    wrong = []
    for key, display in sorted(_PREDICATE_DISPLAY.items()):
        got, want = _inflect_predicate(display, plural_subject=True), expected(display)
        if got != want:
            wrong.append((key, display, got, want))

    total = len(_PREDICATE_DISPLAY)
    print(f"  correct: {total - len(wrong)}/{total}     WRONG: {len(wrong)}/{total}")
    for key, display, got, want in wrong:
        print(f"    {key:24s} {display!r:28s} -> {got!r:26s} want {want!r}")


def section_readers() -> None:
    """§1.7 — reader-vs-reader singularization disagreement."""
    print("\n" + "=" * 74)
    print("§1.7  Do CORE's two readers agree on singularization?")
    print("=" * 74)
    from generate.meaning_graph.reader import _singularize
    from generate.proof_chain.member import _IRREGULAR_PLURALS as member_table
    from generate.templates import pluralize

    pairs = sorted({p: s for p, s in member_table.items() if p != s}.items())
    disagree = [(p, s, _singularize(p)) for p, s in pairs if _singularize(p) != s]
    print(f"  plurals the v3-MEM band reader knows: {len(pairs)}")
    print(f"  MeaningGraph reader AGREES          : {len(pairs) - len(disagree)}/{len(pairs)}")
    print(f"  MeaningGraph reader DISAGREES       : {len(disagree)}/{len(pairs)}")
    silent = [(p, s, g) for p, s, g in disagree if g is not None]
    refused = [(p, s) for p, s, g in disagree if g is None]
    print(f"\n  SILENTLY WRONG singular ({len(silent)}):")
    for plural, singular, got in silent:
        print(f"    {plural:10s} v3-MEM={singular:10s} MeaningGraph={got!r}")
    print(f"\n  REFUSED by MeaningGraph reader ({len(refused)}):")
    print(f"    {', '.join(p for p, _ in refused)}")

    bad_write = [(p, s) for p, s in pairs if pluralize(s) != p]
    print(f"\n  writer cannot reproduce {len(bad_write)}/{len(pairs)} of those plurals:")
    for plural, singular in bad_write:
        print(f"    pluralize({singular!r}) -> {pluralize(singular)!r}, want {plural!r}")


def section_served() -> None:
    """§1.7 — malformed categorical surfaces reaching served output."""
    print("\n" + "=" * 74)
    print("§1.7  Malformed surfaces served by the ratified v1b categorical band")
    print("=" * 74)
    from chat.deduction_surface import deduction_grounded_surface

    probes = ["dogs", "cats", "students", "wolves", "children", "men"]
    print("  synthetic probes:")
    for noun in probes:
        text = (
            f"All {noun} are mammals. All mammals are animals. "
            f"Therefore all {noun} are animals."
        )
        print(f"    in : all {noun} are mammals ...")
        print(f"    out: {deduction_grounded_surface(text)}")

    print("\n  ratified corpus cases that serve a malformed categorical clause:")
    flagged = 0
    served_categorical = 0
    for path in sorted((_REPO_ROOT / "evals/deduction_serve").glob("*/cases.jsonl")):
        for line in path.read_text().splitlines():
            if not line.strip():
                continue
            case = json.loads(line)
            surface = deduction_grounded_surface(case["text"])
            if not surface:
                continue
            import re

            matches = re.findall(r"\b(all|no|some)\s+([a-z_]+)\s+(are|is)\b", surface)
            if not matches:
                continue
            served_categorical += 1
            for quant, noun, _copula in matches:
                if re.search(rf"\b{quant}\s+{noun}s?\b", case["text"], re.I) and not re.search(
                    rf"\b{quant}\s+{noun}\b(?!s)", case["text"], re.I
                ):
                    flagged += 1
                    print(f"    [{case['id']}] {surface}")
                    break
    print(f"\n  {flagged} malformed of {served_categorical} serving a categorical clause")


def section_roundtrip() -> None:
    """§1.6 — the round-trip baseline and the six-reader refusal table."""
    print("\n" + "=" * 74)
    print("§1.6  Round-trip baseline, and every reader on writer output")
    print("=" * 74)
    from evals.grammar_roundtrip.runner import run_lane

    metrics = run_lane().metrics
    for key in (
        "graph_cases", "g_write_rate", "g_read_rate", "g_args_rate",
        "g_predicates_rate", "g_exact_rate", "surface_cases", "s_read_rate",
        "s_renderable_rate", "s_surface_match_rate", "negative_cases", "reject_rate",
    ):
        print(f"  {key:24s} {metrics[key]}")

    print("\n  every reader against writer output and live served surfaces:")
    from generate.meaning_graph.reader import comprehend
    from generate.proof_chain.cond_member import read_cond_member_argument
    from generate.proof_chain.english import read_english_argument
    from generate.proof_chain.exist import read_exist_argument
    from generate.proof_chain.member import read_member_argument
    from generate.proof_chain.verb import read_verb_argument

    readers = {
        "meaning_graph": lambda t: comprehend(t, source_id="probe"),
        "english": read_english_argument,
        "member": read_member_argument,
        "cond_member": read_cond_member_argument,
        "verb": read_verb_argument,
        "exist": read_exist_argument,
    }
    targets = (
        "Molecule binds enzyme.",
        "all wolves is defined a mammal",
        "Knowledge is what a person knows from truth and evidence.",
    )
    outcomes: collections.Counter[str] = collections.Counter()
    for text in targets:
        print(f"\n    {text!r}")
        for name, fn in readers.items():
            try:
                result = fn(text)
                reason = getattr(result, "reason", "") or ""
                kind = type(result).__name__
                outcomes["refused" if "Refus" in kind else "read"] += 1
                print(f"      {name:14s} {kind:22s} {reason}")
            except Exception as exc:  # noqa: BLE001 - a raising reader is a result
                outcomes["raised"] += 1
                print(f"      {name:14s} raised {type(exc).__name__}")
    print(f"\n    totals: {dict(outcomes)}")


_SECTIONS = {
    "tables": section_tables,
    "agreement": section_agreement,
    "readers": section_readers,
    "served": section_served,
    "roundtrip": section_roundtrip,
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--section", choices=sorted(_SECTIONS), action="append",
        help="run only this section (repeatable); default is all",
    )
    args = parser.parse_args()
    for name in args.section or list(_SECTIONS):
        _SECTIONS[name]()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
