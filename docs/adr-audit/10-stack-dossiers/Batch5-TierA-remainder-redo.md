# Batch 5 — Remainder Sweep (ADR-0201–0250, 37 files) — REDO

**Verified against:** `main` @ `cbfc8ccb` | **Auditor:** Claude (main session, direct) | **Date:** 2026-07-29
Covers the Batch-5 remainder after the three stacks already filed directly (`Batch5-TierA-cascade-redo.md` 0239/0240/0241/0243/0244/0246; `Batch5-TierA-collisions-redo.md` 0225×2/0226×3; `Batch5-TierA-misc-redo.md` 0237/0238). Method at this tier: a **corpus-wide Status-vs-build sweep across all 37** (the highest-yield mechanical check, given the pattern established in `Batch4-TierA-reader-reliability-redo.md`), plus targeted artifact verification on the load-bearing members. Findings: renumbered into the corpus sequence (see `20-finding-register.md`).

## The sweep result

Status distribution across the 37: **22 Accepted, 15 Proposed.** The 15 Proposed split cleanly into two *materially different* classes, and the distinction is the substance of this sweep:

**Class 1 — Proposed-with-nothing-built (correct, honest labelling).** ADR-0228, ADR-0229, ADR-0230, ADR-0231, ADR-0232, ADR-0233, ADR-0234, ADR-0235, ADR-0236 — nine consecutive design documents (`geometric-search-run-envelope`, `contract-proof-replay-adapter-boundary`, `sealed-practice-trace-boundary`, `first-candidate-operator-boundary`, `candidate-attempt-run-binding-boundary`, `bound-practice-episode-sealing`, `second-candidate-operator-selection`, `apple-silicon-uma-acceleration-lanes`, `engineering-principles-for-masterful-cleanup`). **Zero `tests/test_adr_02xx` files for any of the nine** — verified by directory scan. These are the descendants of `0226~3`'s residual-gated practice loop, correctly parked as an unbuilt design backlog. Plus ADR-0222/0223/0224, whose own status lines *state* the gating explicitly ("design-only. Implementation is gated behind…", "docs-only until ratified"). **This is the corpus doing it right** and it is the calibration baseline that makes Class 2 a real finding rather than a naming quibble. `AA-503`.

**Class 2 — Proposed-but-load-bearing.** ADR-0201 and ADR-0210/0216 (the latter two not deep-verified at this tier). ADR-0201 is the headline — see below.

## ADR-0201 — the `proof_chain` keystone at `Proposed`

Status line (its own words): *"Proposed (Phase 1 of `proof_chain`; standalone keystone shipped, not yet wired)"* — commendably self-aware about the wiring, still unratified. What has accumulated on top of it since:

