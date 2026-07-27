"""English-clause argument reader — Band v2-EN (ADR-0257).

Reads a natural-English deductive argument ("If it rains then the ground is
wet. It rains. Therefore the ground is wet.") into ``(premises, query)``
propositional formula strings over MINTED OPAQUE ATOM IDS (``a0``, ``a1``, …),
one id per distinct normalized clause. The clause text itself never enters a
formula — ``generate.logic_canonical`` treats ``and``/``or``/``not``/``implies``
as keyword operators, so clause text is lexically unsafe there; ids are always
safe, which frees clause-atoms from every lexical constraint (articles,
copulas, apostrophes, digits — all fine).

Why this is sound (the load-bearing argument, ADR-0257 §3):

  Propositional entailment is closed under uniform substitution of formulas
  for atoms. An ``ENTAILED`` / ``REFUTED`` / inconsistent-premises verdict
  computed over opaque clause-atoms therefore remains true under ANY deeper
  reading of those clauses — if the user mentally refines "the ground is wet"
  into richer structure, or identifies two clauses we kept distinct, every
  positive verdict still holds. The ONE verdict that is not substitution-safe
  is UNKNOWN ("doesn't settle"): internal clause structure we did not read
  could settle it. Serving therefore (a) renders UNKNOWN with an explicitly
  scoped phrasing ("reading each clause as one indivisible claim…"), and
  (b) refuses clauses whose surface form ANNOUNCES internal structure this
  band cannot read — quantifier-led categorical clauses, is-a membership
  clauses, and unnormalized negation — so a genuine syllogism can never be
  misread into a misleading "doesn't follow".

This reader is DELIBERATELY separate from ``generate.meaning_graph.reader``
(the shared 7-lane comprehension reader): argument-mode reading is only sound
because the "therefore" commit gate has already fired, so every clause is a
premise or conclusion BY POSITION. The shared reader's single-token floor and
reserved-word guard are load-bearing for its lanes' wrong=0 and are untouched.
The serving composer tries the shared reader's bands (v1/v1b) FIRST and falls
back here, so every previously-served argument is served byte-identically —
this band only widens.

Refusal-first, closed reason vocabulary (every ``EnglishRefusal.reason``):

  ``empty``, ``question_sentence``, ``no_conclusion``,
  ``multiple_conclusions``, ``conclusion_not_last``, ``no_premises``,
  ``empty_side``, ``nested_conditional``, ``ambiguous_and_or``,
  ``categorical_shape_out_of_band``, ``membership_shape_out_of_band``,
  ``internal_negation_unread``, ``structural_leak``,
  ``too_many_premises``, ``too_many_atoms``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from generate.lexicon import (
    COPULAS,
    NEGATION_BEARING,
    QUANTIFIER_LEAD,
    SENTENTIAL_NOT,
    STRUCTURAL,
)
from generate.proof_chain.shape import (
    EN_ATOMIC,
    EN_CONDITIONAL_CHAIN,
    EN_CONDITIONAL_SINGLE,
    EN_DISJUNCTIVE,
)

#: Sentence splitter — same shape as the shared reader's (body + terminator).
_SENTENCE_RE = re.compile(r"\s*([^.?!]+?)\s*([.?!])")

#: Structural function words. One may never survive into an opaque atom — a
#: leftover here means the clause has structure this grammar did not consume.
_STRUCTURAL = STRUCTURAL

#: Quantifier-led clause = categorical shape ("all whales are mammals") — real
#: internal structure the opaque band must NOT flatten (a valid syllogism read
#: as three opaque atoms would yield a misleading "doesn't follow"). Refused
#: here; the categorical band (v1b) is the honest home for these.
_QUANTIFIER_LEAD = QUANTIFIER_LEAD

#: Negation-bearing tokens inside a clause that this band cannot normalize.
#: Leaving one inside an opaque atom would hide a negation from the engine
#: ("it never rains" vs "it rains" would be unrelated atoms) — refuse instead.
#: This band deliberately EXCLUDES bare ``not``, which the copular rule below
#: normalizes — see ``lexicon.NEGATION_BEARING_WITH_NOT`` for the divergence.
_NEGATION_BEARING = NEGATION_BEARING

#: Copulas whose "<copula> not" form this band DOES normalize into ``~atom``.
_COPULAS = COPULAS

#: Contraction → expanded tokens (applied before parsing; deterministic).
_CONTRACTIONS = {
    "isn't": ("is", "not"),
    "aren't": ("are", "not"),
    "wasn't": ("was", "not"),
    "weren't": ("were", "not"),
}

#: The "it is not the case that <X>" sentential-negation prefix.
_SENTENTIAL_NOT = SENTENTIAL_NOT

#: Honesty caps — an argument beyond these is refused, not truncated.
MAX_PREMISE_SENTENCES = 16
MAX_ATOMS = 24


@dataclass(frozen=True, slots=True)
class EnglishArgument:
    """A successfully-read English argument, engine-ready.

    ``premise_formulas``/``query_formula`` are propositional formula strings
    over minted atom ids; ``atoms[i]`` is the normalized clause text of ``a{i}``.
    ``premise_texts``/``query_text`` are the normalized original sentences —
    the exact reading the surface's "Given:" line restates back to the user.
    """

    premise_formulas: tuple[str, ...]
    query_formula: str
    premise_texts: tuple[str, ...]
    query_text: str
    band: str
    atoms: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class EnglishRefusal:
    """A typed refusal — the argument is not honestly readable by this band."""

    reason: str
    detail: str = ""


class _Reject(Exception):
    def __init__(self, reason: str, detail: str = "") -> None:
        super().__init__(reason)
        self.refusal = EnglishRefusal(reason, detail)


class _AtomTable:
    """Mints one opaque id per distinct normalized clause (first-seen order)."""

    def __init__(self) -> None:
        self._ids: dict[str, str] = {}
        self._display: list[str] = []

    def mint(self, toks: list[str], detail: str) -> str:
        if not toks:
            raise _Reject("empty_side", detail)
        if toks[0] in _QUANTIFIER_LEAD:
            raise _Reject("categorical_shape_out_of_band", detail)
        for i, tok in enumerate(toks):
            if tok in _STRUCTURAL:
                raise _Reject("structural_leak", detail)
            if tok == "not" or tok.endswith("n't") or tok in _NEGATION_BEARING:
                raise _Reject("internal_negation_unread", detail)
            # "<X> is|are a|an <Y>" is a membership clause — internal structure
            # (an is-a fact), out of the opaque band by design.
            if tok in _COPULAS and i + 1 < len(toks) and toks[i + 1] in ("a", "an"):
                raise _Reject("membership_shape_out_of_band", detail)
        key = " ".join(toks)
        if key not in self._ids:
            if len(self._display) >= MAX_ATOMS:
                raise _Reject("too_many_atoms", key)
            self._ids[key] = f"a{len(self._display)}"
            self._display.append(key)
        return self._ids[key]

    @property
    def atoms(self) -> tuple[str, ...]:
        return tuple(self._display)


def _tokenize(body: str) -> list[str]:
    """Sentence body → normalized tokens: lowercased, comma-free, contractions
    expanded. Commas are treated as plain separators (the reading is disclosed
    verbatim in the surface's "Given:" line, so this is a stated normalization,
    not a hidden one)."""
    out: list[str] = []
    for raw in body.replace(",", " ").lower().split():
        out.extend(_CONTRACTIONS.get(raw, (raw,)))
    return out


def _split_on(toks: list[str], sep: str) -> list[list[str]]:
    parts: list[list[str]] = [[]]
    for tok in toks:
        if tok == sep:
            parts.append([])
        else:
            parts[-1].append(tok)
    return parts


def _parse_negatom(toks: list[str], table: _AtomTable, detail: str) -> str:
    """Negation-or-atom: sentential "it is not the case that", leading "not",
    copular "<L> is|are|was|were not <R>" (normalized to ``~atom(<L> <cop> <R>)``),
    else an opaque atom."""
    if tuple(toks[: len(_SENTENTIAL_NOT)]) == _SENTENTIAL_NOT:
        return f"~({_parse_negatom(toks[len(_SENTENTIAL_NOT):], table, detail)})"
    if toks and toks[0] == "not":
        return f"~({_parse_negatom(toks[1:], table, detail)})"
    if "not" in toks:
        i = toks.index("not")
        if i >= 2 and toks[i - 1] in _COPULAS:
            left, cop, right = toks[: i - 1], toks[i - 1], toks[i + 1 :]
            if not left or not right:
                raise _Reject("empty_side", detail)
            return f"~({table.mint([*left, cop, *right], detail)})"
        raise _Reject("internal_negation_unread", detail)
    return table.mint(toks, detail)


def _parse_junction(toks: list[str], table: _AtomTable, detail: str) -> str:
    """Or/and over negation-atoms. "either" is consumed before a disjunction;
    mixed top-level and+or refuses (English scope is genuinely ambiguous)."""
    if "if" in toks or "then" in toks:
        raise _Reject("nested_conditional", detail)
    if toks and toks[0] == "either" and "or" in toks:
        toks = toks[1:]
    has_or = "or" in toks
    has_and = "and" in toks
    if has_or and has_and:
        raise _Reject("ambiguous_and_or", detail)
    if has_or or has_and:
        sep, op = ("or", "|") if has_or else ("and", "&")
        parts = _split_on(toks, sep)
        if any(not p for p in parts):
            raise _Reject("empty_side", detail)
        return f" {op} ".join(f"({_parse_negatom(p, table, detail)})" for p in parts)
    return _parse_negatom(toks, table, detail)


def _parse_node(toks: list[str], table: _AtomTable, detail: str) -> str:
    """One full clause: ``if <A> then <B>`` (junctions allowed on both sides,
    no nested conditionals) or a junction."""
    if toks and toks[0] == "if":
        if "then" not in toks:
            raise _Reject("nested_conditional", detail)
        then_idx = toks.index("then")
        antecedent = toks[1:then_idx]
        consequent = toks[then_idx + 1 :]
        if not antecedent or not consequent:
            raise _Reject("empty_side", detail)
        left = _parse_junction(antecedent, table, detail)
        right = _parse_junction(consequent, table, detail)
        return f"({left}) -> ({right})"
    return _parse_junction(toks, table, detail)


def _parse_premise(toks: list[str], table: _AtomTable, detail: str) -> list[str]:
    """A premise sentence → one or more formulas. A top-level conjunction
    ("<A> and <B>.") is split into separate premises — identical to conjoining,
    and it keeps premise formulas in the same connective inventory the
    shape-bands classify over."""
    if toks and toks[0] != "if" and "and" in toks and "or" not in toks and "if" not in toks:
        parts = _split_on(toks, "and")
        if any(not p for p in parts):
            raise _Reject("empty_side", detail)
        return [_parse_negatom(p, table, detail) for p in parts]
    return [_parse_node(toks, table, detail)]


def _classify_en_band(premise_formulas: tuple[str, ...]) -> str:
    """Structural shape-band over the PREMISES (same axis discipline as
    ``classify_deduction_shape``, namespaced ``en_`` because the READER is
    different — a band's earned license certifies reader fidelity, so a new
    reader must earn its own record per shape (ADR-0256/0257)."""
    if any("|" in p for p in premise_formulas):
        return EN_DISJUNCTIVE
    n_conditional = sum(1 for p in premise_formulas if "->" in p)
    if n_conditional >= 2:
        return EN_CONDITIONAL_CHAIN
    if n_conditional == 1:
        return EN_CONDITIONAL_SINGLE
    return EN_ATOMIC


def read_english_argument(text: str) -> EnglishArgument | EnglishRefusal:
    """Read *text* as an English-clause deductive argument, or refuse (typed).

    Deterministic and pure: same text → same ``EnglishArgument`` (atom ids are
    minted in first-appearance order). The conclusion is the final sentence and
    must be the only "therefore"-led sentence; every earlier sentence is a
    premise. All structure recognition is by closed function-word grammar —
    clause content is never interpreted, only quoted back.
    """
    if not text or not text.strip():
        return EnglishRefusal("empty")
    sentences = [
        (m.group(1), m.group(2)) for m in _SENTENCE_RE.finditer(text) if m.group(1).strip()
    ]
    if not sentences:
        return EnglishRefusal("empty")

    table = _AtomTable()
    premise_formulas: list[str] = []
    premise_texts: list[str] = []
    query_formula: str | None = None
    query_text: str | None = None

    try:
        for idx, (body, terminator) in enumerate(sentences):
            if terminator == "?":
                raise _Reject("question_sentence", body)
            toks = _tokenize(body)
            if not toks:
                continue
            if toks[0] == "therefore":
                if query_formula is not None:
                    raise _Reject("multiple_conclusions", body)
                if idx != len(sentences) - 1:
                    raise _Reject("conclusion_not_last", body)
                rest = toks[1:]
                if not rest:
                    raise _Reject("empty_side", body)
                query_formula = _parse_node(rest, table, body)
                query_text = " ".join(rest)
                continue
            if len(premise_texts) >= MAX_PREMISE_SENTENCES:
                raise _Reject("too_many_premises", body)
            premise_formulas.extend(_parse_premise(toks, table, body))
            premise_texts.append(" ".join(toks))
    except _Reject as rej:
        return rej.refusal

    if query_formula is None or query_text is None:
        return EnglishRefusal("no_conclusion")
    if not premise_formulas:
        return EnglishRefusal("no_premises")

    formulas = tuple(premise_formulas)
    return EnglishArgument(
        premise_formulas=formulas,
        query_formula=query_formula,
        premise_texts=tuple(premise_texts),
        query_text=query_text,
        band=_classify_en_band(formulas),
        atoms=table.atoms,
    )


__all__ = [
    "MAX_ATOMS",
    "MAX_PREMISE_SENTENCES",
    "EnglishArgument",
    "EnglishRefusal",
    "read_english_argument",
]
