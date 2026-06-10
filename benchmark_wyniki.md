# Wyniki Benchmarku Algorytmów Triangulacji

## 1. Czas wykonania dla stałych rozmiarów siatki (w sekundach)

| Algorytm | N=100 | N=1000 | N=5000 | N=10000 |
|---| --- | --- | --- | --- |
| **Python (DNC)** | 0.0099s | 0.0928s | 0.4981s | 1.0734s |
| **Rust (Bowyer-Watson)** | 0.0006s | 0.0014s | 0.0106s | 0.0258s |
| **Rust (DNC)** | 0.0001s | 0.0011s | 0.0072s | 0.0145s |
| **C++ (Bowyer-Watson)** | 0.0002s | 0.0017s | 0.0110s | 0.0263s |
| **C++ (DNC)** | 0.0006s | 0.0057s | 0.0350s | 0.0729s |

---

## 2. Maksymalny rozmiar siatki (N) policzony w czasie poniżej 2.0 sekund

| Algorytm | Max Liczba Punktów (N) |
|---|---|
| **Rust (DNC)** | 787 320 |
| **C++ (DNC)** | 196 828 |
| **Rust (Bowyer-Watson)** | 145 800 |
| **C++ (Bowyer-Watson)** | 145 800 |
| **Python (DNC)** | 14 580 |
