"""ADR-0252 §5 — the blindness invariant, pinned.

The §5 experiment has already been run twice and returned GO twice on rules
that were not binding. Attempt 1's specific defect was **label leakage**: the
structural label reached the embedding coordinates, so Procrustes aligned
identical byte-arrays and the test was a tautology.

These pins make that defect a failing test rather than a thing a reader has to
notice. They are cheap, they are in the smoke suite, and they would each have
caught a real historical error.
"""

from __future__ import annotations

import inspect

import numpy as np
import pytest

from evals.structure_mapping.adr0252_s5 import corpus, embedding
from evals.structure_mapping.adr0252_s5.embedding import EmbeddingRefusal


def test_embedding_module_never_reads_labels() -> None:
    """The mapper may not import, name, or receive a structure label.

    Attempt 1 failed exactly here. A grep-level pin is enough: the embedding is
    a pure function of the graph, so any mention of the label vocabulary in its
    source is either leakage or a comment that will become leakage.
    """
    source = inspect.getsource(embedding)
    body = "\n".join(
        line for line in source.splitlines() if not line.strip().startswith("#")
    )
    # The docstring legitimately discusses the scheme; strip it before scanning.
    body = body.replace(embedding.__doc__ or "", "")
    for label in corpus.STRUCTURES:
        assert f'"{label}"' not in body and f"'{label}'" not in body, (
            f"embedding.py references the structure label {label!r} — the "
            "mapper must be blind to labels (ADR-0252 §5.2)"
        )
    assert "corpus" not in body.replace("corpus.py", ""), (
        "embedding.py must not import the corpus module: labels live there"
    )


def test_embedding_is_a_pure_function_of_the_graph() -> None:
    """Same graph twice → byte-identical cloud. No hidden state, no RNG."""
    cases, _ = corpus.build_corpus()
    graph = cases[0].graph
    first = embedding.embed(graph, attr_scale=0.0)
    second = embedding.embed(graph, attr_scale=0.0)
    assert np.array_equal(first, second)


def test_entity_names_never_reach_the_geometry() -> None:
    """Renaming every entity must not move a single coordinate.

    This is what makes §5.3b's ``rename`` perturbation analytic rather than
    measured, and the verdict document says so; the claim is pinned here so it
    stays true if the scheme changes.
    """
    for kind, left, right in corpus.invariance_pairs():
        if kind != "rename":
            continue
        for scale in (0.0, 0.02):
            assert np.array_equal(
                embedding.embed(left.graph, attr_scale=scale),
                embedding.embed(right.graph, attr_scale=scale),
            ), f"rename changed the geometry for {left.case_id} at attr_scale={scale}"


def test_undeclared_relation_kind_refuses_rather_than_guessing() -> None:
    """No default position for an unknown relation (fail closed, INV-34 shape)."""
    cases, _ = corpus.build_corpus()
    graph = cases[0].graph
    saved = dict(embedding.KIND_HEIGHT)
    try:
        embedding.KIND_HEIGHT = {}  # type: ignore[assignment]
        with pytest.raises(EmbeddingRefusal):
            embedding.embed(graph, attr_scale=0.0)
    finally:
        embedding.KIND_HEIGHT = saved  # type: ignore[assignment]


def test_corpus_marks_every_synthetic_case() -> None:
    """§5.1 permits synthetic variants only 'marked as such'.

    Attempt 2's corpus carried 46 of 51 cases from outside ``holdout_dev/v1``
    with nothing marking them. This pin makes that unrepeatable.
    """
    cases, labels = corpus.build_corpus()
    assert cases, "corpus must not be empty"
    for case in cases:
        assert case.provenance in {"holdout_dev/v1", "synthetic"}
        assert case.case_id in labels
        if case.provenance == "holdout_dev/v1":
            assert case.case_id.startswith("gsm8k-holdout-dev-v1-"), (
                f"{case.case_id} claims holdout provenance without a holdout id"
            )


def test_corpus_has_no_duplicate_graphs() -> None:
    """Identical inputs align at residual 0 by construction.

    Attempt 2's corpus contained at least three exact-duplicate graphs under
    different ids (and three colliding ids), which re-imported attempt 1's
    tautology through the data instead of through the embedding.
    """
    cases, _ = corpus.build_corpus()
    seen: dict[str, str] = {}
    for case in cases:
        key = repr(case.graph.as_json())
        assert key not in seen, (
            f"{case.case_id} duplicates {seen[key]} — duplicate graphs make "
            "same-structure alignment trivially zero"
        )
        seen[key] = case.case_id
