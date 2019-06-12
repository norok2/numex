from numex.plugins import EXT
import numpy as np


def load(
        filepath,
        *_args,
        **_kws):
    """
    Load a NumPy array.

    Args:
        filepath (str): The input file path.
        *_args: Positional arguments for `np.load()`.
        **_kws: Keyword arguments for `np.load()`.

    Returns:
        arr (np.ndarray): The array data.
    """
    arr = np.load(filepath, *_args, **_kws)
    return arr


EXT['npy'] = load
