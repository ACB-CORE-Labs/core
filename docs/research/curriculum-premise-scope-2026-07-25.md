# Curriculum premise scope, negative rows, and band ceilings — measurements

**Date:** 2026-07-25 · **Arc:** curriculum-license-loop Phase A ·
**Decision record:** `docs/adr/ADR-0264-negative-curriculum-and-premise-scope.md`
**Base:** main @ `6ada6f7a`

Four probes, run against a clean tree on canonical Python 3.12.13. Each is
self-contained and reproducible; probe 2 mutates a corpus file and restores it,
asserting byte-identity at the end. Written down because the numbers reverse two
decisions in the plan of record, and a claim that reverses a plan needs to be
re-runnable by whoever doubts it.

Run from a worktree root with `uv run python <file>`.

---

## Probe 1 — negation reaches REFUTED, with correct atom identity

**Question.** The verb band reads three negation shapes. Does a negated premise
mint *the same atom* as the affirmative question it should refute? If the verb
agreement normalizes `does not require` to a different atom than `requires`, the
ROBDD returns UNKNOWN and every authored negative is silently inert.

```python
from generate.proof_chain.verb import read_verb_argument, VerbArgument
from generate.proof_chain.entail import evaluate_entailment_with_trace

POS = ["conservation requires symmetry", "mass requires force"]
QUERY = "conservation requires asymmetry"

CANDIDATES = {
    "A does-not (base verb)": "conservation does not require asymmetry",
    "B does-not (3sg verb)":  "conservation does not requires asymmetry",
    "C sentential-not":       "it is not the case that conservation requires asymmetry",
}

for label, neg in CANDIDATES.items():
    argument = ". ".join(POS + [neg]) + f". Therefore {QUERY}."
    arg = read_verb_argument(argument)
    if not isinstance(arg, VerbArgument):
        print(f"{label:26s} UNREADABLE -> {arg}")
        continue
    tr = evaluate_entailment_with_trace(arg.premise_formulas, arg.query_formula)
    print(f"{label:26s} outcome={tr.outcome.value:9s} reason={tr.reason!r}")
    print(f"{'':26s} premises={arg.premise_formulas}  query={arg.query_formula!r}")
```

**Result.** All three reach `refuted` / `tautological_refutation`, with
`premises=('a0', 'a1', '~(a2)')` against `query='a2'` — same atom, negated.
Agreement normalization is not an obstacle; shape B works despite being
ungrammatical.

**Bearing.** ADR-0264 R2 picks shape C, on the grounds that shape A needs a
de-inflection table that does not exist and shape B depends on an accident.

---

## Probe 2 — the premise cap collapses the band at 17 chains, and `polarity` is ignored

**Question.** Two at once. (a) What happens to a band when the family exceeds
`MAX_PREMISE_SENTENCES = 16`? (b) What does a row carrying
`"polarity": "negative"` actually serve today?

Appends synthetic-but-admissible negative rows to the real physics corpus —
`en_physics_v1` lemmas, `review_status: reviewed`, `connective: requires`, so
they survive `load_curriculum` admission — then asks the real decision path.

```python
import json, sys
from pathlib import Path

CORPUS = Path("teaching/domain_chains/physics_chains_v1.jsonl")
ORIG = CORPUS.read_text(encoding="utf-8")

sys.path.insert(0, ".")
from evals.curriculum_serve.oracle import vocabulary
vocab = sorted(vocabulary("physics"))
print(f"physics vocabulary = {len(vocab)} lemmas: {vocab}")

def row(n, subj, obj, polarity):
    return json.dumps({
        "chain_id": f"physics-modal-neg-{n:03d}", "domain": "physics",
        "operator_family": "modal", "subject": subj, "intent": "verification",
        "connective": "requires", "object": obj,
        "subject_pack_id": "en_physics_v1", "object_pack_id": "en_physics_v1",
        "review_status": "reviewed", "polarity": polarity,
        "provenance": "probe:phase-a:2026-07-25",
    })

taught = {(r["subject"], r["object"]) for r in map(json.loads, ORIG.strip().splitlines())}
cands = [(s, o) for s in vocab for o in vocab if s != o and (s, o) not in taught]

for n_neg in (1, 7, 8, 20):
    rows = [row(i, s, o, "negative") for i, (s, o) in enumerate(cands[:n_neg], 1)]
    CORPUS.write_text(ORIG.rstrip("\n") + "\n" + "\n".join(rows) + "\n", encoding="utf-8")
    for mod in [m for m in list(sys.modules) if m.startswith(("teaching.", "chat.", "evals."))]:
        del sys.modules[mod]
    from teaching.curriculum_premises import load_curriculum, compile_premises
    from chat.curriculum_surface import decide_curriculum_question
    load_curriculum.cache_clear()
    prem, _ = compile_premises(load_curriculum("physics"), "modal")
    s, o = cands[0]
    d_neg = decide_curriculum_question(f"Does {s} require {o}?")
    d_pos = decide_curriculum_question("Does conservation require symmetry?")
    print(f"\n+{n_neg:2d} negative rows -> modal premises={len(prem)}")
    print(f"    negative pair ({s} requires {o}): verdict={d_neg.verdict!r} reason={d_neg.reason!r}")
    print(f"    taught positive:                  verdict={d_pos.verdict!r} reason={d_pos.reason!r}")

CORPUS.write_text(ORIG, encoding="utf-8")
print("\ncorpus restored:", CORPUS.read_text(encoding="utf-8") == ORIG)
```

