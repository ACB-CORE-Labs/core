# Phase 1 — The Card Schema

**Executor:** Fable 5, 2026-07-27. **Companion:** `02-layer-taxonomy.md`.
**Applies to:** every card written in Phases 2 (`10-layer-cards/`) and 3 (`20-component-cards/`), and every claim consumed by Phase 4's registers.

This is D2 executed: the system map's 17-field node schema and 7-value liveness vocabulary are **extended, not replaced**. The map's vocabulary encodes distinctions it earned over 205 subsystems — serving vs merely-executing, never-built vs built-and-disconnected, research that returned a negative result. What it lacks are the four dimensions Phase 0 measured as missing: **evidence, capacity, design-vs-build, fitness**. Those arrive as orthogonal fields, not fatter enums.

---

## 1. Design principles

**P1 — Orthogonal axes, not fatter enums.** *Liveness* answers "is it running?"; *fitness* answers "should it be?" These are independent. The governing example: ADR-0252 condemns the 34 surface organs while ruling they keep serving until a proven replacement exists — liveness `live-serving`, fitness `superseded-in-place`. A single merged status could not express that state, and that state is load-bearing. The same separation holds for *design* (what documents articulate) versus *build* (what code does): a component can be fully designed and unbuilt (`L11` process), or built with no surviving design authority (fragments of allocation physics).

**P2 — Evidence or it is a claim.** Every `live-serving` / `live-internal` verdict requires at least one evidence pointer **that would fail if the mechanism were deleted** (the sabotage test). Evidence that would look identical with the mechanism absent is decoration and does not count toward liveness — this repository has produced exactly that failure (`g_args_rate` was 0.0 while prose claimed the reader read it). A card may cite decoration, but must label it as such.

**P3 — Stamped verification.** Every card carries `verified_at`: the commit SHA actually inspected and the date. A claim inherited from the 2026-06-09 system map without re-verification is written as `claimed (map 2026-06-09)`, never as fact. Staleness must be visible on the card, not discoverable by archaeology.

**P4 — Pins must run.** An invariant "enforced by a test" is only enforced if the pin lives in a suite that executes (a pin registered in no suite never runs). Citing a pin requires naming its suite and confirming the suite's membership count moved when the pin was added, or that the suite demonstrably collects it today.

**P5 — Identity, not value.** When a card asserts two things are the same mechanism (shared, not duplicated), the evidence must be identity-grade (same object, same call path), not equal-looking values or name-greps.

---

## 2. Field specification

### 2.1 Identity block

| Field | Req | Notes |
|---|---|---|
| `id` | ✓ | Stable slug; zones keep their map `zone_id` unchanged for greppability |
| `kind` | ✓ | `layer` \| `zone` \| `component` |
| `parent` | ✓ | Containment: component → zone → macro layer (per taxonomy §4) |
| `verified_at` | ✓ | `<SHA> (<date>)` — the tree actually inspected (P3) |
| `assessor` | ✓ | Who filled the card |

### 2.2 Teleology block *(the "philosophical understanding" dimension)*

| Field | Req | Notes |
|---|---|---|
| `philosophical_intent` | ✓ | What this element is **for** in the cognitive model — one paragraph, teleological, answerable to the north star. Distinct from `what_it_does`. If no document states an intent, write `undetermined` — that is itself a finding |
| `telos_stages` | ✓ | Stages served, from the ratified vocabulary; candidate functions cited as `candidate:CR-n`, never bare |
| `macro_role` | ✓ | Kept from map: the element's role in its layer's story |

### 2.3 Description & contract block *(kept from the map — its strongest part)*

| Field | Req | Notes |
|---|---|---|
| `what_it_is` / `what_it_does` | ✓ | As in the map: essence vs behavior, in prose |
| `inputs` / `outputs` | ✓ | Typed where the code types them |
| `invariants` | ✓ | Each entry: the invariant, its enforcement pin, **and the suite that runs the pin** (P4). An invariant with no running pin is recorded with enforcement `none` — a finding, not a formality |
| `topology_role` | ✓ | The `AGENTS.md` repository-topology classification (runtime boundary / candidate compiler / reviewed data / read-only projection / demo envelope / benchmark artifact / historical note / tooling) — replaces the map's `classification` |

### 2.4 Design-vs-build block *(new — the design/implementation split Shay asked for)*

| Field | Req | Notes |
|---|---|---|
| `design_state` | ✓ | Where the design is articulated (doc/ADR + status) and its one-paragraph summary. `none` if the code has no surviving design authority |
| `build_state.liveness` | ✓ | The 7-value vocabulary, unchanged: `live-serving` → `live-internal` → `partial-wiring-debt` → `spike` → `inert` → `unbuilt` → `research-negative` |
| `build_state.key_files` | ✓ | Kept from map |
| `build_state.evidence[]` | ✓ | See §3.2 — the field P2 is about |

### 2.5 Capacity block *(new — "to what capacity" now has a field)*

| Field | Req | Notes |
|---|---|---|
| `capacity.designed` | ✓ | The envelope the design claims (e.g. "any clause the grammar owns") |
| `capacity.measured` | ✓ | The envelope evidence supports, with numbers (e.g. "reader comprehends 19 constructions; writer emits 1739; overlap 6"; "16-premise cap holds a band to ≤16 entailed cases") |
| `capacity.ceilings` | ✓ | Known hard limits and what imposes them (`unknown` is a legal and honest value) |

### 2.6 Dependency & provenance block

| Field | Req | Notes |
|---|---|---|
| `relationships` | ✓ | Kept: typed edges (`feeds` / `reads` / `depends-on` / `verifies` / …) |
| `owning_adrs` | ✓ | Kept; extended to include governing analysis/ratification docs with dates |

