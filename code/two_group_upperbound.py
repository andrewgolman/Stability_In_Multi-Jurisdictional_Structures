from numpy import linspace
from time import time
from utils import relative_cost_reduction, absolute_cost_reduction

ITERATIONS = 51


def world_instability(k, d):
    min_eps_partition = 1.
    a_res = ()
    for a in linspace(0., 1., ITERATIONS):
        # pseudo federation
        groups = [(1., a, 0.)]  # left size, right size, median
        if k > a:
            groups.append((0., k-a, d))
        next_instability, log = groups_instability(groups, d)
        if next_instability < min_eps_partition:
            min_eps_partition = next_instability
            if a == 0:
                a_res = (a, "F")
            else:
                a_res = (a, int(a * 100))
    for a in linspace(0., 1., ITERATIONS):
        # incomplete union (other side pseudo federation)
        groups = [(a, k, d)]
        if a < 1.:
            groups.append((1.-a, 0., 0.))
        next_instability, log = groups_instability(groups, d)
        if next_instability < min_eps_partition:
            min_eps_partition = next_instability
            if a < 1:
                a_res = (a, "R")
            else:
                a_res = (a, "U")
    for b in linspace(0., min(d, 1.), ITERATIONS):
        # max undef
        groups = [(1., 1., b)]
        if k > 1:
            groups.append((0., k-1., d))
        next_instability, log = groups_instability(groups, d)
        if next_instability < min_eps_partition:
            min_eps_partition = next_instability
            a_res = (b, "M")
    return min_eps_partition, a_res


def cost_groups(groups, d):
    left_groups = list()
    right_groups = list()

    for left, right, median in groups:
        left_costs = 1. / (left + right) + median
        right_costs = 1. / (left + right) + d - median
        if left:
            left_groups.append((left, left_costs))
        if right:
            right_groups.append((right, right_costs))

    left_groups.sort(key=lambda x: -x[1])
    right_groups.sort(key=lambda x: -x[1])

    return left_groups, right_groups


def groups_instability(groups, d, return_log=True):
    left_groups, right_groups = cost_groups(groups, d)
    # print(left_groups, right_groups)

    # 'left groups' means all subcoalitions from the left
    left_threat = max_side_group_desire(left_groups, right_groups, d)
    right_threat = max_side_group_desire(right_groups, left_groups, d, reversed=True)

    mid_threat = max_undef_group_desire(left_groups, right_groups, d)
    biggest_threat = max(left_threat, right_threat, mid_threat)

    if return_log:
        if biggest_threat == left_threat:
            kind = 'L'
        elif biggest_threat == mid_threat:
            kind = 'M'
        else:
            kind = 'R'
        return biggest_threat[0], (kind, biggest_threat, (left_threat, mid_threat, right_threat))
    return biggest_threat[0]


def optimize_undef_costs(size, left_costs, right_costs, d):
    transport_costs = 1. / size
    # equation for a new median: (transport_costs + dist) / left_costs = (transport_costs + d - dist) / right_costs
    new_median = ((transport_costs + d) * left_costs - transport_costs * right_costs) / (left_costs + right_costs)
    if new_median < 0.:
        new_median = 0.
    if new_median > d:
        new_median = d
    new_left_costs = transport_costs + new_median
    new_right_costs = transport_costs + d - new_median
    reduction = min(cost_reduction(left_costs, new_left_costs), cost_reduction(right_costs, new_right_costs))

    return reduction, new_median


def max_undef_group_desire(left_groups, right_groups, d):
    """
    :return: (desire, group_size, group_median)
    """
    if not left_groups or not right_groups:
        return 0.

    desires = [(0., 0, 0)]
    # i = 1
    # j = 1
    # while i < len(left_groups) or j < len(right_groups):
    #     left_size = sum(left_groups[n][0] for n in range(i + 1))
    #     right_size = sum(right_groups[n][0] for n in range(j + 1))
    #     size = 2 * min(left_size, right_size)  # see next if
    #     desires.append(optimize_undef_costs(
    #         size, left_groups[i][1], right_groups[j][1], d
    #     ))
    #     if left_size < right_size:
    #         i += 1
    #     else:
    #         j += 1

    # need for each i to go the furthest possible without overflow. on the other side will just add some small values
    for i, lg in enumerate(left_groups):
        for j, rg in enumerate(right_groups):
            left_size = sum(left_groups[n][0] for n in range(i+1))
            right_size = sum(right_groups[n][0] for n in range(j+1))
            size = 2 * min(left_size, right_size)  # see next if
            desire, median = optimize_undef_costs(
                size, left_groups[i][1], right_groups[j][1], d
            )
            desires.append((desire, size, median))
            if right_size >= left_size:  # stop increasing right size, so next excluded groups costs are not counted
                break

    return max(desires)


def max_side_group_desire(left_groups, right_groups, d, reversed=False):
    """
    :param reversed: whether given left groups are actually right (for median calculation)
    :return: (desire, group_size, group_median)
    """
    if not left_groups:
        return 0.

    desires = [(0, 0, 0)]

    for i, lg in enumerate(left_groups):
        left_size = sum(left_groups[n][0] for n in range(i+1))
        desires.append(
            (cost_reduction(lg[1], 1 / left_size), left_size, d * reversed)
        )
        for j, rg in enumerate(right_groups):
            right_size = sum(right_groups[n][0] for n in range(j+1))
            size = left_size + min(left_size, right_size)  # see next if
            desires.append((min(
                cost_reduction(lg[1], 1 / size),
                cost_reduction(rg[1], 1 / size + d)
            ), size, d * reversed))

            if right_size >= left_size:  # ensure that no excluded agents will be accounted
                break

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


def top_threat_small_undef(k, d):
    a_set = linspace(0., 1., ITERATIONS)
    m_set = linspace(0, d, ITERATIONS)
#     a_set = [0.99]
#     m_set = [0.36]

    for a in a_set:
        for m in m_set:
            if a in [0., 1.]:
                continue
            print(f"a={a}, m={m}, d={d}")
            union_groups = [
                (a, a, m),
                (1 - a, k - a, d),
            ]
            fed_groups = [
                (a, a, m),
                (1 - a, 0, 0),
                (0, k - a, d),
            ]
            ni1, log = groups_instability(union_groups, d)
            print(log[:2], "\t\t", log[2])
            ni2, log = groups_instability(fed_groups, d)
            print(log[:2], "\t\t", log[2])


cost_reduction = relative_cost_reduction


if __name__ == "__main__":
    ITERATIONS = 11
    k = 1.305
    d = 0.63
    # upperbound_rel(1.30, 1.31, 41, 300)
    # print(world_instability(1.306, 0.632))
    # print(world_instability(1.26, 0.645))
    k = 1.4
    d_set = linspace(k/(1+k), 1/k, 10)
    d_set = [sum(d_set) / 10]
    for d in d_set:
        top_threat_small_undef(k, d)
