# MG — Governance & Identity (cross-cutting)

**Kind:** layer (cross-cut) · **Parent:** CORE · **Assessor:** Opus 5 (Phase 2)
**Verified at:** `8927c563` (2026-07-27)
**Liveness:** `live-serving` · **Fitness:** `fit` (with one `strained` region) · **Topology role:** runtime boundary + reviewed pack data

> Who the system is, and what it will not do. MG is cross-cutting because a governance mechanism obeyed by only one layer is not governance — it is a feature. Its philosophical charge is the alignment thesis stated geometrically: keep behavior inside an intended region of possibility space *by construction*, so that alignment is a structural property of the manifold rather than a filter applied to output. The load-bearing asymmetry is that identity and ethics are swappable while safety is not.

**Telos stages:** articulate (governs the served surface), replay/determinism (verdicts are evidence)
**Macro role:** Constrains every layer's behavior to an identity- and safety-consistent region, and refuses in typed form when it cannot.

---

## What it is / What it does

Four pack families with deliberately different mutability. **Safety** (`packs/safety/`) is **never swappable and fail-closed** — five boundaries present in every manifold; a `SafetyVerdict` violation produces a deterministic typed refusal. **Identity** (`packs/identity/`) is swappable; ship default `default_general_v1`; the manifold is loaded from `packs/identity/<pack_id>.json`. **Ethics** (`packs/ethics/`) is swappable with opt-in typed refusal. **Register/anchor-lens** packs shape expression without moving truth.

Identity scoring is **wave-only and fail-closed** (ADR-0244 §3, INV-32): `IdentityCheck.check(trajectory, manifold, wave_field=...)` requires an explicit Cl(4,1) wave field; absence raises typed `MissingWaveStateError`, malformed fields raise `ValueError`, and the scalar-L2 dual-mode fallback has been **excised** and may not be reintroduced. Crucially, live *refusal* remains flag-gated (`identity_wave_gate`, default **off**, explicitly *not authorized*) — the flag controls refusal only, never the scoring path.

The identity contract is protective in both directions: a flagged score must not silently erase useful generation absent an explicit, tested hard-block policy; and **identity-manifold mutation by user prompt or correction is forbidden**, with identity-override attempts *rejected, not learned*. Adversarial override probes are seeded before the concepts they protect (`docs/teaching_order.md` layer 1).

---

## Contract

