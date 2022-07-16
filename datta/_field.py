from __future__ import absolute_import, division, print_function

import six
from basicco import type_checking, caller_module, import_path
from tippo import TYPE_CHECKING, Generic, TypeVar, cast

from ._sentinels import MissingType, MISSING

if TYPE_CHECKING:
    from tippo import Any, Type, Callable, Iterable

__all__ = ["Field"]


T_co = TypeVar("T_co", covariant=True)


class Field(Generic[T_co]):
    __slots__ = (
        "__default",
        "__converter",
        "__factory",
        "__types",
        "__init",
        "__repr",
        "__eq",
        "__hash",
        "__subtypes",
        "__settable",
        "__deletable",
        "__required",
        "__module",
        "__builtin_paths",
        "__metadata",
        "__order",
        "__has_default",
    )
    __counter = 0

    def __init__(
        self,
        default=MISSING,  # type: T_co | MissingType
        converter=None,  # type: Callable[[Any], T_co] | Type[T_co] | str | None
        factory=MISSING,  # type: Callable[..., T_co] | MissingType
        types=(),  # type: tuple[Type[T_co] | Type | str | None, ...] | Type[T_co] | Type | str | None
        init=True,  # type: bool
        repr=True,  # type: bool
        eq=True,  # type: bool
        hash=None,  # type: bool | None
        subtypes=True,  # type: bool
        settable=True,  # type: bool
        deletable=False,  # type: bool
        required=True,  # type: bool
        module=None,  # type: str | None
        builtin_paths=type_checking.DEFAULT_BUILTIN_PATHS,  # type: Iterable[str]
        metadata=None,  # type: Any
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
        self.__default = default
        self.__converter = converter
        self.__factory = factory
        self.__types = type_checking.format_types(types)  # type: tuple[Type[T_co] | Type | str, ...]
        self.__init = bool(init)
        self.__repr = bool(repr)
        self.__eq = bool(eq)
        self.__hash = bool(hash)
        self.__subtypes = bool(subtypes)
        self.__settable = bool(settable)
        self.__deletable = bool(deletable)
        self.__required = bool(required)
        self.__module = module if module is not None else caller_module.caller_module()
        self.__builtin_paths = ((self.__module,) if self.__module is not None else ()) + tuple(builtin_paths)
        self.__metadata = metadata

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

    def convert(self, value):
        # type: (Any) -> T_co
        if self.converter is not None:
            converter = self.converter
            if isinstance(converter, six.string_types):
                converter = import_path.import_path(converter, builtin_paths=self.builtin_paths)
            assert callable(converter)
            return converter(value)
        return value

    def check(self, value):
        # type: (Any) -> None
        if self.types:
            type_checking.assert_is_instance(
                value,
                self.types,
                subtypes=self.subtypes,
                builtin_paths=self.builtin_paths,
            )

    @property
    def default(self):
        # type: () -> T_co | MissingType
        return self.__default

    @property
    def converter(self):
        # type: () -> Callable[[Any], T_co] | str | None
        return self.__converter

    @property
    def factory(self):
        # type: () -> T_co | Callable[..., T_co] | MissingType
        return self.__factory

    @property
    def types(self):
        # type: () -> tuple[Type[T_co] | Type | str, ...]
        return self.__types

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
    def subtypes(self):
        # type: () -> bool
        return self.__subtypes

    @property
    def settable(self):
        # type: () -> bool
        return self.__settable

    @property
    def deletable(self):
        # type: () -> bool
        return self.__deletable

    @property
    def required(self):
        # type: () -> bool
        return self.__required

    @property
    def module(self):
        # type: () -> str | None
        return self.__module

    @property
    def builtin_paths(self):
        # type: () -> tuple[str, ...]
        return self.__builtin_paths

    @property
    def order(self):
        # type: () -> int
        return self.__order

    @property
    def has_default(self):
        # type: () -> bool
        return self.__has_default
