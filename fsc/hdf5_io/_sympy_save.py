"""
Module defining the serialization method for sympy objects.
"""

import sympy

from ._special_types import (
    _SpecialTypeTags,
    _value_serializer,
    add_type_tag,
    to_hdf5_singledispatch,
)


@to_hdf5_singledispatch.register(sympy.MatrixBase)
@to_hdf5_singledispatch.register(sympy.Basic)
@add_type_tag(_SpecialTypeTags.SYMPY)
def _(obj, hdf5_handle):
    _value_serializer(sympy.srepr(obj), hdf5_handle)
