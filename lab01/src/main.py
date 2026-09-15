import numpy as np

class IntervalMatrix:
    def __init__(self, mid: np.ndarray, rad: np.ndarray) -> None:
        self.mid = mid
        self.rad = rad 


    def lower(self) -> np.ndarray:
        return self.mid - self.rad

    
    def upper(self) -> np.ndarray:
        return self.mid + self.rad

if __name__ == "__main__":
    mid = np.array([[0.95, 1.00], [1.05, 1.00]])
    rad = np.array([[0.1, 0.0], [0.1, 0.0]])

    b = IntervalMatrix(mid, rad)
    print(b.lower())
    print(b.upper())