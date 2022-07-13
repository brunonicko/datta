from __future__ import absolute_import, division, print_function

import collections
import copy
import inspect

import six
from basicco import mapping_proxy, scrape_class, mangling
from tippo import TYPE_CHECKING

from ._field import Field
from ._constant import Constant
from ._sentinels import DELETE

if TYPE_CHECKING:
    from tippo import Any

__all__ = ["DataMeta", "Data", "evolve", "fields", "constants"]


class FieldScraper(object):
    __slots__ = ("__cls", "__field_order")

    def __init__(self, cls, cls_fields):
        # type: (DataMeta, dict[str, Field]) -> None
        self.__cls = cls  # type: DataMeta
        self.__field_order = {}  # type: dict[str, int]

    def scrape(self):
        # type: () -> mapping_proxy.MappingProxyType[str, Field]

        # Reset field order.
        self.__field_order = {}

        # Scrape class for fields.
        cls_fields = scrape_class.scrape_class(
            self.__cls,
            self.__member_filter,
            self.__override_filter,
        )  # type: dict[str, Field]

        # Order fields.
        ordered_fields = collections.OrderedDict()
        for field_name, field in sorted(cls_fields.items(), key=lambda i: self.__field_order[i[0]]):
            ordered_fields[field_name] = field

        return mapping_proxy.MappingProxyType(ordered_fields)

    def __member_filter(self, base, member_name, member):
        # type: (DataMeta, str, Any) -> bool

        # Skip non-data base classes.
        if not isinstance(base, DataMeta):
            self.__field_order.pop(member_name)
            return False

        # Get field from data class.
        if isinstance(member, Field):
            if not isinstance(base, DataMeta):
                return False

            # Remember the order, this is the first time seeing this field.
            assert member_name not in self.__field_order
            self.__field_order[member_name] = member.order

            return True

        self.__field_order.pop(member_name)
        return False

    @staticmethod
    def __override_filter(base, member_name, member, previous_member):
        # type: (DataMeta, str, Any, Any) -> bool
        if not isinstance(base, DataMeta):
            error = "non-data {!r} base overrides {} {!r}".format(
                base.__name__,
                type(previous_member).__name__.lower(),
                member_name,
            )
            raise TypeError(error)

        if not isinstance(member, Field):
            error = "{!r} base overrides {} {!r} with a {!r} object".format(
                base.__name__,
                type(previous_member).__name__.lower(),
                member_name,
                type(member).__name__,
            )
            raise TypeError(error)

        return True


class DataMeta(type):
    __constants__ = {}  # type: dict[str, Constant]
    __fields__ = {}  # type: dict[str, Field]
    __kwargs__ = {}  # type: dict[str, object]

    def __new__(mcs, name, bases, dct, **kwargs):

        # Merge kwargs and store them in the class.
        dct["__kwargs__"] = kwargs.update(dct.get("__kwargs__", {}))

        # Gather constants for this class and convert them to values.
        this_constants = {n: dct.pop(c) for n, c in list(dct.items()) if isinstance(c, Constant)}
        __constants__ = {}
        dct["__constants__"] = mapping_proxy.MappingProxyType(__constants__)

        dct.update((n, c.value) for n, c in this_constants.items())

        # Gather fields for this class and convert them to slots.
        this_fields = {n: dct.pop(n) for n, f in list(dct.items()) if isinstance(f, Field)}
        __fields__ = collections.OrderedDict()
        dct["__fields__"] = mapping_proxy.MappingProxyType(__fields__)

        sorted_slots = tuple(_unmangle(n, name) for n, f in sorted(this_fields.items(), key=lambda i: i[1].order))
        dct["__slots__"] = tuple(dct.get("__slots__", ())) + sorted_slots

        # Build class.
        cls = super(DataMeta, mcs).__new__(mcs, name, bases, dct, **kwargs)

        # Gather fields and constants from bases.
        all_constants = {}
        all_fields = {}
        field_order = {}
        for base in inspect.getmro(cls)[::-1][1:]:
            is_data = isinstance(base, DataMeta)

            # Can't have non-slotted class in the chain.
            if not is_data and "__dict__" in base.__dict__:
                error = "unsupported non-slotted base class {!r}".format(base.__name__)
                raise TypeError(error)

            # For each member defined in the class.
            for member_name, member in base.__dict__.items():

                # Base is data, redirect members.
                if is_data:
                    if base is cls:
                        base_fields = this_fields
                        base_constants = this_constants
                    else:
                        base_fields = getattr(base, "__fields__")
                        base_constants = getattr(base, "__constants__")

                    is_field = member_name in base_fields
                    if is_field:
                        member = base_fields[member_name]

                    is_constant = member_name in base_constants
                    if is_constant:
                        member = base_constants[member_name]
                else:
                    is_field = isinstance(member, Field)
                    is_constant = isinstance(member, Constant)

                # Member is not a field.
                if not is_field:

                    # Can't override field with non-field.
                    if member_name in all_fields:
                        error = "class {!r} overrides field {!r} with non-field".format(base.__name__, member_name)
                        raise TypeError(error)

                else:

                    # Base is not data.
                    if not is_data:

                        # Can't override any field.
                        if member_name in all_fields:
                            error = "non-data class {!r} overrides field {!r}".format(base.__name__, member_name)
                            raise TypeError(error)

                    # Remember order only if it's the first time we are seeing this field.
                    if member_name not in field_order:
                        field_order[member_name] = member.order

                    # Remember field.
                    all_fields[member_name] = member

                # Member is not a constant.
                if not is_constant:

                    # Can't override constant with non-constant.
                    if member_name in all_constants:
                        error = "class {!r} overrides constant {!r} with non-constant".format(
                            base.__name__, member_name
                        )
                        raise TypeError(error)

                else:

                    # Base is not data.
                    if not is_data:

                        # Can't override any constant.
                        if member_name in all_constants:
                            error = "non-data class {!r} overrides constant {!r}".format(base.__name__, member_name)
                            raise TypeError(error)

                    # Remember constant.
                    all_constants[member_name] = member

        # Store fields according to their original order, store constants.
        __fields__.update((n, f) for n, f in sorted(all_fields.items(), key=lambda i: field_order[i[0]]))
        __constants__.update(all_constants)

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

    def __init_subclass__(cls, **kwargs):
        pass

    def __init__(self, *args, **kwargs):  # TODO
        for (field_name, field), value in zip(self.__fields__.items(), args):
            object.__setattr__(self, field_name, value)
        for field_name, value in kwargs.items():
            object.__setattr__(self, field_name, value)

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
                value = getattr(self, field_name)
            except AttributeError:
                continue
            yield field_name, value

    def __setattr__(self, name, value):
        field = self.__fields__.get(name)
        if field is not None:
            pass
        super(Data, self).__setattr__(name, value)

    def __delattr__(self, name):
        field = self.__fields__.get(name)
        if field is not None:
            pass
        super(Data, self).__delattr__(name)


def evolve(data, **updates):
    data_copy = copy.copy(data)
    for field_name, value in updates.items():
        if value is DELETE:
            delattr(data_copy, field_name)
        else:
            setattr(data_copy, field_name, value)
    return data_copy


def fields(cls):
    return cls.__fields__


def constants(cls):
    return cls.__constants__
