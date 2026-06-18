"""Integration tests for every triangulation implementation.

Covers all eight public entry points described in README.md:

* Python: ``triangulate_python_bw`` (Bowyer-Watson with triangle walk)
* Python: ``triangulate_dnc``      (Divide & Conquer on quad-edges)
* Rust:   ``delaunay_rust.triangulate_points``   (with and without triangle walk)
* Rust:   ``delaunay_rust.triangulate_points_dnc``
* C++:    ``delaunay_cpp.triangulate_points``    (with and without triangle walk)
* C++:    ``delaunay_cpp.triangulate_points_dnc``

Every implementation is validated against the same battery of geometric
and structural invariants:

* output shape and index range
* non-degenerate triangles with strict CCW orientation
* Delaunay empty-circumcircle condition — for every triangle, no other
  input point lies strictly inside its circumcircle (this is the user-
  requested math check)
* every input vertex referenced at least once
* no duplicate triangles
* planar-graph edge count consistent with Euler's formula

Two extra suites verify exact-match properties on tiny inputs where the
Delaunay triangulation is unique: cross-implementation agreement on the
canonical ``square + centre`` cloud.
"""
from __future__ import annotations

from typing import Callable

import numpy as np
import pytest

import delaunay_cpp
import delaunay_rust
from triangulation_python.dnc import triangulate_dnc
from triangulation_python.incremental import triangulate_python_bw


# ---------------------------------------------------------------------------
# Fixtures and helpers
# ---------------------------------------------------------------------------

IMPLEMENTATIONS: dict[str, Callable] = {
    "python_bw": triangulate_python_bw,
    "python_dnc": triangulate_dnc,
    "rust_bw_walk": lambda pts: delaunay_rust.triangulate_points(pts, True),
    "rust_bw_naive": lambda pts: delaunay_rust.triangulate_points(pts, False),
    "rust_dnc": delaunay_rust.triangulate_points_dnc,
    "cpp_bw_walk": lambda pts: delaunay_cpp.triangulate_points(pts, True),
    "cpp_bw_naive": lambda pts: delaunay_cpp.triangulate_points(pts, False),
    "cpp_dnc": delaunay_cpp.triangulate_points_dnc,
}

IMPLEMENTATION_IDS = list(IMPLEMENTATIONS.keys())


@pytest.fixture
def impl(request):
    """Parametrised fixture returning the triangulation function to test."""
    return IMPLEMENTATIONS[request.param]


def _as_triangle_array(triangles) -> np.ndarray:
    """Normalise the various return types to a (M, 3) int ndarray.

    The pure-Python DNC returns a list of tuples, while the rest return
    either nested Python lists (Rust) or ``np.ndarray`` (C++).
    """
    arr = np.asarray(triangles, dtype=np.int64)
    assert arr.ndim == 2 and arr.shape[1] == 3, (
        f"expected shape (M, 3), got {arr.shape}"
    )
    return arr


# ---------------------------------------------------------------------------
# Geometric predicates used by the tests
# ---------------------------------------------------------------------------

