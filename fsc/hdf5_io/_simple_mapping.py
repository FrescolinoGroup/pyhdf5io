"""
Implements a base class for serializing a given list of attributes of an object.
"""

import contextlib

from fsc.export import export

from ._base_classes import HDF5Enabled
from ._save_load import from_hdf5 as _global_from_hdf5
from ._save_load import to_hdf5 as _global_to_hdf5


@export
class SimpleHDF5Mapping(HDF5Enabled):
    """
    Base class for data classes which simply map their member to HDF5 values / groups.

    The child class needs to define a list ``HDF5_ATTRIBUTES`` of attributes which
    should be serialized. The name of the attributes must correspond to the
    name accepted by the constructor.

    For attributes which *can* be serialized but are not required, it can also
    define a list ``HDF5_OPTIONAL``. The same logic as for the ``HDF5_ATTRIBUTES``
    applies, but no error is raised if an attribute does not exist.
    """

    HDF5_ATTRIBUTES = ()
    HDF5_OPTIONAL = ()

    @classmethod
    def from_hdf5(cls, hdf5_handle):
        cls._check_hdf5_attributes_lists()
        kwargs = dict()
        to_deserialize = list(cls.HDF5_ATTRIBUTES) + [
            key for key in cls.HDF5_OPTIONAL if key in hdf5_handle
        ]

        for key in to_deserialize:
            hdf5_obj = hdf5_handle[key]
            try:
                kwargs[key] = hdf5_obj[()]
            except (AttributeError, TypeError):
                kwargs[key] = _global_from_hdf5(hdf5_obj)
        return cls(**kwargs)

    def to_hdf5(self, hdf5_handle):
        self._check_hdf5_attributes_lists()
        to_serialize = [(key, getattr(self, key)) for key in self.HDF5_ATTRIBUTES]
        for key in self.HDF5_OPTIONAL:
            with contextlib.suppress(AttributeError):
                to_serialize.append((key, getattr(self, key)))

        for key, value in to_serialize:
            try:
                hdf5_handle[key] = value
            except TypeError:
                _global_to_hdf5(value, hdf5_handle.create_group(key))

    @classmethod
    def _check_hdf5_attributes_lists(cls):
        """
        Helper method to check that the HDF5_ATTRIBUTES and HDF5_OPTIONAL
        attributes of the class are consistent.
        """
        for key in cls.HDF5_ATTRIBUTES:
            if not isinstance(key, str):
                raise ValueError(
                    f"The element '{key}' in {cls}.HDF5_ATTRIBUTES must be a string."
                )
        for key in cls.HDF5_OPTIONAL:
            if not isinstance(key, str):
                raise ValueError(
                    f"The element '{key}' in {cls}.HDF5_OPTIONAL must be a string."
                )

        overlapping_keys = set(cls.HDF5_ATTRIBUTES) & set(cls.HDF5_OPTIONAL)
        if overlapping_keys:
            raise ValueError(
                "The keys {overlapping_keys} are present in both {cls}.HDF5_ATTRIBUTES and {cls}.HDF5_OPTIONAL".format(
                    overlapping_keys=overlapping_keys, cls=cls
                )
            )
