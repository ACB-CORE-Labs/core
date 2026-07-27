"""Member-argument reader — Band v3-MEM (ADR-0258).

Reads the classic instantiation syllogism — "Socrates is a man. All men are
mortal. Therefore Socrates is mortal." — by **per-individual propositional
lowering**: one opaque minted atom (``a0``, ``a1``, …) per *(individual,
class)* pair, with every universal premise instantiated at every named
individual (``A(C1,C2)`` ⇒ ``mem(i,C1) -> mem(i,C2)``; ``E(C1,C2)`` ⇒
``mem(i,C1) -> ~mem(i,C2)``). The same verified ROBDD engine decides.

Why this is sound (ADR-0258 §3): universal instantiation at named individuals
is truth-preserving in every first-order model, so ENTAILED / REFUTED /
inconsistent verdicts over the lowered premises hold in every model of the
original argument — and both survive co-reference of distinct names, since
that only ADDS premises and entailment is monotone. For this closed fragment
(singular literals + A/E universals, singular conclusion, Boolean reading)
the lowering is also COMPLETE: a propositional countermodel lifts to a
first-order countermodel whose domain is exactly the named individuals, so
UNKNOWN means genuinely not forced within the disclosed reading. The UNKNOWN
surface still scopes itself (names read as distinct individuals, class words
at face value), and every sentence shape announcing structure this band
cannot read refuses out of band, typed.

Number linking — the ONE semantic identification this band performs: a
universal's class word is usually plural ("all men") while the singular fact
uses the singular ("a man"). Two attested class forms are identified iff
related token-wise by a CLOSED relation: the irregular/invariant table below
(consulted first — table membership makes it the sole authority for that
token, killing over-link hazards like specie/species and new/news), else the
three regular suffix rules (``+s``, ``+es`` after sibilants, ``y↔ies``).
Anything the relation cannot relate stays distinct — under-linking costs
coverage, never soundness.

This reader is used ONLY by the deduction serving path, strictly AFTER Bands
v1 / v1b / v2-EN — pure widening; every previously-served argument is served
byte-identically. Refusal-first, closed reason vocabulary:

  ``empty``, ``question_sentence``, ``no_conclusion``,
  ``multiple_conclusions``, ``conclusion_not_last``, ``no_premises``,
  ``empty_side``, ``quantifier_out_of_band``, ``bare_plural_out_of_band``,
  ``definite_description_out_of_band``, ``relative_clause_out_of_band``,
  ``universal_conclusion_out_of_band``, ``mixed_structure_out_of_band``,
  ``internal_negation_unread``, ``sentence_shape_out_of_band``,
  ``structural_leak``, ``too_many_premises``, ``too_many_atoms``.
"""

from __future__ import annotations

from dataclasses import dataclass

# The v2-EN sentence splitter and tokenizer are reused VERBATIM (one
# normalization discipline, no drift between the English-argument bands) —
# a deliberate private-name import inside the proof_chain package.
from generate.lexicon import (
    CONNECTIVES,
    COPULA_FORMS,
    IRREGULAR_SINGULARS,
    NEGATION_BEARING_WITH_NOT,
    QUANTIFIER_TOKENS,
    SENTENTIAL_NOT,
)
from generate.proof_chain.english import _SENTENCE_RE, _tokenize
from generate.proof_chain.shape import (
    EN_MEMBER_ATOMIC,
    EN_MEMBER_CHAIN,
    EN_MEMBER_NEGATIVE,
    EN_MEMBER_SINGLE,
)

#: Universal-affirmative sentence leads (A-form) and the E-form lead.
_A_LEADS = frozenset({"all", "every", "each"})
_E_LEAD = "no"

#: Quantifier tokens (determiners AND pronouns) this band cannot lower —
#: existential/plurality readings refuse rather than misread "everyone" or
#: "some men" as an individual. A/E leads are dispatched before this check.
_QUANTIFIER_TOKENS = QUANTIFIER_TOKENS

#: Connective structure this band does not compose (a future band fuses the
#: v2-EN connective grammar with these sentence readings — ADR-0258 §6.1).
_CONNECTIVES = CONNECTIVES

#: Negation-bearing tokens with no normalized reading here (only the copular
#: ``is not`` slot and the sentential prefix are normalized).
_NEGATION_BEARING = NEGATION_BEARING_WITH_NOT

#: Relative-clause markers — internal structure a name/class run must not hide.
_RELATIVE_MARKERS = frozenset({"that", "which", "who", "whom", "whose"})

