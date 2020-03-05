Entry points
============

The (de-)serialization methods registered with ``fsc.hdf5-io`` are only available once the Python module defining them has been loaded. To avoid having to explicitly ``import`` all necessary modules before loading a module, ``fsc.hdf5-io`` defines two *entry point groups*:

Serialization: ``fsc.hdf5_io.save``
-----------------------------------

When a Python object whose serialization is not defined is encountered, ``fsc.hdf5-io`` will load (if it exists) the entry point corresponding to the full name of the object's class in the ``fsc.hdf5_io.save`` entrypoint. If there is no entry point for the *exact* Python name, it will also try its module name(s).

For example, if a ``scipy.sparse.csr.csr_matrix`` should be serialized, it will first check for an entry point named ``scipy.sparse.csr.csr_matrix`` in ``fsc.hdf5_io.save``. If this entry point does not exist, it will try ``scipy.sparse.csr``, ``scipy.sparse``, and ``scipy``, stopping at the first entry point that exists.

If you were to define serialization for all ``scipy.sparse`` objects in a module called ``scipy_helpers.sparse.hdf5_io``, you could define the following entry point in the module ``setup.py`` (as an argument to the ``setup`` function):

.. code :: python

    entry_points={
        'fsc.hdf5_io.save': ['scipy.sparse = scipy_helpers.sparse.hdf5_io']
    }

Deserialization: ``fsc.hdf5_io.load``
-------------------------------------

The same principle applies for deserializing HDF5 objects, but the entry point names go by ``type_tag`` instead. For example, if you define ``your_module`` with type tags ``your_module.some_object`` and ``your_module.another_object``, you have two choices:

If the top-level import of ``your_module`` loads all the submodules needed to deserialize both classes, the following configuration enables autoloading:

.. code :: python

    entry_points={
        'fsc.hdf5_io.load': ['your_module = your_module']
    }

If instead they are in two separate submodules ``some_object_submodule`` and ``another_object_submodule`` that are *not* loaded when simply importing ``your_module``, you need to define two entry points:

.. code :: python

    entry_points={
        'fsc.hdf5_io.load': [
            'your_module.some_object = your_module.some_object_submodule',
            'your_module.another_object = your_module.another_object_submodule',
        ]
    }

As a real-world example, ``fsc.hdf5-io`` itself uses entry points to define the (de-)serialization of ``sympy`` objects, without always having to import ``sympy``.
