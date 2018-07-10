from utils import non_negative
from numpy import linspace


def delta_by_costs(old, new):
    return 1 - new/old

# f_i - i-th system from the article

@non_negative
def f2(k, d):  # UNION
    return delta_by_costs(1/(1+k) + d, 1)


@non_negative
def f3(k, d):  # FEDERATION + m(S)=undef
    eta = ((k-1) / 2 + k * d) / (1+k)
    d1 = delta_by_costs(1, 1/2 + eta)
    d2 = delta_by_costs(1 / k, 1/2 + d - eta)
    return min(d1, d2)


@non_negative
def f3two(k, d, a):  # LEFT FEDERATION + m(S)=undef
    theta = min(1, k - a)
    eta = ((k-1-2*a) / (2*theta) + (k-a) * d) / (1+k)
    d1 = delta_by_costs(1 / (1 + a), 1 / (2 * theta) + eta)
    d2 = delta_by_costs(1 / (k - a), 1 / (2 * theta) + d - eta)
    return min(d1, d2)


@non_negative
def f3three(k, d, a):  # LEFT FEDERATION + m(S)=undef
    etas = list()
    etas.append(((k-1-2*a) / 2 + (k-a) * d) / (1+k))
    etas.append(((d+1/2) * a / (1 + d * a) + (1+a) / 2) / (1 + a + a / (1 + d * a)))
    etas.append(1/2 + d)
    ans = list()
    for eta in etas:
        d1 = delta_by_costs(1 / (1 + a), 1 / 2 + eta)
        d2 = delta_by_costs(1 / (k - a), 1 / 2 + d - eta)
        d3 = delta_by_costs(1 / (1 + a) + d, 1 / 2 + d - eta)
        ans.append(min(d1, d2, d3))
    return max(ans)


@non_negative
def f4(k, d):  # FEDERATION + m(S)=right
    d1 = delta_by_costs(1, 1 / (1+k) + d)
    d2 = delta_by_costs(1 / k, 1 / (1+k))
    return min(d1, d2)


@non_negative
def f4upd(k, d, a):  # FEDERATION + m(S)=right
    d1 = delta_by_costs(1 / (1 + a), 1 / (1+k) + d)
    d2 = delta_by_costs(1 / (k - a), 1 / (1+k))
    d3 = delta_by_costs(1 / (1 + a) + d, 1 / (1+k))
    return min(d1, d2, d3)


@non_negative
def f4right(k, d, a):  # FEDERATION + m(S)=right
    d2 = delta_by_costs(1 / (k - a), 1 / k)
    d3 = delta_by_costs(1 / (1 + a) + d, 1 / k)
    d3solo = delta_by_costs(1 / (1 + a) + d, 1 / a)
    return max(min(d2, d3), d3solo)


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


def f(ar):
    k, d, step = tuple(ar)
    union = f2(k, d)
    maxundef = max(f5(k, d), f6(k, d), f7(k, d))
    oldfed = max(f3(k, d), f4(k, d))
    ans = min(union, maxundef, oldfed)
    # for a in linspace(0, 1, step):
    #     if 0 < a < 1:
    #         newfed = max(f4upd(k, d, a), f4right(k, d, a), f3three(k, d, a), f3two(k, d, a))
    #         ans = min(ans, newfed)
    return ans
