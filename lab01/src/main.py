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


    def lp(self, signs: np.ndarray) -> np.ndarray:
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

        if result.success:
            return signs * result.x
        else:
            return None

    def is_singular(self) -> np.ndarray:
        n = self.mid.shape[1]
        for combo in product([1, -1], repeat=n-1):
            signs = [1] + list(combo)
            result_x = self.lp(signs)
            if result_x is not None: return result_x
        return None


    def build_singular_matrix(self, x: np.ndarray) -> np.ndarray:
        T = -self.mid_times(x)
        alpha = T / (self.rad_times_abs(x))
        delta = np.outer(alpha, np.sign(x)) * self.rad

        return self.mid + delta

    def verify_singular_solution(self, x: np.ndarray) -> bool:
        A_prime = self.build_singular_matrix(x)
        full_rank = min(A_prime.shape)
        is_deficient =  np.linalg.matrix_rank(A_prime) < full_rank

        tol = 1e-6
        above_lower = A_prime >= self.lower() - tol
        below_upper = A_prime <= self.upper() + tol
        in_box = np.all(above_lower & below_upper)

        return bool(is_deficient and in_box)

def upper_bound_delta(mid: np.ndarray, R: np.ndarray) -> float:
    x = np.ones(mid.shape[1])
    high = np.max(np.abs(mid @ x) / (R @ x))
    return high


def find_critical_delta(mid: np.ndarray, R: np.ndarray) -> tuple[float, np.ndarray]:
    lower, high = 0.0, upper_bound_delta(mid, R) 
    best_x = None
    for _ in range(100):
        mid_delta = lower + (high - lower) / 2
        matrix = IntervalMatrix(mid, mid_delta * R)
        result_x = matrix.is_singular()
        if result_x is not None:
            high = mid_delta
            best_x = result_x
        else:
            lower = mid_delta
    return high, best_x




if __name__ == "__main__":
    mid_A1 = np.array([[0.95, 1.00], [1.05, 1.00], [1.10, 1.00]])
    R_3 = np.array([[1.0, 1.0], [1.0, 1.0], [1.0, 1.0]])   
    R_4 = np.array([[1.0, 0.0], [1.0, 0.0], [1.0, 0.0]])   

    delta3, x3 = find_critical_delta(mid_A1, R_3)
    matrix3 = IntervalMatrix(mid_A1, delta3 * R_3)
    print(matrix3.verify_singular_solution(x3))   # ожидаем True

    delta4, x4 = find_critical_delta(mid_A1, R_4)
    matrix4 = IntervalMatrix(mid_A1, delta4 * R_4)
    print(matrix4.verify_singular_solution(x4))   # ожидаем True