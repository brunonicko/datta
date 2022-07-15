from __future__ import absolute_import, division, print_function

from basicco import type_checking
from tippo import TYPE_CHECKING, Generic, TypeVar, cast

from ._sentinels import MissingType, MISSING

if TYPE_CHECKING:
    from tippo import Type, Callable

__all__ = ["Field"]


T_co = TypeVar("T_co", covariant=True)


class Field(Generic[T_co]):
    __slots__ = (
        "__order",
        "__types",
        "__default",
        "__factory",
        "__init",
        "__repr",
        "__eq",
        "__hash",
        "__subtypes",
        "__has_default",
    )
    __counter = 0

    def __init__(
        self,
        types=(),  # type: tuple[Type[T_co] | Type | str | None, ...] | Type[T_co] | Type | str | None
        default=MISSING,  # type: T_co | MissingType
        factory=MISSING,  # type: Callable[..., T_co] | MissingType
        init=True,  # type: bool
        repr=True,  # type: bool
        eq=True,  # type: bool
        hash=None,  # type: bool | None
        subtypes=True,  # type: bool
    ):
        # type: (...) -> None

        # Defaults.
        has_default = default is not MISSING
        has_factory = factory is not MISSING
        if has_default and has_factory:
            error = "can't have both default and default factory"
            raise ValueError(error)

        # Increment global counter for field ordering.
        Field.__counter += 1

        # Store attributes.
        self.__types = type_checking.format_types(types)  # type: tuple[Type[T_co] | Type | str, ...]
        self.__default = default
        self.__factory = factory
        self.__init = bool(init)
        self.__repr = bool(repr)
        self.__eq = bool(eq)
        self.__hash = bool(hash)
        self.__subtypes = bool(subtypes)

        self.__order = Field.__counter
        self.__has_default = has_default or has_factory

    def __get__(self, instance, owner):
        # type: (...) -> T_co
        return cast(T_co, NotImplemented)

    def get_default(self):
        # type: () -> T_co
        if self.__default is not MISSING:
            return self.__default
        if self.__factory is not MISSING:
            return self.__factory()
        error = "field has no default"
        raise RuntimeError(error)

    @property
    def order(self):
        # type: () -> int
        return self.__order

    @property
    def default(self):
        # type: () -> T_co | MissingType
        return self.__default

    @property
    def factory(self):
        # type: () -> T_co | Callable[..., T_co] | MissingType
        return self.__factory

    @property
    def init(self):
        # type: () -> bool
        return self.__init

    @property
    def eq(self):
        # type: () -> bool
        return self.__eq

    @property
    def repr(self):
        # type: () -> bool
        return self.__repr

    @property
    def types(self):
        # type: () -> tuple[Type[T_co] | Type | str, ...]
        return self.__types

    @property
    def subtypes(self):
        # type: () -> bool
        return self.__subtypes

    @property
    def has_default(self):
        # type: () -> bool
        return self.__has_default
