# sensorium-falsification — `sensorium/environment/`

**Kind:** zone→component descent · **Parent:** M2 · **Assessor:** Fable 5 (Phase 3)
**Verified at:** `8927c563` (2026-07-27)
**Liveness:** `live-internal` (confirmed) · **Fitness:** `fit` · **Topology role:** deterministic replay surface (not a fusion layer, not a world model)

> Expected-versus-actual environmental falsification: the discipline of saying, before looking, what the world should show — and then checking. Its philosophical role is to keep afferent claims falsifiable without smuggling in a mutable world model, probabilistic confidence, or a learning path. It is deliberately the *narrowest possible* honest instrument.

## What it is / What it does

Four modules, 852 lines: `falsification.py` (compares already-compiled afferent units by merge key), `frame.py` (`ObservationFrame` / `ExpectedObservationFrame`), `scenario.py` (338 — scenario construction), `harness.py` (54). The module docstring states its non-goals in the first sentence: it does not compile raw signals, decode motor commands, fuse modalities, mutate Vault state, or create a world model. Verdict set is closed at two values — `SUPPORTED` (every expected slot matched by merge key, nothing unexpected) / `FALSIFIED` (anything missing, changed, or unexpected). Checksums via `sha256_json`. Neither verdict promotes anything to reviewed memory or mutates packs, vault, identity, or policy.

## Contract & evidence

- ADR-0211 contract frozen in `runtime_contracts.md`, including the forbidden list: no raw pixels/PCM/event streams/byte payloads/actuator traces in traces; no motor/efferent units in v1; no learned latents as substrate; no probabilistic confidence or tolerance thresholds in verdicts; no `generate/*` dependencies; no `ModalityRegistry.decode`.
- The `sensorium` suite (21 files) runs — the zone's tests are scheduled, unlike M6's. would-fail-if-absent: yes.

## Judgment

**Fitness: `fit`.** This is what a v1 should look like: closed verdicts, explicit non-goals in the first paragraph, checksummed evidence, and a hard wall against becoming a world model by accretion. When the sensorium track eventually approaches serving (M2's open entry-criterion question), this bench is the pattern the rest of the afferent stack should be held to.

**Honest wrinkles:** the map filed this zone under layer "L12" — a stratum that exists in no ratified document (flagged in the M2 card; taxonomy should either mint L12 deliberately or drop it). The bench compares *already-compiled* units, so its guarantees are conditional on the sensorium compiler's honesty — which is unmapped territory (the broader 59-module `sensorium/` package remains the largest built-and-disconnected mass in the tree). Zero-subsystem status in the map was an artifact of the final mapping wave, not of emptiness.

**Open questions:** none blocking; inherits M2's "entry criterion for serving" ruling.
