from typing import TypeVar

from basicco import mapping_proxy
from estruttura import (
    ImmutableDictStructure,
    ProxyImmutableDictStructure,
    ProxyUserImmutableDictStructure,
    UserImmutableDictStructure,
)
from pyrsistent import pmap
from pyrsistent.typing import PMap

from ._bases import (
    DataCollection,
    PrivateDataCollection,
    ProxyDataCollection,
    ProxyPrivateDataCollection,
)

KT = TypeVar("KT")
VT = TypeVar("VT")


class PrivateDictData(PrivateDataCollection[KT], ImmutableDictStructure[KT, VT]):
    """Private dictionary data."""

    __slots__ = ("_state",)

    def __iter__(self):
        return iter(self._state)

    def __len__(self):
        return len(self._state)

    def __getitem__(self, key):
        return self._state[key]

    def _hash(self):
        return hash(self._state)

    def _eq(self, other):
        if isinstance(other, dict):
            return self._state == other
        else:
            return isinstance(other, type(self)) and self._state == other._state

    def _do_init(self, initial_values):
        # type: (mapping_proxy.MappingProxyType[KT, VT]) -> None
        self._state = pmap(initial_values)  # type: PMap[KT, VT]

    @classmethod
    def _do_deserialize(cls, values):
        self = cls.__new__(cls)
        self._state = pmap(values)
        return self


PDD = TypeVar("PDD", bound=PrivateDictData)  # private dictionary data self type


class DictData(PrivateDictData[KT, VT], DataCollection[KT], UserImmutableDictStructure[KT, VT]):
    """Dictionary data."""

    __slots__ = ()

    def _do_update(self, inserts, deletes, updates_old, updates_new, updates_and_inserts, all_updates):
        new_state = self._state.update(updates_and_inserts)
        if deletes:
            new_state_evolver = new_state.evolver()
            for key in deletes:
                del new_state_evolver[key]
            new_state = new_state_evolver.persistent()
        cls = type(self)
        new_self = cls.__new__(cls)
        new_self._state = new_state
        return new_self


DD = TypeVar("DD", bound=DictData)  # dictionary data self type


class ProxyPrivateDictData(
    ProxyPrivateDataCollection[PDD, KT],
    ProxyImmutableDictStructure[PDD, KT, VT],
    PrivateDictData[KT, VT],
):
    """Proxy private dictionary data."""

    __slots__ = ()


class ProxyDictData(
    ProxyDataCollection[DD, KT],
    ProxyPrivateDictData[DD, KT, VT],
    ProxyUserImmutableDictStructure[DD, KT, VT],
    DictData[KT, VT],
):
    """Proxy dictionary data."""

    __slots__ = ()
