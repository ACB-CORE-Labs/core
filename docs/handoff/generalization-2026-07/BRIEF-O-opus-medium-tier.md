# Handoff Brief — Tier O (Opus 5, MEDIUM risk)

**Read first:** `docs/plans/generalization-arc-2026-07-24.md` (the plan of
record — §4 gold contract and §6 constraint set are binding), then
`AGENTS.md`. Reference ADRs on demand: 0256–0259 (band recipe),
0175/0199 (license doctrine), 0251/0252 (math-reader guardrails).

**You own, in order:**

1. **O1 — Band v6-EX (existential `some` witnesses).** Follow the band
   recipe exactly as ADR-0258/0259 executed it: reader module in
   `generate/proof_chain/`, shape bands in `shape.py`, surface wiring in
   `chat/deduction_surface.py`, arena templates ≥720/band in
   `evals/deduction_serve/practice/gold.py`, hand-authored lane split,
   ledger reseal, tests, ADR, research doc. Gotchas that bit before:
   cross-module `_Reject` identity (catch both classes); band-N swallows
   band-N+1 test texts (verify the prior band really refuses your
   declined cases); surgical single-line pin edits only (never
   `verify_lane_shas.py --update`).
2. **O2 — Phase 2 physics serve lane** per the §4 curriculum-entailment
   contract. Premises come ONLY from ratified domain chains
   (`teaching/domain_chains/physics_chains_v1.jsonl` + pack mounts);
   anti-recall probes (gold=UNKNOWN for true-but-untaught) are mandatory
   or the lane must not ship. Independent closed-world oracle first,
   then the lane. Biology second, only after O3 lands.
3. **O3 — generic consumption bridge**: extract the seal→ratify→
   SHA-verified-license→serve-gate pattern (models:
   `chat/deduction_serve_license.py`,
   `generate/determine/estimation_license.py`) into a reusable ADR-0175
   Phase-5 bridge so subject arenas plug in without bespoke wiring.
4. **O4 — math reader: seeding-sentence injection** (standing ruling
   #77 — the 75% "no injection" wall). Then compare unblock (4.2).
   Hard guardrails: no bespoke-per-case regex growth (ADR-0251); check
   every new pattern against
   `docs/research/reader-arc-overfit-inventory-2026-07-19.md`; measure
   on the frozen tune/measure split; wrong=0 on the full 500 is the
   gate, parse-rate gain is the goal.

**Constraints (non-negotiable):** wrong=0; all flags stay default-off —
flips are Shay's ratification only; Forgejo-primary (no `gh`); worktree
per unit off `forgejo-https/main`; fresh venv per worktree
(`rm -rf .venv && uv sync --locked --offline`, then `uv run --no-sync`);
pre-push hook runs smoke+warmed_session (~4.5 min — budget timeouts);
PRs opened by Shay via the compare URL the push prints (push PAT 403s
the PR API); Shay merges — never you; branch+worktree deleted after
merge; no timelines in any doc.

**Your exit checkpoint (O→S):** v6-EX merged; ≥1 subject lane serving
wrong=0 with earned licenses; bridge merged; math increment measured and
documented (a null result is a valid checkpoint). Then update
`BRIEF-S-sonnet-low-tier.md` with actual state, update memory, and stop
for the Sonnet handoff.
