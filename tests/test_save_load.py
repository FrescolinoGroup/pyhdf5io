"""
Tests for saving and loading a simple class.
"""

import tempfile

import h5py
import pytest
import numpy as np

from fsc.hdf5_io import save, load

from simple_class import SimpleClass, LegacyClass


@pytest.fixture(params=['tempfile', 'permanent'])
def check_save_load(request, test_name, sample):
    """
    Check that a given object remains the same when saved and loaded.
    """

    def inner_tempfile(x):
        with tempfile.NamedTemporaryFile() as named_file:
            save(x, named_file.name)
            y = load(named_file.name)
        assert x == y

    def inner_permanent(x):
        """
        Compares the current value against a value loaded from a sample file. The file is created if it doesn't exist, and an error is raised.
        """
        file_name = sample((test_name + '.hdf5').replace('/', '_'))
        try:
            y = load(file_name)
            assert x == y
        except IOError:
            save(x, file_name)
            raise ValueError("Sample file did not exist")

    if request.param == 'tempfile':
        return inner_tempfile
    return inner_permanent


def test_file_freefunc(check_save_load):  # pylint: disable=redefined-outer-name
    """
    Test saving and loading to file with the free functions.
    """
    x = SimpleClass(5)
    check_save_load(x)


def test_file_method():
    """
    Test simple saving and loading to file with the instance / class methods.
    """
    x = SimpleClass(6)
    with tempfile.NamedTemporaryFile() as named_file:
        with h5py.File(named_file.name) as h5_file:
            x.to_hdf5(h5_file)
            y = SimpleClass.from_hdf5(h5_file)
    assert x == y


def test_handle_method():
    """
    Test simple saving and loading to an existing HDF5 handle with the instance / class methods.
    """
    x = SimpleClass(3)
    with tempfile.NamedTemporaryFile() as named_file:
        x.to_hdf5_file(named_file.name)
        y = SimpleClass.from_hdf5_file(named_file.name)
    assert x == y


def test_invalid(check_save_load):  # pylint: disable=redefined-outer-name
    """
    Test that saving an object which cannot be serialized raises TypeError.
    """
    with pytest.raises((TypeError, ValueError)):
        check_save_load(lambda x: True)


def test_number(check_save_load):  # pylint: disable=redefined-outer-name
    """
    Test number serialization.
    """
    x = [3, np.float(2.3), 1 + 3j]
    check_save_load(x)


def test_str(check_save_load):  # pylint: disable=redefined-outer-name
    """
    Test string serialization.
    """
    x = 'foobar'
    check_save_load(x)


def test_list(check_save_load):  # pylint: disable=redefined-outer-name
    """
    Test nested list serialization.
    """
    x = [SimpleClass(3), [SimpleClass(5), SimpleClass(10)]]
    check_save_load(x)


def test_dict(check_save_load):  # pylint: disable=redefined-outer-name
    """
    Test dict serialization.
    """
    x = {
        'a': SimpleClass(4),
        'b': [SimpleClass(1), SimpleClass(10)],
        SimpleClass(2): 4
    }
    check_save_load(x)


def test_none(check_save_load):  # pylint: disable=redefined-outer-name
    """
    Test NoneType serialization.
    """
    check_save_load(None)


def test_load_old_dict(sample):
    """
    Test that the 'legacy' version of dict can be de-serialized.
    """
    x = load(sample('old_dict.hdf5'))
    assert x == {'a': SimpleClass(4), 'b': [SimpleClass(1), SimpleClass(10)]}


def test_legacyclass_notag(sample):
    """
    Test that the 'LegacyClass.from_hdf5_file' works even if no 'type_tag' is given.
    """
    x = LegacyClass.from_hdf5_file(sample('no_tag.hdf5'), y=1.2)
    assert x.x == 10
    assert x.y == 1.2
