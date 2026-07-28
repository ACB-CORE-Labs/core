"""ADR-0252 §5 — the structure-mapping acceptance-gate experiment.

Off-serving. Nothing in this package is imported by ``chat/runtime.py`` or by
any serving path; it exists to answer §5's one load-bearing empirical claim and
to leave a reproducible artifact behind when it does.

Package layout mirrors the §5 design so the mapping from document to code is
one-to-one:

    corpus.py     §5.1  the structure-labelled corpus (real + MARKED synthetic)
    embedding.py  §5.2  the relational embedding scheme (blind to labels)
    experiment.py §5.3  the decisive measurements, §5.4 the verdict rule

The blindness invariant: ``embedding.py`` imports nothing from ``corpus.py``'s
label side and never receives a label. ``experiment.py`` loads labels only after
every residual has been computed. ``tests/test_adr_0252_s5_blindness.py`` pins it.
"""
