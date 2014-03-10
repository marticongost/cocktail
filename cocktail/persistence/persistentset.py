#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2008
"""
from copy import copy, deepcopy
from persistent import Persistent
from cocktail.modeling import SetWrapper


class PersistentSet(SetWrapper, Persistent):

    def __init__(self, items = None):
        SetWrapper.__init__(self, items)

    def __copy__(self):
        return self.__class__(copy(self._items))

    def __deepcopy__(self, memo):
        return self.__class__(deepcopy(self._items))

    def __isub__(self, other):
        rvalue = self._items.__isub__(other)
        self._p_changed = True
        return rvalue

    def __iand__(self, other):
        rvalue = self._items.__iand__(other)
        self._p_changed = True
        return rvalue

    def difference_update(self, other):
        rvalue = self._items.difference_update(other)
        self._p_changed = True
        return rvalue
    
    def symmetric_difference_update(self, other):
        rvalue = self._items.symmetric_difference_update(other)
        self._p_changed = True
        return rvalue

    def intersection_update(self, other):
        rvalue = self._items.intersection_update(other)
        self._p_changed = True
        return rvalue

    def clear(self):
        self._items.clear()
        self._p_changed = True

    def update(self, other):
        self._items.update(other)
        self._p_changed = True

    def pop(self):
        rvalue = self._items.pop()
        self._p_changed = True
        return rvalue
        
    def __ior__(self, other):
        rvalue = self._items.__ior__(other)
        self._p_changed = True
        return rvalue

    def add(self, item):
        self._items.add(item)
        self._p_changed = True

    def remove(self, item):
        self._items.remove(item)
        self._p_changed = True

    def discard(self, item):
        if item in self._items:
            self._items.remove(item)
            self._p_changed = True
    
    def __ixor__(self, other):
        rvalue = self._items.__ixor__(other)
        self._p_changed = True
        return rvalue

