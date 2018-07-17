from numex.plugins import EXT
import numpy as np

try:
    import nibabel as nib


    def load(filepath):
        """
        Load a NiBabel-supported image.

        Args:
            filepath (str): The input file path.

        Returns:
            arr (np.ndarray): The array data.

        See Also:
            nibabel.load(), nibabel.get_data(), nibabel.get_affine(),
            nibabel.get_header()
        """
        obj = nib.load(filepath)
        return obj.get_data()


    EXT['nii'] = load
    EXT['nii.gz'] = load

except ImportError:
    pass
