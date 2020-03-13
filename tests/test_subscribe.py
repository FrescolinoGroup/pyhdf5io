"""
Test the subscribe_hdf5 decorator.
"""

import pytest
from fsc.hdf5_io import subscribe_hdf5

from simple_class import SimpleClass


def test_duplicate_throws():
    """
    Test that the same type tag cannot be set twice.
    """
    with pytest.raises(ValueError):

        @subscribe_hdf5('test.simple_class')
        class Foo:  # pylint: disable=unused-variable
            pass


def test_load_old_tag(sample_dir):
    """
    Test that data set with an 'extra_tag' can be deserialized.
    """
    x = SimpleClass.from_hdf5_file(sample_dir / 'old_tag.hdf5')
    assert x == SimpleClass(10)
