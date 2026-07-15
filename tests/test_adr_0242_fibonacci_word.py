"""ADR-0242 V4 (D5) — Fibonacci-word observability scheduler.

Telemetry-only; dual-run deterministic; cannot mutate cognitive truth.
"""

from __future__ import annotations

import pytest

from core.physics.fibonacci_word_schedule import (
    Action,
    fibonacci_word,
    iter_schedule_actions,
    schedule_actions,
    word_length,
)


# Expected words from Drive: W0=B, W1=A, W_{n+1}=W_n W_{n-1}
_EXPECTED = {
    0: "B",
    1: "A",
    2: "AB",
    3: "ABA",
    4: "ABAAB",
    5: "ABAABABA",
    6: "ABAABABAABAAB",
}


def test_w0_is_b():
    assert fibonacci_word(0) == "B"
    assert schedule_actions(0) == ("B",)


def test_w1_is_a():
    assert fibonacci_word(1) == "A"
    assert schedule_actions(1) == ("A",)


@pytest.mark.parametrize("n,expected", sorted(_EXPECTED.items()))
def test_fibonacci_word_table(n: int, expected: str):
    assert fibonacci_word(n) == expected


@pytest.mark.parametrize("n,expected", sorted(_EXPECTED.items()))
def test_schedule_actions_matches_word(n: int, expected: str):
    actions = schedule_actions(n)
    assert actions == tuple(expected)
    assert all(a in (Action.A.value, Action.B.value) for a in actions)


def test_w2_ab_w3_aba_w4_abaab():
    assert fibonacci_word(2) == "AB"
    assert fibonacci_word(3) == "ABA"
    assert fibonacci_word(4) == "ABAAB"


def test_recurrence_w_n_concat():
    """W_{n+1} == W_n + W_{n-1} for several n."""
    for n in range(1, 10):
        assert fibonacci_word(n + 1) == fibonacci_word(n) + fibonacci_word(n - 1)


def test_length_equals_fib_n_plus_1():
    """|W_n| = F_{n+1} with F_0=0, F_1=1, F_2=1, F_3=2, F_4=3, F_5=5, …"""
    # F_{n+1} table for n=0..8 → 1,1,2,3,5,8,13,21,34
    fib_np1 = [1, 1, 2, 3, 5, 8, 13, 21, 34]
    for n, expected_len in enumerate(fib_np1):
        word = fibonacci_word(n)
        assert len(word) == expected_len
        assert word_length(n) == expected_len
        assert len(schedule_actions(n)) == expected_len


def test_dual_run_identical():
    """Deterministic: two independent evaluations produce byte-identical results."""
    for n in range(0, 12):
        a = fibonacci_word(n)
        b = fibonacci_word(n)
        assert a == b
        assert schedule_actions(n) == schedule_actions(n)
        assert tuple(iter_schedule_actions(n)) == schedule_actions(n)


def test_action_enum_values():
    assert Action.A.value == "A"
    assert Action.B.value == "B"
    assert Action.A == "A"
    assert Action.B == "B"


def test_rejects_negative_n():
    with pytest.raises(ValueError, match="non-negative"):
        fibonacci_word(-1)
    with pytest.raises(ValueError, match="non-negative"):
        schedule_actions(-1)
    with pytest.raises(ValueError, match="non-negative"):
        word_length(-1)


def test_rejects_non_int_n():
    with pytest.raises(TypeError):
        fibonacci_word(1.5)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        fibonacci_word(True)  # type: ignore[arg-type]


def test_only_ab_alphabet():
    for n in range(0, 14):
        word = fibonacci_word(n)
        assert set(word) <= {"A", "B"}
        if n == 0:
            assert set(word) == {"B"}
        elif n == 1:
            assert set(word) == {"A"}
        else:
            assert set(word) == {"A", "B"}


def test_module_is_pure_no_side_effect_imports():
    """Sovereignty pin: module must not pull vault/field mutation surfaces."""
    import ast
    from pathlib import Path

    src = Path("core/physics/fibonacci_word_schedule.py").read_text()
    tree = ast.parse(src)
    forbidden = {"vault", "field", "store", "VaultStore", "generate", "chat"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                assert root not in forbidden, alias.name
        if isinstance(node, ast.ImportFrom) and node.module:
            root = node.module.split(".")[0]
            assert root not in forbidden, node.module
