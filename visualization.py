from typing import List, Tuple

import matplotlib.pyplot as plt
import numpy as np

def draw_triangulation(
    points: np.ndarray,
    triangles: List[Tuple[int, int, int]],
    title: str = 'Delaunay Triangulation',
):
    """Rysuje triangulację na podstawie listy trójkątów (indeksy punktów)."""
    plt.figure(figsize=(10, 8))
    plt.scatter(points[:, 0], points[:, 1], s=30, c='black', zorder=3)

    unique_edges = set()
    for a, b, c in triangles:
        unique_edges.add(tuple(sorted((a, b))))
        unique_edges.add(tuple(sorted((b, c))))
        unique_edges.add(tuple(sorted((c, a))))

    for i, j in unique_edges:
        p1 = points[i]
        p2 = points[j]
        plt.plot(
            [p1[0], p2[0]],
            [p1[1], p2[1]],
            color='tab:blue',
            alpha=0.8,
            linewidth=1.0,
            zorder=1,
        )

    for idx, (x, y) in enumerate(points):
        plt.text(x, y, str(idx), fontsize=8, color='tab:red', zorder=4)
            
    plt.title(title)
    plt.axis('equal')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def display_triangulation_structure(triangulation):
    import pandas as pd

    # Tworzymy DataFrame i nazywamy kolumny jako wierzchołki trójkąta
    df_triangles = pd.DataFrame(list(triangulation), columns=['Wierzchołek A', 'Wierzchołek B', 'Wierzchołek C'])

    # Dodajemy nagłówek z ładnym formatowaniem Markdown
    from IPython.display import display, Markdown
    display(Markdown("### **Struktura zbioru trójkątów (Indeksy punktów)**"))

    # Wyświetlamy tabelę (IPython automatycznie zrobi z tego ładny HTML)
    display(df_triangles)