"""
Module defining the deserialization method for sympy objects.
"""

from ._subscribe import subscribe_hdf5
from ._special_types import _SpecialTypeTags, Deserializable


@subscribe_hdf5(_SpecialTypeTags.SYMPY)
class _SympyDeserializer(Deserializable):
    """Helper class to de-serialize sympy objects."""
    @classmethod
    def from_hdf5(cls, hdf5_handle):
        import sympy
        return sympy.sympify(hdf5_handle['value'][()].decode('utf-8'))
