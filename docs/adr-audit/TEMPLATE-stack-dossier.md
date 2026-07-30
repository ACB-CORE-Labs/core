<!--
TEMPLATE — one file per Tier A stack (foundational zones, contested findings, or phased
families with ≥4 files). Tier A gets this fuller treatment instead of the plain per-ADR
card because these are the load-bearing ones — a wrong verdict here is expensive.

Delete this comment block in the filled copy.
-->

# Stack dossier — <zone/family name>

**Zone(s):** — (per `docs/assessment/02-layer-taxonomy.md`) | **Tier:** A
**Member ADRs:** — (list every number+suffix in this stack, in read order)
**Dossier author:** — | **`verified_at` SHA:** `——————`
**Prior evidence adopted, not re-derived:** — (cite any FA-N verdict, gap-register `G-N`, hindrance `H-N`, or layer/component card already covering this zone — read these FIRST, per §4 of the audit plan's evidence-source order)

---

## 0. Why this is one stack

What concept, module, or decision chain ties these ADRs together. If it's a phased family (e.g. `0073a–d`), state the arc in one line: what each variant added over the last.

## 1. Stack-level claim

What is this stack collectively trying to establish — the single sentence a reader should be able to state after reading all member ADRs. If any member ADR's claim is **falsifiable** (has a measurable criterion, the way ADR-0005/0015's holonomy-closure claim did before FA-1), state the criterion explicitly here and treat it the way FA-1 did:

- **Pre-registered criterion:** —
- **Measurement performed / already available:** — (cite the eval, or note "not yet measured — flag for a follow-on FA-style experiment")
- **Verdict:** GO / NO-GO / not yet measurable — <one line>

If nothing in the stack is falsifiable in this sense, say so and skip straight to §2.

## 2. Per-ADR sections

For each member ADR, use the full `TEMPLATE-adr-card.md` shape (§1 Content summary through §10 Evidence sources), as a `###`-level subsection here rather than a separate file. Repeat per member.

### ADR-XXXX[suffix] — <title>

<full card content per TEMPLATE-adr-card.md §1–§10>

### ADR-XXXX[suffix] — <title>

<...>

## 3. Stack-level synthesis

This section is why the stack exists as a unit instead of N independent cards — questions that only make sense once every member has been read.

- **Internal consistency:** do the member ADRs agree with each other? Any place a later variant silently contradicts an earlier one instead of explicitly amending it?
- **Cumulative build state:** across the whole arc, what fraction is actually built vs. scaffolded vs. ghost? A stack can look healthy ADR-by-ADR and still be a chain that stalled halfway.
- **Cumulative necessity/generality read:** does the *stack as a whole* introduce one coherent generalizable mechanism, or N narrow ones that happened to get built in sequence? This is the primary feeder for `22-consolidation-report.md` — a stack is a natural consolidation-cluster candidate in its own right.
- **Blast radius if this stack's central claim is wrong:** which other stacks/zones would need re-verdicting? (Mirrors the ADR-0005/0015 → FA-1 cascade-check this plan calls out by name — do this check explicitly for every Tier A stack, not just the one FA-1 already flagged.)

## 4. Stack-level findings (`AA-N`)

Roll up every `AA-N` raised in the per-ADR sections above, plus any that only became visible at the stack level (per §3). One line each.

- —

## 5. Evidence sources actually consulted (stack-wide)

- —
