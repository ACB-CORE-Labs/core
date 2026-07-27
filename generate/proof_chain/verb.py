"""Verb-predicate argument reader — Band v5-VP (ADR-0260).

Reads deductive arguments whose facts are VERB sentences — "All philosophers
teach. Socrates is a philosopher. Therefore Socrates teaches." — by extending
Band v3-MEM's per-individual propositional lowering with a second atom family:
one opaque minted atom per *(individual, verb-lemma-group, object-term)*
triple, alongside v3-MEM's *(individual, class-group)* membership atoms, in
ONE shared atom space. A verb universal ("all C <verb> [obj]", "no C <verb>
[obj]") instantiates at every named individual as ``mem(i,C) -> [~]verb(i)``,
so a membership fact minted by the copula reading can discharge a verb rule —
the fusion this band exists for. The same verified ROBDD engine decides.

Why this is sound (ADR-0260 §3): identical to ADR-0258 §3's argument.
Universal instantiation at named individuals is truth-preserving in every
first-order model; each *(verb-group, object-term)* pair is one opaque unary
predicate over the same named-individual domain, so ENTAILED / REFUTED /
inconsistent verdicts over the lowered premises hold in every model of the
original argument. Completeness within the fragment lifts the same way: a
propositional countermodel becomes a first-order countermodel whose domain is
exactly the named individuals. The ONE semantic identification added over
v3-MEM is third-person-singular agreement — a universal's base verb form
("teach") and a singular fact's 3sg form ("teaches") are identified iff
related by a CLOSED relation: a verb-specific irregular table (consulted
first, sole authority for its tokens) else the three regular suffix rules
(``+s``, ``+es`` after sibilants, ``y↔ies``). NOUN morphology is deliberately
NOT reused for verbs — the noun table would misroute forms like "lives"
(noun: life; verb: live). Anything the relation cannot relate stays distinct:
under-linking costs coverage, never soundness. Object terms link by exact
token identity only.

Segmentation is scope-tight by design: without a lexicon there is no sound
way to split an arbitrary copula-free token run into subject/verb/object, so
this band reads EXACTLY ``<name> <verb>``, ``<name> <verb> <object>``, their
``does not`` negations, the sentential-not prefix, and universals
``all|every|each|no [the] <class> <verb> [<object>]`` — single-token name,
class, verb, and object. Everything longer or differently shaped refuses,
typed. Copula sentences delegate VERBATIM to v3-MEM's own ``_parse_singular``
/ ``_parse_universal`` (membership facts and is-a universals coexist with
verb sentences in one argument). Connective composition with verb leaves is a
deliberate scope-out (ADR-0260 §5) — any connective token refuses.

Tried strictly AFTER Bands v1 / v1b / v2-EN / v3-MEM / v4-CM (a fallback
tier) — pure widening; every previously-served argument is served
byte-identically. (v2-EN decides pure verb-fact restatements as opaque
clause-atoms already — soundly — so every argument that reaches this band
contains a quantifier lead, an is-a shape, or unnormalized negation that made
the earlier bands refuse.) Refusal-first, closed reason vocabulary:

  ``empty``, ``question_sentence``, ``no_conclusion``,
  ``multiple_conclusions``, ``conclusion_not_last``, ``no_premises``,
  ``empty_side``, ``quantifier_out_of_band``, ``bare_plural_out_of_band``,
  ``definite_description_out_of_band``, ``relative_clause_out_of_band``,
  ``universal_conclusion_out_of_band``, ``mixed_structure_out_of_band``,
  ``internal_negation_unread``, ``sentence_shape_out_of_band``,
  ``tense_out_of_band``, ``structural_leak``, ``too_many_premises``,
  ``too_many_atoms``.
"""

from __future__ import annotations

from dataclasses import dataclass

# The v2-EN sentence splitter and tokenizer are reused VERBATIM (one
# normalization discipline across every argument band), and v3-MEM's singular/
# universal copula parsers, token-run guard, noun-morphology linker, and
# sibilant set are reused VERBATIM — deliberate private-name imports inside
# the proof_chain package, same precedent as generate.proof_chain.member and
# generate.proof_chain.cond_member.
from generate.lexicon import CONNECTIVES
from generate.proof_chain.english import _SENTENCE_RE, _tokenize
from generate.proof_chain.member import (
    _A_LEADS,
    _COPULA_FORMS,
    _E_LEAD,
    _QUANTIFIER_TOKENS,
    _SENTENTIAL_NOT,
    _SIBILANT_ENDINGS,
    _Singular,
    _Universal,
    _check_run,
    _forms_link,
    _parse_singular,
    _parse_universal,
)
from generate.proof_chain.member import _Reject as _MemberReject
from generate.proof_chain.shape import (
    EN_VERB_CHAIN,
    EN_VERB_FACT,
    EN_VERB_NEGATIVE,
    EN_VERB_UNIVERSAL,
)

