import numpy as np


def gen_random(shape, re_scale=100, im_scale=50, dtype=complex):
    arr = re_scale * np.random.random(shape)
    if dtype == complex:
        arr = arr + 1j * im_scale * np.random.random(shape)
    return arr
