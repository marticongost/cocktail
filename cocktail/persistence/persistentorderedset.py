#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			May 2009
"""
from copy import copy, deepcopy
from persistent import Persistent
from cocktail.modeling import OrderedSet
from cocktail.schema.schemacollections import add, _list_add


class PersistentOrderedSet(OrderedSet, Persistent):

    def __init__(self, items = None):
        OrderedSet.__init__(self, items)

    def __setitem__(self, i, item):
        if item not in self._items:
            self._items[i] = item
            self._p_changed = True

    def __delitem__(self, i):
        OrderedSet.__delitem__(self, i)
        self._p_changed = True

    def __setslice__(self, i, j, other):
        head = self._items[:i]
        tail = self._items[j:]
        body = [x for x in other if x not in head and x not in tail]
        
        if body:
            self._items = head + body + tail
            self._p_changed = True

    def __delslice__(self, i, j):
        OrderedSet.__delslice__(self, i, j)
        self._p_changed = True

    def append(self, item, relocate = False):

        added = OrderedSet.append(self, item, relocate)

        if added or relocate:
            self._p_changed = True
            
        return added

    def insert(self, i, item, relocate = False):
        
        added = OrderedSet.insert(self, i, item, relocate)
        
        if added or relocate:            
            self._p_changed = True

        return added

    def pop(self, i = -1):
        item = self._items.pop(i)
        self._p_changed = True
        return item

    def remove(self, item):
        OrderedSet.remove(self, item)
        self._p_changed = True

    def reverse(self):
        OrderedSet.reverse(self)
        self._p_changed = True

    def sort(self, *args):
        OrderedSet.sort(self, *args)
        self._p_changed = True

add.implementations[PersistentOrderedSet] = _list_add

