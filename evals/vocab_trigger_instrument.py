"""evals/vocab_trigger_instrument.py — mechanism-vs-coverage refusal instrument.

The measurable test from `docs/handoffs/COMPREHENSION-READER-AUDIT.md`
(Q5 "measurable tests") generalized to the two composers this arc actually
ships: split declined turns by WHY they declined — a closed-grammar SHAPE
the reader cannot yet parse ("mechanism"), or a TERM/RELATION the ratified
content never taught ("coverage") — and count admissions, so a future
lexicon/curriculum batch's effect can be measured as a before/after delta
instead of asserted.

This is the same axis `project-base-knowledge-pack-expansion-trigger`
(memory) already names for the math reader: pack/base-knowledge expansion
becomes load-bearing exactly when refusals shift from mechanism scope to
vocabulary scope. This module makes that shift countable for the deduction
and curriculum composers, using their own closed, typed refusal reasons —
no heuristic text-matching, no invented policy.

**Three buckets, not two.** A decline is "mechanism" (an unreadable
closed-grammar SHAPE), "coverage" (an absent TERM/RELATION), or
"engine_refused" (a fully-read, well-formed argument the ROBDD engine
itself declines — inconsistent premises, or out of the decidable regime;
`generate/proof_chain/entail.py`'s own REFUSED reasons). The third bucket
is neither a shape gap nor a vocabulary gap; no lexicon or curriculum batch
can move it, so folding it into "mechanism" would misdirect exactly the
signal this instrument exists to make legible.

**Deduction composer — every READER/gate refusal is mechanism-class.**
All ~20 typed shape reasons across the six bands
(`generate/proof_chain/{english,member,cond_member,verb,exist}.py`, plus
the shared reader `generate/meaning_graph/reader.py`) name a closed-grammar
SHAPE the reader will not attempt (``sentence_shape_out_of_band``,
``quantifier_out_of_band``, ``mixed_structure_out_of_band``, ...). None of
them names a missing vocabulary term — these bands read a small closed set
of connective/quantifier words, not open vocabulary, so there is no
vocabulary axis for them to refuse on yet. A future band that reads open
English prose would change this; today this instrument would correctly
report 0 coverage-class deduction refusals, and that is the honest count,
not a bug in the classifier. A deduction argument CAN still decline
engine-side (inconsistent premises) after being read just fine by any band,
including Band v1 itself — see ``deduction_refusal_reason``.

**Curriculum composer — has a real coverage axis.**
`chat/curriculum_surface.py::resolve_domain` refuses ``untaught_vocabulary``
when a query's subject/object term is not in ANY served subject's mounted
vocabulary, and `resolve_family` refuses ``out_of_curriculum`` when the
relation itself was never taught. Both name an absent TERM/RELATION, not an
unreadable shape — coverage-class by the brief's own naming.
``ambiguous_reading`` and ``empty_curriculum`` are arguably vocabulary-
adjacent (the terms ARE taught) but were not named as coverage-class by the
brief, so this instrument does not invent that reclassification — they
stay mechanism-class; see ``_CURRICULUM_COVERAGE_REASONS`` for the exact
closed set of what IS treated as coverage.

Usage — before/after a lexicon or curriculum batch::

    uv run python -m evals.vocab_trigger_instrument --report before.json
    # ... add ratified vocabulary/curriculum content ...
    uv run python -m evals.vocab_trigger_instrument --report after.json
    uv run python -m evals.vocab_trigger_instrument --compare before.json --report after.json

The last form is the admissions-per-batch counter: it re-runs the instrument
against the CURRENT corpora and prints the admitted-count delta against a
prior snapshot, per composer.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, Protocol, runtime_checkable

from chat.curriculum_surface import decide_curriculum_question
from chat.deduction_surface import looks_like_deductive_argument
from evals.deduction_serve.runner import decide as decide_deduction
from generate.meaning_graph.projectors import to_deductive_logic, to_syllogism
from generate.meaning_graph.reader import Comprehension, comprehend
from generate.proof_chain.categorical import CategoricalError, decide_syllogism
from generate.proof_chain.cond_member import CondMemberArgument, read_cond_member_argument
from generate.proof_chain.english import EnglishArgument, read_english_argument
from generate.proof_chain.entail import (
    INCONSISTENT_PREMISES,
    OUT_OF_REGIME_OR_MALFORMED,
    Entailment,
    evaluate_entailment_with_trace,
)
from generate.proof_chain.exist import ExistArgument, read_exist_argument
from generate.proof_chain.member import MemberArgument, read_member_argument
from generate.proof_chain.verb import VerbArgument, read_verb_argument

#: The engine's REFUSED-only reasons (`generate/proof_chain/entail.py`'s
#: closed vocabulary also contains entailed/refuted/unknown reasons under the
#: same ``ENTAILMENT_REASONS`` set; only these two are ever attached to a
#: REFUSED verdict, which is the only outcome that reaches this classifier).
_ENGINE_REFUSED_REASONS: frozenset[str] = frozenset(
    {INCONSISTENT_PREMISES, OUT_OF_REGIME_OR_MALFORMED}
)

#: Three buckets, not two: a decline is either a READER/gate refusal on an
#: unreadable SHAPE ("mechanism"), a composer refusal on an absent TERM or
#: RELATION ("coverage"), or a fully-read, well-formed argument the ROBDD
#: engine itself declines because its premises are inconsistent or the
#: structure is outside the decidable regime ("engine_refused" —
#: `generate/proof_chain/entail.py`'s own REFUSED reasons). The third bucket
#: is neither a shape gap nor a vocabulary gap — expanding a lexicon or a
#: curriculum cannot move it, so lumping it into "mechanism" would misdirect
#: exactly the trigger this instrument exists to make legible.
RefusalClass = Literal["mechanism", "coverage", "engine_refused"]

#: The curriculum composer's own closed reason vocabulary that names an
#: absent TERM or RELATION rather than an unreadable shape (module docstring).
_CURRICULUM_COVERAGE_REASONS: frozenset[str] = frozenset(
    {"untaught_vocabulary", "out_of_curriculum"}
)

@runtime_checkable
class _DecidableArgument(Protocol):
    """The shape every band's ``*Argument`` success type shares
    (`generate/proof_chain/{english,member,cond_member,verb,exist}.py`) —
    named here so the fallback loop below can call
    ``evaluate_entailment_with_trace`` without a per-band branch. Declared
    as read-only properties, not plain attributes: every concrete
    ``*Argument`` is a frozen dataclass, and a mutable Protocol attribute is
    incompatible with a read-only frozen field."""

    @property
    def premise_formulas(self) -> tuple[str, ...]: ...

    @property
    def query_formula(self) -> str: ...


#: The deduction fallback cascade, in the exact order
#: ``chat/deduction_surface.py`` tries them, paired with the ``Argument``
#: type each reader returns on success (vs. a typed ``*Refusal`` on decline).
_DEDUCTION_BAND_READERS: tuple[
    tuple[str, Callable[[str], Any], type[_DecidableArgument]], ...
] = (
    ("v2_en", read_english_argument, EnglishArgument),
    ("v3_mem", read_member_argument, MemberArgument),
    ("v4_condmem", read_cond_member_argument, CondMemberArgument),
    ("v5_verb", read_verb_argument, VerbArgument),
    ("v6_exist", read_exist_argument, ExistArgument),
)


def _engine_reason(premise_formulas: tuple[str, ...], query_formula: str) -> str | None:
    """The engine's REFUSED reason for an already-admitted argument, or
    ``None`` when the engine reached a definite verdict (entailed/refuted/
    unknown) — i.e. this band did NOT decline it; something downstream in
    the cascade order already claimed the case before this point is reached
    in practice, but the caller still checks."""
    trace = evaluate_entailment_with_trace(premise_formulas, query_formula)
    return trace.reason if trace.outcome is Entailment.REFUSED else None


def refusal_class_deduction(reason: str) -> RefusalClass:
    """A reason from the engine's closed REFUSED vocabulary is engine-level
    (inconsistent premises / out of regime) regardless of WHICH band parsed
    the argument before handing it to the engine — any of the seven bands
    can admit a well-formed but inconsistent argument. Everything else is a
    reader/gate SHAPE refusal; no deduction band refuses on vocabulary
    (module docstring)."""
    if reason in _ENGINE_REFUSED_REASONS:
        return "engine_refused"
    return "mechanism"


def refusal_class_curriculum(reason: str) -> RefusalClass:
    """``untaught_vocabulary`` / ``out_of_curriculum`` are coverage-class;
    the engine's own REFUSED reasons (reachable here too — the curriculum
    composer runs the same ROBDD engine over compiled premises) are
    engine-level; every other typed curriculum reason is mechanism-class."""
    if reason in _CURRICULUM_COVERAGE_REASONS:
        return "coverage"
    if reason in _ENGINE_REFUSED_REASONS:
        return "engine_refused"
    return "mechanism"


def deduction_refusal_reason(text: str) -> tuple[str, str]:
    """``(band, reason)`` this text declined at — the band whose engine
    verdict or reader refusal produced the decline
    :func:`evals.deduction_serve.runner.decide` already reported. Mirrors
    ``chat/deduction_surface.py``'s FULL cascade, including Band v1/v1b
    (which the production composer's surface never exposes a reason for
    either — an inconsistent-premises decline there renders the same generic
    wording as a reader refusal) — recovering the typed reason precisely is
    the reason this function exists at all."""
    if not looks_like_deductive_argument(text):
        return "gate", "not_argument_shaped"
    comp = comprehend(text)
    if isinstance(comp, Comprehension):
        projected = to_deductive_logic(comp)
        if projected is not None:
            premises, query = projected
            reason = _engine_reason(premises, query)
            return "v1", reason or ""  # pragma: no cover - decide() said declined
        syllogism = to_syllogism(comp)
        if syllogism is not None:
            structure, s_query = syllogism
            try:
                trace = decide_syllogism(structure, s_query)
            except CategoricalError as exc:
                return "v1b", str(exc) or "categorical_error"
            reason = trace.reason if trace.outcome is Entailment.REFUSED else ""
            return "v1b", reason  # pragma: no cover - decide() said declined
        band, reason = "reader", ""
    else:
        band, reason = "reader", comp.reason
    for band_name, reader, argument_type in _DEDUCTION_BAND_READERS:
        arg = reader(text)
        if isinstance(arg, argument_type):
            engine_reason = _engine_reason(arg.premise_formulas, arg.query_formula)
            return band_name, engine_reason or ""  # pragma: no cover
        band, reason = band_name, arg.reason
    return band, reason


def curriculum_refusal_reason(text: str) -> str:
    """The typed reason ``decide_curriculum_question`` declined *text* for.

    ``decide_curriculum_question`` already carries ``.reason`` on its
    returned ``CurriculumDecision`` for every ``declined`` verdict (gate
    reasons AND the engine's own REFUSED reasons alike) — no second cascade
    walk needed here, unlike the deduction side."""
    return decide_curriculum_question(text).reason


@dataclass(frozen=True, slots=True)
class RefusalHistogram:
    """One composer's admitted/declined split, with declines broken out by
    typed reason and by mechanism-vs-coverage class."""

    n: int
    admitted: int
    declined: int
    by_reason: dict[str, int]
    by_class: dict[str, int]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "n": self.n,
            "admitted": self.admitted,
            "declined": self.declined,
            "by_reason": dict(sorted(self.by_reason.items())),
            "by_class": dict(sorted(self.by_class.items())),
        }


#: Split directories, discovered rather than duplicated from the runners'
#: own (module-private) split tuples — every ``<split>/cases.jsonl`` under
#: each lane root, sorted for determinism. ``deduction_serve/practice/`` and
#: ``curriculum_serve/oracle.py``'s directory carry no ``cases.jsonl`` and
#: are silently skipped by the glob, not filtered explicitly.
_DEDUCTION_ROOT = Path(__file__).resolve().parent / "deduction_serve"
_CURRICULUM_ROOT = Path(__file__).resolve().parent / "curriculum_serve"


def _load_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def _all_deduction_texts() -> list[str]:
    texts: list[str] = []
    for path in sorted(_DEDUCTION_ROOT.glob("*/cases.jsonl")):
        texts.extend(case["text"] for case in _load_jsonl(path))
    return texts


def _all_curriculum_texts() -> list[str]:
    texts: list[str] = []
    for path in sorted(_CURRICULUM_ROOT.glob("*/cases.jsonl")):
        texts.extend(case["text"] for case in _load_jsonl(path))
    return texts


def build_deduction_histogram(texts: list[str]) -> RefusalHistogram:
    by_reason: Counter[str] = Counter()
    by_class: Counter[str] = Counter()
    admitted = 0
    for text in texts:
        if decide_deduction(text) != "declined":
            admitted += 1
            continue
        band, reason = deduction_refusal_reason(text)
        by_reason[f"{band}:{reason}"] += 1
        by_class[refusal_class_deduction(reason)] += 1
    return RefusalHistogram(
        n=len(texts),
        admitted=admitted,
        declined=len(texts) - admitted,
        by_reason=dict(by_reason),
        by_class=dict(by_class),
    )


def build_curriculum_histogram(texts: list[str]) -> RefusalHistogram:
    by_reason: Counter[str] = Counter()
    by_class: Counter[str] = Counter()
    admitted = 0
    for text in texts:
        if decide_curriculum_question(text).verdict != "declined":
            admitted += 1
            continue
        reason = curriculum_refusal_reason(text)
        by_reason[reason] += 1
        by_class[refusal_class_curriculum(reason)] += 1
    return RefusalHistogram(
        n=len(texts),
        admitted=admitted,
        declined=len(texts) - admitted,
        by_reason=dict(by_reason),
        by_class=dict(by_class),
    )


def build_report() -> dict[str, Any]:
    """The deterministic, pinnable snapshot over the CURRENT committed lane
    corpora (`evals/deduction_serve/*/cases.jsonl`,
    `evals/curriculum_serve/*/cases.jsonl`) — pure over those files and the
    production decision paths, so two runs against the same commit produce
    byte-identical JSON."""
    deduction = build_deduction_histogram(_all_deduction_texts())
    curriculum = build_curriculum_histogram(_all_curriculum_texts())
    combined_class: Counter[str] = Counter()
    combined_class.update(deduction.by_class)
    combined_class.update(curriculum.by_class)
    return {
        "schema_version": 1,
        "instrument": "vocab_trigger",
        "deduction": deduction.to_json_dict(),
        "curriculum": curriculum.to_json_dict(),
        "combined": {
            "admitted": deduction.admitted + curriculum.admitted,
            "declined": deduction.declined + curriculum.declined,
            "by_class": dict(sorted(combined_class.items())),
        },
    }


def write_report(path: Path) -> dict[str, Any]:
    report = build_report()
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def admissions_delta(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    """The admissions-per-batch counter: per-composer admitted-count delta
    between two snapshots (``build_report``/``write_report`` output). Run
    once before a lexicon/curriculum batch, once after, and diff — this is
    the falsifiable measurement Option A of the audit's Q5 asks for, applied
    to whichever composer the batch targeted."""
    return {
        "deduction_admitted_delta": (
            after["deduction"]["admitted"] - before["deduction"]["admitted"]
        ),
        "curriculum_admitted_delta": (
            after["curriculum"]["admitted"] - before["curriculum"]["admitted"]
        ),
        "combined_admitted_delta": (
            after["combined"]["admitted"] - before["combined"]["admitted"]
        ),
    }


def _print_histogram(name: str, hist: RefusalHistogram) -> None:
    print(f"[{name}] n={hist.n} admitted={hist.admitted} declined={hist.declined}")
    print(f"    by_class: {dict(sorted(hist.by_class.items()))}")
    for reason, count in sorted(hist.by_reason.items()):
        print(f"      {reason}: {count}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--report", type=Path, default=None,
        help="write the deterministic JSON snapshot to this path",
    )
    parser.add_argument(
        "--compare", type=Path, default=None,
        help="a prior snapshot (from --report) to diff the current run against",
    )
    args = parser.parse_args(argv)

    report = build_report()
    if args.report is not None:
        write_report(args.report)

    if args.compare is not None:
        before = json.loads(args.compare.read_text(encoding="utf-8"))
        delta = admissions_delta(before, report)
        print(f"admissions since {args.compare}: {delta}")
        return 0

    _print_histogram("deduction", RefusalHistogram(**report["deduction"]))
    _print_histogram("curriculum", RefusalHistogram(**report["curriculum"]))
    print(f"[combined] {report['combined']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
