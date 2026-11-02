import math
from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt
from scipy.optimize import minimize_scalar


class Interval:
    def __init__(self, lo: float, hi: float):
        if lo > hi: 
            raise ValueError(f"Нижняя граница больше верхней lo = {lo}, hi = {hi}.")
        self.lo = lo
        self.hi = hi


    def mid(self) -> float:
        return (self.lo + self.hi) / 2.0 


    def rad(self) -> float:
        return (self.hi - self.lo) / 2.0


    def wid(self) -> float:
        return self.hi - self.lo


    def __add__(self, other: "Interval") -> "Interval":
        if not isinstance(other, Interval): 
            other = Interval(other, other)

        new_lo = self.lo + other.lo
        new_hi = self.hi + other.hi
        return Interval(new_lo, new_hi)


    def __radd__ (self, other):
        return self + other


    def __sub__(self, other: "Interval") -> "Interval":
        if not isinstance(other, Interval):
            other = Interval(other, other)

        new_lo = self.lo - other.hi
        new_hi = self.hi - other.lo
        return Interval(new_lo, new_hi)


    def __rsub__(self, other):
        if not isinstance(other, Interval):
            other = Interval(other, other)

        new_lo = other.lo - self.hi
        new_hi = other.hi - self.lo
        return Interval(new_lo, new_hi)


    def __mul__(self, other: "Interval") -> "Interval":
        if not isinstance(other, Interval): 
            other = Interval(other, other)
        comb = []

        for i in [self.lo, self.hi]:
            for j in [other.lo, other.hi]:
                comb.append(i * j)

        new_lo = min(comb)
        new_hi = max(comb)
        return Interval(new_lo, new_hi)


    def __rmul__(self, other):
        return self * other

    
    def __pow__(self, n: int) -> "Interval":
        if not isinstance(n, int):
            raise TypeError(f"Степень не целое число n={n}.")
        elif n < 0:
            raise ValueError(f"Степень отрицательная n={n}.")
        elif n == 0:
            return Interval(1, 1)

        new_interval = self
        for _ in range(1, n):
            new_interval *= self

        return new_interval
        
    def __repr__(self) -> str:
        return f"[{self.lo}, {self.hi}]"


def f1(x: float) -> float:
    return x ** 3 - 3 * x ** 2 + 2


def f1_horner(x: float) -> float:
    return ((x - 3) * x + 0) * x + 2


def df1(x: float):
    return 3 * x ** 2 - 6 * x


def s1(X: "Interval", c: float) -> "Interval":
    return X ** 2 + X * c + c ** 2 - 3 * X - 3 * c


def run_f1() -> None:
    X1 = Interval(0, 3)
    E1 = exact_range(f1, X1)

    print_row("B.1 естественное", f1(X1), E1, X1, 45)
    print_row("B.2 Горнер", f1_horner(X1), E1, X1, 27)

    for c in [0, 1.5, 3]:
        F1 = F_mv(f1, df1, X1, c)
        print_row(f"B.3 среднезначная c={c}", F1, E1, X1)

    for c in [0, 1.5, 3]:
        F1 = F_sl(f1, s1, X1, c)
        print_row(f"B.4 наклонная c={c}", F1, E1, X1)

    visualization(f1, X1, "f1")
    F1 = F_bic(f1, df1, X1)
    print_row("B.5 бицентрированная", F1, E1, X1)


def f2(x):
    cos_part = icos(x) if isinstance(x, Interval) else np.cos(x)
    return x ** 3 * cos_part


def f2_alt(x):
    cos_part = icos(x) if isinstance(x, Interval) else np.cos(x)
    return (x * x) * (x * cos_part)


def df2(x):
    if isinstance(x, Interval):
        return (x ** 2) * (3 * icos(x) - x * isin(x))
    return (x ** 2) * (3 * np.cos(x) - x * np.sin(x))


def s2(X: "Interval", c: float) -> "Interval":
    return (X ** 2 + X * c + c ** 2) * icos(X) + (c ** 3) * ((-1) * isin(X))


def run_f2() -> None:
    X2 = Interval(-2, 2)
    E2 = exact_range(f2, X2)

    print_row("B.1 f2 естественное", f2(X2), E2, X2, 20)
    print_row("B.2 f2 эквивалентная", f2_alt(X2), E2, X2, 20)

    for c in [-2, -1, 0, 1, 2]:
        F = F_mv(f2, df2, X2, c)
        print_row(f"B.3 f2 среднезначная c={c}", F, E2, X2)

    for c in [-2, -1, 0, 1, 2]:
        F = F_sl(f2, s2, X2, c)
        print_row(f"B.4 f2 наклонная c={c}", F, E2, X2)
        
    visualization(f2, X2, "f2")


def F_mv(f, df, X: "Interval", c: float) -> "Interval":
    return f(c) + df(X) * (X - c)


def F_sl(f, s, X: "Interval", c: float) -> "Interval":
    return f(c) + s(X, c) * (X - c)


