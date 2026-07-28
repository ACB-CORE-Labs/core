"""FA-1 — the semantic ground's discrimination, pinned as an instrument (G-25, L2).

Measured 2026-07-28 at `472fc0a8`: mounting the depth packs onto English — the
operation ADR-0005/0015 designs to *add* depth — **removes 37 distinct coordinates
from the manifold**, collapsing 48 surfaces into 11 shared points. English alone
is collision-free (220/220); Greek alone is collision-free (11/11). The damage is
created by the mount, and it is not confined to the depth languages: nine English
surfaces — `ask, question, what, who, where, how, why, when, which` — land on one
coordinate because a single Greek verb shares their primary semantic domain.

ADR-0015 requires resonance *"without flattening their distinctions"* and states
that cross-language alignment is *"a weighted graph, **not** a translation table"*.
Both are violated, exactly and bit-identically. Root cause and the four decoration
proofs it silently green-lit: `docs/analysis/logos-substrate-collapse-2026-07-28.md`.

This pin does the same job the read-rate floor does for perception — it turns a
finding into an instrument, in both directions:

  * the collapse may not silently **widen** — a compiler change that flattens more
    of the ground fails the gate;
  * the recorded numbers may not silently **shrink** either. Repair is the goal, and
    repair is a reviewed decision with a diff: when the ground stops collapsing,
    these constants move in the same commit that fixed it.

The English control is the load-bearing half. It is what makes this a *diagnosis*
(mounting causes the loss) rather than an observation (the ground has collisions),
and it is the reason the numbers above can be attributed to one site.
"""

from __future__ import annotations

from evals.logos.manifold_collapse import TRILINGUAL, measure_all

#: Trilingual mount, measured 2026-07-28 at `472fc0a8`.
RECORDED_SURFACES = 239
RECORDED_DISTINCT = 202
RECORDED_LOST = 37
RECORDED_GROUPS = 11
RECORDED_IN_COLLISION = 48

#: The single most damaging group: the entire WH-word set, one coordinate.
#: Pinned verbatim because the *shape* of the loss is the finding — a reader over
#: this ground cannot geometrically distinguish "who" from "why" from "when".
WH_COLLAPSE = ("ask", "how", "question", "what", "when", "where", "which", "who", "why", "ἐρωτάω")


def test_english_alone_is_collision_free() -> None:
    """The control. If this fails, the diagnosis below is misattributed."""
    reports = measure_all()
    english = reports["en_minimal_v1"]
    assert english.surfaces == english.distinct_coordinates, (
        f"en_minimal_v1 compiled ALONE now has {english.coordinates_lost} lost coordinates "
        f"({english.groups}) — the collapse is no longer created purely by the mount, so "
        "the attribution in docs/analysis/logos-substrate-collapse-2026-07-28.md must be redone"
    )
    greek = reports["grc_logos_micro_v1"]
    assert greek.surfaces == greek.distinct_coordinates, (
        "grc_logos_micro_v1 compiled alone now collides — re-attribute before trusting the mount numbers"
    )


def test_the_mount_destroys_distinctions_it_was_designed_to_add() -> None:
    """The finding, pinned in both directions. Good news still needs a diff."""
    mounted = measure_all()["mounted"]
    assert mounted.config == TRILINGUAL
    assert mounted.surfaces == RECORDED_SURFACES, (
        f"mounted surface count moved: {mounted.surfaces} vs {RECORDED_SURFACES} — the packs "
        "changed shape; this pin measures the compiler, not the corpus. Re-baseline deliberately."
    )
    assert mounted.coordinates_lost == RECORDED_LOST, (
        f"MANIFOLD COLLAPSE MOVED: {mounted.coordinates_lost} coordinates lost vs "
        f"{RECORDED_LOST} recorded. If it grew, a compiler change flattened more of the "
        "semantic ground. If it shrank, the repair landed — update these constants in the "
        "same commit as the fix, and record the new numbers in the analysis doc."
    )
    assert mounted.distinct_coordinates == RECORDED_DISTINCT
    assert len(mounted.groups) == RECORDED_GROUPS
    assert mounted.surfaces_in_collision == RECORDED_IN_COLLISION


def test_the_wh_words_share_one_coordinate() -> None:
    """The damage is not confined to the depth languages — English loses too.

    Nine English question words occupy one point because `ἐρωτάω` shares their
    primary semantic domain and the mount-time nudge overwrites every member of a
    multi-language domain group with the English prototype. This is the concrete
    reason a reader over this ground cannot tell a *who* question from a *why* one.
    """
    mounted = measure_all()["mounted"]
    assert WH_COLLAPSE in mounted.groups, (
        "the WH-word collapse changed shape. If it is gone, the ground gained back the "
        "single most load-bearing distinction it had lost — say so in the analysis doc and "
        f"update this pin. Current groups: {mounted.groups}"
    )


def test_the_instrument_can_report_absence() -> None:
    """A collision detector that cannot report zero would make every number above meaningless."""
    reports = measure_all()
    assert reports["en_minimal_v1"].groups == (), "the control must be able to come back empty"
    assert reports["mounted"].groups, "…and the instrument must still be able to come back non-empty"
    mounted = reports["mounted"]
    assert all(len(group) > 1 for group in mounted.groups), "a 'collision' of one is a counting bug"
    assert mounted.coordinates_lost == sum(len(group) - 1 for group in mounted.groups), (
        "lost coordinates must equal the sum of (group size − 1) — otherwise the census "
        "is double-counting or dropping surfaces"
    )
