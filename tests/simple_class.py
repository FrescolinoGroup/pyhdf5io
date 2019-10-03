"""
Defines a simple serializable class.
"""

from fsc.hdf5_io import subscribe_hdf5, HDF5Enabled, SimpleHDF5Mapping


@subscribe_hdf5(
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
        return cls(x=hdf5_handle['x'][()])

    def __eq__(self, other):
        return self.x == other.x

    def __hash__(self):
        return hash(self.x)

    def __iter__(self):
        return iter([self.x])


@subscribe_hdf5('test.auto_class')
class AutoClass(SimpleHDF5Mapping):
    """
    Class which uses the automatic serialization.
    """
    HDF5_ATTRIBUTES = ['x', 'y']

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


@subscribe_hdf5('test.auto_class_child')
class AutoClassChild(AutoClass):
    """
    Class which inherits from a class using the automatic serialization feature.
    """
    HDF5_ATTRIBUTES = AutoClass.HDF5_ATTRIBUTES + ['z']

    def __init__(self, x, y, z):
        super().__init__(x, y)
        self.z = z

    def __eq__(self, other):
        return super().__eq__(other) and self.z == other.z


@subscribe_hdf5('test.legacy_class', check_on_load=False)
class LegacyClass(SimpleClass):
    """
    Class which accepts kwargs in 'from_hdf5', and should work without 'type_tag'.
    """
    def __init__(self, x, y=0.):
        super().__init__(x=x)
        self.y = float(y)

    @classmethod
    def from_hdf5(cls, hdf5_handle, **kwargs):  # pylint: disable=arguments-differ
        return cls(x=hdf5_handle['x'][()], **kwargs)
