"""
Helper functions
"""

from typing import Union

__all__ = ("decode_if_needed",)


def decode_if_needed(value: Union[str, bytes]) -> str:
    """Convert `bytes` or `str` to `str`

    Converts the input to `str`, decoding it with `utf-8` if needed.
    """
    if isinstance(value, bytes):
        return value.decode("utf-8")
    return value
