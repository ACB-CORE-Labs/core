"""core.ports — Ring 2/3 multi-port residual protocol + integrity handoff.

The shared control grammar of the ADR-0246 preflight §9 (Ring 2) and the
integrity-handoff coordinator (Ring 3): an INTERCONNECT GRAMMAR between CORE's
organs — never a second physics, never a unified scheduler, never a content
generator. Ports keep their non-identical native geometry; the grammar only
standardizes witness → typed residual decomposition → permitted operator
selection → bounded operation or abstention → re-certification → action
decision → append-only replay record.

Distinct from :mod:`core.protocol` (the CORE Trace Protocol v0 wire format) —
that package serializes trace events; this one governs residual decisions.

Every module here is pure, deterministic, f64, content-addressed
(full SHA-256, canonical JSON, no ``default=str``), and off-serving.
"""
