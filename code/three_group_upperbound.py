from numpy import linspace
from time import time
from itertools import combinations, product
from statistics import median
import os
import sys
from utils import relative_cost_reduction, absolute_cost_reduction, costs
from partition import Group, make_group, Partition


PROBES = 11
EPS = 0.0000001


class TriPolarWorld:
    def __init__(self, cities):
        """cities: tuple:(size, position)"""
        self.cities = cities
        self.M = cities[1][0] / cities[0][0]
        self.R = cities[2][0] / cities[0][0]
        self.Dl = (cities[1][1] - cities[0][1]) / cities[0][0]
        self.Dr = (cities[2][1] - cities[1][1]) / cities[0][0]

        self.l = cities[0][0]
        self.m = cities[1][0]
        self.r = cities[2][0]

    def estimation_partitions(self):
        generators = [
            self.union(),
            self.federation(),
            self.left_union(),
            self.skip_union(),
            self.right_union(),
            self.all_undef(),
            self.left_undef(),
            self.right_undef(),
            self.skip_undef(),
        ]
        partitions = list()
        for gen in generators:
            partitions.extend(list(gen))
        return partitions

    def instability(self, partitions=None, verbose=False):
        if partitions is None:
            partitions = self.estimation_partitions()
        instability = 1.
        for partition in partitions:
            inst = partition.instability()
            if verbose and inst < 0.15:
                print([str(group) for group in partition.groups], inst)
            instability = min(instability, inst)
            if instability < EPS:
                break
        return instability

    def union(self):
        med_mid_ind = (self.M + 1 >= self.R)
        yield Partition([
                Group((1, self.M, self.R), (0, self.Dl, self.Dl + self.Dr), self.Dl + (0 if med_mid_ind else self.Dr))
        ])

    def federation(self):
        yield Partition([
            Group((1,), (0,), 0),
            Group((self.M,), (self.Dl,), self.Dl),
            Group((self.R,), (self.Dl + self.Dr,), self.Dl + self.Dr),
        ])

    def left_union(self):
        med_mid_ind = (self.M >= 1)
        yield Partition([
            Group((self.R,), (self.Dl + self.Dr,), self.Dl + self.Dr),
            Group((1, self.M), (0, self.Dl), self.Dl if med_mid_ind else 0),
        ])

    def right_union(self):
        med_mid_ind = (self.M >= self.R)
        yield Partition([
            Group((1,), (0,), 0),
            Group((self.M, self.R), (self.Dl, self.Dl + self.Dr), self.Dl + (0 if med_mid_ind else self.Dr)),
        ])

    def all_undef(self, step=PROBES):
        for med in linspace(0, 1, step):
            if 1 + self.M <= self.R:
                yield Partition([
                    Group((1, self.M, 1 + self.M), (0, self.Dl, self.Dl + self.Dr), self.Dl + self.Dr * med),
                    Group((self.R - self.M - 1,), (self.Dl + self.Dr,), self.Dl + self.Dr)
                ])
            elif self.M < self.R:
                yield Partition([
                    Group((self.R - self.M, self.M, self.R), (0, self.Dl, self.Dl + self.Dr), self.Dl + self.Dr * med),
                    Group((1 - self.R + self.M,), (0,), 0)
                ])
            elif self.M > self.R:
                yield Partition([
                    Group((1, self.R - 1, self.R), (0, self.Dl, self.Dl + self.Dr), self.Dl + self.Dr * med),
                    Group((self.M - self.R + 1,), (self.Dl,), self.Dl)
                ])

    def skip_union(self):
        left_med_ind = (1 >= self.R)
        yield Partition([
            Group((self.M,), (self.Dl,), self.Dl),
            Group((1, self.R), (0, self.Dl + self.Dr), 0 if left_med_ind else (self.Dl + self.Dr)),
        ])

    def skip_undef(self, step=PROBES):
        for med in linspace(0, 1, step):
            if 1 < self.R:
                yield Partition([
                    Group((self.M,), (self.Dl,), self.Dl),
                    Group((1, 1), (0, self.Dl + self.Dr), (self.Dl + self.Dr) * med),
                    Group((self.R - 1,), (self.Dl + self.Dr,), self.Dl + self.Dr),
                ])
            if 1 == self.R:
                yield Partition([
                    Group((self.M,), (self.Dl,), self.Dl),
                    Group((1, 1), (0, self.Dl + self.Dr), (self.Dl + self.Dr) * med),
                ])

    def left_undef(self, step=PROBES):
        for med in linspace(0, 1, step):
            if self.M > 1:
                yield Partition([
                    Group((self.R,), (self.Dl + self.Dr,), self.Dl + self.Dr),
                    Group((1, 1), (0, self.Dl), self.Dl * med),
                    Group((self.M - 1,), (self.Dl,), self.Dl),
                ])
                yield Partition([
                    Group((self.R, self.M - 1,), (self.Dl + self.Dr, self.Dl,), self.Dl + (self.Dr if self.R > self.M - 1 else 0)),
                    Group((1, 1), (0, self.Dl), self.Dl * med),
                ])
            if self.M < 1:
                yield Partition([
                    Group((self.R,), (self.Dl + self.Dr,), self.Dl + self.Dr),
                    Group((self.M, self.M), (0, self.Dl), self.Dl * med),
                    Group((1 - self.M,), (0,), 0),
                ])
                yield Partition([
                    Group((self.R, 1 - self.M), (self.Dl + self.Dr, 0,), self.Dl + self.Dr if self.R > 1 - self.M else 0),
                    Group((self.M, self.M), (0, self.Dl), self.Dl * med),
                ])
            if self.M == 1:
                yield Partition([
                    Group((self.R,), (self.Dl + self.Dr,), self.Dl + self.Dr),
                    Group((1, 1), (0, self.Dl), self.Dl * med),
                ])

    def right_undef(self, step=PROBES):
        for med in linspace(0, 1, step):
            if self.M > self.R:
                yield Partition([
                    Group((1,), (0,), 0),
                    Group((self.R, self.R), (self.Dl, self.Dl + self.Dr), self.Dl + self.Dr * med),
                    Group((self.M - self.R,), (self.Dl,), self.M),
                ])
                # print("GET IN")
                # print((1, self.M - self.R), (0, self.Dl), 0 if 1 > self.M else self.Dl)
                # print((self.R, self.R), (self.Dl, self.Dl + self.Dr), self.Dl + self.Dr * med)
                # print(Partition([
                #     Group((1, self.M - self.R), (0, self.Dl), 0 if 1 > self.M else self.Dl),
                #     Group((self.R, self.R), (self.Dl, self.Dl + self.Dr), self.Dl + self.Dr * med),
                # ]).instability())
                yield Partition([
                    Group((1, self.M - self.R), (0, self.Dl), 0 if 1 > self.M - self.R else self.Dl),
                    Group((self.R, self.R), (self.Dl, self.Dl + self.Dr), self.Dl + self.Dr * med),
                ])
            if self.M < self.R:
                yield Partition([
                    Group((1,), (0,), 0),
                    Group((self.M, self.M), (self.Dl, self.Dl + self.Dr), self.Dl + self.Dr * med),
                    Group((self.R - self.M,), (self.Dl + self.Dr,), self.Dl + self.Dr),
                ])
                yield Partition([
                    Group((1, self.R - self.M), (0, self.Dl + self.Dr), 0 if 1 > self.R - self.M else self.Dl + self.Dr),
                    Group((self.M, self.M), (self.Dl, self.Dl + self.Dr), self.Dl + self.Dr * med),
                ])
            if self.M == self.R:
                yield Partition([
                    Group((1,), (0,), 0),
                    Group((self.R, self.R), (self.Dl, self.Dl + self.Dr), self.Dl + self.Dr * med),
                ])

    def n_stability(self, n, verbose=False):
        # partitions = list([self.federation()])
        partitions = list()
        partitions.extend(list(self.federation()))
        for groups in n_partitions(n, self.l, self.m, self.r):
            partitions.extend(list(self.partition_by_groups(groups)))
        return self.instability(partitions, verbose=verbose)

    def partition_by_groups(self, groups):
        normalized_groups = list()
        for group in groups:
            normalized_groups.append(self.normalize_group(*group))
        # for normalized_groups in product(normalized_group_sets):
        yield Partition(normalized_groups)

    def normalize_group(self, l, m, r):
        if l > m + r:
            medians = [0]
        elif l == m + r:
            medians = [linspace(0, self.Dl, 3)[1]]
        elif r > l + m:
            medians = [self.Dl + self.Dr]
        elif r == l + m:
            medians = [linspace(self.Dl, self.Dl + self.Dr, 3)[1]]
        else:
            medians = [self.Dl]
        return Group((l / self.l, m / self.l, r / self.l), (0, self.Dl, self.Dl + self.Dr), medians[0])


