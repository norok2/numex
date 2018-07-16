import numpy as np

def load(filepath, *args, **kwargs):
    arr = np.load(filepath, *args, **kwargs)
    return arr
