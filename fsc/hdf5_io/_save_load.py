"""
Defines free functions to serialize / deserialize bands-inspect objects to HDF5.
"""

from functools import lru_cache, singledispatch

import h5py

from fsc.export import export

from ._subscribe import SERIALIZE_MAPPING, TYPE_TAG_KEY

__all__ = ["save", "load"]


@lru_cache(maxsize=None)
def _get_entrypoint_mapping(group):
    """
    Helper function to get the entry point mapping corresponding to a
    given group name
    """
    import pkg_resources  # pylint: disable=import-outside-toplevel

    return {ep.name: ep for ep in pkg_resources.iter_entry_points(group=group)}


def _try_loading_parts(*, identifier, entry_point_mapping):
    """
    Helper function to load an entrypoint corresponding to the given
    identifier. If an exact match for the identifier is not found, the
    colon-separated "parent identifiers" will be checked.

    For example, for an entry point named 'nobody.expects.the',
    it will check 'nobody.expects.the', 'nobody.expects', 'nobody', in
    that order.

    :param identifier: The identifier for which an entrypoint is to be loaded.
    :type identifier: str

    :param entry_point_mapping: A mapping between entrypoint names and the entrypoints themselves.
    :type entry_point_mapping: dict

    :returns: The name of the entry point that was loaded (if any), or False.
    """
    split_identifier = identifier.split(".")
    for partial_identifier_length in range(len(split_identifier), 0, -1):
        partial_identifier = ".".join(split_identifier[:partial_identifier_length])
        if partial_identifier in entry_point_mapping:
            entry_point_mapping[partial_identifier].load()
            return partial_identifier
    return False


@export
def from_hdf5(hdf5_handle):
    """
    Deserializes the given HDF5 handle into an object.

    :param hdf5_handle: HDF5 location where the serialized object is stored.
    :type hdf5_handle: :py:class:`h5py.File<File>` or :py:class:`h5py.Group<Group>`.
    """
    try:
        type_tag = hdf5_handle[TYPE_TAG_KEY][()].decode("utf-8")
    except KeyError as err:
        raise ValueError(
            f"HDF5 object '{hdf5_handle.name}' cannot be de-serialized: No type information given."
        ) from err
    try:
        obj_class = SERIALIZE_MAPPING[type_tag]
    except KeyError as err:
        partial_tag = _try_loading_parts(
            identifier=type_tag,
            entry_point_mapping=_get_entrypoint_mapping("fsc.hdf5_io.load"),
        )
        if not partial_tag:
            raise KeyError(
                f"Unknown {TYPE_TAG_KEY} '{type_tag}'. The module defining this class has not been imported, and no matching entry point was found."
            ) from err
        try:
            obj_class = SERIALIZE_MAPPING[type_tag]
        except KeyError as err2:
            raise KeyError(
                f"Unknown {TYPE_TAG_KEY} '{type_tag}'. The module defining this class has not been imported, even after loading entry point {partial_tag}."
            ) from err2
    return obj_class.from_hdf5(hdf5_handle)


@export
def to_hdf5(obj, hdf5_handle):
    """
    Serializes a given object to HDF5 format.

    :param obj: Object to serialize.

    :param hdf5_handle: HDF5 location where the serialized object gets stored.
    :type hdf5_handle: :py:class:`h5py.File<File>` or :py:class:`h5py.Group<Group>`.
    """
    if hasattr(obj, "to_hdf5"):
        obj.to_hdf5(hdf5_handle)
    else:
        try:
            to_hdf5_singledispatch(obj, hdf5_handle)
        except SerializerNotFound as exc:
            objtype = type(obj)
            objmodule = objtype.__module__
            if objmodule is None:
                fullname = objtype.__qualname__
            else:
                fullname = objmodule + "." + objtype.__qualname__

            if not _try_loading_parts(
                identifier=fullname,
                entry_point_mapping=_get_entrypoint_mapping("fsc.hdf5_io.save"),
            ):
                raise TypeError(
                    f"Cannot serialize object of type '{fullname}', and no corresponding entry point found."
                ) from exc
            to_hdf5_singledispatch(obj, hdf5_handle)


class SerializerNotFound(TypeError):
    """
    Error to raise when the singledispatch for serializing an object to
    HDF5 format fails to find a matching function.
    """


@export
@singledispatch
def to_hdf5_singledispatch(obj, hdf5_handle):
    """
    Singledispatch function which is called to serialize and object when it does not have a ``to_hdf5`` method.

    :param obj: Object to serialize.

    :param hdf5_handle: HDF5 location where the serialized object gets stored.
    :type hdf5_handle: :py:class:`h5py.File<File>` or :py:class:`h5py.Group<Group>`.
    """
    raise SerializerNotFound(f"Cannot serialize object '{obj}' of type '{type(obj)}'")


@export
def from_hdf5_file(hdf5_file):
    """
    Loads the object from a file in HDF5 format.

    :param hdf5_file: Path of the file.
    :type hdf5_file: str
    """
    with h5py.File(hdf5_file, "r") as f:
        return from_hdf5(f)


load = from_hdf5_file  # pylint: disable=invalid-name
load.__doc__ = """Alias for :func:`from_hdf5_file`."""


@export
def to_hdf5_file(obj, hdf5_file):
    """
    Saves the object to a file, in HDF5 format.

    :param obj: The object to be saved.

    :param hdf5_file: Path of the file.
    :type hdf5_file: str
    """
    with h5py.File(hdf5_file, "w") as f:
        to_hdf5(obj, f)


save = to_hdf5_file  # pylint: disable=invalid-name
save.__doc__ = """Alias for :func:`to_hdf5_file`."""