#: Connective structure this band does not compose (a future band fuses the
#: v2-EN/v4-CM connective grammar with verb sentences — ADR-0260 §5).
_CONNECTIVES = CONNECTIVES

#: Auxiliary/determiner tokens that can never BE the verb or object of an
#: in-band sentence. ``does`` is consumed only by the exact ``does not``
#: negation shape; ``did not`` is past tense (a scope-out); bare ``do not``
#: with a singular subject is not an in-band agreement pattern.
_ARTICLES = frozenset({"a", "an", "the"})
_AUXILIARIES = frozenset({"do", "does", "did"})

#: Closed irregular 3sg table (3sg form → base). Consulted BEFORE the regular
#: suffix rules; table membership makes it the sole authority for that token.
#: Deliberately verb-specific — the noun table (member.py) would misroute
#: forms like "lives" (noun: life; verb: live).
_VERB_IRREGULAR_3SG: dict[str, str] = {
    "has": "have",
    "goes": "go",
    "does": "do",
}
_VERB_TABLE_TOKENS = frozenset(_VERB_IRREGULAR_3SG) | frozenset(
    _VERB_IRREGULAR_3SG.values()
)

#: Honesty caps — beyond these the argument is refused, never truncated.
#: ``MAX_ATOMS`` counts minted atoms of BOTH families, so instantiation
#: fan-out is capped exactly where it multiplies.
MAX_PREMISE_SENTENCES = 16
MAX_ATOMS = 24


@dataclass(frozen=True, slots=True)
class VerbArgument:
    """A successfully-read verb-predicate argument, engine-ready.

    Same shape as ``MemberArgument``: ``premise_formulas``/``query_formula``
    are propositional formula strings over minted atom ids; ``atoms[i]``
    displays the fact behind ``a{i}`` (``individual : class`` for membership
    atoms, ``individual : verb [object]`` for verb atoms).
    """

    premise_formulas: tuple[str, ...]
    query_formula: str
    premise_texts: tuple[str, ...]
    query_text: str
    band: str
    atoms: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class VerbRefusal:
    """A typed refusal — the argument is not honestly readable by this band."""

    reason: str
    detail: str = ""


class _Reject(Exception):
    def __init__(self, reason: str, detail: str = "") -> None:
        super().__init__(reason)
        self.refusal = VerbRefusal(reason, detail)


@dataclass(frozen=True, slots=True)
class _VerbFact:
    """``<NAME> <verb3sg> [<object>]`` (optionally ``does not`` / sentential-
    not negated) — a verb literal about one individual."""

    ind: tuple[str, ...]
    verb: str
    obj: str | None
    negated: bool


@dataclass(frozen=True, slots=True)
class _VerbUniversal:
    """``all|every|each|no [the] <class> <verb> [<object>]`` — instantiated
    per individual at lowering time as ``mem(i, class) -> [~]verb(i)``.
    ``negative`` marks the E-form (``no``)."""

    subject: tuple[str, ...]
    verb: str
    obj: str | None
    negative: bool


_Record = _Singular | _Universal | _VerbFact | _VerbUniversal


def _verb_tokens_link(a: str, b: str) -> bool:
    """True iff single tokens *a* and *b* are agreement forms of one verb
    lemma under the closed relation (irregular table first, then the three
    regular 3sg suffix rules)."""
    if a == b:
        return True
    if a in _VERB_TABLE_TOKENS or b in _VERB_TABLE_TOKENS:
        return _VERB_IRREGULAR_3SG.get(a) == b or _VERB_IRREGULAR_3SG.get(b) == a
    short, long_ = (a, b) if len(a) <= len(b) else (b, a)
    if long_ == short + "s" and not short.endswith(_SIBILANT_ENDINGS):
        return True
    if long_ == short + "es" and short.endswith(_SIBILANT_ENDINGS):
        return True
    if short.endswith("y") and long_ == short[:-1] + "ies":
        return True
    return False


