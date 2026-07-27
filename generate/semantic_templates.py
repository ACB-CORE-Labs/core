"""Intent-aware semantic templates for the realizer.

Maps (IntentTag, relation_predicate) pairs to deterministic surface
templates that use the seed pack's relation predicates (defines, means,
grounds, supports, contrasts_with, corrects).

Design constraints:
  - No LLM fallback
  - No random template selection
  - Deterministic: same (intent, predicate, subject, object) -> same surface
  - Uses seed pack vocabulary directly
"""

from __future__ import annotations

from generate.lexicon import PREDICATE_DISPLAY
from generate.intent import IntentTag


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

_PREDICATE_HUMANIZE: dict[str, str] = PREDICATE_DISPLAY


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
) -> str:
    """Render a semantic surface from intent, subject, predicate, and object.

    When language + root are supplied (from enriched PropositionGraph nodes
    carrying 3-core-language depth), the surface incorporates etymological
    precision for Hebrew (root density) and Koine Greek (Logos precision).
    English base remains unchanged.
    """
    template = _INTENT_TEMPLATES.get(intent, _INTENT_TEMPLATES[IntentTag.UNKNOWN])
    predicate_h = humanize_predicate(predicate)
    obj_display = obj if obj not in ("<pending>", "<prior>") else "..."

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

    return template.format(
        subject=subject,
        predicate_h=predicate_h,
        obj=obj_display,
        secondary=secondary or obj_display,
    )
