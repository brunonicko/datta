from __future__ import absolute_import, division, print_function

import collections
import copy
import inspect
import types

import six
from basicco import mapping_proxy, scrape_class, mangling, type_checking
from tippo import TYPE_CHECKING, cast

from ._field import Field
from ._constant import Constant
from ._sentinels import DELETE

if TYPE_CHECKING:
    from tippo import Any, Type

__all__ = ["FieldScraper", "ConstantScraper", "DataMeta", "Data", "evolve", "fields", "constants"]


_READ_ONLY_ATTRS = {"__fields__", "__constants__", "__slots__"}


class FieldScraper(object):
    """Scrapes all fields in a Data class."""

    __slots__ = ("__cls", "__cls_fields", "__field_order")

    def __init__(self, cls, _cls_fields=None):
        # type: (DataMeta, dict[str, Field] | None) -> None
        self.__cls = cls  # type: DataMeta
        self.__cls_fields = _cls_fields  # type: dict[str, Field] | None
        self.__field_order = {}  # type: dict[str, int]

    def scrape(self):
        # type: () -> mapping_proxy.MappingProxyType[str, Field]

        # Reset field order.
        self.__field_order = {}

        # Scrape class for fields.
        cls_fields = scrape_class.scrape_class(
            self.__cls,
            member_filter=self.__member_filter,  # type: ignore
            override_filter=self.__override_filter,  # type: ignore
            member_replacer=self.__field_replacer,  # type: ignore
        )  # type: dict[str, Field]

        # Order fields.
        ordered_fields = collections.OrderedDict()
        for field_name, field in sorted(cls_fields.items(), key=lambda i: self.__field_order[i[0]]):
            ordered_fields[field_name] = field

        return mapping_proxy.MappingProxyType(ordered_fields)

    def __get_field(self, cls, name):
        # type: (DataMeta, str) -> Field | None
        if self.__cls_fields is not None and cls is self.__cls:
            return self.__cls_fields.get(name)
        else:
            return cls.__fields__.get(name)

    def __member_filter(self, base, member_name, _member):
        # type: (Type, str, Any) -> bool
        assert member_name not in self.__field_order

        # Skip non-data base classes.
        if not isinstance(base, DataMeta):
            return False

        # Get field from data class.
        field = self.__get_field(cast(DataMeta, base), member_name)  # type: Field | None
        if field is not None:
            self.__field_order[member_name] = field.order
            return True

        return False

    def __override_filter(self, base, member_name, member, previous_member):
        # type: (Type, str, Any, Any) -> bool

        # Can't override fields if non-data class.
        if not isinstance(base, DataMeta):
            error = "non-data {!r} base overrides {} {!r}".format(
                base.__name__,
                type(previous_member).__name__.lower(),
                member_name,
            )
            raise TypeError(error)

        # Can't override fields with non-fields.
        field = self.__get_field(cast(DataMeta, base), member_name)  # type: Field | None
        if field is None:
            error = "{!r} base overrides {} {!r} with a {!r} object".format(
                base.__name__,
                type(previous_member).__name__.lower(),
                member_name,
                type(member).__name__,
            )
            raise TypeError(error)

        # TODO: liskov check
        return True

    def __field_replacer(self, base, member_name, _member):
        # type: (DataMeta, str, types.MemberDescriptorType) -> Field
        field = self.__get_field(base, member_name)
        assert field is not None
        return field


class ConstantScraper(object):
    __slots__ = ("__cls", "__cls_constants")

    def __init__(self, cls, _cls_constants=None):
        # type: (DataMeta, dict[str, Constant] | None) -> None
        self.__cls = cls  # type: DataMeta
        self.__cls_constants = _cls_constants  # type: dict[str, Constant] | None

    def scrape(self):
        # type: () -> mapping_proxy.MappingProxyType[str, Constant]

        # Scrape class for constants.
        cls_constants = scrape_class.scrape_class(
            self.__cls,
            member_filter=self.__member_filter,  # type: ignore
            override_filter=self.__override_filter,  # type: ignore
            member_replacer=self.__constant_replacer,  # type: ignore
        )  # type: dict[str, Constant]
        return mapping_proxy.MappingProxyType(cls_constants)

    def __get_constant(self, cls, name):
        # type: (DataMeta, str) -> Constant | None
        if self.__cls_constants is not None and cls is self.__cls:
            return self.__cls_constants.get(name)
        else:
            return cls.__constants__.get(name)

    def __member_filter(self, base, member_name, _member):
        # type: (Type, str, Any) -> bool

        # Skip non-data base classes.
        if not isinstance(base, DataMeta):
            return False

        # Get constant from data class.
        constant = self.__get_constant(cast(DataMeta, base), member_name)  # type: Constant | None
        return constant is not None

    def __override_filter(self, base, member_name, member, previous_member):
        # type: (Type, str, Any, Any) -> bool

        # Can't override constants if non-data class.
        if not isinstance(base, DataMeta):
            error = "non-data {!r} base overrides {} {!r}".format(
                base.__name__,
                type(previous_member).__name__.lower(),
                member_name,
            )
            raise TypeError(error)

        # Can't override constants with non-constants.
        constant = self.__get_constant(cast(DataMeta, base), member_name)  # type: Constant | None
        if constant is None:
            error = "{!r} base overrides {} {!r} with a {!r} object".format(
                base.__name__,
                type(previous_member).__name__.lower(),
                member_name,
                type(member).__name__,
            )
            raise TypeError(error)

        # TODO: liskov check
        return True

    def __constant_replacer(self, base, member_name, _member):
        # type: (DataMeta, str, types.MemberDescriptorType) -> Constant
        constant = self.__get_constant(base, member_name)
        assert constant is not None
        return constant


