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
        n = self.mid.shape[0]
        D = np.diag(signs)

        M1 = self.mid @ D - self.rad
        M2 = -self.mid @ D - self.rad

        c = np.zeros(n)             # Целевая функция: вектор нулей длины n
        A_eq = np.ones([1, n])      # Матрица равенств: вектор-строка из единиц формы (1, n)
        b_eq = [1]                  # Правая часть уравнения-равенства: сумма всех переменных должна быть равна 1
        A_ub = np.vstack([M1, M2])  # Матрица неравенств: объединение двух матриц ограничений M1 и M2 по осям
        b_ub = np.zeros(2 * n)      # Правая часть неравенств: вектор из четырёх нулей
        bounds = [(0, None)] * n    # Границы переменных: задаёт неотрицательность переменных (xi >= 0) для всех n переменных.

        result = linprog(c=c, A_eq=A_eq, b_eq=b_eq, A_ub=A_ub, b_ub=b_ub, bounds=bounds)
        return(result.success)


    def is_singular(self) -> bool:
        n = self.mid.shape[0]
        for combo in product([1, -1], repeat=n-1):
            signs = [1] + list(combo)
            if self.lp(signs): return True
        return False


if __name__ == "__main__":
    mid = np.array([[1, 1], [1, -1]])

    rad_1 = np.array([[1, 1], [1, 1]])
    print(IntervalMatrix(mid, rad_1).is_singular())   # True

    rad_05 = np.array([[0.5, 0.5], [0.5, 0.5]])
    print(IntervalMatrix(mid, rad_05).is_singular())   # False

       