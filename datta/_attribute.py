import estruttura
from tippo import Any, Iterable, Callable, TypeVar, Type, cast

from ._utils import auto_caller_module
from ._constants import MissingType, MISSING
from ._relationship import Relationship
from ._serializers import Serializer, TypedSerializer


T = TypeVar("T")


class Attribute(estruttura.Attribute[T]):
    __slots__ = ()


getter = estruttura.getter
setter = estruttura.setter
deleter = estruttura.deleter


@auto_caller_module
def attribute(
    default=MISSING,  # type: T | MissingType
    factory=MISSING,  # type: Callable[..., T] | str | MissingType
    converter=None,  # type: Callable[[Any], T] | Type[T] | str | None
    validator=None,  # type: Callable[[Any], None] | str | None
    types=(),  # type: Iterable[Type[T] | str | None] | Type[T] | str | None
    subtypes=False,  # type: bool
    serializer=TypedSerializer(),  # type: Serializer[T] | None
    required=None,  # type: bool | None
    init=None,  # type: bool | None
    settable=None,  # type: bool | None
    deletable=None,  # type: bool | None
    serializable=None,  # type: bool | None
    serialize_as=None,  # type: str | None
    serialize_default=True,  # type: bool
    constant=False,  # type: bool
    repr=None,  # type: bool | None
    eq=None,  # type: bool | None
    order=None,  # type: bool | None
    hash=None,  # type: bool | None
    doc="",  # type: str
    metadata=None,  # type: Any
    extra_paths=(),  # type: Iterable[str]
    builtin_paths=None,  # type: Iterable[str] | None
):
    # type: (...) -> T
    return cast(
        T,
        Attribute(
            default=default,
            factory=factory,
            relationship=Relationship(
                converter=converter,
                validator=validator,
                types=types,
                subtypes=subtypes,
                serializer=serializer,
                extra_paths=extra_paths,
                builtin_paths=builtin_paths,
            ),
            required=required,
            init=init,
            settable=settable,
            deletable=deletable,
            serializable=serializable,
            serialize_as=serialize_as,
            serialize_default=serialize_default,
            constant=constant,
            repr=repr,
            eq=eq,
            order=order,
            hash=hash,
            doc=doc,
            metadata=metadata,
            extra_paths=extra_paths,
            builtin_paths=builtin_paths,
        )
    )
