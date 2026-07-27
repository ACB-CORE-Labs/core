---
name: ollama-offload
description: Offload bounded, checkable work to a local Ollama model at zero cost — classifying log lines, extracting fields from output you already hold, summarizing long logs, triaging which items deserve a real look. Use when facing bulk mechanical text work whose result you can verify. Not for reasoning, deciding, or writing code.
---

# Offloading to a local model

`ollama-offload` (in `.claude/bin/`) runs a local model against work whose
output space is small enough to check. It is free, runs offline, and takes
1–3 s per call.

## The rule that makes this safe

**A local model may point. It may never assert.**

Its output is stamped `SPECULATIVE` and must be treated as such: a pointer that
narrows where you look, never a fact you repeat. The moment you would quote its
output as a finding, you have crossed the line — go read the source it pointed at
and quote that instead.

This is the same learning boundary CORE already enforces on itself: provisional
state may move autonomously **iff** it is typed, isolated, replayable, and unable
to masquerade as ratified truth. Local-model output qualifies only while it stays
labelled.

## Before you reach for it: the absence test

Ask what happens **with the model removed**. If `rg`, `jq`, `sort -u`, or a
three-line script gets the same answer deterministically, use those — they are
faster, exact, and reproducible. A model is the wrong tool for work a grep can do.

Reach for the model only when the input is genuinely unstructured natural
language and the output is genuinely bounded.

## The four modes

Each is bounded by a JSON schema enforced at sampling time, so malformed output
cannot be produced — not merely rejected afterward.

```bash
# One label from a closed set. Highest trust: finite, checkable output space.
… | .claude/bin/ollama-offload classify --labels ImportError,AssertionError,Timeout,Other

# Named fields, verbatim, out of text you already hold.
… | .claude/bin/ollama-offload extract --fields test_file,test_name,error_type

# N bullets from a long log you are keeping. Lossy — the source stays authoritative.
… | .claude/bin/ollama-offload summarize --bullets 5

# Narrow a list to the items worth a real look. One item per line.
… | .claude/bin/ollama-offload triage --max 3 --task "which of these could touch an invariant?"
```

Good uses: bucketing a few hundred pytest failure lines by error class; pulling
`file:line` out of unstructured tracebacks; deciding which 3 of 200 log entries a
real model should read; first-pass grouping of eval outputs before you inspect
them.

## What it will not do, by construction

There is no `answer`, `write`, `fix`, or `decide` mode, and adding one would be
the wrong fix. Never route to a local model:

- anything that writes to the repo
- anything touching an invariant-critical path
- multi-step reasoning, algebra, or design judgment
- anything whose output would be consumed as truth rather than as a pointer
- ADRs, invariants, or governance text

## Exit codes — check them

| Code | Meaning |
| :-- | :-- |
| 0 | validated result on stdout |
| 2 | usage error (bad flags, empty or oversized input) |
| 3 | model reached, output failed validation — **including truncation** |
| 4 | ollama unreachable, timed out, or model not installed |

Exit 3 on truncation matters more than it looks: Ollama returns an **empty**
response body when a generation hits the length cap, which reads as a confident
empty answer. The tool treats that as failure. Never consume a non-zero result.

## Configuration

```bash
OLLAMA_OFFLOAD_MODEL=gemma4:e2b     # default; any installed model works
OLLAMA_HOST=http://127.0.0.1:11434  # default
```

Check availability with `ollama list`. If Ollama is not running, the tool exits
4 and you simply do the work yourself — it is an optimization, never a dependency.
