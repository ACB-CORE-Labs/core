# Full-suite reds ledger — 2026-07

Operator: Grok-4.5 (W2 pre-existing reds sweep)  
Branch: `fix/pre-existing-test-reds-v2`  
Base: `forgejo/main` @ `54228d45`

## Enumeration

| Lane | Command | Result |
|------|---------|--------|
| Fast | `pytest -m "not quarantine and not slow" -n auto -q` | **5 failed**, 11660 passed, 106 skipped (pre-fix) |
| Fast recheck | same after fix | (see verification below) |
| Slow | `pytest -m "slow and not quarantine" -n auto -q` | **1 failed, 909 passed, 1 skipped, 1 xfailed** (37m06s, 2026-07-15 sweep @ `8f67590d`+#47). The 1 red = `test_public_showcase.py::TestRuntimeBudget` — stale constant pin (30) vs the deliberate 640dbe8f re-budget (60); fixed alongside this row. Slow lane is otherwise clean → the historical "~31 reds" figure is fully retired. |
| Full | `pytest -m "not quarantine"` | union of fast + slow |

The brief’s “~31 reds” appears to reflect an older main tip. On current `forgejo/main`, the **non-quarantine fast lane** surfaces **exactly 5** dedicated failures. Smoke/pack/lane gates stay green because they never execute these nodes.

## Red list and disposition

| # | Test | Class | Cause | Disposition |
|---|------|-------|-------|-------------|
| 1 | `tests/test_deductive_entailment_authority_demo.py::test_inv21_and_inv29_allowlists_are_unchanged` | (b) pin drift | Demo pin omitted ADR-0241 writer `core/physics/holographic_vault.py` already on canonical INV-21 allowlist | **Fixed test** — pin updated to match `ALLOWED_VAULT_WRITERS` |
| 2 | `tests/test_proof_carrying_promotion_demo.py::test_inv21_and_inv29_allowlists_are_unchanged` | (b) pin drift | Same as #1 | **Fixed test** — same pin update |
| 3 | `tests/test_engine_loop_proof.py::test_generated_final_state_satisfies_versor_condition_by_construction` | (b) producer | `_recall_state` called `rotor_power` on mixed-parity transitions (multi-token even field ↔ grade-1 vault hit → odd unit versor). Exact `rotor_power` correctly refuses non-rotors | **Fixed producer** — `generate/stream.py` skips non-powerable weighted hits (`try/except ValueError`) |
| 4 | `tests/test_register_pack_convivial_v1.py::test_runtime_chat_turn_idx_distinct_under_convivial` | (b) producer | Session anchor pull called `rotor_power` on non-rotor transition during `finalize_turn` | **Fixed producer** — `session/context.py` skips pull when power fails |
| 5 | `tests/test_session_coherence.py::test_session_anchor_pull_output_satisfies_versor_condition` | (b) fixture + producer | Test used even-grade `_random_rotor` against grade-1 anchor (mixed parity); also needs producer guard | **Fixed test fixture** to grade-1 reflector + producer guard in #4 |

## Classification key (from brief)

- **(a)** stale committed artifact → regenerate via sanctioned generator  
- **(b)** telemetry/schema/pin drift → fix test if wrong, else producer  
- **(c)** genuinely broken capability → quarantine + ledger owner-thread  

No **(a)** artifact regens and no **(c)** quarantines in this sweep. `QUARANTINE` remains empty.

## Root-cause notes

### INV-21 allowlist pin drift
Canonical allowlist lives in `tests/test_architectural_invariants.py` and already includes holographic vault (ADR-0241). Two demo “unchanged” pins were stale copies.

### Mixed-parity `rotor_power` calls
- Multi-token `inject` yields **even-grade** field states.  
- Single-token vault entries are often **grade-1**.  
- `word_transition_rotor(A,B) = B * reverse(A)` between different parities is a **unit odd versor**, not a rotor.  
- Historical `rotor_power` returned identity for non-simple cases (silent no-op). Exact power fail-closes; callers must not crash the cognitive path.  
- Guard matches existing `word_transition_rotor` `ValueError` continue/return pattern. **No assertion weakened; algebra fail-closed kept.**

## Owner-thread follow-ups (non-blocking)

| Thread | Why |
|--------|-----|
| Grade-parity policy for field vs vault entries | Soft-weighted recall currently *skips* mixed-parity hits; a future design may map grade-1 hits into even motors or store multi-token finals consistently |
| Demo allowlist pins | Prefer importing/asserting equality against the single canonical frozenset to prevent re-drift |

## Hard-rule checklist

- [x] Never weakened an assertion to pass  
- [x] Never deleted a test  
- [x] No wrong=0 surface touched  
- [x] No lane-pin artifact regen (N/A)  
- [x] Did not edit `.github/workflows/`, `core/physics/chiral_gate.py`, or `core/physics/goldtether.py`

## Verification (record at ship)

```text
[Verification]:
  targeted fixed reds + modules: 10 passed
  python scripts/verify_lane_shas.py: 9/9 match pinned SHAs
  uv run core test --suite smoke -q: 175 passed
  pre-fix fast lane enumerate: 5 failed / 11660 passed / 106 skipped
  post-fix: those 5 green; no quarantine entries added
```
