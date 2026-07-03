# Calibration Package

`calibration/` is the deterministic operator-parameter replay and tuning
package. It explores bounded `CalibrationParams` candidates against eval cases
and emits before/after metrics for review.

It is not the ADR-0175 reliability ledger and it does not grant serving
licenses. Serving discipline is owned by `core.reliability_gate`; Workbench reads
that evidence through `workbench/calibration.py` without re-running lanes or
mutating license state.

This boundary is intentional:

- `calibration/params.py`, `calibration/replay.py`, `calibration/tune.py`, and
  `calibration/report.py` support deterministic parameter audits.
- `workbench/calibration.py` projects committed practice and serving artifacts
  into a read-only UI/API surface.
