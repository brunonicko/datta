import copy

import six
from basicco.runtime_final import final
from estruttura import (
    BaseImmutableCollectionStructure,
    BaseImmutableStructure,
    BaseStructureMeta,
    BaseUserImmutableCollectionStructure,
    BaseUserImmutableStructure,
)
from tippo import TypeVar

from ._relationship import Relationship

T_co = TypeVar("T_co", covariant=True)


class BaseDataMeta(BaseStructureMeta):
    """Metaclass for :class:`BasePrivateData`."""


# noinspection PyAbstractClass
class BasePrivateData(six.with_metaclass(BaseDataMeta, BaseImmutableStructure)):
    """Base private data."""

    __slots__ = ("__hash",)

    @final
    def __cache_hash__(self, hash_):
        self.__hash = hash_

    @final
    def __retrieve_hash__(self):
        try:
            return self.__hash
        except AttributeError:
            self.__hash = None
            return None

    @final
    def _do_copy(self):
        return copy.copy(self)


# noinspection PyAbstractClass
class BaseData(BasePrivateData, BaseUserImmutableStructure):
    """Base data."""

    __slots__ = ("__hash",)


# noinspection PyAbstractClass
class PrivateDataCollection(BasePrivateData, BaseImmutableCollectionStructure[T_co]):
    """Private data collection."""

    __slots__ = ()

    relationship = Relationship()  # type: Relationship[T_co]


# noinspection PyAbstractClass
class DataCollection(PrivateDataCollection[T_co], BaseUserImmutableCollectionStructure[T_co]):
    """Base data collection."""

    __slots__ = ()
