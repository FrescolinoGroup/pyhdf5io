"""
Defines the (de-)serialization for special built-in types.
"""

from types import SimpleNamespace
from numbers import Complex
from collections.abc import Iterable, Mapping

from ._base_classes import HDF5Enabled, Deserializable

from ._save_load import from_hdf5, to_hdf5
from ._subscribe import subscribe_hdf5

__all__ = []


class _SpecialTypeTags(SimpleNamespace):
    LIST = 'builtins.list'
    DICT = 'builtins.dict'
    NUMBER = 'builtins.number'


@subscribe_hdf5(_SpecialTypeTags.DICT)
class _DictDeserializer(Deserializable):
    @classmethod
    def from_hdf5(cls, hdf5_handle):
        res = dict()
        value_group = hdf5_handle['value']
        for key in value_group:
            res[key] = from_hdf5(value_group[key])
        return res


@subscribe_hdf5(_SpecialTypeTags.LIST)
class _ListDeserializer(Deserializable):
    @classmethod
    def from_hdf5(cls, hdf5_handle):
        int_keys = [key for key in hdf5_handle if key != 'type_tag']
        return [
            from_hdf5(hdf5_handle[key]) for key in sorted(int_keys, key=int)
        ]


@subscribe_hdf5(_SpecialTypeTags.NUMBER)
class _NumpyIntDeserializer(Deserializable):
    @classmethod
    def from_hdf5(cls, hdf5_handle):
        return hdf5_handle['value'].value


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


@to_hdf5.register(Complex)
def _(obj, hdf5_handle):
    hdf5_handle['type_tag'] = _SpecialTypeTags.NUMBER
    hdf5_handle['value'] = obj