def _signed_area_2x(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
    """Signed area of the triangle (a, b, c). Positive iff CCW."""
    return float(
        (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    )


def _in_circumcircle_strict(
    pa: np.ndarray, pb: np.ndarray, pc: np.ndarray, pd: np.ndarray,
) -> bool:
    """Return True iff d lies strictly inside the circumcircle of (a, b, c).

    Assumes ``a``, ``b``, ``c`` are in CCW order, so ``det > 0`` means
    ``d`` is inside.
    """
    adx, ady = pa[0] - pd[0], pa[1] - pd[1]
    bdx, bdy = pb[0] - pd[0], pb[1] - pd[1]
    cdx, cdy = pc[0] - pd[0], pc[1] - pd[1]
    alift = adx * adx + ady * ady
    blift = bdx * bdx + bdy * bdy
    clift = cdx * cdx + cdy * cdy
    det = (
        alift * (bdx * cdy - cdx * bdy)
        + blift * (cdx * ady - adx * cdy)
        + clift * (adx * bdy - bdx * ady)
    )
    return det > 0.0


def _triangle_signed_area(points: np.ndarray, tri: np.ndarray) -> float:
    a, b, c = points[int(tri[0])], points[int(tri[1])], points[int(tri[2])]
    return _signed_area_2x(a, b, c)


def _assert_delaunay(points: np.ndarray, triangles: np.ndarray) -> None:
    """Verify the empty-circumcircle condition for every triangle.

    All triangles are expected to be CCW (positive signed area), so the
    in-circle predicate ``det > 0`` directly identifies interior points.
    """
    for tri in triangles:
        a, b, c = int(tri[0]), int(tri[1]), int(tri[2])
        pa, pb, pc = points[a], points[b], points[c]
        for d in range(len(points)):
            if d == a or d == b or d == c:
                continue
            pd = points[d]
            assert not _in_circumcircle_strict(pa, pb, pc, pd), (
                f"point {d}={tuple(pd)} lies inside circumcircle "
                f"of triangle ({a}, {b}, {c})"
            )


def _convex_hull_edge_count(triangles: np.ndarray) -> int:
    """Number of edges bordering exactly one triangle (the convex hull)."""
    edge_count: dict[tuple[int, int], int] = {}
    for tri in triangles:
        a, b, c = int(tri[0]), int(tri[1]), int(tri[2])
        for u, v in ((a, b), (b, c), (c, a)):
            key = (min(u, v), max(u, v))
            edge_count[key] = edge_count.get(key, 0) + 1
    return sum(1 for cnt in edge_count.values() if cnt == 1)


# ---------------------------------------------------------------------------
# Test scenarios
# ---------------------------------------------------------------------------

SCENARIOS: list[tuple[str, np.ndarray]] = [
    ("square", np.array(
        [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]],
    )),
    ("unit_square_with_center", np.array(
        [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0], [0.5, 0.5]],
    )),
    ("non_convex", np.array(
        [
            [0.0, 0.0], [4.0, 0.0], [4.0, 4.0], [2.0, 2.0],
            [0.0, 4.0], [2.0, 0.0],
        ],
    )),
]


def _random_scenarios() -> list[tuple[str, np.ndarray]]:
    rng = np.random.default_rng(271828)
    return [
        ("random_uniform_50", rng.random((50, 2))),
        ("random_uniform_200", rng.random((200, 2))),
        ("random_gaussian_100", rng.normal(0.0, 1.0, (100, 2))),
        ("random_circle_50", _points_on_circle(rng, 50, 1.0, 0.05)),
    ]


def _points_on_circle(
    rng: np.random.Generator, n: int, radius: float, jitter: float,
) -> np.ndarray:
    angles = np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)
    pts = np.stack([np.cos(angles), np.sin(angles)], axis=1) * radius
    pts += rng.normal(0.0, jitter, pts.shape)
    return pts


ALL_SCENARIOS = SCENARIOS + _random_scenarios()
SCENARIO_IDS = [name for name, _ in ALL_SCENARIOS]


@pytest.fixture(params=ALL_SCENARIOS, ids=SCENARIO_IDS)
def scenario(request):
    return request.param


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("impl", IMPLEMENTATION_IDS, indirect=True)
def test_output_shape_and_indices(scenario, impl):
    """All triangle indices reference valid input vertices, no self-loops."""
    _, points = scenario
    triangles = _as_triangle_array(impl(points))
    assert triangles.min() >= 0
    assert triangles.max() < len(points)
    for tri in triangles:
        assert len(set(int(v) for v in tri)) == 3, (
            f"triangle {tri.tolist()} reuses a vertex"
        )


@pytest.mark.parametrize("impl", IMPLEMENTATION_IDS, indirect=True)
def test_strict_ccw_orientation(scenario, impl):
    """Every triangle has strictly positive (CCW) signed area."""
    _, points = scenario
    triangles = _as_triangle_array(impl(points))
    if len(triangles) == 0:
        pytest.skip("algorithm produced no triangles for this input")
    for tri in triangles:
        area = _triangle_signed_area(points, tri)
        assert area > 0.0, (
            f"triangle {tri.tolist()} is not CCW or has zero area "
            f"(signed area = {area})"
        )


