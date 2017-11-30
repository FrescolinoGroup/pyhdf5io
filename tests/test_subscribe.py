"""
Test the subscribe_serialize decorator.
"""

import pytest
from fsc.hdf5_io import subscribe_serialize

def test_duplicate_throws():
    with pytest.raises(ValueError):
        @subscribe_serialize('test.simple_class')
        class Foo: # pylint: disable=unused-variable
            pass
