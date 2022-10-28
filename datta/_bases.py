import six
import estruttura
from tippo import TypeVar

from ._relationship import Relationship


T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)


class BaseDataMeta(estruttura.BaseStructureMeta):
    """Metaclass for :class:`BaseData`."""


# noinspection PyAbstractClass
class BaseData(six.with_metaclass(BaseDataMeta, estruttura.BaseImmutableStructure)):
    """Base data."""

    __slots__ = ()


# noinspection PyAbstractClass
class BaseDataCollection(BaseData, estruttura.BaseImmutableCollectionStructure[T_co]):
    relationship = Relationship()  # type: Relationship[T_co]

    __slots__ = ()
