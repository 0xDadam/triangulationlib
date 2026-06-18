# Triangulacja Delaunaya: Python · Rust · C++

Repozytorium porównuje trzy implementacje triangulacji Delaunaya — referencyjną w czystym Pythonie oraz dwie natywne (Rust i C++) udostępnione jako moduły Pythona przez FFI. Każda z bibliotek implementuje dwa algorytmy:

- **Bowyer–Watson** (przyrostowy) — w wariancie naiwnym O(N²) i w wariancie zoptymalizowanym heurystyką *Triangle Walk* O(N√N).
- **Divide & Conquer** (dziel i zwyciężaj) — oparty na strukturze Quad-Edge Guibasa-Stolfiego, złożoność O(N log N).

Wynikiem każdej funkcji jest lista trójkątów w postaci indeksów punktów wejściowych (`(N, 2)`-wymiarowa tablica NumPy), bez trójkątów zawierających wierzchołki super-trójkąta.

## Struktura repozytorium

```
triangulationlib/
├── triangulation_python/      # implementacja referencyjna (czysty Python)
│   ├── geometry.py            #   predykaty: ccw, in_circle, left/right_of
│   ├── quad_edge.py           #   struktura Quad-Edge (Guibas–Stolfi)
│   ├── incremental.py         #   Bowyer–Watson (klasa DelaunayTriangulation)
│   └── dnc.py                 #   Divide & Conquer na quad-edge'ach
│
├── triangulation_rust/        # biblioteka Rust → moduł `delaunay_rust`
│   ├── Cargo.toml             #   pyo3, numpy, slotmap
│   ├── pyproject.toml         #   build backend: maturin
│   └── src/
│       ├── lib.rs             #   bindingi PyO3
│       ├── geometry/          #   Point, Triangle, predykaty
│       ├── py_convert.rs      #   konwersja ndarray ↔ Vec<Point>
│       └── algorithms/
│           ├── incremental/   #   Bowyer–Watson z triangle walk
│           └── divide_and_conquer/  #   quad-edge w Ruście
│
├── triangulation_cpp/         # biblioteka C++ → moduł `delaunay_cpp`
│   ├── CMakeLists.txt         #   scikit-build-core, pybind11, C++23, -O3 -march=native
│   ├── pyproject.toml         #   build backend: scikit-build-core
│   └── src/
│       ├── main_module.cpp    #   bindingi pybind11
│       ├── py_convert.hpp     #   konwersja py::array_t ↔ std::vector<Point>
│       ├── geometry/          #   point.hpp, triangle.hpp, predykaty
│       └── algorithms/
│           ├── incremental/   #   Bowyer–Watson z triangle walk
│           └── divide_and_conquer/  #   quad-edge w C++ (SlotMap)
│
├── tests/                     # testy integracyjne (pytest)
│   ├── conftest.py            #   dodaje katalog projektu do sys.path
│   └── test_triangulations.py #   sprawdza warunek Delaunaya dla każdego wariantu
│
├── triangulations_test.py     # benchmark porównawczy (zapisuje benchmark_wyniki.md)
├── visualization.py           # rysowanie wynikowej siatki (matplotlib)
├── benchmark_wyniki.md        # ostatnie wyniki benchmarku
├── prezentacja.md             # pełna prezentacja projektu (algorytmy, decyzje, wnioski)
├── project_presentation.ipynb # wersja notatnikowa prezentacji
└── environment.yml           # środowisko conda (python 3.12, maturin, pybind11, cmake)
```

## Szybki start

### 1. Środowisko

```bash
conda env create -f environment.yml
conda activate delaunay_env
```

### 2. Instalacja modułów natywnych

```bash
# Rust (maturin)
pip install -e ./triangulation_rust

# C++ (scikit-build-core)
pip install -e ./triangulation_cpp
```

