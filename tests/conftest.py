"""
Configuration file for pytest tests.
"""

import pathlib

import pytest


@pytest.fixture
def test_name(request):
    """Returns a unique name for each test instance."""
    return request.module.__name__ + '/' + request._parent_request._pyfuncitem.name  # pylint: disable=protected-access


@pytest.fixture
def sample_dir():
    """
    Returns the pathlib.Path of the samples directory.
    """
    return pathlib.Path(__file__).parent.resolve() / 'samples'