- **Inputs:** trajectory + final wave field from M3/M4, mounted identity/safety/ethics/register packs, session identity path.
- **Outputs:** `IdentityScore` (with `flagged`), `SafetyVerdict`, `EthicsVerdict`, typed refusals, hedge injection, `TurnVerdicts`.
- **Invariants:**
  - **INV-32** — identity scoring is wave-only; no scalar-L2 fallback exists — pins: `tests/test_stage2_physics_hardening.py` (excised symbols absent), `tests/test_adr_0244_identity_gate_runtime.py`.
  - Identity manifold is never mutated by prompt or correction; override attempts rejected, not learned.
  - Safety pack is never swappable; violation → deterministic typed refusal.
  - Hedge injection is exclusive with refusal (never both).
  - No epistemic seal: no `final`/`frozen`/`axiom`/`permanent` flag may exist (shared with M1's non-hardening invariant).

---

## Design vs build

- **Design:** ADR-0027 (identity packs), ADR-0244 (wave-field identity manifold and inalienable geometric alignment), ADR-0246 (induced identity action and path integrity), ADR-0010 (identity physics — the mind-physics blueprint element that *did* land), ADR-0220 (engine identity split from build provenance), `docs/identity_packs.md`, `docs/safety_packs.md`, `docs/ethics_packs.md`, `docs/refusal-taxonomy.md`, `docs/position_paper.md` §6.
- **Build:** `live-serving`. Key files: `packs/safety/check.py`, `packs/identity/loader.py`, `packs/ethics/check.py`, `core/physics/identity.py`, `core/physics/identity_manifold.py`, `core/physics/identity_action.py`.
- **Evidence:**
  - Safety and identity are constructed and consulted on the live serving path — code-read — `chat/runtime.py:93,104-105` (`load_identity_manifold`, `SafetyCheck`, `load_safety_pack`) — would-fail-if-absent: **yes**.
  - Scalar-L2 fallback is excised and its absence is pinned — pin — `tests/test_stage2_physics_hardening.py` — would-fail-if-absent: **yes** (a reintroduced symbol fails the pin).
  - Identity protection under adversarial input is claimed and evidenced in `docs/position_paper.md` §4 with an eval lane (`evals/identity_divergence/`) — lane.
  - Three merged authority demos (claims / proposed tool actions / epistemic-state assignment) — `docs/position_paper.md`, PRs #687/#688/#690.

---

## Capacity

- **Designed:** alignment as a structural property — the system cannot leave the intended region because the geometry does not admit it.
- **Measured:** identity scoring is metric-exact geometry (Gram / operator-preservation) on every turn; refusal is typed and taxonomized; five safety boundaries present in every manifold.
- **Ceilings:** **live identity *refusal* is off.** `identity_wave_gate` defaults `False` and is documented as "not authorized" — so identity currently *scores and flags* but does not *block*. Likewise `identity_action_surface=False` and `strict_identity_continuity=False`.

---

## Dependencies & provenance

**governs** → M4 (surface), M3 (what may be concluded), M5 (identity mutation forbidden); **reads** → M1 (packs), M0 (wave field, Gram geometry); **evidenced-by** → MV; **overlaps** → M6 (same-life continuity across reboot).

---

## Stage coverage

| Stage | Verdict | Evidence |
|---|---|---|
| articulate (governance of) | **covered** | Safety/ethics/identity consulted on the live path; typed refusal; hedge injection |
| *(identity enforcement)* | **claimed-only** | Scoring is live and fail-closed; **blocking is flag-gated off and unauthorized** |

**Zone roster:** `governance-identity-safety` (live-serving, **confirmed** by serving-path imports); `L9-epistemic-verdicts` ✱ (owned by M4, cross-referenced here).

**Rollup note:** the only macro layer besides M4 that the map rates `live-serving` at zone level, and re-verification supports it.

---

## Judgment

**Fitness: `fit`, with the enforcement region `strained`.** The design here is the strongest expression of CORE's alignment thesis: making safety non-swappable while identity and ethics are swappable is a genuine structural distinction rather than a policy label, and excising the scalar fallback outright — rather than deprecating it — is the correct response to a dual-mode hazard. The `strained` region is enforcement: the machinery is built, hardened, pinned, and **not switched on**.

**Honest wrinkles:**
- **Identity flags but does not block.** The gate is default-off and explicitly *not authorized*, which is an honest and deliberate posture — but it means the strongest claim in the alignment story ("behavior stays in the intended region") is, at runtime today, a *measurement* rather than a *constraint*. The distinction between scoring and refusing must be stated precisely wherever this capability is described externally; `runtime_contracts.md` does state it precisely, and this card records it so no downstream summary blurs it.
- Cross-cutting writ is asserted but not mechanically verified. I found no pin that would fail if some layer *bypassed* governance — as distinct from pins that verify governance works when called. For a cross-cutting layer that is the invariant that matters most, and its absence is the analogue of M1's unverified no-approximate-recall pin. Flagged for Phase 3.
- Safety's non-swappability is doctrine plus loader design; whether a *test* fails on an attempt to swap the safety pack was not verified at this SHA.
- MG is where CORE's most defensible public claims live. That makes precision about flag state a reputational as well as a technical obligation.

**Open questions:**
- Is there a pin that fails when a layer bypasses governance entirely? (→ Phase 3)
- Under what evidence should `identity_wave_gate` be authorized live? (→ ruling)
- Is safety-pack non-swappability mechanically enforced or loader-conventional? (→ Phase 3)
