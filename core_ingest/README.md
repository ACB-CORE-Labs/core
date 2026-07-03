# Core Ingest

`core_ingest/` converts external source material into typed candidate pressure:
content-addressed packets with provenance, modality, determinism class, review
level, and semantic keys.

Its durable path runs the three-gate `IngestCompiler` and can export
`LearningArtifact` objects. Its read-only CLI surface (`core ingest compile`) is
for inspection and does not write vault entries, mutate packs, ratify learning,
or call `ingest/gate.py`.

Boundary:

- `core_ingest` prepares and validates candidate pressure.
- `ingest/gate.py` injects runtime field state into the versor manifold.
- durable mutation still belongs to the reviewed teaching path.
