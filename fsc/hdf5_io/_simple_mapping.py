"""
Implements a base class for serializing a given list of attributes of an object.
"""

from fsc.export import export

from ._base_classes import HDF5Enabled
from ._save_load import to_hdf5 as _global_to_hdf5, from_hdf5 as _global_from_hdf5


@export
class SimpleHDF5Mapping(HDF5Enabled):
    """
    Base class for data classes which simply map their member to HDF5 values / groups.

    The child class needs to define a list ``HDF5_ATTRIBUTES`` of attributes which
    should be serialized. The name of the attributes must correspond to the
    name accepted by the constructor.
    """
    HDF5_ATTRIBUTES = ()
    HDF5_OPTIONAL = ()

    @classmethod
    def from_hdf5(cls, hdf5_handle):
        kwargs = dict()
        for key in cls.HDF5_ATTRIBUTES:
            try:
                hdf5_obj = hdf5_handle[key]
            except KeyError:
                if key in cls.HDF5_OPTIONAL:
                    continue
                raise
            try:
                kwargs[key] = hdf5_obj.value
            except AttributeError:
                kwargs[key] = _global_from_hdf5(hdf5_obj)
        return cls(**kwargs)

    def to_hdf5(self, hdf5_handle):
        for key in self.HDF5_ATTRIBUTES:
            try:
                value = getattr(self, key)
            except AttributeError:
                if key in self.HDF5_OPTIONAL:
                    continue
                raise
            try:
                hdf5_handle[key] = value
            except TypeError:
                _global_to_hdf5(value, hdf5_handle.create_group(key))
