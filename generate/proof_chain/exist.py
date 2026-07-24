"""Existential-argument reader — Band v6-EX (ADR-0261).

Completes the all / no / some square. Reads deductive arguments containing
existential ("some") sentences — "All wolves are mammals. Some wolves are
tame. Therefore some mammals are tame." — by extending Band v5-VP's
per-individual propositional lowering with TWO new domain elements:

- a **witness** per existential PREMISE (Skolem constant): "some C1 are C2"
  ⇒ ``mem(w,C1) & mem(w,C2)`` for a fresh ``w`` that nothing else names;
- one **arbitrary individual** ``k``, minted iff the CONCLUSION is
  existential: an element about which no fact is asserted and at which every
  universal is still instantiated.

An existential conclusion lowers to the disjunction of its conjunction over
EVERY domain element (named individuals, witnesses, and ``k``). The same
verified ROBDD engine decides. Both atom families of v5-VP carry over
unchanged, so existentials compose with membership facts, is-a universals,
verb facts, and verb universals in one shared atom space.

Why this is sound (ADR-0261 §3), in the two directions that matter:

* **ENTAILED.** Let *M* be any first-order model of the argument's premises.
  Every witness is interpretable in *M* (its existential premise asserts a
  satisfier), universal instantiation is truth-preserving at every element,
  and ``k`` may be interpreted as ANY element (domains are non-empty), so
  every lowered premise formula holds in *M*. If the lowered premises
  propositionally entail the query's disjunction, some domain element
  satisfies the conjunction in *M* — which is exactly ∃. Skolem constants
  never appear in the original argument, so this is the standard
  entailment-preserving Skolemization.
* **REFUTED.** The conjunction dual is entailed only if it is entailed at
  ``k`` — and ``k`` is arbitrary (no premise mentions it), so what holds of
  ``k`` holds of every element: the universal ∀x¬(…) that refuting ∃ requires
  is genuinely derived, never assumed by domain closure. This is the ONE
  place a naive witness-only lowering would be unsound: without ``k``,
  "Rex is a wolf. Rex is not tame. Therefore some wolves are tame." would
  read as REFUTED (the only wolf in the lowering is not tame) instead of the
  honest UNKNOWN. ``k`` is what keeps the domain open.

Completeness within the fragment lifts the same way as v3-MEM/v5-VP: a
propositional countermodel becomes a first-order countermodel whose domain is
exactly the named individuals, witnesses, and ``k``.

**No existential import.** "All C are P. Therefore some C are P." is UNKNOWN,
not ENTAILED — a universal is vacuously true over an empty class, so the
subaltern moods (Darapti, Felapton, Bamalip) come out UNKNOWN here. That is
the modern first-order reading and the conservative one; the categorical band
(v1b) already reads the square the same way (its own arena carries the
"existential-import overreach" case as INVALID).

Sentence shapes added over v5-VP, all with a ``some`` lead:
``some <C1> are|is [not] [a|an] <C2>`` (I-form and O-form) and
``some <C> <verb> [<object>]`` / ``some <C> do not <verb> [<object>]``. The
plural ``do not`` is read HERE (unlike v5-VP, which refuses it) because with
an existential subject there is no scope ambiguity: "some C do not V" is
∃x(C(x) ∧ ¬V(x)), full stop. ``all C do not V`` remains refused — that one is
genuinely ambiguous. Every other sentence shape delegates VERBATIM to v3-MEM
and v5-VP's own parsers, refusals included.

Tried strictly AFTER Bands v1 / v1b / v2-EN / v3-MEM / v4-CM / v5-VP (the
last fallback tier) — pure widening; every previously-served argument is
served byte-identically. Every earlier band refuses a ``some``-led sentence
(``quantifier_out_of_band`` / ``categorical_shape_out_of_band``), and the
categorical band v1b, which does read some-syllogisms, is tried BEFORE this
one and keeps them. Refusal-first, closed reason vocabulary:

  ``empty``, ``question_sentence``, ``no_conclusion``,
  ``multiple_conclusions``, ``conclusion_not_last``, ``no_premises``,
  ``empty_side``, ``quantifier_out_of_band``, ``bare_plural_out_of_band``,
  ``definite_description_out_of_band``, ``relative_clause_out_of_band``,
  ``universal_conclusion_out_of_band``, ``mixed_structure_out_of_band``,
  ``internal_negation_unread``, ``sentence_shape_out_of_band``,
  ``tense_out_of_band``, ``partitive_out_of_band``, ``structural_leak``,
  ``too_many_premises``, ``too_many_atoms``.
"""

