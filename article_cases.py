from DoubleAllocation import *
from numpy import linspace
from upperbound071theorem import upperbound071_function


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


def case_2(probes=2000):
    l = 56
    r = 73
    d = 0.6363245 / 56
    p = DoubleAllocation(l, r, d)
    print(p.true_stability(probes=probes, verbose=True))


def case_3(k_space, d_probes=101):
    data = 0, 0, 0
    for k in k_space:
        print(f"done with k={k}")
        for d in linspace(k / (1 + k), 1 / k, d_probes):
            next = upperbound071_function((k, d))
            if next > data[0]:
                data = next, k, d
    print("result:", data)


def case_4(space, probes=1000):
    for d in space:
        p = DoubleAllocation(3, 4, d, enable_absolute_costs=True)
        val = p.true_stability(probes=probes)
        if val > 0.001:
            print(d, val)


def case_5(space, probes=1000):
    for d in space:
        p = DoubleAllocation(4, 5, d, enable_absolute_costs=True)
        val = p.true_stability(probes=probes)
        if val > 0.001:
            print(d, val)


# be careful, this may take up to...
# case_1()  # a few hours, change LIM to see the progress or see the final results in the CASE_ABS.TXT
case_2()  # 15 minutes
# case_3(linspace(1, 1.62, 101), 101)  # 15 minutes
# case_4(linspace(0.208, 0.209, 51))  # a few seconds
# case_5(linspace(0.1749, 0.1751, 11))  # a few seconds
