class Interval:
    def __init__ (self, lo: float, hi: float):
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


def main():
    interval = Interval(-5, 1)
    print(interval.mid())
    print(interval.rad())
    print(interval.wid())

if __name__ == "__main__":
    main()