#: All copular forms recognized for DISPATCH; only ``is``/``are`` are in-band
#: (tense is a deliberate scope-out — ADR-0258 §6.3).
_COPULA_FORMS = COPULA_FORMS

#: The "it is not the case that <singular>" sentential-negation prefix.
_SENTENTIAL_NOT = SENTENTIAL_NOT

#: Honesty caps — beyond these the argument is refused, never truncated.
#: ``MAX_ATOMS`` counts minted (individual, class) pairs, so instantiation
#: fan-out (individuals × classes) is capped exactly where it multiplies.
MAX_PREMISE_SENTENCES = 16
MAX_ATOMS = 24

#: Closed irregular/invariant number table (plural → singular; an INVARIANT
#: form maps to itself). Consulted BEFORE the regular suffix rules: if either
#: token of a candidate pair appears anywhere in this table, the table is the
#: only authority for that pair — which is what keeps ``species``/``specie``
#: and ``news``/``new`` unlinked. CORE's first morphology table; promoted to
#: a ratified pack when the tri-language siblings land (ADR-0258 §5).
_IRREGULAR_PLURALS: dict[str, str] = IRREGULAR_SINGULARS
_TABLE_TOKENS = frozenset(_IRREGULAR_PLURALS) | frozenset(_IRREGULAR_PLURALS.values())

_SIBILANT_ENDINGS = ("s", "x", "z", "ch", "sh")


@dataclass(frozen=True, slots=True)
class MemberArgument:
    """A successfully-read member argument, engine-ready.

    ``premise_formulas``/``query_formula`` are propositional formula strings
    over minted atom ids; ``atoms[i]`` displays the *(individual, class)*
    pair behind ``a{i}``. ``premise_texts``/``query_text`` are the normalized
    original sentences — the exact reading the surface restates to the user.
    """

    premise_formulas: tuple[str, ...]
    query_formula: str
    premise_texts: tuple[str, ...]
    query_text: str
    band: str
    atoms: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class MemberRefusal:
    """A typed refusal — the argument is not honestly readable by this band."""

    reason: str
    detail: str = ""


class _Reject(Exception):
    def __init__(self, reason: str, detail: str = "") -> None:
        super().__init__(reason)
        self.refusal = MemberRefusal(reason, detail)


@dataclass(frozen=True, slots=True)
class _Singular:
    """``<NAME> is [not] [a|an] <CLASS>`` — a literal about one individual."""

    ind: tuple[str, ...]
    cls: tuple[str, ...]
    negated: bool


@dataclass(frozen=True, slots=True)
class _Universal:
    """``all|every|each|no <C1> are|is [a|an] <C2>`` — instantiated per
    individual at lowering time. ``negative`` marks the E-form (``no``)."""

    subject: tuple[str, ...]
    predicate: tuple[str, ...]
    negative: bool


def _tokens_link(a: str, b: str) -> bool:
    """True iff single tokens *a* and *b* are number-forms of one class word
    under the closed relation (irregular/invariant table first, then the
    three regular suffix rules)."""
    if a == b:
        return True
    if a in _TABLE_TOKENS or b in _TABLE_TOKENS:
        return _IRREGULAR_PLURALS.get(a) == b or _IRREGULAR_PLURALS.get(b) == a
    short, long_ = (a, b) if len(a) <= len(b) else (b, a)
    if long_ == short + "s" and not short.endswith(_SIBILANT_ENDINGS):
        return True
    if long_ == short + "es" and short.endswith(_SIBILANT_ENDINGS):
        return True
    if short.endswith("y") and long_ == short[:-1] + "ies":
        return True
    return False


def _forms_link(a: tuple[str, ...], b: tuple[str, ...]) -> bool:
    """Multi-token class forms link token-wise (head-noun pluralization —
    "guard dogs" ↔ "guard dog"); differing lengths never link."""
    return len(a) == len(b) and all(_tokens_link(x, y) for x, y in zip(a, b))


