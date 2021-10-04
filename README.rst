Simple HDF5 serialization
=========================

The `fsc.hdf5-io` library provides a simple way to serialize Python objects to HDF5.

*   **Simple:** For plain data classes, HDF5 serialization can be added with just a few lines of code:

    .. code:: python

        from fsc.hdf5_io import save, load, subscribe_hdf5, SimpleHDF5Mapping

        @subscribe_hdf5("my_library.my_data_class")
        class MyDataClass(SimpleHDF5Mapping):
            HDF5_ATTRIBUTES = ["a", "b", "c"] # List attributes to serialize

            def __init__(self, a, b, c):
                self.a = a
                ...

       save(MyDataClass(a=2, b=[1, 2, 3], c="c"), "my_file.hdf5")
       new_object = load("my_file.hdf5")
    
*   **Batteries included:** Support for built-in types, numpy arrays, and sympy objects out of the box:

    .. code:: python

        import numpy as np

        save(np.array([1, 2, 3]), "array.hdf5")
        
*   **Customizable:** When needed, custom (de-)serialization can be defined:

    .. code:: python
    
        from fsc.hdf5_io import HDF5Enabled

        @subscribe_hdf5("my_library.my_complex_class")
        class MyComplexClass(HDF5Enabled):

            def to_hdf5(self, hdf5_handle):
                hdf5_handle['a'] = self.a
                
            @classmethod
            def from_hdf5(cls, hdf5_handle):
                return cls(a=hdf5_handle['a'][()])
    
*   **Mix and Match:** Arbitrary nesting of containers, and mixing of libraries:

    .. code:: python
    
        import sympy

        save(
            [
                "a", 
                {3: (1, 2, 3)}, 
                np.array([1, 2, 3]), 
                sympy.sympify("Matrix([[1, 2], [3, 4]])")
            ], 
            "nesting.hdf5"
        )


*   **Extensible:** Supports plugin hooks, so that libraries don't need to be explicitly imported before loading files.

    .. code:: python
    
        # Fresh Python interpreter, no other imports
        from fsc.hdf5_io import load
        
        # File saved above -- numpy and sympy need to be installed
        load("nesting.hdf5")


*   **Installation:** ``pip install fsc.hdf5-io``

*   **Documentation:** https://fsc-hdf5-io.readthedocs.io