### 2.7 Judgment block *(new — feeds Phase 4)*

| Field | Req | Notes |
|---|---|---|
| `fitness.verdict` | ✓ | See §3.3 |
| `fitness.rationale` | ✓ | Why — with evidence pointers. `undetermined` requires naming what evidence would determine it |
| `honest_wrinkles` | ✓ | Kept from the map, deliberately: what is true about this element that its labels would otherwise hide |
| `open_questions` | ○ | Questions the card raises but cannot answer; each tagged with who can (Phase 3 / Phase 4 / ruling) |

### 2.8 Layer cards only

| Field | Req | Notes |
|---|---|---|
| `stage_coverage` | ✓ | For each `telos_stage` the layer claims: covered / claimed-only / uncovered, with the evidence that decides it (taxonomy §6) |
| `zone_roster` | ✓ | The layer's zones from taxonomy §4, with re-verified liveness |
| `rollup_note` | ✓ | Mandatory restatement: zone liveness is weakest-link; the subsystem-level picture; never a completion rate |

---

## 3. Vocabularies

### 3.1 Liveness (unchanged, 7 values, ordered)

`live-serving` · `live-internal` · `partial-wiring-debt` · `spike` · `inert` · `unbuilt` · `research-negative`

`research-negative` is knowledge, not failure — a mechanism investigated and honestly refuted (field-wedge). Do not "clean it up" into `inert`.

### 3.2 Evidence entry shape

```text
{ claim, kind: test | lane | pin | acceptance-packet | measurement | code-read,
  pointer: <path or doc + location>,
  would_fail_if_absent: yes | no | unknown }
```

Only `would_fail_if_absent: yes` counts toward liveness (P2). `code-read` is legitimate evidence for *existence and wiring* (per the read-the-code doctrine) but never for *behavior* — behavior needs a test, lane, or measurement.

### 3.3 Fitness (new, 6 values)

| Verdict | Meaning |
|---|---|
| `fit` | Right mechanism, right owner, serving its intent |
| `strained` | Right place, but shape or capacity no longer matches the load (e.g. an index that stopped scaling) |
| `misplaced` | Sound mechanism, wrong owner — belongs to another layer/component whose design parameters (possibly extended) suit it |
| `wrong-solution` | The mechanism does not serve the underlying problem; a different approach is needed |
| `superseded-in-place` | Condemned by ruling but deliberately still serving until a proven replacement exists |
| `undetermined` | Not yet judged — must name the deciding evidence |

`misplaced` and `wrong-solution` entries are the direct feed for Phase 4's hindrance audit (`31-hindrance-audit.md`); every such verdict must name its **evidence** and its **proposed better home** — and decides nothing (rulings are Shay's).

---

## 4. Card template

```markdown
# <id> — <name>

**Kind:** <layer|zone|component> · **Parent:** <parent> · **Assessor:** <who>
**Verified at:** `<SHA>` (<date>)
**Liveness:** `<value>` · **Fitness:** `<verdict>` · **Topology role:** <role>

> <philosophical_intent — one paragraph>

**Telos stages:** <stages; candidates as candidate:CR-n>
**Macro role:** <one line>

## What it is / What it does
<prose, two short paragraphs>

## Contract
- Inputs: …
- Outputs: …
- Invariants: <invariant> — pin: <test> — suite: <suite> — status: <running|none>

## Design vs build
- Design: <doc/ADR + status> — <summary or `none`>
- Build: <liveness>; key files: …
- Evidence:
  - <claim> — <kind> — <pointer> — would-fail-if-absent: <yes|no|unknown>

## Capacity
- Designed: … · Measured: … · Ceilings: …

## Dependencies & provenance
- Relationships: …
- Owning ADRs / governing docs: …

## Judgment
- Fitness rationale: …
- Honest wrinkles: …
- Open questions: … (→ Phase 3 / Phase 4 / ruling)
```

Layer cards append the `stage_coverage` table, `zone_roster`, and `rollup_note` (§2.8).

---

## 5. Anti-patterns (each has already occurred in this repository's history)

1. **Exists ≠ live.** A module's presence proves nothing about execution. (Dormant readback rules; `explain.py`.)
2. **Threaded ≠ behavioral.** A flag reaching a call site is not the flag changing output; pair every wiring claim with a behavior sweep. (The ignored-flag lesson.)
3. **Green ≠ meaningful.** A measurement that would look identical with the mechanism removed measures nothing. (`g_args_rate` = 0.0.)
4. **Pinned ≠ enforced.** A pin in no suite never runs; check the count moved. (The suite-membership lesson.)
5. **Documented ≠ true.** Roughly a third of a plausible external blueprint was falsified by reading the code (Finding 0-G). Documents are testimony; code is evidence.
6. **Zone label ≠ completion rate.** Weakest-link rollups understate; quoting them as progress metrics misleads in both directions.
7. **Acceptance ≠ comprehension.** Never quote an acceptance metric without its identity metric; use faithful / fabricating / refused — never two buckets.

---

## 6. Depth allocation for Phase 3

Full-depth descent (every component gets a full card): serving-path truth behavior (M4 + the M3 serve seam), the two-grammars frontier and the four ⚑ zero-subsystem zones, the learning boundary (M5's INV regime), M6's built footings and unbuilt center, and everything carrying a `fitness` verdict other than `fit`.

Cite-and-summarize (short card pointing at the acceptance packet): closed arcs with ratified acceptance evidence (deduction bands v1–v6, cohesion ADR-0241/0242, GSM8K sealed-lane machinery), unless Phase 2 surfaces a contradiction — in which case they promote to full depth.

The rule's purpose is honesty about attention, not economy for its own sake: a short card must say *why* it is short and what would reopen it.
