"""Deterministic English morphology for the realizer.

Handles inflection of predicates for tense, aspect, and negation, and
(Phase 2B) **noun number** in both directions.

This is intentionally rule-based and limited to the seed vocabulary.
Irregular forms are listed explicitly; regular forms follow English rules.

Phase 2A gave every *table* one owner (``generate/lexicon.py``); this module
is the single owner of the *rules* that read them. Before 2B the regular
number rules were written twice — ``templates.pluralize`` and
``meaning_graph/reader._singularize`` — and the two disagreed about which
irregulars they knew, which is how CORE came to serve ``all wolve are
mammal``.
"""
from __future__ import annotations

from generate.lexicon import (
    INVARIANT_NUMBER,
    VES_PLURAL_SINGULARS,
    IRREGULAR_PLURALS,
    IRREGULAR_SINGULARS,
    MASS_NOUNS,
)


# Genuinely irregular English verbs (the previous tables held only
# regular forms that the suffix rules already produce correctly).
# Listed as 3rd-person singular present → (past, past_participle).
# Coverage: ~100 common English irregulars including every verb that
# the seed packs and Phase 5 OOD lanes use whose past form does not
# follow the regular -ed rule.  Adding a verb here is the cheap fix
# for english_fluency_ood gaps.md G1.
_IRREGULAR_FORMS: dict[str, tuple[str, str]] = {
    # be / have / do
    "is": ("was", "been"),
    "are": ("were", "been"),
    "has": ("had", "had"),
    "does": ("did", "done"),
    # mental / cognitive
    "thinks": ("thought", "thought"),
    "knows": ("knew", "known"),
    "sees": ("saw", "seen"),
    "hears": ("heard", "heard"),
    "feels": ("felt", "felt"),
    "finds": ("found", "found"),
    "loses": ("lost", "lost"),
    "means": ("meant", "meant"),
    "reads": ("read", "read"),
    "tells": ("told", "told"),
    "says": ("said", "said"),
    "thinks": ("thought", "thought"),
    # motion
    "goes": ("went", "gone"),
    "comes": ("came", "come"),
    "runs": ("ran", "run"),
    "stands": ("stood", "stood"),
    "sits": ("sat", "sat"),
    "lies": ("lay", "lain"),
    "flies": ("flew", "flown"),
    "swims": ("swam", "swum"),
    "rides": ("rode", "ridden"),
    "drives": ("drove", "driven"),
    "rises": ("rose", "risen"),
    "falls": ("fell", "fallen"),
    # giving / taking / holding
    "gives": ("gave", "given"),
    "takes": ("took", "taken"),
    "brings": ("brought", "brought"),
    "buys": ("bought", "bought"),
    "sells": ("sold", "sold"),
    "holds": ("held", "held"),
    "keeps": ("kept", "kept"),
    "leaves": ("left", "left"),
    "lends": ("lent", "lent"),
    "sends": ("sent", "sent"),
    "spends": ("spent", "spent"),
    "puts": ("put", "put"),
    "sets": ("set", "set"),
    "lets": ("let", "let"),
    # building / making / breaking
    "makes": ("made", "made"),
    "builds": ("built", "built"),
    "breaks": ("broke", "broken"),
    "tears": ("tore", "torn"),
    "burns": ("burned", "burned"),
    "shines": ("shone", "shone"),
    "draws": ("drew", "drawn"),
    "writes": ("wrote", "written"),
    "speaks": ("spoke", "spoken"),
    "wins": ("won", "won"),
    "loses": ("lost", "lost"),
    # binding / connecting
    "binds": ("bound", "bound"),
    "winds": ("wound", "wound"),
    "weaves": ("wove", "woven"),
    "flies": ("flew", "flown"),
    "spins": ("spun", "spun"),
    "sticks": ("stuck", "stuck"),
    "swears": ("swore", "sworn"),
    # giving form / shape
    "becomes": ("became", "become"),
    "grows": ("grew", "grown"),
    "blows": ("blew", "blown"),
    "throws": ("threw", "thrown"),
    "shakes": ("shook", "shaken"),
    "wakes": ("woke", "woken"),
    # eating / drinking / cooking
    "eats": ("ate", "eaten"),
    "drinks": ("drank", "drunk"),
    "feeds": ("fed", "fed"),
    "bites": ("bit", "bitten"),
    "freezes": ("froze", "frozen"),
    # cutting / striking
    "cuts": ("cut", "cut"),
    "hits": ("hit", "hit"),
    "shoots": ("shot", "shot"),
    "splits": ("split", "split"),
    "strikes": ("struck", "struck"),
    "fights": ("fought", "fought"),
    "wears": ("wore", "worn"),
    # sleeping / rising / etc
    "sleeps": ("slept", "slept"),
    "wakes": ("woke", "woken"),
    "rises": ("rose", "risen"),
    # finding / hiding
    "hides": ("hid", "hidden"),
    "seeks": ("sought", "sought"),
    "catches": ("caught", "caught"),
    "teaches": ("taught", "taught"),
    "thinks": ("thought", "thought"),
    "brings": ("brought", "brought"),
    # less common / archaic
    "begins": ("began", "begun"),
    "deals": ("dealt", "dealt"),
    "leads": ("led", "led"),
    "meets": ("met", "met"),
    "sits": ("sat", "sat"),
    "swears": ("swore", "sworn"),
    "shoots": ("shot", "shot"),
    "casts": ("cast", "cast"),
    "costs": ("cost", "cost"),
    "hurts": ("hurt", "hurt"),
    "lets": ("let", "let"),
    "quits": ("quit", "quit"),
    "shuts": ("shut", "shut"),
}

