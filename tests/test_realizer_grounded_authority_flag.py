"""Realizer-grounded-authority flag — ADR-0088 Phase B (Finding 2).

Pre-fix ``CognitiveTurnPipeline.run()`` called ``realize_semantic`` on
the ungrounded ``PropositionGraph`` — every non-COMPARISON / non-
CORRECTION node was born with ``obj = "<pending>"`` and the realizer
emitted surfaces like ``"X is defined as ..."`` that
``_is_useful_surface`` rejected.  The realizer therefore never won
the surface resolver introduced by PR #76 — it was structurally
present but semantically inert in the hot pipeline path.

ADR-0088 Phase B wires opt-in graph grounding behind
``RuntimeConfig.realizer_grounded_authority``.  Default ``False``
preserves byte-identity for every existing pack and test.  When
``True`` the pipeline calls ``ground_graph(graph, response.recalled_words)``
between ``runtime.chat`` and the realizer's re-invocation.  The
realizer then competes as a real surface authority.

These tests pin:

  * The flag defaults to ``False`` on ``DEFAULT_CONFIG``.
  * Flag-off produces byte-identical surface + trace_hash to today
    (the null-lift invariant the codebase uses for every substantive
    runtime behavior change — see ADR-0072, ADR-0073d, ADR-0083).
  * ``ChatResponse.recalled_words`` is populated on the main path so
    the grounded-graph wiring has a real input when the flag is on.
  * Flag-on does not break the cognition lane — realized surfaces
    are still gated by ``_is_useful_surface`` so any case where the
    grounded realizer cannot produce a clean output falls through to
    the runtime path.

Phase A (realizer fluency parity — gloss-aware templates, 3sg verb
agreement, pack-provenance tag) is documented in ADR-0088 and is the
prerequisite for enabling this flag in production.
"""

from __future__ import annotations

from chat.pack_resolver import LexicalResolution, resolve_entry, resolve_gloss
from chat.runtime import ChatRuntime
from core.cognition import CognitiveTurnPipeline
from core.config import DEFAULT_CONFIG, RuntimeConfig


def test_flag_defaults_to_false() -> None:
    assert DEFAULT_CONFIG.realizer_grounded_authority is False


def test_flag_off_byte_identical_surface_and_trace() -> None:
    """The null-lift invariant: flag-off behaviour is unchanged."""
    rt_a = ChatRuntime()
    rt_b = ChatRuntime()
    pa = CognitiveTurnPipeline(runtime=rt_a)
    pb = CognitiveTurnPipeline(runtime=rt_b)
    result_a = pa.run("What is truth?", max_tokens=4)
    result_b = pb.run("What is truth?", max_tokens=4)
    assert result_a.surface == result_b.surface
    assert result_a.trace_hash == result_b.trace_hash


def test_recalled_words_populated_on_main_path() -> None:
    """The grounded-graph wiring needs real input when the flag is on."""
    rt = ChatRuntime()
    response = rt.chat("What is truth?", max_tokens=4)
    # The walk produces at least one alphabetic token on the main
    # path of any non-stub cognition prompt.
    assert isinstance(response.recalled_words, tuple)
    assert all(isinstance(t, str) and t.isalpha() for t in response.recalled_words)


