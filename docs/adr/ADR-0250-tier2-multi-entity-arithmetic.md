# ADR-0250: Tier-2 Multi-Entity Arithmetic — the Multi-Register Extension

**Status**: **Accepted**
**Date**: 2026-07-18
**Authors**: Joshua Shay + multi-model R&D (implemented Fable 5)
**Depends on**: ADR-0249 (reader→Hamiltonian compiler — quantity kernel, relation compiler, turn programs), ADR-0243/0244/0245 (relaxation, content-addressing, f64)
**Design record**: `docs/research/tier2-multi-entity-arithmetic-spike-2026-07-18.md`
**Acceptance evidence**: `docs/handoff/ADR-0250-Acceptance-Evidence.md`

---

## ERRATA (2026-07-18) — corpus mislabel corrected; status stays Accepted

This ADR calls the authored corpus the **"entire real GSM8K dev holdout."** That label is wrong: per
ADR-0119.2, `dev` (50) and `public` (150) are **CORE-authored, GSM8K-*style*** problems, **not** real
GSM8K. Read every "real GSM8K" reference here as **"CORE-authored GSM8K-style corpus (ADR-0119.2)."**

**Nothing about the Tier-2 mechanism is retracted** — the multi-register model, coupled-translator
transfers, the relative conservation hard-reject, prepare→validate→commit atomicity, the certified
summation turn, and the chain-of-custody all stand; the authored corpus is the mechanism-correctness
instrument and the 50/50 (200/200 across both ADRs) is exactly that evidence. Only the corpus label
falls. Measured real-GSM8K reach (spike `docs/research/dev2-frontier-measurement-spike-2026-07-18.md`):
reader parses 5/500, corridor 0/500 — reader-gated. Recorded here as the honest-measurement doctrine
catching its own mislabel.

---

## 1. What this ADR is

ADR-0249 closed Tier-1 (single-accumulator affine arithmetic) and recorded the 24 multi-entity
GSM8K dev-holdout cases as the Tier-2 frontier. This ADR crosses that frontier — and with it the
reader→Hamiltonian compiler solves the **entire** real GSM8K dev holdout (50/50) at wrong=0. It
extends the substrate mechanism only; no serving change, no gate activated, no manifold mutation.

## 2. The multi-register model

Multi-entity state is a **product of independent conformal lines**: one register (null point /
its own relaxation) per entity. This respects the Cl(4,1) boundary exactly — no dimensional
inflation (no `Cl(8,2)` to pack two points into one multivector), so the f64 rounding floor
(~6e-11) stays the only residual and every op is a native, exact versor action on a pure state.
Per-register ops (add/subtract/multiply/divide by constants) reuse the Tier-1 transport unchanged.

## 3. Transfers + the conservation pin

A constant-operand transfer ("actor gives `k` to target", ADR-0116 decomposition) is a **coupled
pair of translators** — `T₋ₖ` on the actor register, `T₊ₖ` on the target — acting on disjoint
registers, so exactness across the independent null points is inherited from ADR-0249 P1.

**Conservation pin (hard-reject, relative).** `Σ decode(after) ≡ Σ decode(before)` within
`|Δ| ≤ rtol·max(1,|before|)`. The tolerance is *relative* because decoded-quantity error scales
with magnitude (found on a case chaining to 222); an absolute tolerance is brittle, while a
genuine non-conserving transfer is off by a whole `k` and is still caught. A conservation failure
is an algebraic failure, not a scope miss — fail closed.

## 4. Transactional atomicity

Registers are an **immutable snapshot**. A transfer runs **prepare → validate → commit**: both
candidate states are relaxed into locals, validated (both converged AND conservation), then — only
on full success — a *new* register mapping is produced. A failure anywhere means the new mapping is
never built, so the original stands untouched: no partial-mutation window, no rollback. Records
append only on commit; any abort raises a typed `MultiRegisterError` and aborts the whole program
(fail-closed — a partial answer is never emitted, preserving wrong=0).

## 5. Certified summation + chain of custody

A total-like unknown (`unknown.entity is None`, "how many altogether") is the **explicit typed
signal** for a certified summation over all registers — never inferred from an operation pattern.
Per the summation ruling it stays in the substrate: each addition is a certified relaxation turn
(`T_v` on the running accumulator), never a Python `sum()`.

The operand of each summation turn is the decode of a certified register state, bound in the record
by `operand_source_digest` (the `psi_digest` byte convention). Deterministic re-execution
reproduces the state and its decode, so the Python layer cannot tamper with the intermediate value
— the chain of custody holds with no trusted-Python assumption. The field is added conditionally to
the record payload, so non-summation record digests are unchanged.

## 6. Honest measurement (done-when)

On the sealed real GSM8K dev holdout (50 cases): **50/50 solved, wrong=0** — Tier-1 (26) + T2a
single-entity (18) + summation (6). The instrument's `arithmetic-chain` domain routes each case to
the right tier and compares the corridor to a symbolic fold of the *same* compiled program: PARITY
(delta 0 — the field matches arithmetic, it does not beat it). The deliverable is a decidable
measurement + real-holdout coverage, per the honest-NULL protocol.

## 7. Scope + recorded frontier

Tier-2a: single-accumulator-per-entity affine + constant-operand transfers, positive scale,
matching units. 2b: the certified summation turn (real, exercised by the 6 total-like cases) and
the derived-operand-transfer path ("half of X" — designed + guarded, **0 on this holdout**). Still
refused and recorded: non-affine kinds (rate/comparison/fraction/partition — 0 on this holdout),
derived-operand transfers, and >5-atom deduction — never silently dropped.

## 8. Governance

Off-serving (A-04): `evals/multi_register_program.py` + the instrument domain; never imported by
`chat/runtime.py`. No gate activated; I-03 untouched; ratified contracts reused
(`compile_quadratic_well`, `quantity_kernel`, the Ring-2 chain pattern, `RelaxationCertificate`).
Local-first CI: smoke green in-worktree at every phase.

## 9. What this ADR does NOT claim

- Not a serving change; the symbolic `generate/` path remains the serve path.
- Not a lift over symbolic solvers on arithmetic (PARITY is the honest result).
- Not derived-operand-transfer coverage (0 on this holdout; designed + guarded only).
- Not an activation of any admission gate (ADR-0246 §3.7 stays uncalibrated).

## 10. Ruling record (Shay)

**RATIFIED 2026-07-18 by Joshua Shay — ADR-0250 ACCEPTED.** The design rulings (multi-register
product-of-lines; relative conservation hard-reject; prepare→validate→commit atomicity; certified
summation turn; ship 2b designed+guarded) are affirmed, citing the acceptance evidence pack
(`docs/handoff/ADR-0250-Acceptance-Evidence.md`) as-is. The full-holdout result — the
reader→Hamiltonian compiler solving the entire real GSM8K dev holdout 50/50 wrong=0 by chained
certified relaxation — is affirmed as the definitive outcome. Next arc: re-arm the measurement
(seal dev-holdout-2, a larger real GSM8K slice where the frontier kinds appear) and let the honest
coverage table pick the next capability tier; dev-1 stays pinned at 50/50 as a regression floor.
