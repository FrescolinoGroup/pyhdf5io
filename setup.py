"""
Usage: pip install .[dev]
"""

import sys

from setuptools import setup

PKGNAME = "hdf5_io"
PKGNAME_QUALIFIED = "fsc." + PKGNAME

with open("doc/description.txt") as f:
    DESCRIPTION = f.read().strip()
try:
    with open("doc/README") as f:
        README = f.read()
except OSError:
    README = DESCRIPTION

with open("version.txt") as f:
    VERSION = f.read().strip()

if sys.version_info < (3, 7):
    raise ValueError("only Python 3.7 and higher are supported")

setup(
    name=PKGNAME_QUALIFIED,
    version=VERSION,
    packages=[PKGNAME_QUALIFIED],
    url="http://frescolinogroup.github.io/frescolino/pyhdf5io/"
    + ".".join(VERSION.split(".")[:2]),
    include_package_data=True,
    author="C. Frescolino",
    author_email="frescolino@lists.phys.ethz.ch",
    description=DESCRIPTION,
    install_requires=["numpy>=1.17.5", "decorator", "h5py~=3.0", "fsc.export"],
    python_requires=">=3.7",
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "pre-commit==2.15.0",
            "pylint==2.11.1",
            "sphinx",
            "sphinx-rtd-theme",
            "ipython>=6.2",
            "matplotlib",
            "sympy",
        ]
    },
    entry_points={
        "fsc.hdf5_io.load": ["sympy.object = fsc.hdf5_io._sympy_load"],
        "fsc.hdf5_io.save": ["sympy = fsc.hdf5_io._sympy_save"],
    },
    long_description=README,
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Topic :: Utilities",
    ],
    license="Apache",
)
