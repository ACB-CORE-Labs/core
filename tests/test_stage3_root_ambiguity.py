"""Stage 3 — fail-closed multi-root Hebrew/Greek depth policy."""

from __future__ import annotations

from generate.problem_frame_contracts import ContractAssessment
from recognition.depth_canonical import (
    RootSenseAmbiguity,
    build_node_depths,
    canonicalize_token,
    enrich_assessments_with_depth,
    observe_root_ambiguity,
    observed_roots,
)


def test_observed_roots_unique_stable_order():
    depth = {
        "n1": {"language": "he", "root": "א-מ-ן"},
        "n2": {"language": "he", "root": "ד-ב-ר"},
        "n3": {"language": "he", "root": "א-מ-ן"},
    }
    assert observed_roots(depth) == ("א-מ-ן", "ד-ב-ר")


def test_observe_root_ambiguity_when_multi():
    depth = {
        "n1": {"language": "he", "root": "א-מ-ן"},
        "n2": {"language": "he", "root": "ד-ב-ר"},
    }
    amb = observe_root_ambiguity(depth)
    assert isinstance(amb, RootSenseAmbiguity)
    assert amb.candidates == ("א-מ-ן", "ד-ב-ר")
    assert amb.resolved is False


def test_enrich_assessments_fails_closed_on_multi_root_no_first_match():
    depth = {
        "n1": {"language": "he", "root": "א-מ-ן"},
        "n2": {"language": "he", "root": "ד-ב-ר"},
    }
    a = ContractAssessment(candidate_organ="t", runnable=True, explanation="base")
    en = enrich_assessments_with_depth((a,), depth)
    assert en[0].runnable is False
    assert "AMBIGUOUS_ROOTS" in (en[0].explanation or "")
    assert "א-מ-ן" in (en[0].explanation or "")
    assert "ד-ב-ר" in (en[0].explanation or "")
    # Must NOT silently commit only the first root as the sole note.
    assert "[root:א-מ-ן]" not in (en[0].explanation or "") or "AMBIGUOUS" in (
        en[0].explanation or ""
    )
    assert "ambiguous_hebrew_roots" in (en[0].unresolved_hazards or ())


def test_enrich_single_root_still_annotates():
    depth = {"n1": {"language": "he", "root": "א-מ-ן"}}
    a = ContractAssessment(candidate_organ="t", runnable=True, explanation="base")
    en = enrich_assessments_with_depth((a,), depth)
    assert en[0].runnable is True
    assert "[root:א-מ-ן]" in (en[0].explanation or "")


def test_canonicalize_multi_root_node_fails_closed():
    depths = {
        "n1": {"language": "he", "roots": ("א-מ-ן", "ד-ב-ר")},
    }
    # Surface retained — no silent first-root commit.
    assert canonicalize_token("דָּבָר", "n1", depths) == "דָּבָר"


def test_canonicalize_single_root_still_maps():
    depths = {"n1": {"language": "he", "root": "א-מ-ן"}}
    assert canonicalize_token("אמת", "n1", depths) == "א-מ-ן"


def test_build_node_depths_carries_roots_tuple():
    class _N:
        node_id = "n1"
        language = "he"
        root = None
        roots = ("א-מ-ן", "ד-ב-ר")
        morphology_id = None

    d = build_node_depths([_N()])
    assert d["n1"]["roots"] == ("א-מ-ן", "ד-ב-ר")
    amb = observe_root_ambiguity(d)
    assert amb is not None
    assert len(amb.candidates) == 2