Po instalacji dostępne są moduły `delaunay_rust` i `delaunay_cpp`. Moduł `triangulation_python` jest zwykłym pakietem dodanym do ścieżki (`import triangulation_python`).

### 3. Przykład użycia

```python
import numpy as np
import delaunay_rust
import delaunay_cpp
from triangulation_python.dnc import triangulate_dnc
from triangulation_python.incremental import triangulate_python_bw

points = np.random.rand(1000, 2)

# Bowyer–Watson (z triangle walk, domyślnie)
triangles_py = triangulate_python_bw(points)
triangles_rs = delaunay_rust.triangulate_points(points, True)
triangles_cpp = delaunay_cpp.triangulate_points(points, True)

# Divide & Conquer
triangles_py_dnc = triangulate_dnc(points)
triangles_rs_dnc = delaunay_rust.triangulate_points_dnc(points)
triangles_cpp_dnc = delaunay_cpp.triangulate_points_dnc(points)
```

Wizualizacja wyniku:

```python
from visualization import draw_triangulation
draw_triangulation(points, triangles_rs_dnc, title="Delaunay — Rust DNC")
```

## Publiczne API

Wszystkie trzy implementacje przyjmują `np.ndarray` o kształcie `(N, 2)` i zwracają `np.ndarray` o kształcie `(M, 3)` — indeksy wierzchołków (CCW) posortowanych trójkątów.

| Moduł | Funkcja | Algorytm | Dodatkowe flagi |
|---|---|---|---|
| `triangulation_python.incremental` | `triangulate_python_bw(points)` | Bowyer–Watson | zawsze triangle walk |
| `triangulation_python.dnc` | `triangulate_dnc(points)` | Divide & Conquer | — |
| `delaunay_rust` | `triangulate_points(points, use_triangle_walk=True)` | Bowyer–Watson | `use_triangle_walk=False` → wariant naiwny |
| `delaunay_rust` | `triangulate_points_dnc(points)` | Divide & Conquer | — |
| `delaunay_cpp` | `triangulate_points(points, use_triangle_walk=True)` | Bowyer–Watson | `use_triangle_walk=False` → wariant naiwny |
| `delaunay_cpp` | `triangulate_points_dnc(points)` | Divide & Conquer | — |

## Benchmark

Uruchomienie `python triangulations_test.py` wykonuje dwa testy dla każdego z sześciu wariantów:

1. **Stałe rozmiary siatki** (N = 100, 1 000, 5 000, 10 000) — czas wykonania w sekundach.
2. **Maksymalne N w limicie 2 s** — największa chmura punktów policzona poniżej 2-sekundowego limitu; rozmiar rośnie heurystycznie (×3 / ×1.5 / ×1.2 w zależności od zbliżania się do progu).

Wyniki trafiają do pliku `benchmark_wyniki.md`. Orientacyjne liczby z ostatniego uruchomienia:

| Algorytm | N = 10 000 | Max N (< 2 s) |
|---|---:|---:|
| Rust (DNC) | 0.015 s | 787 320 |
| C++ (DNC) | 0.019 s | 656 100 |
| C++ (Bowyer–Watson) | 0.030 s | 145 800 |
| Rust (Bowyer–Watson) | 0.027 s | 121 500 |
| Python (DNC) | 1.10 s | 14 580 |
| Python (Bowyer–Watson) | 2.28 s | 8 100 |

DNC wygrywa z Bowyer–Watsonem zarówno w czystej złożoności (N log N vs N√N), jak i w praktyce — implementacje natywne liczą ponad 100 tys. punktów w ułamku sekundy. Pełne omówienie wyników i decyzji architektonicznych znajduje się w `prezentacja.md` / `project_presentation.ipynb`.

## Testy integracyjne (pytest)

Siedem zestawów testów w `tests/test_triangulations.py` weryfikuje każdy z ośmiu wariantów triangulacji (Python/Rust/C++ × Bowyer–Watson/DNC, plus wariant naiwny BW bez triangle walk):

