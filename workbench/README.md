# CORE Workbench Backend

`workbench/` is the local operator/auditor API package for CORE. It exposes
read models over committed artifacts, runtime traces, evidence bundles, demo
envelopes, calibration ledgers, and narrow allowlisted actions.

It is distinct from:

- `workbench-ui/` — the React/Vite frontend.
- `workbench_data/` — ignored local read-model artifacts such as turn journals.
- `docs/workbench/` — plans, contracts, guides, and design documentation.

Backend modules should preserve the Workbench trust boundary:

- read-only by default;
- no hidden model calls or background execution;
- execution only through explicit allowlisted endpoints;
- artifact projections must include source paths/digests when available.

`apple_uma_report.py` belongs here because it projects a persisted benchmark
report into a stable UI/API read model. It does not run benchmarks, import MLX,
mutate reports, or authorize serving.
