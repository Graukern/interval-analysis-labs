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


def print_case_report(title: str, mid: np.ndarray, R: np.ndarray) -> None:
    print("=" * 70)
    print(f" {title} ")
    print("=" * 70)

    # 1. Поиск критического delta
    delta_crit, x_sol = find_critical_delta(mid, R)
    print(f"1. Диапазон значений параметра delta:")
    print(f"   Минимальное delta_crit = {delta_crit:.8f}")
    print(f"   Матрица особенная при delta in [{delta_crit:.8f}, +inf)")
    print(f"   Ненулевой вектор x: {np.round(x_sol, 6)}")

    # 2. Построение точечной матрицы A'
    matrix_crit = IntervalMatrix(mid, delta_crit * R)
    A_prime = matrix_crit.build_singular_matrix(x_sol)
    print("\n2. Построенная точечная матрица A':")
    print(np.array2string(A_prime, precision=6, suppress_small=True))

    # 3. Проверка свойств
    is_valid = matrix_crit.verify_singular_solution(x_sol)
    full_rank = min(A_prime.shape)
    actual_rank = np.linalg.matrix_rank(A_prime)
    
    print("\n3. Проверка принадлежности и особенности:")
    print(f"   Ранг матрицы: {actual_rank} (полный ранг = {full_rank})")
    print(f"   Дефицит ранга: {actual_rank < full_rank}")
    
    if A_prime.shape[0] == A_prime.shape[1]:
        print(f"   det(A') = {np.linalg.det(A_prime):.2e}")
    else:
        # Для прямоугольной 3x2 проверяем норму невязки A' @ x
        res_norm = np.linalg.norm(A_prime @ x_sol)
        print(f"   ||A' @ x|| = {res_norm:.2e} (столбцы линейно зависимы)")

    print(f"   Принадлежит интервалу [mid - rad, mid + rad]: {is_valid}")
    print()


if __name__ == "__main__":
    np.set_printoptions(precision=6, suppress=True)

    # --- Задание 1. Прямоугольная матрица A1 (3x2) ---
    mid_A1 = np.array([
        [0.95, 1.00],
        [1.05, 1.00],
        [1.10, 1.00]
    ])

    # Случай 1: rad A1 (все элементы с погрешностью / томография)
    R_A1_full = np.array([
        [1.0, 1.0],
        [1.0, 1.0],
        [1.0, 1.0]
    ])
    print_case_report(
        "Задание 1.1: Прямоугольная матрица A1 (все элементы варьируются)",
        mid_A1,
        R_A1_full
    )

    # Случай 2: rad A1 (только 1-й столбец с погрешностью / регрессия)
    R_A1_col1 = np.array([
        [1.0, 0.0],
        [1.0, 0.0],
        [1.0, 0.0]
    ])
    print_case_report(
        "Задание 1.2: Прямоугольная матрица A1 (только 1-й столбец варьируется)",
        mid_A1,
        R_A1_col1
    )

    # --- Задание 2. Квадратная матрица A2 (3x3) ---
    mid_A2 = np.array([
        [1.10, 0.90, 1.10],
        [1.40, 1.00, 0.80],
        [0.80, 1.40, 1.20]
    ])
    R_A2 = np.ones((3, 3))
    print_case_report(
        "Задание 2: Квадратная матрица A2 (3x3)",
        mid_A2,
        R_A2
    )