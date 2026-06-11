# Wyniki Benchmarku Algorytmów Triangulacji

## 1. Czas wykonania dla stałych rozmiarów siatki (w sekundach)

| Algorytm | N=100 | N=1000 | N=5000 | N=10000 |
|---| --- | --- | --- | --- |
| **Python (DNC)** | 0.0084s | 0.0871s | 0.5011s | 1.1001s |
| **Rust (DNC)** | 0.0002s | 0.0011s | 0.0078s | 0.0147s |
| **C++ (DNC)** | 0.0002s | 0.0015s | 0.0092s | 0.0191s |
| **Python (Bowyer-Watson)** | 0.0048s | 0.0618s | 0.6786s | 2.2801s |
| **Rust (Bowyer-Watson)** | 0.0003s | 0.0013s | 0.0110s | 0.0273s |
| **C++ (Bowyer-Watson)** | 0.0002s | 0.0015s | 0.0117s | 0.0296s |

---

## 2. Maksymalny rozmiar siatki (N) policzony w czasie poniżej 2.0 sekund

| Algorytm | Max Liczba Punktów (N) |
|---|---|
| **Rust (DNC)** | 787 320 |
| **C++ (DNC)** | 656 100 |
| **C++ (Bowyer-Watson)** | 145 800 |
| **Rust (Bowyer-Watson)** | 121 500 |
| **Python (DNC)** | 14 580 |
| **Python (Bowyer-Watson)** | 8 100 |
