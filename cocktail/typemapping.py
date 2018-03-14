#-*- coding: utf-8 -*-
u"""
Defines the `TypeMapping` class.
"""
from inspect import getmro

_undefined = object()


class TypeMapping(dict):
    """An inheritance aware type/value mapping.

    A type mapping allows to associate arbitrary values to types. It works a
    lot like a regular dictionary, with the following considerations:

        * All keys in the dictionary must be references to classes
        * When retrieving values by key, type inheritance is taken into
          account, mimicking attribute inheritance

    An example:

    >>> class A:
    ...    pass
    >>> class B(A):
    ...    pass
    >>> mapping = TypeMapping()
    >>> mapping[A] = "A"
    >>> mapping[B]
    "A"

    Type mappings are espcially useful to extend classes with additional data
    and behavior without polluting their namespace.
    """

    def __getitem__(self, cls):

        value = self.get(cls, _undefined)

        if value is _undefined:
            raise KeyError(cls)

        return value

    def get(self, cls, default = None, recursive = True):
        if not recursive:
            return dict.get(self, cls, default)

        for cls in getmro(cls):
            value = dict.get(self, cls, _undefined)
            if value is not _undefined:
                return value
        else:
            return default

    def iter_by_type(self, cls):
        for cls in getmro(cls):
            value = dict.get(self, cls, _undefined)
            if value is not _undefined:
                yield (cls, value)


class ChainTypeMapping(TypeMapping):

    __parent = None

    @property
    def parent(self):
        return self.__parent

    def new_child(self, *args, **kwargs):
        child = self.__class__(*args, **kwargs)
        child.__parent = self
        return child

    def get(self, cls, default = None, recursive = True):

        if recursive:
            for cls in getmro(cls):
                mapping = self
                while mapping is not None:
                    value = dict.get(mapping, cls, _undefined)
                    if value is not _undefined:
                        return value
                    mapping = mapping.__parent
        else:
            mapping = self
            while mapping is not None:
                value = dict.get(mapping, cls, _undefined)
                if value is not _undefined:
                    return value
                mapping = mapping.__parent

        return default

    def iter_by_type(self, cls, recursive = True):
        if recursive:
            for cls in getmro(cls):
                mapping = self
                while mapping is not None:
                    value = dict.get(mapping, cls, _undefined)
                    if value is _undefined:
                        mapping = mapping.__parent
                    else:
                        yield (cls, value)
                        break
        else:
            for entry in TypeMapping.iter_by_type(self, cls):
                yield entry