# Legacy compatibility — historic call sites use these names.  All
# regular-verb entries here match the suffix-rule output, so removing
# them is purely cosmetic; new irregulars live in `_IRREGULAR_FORMS`.
_IRREGULAR_PAST: dict[str, str] = {v: forms[0] for v, forms in _IRREGULAR_FORMS.items()}

_IRREGULAR_PARTICIPLE: dict[str, str] = {
    # Present-participle (-ing) is almost always regular.  Only handle
    # the truly weird cases (lie→lying handled by the suffix rule;
    # be→being is the one English present-participle that needs a
    # special entry, but `is` doesn't normally surface as a content
    # predicate in our realizer pipeline).
}

_IRREGULAR_PAST_PARTICIPLE: dict[str, str] = {v: forms[1] for v, forms in _IRREGULAR_FORMS.items()}


# Short -ies verbs whose base is -ie (not -y).  English's "ies → y"
# rule (cries→cry, flies→fly) breaks for these short stems where the
# original lemma keeps the -ie (dies→die, lies→lie, ties→tie).
_IES_KEEP_IE: frozenset[str] = frozenset({"dies", "lies", "ties", "vies", "pies", "hies"})


#: Stem endings that take ``-es`` for the 3sg rather than a bare ``-s``.
#:
#: ``ss`` and not ``s``: the sibilant rule fires on a DOUBLED s ("passes" ->
#: "pass"), while a stem ending in a single ``s`` is almost always a stem
#: ending in ``e`` that took a plain ``-s`` ("causes" -> "cause"). Before this
#: distinction, ``base_form("causes")`` returned **"caus"**, which is the
#: single-verb half of the 9-of-26 agreement defect.
_ES_STEM_ENDINGS = ("ss", "sh", "ch", "x", "z", "o")


def _base_form(verb_3sg: str) -> str:
    if verb_3sg in _IES_KEEP_IE:
        return verb_3sg[:-1]
    if verb_3sg.endswith("ies"):
        return verb_3sg[:-3] + "y"
    if verb_3sg.endswith("es"):
        return verb_3sg[:-2] if verb_3sg[:-2].endswith(_ES_STEM_ENDINGS) else verb_3sg[:-1]
    if verb_3sg.endswith("s"):
        return verb_3sg[:-1]
    return verb_3sg