def _check_verb_token(tok: str, detail: str) -> None:
    """Guard the verb slot: the shared opaque-run guard plus the aux/article
    exclusions (an auxiliary or determiner is never an in-band verb lemma)."""
    _check_run((tok,), detail)
    if tok in _ARTICLES or tok in _AUXILIARIES:
        raise _Reject("sentence_shape_out_of_band", detail)


def _check_term_token(tok: str, detail: str) -> None:
    """Guard a name/object slot: the shared opaque-run guard plus a dangling-
    determiner check."""
    _check_run((tok,), detail)
    if tok in _ARTICLES:
        raise _Reject("sentence_shape_out_of_band", detail)


def _parse_verb_fact(toks: list[str], detail: str) -> _VerbFact:
    """``<name> <verb> [<obj>]`` / ``<name> does not <verb> [<obj>]``."""
    negated = False
    if len(toks) >= 3 and toks[1] in _AUXILIARIES and toks[2] == "not":
        if toks[1] == "did":
            raise _Reject("tense_out_of_band", detail)
        if toks[1] == "do":
            raise _Reject("sentence_shape_out_of_band", detail)
        negated = True
        toks = [toks[0], *toks[3:]]
    if any(t == "not" or t.endswith("n't") for t in toks):
        raise _Reject("internal_negation_unread", detail)
    if len(toks) < 2 or len(toks) > 3:
        raise _Reject("sentence_shape_out_of_band", detail)
    name, verb = toks[0], toks[1]
    obj = toks[2] if len(toks) == 3 else None
    _check_term_token(name, detail)
    _check_verb_token(verb, detail)
    if obj is not None:
        _check_term_token(obj, detail)
    return _VerbFact((name,), verb, obj, negated)


def _parse_verb_universal(toks: list[str], detail: str) -> _VerbUniversal:
    """``all|every|each|no [the] <class> <verb> [<obj>]`` — no copula form."""
    negative = toks[0] == _E_LEAD
    rest = toks[1:]
    if rest and rest[0] == "the":  # "all the dogs bark" — determiner, dropped
        rest = rest[1:]
    if any(t == "not" or t.endswith("n't") for t in rest):
        # "All men do not teach" — scope-ambiguous (¬∀ vs ∀¬); the E-form
        # ("no …") is the unambiguous spelling this band reads.
        raise _Reject("internal_negation_unread", detail)
    if any(t == "did" for t in rest):
        raise _Reject("tense_out_of_band", detail)
    if len(rest) < 2 or len(rest) > 3:
        raise _Reject("sentence_shape_out_of_band", detail)
    cls, verb = rest[0], rest[1]
    obj = rest[2] if len(rest) == 3 else None
    _check_term_token(cls, detail)
    _check_verb_token(verb, detail)
    if obj is not None:
        _check_term_token(obj, detail)
    return _VerbUniversal((cls,), verb, obj, negative)


def _parse_fact(toks: list[str], detail: str) -> _Singular | _VerbFact:
    """A non-universal sentence: sentential-not unwraps first (its prefix
    contains a copula, so it must be checked before copula routing); then a
    copula routes to v3-MEM's own singular parser (membership fact), else the
    verb-fact grammar."""
    if tuple(toks[: len(_SENTENTIAL_NOT)]) == _SENTENTIAL_NOT:
        inner = _parse_fact(toks[len(_SENTENTIAL_NOT) :], detail)
        if isinstance(inner, _Singular):
            return _Singular(inner.ind, inner.cls, negated=not inner.negated)
        return _VerbFact(inner.ind, inner.verb, inner.obj, negated=not inner.negated)
    if not toks:
        raise _Reject("empty_side", detail)
    if any(t in _COPULA_FORMS for t in toks):
        return _parse_singular(toks, detail)
    return _parse_verb_fact(toks, detail)


def _parse_sentence(toks: list[str], detail: str) -> _Record:
    if any(t in _CONNECTIVES for t in toks):
        raise _Reject("mixed_structure_out_of_band", detail)
    head = toks[0]
    if head in _A_LEADS or head == _E_LEAD:
        if any(t in ("is", "are") for t in toks):
            return _parse_universal(toks, detail)  # is-a universal (v3-MEM's)
        return _parse_verb_universal(toks, detail)
    if head in _QUANTIFIER_TOKENS:
        raise _Reject("quantifier_out_of_band", detail)
    return _parse_fact(toks, detail)


