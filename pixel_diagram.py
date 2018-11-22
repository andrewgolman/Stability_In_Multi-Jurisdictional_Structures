from numpy import linspace
import scipy.misc as smp
from two_group_upperbound import world_instability


def diagram():
    size = 4
    data = np.zeros((size, size, 3), dtype=np.uint8)
    for k, kp in zip(linspace(1, 2, size), range(size)):
        for d, dp in zip(linspace(0.5, 1, size), range(size)):
            instab, a = world_instability(k, d)
            if instab < 0.0000001:
                a = (0, "S")
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
    for k, kp in zip(linspace(1, 2, size), range(size)):
        for d, dp in zip(linspace(1.6, 3.2, size), range(size)):
            instab, a = world_instability(d/k, 1/k)
            if instab < 0.0000001:
                a = (0, "S")
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
