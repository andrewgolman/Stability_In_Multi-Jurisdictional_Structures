from DoubleAllocation import *
from numpy import linspace
from optimization import f, constraint
from scipy.optimize import minimize


def case_1():
    for i in range(1, 100):
        for j in range(i+1, 100):
            res = (Stability(0, None), 0)
            for d in linspace(0, 1, 1000):
                p = DoubleAllocation(i, j, d)
                st = p.trivial_stability()
                if st.value > res[0].value:
                    res = (st, d)
            LIM = 0.008
            if res[0].value > LIM:
                print(i, j, round(res[1], 4), res[0].value + 0.001)


def case_2():
    l = 29
    r = 38
    d = 0.022
    p = DoubleAllocation(l, r, d)
    print(p.true_stability(200))


def case_3():
    print(minimize(f, x0=(1.5, 0.5), method='L-BFGS-B', bounds=((1, 2), (0, 1))))

case_3()