def read_verb_argument(text: str) -> VerbArgument | VerbRefusal:
    """Read *text* as a verb-predicate argument, or refuse (typed).

    Deterministic and pure: same text → same ``VerbArgument``. The conclusion
    is the final sentence, the sole "therefore"-led one, and must be a
    singular fact (membership or verb); every earlier sentence is a premise.
    Lowering is two-pass exactly as v3-MEM's — sentences parse first, THEN
    individuals / class-groups / verb-groups are collected, THEN atoms mint
    and universals instantiate at every named individual — with premise
    formulas emitted in sentence order.
    """
    if not text or not text.strip():
        return VerbRefusal("empty")
    sentences = [
        (m.group(1), m.group(2)) for m in _SENTENCE_RE.finditer(text) if m.group(1).strip()
    ]
    if not sentences:
        return VerbRefusal("empty")

    premises: list[_Record] = []
    premise_texts: list[str] = []
    conclusion: _Singular | _VerbFact | None = None
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
                if any(t in _CONNECTIVES for t in rest):
                    raise _Reject("mixed_structure_out_of_band", body)
                if rest[0] in _A_LEADS or rest[0] == _E_LEAD:
                    raise _Reject("universal_conclusion_out_of_band", body)
                if rest[0] in _QUANTIFIER_TOKENS:
                    raise _Reject("quantifier_out_of_band", body)
                conclusion = _parse_fact(rest, body)
                query_text = " ".join(rest)
                continue
            if len(premises) >= MAX_PREMISE_SENTENCES:
                raise _Reject("too_many_premises", body)
            premises.append(_parse_sentence(toks, body))
            premise_texts.append(" ".join(toks))

        if conclusion is None or query_text is None:
            return VerbRefusal("no_conclusion")
        if not premises:
            return VerbRefusal("no_premises")

        records: list[_Record] = [*premises, conclusion]

        # Every argument this band DECIDES contains at least one verb
        # construct — a pure-copula argument is v3-MEM/v4-CM territory (and
        # only ever reaches here when those bands refused it, in which case
        # the delegated parsers above raised the same typed refusal already;
        # this check is a defensive closure of that invariant).
        if not any(isinstance(r, (_VerbFact, _VerbUniversal)) for r in records):
            raise _Reject("sentence_shape_out_of_band", "no verb predicate read")

        # --- lowering (ADR-0260 §2): v3-MEM's two-pass scheme, two families --
        individuals: list[tuple[str, ...]] = []
        for rec in records:
            if isinstance(rec, (_Singular, _VerbFact)) and rec.ind not in individuals:
                individuals.append(rec.ind)

        # Class groups — the SAME closed noun-morphology relation as v3-MEM.
        cls_group_of: dict[tuple[str, ...], int] = {}
        cls_reps: list[tuple[str, ...]] = []
        for rec in records:
            forms: list[tuple[str, ...]] = []
            if isinstance(rec, _Singular):
                forms = [rec.cls]
            elif isinstance(rec, _Universal):
                forms = [rec.subject, rec.predicate]
            elif isinstance(rec, _VerbUniversal):
                forms = [rec.subject]
            for form in forms:
                if form in cls_group_of:
                    continue
                for gi, rep in enumerate(cls_reps):
                    if _forms_link(form, rep):
                        cls_group_of[form] = gi
                        break
                else:
                    cls_group_of[form] = len(cls_reps)
                    cls_reps.append(form)

        # Verb groups — the closed verb-agreement relation (this band's one
        # new semantic identification).
        verb_group_of: dict[str, int] = {}
        verb_reps: list[str] = []
        for rec in records:
            if not isinstance(rec, (_VerbFact, _VerbUniversal)):
                continue
            form = rec.verb
            if form in verb_group_of:
                continue
            for gi, rep in enumerate(verb_reps):
                if _verb_tokens_link(form, rep):
                    verb_group_of[form] = gi
                    break
            else:
                verb_group_of[form] = len(verb_reps)
                verb_reps.append(form)

        mint: dict[tuple, str] = {}
        atom_display: list[str] = []

        def _mint(key: tuple, display: str, detail: str) -> str:
            if key not in mint:
                if len(atom_display) >= MAX_ATOMS:
                    raise _Reject("too_many_atoms", detail)
                mint[key] = f"a{len(atom_display)}"
                atom_display.append(display)
            return mint[key]

        def mem_atom(ind_idx: int, group: int, detail: str) -> str:
            return _mint(
                ("mem", ind_idx, group),
                f"{' '.join(individuals[ind_idx])} : {' '.join(cls_reps[group])}",
                detail,
            )

        def verb_atom(ind_idx: int, group: int, obj: str | None, detail: str) -> str:
            shown = verb_reps[group] if obj is None else f"{verb_reps[group]} {obj}"
            return _mint(
                ("verb", ind_idx, group, obj),
                f"{' '.join(individuals[ind_idx])} : {shown}",
                detail,
            )

        premise_formulas: list[str] = []
        for rec, body_text in zip(premises, premise_texts):
            if isinstance(rec, _Singular):
                atom = mem_atom(
                    individuals.index(rec.ind), cls_group_of[rec.cls], body_text
                )
                premise_formulas.append(f"~({atom})" if rec.negated else atom)
            elif isinstance(rec, _VerbFact):
                atom = verb_atom(
                    individuals.index(rec.ind),
                    verb_group_of[rec.verb],
                    rec.obj,
                    body_text,
                )
                premise_formulas.append(f"~({atom})" if rec.negated else atom)
            elif isinstance(rec, _Universal):
                for ind_idx in range(len(individuals)):
                    antecedent = mem_atom(ind_idx, cls_group_of[rec.subject], body_text)
                    consequent = mem_atom(ind_idx, cls_group_of[rec.predicate], body_text)
                    premise_formulas.append(
                        f"({antecedent}) -> (~({consequent}))"
                        if rec.negative
                        else f"({antecedent}) -> ({consequent})"
                    )
            else:  # _VerbUniversal
                for ind_idx in range(len(individuals)):
                    antecedent = mem_atom(ind_idx, cls_group_of[rec.subject], body_text)
                    consequent = verb_atom(
                        ind_idx, verb_group_of[rec.verb], rec.obj, body_text
                    )
                    premise_formulas.append(
                        f"({antecedent}) -> (~({consequent}))"
                        if rec.negative
                        else f"({antecedent}) -> ({consequent})"
                    )

        if isinstance(conclusion, _Singular):
            query_atom = mem_atom(
                individuals.index(conclusion.ind),
                cls_group_of[conclusion.cls],
                query_text,
            )
        else:
            query_atom = verb_atom(
                individuals.index(conclusion.ind),
                verb_group_of[conclusion.verb],
                conclusion.obj,
                query_text,
            )
        query_formula = f"~({query_atom})" if conclusion.negated else query_atom
    except (_Reject, _MemberReject) as rej:
        # ``_parse_singular``/``_parse_universal`` are v3-MEM's own functions,
        # reused verbatim — their failures raise v3-MEM's OWN ``_Reject``
        # class (same shape, different identity), so both are caught here and
        # normalized to THIS band's refusal type (the v4-CM lesson).
        return VerbRefusal(rej.refusal.reason, rej.refusal.detail)

    universals = [r for r in premises if isinstance(r, (_Universal, _VerbUniversal))]
    if any(
        (isinstance(u, _Universal) and u.negative)
        or (isinstance(u, _VerbUniversal) and u.negative)
        for u in universals
    ):
        band = EN_VERB_NEGATIVE
    elif len(universals) >= 2:
        band = EN_VERB_CHAIN
    elif len(universals) == 1:
        band = EN_VERB_UNIVERSAL
    else:
        band = EN_VERB_FACT

    return VerbArgument(
        premise_formulas=tuple(premise_formulas),
        query_formula=query_formula,
        premise_texts=tuple(premise_texts),
        query_text=query_text,
        band=band,
        atoms=tuple(atom_display),
    )


def verb_forms_link(a: str, b: str) -> bool:
    """Public view of this band's closed verb-agreement relation.

    Exported so paths OUTSIDE the proof_chain package (the curriculum
    composer, ADR-0262) can normalize a base form against a stated
    third-person form using the SAME closed table and suffix rules the reader
    uses — one agreement authority, not two.
    """
    return _verb_tokens_link(a, b)


__all__ = [
    "MAX_ATOMS",
    "MAX_PREMISE_SENTENCES",
    "VerbArgument",
    "VerbRefusal",
    "read_verb_argument",
    "verb_forms_link",
]
