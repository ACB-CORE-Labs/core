"""ADR-0244 §2.10 — the Fibonacci-word scheduler actually reduces phase-locking.

The existing `test_adr_0242_fibonacci_word.py` pins the *structure* (recurrence,
length, sovereignty). This audit pins the *load-bearing spec claim*: §2.10 says
the schedule is chosen "to reduce harmonic phase-locking with external batching /
eval fixtures / compiler cadences." That property is not free — it comes from the
Fibonacci word being a Sturmian sequence with golden-ratio letter density and no
short-scale clustering. If a future refactor swapped the recurrence for something
periodic, structure tests might still pass while the anti-phase-locking guarantee
silently died; these tests fail first.
"""

from __future__ import annotations

import pytest

from core.physics.fibonacci_word_schedule import fibonacci_word, word_length

_PHI = (1.0 + 5.0**0.5) / 2.0


def _fib(k: int) -> int:
    a, b = 0, 1
    for _ in range(k):
        a, b = b, a + b
    return a


@pytest.mark.parametrize("n", range(2, 16))
def test_letter_density_is_the_golden_ratio(n: int):
    # count(A) = F_n, count(B) = F_{n-1}; A/B → φ. A maximally-irrational duty
    # cycle is what avoids resonance with any periodic external cadence.
    w = fibonacci_word(n)
    assert w.count("A") == _fib(n)
    assert w.count("B") == _fib(n - 1)
    assert len(w) == word_length(n)


def test_ratio_converges_to_phi():
    w = fibonacci_word(15)
    assert abs(w.count("A") / w.count("B") - _PHI) < 1e-4


@pytest.mark.parametrize("n", range(2, 18))
def test_no_harmonic_clustering(n: int):
    # The high-cost B check never bunches (no "BB"); low-cost A runs are bounded
    # at 2 (no "AAA"). Both are classic Fibonacci-word properties and are exactly
    # what "reduce harmonic phase-locking" means operationally: neither action
    # forms a locally periodic burst.
    w = fibonacci_word(n)
    assert "BB" not in w
    assert "AAA" not in w


def test_word_is_aperiodic():
    # A long Fibonacci word has no period p ≤ |W|/2 — it is genuinely
    # quasi-periodic, not a disguised periodic schedule.
    w = fibonacci_word(16)
    length = len(w)
    for p in range(1, length // 2 + 1):
        assert not all(w[i] == w[i + p] for i in range(length - p)), f"period {p}"
