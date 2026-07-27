"""Intent-aware semantic templates for the realizer.

Maps (IntentTag, relation_predicate) pairs to deterministic surface
templates that use the seed pack's relation predicates (defines, means,
grounds, supports, contrasts_with, corrects).

Design constraints:
  - No LLM fallback
  - No random template selection
  - Deterministic: same (intent, predicate, subject, object) -> same surface
  - Uses seed pack vocabulary directly

Division of labour (Phase 5)
----------------------------
This module owns **discourse framing** — which frame an intent speaks in, and
the 3-language depth notes. It does **not** own clause grammar.

Four of the eight intent templates are not frames at all: they are ordinary
clauses (``{subject} {predicate_h} {obj}``, optionally with a fixed predicate
or a prefix). Those are handed to ``generate.templates.render_step``, the
single owner of English clause grammar — number, agreement, negation, tense,
aspect. Writing a second copy of negation here is how this codebase came to
have two grammars in the first place; Phase 2A spent a whole unit undoing that
duplication, and the fix must not rebuild it one level up.

The delegation is **provably output-preserving**: across all four delegated
intents x every predicate in ``PREDICATE_DISPLAY`` (plus an unknown one) x
every object sentinel, 192 of 192 surfaces are byte-identical to the
pre-delegation output. The only surfaces this moves are ones that were WRONG.
"""

from __future__ import annotations

from generate.graph_planner import RhetoricalMove
from generate.intent import IntentTag
from generate.lexicon import PREDICATE_DISPLAY
from generate.templates import render_step


_INTENT_TEMPLATES: dict[IntentTag, str] = {
    IntentTag.DEFINITION: "{subject} is defined as {obj}",
    IntentTag.CAUSE: "{subject} is grounded in {obj}",
    IntentTag.PROCEDURE: "first, {obj}; then, {subject} follows",
    IntentTag.COMPARISON: "{subject} and {secondary} are distinguished: {subject} {predicate_h} {secondary}",
    IntentTag.CORRECTION: "correction: {subject} {predicate_h} {obj}",
    IntentTag.RECALL: "recalling {subject}: {obj}",
    IntentTag.VERIFICATION: "{subject} is verified: {obj}",
    IntentTag.UNKNOWN: "{subject} {predicate_h} {obj}",
}

#: Intents whose template IS a clause, mapped to (predicate override, move).
#:
#: ``None`` keeps the step's own predicate. DEFINITION and CAUSE pin one,
#: because the *intent* — not the node — decides how a definition is framed.
#: That was already true of the format strings above; it is preserved exactly.
_CLAUSE_INTENTS: dict[IntentTag, tuple[str | None, RhetoricalMove]] = {
    IntentTag.UNKNOWN: (None, RhetoricalMove.ASSERT),
    IntentTag.CORRECTION: (None, RhetoricalMove.CORRECT),
    IntentTag.DEFINITION: ("is_defined_as", RhetoricalMove.ASSERT),
    IntentTag.CAUSE: ("is_grounded_in", RhetoricalMove.ASSERT),
}

#: Frames that are not clauses but still carry a finite verb, so a denial still
#: has somewhere to attach. Written out rather than derived: negating a frame
#: is a wording decision per frame, not a rule.
_NEGATED_FRAMES: dict[IntentTag, str] = {
    IntentTag.VERIFICATION: "{subject} is not verified: {obj}",
    IntentTag.PROCEDURE: "first, {obj}; then, {subject} does not follow",
    IntentTag.COMPARISON: (
        "{subject} and {secondary} are not distinguished: "
        "{subject} does not {predicate_h} {secondary}"
    ),
}

