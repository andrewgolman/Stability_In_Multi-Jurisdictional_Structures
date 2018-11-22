import numpy as np
import scipy.misc as smp
from two_group_upperbound import world_instability


def draw_diagram(a_space, b_space, instability, size=64):
    data = np.zeros((size, size, 3), dtype=np.uint8)
    for a, a_pixel in zip(a_space, range(size)):
        for b, b_pixel in zip(b_space, range(size)):
            instab, alpha = instability(a, b)
            if instab < 0.0000001:
                alpha = (0, "S")
            if alpha[1] == "S":
                data[a_pixel, b_pixel] = [255, 255, 255]
            elif alpha[1] == "U":
                data[a_pixel, b_pixel] = [255, 0, 0]
            elif alpha[1] == "M":
                data[a_pixel, b_pixel] = [0, 255, 0]
            elif alpha[1] == "F":
                data[a_pixel, b_pixel] = [0, 0, 255]
            else:
                data[a_pixel, b_pixel] = [128 + int(alpha[1]) * 10]

    img = smp.toimage(data)
    img.show()


def k_d_diagram(size):
    k_space = np.linspace(1, 2, size)
    d_space = np.linspace(0.5, 1, size)
    instability = lambda k, d: world_instability(k, d)
    draw_diagram(k_space, d_space, instability, size)


def relation_diagram(size):
    a_space = np.linspace(1, 2, size)
    b_space = np.linspace(1,6, 3.2, size)
    instability = lambda a, b: world_instability(b/a, 1/a)
    draw_diagram(a_space, b_space, instability)


if __name__ == "__main__":
    k_d_diagram(16)
