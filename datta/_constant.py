from __future__ import absolute_import, division, print_function

from basicco import type_checking
from tippo import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from tippo import Type

__all__ = ["Constant"]


T_co = TypeVar("T_co", covariant=True)


class Constant(Generic[T_co]):
    __slots__ = ("__value", "__types", "__subtypes")

    def __init__(self, value, types=(), subtypes=True):
        # type: (T_co, tuple[Type[T_co] | Type | str | None, ...] | Type[T_co] | Type | str | None, bool) -> None
        self.__value = value  # type: T_co
        self.__types = type_checking.format_types(types)  # type: tuple[Type[T_co] | Type | str, ...]
        self.__subtypes = bool(subtypes)

        if self.__types:
            type_checking.assert_is_instance(value, self.__types, subtypes=subtypes)

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

    @property
    def subtypes(self):
        # type: () -> bool
        return self.__subtypes