**Result.**

```
physics vocabulary = 16 lemmas
+ 1 negative rows -> modal premises=10   negative pair='entailed'   taught positive='entailed'
+ 7 negative rows -> modal premises=16   negative pair='entailed'   taught positive='entailed'
+ 8 negative rows -> modal premises=17   negative pair='declined'   taught positive='declined'
                                          reason='compiled_premises_unreadable'
+20 negative rows -> modal premises=29   both 'declined'
corpus restored: True
```

**Bearing, (b) first because it is worse.** At +1 row the question the negative
was authored to refute answers **`entailed`** — surfaced to a user as *"Yes — my
physics curriculum teaches that acceleration requires charge, directly."* The
`polarity` field is read by nothing. `evals/curriculum_serve/oracle.py` ignores
it too, so lane gold agrees with the wrong answer and `wrong=0` stays green. This
is ADR-0264 Fact 1 and it is the reason Phase A had to precede Phase F.

**Bearing, (a).** At 17 chains the band stops answering everything, including the
taught positive that works today. ADR-0262 §5.1 prescribes ≈219 chains per
band; ADR-0262 §6 scopes the cap out as a future contingency. The remedy trips
the deferred fix at row 17. ADR-0264 §4.1.

Also confirms `physics · modal` holds **9** chains, not 8: `physics-causal-008`
declares `operator_family: causal` but its connective is `requires`, and
`CONNECTIVE_FAMILY` is the sole family authority. That is where the plan's `n=9`
came from.

---

## Probe 3 — narrowed premise scope is verdict-identical

**Question.** ADR-0262 §6 proposes compiling "the query's k-hop neighborhood"
and argues it is sound because "fewer premises can lose an entailment, never
create one." Sound is not the property needed — a narrowing can be sound while
silently losing true entailments, which is coverage loss in exactly the class the
license counts. Is there a scope that is verdict-*identical*?

Compares two candidate scopes against full-family compilation over every
routable question in all four served domains (philosophy_theology sampled to its
first 40 lemmas to stay tractable).

```python
from teaching.curriculum_premises import CONNECTIVE_FAMILY, load_curriculum
from chat.curriculum_surface import SERVED_DOMAINS
from generate.proof_chain.verb import read_verb_argument, VerbArgument
from generate.proof_chain.exist import read_exist_argument, ExistArgument
from generate.proof_chain.entail import evaluate_entailment_with_trace, Entailment

VERDICT = {Entailment.ENTAILED: "entailed", Entailment.REFUTED: "refuted",
           Entailment.UNKNOWN: "unknown", Entailment.REFUSED: "declined"}

def decide(premise_sentences, conclusion):
    if not premise_sentences:
        return "EMPTY_SCOPE"
    argument = ". ".join(premise_sentences) + f". Therefore {conclusion}."
    arg = read_verb_argument(argument)
    if not isinstance(arg, VerbArgument):
        arg = read_exist_argument(argument)
        if not isinstance(arg, ExistArgument):
            return "unreadable"
    return VERDICT[evaluate_entailment_with_trace(arg.premise_formulas, arg.query_formula).outcome]

fam_conn = {}
for c, f in CONNECTIVE_FAMILY.items():
    fam_conn.setdefault(f, []).append(c)

total = mismatch_ti = mismatch_qa = empty_qa = 0
for domain in SERVED_DOMAINS:
    cur = load_curriculum(domain)
    vocab = sorted(cur.vocabulary)
    if len(vocab) > 40:
        vocab = vocab[:40]
    for family, conns in fam_conn.items():
        chains = cur.family(family)
        if not chains:
            continue
        for connective in conns:
            for s in vocab:
                for o in vocab:
                    if s == o:
                        continue
                    concl = f"{s} {connective} {o}"
                    full = [c.sentence for c in chains]
                    ti = [c.sentence for c in chains if c.subject in (s, o) or c.obj in (s, o)]
                    qa = [c.sentence for c in chains
                          if c.subject == s and c.connective == connective and c.obj == o]
                    v_full, v_ti, v_qa = decide(full, concl), decide(ti, concl), decide(qa, concl)
                    total += 1
                    if v_ti != v_full and v_ti != "EMPTY_SCOPE":
                        mismatch_ti += 1
                    if v_qa == "EMPTY_SCOPE":
                        empty_qa += 1
                    elif v_qa != v_full:
                        mismatch_qa += 1

print(f"questions compared        : {total}")
print(f"term-incidence mismatches : {mismatch_ti}")
print(f"query-atom mismatches     : {mismatch_qa}")
print(f"query-atom EMPTY scopes    : {empty_qa}")
```

