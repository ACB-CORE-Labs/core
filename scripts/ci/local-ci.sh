#!/bin/sh
# CORE local-first CI runner.
#
# AGENTS.md: "The real CI is local-first. Run validation in the worktree...
# Do not treat remote Actions / Docker job containers as the merge gate."
# This script is that runner — one entry point for the gate tiers, usable on
# any host, with an honest statement of which interpreter produced the result.
#
#   sh scripts/ci/local-ci.sh              # gate tier (what pre-push runs)
#   sh scripts/ci/local-ci.sh --tier smoke
#   sh scripts/ci/local-ci.sh --tier full  # the whole tests/ tree, parallel
#   sh scripts/ci/local-ci.sh --list
#
# WHY THIS EXISTS
# ---------------
# `pyproject.toml` pins `requires-python == "3.12.13"` — an EXACT patch
# version. On a host that does not have precisely 3.12.13, `uv sync --locked`
# fails outright and every gate becomes unrunnable. For a project whose merge
# bar IS the local run, an unrunnable local gate is the failure mode that
# matters most: it is how `tests/test_lane_sha_verifier.py` sat red on clean
# main from the deduction-serve arc until 2026-07-25 with nobody noticing.
#
# THE INTERPRETER CONTRACT (the part to read before trusting a green run)
# ----------------------------------------------------------------------
# The pinned interpreter is CANONICAL. A run on any other interpreter is
# NON-CANONICAL and this script says so, loudly, on every such run.
#
# Fallback is opt-in, never automatic — the same discipline as
# `core.ratified_ledger`'s `missing_ok`: a degraded mode is legitimate, and a
# degraded mode that reports itself as the real thing is not. Default is
# fail-closed with instructions.
#
#   --allow-interpreter-fallback   run on any 3.12.x, stamped NON-CANONICAL
#
# Measured note, so the flag is not cargo-culted: on 2026-07-25 the full
# committed-SHA / trace_hash / content_sha256 / lane-SHA pin set (119 tests)
# was run on 3.12.11 and 118 passed — the single failure was a stale lane
# roster that fails on 3.12.13 too. That is evidence the exact pin is not
# load-bearing for bit-exactness, NOT a ruling that it should be relaxed.
# Relaxing it is a reproducibility decision and belongs to a human.

set -eu

repo_root="$(git rev-parse --show-toplevel)"
cd "${repo_root}"

TIER="gate"
ALLOW_FALLBACK=0
PYTEST_EXTRA=""

usage() {
    cat <<'EOF'
usage: local-ci.sh [--tier TIER] [--allow-interpreter-fallback] [--list] [-- ARGS]

tiers:
  smoke   smoke suite only                     (~1 min)  = CI smoke.yml parity
  gate    smoke + warmed_session + deductive + teaching  (~9 min) = the pre-push gate
  full    the entire tests/ tree, parallel     (~10 min) = the merge bar

options:
  --allow-interpreter-fallback  permit a non-pinned 3.12.x; marks run NON-CANONICAL
  --list                        print the tier definitions and exit
  --                            pass remaining args through to pytest
EOF
}

while [ $# -gt 0 ]; do
    case "$1" in
        --tier) TIER="$2"; shift 2 ;;
        --tier=*) TIER="${1#*=}"; shift ;;
        --allow-interpreter-fallback) ALLOW_FALLBACK=1; shift ;;
        --list) usage; exit 0 ;;
        -h|--help) usage; exit 0 ;;
        --) shift; PYTEST_EXTRA="$*"; break ;;
        *) echo "[local-ci] unknown argument: $1" >&2; usage >&2; exit 2 ;;
    esac
done

case "${TIER}" in
    smoke|gate|full) ;;
    *) echo "[local-ci] unknown tier: ${TIER} (smoke|gate|full)" >&2; exit 2 ;;
esac

# --- interpreter resolution ------------------------------------------------

