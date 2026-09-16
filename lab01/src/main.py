import numpy as np
from scipy.optimize import linprog
from itertools import product

class IntervalMatrix:
    def __init__(self, mid: np.ndarray, rad: np.ndarray) -> None:
        self.mid = mid
        self.rad = rad 


    def lower(self) -> np.ndarray:
        return self.mid - self.rad

    
    def upper(self) -> np.ndarray:
        return self.mid + self.rad


    def mid_times(self, x: np.ndarray) -> np.ndarray:
        return self.mid @ x


    def rad_times_abs(self, x: np.ndarray) -> np.ndarray:
        return self.rad @ np.abs(x)


    def lp(self, signs: np.ndarray) -> bool:
        n_rows = self.mid.shape[0]
        n_vars = self.mid.shape[1]
        D = np.diag(signs)

        M1 = self.mid @ D - self.rad
        M2 = -self.mid @ D - self.rad

        c = np.zeros(n_vars)             # Целевая функция: вектор нулей длины n
        A_eq = np.ones([1, n_vars])      # Матрица равенств: вектор-строка из единиц формы (1, n)
        b_eq = [1]                       # Правая часть уравнения-равенства: сумма всех переменных должна быть равна 1
        A_ub = np.vstack([M1, M2])       # Матрица неравенств: объединение двух матриц ограничений M1 и M2 по осям
        b_ub = np.zeros(2 * n_rows)      # Правая часть неравенств: вектор из четырёх нулей
        bounds = [(0, None)] * n_vars    # Границы переменных: задаёт неотрицательность переменных (xi >= 0) для всех n переменных.

        result = linprog(c=c, A_eq=A_eq, b_eq=b_eq, A_ub=A_ub, b_ub=b_ub, bounds=bounds)
        return(result.success)


    def is_singular(self) -> bool:
        n = self.mid.shape[1]
        for combo in product([1, -1], repeat=n-1):
            signs = [1] + list(combo)
            if self.lp(signs): return True
        return False


def upper_bound_delta(mid: np.ndarray, R: np.ndarray) -> float:
    x = np.ones(mid.shape[1])
    high = np.max(np.abs(mid @ x) / (R @ x))
    return high


def find_critical_delta(mid: np.ndarray, R: np.ndarray) -> float:
    lower, high = 0.0, upper_bound_delta(mid, R) 
    for _ in range(100):
        mid_delta = lower + (high - lower) / 2
        matrix = IntervalMatrix(mid, mid_delta * R)
        if matrix.is_singular():
            high = mid_delta
        else:
            lower = mid_delta
    return high


if __name__ == "__main__":
    mid_A1 = np.array([[0.95, 1.00], [1.05, 1.00], [1.10, 1.00]])
    R_3 = np.array([[1.0, 1.0], [1.0, 1.0], [1.0, 1.0]])

    m = IntervalMatrix(mid_A1, 1.05 * R_3)
    print(m.is_singular())   # ожидаем True

    mid_A1 = np.array([[0.95, 1.00], [1.05, 1.00], [1.10, 1.00]])
    R_3 = np.array([[1.0, 1.0], [1.0, 1.0], [1.0, 1.0]])
    R_4 = np.array([[1.0, 0.0], [1.0, 0.0], [1.0, 0.0]])

    print(find_critical_delta(mid_A1, R_3))
    print(find_critical_delta(mid_A1, R_4))
       