from __future__ import absolute_import, division, print_function

from basicco import type_checking
from tippo import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from tippo import Type

__all__ = ["Constant"]


T_co = TypeVar("T_co", covariant=True)


class Constant(Generic[T_co]):
    __slots__ = ("__value", "__types")

    def __init__(self, value, types=()):
        # type: (T_co, tuple[Type[T_co] | Type | str | None, ...] | Type[T_co] | Type | str | None) -> None
        self.__value = value
        self.__types = type_checking.format_types(types)

    def __get__(self, instance, owner):
        # type: (...) -> T_co
        return self.__value

    @property
    def value(self):
        # type: () -> T_co
        return self.__value

    @property
    def types(self):
        # type: () -> tuple[Type[T_co] | Type | str, ...]
        return self.__types
