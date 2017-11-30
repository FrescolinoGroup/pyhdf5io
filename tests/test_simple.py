"""
Defines a simple serializable class.
"""

import tempfile

from fsc.hdf5_io import subscribe_serialize, Serializable, save, load

@subscribe_serialize('simple_class')
class SimpleClass(Serializable):
    """
    A simple class implementing the Serializable concept.
    """
    def __init__(self, x):
        self.x = int(x)

    def to_hdf5(self, hdf5_handle):
        hdf5_handle['x'] = 5

    @classmethod
    def from_hdf5(cls, hdf5_handle):
        return cls(x=hdf5_handle['x'].value)


def test_simple_class():
    x = SimpleClass(5)
    with tempfile.NamedTemporaryFile() as nf:
        save(x, nf.name)
        y = load(nf.name)
    assert x.x == y.x
