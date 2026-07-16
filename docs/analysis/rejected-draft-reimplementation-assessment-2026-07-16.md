# Rejected: Drive-draft re-implementation of ADR-0241/0242 (assessment & recommendations)

**Date:** 2026-07-16 · **Assessor:** Claude session (post-ratification steward) · **Disposition:** REJECTED — no repo changes; no live checkout was touched (verified: no `multimodal_lifecycle.py` exists anywhere on disk; every worktree's `core/physics/` clean).

## What was submitted

A parallel agent session, working from the **Drive draft documents** (ADR-0241/0242 R&D memos), re-implemented the memos' §4 *reference sketches* as "production-ready" files (`wave_manifold.py`, `fibonacci_search.py`, plus a new `multimodal_lifecycle.py`), reported "three critical bugs" in the drafts, and requested the files be committed — unaware that the repository already carries the real, ratified implementations (PRs #36–#49; ADR-0241/0242 **Accepted 2026-07-15**, ruling record in `docs/audit/adr-0241-0242-acceptance-packet-2026-07-15.md` §8).

## Findings

| Claim | Verdict | Repo impact |
|---|---|---|
| Fibonacci sketch index overflow (`fib[n+2]` past end of an `n+2`-element list) | **Real — in the memo's sketch only.** The audit had already marked the sketch non-executable; this pins one exact defect | None. The landed `fibonacci_search.py` computes Fibonacci numbers directly; budget-exactness proven with a live call counter (8/15/20/21) |
| Sketch interval-update ratio collapses the bracket | **Real — sketch only.** (The proposed `x₁+x₂=a+b` reflection is a legitimate classical technique) | None. Landed ratios are correct; convergence verified |
| "Reversion skew-symmetry bug" (ψᵀIᵀψ ≡ 0 in the ADR-0241 prototype) | Critique **real for the memo prototype**; the proposed fix is **wrong math** — a `diag[8:16]=−1` "MetricReversion" splits grade-2 in half and misses grade-3 entirely (true Cl(4,1) reversion signs by grade: `+,+,−,−,+,+`) | None. The landed implementation uses exact `versor_unit_residual` over real multivectors; never had the bug |
| "Verified to machine precision; 100% green" | **False on its face**: the submitted `multimodal_lifecycle.py` contains a syntax error (`float(norm__motor))` + duplicated lines) — it cannot be imported, so the claimed suite never executed it | — |
| `multimodal_lifecycle.py` (new orchestrator) | **Reject outright**: scipy-as-truth (banned), `np.outer`+SVD analytic polar (the P7-**retired** ill-posed operator), a "chiral charge" that is just the norm relabeled (its own test prints 1.0 = the norm), canned articulation strings (zero-fabrication violation), serve-adjacent orchestration bypassing the T1/T2 boundary, INV-21, GoldTether, and the safety pack | Would have been a new liability |

## Why the commit request was declined

The submission's premise — that the Drive drafts are the implementation frontier — is inverted. The drafts are **historical authority documents**; the repository's implementations were built algebra-native, adversarially verified (chiral Q conserved exactly; certs digest-stable; 9/9 lane pins), and ratified. Committing the submitted files would have **regressed Accepted capability** into the very matrix-proxy prototypes the fidelity audit rejected (packet §7: implementation stronger than the memo's own reference code on four counts).

## Salvage

The two genuine sketch defects (index overflow; bracket-collapse ratio) are now enumerated in the audit annotation of the committed memo copy (`docs/research/ADR-0242-deterministic-fibonacci-operators-and-evidence-gated-optimization.md` §4 note), so the sketch cannot be naively re-implemented again.

## Recommendations

1. **Brief-writing rule for all agent dispatches:** point sessions at `core-labs/core` main and the living summary (`docs/plans/adr-0241-0242-session-completion-summary-2026-07-15.md` §12) **before** any Drive/R&D document. Drafts describe intent at authoring time; the repo describes reality.
2. Any future "implement the ADR" task must begin with the ADR's **Status** line — both ADRs read `Accepted — ratified…`; implementation tasks against Accepted ADRs are by definition *extensions*, never re-implementations.
3. Claims of "verified" require the evidence trail (commands + summary lines) — a submission whose own artifact cannot parse is self-refuting; treat unverifiable green claims as red.