**Result.**

```
questions compared         : 8520
term-incidence mismatches  : 0
query-atom mismatches      : 0     (over non-empty scopes)
query-atom EMPTY scopes    : 8463
max premises, full-family  : 9
max premises, term-incidence: 8
```

**Bearing.** Verdict-identity holds for any scope that is a superset of the
query-atom rows, because every compiled premise mints one *independent*
propositional atom and no other atom appears in the query formula. That exact
condition is ADR-0264 R5 — stronger than §6's soundness argument and the reason
narrowing here is not the ADR-0261 §5.1 premise-dropping failure.

8,463 of 8,520 (99.3%) have an empty query-atom scope. Those must return UNKNOWN,
not the current `empty_curriculum` refusal — ADR-0264 R6. The same 99.3% is the
quantified UNKNOWN-padding exposure that Phase B's mix floor has to bound.

---

## Probe 4 — band ceilings against the licensing threshold

**Question.** A question routes only if exactly one served subject's vocabulary
contains both terms. So honest volume is bounded by *vocabulary*, not corpus
size. Which bands can reach n ≥ 657?

```python
from collections import Counter, defaultdict
from teaching.curriculum_premises import CONNECTIVE_FAMILY, load_curriculum, compile_premises
from chat.curriculum_surface import SERVED_DOMAINS

fam_conn = defaultdict(list)
for c, f in CONNECTIVE_FAMILY.items():
    fam_conn[f].append(c)

vocab = {d: load_curriculum(d).vocabulary for d in SERVED_DOMAINS}
owner = Counter(t for d in SERVED_DOMAINS for t in vocab[d])

routable = {}
for d in SERVED_DOMAINS:
    excl = {t for t in vocab[d] if owner[t] == 1}
    routable[d] = sum(1 for s in excl for o in excl if s != o)
    print(f"{d:22s} |V|={len(vocab[d]):4d} exclusive={len(excl):4d} routable={routable[d]:6d}")

for d in SERVED_DOMAINS:
    cur = load_curriculum(d)
    for f in sorted(fam_conn):
        n_chains = len(compile_premises(cur, f)[0])
        if not n_chains:
            continue
        cap = routable[d] * len(fam_conn[f])
        print(f"curriculum_{d}_{f:12s} chains={n_chains:3d} max_honest_n={cap:6d} "
              f"{'reachable' if cap >= 657 else 'IMPOSSIBLE'}")
```

**Result.** 8 of 11 bands are structurally unable to reach 657 — including
`curriculum_physics_modal` (480), the plan of record's chosen first content
target. Full table in ADR-0264 §4.2.

```
physics              |V|=  16 exclusive=  16 routable=   240
mathematics_logic    |V|=  16 exclusive=  15 routable=   210
systems_software     |V|=  16 exclusive=  15 routable=   210
philosophy_theology  |V|= 151 exclusive= 149 routable= 22052
```

**Bearing.** `physics · modal` was chosen for having the most ratified chains.
Chain count is not the constraint. Its 480 ceiling counts *every possible
question* and still falls short, and no amount of authoring raises it — only
growing `en_physics_v1` would. `philosophy_theology · modal` has the same 8-chain
start and a 44,104 ceiling. ADR-0264 §4.2 retargets Phase F accordingly.

Cross-check against ADR-0262 §5.1, which computed the question space as
`|V|² − |V|` and got physics 240 (identical) and philosophy_theology 22,650
(vs 22,052 here). The difference is that this probe excludes lemmas taught by
more than one served subject, which `resolve_domain` refuses as
`ambiguous_reading`. 22,052 is the tighter and correct figure; §5.1's arithmetic
was right and its bound slightly loose.

---

## What these four probes jointly establish

A taught edge yields exactly one `entailed` question, so entailed cases available
= chains in the family. The cap holds that to ≤16. Against n ≥ 657 committed, a
license therefore needs a ledger ≥ 97.6% non-entailed — which ADR-0262 §5.1
already rules unacceptable, and its ⅓-entailed target caps committed volume at
48.

**So no curriculum band can earn a SERVE license as the architecture stands**,
and the blocker is engineering (premise scope), not content. That inverts the
conclusion two arcs closed on. Probe 3 is the unblock: it shows the narrowing
that removes the ceiling costs nothing in verdict fidelity.