def _check_run(toks: tuple[str, ...], detail: str) -> None:
    """Guard an opaque name/class token run: structure it must not hide
    refuses out of band, typed. Order matters — quantifier pronouns
    (``nobody``) are quantifier refusals, not negation refusals."""
    if not toks:
        raise _Reject("empty_side", detail)
    for tok in toks:
        if tok == "therefore":
            raise _Reject("structural_leak", detail)
        if tok in _RELATIVE_MARKERS:
            raise _Reject("relative_clause_out_of_band", detail)
        if tok in _QUANTIFIER_TOKENS:
            raise _Reject("quantifier_out_of_band", detail)
        if tok in _NEGATION_BEARING or tok.endswith("n't"):
            raise _Reject("internal_negation_unread", detail)
        if tok in _COPULA_FORMS:
            raise _Reject("sentence_shape_out_of_band", detail)


def _parse_universal(toks: list[str], detail: str) -> _Universal:
    negative = toks[0] == _E_LEAD
    rest = toks[1:]
    cop_idx = next((i for i, t in enumerate(rest) if t in ("is", "are")), None)
    if cop_idx is None:
        raise _Reject("sentence_shape_out_of_band", detail)
    subject = rest[:cop_idx]
    if subject and subject[0] == "the":  # "all the dogs" — determiner, dropped
        subject = subject[1:]
    predicate = rest[cop_idx + 1 :]
    if predicate and predicate[0] == "not":
        # "All men are not mortal" — genuinely scope-ambiguous English
        # (¬∀ vs ∀¬); refuse rather than guess. E-form ("no …") is the
        # unambiguous spelling this band reads.
        raise _Reject("internal_negation_unread", detail)
    if predicate and predicate[0] in ("a", "an"):
        predicate = predicate[1:]
    elif predicate and predicate[0] == "the":
        raise _Reject("definite_description_out_of_band", detail)
    _check_run(tuple(subject), detail)
    _check_run(tuple(predicate), detail)
    return _Universal(tuple(subject), tuple(predicate), negative)


def _parse_singular(toks: list[str], detail: str) -> _Singular:
    if tuple(toks[: len(_SENTENTIAL_NOT)]) == _SENTENTIAL_NOT:
        inner = _parse_singular(toks[len(_SENTENTIAL_NOT) :], detail)
        return _Singular(inner.ind, inner.cls, negated=not inner.negated)
    cop_idx = next((i for i, t in enumerate(toks) if t in _COPULA_FORMS), None)
    if cop_idx is None or toks[cop_idx] in ("was", "were"):
        raise _Reject("sentence_shape_out_of_band", detail)
    if toks[cop_idx] == "are":
        # "Dogs are loyal" — a bare-plural generic is an implicit universal
        # this band refuses to guess (ADR-0258 §3).
        raise _Reject("bare_plural_out_of_band", detail)
    name = tuple(toks[:cop_idx])
    rhs = toks[cop_idx + 1 :]
    negated = False
    if rhs and rhs[0] == "not":
        negated = True
        rhs = rhs[1:]
    if rhs and rhs[0] in ("a", "an"):
        rhs = rhs[1:]
    elif rhs and rhs[0] == "the":
        # "Socrates is the philosopher" — identity via definite description,
        # not class membership (ADR-0258 §6.4).
        raise _Reject("definite_description_out_of_band", detail)
    _check_run(name, detail)
    _check_run(tuple(rhs), detail)
    return _Singular(name, tuple(rhs), negated)


def _parse_sentence(toks: list[str], detail: str) -> _Singular | _Universal:
    if any(t in _CONNECTIVES for t in toks):
        raise _Reject("mixed_structure_out_of_band", detail)
    head = toks[0]
    if head in _A_LEADS or head == _E_LEAD:
        return _parse_universal(toks, detail)
    if head in _QUANTIFIER_TOKENS:
        raise _Reject("quantifier_out_of_band", detail)
    return _parse_singular(toks, detail)