def n_partitions(count, l, m, r):
    if count == 1:
        return [[(l, m, r)]] if l + m + r else list()
    partitions = list()
    for first_l in range(l + 1):
        for first_m in range(m + 1):
            for first_r in range(r + 1):
                first_group = [(first_l, first_m, first_r)] if first_l + first_m + first_r else list()
                for tail in n_partitions(count - 1, l - first_l, m - first_m, r - first_r):
                    partitions.append(first_group + tail)
    print(len(partitions))
    return partitions


def main():
    l = 10
    m = 9
    r = 10
    dl = 0.7
    dr = 0.7

    TriPolarWorld([(l, 0), (m, dl * l), (r, (dl + dr) * l)]).n_stability(2, verbose=True)


def test():
    classes = [
        (1, 0, 1),
        (1, 0.5, 1),
    ]
    assert(Partition(0).formation_desire_median_range(classes, 2, 0, 1) == 0.25)
    g1 = Group((1,), (0,), 0)
    g2 = Group((1,), (0.5,), 0.5)
    assert(abs(Partition([g1, g2]).instability() - 0.25) < 0.0001)

    g1 = Group((1,), (0,), 0)
    g2 = Group((1.3,), (0.64,), 0.64)
    print(Partition([g1, g2]).instability())


def estimation(lim):
    for M in linspace(0, 2, 101):
        for R in linspace(1, 3, 101):
            for Dl in linspace(0, 1, 101):
                    Dr = Dl
                # for Dr in linspace(0, 1, 21):
                    if M == 0 or R == 0 or Dl == 0 or Dr == 0:
                        continue
                    world = TriPolarWorld([(1, 0), (M, Dl), (R, Dl + Dr)])
                    instability = world.instability(verbose=False)
                    if instability > lim:
                        print(1, M, R, Dl, Dr, instability)
        print(M)


if __name__ == "__main__":
    estimation(0.02)
    # main()
    # test()
