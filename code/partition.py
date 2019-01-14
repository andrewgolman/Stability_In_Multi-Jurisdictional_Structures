from numpy import linspace
from itertools import combinations
from utils import relative_cost_reduction, absolute_cost_reduction, costs

cost_reduction = relative_cost_reduction


class Group:
    def __init__(self, sizes, points, median):
        self.sizes = sizes
        self.points = points
        self.median = median

    def data(self):
        return self.sizes, self.points, self.median

    def size(self):
        return sum(self.sizes)

    def __str__(self):
        return f"Group: s:{self.sizes}, pos:{self.points}, med:{self.median}"


def make_group(classes, median):
    sizes = [cl[0] for cl in classes]
    points = [cl[1] for cl in classes]
    return Group(sizes, points, median)


class Partition:
    def __init__(self, groups):
        """group: Group"""
        self.groups = groups

    def subgroups(self):
        """Triples: (size, position, costs), sorted by position"""
        subgroups = list()
        for group in self.groups:
            for size, point in zip(group.sizes, group.points):
                if size:
                    subgroups.append((size, point, costs(group.size(), point - group.median)))
        return sorted(subgroups, key=lambda i: i[1])

    def factorclass_combinations(self):
        """All factorclass subsets"""
        subgroups = self.subgroups()
        for n in range(1, len(subgroups) + 1):
            for subset in combinations(subgroups, n):
                yield subset

    def formation_size(self, classes, median):
        left = 0
        right = 0
        mid = 0
        for cl in classes:
            if cl[1] < median:
                left += cl[0]
            elif cl[1] == median:
                mid += cl[0]
            else:
                right += cl[0]
        if left > right:
            left, right = right, left
        if left + mid < right:
            right = left + mid

        return left + mid + right

    def formation_desire(self, classes, size, point):
        desire = 1.
        for cl in classes:
            desire = min(desire, cost_reduction(cl[2], costs(size, cl[1], point)))
        return desire

    def coefs(self, cl, size, border):
        if cl[1] <= border:
            k = -1. / cl[2]
            d = 1 + cl[1] / cl[2] - 1. / size / cl[2]
        else:
            k = 1. / cl[2]
            d = 1 - cl[1] / cl[2] - 1. / size / cl[2]
        return k, d

    def max_min_med(self, k1, b1, k2, b2, lpoint, rpoint):
        if k1 == k2:
            if b1 > b2:
                k1, b1, k2, b2 = k2, b2, k1, b1
            if k1 > 0:
                return lpoint
            else:
                return rpoint

        intersection = (b1 - b2) / (k2 - k1)
        if intersection < lpoint:
            return lpoint
        elif intersection > rpoint:
            return rpoint
        else:
            return intersection

    def point_lies_upper(self, k, b, x, y):
        return k * x + b < y

    def formation_desire_median_range(self, classes, size, lpoint, rpoint):
        medians = [lpoint, rpoint]
        for cl in classes:
            k1, b1 = self.coefs(cl, size, lpoint)
            for other_cl in classes:
                if other_cl != cl:
                    k2, b2 = self.coefs(other_cl, size, lpoint)
                    medians.append(self.max_min_med(k1, b1, k2, b2, lpoint, rpoint))
        desire = 0.
        for med in medians:
            next_desire = 1.
            for cl in classes:
                next_desire = min(next_desire, cost_reduction(cl[2], costs(size, cl[1], med)))
            desire = max(desire, next_desire)
        return desire

    def subset_formation_desire(self, classes, extended_result=False):
        optimum = 0.
        opt_point = None
        opt_size = 0.
        points = list(set([i[1] for i in classes]))
        for point in points:
            size = self.formation_size(classes, point)
            desire = self.formation_desire(classes, size, point)
            if desire > optimum:
                optimum = desire
                opt_point = point
                opt_size = size

        for i in range(len(points) - 1):
            size = self.formation_size(classes, (points[i] + points[i+1]) / 2)
            desire = self.formation_desire_median_range(classes, size, points[i], points[i+1])
            if desire > optimum:
                optimum = desire
                opt_point = (points[i] + points[i+1]) / 2
                opt_size = size

        if extended_result:
            return optimum, opt_size, opt_point
        return optimum

    def instability(self):
        optimum = 0.
        for factorclass_subset in self.factorclass_combinations():
            desire = self.subset_formation_desire(factorclass_subset)
            if desire > optimum:
                optimum = desire
        return optimum

    def threats(self):
        for factorclass_subset in self.factorclass_combinations():
            desire, size, med = self.subset_formation_desire(factorclass_subset, extended_result=True)
            if desire > 0.001:
                print("THREAT")
                print("Classes:")
                for cl in factorclass_subset:
                    print(f"Size: {cl[0]}, pos: {cl[1]}, costs: {cl[2]}")
                print(f"Desire: {desire}")
                print(f"Size: {size}")
                print(f"Median: {med}")
