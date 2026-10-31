import math

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

    
def main():
    a = Interval(2, 3)
    b = Interval(1, 5)
    c = Interval(-1, 8)

    print(dist(a, b))
    print(dist(b, c))
    print(dist(a, c))

    
if __name__ == "__main__":
    main()