```bash
python -m pytest tests/ -v
```

Co sprawdzają:

| Test | Co weryfikuje |
|---|---|
| `test_output_shape_and_indices` | Kształt `(M, 3)`, zakres indeksów, brak trójkątów z powtórzonym wierzchołkiem |
| `test_strict_ccw_orientation` | Każdy trójkąt ma ściśle dodatnie pole ze znakiem (CCW) |
| `test_delaunay_empty_circumcircle` | **Definicja Delaunaya**: dla każdego trójkąta żaden inny punkt wejściowy nie leży ściśle wewnątrz jego okręgu opisanego (predykat in-circle z wyznacznika 3×3) |
| `test_no_duplicate_triangles` | Brak zduplikowanych trójkątów (niezależnie od orientacji) |
| `test_all_vertices_used` | Każdy punkt wejściowy pojawia się w co najmniej jednym trójkącie |
| `test_planar_edge_count` | Spójność z twierdzeniem Eulera: `3·M = 2·E_i + E_h` |
| `test_unit_square_two_triangles`, `test_three_points_single_triangle`, `test_all_implementations_agree_on_square_with_center` | Testy dokładnych wyników na małych chmurach z jednoznaczną triangulacją |

Testy są parametryzowane na wielu scenariuszach: kwadrat, kwadrat z punktem środkowym, chmury wielokątów niewypukłych, losowe chmury jednostajne (50 i 200 punktów), chmury gaussowskie (100 punktów) oraz chmury na okręgu z niewielkim szumem.

## Główne decyzje implementacyjne

- **Reprezentacja grafu.** Python trzyma trójkąty jako obiekty na stercie z referencjami (`Triangle.neighbors = [None, None, None]`). Rust i C++ używają płaskich `Vec` / `std::vector` indeksów — gwarantuje to ciągłość pamięci i dobrą lokalność cache.
- **Brak `std::shared_ptr` w C++.** Cykliczne referencje między trójkątami wymuszałyby wielowątkowe liczniki odwołań; indeksy rozwiązują ten problem za darmo.
- **Prealokacja.** Z twierdzenia Eulera dla grafów planarnych wynika, że liczba krawędzi ≤ 3N−3, więc `Vec::with_capacity(points.len() * 2)` wystarcza, by uniknąć realokacji w trakcie triangulacji.
- **Nullability sąsiada.** Python — `None`. Rust — `Option<usize>`. C++ — sentinel `NO_NEIGHBOR = std::numeric_limits<size_t>::max()`.
- **Borrow checker vs. C++.** W Ruście aktualizacja sąsiadów nowo dodawanego trójkąta wymaga rozbicia logiki na dwa przebiegi (`push`, potem mutacja starych sąsiadów), ponieważ jednoczesne `&mut triangles[n]` dla wielu indeksów jest niedozwolone. C++ pozwala scalić te przebiegi w jedną pętlę — kod jest krótszy, kosztem bezpieczeństwa, które i tak daje borrow checker.
- **Struktura Quad-Edge.** DNC opiera się na strukturze krawędzi skierowanych Guibasa-Stolfiego. W Pythonie to klasa `Edge` z atrybutami `onext`/`oprev`/`sym`. W C++ do zarządzania pulą krawędzi służy `SlotMap`. W Ruście ten sam pomysł realizuje crate `slotmap`.

## Materiały dodatkowe

- `tests/test_triangulations.py` — testy integracyjne pytest (warunek Delaunaya + testy strukturalne dla każdego wariantu).
- `prezentacja.md` — pełne omówienie algorytmów, decyzji architektonicznych i wniosków z benchmarku (po polsku).
- `project_presentation.ipynb` — wersja notatnikowa tej samej treści.
- `benchmark_wyniki.md` — tabela wyników z ostatniego uruchomienia benchmarku.
- `visualization.py` — `draw_triangulation(points, triangles, title)` do ręcznej weryfikacji siatki.
