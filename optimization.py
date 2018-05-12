from scipy.optimize import minimize
import numpy as np


def delta_by_costs(old, new):
    return 1 - new/old


def f2(k, d):  # UNION
    return delta_by_costs(1/(1+k) + d, 1)


def f3(k, d):  # FEDERATION + UNDEF
    eta = ((k-1) / 2 + k * d) / (1+k)
    # print(eta)
    d1 = delta_by_costs(1, 1/2 + eta)
    d2 = delta_by_costs(1 / k, 1/2 + d - eta)
    return min(d1, d2, 0)


def f4(k, d):  # FEDERATION + RIGHT
    # print(k, d)
    d1 = delta_by_costs(1, 1 / (1+k) + d)
    d2 = delta_by_costs(1 / k, 1 / (1+k))
    return min(d1, d2, 0)


def f5(k, d):  # MAXUNDEF
    m = d/2
    d1 = delta_by_costs(1 / 2 + m, 1 / (1+k) + d)
    d2 = delta_by_costs(1 / 2 + d - m, 1 / (1+k))
    return min(d1, d2, 0)


def f(ar):
    k, d = tuple(ar)
    return min(f2(k, d), max(f3(k, d), f4(k, d)), f5(k, d))

# constraint = LinearConstraint(np.ones((2,)), lb=np.array([[1], [0]]), ub=np.array([[2], [1]]))


def constraint(ar):
    a = tuple(ar)
    return not (1 < a[0] < 2 and 0 < a[1] < 1)

# print(minimize(f, x0=(1.5, 0.5), method='L-BFGS-B', bounds=((1, 2), (0, 1))))
