from fsc.hdf5_io import subscribe_serialize, Serializable


@subscribe_serialize('test.simple_class')
class SimpleClass(Serializable):
    """
    Simple class that implements the Serializable concept.
    """

    def __init__(self, x):
        self.x = int(x)

    def to_hdf5(self, hdf5_handle):
        hdf5_handle['x'] = self.x

    @classmethod
    def from_hdf5(cls, hdf5_handle):
        return cls(x=hdf5_handle['x'].value)

    def __eq__(self, other):
        return self.x == other.x
