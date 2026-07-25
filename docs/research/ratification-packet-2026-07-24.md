# Ratification Packet — `deduction_serving_enabled` and `curriculum_serving_enabled`

**Tier S1** (generalization-arc-2026-07-24 §6). Evidence collation only — the
flag flip is Shay's decision alone, never inferred from this document or from
approval of adjacent work. This packet has two independent sections: one
recording a decision already made, one recording why a decision has not been
made.

---

## 1. `deduction_serving_enabled` — RATIFIED ON (2026-07-24, main @ `5fd9a861`)

This section is a **record**, not an input to the decision. Shay ratified the
flag flip on 2026-07-24; the evidence below is what stood behind that
ratification, preserved for audit and for anyone rolling back or re-deriving
the decision later.

### 1.1 Sealed-practice ledger — 25 bands, 720/720 wrong=0 each

`chat/data/deduction_serve_ledger.json` (schema `deduction_serve_ledger_v1`,
provenance `evals.deduction_serve.practice.runner.seal_ledger`, content
`a056f899…`). The engine only *reads* this artifact — it is committed,
SHA-sealed, and never written by serving.

| # | classes | committed | correct | wrong | refused |
|---|---|---|---|---|---|
| 25 | see below | 720 each | 720 each | **0** | 0 |

Classes (25): `atomic`, `categorical`, `conditional_chain`,
`conditional_single`, `disjunctive` (Band v1/v1b) · `en_atomic`,
`en_conditional_chain`, `en_conditional_single`, `en_disjunctive` (Band
v2-EN, ADR-0257) · `en_member_atomic`, `en_member_chain`,
`en_member_negative`, `en_member_single` (Band v3-MEM, ADR-0258) ·
`en_condmem_chain`, `en_condmem_conditional`, `en_condmem_disjunctive`,
`en_condmem_fused` (Band v4-CM, ADR-0259) · `en_verb_chain`, `en_verb_fact`,
`en_verb_negative`, `en_verb_universal` (Band v5-VP, ADR-0260) ·
`en_exist_chain`, `en_exist_negative`, `en_exist_universal`,
`en_exist_witness` (Band v6-EX, ADR-0261).

### 1.2 Earned-license gate ceilings (ADR-0175 §4a, `core/reliability_gate/`)

`Action.SERVE` ceiling is θ=0.99 (`core/reliability_gate/ceilings.py`). The
floor is a pinned one-sided Wilson lower bound
(`core/reliability_gate/floor.py::conservative_floor`), deterministic and
replay-stable (no learned weights, no sampling). For a perfect record
(`successes == committed`) the bound reduces to
`committed / (committed + z²)` with `z = WILSON_Z = 2.576`; solving
`committed / (committed + z²) ≥ 0.99` gives `committed ≥ 99·z² ≈ 656.9`,
i.e. **n ≥ 657** — where the standing "n≥657 committed" figure comes from,
not a chosen round number. All 25 classes commit 720 ≥ 657 with a perfect
record, clearing the floor with margin.

### 1.3 Serve-lane results — production pipeline, independent gold

`evals/deduction_serve/report.json` runs the *exact* pipeline
`chat/deduction_surface.py` calls in serving (shape-gate → reader →
projector → ROBDD engine), scored against independently-authored gold —
**166/166 correct, 0 wrong, 0 declined**, across six splits:

| split | n | band |
|---|---|---|
| v1 | 28 | propositional / categorical |
| v2_en | 26 | English opaque-clause arguments |
| v2_member | 26 | singular-membership arguments |
| v2_condmem | 26 | conditional-membership fusion |
| v2_verb | 28 | verb-predicate arguments |
| v2_exist | 32 | existential arguments |

`wrong` staying 0 is the lane's non-negotiable gate (a decline is a coverage
miss, tracked but never conflated with a wrong answer); `all_correct=true`
confirms every committed case, not just the wrong-count, matches gold.

### 1.4 Commit gate — narrow by construction

`chat/deduction_surface.py::looks_like_deductive_argument` is a single
regex: a sentence-initial `"therefore"` conclusion clause
(`_ARGUMENT_CONCLUSION_RE`). This is a genuine signal of intent — text
shaped that way IS an argument — so the composer can commit on shape alone
without risking hijacking ordinary turns. (Contrast with curriculum's gate,
§2.4 below, which cannot use shape alone.) Once committed, every branch is
fail-closed (INV-34): a decided verdict, a typed reader refusal, or the
generic out-of-band surface — never a silent fall-through to a different
composer.

### 1.5 Blast radius (verified before the flip, not assumed)

- Deductive suite (`core test --suite deductive`) — 268 passed with the flag
  on.
- `chat/runtime.py::_maybe_pack_grounded_surface` — the deduction branch is
  checked **before** the empty-vault gate (unlike pack/teaching/partial/oov):
  a pure function of input text, independent of vault/field warm-or-cold
  state, so it cannot perturb any other dispatch path's preconditions. A
  claimed turn sets `grounding_source="deduction"`; every other path is
  reached exactly as before when the composer declines
  (`DispatchAttempt(source="deduction", outcome="skipped", ...)`).