from __future__ import annotations

from dataclasses import dataclass

# The v2-EN sentence splitter/tokenizer, v3-MEM's copula parsers and shared
# guards, and v5-VP's verb grammar are reused VERBATIM — one normalization
# discipline across every argument band; deliberate private-name imports
# inside the proof_chain package, same precedent as member/cond_member/verb.
from generate.proof_chain.english import _SENTENCE_RE, _tokenize
from generate.proof_chain.member import (
    _A_LEADS,
    _COPULA_FORMS,
    _E_LEAD,
    _QUANTIFIER_TOKENS,
    _SENTENTIAL_NOT,
    _Singular,
    _Universal,
    _check_run,
    _forms_link,
    _parse_singular,
    _parse_universal,
)
from generate.proof_chain.member import _Reject as _MemberReject
from generate.proof_chain.shape import (
    EN_EXIST_CHAIN,
    EN_EXIST_NEGATIVE,
    EN_EXIST_UNIVERSAL,
    EN_EXIST_WITNESS,
)
from generate.proof_chain.verb import (
    _AUXILIARIES,
    _CONNECTIVES,
    _VerbFact,
    _VerbUniversal,
    _check_term_token,
    _check_verb_token,
    _parse_fact,
    _parse_verb_universal,
    _verb_tokens_link,
)
from generate.proof_chain.verb import _Reject as _VerbReject

#: The one existential lead this band reads. Every other quantifier token
#: keeps v3-MEM's ``quantifier_out_of_band`` refusal.
_SOME = "some"

#: Partitive marker — "some of the wolves" is a different construction
#: (quantification over a contextually-fixed set, not over a class), so it
#: refuses rather than being read as an opaque class run.
_PARTITIVE = "of"

#: Honesty caps — beyond these the argument is refused, never truncated.
#: ``MAX_ATOMS`` now also bounds an existential conclusion's disjunction,
#: which mints up to two atoms per domain element, so the cap binds exactly
#: where the lowering multiplies.
MAX_PREMISE_SENTENCES = 16
MAX_ATOMS = 24

#: Display names for the two synthetic domain elements. Presentation only —
#: atom identity is the domain INDEX, so these can never collide with a name
#: the user actually wrote.
_WITNESS_DISPLAY = "witness {n}"
_ARBITRARY_DISPLAY = "any individual"


@dataclass(frozen=True, slots=True)
class ExistArgument:
    """A successfully-read existential argument, engine-ready.

    Same shape as ``VerbArgument``: ``premise_formulas``/``query_formula`` are
    propositional formula strings over minted atom ids; ``atoms[i]`` displays
    the fact behind ``a{i}`` (``individual : class`` for membership atoms,
    ``individual : verb [object]`` for verb atoms, where ``individual`` may be
    a witness or the arbitrary element).
    """

    premise_formulas: tuple[str, ...]
    query_formula: str
    premise_texts: tuple[str, ...]
    query_text: str
    band: str
    atoms: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ExistRefusal:
    """A typed refusal — the argument is not honestly readable by this band."""

    reason: str
    detail: str = ""


class _Reject(Exception):
    def __init__(self, reason: str, detail: str = "") -> None:
        super().__init__(reason)
        self.refusal = ExistRefusal(reason, detail)


@dataclass(frozen=True, slots=True)
class _ExistCopula:
    """``some <C1> are|is [not] [a|an] <C2>`` — an I-form (or O-form when
    ``negated``) over a fresh witness at lowering time."""

    subject: tuple[str, ...]
    predicate: tuple[str, ...]
    negated: bool


@dataclass(frozen=True, slots=True)
class _ExistVerb:
    """``some <C> [do not] <verb> [<object>]`` — the verb-predicate I/O-form
    over a fresh witness at lowering time."""

    subject: tuple[str, ...]
    verb: str
    obj: str | None
    negated: bool


