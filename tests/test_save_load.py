"""
Tests for saving and loading a simple class.
"""

import tempfile

import h5py
import pytest
import numpy as np
from numpy.testing import assert_equal

from fsc.hdf5_io import save, load

from simple_class import (
    SimpleClass, LegacyClass, AutoClass, AutoClassChild, AutoClassWithOptional,
    InvalidAttributeKeyType, InvalidOptionalKeyType, ClashingKeys
)


@pytest.fixture(params=['tempfile', 'permanent'])
def check_save_load(request, test_name, sample_dir):
    """
    Check that a given object remains the same when saved and loaded.
    """
    def inner_tempfile(x):
        with tempfile.NamedTemporaryFile() as named_file:
            save(x, named_file.name)
            y = load(named_file.name)
        assert_equal(x, y)

    def inner_permanent(x):
        """
        Compares the current value against a value loaded from a sample file. The file is created if it doesn't exist, and an error is raised.
        """
        file_name = sample_dir / (test_name + '.hdf5').replace('/', '_')
        try:
            y = load(file_name)
            assert_equal(x, y)
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
        with h5py.File(named_file.name, 'r+') as h5_file:
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
    x = [3, np.float64(2.3), 1 + 3j]
    check_save_load(x)


def test_str(check_save_load):  # pylint: disable=redefined-outer-name
    """
    Test string serialization.
    """
    x = 'foobar'
    check_save_load(x)


def test_bytes(check_save_load):  # pylint: disable=redefined-outer-name
    """
    Test bytes serialization.
    """
    x = b'foobar'
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
        SimpleClass(2): 4,
        (1, 2, 3): 5
    }
    check_save_load(x)


def test_none(check_save_load):  # pylint: disable=redefined-outer-name
    """
    Test NoneType serialization.
    """
    check_save_load(None)


def test_auto_class(check_save_load):  # pylint: disable=redefined-outer-name
    """
    Test serialization using the ``SimpleHDF5Mapping``.
    """
    check_save_load(AutoClass(x=2., y=[1, 2., 3., SimpleClass(3)]))


@pytest.mark.parametrize(
    'obj',
    [AutoClassWithOptional(x=1, y=2),
     AutoClassWithOptional(x=1, y=2, z=3)]
)
def test_optional_attributes(check_save_load, obj):  # pylint: disable=redefined-outer-name
    """
    Test the ``SimpleHDF5Mapping`` with optional attributes.
    """
    check_save_load(obj)


def test_auto_class_child(check_save_load):  # pylint: disable=redefined-outer-name
    """
    Test serialization using the ``SimpleHDF5Mapping`` with inheritance.
    """
    from fsc.hdf5_io._subscribe import SERIALIZE_MAPPING
    print(SERIALIZE_MAPPING)
    check_save_load(
        AutoClassChild(
            x=2., y=[1, 2., 3., SimpleClass(3)], z=AutoClass(x=1., y=[3])
        )
    )


def test_load_old_dict(sample_dir):
    """
    Test that the 'legacy' version of dict can be de-serialized.
    """
    x = load(sample_dir / 'old_dict.hdf5')
    assert x == {'a': SimpleClass(4), 'b': [SimpleClass(1), SimpleClass(10)]}


def test_legacyclass_notag(sample_dir):
    """
    Test that the 'LegacyClass.from_hdf5_file' works even if no 'type_tag' is given.
    """
    x = LegacyClass.from_hdf5_file(sample_dir / 'no_tag.hdf5', y=1.2)
    assert x.x == 10
    assert x.y == 1.2


@pytest.mark.parametrize(
    'obj', [
        np.array([[1, 2, 3], [4, 5, 6]]),
        np.array([1, 2., None, 'foo'], dtype=object),
        np.array(['foo', 'bar', 'baz']), (np.array(['foo', 'bar', 'baz']), ),
        np.array([[1, 2], [4, 5]], dtype=[('age', 'i4'), ('weight', 'f4')])
    ]
)
def test_numpy_array(check_save_load, obj):  # pylint: disable=redefined-outer-name
    """
    Check save / load for numpy arrays
    """
    check_save_load(obj)


def test_unhashable_dict_key(sample_dir):
    """
    Test loading an invalid dictionary with keys that can not be made
    hashable.
    """
    filename = sample_dir / 'invalid' / 'unhashable_dict_key.hdf5'
    with pytest.raises(ValueError):
        load(filename)


@pytest.mark.parametrize(
    'filename', ['inexistent_tag.hdf5', 'inexistent_tag_with_entrypoint.hdf5']
)
def test_inexistent_tag(sample_dir, filename):
    """
    Test loading files with inexistent type tags.
    """
    filename_full = sample_dir / 'invalid' / filename
    with pytest.raises(KeyError):
        load(filename_full)


@pytest.mark.parametrize(
    'obj',
    [InvalidAttributeKeyType(),
     InvalidOptionalKeyType(),
     ClashingKeys()]
)
def test_incorrect_key_check(obj):
    """
    Test that the HDF5_ATTRIBUTES and HDF5_OPTIONAL attributes are
    checked for consistency upon saving.
    """
    with tempfile.NamedTemporaryFile() as tmpf:
        with pytest.raises(ValueError):
            save(obj, tmpf.name)
