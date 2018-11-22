from typing import List
from numpy import linspace
from time import time


class Stability:
    def __init__(self, value, data):
        self.value = round(value, 5)
        self.data = data


class Partition:
    def __init__(self, allocation, groups):
        self.left_costs_ = []
        self.right_costs_ = []
        for g in groups:
            left, right, median = g.data()
            self.left_costs_.extend([1 / (left+right) + median] * left)
            self.right_costs_.extend([1 / (left+right) + allocation.dist - median] * right)

    def left_costs(self) -> List[float]:
        return self.left_costs_

    def right_costs(self) -> List[float]:
        return self.right_costs_


class Group:
    def __init__(self, allocation, left, right, med=None):
        self.left_ = left
        self.right_ = right
        if left < right:
            self.median_ = allocation.dist
        elif left > right:
            self.median_ = 0
        elif med is None:
            self.median_ = allocation.dist / 2
        else:
            self.median_ = med

    def __str__(self):
        return self.left_, self.right_, self.median_

    def data(self):
        return self.left_, self.right_, self.median_


class DoubleAllocation:
    def __init__(self, left: int, right: int, dist: float, enable_absolute_costs=False):
        if left > right:
            left, right = right, left
        self.dist = dist
        self.left = left
        self.right = right
        self.left_agents = [0] * self.left
        self.right_agents = [dist] * self.right
        self.absolute_costs = enable_absolute_costs

    def to_the_segment(self, point: float) -> float:
        if point > self.dist:
            return self.dist
        if point < 0.:
            return 0.
        return point

    def costs(self, size, distance):
        return 1 / size + distance

    def delta(self, old, new):
        if self.absolute_costs:
            return old - new
        return (old-new)/old

    def stability_for_partition(self, partition: Partition):
        left_costs = list(reversed(sorted(partition.left_costs())))
        right_costs = list(reversed(sorted(partition.right_costs())))
        ans = 0
        for i in range(1, self.left + 1):  # pure left groups
            delta_costs_left = self.delta(left_costs[i-1], self.costs(i, 0))
            ans = max(ans, delta_costs_left)
        for i in range(1, self.right + 1):  # pure right groups
            delta_costs_right = self.delta(right_costs[i-1], self.costs(i, 0))
            ans = max(ans, delta_costs_right)
        for i in range(1, self.left + 1):  # undefined groups

            if not self.absolute_costs:
                transport_costs = 1. / 2 / i
                lc = left_costs[i-1]
                rc = right_costs[i-1]
                med = self.to_the_segment(((transport_costs + self.dist) * lc - transport_costs * rc) / (lc + rc))
            else:
                med = self.to_the_segment((left_costs[i - 1] - right_costs[i - 1] + self.dist) / 2)

            delta_costs_left = self.delta(left_costs[i-1], self.costs(2*i, med))
            delta_costs_right = self.delta(right_costs[i-1], self.costs(2*i, self.dist - med))
            ans = max(ans, min(delta_costs_left, delta_costs_right))

        for i in range(1, self.left + 1):  # left part
            for j in range(1, i):  # right part
                delta_costs_left = self.delta(left_costs[i-1], self.costs(i+j, 0))
                delta_costs_right = self.delta(right_costs[j-1], self.costs(i+j, self.dist))
                ans = max(ans, min(delta_costs_left, delta_costs_right))

        for j in range(1, self.right + 1):  # right part
            for i in range(1, min(j, self.left + 1)):  # left part
                delta_costs_left = self.delta(left_costs[i-1], self.costs(i+j, self.dist))
                delta_costs_right = self.delta(right_costs[j-1], self.costs(i+j, 0))
                ans = max(ans, min(delta_costs_left, delta_costs_right))

        return ans

    def federation_groups(self, left, right):
        return [Group(self, left, 0), Group(self, 0, right)]

    def unity_groups(self, left, right):
        return [Group(self, left, right)]

    def undefmax_groups(self, left, right, median=None):
        return [Group(self, left, left, median), Group(self, 0, right - left)]

    def federation(self):
        return Partition(self, self.federation_groups(self.left, self.right))

    def unity(self):
        return Partition(self, self.unity_groups(self.left, self.right))

    def undefmax(self):
        return Partition(self, self.undefmax_groups(self.left, self.right))

    def one_middle_group_partitions(self):
        ans = []
        for i in range(1, self.left):
            r = self.right - i
            l = self.left - i
            ans.append(Partition(self, self.federation_groups(l, r) + [Group(self, i, i)]))
            ans.append(Partition(self, self.unity_groups(l, r) + [Group(self, i, i)]))
            # ans.append(Partition(self, self.undefmax_groups(l, r) + [Group(self, i, i)]))
        ans.append(self.federation())
        ans.append(self.unity())
        ans.append(self.undefmax())
        return ans

    def trivial_stability(self):
        a = self.stability_for_partition(self.federation())
        b = self.stability_for_partition(self.unity())
        c = self.stability_for_partition(self.undefmax())
        stability = min(a, b, c)
        data = (int(1000*a), int(1000*b), int(1000*c))
        return Stability(stability, data)

    def stability_for_partitions(self):
        partitions = self.one_middle_group_partitions()
        ans = (1, None)
        stat = []
        for p in partitions:
            cur = self.stability_for_partition(p)
            stat.append(cur)
            if cur < ans[0]:
                ans = (cur, p)
        return Stability(ans[0], ans[1])

    def true_stability(self, probes, verbose=False, only_boundary_cases=False):
        """
        # constructor usage: partition(self, allocation, groups):
        # constructor usage: group(self, allocation, left, right, med=None)
        """
        ans = 1
        t = time()
        a_range = range(self.left) if not only_boundary_cases else [0, self.left]
        for a in a_range:
            if verbose:
                print("Starting groups with {} med group. Current eps={}.".format(a, ans))
            for m in linspace(0, self.dist, probes):
                for l in range(self.left - a):
                    groups = list()
                    if a:
                        groups.append(Group(self, a, a, m))
                    groups.append(Group(self, l, self.right - a))
                    if l+a != self.left:
                        groups.append(Group(self, self.left - l - a, 0))
                    partition = Partition(self, groups)
                    next_val = self.stability_for_partition(partition)
                    if next_val < ans:
                        ans = next_val
                        if verbose:
                            print("l", a, m, l, ans)
                for r in range(self.right - a):
                    groups = list()
                    if a:
                        groups.append(Group(self, a, a, m))
                    if a != self.left or r:
                        groups.append(Group(self, self.left - a, r))
                    if a+r != self.right:
                        groups.append(Group(self, 0, self.right - r - a))
                    partition = Partition(self, groups)
                    next_val = self.stability_for_partition(partition)
                    if next_val < ans:
                        ans = next_val
                        if verbose:
                            print("r", a, m, r, ans)
                if a == 0:
                    break
            if verbose:
                print("{} seconds elapsed".format(time() - t))
        return ans


if __name__ == "__main__":
    l = 56
    r = 73
    d = 0.6363245 / 56
    p = DoubleAllocation(l, r, d)
    print(p.stability_for_partition(p.federation()))
    print(p.stability_for_partition(p.unity()))
    print(p.stability_for_partition(p.undefmax()))