#: 3sg present -> plural present, for the forms where the plural is not simply
#: the bare stem. Everything else pluralizes by dropping the ``-s``.
_PLURAL_PRESENT: dict[str, str] = {
    "is": "are", "are": "are",
    "has": "have", "have": "have",
    "does": "do", "do": "do",
    "was": "were", "were": "were",
}


def plural_present(verb_3sg: str) -> str:
    """A third-person-singular verb → its plural-subject present form."""
    if verb_3sg in _PLURAL_PRESENT:
        return _PLURAL_PRESENT[verb_3sg]
    return _base_form(verb_3sg)


def agree_plural_phrase(phrase: str) -> str:
    """Put a whole predicate PHRASE into plural agreement.

    Number is marked on the finite verb, which is the first token of every
    humanized predicate ("is defined as", "has the following steps",
    "belongs to", "contrasts with"). Only that token inflects; the rest is
    carried through untouched.

    This exists because :func:`base_form` is a SINGLE-VERB function and was
    being applied to whole phrases, stripping the last character-class of the
    final word: "is defined as" -> "is defined a", "has the following steps"
    -> "has the following step". Nine of the 26 seed predicates were wrong
    that way, and every multi-word one was.
    """
    if not phrase:
        return phrase
    head, sep, rest = phrase.partition(" ")
    return plural_present(head) + sep + rest


def past_tense(verb_3sg: str) -> str:
    if verb_3sg in _IRREGULAR_PAST:
        return _IRREGULAR_PAST[verb_3sg]
    base = _base_form(verb_3sg)
    if base.endswith("e"):
        return base + "d"                  # make → made? no — make is irregular; bake → baked
    if base.endswith("y") and len(base) > 1 and base[-2] not in "aeiou":
        return base[:-1] + "ied"            # cry → cried
    if _is_cvc_ending(base):
        return base + base[-1] + "ed"       # stop → stopped, plan → planned
    return base + "ed"


_VOWELS = frozenset("aeiou")


def _is_cvc_ending(base: str) -> bool:
    """True if `base` ends in consonant-vowel-consonant (excluding w/x/y),
    the trigger pattern for doubling the final consonant before -ing /
    -ed in English."""
    if len(base) < 3:
        return False
    c1, v, c2 = base[-3], base[-2], base[-1]
    if c2 in {"w", "x", "y"}:
        return False
    return (c1 not in _VOWELS) and (v in _VOWELS) and (c2 not in _VOWELS)


def present_participle(verb_3sg: str) -> str:
    if verb_3sg in _IRREGULAR_PARTICIPLE:
        return _IRREGULAR_PARTICIPLE[verb_3sg]
    base = _base_form(verb_3sg)
    if base.endswith("ie"):
        return base[:-2] + "ying"          # die → dying, lie → lying
    if base.endswith("e") and not base.endswith("ee"):
        return base[:-1] + "ing"            # make → making
    if _is_cvc_ending(base):
        return base + base[-1] + "ing"      # run → running, swim → swimming
    return base + "ing"


def past_participle(verb_3sg: str) -> str:
    if verb_3sg in _IRREGULAR_PAST_PARTICIPLE:
        return _IRREGULAR_PAST_PARTICIPLE[verb_3sg]
    return past_tense(verb_3sg)


_SIBILANT_PLURAL_ENDINGS = ("s", "sh", "ch", "x", "z")


def is_mass_noun(noun: str) -> bool:
    """Uncountable ⇒ never pluralized, even under a quantifier."""
    return noun.lower() in MASS_NOUNS