def read_member_argument(text: str) -> MemberArgument | MemberRefusal:
    """Read *text* as a member argument, or refuse (typed).

    Deterministic and pure: same text → same ``MemberArgument``. The
    conclusion is the final sentence, the sole "therefore"-led one, and must
    be singular; every earlier sentence is a premise. Lowering is two-pass —
    sentences parse first, then universals instantiate at every named
    individual (so a universal may precede the individuals it binds) — with
    premise formulas emitted in sentence order and atom ids minted in
    emission order.
    """
    if not text or not text.strip():
        return MemberRefusal("empty")
    sentences = [
        (m.group(1), m.group(2)) for m in _SENTENCE_RE.finditer(text) if m.group(1).strip()
    ]
    if not sentences:
        return MemberRefusal("empty")

    premises: list[_Singular | _Universal] = []
    premise_texts: list[str] = []
    conclusion: _Singular | None = None
    query_text: str | None = None

    try:
        for idx, (body, terminator) in enumerate(sentences):
            if terminator == "?":
                raise _Reject("question_sentence", body)
            toks = _tokenize(body)
            if not toks:
                continue
            if toks[0] == "therefore":
                if conclusion is not None:
                    raise _Reject("multiple_conclusions", body)
                if idx != len(sentences) - 1:
                    raise _Reject("conclusion_not_last", body)
                rest = toks[1:]
                if not rest:
                    raise _Reject("empty_side", body)
                parsed = _parse_sentence(rest, body)
                if not isinstance(parsed, _Singular):
                    raise _Reject("universal_conclusion_out_of_band", body)
                conclusion = parsed
                query_text = " ".join(rest)
                continue
            if len(premises) >= MAX_PREMISE_SENTENCES:
                raise _Reject("too_many_premises", body)
            premises.append(_parse_sentence(toks, body))
            premise_texts.append(" ".join(toks))

        if conclusion is None or query_text is None:
            return MemberRefusal("no_conclusion")
        if not premises:
            return MemberRefusal("no_premises")

        # --- lowering (ADR-0258 §2) ------------------------------------------
        records: list[_Singular | _Universal] = [*premises, conclusion]

        # Named individuals, first-appearance order.
        individuals: list[tuple[str, ...]] = []
        for rec in records:
            if isinstance(rec, _Singular) and rec.ind not in individuals:
                individuals.append(rec.ind)

        # Class groups: each attested form joins the FIRST group whose
        # representative (its first-attested form) it links to — greedy,
        # deterministic, closed.
        group_of: dict[tuple[str, ...], int] = {}
        reps: list[tuple[str, ...]] = []
        for rec in records:
            forms = (
                [rec.cls] if isinstance(rec, _Singular) else [rec.subject, rec.predicate]
            )
            for form in forms:
                if form in group_of:
                    continue
                for gi, rep in enumerate(reps):
                    if _forms_link(form, rep):
                        group_of[form] = gi
                        break
                else:
                    group_of[form] = len(reps)
                    reps.append(form)

        mint: dict[tuple[int, int], str] = {}
        atom_display: list[str] = []

        def atom_for(ind_idx: int, group: int, detail: str) -> str:
            key = (ind_idx, group)
            if key not in mint:
                if len(atom_display) >= MAX_ATOMS:
                    raise _Reject("too_many_atoms", detail)
                mint[key] = f"a{len(atom_display)}"
                atom_display.append(
                    f"{' '.join(individuals[ind_idx])} : {' '.join(reps[group])}"
                )
            return mint[key]

        premise_formulas: list[str] = []
        for rec, body_text in zip(premises, premise_texts):
            if isinstance(rec, _Singular):
                atom = atom_for(individuals.index(rec.ind), group_of[rec.cls], body_text)
                premise_formulas.append(f"~({atom})" if rec.negated else atom)
                continue
            for ind_idx in range(len(individuals)):
                antecedent = atom_for(ind_idx, group_of[rec.subject], body_text)
                consequent = atom_for(ind_idx, group_of[rec.predicate], body_text)
                premise_formulas.append(
                    f"({antecedent}) -> (~({consequent}))"
                    if rec.negative
                    else f"({antecedent}) -> ({consequent})"
                )
        query_atom = atom_for(
            individuals.index(conclusion.ind), group_of[conclusion.cls], query_text
        )
        query_formula = f"~({query_atom})" if conclusion.negated else query_atom
    except _Reject as rej:
        return rej.refusal

    n_universal = sum(1 for r in premises if isinstance(r, _Universal))
    n_negative = sum(
        1 for r in premises if isinstance(r, _Universal) and r.negative
    )
    if n_negative:
        band = EN_MEMBER_NEGATIVE
    elif n_universal >= 2:
        band = EN_MEMBER_CHAIN
    elif n_universal == 1:
        band = EN_MEMBER_SINGLE
    else:
        band = EN_MEMBER_ATOMIC

    return MemberArgument(
        premise_formulas=tuple(premise_formulas),
        query_formula=query_formula,
        premise_texts=tuple(premise_texts),
        query_text=query_text,
        band=band,
        atoms=tuple(atom_display),
    )


__all__ = [
    "MAX_ATOMS",
    "MAX_PREMISE_SENTENCES",
    "MemberArgument",
    "MemberRefusal",
    "read_member_argument",
]
