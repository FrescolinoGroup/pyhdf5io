"""
Configuration file for pytest tests.
"""

import os

import pytest


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
