from __future__ import absolute_import, division, print_function

from tippo import TYPE_CHECKING, Generic, TypeVar, cast

if TYPE_CHECKING:
    from tippo import Type

__all__ = ["Constant"]


T = TypeVar("T")


class Constant(Generic[T]):
    __slots__ = ("__value", "__types")

    def __init__(self, value, types=()):
        # type: (T, tuple[Type[T], ...] | Type[T]) -> None
        self.__value = value
        self.__types = types

    def __get__(self, instance, owner):
        # type: (...) -> T
        return self.__value

    @property
    def value(self):
        # type: () -> T
        return self.__value

    @property
    def types(self):
        # type: () -> tuple[Type[T], ...] | Type[T]
        return self.__types
