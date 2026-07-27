"""Lexical fillers — the controls that keep this a construction measurement.

The reader refuses for two unrelated reasons: it has no template for a shape
(*construction*), or it cannot singularize a token (*morphology*). Folding those
together produces a number that moves when someone adds a noun, which is not
what Phase 5 needs to size.

So every construction is probed with several vocabularies. A construction counts
as shared only when **all count-noun fillers agree**; a construction that reads
under one filler and refuses under another is reported as ``filler_dependent``,
which is the signature of a morphology gap rather than a missing template.

The mass-noun filler is deliberately excluded from the headline and reported on
its own. Mass nouns have no plural, so the writer's own rule keeps them singular
under a quantifier ("all evidence supports truth") — and the reader's
categorical template *requires* a plural head. That is a real inventory
mismatch, but it is a different one from "the reader has no template", and
averaging it into the overlap rate would hide both.
"""

from __future__ import annotations

from evals.construction_inventory.reader_space import LexicalFiller

#: Count-noun fillers — these determine the headline overlap.
COUNT_FILLERS: tuple[LexicalFiller, ...] = (
    LexicalFiller("regular", "dog", "mammal", "dogs", "mammals", "p", "q"),
    LexicalFiller("f_plural", "wolf", "canine", "wolves", "canines", "r", "s"),
    LexicalFiller("suppletive", "child", "person", "children", "people", "u", "v"),
)

#: Mass-noun filler — diagnostic only, never part of the headline.
MASS_FILLER = LexicalFiller("mass", "evidence", "truth", "evidence", "truth", "m", "n")

ALL_FILLERS: tuple[LexicalFiller, ...] = (*COUNT_FILLERS, MASS_FILLER)

#: Third lexical slot, used by the frame intents that take a ``secondary``.
SECONDARY: dict[str, str] = {
    "regular": "cat",
    "f_plural": "fox",
    "suppletive": "adult",
    "mass": "meaning",
}


__all__ = ("ALL_FILLERS", "COUNT_FILLERS", "MASS_FILLER", "SECONDARY")
