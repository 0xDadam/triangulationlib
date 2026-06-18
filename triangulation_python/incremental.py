EPS = 1e-12
import numpy as np

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Point({self.x}, {self.y})"

    def __eq__(self, other):
        if not isinstance(other, Point):
            return False
        return abs(self.x - other.x) < EPS and abs(self.y - other.y) < EPS

    # potrzebne do wizualizacji
    def __hash__(self):
        return hash((self.x, self.y))

def in_circle(a, b, c, d):
    ax, ay = a.x - d.x, a.y - d.y
    bx, by = b.x - d.x, b.y - d.y
    cx, cy = c.x - d.x, c.y - d.y

    #uproszczony wyznacznik z 4x4 na 3x3 
    det = (
        (ax * ax + ay * ay) * (bx * cy - cx * by) -
        (bx * bx + by * by) * (ax * cy - cx * ay) +
        (cx * cx + cy * cy) * (ax * by - bx * ay)
    )

    if det > EPS:
        return True
    elif det < -EPS:
        return False
    else:
        return True
    

def det_orient(a, b, c):
    return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x)


class Triangle:
    def __init__(self, p0, p1, p2):
        #ccw!
        self.vertices = [p0, p1, p2]
        #neighbors[i] - trrojkat stykajacy sie krawedzoia vertices[i], vertices[(i + 1) % 3]
        self.neighbors = [None, None, None] 
        self.active = True 

    def __repr__(self):
        return f"Tri({self.vertices[0]}, {self.vertices[1]}, {self.vertices[2]})"

    def contains_point(self, p):
        d1 = det_orient(self.vertices[0], self.vertices[1], p)
        d2 = det_orient(self.vertices[1], self.vertices[2], p)
        d3 = det_orient(self.vertices[2], self.vertices[0], p)
        #wszystkie po lewej -> w srodku
        return d1 >= -EPS and d2 >= -EPS and d3 >= -EPS


def find_triangle_naive(triangles, p):
    for tri in triangles:
        if tri.active and tri.contains_point(p):
            return tri
    return None

def find_triangle_walk(triangles, p, start_tri=None):
    if start_tri is None or not start_tri.active:
            start_tri = triangles[-1]
    current = start_tri
    limit = len(triangles) + 10
    step = 0

    while step < limit:
        step += 1
        for i in range(3):
            p1 = current.vertices[i]
            p2 = current.vertices[(i + 1) % 3]
            
            if det_orient(p1, p2, p) < -EPS:
                neighbor = current.neighbors[i]
                if neighbor is None:
                    return current 
                current = neighbor
                break
        else:
            return current

    print("1")
    return find_triangle_naive(triangles, p)
        
