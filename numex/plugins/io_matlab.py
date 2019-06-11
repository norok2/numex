from numex.plugins import EXT
import numpy as np

try:
    import h5py
except ImportError:
    h5py = None

try:
    from scipy.io import loadmat
except ImportError:
    loadmat = None


# ======================================================================
def load(
        filepath,
        selected=None,
        *_args,
        **_kws):
    """
    Read a MATLAB file.

    File versions v4 (Level 1.0), v6 and v7 to 7.2 are supported through SciPy.
    File versions v7.3+ are supported through h5py.

    Args:
        filepath (str): The input filepath.

    Returns:
        arr (ndarray): The array data.
    """

    # Load MATLAB v4 (Level 1.0), v6 and v7 to 7.2 files
    try:
        from scipy.io import loadmat


        mats = loadmat(filepath, *_args, **_kws)
    except ImportError:
        mats = None
    except NotImplementedError:
        mats = None

    # Load MATLAB v7.3+ files
    try:
        import h5py


        mats = h5py.File(filepath, 'r')
    except ImportError:
        mats = None

    if mats is not None:
        data = {}
        for k, v in mats.items():
            data[k] = np.array(v)

        if selected is None:

            for k, v in data.items():
                if selected is None or v.size > data[selected]:
                    selected = k
        return data[selected]
    else:
        text = 'Could not load data from MATLAB file `{}`'.format(filepath)
        raise IOError(text)


EXT['mat'] = load
