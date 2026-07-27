# M2 — Afferent Boundary

**Kind:** layer · **Parent:** CORE · **Assessor:** Opus 5 (Phase 2)
**Verified at:** `8927c563` (2026-07-27)
**Liveness:** `partial-wiring-debt` (text) / `inert` (non-text) · **Fitness:** `strained` · **Topology role:** runtime boundary

> World → field. M2 is where untrusted reality becomes admissible structure, and it is the only layer whose failure mode is *contamination* rather than error: everything downstream inherits whatever M2 admits. Its philosophical charge is that admission is an act with consequences — the gate does not merely parse, it *vouches*. Every entry point is therefore a trust boundary, and normalization is permitted here precisely because this is a declared construction boundary, not a repair site.

**Telos stages:** listen/ingest
**Macro role:** Admits input into the field under a closure-preserving construction boundary, or refuses it.

---

## What it is / What it does

`ingest/gate.py::inject` is the live text path: it converts tokens into field excitation and is one of the explicitly **allowed normalization boundaries** in `AGENTS.md` — permitted because injection is construction, not drift repair. `core_ingest/` (7 modules) is the ingest compiler. `ingest/` itself is small (2 modules). OOV policy is applied at the same seam via `packs.OOVPolicy`.

`sensorium/` (59 modules — the largest non-test, non-generate package after `core/`) is the afferent track for non-text modalities, plus `sensorium.environment.falsification` (ADR-0211), a deterministic replay surface comparing expected against actual `ObservationFrame` evidence with a closed two-verdict set (`SUPPORTED` / `FALSIFIED`). Neither verdict promotes anything to reviewed memory or mutates packs, vault, identity, or policy.

**Verified at this SHA: `sensorium` is imported by neither `chat/runtime.py` nor `core/cognition/pipeline.py`.** The afferent track is off the serving path entirely — consistent with the map's `inert` label for `sensorium-afferent`, and consistent with the position paper's honest statement that vision, audio, and motor modalities are *planned, not built*: the `ProjectionHead` protocol supports them architecturally; the projection heads do not exist.

---

## Contract

- **Inputs:** raw user text; (designed) non-text modality frames.
- **Outputs:** injected `FieldState` satisfying `versor_condition < 1e-6`, OOV decisions, `ObservationFrame` evidence, falsification verdicts.
- **Invariants:**
  - Every accepted field state satisfies the versor condition **at the gate** — pin: algebra/ingest suites — status: running.
  - Normalization is allowed **only** at declared construction boundaries (`ingest/gate.py` is named explicitly); drift repair is forbidden and may not be disguised by naming.
  - Falsification bench forbids raw pixels/PCM/event streams/byte payloads/actuator traces in traces; forbids motor-efferent units in v1; forbids learned latents as substrate; forbids probabilistic confidence or tolerance thresholds in verdicts; forbids `generate/*` dependencies and vault mutation — pin: sensorium suite (21 files) — status: running.
  - Trust-boundary defaults: explicit opt-in for arbitrary execution; reject unsafe paths before filesystem access; no hidden background execution.

---

## Design vs build

- **Design:** ADR-0007 (ingest → `CandidateGeometricPressure` → `FieldState`), ADR-0211 (environmental falsification), ADR-0243 §multimodal ingress, `AGENTS.md` allowed-normalization-boundaries rule, formation's six trust boundaries as the adjacent standard (M5).
- **Build:** text path `partial-wiring-debt`; non-text `inert`.
- **Evidence:**
  - `inject` is the live serving entry — code-read — `chat/runtime.py:115 from ingest.gate import inject` — would-fail-if-absent: **yes**.
  - Sensorium is absent from both serving entrypoints — code-read (negative) — would-fail-if-absent: **n/a; this is evidence of absence**.
  - `sensorium` suite exists with 21 test files — code-read — `core/cli_test.py` — would-fail-if-absent: **yes** (the falsification bench is genuinely exercised).
  - `unified_ingest=False` (`core/config.py:243`) — measurement — the unified ingest path is built and **off by default**.

---

## Capacity

- **Designed:** any modality admitted through a closure-preserving, trust-bounded gate.
- **Measured:** text only, in production. Non-text afferent machinery is substantial (59 modules) and exercised by its own suite, but reaches no serving path.
- **Ceilings:** no projection heads exist for vision/audio/motor. The falsification bench is deliberately v1-closed (two verdicts, no probabilistic confidence, no tolerance thresholds) — a scoping decision, not a defect.

---

## Dependencies & provenance

**feeds** → M0 (field excitation), M3 (tokens, OOV decisions); **reads** → M1 (packs, OOV policy, vocabulary); **verified-by** → MV.

---

## Stage coverage

| Stage | Verdict | Evidence |
|---|---|---|
| listen/ingest (text) | **covered** | `inject` is on the live path and gate-checks closure |
| listen/ingest (non-text) | **uncovered** | Sensorium imports nowhere on the serving path; no projection heads exist |

**Zone roster:** `ingest-boundary`, `ingest-compiler`, `sensorium-afferent` (inert, **confirmed** by import evidence), `sensorium-falsification` ⚑ (live-internal; zero subsystems mapped).

**⚑ Zero-subsystem zone.** `sensorium-falsification` is the fourth unmapped zone and the only one outside M3. What is known: it corresponds to `sensorium.environment.falsification` under ADR-0211 with a closed verdict set and an explicit forbidden-list, and its suite runs. What is unmapped: internal decomposition and the boundary against the rest of `sensorium/`. The system map labels it layer **"L12"** — a stratum no other CORE document uses. That label should be either adopted deliberately or dropped; it currently exists only in a local, gitignored artifact.

**Rollup note:** weakest-link rollup, and here it is genuinely informative rather than misleading: M2's text half serves and its non-text half does not.

---

## Judgment

**Fitness: `strained`.** The text gate is sound and correctly privileged as a construction boundary. The strain is proportional: **59 modules of afferent machinery reach no serving path**, which is the largest quantity of built-and-disconnected code the assessment has located. That is not automatically waste — a deliberately staged capability awaiting projection heads is legitimate — but it is a large standing bet whose entry criterion is nowhere stated.

**Honest wrinkles:**
- The single most consequential asymmetry in this layer: **M5's formation pipeline declares six explicit trust boundaries with content-addressed inputs and outputs and an audit record for every rejection; M2 — the boundary that actually faces untrusted user text in production — has no comparable declared table.** Both are "the place the world gets in," and only one of them has a published contract of that rigor. This is a Phase 4 item and, in this assessor's reading, the strongest single hindrance-audit lead outside M6: the standard exists in-repo and has not been applied where the exposure is highest.
- `sensorium-falsification`'s "L12" layer label exists in one local artifact and no ratified document. Minor, but it is exactly how a phantom stratum enters an architecture.
- `unified_ingest` is built and off; like M5's learning flags, the gap between built and on is undocumented.
- The falsification bench's explicit prohibition on motor/efferent units in v1 is the **only** place in the corpus that takes a position adjacent to Candidate CR-3 (efferent action) — and it is a scoping constraint on one bench, not a system-level ruling. CR-3 remains unruled.

**Open questions:**
- Should M2 adopt formation's trust-boundary table format? (→ Phase 4 / ruling)
- What is the entry criterion for the sensorium track reaching serving? (→ ruling)
- Adopt or drop the "L12" label (→ Phase 1 taxonomy amendment or ruling)