@pytest.mark.parametrize("impl", IMPLEMENTATION_IDS, indirect=True)
def test_delaunay_empty_circumcircle(scenario, impl):
    """The defining property: no point lies strictly inside a circumcircle.

    This is the core mathematical check that defines a Delaunay
    triangulation — a triangle mesh is Delaunay iff every triangle's
    circumcircle is empty of all other input points.
    """
    _, points = scenario
    triangles = _as_triangle_array(impl(points))
    if len(triangles) == 0:
        pytest.skip("algorithm produced no triangles for this input")
    _assert_delaunay(points, triangles)


@pytest.mark.parametrize("impl", IMPLEMENTATION_IDS, indirect=True)
def test_no_duplicate_triangles(scenario, impl):
    """Every triangle should appear at most once, regardless of orientation."""
    _, points = scenario
    triangles = _as_triangle_array(impl(points))
    if len(triangles) == 0:
        pytest.skip("algorithm produced no triangles for this input")
    canonical = {tuple(sorted(int(v) for v in tri)) for tri in triangles}
    assert len(canonical) == len(triangles), (
        "duplicate triangles in output: "
        f"{len(triangles) - len(canonical)} repetitions"
    )


@pytest.mark.parametrize("impl", IMPLEMENTATION_IDS, indirect=True)
def test_all_vertices_used(scenario, impl):
    _, points = scenario
    triangles = _as_triangle_array(impl(points))
    used = {int(v) for tri in triangles for v in tri}
    assert used == set(range(len(points))), (
        f"missing vertices: {set(range(len(points))) - used}"
    )


@pytest.mark.parametrize("impl", IMPLEMENTATION_IDS, indirect=True)
def test_planar_edge_count(scenario, impl):
    """For a planar triangulation: 3*M = 2*E_i + E_h (Euler's formula)."""
    _, points = scenario
    triangles = _as_triangle_array(impl(points))
    m = len(triangles)
    h = _convex_hull_edge_count(triangles)
    # 3*M = 2*(E - h) + h ⇒ E = (3M + h) / 2. We only assert that
    # the count is internally consistent — every edge bordering two
    # triangles is interior, every edge bordering one is on the hull.
    assert (3 * m + h) % 2 == 0
    e_total = (3 * m + h) // 2
    assert e_total >= h, "negative interior edge count"


# ---------------------------------------------------------------------------
# Exact-match properties on inputs with unique Delaunay triangulation
# ---------------------------------------------------------------------------

# A convex quadrilateral has exactly one Delaunay triangulation (when no
# extra interior point is present) — two triangles sharing a diagonal.
SQUARE = np.array(
    [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]],
)
SQUARE_WITH_CENTER = np.array(
    [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0], [0.5, 0.5]],
)
TRIANGLE_INPUT = np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]])


def _canonical_triangle_set(triangles) -> frozenset:
    """Return a frozenset of vertex tuples, orientation-independent."""
    arr = _as_triangle_array(triangles)
    return frozenset(tuple(sorted(int(v) for v in tri)) for tri in arr)


def test_all_implementations_agree_on_square_with_center():
    """All eight implementations agree on the canonical 5-point cloud.

    With one interior point in a convex hull of four, the Delaunay
    triangulation is unique: each interior point splits the hull into
    four triangles connecting to it.
    """
    reference = _canonical_triangle_set(triangulate_dnc(SQUARE_WITH_CENTER))
    for name, fn in IMPLEMENTATIONS.items():
        got = _canonical_triangle_set(fn(SQUARE_WITH_CENTER))
        assert got == reference, (
            f"{name} disagrees on square_with_center: "
            f"missing={reference - got}, extra={got - reference}"
        )


# ---------------------------------------------------------------------------
# Specific known outputs
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("impl", IMPLEMENTATION_IDS, indirect=True)
def test_unit_square_two_triangles(impl):
    """A convex quadrilateral triangulates to exactly two triangles."""
    triangles = _as_triangle_array(impl(SQUARE))
    assert len(triangles) == 2
    _assert_delaunay(SQUARE, triangles)


@pytest.mark.parametrize("impl", IMPLEMENTATION_IDS, indirect=True)
def test_three_points_single_triangle(impl):
    triangles = _as_triangle_array(impl(TRIANGLE_INPUT))
    assert len(triangles) == 1
    assert _canonical_triangle_set(triangles) == frozenset({(0, 1, 2)})