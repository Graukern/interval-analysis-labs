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


def main() -> None:
    print(Interval(-1.30, -0.70).mag())
    print(Interval(2, 5).inner_sub(Interval(-0.5, 0.5)))
    print(Interval(1, 2).inner_sub(Interval(-0.5, 0.5)))
    print(Interval(0.65, 1.25) * (-1.597))
    print()

    A = [
    [Interval( 1,  2), Interval( 3,  4)],
    [Interval( 5,  6), Interval( 7,  8)],
    [Interval( 9, 10), Interval(11, 12)],
    ]
    b = [Interval(1, 1), Interval(2, 2), Interval(3, 3)]

    system = IntervalSystem(A, b)
    print(system.m, system.n)
    print()

if __name__ == "__main__":
    main()