from numex.plugins import EXT
import numpy as np

try:
    import nibabel as nib


    # ======================================================================
    def load(filepath):
        """
        Read a CFL header+data pair.

        Args:
            filepath (str): The input filepath.
                Can be either '.hdr' / '.cfl' files.
                Both files must exist.

        Returns:
            arr (ndarray): The data read.
        """
        # determine base filepath
        mask = slice(None, -4, None) \
            if filepath.endswith('.hdr') or filepath.endswith('.cfl') \
            else slice(None)
        base_filepath = filepath[mask]

        # load header
        with open(base_filepath + '.hdr', 'r') as header_file:
            header_file.readline()  # skip comment line
            dim_line = header_file.readline()

        # obtain the shape of the image
        shape = [int(i) for i in dim_line.strip().split(' ')]
        # remove trailing singleton dimensions from shape
        while shape[-1] == 1:
            shape.pop(-1)
        # calculate the data size
        data_size = int(np.prod(shape))

        # load data
        with open(base_filepath + '.cfl', 'r') as data_file:
            arr = np.fromfile(
                data_file, dtype=np.complex64, count=data_size)

        # note: BART uses FORTRAN-style memory allocation
        return arr.reshape(shape, order='F')


    EXT['nii'] = load
    EXT['nii.gz'] = load

except ImportError:
    pass
