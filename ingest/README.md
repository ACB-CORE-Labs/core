# Runtime Ingest Gate

`ingest/` owns the runtime injection boundary: raw token/state material enters
the versor manifold through `ingest/gate.py`.

This is an allowed normalization boundary. `inject()` calls
`algebra.versor.normalize_to_versor()` once at construction time and returns a
`FieldState` satisfying the field invariant.

It is not the durable learning compiler. Candidate learning material should be
prepared by `core_ingest` and reviewed through the teaching/governance path
before it becomes durable standing.
