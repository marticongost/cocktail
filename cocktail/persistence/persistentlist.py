#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2008
"""
from copy import copy, deepcopy
from persistent import Persistent
from cocktail.modeling import ListWrapper
from cocktail.schema.schemacollections import add, _list_add


class PersistentList(ListWrapper, Persistent):

    def __init__(self, items = None):
        ListWrapper.__init__(self, items)

    def __copy__(self):
        return self.__class__(copy(self._items))

    def __deepcopy__(self, memo):
        return self.__class__(deepcopy(self._items))

    def __setitem__(self, i, item):
        self._items.__setitem__(i, item)        
        self._p_changed = True

    def __delitem__(self, i):
        self._items.__delitem__(i)
        self._p_changed = True

    def __setslice__(self, i, j, other):
        self._items.__setslice__(i, j, other)
        self._p_changed = True

    def __delslice__(self, i, j):
        self._items.__delslice__(i, j)
        self._p_changed = True

    def __iadd__(self, other):
        self._items.__iadd__(other)
        self._p_changed = True
        return self

    def __imul__(self, n):
        self._items.__imul__(n)
        self._p_changed = True
        return self

    def append(self, item):
        self._items.append(item)
        self._p_changed = True

    def insert(self, i, item):
        self._items.insert(i, item)
        self._p_changed = True

    def pop(self, i = -1):
        item = self._items.pop(i)
        self._p_changed = True
        return item

    def remove(self, item):
        self._items.remove(item)
        self._p_changed = True

    def reverse(self):
        self._items.reverse()
        self._p_changed = True

    def sort(self, *args):
        self._items.sort(*args)
        self._p_changed = True

    def extend(self, other):
        self._items.extend(other)
        self._p_changed = True


add.implementations[PersistentList] = _list_add

