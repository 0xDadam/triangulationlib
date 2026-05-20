import numpy as np
import delaunay_rust

punkty = np.random.rand(100, 2)

wynik = delaunay_rust.triangulate_points(punkty)

print(wynik)