- **ADR-0201.1 is `Accepted`** and describes itself as *"additive hardening of ADR-0201"* — a ratified document hardening an unratified one.
- **ADR-0202, 0203, 0204, 0205 are all `Accepted`**, each labelled a `proof_chain` phase (2.1 "the isolated guard", 2.2 "structure only", 2.3 "the first inference"). ADR-0202 calls itself a *"normative contract — single source"*.
- **`generate/proof_chain/` is now a 15-module package** (`builder`, `categorical`, `certificate`, `cond_member`, `engine_pin`, `english`, `entail`, `exist`, `member`, `model`, `render`, `rules`, `shape`, `verb`, `__init__`) and is **the live engine under all six Batch-6 deduction bands** (ADR-0256–0261, every one Accepted, collectively licensing 25 shape-classes at θ_SERVE=0.99 — independently recomputed in `Batch6-TierA-redo.md`).
- No `tests/test_adr_0201*` file exists (the canonicalizer's "not yet wired" claim is consistent with that; the *package* it keystones is heavily exercised through the band tests).

So the corpus's most load-bearing reasoning subsystem has an unratified Phase-1 keystone, one Accepted hardening of it, four Accepted phases built on it, and a fully-licensed serving arc downstream. `AA-504`.

## Accepted members — artifact verification (terse)

Test-file counts by ADR number (directory scan) and artifact existence:
- **Well-pinned:** 0242 (6 test files — Fibonacci recency constants; the `τ_n` schedule the assessment's CR-4 cites as "a constants schedule, not a clock"), 0249 (5), 0250 (4), 0219 (1 — the atomic generation-dir API ADR-0255 correctly builds on, verified in Batch 6), 0218 (1), 0245 (1), 0206 (1 — response-governance bridge; `generate/determine/` exists as INDEX claims).
- **Accepted with zero ADR-numbered test files:** 0207, 0208, 0209, 0211, 0217, 0220, 0221, 0227, 0247, 0248. Note this is *weak* evidence on its own — this corpus does not consistently name tests after ADRs (ADR-0165's enforcement lives in `test_lexeme_primitives.py`, not `test_adr_0165*.py`), so a zero here means "not traceable by naming convention," not "untested." Recorded as a traceability observation, not a defect. `AA-505`.
- **0207** is load-bearing beyond its own content: it is the *ratifier* of ADR-0164/0165/0174 (Batch 4) and, per their status lines, of 0208/0209 — a ratification hub whose own acceptance evidence isn't traceable by name.
- **0211** (environmental falsification, Accepted) — the CR-3 efferent-deferral anchor. Verified its §Context chain: ADR-0209 established sensorimotor feedback as *afferent* evidence; **ADR-0198 established real motor emission as fail-closed until a verdict-enforcing efferent gate exists.** So the assessment's CR-3 ("is action deferred or out of telos? today neither is stated") is *partially answered in the corpus already* — 0198+0211 constitute a fail-closed deferral with a named unblocking condition. Worth surfacing to whoever rules CR-3. `AA-506`.

## Findings rollup

- **`AA-504` 🔴** — The `proof_chain` keystone (ADR-0201) is `Proposed` while ADR-0201.1 (Accepted) hardens it, ADR-0202–0205 (all Accepted) build four phases on it, and its 15-module package is the live engine under all six Accepted, Wilson-licensed deduction bands. Same class as `AA-491` (ADR-0175) and jointly with it means **both** load-bearing pillars of the deduction-serve arc — the reasoning engine's keystone and the licensing regime's invariants — rest on unratified documents.
- **`AA-506` 🟢** — ADR-0198 + ADR-0211 already constitute an explicit fail-closed efferent deferral with a named unblocking condition ("until a verdict-enforcing efferent gate exists"), partially answering the assessment's open CR-3. Route to that ruling rather than re-deriving it.
- **`AA-505` 🟢** — Ten Accepted ADRs in this range have no ADR-numbered test file. Given this corpus's inconsistent test-naming (ADR-0165's pin lives in `test_lexeme_primitives.py`), this is an **evidence-traceability** gap, not a coverage claim: there is no reliable way to ask "what proves ADR-N?" by convention. A `Validation:`-section-to-test-path convention (which the better ADRs already follow voluntarily — 0254, 0255, 0181, 0197 all name their test files explicitly) would close it.
- **`AA-503` 🟢** — ADR-0228–0236 (nine files) plus 0222/0223/0224 are `Proposed` with zero implementation and self-describing gating language — the corpus's correct handling of an unbuilt design backlog, and the calibration baseline that makes `AA-504`/`AA-491` findings rather than pedantry.

**Severity tally: 1 🔴 / 0 🟡 / 0 🔵 / 3 🟢.**

**Coverage note, stated honestly:** this is a *sweep*, not 37 full 7-axis cards. Every one of the 37 was status-checked and classified; the load-bearing members (0201, 0206, 0207, 0211, 0219, 0242, 0249, 0250) were artifact-verified; ADR-0210, 0216, 0217, 0220, 0221, 0223, 0224, 0227, 0247, 0248 received status-and-existence checks only. At the charter's reduced-rigor tier this is the intended depth for a remainder sweep, but a future pass wanting per-ADR cards for that last group should not read this file as having produced them.
