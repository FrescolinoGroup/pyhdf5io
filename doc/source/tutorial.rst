Tutorial
========

In this tutorial we'll see how to add HDF5 serialization to classes. Let's start with defining a simple class:

.. ipython::

    In [0]: class Snek:
       ...:     def __init__(self, length):
       ...:         self.length = length
       ...:     def __repr__(self):
       ...:         return '≻:' + '=' * self.length + '>···'
       ...:

    In [0]: Snek(10)


To make this Snek HDF5 serializable, we need to answer these questions three:

1. How is the Snek serialized to HDF5?
2. How is the HDF5 converted back into a Snek?
3. What is :strike:`your favourite colour` the unique tag identifying the Snek class?

To define how the Snek is serialized to HDF5, we add a ``to_hdf5`` method. This method is passed a ``hdf5_handle``, which is a :py:class:`h5py.File<File>` or :py:class:`h5py.Group<Group>` defining the (current) root of the HDF5 file where the object should be added.

For de-serialization, the ``from_hdf5`` classmethod should be implemented. Again, this method is passed a ``hdf5_handle``. It should return the deserialized object.

Finally, the :func:`.subscribe_hdf5` class decorator is used to define a unique ``type_tag`` which identifies this class.

.. note::

    The ``type_tag`` needs to be unique across all projects using ``fsc.hdf5_io``. For this reason, you should always prepend it with the name of your module.


.. ipython::

    In [0]: from fsc.hdf5_io import subscribe_hdf5, HDF5Enabled

    In [0]: @subscribe_hdf5('my_snek_module.snek')
       ...: class HDF5Snek(Snek, HDF5Enabled):
       ...:     def to_hdf5(self, hdf5_handle):
       ...:         hdf5_handle['length'] = self.length
       ...:     @classmethod
       ...:     def from_hdf5(cls, hdf5_handle):
       ...:         return cls(hdf5_handle['length'][()])
       ...:

    In [0]: HDF5Snek(12)

Notice also that we inherit from :class:`.HDF5Enabled`. This abstract base class checks for the existence of the HDF5 (de-)serialization functions, and adds methods ``to_hdf5_file`` and ``from_hdf5_file`` to save and load directly to a file.

Now we can use the :func:`.save` and :func:`.load` methods to save and load Sneks in HDF5 format:

.. ipython::

    In [0]: from fsc.hdf5_io import save, load

    In [0]: from tempfile import NamedTemporaryFile

    In [0]: mysnek = HDF5Snek(12)

    In [0]: with NamedTemporaryFile() as f:
       ...:     save(mysnek, f.name)
       ...:     snek_clone = load(f.name)

    In [0]: snek_clone


You can also save and load lists or dictionaries containing Sneks:

.. ipython::

    In [0]: with NamedTemporaryFile() as f:
       ...:     save([HDF5Snek(2), HDF5Snek(4)], f.name)
       ...:     snek_2, snek_4 = load(f.name)

    In [0]: print(snek_2, snek_4)


A common use case is to serialize all the attributes of an object, a base
class :class:`.SimpleHDF5Mapping` exists for this case. A subclass needs to
define a lists ``HDF5_ATTRIBUTES`` of attributes that should be serialized.
The attribute names must be the same as the arguments accepted by the
constructor.

We can re-write the ``Snek`` as

.. ipython::

    In [0]: from fsc.hdf5_io import SimpleHDF5Mapping

    In [0]: @subscribe_hdf5('my_snek_module.simplified_snek')
       ...: class SimplifiedHDF5Snek(Snek, SimpleHDF5Mapping):
       ...:     HDF5_ATTRIBUTES = ['length']

    In [0]: new_snek = SimplifiedHDF5Snek(9)

    In [0]: with NamedTemporaryFile() as f:
       ...:     save(new_snek, f.name)
       ...:     new_snek_clone = load(f.name)

    In [0]: new_snek_clone

We can extend the Snek functionality by adding a list of friends:

.. ipython::

    In [0]: @subscribe_hdf5('my_snek_module.snek_with_friends')
       ...: class SnekWithFriends(SimplifiedHDF5Snek):
       ...:     HDF5_ATTRIBUTES = SimplifiedHDF5Snek.HDF5_ATTRIBUTES + ['friends']
       ...:     def __init__(self, length, friends):
       ...:         super().__init__(length)
       ...:         self.friends = friends

    In [0]: snek_with_friends = SnekWithFriends(3, friends=[mysnek, new_snek])

    In [0]: snek_with_friends

    In [0]: snek_with_friends.friends

    In [0]: with NamedTemporaryFile() as f:
       ...:     save(snek_with_friends, f.name)
       ...:     snek_with_friends_clone = load(f.name)

    In [0]: snek_with_friends_clone

    In [0]: snek_with_friends_clone.friends
