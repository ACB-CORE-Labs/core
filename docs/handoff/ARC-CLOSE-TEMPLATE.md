# Arc-Close Brief — TEMPLATE

> Copy to `docs/handoff/<arc-slug>/BRIEF-CLOSE-<arc-slug>.md` when an arc ends.
> Delete every instruction block (`>`) as you fill it in.

## Why this template exists

The handoff system is mature in one direction only. `BRIEF-O` / `BRIEF-S` are
**downward** briefs: a planning tier telling an execution tier what to build.
Nothing goes back **up**. When an arc closes, the tier that actually executed it
holds the corrected ground truth — which assumptions were falsified, what the
flag state now is, which "next steps" the measurements killed — and that
knowledge currently survives only as commit messages and research docs, which
the next arc's opener must reconstruct by re-reading every ADR from the arc's
first number onward.

The generalization arc minted eight ADRs in roughly 48 hours. That is the
cadence this template is sized for: an opener should be able to start scoping
from **this one file** and reach for ADRs on demand, not as a prerequisite.

The single most important section is **Falsified assumptions**. A downward brief
states a plan; an arc-close brief states which parts of that plan turned out to
be wrong. That is the part which cannot be recovered from the diff.

---

# Arc-Close Brief — <arc name>

**Arc:** <slug> · **Closed:** <YYYY-MM-DD> · **Closing tier:** <Fable/Opus/Sonnet + risk tier>
**Plan of record:** `docs/plans/<plan>.md`
**ADRs minted:** <ADR-NNNN … ADR-NNNN>

## 1. What shipped

> One line per landed capability, each naming its enforcement site. Not commit
> messages — capabilities. A reader should be able to tell what the system can
> now do that it could not before.

| Capability | ADR | Enforcement site | Evidence |
|---|---|---|---|
| | | | |

## 2. Flag state at close

> The single highest-value table here. Every flag the arc touched, its default
> **now**, and what ratified it. A flag flipped ON is a live capability whose
> test suite is a regression suite — say so.

| Flag | Default at close | Ratified by | Notes |
|---|---|---|---|
| | | | |

## 3. Falsified assumptions

> **Do not skip this section.** For each: what the plan assumed, what the
> measurement showed, and where the evidence lives. An assumption that was
> merely *not reached* is not falsified — say "untested" and mean it.

| Plan assumed | Measurement showed | Evidence |
|---|---|---|
| | | | 

## 4. Binding constraint going into the next arc

> One paragraph. Not a list. If the next arc has one thing standing between it
> and progress, name it and quantify it. "Curriculum volume: every band is
> 24×–73× short of the entailed-bucket floor" is a binding constraint;
> "we should improve coverage" is not.

## 5. Trigger state

> For any phase the plan declared trigger-gated: is the trigger now met? Cite
> what met it. If met, say what the next tier must design **before** writing
> code — the design work that should land in a higher tier than the
> implementation.

## 6. What is NOT next, and why

> The most expensive thing an opener can do is resume a thread the closing tier
> already killed. List the plausible-looking next steps that the arc's own
> evidence rules out, each with its reason. Be specific enough that someone
> cannot re-propose them without engaging the evidence.

## 7. Open items carried forward

| Item | Kind | Where it is recorded |
|---|---|---|
| | deferred / blocked / untested | |

## 8. Gates and their state at close

> Local-first is the merge bar (`AGENTS.md`), so record what was actually run,
> with counts. "Green" without a count is not evidence.

| Gate | Command | Result at close |
|---|---|---|
| smoke | `uv run core test --suite smoke -q` | |
| deductive | `uv run core test --suite deductive -q` | |
| lane pins | | |

## 9. Ground truth corrections for the next opener

> Free text. The things you would say out loud if you could brief the next
> session in person — including anything in the plan of record that is now
> stale. If a comment in the code reasons from a premise that has since
> changed, name the file and line: that is exactly the class of staleness
> nobody greps for.
