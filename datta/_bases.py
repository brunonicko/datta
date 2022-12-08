from typing import TypeVar

import six
from estruttura import (
    BaseImmutableCollectionStructure,
    BaseImmutableStructure,
    BaseProxyImmutableCollectionStructure,
    BaseProxyImmutableStructure,
    BaseProxyStructureMeta,
    BaseProxyUserImmutableCollectionStructure,
    BaseProxyUserImmutableStructure,
    BaseStructureMeta,
    BaseUserImmutableCollectionStructure,
    BaseUserImmutableStructure,
)

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)


class BaseDataMeta(BaseStructureMeta):
    """Metaclass for :class:`BasePrivateData`."""


# noinspection PyAbstractClass
class BasePrivateData(six.with_metaclass(BaseDataMeta, BaseImmutableStructure)):
    """Base private data."""

    __slots__ = ()


BPD = TypeVar("BPD", bound=BasePrivateData)  # base private data self type


# noinspection PyAbstractClass
class BaseData(BasePrivateData, BaseUserImmutableStructure):
    """Base data."""

    __slots__ = ()


BD = TypeVar("BD", bound=BaseData)  # base data self type


class BaseProxyDataMeta(BaseDataMeta, BaseProxyStructureMeta):
    """Metaclass for :class:`BaseProxyPrivateData`."""


# noinspection PyAbstractClass
class BaseProxyPrivateData(six.with_metaclass(BaseProxyDataMeta, BaseProxyImmutableStructure[BPD], BasePrivateData)):
    """Base proxy private data."""

    __slots__ = ()


# noinspection PyAbstractClass
class BaseProxyData(BaseProxyPrivateData[BD], BaseProxyUserImmutableStructure[BD], BaseData):
    """Base proxy data."""

    __slots__ = ()


# noinspection PyAbstractClass
class PrivateDataCollection(BasePrivateData, BaseImmutableCollectionStructure[T_co]):
    """Private data collection."""

    __slots__ = ()


PDC = TypeVar("PDC", bound=PrivateDataCollection)  # private data collection self type


# noinspection PyAbstractClass
class DataCollection(PrivateDataCollection[T_co], BaseUserImmutableCollectionStructure[T_co]):
    """Base data collection."""

    __slots__ = ()

    def _do_clear(self):
        return type(self)()


DC = TypeVar("DC", bound=DataCollection)  # data collection self type


# noinspection PyAbstractClass
class ProxyPrivateDataCollection(
    BaseProxyPrivateData[PDC],
    BaseProxyImmutableCollectionStructure[PDC, T_co],
    PrivateDataCollection[T_co],
):
    """Proxy private data collection."""

    __slots__ = ()


# noinspection PyAbstractClass
class ProxyDataCollection(
    ProxyPrivateDataCollection[DC, T_co],
    BaseProxyUserImmutableCollectionStructure[DC, T_co],
    DataCollection[T_co],
):
    """Proxy data collection."""

    __slots__ = ()
