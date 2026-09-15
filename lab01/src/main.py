import numpy as np
from scipy.optimize import linprog

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

    def lp(self) -> bool:
        M1 = self.mid - self.rad
        M2 = -self.mid - self.rad

        result = linprog(c=[0,0], A_eq=[[1, 1]], b_eq=[1], A_ub=np.vstack([M1, M2]), b_ub=np.zeros(4), bounds=[(0, None), (0, None)])   
        return(result.success)



if __name__ == "__main__":
    mid = np.array([[1, 1], [1, -1]])

    rad_1 = np.array([[1, 1], [1, 1]])
    print(IntervalMatrix(mid, rad_1).lp())   

    rad_05 = np.array([[0.5, 0.5], [0.5, 0.5]])
    print(IntervalMatrix(mid, rad_05).lp())   