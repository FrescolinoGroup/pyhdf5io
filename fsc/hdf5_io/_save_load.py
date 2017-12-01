"""
Defines free functions to serialize / deserialize bands-inspect objects to HDF5.
"""

from types import SimpleNamespace
from functools import singledispatch
from collections.abc import Iterable, Mapping

import h5py
from fsc.export import export

from ._serializable import HDF5Enabled, Deserializable
from ._serialize_mapping import SERIALIZE_MAPPING

__all__ = ['save', 'load']


class _SpecialTypeTags(SimpleNamespace):
    LIST = 'builtins.list'
    DICT = 'builtins.dict'


class _DictDeserializer(Deserializable):
    @staticmethod
    def from_hdf5(hdf5_handle):
        res = dict()
        value_group = hdf5_handle['value']
        for key in value_group:
            res[key] = from_hdf5(value_group[key])
        return res


class _ListDeserializer(Deserializable):
    @staticmethod
    def from_hdf5(hdf5_handle):
        int_keys = [key for key in hdf5_handle if key != 'type_tag']
        return [
            from_hdf5(hdf5_handle[key]) for key in sorted(int_keys, key=int)
        ]


SERIALIZE_MAPPING[_SpecialTypeTags.DICT] = _DictDeserializer
SERIALIZE_MAPPING[_SpecialTypeTags.LIST] = _ListDeserializer


@export
@singledispatch
def to_hdf5(obj, hdf5_handle):  # pylint: disable=unused-argument
    """
    Serializes a given object to HDF5 format.

    :param obj: Object to serialize.

    :param hdf5_handle: HDF5 location where the serialized object is stored.
    :type hdf5_handle: :py:class:`h5py.File<File>` or :py:class:`h5py.Group<Group>`.
    """
    raise TypeError(
        "Cannot serialize object '{}' of type '{}'".format(obj, type(obj))
    )


@to_hdf5.register(HDF5Enabled)
def _(obj, hdf5_handle):
    obj.to_hdf5(hdf5_handle)


@to_hdf5.register(Iterable)
def _(obj, hdf5_handle):
    hdf5_handle['type_tag'] = _SpecialTypeTags.LIST
    for i, part in enumerate(obj):
        sub_group = hdf5_handle.create_group(str(i))
        to_hdf5(part, sub_group)


@to_hdf5.register(Mapping)
def _(obj, hdf5_handle):
    hdf5_handle['type_tag'] = _SpecialTypeTags.DICT
    value_group = hdf5_handle.create_group('value')
    for key, val in obj.items():
        sub_group = value_group.create_group(key)
        to_hdf5(val, sub_group)


@export
def from_hdf5(hdf5_handle):
    """
    Deserializes a given object from HDF5 format.

    :param hdf5_handle: HDF5 location where the serialized object is stored.
    :type hdf5_handle: :py:class:`h5py.File<File>` or :py:class:`h5py.Group<Group>`.
    """
    type_tag = hdf5_handle['type_tag'].value
    return SERIALIZE_MAPPING[type_tag].from_hdf5(hdf5_handle)


@export
def to_hdf5_file(obj, hdf5_file):
    """
    Saves the object to a file, in HDF5 format.

    :param obj: The object to be saved.

    :param hdf5_file: Path of the file.
    :type hdf5_file: str
    """
    with h5py.File(hdf5_file, 'w') as f:
        to_hdf5(obj, f)


save = to_hdf5_file  # pylint: disable=invalid-name


@export
def from_hdf5_file(hdf5_file):
    """
    Loads the object from a file in HDF5 format.

    :param hdf5_file: Path of the file.
    :type hdf5_file: str
    """
    with h5py.File(hdf5_file, 'r') as f:
        return from_hdf5(f)


load = from_hdf5_file  # pylint: disable=invalid-name
