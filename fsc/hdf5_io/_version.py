"""
Defines the module's version, read from the version.txt file.
"""

import pathlib

with open(pathlib.Path(__file__).resolve().parent / 'version.txt', 'r') as f:
    __version__ = f.read().strip()
