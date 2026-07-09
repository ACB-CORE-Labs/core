"""Capability obligations for 3-lang (he/grc) depth PropGraph spine.

These tests seal the landed depth contract as something that must not
regress silently: top-level CognitiveTurnResult fields, same-turn token
depth resolution for recognition, multi-exemplar he/grc coverage, and
construction assessment enrichment.
"""

from __future__ import annotations

import pytest

from algebra.versor import versor_condition
from chat.pack_resolver import (
    DEFAULT_RESOLVABLE_PACK_IDS,
    DEPTH_PACK_IDS,
    resolve_entry,
    resolve_token_depths,
)
from chat.runtime import ChatRuntime
from core.cognition.pipeline import CognitiveTurnPipeline
from generate.problem_frame_builder import build_problem_frame
from generate.problem_frame_contracts import (
    _dilation_versor_payload,
    _scale_from_geometric_signature,
    assess_contracts,
)
from recognition.anti_unifier import derive_recognizer, recognize
from recognition.outcome import EvidenceSpan, FeatureBundle


pytestmark = pytest.mark.requires_depth_packs

_COMBINED_PACKS = DEFAULT_RESOLVABLE_PACK_IDS + DEPTH_PACK_IDS

# Sealed exemplars: surface form that pack_resolver must ground with root.
_HE_GRC_EXEMPLARS: tuple[tuple[str, str, str], ...] = (
    ("אמת", "he", "define אמת"),
    ("דבר", "he", "define דבר"),
    ("λόγος", "grc", "define λόγος"),
    ("φῶς", "grc", "define φῶς"),
)


def test_resolve_token_depths_same_turn_hebrew_and_greek() -> None:
    """P1: provisional t{i} depths before graph exists."""
    depths, agent = resolve_token_depths(("define", "אמת"))
    assert agent is not None
    assert agent.startswith("t")
    assert depths[agent]["language"] == "he"
    assert depths[agent]["root"] in ("א-מ-נ", "א-מ-ן")

    depths_g, agent_g = resolve_token_depths(("define", "λόγος"))
    assert agent_g is not None
    assert depths_g[agent_g]["language"] == "grc"
    assert depths_g[agent_g]["root"]

    empty, no_agent = resolve_token_depths(("hello", "world"))
    assert empty == {}
    assert no_agent is None


def test_same_turn_recognize_uses_early_token_depths() -> None:
    """P1: first-turn surface form root-canonicalizes without prior graph depths."""
    depths, agent = resolve_token_depths(("אמת", "is", "3", "units"))
    assert agent is not None and depths

    root = depths[agent]["root"]
    tokens_surface = ("אמת", "is", "3", "units")
    tokens_root = (root, "is", "3", "units")
    bundle_root = FeatureBundle.from_mapping(
        {
            "agent": (root, EvidenceSpan(0, 1, root)),
            "relation": ("is", EvidenceSpan(1, 2, "is")),
            "count": (3, EvidenceSpan(2, 3, "3")),
            "unit": ("units", EvidenceSpan(3, 4, "units")),
        }
    )
    rec = derive_recognizer(
        [(tokens_root, bundle_root)], depths=depths, agent_node_id=agent
    )
    outcome = recognize(
        rec, tokens_surface, depths=depths, agent_node_id=agent
    )
    assert outcome.admitted or str(outcome.state).lower() in (
        "evidenced",
        "undetermined",
    )
    if outcome.proposition is not None:
        ag = outcome.proposition.get("agent")
        assert ag is not None
        assert ag.value == root


