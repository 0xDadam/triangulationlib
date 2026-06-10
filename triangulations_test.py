import numpy as np
import time
import gc

from triangulation_python.dnc import triangulate_dnc
import delaunay_cpp
import delaunay_rust

def run_benchmark():
    np.random.seed(271)
    
    algorithms = {
        "Python (DNC)": lambda pts: triangulate_dnc(pts),
        "Rust (Bowyer-Watson)": lambda pts: delaunay_rust.triangulate_points(pts, True),
        "Rust (DNC)": lambda pts: delaunay_rust.triangulate_points_dnc(pts),
        "C++ (Bowyer-Watson)": lambda pts: delaunay_cpp.triangulate_points(pts),
        "C++ (DNC)": lambda pts: delaunay_cpp.triangulate_points_dnc(pts)
    }

    # --- ETAP 1: Porównanie dla zdefiniowanych rozmiarów ---
    fixed_sizes = [100, 1000, 5000, 10000]
    fixed_results = {name: [] for name in algorithms}
    
    print("Rozpoczynam testy dla stałych rozmiarów...")
    for size in fixed_sizes:
        print(f" -> Generowanie chmury {size} punktów...")
        input_point_cloud = np.random.rand(size, 2)
        
        for name, func in algorithms.items():
            gc.collect() # Czyszczenie pamięci przed pomiarem
            start_time = time.perf_counter()
            try:
                func(input_point_cloud)
                elapsed = time.perf_counter() - start_time
            except Exception as e:
                print(f"Błąd w {name}: {e}")
                elapsed = None
            
            fixed_results[name].append(elapsed)

    # --- ETAP 2: Szukanie maksymalnego N dla limitu 2 sekund ---
    target_time_limit = 2.0
    max_n_results = {}
    
    print(f"\nRozpoczynam szukanie maksymalnej siatki dla limitu {target_time_limit}s...")
    for name, func in algorithms.items():
        print(f" -> Testowanie: {name}")
        current_n = 1000
        max_successful_n = 0
        
        while True:
            pts = np.random.rand(current_n, 2)
            gc.collect()
            start_time = time.perf_counter()
            
            try:
                func(pts)
                elapsed = time.perf_counter() - start_time
            except Exception:
                break
                
            if elapsed > target_time_limit:
                break
            else:
                max_successful_n = current_n
                # Heurystyka zwiększania N: rośniemy agresywnie, gdy czas jest krótki, 
                # i wolniej, gdy zbliżamy się do 2 sekund.
                if elapsed < 0.2:
                    current_n = int(current_n * 3)
                elif elapsed < 1.0:
                    current_n = int(current_n * 1.5)
                else:
                    current_n = int(current_n * 1.2)
                    
        max_n_results[name] = max_successful_n
        print(f"    Max N: {max_successful_n}")

    # --- ETAP 3: Generowanie pliku Markdown ---
    print("\nZapisywanie wyników do pliku 'benchmark_wyniki.md'...")
    md_content = "# Wyniki Benchmarku Algorytmów Triangulacji\n\n"
    
    # Tabela 1
    md_content += "## 1. Czas wykonania dla stałych rozmiarów siatki (w sekundach)\n\n"
    md_content += "| Algorytm | " + " | ".join([f"N={s}" for s in fixed_sizes]) + " |\n"
    md_content += "|---| " + " | ".join(["---" for _ in fixed_sizes]) + " |\n"
    
    for name in algorithms:
        times = []
        for t in fixed_results[name]:
            if t is None:
                times.append("Błąd")
            else:
                times.append(f"{t:.4f}s")
        md_content += f"| **{name}** | " + " | ".join(times) + " |\n"
        
    md_content += "\n---\n\n"
    
    # Tabela 2
    md_content += f"## 2. Maksymalny rozmiar siatki (N) policzony w czasie poniżej {target_time_limit} sekund\n\n"
    md_content += "| Algorytm | Max Liczba Punktów (N) |\n"
    md_content += "|---|---|\n"
    
    # Sortowanie od najlepszego (największe N) do najsłabszego
    sorted_max_n = sorted(max_n_results.items(), key=lambda item: item[1], reverse=True)
    
    for name, max_n in sorted_max_n:
        md_content += f"| **{name}** | {max_n:,} |\n".replace(',', ' ') # formatowanie z odstępem tysięcznym

    with open("benchmark_wyniki.md", "w", encoding="utf-8") as file:
        file.write(md_content)
        
    print("Gotowe! Plik został wygenerowany.")

if __name__ == "__main__":
    run_benchmark()