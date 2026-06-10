# Wyniki Benchmarku Algorytmów Triangulacji

## 1. Czas wykonania dla stałych rozmiarów siatki (w sekundach)

| Algorytm | N=100 | N=1000 | N=5000 | N=10000 |
|---| --- | --- | --- | --- |
| **Python (DNC)** | 0.0071s | 0.1126s | 0.5399s | 1.1250s |
| **Rust (Bowyer-Watson)** | 0.0005s | 0.0014s | 0.0108s | 0.0248s |
| **Rust (DNC)** | 0.0001s | 0.0011s | 0.0076s | 0.0148s |
| **C++ (Bowyer-Watson)** | 0.0002s | 0.0016s | 0.0124s | 0.0280s |
| **C++ (DNC)** | 0.0001s | 0.0016s | 0.0101s | 0.0197s |

---

## 2. Maksymalny rozmiar siatki (N) policzony w czasie poniżej 2.0 sekund

| Algorytm | Max Liczba Punktów (N) |
|---|---|
| **Rust (DNC)** | 787 320 |
| **C++ (DNC)** | 656 100 |
| **C++ (Bowyer-Watson)** | 145 800 |
| **Rust (Bowyer-Watson)** | 121 500 |
| **Python (DNC)** | 14 580 |