def F_bic(f, df, X: "Interval") -> "Interval":
    df_interval = df(X)
    df_mid = df_interval.mid()
    df_rad = df_interval.rad()
    p = cut(df_mid / df_rad, Interval(-1, 1))

    c_lo = X.mid() - p * X.rad()
    c_hi = X.mid() + p * X.rad()

    return intersect(F_mv(f, df, X, c_lo), F_mv(f, df, X, c_hi))


def icos(x: Interval) -> Interval:
    has_valley = False
    has_peak = False

    k_lo = math.floor(x.lo / (2 * math.pi))
    k_hi = math.ceil(x.hi / (2 * math.pi))

    for k in range(k_lo, k_hi + 1):
        if x.lo <= math.pi + 2 * math.pi * k <= x.hi:
            has_valley = True
        if x.lo <= 2 * math.pi * k <= x.hi:
            has_peak = True
        if has_valley and has_peak:
            break

    new_lo = -1 if has_valley else min(math.cos(x.lo), math.cos(x.hi))
    new_hi = 1 if has_peak else max(math.cos(x.lo), math.cos(x.hi))
        
    return Interval(new_lo, new_hi)


def isin(x: Interval) -> Interval:
    has_valley = False
    has_peak = False

    k_lo = math.floor(x.lo / (2 * math.pi))
    k_hi = math.ceil(x.hi / (2 * math.pi))

    for k in range(k_lo, k_hi + 1):
        if x.lo <= -math.pi / 2 + 2 * math.pi * k <= x.hi:
            has_valley = True
        if x.lo <= math.pi / 2 + 2 * math.pi * k <= x.hi:
            has_peak = True
        if has_valley and has_peak:
            break

    new_lo = -1 if has_valley else min(math.sin(x.lo), math.sin(x.hi))
    new_hi = 1 if has_peak else max(math.sin(x.lo), math.sin(x.hi))

    return Interval(new_lo, new_hi)


def dist(a: Interval, b: Interval) -> float:
    return max(abs(a.lo - b.lo), abs(a.hi - b.hi))


def exact_range(f, X:Interval) -> Interval:
    N = 10001
    xs = np.linspace(X.lo, X.hi, N)
    ys = f(xs)

    i_min = np.argmin(ys)
    i_max = np.argmax(ys)

    new_lo = minimize_scalar(f, bounds=(xs[max(i_min - 1, 0)], xs[min(i_min + 1, N - 1)]), method="bounded").fun
    new_hi = -minimize_scalar(lambda x: -f(x), bounds=(xs[max(i_max - 1, 0)], xs[min(i_max + 1, N - 1)]), method="bounded").fun

    return Interval(min(ys.min(), new_lo), max(ys.max(), new_hi))


def cut(x: float, bound: "Interval") -> float:
    if x < bound.lo: return bound.lo
    elif x > bound.hi: return bound.hi
    
    return x


def intersect(a: "Interval", b: "Interval") -> "Interval":
    new_lo = max(a.lo, b.lo)
    new_hi = min(a.hi, b.hi)

    return Interval(new_lo, new_hi)


def l_const(df, X: Interval) -> float:
    df_bounds = exact_range(df, X)
    return max(abs(df_bounds.lo), abs(df_bounds.hi))


def lip_bound(F: Interval, L, X: Interval) -> bool:
    return F.rad() <= X.rad() * L


def contains(F: Interval, E: Interval) -> bool:
    eps = 1e-9
    return F.lo <= E.lo + eps and F.hi >= E.hi - eps


def print_row(name: str, F: Interval, E: Interval, X: Interval, L: float | None = None) -> None:
    lip_val = f"{lip_bound(F, L, X)}" if L is not None else "-"
    incl_val = f"{contains(F, E)}"
    print(
        f"{name:<25} | F: [{F.lo:8.3f}, {F.hi:8.3f}] | rad: {F.rad():7.3f} | dist: {dist(F, E):7.3f} | incl: {incl_val:<5} | lip: {lip_val}"
    )

def visualization(f, X:Interval, func_name: str) -> None:
    N = 300
    x_f = np.linspace(X.lo, X.hi, N)
    y_f = f(x_f)

    bounds = exact_range(f, X)
    y_min = bounds.lo
    y_max = bounds.hi

    plt.figure(figsize=(10, 6))

    plt.plot(x_f, y_f, label='$f(x)$', color='blue')
    plt.axhline(y_min, ls='--', linewidth=2, color='red', label=f'Min:{y_min:.2f}')
    plt.axhline(y_max, ls='--', linewidth=2, color='green', label=f'Max:{y_max:.2f}')

    plt.fill_between(x_f, y_min, y_max, color='gray', alpha=0.2)

    
    plt.xlabel('$x$')
    plt.ylabel('$f(x)$')
    plt.legend(loc='upper left', bbox_to_anchor=(1.05, 1), borderaxespad=0.)
    plt.grid()
    plt.tight_layout()

    script_dir = Path(__file__).resolve().parent
    save_path = script_dir.parent / "report" / "figures" / f"{func_name}.png"
    save_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches="tight")

    # plt.show()
    plt.close()


def main() -> None:
    run_f1()
    print()
    run_f2()


if __name__ == "__main__":
    main()