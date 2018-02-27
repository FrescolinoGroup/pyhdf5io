"""
Configuration file for pytest tests.
"""

import os

import pytest


@pytest.fixture
def test_name(request):
    """Returns a unique name for each test instance."""
    return request.module.__name__ + '/' + request._parent_request._pyfuncitem.name  # pylint: disable=protected-access


@pytest.fixture
def sample():
    """
    Returns the full path corresponding to a given sample name.
    """

    def inner(name):
        return os.path.join(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)), 'samples'
            ), name
        )

    return inner
