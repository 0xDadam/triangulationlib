# Wyniki Benchmarku Algorytmów Triangulacji

## 1. Czas wykonania dla stałych rozmiarów siatki (w sekundach)

| Algorytm | N=100 | N=1000 | N=5000 | N=10000 |
|---| --- | --- | --- | --- |
| **Python (DNC)** | 0.0062s | 0.0874s | 0.4935s | 1.0731s |
| **Rust (DNC)** | 0.0003s | 0.0011s | 0.0073s | 0.0152s |
| **C++ (DNC)** | 0.0002s | 0.0016s | 0.0094s | 0.0197s |
| **Python (Bowyer-Watson)** | 0.0048s | 0.0632s | 0.6571s | 2.1104s |
| **Rust (Bowyer-Watson)** | 0.0001s | 0.0013s | 0.0105s | 0.0248s |
| **C++ (Bowyer-Watson)** | 0.0001s | 0.0016s | 0.0112s | 0.0273s |

---

## 2. Maksymalny rozmiar siatki (N) policzony w czasie poniżej 2.0 sekund

| Algorytm | Max Liczba Punktów (N) |
|---|---|
| **Rust (DNC)** | 787 320 |
| **C++ (DNC)** | 656 100 |
| **Rust (Bowyer-Watson)** | 145 800 |
| **C++ (Bowyer-Watson)** | 145 800 |
| **Python (DNC)** | 14 580 |
| **Python (Bowyer-Watson)** | 8 100 |
