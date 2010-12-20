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

    def get(self, cls, default = None):
        for cls in getmro(cls):
            value = dict.get(self, cls, _undefined)
            if value is not _undefined:
                return value
        else:
            return default


