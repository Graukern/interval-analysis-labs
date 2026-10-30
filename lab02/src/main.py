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
        new_lo = self.lo + other.lo
        new_hi = self.hi + other.hi
        return Interval(new_lo, new_hi)


    def __sub__(self, other: "Interval") -> "Interval":
        new_lo = self.lo - other.hi
        new_hi = self.hi - other.lo
        return Interval(new_lo, new_hi)

    
    def __repr__(self) -> str:
        return f"[{self.lo}, {self.hi}]"

    
def main():
    a = Interval(1, 2)
    b = Interval(3, 5)

    print(a + b)
    print(a - b)


if __name__ == "__main__":
    main()