"""
This module contains functions to save and load objects, using the HDF5 format.
"""

from ._base_classes import *
from ._save_load import *

# Needs to be loaded on import to define the special type serialization.
from ._simple_mapping import *
from ._special_types import *
from ._subscribe import *
from ._version import __version__

# pylint: disable=undefined-variable
__all__ = (
    _save_load.__all__
    + _base_classes.__all__
    + _subscribe.__all__
    + _simple_mapping.__all__
)
