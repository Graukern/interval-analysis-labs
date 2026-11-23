import numpy as np
from matplotlib import pyplot as plt


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

        
    def __repr__(self) -> str:
        return f"[{self.lo}, {self.hi}]"


    def mag(self) -> float:
        return max(abs(self.lo), abs(self.hi))


    def inner_sub(self, other: "Interval") -> "Interval":
        if not isinstance(other, Interval): 
            other = Interval(other, other)
        new_lo = self.lo - other.lo
        new_hi = self.hi - other.hi
        return Interval(new_lo, new_hi)


class IntervalSystem:
    def __init__(self, A: list[list[Interval]], b: list[Interval]):
        if len(A) != len(b):
            raise ValueError("Размеры матрицы A и вектора b не совпадают")
        self.A = A
        self.b = b


    @property
    def m(self) -> int:
        return len(self.A)


    @property
    def n(self) -> int:
        return len(self.A[0])


    def __repr__(self) -> str:
        return "\n".join(
            f"{row!r} | {bi!r}" for row, bi in zip(self.A, self.b)
        )


    def tol(self, x: list[float]) -> float:
        if len(x) != self.n:
            raise ValueError("Число координат x должно совпадать с числом столбцов A")

        margins = []
        for row, bi in zip(self.A, self.b):
            y = Interval(0, 0)
            for aij, xj in zip(row, x):
                y = y + aij * xj

            margins.append(bi.rad() - (bi.mid() - y).mag())

        return min(margins)


def main() -> None:
    A = [
        [Interval( 0.65,  1.25), Interval(-1.30, -0.70)],
        [Interval( 0.75,  1.35), Interval(-1.24, -0.68)],
        [Interval( 0.80,  1.40), Interval(-1.36, -0.76)],
        [Interval(-0.30,  0.30), Interval(-1.18, -0.62)],
    ]

    b = [
        Interval(2.80, 2.90),
        Interval(2.90, 3.00),
        Interval(2.95, 3.05),
        Interval(1.85, 1.95),
    ]

    system_1 = IntervalSystem(A[:2], b[:2])
    system_2 = IntervalSystem(A[:3], b[:3])
    system_3 = IntervalSystem(A[:4], b[:4])

    print("--- A1, b1 (2 строки) ---")
    print(system_1)

    print("\n--- A2, b2 (3 строки) ---")
    print(system_2)

    print("\n--- A3, b3 (4 строки) ---")
    print(system_3)


    print(system_1.tol([0.0, 0.0]))
if __name__ == "__main__":
    main()