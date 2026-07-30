# Batch 5 — Tier A Collision Cluster (0225×2, 0226×3) — REDO

**Verified against:** `main` @ `cbfc8ccb` | **Auditor:** Claude (main session, direct) | **Date:** 2026-07-29
The five collision files at numbers 0225/0226 (census audit IDs `0225~1/~2`, `0226~1/~2/~3`), audited together because the collision itself is the story. Findings: renumbered into the corpus sequence (see `20-finding-register.md`).

## Per-file (terse)

- **`0225~1`** (`ADR-0225-adr-corpus-hygiene.md`, Accepted 2026-06-30) — the numbering-governance ADR. Its own §Context documents dodging an 0201 collision and taking "the next available top-level ADR number after ADR-0224" — **but 0225 was already occupied** by `contract-residual-read-model` (dated 2026-06-22, eight days earlier). The collision-avoidance procedure failed at the very number it minted. Worse on the substance: the ADR's core mandate — every future runtime/packs/teaching/memory/replay/invariants ADR "must explicitly cite these standing anchors" in a Governance-citations section — has **zero adopters**: grep across all ~60 subsequent ADR files (0226–0265) finds no such section anywhere (several late ADRs cite invariants inline, e.g. 0254's "Preserves" header — the spirit survives ad hoc; the mandated mechanism was never once used). Build: n/a (governance). Liveness of the *rules*: the README/INDEX upkeep half is live (this audit itself repaired the index); the citation mandate is **dead on arrival**. `AA-497`, `AA-498`.
- **`0225~2`** (`contract-residual-read-model`, Accepted 2026-06-22, authored by an external "Antigravity" agent) — authorizes exactly one diagnostic-only PR. Build full: `generate/contract_residuals.py` exists; scope discipline (no serving behavior) consistent with the file living in `generate/` as a projection. Clean on its own terms.
- **`0226~1`** (`gsm8k-math-eval-corpus`, Accepted) — 200-case synthetic corpus. Build full: `scripts/generate_gsm8k_public_corpus.py` and `evals/gsm8k_math/verify_all.py` both exist. Unrelated by topic to its number-mates. Clean.
- **`0226~2`** (`ADR-0226-ratification.md`, "Accepted" 2026-06-22) — a bare ratification record whose target is `0226~3` (it authorizes "diagnostic-only `SearchGateDecision` over `ContractResidual`" — the practice-loop topic, not the gsm8k corpus). `generate/search_gate.py` + tests exist, consistent with the staged authorization. But see `AA-499`.
- **`0226~3`** (`residual-gated-practice-loop-v1`) — **status still reads `Proposed`** while its sibling ratification record says "accepted for staged implementation." One number, three unrelated files, and an intra-number record contradiction: the ratification doc and the ratified ADR disagree about the ADR's own status. `AA-499`.

## Findings rollup

- **`AA-497` 🟡** — ADR-0225(hygiene)'s mandated "Governance citations" section has 0% adoption across all ~60 subsequent ADRs; the corpus-governance decision most directly aimed at preventing record drift is itself an unenforced dead letter (no CI/lint check exists for it — verified no such check in `tests/` by name).
- **`AA-498` 🟢** — The hygiene ADR itself collided at its own number while documenting its collision-avoidance procedure; already visible in the census, recorded here with the §Context evidence so the eventual numbering cleanup cites the primary text.
- **`AA-499` 🟡** — `0226~3` reads `Proposed` while `0226~2` records it accepted-for-staged-implementation (both dated 2026-06-22, unreconciled since); the H-8 "two documents disagree about reality" pattern *within a single ADR number*.

**Severity tally: 0 🔴 / 2 🟡 / 0 🔵 / 1 🟢.**
