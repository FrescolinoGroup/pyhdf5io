"""
Base classes for serializing bands-inspect data types.
"""

import abc

import h5py

from fsc.export import export
from ._save_load import to_hdf5 as _global_to_hdf5, from_hdf5 as _global_from_hdf5


class Deserializable(abc.ABC):
    """
    Base class for data which can be deserialized from the HDF5 format.
    """

    @classmethod
    @abc.abstractmethod
    def from_hdf5(cls, hdf5_handle):
        """
        Deserializes the object stored in HDF5 format.
        """
        raise NotImplementedError

    @classmethod
    def from_hdf5_file(cls, hdf5_file, *args, **kwargs):
        """
        Loads the object from a file in HDF5 format.

        :param hdf5_file: Path of the file.
        :type hdf5_file: str
        """
        with h5py.File(hdf5_file, 'r') as f:
            return cls.from_hdf5(f, *args, **kwargs)


class Serializable(abc.ABC):
    """
    Base class for data which can be serialized to the HDF5 format.
    """

    @abc.abstractmethod
    def to_hdf5(self, hdf5_handle):
        """
        Serializes the object to HDF5 format, attaching it to the given HDF5 handle (might be a HDF5 File or Dataset).
        """
        raise NotImplementedError

    def to_hdf5_file(self, hdf5_file):
        """
        Saves the object to a file, in HDF5 format.

        :param hdf5_file: Path of the file.
        :type hdf5_file: str
        """
        from ._save_load import to_hdf5_file
        to_hdf5_file(self, hdf5_file)


@export  # pylint: disable=abstract-method
class HDF5Enabled(Serializable, Deserializable):
    """
    Base class for data which can be serialized to and deserialized from HDF5.
    """
    pass


@export
class SimpleHDF5Mapping(HDF5Enabled):
    """
    Base class for data classes which simply map their member to HDF5 values / groups.

    The child class needs to define a list ``HDF5_ATTRIBUTES`` of attributes which
    should be serialized. The name of the attributes must correspond to the
    name accepted by the constructor.
    """
    HDF5_ATTRIBUTES = ()

    @classmethod
    def from_hdf5(cls, hdf5_handle):
        kwargs = dict()
        for key in cls.HDF5_ATTRIBUTES:
            try:
                kwargs[key] = hdf5_handle[key].value
            except AttributeError:
                kwargs[key] = _global_from_hdf5(hdf5_handle[key])
        return cls(**kwargs)

    def to_hdf5(self, hdf5_handle):
        for key in self.HDF5_ATTRIBUTES:
            value = getattr(self, key)
            try:
                hdf5_handle[key] = value
            except TypeError:
                _global_to_hdf5(value, hdf5_handle.create_group(key))
