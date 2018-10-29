from numex.plugins import EXT
import numpy as np


def load(
        filepath,
        *args,
        **kwargs):
    """
    Load a NumPy array.

    Args:
        filepath (str): The input file path.
        *args (Iterable): Positional arguments for `np.load()`.
        **kwargs (dict|Iterable): Keyword arguments for `np.load()`.

    Returns:
        arr (np.ndarray): The array data.
    """
    arr = np.load(filepath, *args, **kwargs)
    return arr


EXT['npy'] = load
