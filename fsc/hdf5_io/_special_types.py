"""
Defines the (de-)serialization for special built-in types.
"""

from collections.abc import Hashable, Iterable, Mapping
from functools import singledispatch
from numbers import Complex
from types import SimpleNamespace

import numpy as np

from ._base_classes import Deserializable
from ._save_load import from_hdf5, to_hdf5, to_hdf5_singledispatch
from ._subscribe import TYPE_TAG_KEY, subscribe_hdf5

__all__ = []


class _SpecialTypeTags(SimpleNamespace):
    """
    Defines the type tags for special types.
    """

    LIST = "builtins.list"
    TUPLE = "builtins.tuple"
    DICT = "builtins.dict"
    NUMBER = "builtins.number"
    STR = "builtins.str"
    BYTES = "builtins.bytes"
    NONE = "builtins.none"
    NUMPY_ARRAY = "numpy.ndarray"
    SYMPY = "sympy.object"  # defined in _sympy_load.py and _sympy_save.py


@subscribe_hdf5(_SpecialTypeTags.DICT)
class _DictDeserializer(Deserializable):
    """Helper class to de-serialize dict objects."""

    @classmethod
    def from_hdf5(cls, hdf5_handle):
        try:
            items = from_hdf5(hdf5_handle["items"])
            return {_ensure_hashable(k): v for k, v in items}
        # Handle legacy dicts with only string keys:
        except KeyError:
            res = dict()
            value_group = hdf5_handle["value"]
            for key in value_group:
                res[key] = from_hdf5(value_group[key])
            return res


@subscribe_hdf5(_SpecialTypeTags.LIST)
class _ListDeserializer(Deserializable):
    """Helper class to de-serialize list objects."""

    @classmethod
    def from_hdf5(cls, hdf5_handle):
        return _deserialize_iterable(hdf5_handle)


@subscribe_hdf5(_SpecialTypeTags.TUPLE)
class _TupleDeserializer(Deserializable):
    """Helper class to de-serialize tuple objects."""

    @classmethod
    def from_hdf5(cls, hdf5_handle):
        return tuple(_deserialize_iterable(hdf5_handle))


def _deserialize_iterable(hdf5_handle):
    int_keys = [key for key in hdf5_handle if key != TYPE_TAG_KEY]
    return [from_hdf5(hdf5_handle[key]) for key in sorted(int_keys, key=int)]


@subscribe_hdf5(_SpecialTypeTags.NUMBER, extra_tags=(_SpecialTypeTags.BYTES,))
class _ValueDeserializer(Deserializable):
    """Helper class to de-serialize numbers."""

    @classmethod
    def from_hdf5(cls, hdf5_handle):
        return hdf5_handle["value"][()]


@subscribe_hdf5(_SpecialTypeTags.STR)
class _StringDeserializer(Deserializable):
    """Helper class to de-serialize strings."""

    @classmethod
    def from_hdf5(cls, hdf5_handle):
        return hdf5_handle["value"][()].decode("utf-8")


@subscribe_hdf5(_SpecialTypeTags.NUMPY_ARRAY)
class _NumpyArraryDeserializer(Deserializable):
    """Helper class to de-serialize numpy arrays."""

    @classmethod
    def from_hdf5(cls, hdf5_handle):
        if "value" in hdf5_handle:
            return hdf5_handle["value"][()]
        return np.array(_deserialize_iterable(hdf5_handle))


@subscribe_hdf5(_SpecialTypeTags.NONE)
class _NoneDeserializer(Deserializable):
    """Helper class to de-serialize ``None``."""

    @classmethod
    def from_hdf5(cls, hdf5_handle):
        return None


def add_type_tag(tag):
    """
    Decorator which adds the given type tag when creating the HDF5 object.
    """

    def outer(func):
        def inner(obj, hdf5_handle):
            hdf5_handle[TYPE_TAG_KEY] = tag
            func(obj, hdf5_handle)

        return inner

    return outer


@to_hdf5_singledispatch.register(Iterable)
@add_type_tag(_SpecialTypeTags.LIST)
def _(obj, hdf5_handle):
    _serialize_iterable(obj, hdf5_handle)


@to_hdf5_singledispatch.register(tuple)
@add_type_tag(_SpecialTypeTags.TUPLE)
def _(obj, hdf5_handle):
    _serialize_iterable(obj, hdf5_handle)


def _serialize_iterable(obj, hdf5_handle):
    for i, part in enumerate(obj):
        sub_group = hdf5_handle.create_group(str(i))
        to_hdf5(part, sub_group)


@to_hdf5_singledispatch.register(Mapping)
@add_type_tag(_SpecialTypeTags.DICT)
def _(obj, hdf5_handle):
    items_group = hdf5_handle.create_group("items")
    to_hdf5(obj.items(), items_group)


@to_hdf5_singledispatch.register(Complex)
@add_type_tag(_SpecialTypeTags.NUMBER)
def _(obj, hdf5_handle):
    _value_serializer(obj, hdf5_handle)


@to_hdf5_singledispatch.register(str)
@to_hdf5_singledispatch.register(np.str_)
@add_type_tag(_SpecialTypeTags.STR)
def _(obj, hdf5_handle):
    _value_serializer(str(obj), hdf5_handle)


@to_hdf5_singledispatch.register(bytes)
@add_type_tag(_SpecialTypeTags.BYTES)
def _(obj, hdf5_handle):
    _value_serializer(obj, hdf5_handle)


@to_hdf5_singledispatch.register(type(None))
@add_type_tag(_SpecialTypeTags.NONE)
def _(obj, hdf5_handle):
    pass


@to_hdf5_singledispatch.register(np.ndarray)
@add_type_tag(_SpecialTypeTags.NUMPY_ARRAY)
def _(obj, hdf5_handle):  # pylint: disable=missing-docstring
    try:
        _value_serializer(obj, hdf5_handle)
    except TypeError:
        # if the numpy dtype does not have a native HDF5 equivalent,
        # treat it as an iterable instead
        _serialize_iterable(obj, hdf5_handle)


def _value_serializer(obj, hdf5_handle):
    hdf5_handle["value"] = obj


def _ensure_hashable(obj):
    if isinstance(obj, Hashable):
        return obj
    return _to_hashable(obj)


@singledispatch
def _to_hashable(obj):
    raise ValueError(
        f"Cannot convert object '{obj}' of type '{type(obj)}' to a hashable object."
    )


@_to_hashable.register(Iterable)
def _(obj):
    return tuple(_ensure_hashable(val) for val in obj)
