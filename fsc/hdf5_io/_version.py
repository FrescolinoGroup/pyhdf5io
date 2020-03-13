"""
Defines the module's version, read from the version.txt file.
"""

import pathlib

with open(pathlib.Path(__file__).parent.resolve() / 'version.txt', 'r') as f:
    __version__ = f.read().strip()
