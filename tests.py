from DoubleAllocation import *
from numpy import linspace
from utils import *
LIM = 0.01

def test_non_trivial():
    pairs = get_pairs()
    for i, j in pairs[:10]:
        res = (Stability(1, None), 0)
        for d in linspace(0, 0.4, 21):
            p = DoubleAllocation(i, j, d)
            st = p.stability_for_partitions()
            if st.value < res[0].value:
                res = (st, d)
        if res[0].value > LIM:
            # print(i, j, res[1], res[0].value, res[0].data, file=file)
            print(i, j, res[1], res[0].value, res[0].data)


def analyze():
    pairs = get_pairs()
    for i, j in pairs:
        res = (Stability(0, None), 0)
        for d in linspace(0, 0.1, 101):
            p = DoubleAllocation(i, j, d)
            st = p.trivial_stability()
            if st.value > res[0].value:
                res = (st, d)
        if res[0].value > LIM:
            # print(i, j, res[1], res[0].value, res[0].data, file=file)
            print(i, j, res[1], res[0].value, res[0].data)


def test_trivial_all_to_n(n, start=1, start_all=1):
    # file = open("2coalitionsDIV.txt", "w")
    for i in range(start_all, n):
        if not i % 10:
            print(i)
        for j in range(max(start, i+1), min(n, int(i*1.63)+1)):
            res = (Stability(0, None), 0)
            for d in linspace(0, 1, 1000):
                p = DoubleAllocation(i, j, d)
                st = p.trivial_stability()
                if st.value > res[0].value:
                    res = (st, d)
            if res[0].value > LIM:
                # print(i, j, res[1], res[0].value, res[0].data, file=file)
                print(i, j, round(res[1], 4), res[0].value)


def test_trivial_one_case(i, j, d):
    p = DoubleAllocation(i, j, d)
    st = p.trivial_stability()
    res = (st, d)
    print(res[0].value)
    print(i, j, round(res[1], 8), res[0].value)


def test_trivial_agents(n, m, create_file=False):
    if create_file:
        file = open("2coalitions_"+str(n)+"_"+str(m)+".txt", "w")
    maxst = 0
    for d in linspace(0, 1, 2001):
        p = DoubleAllocation(n, m, d)
        st = p.trivial_stability()
        if create_file and st >= LIM:
            print(d, st, file=file)
        maxst = max(st, maxst)
    print(n, m, maxst)


def simple_test():
    print(DoubleAllocation(2, 3, 14 / 45).trivial_stability().value)
    # assert(abs(DoubleAllocation(2, 3, 14 / 45).is_trivially_stable() - 1/90) < 0.0001)


def test_useless_lowerbound_theorem():
    data = get_data()
    n = 0
    for i in data:
        l, r, d, eps = tuple(i)
        if l > (4 / (1-eps) - 2) / d:
            print(i, (4 / (1 - eps) - 2) / d)
            n += 1
    if not n:
        print("useless")



def lowerbound_costs_city(n, eps):
    return 1 / n / (1 - eps)


def lowerbound_costs_undefined(n, eps, d):
    return (1 / 2 / n + d) / (1 - eps)


def test_lowerbound_costs():
    l, r, d, eps = 3, 4, 0.212, 0.057
    for i in range(1, r+1):
        print(round(1 / lowerbound_costs_city(i, eps)))
    print()
    for i in range(1, l+1):
        print(lowerbound_costs_undefined(i, eps, d/2))


def test_new_induction():
    data = get_data()
    for i in data:
        l, r, d, eps = tuple(i)
        if 1/2.95 * (1 + 2 * l * d) >= 1 - eps:
            print(l, r, d, eps)
            print(1 / 2 - eps, l * d)
            print(int(l / ((1 / 4 - eps / 2) / d)))
        # else:
        #     print(l, r, d, eps)
        #     print((1 / 4 - eps / 2) / d, l / 2)


def test_true_stability():
    l = 29
    r = 38
    d = 0.022
    p = DoubleAllocation(l, r, d)
    print(p.true_stability(200))


def main():
    # test_trivial_all_to_n(100, start=51, start_all=35)
    # test_new_induction()
    # test_trivial_one_case(1000, 1307, 0.64399554113739/1000)
    # test_true_stability()
    test_trivial_all_to_n(100)
    # simple_test()

main()

# (0.06865687401542786, 1.306868686868687, 0.64399554113739832)

# 0.05507279693486589
