from typing import Optional

class Edge:
    """Pojedyncza krawędź skierowana w strukturze Quad-Edge."""
    __slots__ = ['qe', 'index', 'next', 'data']

    def __init__(self, qe: 'QuadEdge', index: int):
        self.qe: QuadEdge = qe
        self.index: int = index
        self.next: 'Edge' = self
        self.data: Optional[int] = None

    @property
    def rot(self) -> 'Edge':
        return self.qe.edges[(self.index + 1) % 4]
    
    @property
    def sym(self) -> 'Edge':
        return self.qe.edges[(self.index + 2) % 4]
    
    @property
    def rot_inv(self) -> 'Edge':
        return self.qe.edges[(self.index + 3) % 4]
    
    @property
    def onext(self) -> 'Edge':
        return self.next

    @property
    def oprev(self) -> 'Edge':
        return self.rot.onext.rot

    @property
    def lnext(self) -> 'Edge':
        return self.rot_inv.onext.rot

    @property
    def lprev(self) -> 'Edge':
        return self.next.sym

    @property
    def rnext(self) -> 'Edge':
        return self.rot.onext.rot_inv

    @property
    def rprev(self) -> 'Edge':
        return self.sym.onext

    @property
    def dnext(self) -> 'Edge':
        return self.sym.onext.sym

    @property
    def dprev(self) -> 'Edge':
        return self.rot_inv.onext.rot_inv
    
    @property
    def origin(self) -> int:
        assert self.data is not None, "Próba dostępu do pustej wartości (krawędź dualna)!"
        return self.data
    
    @origin.setter
    def origin(self, value: int):
        self.data = value

    @property
    def dest(self) -> int:
        assert self.sym.data is not None, "Próba dostępu do pustej wartości (krawędź dualna)!"
        return self.sym.data
    
    @dest.setter
    def dest(self, value: int):
        self.sym.data = value

class QuadEdge:
    """Krzyż topologiczny reprezentujący pojedynczą krawędź i jej dualną."""
    def __init__(self):
        self.edges = [Edge(self, i) for i in range(4)]
        e = self.edges
        
        e[0].next = e[0]
        e[1].next = e[3]
        e[2].next = e[2]
        e[3].next = e[1]

def splice(a: Edge, b: Edge) -> None:
    """Przełącza i łączy topologicznie dwie krawędzie (w przestrzeni pierwotnej i dualnej)."""
    alpha = a.onext.rot
    beta = b.onext.rot

    a.next, b.next = b.next, a.next
    alpha.next, beta.next = beta.next, alpha.next

def make_edge(origin_data: int, dest_data: int) -> Edge:
    """Zwraca nową strukturę QuadEdge, reprezentowaną przez krawędź e0, z zainicjowanymi ID."""
    qe = QuadEdge()
    e = qe.edges[0]
    e.origin = origin_data
    e.dest = dest_data
    return e

def connect(a: Edge, b: Edge) -> Edge:
    """Łączy punkt docelowy krawędzi a (a.dest) z punktem początkowym krawędzi b (b.origin)."""
    e = make_edge(a.dest, b.origin)
    splice(e, a.lnext)
    splice(e.sym, b)
    return e

def delete_edge(e: Edge) -> None:
    """Usuwa krawędź ze struktury topologicznej QuadEdge, odczepiając ją bezpiecznie od otoczenia."""
    splice(e, e.oprev)
    splice(e.sym, e.sym.oprev)