_Existential = _ExistCopula | _ExistVerb
_Record = _Singular | _Universal | _VerbFact | _VerbUniversal | _ExistCopula | _ExistVerb


def _check_exist_subject(toks: tuple[str, ...], detail: str) -> None:
    """Guard an existential subject run: the shared opaque-run guard plus the
    partitive exclusion."""
    if _PARTITIVE in toks:
        raise _Reject("partitive_out_of_band", detail)
    _check_run(toks, detail)


def _parse_exist_copula(toks: list[str], detail: str) -> _ExistCopula:
    """``some <C1> are|is [not] [a|an] <C2>``.

    Deliberately NOT v3-MEM's ``_parse_universal``: that parser refuses a
    predicate-leading ``not`` because "all C are not P" is scope-ambiguous
    (¬∀ vs ∀¬). "Some C are not P" has no such ambiguity — it is the O-form,
    ∃x(C(x) ∧ ¬P(x)) — so the negation is read here.
    """
    rest = toks[1:]
    cop_idx = next((i for i, t in enumerate(rest) if t in ("is", "are")), None)
    if cop_idx is None:
        raise _Reject("sentence_shape_out_of_band", detail)
    subject = rest[:cop_idx]
    if subject and subject[0] == "the":  # "some of the …" is caught below
        subject = subject[1:]
    predicate = rest[cop_idx + 1 :]
    negated = False
    if predicate and predicate[0] == "not":
        negated = True
        predicate = predicate[1:]
    if predicate and predicate[0] in ("a", "an"):
        predicate = predicate[1:]
    elif predicate and predicate[0] == "the":
        raise _Reject("definite_description_out_of_band", detail)
    _check_exist_subject(tuple(subject), detail)
    _check_run(tuple(predicate), detail)
    return _ExistCopula(tuple(subject), tuple(predicate), negated)


def _parse_exist_verb(toks: list[str], detail: str) -> _ExistVerb:
    """``some <C> <verb> [<obj>]`` / ``some <C> do not <verb> [<obj>]`` — no
    copula form. Single-token class, verb, and object, exactly as v5-VP's
    verb universals."""
    rest = toks[1:]
    if rest and rest[0] == "the":
        rest = rest[1:]
    if _PARTITIVE in rest:
        raise _Reject("partitive_out_of_band", detail)
    negated = False
    if len(rest) >= 3 and rest[1] in _AUXILIARIES and rest[2] == "not":
        if rest[1] == "did":
            raise _Reject("tense_out_of_band", detail)
        if rest[1] == "does":
            # "some wolves does not run" — agreement this band does not read.
            raise _Reject("sentence_shape_out_of_band", detail)
        negated = True
        rest = [rest[0], *rest[3:]]
    if any(t == "not" or t.endswith("n't") for t in rest):
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
    return _ExistVerb((cls,), verb, obj, negated)


def _parse_existential(toks: list[str], detail: str) -> _Existential:
    """A ``some``-led sentence: a copula form routes to the I/O-form copula
    parser, else the verb grammar."""
    if any(t in _COPULA_FORMS for t in toks):
        if any(t in ("was", "were") for t in toks):
            raise _Reject("tense_out_of_band", detail)
        return _parse_exist_copula(toks, detail)
    return _parse_exist_verb(toks, detail)


def _parse_sentence(toks: list[str], detail: str) -> _Record:
    if any(t in _CONNECTIVES for t in toks):
        raise _Reject("mixed_structure_out_of_band", detail)
    head = toks[0]
    if head == _SOME:
        return _parse_existential(toks, detail)
    if head in _A_LEADS or head == _E_LEAD:
        if any(t in ("is", "are") for t in toks):
            return _parse_universal(toks, detail)  # is-a universal (v3-MEM's)
        return _parse_verb_universal(toks, detail)  # verb universal (v5-VP's)
    if head in _QUANTIFIER_TOKENS:
        raise _Reject("quantifier_out_of_band", detail)
    return _parse_fact(toks, detail)  # singular membership / verb fact (v5-VP's)


