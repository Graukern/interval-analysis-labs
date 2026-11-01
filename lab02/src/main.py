import math
from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt
from scipy.optimize import minimize_scalar


def f1(x: float) -> float:
    return x ** 3 - 3 * x ** 2 + 2


def f2(x: float) -> float:
    return x ** 3 * np.cos(x) 


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


def main():
    a = Interval(-5, 1)
    b = Interval(-1, 2)
    c = Interval(0, 3)

    print(a ** 3)
    print(b ** 2)
    print(c ** 3)

    print(a ** 0)
    print(b ** 1)
    


if __name__ == "__main__":
    main()