#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2008
"""
from copy import copy, deepcopy
from persistent import Persistent
from cocktail.modeling import DictWrapper


class PersistentMapping(DictWrapper, Persistent):

    def __init__(self, items = None):
        DictWrapper.__init__(self, items)

    def __copy__(self):
        return self.__class__(copy(self._items))

    def __deepcopy__(self, memo):
        return self.__class__(deepcopy(self._items))

    def __delitem__(self, key):
        self._items.__delitem__(key)
        self._p_changed = True

    def __setitem__(self, key, value):
        self._items.__setitem__(key, value)
        self._p_changed = True

    def clear(self):
        self._items.clear()
        self._p_changed = True

    def update(self, *args, **kwargs):
        self._items.update(*args, **kwargs)
        self._p_changed = True

    def setdefault(self, key, default = None):
        if key not in self._items:
            self._p_changed = True
        return self._items.setdefault(key, default)

    def pop(self, key, *args):
        self._p_changed = True
        return self._items.pop(key, *args)

    def popitem(self):
        self._p_changed = True
        return self._items.popitem()

