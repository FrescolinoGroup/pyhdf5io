"""
Tests for saving and loading a simple class.
"""

import tempfile

import h5py

from fsc.hdf5_io import save, load

from simple_class import SimpleClass


def test_file_freefunc():
    """
    Test saving and loading to file with the free functions.
    """
    x = SimpleClass(5)
    with tempfile.NamedTemporaryFile() as named_file:
        save(x, named_file.name)
        y = load(named_file.name)
    assert x == y


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