class DataMeta(type):
    __constants__ = {}  # type: dict[str, Constant]
    __fields__ = {}  # type: dict[str, Field]

    def __new__(mcs, name, bases, dct, **kwargs):

        # Gather fields for this class and convert them to slots.
        this_fields = {n: dct.pop(n) for n, f in list(dct.items()) if isinstance(f, Field)}
        sorted_slots = tuple(
            mangling.unmangle(n, name) for n, f in sorted(this_fields.items(), key=lambda i: i[1].order)
        )
        dct["__slots__"] = tuple(dct.get("__slots__", ())) + sorted_slots
        dct["__fields__"] = None

        # Gather constants for this class and convert them to class attributes.
        this_constants = {n: c.value for n, c in dct.items() if isinstance(c, Constant)}
        dct.update(this_constants)
        dct["__constants__"] = None

        # Build class.
        cls = super(DataMeta, mcs).__new__(mcs, name, bases, dct, **kwargs)

        # Make sure all bases have slots.
        for base in reversed(inspect.getmro(cls)):
            if base is object:
                continue
            if isinstance(base.__dict__.get("__dict__"), types.GetSetDescriptorType):
                error = "base {!r} does not define '__slots__'".format(base.__name__)
                raise TypeError(error)

        # Scrape fields.
        all_fields = FieldScraper(cls, this_fields).scrape()
        type.__setattr__(cls, "__fields__", all_fields)

        # Scrape constants.
        all_constants = ConstantScraper(cls, this_constants).scrape()
        type.__setattr__(cls, "__constants__", all_constants)

        return cls

    def __setattr__(cls, name, value):
        if name in _READ_ONLY_ATTRS or name in cls.__fields__ or name in cls.__constants__:
            error = "can't set read-only class attribute {!r}".format(name)
            raise AttributeError(error)
        super(DataMeta, cls).__setattr__(name, value)

    def __delattr__(cls, name):
        if name in _READ_ONLY_ATTRS or name in cls.__fields__ or name in cls.__constants__:
            error = "can't delete read-only class attribute {!r}".format(name)
            raise AttributeError(error)
        super(DataMeta, cls).__delattr__(name)


class Data(six.with_metaclass(DataMeta, object)):
    __slots__ = ("__hash",)
    __constants__ = {}  # type: dict[str, Constant]
    __fields__ = {}  # type: dict[str, Field]

    def __init__(self, *args, **kwargs):  # TODO
        for (field_name, field), value in zip(self.__fields__.items(), args):
            self.__setfield__(field_name, value)
        for field_name, value in kwargs.items():
            self.__setfield__(field_name, value)

    def __repr__(self):
        repr_args = []
        for field_name, field in self.__fields__.items():
            if not field.repr or not hasattr(self, field_name):
                continue
            value = getattr(self, field_name)
            if not field.has_default and field.init:
                repr_args.append("{!r}".format(value))
            else:
                repr_args.append("{}={!r}".format(field_name, value))
        return "{}({})".format(type(self).__name__, ", ".join(repr_args))

    def __hash__(self):
        try:

            # Try to use cached hash value.
            return self.__hash

        except AttributeError:

            # Calculate hash, cache it, and return it.
            self.__hash = hash(tuple(self))
            return self.__hash

    def __eq__(self, other):
        return type(self) is type(other) and dict(self) == dict(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __getstate__(self):

        # Gather slot names from all bases.
        slots = set()
        for base in inspect.getmro(type(self))[::-1][1:]:
            for slot in getattr(base, "__slots__", ()):

                # Skip hash cache.
                if base is Data and slot == "__hash":
                    continue

                # Add privatized slot name.
                if slot.startswith("__") and not slot.endswith("__"):
                    slot = "_{}{}".format(base.__name__.lstrip("_"), slot)
                slots.add(slot)

        # Store state value for each slot.
        state = {}
        for slot in slots:
            if slot == "__weakref__":
                continue
            try:
                value = object.__getattribute__(self, slot)
            except AttributeError:
                continue
            state[slot] = value

        return state

    def __setstate__(self, state):
        for name, value in state.items():
            object.__setattr__(self, name, value)

    def __iter__(self):
        for field_name in self.__fields__:
            try:
                value = object.__getattribute__(self, field_name)
            except AttributeError:
                continue
            yield field_name, value

    def __setfield__(self, name, value):
        field = self.__fields__[name]
        if field.types:
            type_checking.assert_is_instance(value, field.types)
        super(Data, self).__setattr__(name, value)

    def __delfield__(self, name):
        # field = self.__fields__[name]
        super(Data, self).__delattr__(name)

    def __setattr__(self, name, value):
        if name in self.__fields__:
            error = "{!r} objects are immutable".format(type(self).__name__)
            raise AttributeError(error)
        super(Data, self).__setattr__(name, value)

    def __delattr__(self, name):
        if name in self.__fields__:
            error = "{!r} objects are immutable".format(type(self).__name__)
            raise AttributeError(error)
        super(Data, self).__delattr__(name)


def evolve(data, **updates):
    data_copy = copy.copy(data)
    for field_name, value in updates.items():
        if value is DELETE:
            data_copy.__delfield__(field_name)
        else:
            data_copy.__setfield__(field_name, value)
    return data_copy


def fields(cls):
    return cls.__fields__


def constants(cls):
    return cls.__constants__