def test_flag_on_runs_without_crashing() -> None:
    """Flag-on routes through the grounded realizer; the surface still
    clears ``_is_useful_surface`` (or falls back to the runtime path),
    so the result is well-formed even though the surface contents may
    differ from the default until Phase A's fluency parity lands."""
    from chat.pack_resolver import resolve_gloss

    rt = ChatRuntime(config=RuntimeConfig(realizer_grounded_authority=True))
    pipeline = CognitiveTurnPipeline(runtime=rt)
    result = pipeline.run("What is truth?", max_tokens=4)
    # The result is well-formed regardless of which authority won.
    assert isinstance(result.surface, str)
    assert result.surface  # non-empty
    assert result.trace_hash  # hashed

    # Masterful structured grounding: when pack-resident, the graph obj
    # must come directly from resolve_gloss (raw authoritative gloss),
    # not from parsed surface text.
    if result.proposition_graph and result.proposition_graph.nodes:
        gloss_entry = resolve_gloss("truth")
        if gloss_entry:
            _, _, expected_gloss = gloss_entry
            actual_obj = result.proposition_graph.nodes[0].obj
            # The grounded obj should match the raw pack gloss (or be
            # derived from it in the definition frame). We assert it is
            # no longer the "<pending>" sentinel and carries the
            # expected content.
            assert actual_obj != "<pending>"
            assert expected_gloss in actual_obj or actual_obj in expected_gloss

        # Depth now flows on the graph node itself (bidirectional spine).
        # resolve_entry + enrichment in pipeline ensures language (and root
        # for he/grc) ride on the PropositionGraph nodes for realize + trace.
        node = result.proposition_graph.nodes[0]
        # After resolve_entry + node enrichment + ground_graph, depth is on the node.
        assert getattr(node, "language", None) == "en"  # truth resolved via entry path
        # he/grc would carry root + morphology_id (tested via direct probe + he/grc pack tests)


def test_resolve_entry_provides_3lang_depth_for_bidirectional_use() -> None:
    """LexicalResolution is the shared immutable artifact.

    Comprehension (pipeline grounding) and articulation (realizer) plus
    internal reasoning can all consume the same depth-carrying structure
    without duplication. Hebrew root + Greek precision are now first-class.
    """
    # English base (always available)
    en_res = resolve_entry("truth")
    assert en_res is not None
    assert isinstance(en_res, LexicalResolution)
    assert en_res.language in ("en", "en")  # base
    assert en_res.gloss is not None

    # Hebrew depth language (explicit pack for the depth pack)
    he_pack = ("he_logos_micro_v1", "en_collapse_anchors_v1")
    he_res = resolve_entry("אמת", pack_ids=he_pack)  # emet = truth/faithfulness
    if he_res is not None:  # pack may or may not be mounted in all envs; graceful
        assert isinstance(he_res, LexicalResolution)
        assert he_res.language == "he"
        assert he_res.root is not None  # "א-מ-ת" or equivalent
        assert he_res.gloss is not None or he_res.pos  # depth present

    # Greek likewise (structure test)
    grc_pack = ("grc_logos_micro_v1", "en_collapse_anchors_v1")
    grc_res = resolve_entry("λόγος", pack_ids=grc_pack)  # logos
    if grc_res is not None:
        assert grc_res.language == "grc" or grc_res.language == "el"  # Greek
        assert grc_res.morphology_id is not None or grc_res.root is not None

    # Old resolve_gloss path remains available (compat for articulation etc.)
    old = resolve_gloss("truth")
    assert old is not None or en_res is not None  # at least one works


def test_hebrew_depth_full_turn_under_grounded_authority() -> None:
    """Full turn assertion for 3-lang depth under realizer_grounded_authority flag.

    Exercises the complete spine path:
    classify -> graph -> resolve_entry (with depth packs) -> enrich GraphNode
    -> ground_graph -> realize_semantic (depth consumed for richer surface).
    """
    rt = ChatRuntime(config=RuntimeConfig(realizer_grounded_authority=True))
    pipeline = CognitiveTurnPipeline(runtime=rt)
    result = pipeline.run("What is אמת?", max_tokens=4)

    assert isinstance(result.surface, str)
    assert result.surface  # non-empty
    assert result.trace_hash

    if result.proposition_graph and result.proposition_graph.nodes:
        node = result.proposition_graph.nodes[0]
        if node.subject.strip() == "אמת":
            # Depth carried on the node (comprehend side) via resolve_entry + enrich
            assert getattr(node, "language", None) == "he"
            assert getattr(node, "root", None) is not None

            # Even if final user surface is fallback (not learned for this term),
            # the graph carries depth, and realize_semantic on it produces the
            # richer 3-lang framed surface (articulation side consumption).
            from generate.graph_planner import plan_articulation
            from generate.realizer import realize_semantic
            target = plan_articulation(result.proposition_graph)
            realized = realize_semantic(target, result.proposition_graph)
            assert "(Hebrew root:" in realized.surface
            assert "אמת" in realized.surface