pinned="$(cat .python-version 2>/dev/null || echo '')"
[ -n "${pinned}" ] || pinned="3.12.13"
canonical=0
RUNNER=""

if command -v uv >/dev/null 2>&1 && uv python find "${pinned}" >/dev/null 2>&1; then
    canonical=1
    RUNNER="uv run --"
    echo "[local-ci] interpreter: ${pinned} (CANONICAL — matches the repo pin)"
else
    if [ "${ALLOW_FALLBACK}" -eq 0 ]; then
        cat >&2 <<EOF
[local-ci] BLOCKED: the pinned interpreter (${pinned}) is not available here.

  \`pyproject.toml\` pins requires-python == "${pinned}", so \`uv sync --locked\`
  cannot resolve and the canonical gate cannot run on this host.

  Either provision it:      uv python install ${pinned}
  or run degraded, knowingly:
                            sh scripts/ci/local-ci.sh --tier ${TIER} \\
                                --allow-interpreter-fallback

  A degraded run is legitimate. A degraded run reported as canonical is not,
  which is why this is opt-in rather than automatic.
EOF
        exit 3
    fi
    fallback=""
    for cand in python3.12 python3; do
        if command -v "${cand}" >/dev/null 2>&1 && \
           "${cand}" -c 'import sys; sys.exit(0 if sys.version_info[:2]==(3,12) else 1)' 2>/dev/null; then
            fallback="${cand}"; break
        fi
    done
    if [ -z "${fallback}" ]; then
        echo "[local-ci] BLOCKED: no 3.12.x interpreter found at all." >&2
        exit 3
    fi
    actual="$(${fallback} -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')"
    RUNNER="${fallback} -m"
    cat >&2 <<EOF

  ############################################################
  #  NON-CANONICAL RUN                                       #
  #  interpreter ${actual} != pinned ${pinned}
  #  Results are indicative, NOT merge evidence.             #
  #  Re-run on ${pinned} before merging.
  ############################################################

EOF
fi

# Two invocation shapes, one interface. Suite membership is NEVER restated
# here — it is read from ``core/cli_test.py::TEST_SUITES`` through the CLI, so
# this runner cannot drift from the pre-push gate the way smoke.yml drifted
# from it.
if [ "${canonical}" -eq 1 ]; then
    suite() { uv run core test --suite "$1" -q; }
    pytest_() { uv run python -m pytest "$@"; }
else
    suite() { ${RUNNER} core.cli test --suite "$1" -q; }
    pytest_() { ${RUNNER} pytest "$@"; }
fi

step() {
    label="$1"; shift
    echo "[local-ci] ${label} ..."
    if ! "$@"; then
        echo "[local-ci] FAILED: ${label}" >&2
        exit 1
    fi
}

# --- gates -----------------------------------------------------------------

start="$(date +%s)"

case "${TIER}" in
    smoke)
        step "smoke suite" suite smoke
        ;;
    gate)
        echo "[local-ci] tier=gate — same four steps as scripts/hooks/pre-push"
        step "(1/4) smoke suite" suite smoke
        step "(2/4) warmed_session lane" pytest_ tests/test_warmed_session_lane.py -q --no-header
        step "(3/4) deductive suite" suite deductive
        step "(4/4) teaching suite" suite teaching
        ;;
    full)
        jobs="$(nproc 2>/dev/null || echo 4)"
        step "full tests/ tree (-n ${jobs})" \
            pytest_ tests/ -q --no-header -p no:cacheprovider -n "${jobs}" --dist loadfile
        ;;
esac

elapsed=$(( $(date +%s) - start ))
if [ "${canonical}" -eq 1 ]; then
    echo "[local-ci] PASSED tier=${TIER} in ${elapsed}s — CANONICAL (${pinned})."
else
    echo "[local-ci] PASSED tier=${TIER} in ${elapsed}s — NON-CANONICAL; not merge evidence." >&2
fi
