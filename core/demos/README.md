# Demo Composition Layer

`core/demos/` contains the typed composition surface for demos:
contracts, adapters, showcase rendering, and expert-demo packaging.

It does not own standalone scenario fixtures. Those live under top-level
`demos/`, where each demo package can pin its inputs, expected artifacts, and
honesty ledger.

Boundary:

- `demos/` proves a narrow claim inside a deterministic local envelope.
- `core/demos/` adapts proven demos into shared presentation and Workbench
  surfaces.
