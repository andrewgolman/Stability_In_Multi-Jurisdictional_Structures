from utils import non_negative


def delta_by_costs(old, new):
    return 1 - new/old


""" fi corresponds to the i-th system from the article """


@non_negative
def f2(k, d):  # UNION
    return delta_by_costs(1/(1+k) + d, 1)


@non_negative
def f3(k, d):  # FEDERATION + m(S)=undef
    eta = ((k-1) / 2 + k * d) / (1+k)
    # print(eta)
    d1 = delta_by_costs(1, 1/2 + eta)
    d2 = delta_by_costs(1 / k, 1/2 + d - eta)
    return min(d1, d2)


@non_negative
def f4(k, d):  # FEDERATION + m(S)=right
    d1 = delta_by_costs(1, 1 / (1+k) + d)
    d2 = delta_by_costs(1 / k, 1 / (1+k))
    return min(d1, d2)


@non_negative
def f5(k, d):  # MAXUNDEF + S=left agents
    m = d / 2
    return delta_by_costs(1 / 2 + m, 1 / k)


@non_negative
def f6(k, d):  # MAXUNDEF + S=all agents
    m = d/2
    d1 = delta_by_costs(1 / 2 + m, 1 / (1+k) + d)
    d2 = delta_by_costs(1 / 2 + d - m, 1 / (1+k))
    d3 = delta_by_costs(1/2 + d - m, 1/k)
    d4 = delta_by_costs(1/2 + m, 1/k)
    return max(min(d1, d2), d3, d4)


@non_negative
def f7(k, d):  # MAXUNDEF + S=right agents
    m = d / 2
    d1 = delta_by_costs(1 / 2 + d - m, 1 / k)
    d2 = 1 / k
    return min(d1, d2)


def upperbound071_function(ar):
    k, d = tuple(ar)
    return min(f2(k, d), max(f3(k, d), f4(k, d)), max(f5(k, d), f6(k, d), f7(k, d)))