- Lane pins (`scripts/verify_lane_shas.py`) stayed 10/11 across the flip —
  unchanged, i.e. the flip touched nothing any other pinned lane measures.

### 1.6 Rollback

One line: `deduction_serving_enabled: bool = True` → `False` in
`core/config.py`. Flag-off is byte-identical to pre-arc dispatch — pinned by
`tests/test_deduction_surface.py::test_flag_off_preserves_pack_token_gloss_byte_identity`.
No residue: the composer is a pure function gated entirely by the one flag
read at `chat/runtime.py:1748`; nothing it touches persists state.

### 1.7 Unearned shapes stay disclosed, not withheld

Every band above is licensed. A future band, or a deployment whose ledger is
stripped, still gets the sound ROBDD answer — served DISCLOSED via the
`_UNVERIFIED_SHAPE_DISCLOSURE` hedge (`chat/deduction_surface.py`), never
presented as verified. This is what makes serving an *earned* capability
rather than a merely flagged one, and it is why disclosure is not itself
evidence against ratifying a *licensed* band.

---

## 2. `curriculum_serving_enabled` — stays OFF (ADR-0262)

This section exists to make the non-decision as auditable as the decision
above: **every curriculum band is unearned**, so flipping this flag would
enable a capability that answers *disclosed*, never authoritatively — sound,
but with no demonstrated track record on the pipeline serving it.

### 2.1 Same shape of evidence, opposite conclusion

`evals/curriculum_serve/report.json`: physics lane **32/32 correct, 0 wrong,
0 declined**, `all_correct=true`, 5 anti-recall probes (≥ the §4.7 floor of
3). This is a clean lane pass — the mechanism is proven — but it says
nothing about *volume*, which is the actual gate.

### 2.2 Why no band can earn SERVE from present data (ADR-0262 §5.1)

The reliability floor (§1.2 above) needs **n ≥ 657 committed** per band, and
a band here is `(subject × relation family)` — e.g.
`curriculum_physics_causal`. Physics teaches 7 causal + 9 modal relations
total (§6 below has the full count), so **at most 16 questions in the
entire subject can ever come back `entailed`** — roughly 25× short of a
single band's floor, before even asking for a *mix* of entailed/refuted/
unknown outcomes (a real reliability claim needs more than one outcome
class repeated). This is a volume ceiling on the ratified curriculum, not a
defect in the reader, the bands, or the engine — all of which are the same
verified components §1 already licensed.

### 2.3 The ledger says it plainly

Every one of the curriculum bands present in a ledger would show `committed`
in the low tens, nowhere near 657. (No curriculum-specific sealed ledger
exists yet, precisely because sealing one at this volume would just
document the shortfall — see [[project-curriculum-grounded-serving]] and
S6, `docs/research/curriculum-volume-quantification-2026-07-24.md`.)

### 2.4 Commit gate — routability, not shape (ADR-0262 §5.3, already fixed)

Unlike deduction's `"therefore"` gate, curriculum's `"Does …?"` shape is not
itself a signal of intent — it is one of the most common ways to open *any*
English question. `chat/curriculum_surface.py::is_curriculum_question`
commits only when the question parses to three tokens AND both terms are
vocabulary some served subject actually teaches (`resolve_domain`); an
`untaught_vocabulary` refusal is explicitly **not** a claim (the composer
declines the turn entirely, byte-identical to before this composer
existed). This was a real defect found and fixed this arc (commit-gate
firing on any `Does …?` text, e.g. "Does the build pass?"); the fix is
already on `main` and is not part of what remains gated by this flag.

### 2.5 What flipping ON today would mean

Every served answer would carry the `_UNVERIFIED_SHAPE_DISCLOSURE` hedge —
"(answered from my curriculum, but I haven't yet earned a verified track
record on questions of this shape)" — because `_license_gate`
(`chat/curriculum_surface.py`) finds no `Action.SERVE` license for any
`curriculum_<domain>_<family>` band. The capability would be real and
sound (same argument bands, same ROBDD engine as §1) but never
authoritative. This is not unsafe to ship; it is simply not yet *earned*,
and the standing rule (Shay, 2026-07-24) is that a flag flips on earned
evidence, not on proximity to it — see
[[project-deduction-serving-ratified]].

### 2.6 Rollback / blast radius, for parity with §1.6

Same shape as deduction: one line in `core/config.py`
(`curriculum_serving_enabled: bool = False`, already the default — nothing
to roll back), checked immediately after the deduction branch in
`chat/runtime.py:1764`, pure function of text + ratified curriculum, no
vault/field dependency. Flag-off is byte-identical to pre-arc dispatch by
construction (the branch is dead code when the flag is False).

---

## 3. What would close §2 (evidence only — not a proposal to act)

Nothing in Tier S closes this gap; it closes only when ratified curriculum
content grows roughly 25× per served `(subject × family)` — a content
question for Shay, not an engineering one. See S6's quantification,
`docs/research/curriculum-volume-quantification-2026-07-24.md`, for the
per-subject arithmetic.
