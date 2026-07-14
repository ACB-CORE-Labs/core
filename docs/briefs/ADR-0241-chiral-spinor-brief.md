# Brief: ADR-0241 Non-Vacuous Chiral Spinor Charge (P8)

**For:** Antigravity / Gemini design + TDD  
**Status:** STOP POINT after P7 demotion  
**Branch:** `feat/adr-0241-0242-implementation` (PR #37)

---

## Takeoff

```bash
git fetch forgejo
git checkout feat/adr-0241-0242-implementation
git pull forgejo feat/adr-0241-0242-implementation
```

Read:

1. `AGENTS.md`
2. `docs/adr/ADR-0241-...md` (chiral charge row; #19 retirement)
3. `docs/research/third-door-blueprint-fidelity.md` W4 / #19 section
4. `core/physics/wave_manifold.py` — `chiral_charge`, `left_spinor_step`
5. `docs/briefs/P7_design_note.md` (honesty doctrine — do not invent theater)

---

## Problem

ADR claims non-vacuous \(\mathcal{Q}=\langle\psi I_5\widetilde{\psi}\rangle_0\).  
Today `chiral_charge` is **honest structural ~0** on real Cl(4,1) (even product × central \(I_5\) has no grade-0 for the #19 family). Tests lock conservation of ~0 and even-versor honesty.

P8 goal: either (A) a **non-vacuous spinor path** with informative conserved Q, without reviving vacuous #19 gate on even unit versors; or (B) **permanent demotion** of non-vacuous claim with ADR language + fidelity ⚪ RETIRED, if design proves impossible under real Cl(4,1) without complex/pair structure.

---

## Hard constraints

- Must **not** revive grade-5 gate on even unit versors (#19)
- Even field-state path stays honest (~0 or N/A)
- Spinor / odd-capable path: if non-vacuous, Q informative + conserved under left unitary \(R\)
- Algebra-native; no hot-path unitize; off-serve
- Prefer fail-closed / honest demotion over fake non-zero Q

## Design options to evaluate (pick one with proof sketch)

1. Pair-spinor / complex structure via central \(I_5\) as algebraic \(i\)
2. Even/odd split with grade-sensitive charge
3. Two-component left ideals in Cl(4,1)
4. Permanent demotion (document why real Cl(4,1) cannot host non-vacuous Q)

## RED tests (if implementing non-vacuous)

```text
test_chiral_charge_nonzero_on_designed_spinor_packet
test_chiral_charge_conserved_under_left_unitary_R
test_chiral_charge_still_honest_zero_on_even_unit_versor
test_goldtether_chiral_term_only_when_informative
```

If demoting: one behavioral pin that documents structural vacuity remains and ADR/fidelity language is honest.

## Out of scope

P9 contemplation seam, Rust, serve wiring, re-opening retired multi-grade analytic polar (P7).

## Success

Non-vacuous spinor Q **or** honest permanent demotion; W4 fidelity flipped under honest criterion; PR #37 updated on Forgejo.
