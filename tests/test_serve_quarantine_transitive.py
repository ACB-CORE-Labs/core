"""A-04 (transitive) — the serve process must not LOAD the wave/fibonacci substrate.

The existing `test_phase0_a04_serve_path_quarantines_wave_and_fibonacci` walks only
`chat/runtime.py`'s own AST import nodes, so it catches DIRECT imports only. The
stated invariant is process-level ("serve path stays quarantined"; modules labelled
"never serve"). This pin enforces the stated invariant: importing `chat.runtime` in
a clean interpreter must not pull any banned module into `sys.modules`.

RED until the `core/physics/__init__.py` barrel stops eagerly importing the
off-serving substrate (Finding #2, docs/research/adr-0241-0242-adversarial-and-fidelity-findings.md).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]

# Genuinely off-serving; must never load into the serve process.
_BANNED = (
    "core.physics.holographic_vault",
    "core.physics.fibonacci_search",
    "core.physics.fibonacci_word_schedule",
    "core.physics.atlas_packing",
    "core.physics.wave_seam",
    "core.physics.wave_energy_boundary",
    "core.physics.multi_scale_energy",
    "core.physics.sensorium_wave_feed",
    "core.physics.cognitive_lifecycle",  # ADR-0243 lifecycle — never serve
    "core.physics.biography_wiring",  # ADR-0243 §2.5 PASS→biography wiring — never serve
    # NOTE: core.physics.wave_manifold is intentionally excluded pending the
    # Joshua design ruling (goldtether delegates to it). Add it here if the
    # ruling is "quarantine wave_manifold for real".
)


def test_idle_tick_contemplation_import_does_not_load_offserving_substrate():
    """The stated invariant is PROCESS-level, and the serve process executes
    more than ``import chat.runtime``: the optional idle-tick frontier pass
    lazily runs ``from core.contemplation.runner import run_contemplation,
    write_contemplation_run`` inside the same always-on process that serves
    turns (chat/runtime.py idle_tick, ``contemplate_frontier_during_idle``;
    enabled by ``core/cli.py`` for the daemon).  That import edge must stay
    banned-module-clean too.

    Pre-ADR-0243-Lane-A this leaked ``core.physics.holographic_vault`` via the
    package ``__init__``'s eager ``wave_seam`` import; Lane A made the
    wave-seam re-exports lazy (PEP 562) and keeps the discovery-gate import
    (``core.physics.multi_scale_energy``) function-local.  The lazy re-export
    must still resolve when actually referenced (checked last, in the same
    probe, AFTER the leak assertion's snapshot).
    """
    probe = (
        "import importlib, sys, json;"
        "importlib.import_module('chat.runtime');"
        # Mirror of chat/runtime.py idle_tick's lazy import, verbatim edge.
        "from core.contemplation.runner import run_contemplation, write_contemplation_run;"
        f"banned={list(_BANNED)!r};"
        "leaked=sorted(m for m in sys.modules for b in banned if m==b or m.startswith(b+'.'));"
        # Lazy re-export still works off-serve (loads wave_seam on demand).
        "import core.contemplation as c;"
        "assert c.WaveModeHypothesis is not None;"
        "print(json.dumps(leaked))"
    )
    result = subprocess.run(
        [sys.executable, "-c", probe],
        cwd=str(_ROOT),
        capture_output=True,
        text=True,
        env={"PYTHONPATH": str(_ROOT), "PATH": ""},
    )
    assert result.returncode == 0, f"probe failed: {result.stderr[-2000:]}"
    leaked = result.stdout.strip().splitlines()[-1]
    import json as _json

    leaked_list = _json.loads(leaked)
    assert not leaked_list, (
        "serve-process idle_tick contemplation import loaded off-serving "
        f"modules (A-04 breach): {leaked_list}"
    )


def test_import_chat_runtime_does_not_load_offserving_substrate():
    probe = (
        "import importlib, sys, json;"
        "importlib.import_module('chat.runtime');"
        f"banned={list(_BANNED)!r};"
        "leaked=sorted(m for m in sys.modules for b in banned if m==b or m.startswith(b+'.'));"
        "print(json.dumps(leaked))"
    )
    result = subprocess.run(
        [sys.executable, "-c", probe],
        cwd=str(_ROOT),
        capture_output=True,
        text=True,
        env={"PYTHONPATH": str(_ROOT), "PATH": ""},
    )
    assert result.returncode == 0, f"probe failed: {result.stderr[-2000:]}"
    leaked = result.stdout.strip().splitlines()[-1]
    import json as _json

    leaked_list = _json.loads(leaked)
    assert not leaked_list, (
        "serve process transitively loaded off-serving modules "
        f"(A-04 breach via core/physics barrel): {leaked_list}"
    )
