"""
Run tests for saving / loading sympy objects. These tests are skipped if sympy
is not installed.
"""

import pytest

sympy = pytest.importorskip('sympy')  # pylint: disable=invalid-name

from test_save_load import check_save_load  # pylint: disable=unused-import


@pytest.mark.parametrize(
    'obj',
    [sympy.sympify('Matrix([[1, I], [x, y]])'),
     sympy.sympify('1 + x + z**2')]
)
def test_sympy(check_save_load, obj):  # pylint: disable=redefined-outer-name
    """
    Check save / load for sympy matrices
    """
    check_save_load(obj)
