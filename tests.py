from DoubleAllocation import *
from numpy import linspace
LIM = 0.0002


def test_trivial_all_to_n(n):
    file = open("2coalitionsDIV.txt", "w")
    for i in range(1, n):
        for j in range(i+1, n):
            res = (0, 0)
            for d in linspace(0, 1, 501):
                p = DoubleAllocation(i, j, d)
                st = p.is_trivially_stable()
                if st > res[0]:
                    res = (st, d)
            if res[0] > LIM:
                print(i, j, res[1], res[0], file=file)
                print(i, j, res[1], res[0])


def test_trivial_agents(n, m, create_file=False):
    if create_file:
        file = open("2coalitions_"+str(n)+"_"+str(m)+".txt", "w")
    maxst = 0
    for d in linspace(0, 1, 2001):
        p = DoubleAllocation(n, m, d)
        st = p.is_trivially_stable()
        if create_file and st >= LIM:
            print(d, st, file=file)
        maxst = max(st, maxst)
    print(n, m, maxst)


def simple_test():
    print(DoubleAllocation(2, 3, 14 / 45).is_trivially_stable())
    # assert(abs(DoubleAllocation(2, 3, 14 / 45).is_trivially_stable() - 1/90) < 0.0001)


def main():
    simple_test()

main()
