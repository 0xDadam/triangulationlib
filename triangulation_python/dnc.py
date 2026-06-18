import numpy as np
from typing import List, Tuple
from triangulation_python.quad_edge import Edge, make_edge, connect, splice, delete_edge
from triangulation_python.geometry import ccw_index, right_of, left_of, in_circle

def is_valid_candidate(edge: Edge, base_lre: Edge, points: np.ndarray) -> bool:
    """Sprawdza, czy potencjalny punkt kandydujący jest powyżej base_lre (z prawej strony wektora R->L)."""
    return right_of(edge.dest, base_lre, points)

def merge_triangulations(ldo_left: Edge, rdo_left: Edge, ldo_right: Edge, rdo_right: Edge, points: np.ndarray) -> Tuple[Edge, Edge]:
    """Faza 'Merge' złączająca dwie niezalezne triangulacje napinając zamek LR z dołu do góry."""
    
    # 1. ZNALEZIENIE DOLNEJ STYCZNEJ (LOWER TANGENT)
    ldo_inner = rdo_left
    rdo_inner = ldo_right
    
    while True:
        if left_of(rdo_inner.origin, ldo_inner, points):
            ldo_inner = ldo_inner.lnext
        elif right_of(ldo_inner.origin, rdo_inner, points):
            rdo_inner = rdo_inner.rprev
        else:
            break

    base_lre = connect(rdo_inner.sym, ldo_inner)
    
    if ldo_left.origin == ldo_inner.origin:
        ldo_left = base_lre.sym
    if rdo_right.origin == rdo_inner.origin:
        rdo_right = base_lre
        
    # 2. ZAMEK BŁYSKAWICZNY W GÓRĘ (THE ZIPPER)
    while True:
        lcand = base_lre.sym.onext
        if is_valid_candidate(lcand, base_lre, points):
            while in_circle(base_lre.dest, base_lre.origin, lcand.dest, lcand.onext.dest, points):
                t = lcand.onext
                delete_edge(lcand)
                lcand = t

        rcand = base_lre.oprev
        if is_valid_candidate(rcand, base_lre, points):
            while in_circle(base_lre.dest, base_lre.origin, rcand.dest, rcand.oprev.dest, points):
                t = rcand.oprev
                delete_edge(rcand)
                rcand = t

        l_valid = is_valid_candidate(lcand, base_lre, points)
        r_valid = is_valid_candidate(rcand, base_lre, points)
        
        if not l_valid and not r_valid:
            break
            
        if not l_valid or (r_valid and in_circle(lcand.dest, lcand.origin, rcand.origin, rcand.dest, points)):
            base_lre = connect(rcand, base_lre.sym)
        else:
            base_lre = connect(base_lre.sym, lcand.sym)

    return ldo_left, rdo_right

def build_delaunay_triangulation(points: np.ndarray, start: int, end: int) -> Tuple[Edge, Edge]:
    """
    Dziel i zwyciężaj dla triangulacji Delaunay'a (algorytm Guibasa-Stolfiego).
    Zwraca krotkę (ldo, rdo) - lewą i prawą skrajną krawędź otoczki wypukłej.
    """
    n = end - start
    
    # --- PRZYPADEK BAZOWY: 2 PUNKTY ---
    if n == 2:
        a = make_edge(start, start + 1)
        return a, a.sym
        
    # --- PRZYPADEK BAZOWY: 3 PUNKTY ---
    elif n == 3:
        a = make_edge(start, start + 1)
        b = make_edge(start + 1, start + 2)
        splice(a.sym, b)
        
        c_val = ccw_index(start, start + 1, start + 2, points)
        if c_val > 0:
            connect(b, a)
            return a, b.sym
        elif c_val < 0:
            c = connect(b, a)
            return c.sym, c
        else:
            return a, b.sym

    # --- KROK REKURENCYJNY (DIVIDE) ---
    mid = (start + end) // 2
    ldo_left, rdo_left = build_delaunay_triangulation(points, start, mid)
    ldo_right, rdo_right = build_delaunay_triangulation(points, mid, end)
    
    # --- FAZA MERGE (CONQUER) ---
    return merge_triangulations(ldo_left, rdo_left, ldo_right, rdo_right, points)


def _extract_triangles_from_edges(
    seed_edges: Tuple[Edge, Edge],
    points: np.ndarray,
    sorted_to_original: np.ndarray,
) -> List[Tuple[int, int, int]]:
    """Extract primal triangles by traversing reachable directed edges.

    Each triangle is returned in CCW order. Because the quad-edge
    traversal visits every triangle up to three times (once per incident
    directed edge), the raw vertex triples are first canonicalised by
    sorted vertex set — that gives us one entry per undirected triangle —
    then re-rotated into CCW order so the caller sees a consistent
    orientation.
    """
    canonical_by_vertex_set: dict[tuple[int, int, int], Tuple[int, int, int]] = {}
    visited: set[tuple[int, int]] = set()
    stack = [seed_edges[0], seed_edges[1]]

    while stack:
        e = stack.pop()
        edge_id = (id(e.qe), e.index)
        if edge_id in visited:
            continue
        visited.add(edge_id)

        if e.data is not None and e.sym.data is not None:
            if e.lnext.lnext.lnext == e:
                a, b, c = e.origin, e.dest, e.lnext.dest
                key = tuple(sorted((a, b, c)))
                if key not in canonical_by_vertex_set:
                    canonical_by_vertex_set[key] = (a, b, c)

        stack.extend([e.onext, e.sym])

    triangles: List[Tuple[int, int, int]] = []
    for key, (a, b, c) in canonical_by_vertex_set.items():
        if ccw_index(a, b, c, points) < 0:
            a, b, c = a, c, b
        triangles.append(
            (
                int(sorted_to_original[a]),
                int(sorted_to_original[b]),
                int(sorted_to_original[c]),
            )
        )
    triangles.sort()
    return triangles


def triangulate_dnc(points: np.ndarray) -> List[Tuple[int, int, int]]:
    """Build Delaunay triangulation and return triangles as original point indices."""
    if len(points) < 3:
        return []

    sorted_indices = np.lexsort((points[:, 1], points[:, 0]))
    sorted_points = points[sorted_indices]

    ldo, rdo = build_delaunay_triangulation(sorted_points, 0, len(sorted_points))
    return _extract_triangles_from_edges((ldo, rdo), sorted_points, sorted_indices)

# if __name__ == '__main__':
#     np.random.seed(271)
#     input_point_cloud = np.random.rand(100, 2)

#     triangles = triangulate_dnc(input_point_cloud)
#     # triangles = delaunay_rust.triangulate_points(input_point_cloud, True)
#     # triangles = delaunay_rust.triangulate_points_dnc(input_point_cloud)
#     # triangles = delaunay_cpp.triangulate_points_dnc(input_point_cloud)

#     print(f"Liczba trojkatow: {len(triangles)}")
    
#     draw_triangulation(input_point_cloud, triangles)