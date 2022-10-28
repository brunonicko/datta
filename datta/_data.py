import copy

import six
import estruttura
from basicco import mangling
from tippo import cast


class DataMeta(estruttura.StructureMeta):

    @staticmethod
    def __edit_dct__(this_attribute_map, attribute_map, name, bases, dct, **kwargs):
        slots = list(dct.pop("__slots__", ()) or ())
        for attribute_name in this_attribute_map:
            del dct[attribute_name]
            slots.append(mangling.unmangle(attribute_name, name))
        dct["__slots__"] = tuple(slots)
        return dct


class Data(six.with_metaclass(DataMeta, estruttura.ImmutableStructure)):
    __slots__ = ()

    def __getitem__(self, name):
        if name in type(self).__attributes__:
            try:
                return getattr(self, name)
            except AttributeError:
                pass
        raise KeyError(name)

    def __contains__(self, name):
        return name in type(self).__attributes__ and hasattr(self, cast(str, name))

    def _do_init(self, initial_values):
        for name, value in six.iteritems(initial_values):
            object.__setattr__(self, name, value)

    def _do_update(self, inserts, deletes, updates_old, updates_new, updates_and_inserts):
        new_self = copy.copy(self)
        for name in deletes:
            object.__delattr__(new_self, name)
        new_self._do_init(updates_and_inserts)
        return new_self

    @classmethod
    def _do_deserialize(cls, values):
        self = cls.__new__(cls)
        self._do_init(values)
        return self
