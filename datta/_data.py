from typing import TypeVar

import six
from basicco import mangling, mapping_proxy
from estruttura import (
    ImmutableStructure,
    ProxyImmutableStructure,
    ProxyStructureMeta,
    ProxyUserImmutableStructure,
    StructureMeta,
    UserImmutableStructure,
)

from ._attribute import Attribute
from ._bases import (
    BaseData,
    BaseDataMeta,
    BasePrivateData,
    BaseProxyData,
    BaseProxyDataMeta,
    BaseProxyPrivateData,
)

KT = TypeVar("KT")
VT = TypeVar("VT")


class DataMeta(StructureMeta, BaseDataMeta):
    @staticmethod
    def __edit_dct__(this_attribute_map, attribute_map, name, bases, dct, **kwargs):  # noqa
        slots = list(dct.get("__slots__", ()))
        for attribute_name, attribute in six.iteritems(this_attribute_map):
            if attribute.constant:
                dct[attribute_name] = attribute.default
            else:
                slots.append(mangling.mangle(attribute_name, name))
                del dct[attribute_name]
        dct["__slots__"] = tuple(slots)
        return dct


class PrivateData(six.with_metaclass(DataMeta, BasePrivateData, ImmutableStructure)):
    """Private data."""

    __slots__ = ()

    __attribute_type__ = Attribute

    def __getitem__(self, name):
        return getattr(self, name)

    def __contains__(self, name):
        return isinstance(name, six.string_types) and name in type(self).__attribute_map__ and hasattr(self, name)

    def __setattr__(self, name, value):
        if name in type(self).__attribute_map__:
            error = "{!r} objects are immutable".format(type(self).__name__)
            raise AttributeError(error)
        super(PrivateData, self).__setattr__(name, value)

    def _do_init(self, initial_values):
        # type: (mapping_proxy.MappingProxyType) -> None
        for name, value in six.iteritems(initial_values):
            object.__setattr__(self, name, value)

    @classmethod
    def _do_deserialize(cls, values):
        self = cls.__new__(cls)
        self._do_init(values)
        return self


PD = TypeVar("PD", bound=PrivateData)  # private dictionary data self type


class Data(PrivateData, BaseData, UserImmutableStructure):
    """Data."""

    __slots__ = ()

    def _do_update(self, inserts, deletes, updates_old, updates_new, updates_and_inserts, all_updates):
        cls = type(self)
        new_self = cls.__new__(cls)
        new_self._do_init(updates_and_inserts)
        return new_self


D = TypeVar("D", bound=Data)  # dictionary data self type


class ProxyDataMeta(BaseProxyDataMeta, ProxyStructureMeta, DataMeta):
    pass


class ProxyPrivateData(
    six.with_metaclass(
        ProxyDataMeta,
        BaseProxyPrivateData[PD],
        ProxyImmutableStructure[PD],
        PrivateData,
    )
):
    """Proxy private data."""

    __slots__ = ()


class ProxyData(BaseProxyData[D], ProxyPrivateData[D], ProxyUserImmutableStructure[D], Data):
    """Proxy data."""

    __slots__ = ()
