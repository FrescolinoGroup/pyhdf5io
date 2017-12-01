"""
Defines a simple serializable class.
"""

from fsc.hdf5_io import subscribe_serialize, HDF5Enabled


@subscribe_serialize(
    'test.simple_class', extra_tags=('test.simple_class_old_tag', )
)
class SimpleClass(HDF5Enabled):
    """
    Simple class that implements the HDF5Enabled concept.
    """

    def __init__(self, x):
        self.x = int(x)

    def to_hdf5(self, hdf5_handle):
        hdf5_handle['x'] = self.x

    @classmethod
    def from_hdf5(cls, hdf5_handle):
        return cls(x=hdf5_handle['x'].value)

    def __eq__(self, other):
        return self.x == other.x