class DelaunayTriangulation:
    def __init__(self, width=1000, height=1000):
        p1 = Point(-10 * width, -10 * height)
        p2 = Point(10 * width, -10 * height)
        p3 = Point(0, 10 * height)
        
        self.super_triangle = Triangle(p1, p2, p3)
        self.triangles = [self.super_triangle]
    
    def add_point(self, p, search_method="walk"):
        if search_method == "naive":
            start_tri = find_triangle_naive(self.triangles, p)
        else:
            start_search = self.triangles[-1] if self.triangles else None
            start_tri = find_triangle_walk(self.triangles, p, start_search)

        if start_tri is None:
            return
            
        bad_triangles = []
        self._find_bad_triangles(p, start_tri, bad_triangles)
        
        boundary = [] 
        
        for t in bad_triangles:
            t.active = False
            for i in range(3):
                neighbor = t.neighbors[i]
                if neighbor not in bad_triangles:
                    edge = (t.vertices[i], t.vertices[(i + 1) % 3])
                    boundary.append((edge, neighbor))
        
        #usuwam zle trojkaty
        self.triangles = [t for t in self.triangles if t.active]

        new_triangles = []
        for (p1, p2), neighbor in boundary:
            new_tri = Triangle(p1, p2, p)
            new_tri.neighbors[0] = neighbor
            
            if neighbor:
                for i in range(3):
                    if neighbor.vertices[i] == p2 and neighbor.vertices[(i + 1) % 3] == p1:
                        neighbor.neighbors[i] = new_tri
                        break
            
            new_triangles.append(new_tri)
        
        self._link_new_triangles(new_triangles, p)
        self.triangles.extend(new_triangles)

    def _find_bad_triangles(self, p, start_tri, bad_triangles):
        if not in_circle(start_tri.vertices[0], start_tri.vertices[1], start_tri.vertices[2], p):
            return

        stack = [start_tri]
        visited = set()
        
        while stack:
            t = stack.pop()
            if t in visited: continue
            visited.add(t)
            
            #warunek delaunaya
            if in_circle(t.vertices[0], t.vertices[1], t.vertices[2], p):
                bad_triangles.append(t)

                for n in t.neighbors:
                    if n and n not in visited and n.active:
                        stack.append(n)
                        
    def _link_new_triangles(self, new_triangles, center_p):
        for t1 in new_triangles:
            for t2 in new_triangles:
                if t1 == t2: continue
                
                if t1.vertices[1] == t2.vertices[0]:
                    t1.neighbors[1] = t2

                if t1.vertices[0] == t2.vertices[1]:
                    t1.neighbors[2] = t2

    def get_final_triangles(self, input_points):
        """
        Filtruje trójkąty usuwając te powiązane z super-trójkątem
        i zwraca tablicę indeksów w formacie [[id1, id2, id3], ...]

        Każdy trójkąt jest zwracany w orientacji CCW: jeżeli wypadł CW
        (bo krawędź graniczna pochodzi od trójkąta zdegenerowanego),
        dwa ostatnie wierzchołki są zamieniane przed zwróceniem.
        """
        # Tworzymy mapowanie: obiekt Point -> jego indeks w oryginalnej chmurze punktów
        point_to_idx = {Point(pt[0], pt[1]): i for i, pt in enumerate(input_points)}

        final_triangles = []
        for t in self.triangles:
            if not t.active:
                continue

            # Sprawdzamy, czy któryś wierzchołek należy do super-trójkąta
            # (Super-trójkąt ma współrzędne rzędu 10 * width, czyli nie ma go w point_to_idx)
            is_super_triangle_vertex = False
            for v in t.vertices:
                if v not in point_to_idx:
                    is_super_triangle_vertex = True
                    break

            if not is_super_triangle_vertex:
                idx0 = point_to_idx[t.vertices[0]]
                idx1 = point_to_idx[t.vertices[1]]
                idx2 = point_to_idx[t.vertices[2]]

                # Wymuszamy orientację CCW: jeżeli pole ze znakiem jest
                # niedodatnie, zamieniamy ostatnie dwa indeksy.
                p0, p1, p2 = t.vertices[0], t.vertices[1], t.vertices[2]
                if det_orient(p0, p1, p2) <= 0:
                    idx1, idx2 = idx2, idx1

                final_triangles.append([idx0, idx1, idx2])

        return np.array(final_triangles, dtype=np.int32)
    
def triangulate_python_bw(points):
    """
    Główna funkcja interfejsu dla benchmarku.
    Przyjmuje tablicę numpy o kształcie (N, 2) i zwraca tablicę (M, 3).
    """
    # Inicjalizacja algorytmu z dopasowaniem do zakresu danych (zakładamy [0, 1])
    dt = DelaunayTriangulation(width=1, height=1)

    # Dodawanie punktów jeden po drugim
    for pt in points:
        p = Point(pt[0], pt[1])
        dt.add_point(p, search_method="walk") # "walk" jest znacznie szybszy niż "naive"
        
    # Pobranie i przefiltrowanie końcowej siatki
    return dt.get_final_triangles(points)