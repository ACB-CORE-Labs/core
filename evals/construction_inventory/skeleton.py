"""The construction quotient: a surface reduced to what the reader parses by.

The reader is documented as reading "STRUCTURE symbolically from the token
sequence via domain-agnostic templates keyed on FUNCTION WORDS + ORDER". Take
that literally and it defines an equivalence relation on surfaces: replace every
token the reader does *not* key on with a placeholder, and two surfaces with the
same result are — by the reader's own design — indistinguishable to its parser.

That relation is what makes "how many constructions?" a countable question
instead of a judgement call. The quotient is not chosen by this module; it is
read off ``reader._RESERVED``, so it cannot be gerrymandered to flatter a
number, and it widens automatically when the reader learns a new function word.

**The one place the abstraction leaks**, stated here because a silent leak in a
measurement instrument is worse than the defect it measures: ``_chunk_class``
refuses on an unrecognized plural, which depends on the *token*, not on whether
the token is reserved. So the skeleton determines the reader's verdict **up to
morphology**. The lane handles this by sweeping several lexical fillers per
construction and only counting a construction as shared when every filler
agrees — see ``runner.py``. Morphology refusals are then visible as
filler-dependent disagreement rather than being silently folded into the
construction count.
"""

from __future__ import annotations

from generate.meaning_graph.reader import _RESERVED

#: Function words the reader keys on that ``_RESERVED`` does not list.
#:
#: ``_parse_propositional`` dispatches on ``if`` and ``then``, but neither is in
#: ``_RESERVED`` — so ``_chunk`` will happily swallow them into a noun phrase.
#: That asymmetry is a reader defect (see contract.md, "What this lane found"),
#: not an artefact of this module; it is recorded here so the quotient reflects
#: the tokens the parser *actually* branches on rather than the ones it declares.
_UNDECLARED_KEYWORDS: frozenset[str] = frozenset({"if", "then"})

#: The reader's full function-word vocabulary, derived from source.
READER_FUNCTION_WORDS: frozenset[str] = frozenset(_RESERVED) | _UNDECLARED_KEYWORDS

#: Stands in for any token the reader treats as content.
CONTENT = "*"

_PUNCT = ".,;:?!"


def skeleton(surface: str) -> str:
    """Reduce *surface* to its reader-visible construction.

    Content tokens collapse to ``*``; function words and attached punctuation
    survive, because both change how the reader splits and dispatches.
    """
    out: list[str] = []
    for token in surface.lower().split():
        core = token.strip(_PUNCT)
        trailing = token[len(core):] if core and token.startswith(core) else ""
        out.append((core if core in READER_FUNCTION_WORDS else CONTENT) + trailing)
    return " ".join(out)


__all__ = ("CONTENT", "READER_FUNCTION_WORDS", "skeleton")
