from numpy import linspace
from time import time
from utils import relative_cost_reduction, absolute_cost_reduction

ITERATIONS = 101


def world_instability(k, d):
    min_eps_partition = 1.
    a_res = ()
    for a in linspace(0., 1., ITERATIONS):
        groups = [(1., a, 0.)]
        if k > a:
            groups.append((0., k-a, d))
        next_instability = groups_instability(groups, d)
        if next_instability < min_eps_partition:
            min_eps_partition = next_instability
            if a == 0:
                a_res = (a, "F")
            else:
                a_res = (a, int(a * 100))
    for a in linspace(0., 1., ITERATIONS):
        groups = [(a, k, d)]
        if a < 1.:
            groups.append((1.-a, 0., 0.))
        next_instability = groups_instability(groups, d)
        if next_instability < min_eps_partition:
            min_eps_partition = next_instability
            if a < 1:
                a_res = (a, "R")
            else:
                a_res = (a, "U")
    for b in linspace(0., min(d, 1.), ITERATIONS):
        groups = [(1., 1., b)]
        if k > 1:
            groups.append((0., k-1., d))
        next_instability = groups_instability(groups, d)
        if next_instability < min_eps_partition:
            min_eps_partition = next_instability
            a_res = (b, "M")
    return min_eps_partition, a_res


def groups_instability(groups, d):
    left_groups = list()
    right_groups = list()
    for left, right, median in groups:
        left_costs = 1. / (left + right) + median
        right_costs = 1. / (left + right) + d - median
        if left:
            left_groups.append((left, left_costs))
        if right:
            right_groups.append((right, right_costs))
    biggest_desire = 0.
    biggest_desire = max(biggest_desire, max_side_group_desire(left_groups, right_groups, d))
    biggest_desire = max(biggest_desire, max_side_group_desire(right_groups, left_groups, d, reversed=True))
    biggest_desire = max(biggest_desire, max_undef_group_desire(left_groups, right_groups, d))
    return biggest_desire


def optimize_costs(size, left_costs, right_costs, d):
    transport_costs = 1. / size
    # equation for a new median: (transport_costs + dist) / left_costs = (transport_costs + d - dist) / right_costs
    new_median = ((transport_costs + d) * left_costs - transport_costs * right_costs) / (left_costs + right_costs)
    if new_median < 0.:
        new_median = 0.
    if new_median > d:
        new_median = d
    new_left_costs = transport_costs + new_median
    new_right_costs = transport_costs + d - new_median
    return min(cost_reduction(left_costs, new_left_costs), cost_reduction(right_costs, new_right_costs))


def max_undef_group_desire(left_groups, right_groups, d):
    if not left_groups or not right_groups:
        return 0.

    max_desire = 0.

    if len(right_groups) < len(left_groups):
        left_groups, right_groups = right_groups, left_groups
    # now it's 1-1 or 1-2

    if len(right_groups) >= 1:
        size = min(left_groups[0][0], right_groups[0][0]) * 2
        new_desire = optimize_costs(size, left_groups[0][1], right_groups[0][1], d)
        max_desire = max(max_desire, new_desire)

    if len(right_groups) == 2:
        size = min(left_groups[0][0], right_groups[1][0]) * 2
        new_desire = optimize_costs(size, left_groups[0][1], right_groups[1][1], d)
        max_desire = max(max_desire, new_desire)

        size = min(left_groups[0][0], right_groups[0][0] + right_groups[1][0]) * 2
        new_desire = optimize_costs(size, left_groups[0][1], min(right_groups[0][1], right_groups[1][1]), d)
        max_desire = max(max_desire, new_desire)

    return max_desire


def max_side_group_desire(left_groups, right_groups, d, reversed=False):
    if not left_groups:
        return 0.

    desires = [0.]
    # need only cases not evaluated in mid_separation
    if len(left_groups) >= 1:
        desires.append(cost_reduction(left_groups[0][1], 1./left_groups[0][0]))

    if len(left_groups) >= 2:
        desires.append(cost_reduction(left_groups[1][1], 1. / left_groups[1][0]))

        old_costs = min(left_groups[0][1], left_groups[1][1])
        desires.append(cost_reduction(old_costs, 1. / (left_groups[0][0] + left_groups[1][0])))

    if not reversed and right_groups:
        if len(right_groups) == 2:
            if right_groups[0][0] < 1.:
                new_size = left_groups[0][0] + right_groups[0][0]
                desires.append(min(
                    cost_reduction(left_groups[0][1], 1. / new_size),
                    cost_reduction(right_groups[0][1], 1. / new_size + d)
                ))
            if right_groups[1][0] < 1.:
                new_size = left_groups[0][0] + right_groups[1][0]
                desires.append(min(
                    cost_reduction(left_groups[0][1], 1. / new_size),
                    cost_reduction(right_groups[1][1], 1. / new_size + d)
                ))

    if reversed and right_groups:
        if len(left_groups) == 2:
            if left_groups[0][0] > 1.:
                new_size = left_groups[0][0] + right_groups[0][0]
                desires.append(min(
                    cost_reduction(left_groups[0][1], 1. / new_size),
                    cost_reduction(right_groups[0][1], 1. / new_size + d)
                ))
            if left_groups[1][0] > 1.:
                new_size = left_groups[1][0] + right_groups[0][0]
                desires.append(min(
                    cost_reduction(left_groups[1][1], 1. / new_size),
                    cost_reduction(right_groups[0][1], 1. / new_size + d)
                ))

        if len(left_groups) == 1:
            if len(right_groups) >= 1:
                new_size = left_groups[0][0] + right_groups[0][0]
                desires.append(min(
                    cost_reduction(left_groups[0][1], 1. / new_size),
                    cost_reduction(right_groups[0][1], 1. / new_size + d)
                ))
            if len(right_groups) == 2:
                new_size = left_groups[0][0] + right_groups[1][0]
                desires.append(min(
                    cost_reduction(left_groups[0][1], 1. / new_size),
                    cost_reduction(right_groups[1][1], 1. / new_size + d)
                ))

                new_size = left_groups[0][0] + right_groups[0][0] + right_groups[1][0]
                desires.append(min(
                    cost_reduction(left_groups[0][1], 1. / new_size),
                    cost_reduction(right_groups[0][1], 1. / new_size + d),
                    cost_reduction(right_groups[1][1], 1. / new_size + d)
                ))

    return max(desires)


def upperbound(d_space, k_start=1., k_end=1.62, k_iter=1000):
    t = time()
    for k in linspace(k_start, k_end, k_iter):
        eps = 0.
        d_res = 0
        a_res = 0
        for d in d_space(k):
            next_instab, a = world_instability(k, d)
            if next_instab > eps:
                eps, d_res, a_res = next_instab, d, a

        print("Time passed:", str(time() - t))
        print(f"k={round(k, 2)}, d={round(d_res, 2)}, a_res={a_res}, eps={eps}")


def upperbound_rel(k_start=1., k_end=1.62, k_iter=1000, d_iter=300):
    d_space = lambda k: linspace(k / (1 + k), 1 / k, d_iter)
    upperbound(d_space, k_start, k_end, k_iter)


def upperbound_abs(k_start=1., k_end=2., k_iter=1000, d_iter=300):
    d_space = linspace(0, 1, d_iter)
    upperbound(d_space, k_start, k_end, k_iter)


if __name__ == "__main__":
    ITERATIONS = 101
    cost_reduction = relative_cost_reduction
    upperbound_rel(1.30, 1.31, 41, 300)