def test_pipeline_same_turn_early_depths_wired_into_recognize(monkeypatch: pytest.MonkeyPatch) -> None:
    """P1 integration: pipeline passes early depths on first turn (no prior _last)."""
    captured: dict = {}

    def _spy_recognize(recognizer, tokens, depths=None, agent_node_id=None):  # type: ignore[no-untyped-def]
        captured["depths"] = depths
        captured["agent_node_id"] = agent_node_id
        captured["tokens"] = tokens
        # Refuse so we do not need a valid teaching set — we only spy wiring.
        from recognition.outcome import (
            RecognitionOutcome,
            RecognitionProvenance,
            ShapeRefusal,
        )

        return RecognitionOutcome(
            state="undetermined",
            provenance=RecognitionProvenance(
                mechanism="anti_unification",
                teaching_set_id="spy",
                resolution_level="shape",
            ),
            refusal_reason=ShapeRefusal(reason="spy_refuse_for_depth_wiring"),
        )

    # Minimal recognizer stub with teaching_set_id for epistemic node id path.
    class _StubRec:
        teaching_set_id = "spy-teaching-set"

    import core.cognition.pipeline as pipeline_mod

    monkeypatch.setattr(pipeline_mod, "recognize", _spy_recognize)
    rt = ChatRuntime()
    pl = CognitiveTurnPipeline(runtime=rt, recognizer=_StubRec())  # type: ignore[arg-type]
    assert pl._last_node_depths in (None, {})
    pl.run("define אמת", max_tokens=1)
    assert captured.get("depths"), "expected same-turn early depths"
    assert any(
        d.get("language") == "he" and d.get("root")
        for d in captured["depths"].values()
    )
    assert captured.get("agent_node_id")


@pytest.mark.parametrize("lemma,lang,prompt", _HE_GRC_EXEMPLARS)
def test_depth_capability_exemplars_on_result(lemma: str, lang: str, prompt: str) -> None:
    """P2/P3: sealed he/grc exemplars emit node_depths + graph_anti_unify on result."""
    res = resolve_entry(lemma, pack_ids=_COMBINED_PACKS)
    assert res is not None
    assert res.language == lang
    assert res.root

    rt = ChatRuntime()
    pl = CognitiveTurnPipeline(runtime=rt)
    result = pl.run(prompt, max_tokens=1)

    nd = result.node_depths
    gau = result.graph_anti_unify
    assert isinstance(nd, dict) and len(nd) > 0
    assert any(v.get("language") == lang and v.get("root") for v in nd.values())
    # PR #3 filter: no English-only pollution without root
    for entry in nd.values():
        assert entry.get("language") in ("he", "grc") or entry.get("root")

    assert isinstance(gau, dict)
    matched = gau.get("matched_roots") or []
    assert matched, f"expected matched_roots for {prompt!r}"
    roots = {r for _, r in matched}
    assert res.root in roots or any(res.root in str(r) for r in roots)

    # oov context dual-emit
    ctx = result.oov_geometric_context or {}
    assert ctx.get("node_depths")
    assert ctx.get("graph_anti_unify")


def test_construction_assess_with_he_root_depth() -> None:
    """P3: construction assessment path enriches with real he root note."""
    depth = {"p0": {"language": "he", "root": "א-מ-נ"}}
    frame = build_problem_frame("A school has 100 students.")
    assessments = assess_contracts(frame, depth=depth)
    assert any("[root:א-מ-נ]" in (getattr(a, "explanation", "") or "") for a in assessments)


def test_dilation_payload_from_scale_and_signature() -> None:
    """Pack-shaped geometric_signature + frame scale drive dilation versor."""
    payload = _dilation_versor_payload(0.5)
    assert payload.shape == (32,)
    assert float(versor_condition(payload)) < 1e-6

    assert _scale_from_geometric_signature({"scale": 0.25}) == 0.25
    assert _scale_from_geometric_signature({"numerator": 1, "denominator": 3}) == pytest.approx(
        1 / 3
    )
    assert _scale_from_geometric_signature({"note": "no scale"}) is None

    # Post-pivot: frame-grounded scale (KernelFacts Fraction), not prose regex.
    from generate.problem_frame_contracts import (
        assess_fraction_decrease,
        assess_geometric_proposals,
    )

    text = (
        "In one hour, Addison mountain's temperature will decrease to 3/4 of its temperature. "
        "If the current temperature of the mountain is 84 degrees, what will the temperature "
        "decrease by?"
    )
    frame = build_problem_frame(text)
    geom = assess_geometric_proposals(frame)
    assert len(geom) == 1
    assert geom[0].runnable
    assert geom[0].bindings
    assert geom[0].bindings[0].semantic_identity == "3/4"
    assert float(versor_condition(geom[0].bindings[0].geometric_payload)) < 1e-6

    obligation = assess_fraction_decrease(frame)
    assert obligation.runnable
    assert obligation.bindings
    assert obligation.bindings[0].semantic_identity == "3/4"
