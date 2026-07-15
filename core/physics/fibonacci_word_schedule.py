"""core.physics.fibonacci_word_schedule — ADR-0242 V4 (D5) observability choreography.

Fibonacci-word scheduler for telemetry / sealed-holdout sampling only.

Drive recurrence
----------------
    W_0 = B
    W_1 = A
    W_{n+1} = W_n W_{n-1}   (string concatenation)

where:
  * A — low-cost local measurement
  * B — high-cost cross-band check

Length formula
--------------
With the standard Fibonacci sequence F_0 = 0, F_1 = 1, F_2 = 1, F_3 = 2, …:

    |W_n| = F_{n+1}   for n >= 0
    (equivalently |W_0|=1, |W_1|=1, |W_2|=2, |W_3|=3, |W_4|=5, …)

Sovereignty (ADR-0242 absolute invariant)
----------------------------------------
This module is **outside the cognitive truth path**. It schedules
observability / telemetry actions only. It MUST NOT:

  * mutate vault standing or call VaultStore.store
  * mutate field state or authorize COHERENT promotion
  * dictate proposition truth, safety policy, or identity
  * be imported from the serve hot path (A-04 quarantine)

Pure and deterministic: no I/O, no randomness, no field/vault side effects.
"""

from __future__ import annotations

from enum import Enum
from typing import Iterator


class Action(str, Enum):
    """Observability action labels (telemetry only; not cognitive truth)."""

    A = "A"  # low-cost local measurement
    B = "B"  # high-cost cross-band check


def _require_nonneg_int(n: int, *, name: str = "n") -> int:
    if not isinstance(n, int) or isinstance(n, bool):
        raise TypeError(f"{name} must be an int, got {type(n).__name__}")
    if n < 0:
        raise ValueError(f"{name} must be non-negative, got {n}")
    return n


def fibonacci_word(n: int) -> str:
    """Return the Fibonacci word W_n as a string of 'A'/'B' characters.

    W_0 = \"B\", W_1 = \"A\", W_{k+1} = W_k + W_{k-1}.
    Length |W_n| = F_{n+1} with F_0=0, F_1=1.
    """
    n = _require_nonneg_int(n)
    if n == 0:
        return Action.B.value
    if n == 1:
        return Action.A.value
    # Iterative doubling: O(n) concatenations, O(F_{n+1}) total chars.
    prev = Action.B.value  # W_0
    curr = Action.A.value  # W_1
    for _ in range(2, n + 1):
        prev, curr = curr, curr + prev
    return curr


def schedule_actions(n: int) -> tuple[str, ...]:
    """Return the action sequence for W_n as an immutable tuple of \"A\"/\"B\".

    Same recurrence and length as :func:`fibonacci_word`; form convenient for
    iteration without splitting a string.
    """
    word = fibonacci_word(n)
    return tuple(word)


def iter_schedule_actions(n: int) -> Iterator[str]:
    """Iterate actions of W_n without building an intermediate tuple."""
    yield from fibonacci_word(n)


def word_length(n: int) -> int:
    """Return |W_n| = F_{n+1} (F_0=0, F_1=1) without building the word."""
    n = _require_nonneg_int(n)
    # F_{n+1}: a,b walk F_0=0, F_1=1 for (n+1) steps → a = F_{n+1}
    a, b = 0, 1
    for _ in range(n + 1):
        a, b = b, a + b
    return a


__all__ = [
    "Action",
    "fibonacci_word",
    "schedule_actions",
    "iter_schedule_actions",
    "word_length",
]
