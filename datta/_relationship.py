import estruttura
from tippo import TypeVar, Callable, Any, Type, Iterable

from ._utils import auto_caller_module
from ._serializers import Serializer, TypedSerializer


T = TypeVar("T")


class Relationship(estruttura.Relationship[T]):
    __slots__ = ()


@auto_caller_module
def relationship(
    converter=None,  # type: Callable[[Any], T] | Type[T] | str | None
    validator=None,  # type: Callable[[Any], None] | str | None
    types=(),  # type: Iterable[Type[T] | str | None] | Type[T] | str | None
    subtypes=False,  # type: bool
    serializer=TypedSerializer(),  # type: Serializer[T] | None
    extra_paths=(),  # type: Iterable[str]
    builtin_paths=None,  # type: Iterable[str] | None
):
    # type: (...) -> Relationship[T]
    return Relationship(
        converter=converter,
        validator=validator,
        types=types,
        subtypes=subtypes,
        serializer=serializer,
        extra_paths=extra_paths,
        builtin_paths=builtin_paths,
    )
