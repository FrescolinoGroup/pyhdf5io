"""
Module defining the deserialization method for sympy objects.
"""

from ._special_types import Deserializable, _SpecialTypeTags
from ._subscribe import subscribe_hdf5


@subscribe_hdf5(_SpecialTypeTags.SYMPY)
class _SympyDeserializer(Deserializable):
    """Helper class to de-serialize sympy objects."""

    @classmethod
    def from_hdf5(cls, hdf5_handle):
        import sympy  # pylint: disable=import-outside-toplevel

        return sympy.sympify(hdf5_handle["value"][()].decode("utf-8"))