def _head_and_prefix(noun: str) -> tuple[str, str]:
    """Split a canonical id into (everything-before-head, head).

    Reader ids are lowercase tokens joined with ``_`` (``guard_dog``), and
    number marks the **head**, which in English compounds is the last token:
    ``guard_dog`` → ``guard_dogs``, never ``guards_dog``. Space-joined input is
    handled the same way so display strings and ids behave alike.
    """
    for sep in ("_", " "):
        if sep in noun:
            prefix, _, head = noun.rpartition(sep)
            return prefix + sep, head
    return "", noun


def pluralize(noun: str) -> str:
    """Singular → plural. Table first, then closed regular rules.

    Mass nouns and the empty string are returned unchanged. Compound ids
    inflect on the head only.
    """
    if not noun:
        return noun
    if is_mass_noun(noun):
        return noun
    prefix, head = _head_and_prefix(noun)
    if head in IRREGULAR_PLURALS:
        return prefix + IRREGULAR_PLURALS[head]
    # Invariant number (sheep, aircraft, means, offspring, ...) — derived from
    # the singularizer's own invariant rows, so the two directions agree.
    if head in INVARIANT_NUMBER:
        return noun
    if is_mass_noun(head):
        return noun
    if head.endswith(_SIBILANT_PLURAL_ENDINGS):
        return prefix + head + "es"
    if head.endswith("y") and len(head) > 1 and head[-2] not in "aeiou":
        return prefix + head[:-1] + "ies"
    # f/fe -> ves is a CLOSED set, not a productive rule: proof->proofs and
    # chief->chiefs, but wolf->wolves. The set is derived from the number
    # table's own ves-rows, so the rule can never claim a word the table does
    # not know. Without this, pluralize("proof") returned "prooves".
    if head in VES_PLURAL_SINGULARS:
        return prefix + (head[:-2] if head.endswith("fe") else head[:-1]) + "ves"
    return prefix + head + "s"


def singularize(noun: str) -> str | None:
    """Plural → singular, or ``None`` when not confidently a plural.

    The table is consulted first and is **authoritative**: if the token
    appears there, its value wins and no suffix rule runs. That is what keeps
    ``news``/``new`` and ``species``/``specy`` unlinked — a bare ``-s`` strip
    corrupts both, and did, in served text.

    ``None`` (rather than a guess) is returned for anything the closed rules
    do not confidently cover, so a caller can refuse instead of minting a
    corrupted id.
    """
    if not noun:
        return None
    prefix, head = _head_and_prefix(noun)
    # An INVARIANT form is ambiguous in number — "fish are mammals" is plural,
    # "a fish is a mammal" is singular, and the token cannot tell you which. A
    # reader that must not guess number therefore has to DECLINE these, even
    # though the table technically maps fish -> fish.
    #
    # This is load-bearing for soundness, not tidiness. The serving composer
    # tries the categorical band (v1b) FIRST and falls back to later, more
    # capable bands. Resolving an invariant makes v1b ACCEPT a sentence it
    # cannot decide, which steals the case from the band that can: with
    # "No fish are mammals. Therefore some fish are mammals." v1b answers
    # "invalid" where v6-EX correctly answers "refuted" (ds-ex-0012). Declining
    # keeps the fall-through intact. Same family as ADR-0261 §5.1
    # refuse-don't-drop.
    if head in INVARIANT_NUMBER:
        return None
    if head in IRREGULAR_SINGULARS:
        return prefix + IRREGULAR_SINGULARS[head]
    # A singular that the pluralizer knows is irregular is not a plural at all
    # ("child" must not become "chil"), and neither is a known mass noun.
    if head in IRREGULAR_PLURALS or is_mass_noun(head):
        return None
    if head.endswith("ies") and len(head) > 3:
        return prefix + head[:-3] + "y"
    if head.endswith(("ses", "xes", "zes", "ches", "shes")):
        return prefix + head[:-2]
    if head.endswith("s") and not head.endswith("ss") and len(head) > 1:
        return prefix + head[:-1]
    return None


def base_form(verb_3sg: str) -> str:
    return _base_form(verb_3sg)
