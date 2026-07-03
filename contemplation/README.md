# Contemplation Artifacts

This directory is an artifact namespace for committed contemplation process
reports, especially the `runs/` evidence consumed by teaching queue and
Workbench readers.

It is intentionally not a Python package:

- no `contemplation/__init__.py`
- no Python source files under this tree
- executable contemplation code lives under `core/contemplation/`
- always-on runtime life writes local reports under
  `<engine_state>/contemplation_runs/`

Keeping this split explicit prevents `import contemplation` ambiguity while
preserving the deterministic JSON evidence shape expected by queue and
Workbench surfaces.
