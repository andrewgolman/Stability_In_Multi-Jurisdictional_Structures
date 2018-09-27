from numpy import linspace

ITER = 101

def relative_cost_reduction(old_costs, new_costs):
    return old_costs - new_costs
    return 1 - new_costs / old_costs


def world_instability(k, d):
    min_eps_partition = 1.
    a_res = ()
    for a in linspace(0., 1., ITER):
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
    for a in linspace(0., 1., ITER):
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
    for b in linspace(0., min(d, 1.), ITER):
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
        # if (left + right) < 0.01:
        #     print("WARNING")
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
    # (transport_costs + dist) / left_costs = (transport_costs + d - dist) / right_costs
    new_median = ((transport_costs + d) * left_costs - transport_costs * right_costs) / (left_costs + right_costs)
    if new_median < 0.:
        new_median = 0.
    if new_median > d:
        new_median = d
    new_left_costs = transport_costs + new_median
    new_right_costs = transport_costs + d - new_median
    return min(relative_cost_reduction(left_costs, new_left_costs), relative_cost_reduction(right_costs, new_right_costs))


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
        desires.append(relative_cost_reduction(left_groups[0][1], 1./left_groups[0][0]))

    if len(left_groups) >= 2:
        desires.append(relative_cost_reduction(left_groups[1][1], 1. / left_groups[1][0]))

        old_costs = min(left_groups[0][1], left_groups[1][1])
        desires.append(relative_cost_reduction(old_costs, 1. / (left_groups[0][0] + left_groups[1][0])))

    if not reversed and right_groups:
        if len(right_groups) == 2:
            if right_groups[0][0] < 1.:
                new_size = left_groups[0][0] + right_groups[0][0]
                desires.append(min(
                    relative_cost_reduction(left_groups[0][1], 1. / new_size),
                    relative_cost_reduction(right_groups[0][1], 1. / new_size + d)
                ))
            if right_groups[1][0] < 1.:
                new_size = left_groups[0][0] + right_groups[1][0]
                desires.append(min(
                    relative_cost_reduction(left_groups[0][1], 1. / new_size),
                    relative_cost_reduction(right_groups[1][1], 1. / new_size + d)
                ))

    if reversed and right_groups:
        if len(left_groups) == 2:
            if left_groups[0][0] > 1.:
                new_size = left_groups[0][0] + right_groups[0][0]
                desires.append(min(
                    relative_cost_reduction(left_groups[0][1], 1. / new_size),
                    relative_cost_reduction(right_groups[0][1], 1. / new_size + d)
                ))
            if left_groups[1][0] > 1.:
                new_size = left_groups[1][0] + right_groups[0][0]
                desires.append(min(
                    relative_cost_reduction(left_groups[1][1], 1. / new_size),
                    relative_cost_reduction(right_groups[0][1], 1. / new_size + d)
                ))

        if len(left_groups) == 1:
            if len(right_groups) >= 1:
                new_size = left_groups[0][0] + right_groups[0][0]
                desires.append(min(
                    relative_cost_reduction(left_groups[0][1], 1. / new_size),
                    relative_cost_reduction(right_groups[0][1], 1. / new_size + d)
                ))
            if len(right_groups) == 2:
                new_size = left_groups[0][0] + right_groups[1][0]
                desires.append(min(
                    relative_cost_reduction(left_groups[0][1], 1. / new_size),
                    relative_cost_reduction(right_groups[1][1], 1. / new_size + d)
                ))

                new_size = left_groups[0][0] + right_groups[0][0] + right_groups[1][0]
                desires.append(min(
                    relative_cost_reduction(left_groups[0][1], 1. / new_size),
                    relative_cost_reduction(right_groups[0][1], 1. / new_size + d),
                    relative_cost_reduction(right_groups[1][1], 1. / new_size + d)
                ))

    return max(desires)


from time import time
import numpy as np
import scipy.misc as smp

def diagram():
    size = 4
    data = np.zeros((size, size, 3), dtype=np.uint8)
    # data[512, 512] = [254, 0, 0]  # Makes the middle pixel red
    # data[512, 513] = [0, 0, 255]  # Makes the next pixel blue
    for k, kp in zip(linspace(1, 2, size), range(size)):
        for d, dp in zip(linspace(0.5, 1, size), range(size)):
            instab, a = world_instability(k, d)
            if instab < 0.0000001:
                a = (0, "S")
            # if k == 1.30 and d == 0.64:
            #     print("_", end="")
            if a[1] == "S":
                data[kp, dp] = [255, 255, 255]
            elif a[1] == "U":
                data[kp, dp] = [255, 0, 0]
            elif a[1] == "M":
                data[kp, dp] = [0, 255, 0]
            elif a[1] == "F":
                data[kp, dp] = [0, 0, 255]
            else:
                data[kp, dp] = [128 + int(a[1]) * 10]

    img = smp.toimage(data)
    img.show()


def diagram2():
    size = 64
    data = np.zeros((size, size, 3), dtype=np.uint8)
    # data[512, 512] = [254, 0, 0]  # Makes the middle pixel red
    # data[512, 513] = [0, 0, 255]  # Makes the next pixel blue
    for k, kp in zip(linspace(1, 2, size), range(size)):
        for d, dp in zip(linspace(1.6, 3.2, size), range(size)):
            instab, a = world_instability(d/k, 1/k)
            if instab < 0.0000001:
                a = (0, "S")
            # if k == 1.30 and d == 0.64:
            #     print("_", end="")
            if a[1] == "S":
                data[kp, dp] = [255, 255, 255]
            elif a[1] == "U":
                data[kp, dp] = [255, 0, 0]
            elif a[1] == "M":
                data[kp, dp] = [0, 255, 0]
            elif a[1] == "F":
                data[kp, dp] = [0, 0, 255]
            else:
                data[kp, dp] = [128 + int(a[1]) * 10]

    img = smp.toimage(data)
    img.show()


def main():
    # print(world_instability(73./56., 0.6363245))
    t = time()
    for k in linspace(1.30, 1.31, 41):
        res = 0.
        d_res = 0
        a_res = 0
        for d in linspace(k/(1 + k), 1/k, 300):
            next_instab, a = world_instability(k, d)
            if next_instab > res:
                res, d_res, a_res = next_instab, d, a

        # print("TIME: " + str(time() - t))
        print(k, d_res, a_res, res)


def main_abs():
    t = time()
    for k in linspace(1.295, 1.325, 10):
        res = 0.
        d_res = 0
        a_res = 0
        for d in linspace(0, 1, 2000):
            next_instab, a = world_instability(k, d)
            if next_instab > res:
                res, d_res, a_res = next_instab, d, a

        # print("TIME: " + str(time() - t))
        print(k, d_res, a_res, res)


main_abs()
