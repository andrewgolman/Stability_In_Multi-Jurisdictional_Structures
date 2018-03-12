from typing import List

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
    def __init__(self, allocation, left, right, med=-1):
        self.left_ = left
        self.right_ = right
        if left < right:
            self.median_ = allocation.dist
        elif left > right:
            self.median_ = 0
        elif med == -1:
            self.median_ = allocation.dist / 2
        else:
            self.median_ = med

    def data(self):
        return self.left_, self.right_, self.median_


class DoubleAllocation:
    def __init__(self, left: int, right: int, dist: float):
        if left > right:
            left, right = right, left
        self.dist = dist
        self.left = left
        self.right = right
        self.left_agents = [0] * self.left
        self.right_agents = [dist] * self.right

    def to_the_segment(self, point: float) -> float:
        if point > self.dist:
            return self.dist
        if point < 0:
            return 0
        return point

    def costs(self, size, distance):
        return 1 / size + distance

    def delta(self, old, new):
        return (old-new)/old

    def stability_for_partition(self, partition: Partition):
        # print(partition.left_costs_)
        # print(partition.left_costs_.sort())
        # print(list(reversed(sorted(partition.left_costs()))))
        left_costs = list(reversed(sorted(partition.left_costs())))
        right_costs = list(reversed(sorted(partition.right_costs())))
        ans = 0
        for i in range(self.left):
            delta_costs_left = self.delta(left_costs[i], self.costs(i+1, 0))
            ans = max(ans, delta_costs_left)
        for i in range(self.right):
            delta_costs_right = self.delta(right_costs[i], self.costs(i+1, 0))
            ans = max(ans, delta_costs_right)
        for i in range(self.left):
            med = self.to_the_segment((left_costs[i] - right_costs[i] + self.dist) / 2)
            # delta_costs_left = left_costs[i] - 1 / 2 / (i+1) - med
            # delta_costs_right = right_costs[i] - 1 / 2 / (i+1) - self.dist + med
            delta_costs_left = self.delta(left_costs[i], self.costs(2*(i+1), med))
            delta_costs_right = self.delta(right_costs[i], self.costs(2*(i+1), self.dist - med))
            ans = max(ans, min(delta_costs_left, delta_costs_right))

        for i in range(1, self.left): # TODO to be optimized
            for j in range(i):
                # delta_costs_left = left_costs[i] - 1 / (i+j+2)
                # delta_costs_right = right_costs[j] - 1 / (i+j+2) - self.dist
                delta_costs_left = self.delta(left_costs[i], self.costs(i+j+2, 0))
                delta_costs_right = self.delta(right_costs[i], self.costs(i+j+2, self.dist))
                ans = max(ans, min(delta_costs_left, delta_costs_right))

        for j in range(1, self.right):  # TODO to be optimized
            for i in range(min(j, self.left)):
                delta_costs_left = self.delta(left_costs[i], self.costs(i + j + 2, self.dist))
                delta_costs_right = self.delta(right_costs[i], self.costs(i + j + 2, 0))
                ans = max(ans, min(delta_costs_left, delta_costs_right))

        return ans

    def federation(self):
        return Partition(self, [Group(self, self.left, 0), Group(self, 0, self.right)])

    def unity(self):
        return Partition(self, [Group(self, self.left, self.right)])

    def dualmax(self):
        return Partition(self, [Group(self, self.left, self.left), Group(self, 0, self.right - self.left)])

    def is_trivially_stable(self):
        a = self.stability_for_partition(self.federation())
        b = self.stability_for_partition(self.unity())
        c = self.stability_for_partition(self.dualmax())
        return min(a, b, c)

