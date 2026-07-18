# ADR-0248: Integrity-Coordinated Handoffs — the Ring-3 Coordination Seam

**Status**: **Proposed** — pending explicit human ratification (no self-Accept)
**Date**: 2026-07-17
**Authors**: Joshua Shay + multi-model R&D (implemented Fable 5)
**Depends on**: ADR-0247 (Proposed — supplies the port decisions), existing epistemic/normative organs (`core/epistemic_state.py`)
**Preflight authority**: ADR-0246 preflight brief §9 (Ring 3)

---

## 1. What Ring 3 is — and what this ADR does and does not claim

The preflight fixes Ring 3's boundary in one sentence: **"Integrity
coordinates handoffs; it does not replace content-bearing cognition."** The
content organs themselves largely EXIST in CORE already:

| Ring-3 element (preflight §9) | Existing organ |
|---|---|
| Composition / bind–infer | proof-DAG substrate (`proof_chain`, PropositionGraph, EntailmentTrace), depth-1 composer, transitive-chain surface |
| Epistemic standing | `EpistemicState` (15 typed states) + `NormativeClearance`, live in every TurnEvent |
| Observe→learn (governed) | contemplation loop — proposal-only, replay-gated corpus extension |
| Discourse planning | response governance (`govern_response`, STRICT-only scaffold) + hedge doctrine |

What was MISSING is the coordination seam itself: nothing fused the
integrity-side evidence (the Ring-2 port decisions) with the content-side
standing into one typed decision at the handoff boundary. **This ADR builds
exactly that seam and nothing more.** It does not claim to deliver the Ring-3
*programme* (world-model, counterfactuals, full governed-learning loop) — that
remains open, honestly listed in §4.

## 2. Decision

`core/ports/integrity_handoff.py` — a pure coordinator
(`coordinate_handoff(chain, epistemic_state=…, normative_clearance=…) →
IntegrityHandoff`) producing `proceed | hedge | abstain`, with conjunctive,
strongest-restriction-wins fusion rules (pinned in
`tests/test_ring3_integrity_handoff.py`):

1. no port evidence / unverifiable replay chain → **abstain** (fail-closed);
2. any Ring-2 port abstained → **abstain**;
3. normative `violated`/`suppressed` → **abstain**;
4. normative `unassessable` → at most **hedge**;
5. weak epistemic standing (undetermined / unverified_possible /
   unverified_novel / ambiguous / contradicted / epistemic_state_needed /
   scope_boundary / computationally_bounded) → at most **hedge** — mirroring
   the existing hedge-injection doctrine: qualified content may still surface;
   only integrity violations silence a turn;
6. otherwise → **proceed**.

`IntegrityHandoff` is **content-free by type** (pinned: no surface/content/
text fields) — routing, per-port attribution, and digests only. It binds the
replay-chain tip digest and is itself content-addressed (`handoff_digest()`,
full SHA-256), so every routing decision is auditable back to every port's
recorded evidence.

## 3. Operational status

Observe-only and off-serving: no serve code consumes the coordinator yet.
Wiring it into discourse planning / response governance is a future,
flag-gated, byte-identical-off unit — subject to the same doctrine as every
identity-adjacent serve change (default-off, calibrated evidence, human
ratification).

## 4. Honestly open (the rest of the Ring-3 programme)

World-model construction; counterfactual binding at depth; the full
observe→learn consumption loop (ratify-vs-consume gap); discourse planning
beyond STRICT; semantic axis grounding (blocked on a positive §11-style result
— the current evidence is a validated NULL). None of these are diminished by
this seam existing; they now have a typed integrity boundary to hand through.

## 5. Consequences

Content cognition and integrity measurement stay separate powers: integrity
can silence or qualify a turn but can never write one, and content can never
bypass the conjunctive integrity floor — with the whole negotiation recorded
in tamper-evident, content-addressed form.