#: RECALL is a speech act ("recalling X: Y"), not an assertion, so it contains
#: no proposition to deny. Rather than emit a frame that quietly drops the
#: denial — the defect this change exists to remove — a negated RECALL falls
#: back to the clause path, which can say "not". Losing the framing is the
#: right trade against asserting the opposite of the graph (ADR-0261 §5.1,
#: refuse-don't-drop).
_UNFRAMEABLE_WHEN_NEGATED: frozenset[IntentTag] = frozenset({IntentTag.RECALL})

_PREDICATE_HUMANIZE: dict[str, str] = PREDICATE_DISPLAY

#: Object sentinels meaning "not grounded yet". ``render_step`` knows only
#: ``<pending>``; this module has always also mapped ``<prior>``.
_OBJ_SENTINELS = ("<pending>", "<prior>")


def humanize_predicate(predicate: str) -> str:
    return _PREDICATE_HUMANIZE.get(predicate, predicate.replace("_", " "))


def render_semantic(
    intent: IntentTag,
    subject: str,
    predicate: str,
    obj: str,
    secondary: str | None = None,
    language: str | None = None,
    root: str | None = None,
    negated: bool = False,
) -> str:
    """Render a semantic surface from intent, subject, predicate, and object.

    When language + root are supplied (from enriched PropositionGraph nodes
    carrying 3-core-language depth), the surface incorporates etymological
    precision for Hebrew (root density) and Koine Greek (Logos precision).
    English base remains unchanged.

    ``negated`` denies the proposition. It reaches here from the user's own
    words: ``intent.negated`` -> ``GraphNode.negated`` ->
    ``ArticulationStep.negated``. Before Phase 5 that chain was broken at the
    graph and this function had no parameter for it, so CORE served the
    affirmative of every denial it was given.
    """
    predicate_h = humanize_predicate(predicate)
    obj_display = obj if obj not in _OBJ_SENTINELS else "..."

    # Masterful 3-language depth framing on the articulation side.
    # Depth travels with the shared GraphNode from resolve_entry grounding.
    if language and root and language != "en":
        if language == "he":
            depth_note = f" (Hebrew root: {root})"
        elif language in ("grc", "el"):
            depth_note = f" (Koine Greek: {root})"
        else:
            depth_note = f" ({language} root: {root})"

        # For definition-style intents, highlight the term itself.
        # For others, qualify the object referent.
        if intent in (IntentTag.DEFINITION, IntentTag.RECALL, IntentTag.VERIFICATION):
            subject = f"{subject}{depth_note}"
        else:
            obj_display = f"{obj_display}{depth_note}"

    # --- clause-shaped intents: hand the clause to its one owner ----------
    #
    # An intent with no frame of its own has always fallen back to the UNKNOWN
    # *template*; it now falls back to the UNKNOWN *clause*. That distinction
    # is the whole point: the template cannot say "not" and the clause can, so
    # the default has to be the capable path. Five live intents were sitting on
    # that fallback — TRANSITIVE_QUERY, FRAME_TRANSFER, NARRATIVE, EXAMPLE,
    # DEDUCTION — each serving a denial as its own assertion, and the next
    # intent added without a template would have joined them silently.
    clause_intent = intent
    if intent not in _INTENT_TEMPLATES:
        clause_intent = IntentTag.UNKNOWN
    elif negated and intent in _UNFRAMEABLE_WHEN_NEGATED:
        clause_intent = IntentTag.UNKNOWN
    if clause_intent in _CLAUSE_INTENTS:
        override, move = _CLAUSE_INTENTS[clause_intent]
        return render_step(
            move,
            subject,
            override or predicate,
            obj_display,
            negated=negated,
        )

    # --- frames: keep the discourse shape, deny inside it -----------------
    if negated and intent in _NEGATED_FRAMES:
        template = _NEGATED_FRAMES[intent]
    else:
        template = _INTENT_TEMPLATES.get(intent, _INTENT_TEMPLATES[IntentTag.UNKNOWN])

    return template.format(
        subject=subject,
        predicate_h=predicate_h,
        obj=obj_display,
        secondary=secondary or obj_display,
    )
