import numpy as np
from triangulation_python.quad_edge import Edge


def ccw(pa: np.ndarray, pb: np.ndarray, pc: np.ndarray) -> float:
    """
    Test Counter-Clockwise (wyznacznik 2x2 macierzy).
    Jęsli > 0, to tworzą skręt w lewo (C w stosunku do odcinka A->B).
    Jeśli < 0, skręt w prawo (zgodnie ze wskazówkami zegara).
    Jeśli 0, leżą na jednej prostej współliniowo (collinear).
    """
    return (pb[0] - pa[0]) * (pc[1] - pa[1]) - (pb[1] - pa[1]) * (pc[0] - pa[0])

def ccw_index(pa: int, pb: int, pc: int, points:np.ndarray) -> float:
    return ccw(points[pa], points[pb], points[pc])

def right_of(x: int, e: Edge, points: np.ndarray) -> bool:
    """
    Czy punkt x znajduje się stricte po prawej stronie krawędzi e 
    skierowanej od e.origin do e.dest?
    """
    return ccw(points[x], points[e.dest], points[e.origin]) > 0

def left_of(x: int, e: Edge, points: np.ndarray) -> bool:
    """
    Czy punkt x znajduje się stricte po lewej stronie krawędzi e?
    """
    return ccw(points[x], points[e.origin], points[e.dest]) > 0

def in_circle(a: int, b: int, c: int, d: int, points: np.ndarray) -> bool:
    """
    Zwraca wartość > 0 (True) jeśli punkt 'd' leży ściśle WEWNĄTRZ okręgu 
    opisanego na trójkącie powstałym z punktów a, b, c (zakładając że a,b,c idą CCW).
    Wykorzystuje indeksy wierzchołków i tablicę punktów.
    """
    pa, pb, pc, pd = points[a], points[b], points[c], points[d]
    
    adx = pa[0] - pd[0]
    ady = pa[1] - pd[1]
    
    bdx = pb[0] - pd[0]
    bdy = pb[1] - pd[1]
    
    cdx = pc[0] - pd[0]
    cdy = pc[1] - pd[1]
    
    alift = adx * adx + ady * ady
    blift = bdx * bdx + bdy * bdy
    clift = cdx * cdx + cdy * cdy
    
    det = (
        alift * (bdx * cdy - cdx * bdy) +
        blift * (cdx * ady - adx * cdy) +
        clift * (adx * bdy - bdx * ady)
    )
    
    return det > 0
