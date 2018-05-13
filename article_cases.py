from DoubleAllocation import *
from numpy import linspace
from optimization import f


def case_1():
    for i in range(1, 100):
        for j in range(i+1, 100):
            res = (Stability(0, None), 0)
            for d in linspace(0, 1, 1000):
                p = DoubleAllocation(i, j, d, enable_absolute_costs=True)
                st = p.trivial_stability()
                if st.value > res[0].value:
                    res = (st, d)
            LIM = 0.008
            if res[0].value + 0.001 > LIM:
                print("L={}, R={}, d={}, eps <= {}".format(i, j, round(res[1], 4), res[0].value + 0.001))


def case_2():
    l = 29
    r = 38
    d = 0.022
    p = DoubleAllocation(l, r, d)
    print(p.true_stability(200))


def case_3():
    data = 0, 0, 0
    for k in linspace(1, 1.62, 10000):
        for d in linspace(k / (1 + k), 1 / k, 10000):
            next = f((k, d))
            if next > data[0]:
                data = next, k, d
    print(data)


# be careful, this may take up to...
# case_1() # a few hours, change LIM to see the progress or see the final results in the CASE_ABS.TXT
# case_2() # 15 minutes
# case_3() # 15 minutes
