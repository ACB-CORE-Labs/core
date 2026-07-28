"""PR-6 / G-9 — three AGENTS.md prohibitions, enforced by test rather than review.

G-9's charge: "law-enforced-by-review is weaker than law-enforced-by-test." Each
prohibition below is stated in AGENTS.md and, before this file, was guarded by
nothing that could fail — or by something far narrower than the law.

The verification pass that preceded this file (PR-6's stated method) found the
three in genuinely different states, and the difference is the finding:

**(a) Exact recall** — AGENTS.md §"Exact recall" bans cosine similarity, ANN,
HNSW and embedding ranking from runtime memory truth. The only import ban in the
repository covered **one file** (``core/physics/wave_manifold.py``, in
``test_third_door_cohesion.py``, itself in no curated suite). The actual recall
path, ``generate/realize/recall.py``, *documents* the prohibition in its module
docstring — "an exact, deterministic equality scan (no cosine / HNSW / ANN)" —
and nothing enforced it. A claim in a docstring is the exact failure class this
assessment exists to catch.

**(b) Governance bypass** — INV-07 pins that a D2–D4 frontend cannot *claim*
AUTO_ACCEPT_ELIGIBLE, which is governance working when called. Nothing pinned
that a serving path cannot skip governance altogether by simply not calling it.

**(c) Safety-pack non-swappability** — this one was already well pinned
(``tests/test_safety_pack.py``: unratified pack refused in production, missing
companion report refused, seal failure refused, path traversal rejected, missing
pack fails closed). Its gap was not coverage but *reach*: the file ran in no
curated suite, so a safety-critical fail-closed contract was verified only after
merge. Promoting it onto the gate is the fix; the assertion below guards that
placement rather than duplicating its content.

Every pin here was observed failing before it was allowed to pass.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]

# AGENTS.md §"Exact recall" — the named prohibitions, plus the libraries that
# are approximate-nearest-neighbour engines by construction. ``scipy.spatial``
# carries KDTree/cKDTree; ``sklearn`` carries every cosine ranker in common use.
_BANNED_LIBRARIES = frozenset(
    {"faiss", "hnswlib", "annoy", "nmslib", "pynndescent", "sklearn", "scann"}
)

# Subtrees where runtime recall truth is decided. A ban here is the law; a ban
# in one physics module was what existed before.
_RECALL_ROOTS = ("vault", "generate/realize", "generate/meaning_graph", "field", "recognition")


def _python_files(rel_root: str) -> list[Path]:
    root = _ROOT / rel_root
    if not root.exists():
        return []
    return sorted(p for p in root.rglob("*.py") if "__pycache__" not in p.parts)


def _imported_roots(tree: ast.AST) -> set[str]:
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    return roots


# ---------------------------------------------------------------------------
# (a) Exact recall — no approximate ranker anywhere truth is recalled
# ---------------------------------------------------------------------------


def test_recall_paths_import_no_approximate_neighbour_library() -> None:
    """AGENTS.md §Exact recall, enforced over the paths that actually recall."""
    offenders: list[str] = []
    for rel_root in _RECALL_ROOTS:
        for path in _python_files(rel_root):
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"))
            except SyntaxError:  # pragma: no cover - a parse failure is another test's problem
                continue
            banned = _imported_roots(tree) & _BANNED_LIBRARIES
            if banned:
                offenders.append(f"{path.relative_to(_ROOT)}: {sorted(banned)}")
    assert not offenders, (
        "approximate-nearest-neighbour libraries imported on a recall path — "
        "AGENTS.md §'Exact recall' requires exact CGA recall primitives only:\n  "
        + "\n  ".join(offenders)
    )


def test_recall_paths_define_no_cosine_similarity_ranker() -> None:
    """A hand-rolled cosine ranker evades an import ban; this catches it.

    Banning libraries only stops the convenient version. ``cosine_similarity``
    is ten lines of numpy, and writing it inline is the realistic way this
    prohibition gets violated by someone who means well.
    """
    pattern = re.compile(r"\bdef\s+\w*cosine\w*\s*\(", re.IGNORECASE)
    offenders: list[str] = []
    for rel_root in _RECALL_ROOTS:
        for path in _python_files(rel_root):
            text = path.read_text(encoding="utf-8")
            for match in pattern.finditer(text):
                line = text[: match.start()].count("\n") + 1
                offenders.append(f"{path.relative_to(_ROOT)}:{line}")
    assert not offenders, (
        "a cosine-similarity function is defined on a recall path; runtime "
        "recall must be exact (AGENTS.md §'Exact recall'):\n  " + "\n  ".join(offenders)
    )


def test_the_documented_exact_recall_claim_has_a_pin_behind_it() -> None:
    """``generate/realize/recall.py`` says it is exact — this is why that is true.

    The module docstring has claimed "no cosine / HNSW / ANN" since it was
    written. This asserts the claim is still made *and* that the file is inside
    the scanned roots above, so the sentence and the enforcement cannot drift
    apart: deleting the claim, or moving the file out from under the scan,
    fails here.
    """
    recall = _ROOT / "generate" / "realize" / "recall.py"
    assert recall.exists(), "the recall path moved; update _RECALL_ROOTS with it"
    text = recall.read_text(encoding="utf-8")
    assert "no cosine" in text.lower(), (
        "recall.py dropped its exactness claim — either it is no longer exact "
        "(a doctrine violation) or the record of why it matters was lost"
    )
    assert any(
        str(recall.relative_to(_ROOT)).startswith(root) for root in _RECALL_ROOTS
    ), "recall.py is not covered by the prohibition scan above"


# ---------------------------------------------------------------------------
# (b) Governance cannot be bypassed by not calling it
# ---------------------------------------------------------------------------


def _functions_containing(tree: ast.AST, predicate) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if any(predicate(sub) for sub in ast.walk(node)):
                names.add(node.name)
    return names


def _is_turn_verdicts_construction(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "TurnVerdicts"
    )


def _is_safety_check_call(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "check"
        and isinstance(node.func.value, ast.Attribute)
        and node.func.value.attr == "safety_check"
    )


def test_no_serving_path_builds_verdicts_without_running_the_safety_check() -> None:
    """The bypass pin G-9(b) asks for: governance is unskippable, not merely correct.

    INV-07 already proves governance *works when called*. This proves it cannot
    be routed around — a new serving path that assembles a ``TurnVerdicts``
    without invoking ``safety_check.check`` fails here, which is precisely how
    a bypass would be introduced (a third ``chat``-like entry point that forgot,
    not a malicious edit to the checker).
    """
    tree = ast.parse((_ROOT / "chat" / "runtime.py").read_text(encoding="utf-8"))
    builds_verdicts = _functions_containing(tree, _is_turn_verdicts_construction)
    runs_safety = _functions_containing(tree, _is_safety_check_call)

    assert builds_verdicts, "no TurnVerdicts construction found — pin needs updating"
    ungoverned = sorted(builds_verdicts - runs_safety)
    assert not ungoverned, (
        "these functions assemble a turn's verdicts without running the safety "
        f"check — governance is bypassable from them: {ungoverned}"
    )


def test_the_safety_check_is_invoked_against_the_loaded_pack() -> None:
    """Governance must consult the *runtime's* pack, not an ad-hoc one.

    A bypass does not have to skip the call; it can call the checker with a
    substituted pack. Every ``safety_check.check`` call site must pass
    ``self.safety_pack``.
    """
    text = (_ROOT / "chat" / "runtime.py").read_text(encoding="utf-8")
    tree = ast.parse(text)
    bad: list[str] = []
    for node in ast.walk(tree):
        if not _is_safety_check_call(node):
            continue
        passes_runtime_pack = any(
            isinstance(arg, ast.Attribute)
            and arg.attr == "safety_pack"
            and isinstance(arg.value, ast.Name)
            and arg.value.id == "self"
            for arg in node.args
        )
        if not passes_runtime_pack:
            bad.append(f"chat/runtime.py:{node.lineno}")
    assert not bad, (
        "safety_check.check called without the runtime's own loaded pack "
        f"(self.safety_pack): {bad}"
    )


# ---------------------------------------------------------------------------
# (c) Safety-pack non-swappability — already pinned; guard its reach
# ---------------------------------------------------------------------------


def _curated_suites() -> dict[str, tuple[str, ...]]:
    src = (_ROOT / "core" / "cli_test.py").read_text(encoding="utf-8")
    match = re.search(r"TEST_SUITES\s*(?::[^=]+)?=\s*\{", src)
    assert match is not None
    start = match.end() - 1
    depth = 0
    end = len(src)
    for i, ch in enumerate(src[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    return ast.literal_eval(src[start:end])


def test_safety_pack_contract_runs_on_the_pre_push_gate() -> None:
    """A fail-closed safety contract verified only after merge is half a contract.

    ``tests/test_safety_pack.py`` pins the substance — unratified pack refused
    in production, missing companion report refused, seal failure refused, path
    traversal rejected, missing pack fails closed. It ran in no curated suite,
    so none of that blocked a push. This keeps it on the gate.
    """
    suites = _curated_suites()
    assert "tests/test_safety_pack.py" in suites["smoke"], (
        "the safety-pack fail-closed contract must run on the pre-push gate"
    )


def test_the_runtime_default_safety_pack_is_the_ratified_one() -> None:
    """The runtime may not boot on a pack other than the ratified default."""
    from packs.safety.loader import DEFAULT_SAFETY_PACK

    text = (_ROOT / "chat" / "runtime.py").read_text(encoding="utf-8")
    assert "load_safety_pack()" in text, (
        "the runtime no longer loads the safety pack through the ratified loader"
    )
    assert DEFAULT_SAFETY_PACK == "core_safety_axes_v1", (
        "the ratified default safety pack changed; that is an ADR-level move, "
        "not a constant edit"
    )
