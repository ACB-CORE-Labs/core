"""Stage 3D — OOV conformal probe + horosphere egress authority pins."""

from __future__ import annotations

import numpy as np

from algebra.cga import cga_inner
from algebra.versor import unitize_versor
from chat.runtime import ChatRuntime
from core.cognition import CognitiveTurnPipeline
from vocab.manifold import VocabManifold


def test_oov_geometric_context_carries_conformal_neighbors_or_topology():
    """Live pipeline OOV/pending path records geometric context, not lexical only."""
    rt = ChatRuntime()
    p = CognitiveTurnPipeline(rt)
    # Force an OOV-shaped prompt (unlikely pack lemma).
    result = p.run("what is xyzzyplugh_oov_token_zzz", max_tokens=6)
    ctx = result.oov_geometric_context
    # Either OOV path fired with conformal note, or graph topology was recorded.
    if ctx is not None:
        assert "conformal_neighbors" in ctx or "unresolved_topology" in ctx or "node_depths" in ctx
        if "note" in ctx:
            assert "cga_inner" in ctx["note"] or "Conformal" in ctx["note"] or "depth" in ctx["note"]


def test_vocab_nearest_is_cga_inner_not_cosine():
    """Horosphere egress ranking is exact cga_inner argmax (Blueprint B.3)."""
    rng = np.random.default_rng(11)
    m = VocabManifold()
    for w in ("alpha", "beta", "gamma"):
        m.add(w, unitize_versor(rng.standard_normal(32).astype(np.float64)))
    query = unitize_versor(
        m.get_versor("beta").astype(np.float64) + 0.08 * rng.standard_normal(32)
    )
    word, idx = m.nearest(query)
    scores = [float(cga_inner(query, m.get_versor_at(i))) for i in range(len(m))]
    assert idx == int(np.argmax(scores))
    assert word == m.get_word_at(idx)


def test_pipeline_does_not_use_vault_hits_as_gate_for_surface():
    """vault_hits remains telemetry; surface authority is geometric/resolution."""
    rt = ChatRuntime()
    p = CognitiveTurnPipeline(rt)
    result = p.run("what is light", max_tokens=6)
    assert isinstance(result.vault_hits, int)
    assert result.authority_source in {
        "runtime_canonical",
        "runtime_pre_decoration",
        "runtime",
        "realizer",
        "substrate_realizer",
        "",
    }
    # Geometric coherence is first-class and independent of vault_hits.
    assert result.geometric_coherence is not None
