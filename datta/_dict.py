from pyrsistent import pmap
from pyrsistent.typing import PMap
from estruttura import (
    ImmutableDictStructure,
    UserImmutableDictStructure,
)
from typing import TypeVar

from ._bases import (
    PrivateDataCollection,
    DataCollection,
    ProxyPrivateDataCollection,
    ProxyDataCollection,
)


KT = TypeVar("KT")
VT = TypeVar("VT")


class PrivateDictData(PrivateDataCollection[KT], ImmutableDictStructure[KT, VT]):
    """Private dictionary data."""

    __slots__ = ("_internal",)

    def __iter__(self):
        return iter(self._internal)

    def __len__(self):
        return len(self._internal)

    def __getitem__(self, key):
        return self._internal[key]

    def _hash(self):
        return hash(self._internal)

    def _eq(self, other):
        if isinstance(other, dict):
            return self._internal == other
        else:
            return isinstance(other, type(self)) and self._internal == other._internal

    def _do_init(self, initial_values):
        self._internal = pmap(initial_values)

    @classmethod
    def _do_deserialize(cls, values):
        self = cls.__new__(cls)
        self._internal = pmap(values)
        return self


class DictData(PrivateDictData[KT, VT], DataCollection[KT], UserImmutableDictStructure[KT, VT]):
    """Immutable dictionary data."""

    __slots__ = ()

    def _do_update(self, inserts, deletes, updates_old, updates_new, updates_and_inserts, all_updates):
        new_internal = dict((k, v) for k, v in self._internal.items() if k not in deletes)
        new_internal.update(updates_and_inserts)
        cls = type(self)
        new_self = cls.__new__(cls)
        new_self._internal = new_internal
        return new_self

    def _do_clear(self):
        return type(self)()
