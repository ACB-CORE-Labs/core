# Deterministic Demo Packages

`demos/` contains standalone, claim-scoped demonstration packages. Each demo
has its own fixtures, expected artifacts, local authority code, and runner.

These packages are intentionally importable because tests and Workbench demo
routes execute them as deterministic envelopes. They are not generic runtime
adapters and they must not perform hidden side effects.

Use this directory for bounded proof demos such as proposer authority,
proof-carrying promotion, epistemic truth-state refusal, or domain-specific
decision substrates.

Use `core/demos/` for composition contracts, showcase adapters, and runtime
presentation of already-proven demos.