def read_exist_argument(text: str) -> ExistArgument | ExistRefusal:
    """Read *text* as an existential argument, or refuse (typed).

    Deterministic and pure: same text → same ``ExistArgument``. The conclusion
    is the final sentence, the sole "therefore"-led one, and may be a singular
    fact (membership or verb) or an existential; universal conclusions stay
    out of band. Lowering is two-pass exactly as v3-MEM/v5-VP's — sentences
    parse first, THEN the domain (named individuals, one witness per
    existential premise, and the arbitrary element when the conclusion is
    existential) is fixed, THEN atoms mint and universals instantiate at every
    domain element — with premise formulas emitted in sentence order.
    """
    if not text or not text.strip():
        return ExistRefusal("empty")
    sentences = [
        (m.group(1), m.group(2)) for m in _SENTENCE_RE.finditer(text) if m.group(1).strip()
    ]
    if not sentences:
        return ExistRefusal("empty")

    premises: list[_Record] = []
    premise_texts: list[str] = []
    conclusion: _Singular | _VerbFact | _ExistCopula | _ExistVerb | None = None
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
                if rest[0] == _SOME:
                    conclusion = _parse_existential(rest, body)
                elif rest[0] in _QUANTIFIER_TOKENS:
                    raise _Reject("quantifier_out_of_band", body)
                else:
                    conclusion = _parse_fact(rest, body)
                query_text = " ".join(rest)
                continue
            if len(premises) >= MAX_PREMISE_SENTENCES:
                raise _Reject("too_many_premises", body)
            premises.append(_parse_sentence(toks, body))
            premise_texts.append(" ".join(toks))

        if conclusion is None or query_text is None:
            return ExistRefusal("no_conclusion")
        if not premises:
            return ExistRefusal("no_premises")

        records: list[_Record] = [*premises, conclusion]

        # Every argument this band DECIDES contains at least one existential
        # construct — a purely universal/singular argument is v3-MEM/v5-VP
        # territory (and only ever reaches here when those bands refused it,
        # in which case the delegated parsers above raised the same typed
        # refusal already; this is a defensive closure of that invariant).
        if not any(isinstance(r, (_ExistCopula, _ExistVerb)) for r in records):
            raise _Reject("sentence_shape_out_of_band", "no existential read")

        # --- domain (ADR-0261 §2) -------------------------------------------
        # Display name per domain index; named individuals first (first-
        # appearance order), then one witness per existential premise, then
        # the arbitrary element iff the conclusion is existential.
        domain: list[str] = []
        named_index: dict[tuple[str, ...], int] = {}
        for rec in records:
            if isinstance(rec, (_Singular, _VerbFact)) and rec.ind not in named_index:
                named_index[rec.ind] = len(domain)
                domain.append(" ".join(rec.ind))
        witness_index: dict[int, int] = {}
        for pos, rec in enumerate(premises):
            if isinstance(rec, (_ExistCopula, _ExistVerb)):
                witness_index[pos] = len(domain)
                domain.append(_WITNESS_DISPLAY.format(n=len(witness_index)))
        conclusion_is_existential = isinstance(conclusion, (_ExistCopula, _ExistVerb))
        if conclusion_is_existential:
            domain.append(_ARBITRARY_DISPLAY)

        # Class groups — the SAME closed noun-morphology relation as v3-MEM.
        cls_group_of: dict[tuple[str, ...], int] = {}
        cls_reps: list[tuple[str, ...]] = []
        for rec in records:
            forms: list[tuple[str, ...]] = []
            if isinstance(rec, _Singular):
                forms = [rec.cls]
            elif isinstance(rec, (_Universal, _ExistCopula)):
                forms = [rec.subject, rec.predicate]
            elif isinstance(rec, (_VerbUniversal, _ExistVerb)):
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

        # Verb groups — v5-VP's closed agreement relation, unchanged.
        verb_group_of: dict[str, int] = {}
        verb_reps: list[str] = []
        for rec in records:
            if not isinstance(rec, (_VerbFact, _VerbUniversal, _ExistVerb)):
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
                f"{domain[ind_idx]} : {' '.join(cls_reps[group])}",
                detail,
            )

        def verb_atom(ind_idx: int, group: int, obj: str | None, detail: str) -> str:
            shown = verb_reps[group] if obj is None else f"{verb_reps[group]} {obj}"
            return _mint(("verb", ind_idx, group, obj), f"{domain[ind_idx]} : {shown}", detail)

        def literal(atom: str, negated: bool) -> str:
            return f"~({atom})" if negated else atom

        def conjunction(ind_idx: int, rec: _Existential, detail: str) -> str:
            """``mem(i, subject) & [~]<predicate>(i)`` for one domain element —
            the body of both an existential premise and an existential query
            disjunct."""
            subject = mem_atom(ind_idx, cls_group_of[rec.subject], detail)
            if isinstance(rec, _ExistCopula):
                predicate = mem_atom(ind_idx, cls_group_of[rec.predicate], detail)
            else:
                predicate = verb_atom(ind_idx, verb_group_of[rec.verb], rec.obj, detail)
            return f"({subject}) & ({literal(predicate, rec.negated)})"

        premise_formulas: list[str] = []
        for pos, (rec, body_text) in enumerate(zip(premises, premise_texts)):
            if isinstance(rec, _Singular):
                atom = mem_atom(named_index[rec.ind], cls_group_of[rec.cls], body_text)
                premise_formulas.append(literal(atom, rec.negated))
            elif isinstance(rec, _VerbFact):
                atom = verb_atom(
                    named_index[rec.ind], verb_group_of[rec.verb], rec.obj, body_text
                )
                premise_formulas.append(literal(atom, rec.negated))
            elif isinstance(rec, (_ExistCopula, _ExistVerb)):
                premise_formulas.append(conjunction(witness_index[pos], rec, body_text))
            elif isinstance(rec, _Universal):
                for ind_idx in range(len(domain)):
                    antecedent = mem_atom(ind_idx, cls_group_of[rec.subject], body_text)
                    consequent = mem_atom(ind_idx, cls_group_of[rec.predicate], body_text)
                    premise_formulas.append(
                        f"({antecedent}) -> ({literal(consequent, rec.negative)})"
                    )
            else:  # _VerbUniversal
                for ind_idx in range(len(domain)):
                    antecedent = mem_atom(ind_idx, cls_group_of[rec.subject], body_text)
                    consequent = verb_atom(
                        ind_idx, verb_group_of[rec.verb], rec.obj, body_text
                    )
                    premise_formulas.append(
                        f"({antecedent}) -> ({literal(consequent, rec.negative)})"
                    )

        if isinstance(conclusion, (_ExistCopula, _ExistVerb)):
            query_formula = " | ".join(
                f"({conjunction(ind_idx, conclusion, query_text)})"
                for ind_idx in range(len(domain))
            )
        elif isinstance(conclusion, _Singular):
            query_formula = literal(
                mem_atom(
                    named_index[conclusion.ind], cls_group_of[conclusion.cls], query_text
                ),
                conclusion.negated,
            )
        else:
            query_formula = literal(
                verb_atom(
                    named_index[conclusion.ind],
                    verb_group_of[conclusion.verb],
                    conclusion.obj,
                    query_text,
                ),
                conclusion.negated,
            )
    except (_Reject, _MemberReject, _VerbReject) as rej:
        # ``_parse_singular`` / ``_parse_universal`` are v3-MEM's own functions
        # and ``_parse_fact`` / ``_parse_verb_universal`` are v5-VP's, all
        # reused verbatim — their failures raise THEIR OWN ``_Reject`` classes
        # (same shape, different identity), so all three are caught here and
        # normalized to THIS band's refusal type (the v4-CM lesson, extended).
        return ExistRefusal(rej.refusal.reason, rej.refusal.detail)

    universals = [r for r in premises if isinstance(r, (_Universal, _VerbUniversal))]
    if any(u.negative for u in universals):
        band = EN_EXIST_NEGATIVE
    elif len(universals) >= 2:
        band = EN_EXIST_CHAIN
    elif len(universals) == 1:
        band = EN_EXIST_UNIVERSAL
    else:
        band = EN_EXIST_WITNESS

    return ExistArgument(
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
    "ExistArgument",
    "ExistRefusal",
    "read_exist_argument",
]
